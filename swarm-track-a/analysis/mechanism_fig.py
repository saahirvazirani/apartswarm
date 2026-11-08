#!/usr/bin/env python3
"""Figure 5: mechanism-chain summary forest plot.

Harvests the already-computed numbers for every candidate explanation of the
gemma self-leniency from the analysis/out/ markdown/JSON outputs (the files are
the source of truth; nothing is recomputed here) and renders a grouped forest
plot: surface-level accounts that were tested and came back null (grey-blue)
vs the family blind spot that survives (red).

Rows and sources:
  - Stated identity (told vs blind)      analysis/out/told/deltas.md
  - Surface form (gemma-26b paraphrase)  analysis/out/para/deltas.md
  - Writer obfuscation (gemma-31b)       analysis/out/para_g31/deltas.md
  - Excuse vocabulary on misses          analysis/out/reasons/reasons.md
  - Cross-family paraphraser (Stage 1e)  analysis/out/para_ds/deltas.md (optional:
      if absent the row renders as a hollow "in flight (pre-registered)" marker;
      re-running this script after Stage 1e finishes picks the file up)
  - Matched-FPR pooled diagonal-cross    analysis/out/matched/matched.md
  - Gemma-block GLM odds ratio           analysis/out/matched/block_fit.json

Output: analysis/out/mech/fig5_mechanism.png + mech.md (numbers + provenance).
Usage:  .venv/bin/python analysis/mechanism_fig.py
"""

import json
import re
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parent
OUT_ROOT = ROOT / "out"
OUT = OUT_ROOT / "mech"

# -- palette (fixed assignment: color follows the verdict category) -----------
C_NULL = "#5b7fa6"      # grey-blue: tested, ruled out / null
C_SURV = "#c0392b"      # red: survives
C_PEND = "#8a8f98"      # grey: pending (hollow marker)
INK = "#1f2430"
INK_MUTED = "#6b7280"
GRID = "#d8dce3"
REF = "#9aa1ab"

NUM = r"([+-]?\d+(?:\.\d+)?)"
TRIPLE = re.compile(NUM + r"\s*\[\s*" + NUM + r"\s*,\s*" + NUM + r"\s*\]")


def _norm(text: str) -> str:
    return text.replace("−", "-").replace("**", "")


def parse_triple(path: Path, marker: str):
    """First line containing `marker` -> (est, lo, hi). The file wins."""
    for line in _norm(path.read_text()).splitlines():
        if marker in line:
            m = TRIPLE.search(line)
            if m:
                return tuple(float(g) for g in m.groups())
    raise ValueError(f"no 'est [lo, hi]' on a line containing {marker!r} in {path}")


def harvest():
    diag_marker = "(diagonal delta) - (cross-family delta)"
    told = parse_triple(OUT_ROOT / "told" / "deltas.md", diag_marker)
    para = parse_triple(OUT_ROOT / "para" / "deltas.md", diag_marker)
    para_g31 = parse_triple(OUT_ROOT / "para_g31" / "deltas.md", diag_marker)

    para_ds_path = OUT_ROOT / "para_ds" / "deltas.md"
    para_ds = parse_triple(para_ds_path, diag_marker) if para_ds_path.exists() else None

    reasons = parse_triple(
        OUT_ROOT / "reasons" / "reasons.md", "per-submission difference"
    )
    matched = parse_triple(
        OUT_ROOT / "matched" / "matched.md", "diagonal - cross-family (interp)"
    )  # first occurrence = telemetry attack (Stage 1)

    fit = json.loads((OUT_ROOT / "matched" / "block_fit.json").read_text())
    gb = fit["terms"]["gemma_block"]
    orr = (gb["odds_ratio"], gb["or_ci95"][0], gb["or_ci95"][1])

    return told, para, para_g31, para_ds, reasons, matched, orr


def fmt(v, digits=2):
    return f"{v:+.{digits}f}" if v < 0 or v >= 0 else str(v)


