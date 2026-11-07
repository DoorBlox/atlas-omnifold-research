# ATLAS OmniFold Z+jets — Reproducible 2D Research

[![ATLAS Phase 7 lightweight scientific checks](https://github.com/DoorBlox/atlas-omnifold-research/actions/workflows/atlas-phase7-lite.yml/badge.svg)](https://github.com/DoorBlox/atlas-omnifold-research/actions/workflows/atlas-phase7-lite.yml)
[![ATLAS Phase 7 analysis](https://github.com/DoorBlox/atlas-omnifold-research/actions/workflows/atlas-phase7.yml/badge.svg)](https://github.com/DoorBlox/atlas-omnifold-research/actions/workflows/atlas-phase7.yml)

A reproducible, independent **downstream research analysis** of the [ATLAS 2024 unbinned Z+jets OmniFold measurement](https://doi.org/10.1103/PhysRevLett.133.261803), using the [official public dataset](https://doi.org/10.5281/zenodo.11507450). We study the joint shape of **leading charged-jet mass and charged-track multiplicity** using a frozen, generator-defined 2×2 partition.

> **Research status: descriptive results verified; formal inference not approved (G15 NO-GO).**
> This is an independent student research project, **not an official ATLAS analysis or an endorsed 2D uncertainty prescription**. The model for Sherpa/DD unfolding and systematic correlations is still provisional. Do not interpret the uncalibrated quadratic diagnostics as p-values or significance.

## Start here

**[Master research handoff](docs/START_HERE_HANDOFF.md)** — the authoritative continuity document for resuming after a chat context limit. It contains the full scientific scope, provenance, exact GitHub Actions runs, corrected earlier assumptions, validation gates, current blockers, and a ready-to-use continuation prompt.

**[Scientific results & limitations](docs/PHASE7_REFERENCE_AUDIT_CORRECTED_CALIBRATION.md)** · **[Notebook-method audit](docs/PHASE7_NOTEBOOK_METHOD_RECONCILIATION.md)** · **[Covariance sensitivity](docs/PHASE7_MODEL_SENSITIVITY_CHECKPOINT.md)** · **[Finite-MC cross-covariance audit](docs/PHASE7_SHARED_MC_BOUNDS_AND_CI_OPTIMIZATION.md)**

## Measurement and reproducibility

| Property | Current frozen analysis |
|---|---|
| Observable | Leading charged-jet mass × charged-track multiplicity |
| Selection | `pT_trackj1 > 5 GeV` |
| Generator-defined thresholds | Mass **10.5946064 GeV**; multiplicity **11 tracks** |
| Four ordered cells | LL / LH / HL / HH (mass low/high × track count low/high) |
| Nominal selected rows | **417,401** |
| Independent pseudodata target | **23,888,304** selected target rows |
| Source-level uncertainty prototype | 29 components; **not yet a validated 2D covariance model** |

Frozen output from official-data processing: [real covariance run #42324639484](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42324639484), [pseudodata closure run #42327464929](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42327464929). A corrected reference-family audit ran in [#42377662887](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42377662887). The latest conditional finite-MC bounds and covariance-denominator audit passed **46 tests** in [#42384589187](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42384589187); [lightweight CI #42384751385](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42384751385) passed **34 tests**.

## No-repeat-download data strategy

The permanent [`data/derived/phase7-v1/`](data/derived/phase7-v1) stores **33,594 bytes of byte-preserved, SHA-256-pinned four-cell results**: real/pseudodata cell fractions, frozen boundaries, all 29 source covariance matrices and manifests, and the scientific gate statements. It contains **no raw event records**, and does not allow arbitrary rebinning or reconstruction of signed source shifts. [Provenance and integrity documentation](docs/DERIVED_SNAPSHOT.md).

For routine no-download analysis on the cloned repository (Python 3.11):

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python -m src.phase7_snapshot verify --root data/derived/phase7-v1
python -m src.phase7_interaction --snapshot data/derived/phase7-v1 --out outputs
python -m src.phase7_crosscov_bounds --snapshot data/derived/phase7-v1 --out outputs
```

Two workflows reduce GitHub Actions usage:

- **[`atlas-phase7-lite.yml`](.github/workflows/atlas-phase7-lite.yml):** quick derived-statistics regression and sensitivity work, using the committed snapshot and a minimal NumPy/pytest installation.
- **[`atlas-phase7.yml`](.github/workflows/atlas-phase7.yml):** original event-level extraction and scientific stages, invoked deliberately when the existing snapshot lacks essential statistics.

When new signed four-cell variation sums or shared generator–unfolded weight products are indispensable, the next versioned extraction should produce **small, checksum-verified `phase7-v2` sufficient statistics in a single official-data pass**. It must not overwrite v1 or quietly change bin boundaries.

## What remains unresolved

The major challenge is deciding and validating an **a priori 2D covariance prescription**, particularly Sherpa hidden-variable and DD unfolding uncertainties. Other checks include sample-dependent source inclusion, potentially shared generator/measurement covariance, and null calibration beyond conditional Gaussian toys. The [joint-association analysis](docs/PHASE7_ASSOCIATION_DECOMPOSITION.md) shows these modelling choices have a material effect on the estimated uncertainty.

**No final real-data compatibility p-value, exclusion or discovery significance is authorized.** Results should be quoted as descriptive and conditional on explicitly stated modelling assumptions.

## Primary sources and project scope

ATLAS Collaboration, *Simultaneous Unbinned Differential Cross-Section Measurement of Twenty-Four Z+jets Kinematic Observables with the ATLAS Detector*, [Phys. Rev. Lett. **133**, 261803 (2024)](https://doi.org/10.1103/PhysRevLett.133.261803). ATLAS public event-level measurement and demonstration notebooks: [Zenodo 11507450](https://doi.org/10.5281/zenodo.11507450). Consult original ATLAS documentation for the underlying experiment and terminology.

This repository **reuses published open data for an independent analysis** and does not redistribute the original multi-GB event dataset. Preserve attribution and check the upstream license before any broader redistribution.

**[All GitHub Actions](https://github.com/DoorBlox/atlas-omnifold-research/actions)** · **[Run tracking / issue #1](https://github.com/DoorBlox/atlas-omnifold-research/issues/1)** · **[Master handoff](docs/START_HERE_HANDOFF.md)**
