"""Robustness of the identity effect (post-hoc, reported as such): per-monitor and per-policy leniency indices, and
leave-one-family-out refits of the pre-registered two-way model.

  .venv/bin/python analysis/robustness.py --scores runs/stage1_mon*/scores.jsonl --out analysis/out/full

Leniency index of monitor m  = mean TPR of m on cross-family policies - TPR of m on its own policy (positive = lenient to itself).
Leniency index of policy p   = mean TPR of cross-family monitors on p - TPR of p's own monitor on p.
Leave-one-family-out: drop every unit whose policy OR monitor is in family F, refit the GLM / LPM and the task bootstrap.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate import FAMILY, MODEL_ORDER, cells, load_scores, per_submission  # noqa: E402
from fit import build_units, glm_fit, task_bootstrap  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fpr", type=float, default=0.05)
    ap.add_argument("--boots", type=int, default=1000)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    df = load_scores([Path(p) for p in args.scores])
    df = df[df.mon_condition == "blind"]
    sub = per_submission(df)
    c = cells(sub, args.fpr)
    c = c[c.n_attack > 0]
    lines = ["# Robustness of the identity effect (post-hoc)", ""]

    # per-monitor leniency index
    lines += ["## Per-monitor leniency index (cross-family mean TPR − TPR on own model; AUROC version alongside)", "",
              "| monitor | TPR own | TPR cross-family (mean) | leniency (TPR) | AUROC own | AUROC cross | leniency (AUROC) |", "|---|---|---|---|---|---|---|"]
    rows = []
    for m in [x for x in MODEL_ORDER if x in set(c.monitor)]:
        own = c[(c.monitor == m) & (c.policy == m)]
        cross = c[(c.monitor == m) & (c.rel == "cross_family")]
        if own.empty or cross.empty:
            continue
        r = dict(monitor=m, tpr_own=float(own.tpr.iloc[0]), tpr_cross=float(cross.tpr.mean()), auroc_own=float(own.auroc.iloc[0]), auroc_cross=float(cross.auroc.mean()))
        r["leniency_tpr"] = r["tpr_cross"] - r["tpr_own"]
        r["leniency_auroc"] = r["auroc_cross"] - r["auroc_own"]
        rows.append(r)
        lines.append(f"| {m} | {r['tpr_own']:.2f} | {r['tpr_cross']:.2f} | {r['leniency_tpr']:+.2f} | {r['auroc_own']:.3f} | {r['auroc_cross']:.3f} | {r['leniency_auroc']:+.3f} |")
    pd.DataFrame(rows).to_csv(out / "leniency_by_monitor.csv", index=False)

    # per-policy
    lines += ["", "## Per-policy index (cross-family monitors' mean TPR on p − own monitor's TPR on p)", "",
              "| policy | TPR by own monitor | TPR by cross-family monitors (mean) | difference |", "|---|---|---|---|"]
    rows = []
    for p in [x for x in MODEL_ORDER if x in set(c.policy)]:
        own = c[(c.monitor == p) & (c.policy == p)]
        cross = c[(c.policy == p) & (c.rel == "cross_family")]
        if own.empty or cross.empty:
            continue
        r = dict(policy=p, tpr_own=float(own.tpr.iloc[0]), tpr_cross=float(cross.tpr.mean()))
        r["diff"] = r["tpr_cross"] - r["tpr_own"]
        rows.append(r)
        lines.append(f"| {p} | {r['tpr_own']:.2f} | {r['tpr_cross']:.2f} | {r['diff']:+.2f} |")
    pd.DataFrame(rows).to_csv(out / "leniency_by_policy.csv", index=False)

    # leave-one-family-out
    units = build_units(sub, c)
    lines += ["", "## Leave-one-family-out refits (drop every unit whose policy or monitor is in the family)", "",
              "| dropped family | units | same_model log-odds [95% CI] | same_family log-odds [95% CI] | same-model catch | cross-family catch | diag − cross [95% CI] |",
              "|---|---|---|---|---|---|---|"]
    res = {}
    for fam in ["(none)"] + sorted(set(FAMILY.values())):
        u = units if fam == "(none)" else units[(units.policy.map(FAMILY) != fam) & (units.monitor.map(FAMILY) != fam)]
        if u.empty or u.same_model.nunique() < 2:
            continue
        g = glm_fit(u)
        b = task_bootstrap(u, args.boots)
        def fmt(term):
            if term in g and "ci95" in g[term]:
                return f"{g[term]['coef']:+.2f} [{g[term]['ci95'][0]:+.2f}, {g[term]['ci95'][1]:+.2f}]"
            if "lpm" in g and term in g["lpm"]:
                r = g["lpm"][term]
                return f"LPM {r['coef']:+.3f} [{r['ci95'][0]:+.3f}, {r['ci95'][1]:+.3f}]"
            return "—"
        res[fam] = {"n": int(len(u)), "glm": {k: v for k, v in g.items() if k != "summary"}, "bootstrap": b}
        lines.append(f"| {fam} | {len(u)} | {fmt('same_model')} | {fmt('same_family_diff_model')} | {b['same_model']['rate']:.3f} | "
                     f"{b['cross_family']['rate']:.3f} | {b['diag_minus_cross']['value']:+.3f} [{b['diag_minus_cross']['ci95'][0]:+.3f}, {b['diag_minus_cross']['ci95'][1]:+.3f}] |")
    # drop-one-monitor (diagonal cell) sensitivity
    lines += ["", "## Drop-one-diagonal-cell sensitivity (remove one monitor's own-model units only)", "",
              "| removed diagonal cell | same_model log-odds [95% CI] | diag − cross [95% CI] |", "|---|---|---|"]
    for m in [x for x in MODEL_ORDER if x in set(units.monitor)]:
        u = units[~((units.policy == m) & (units.monitor == m))]
        g = glm_fit(u)
        b = task_bootstrap(u, args.boots // 2)
        t = g.get("same_model", {})
        s = f"{t['coef']:+.2f} [{t['ci95'][0]:+.2f}, {t['ci95'][1]:+.2f}]" if "ci95" in t else "—"
        lines.append(f"| {m}→{m} | {s} | {b['diag_minus_cross']['value']:+.3f} [{b['diag_minus_cross']['ci95'][0]:+.3f}, {b['diag_minus_cross']['ci95'][1]:+.3f}] |")
    (out / "robustness.md").write_text("\n".join(lines) + "\n")
    (out / "robustness.json").write_text(json.dumps(res, indent=2, default=float))
    print("\n".join(lines))
    print(f"\n[written] {out}/robustness.md, leniency_by_monitor.csv, leniency_by_policy.csv")


if __name__ == "__main__":
    main()
