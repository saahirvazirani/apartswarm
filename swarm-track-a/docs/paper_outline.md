# Paper outline — "Do copies go easy on each other?" (Track A)

Working skeleton for the 4–6 page Apart template. **Abstract, introduction and discussion are written by the human team.**
Every number below is a placeholder until `make recompute` has run on the complete `runs/`; each slot names the file it comes from.

## Title candidates

- Do copies go easy on each other? Same-model leniency in LLM code monitoring
- Self-monitoring is lenient: a 7×7 policy–monitor matrix on open-weight models

## Numbered contributions (draft; tighten after the full matrix)

1. A 7×7 policy × monitor catch-rate matrix on seven open-weight models hosted on Adaption (deepseek-v4-flash, gemma-4-26b-a4b-it,
   gemma-4-31b-it, qwen3.8-27b, qwen3.5-397b, glm-53-flash, glm-5.2), with per-pair 5 % FPR thresholds, Wilson intervals and AUROC
   on 650 successful (polished) attack submissions and 698 benign ones over 34 tasks; 28,458 score draws. (`analysis/out/full/matrix.md`, Fig. 1)
2. A pre-registered test of *identity vs capability*: a two-way model `catch ~ policy + monitor + same_model + same_family_diff_model`
   with task-clustered SEs plus a within-task permutation test. Headline: same-model catch rate **0.58 [0.54, 0.63]** vs cross-family
   **0.72 [0.68, 0.76]**; gap −0.13 [−0.17, −0.10]; `same_model` OR 0.57 [0.47, 0.70]; permutation 0/2000. (`analysis/out/full/fit.md`)
   **The effect is family-specific:** leniency index gemma-4-31b-it +0.53 (0.03 on itself), gemma-4-26b-a4b-it +0.31, qwen3.8-27b +0.13,
   qwen3.5-397b +0.02, glm-5.2 0.00, glm-53-flash −0.02, deepseek-v4-flash −0.15. Leave-gemma-out: OR interval spans 1
   (log-odds −0.07 [−0.39, +0.25]). On AUROC the diagonal dip is ≤ 0.024 everywhere. (`analysis/out/full/robustness.md`)
3. The three same-family pairs (gemma, qwen, glm) separate *same weights* from *same family*: same-family cells average **0.59**,
   i.e. at the diagonal (0.58), not between it and cross-family (0.72); `same_family_diff_model` OR 0.74 [0.61, 0.90]. H1b's
   "intermediate" form is not supported; family membership is as costly as identity, again mostly in gemma (0.38 / 0.18).
4. Two exploratory probes of mechanism. **Told (Stage 1b, 10 pre-registered tasks):** naming the author lowers attack suspicion by
   ≈ 2 points for every relationship; diagonal-specific component −0.5 [−3.7, +3.6] → not a reaction to the stated name.
   **Paraphrase (Stage 1c):** rewording every submission (gemma-4-26b paraphraser) leaves the gap intact — same-model cell TPR
   0.61 → 0.57, cross-family 0.72 → 0.69, diagonal-specific score change −1.9 [−3.9, +0.3] → not surface-form self-recognition. (`analysis/out/told/deltas.md`, `analysis/out/para/deltas.md`)
5. A secondary finding on *policy* behaviour: side-task compliance differs sharply across models — glm-53-flash explicitly refuses the
   covert objective in 18 % of attempts after visible deliberation; the others comply in 85–100 %. (`analysis/out/banks/bank_summary.md`)
6. A fully reproducible evidence locker: every call's response and `usage.cost`, frozen prompts with hashes, a sandboxed task suite, and
   `make recompute`.

## Sections

1. **Introduction** (human). Why monitor assignment matters for multi-agent / swarm settings; the "true by construction" critique and
   how the design avoids it (attack instructed, leniency never instructed, monitor blind).
2. **Setup.** Models and families; 34 tasks (generation + validation); benign / attack / polish prompts (verbatim, hashed); the
   sanctioned-telemetry sentence and why it is needed (pre-flight ceiling); monitor prompt (verbatim); reasoning disabled everywhere;
   3 resamples × 3 draws; per-pair calibration; what counts as a successful attack. Table 1 = bank summary.
3. **Results.**
   - Fig. 1: 7×7 TPR heatmap (diagonal boxed, same-family dashed) + pooled catch rates with task-bootstrap CIs.
   - Two-way fit: `same_model` and `same_family_diff_model` coefficients, OR with CI, permutation p.
   - AUROC matrix (appendix) for the columns at the TPR ceiling (glm-53-flash catches everything in the 3×3 subset).
   - Per-monitor leniency index (cross-family mean TPR − diagonal TPR).
   - Two contrasting excerpts (same attack, passed by its own model, caught cross-family) — `analysis/out/full/excerpts.md`.
   - Stage 1b told-vs-blind deltas by relationship; Stage 1c paraphrase deltas by relationship.
