# Phase 7 — Replica covariance denominator (R versus R-1) audit

**Date:** 2026-11-07. **Status:** experimentally executed on the frozen, verified official ATLAS 2×2 summaries. **No original archive download. No validated p-value (G15 NO-GO).**

## Scientific motivation and source distinction

The historical `src/phase7_covariance.py` used **population 1/R** for its three replica-family covariance matrices. The exact body of the original CERN helper [multifold_util.py](https://gitlab.cern.ch/atlas-physics/public/sm-z-jets-omnifold-2024/-/raw/master/multifold_util.py) could not be fetched in this environment, so its normalization is **not independently verified**.

Two accessible **independent, non-authoritative ATLAS-style implementations** use **sample covariance 1/(R-1)**:
- [`kgreif24/zjets_omnifold` covariance builder](https://github.com/kgreif24/zjets_omnifold/blob/d6b8cc232c5dd83524e56521954db9d60daa9a31/analyze/uncertainties.py), which explicitly computes the centered sum divided by `n-1`.
- [`aashirvad08/omnifold-publication` port](https://github.com/aashirvad08/omnifold-publication/blob/c7ffa31628eb88b0a8b987d7e89c10ea29fb4624/omnifold_publication/uncertainty.py) and its independent [sample-covariance tests](https://github.com/aashirvad08/omnifold-publication/blob/c7ffa31628eb88b0a8b987d7e89c10ea29fb4624/tests/test_covariance.py), which claim to reproduce the 1D `fill_cov_matrix` convention. These are **secondary evidence**, not a verified upstream ATLAS source.

For a fixed replica stack, the exact algebraic correction is

`C_sample = (R/(R-1)) * C_population`

with `R` read and validated from the archived source manifests. Both standalone bootstrap families and the NN ensemble covariance receive this factor; the separately applied NN mean-ensemble variance divisor `/R` is unchanged.

No event weights, binning, central fractions, raw ATLAS files, or DD/Sherpa source matrices were modified.

## Verified numerical effect

**Execution:** [lightweight GitHub Actions run #42384082085](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42384082085). It **passed 12 regression tests**, verified the original snapshot, executed the denominator audit and the independent descriptive marginal/association calculation, and uploaded artifact `phase7-lite-audits-1` (artifact ID 13578518447). The parallel heavier ATLAS workflow was **skipped** on this `[atlas-lite]` commit.

| Frozen sample | Data bootstrap | MC training bootstrap | NN ensemble |
|---|---:|---:|---:|
| Real ATLAS | 100 × (100/99) | 25 × (25/24) | 100 × (100/99) |
| Official pseudodata | 25 × (25/24) | 25 × (25/24) | 100 × (100/99) |

| Diagnostic | Historical population covariance | Sample-denominator **candidate** |
|---|---:|---:|
| Real-data total covariance trace | 0.000505975892 | 0.000506111295 (**+0.02676%**) |
| Pseudodata covariance trace | 0.000478173702 | 0.000478424619 (**+0.05247%**) |
| Real-data uncalibrated quadratic | 1.607909840 | 1.606995133 |
| Pseudodata uncalibrated quadratic | 1.802995969 | 1.802569862 |
| Real-data provisional log-odds SE (measurement covariance only) | 0.092422497 | 0.092432229 |
| Pseudodata provisional log-odds SE (measurement covariance only) | 0.056396187 | 0.056418207 |

The rank remains 3 and the covariance retains the expected zero-sum normalization mode. The correction has a **small** effect relative to the much larger source-family inclusion and Sherpa/DD correlation sensitivity previously documented.

**Do not turn these quadratic values into chi-square p-values or statistical significance.** The exact ATLAS 1D helper body and appropriate 2D covariance protocol still require verification.

## Reproduction, provenance and restrictions

```bash
python -m pytest -q tests/test_phase7_snapshot.py tests/test_phase7_divisor_audit.py
python -m src.phase7_snapshot verify --root data/derived/phase7-v1
python -m src.phase7_divisor_audit --snapshot data/derived/phase7-v1 --out outputs/divisor
```

- Code: `src/phase7_divisor_audit.py`; regression tests: `tests/test_phase7_divisor_audit.py`.
- The immutable `data/derived/phase7-v1` baseline is unchanged; alternative candidate matrices are written only to the run's report artifact, not substituted for original source matrices.
- A separate `atlas-phase7-lite.yml` CI workflow uses only NumPy and pytest; no HDF5, PyTables or large source file downloads.
- Reconstructed `1/(R-1)` covariance **does not repair** shared-generator cross-covariance, 2D Sherpa smoothing, DD source normalization, missing signed per-cell shifts or detector-level repeated-sampling coverage.
- G3/G4/G6 remain as previously verified for the original v1. **G5/G8/G12 unresolved; G15 NO-GO.**

**Next research step:** verify the primary CERN `fill_cov_matrix` source, then pre-specify a 2D DD/HV/source-family covariance protocol. The saved v1 matrices are adequate for this divisor audit; a one-time targeted event-level extraction should only be designed when a future signed source-shift or cross-moment calculation is justified.
