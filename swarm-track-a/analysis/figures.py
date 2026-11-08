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

# ---- shared publication style (same system as analysis/strengthen.py) ----
INK = "#1F2937"       # all text and values
MUTED = "#6B7280"     # secondary text, ticks, error bars
GRID = "#E5E7EB"
CRIMSON = "#B3324B"   # same model / diagonal
CRIMSON_DEEP = "#8E2340"
AMBER = "#C06C10"     # same family, different model
BLUE = "#2563EB"      # cross family / trusted


def apply_style() -> None:
    plt.rcParams.update({
        "savefig.dpi": 300,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": MUTED,
        "axes.linewidth": 0.8,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "xtick.labelcolor": INK,
        "ytick.labelcolor": INK,
        "grid.color": GRID,
        "grid.linewidth": 0.8,
        "axes.axisbelow": True,
        "legend.frameon": False,
        "font.size": 11,
        "text.color": INK,
    })


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

    apply_style()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={"width_ratios": [1.7, 1]})

    # (a) heatmap: single-hue sequential ramp, light = low, dark = high
    im = ax.imshow(M, vmin=0, vmax=1, cmap="Blues")
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(length=0)
    ax.set_xticks(range(len(mons)), [SHORT[m] for m in mons], rotation=35, ha="right", fontsize=10)
    ax.set_yticks(range(len(pols)), [SHORT[p] for p in pols], fontsize=10)
    ax.set_xlabel("monitor model")
    ax.set_ylabel("policy model (author of the submission)")
    for i, p in enumerate(pols):
        for j, m in enumerate(mons):
            r = c[(c.policy == p) & (c.monitor == m)]
            if r.empty or np.isnan(M[i, j]):
                continue
            txt = f"{M[i, j]:.2f}"  # per-cell CIs live in matrix.md / appendix, not on the heatmap (legibility)
            ax.text(j, i, txt, ha="center", va="center", fontsize=11,
                    color="white" if M[i, j] >= 0.5 else INK, fontweight="bold" if p == m else "normal")
            if p == m:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=CRIMSON, lw=2.4))
            elif FAMILY[p] == FAMILY[m]:
                ax.add_patch(plt.Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=AMBER, lw=1.6, ls="--"))
    gi = [k for k, x in enumerate(pols) if FAMILY.get(x) == "gemma"]
    gj = [k for k, x in enumerate(mons) if FAMILY.get(x) == "gemma"]
    if gi and gj:
        ax.add_patch(plt.Rectangle((min(gj) - 0.5, min(gi) - 0.5), len(gj), len(gi), fill=False,
                                   edgecolor=CRIMSON_DEEP, lw=3.4))
        ax.text(min(gj) + len(gj) / 2 - 0.5, -0.75, "gemma block", color="#8E2340",
                fontsize=12, fontweight="bold", ha="center", clip_on=False)
    cb = fig.colorbar(im, ax=ax, fraction=0.028, pad=0.02)
    cb.set_label("TPR at per-pair 5% FPR" if args.value == "tpr" else "AUROC", color=MUTED, fontsize=10)
    cb.ax.tick_params(color=MUTED, labelcolor=INK, labelsize=9)
    cb.outline.set_edgecolor(GRID)
    ax.set_title("(a) Catch rate; crimson box = same model, dashed amber = same family", fontsize=11, pad=28)

    # (b) pooled catch rate by relationship
    b = fit.get("bootstrap", {})
    labels, vals, los, his = [], [], [], []
    for key, lab in [("same_model", "same model\n(diagonal)"), ("same_family", "same family,\ndifferent model"), ("cross_family", "cross-family")]:
        d = b.get(key, {})
        if d and d.get("rate") is not None and not (isinstance(d["rate"], float) and np.isnan(d["rate"])):
            labels.append(lab); vals.append(d["rate"]); los.append(d["ci95"][0]); his.append(d["ci95"][1])
    x = np.arange(len(labels))
    colors = [CRIMSON, AMBER, BLUE][: len(labels)]
    bx.bar(x, vals, width=0.6, color=colors, edgecolor="white", linewidth=1.5)
    bx.errorbar(x, vals, yerr=[np.array(vals) - np.array(los), np.array(his) - np.array(vals)],
                fmt="none", ecolor=MUTED, capsize=3, lw=1.2)
    for xi, v, hiv in zip(x, vals, his):
        bx.text(xi, hiv + 0.025, f"{v:.2f}", ha="center", fontsize=10.5, color=INK)
    bx.set_xticks(x, labels, fontsize=10)
    bx.set_ylim(0, 1.05)
    bx.set_ylabel("catch rate (pooled over cells)")
    bx.grid(axis="y")
    g = fit.get("glm", {}).get("same_model", {})
    perm = fit.get("permutation", {})
    cap = []
    if g:
        lo, hi = g["ci95"]
        if any(isinstance(v, float) and np.isnan(v) for v in (lo, hi)) or abs(g["coef"]) > 15:
            cap.append("same_model log-odds not estimable (separation)")
        else:
            cap.append(f"same_model log-odds {g['coef']:+.2f} [{lo:+.2f}, {hi:+.2f}]")
    if perm:
        cap.append(f"permutation p (one-sided leniency) = {perm.get('p_one_sided_leniency', float('nan')):.3f}")
    bx.set_title("(b) Pooled catch rate, task-bootstrap 95% CI", fontsize=11, pad=34)
    if cap:
        bx.text(0.5, 1.025, "\n".join(cap), transform=bx.transAxes, ha="center", va="bottom",
                fontsize=9, color=MUTED)
    if args.title:
        main_t, _, detail = args.title.partition(" (")
        fig.suptitle(main_t, fontsize=14, y=0.99)
        if detail:
            fig.text(0.5, 0.925, "(" + detail, ha="center", fontsize=10.5, color=MUTED)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    fig.savefig(args.out, dpi=300)
    print(f"[written] {args.out}")


if __name__ == "__main__":
    main()
