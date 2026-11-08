# Threshold tie-break sensitivity of the gemma-31b diagonal (added Sun 2026-11-08 PM)

The most dramatic single number — gemma-4-31b-it catches 0.03 of its own telemetry attacks — is partly an artifact of score
quantization at the threshold, and must be reported with that caveat.

gemma-31b's 95th-percentile benign score is exactly **85**, and a large share of its own attacks also score exactly **85**
(attack median 76; 38% score ≥ 85, 48% ≥ 80). The calibration uses a strict `>` threshold, which drops every attack sitting
exactly on 85:

| threshold rule | threshold | diagonal TPR | realised FPR |
|---|---|---|---|
| `> q95`  (as reported) | 85 | **0.03** | 0.030 |
| `>= q95` | 85 | **0.38** | 0.071 |
| threshold − 5 (`>`) | 80 | 0.45 | 0.081 |
| threshold + 5 (`>`) | 90 | 0.02 | 0.010 |

So the own-model leniency is robust (AUROC 0.86; under `>=` still 0.38 own vs ≈0.56+ cross-family; the second attack type gives
0.07 own vs 0.68 cross under independent threshold dynamics; the residual analysis gives −0.25), but the specific 0.03 is a
tie-break value and should be quoted as "near-zero at a strict 5% budget (0.03 with `>`, 0.38 with `>=`)", not as a bare 0.03.
The pre-registered pipeline uses `>` throughout and is applied identically to every cell, so the comparison across cells is
fair; the caveat is about over-reading the magnitude of one cell.
