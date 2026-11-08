# Two-way fit (blind; attack stage = polished; FPR 5%; 4549 units, 34 tasks)

- **same_model** (logistic, cluster-task SE): log-odds -0.555 (95% CI -0.751, -0.360), OR 0.57 [0.47, 0.70], p=2.56e-08
- **same_family_diff_model** (logistic, cluster-task SE): log-odds -0.304 (95% CI -0.500, -0.107), OR 0.74 [0.61, 0.90], p=0.00245
- **same_model** (linear probability, cluster-task SE): -0.111 catch-rate points (95% CI -0.143, -0.080), p=5.8e-12
- **same_family_diff_model** (linear probability, cluster-task SE): -0.064 catch-rate points (95% CI -0.094, -0.034), p=2.7e-05
- score model same_model: -1.68 points (95% CI -3.41, +0.06), p=0.0577
- score model same_family_diff_model: -0.31 points (95% CI -2.25, +1.63), p=0.755

Permutation (2000 shuffles of policy labels within task): observed diag−cross = -0.134; one-sided p(leniency) = 0.0000; two-sided p = 0.0000

Task bootstrap (95% percentile CI):
- same-model catch rate 0.584 [0.540, 0.630]
- same-family catch rate 0.591 [0.539, 0.651]
- cross-family catch rate 0.718 [0.675, 0.762]
- diagonal − cross-family -0.134 [-0.168, -0.100]