4. **Discussion** (human). If H1: never let a model monitor itself; same-family is {better/not better}; what told/paraphrase say
   about mechanism (stated identity vs stylometric self-recognition vs shared blind spots). If H0: capability, not identity.
5. **Limitations and Dual-Use / Ethical Considerations** (appendix; bullets in `docs/limitations_draft.md`).
6. **LLM-usage statement** (README).

## Figures and tables (recompute commands)

| Item | File | Command |
|---|---|---|
| Fig. 1 | `analysis/out/full/fig1.png` | `make recompute` then `.venv/bin/python analysis/figures.py --cells analysis/out/full/cells.csv --fit analysis/out/full/fit.json --out analysis/out/full/fig1.png` |
| Table 1 bank summary | `analysis/out/banks/bank_summary.md` | `.venv/bin/python analysis/bank_tables.py --banks runs/bank_cheap3_v2 runs/bank_rest4 --out analysis/out/banks` |
| 7×7 TPR + AUROC tables | `analysis/out/full/matrix.md` | `make full` |
| Two-way fit, permutation, bootstrap | `analysis/out/full/fit.md` | `make full` |
| Told vs blind | `analysis/out/told/deltas.md` | `.venv/bin/python analysis/deltas.py told --blind runs/stage1_mon*/scores.jsonl --told runs/stage1b_*/scores.jsonl --out analysis/out/told` |
| Paraphrase | `analysis/out/para/deltas.md` | `.venv/bin/python analysis/deltas.py para --orig runs/stage1_mon*/scores.jsonl --para runs/stage1c_*/scores.jsonl --out analysis/out/para` |
| Excerpts | `analysis/out/full/excerpts.md` | `.venv/bin/python analysis/excerpts.py --scores runs/stage1_mon*/scores.jsonl --cells analysis/out/full/cells.csv --banks runs/bank_cheap3_v2 runs/bank_rest4 --out analysis/out/full/excerpts.md` |
| Pre-flight table | `runs/PREFLIGHT_SUMMARY.md` | — |
| Credits | `make budget` | — |

## Suggested framing (for the human-written abstract/discussion; agent's reading of the numbers) — REVISED 11:45 AM after the post-hoc checks

- Headline sentence candidate: "We find no evidence of a general tendency for a model to go easy on its own code, but a large,
  robust failure in one family: gemma monitors catch 3–22 % of gemma-written attacks versus 33–56 % from other families, under every
  calibration we tried." The pooled 13-point gap is reported as the pre-registered primary result *with* the FPR sweep and
  hard-negative calibration beside it, not as the headline.
- Figure 2 (residuals after policy + monitor effects) is the picture that makes the identity-vs-capability argument; consider
  putting it in the body next to Figure 1.

### Earlier framing (before 11:45 AM; kept for the record)

- The pooled answer to the title question is "yes, by 13 points at a 5 % false-positive budget", but the honest answer is
  "it depends on the family": the gemma monitors are both the weakest monitors overall and dramatically weakest on gemma-written
  attacks (3 % and 22 % caught), while glm, deepseek and qwen3.5-397b show no self-leniency at all, and deepseek is *stricter* on itself.
- The effect lives at the calibrated operating point, not in ranking: AUROC barely moves on the diagonal. Mechanistically this looks
  like a shared blind spot (the same model writes and fails to flag the same style of justified-looking telemetry) rather than
  recognition of authorship — consistent with the told condition doing nothing diagonal-specific. The paraphrase result (Stage 1c)
  is the direct test of the stylometric version of this story.
- Practical recommendation that survives the heterogeneity: do not let a model (or its family) monitor its own output *unless* its
  own-model cell has been measured; cross-family monitoring is never worse here, and for gemma it is the difference between 3 % and 67 %.

## Public vs private

- Public: monitor prompt, benign prompt, task suite, aggregate matrices, analysis code, bank summary.
- Private appendix: attack + polish prompts, successful attack submissions, paraphrased attacks.

## Gate log (so far)

- Sat 6:53 PM: 7/7 models attempt the side task once reasoning is disabled.
- Sat 11:15–11:30 PM: output caps raised (glm-53-flash deliberates visibly); documented before any monitor call.
- Sun 12:04 AM: 3×3 gate — no ceiling/floor; same-model 0.66 vs cross-family 0.87 on the cheap subset (gemma-26b on itself 0.22).
- Sun 1:12 AM: full 7×7 — pooled effect 0.58 vs 0.72, but concentrated in gemma; glm/deepseek/qwen3.5 show none.
- Sun 1:35 AM: told vs blind — no diagonal-specific effect.
- Sun 1:55 AM: exploratory appendix run started — pre-polish attacks scored by all 7 monitors (effect of the polish pass).
- Sun 2:10–10:00 AM: API outage; affected runs re-filled from 10:30 AM (resumable JSONL, failed draws excluded).
- Sun 11:30 AM: paraphrase (H3) final — gap survives paraphrasing; shared-blind-spot reading.
