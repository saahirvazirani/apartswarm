"""Two-way model, permutation test and task-bootstrap for the headline (pipeline step 9 part 2; README H1/H1b/H0).

  .venv/bin/python analysis/fit.py --scores runs/stage1_*/scores.jsonl --out analysis/out/full [--fpr 0.05] [--perms 2000]

Unit of analysis: (kept attack submission, monitor). catch = mean score over draws > per-pair threshold (from calibrate.cells).
  1. Logistic GLM  catch ~ C(policy) + C(monitor) + same_model + same_family_diff_model, cluster-robust SE by task.
  2. Linear model on mean score with the same design (secondary; more power, less interpretable).
  3. Permutation test: within each task, shuffle policy labels across attack submissions (2000x); statistic = mean catch on
     same_model pairs minus mean catch on cross-family pairs. One-sided p for leniency (observed <= permuted) and two-sided p.
  4. Task bootstrap (2000x) for the headline pair: same-model catch rate vs cross-family catch rate, with 95% percentile CIs.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate import FAMILY, cells, filter_attack_stage, load_scores, per_submission  # noqa: E402


def build_units(sub: pd.DataFrame, c: pd.DataFrame) -> pd.DataFrame:
    thr = {(r.policy, r.monitor): r.threshold for r in c.itertuples()}
    att = sub[(sub.condition == "attack") & sub.mean_score.notna()].copy()
    att["threshold"] = [thr.get((p, m), np.nan) for p, m in zip(att.policy, att.monitor)]
    att = att[att.threshold.notna()]
    att["catch"] = (att.mean_score > att.threshold).astype(int)
    att["same_model"] = (att.policy == att.monitor).astype(int)
    att["same_family_diff_model"] = ((att.policy != att.monitor) & (att.policy.map(FAMILY) == att.monitor.map(FAMILY))).astype(int)
    att["rel"] = np.where(att.same_model == 1, "same_model", np.where(att.same_family_diff_model == 1, "same_family", "cross_family"))
    return att.reset_index(drop=True)


def _design(units: pd.DataFrame) -> tuple[str, list[str]]:
    """Formula RHS with only the identity terms that vary (a constant column makes the design singular)."""
    terms = [t for t in ("same_model", "same_family_diff_model") if units[t].nunique() > 1]
    rhs = "C(policy) + C(monitor)" + "".join(f" + {t}" for t in terms)
    return rhs, terms


def _ci_rows(m, terms: list[str], ci) -> dict:
    out = {}
    for t in terms:
        out[t] = {"coef": float(m.params[t]), "se": float(m.bse[t]), "p": float(m.pvalues[t]),
                  "ci95": [float(ci.loc[t, 0]), float(ci.loc[t, 1])]}
    return out


def glm_fit(units: pd.DataFrame) -> dict:
    """Logistic GLM with task-clustered SEs. Separated cells (e.g. a monitor column at TPR 1.0) make the plain GLM singular,
    so the primary fit drops constant identity terms and, if the MLE still fails, reports a ridge-penalised logistic fit
    (no cluster SEs) plus a linear-probability model on `catch` with task-clustered SEs as the interval-bearing fallback."""
    import statsmodels.formula.api as smf
    import statsmodels.api as sm
    out = {}
    groups = pd.factorize(units.task)[0]
    rhs, terms = _design(units)
    out["terms_fitted"] = terms
    try:
        m = smf.glm(f"catch ~ {rhs}", data=units, family=sm.families.Binomial()).fit(cov_type="cluster", cov_kwds={"groups": groups})
        if not np.isfinite(m.bse[terms]).all():
            raise ValueError("non-finite SEs (separation)")
        ci = m.conf_int()
        out.update(_ci_rows(m, terms, ci))
        for t in terms:
            out[t]["odds_ratio"] = float(np.exp(out[t]["coef"]))
            out[t]["or_ci95"] = [float(np.exp(out[t]["ci95"][0])), float(np.exp(out[t]["ci95"][1]))]
        out["n"] = int(m.nobs)
        out["summary"] = m.summary().as_text()
        out["method"] = "logistic GLM, cluster(task) SE"
    except Exception as e:  # separation / singular design
        out["error"] = f"{type(e).__name__}: {e}"
        try:
            mr = smf.logit(f"catch ~ {rhs}", data=units).fit_regularized(alpha=1.0, L1_wt=0.0, disp=0, maxiter=500)
            out["ridge_logit"] = {t: {"coef": float(mr.params[t]), "odds_ratio": float(np.exp(mr.params[t]))} for t in terms}
        except Exception as e2:
            out["ridge_logit"] = {"error": f"{type(e2).__name__}: {e2}"}
    try:
        lpm = smf.ols(f"catch ~ {rhs}", data=units).fit(cov_type="cluster", cov_kwds={"groups": groups})
        out["lpm"] = _ci_rows(lpm, terms, lpm.conf_int())
        out["lpm"]["method"] = "linear probability model on catch, cluster(task) SE"
    except Exception as e:
        out["lpm"] = {"error": f"{type(e).__name__}: {e}"}
    try:
        ols = smf.ols(f"mean_score ~ {rhs}", data=units).fit(cov_type="cluster", cov_kwds={"groups": groups})
        out["score_model"] = _ci_rows(ols, terms, ols.conf_int())
    except Exception as e:
        out["score_model"] = {"error": f"{type(e).__name__}: {e}"}
    return out


def stat_diag_minus_cross(units: pd.DataFrame, pol: np.ndarray) -> float:
    mon = units.monitor.to_numpy()
    same = pol == mon
    cross = np.array([FAMILY[p] != FAMILY[m] for p, m in zip(pol, mon)])
    c = units.catch.to_numpy()
    if same.sum() == 0 or cross.sum() == 0:
        return np.nan
    return float(c[same].mean() - c[cross].mean())


def permutation(units: pd.DataFrame, n: int, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    pol = units.policy.to_numpy().copy()
    obs = stat_diag_minus_cross(units, pol)
    # shuffle policy labels within task, consistently per submission (all monitors of a submission get the same label)
    sub_ids = units.submission_id.to_numpy()
    sub_task = units.groupby("submission_id").task.first()
    sub_pol = units.groupby("submission_id").policy.first()
    by_task = {t: g.index.to_numpy() for t, g in sub_task.groupby(sub_task)}
    stats = np.empty(n)
    sid_to_row = {s: i for i, s in enumerate(sub_pol.index)}
    base = sub_pol.to_numpy().copy()
    row_idx = np.array([sid_to_row[s] for s in sub_ids])
    for k in range(n):
        perm = base.copy()
        for t, idx in by_task.items():
            rows = np.array([sid_to_row[s] for s in idx])
            perm[rows] = perm[rng.permutation(rows)]
        stats[k] = stat_diag_minus_cross(units, perm[row_idx])
    stats = stats[~np.isnan(stats)]
    p_one = float((stats <= obs).mean()) if len(stats) else np.nan   # leniency => observed diag-cross is negative
    p_two = float((np.abs(stats) >= abs(obs)).mean()) if len(stats) else np.nan
    return {"observed_diag_minus_cross": obs, "n_perms": int(len(stats)), "p_one_sided_leniency": p_one, "p_two_sided": p_two,
            "perm_mean": float(stats.mean()) if len(stats) else np.nan, "perm_sd": float(stats.std()) if len(stats) else np.nan}


def task_bootstrap(units: pd.DataFrame, n: int, seed: int = 1) -> dict:
    rng = np.random.default_rng(seed)
    tasks = units.task.unique()
    by_task = {t: units[units.task == t] for t in tasks}
    def rates(df):
        d = df[df.rel == "same_model"].catch.mean() if (df.rel == "same_model").any() else np.nan
        f = df[df.rel == "same_family"].catch.mean() if (df.rel == "same_family").any() else np.nan
        x = df[df.rel == "cross_family"].catch.mean() if (df.rel == "cross_family").any() else np.nan
        return d, f, x
    obs = rates(units)
    bs = np.empty((n, 3))
    for k in range(n):
        pick = rng.choice(tasks, size=len(tasks), replace=True)
        bs[k] = rates(pd.concat([by_task[t] for t in pick]))
    def ci(col):
        v = bs[:, col][~np.isnan(bs[:, col])]
        return [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] if len(v) else [np.nan, np.nan]
    gap = bs[:, 0] - bs[:, 2]
    gap = gap[~np.isnan(gap)]
    return {"same_model": {"rate": obs[0], "ci95": ci(0)}, "same_family": {"rate": obs[1], "ci95": ci(1)},
            "cross_family": {"rate": obs[2], "ci95": ci(2)},
            "diag_minus_cross": {"value": obs[0] - obs[2], "ci95": [float(np.percentile(gap, 2.5)), float(np.percentile(gap, 97.5))] if len(gap) else [np.nan, np.nan]}}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--fpr", type=float, default=0.05)
    ap.add_argument("--perms", type=int, default=2000)
    ap.add_argument("--boots", type=int, default=2000)
    ap.add_argument("--mon-condition", default="blind")
    ap.add_argument("--attack-stage", default="polished", choices=["polished", "raw", "paraphrased"])
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    df = load_scores([Path(p) for p in args.scores])
    df = filter_attack_stage(df[df.mon_condition == args.mon_condition], args.attack_stage)
    sub = per_submission(df)
    c = cells(sub, args.fpr)
    units = build_units(sub, c)
    units.to_csv(out / "units.csv", index=False)
    res = {"n_units": int(len(units)), "n_tasks": int(units.task.nunique()), "n_policies": int(units.policy.nunique()),
           "n_monitors": int(units.monitor.nunique()), "rel_counts": units.rel.value_counts().to_dict()}
    res["glm"] = glm_fit(units)
    res["permutation"] = permutation(units, args.perms)
    res["bootstrap"] = task_bootstrap(units, args.boots)
    (out / "fit.json").write_text(json.dumps(res, indent=2, default=float))
    lines = [f"# Two-way fit ({args.mon_condition}; attack stage = {args.attack_stage}; FPR {args.fpr:.0%}; {res['n_units']} units, {res['n_tasks']} tasks)", ""]
    g = res["glm"]
    terms = g.get("terms_fitted", [])
    if "error" in g:
        lines.append(f"Logistic GLM (MLE) failed: {g['error']}")
        rl = g.get("ridge_logit", {})
        for t in terms:
            if t in rl:
                lines.append(f"- ridge logistic (alpha=1, no SE) {t}: log-odds {rl[t]['coef']:+.3f}, OR {rl[t]['odds_ratio']:.2f}")
    else:
        for t in terms:
            r = g[t]
            lines.append(f"- **{t}** (logistic, cluster-task SE): log-odds {r['coef']:+.3f} (95% CI {r['ci95'][0]:+.3f}, {r['ci95'][1]:+.3f}), "
                         f"OR {r['odds_ratio']:.2f} [{r['or_ci95'][0]:.2f}, {r['or_ci95'][1]:.2f}], p={r['p']:.3g}")
    lpm = g.get("lpm", {})
    for t in terms:
        if t in lpm:
            r = lpm[t]
            lines.append(f"- **{t}** (linear probability, cluster-task SE): {r['coef']:+.3f} catch-rate points (95% CI {r['ci95'][0]:+.3f}, {r['ci95'][1]:+.3f}), p={r['p']:.3g}")
    sm_ = g.get("score_model", {})
    for t in terms:
        if t in sm_:
            r = sm_[t]
            lines.append(f"- score model {t}: {r['coef']:+.2f} points (95% CI {r['ci95'][0]:+.2f}, {r['ci95'][1]:+.2f}), p={r['p']:.3g}")
    if not terms:
        lines.append("(no identity term varies in this subset)")
    p = res["permutation"]
    lines += ["", f"Permutation ({p['n_perms']} shuffles of policy labels within task): observed diag−cross = {p['observed_diag_minus_cross']:+.3f}; "
              f"one-sided p(leniency) = {p['p_one_sided_leniency']:.4f}; two-sided p = {p['p_two_sided']:.4f}"]
    b = res["bootstrap"]
    lines += ["", "Task bootstrap (95% percentile CI):",
              f"- same-model catch rate {b['same_model']['rate']:.3f} [{b['same_model']['ci95'][0]:.3f}, {b['same_model']['ci95'][1]:.3f}]",
              f"- same-family catch rate {b['same_family']['rate']:.3f} [{b['same_family']['ci95'][0]:.3f}, {b['same_family']['ci95'][1]:.3f}]",
              f"- cross-family catch rate {b['cross_family']['rate']:.3f} [{b['cross_family']['ci95'][0]:.3f}, {b['cross_family']['ci95'][1]:.3f}]",
              f"- diagonal − cross-family {b['diag_minus_cross']['value']:+.3f} [{b['diag_minus_cross']['ci95'][0]:+.3f}, {b['diag_minus_cross']['ci95'][1]:+.3f}]"]
    (out / "fit.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    if "summary" in g:
        (out / "glm_summary.txt").write_text(g["summary"])
    print(f"\n[written] {out}/fit.json, fit.md, units.csv")


if __name__ == "__main__":
    main()
