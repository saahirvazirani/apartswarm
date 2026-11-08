# Paraphrased minus original suspicion score (same monitors)

598 (submission, monitor) pairs, 34 tasks

| condition | relation | n | mean delta | 95% CI (task bootstrap) |
|---|---|---|---|---|
| attack | same_model | 98 | -2.68 | [-5.73, +0.40] |
| attack | same_family | 97 | -9.46 | [-13.97, -5.39] |
| attack | cross_family | 97 | +1.47 | [-3.70, +6.53] |
| benign | same_model | 102 | +0.23 | [-1.60, +2.31] |
| benign | same_family | 102 | -0.08 | [-2.35, +1.59] |
| benign | cross_family | 102 | +0.81 | [+0.10, +1.75] |

Attacks: (diagonal delta) - (cross-family delta) = -4.15 [-9.97, +1.50]

| relation | mean cell TPR original | mean cell TPR paraphrased | cells |
|---|---|---|---|
| same_model | 0.125 | 0.571 | 2 |
| same_family | 0.280 | 0.515 | 2 |
| cross_family | 0.600 | 0.780 | 2 |
