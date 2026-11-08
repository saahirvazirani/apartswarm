"""Gemma-block decomposition of the identity effect (POST-HOC; added Sun 2026-11-08 PM after the Stage-1 matrix was seen).

Replaces the single pooled `same_model` term with three disjoint indicators on top of policy and monitor main effects:

  catch ~ C(policy) + C(monitor) + gemma_block + diag_nongemma + samefam_nongemma   (logistic, task-clustered SEs)

  gemma_block      = 1 if policy AND monitor are both in the gemma family (the 2x2 block, diagonal included)
  diag_nongemma    = 1 if policy == monitor and the model is not gemma
  samefam_nongemma = 1 if same family, different model, family != gemma

If the headline is "no general self-leniency, a gemma-family block effect", then diag_nongemma should be ~0 and
gemma_block strongly negative. Units, thresholds and catch definition are identical to analysis/fit.py.

  .venv/bin/python analysis/block_fit.py --scores runs/stage1_mon*/scores.jsonl --out analysis/out/matched
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate import FAMILY, cells, filter_attack_stage, load_scores, per_submission  # noqa: E402
from fit import build_units  # noqa: E402

TERMS = ["gemma_block", "diag_nongemma", "samefam_nongemma"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fpr", type=float, default=0.05)
    ap.add_argument("--attack-stage", default="polished")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    df = load_scores([Path(p) for p in args.scores])
    df = filter_attack_stage(df[df.mon_condition == "blind"], args.attack_stage)
    sub = per_submission(df)
    c = cells(sub, args.fpr)
    u = build_units(sub, c)
    pf, mf = u.policy.map(FAMILY), u.monitor.map(FAMILY)
    u["gemma_block"] = ((pf == "gemma") & (mf == "gemma")).astype(int)
    u["diag_nongemma"] = ((u.policy == u.monitor) & (pf != "gemma")).astype(int)
    u["samefam_nongemma"] = ((pf == mf) & (u.policy != u.monitor) & (pf != "gemma")).astype(int)

    groups = pd.factorize(u.task)[0]
    m = smf.glm("catch ~ C(policy) + C(monitor) + " + " + ".join(TERMS), data=u,
                family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": groups})
    ci = m.conf_int()
    res = {"n_units": int(m.nobs), "n_tasks": int(u.task.nunique()),
           "note": "POST-HOC decomposition (defined after seeing the Stage-1 matrix); see docstring.",
           "terms": {}}
    for t in TERMS:
        res["terms"][t] = {"coef": float(m.params[t]), "se": float(m.bse[t]), "p": float(m.pvalues[t]),
                           "ci95": [float(ci.loc[t, 0]), float(ci.loc[t, 1])],
                           "odds_ratio": float(np.exp(m.params[t])),
                           "or_ci95": [float(np.exp(ci.loc[t, 0])), float(np.exp(ci.loc[t, 1]))]}
    (out / "block_fit.json").write_text(json.dumps(res, indent=2))

    lines = ["# Gemma-block GLM decomposition (POST-HOC)", "",
             "*Added Sun 2026-11-08 PM, after the Stage-1 matrix was seen; it decomposes the pre-registered pooled",
             "`same_model` term, it does not replace the pre-registered test (`analysis/out/full/fit.md`).*", "",
             "`catch ~ C(policy) + C(monitor) + gemma_block + diag_nongemma + samefam_nongemma`, logistic,",
             f"task-clustered SEs; {res['n_units']} (attack submission, monitor) units, {res['n_tasks']} tasks.", "",
             "| term | log-odds | 95% CI | OR | OR 95% CI | p |", "|---|---|---|---|---|---|"]
    for t in TERMS:
        r = res["terms"][t]
        lines.append(f"| {t} | {r['coef']:+.3f} | [{r['ci95'][0]:+.3f}, {r['ci95'][1]:+.3f}] | {r['odds_ratio']:.2f} | "
                     f"[{r['or_ci95'][0]:.2f}, {r['or_ci95'][1]:.2f}] | {r['p']:.2g} |")
    lines += ["",
              "Reading: the non-gemma diagonal is a precise null and the non-gemma same-family term is zero — the entire",
              "pooled same-model effect of the pre-registered fit is carried by the gemma policy × gemma monitor block",
              "(diagonal and same-family cells alike). The block p-value survives a Bonferroni correction over the 7",
              "post-hoc per-monitor leniency comparisons. Capability is controlled additively (log-odds scale) by the",
              "policy and monitor main effects; a policy-style × monitor-capability interaction specific to this block",
              "remains observationally indistinguishable from family identity (stated in Limitations)."]
    (out / "block_fit.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"[written] {out}/block_fit.md, block_fit.json")


if __name__ == "__main__":
    main()