def row_valstr(est, lo, hi, digits=2, signed=True):
    s = "+" if signed else ""
    return f"{est:{s}.{digits}f} [{lo:{s}.{digits}f}, {hi:{s}.{digits}f}]"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    told, para, para_g31, para_ds, reasons, matched, orr = harvest()

    # ---- panel row definitions ----------------------------------------------
    # (label, (est, lo, hi) or None, verdict, color, value-digits)
    panel_a = [
        ("Stated identity\n(told vs blind, diagonal-specific)", told, "null", C_NULL, 1),
        ("Surface form\n(gemma-26b paraphrase, diag-specific)", para, "null", C_NULL, 1),
        ("Writer-specific obfuscation\n(gemma-31b rewriter, diag-specific)", para_g31, "null", C_NULL, 1),
    ]
    if para_ds is not None:
        panel_a.append(
            ("Cross-family paraphraser\n(deepseek, Stage 1e, diag-specific)",
             para_ds, "null" if para_ds[1] <= 0 <= para_ds[2] else "non-null", C_NULL, 1)
        )
    else:
        panel_a.append(
            ("Cross-family paraphraser\n(deepseek, Stage 1e, diag-specific)",
             None, "pending", C_PEND, 1)
        )

    panel_b = [
        ("Excuse vocabulary on misses\n(own - cross accepts-justification)", reasons, "null", C_NULL, 3),
        ("Matched-FPR catch-rate gap\n(pooled diagonal - cross-family)", matched, "SURVIVES", C_SURV, 3),
    ]
    panel_c = [
        ("Gemma-block GLM\n(odds ratio, capability-adjusted)", orr, "SURVIVES", C_SURV, 2),
    ]

    # ---- figure --------------------------------------------------------------
    fig = plt.figure(figsize=(10.4, 7.6))
    gs = fig.add_gridspec(
        3, 1, height_ratios=[len(panel_a), len(panel_b), 1.15],
        hspace=0.62, left=0.315, right=0.845, top=0.855, bottom=0.075,
    )
    ax_a = fig.add_subplot(gs[0])
    ax_b = fig.add_subplot(gs[1])
    ax_c = fig.add_subplot(gs[2])

    def style(ax):
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
        ax.tick_params(axis="x", colors=INK_MUTED, labelsize=8.5, length=3)
        ax.tick_params(axis="y", length=0)
        ax.xaxis.grid(True, color=GRID, lw=0.6, zorder=0)
        ax.set_axisbelow(True)

    def draw_panel(ax, rows, title, xlabel, ref=0.0, log=False, signed=True):
        n = len(rows)
        ys = list(range(n - 1, -1, -1))
        for y, (label, triple, verdict, color, digits) in zip(ys, rows):
            if triple is None:
                # hollow pending marker at the reference line, no CI
                ax.plot(ref, y, "o", ms=9, mfc="none", mec=C_PEND, mew=1.6, zorder=4)
                ax.text(ref, y + 0.30, "in flight (pre-registered)",
                        ha="center", va="bottom", fontsize=7.6,
                        color=INK_MUTED, style="italic")
            else:
                est, lo, hi = triple
                ax.plot([lo, hi], [y, y], color=color, lw=2.0,
                        solid_capstyle="round", zorder=3)
                for cap in (lo, hi):
                    ax.plot([cap, cap], [y - 0.11, y + 0.11], color=color,
                            lw=1.6, zorder=3)
                ax.plot(est, y, "o", ms=8, mfc=color, mec="white", mew=1.1, zorder=4)
                ax.text(est, y + 0.30, row_valstr(est, lo, hi, digits, signed),
                        ha="center", va="bottom", fontsize=7.6, color=INK_MUTED)
            # verdict tag, right margin
            tag_color = C_SURV if verdict == "SURVIVES" else (
                C_PEND if verdict == "pending" else C_NULL)
            weight = "bold" if verdict == "SURVIVES" else "normal"
            ax.text(1.025, y, verdict, transform=ax.get_yaxis_transform(),
                    ha="left", va="center", fontsize=8.6, color=tag_color,
                    fontweight=weight,
                    bbox=dict(boxstyle="round,pad=0.28", fc="none",
                              ec=tag_color, lw=0.9))
        ax.set_yticks(ys)
        ax.set_yticklabels([r[0] for r in rows], fontsize=8.8, color=INK)
        ax.set_ylim(-0.6, n - 0.25)
        if log:
            ax.set_xscale("log")
        ax.axvline(ref, color=REF, lw=1.1, ls=(0, (4, 3)), zorder=1)
        ax.set_xlabel(xlabel, fontsize=8.5, color=INK_MUTED, labelpad=2)
        ax.set_title(title, loc="left", fontsize=9.6, color=INK,
                     fontweight="bold", pad=10)
        style(ax)

    draw_panel(
        ax_a, panel_a,
        "A. Score-scale tests - does the diagonal-specific suspicion shift explain it?",
        "diagonal-specific Δ suspicion (score points, 0–100 scale); 0 = no diagonal-specific effect",
    )
    ax_a.set_xlim(-8.5, 6.5)

    draw_panel(
        ax_b, panel_b,
        "B. Proportion / catch-rate tests",
        "difference (proportion / catch rate); 0 = no own-vs-cross difference",
    )
    ax_b.set_xlim(-0.21, 0.13)

    draw_panel(
        ax_c, panel_c,
        "C. What survives - capability-adjusted family effect",
        "odds ratio of catching a gemma attack inside the gemma block (log scale); 1 = no effect",
        ref=1.0, log=True, signed=False,
    )
    ax_c.set_xlim(0.12, 2.6)
    ax_c.xaxis.set_major_locator(mticker.FixedLocator([0.2, 0.29, 0.5, 1.0, 2.0]))
    ax_c.xaxis.set_major_formatter(mticker.FixedFormatter(["0.2", "0.29", "0.5", "1", "2"]))
    ax_c.xaxis.set_minor_locator(mticker.NullLocator())
    ax_c.xaxis.set_minor_formatter(mticker.NullFormatter())

    fig.suptitle(
        "Figure 5. Every surface-level account tested and ruled out; "
        "the family blind spot survives",
        fontsize=12.5, color=INK, fontweight="bold", x=0.5, y=0.975,
    )
    fig.text(
        0.5, 0.935,
        "Each row: one candidate mechanism for the gemma self-leniency, point estimate with 95% CI. "
        "Units differ by panel; every panel has its own axis and null-reference line.",
        ha="center", fontsize=8.6, color=INK_MUTED,
    )
    handles = [
        Line2D([], [], marker="o", color=C_NULL, lw=2, mec="white",
               label="ruled out / null"),
        Line2D([], [], marker="o", color=C_SURV, lw=2, mec="white",
               label="survives"),
        Line2D([], [], marker="o", color="none", mfc="none", mec=C_PEND,
               mew=1.6, label="in flight (pre-registered)"),
    ]
    fig.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, 0.925),
               ncol=3, frameon=False, fontsize=8.4, handletextpad=0.5,
               columnspacing=1.6)

    png = OUT / "fig5_mechanism.png"
    fig.savefig(png, dpi=170, facecolor="white")
    plt.close(fig)

    # ---- mech.md -------------------------------------------------------------
    def md_row(name, triple, unit, verdict, src, digits=2, signed=True):
        val = ("in flight (pre-registered), file absent" if triple is None
               else row_valstr(*triple, digits, signed))
        return f"| {name} | {val} | {unit} | {verdict} | `{src}` |"

    lines = [
        "# Figure 5 mechanism-chain summary - numbers and provenance",
        "",
        "Harvested verbatim by `analysis/mechanism_fig.py` from the files below "
        "(the files are the source of truth; nothing recomputed). "
        "Re-running the script picks up `analysis/out/para_ds/deltas.md` automatically "
        "once Stage 1e lands.",
        "",
        "| row | estimate [95% CI] | unit | verdict | source |",
        "|---|---|---|---|---|",
        md_row("Stated identity (told vs blind, diagonal-specific component)",
               told, "suspicion score points", "null",
               "analysis/out/told/deltas.md"),
        md_row("Surface form (gemma-26b paraphrase, diagonal-specific component)",
               para, "suspicion score points", "null",
               "analysis/out/para/deltas.md"),
        md_row("Writer-specific obfuscation (gemma-31b rewriter, diagonal-specific component)",
               para_g31, "suspicion score points", "null",
               "analysis/out/para_g31/deltas.md"),
        md_row("Cross-family paraphraser (deepseek, Stage 1e, diagonal-specific component)",
               para_ds, "suspicion score points",
               ("pending" if para_ds is None else
                ("null" if para_ds[1] <= 0 <= para_ds[2] else "non-null")),
               "analysis/out/para_ds/deltas.md"),
        md_row("Excuse vocabulary (own - cross accepts-justification on misses)",
               reasons, "proportion", "null",
               "analysis/out/reasons/reasons.md", digits=3),
        md_row("Matched-FPR pooled diagonal - cross-family gap (telemetry)",
               matched, "catch-rate (TPR at 5% FPR)", "SURVIVES",
               "analysis/out/matched/matched.md", digits=3),
        md_row("Gemma-block GLM (capability-adjusted)",
               orr, "odds ratio", "SURVIVES",
               "analysis/out/matched/block_fit.json", signed=False),
        "",
        f"Figure: `analysis/out/mech/fig5_mechanism.png` (dpi 170).",
        "",
    ]
    (OUT / "mech.md").write_text("\n".join(lines))
    print(f"wrote {png}")
    print(f"wrote {OUT / 'mech.md'}")


if __name__ == "__main__":
    main()
