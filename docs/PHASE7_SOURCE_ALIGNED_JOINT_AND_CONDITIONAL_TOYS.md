# Phase 7 — source-aligned conditional joint covariance and calibrated-toy audit

**Verified: 2026-11-07. G15 NO-GO — no real-data p-value.**

Primary 2024 ATLAS released weights: DOI https://doi.org/10.5281/zenodo.11507450. Frozen mass cut 10.594606399536133 GeV, multiplicity cut 11, track-jet pT > 5 GeV. Official 1D CERN multifold_util.py hash: cf43074fb3635b5c484dd1f35b9dc95cea938d86d206b4a2e83ab1f739e73d7f.

**Actual successful executions:**
- [Run 42390907347](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42390907347): 68 tests passed; signed v2 four-cell moments reproduced corrected R-1 source covariance and finite-MC shared-generator candidate.
- [Run 42391098288](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42391098288): 73 tests passed; 5,000 corrected Gaussian toys per scenario; no full archive download. Artifact phase7-lite-audits-12, ID 13581970715.
- Official 1D source verification: [run 42390285792](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42390285792).

## Why two reference samples need distinct treatments

The original CERN one-dimensional fill_cov_matrix uses a sample replica divisor R-1 for bootstrap covariance. Our **project-defined normalized 2×2 extension** normalizes each of the four-cell replica histograms first, then applies R-1 and the extra ensemble mean divisor /R for NN. Real versus pseudodata data-bootstrap families contain **100 and 25 actual replicas** respectively (both have 25 MC-training and 100 NN ensemble replicas). The new program src/phase7_joint_reference.py independently reconstructs the corrected covariances from signed v2 moments; all differences from R/(R-1)-rescaled archived v1 are at most 8.47e-22.

For real ATLAS vs the nominal generator, the unfolded p and generator q weights live on **the same events**. The finite-evaluation-MC contribution must therefore be REPLACED, not augmented, by their paired normalized-weight covariance:

C_paired = J_p diag(sum(w_p^2)) J_p^T + J_q diag(sum(w_q^2)) J_q^T - J_p diag(sum(w_p*w_q)) J_q^T - J_q diag(sum(w_p*w_q)) J_p^T.

The associated observable variance uses independent derivatives at p and q; in particular, the **joint log-odds gradients are different**. This is a conditional weighted-Poisson event-support model with learned weights held fixed, not the complete trained-unfolding sampling covariance.

For official pseudodata against **independent known target truth**, no shared generator term is used. Instead, its finite-MC contribution is C_truth = (I-q1^T) diag(q_i^2/N_eff,i) (I-1q^T). We retain all 29 unfolded source components. In the real case we also retain all 29 original source identities, replacing the single finite-evaluation-MC term, and assume the other 28 source families do not fluctuate with the generator reference.

All four fixed DD/Sherpa models use **signed count-level shifts**, a normalization Jacobian, and either full source correlation or four independent raw-count nuisances (source alternatives explicitly discussed in the publication User Guide). The official one-dimensional Sherpa smoother does NOT provide a unique 2D kernel; no arbitrary flattening is used.

## Executed conditional joint 2D diagnostics (NOT p-values)

| Prespecified DD/Sherpa source correlation | Pseudodata vs known target quadratic | Real vs shared nominal generator quadratic | Real joint log-odds conditional SE |
|---|---:|---:|---:|
| Both fully correlated | 1.789662 | 1.614189 | 0.09232094 |
| DD four-bin independent, Sherpa full | 1.744988 | 1.436777 | 0.10642217 |
| DD full, Sherpa four-bin independent | 2.146973 | 1.576265 | 0.13690379 |
| Both four-bin independent | 2.565135 | 1.327629 | 0.14678273 |

These uncalibrated quadratic diagnostics describe model sensitivity only. No real-model selection or hypothesis p-value was computed.

## R-1 corrected conditional Gaussian null simulation

The separate src/phase7_conditional_null.py simulates independent Gaussian source perturbations with observed covariance held as the assumed truth, re-estimating each replica covariance in EVERY trial with divisor **R-1** and dividing the NN mean covariance by R. Its null residuals are simulated independently of the estimated replica covariance. All other sources, source dependence, generator/measurement learned-weight dependence and nuisance amplitudes are held fixed. It simulates **5,000** trials PER scenario, with a reference three-contrast chi-square 95% threshold of 7.814727903251179. Wilson binomial intervals reflect only simulation error:

