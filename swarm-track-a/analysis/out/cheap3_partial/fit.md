# Two-way fit (blind; FPR 5%; 770 units, 34 tasks)

- **same_model** (logistic, cluster-task SE): log-odds -1.987 (95% CI -2.710, -1.264), OR 0.14 [0.07, 0.28], p=7.25e-08
- **same_model** (linear probability, cluster-task SE): -0.183 catch-rate points (95% CI -0.237, -0.130), p=2.07e-11
- score model same_model: -1.60 points (95% CI -4.94, +1.75), p=0.349

Permutation (300 shuffles of policy labels within task): observed diag−cross = -0.211; one-sided p(leniency) = 0.0000; two-sided p = 0.0000

Task bootstrap (95% percentile CI):
- same-model catch rate 0.656 [0.602, 0.709]
- same-family catch rate nan [nan, nan]
- cross-family catch rate 0.868 [0.828, 0.903]
- diagonal − cross-family -0.211 [-0.267, -0.160]
