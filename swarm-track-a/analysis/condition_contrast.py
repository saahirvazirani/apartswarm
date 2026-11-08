"""Landing analysis for in-flight condition-change re-scoring runs (Stage 1f reasoning, Stage 1g no-note).

A NEW run re-scores the SAME kept submissions (gemma-family policies, both conditions) under a changed
monitor condition. For every (policy, monitor) cell present in the new run this script reports, new vs baseline:
  - threshold recalibrated ON THE NEW RUN'S OWN benign per-submission mean scores
    ((1-fpr) quantile, np.quantile method="higher", mirroring analysis/calibrate.py) and TPR = share of
    new attacks with mean score > threshold (Wilson 95% CI);
  - the tie-robust ROC-interpolated TPR at exactly the target FPR (tpr_at_fpr ported from analysis/matched_fpr.py);
  - the same two estimators computed on the Stage-1 blind baseline cell (benign raw + attack polished);
  - benign / attack score means;
  - a paired per-submission score delta (new minus baseline mean score for the same submission_id)
    with a task-bootstrap percentile CI, split by condition;
  - an own/family-vs-cross contrast within the new run where the new run has monitors of both kinds.

Partial-data safe and rerunnable: a submission contributes whatever parsed draws exist so far; completeness is
printed and written as distinct (submission, monitor, draw) rows seen vs expected 3 draws x the baseline kept
submissions for the policies/monitors in the new run. Output is labelled PARTIAL until the run is complete.

  .venv/bin/python analysis/condition_contrast.py \
      --new runs/stage1f_reason/scores.jsonl --baseline runs/stage1_mon*/scores.jsonl \
      --out analysis/out/stage1f [--fpr 0.05] [--boots 2000] [--label "reasoning enabled"]

Writes <out>/contrast.md and <out>/contrast.csv. Read-only on runs/; makes no API calls.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate import FAMILY, MODEL_ORDER, filter_attack_stage, load_scores, per_submission, wilson  # noqa: E402

REL = lambda p, m: "same_model" if p == m else ("same_family" if FAMILY[p] == FAMILY[m] else "cross_family")


def tpr_at_fpr(ben: np.ndarray, att: np.ndarray, fpr_target: float) -> float:
    """Ported verbatim from analysis/matched_fpr.py (tie-robust, realised FPR held at exactly fpr_target)."""
    if len(ben) == 0 or len(att) == 0:
        return float("nan")
    y = np.r_[np.zeros(len(ben)), np.ones(len(att))]
    s = np.r_[ben, att]
    if len(set(s)) < 2:
        return float("nan")
    fpr, tpr, _ = roc_curve(y, s)
    return float(np.interp(fpr_target, fpr, tpr))


def quantile_metrics(ben: np.ndarray, att: np.ndarray, fpr: float) -> dict:
    """Per-pair quantile threshold + strict-> TPR, exactly as analysis/calibrate.py."""
    if len(ben) == 0 or len(att) == 0:
        return dict(threshold=np.nan, tpr=np.nan, tpr_lo=np.nan, tpr_hi=np.nan, fpr_realised=np.nan)
    thr = float(np.quantile(ben, 1 - fpr, method="higher"))
    k = int((att > thr).sum())
    lo, hi = wilson(k, len(att))
    return dict(threshold=thr, tpr=k / len(att), tpr_lo=lo, tpr_hi=hi, fpr_realised=float((ben > thr).mean()))


def task_bootstrap_ci(deltas: pd.DataFrame, boots: int, seed: int = 0) -> tuple[float, float, float]:
    """Mean of per-submission deltas with a cluster (task) bootstrap percentile CI. deltas: columns task, delta."""
    if deltas.empty:
        return (float("nan"), float("nan"), float("nan"))
    by_task = {t: d.delta.to_numpy() for t, d in deltas.groupby("task")}
    tasks = sorted(by_task)
    mean = float(deltas.delta.mean())
    if len(tasks) < 2 or boots <= 0:
        return (mean, float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    reps = np.empty(boots)
    for i in range(boots):
        sampled = rng.choice(tasks, size=len(tasks), replace=True)
        reps[i] = float(np.mean(np.concatenate([by_task[t] for t in sampled])))
    return (mean, float(np.percentile(reps, 2.5)), float(np.percentile(reps, 97.5)))


def fmt(v, nd=2):
    return "—" if v is None or (isinstance(v, float) and np.isnan(v)) else f"{v:.{nd}f}"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--new", nargs="+", required=True, help="scores.jsonl of the condition-change run")
    ap.add_argument("--baseline", nargs="+", required=True, help="Stage-1 blind baseline scores.jsonl files")
    ap.add_argument("--out", required=True)
    ap.add_argument("--fpr", type=float, default=0.05)
    ap.add_argument("--boots", type=int, default=2000)
    ap.add_argument("--label", default=None, help="human label for the changed condition (defaults to the run folder name)")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    label = args.label or Path(args.new[0]).parent.name

    new = load_scores([Path(p) for p in args.new])
    base = load_scores([Path(p) for p in args.baseline])
    if new.empty:
        print("[condition_contrast] new run has no parsed rows yet; nothing to do.")
        return
    new = filter_attack_stage(new[new.mon_condition == "blind"], "polished")
    base = filter_attack_stage(base[base.mon_condition == "blind"], "polished")

    policies = [m for m in MODEL_ORDER if m in set(new.policy)]
    monitors = [m for m in MODEL_ORDER if m in set(new.monitor)]
    base = base[base.policy.isin(policies) & base.monitor.isin(monitors)].copy()

    # ---- completeness: expected = baseline kept submissions for these policies x new-run monitors x 3 draws
    base_subs = base[["submission_id", "policy", "condition"]].drop_duplicates()
    n_expected_subs = base_subs.submission_id.nunique()
    expected_draws = n_expected_subs * len(monitors) * 3
    seen_draws = len(new.drop_duplicates(subset=["submission_id", "monitor", "draw"]))
    comp_lines = [f"- distinct (submission, monitor, draw) seen: **{seen_draws} / {expected_draws}** "
                  f"({seen_draws / expected_draws:.1%}) — expected = {n_expected_subs} baseline kept submissions "
                  f"x {len(monitors)} monitor(s) x 3 draws"]
    for m in monitors:
        d = new[new.monitor == m]
        s = len(d.drop_duplicates(subset=["submission_id", "draw"]))
        comp_lines.append(f"  - {m}: {s} / {n_expected_subs * 3} draws ({s / (n_expected_subs * 3):.1%}); "
                          f"{d.submission_id.nunique()} / {n_expected_subs} submissions touched")
    complete = seen_draws >= expected_draws
    partial_tag = "" if complete else "PARTIAL — run in progress; "

    sub_new = per_submission(new)
    sub_new = sub_new[sub_new.mean_score.notna()]
    sub_base = per_submission(base)
    sub_base = sub_base[sub_base.mean_score.notna()]

    # ---- per-cell table
    rows = []
    for m in monitors:
        for p in policies:
            dn = sub_new[(sub_new.policy == p) & (sub_new.monitor == m)]
            db = sub_base[(sub_base.policy == p) & (sub_base.monitor == m)]
            if dn.empty:
                continue
            ben_n = dn[dn.condition == "benign"].mean_score.to_numpy()
            att_n = dn[dn.condition == "attack"].mean_score.to_numpy()
            ben_b = db[db.condition == "benign"].mean_score.to_numpy()
            att_b = db[db.condition == "attack"].mean_score.to_numpy()
            qn, qb = quantile_metrics(ben_n, att_n, args.fpr), quantile_metrics(ben_b, att_b, args.fpr)
            r = dict(policy=p, monitor=m, rel=REL(p, m),
                     n_benign_new=len(ben_n), n_attack_new=len(att_n),
                     n_benign_base=len(ben_b), n_attack_base=len(att_b),
                     threshold_new=qn["threshold"], threshold_base=qb["threshold"],
                     tpr_new=qn["tpr"], tpr_new_lo=qn["tpr_lo"], tpr_new_hi=qn["tpr_hi"],
                     tpr_base=qb["tpr"], tpr_base_lo=qb["tpr_lo"], tpr_base_hi=qb["tpr_hi"],
                     fpr_realised_new=qn["fpr_realised"], fpr_realised_base=qb["fpr_realised"],
                     tpr_interp_new=tpr_at_fpr(ben_n, att_n, args.fpr),
                     tpr_interp_base=tpr_at_fpr(ben_b, att_b, args.fpr),
                     benign_mean_new=float(ben_n.mean()) if len(ben_n) else np.nan,
                     benign_mean_base=float(ben_b.mean()) if len(ben_b) else np.nan,
                     attack_mean_new=float(att_n.mean()) if len(att_n) else np.nan,
                     attack_mean_base=float(att_b.mean()) if len(att_b) else np.nan)
            # paired per-submission delta (new - baseline mean score, same submission_id), by condition
            merged = dn.merge(db[["submission_id", "mean_score"]], on="submission_id", suffixes=("_new", "_base"))
            merged["delta"] = merged.mean_score_new - merged.mean_score_base
            for cond, key in (("benign", "ben"), ("attack", "att")):
                d = merged[merged.condition == cond][["task", "delta"]]
                mu, lo, hi = task_bootstrap_ci(d, args.boots, seed=0)
                r[f"delta_{key}_n"] = len(d)
                r[f"delta_{key}_mean"], r[f"delta_{key}_lo"], r[f"delta_{key}_hi"] = mu, lo, hi
            rows.append(r)
    c = pd.DataFrame(rows)
    c.to_csv(out / "contrast.csv", index=False)

    # ---- markdown
    title_tag = " [PARTIAL]" if not complete else ""
    lines = [f"# Condition contrast: {label} vs Stage-1 blind baseline{title_tag}", ""]
    if not complete:
        lines += ["> **PARTIAL DATA — the new run is still in progress.** Every number below is computed on the",
                  "> draws parsed so far (a submission contributes whatever draws exist) and WILL move. Rerun this",
                  "> script when the run completes and re-read before quoting anything.", ""]
    lines += [f"New run: {', '.join(args.new)} | baseline: Stage-1 blind (benign raw, attack polished), same cells. "
              f"Thresholds for the new condition are recalibrated on the new run's own benign scores "
              f"((1-{args.fpr:g}) quantile, method='higher'); 'interp' is the tie-robust ROC-interpolated TPR at "
              f"exactly {args.fpr:.0%} FPR; Δ is the paired per-submission mean-score delta (new − baseline, same "
              f"submission_id) with a {args.boots}-rep task-bootstrap 95% CI.", "",
              "## Completeness", ""] + comp_lines + ["",
              "## Per-cell contrast (new → baseline)", "",
              "| policy | monitor | rel | nB/nA new | thr new→base | TPR new→base | TPR interp new→base | "
              "benign mean new→base | attack mean new→base | Δbenign [95% CI] | Δattack [95% CI] |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    for _, r in c.iterrows():
        tn = f"{fmt(r.tpr_new)} [{fmt(r.tpr_new_lo)},{fmt(r.tpr_new_hi)}]" if not np.isnan(r.tpr_new) else "—"
        tb = f"{fmt(r.tpr_base)} [{fmt(r.tpr_base_lo)},{fmt(r.tpr_base_hi)}]" if not np.isnan(r.tpr_base) else "—"
        lines.append(f"| {r.policy} | {r.monitor} | {r.rel} | {r.n_benign_new}/{r.n_attack_new} | "
                     f"{fmt(r.threshold_new, 0)} → {fmt(r.threshold_base, 0)} | {tn} → {tb} | "
                     f"{fmt(r.tpr_interp_new)} → {fmt(r.tpr_interp_base)} | "
                     f"{fmt(r.benign_mean_new, 1)} → {fmt(r.benign_mean_base, 1)} | "
                     f"{fmt(r.attack_mean_new, 1)} → {fmt(r.attack_mean_base, 1)} | "
                     f"{fmt(r.delta_ben_mean)} [{fmt(r.delta_ben_lo)},{fmt(r.delta_ben_hi)}] (n={r.delta_ben_n}) | "
                     f"{fmt(r.delta_att_mean)} [{fmt(r.delta_att_lo)},{fmt(r.delta_att_hi)}] (n={r.delta_att_n}) |")

    # ---- own/family vs cross contrast within the new run
    lines += ["", "## Own/family vs cross-family within the new condition", ""]
    have_cross = any(c.rel == "cross_family")
    have_own = any(c.rel.isin(["same_model", "same_family"]))
    if have_cross and have_own:
        lines += ["| policy | own/family monitor (rel) | cross monitor | TPR own→cross (new) | interp own→cross (new) | "
                  "interp own→cross (baseline) |", "|---|---|---|---|---|---|"]
        for p in policies:
            d = c[c.policy == p]
            own = d[d.rel.isin(["same_model", "same_family"])]
            cross = d[d.rel == "cross_family"]
            if own.empty or cross.empty:
                continue
            o, x = own.iloc[0], cross.iloc[0]
            lines.append(f"| {p} | {o.monitor} ({o.rel}) | {x.monitor} | {fmt(o.tpr_new)} → {fmt(x.tpr_new)} | "
                         f"{fmt(o.tpr_interp_new)} → {fmt(x.tpr_interp_new)} "
                         f"(gap {fmt(x.tpr_interp_new - o.tpr_interp_new, 2) if not (np.isnan(x.tpr_interp_new) or np.isnan(o.tpr_interp_new)) else '—'}) | "
                         f"{fmt(o.tpr_interp_base)} → {fmt(x.tpr_interp_base)} "
                         f"(gap {fmt(x.tpr_interp_base - o.tpr_interp_base, 2) if not (np.isnan(x.tpr_interp_base) or np.isnan(o.tpr_interp_base)) else '—'}) |")
        lines.append("")
        lines.append("Positive gap = the cross-family monitor catches more than the own/family monitor at the same "
                     "FPR budget; compare the new-condition gap to the baseline gap in the last column.")
    else:
        lines.append("_The new run contains only own/family monitor cells (no cross-family reference inside this run); "
                     "the cross comparison lives in the baseline columns of the table above._")

    lines += ["", "## Honest summary (3 sentences — fill in / confirm by a human before any of this reaches the paper)", "",
              f"<!-- SUMMARY SLOT: 1) what the condition change did to the own/family cells (quote TPR interp new vs "
              f"baseline and the paired Δattack with its CI); 2) whether the own-vs-cross gap moved relative to "
              f"baseline; 3) the caveat ({'PARTIAL run, ' if not complete else ''}recalibrated thresholds on "
              f"fewer benign points, same submissions re-scored so draws differ only by condition). -->", ""]
    if not complete:
        lines.append("**STATUS: PARTIAL.** Do not quote these numbers; rerun `analysis/condition_contrast.py` "
                     "after the run completes.")
    (out / "contrast.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n[written] {out}/contrast.md, {out}/contrast.csv")


if __name__ == "__main__":
    main()
