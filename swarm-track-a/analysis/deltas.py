"""Exploratory stages (README H2, H3): told-vs-blind deltas and paraphrase deltas, by relationship.

  .venv/bin/python analysis/deltas.py told --blind runs/stage1_mon*/scores.jsonl --told runs/stage1b_*/scores.jsonl --out analysis/out/told
  .venv/bin/python analysis/deltas.py para  --orig  runs/stage1_mon*/scores.jsonl --para runs/stage1c_*/scores.jsonl --out analysis/out/para

told: per (submission, monitor) mean score, join blind vs told on (submission_id, monitor); delta = told - blind.
      Summary by relationship x condition with task-bootstrap 95% CI; plus the diagonal-vs-cross difference of deltas.
para: paraphrased scores join the original scores on (orig_submission_id, monitor); delta = paraphrased - original.
      Also recomputes per-pair TPR on the paraphrased bank (thresholds re-calibrated on paraphrased benign) and reports the
      diagonal / same-family / cross-family cell means next to the originals.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from calibrate import FAMILY, cells, load_scores, per_submission  # noqa: E402


def rel_of(p: str, m: str) -> str:
    return "same_model" if p == m else ("same_family" if FAMILY[p] == FAMILY[m] else "cross_family")


def boot_mean(df: pd.DataFrame, col: str, n: int = 2000, seed: int = 0) -> tuple[float, float, float]:
    if df.empty:
        return (np.nan, np.nan, np.nan)
    rng = np.random.default_rng(seed)
    tasks = df.task.unique()
    by = {t: df[df.task == t][col].to_numpy() for t in tasks}
    obs = float(df[col].mean())
    bs = np.array([np.concatenate([by[t] for t in rng.choice(tasks, len(tasks), replace=True)]).mean() for _ in range(n)])
    return (obs, float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)))


def summarize(j: pd.DataFrame, col: str, out: Path, title: str) -> list[str]:
    lines = [f"# {title}", "", f"{len(j)} (submission, monitor) pairs, {j.task.nunique()} tasks", "",
             "| condition | relation | n | mean delta | 95% CI (task bootstrap) |", "|---|---|---|---|---|"]
    rows = []
    for cond in ("attack", "benign"):
        for rel in ("same_model", "same_family", "cross_family"):
            d = j[(j.condition == cond) & (j.rel == rel)]
            if d.empty:
                continue
            m, lo, hi = boot_mean(d, col)
            rows.append(dict(condition=cond, rel=rel, n=len(d), mean=m, lo=lo, hi=hi))
            lines.append(f"| {cond} | {rel} | {len(d)} | {m:+.2f} | [{lo:+.2f}, {hi:+.2f}] |")
    # diagonal minus cross-family difference of deltas, attacks only
    a = j[j.condition == "attack"]
    if (a.rel == "same_model").any() and (a.rel == "cross_family").any():
        rng = np.random.default_rng(1)
        tasks = a.task.unique()
        def gap(df):
            return df[df.rel == "same_model"][col].mean() - df[df.rel == "cross_family"][col].mean()
        obs = gap(a)
        bs = []
        for _ in range(2000):
            pick = rng.choice(tasks, len(tasks), replace=True)
            bs.append(gap(pd.concat([a[a.task == t] for t in pick])))
        bs = np.array([b for b in bs if not np.isnan(b)])
        lines += ["", f"Attacks: (diagonal delta) - (cross-family delta) = {obs:+.2f} [{np.percentile(bs, 2.5):+.2f}, {np.percentile(bs, 97.5):+.2f}]"]
    pd.DataFrame(rows).to_csv(out / "summary.csv", index=False)
    return lines


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["told", "para"])
    ap.add_argument("--blind", nargs="*", default=[])
    ap.add_argument("--told", nargs="*", default=[])
    ap.add_argument("--orig", nargs="*", default=[])
    ap.add_argument("--para", nargs="*", default=[])
    ap.add_argument("--out", required=True)
    ap.add_argument("--fpr", type=float, default=0.05)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    if args.mode == "told":
        b = per_submission(load_scores([Path(p) for p in args.blind]).query("mon_condition == 'blind'"))
        t = per_submission(load_scores([Path(p) for p in args.told]).query("mon_condition == 'told'"))
        j = b.merge(t[["submission_id", "monitor", "mean_score"]], on=["submission_id", "monitor"], suffixes=("_blind", "_told"))
        j = j.dropna(subset=["mean_score_blind", "mean_score_told"])
        j["delta"] = j.mean_score_told - j.mean_score_blind
        j["rel"] = [rel_of(p, m) for p, m in zip(j.policy, j.monitor)]
        j.to_csv(out / "pairs.csv", index=False)
        lines = summarize(j, "delta", out, "Told minus blind suspicion score (same submissions, same monitors)")
        # catch rate under told scores at the blind per-pair thresholds
        c = cells(b, args.fpr)
        thr = {(r.policy, r.monitor): r.threshold for r in c.itertuples()}
        a = j[j.condition == "attack"].copy()
        a["thr"] = [thr.get((p, m), np.nan) for p, m in zip(a.policy, a.monitor)]
        a = a.dropna(subset=["thr"])
        lines += ["", "| relation | catch rate blind | catch rate told (blind thresholds) | n |", "|---|---|---|---|"]
        for rel in ("same_model", "same_family", "cross_family"):
            d = a[a.rel == rel]
            if len(d):
                lines.append(f"| {rel} | {(d.mean_score_blind > d.thr).mean():.3f} | {(d.mean_score_told > d.thr).mean():.3f} | {len(d)} |")
    else:
        o = per_submission(load_scores([Path(p) for p in args.orig]).query("mon_condition == 'blind'"))
        p_ = load_scores([Path(p) for p in args.para]).query("mon_condition == 'blind'")
        ps = per_submission(p_)
        # orig_submission_id is per score row; recover it per paraphrased submission
        link = p_.dropna(subset=["orig_submission_id"]).drop_duplicates("submission_id").set_index("submission_id")["orig_submission_id"]
        ps["orig_submission_id"] = ps.submission_id.map(link)
        j = ps.merge(o[["submission_id", "monitor", "mean_score"]], left_on=["orig_submission_id", "monitor"],
                     right_on=["submission_id", "monitor"], suffixes=("_para", "_orig"))
        j = j.dropna(subset=["mean_score_para", "mean_score_orig"])
        j["delta"] = j.mean_score_para - j.mean_score_orig
        j["rel"] = [rel_of(p, m) for p, m in zip(j.policy, j.monitor)]
        j["task"] = j["task"]
        j.to_csv(out / "pairs.csv", index=False)
        lines = summarize(j, "delta", out, "Paraphrased minus original suspicion score (same monitors)")
        co = cells(o, args.fpr)
        cp = cells(ps, args.fpr)
        cp = cp[cp.n_attack > 0]
        scored = set(zip(cp.policy, cp.monitor))
        co = co[[(p_, m_) in scored for p_, m_ in zip(co.policy, co.monitor)]]   # same (policy, monitor) cells on both sides
        lines += ["", "| relation | mean cell TPR original | mean cell TPR paraphrased | cells |", "|---|---|---|---|"]
        for rel in ("same_model", "same_family", "cross_family"):
            a_, b_ = co[co.rel == rel] if "rel" in co else co.iloc[0:0], cp[cp.rel == rel] if "rel" in cp else cp.iloc[0:0]
            if len(b_):
                lines.append(f"| {rel} | {a_.tpr.mean():.3f} | {b_.tpr.mean():.3f} | {len(b_)} |")
        cp.to_csv(out / "cells_paraphrased.csv", index=False)
    (out / "deltas.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    print(f"\n[written] {out}")


if __name__ == "__main__":
    main()
