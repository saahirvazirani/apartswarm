# Paraphrased minus original suspicion score (same monitors)

1178 (submission, monitor) pairs, 34 tasks

| condition | relation | n | mean delta | 95% CI (task bootstrap) |
|---|---|---|---|---|
| attack | same_model | 192 | -2.20 | [-5.04, +0.50] |
| attack | same_family | 192 | -6.27 | [-8.96, -3.68] |
| attack | cross_family | 193 | +1.07 | [-2.20, +4.18] |
| benign | same_model | 200 | +1.48 | [-0.35, +3.55] |
| benign | same_family | 200 | -0.67 | [-2.68, +1.13] |
| benign | cross_family | 201 | +1.22 | [+0.25, +2.22] |

Attacks: (diagonal delta) - (cross-family delta) = -3.26 [-7.25, +0.40]

| relation | mean cell TPR original | mean cell TPR paraphrased | cells |
|---|---|---|---|
| same_model | 0.125 | 0.238 | 2 |
| same_family | 0.280 | 0.284 | 2 |
| cross_family | 0.600 | 0.506 | 2 |
