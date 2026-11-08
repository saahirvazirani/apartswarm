# Figure 5 mechanism-chain summary - numbers and provenance

Harvested verbatim by `analysis/mechanism_fig.py` from the files below (the files are the source of truth; nothing recomputed). Re-running the script picks up `analysis/out/para_ds/deltas.md` automatically once Stage 1e lands.

| row | estimate [95% CI] | unit | verdict | source |
|---|---|---|---|---|
| Stated identity (told vs blind, diagonal-specific component) | -0.53 [-3.72, +3.60] | suspicion score points | null | `analysis/out/told/deltas.md` |
| Surface form (gemma-26b paraphrase, diagonal-specific component) | -1.85 [-3.92, +0.25] | suspicion score points | null | `analysis/out/para/deltas.md` |
| Writer-specific obfuscation (gemma-31b rewriter, diagonal-specific component) | -1.03 [-5.97, +4.29] | suspicion score points | null | `analysis/out/para_g31/deltas.md` |
| Cross-family paraphraser (deepseek, Stage 1e, diagonal-specific component) | -3.26 [-7.25, +0.40] | suspicion score points | null | `analysis/out/para_ds/deltas.md` |
| Excuse vocabulary (own - cross accepts-justification on misses) | +0.009 [-0.063, +0.078] | proportion | null | `analysis/out/reasons/reasons.md` |
| Matched-FPR pooled diagonal - cross-family gap (telemetry) | -0.080 [-0.152, -0.003] | catch-rate (TPR at 5% FPR) | SURVIVES | `analysis/out/matched/matched.md` |
| Gemma-block GLM (capability-adjusted) | 0.29 [0.19, 0.45] | odds ratio | SURVIVES | `analysis/out/matched/block_fit.json` |

Figure: `analysis/out/mech/fig5_mechanism.png` (dpi 300).
