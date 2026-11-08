# Robustness of the identity effect (post-hoc)

## Per-monitor leniency index (cross-family mean TPR − TPR on own model; AUROC version alongside)

| monitor | TPR own | TPR cross-family (mean) | leniency (TPR) | AUROC own | AUROC cross | leniency (AUROC) |
|---|---|---|---|---|---|---|
| deepseek-v4-flash | 0.88 | 0.72 | -0.15 | 0.932 | 0.923 | -0.010 |
| gemma-4-26b-a4b-it | 0.22 | 0.53 | +0.31 | 0.912 | 0.920 | +0.008 |
| gemma-4-31b-it | 0.03 | 0.56 | +0.53 | 0.859 | 0.883 | +0.024 |
| qwen3.8-27b | 0.47 | 0.61 | +0.13 | 0.922 | 0.937 | +0.015 |
| qwen3.5-397b | 0.78 | 0.80 | +0.02 | 0.955 | 0.969 | +0.014 |
| glm-53-flash | 1.00 | 0.98 | -0.02 | 0.998 | 0.996 | -0.002 |
| glm-5.2 | 0.86 | 0.86 | +0.00 | 0.976 | 0.977 | +0.001 |

## Per-policy index (cross-family monitors' mean TPR on p − own monitor's TPR on p)

| policy | TPR by own monitor | TPR by cross-family monitors (mean) | difference |
|---|---|---|---|
| deepseek-v4-flash | 0.88 | 0.94 | +0.07 |
| gemma-4-26b-a4b-it | 0.22 | 0.84 | +0.62 |
| gemma-4-31b-it | 0.03 | 0.67 | +0.64 |
| qwen3.8-27b | 0.47 | 0.60 | +0.12 |
| qwen3.5-397b | 0.78 | 0.67 | -0.12 |
| glm-53-flash | 1.00 | 0.72 | -0.28 |
| glm-5.2 | 0.86 | 0.59 | -0.26 |

## Leave-one-family-out refits (drop every unit whose policy or monitor is in the family)

| dropped family | units | same_model log-odds [95% CI] | same_family log-odds [95% CI] | same-model catch | cross-family catch | diag − cross [95% CI] |
|---|---|---|---|---|---|---|
| (none) | 4549 | -0.56 [-0.75, -0.36] | -0.30 [-0.50, -0.11] | 0.584 | 0.718 | -0.134 [-0.170, -0.100] |
| deepseek | 3419 | -0.47 [-0.67, -0.27] | -0.28 [-0.49, -0.07] | 0.543 | 0.670 | -0.127 [-0.168, -0.092] |
| gemma | 2249 | -0.07 [-0.39, +0.25] | -0.27 [-0.54, +0.00] | 0.788 | 0.813 | -0.025 [-0.061, +0.013] |
| glm | 2375 | -0.61 [-0.86, -0.37] | -0.20 [-0.43, +0.03] | 0.461 | 0.630 | -0.169 [-0.209, -0.124] |
| qwen | 2274 | -1.47 [-1.76, -1.17] | -0.77 [-1.12, -0.41] | 0.562 | 0.790 | -0.229 [-0.260, -0.194] |

## Drop-one-diagonal-cell sensitivity (remove one monitor's own-model units only)

| removed diagonal cell | same_model log-odds [95% CI] | diag − cross [95% CI] |
|---|---|---|
| deepseek-v4-flash→deepseek-v4-flash | -0.48 [-0.68, -0.28] | -0.175 [-0.213, -0.136] |
| gemma-4-26b-a4b-it→gemma-4-26b-a4b-it | -0.40 [-0.64, -0.15] | -0.067 [-0.103, -0.031] |
| gemma-4-31b-it→gemma-4-31b-it | -0.34 [-0.56, -0.13] | -0.033 [-0.069, +0.005] |
| qwen3.8-27b→qwen3.8-27b | -0.75 [-0.95, -0.56] | -0.115 [-0.150, -0.083] |
| qwen3.5-397b→qwen3.5-397b | -0.70 [-0.89, -0.50] | -0.171 [-0.205, -0.141] |
| glm-53-flash→glm-53-flash | -0.59 [-0.79, -0.38] | -0.189 [-0.224, -0.154] |
| glm-5.2→glm-5.2 | -0.64 [-0.88, -0.41] | -0.182 [-0.220, -0.147] |
