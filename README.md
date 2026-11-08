# ATLAS OmniFold Z+jets — Reproducible 2D Research

[![ATLAS Phase 7 lightweight scientific checks](https://github.com/DoorBlox/atlas-omnifold-research/actions/workflows/atlas-phase7-lite.yml/badge.svg)](https://github.com/DoorBlox/atlas-omnifold-research/actions/workflows/atlas-phase7-lite.yml)
[![ATLAS Phase 7 analysis](https://github.com/DoorBlox/atlas-omnifold-research/actions/workflows/atlas-phase7.yml/badge.svg)](https://github.com/DoorBlox/atlas-omnifold-research/actions/workflows/atlas-phase7.yml)

A reproducible, independent **downstream research analysis** of the [ATLAS 2024 unbinned Z+jets OmniFold measurement](https://doi.org/10.1103/PhysRevLett.133.261803), using the [official public dataset](https://doi.org/10.5281/zenodo.11507450). We study the joint shape of **leading charged-jet mass and charged-track multiplicity** using a frozen, generator-defined 2×2 partition.

> **Research status: descriptive results verified; formal inference not approved (G15 NO-GO).**
> This is an independent student research project, **not an official ATLAS analysis or an endorsed 2D uncertainty prescription**. The model for Sherpa/DD unfolding and systematic correlations is still provisional. Do not interpret the uncalibrated quadratic diagnostics as p-values or significance.

## Start here

**[Canonical revised KTI scope and publication blueprint](plans/KTI_DESCRIPTIVE_SCOPE_BLUEPRINT_2026_11_08.md)** — one consistent 17-word title, two research questions and objectives, precise ATLAS data/comparator definitions, honest limitations, internal G5/G8/G11/G12/G15 glossary, executable editorial tasks and dependency graph, and realistic journal-readiness criteria. The [four-tab school Google Doc](https://docs.google.com/document/d/1rTafCdT6ESCpH43HtrssArHpiUzVEhoYABzwQJewQ00/edit) has been reconciled to the descriptive scope; ARTICLE remains a working draft pending Zotero/adviser/figure-layout review. No real-data p-value or journal acceptance is claimed.

**[Completed November 18 KTI evidence bundle](results/kti-nov18/README.md)** — **five verified CSV numerical tables, four source-backed SVG figures, a Methods/Results draft, 12 checksum and physics QA checks, and a SHA-256 output manifest**. All 14 generated files are permanently committed under [results/kti-nov18](results/kti-nov18), merged through [PR #3](https://github.com/DoorBlox/atlas-omnifold-research/pull/3). [CI run 42442355027](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42442355027) **PASSED 107 tests**; artifact `phase7-lite-audits-19` (ID 13602112226). [Actual fractions](results/kti-nov18/tables/joint_cells.csv), [marginals and log-odds](results/kti-nov18/tables/marginal_association.csv), [four-model sensitivity](results/kti-nov18/tables/scenario_sensitivity.csv), [source variance shares](results/kti-nov18/tables/source_variance.csv), and [article-ready Methods/Results text](results/kti-nov18/MANUSCRIPT_RESULTS.md). **Descriptive only; G5 PROVISIONAL, G8/G12 UNVERIFIED, G15 NO-GO.**

**[Fact-check of the second Deep Research report](docs/PHASE7_DEEP_RESEARCH_REPORT_10_FACTCHECK.md)** — its example four-cell fractions, all-positive covariance and source percentages are not ATLAS measurements. The actual source-backed results above supersede them.

**[Master research handoff](docs/START_HERE_HANDOFF.md)** — the authoritative continuity document for resuming after a chat context limit. It contains the full scientific scope, provenance, exact GitHub Actions runs, corrected earlier assumptions, validation gates, current blockers, and a ready-to-use continuation prompt.

**[Deep Research critical adjudication (2026-11-08)](docs/PHASE7_DEEP_RESEARCH_ADJUDICATION_2026_11_08.md)** · **[Latest conditional covariance + null simulations](docs/PHASE7_SOURCE_ALIGNED_JOINT_AND_CONDITIONAL_TOYS.md)** · **[Official CERN helper source audit](docs/PHASE7_PRIMARY_SOURCE_COVARIANCE_AUDIT.md)** · **[What it takes for GO](docs/PHASE7_GO_EVIDENCE_REQUIREMENTS.md)** · **[Latest v2 extraction and safeguards](docs/PHASE7_V2_EXTRACTION_PLAN.md)** · **[ATLAS-guided four-bin covariance protocols](docs/PHASE7_CORRELATION_PROTOCOL_V2.md)** · **[Scientific results & limitations](docs/PHASE7_REFERENCE_AUDIT_CORRECTED_CALIBRATION.md)** · **[Notebook-method audit](docs/PHASE7_NOTEBOOK_METHOD_RECONCILIATION.md)** · **[Covariance sensitivity](docs/PHASE7_MODEL_SENSITIVITY_CHECKPOINT.md)** · **[Finite-MC cross-covariance audit](docs/PHASE7_SHARED_MC_BOUNDS_AND_CI_OPTIMIZATION.md)**

**Earlier source-family verification (8 November 2026):** [GitHub Actions run 42438948363](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42438948363) passed **98 tests** (source-accounting artifact **13600771619**, phase7-lite-audits-17). Frozen source manifests now reconcile **29 = 25 systematic-labelled + 4 stochastic** components; the official 1D example's 15 selected names omit 14 systematic terms. This resolves an erroneous 25-vs-29 claim in the external Deep Research report; **no official 2D model or real-data p-value follows**. We have source-verified the R−1 replica estimator, reconstructed all 29 signed source covariances, corrected real-generator shared-event finite-MC treatment, executed pseudodata-first 2×2 correlation sensitivities and two distinct conditional-null simulations. An extra source-width Sherpa factorized two-axis kernel is numerically the identity for our 2×2 threshold categories, but **no official 2D smoothing is prescribed**. The remaining G15 block is methodological: a pre-specified, validated **2D systematic-correlation and sampling model**; the released single pseudodata closure and source replicas do not demonstrate independent physical repeat-unfolding coverage. **No real-data p-value is claimed.**

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

Frozen output from official-data processing: [real covariance run #42324639484](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42324639484), [pseudodata closure run #42327464929](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42327464929). A corrected reference-family audit ran in [#42377662887](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42377662887). The original-data **v2 signed-statistics capture** succeeded in [run #42386487963](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42386487963). [No-download v2 covariance reconstruction #42388030573](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42388030573) passed **38 tests** with **zero reconstruction error for every one of the 29 source matrices**. The [publication-guided four-bin correlation audit #42388258968](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42388258968) passed **43 tests**.

## No-repeat-download data strategy

The permanent [`data/derived/phase7-v1/`](data/derived/phase7-v1) preserves **33,594 bytes** of SHA-256-pinned original four-cell fractions, uncertainty matrices, manifest and bin definitions. **New:** [`data/derived/phase7-v2/`](data/derived/phase7-v2) now preserves ~188 KB of verified **signed four-cell weight sums and squared/mixed moments** from six official HDF5 inputs. V2 captures **251 real nominal weight columns and 176 pseudodata nominal weight columns**, plus the Sherpa/non-DY alternative supports. Both nominal samples exactly reproduce v1's 417,401 selected rows and cell fractions. Original archive and individual HDF5 hashes are retained in provenance; **no raw event records or original ZIP files are stored in the repository**. These summaries support source-level covariance reconstruction for the same frozen bins but do not support arbitrary rebinning, retraining, or repeated-unfolding coverage. See [v1 integrity](docs/DERIVED_SNAPSHOT.md) and [v2 extraction plan](docs/PHASE7_V2_EXTRACTION_PLAN.md).

For routine no-download analysis on the cloned repository (Python 3.11):

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python -m src.phase7_snapshot verify --root data/derived/phase7-v1
python -m src.phase7_interaction --snapshot data/derived/phase7-v1 --out outputs
python -m src.phase7_crosscov_bounds --snapshot data/derived/phase7-v1 --out outputs
python -m src.phase7_v2_reconstruct --v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 --out outputs/v2-audit
python -m src.phase7_twopoint_protocol --v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 --out outputs/twopoint
```

The one-time [v2 archival workflow](.github/workflows/atlas-phase7-v2.yml) completed successfully; regular small-data analysis will not repeat it. Two primary workflows reduce GitHub Actions usage:

- **[`atlas-phase7-lite.yml`](.github/workflows/atlas-phase7-lite.yml):** quick derived-statistics regression and sensitivity work, using the committed snapshot and a minimal NumPy/pytest installation.
- **[`atlas-phase7.yml`](.github/workflows/atlas-phase7.yml):** original event-level extraction and scientific stages, invoked deliberately when the existing snapshot lacks essential statistics.

The **one-time v2 extraction is complete**. Signed source-bin variation sums and mixed generator–unfolded products are now reusable for this four-cell grid. They enabled a direct conditional shared-event finite-MC calculation and four **pre-specified** DD/Sherpa correlation models, without any further 3.65 GB downloads. The primary model is fully correlated across bins; the alternative treats each of the four raw-count cells as an independent nuisance. Those options are grounded in [the official ATLAS supplemental user guide](https://cds.cern.ch/record/2899105/files/2405.20041.pdf?version=5) but are still a provisional normalized 2D extension, not official CERN implementation. See [methodology protocol](docs/PHASE7_CORRELATION_PROTOCOL_V2.md).

## What remains unresolved

The major challenge is deciding and validating an **a priori 2D covariance prescription**, particularly Sherpa hidden-variable and DD unfolding uncertainties. Other checks include sample-dependent source inclusion, potentially shared generator/measurement covariance, and null calibration beyond conditional Gaussian toys. The [joint-association analysis](docs/PHASE7_ASSOCIATION_DECOMPOSITION.md) shows these modelling choices have a material effect on the estimated uncertainty.

**No final real-data compatibility p-value, exclusion or discovery significance is authorized.** Results should be quoted as descriptive and conditional on explicitly stated modelling assumptions.

## Primary sources and project scope

ATLAS Collaboration, *Simultaneous Unbinned Differential Cross-Section Measurement of Twenty-Four Z+jets Kinematic Observables with the ATLAS Detector*, [Phys. Rev. Lett. **133**, 261803 (2024)](https://doi.org/10.1103/PhysRevLett.133.261803). ATLAS public event-level measurement and demonstration notebooks: [Zenodo 11507450](https://doi.org/10.5281/zenodo.11507450). Consult original ATLAS documentation for the underlying experiment and terminology.

This repository **reuses published open data for an independent analysis** and does not redistribute the original multi-GB event dataset. Preserve attribution and check the upstream license before any broader redistribution.

**[All GitHub Actions](https://github.com/DoorBlox/atlas-omnifold-research/actions)** · **[Run tracking / issue #1](https://github.com/DoorBlox/atlas-omnifold-research/issues/1)** · **[Master handoff](docs/START_HERE_HANDOFF.md)**
