"""Credit tracker (CLAUDE.md rule 7): sums `cost` over every runs/*/usage.jsonl.

  PYTHONPATH=src .venv/bin/python -m track_a.budget
"""
from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime

from .config import BUDGET_CAP, RUNS, SLOW_SOFT_CAP


def main() -> None:
    by_run: dict[str, float] = defaultdict(float)
    by_model: dict[str, float] = defaultdict(float)
    by_hour: dict[str, float] = defaultdict(float)
    n_calls = 0
    n_err = 0
    for p in sorted(RUNS.glob("*/usage.jsonl")):
        with p.open() as f:
            for line in f:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                n_calls += 1
                if r.get("status") != 200:
                    n_err += 1
                c = float(r.get("cost") or 0.0)
                by_run[p.parent.name] += c
                by_model[r.get("model", "?")] += c
                by_hour[datetime.fromtimestamp(r["t"]).strftime("%a %H:00")] += c
    total = sum(by_run.values())
    print(f"TOTAL {total:.3f} / {BUDGET_CAP} credits  (slow-lane soft cap {SLOW_SOFT_CAP})  | calls {n_calls}, non-200 attempts {n_err}")
    print("\nby run:")
    for k, v in sorted(by_run.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<40} {v:8.3f}")
    print("\nby model:")
    for k, v in sorted(by_model.items(), key=lambda kv: -kv[1]):
        print(f"  {k:<24} {v:8.3f}")
    print("\nby hour:")
    for k, v in sorted(by_hour.items()):
        print(f"  {k:<10} {v:8.3f}")


if __name__ == "__main__":
    main()
