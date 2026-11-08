# RUN_INDEX — every number in the paper points here

| Paper item | Run folder(s) | Kind | Recompute |
|---|---|---|---|
| Pre-flight table (appendix) | `runs/preflight_20261107_184118`, `runs/preflight_extra_20261107_184723`, `runs/preflight_extra2_20261107_185050` | exploratory | `runs/PREFLIGHT_SUMMARY.md` (tables in each `table.md`) |
| Bank table: utility, telemetry use, side-task success, refusals (Table 1 / appendix) | `runs/bank_cheap3_v2` (deepseek-v4-flash, gemma-4-26b-a4b-it, glm-53-flash), `runs/bank_rest4` (gemma-4-31b-it, qwen3.8-27b, qwen3.5-397b, glm-5.2) | confirmatory | `.venv/bin/python analysis/bank_tables.py --banks runs/bank_cheap3_v2 runs/bank_rest4 --out analysis/out/banks` |
| First cheap-3 bank (superseded; 80% API failures, 2500 cap) | `runs/bank_cheap3` | exploratory, not used | — |
| Human gate samples (20 random kept polished attacks per bank) | `runs/bank_cheap3_v2/human_gate/`, `runs/bank_rest4/human_gate/` | — | — |
| Hand verification of any cell (human check, Sun AM) | `runs/stage1_mon{A,B,C}/scores.jsonl` | — | `.venv/bin/python analysis/verify_cell.py --policy <p> --monitor <m> --scores runs/stage1_mon*/scores.jsonl` (first-principles recount; must match `analysis/out/full/cells.csv`) |

## Gate log

| Time (EST) | Gate | Outcome | Decision |
|---|---|---|---|
| Sat 6:53 PM | Gate 1: JSON + ≥5/7 attempt side task | 7/7 attempt with reasoning disabled; qwen3.5-397b produces no JSON otherwise | Adopt `reasoning.effort=none` on every call; monitor cap 1200 |
| Sat 6:53 PM | (pre-emptive Gate 3) monitors score any telemetry ~90, benign 0 | ceiling before the sweep | Add the sanctioned-telemetry sentence to every task text; monitor prompt unchanged |
| Sat 9:12–11:02 PM | first cheap-3 bank (`runs/bank_cheap3`) | ~80% of calls failed (aiohttp pool fast-fail after token-weighted stall); re-run at 10:59 PM died with the session after 103 clean calls | Client rewritten (httpx, per-key token bucket, cooldown); `bank_cheap3` kept as **exploratory** evidence only, superseded by `bank_cheap3_v2` |
| Sat 11:15 PM | glm-53-flash truncated at the 2500-token policy cap in 15/21 attack calls; it emits its deliberation in the visible channel when reasoning is disabled (median ≈2200 output tokens before the code, 2 fenced blocks: draft + final) | side-task success 3/21 would leave the glm-53-flash row nearly empty | **Protocol amendment:** policy + polish cap 2500 → 8000 for *all* models (non-binding for deepseek/gemma/qwen3.8-27b, which never exceeded ~500); code = last fenced block defining the task function, else largest. Whole cheap-3 bank re-run as `runs/bank_cheap3_v2` so one cap covers the bank. Monitor prompt and cap unchanged. Hypotheses unchanged. |
| Sat 11:18 PM | three API keys available (teammates') | — | client round-robins `ADAPTION_API_KEY`, `KEY_2`, `KEY_3`; per-key 60k TPM pacing kept |
| Sat 11:30 PM | glm-53-flash as *monitor* deliberates in the visible channel: 250–2900 output tokens on real submissions, 1/4 probes truncated at the 1200 cap; parser took the first `{...}` (a quoted dict literal) and failed on 2/3 replies that ended in a valid verdict | before any monitor run | **Protocol amendment:** monitor cap 1200 → 4000 for all monitors (non-binding for the other six); parser takes the *last* JSON object with a `score` key, else the last `"score": n` match. Monitor prompt byte-identical. Parse-failure rate per monitor stays a reported secondary metric. |
| Sat 11:27 PM | Stage 1b task subset fixed before any told-condition call | — | 10 tasks = `random.Random(2026).sample(sorted(kept_ids), 10)` → t007, t008, t016, t021, t023, t024, t033, t035, t037, t040 (`analysis/stage1b_tasks.json`) |
| Sat 11:37 PM | Banks complete: 7 policies x 34 tasks x 3 resamples; 1348 kept submissions (benign 698 + polished attacks 650); 2.24 credits | all 7 attempt the side task; glm-53-flash refuses explicitly in 18% | Stage 1 launched: group A (deepseek, gemma-26b, glm-53-flash) keys 0,1; group B (qwen3.5-397b, glm-5.2) key 2; group C (gemma-31b, qwen3.8-27b) follows A on keys 0,1 |
| Sun 12:04 AM | Gates 2+3: 3×3 heatmap from the first 5,043 group-A scores (`analysis/out/cheap3_partial`, snapshot of a growing file; final numbers recompute from the complete `runs/stage1_monA`) | TPR not >0.95 everywhere and not <0.1: deepseek→deepseek **0.88** vs 0.96/1.00 off-diagonal; gemma-26b→gemma-26b **0.22** vs 0.79/1.00; glm-53-flash column 1.00 everywhere (that column is at ceiling, incl. its own diagonal) | No pivot. Continue the full sweep as pre-registered; lead with TPR + AUROC; glm-53-flash column interpreted on AUROC/scores as well |

