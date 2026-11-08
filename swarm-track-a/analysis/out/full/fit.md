# Two-way fit (blind; FPR 5%; 3215 units, 34 tasks)

- **same_model** (logistic, cluster-task SE): log-odds -0.559 (95% CI -0.810, -0.307), OR 0.57 [0.44, 0.74], p=1.36e-05
- **same_family_diff_model** (logistic, cluster-task SE): log-odds -0.752 (95% CI -1.111, -0.392), OR 0.47 [0.33, 0.68], p=4.13e-05
- **same_model** (linear probability, cluster-task SE): -0.093 catch-rate points (95% CI -0.128, -0.058), p=1.39e-07
- **same_family_diff_model** (linear probability, cluster-task SE): -0.140 catch-rate points (95% CI -0.184, -0.096), p=2.88e-10
- score model same_model: -1.50 points (95% CI -3.91, +0.90), p=0.221
- score model same_family_diff_model: -0.85 points (95% CI -3.28, +1.57), p=0.49

Permutation (2000 shuffles of policy labels within task): observed diag−cross = -0.045; one-sided p(leniency) = 0.0550; two-sided p = 0.0550

Task bootstrap (95% percentile CI):
- same-model catch rate 0.728 [0.680, 0.777]
- same-family catch rate 0.596 [0.543, 0.653]
- cross-family catch rate 0.773 [0.736, 0.810]
- diagonal − cross-family -0.045 [-0.081, -0.010]
