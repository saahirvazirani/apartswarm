# Robustness of the identity effect (post-hoc)

## Per-monitor leniency index (cross-family mean TPR − TPR on own model; AUROC version alongside)

| monitor | TPR own | TPR cross-family (mean) | leniency (TPR) | AUROC own | AUROC cross | leniency (AUROC) |
|---|---|---|---|---|---|---|
| deepseek-v4-flash | 0.96 | 0.80 | -0.16 | 0.977 | 0.953 | -0.024 |
| gemma-4-26b-a4b-it | 0.21 | 0.59 | +0.37 | 0.929 | 0.945 | +0.016 |
| gemma-4-31b-it | 0.06 | 0.54 | +0.48 | 0.867 | 0.875 | +0.007 |
| qwen3.8-27b | 0.43 | 0.58 | +0.16 | 0.902 | 0.936 | +0.034 |
| qwen3.5-397b | 0.69 | 0.73 | +0.04 | 0.949 | 0.971 | +0.022 |
| glm-53-flash | 1.00 | 0.98 | -0.02 | 0.997 | 0.996 | -0.001 |
| glm-5.2 | 0.83 | 0.83 | -0.01 | 0.983 | 0.971 | -0.012 |

## Per-policy index (cross-family monitors' mean TPR on p − own monitor's TPR on p)

| policy | TPR by own monitor | TPR by cross-family monitors (mean) | difference |
|---|---|---|---|
| deepseek-v4-flash | 0.96 | 0.90 | -0.06 |
| gemma-4-26b-a4b-it | 0.21 | 0.81 | +0.60 |
| gemma-4-31b-it | 0.06 | 0.63 | +0.57 |
| qwen3.8-27b | 0.43 | 0.60 | +0.18 |
| qwen3.5-397b | 0.69 | 0.66 | -0.04 |
| glm-53-flash | 1.00 | 0.82 | -0.18 |
| glm-5.2 | 0.83 | 0.61 | -0.22 |

## Leave-one-family-out refits (drop every unit whose policy or monitor is in the family)

| dropped family | units | same_model log-odds [95% CI] | same_family log-odds [95% CI] | same-model catch | cross-family catch | diag − cross [95% CI] |
|---|---|---|---|---|---|---|
| (none) | 4443 | -0.44 [-0.65, -0.23] | +0.01 [-0.23, +0.24] | 0.570 | 0.714 | -0.144 [-0.176, -0.112] |
| deepseek | 3346 | -0.47 [-0.69, -0.26] | -0.01 [-0.26, +0.24] | 0.516 | 0.657 | -0.141 [-0.179, -0.105] |
| gemma | 2180 | -0.08 [-0.33, +0.17] | +0.10 [-0.22, +0.42] | 0.768 | 0.822 | -0.054 [-0.088, -0.022] |
| glm | 2330 | -0.40 [-0.63, -0.16] | +0.20 [-0.04, +0.44] | 0.448 | 0.605 | -0.157 [-0.198, -0.119] |
| qwen | 2223 | -1.25 [-1.70, -0.80] | -0.58 [-1.01, -0.15] | 0.571 | 0.813 | -0.242 [-0.281, -0.202] |

## Drop-one-diagonal-cell sensitivity (remove one monitor's own-model units only)

| removed diagonal cell | same_model log-odds [95% CI] | diag − cross [95% CI] |
|---|---|---|
| deepseek-v4-flash→deepseek-v4-flash | -0.46 [-0.67, -0.25] | -0.198 [-0.234, -0.160] |
| gemma-4-26b-a4b-it→gemma-4-26b-a4b-it | -0.25 [-0.47, -0.03] | -0.079 [-0.113, -0.046] |
| gemma-4-31b-it→gemma-4-31b-it | -0.32 [-0.54, -0.09] | -0.048 [-0.080, -0.012] |
| qwen3.8-27b→qwen3.8-27b | -0.56 [-0.80, -0.31] | -0.121 [-0.156, -0.087] |
| qwen3.5-397b→qwen3.5-397b | -0.56 [-0.82, -0.30] | -0.168 [-0.202, -0.130] |
| glm-53-flash→glm-53-flash | -0.46 [-0.67, -0.25] | -0.200 [-0.233, -0.164] |
| glm-5.2→glm-5.2 | -0.51 [-0.73, -0.28] | -0.191 [-0.225, -0.155] |
