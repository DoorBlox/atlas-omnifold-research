> **SUPERSEDED for real-data replica-count calibration (2026-11-07).** The first real-data Gaussian toy study incorrectly assumed 25 rather than 100 data-bootstrap replicas. Its old real-data toy result (5.25% plug-in rejection) must not be cited as corrected. See [verified corrected audit and calibration](PHASE7_REFERENCE_AUDIT_CORRECTED_CALIBRATION.md) and [GitHub run #42377662887](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42377662887): corrected real-data 4.60%, pseudodata 4.78%. Original results below are kept for historical provenance only. G15 remains **NO-GO**.

# Phase 7 Gaussian finite-covariance toy calibration — executed checkpoint

**Execution:** [GitHub Actions run 42331285712](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42331285712), artifact `phase7-preflight-25`, file `finite_covariance_toy_calibration.json`. Source: nominal real and pseudodata source-wise covariances from runs 42324639484 and 42327464929. **19 GitHub regression tests passed.**

## What was simulated

Three-dimensional zero-mean Gaussian residuals were generated with the observed provisional ATLAS 2×2 contrast covariance treated as the **true fixed covariance**. For each simulated residual, the covariance contributions from the 25 data-bootstrap replicas, 25 MC-training replicas and 100 neural-network ensemble members were re-estimated from independent Gaussian draws. All other source covariances—including the particularly important Sherpa and DD two-point sources—were **fixed** at their observed values. The comparison was between known-covariance and plug-in-estimated covariance quadratic statistics, at the `chi2(df=3)` nominal 95th-percentile threshold, 7.814727903251179.

This does **not** simulate ATLAS detector events, training, unfolding, repeated experiments, shared-generator covariance, or uncertain systematic correlations. The residual and replica draw families are independent by model assumption, not an experimentally established property.

## Executed simulation results (10,000 toys per scenario)

| Assumed covariance | Known-C rejection | Re-estimated-replica rejection | Known-C empirical 95th | Plug-in empirical 95th |
|---|---:|---:|---:|---:|
| Real-data provisional sources | 5.20% | 5.25% | 7.9065 | 7.9208 |
| Official pseudodata provisional sources | 4.79% | 4.78% | 7.6782 | 7.6879 |
| Pseudodata with Sherpa omitted (extreme *stress test*, not a permissible primary model) | 4.37% | 4.40% | 7.5431 | 7.5899 |

Binomial Monte Carlo standard error near 5% with 10,000 toys is about 0.22 percentage points; small deviations from 5% are expected by finite simulation.

These results show that, **for the assumed Gaussian model with fixed non-replica components**, re-estimation of the replica-family components has only a modest effect on the toy null distribution. That is compatible with the fact that the observed covariance is substantially influenced by fixed one-shift and alternative-support source components.

## Gate status

- **G8:** conditional-model toy run **EXECUTED**, but **ATLAS-specific repeated-sampling calibration UNVERIFIED**.
- **G11:** single official pseudodata known-truth closure **EXECUTED**, not repeated-sampling coverage.
- **G5/G12:** Sherpa, DD and 2D source-correlation assumptions **UNVERIFIED**; strong sensitivity to the Sherpa component persists.
- **G15: NO-GO** for the final real-data p-value.

**Never replace an experimentally validated covariance model with the toy model or interpret this report as a detector-level calibration.** Do not select a covariance scenario based on the resulting apparent compatibility.

## Next defensible options

1. Seek/reproduce the official 1D covariance machinery using `multifold_util.py` and the notebook-provided systematics, and explain any deviations in the 2D extension.
2. Validate source-specific covariance model alternatives on pseudodata using a predefined rule. Report sensitivity; do not choose models post hoc.
3. If repeated ATLAS-like null experiments remain unavailable, close the KTI as a covariance-aware descriptive comparison with an explicit NO-GO for formal inferential claims.