| DD/Sherpa model | Pseudodata-source toy rejection at reference threshold | Real-source toy rejection |
|---|---:|---:|
| Both fully correlated | 4.78% | 4.98% |
| DD four-bin, Sherpa full | 5.54% | 5.30% |
| DD full, Sherpa four-bin | 4.52% | 5.16% |
| Both four-bin | 4.54% | 4.72% |

This is **conditional Gaussian behaviour** by design, NOT genuine ATLAS repeated-experiment false-positive rate, NOT empirical detector-level unfolding coverage and NOT real-data p-values. The older Gaussian-toy script used the R population divisor; its results remain a historical legacy stage, not retroactively source-aligned.

## Gate decisions and actionable work

- **G5 PROVISIONAL**: Exact 1D helper source, replica R-1, signed DD/Sherpa and finite-MC algebra are reviewed. However the specific 2D family-inclusion, DD/Sherpa correlations, learned-weight covariance and generator-related systematic dependence are NOT independently validated.
- **G8 UNVERIFIED**: Conditional Gaussian simulations support numerical calibration under assumptions, not independent pseudo-experiment frequentist coverage of the released unfolding.
- **G12 UNVERIFIED**: Four 2D nuisance-correlation alternatives remain pre-specified and stress-tested on the single published pseudodata target, but selection of a verified 2D model is still missing.
- **G15 NO-GO**: No full physically calibrated compatibility p-value or sigma claim can be made.

Next useful step: examine the actual **released replica-shape distributions** for Gaussianity/non-Gaussianity and evaluate a complementary empirical-bootstrap-conditional null, without conflating it with repeated unfolding. Further improvement requires independently justified source correlations and, if claiming experimental coverage, repeated full pseudo-measurements with independent detector-level unfolding. No further 3.65 GB data transfer is required for existing frozen four-cell calculations.

**Reproduce using only small committed derived files:**

- python -m pytest -q tests/test_phase7_joint_reference.py tests/test_phase7_conditional_null.py
- python -m src.phase7_joint_reference --v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 --out outputs/joint-reference
- python -m src.phase7_conditional_null --v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 --out outputs/conditional-toys --toys 5000

**G15 NO-GO. No real-data p-value was evaluated.**


## Subsequent empirical-replica stress test — actual frozen source shapes (run 42391320503)

[Verified CI run 42391320503](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42391320503) succeeded with **77 tests passed**. Artifact: phase7-lite-audits-13, ID **13582115356**. The new source src/phase7_empirical_replica_null.py reads all original frozen normalized four-cell replica shapes from v2, with the actual counts (real data bootstrap 100; pseudo bootstrap 25; MC 25; NN 100). It validates exact equality of the unbiased replica-shape source matrices before simulation.

The distinct HYBRID conditional null resamples centered real source-family shape offsets, scaling their sample covariance to match the R-1 covariance. The NN mean is approximated by resampling R empirical network offsets and averaging, with the corresponding finite empirical-population correction. Remaining measured source terms are treated as fixed-covariance Gaussian draws. Unlike the previous all-Gaussian model, this probes observed bootstrap skewness; however it still reuses replicas of **one** unfolded dataset and does not recreate independent detector-level measurements or retraining.

**10,000 trials per scenario; nominal reference three-contrast 95% threshold 7.8147279.**

| Source correlation model | Pseudodata empirical-hybrid rejection | Real-data-source empirical-hybrid rejection |
|---|---:|---:|
| Both fully correlated | 4.95% | 5.55% |
| DD four independent, Sherpa full | 4.82% | 5.12% |
| DD full, Sherpa four independent | 5.26% | 5.01% |
| Both four independent | 4.99% | 4.82% |

Descriptive skewness of three fixed contrast coordinates (no normality-test decision): pseudodata data-bootstrap with R=25: **[-0.808, -0.296, +0.013]**; real data-bootstrap with R=100: **[+0.183, +0.178, +0.210]**. NN ensemble has 100 replicas and relatively modest marginal skew in both samples. With R=25, sample skewness and kurtosis estimates are noisy, so do not overinterpret. Exact per-family kurtosis and Monte Carlo Wilson intervals are in replica-null/empirical_replica_null.json in the referenced Actions artifact.

**Scientific conclusion:** The hybrid conditional null has not exposed a gross non-Gaussian discrepancy relative to the separately simulated source-wise Gaussian null at this threshold. This is NOT a measurement of ATLAS coverage, a source-correlation validation, a formal goodness-of-fit test, or a permission to report real-data p-values. G5 remains PROVISIONAL; G8 and G12 remain experimentally UNVERIFIED; G15 NO-GO. No additional original ATLAS archive download was required.
