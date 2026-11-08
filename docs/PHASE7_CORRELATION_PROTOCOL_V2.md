# Phase 7 v2 — Pre-specified four-cell two-point correlation protocols

**Date:** 2026-11-07. **Scope:** source-backed, **provisional 2D** uncertainty-model sensitivity on the immutable generator-defined four-cell partition. **G5/G8/G12 not validated; G15 NO-GO.**

## Primary publication source (read before interpreting covariance)

ATLAS Collaboration, *Simultaneous Unbinned Differential Cross-Section Measurement of Twenty-Four Z+jets Kinematic Observables with the ATLAS Detector*, Phys. Rev. Lett. **133** (2024) 261803, DOI [10.1103/PhysRevLett.133.261803](https://doi.org/10.1103/PhysRevLett.133.261803). See the [paper's Supplemental Material / User Guide](https://cds.cern.ch/record/2899105/files/2405.20041.pdf?version=5), **Section 2: Usage recommendations**, especially recommendation 5.

The official publication states:

1. The default recommended treatment is **fully correlated systematic source uncertainties across bins**.
2. **Two-point** unfolding sources need special care because their internal correlations are not known. For **four bins**, the guide explicitly discusses treating source-bin contributions as **four separate nuisance components** (fully uncorrelated across those bins) as a possible alternative.
3. **Any correlation assumption must be checked using the pseudo-measurement against known truth before drawing conclusions from real data.** The guide further recommends bin support with at least 5,000 effective MC events, data statistical precision below 15%, and jet pT greater than 5 GeV. Our frozen 2x2 analysis implemented these support/selection gates.
4. More sophisticated *smoothly varying* decorrelations are potential alternatives, but the guide does not supply a unique analytic 2D smoothing rule. The exact `multifold_util.smooth_uncertainty` implementation **was subsequently retrieved and SHA-256 verified** in [CI 42390285792](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42390285792); its 1D kernel does **not** specify any 2D smoother. This supersedes the historical access limitation.

**Important:** The published guide motivates alternatives but does not automatically turn our chosen normalized 2x2 transformation into an ATLAS-approved covariance or grant a calibrated compatibility p-value.

## Fixed a priori models

Use the **same** nominal 2x2 shapes, **same** 29 archived source families, **same** frozen mass/track thresholds, and **same** v2 signed count-level shifts across all models. Only source-internal correlations of the **DD** and **Sherpa hidden-variable** two-point sources may change. Their uncertainty amplitudes are never tuned to the real residual. Experimental, theory, bootstrap, finite MC and other source families are held unchanged for these scenarios.

For signed unnormalized four-cell source shift `delta`, nominal four-count `h` and normalizer `H=sum(h)`, define `p=h/H` and the first-order normalized-shape Jacobian `J=(I-p 1^T)/H`.

- **Default fully correlated:** one nuisance per source, `C_full = (J delta)(J delta)^T`.
- **Alternative four independent bins:** `C_4ind = J diag(delta_i^2) J^T`. This provides four independent **raw count-bin** nuisance shifts, projected onto the three-dimensional normalized shape space. It is **not** identical to diagonalizing a normalized 4x4 covariance matrix, which would violate the normalization null mode.

The **DD** count-level shift is `delta_DD,i=(weights_dd,i-target_dd,i)*nominal_i/target_dd,i`, requiring positive target counts. The **Sherpa** raw-count shift is `delta_Sherpa,i=alternative_nominal_i - nominal_i`. Both are taken directly from the immutable signed `phase7-v2` source summaries; no sign is guessed by factoring rank-one covariance matrices.

The **four scenarios are fixed before evaluating any new results**, in this order:

| Scenario | DD | Sherpa |
|---|---|---|
| Primary: both fully correlated | One nuisance | One nuisance |
| DD-only alternative | Four per-bin nuisances | One nuisance |
| Sherpa-only alternative | One nuisance | Four per-bin nuisances |
| Both alternatives | Four per-bin nuisances | Four per-bin nuisances |

The code computes the pseudodata-versus-independent-target diagnostics **before** the real-data diagnostics. All diagnostic quadratic values are labelled **UNCALIBRATED** and are **not p-values**. No model is selected post hoc by comparing its real-data goodness of fit.

## Checks and scientific limits

- Exactly the same 29 original source families retained; no DD or Sherpa source is dropped or set to zero.
- All 4x4 component matrices symmetric, PSD and with normalization-null direction; numerical 3-dimensional contrast covariance positive definite.
- v1 and v2 SHA-256/provenance checks must pass before calculating.
- The alternative is a first-order Jacobian covariance. The original historical v1 recipe used an exact normalized nuisance shift for some sources; the two are conceptually distinguishable. A future report must evaluate whether nonlinearity materially changes results.
- This is **one** released pseudodata sample; it is not a frequentist coverage study and has no source-verified 2D smoothing or full ATLAS generator-measurement covariance calibration.
- Thus **G5 remains provisional, G8 and G12 remain unverified, G15 NO-GO** for formal real-data compatibility significance.

**Reproduce with no raw-data download:** `python -m src.phase7_twopoint_protocol --v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 --out outputs/twopoint`.

Scientific implementation: `src/phase7_twopoint_protocol.py`; regression protection: `tests/test_phase7_twopoint_protocol.py`.

## Exact-normalization versus first-order Jacobian check (pinned v2, 2026-11-07)

A source of approximation in the code is linearizing a normalized count-level nuisance shift `delta`. For nominal source counts `h`, total `H=sum(h)`, nominal normalized shape `p=h/H` and `D=sum(delta)`, the **exact** shifted normalized difference and its first-order approximation are related by the *identity*:

```text
shift_exact = (h+delta)/(H+D) - h/H
shift_linear = (delta - p*D)/H
shift_exact = shift_linear / (1 + D/H)
```

Therefore the Euclidean relative difference between linear and exact shift vectors is exactly `abs(D/H)`, when the shift is nonzero and `H+D>0`. This measures only **normalization nonlinearity**, not the validity of the correlation assumption.

Computed directly from checksum-pinned official `data/derived/phase7-v2/moments.json` signed four-cell sums:

| Sample | Two-point source | `abs(D/H)` = relative shift-vector difference | Maximum absolute normalized cell shift difference |
|---|---|---:|---:|
| Real | DD unfolding | 0.7341% | 0.00005963 |
| Real | Sherpa hidden variable | 0.5009% | 0.00004659 |
| Pseudodata | DD unfolding | 0.9258% | 0.00007499 |
| Pseudodata | Sherpa hidden variable | 0.4094% | 0.00003024 |

These are small **normalization-approximation differences** in this frozen 2x2 partition, and do not validate 2D source correlations or make the real-data quadratic a calibrated significance test. The ATLAS helper's 1D smoothing code remains independently inaccessible. **G15 NO-GO.**
