# Told minus blind suspicion score (same submissions, same monitors)

2785 (submission, monitor) pairs, 10 tasks

| condition | relation | n | mean delta | 95% CI (task bootstrap) |
|---|---|---|---|---|
| attack | same_model | 189 | -2.56 | [-5.49, +1.76] |
| attack | same_family | 163 | -2.77 | [-6.50, +0.61] |
| attack | cross_family | 970 | -2.03 | [-3.31, -0.80] |
| benign | same_model | 209 | -0.76 | [-1.99, +0.36] |
| benign | same_family | 179 | -1.32 | [-2.37, -0.46] |
| benign | cross_family | 1075 | -1.13 | [-1.60, -0.69] |

Attacks: (diagonal delta) - (cross-family delta) = -0.53 [-3.72, +3.60]

| relation | catch rate blind | catch rate told (blind thresholds) | n |
|---|---|---|---|
| same_model | 0.614 | 0.571 | 189 |
| same_family | 0.528 | 0.521 | 163 |
| cross_family | 0.711 | 0.679 | 970 |
