# Two-way fit (blind; attack stage = raw; FPR 5%; 4443 units, 34 tasks)

- **same_model** (logistic, cluster-task SE): log-odds -0.444 (95% CI -0.654, -0.234), OR 0.64 [0.52, 0.79], p=3.3e-05
- **same_family_diff_model** (logistic, cluster-task SE): log-odds +0.005 (95% CI -0.232, +0.243), OR 1.01 [0.79, 1.27], p=0.965
- **same_model** (linear probability, cluster-task SE): -0.115 catch-rate points (95% CI -0.148, -0.083), p=3.73e-12
- **same_family_diff_model** (linear probability, cluster-task SE): -0.032 catch-rate points (95% CI -0.070, +0.006), p=0.0985
- score model same_model: -0.88 points (95% CI -2.81, +1.04), p=0.369
- score model same_family_diff_model: -0.80 points (95% CI -2.74, +1.14), p=0.42

Permutation (2000 shuffles of policy labels within task): observed diag−cross = -0.144; one-sided p(leniency) = 0.0000; two-sided p = 0.0000

Task bootstrap (95% percentile CI):
- same-model catch rate 0.570 [0.526, 0.620]
- same-family catch rate 0.606 [0.547, 0.662]
- cross-family catch rate 0.714 [0.673, 0.755]
- diagonal − cross-family -0.144 [-0.177, -0.112]
