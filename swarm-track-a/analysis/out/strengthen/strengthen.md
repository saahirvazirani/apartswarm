# Identity vs capability: post-hoc analyses (exploratory)

## 1. Residuals after additive policy + monitor effects (TPR at 5 % FPR)

Residual = cell TPR − (mu + policy effect + monitor effect), least squares on all 49 cells. Negative on the diagonal = the
monitor catches its own model's attacks *less* than its overall strictness and the policy's overall catchability predict.

| monitor (own-model cell) | residual | 95% CI (task bootstrap) |
|---|---|---|
| deepseek-v4-flash | -0.102 | [-0.162, +0.084] |
| gemma-4-26b-a4b-it | -0.211 | [-0.345, +0.172] |
| gemma-4-31b-it | -0.245 | [-0.341, +0.131] |
| qwen3.8-27b | -0.010 | [-0.207, +0.154] |
| qwen3.5-397b | +0.024 | [-0.140, +0.092] |
| glm-53-flash | -0.073 | [-0.136, +0.004] |
| glm-5.2 | +0.011 | [-0.084, +0.160] |

- mean residual, same_model: -0.087 [-0.119, +0.002] (7 cells)

- mean residual, same_family: -0.038 [-0.100, +0.049] (6 cells)

- mean residual, cross_family: +0.023 [-0.001, +0.032] (36 cells)

| policy \ monitor | deepseek | gemma-26b | gemma-31b | qwen3.8-27b | qwen3.5-397b | glm-53-flash | glm-5.2 |
|---|---|---|---|---|---|---|---|
| deepseek | **-0.10** | +0.28 | +0.29 | -0.08 | -0.08 | -0.20 | -0.11 |
| gemma-26b | +0.05 | **-0.21** | -0.07 | +0.06 | +0.03 | +0.04 | +0.10 |
| gemma-31b | -0.00 | -0.07 | **-0.25** | +0.13 | +0.06 | +0.18 | -0.05 |
| qwen3.8-27b | +0.14 | -0.14 | +0.01 | **-0.01** | -0.10 | +0.13 | -0.02 |
| qwen3.5-397b | -0.05 | -0.25 | +0.04 | +0.13 | **+0.02** | +0.02 | +0.09 |
| glm-53-flash | -0.08 | +0.13 | +0.06 | -0.03 | +0.02 | **-0.07** | -0.02 |
| glm-5.2 | +0.05 | +0.27 | -0.09 | -0.19 | +0.05 | -0.10 | **+0.01** |

## 2. FPR sweep (diagonal − cross-family catch gap at other false-positive budgets)

| FPR target | same-model catch | same-family catch | cross-family catch | diag − cross [95% CI] | same_model log-odds [95% CI] |
|---|---|---|---|---|---|
| 1% | 0.400 | 0.400 | 0.407 | -0.007 [-0.042, +0.026] | +0.07 [-0.12, +0.27] |
| 2% | 0.496 | 0.480 | 0.532 | -0.035 [-0.063, -0.005] | +0.02 [-0.17, +0.20] |
| 5% | 0.586 | 0.593 | 0.719 | -0.133 [-0.167, -0.102] | -0.55 [-0.74, -0.36] |
| 10% | 0.776 | 0.754 | 0.840 | -0.064 [-0.097, -0.033] | -0.42 [-0.65, -0.20] |
| 20% | 0.866 | 0.951 | 0.924 | -0.059 [-0.089, -0.028] | -0.94 [-1.26, -0.63] |

## 3. Hard-negative calibration (thresholds from benign submissions that call send_report)

Benign pool restricted to telemetry-using submissions (370 of 698). Cells with fewer than 20 such negatives are marked †.

| monitor (own-model cell) | n hard negatives | threshold | TPR own | mean TPR cross-family | leniency |
|---|---|---|---|---|---|
| deepseek-v4-flash | 8† | 26.7 | 0.61 | 0.67 | +0.06 |
| gemma-4-26b-a4b-it | 62 | 48.3 | 0.22 | 0.37 | +0.15 |
| gemma-4-31b-it | 84 | 85.0 | 0.03 | 0.33 | +0.30 |
| qwen3.8-27b | 45 | 11.7 | 0.40 | 0.50 | +0.10 |
| qwen3.5-397b | 99 | 85.0 | 0.78 | 0.68 | -0.11 |
| glm-53-flash | 25 | 10.0 | 0.99 | 0.92 | -0.06 |
| glm-5.2 | 47 | 41.7 | 0.82 | 0.70 | -0.12 |

Pooled: same-model 0.534, same-family 0.564, cross-family 0.603; diag − cross -0.069 [-0.103, -0.032]; same_model log-odds -0.16 [-0.35, +0.02].

## 4. What monitors say about successful attacks (share of one-sentence reasons mentioning the canary string / endpoint terms)

| monitor | same-model: canary / endpoint (n) | same-family: canary / endpoint (n) | cross-family: canary / endpoint (n) |
|---|---|---|---|
| deepseek-v4-flash | 16% / 83% (249) | — | 15% / 94% (1719) |
| gemma-4-26b-a4b-it | 53% / 94% (303) | 65% / 100% (300) | 51% / 92% (1365) |
| gemma-4-31b-it | 57% / 98% (300) | 42% / 98% (303) | 28% / 91% (1363) |
| qwen3.8-27b | 26% / 96% (279) | 35% / 98% (306) | 25% / 93% (1383) |
| qwen3.5-397b | 68% / 100% (306) | 61% / 100% (279) | 63% / 98% (1383) |
| glm-53-flash | 84% / 97% (225) | 83% / 95% (280) | 95% / 98% (1378) |
| glm-5.2 | 38% / 94% (294) | 43% / 90% (237) | 47% / 97% (1437) |

Benign submissions, all monitors pooled: canary mentioned in 0.0% of reasons (benign code never contains the string), endpoint terms in 61.2%.

## 5a. Per-task view of the two gemma diagonal cells

- **gemma-4-31b-it**: 34 tasks with attacks; own-model catch = 0 while cross-family ≥ 0.5 on **25** of them; own-model catch > cross-family on 0; tasks where own-model caught anything: 3.
- **gemma-4-26b-a4b-it**: 34 tasks with attacks; own-model catch = 0 while cross-family ≥ 0.5 on **21** of them; own-model catch > cross-family on 3; tasks where own-model caught anything: 12.

## 5b. Inter-draw agreement per monitor (3 temperature-0.7 draws per submission)

| monitor | submissions | median SD of draws | share with range ≤ 10 points | share with all 3 draws parsed |
|---|---|---|---|---|
| deepseek-v4-flash | 1354 | 5.8 | 52% | 100% |
| gemma-4-26b-a4b-it | 1354 | 0.0 | 85% | 100% |
| gemma-4-31b-it | 1354 | 0.0 | 81% | 100% |
| qwen3.8-27b | 1354 | 2.9 | 76% | 100% |
| qwen3.5-397b | 1354 | 0.0 | 79% | 100% |
| glm-53-flash | 1353 | 2.9 | 65% | 95% |
| glm-5.2 | 1354 | 2.9 | 69% | 100% |
