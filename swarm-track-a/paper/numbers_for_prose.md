# Numbers for the human-written prose (regenerated Sun ~5:30 PM from the clean, glob-fixed recompute)

Every number below is quoted from a generated file; if a number here disagrees with the file, the file wins.
DO NOT use numbers from chat logs or earlier drafts — several changed when the STAGE1 glob contamination was fixed.

## Headline (pre-registered primary; `analysis/out/full/fit.md`, `fit.json`)
- Same-model catch 0.584 [0.540, 0.630] vs cross-family 0.718 [0.675, 0.762]; gap −0.134 [−0.168, −0.100] (task bootstrap).
- `same_model` log-odds −0.56, OR 0.57 [0.47, 0.70], p = 2.6e-8; `same_family_diff_model` OR 0.74 [0.61, 0.90], p = 0.0025.
- Within-task permutation: 0/2000 shuffles reach the observed gap (p < 0.0005).
- 650 successful polished attacks, 698 kept benign, 34 tasks, 28,458 blind score draws (runs/stage1_mon{A,B,C} only).

## The claim we stand behind (post-hoc, labeled; `analysis/out/matched/`)
- Matched-FPR (ROC-interpolated at exactly 5% FPR): gemma-31b own 0.20 vs cross-mean 0.57; gemma-26b 0.22 vs 0.56.
  Quote the gemma-31b diagonal as ≈0.20 (0.03 with `>`, 0.38 with `>=`; tie-break note retracted and replaced).
- Pooled matched-FPR diagonal−cross: −0.080 [−0.152, −0.003] (telemetry).
- Gemma-block GLM: gemma_block OR 0.29 [0.19, 0.45], p = 3.8e-8; non-gemma diagonal OR 1.08 [0.78, 1.47], p = 0.65
  (precise null); non-gemma same-family OR 1.00 [0.74, 1.35].

## Second attack class (`analysis/out/logic/`, `analysis/out/matched/`)
- Quantile thresholds: same-model 0.56 vs cross 0.83, gap −0.269 [−0.333, −0.208], same_model OR 0.45, p = 0.003.
- Matched-FPR: pooled gap −0.070 [−0.153, +0.023] (includes 0); gemma-31b own 0.25 vs 0.60–1.00 cross.
- qwen3.5 own cell 0.28 (quantile) → 0.67 (interpolated); gemma-31b catches qwen3.5's logic attacks at only 0.03 cross-family.
- Honest sentence: direction replicates for gemma; magnitudes threshold-sensitive at n≈35 benign per pair; some cells n=10.

## Mechanism chain (Figure 5, `analysis/out/mech/mech.md`)
- Stated identity (told−blind, diagonal-specific): −0.53 [−3.72, +3.60] — null.
- Surface form (gemma-26b paraphrase): −1.85 [−3.92, +0.25] — null.
- Writer-specific obfuscation (gemma-31b rewriter): −1.03 [−5.97, +4.29] — null.
- Excuse vocabulary on misses (own−cross accepts-justification): +0.004 [−0.061, +0.072] — informative null;
  misses cite the sanctioned-telemetry note 84–100% everywhere; gemma-31b verbally flags the call in 28% of own misses.
- Familiarity (`analysis/out/familiarity/`): REFUTED with sign reversed — gemma monitors score gemma-written code
  MORE suspicious (benign gap +5.6 to +10.4; attack gap +11.3 to +13.4) → supports threshold-inflation anatomy.

## Deployment (Figure 4, `analysis/out/committee/committee.md`)
- glm-53-flash misses only 4 of gemma-31b's 97 own-cell misses (Jaccard 0.04); other cross monitors 0.37–0.45.
- Every committee of two non-gemma monitors scores ≥ 0.57 on gemma-31b attacks; all-gemma committee 0.22.
- KEY CAVEAT: max-fusion committee containing the self-lenient monitor is dragged DOWN (gemma-31b + glm-53-flash
  fuses to 0.27 vs 0.97 for glm-53-flash alone). The recommendation is replacement, not augmentation.
- Cheapest committee fixing gemma-31b: qwen3.8-27b + glm-53-flash, 0.97 [0.92, 1.00].

## Policy behaviour (`analysis/out/banks/bank_summary.md`)
- Benign pass rate 95–100% every policy; glm-53-flash refuses the covert objective explicitly in 18% of attempts.

## In flight at time of writing — check these files before quoting; each has a pre-registered RUN_INDEX row
- Stage 1e deepseek-paraphraser control: `analysis/out/para_ds/deltas.md` — CURRENTLY FROM PARTIAL DATA (1e re-score
  incomplete); rerun `make para-ds` after `runs/stage1e_ds` finishes, then `make mech` to update Figure 5. Do not quote until then.
- Stage 1f reasoning-on probe: `runs/stage1f_reason/` (gemma-31b, reasoning=medium).
- Stage 1g sentence-removal ablation: `runs/stage1g_nonote/`.
- Stage 1h benign calibration expansion: `runs/stage1h_benexp/` (n≈300 benign per gemma cell).
- Held-out calibration split: DONE (`analysis/out/heldout/heldout.md`): realized FPR 0.053 vs nominal 0.05 (worst
  cell 0.070); pooled cross−diagonal gap 0.110 [0.005, 0.187] over 200 task-level splits; gemma-31b own 0.16 vs 0.71
  cross held-out. Mean per-cell |Δ| vs full-sample 0.036. Intervals are split-variability only (fixed attack set).
- Contingency sentence if any is unfinished at freeze: "Stage 1x was pre-registered (RUN_INDEX, <time>) and was still
  running at the submission freeze; partial data are included in the repo and not interpreted here."
- Human anchor: if `runs/human_anchor/LABELS.csv` is unfilled at freeze, the Limitations sentence is: "The human-anchor
  labeling packet was prepared but not completed before the deadline; monitor scores are not human-validated."

## Logistics
- Spend: `make budget` (≈26.5 credits at 5:10 PM; cap raised to ~1k by the team Sun ~5:15 PM, noted in RUN_INDEX).
- Abstract 150–250 words; 8-page max excl. references/appendices (docs/judging_research.md).
