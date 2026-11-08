# Robustness of the identity effect (post-hoc)

## Per-monitor leniency index (cross-family mean TPR − TPR on own model; AUROC version alongside)

| monitor | TPR own | TPR cross-family (mean) | leniency (TPR) | AUROC own | AUROC cross | leniency (AUROC) |
|---|---|---|---|---|---|---|
| deepseek-v4-flash | 0.88 | 0.72 | -0.15 | 0.935 | 0.923 | -0.011 |
| gemma-4-26b-a4b-it | 0.22 | 0.53 | +0.32 | 0.912 | 0.920 | +0.009 |
| gemma-4-31b-it | 0.03 | 0.56 | +0.53 | 0.859 | 0.883 | +0.024 |
| qwen3.8-27b | 0.47 | 0.61 | +0.13 | 0.922 | 0.938 | +0.015 |
| qwen3.5-397b | 0.78 | 0.80 | +0.02 | 0.955 | 0.970 | +0.015 |
| glm-53-flash | 1.00 | 0.98 | -0.02 | 0.998 | 0.996 | -0.002 |
| glm-5.2 | 0.86 | 0.86 | +0.00 | 0.976 | 0.977 | +0.001 |

## Per-policy index (cross-family monitors' mean TPR on p − own monitor's TPR on p)

| policy | TPR by own monitor | TPR by cross-family monitors (mean) | difference |
|---|---|---|---|
| deepseek-v4-flash | 0.88 | 0.94 | +0.06 |
| gemma-4-26b-a4b-it | 0.22 | 0.84 | +0.62 |
| gemma-4-31b-it | 0.03 | 0.67 | +0.64 |
| qwen3.8-27b | 0.47 | 0.60 | +0.12 |
| qwen3.5-397b | 0.78 | 0.67 | -0.12 |
| glm-53-flash | 1.00 | 0.73 | -0.27 |
| glm-5.2 | 0.86 | 0.59 | -0.26 |

## Leave-one-family-out refits (drop every unit whose policy or monitor is in the family)

| dropped family | units | same_model log-odds [95% CI] | same_family log-odds [95% CI] | same-model catch | cross-family catch | diag − cross [95% CI] |
|---|---|---|---|---|---|---|
| (none) | 4591 | -0.55 [-0.74, -0.36] | -0.30 [-0.49, -0.10] | 0.586 | 0.719 | -0.133 [-0.168, -0.100] |
| deepseek | 3437 | -0.47 [-0.67, -0.28] | -0.27 [-0.48, -0.06] | 0.544 | 0.671 | -0.128 [-0.167, -0.093] |
| gemma | 2274 | -0.06 [-0.37, +0.26] | -0.26 [-0.53, +0.01] | 0.791 | 0.814 | -0.023 [-0.060, +0.015] |
| glm | 2395 | -0.61 [-0.84, -0.37] | -0.19 [-0.42, +0.04] | 0.463 | 0.631 | -0.167 [-0.207, -0.126] |
| qwen | 2304 | -1.45 [-1.74, -1.15] | -0.74 [-1.10, -0.39] | 0.565 | 0.792 | -0.227 [-0.258, -0.195] |

## Drop-one-diagonal-cell sensitivity (remove one monitor's own-model units only)

| removed diagonal cell | same_model log-odds [95% CI] | diag − cross [95% CI] |
|---|---|---|
| deepseek-v4-flash→deepseek-v4-flash | -0.48 [-0.68, -0.29] | -0.176 [-0.214, -0.140] |
| gemma-4-26b-a4b-it→gemma-4-26b-a4b-it | -0.39 [-0.63, -0.14] | -0.066 [-0.108, -0.029] |
| gemma-4-31b-it→gemma-4-31b-it | -0.34 [-0.55, -0.13] | -0.033 [-0.072, +0.003] |
| qwen3.8-27b→qwen3.8-27b | -0.75 [-0.94, -0.56] | -0.114 [-0.151, -0.083] |
| qwen3.5-397b→qwen3.5-397b | -0.69 [-0.89, -0.50] | -0.170 [-0.204, -0.139] |
| glm-53-flash→glm-53-flash | -0.58 [-0.78, -0.39] | -0.189 [-0.225, -0.154] |
| glm-5.2→glm-5.2 | -0.64 [-0.87, -0.41] | -0.181 [-0.221, -0.146] |
