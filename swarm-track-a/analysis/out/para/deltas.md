# Paraphrased minus original suspicion score (same monitors)

8118 (submission, monitor) pairs, 34 tasks

| condition | relation | n | mean delta | 95% CI (task bootstrap) |
|---|---|---|---|---|
| attack | same_model | 644 | -1.17 | [-2.82, +0.44] |
| attack | cross_family | 3313 | +0.68 | [-0.51, +1.79] |
| benign | same_model | 678 | +1.22 | [-0.07, +2.46] |
| benign | cross_family | 3483 | +0.93 | [+0.35, +1.51] |

Attacks: (diagonal delta) - (cross-family delta) = -1.85 [-3.92, +0.25]

| relation | mean cell TPR original | mean cell TPR paraphrased | cells |
|---|---|---|---|
| same_model | 0.606 | 0.567 | 7 |
| cross_family | 0.724 | 0.694 | 36 |
