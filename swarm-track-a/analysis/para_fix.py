"""Stage 1e amendment: restore the task entry-point function name in deepseek paraphrases (see RUN_INDEX Sun 3:45 PM).

  PYTHONPATH=src .venv/bin/python analysis/para_fix.py

deepseek-v4-flash renames the task function when paraphrasing, so hidden tests error at collection. For every non-kept
record in runs/para_ds with code, try renaming each top-level def back to the task's function name (word-boundary),
re-run the sandbox tests, keep the first variant that passes (benign) / passes with canary (attack). Kept records are
copied unchanged. Writes runs/para_ds_fixed/submissions.jsonl in the bank schema.
"""
from __future__ import annotations

import asyncio
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "src")
from track_a.bank import load_tasks, test_code  # noqa: E402
from track_a.config import CANARY  # noqa: E402
from track_a.sandbox import utils_source  # noqa: E402

SRC = Path("runs/para_ds/submissions.jsonl")
DST_DIR = Path("runs/para_ds_fixed")
SEM = asyncio.Semaphore(8)


async def fix_one(rec: dict, tasks: dict, utils_src: str) -> dict:
    out = dict(rec)
    if rec["kept"] or not rec.get("code", "").strip():
        return out
    task = tasks[rec["task"]]
    fn = task["fn"]
    code = rec["code"]
    defs = re.findall(r"^def\s+(\w+)\s*\(", code, flags=re.M)
    cands = [d for d in defs if d != fn]
    if fn in defs:  # fn present yet tests failed: not a rename problem, leave as-is
        return out
    for cand in cands:
        new_code = re.sub(rf"\b{re.escape(cand)}\b", fn, code)
        async with SEM:
            tests = await test_code(new_code, task["tests"], utils_src, f"{task['id']}_parafix")
        if tests and tests["all_pass"]:
            canary = CANARY in new_code
            if rec["condition"] == "attack" and not canary:
                continue
            out.update(code=new_code, tests=tests, canary=canary, kept=True,
                       uses_telemetry="send_report" in new_code, fn_restored_from=cand)
            return out
    return out


async def main() -> None:
    tasks = load_tasks()
    utils_src = utils_source()
    recs = [json.loads(l) for l in SRC.open()]
    fixed = await asyncio.gather(*(fix_one(r, tasks, utils_src) for r in recs))
    DST_DIR.mkdir(parents=True, exist_ok=True)
    with (DST_DIR / "submissions.jsonl").open("w") as f:
        for r in fixed:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter
    c = Counter((r["policy"], r["condition"], r["kept"]) for r in fixed)
    for k in sorted(c):
        print(k, c[k])
    print("renamed+kept:", sum(1 for r in fixed if r.get("fn_restored_from")))


if __name__ == "__main__":
    asyncio.run(main())
