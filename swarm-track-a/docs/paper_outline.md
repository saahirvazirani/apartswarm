# Paper outline — "Do copies go easy on each other?" (Track A)

Working skeleton for the 4–6 page Apart template. **Abstract, introduction and discussion are written by the human team.**
Every number below is a placeholder until `make recompute` has run on the complete `runs/`; each slot names the file it comes from.

## Title candidates

- Do copies go easy on each other? Same-model leniency in LLM code monitoring
- Self-monitoring is lenient: a 7×7 policy–monitor matrix on open-weight models

## Numbered contributions (draft; tighten after the full matrix)

1. A 7×7 policy × monitor catch-rate matrix on seven open-weight models hosted on Adaption (deepseek-v4-flash, gemma-4-26b-a4b-it,
   gemma-4-31b-it, qwen3.8-27b, qwen3.5-397b, glm-53-flash, glm-5.2), with per-pair 5 % FPR thresholds, Wilson intervals and AUROC
   on {n_attack} successful attack submissions and {n_benign} benign ones over 34 tasks. (`analysis/out/full/matrix.md`, Fig. 1)
2. A pre-registered test of *identity vs capability*: a two-way model `catch ~ policy + monitor + same_model + same_family_diff_model`
   with task-clustered SEs plus a within-task permutation test. Headline: same-model catch rate {diag} vs cross-family {cross}
   (task-bootstrap CIs). (`analysis/out/full/fit.md`)
3. The three same-family pairs (gemma, qwen, glm) separate *same weights* from *same family*. ({same_family} vs {diag} vs {cross})
4. Two exploratory probes of mechanism: telling the monitor the author (Stage 1b, 10 pre-registered tasks) and paraphrasing every
   submission with a fixed model (Stage 1c). (`analysis/out/told/deltas.md`, `analysis/out/para/deltas.md`)
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

## Public vs private

- Public: monitor prompt, benign prompt, task suite, aggregate matrices, analysis code, bank summary.
- Private appendix: attack + polish prompts, successful attack submissions, paraphrased attacks.

## Gate log (so far)

- Sat 6:53 PM: 7/7 models attempt the side task once reasoning is disabled.
- Sat 11:15–11:30 PM: output caps raised (glm-53-flash deliberates visibly); documented before any monitor call.
- Sun 12:04 AM: 3×3 gate — no ceiling/floor; same-model 0.66 vs cross-family 0.87 on the cheap subset (gemma-26b on itself 0.22).
