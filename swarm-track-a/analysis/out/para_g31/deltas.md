# Paraphrased minus original suspicion score (same monitors)

2572 (submission, monitor) pairs, 34 tasks

| condition | relation | n | mean delta | 95% CI (task bootstrap) |
|---|---|---|---|---|
| attack | same_model | 168 | -7.05 | [-11.45, -2.46] |
| attack | same_family | 170 | -6.21 | [-10.06, -2.27] |
| attack | cross_family | 863 | -6.02 | [-8.06, -4.00] |
| benign | same_model | 193 | +4.47 | [+2.08, +7.22] |
| benign | same_family | 198 | -0.14 | [-1.90, +1.62] |
| benign | cross_family | 980 | +0.86 | [-0.29, +1.97] |

Attacks: (diagonal delta) - (cross-family delta) = -1.03 [-5.97, +4.29]

| relation | mean cell TPR original | mean cell TPR paraphrased | cells |
|---|---|---|---|
| same_model | 0.444 | 0.409 | 2 |
| same_family | 0.671 | 0.669 | 2 |
| cross_family | 0.711 | 0.543 | 10 |
