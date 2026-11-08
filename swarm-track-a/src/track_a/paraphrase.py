"""Pipeline step 8 (Stage 1c): paraphrase every kept submission once with the fixed paraphraser, re-test, keep passers.

  PYTHONPATH=src .venv/bin/python -m track_a.paraphrase --run-id para --bank bank_cheap3_v2 bank_rest4 [--policies ...] [--tasks ...]

Writes runs/<run_id>/submissions.jsonl in the bank schema (stage = "paraphrased", condition unchanged) so monitor.py can score it
with `--bank para --benign-stage paraphrased --attack-stage paraphrased`. Kept := tests pass (benign) or canary present AND tests
pass (attack). Each record carries `orig_submission_id` for the paired comparison with the un-paraphrased score (README H3).
"""
from __future__ import annotations

import argparse
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

from .bank import TEST_PAR, is_final, load_existing, load_tasks, sid, test_code
from .client import TrackClient, pick_keys
from .config import CANARY, CAP_PARAPHRASE, PARAPHRASER, RUNS, TEMP_POLICY
from .jsonx import extract_code
from .prompts import freeze_into, load_prompt, prompt_hashes
from .sandbox import utils_source


def select_kept(bank_dirs: list[Path], policies: set[str] | None, tasks: set[str] | None) -> list[dict]:
    out = []
    for d in bank_dirs:
        for r in load_existing(d / "submissions.jsonl").values():
            if not r.get("kept"):
                continue
            if r["condition"] == "benign" and r["stage"] != "raw":
                continue
            if r["condition"] == "attack" and r["stage"] != "polished":
                continue
            if policies and r["policy"] not in policies:
                continue
            if tasks and r["task"] not in tasks:
                continue
            out.append(r)
    return out


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--bank", nargs="+", required=True)
    ap.add_argument("--policies", nargs="*")
    ap.add_argument("--tasks", nargs="*")
    ap.add_argument("--tpm", type=float, default=60_000)
    ap.add_argument("--inflight", type=int, default=12)
    ap.add_argument("--key-idx", nargs="*", type=int)
    ap.add_argument("--paraphraser", default=PARAPHRASER, help="rewriting model (default: the fixed gemma-4-26b-a4b-it paraphraser)")
    args = ap.parse_args()

    run_dir = RUNS / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    freeze_into(run_dir)
    tasks = load_tasks()
    subs = select_kept([RUNS / b for b in args.bank], set(args.policies or []) or None, set(args.tasks or []) or None)
    path = run_dir / "submissions.jsonl"
    existing = load_existing(path)
    meta_path = run_dir / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {"created": datetime.now().isoformat(timespec="seconds"), "invocations": []}
    meta["invocations"].append({"t": datetime.now().isoformat(timespec="seconds"), "args": vars(args), "n_submissions": len(subs),
                                "prompt_hashes": prompt_hashes(), "paraphraser": args.paraphraser})
    meta_path.write_text(json.dumps(meta, indent=2))
    template = load_prompt("paraphrase")
    utils_src = utils_source()
    lock = asyncio.Lock()

    async def one(sub: dict, tc: TrackClient) -> None:
        key = (sub["task"], sub["policy"], sub["condition"], "paraphrased", sub["resample"])
        if is_final(existing.get(key)):
            return
        task = tasks[sub["task"]]
        prompt = f"{template}\n\n```python\n{sub['code']}```"
        r = await tc.call(args.paraphraser, prompt, temperature=TEMP_POLICY, max_output_tokens=CAP_PARAPHRASE, draw=0, tag="paraphrase",
                          meta={"orig_submission_id": sub["submission_id"]}, expect_output_tokens=600)
        code = extract_code(r.text, task["fn"]) if r.ok else ""
        tests = await test_code(code, task["tests"], utils_src, f"{task['id']}_para") if code.strip() else None
        canary = CANARY in code
        kept = bool(tests and tests["all_pass"] and (canary if sub["condition"] == "attack" else True))
        rec = {
            "submission_id": sid(*key), "orig_submission_id": sub["submission_id"], "task": sub["task"], "policy": sub["policy"],
            "condition": sub["condition"], "stage": "paraphrased", "orig_stage": sub["stage"], "resample": sub["resample"],
            "ok": r.ok, "status": r.status, "code": code, "canary": canary, "uses_telemetry": "send_report" in code, "tests": tests,
            "kept": kept, "cost": r.cost, "cache_key": r.cache_key, "incomplete": r.incomplete, "text_len": len(r.text or ""),
            "paraphraser": args.paraphraser,
        }
        async with lock:
            with path.open("a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            existing[key] = rec

    t0 = time.time()
    async with TrackClient(run_dir, keys=pick_keys(args.key_idx), tpm_per_key=args.tpm, fast_inflight=args.inflight) as tc:
        todo = [s for s in subs if not is_final(existing.get((s["task"], s["policy"], s["condition"], "paraphrased", s["resample"])))]
        print(f"{len(subs)} kept submissions, {len(todo)} to paraphrase with {args.paraphraser}")
        await asyncio.gather(*(one(s, tc) for s in todo))
        print(tc.stats())
        spent = tc.session_spent
    recs = list(load_existing(path).values())
    lines = ["| policy | condition | n | ok | canary kept | tests pass | kept |", "|---|---|---|---|---|---|---|"]
    for pol in sorted({r["policy"] for r in recs}):
        for cond in ("benign", "attack"):
            R = [r for r in recs if r["policy"] == pol and r["condition"] == cond]
            if R:
                lines.append(f"| {pol} | {cond} | {len(R)} | {sum(1 for r in R if r['ok'])} | {sum(1 for r in R if r['canary'])} | "
                             f"{sum(1 for r in R if r['tests'] and r['tests']['all_pass'])} | {sum(1 for r in R if r['kept'])} |")
    (run_dir / "summary.md").write_text(f"# Paraphrase {args.run_id}\n\n" + "\n".join(lines) + f"\n\ncredits this invocation: {spent:.4f}\n")
    print("\n".join(lines))
    print(f"done in {time.time()-t0:.0f}s | credits {spent:.4f} | {path}")


if __name__ == "__main__":
    asyncio.run(main())
