# Two-way fit (blind; attack stage = polished; FPR 5%; 4591 units, 34 tasks)

- **same_model** (logistic, cluster-task SE): log-odds -0.552 (95% CI -0.742, -0.362), OR 0.58 [0.48, 0.70], p=1.23e-08
- **same_family_diff_model** (logistic, cluster-task SE): log-odds -0.298 (95% CI -0.495, -0.100), OR 0.74 [0.61, 0.90], p=0.00308
- **same_model** (linear probability, cluster-task SE): -0.112 catch-rate points (95% CI -0.142, -0.081), p=1.36e-12
- **same_family_diff_model** (linear probability, cluster-task SE): -0.063 catch-rate points (95% CI -0.093, -0.034), p=2.6e-05
- score model same_model: -1.79 points (95% CI -3.53, -0.06), p=0.0425
- score model same_family_diff_model: -0.36 points (95% CI -2.29, +1.57), p=0.715

Permutation (2000 shuffles of policy labels within task): observed diag−cross = -0.133; one-sided p(leniency) = 0.0000; two-sided p = 0.0000

Task bootstrap (95% percentile CI):
- same-model catch rate 0.586 [0.542, 0.633]
- same-family catch rate 0.593 [0.541, 0.652]
- cross-family catch rate 0.719 [0.678, 0.763]
- diagonal − cross-family -0.133 [-0.165, -0.101]
