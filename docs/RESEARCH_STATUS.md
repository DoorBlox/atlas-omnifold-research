# Current research status

**Numerical baseline: 8 November 2026. Writing and continuity reviewed: 9 November 2026.** The project is an independent, reproducible **descriptive secondary analysis** of the [2024 ATLAS OmniFold Z+jets measurement](https://doi.org/10.1103/PhysRevLett.133.261803) and its [2024 event-weight release](https://doi.org/10.5281/zenodo.11507450). Read the [active ChatGPT handoff](../CHATGPT_HANDOFF.md) for the current manuscript and next actions.

## Research questions

1. Which four-cell, low-mass marginal, low-multiplicity marginal and joint log-odds contrasts arise between unfolded real data and the **shared-event nominal generator**?
2. How do four stated DD/Sherpa within-source assumptions affect **conditional** precision, and what can one comparison of unfolded pseudodata with **independent known truth** check?

The leading charged jet selection is `pT_trackj1 > 5 GeV`, split at mass `10.594606399536133 GeV` and constituent multiplicity `11`. Cells are LL/LH/HL/HH, mass first.

## Completed evidence

Five CSV tables, four SVG figures and a reproducibility manifest are archived in [`results/four-cell-v1/`](../results/four-cell-v1/README.md), generated from frozen v1/v2 moments. The original numerical release was completed **8 November 2026**. The [migration record](RELEASE_MIGRATION.md) documents the move to its descriptive version-one directory and the unchanged numerical/figure contents.

| Observed contrast | Real vs shared nominal generator | Pseudodata vs independent truth |
| --- | ---: | ---: |
| Low-mass marginal | +0.0036800854 | −0.0229756608 |
| Low-multiplicity marginal | −0.0146902523 | −0.0019636003 |
| Joint log-odds difference | −0.0597334776 | +0.0522361448 |
| Binary-indicator covariance difference `D` | −0.0001685161 | +0.0014603768 |

The real conditional log-odds SE varies from `0.092321` to `0.146783`; pseudodata from `0.056651` to `0.112847` across four source-correlation assumptions. The additional `D` and path-dependent log-odds decomposition are documented in the [association audit](JOINT_ASSOCIATION_AUDIT.md).

## Current manuscript

The author selected `ATLAS_Four_Cell_Science_Checked_Formatted_Equations.docx` (SHA-256 `e4d3e49b19e0c683bff7340769d4c646f2c1b13791551a941308aeb0182f8e62`). It follows the author's own rewritten prose, focused scientific checks and editable Word equation formatting. Three tables and four figures come from the frozen analysis. It **supersedes the assistant v0.6**. The Word bytes remain a private downloadable artifact and are not committed to public GitHub. [Artifact registry](ARTIFACT_REGISTRY.md) · [review status](MANUSCRIPT_REVIEW.md) · [writing workflow](WRITING_WORKFLOW.md).

Prior AI-writing classifier reports concern earlier versions. There is no claimed detector score or adviser approval for the latest formatted author file. Final citation verification and human scientific/editorial review remain open.


## Gate register

| Gate | State | Evidence boundary |
| --- | --- | --- |
| G5 | PROVISIONAL | Source-family mapping and joint dependencies require justification |
| G8 | UNVERIFIED | No validated independent full-unfolding repetition series |
| G11 | ONE CASE EXECUTED | Single known-target pseudodata case |
| G12 | UNVERIFIED | No accepted unique four-cell nuisance-correlation model |
| G15 | NO-GO | No calibrated real-data generator-compatibility conclusion |

Reproducibility tests establish software and numerical consistency. A domain reviewer and experimental validation would be needed to expand beyond the descriptive scope.

## Open work

Adviser approval of scientific scope and final text; full Zotero source/citation reconciliation; submission policy, venue fit and required author/AI/funding declarations; final manuscript proof. [Issue register](ISSUE_REGISTER.md), [roadmap](../plans/RESEARCH_PLAN.md), [document map](REPORT_REGISTER.md).
