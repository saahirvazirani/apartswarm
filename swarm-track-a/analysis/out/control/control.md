# Control-protocol view and calibration-free robustness

## 1. Audit-budget frontier (AI-control framing: audit the top-b% most suspicious; catch = audited)

Budget to catch 90 % of a policy's successful attacks, and area under the safety curve (AUSC, higher = safer at low budget).

| policy | own-model monitor | trusted glm-53-flash | best cross-family | own AUSC | glm-53-flash AUSC |
|---|---|---|---|---|---|
| deepseek-v4-flash | 41% | 39% | 39% (glm-53-flash) | 0.787 | 0.785 |
| gemma-4-26b-a4b-it | 54% | 43% | 43% (glm-53-flash) | 0.739 | 0.763 |
| gemma-4-31b-it | 59% | 45% | 32% (qwen3.5-397b) | 0.724 | 0.756 |
| qwen3.8-27b | 50% | 43% | 43% (glm-53-flash) | 0.752 | 0.763 |
| qwen3.5-397b | 55% | 45% | 45% (glm-53-flash) | 0.788 | 0.759 |
| glm-53-flash | 40% | 40% | 28% (gemma-31b) | 0.789 | 0.789 |
| glm-5.2 | 47% | 47% | 48% (qwen3.5-397b) | 0.757 | 0.757 |

Figure 3: `fig3_audit_budget.png`. Trusted monitor = glm-53-flash (cheapest glm). Reading: for gemma policies the own-model monitor needs a very large audit budget to reach 90 % safety, while the cheap trusted monitor reaches it at a small budget; for non-gemma policies own and trusted are comparable.

## 2. Calibration-free robustness

**Single global threshold per monitor** (one threshold for the whole row at 5% pooled FPR, not per policy):
- same-model catch 0.570, same-family 0.568, cross-family 0.592
- diagonal − cross-family -0.022 [-0.060, +0.016] (task bootstrap)

The gap is of the same sign and magnitude under a global threshold as under per-pair calibration, so it is not an artifact of per-pair thresholds. The AUROC matrix (`analysis/out/full/matrix.md`) is the fully threshold-free view; there the diagonal dip is ≤ 0.02–0.03, i.e. the effect is an operating-point (calibration) phenomenon, consistent across both threshold schemes.
