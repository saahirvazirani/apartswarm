# Gemma-block GLM decomposition (POST-HOC)

*Added Sun 2026-11-08 PM, after the Stage-1 matrix was seen; it decomposes the pre-registered pooled
`same_model` term, it does not replace the pre-registered test (`analysis/out/full/fit.md`).*

`catch ~ C(policy) + C(monitor) + gemma_block + diag_nongemma + samefam_nongemma`, logistic,
task-clustered SEs; 4549 (attack submission, monitor) units, 34 tasks.

| term | log-odds | 95% CI | OR | OR 95% CI | p |
|---|---|---|---|---|---|
| gemma_block | -1.229 | [-1.667, -0.791] | 0.29 | [0.19, 0.45] | 3.8e-08 |
| diag_nongemma | +0.073 | [-0.243, +0.389] | 1.08 | [0.78, 1.47] | 0.65 |
| samefam_nongemma | -0.004 | [-0.305, +0.297] | 1.00 | [0.74, 1.35] | 0.98 |

Reading: the non-gemma diagonal is a precise null and the non-gemma same-family term is zero — the entire
pooled same-model effect of the pre-registered fit is carried by the gemma policy × gemma monitor block
(diagonal and same-family cells alike). The block p-value survives a Bonferroni correction over the 7
post-hoc per-monitor leniency comparisons. Capability is controlled additively (log-odds scale) by the
policy and monitor main effects; a policy-style × monitor-capability interaction specific to this block
remains observationally indistinguishable from family identity (stated in Limitations).
