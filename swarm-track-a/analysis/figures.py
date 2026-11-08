"""Figure 1: 7x7 catch-rate matrix + diagonal / same-family / cross-family bars with task-bootstrap CIs.

  .venv/bin/python analysis/figures.py --cells analysis/out/full/cells.csv --fit analysis/out/full/fit.json --out analysis/out/full/fig1.png

Reads only the outputs of calibrate.py and fit.py so that every number in the figure reproduces from runs/ via `make recompute`.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

MODEL_ORDER = ["deepseek-v4-flash", "gemma-4-26b-a4b-it", "gemma-4-31b-it", "qwen3.8-27b", "qwen3.5-397b", "glm-53-flash", "glm-5.2"]
SHORT = {"deepseek-v4-flash": "deepseek-v4-flash", "gemma-4-26b-a4b-it": "gemma-4-26b", "gemma-4-31b-it": "gemma-4-31b",
         "qwen3.8-27b": "qwen3.8-27b", "qwen3.5-397b": "qwen3.5-397b", "glm-53-flash": "glm-53-flash", "glm-5.2": "glm-5.2"}
FAMILY = {"deepseek-v4-flash": "deepseek", "gemma-4-26b-a4b-it": "gemma", "gemma-4-31b-it": "gemma", "qwen3.8-27b": "qwen",
          "qwen3.5-397b": "qwen", "glm-53-flash": "glm", "glm-5.2": "glm"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cells", required=True)
    ap.add_argument("--fit", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--value", default="tpr", choices=["tpr", "auroc"])
    ap.add_argument("--title", default="")
    args = ap.parse_args()
    c = pd.read_csv(args.cells)
    fit = json.loads(Path(args.fit).read_text())
    pols = [m for m in MODEL_ORDER if m in set(c.policy)]
    mons = [m for m in MODEL_ORDER if m in set(c.monitor)]
    M = np.full((len(pols), len(mons)), np.nan)
    for i, p in enumerate(pols):
        for j, m in enumerate(mons):
            r = c[(c.policy == p) & (c.monitor == m)]
            if not r.empty:
                M[i, j] = r.iloc[0][args.value]

    fig, (ax, bx) = plt.subplots(1, 2, figsize=(13, 5.6), gridspec_kw={"width_ratios": [1.6, 1]})
    im = ax.imshow(M, vmin=0, vmax=1, cmap="viridis")
    ax.set_xticks(range(len(mons)), [SHORT[m] for m in mons], rotation=35, ha="right", fontsize=9)
    ax.set_yticks(range(len(pols)), [SHORT[p] for p in pols], fontsize=9)
    ax.set_xlabel("monitor model")
    ax.set_ylabel("policy model (author of the submission)")
    for i, p in enumerate(pols):
        for j, m in enumerate(mons):
            r = c[(c.policy == p) & (c.monitor == m)]
            if r.empty or np.isnan(M[i, j]):
                continue
            r = r.iloc[0]
            txt = f"{M[i, j]:.2f}"
            if args.value == "tpr":
                txt += f"\n[{r.tpr_lo:.2f},{r.tpr_hi:.2f}]"
            ax.text(j, i, txt, ha="center", va="center", fontsize=7.5, color="white" if M[i, j] < 0.6 else "black",
                    fontweight="bold" if p == m else "normal")
            if p == m:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor="red", lw=2.2))
            elif FAMILY[p] == FAMILY[m]:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor="orange", lw=1.4, ls="--"))
    cb = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.02)
    cb.set_label("TPR at per-pair 5% FPR" if args.value == "tpr" else "AUROC")
    ax.set_title("(a) catch rate; red = same model, dashed orange = same family", fontsize=10)

    b = fit.get("bootstrap", {})
    labels, vals, los, his = [], [], [], []
    for key, lab in [("same_model", "same model\n(diagonal)"), ("same_family", "same family,\ndifferent model"), ("cross_family", "cross-family")]:
        d = b.get(key, {})
        if d and d.get("rate") is not None and not (isinstance(d["rate"], float) and np.isnan(d["rate"])):
            labels.append(lab); vals.append(d["rate"]); los.append(d["ci95"][0]); his.append(d["ci95"][1])
    x = np.arange(len(labels))
    colors = ["#c0392b", "#e67e22", "#2980b9"][: len(labels)]
    bx.bar(x, vals, color=colors, alpha=0.85)
    bx.errorbar(x, vals, yerr=[np.array(vals) - np.array(los), np.array(his) - np.array(vals)], fmt="none", ecolor="black", capsize=5, lw=1.4)
    for xi, v in zip(x, vals):
        bx.text(xi, v + 0.02, f"{v:.2f}", ha="center", fontsize=9)
    bx.set_xticks(x, labels, fontsize=9)
    bx.set_ylim(0, 1.05)
    bx.set_ylabel("catch rate (pooled over cells)")
    g = fit.get("glm", {}).get("same_model", {})
    perm = fit.get("permutation", {})
    sub = ""
    if g:
        sub += f"same_model log-odds {g['coef']:+.2f} [{g['ci95'][0]:+.2f}, {g['ci95'][1]:+.2f}]"
    if perm:
        sub += f"\npermutation p (one-sided leniency) = {perm.get('p_one_sided_leniency', float('nan')):.3f}"
    bx.set_title("(b) pooled catch rate, task-bootstrap 95% CI\n" + sub, fontsize=9)
    if args.title:
        fig.suptitle(args.title, fontsize=11)
    fig.tight_layout()
    fig.savefig(args.out, dpi=170)
    print(f"[written] {args.out}")


if __name__ == "__main__":
    main()
