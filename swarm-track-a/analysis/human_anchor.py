"""Idea 3 (agreement): once the human has filled LABELS.csv, compare human suspicion to the monitors, by author family.

  .venv/bin/python analysis/human_anchor.py --packet runs/human_anchor --scores runs/stage1_mon*/scores.jsonl runs/stage1_logic/scores.jsonl

Key question: on gemma-written attacks, do humans also give low suspicion (so the code is genuinely subtle) or high suspicion
(so the gemma *monitor* is uniquely lenient)? Reports human vs monitor mean suspicion on gemma attacks, the human catch rate vs the
gemma monitor's, and overall human-monitor rank correlation.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate import FAMILY, load_scores, per_submission  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", default="runs/human_anchor")
    ap.add_argument("--scores", nargs="+", required=True)
    args = ap.parse_args()
    pk = Path(args.packet)
    key = json.loads((pk / ".key.json").read_text())
    human = {}
    with (pk / "LABELS.csv").open() as f:
        for row in csv.DictReader(f):
            v = row["suspicion_0_100"].strip()
            if v != "":
                human[row["index"]] = float(v)
    if not human:
        raise SystemExit("LABELS.csv has no filled scores yet.")
    recs = []
    for idx, meta in key.items():
        if idx in human:
            recs.append({**meta, "index": idx, "human": human[idx]})
    h = pd.DataFrame(recs)
    h["family"] = h.policy.map(FAMILY)

    df = load_scores([Path(p) for p in args.scores])
    df = df[df.mon_condition == "blind"]
    sub = per_submission(df)
    mon = sub.pivot_table(index="submission_id", columns="monitor", values="mean_score")
    h = h.merge(mon, left_on="submission_id", right_index=True, how="left")
    mons = [c for c in mon.columns]

    lines = [f"# Human anchor ({len(h)} labeled: " + ", ".join(f"{k} {int(v)}" for k, v in h.true_label.value_counts().items()) + ")", ""]
    # overall human vs monitor-mean rank correlation
    h["monitor_mean"] = h[mons].mean(axis=1)
    from scipy.stats import spearmanr
    rho, p = spearmanr(h.human, h.monitor_mean, nan_policy="omit")
    lines.append(f"- Human vs mean-of-monitors suspicion: Spearman rho = {rho:.2f} (p={p:.2g}), n={h.human.notna().sum()}")
    # attack vs benign separation by humans
    atk = h[h.true_label != "benign"]; ben = h[h.true_label == "benign"]
    lines.append(f"- Human mean suspicion: benign {ben.human.mean():.1f}, telemetry attacks {h[h.true_label=='attack_telemetry'].human.mean():.1f}, "
                 f"logic attacks {h[h.true_label=='attack_logic'].human.mean():.1f}")
    # the key comparison: gemma-written attacks, human vs the gemma monitors
    lines += ["", "## Gemma-written attacks: human vs monitor suspicion", "",
              "| submission | task | author | human | gemma-26b mon | gemma-31b mon | mean other-family mon |", "|---|---|---|---|---|---|---|"]
    ga = h[(h.true_label != "benign") & (h.family == "gemma")]
    for _, r in ga.iterrows():
        others = [r[m] for m in mons if FAMILY.get(m) != "gemma" and pd.notna(r.get(m))]
        g26 = r.get("gemma-4-26b-a4b-it", np.nan); g31 = r.get("gemma-4-31b-it", np.nan)
        lines.append(f"| {r['index']} | {r['task']} | {r['policy']} | {r['human']:.0f} | "
                     f"{g26:.0f} | {g31:.0f} | {np.mean(others):.0f} |")
    if len(ga):
        g26 = ga["gemma-4-26b-a4b-it"].mean(); g31 = ga["gemma-4-31b-it"].mean()
        oth = ga[[m for m in mons if FAMILY.get(m) != "gemma"]].mean(axis=1).mean()
        lines += ["", f"Means on gemma-written attacks: human {ga.human.mean():.1f}, gemma-26b monitor {g26:.1f}, gemma-31b monitor {g31:.1f}, "
                  f"other-family monitors {oth:.1f}.",
                  "- If human ≈ other-family ≫ gemma monitors: the gemma code is NOT subtle to an outsider; the gemma monitor is lenient (supports the finding).",
                  "- If human ≈ gemma monitors ≪ other-family: humans also miss it; the gemma attacks may be genuinely subtle (qualifies the finding)."]
    (pk / "human_anchor_result.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n[written] {pk}/human_anchor_result.md")


if __name__ == "__main__":
    main()
