# Research status: current, authoritative

**Checked 8 November 2026.** This is the first place to look for scientific and editorial status. This file is intentionally short; the detailed primary source is the [immutable numerical bundle](../results/README.md). The former 60-kB append-only handoff is preserved in [the historical handoff](HANDOFF_HISTORY.md). **None of these documents predicts what will happen on November 18.**

## Current project contract

**Working title:** *A Reproducible Four-Cell Analysis of Leading Charged-Jet Mass and Track Multiplicity in ATLAS 2024 OmniFold Z+Jets Data*.

This is an independent, reproducible **descriptive secondary analysis** of the [ATLAS 2024 PRL](https://doi.org/10.1103/PhysRevLett.133.261803) and the [2024 Zenodo event-weight release](https://doi.org/10.5281/zenodo.11507450). It does **not** retrain OmniFold, measure new ATLAS events, establish generator compatibility, or approve a new two-dimensional systematic covariance prescription.

**Exactly two questions:**
1. Which normalized four-cell, mass-low marginal, multiplicity-low marginal and log-odds contrasts arise between real unfolded weights and the nominal generator under fixed generator-defined thresholds?
2. How do the conditional uncertainty summaries respond to four stated DD/Sherpa correlation assumptions, and what does one independent known-target pseudodata comparison test or fail to test?

Selected events satisfy `pT_trackj1 > 5 GeV`; the fixed mass threshold is `10.594606399536133 GeV` and the leading-jet charged-constituent multiplicity threshold is `11`. Cell order is `LL/LH/HL/HH`, **mass first**. Multiplicity means **leading charged-jet constituents**, not the event-wide charged track count.

## Verified achievements

- **Numerical milestone achieved 8 November 2026**: 5 frozen CSV tables, 4 SVG figures, 12 positive bundle checks, reproducibility manifest, generator and pseudo comparison. The folder `results/kti-nov18` is named after a **target school milestone**, not its completion date.
- Prior frozen-code CI run [42442490666](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42442490666) passed **107 tests**. Tests show numerical consistency, not physical nuisance calibration.
- Real unfolded minus nominal-generator: low-mass `+0.0036800854`, low-multiplicity `-0.0146902523`, joint log odds `-0.0597334776`; pseudo versus independent target: `-0.0229756608`, `-0.0019636003`, `+0.0522361448`.
- Four DD/Sherpa conditional SE models: real log-odds SE `0.092321–0.146783`; pseudo `0.056651–0.112847`. These are **scenario-dependent**, not validated uncertainty intervals.
- A v0.3 Word **review draft** now incorporates the new D analysis: **13 rendered pages, 3 unchanged numerical tables, 4 unchanged figures, 14 unchanged bibliography entries**. The earlier v0.2 had 12 pages. Neither Word file is in GitHub or synchronized to Google Doc ARTICLE. The latest file hash is recorded in [manuscript review](MANUSCRIPT_REVIEW.md).
- An independent additional algebraic check now distinguishes log odds from the binary indicator covariance `D` in [JOINT_ASSOCIATION_AUDIT.md](JOINT_ASSOCIATION_AUDIT.md). This is supplemental descriptive analysis, **not** a new accepted uncertainty model or experimental validation.

## Current gate register

| Gate | Status | What it actually means |
| --- | --- | --- |
| G5 | **PROVISIONAL** | Reconstructed 29 components (25 systematic-labelled + 4 stochastic), but inclusion/source identities/dependencies not approved as the unique 2D experimental model |
| G8 | **UNVERIFIED** | Repeated independent detector sampling and full unfolding coverage have not been demonstrated |
| G11 | **ONE CHECK EXECUTED** | One known-target independent pseudodata comparison, not 25 independent pseudodata experiments |
| G12 | **UNVERIFIED** | No uniquely justified primary two-dimensional DD/Sherpa and cross-source correlation prescription |
| G15 | **NO-GO** | No calibrated real-data compatibility p-value, significance, generator acceptance/rejection or experimental-coverage statement |

Green software CI, a positive-semidefinite normalized 4×4 covariance, or a high/low AI-detector score cannot change those statuses.

## Next actionable decisions

1. **Now:** ask adviser to confirm whether a descriptive 2×2 secondary analysis meets the school research-paper requirement. Do not imply acceptance.
2. **Now:** qualified author/adviser review of the new D and path-dependent log-odds interpretation already inserted into v0.3. No fresh event-level data is required for that descriptive revision.
3. **Before submission:** author/adviser review, verify all citations with Zotero and publisher records, verify figures and source claims, finalize attribution, contributions, conflicts, funding, AI assistance disclosure.
4. **If formal inference is desired later:** independently justify covariance-source inclusion, full 2D dependencies and null calibration with actual repeated-unfolding validation. Without those new inputs, gate G15 stays closed. This is an **optional different research project**, not a hidden requirement for the descriptive KTI.
5. **Submission/presentation date:** not assumed from a folder called `kti-nov18`. Verify independently with school/adviser.

See [research issues](ISSUE_REGISTER.md), [roadmap](../plans/RESEARCH_PLAN.md), [document register](REPORT_REGISTER.md), and [short handoff](START_HERE_HANDOFF.md).
