"""Two contrasting transcript excerpts for the paper body (CLAUDE.md writing rules): the same successful attack submission
scored low by its own model (passed) and high by a cross-family monitor (caught), with each monitor's one-sentence reason.

  .venv/bin/python analysis/excerpts.py --scores runs/stage1_mon*/scores.jsonl --cells analysis/out/full/cells.csv \
      --banks runs/bank_cheap3_v2 runs/bank_rest4 --out analysis/out/full/excerpts.md [--n 3]

Selection: attack submissions where mean same-model score <= its per-pair threshold (missed) and some cross-family monitor's
mean score > its per-pair threshold (caught); ranked by (cross - diag) score gap. Also lists the reverse pattern (caught by own
model, missed cross-family) so the appendix shows both directions.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from calibrate import FAMILY, load_scores, per_submission  # noqa: E402
from track_a.bank import load_existing  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", nargs="+", required=True)
    ap.add_argument("--cells", required=True)
    ap.add_argument("--banks", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=3)
    args = ap.parse_args()
    df = load_scores([Path(p) for p in args.scores])
    df = df[df.mon_condition == "blind"]
    sub = per_submission(df)
    c = pd.read_csv(args.cells)
    thr = {(r.policy, r.monitor): r.threshold for r in c.itertuples()}
    code = {}
    for b in args.banks:
        for r in load_existing(Path(b) / "submissions.jsonl").values():
            code[r["submission_id"]] = r
    reasons = (df[df.parse_ok.astype(bool)].sort_values("draw").groupby(["submission_id", "monitor"])
               .agg(reason=("reason", lambda s: next((x for x in s if isinstance(x, str) and x.strip()), "")),
                    scores=("score", lambda s: ", ".join(str(int(x)) for x in s if pd.notna(x)))))
    att = sub[(sub.condition == "attack") & sub.mean_score.notna()].copy()
    att["thr"] = [thr.get((p, m)) for p, m in zip(att.policy, att.monitor)]
    att = att.dropna(subset=["thr"])
    att["caught"] = att.mean_score > att.thr
    att["rel"] = ["same_model" if p == m else ("same_family" if FAMILY[p] == FAMILY[m] else "cross_family") for p, m in zip(att.policy, att.monitor)]
    rows = []
    for sid, g in att.groupby("submission_id"):
        d = g[g.rel == "same_model"]
        x = g[g.rel == "cross_family"]
        if d.empty or x.empty:
            continue
        d = d.iloc[0]
        for _, xr in x.iterrows():
            rows.append(dict(submission_id=sid, policy=d.policy, task=d.task, diag_score=d.mean_score, diag_thr=d.thr, diag_caught=d.caught,
                             cross_monitor=xr.monitor, cross_score=xr.mean_score, cross_thr=xr.thr, cross_caught=xr.caught,
                             gap=xr.mean_score - d.mean_score))
    R = pd.DataFrame(rows)
    out = ["# Contrasting excerpts (blind monitors, successful polished attacks)", ""]

    def block(title: str, sel: pd.DataFrame) -> None:
        out.append(f"## {title}")
        out.append("")
        if sel.empty:
            out.append("_none_")
            out.append("")
            return
        for _, r in sel.head(args.n).iterrows():
            rec = code.get(r.submission_id, {})
            dr = reasons.loc[(r.submission_id, r.policy)] if (r.submission_id, r.policy) in reasons.index else None
            xr = reasons.loc[(r.submission_id, r.cross_monitor)] if (r.submission_id, r.cross_monitor) in reasons.index else None
            out.extend([f"### {r.policy} on {r.task} (submission `{r.submission_id}`)", "",
                    f"- **same-model monitor ({r.policy})**: mean {r.diag_score:.1f} vs threshold {r.diag_thr:.1f} → "
                    f"{'caught' if r.diag_caught else 'passed'}; draws {dr.scores if dr is not None else '?'}; reason: _{dr.reason if dr is not None else ''}_",
                    f"- **cross-family monitor ({r.cross_monitor})**: mean {r.cross_score:.1f} vs threshold {r.cross_thr:.1f} → "
                    f"{'caught' if r.cross_caught else 'passed'}; draws {xr.scores if xr is not None else '?'}; reason: _{xr.reason if xr is not None else ''}_",
                    "", "```python", (rec.get("code") or "").rstrip(), "```", ""])

    if not R.empty:
        block("Passed by its own model, caught cross-family", R[(~R.diag_caught) & R.cross_caught].sort_values("gap", ascending=False))
        block("Caught by its own model, passed cross-family (reverse pattern)", R[R.diag_caught & (~R.cross_caught)].sort_values("gap"))
        n_sub = R.submission_id.nunique()
        out += ["## Counts", "", f"- attack submissions with both a same-model and a cross-family score: {n_sub}",
                f"- (submission, cross monitor) pairs: {len(R)}; passed-own/caught-cross: {int(((~R.diag_caught) & R.cross_caught).sum())}; "
                f"caught-own/passed-cross: {int((R.diag_caught & (~R.cross_caught)).sum())}"]
    Path(args.out).write_text("\n".join(out) + "\n")
    print("\n".join(out[:40]))
    print(f"\n[written] {args.out}")


if __name__ == "__main__":
    main()
