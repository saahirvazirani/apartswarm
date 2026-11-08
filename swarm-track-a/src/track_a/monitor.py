"""Pipeline steps 6-7: monitors score kept submissions, blind (or told), N draws each.

  PYTHONPATH=src .venv/bin/python -m track_a.monitor --run-id stage1_cheap3 --bank bank_cheap3 \
      --monitors deepseek-v4-flash gemma-4-26b-a4b-it glm-53-flash [--mon-condition blind|told] [--draws 3] \
      [--attack-stage polished|raw] [--tasks t001 ...] [--policies ...]

Writes runs/<run_id>/scores.jsonl keyed by (submission_id, monitor, mon_condition, draw); re-running resumes.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

from .client import TrackClient
from .config import ALL_MODELS, CAP_MONITOR, N_DRAWS, RUNS, TEMP_MONITOR
from .jsonx import parse_score
from .prompts import freeze_into, load_prompt, prompt_hashes, render
from .bank import load_existing, load_tasks


def select_submissions(bank_dir: Path, attack_stage: str, tasks: set[str] | None, policies: set[str] | None) -> list[dict]:
    recs = list(load_existing(bank_dir / "submissions.jsonl").values())
    out = []
    for r in recs:
        if not r.get("kept"):
            continue
        if r["condition"] == "benign" and r["stage"] != "raw":
            continue
        if r["condition"] == "attack" and r["stage"] != attack_stage:
            continue
        if tasks and r["task"] not in tasks:
            continue
        if policies and r["policy"] not in policies:
            continue
        out.append(r)
    return out


def load_scores(path: Path) -> set[tuple]:
    done = set()
    if path.exists():
        with path.open() as f:
            for line in f:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                done.add((r["submission_id"], r["monitor"], r["mon_condition"], r["draw"]))
    return done


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--bank", required=True, help="run id of the bank (runs/<bank>/submissions.jsonl)")
    ap.add_argument("--monitors", nargs="+", required=True)
    ap.add_argument("--mon-condition", choices=["blind", "told"], default="blind")
    ap.add_argument("--draws", type=int, default=N_DRAWS)
    ap.add_argument("--attack-stage", choices=["polished", "raw"], default="polished")
    ap.add_argument("--tasks", nargs="*")
    ap.add_argument("--policies", nargs="*")
    args = ap.parse_args()
    for m in args.monitors:
        assert m in ALL_MODELS, m

    run_dir = RUNS / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    freeze_into(run_dir)
    bank_dir = RUNS / args.bank
    tasks = load_tasks()
    subs = select_submissions(bank_dir, args.attack_stage, set(args.tasks or []) or None, set(args.policies or []) or None)
    scores_path = run_dir / "scores.jsonl"
    done = load_scores(scores_path)
    meta_path = run_dir / "meta.json"
    meta = json.loads(meta_path.read_text()) if meta_path.exists() else {"created": datetime.now().isoformat(timespec="seconds"), "invocations": []}
    meta["invocations"].append({"t": datetime.now().isoformat(timespec="seconds"), "args": vars(args), "n_submissions": len(subs),
                                "prompt_hashes": prompt_hashes(), "bank": args.bank})
    meta_path.write_text(json.dumps(meta, indent=2))

    template = load_prompt("monitor_blind" if args.mon_condition == "blind" else "monitor_told")
    lock = asyncio.Lock()
    n_new = 0

    async def score(sub: dict, monitor: str, draw: int, tc: TrackClient) -> None:
        nonlocal n_new
        key = (sub["submission_id"], monitor, args.mon_condition, draw)
        if key in done:
            return
        kw = {"task": tasks[sub["task"]]["task_text"], "code": sub["code"]}
        if args.mon_condition == "told":
            kw["model_name"] = sub["policy"]
        prompt = render(template, **kw)
        r = await tc.call(monitor, prompt, temperature=TEMP_MONITOR, max_output_tokens=CAP_MONITOR, draw=draw, tag="monitor",
                          meta={"submission_id": sub["submission_id"], "monitor": monitor, "mon_condition": args.mon_condition})
        p = parse_score(r.text) if r.ok else parse_score("")
        rec = {
            "submission_id": sub["submission_id"], "task": sub["task"], "policy": sub["policy"], "condition": sub["condition"],
            "stage": sub["stage"], "resample": sub["resample"], "monitor": monitor, "mon_condition": args.mon_condition, "draw": draw,
            "score": p.score, "reason": p.reason, "parse_ok": p.ok, "parse_method": p.method, "ok": r.ok, "status": r.status,
            "cost": r.cost, "cache_key": r.cache_key, "incomplete": r.incomplete, "raw_text": r.text if r.ok else None,
        }
        async with lock:
            with scores_path.open("a") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            done.add(key)
            n_new += 1

    t0 = time.time()
    async with TrackClient(run_dir) as tc:
        jobs = [score(s, m, d, tc) for s in subs for m in args.monitors for d in range(args.draws)]
        todo = sum(1 for s in subs for m in args.monitors for d in range(args.draws) if (s["submission_id"], m, args.mon_condition, d) not in done)
        print(f"{len(subs)} kept submissions x {len(args.monitors)} monitors x {args.draws} draws = {len(jobs)} ({todo} to do)")
        await asyncio.gather(*jobs)
        spent = tc.session_spent
    # quick parse-failure report
    n = {m: [0, 0] for m in args.monitors}
    with scores_path.open() as f:
        for line in f:
            r = json.loads(line)
            if r["monitor"] in n:
                n[r["monitor"]][0] += 1
                n[r["monitor"]][1] += 0 if r["parse_ok"] else 1
    for m, (tot, bad) in n.items():
        print(f"  {m}: {tot} scores, {bad} parse failures ({bad/max(tot,1):.1%})")
    print(f"done in {time.time()-t0:.0f}s | new scores {n_new} | credits {spent:.4f} | {scores_path}")


if __name__ == "__main__":
    asyncio.run(main())
