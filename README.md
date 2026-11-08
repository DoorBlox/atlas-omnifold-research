# ATLAS OmniFold Z+jets: reproducible four-cell secondary analysis

[![ATLAS Phase 7 lightweight scientific checks](https://github.com/DoorBlox/atlas-omnifold-research/actions/workflows/atlas-phase7-lite.yml/badge.svg)](https://github.com/DoorBlox/atlas-omnifold-research/actions/workflows/atlas-phase7-lite.yml)

An **independent student research project** using the [ATLAS 2024 OmniFold 24-dimensional Z+jets measurement](https://doi.org/10.1103/PhysRevLett.133.261803) and its [public 2024 Zenodo HDF5 release](https://doi.org/10.5281/zenodo.11507450). We reconstruct a generator-defined normalized **2×2 leading charged-jet mass × charged-constituent multiplicity** distribution, its two low-category marginals and joint association. We compare real unfolded weights to a **shared-event nominal generator**, and one released unfolded pseudodata sample to an **independent known-target truth**.

**Current result: numerical reproducibility achieved; formal generator inference not validated.** The KTI is descriptive. Four provisional DD/Sherpa source-correlation assumptions give **model-conditional** standard errors, not experimentally calibrated uncertainty intervals. There is **no justified real-data compatibility p-value or generator acceptance/rejection**.

## Read the project (one canonical entry per topic)

| Entry point | What it covers |
| --- | --- |
| [Research status](docs/RESEARCH_STATUS.md) | Verified achievements and open scientific gates |
| [Frozen result release](results/README.md) | Five CSV tables, four figures, checksums, provenance and reproduction |
| [Association recheck](docs/JOINT_ASSOCIATION_AUDIT.md) | New insight: log-odds contrast versus binary-indicator association covariance |
| [Open issue register](docs/ISSUE_REGISTER.md) | What is resolved, provisional, blocked or awaiting human review |
| [Manuscript review and integrity](docs/MANUSCRIPT_REVIEW.md) | Word draft version, limitations, Turnitin report and academic writing |
| [Research plan](plans/RESEARCH_PLAN.md) | Next scientifically justified and editorial tasks |
| [Start-here handoff](docs/START_HERE_HANDOFF.md) | Short instructions for future sessions |
| [Repository/document map](docs/REPOSITORY_MAP.md) · [report register](docs/REPORT_REGISTER.md) | Code and historical report navigation |

**Why a folder says `kti-nov18`:** the name was chosen for a **planned 18 November 2026 milestone**, but the complete version-one numerical deliverable was **already produced and committed on 8 November 2026**. It does not record an event on November 18 or predict any future outcome. The [`results/README.md`](results/README.md) is the stable result alias; the original `results/kti-nov18/` directory is retained to preserve reproducibility and SHA-256 manifest coverage.

## Central descriptive results

Frozen selection: `pT_trackj1 > 5 GeV`; generator mass split `10.594606399536133 GeV`, charged constituent count split `11`. Cell order LL/LH/HL/HH, mass first.

| Unfolded − appropriate reference | Real vs shared generator | Pseudodata vs independent truth |
| --- | ---: | ---: |
| Mass-low marginal | +0.0036800854 | -0.0229756608 |
| Multiplicity-low marginal | -0.0146902523 | -0.0019636003 |
| Joint log-odds | -0.0597334776 | +0.0522361448 |
| Binary-indicator covariance `D` (new descriptive recheck) | -0.0001685161 | +0.0014603768 |

A path-dependent marginal/association counterfactual is [documented here](docs/JOINT_ASSOCIATION_AUDIT.md) and reproduced by [source code](src/joint_association_audit.py) and [regression tests](tests/test_joint_association_audit.py). It is a different, **purely descriptive measure** and does not change the released four-cell values.

## Repeat the existing version-one release

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests/test_phase7_kti_bundle.py
python -m src.phase7_kti_bundle --v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 --out outputs/kti-nov18
```

The repository contains derived signed/mixed moments and generated outputs, **not** the original multi-GB public ATLAS event ZIP, private detector samples or trained OmniFold checkpoints. [Earlier frozen-code CI run](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42442490666) recorded 107 passing tests and 12 positive bundle checks. **These demonstrate computational reproducibility only.** The released source families and DD/Sherpa correlations are not an official ATLAS 2D uncertainty prescription.

## Scientific integrity, credit and manuscript

This project is **not authored, endorsed or approved by ATLAS**. Cite the parent experimental measurement and original dataset. No actual detector measurement, generator model validation, first-ever multidimensional jet study, experimental coverage or specialist journal publication is claimed.

**Current writing artifact (v0.5):** a complete evidence-preserving manuscript rewrite was produced on 8 November 2026. All 64 editable prose, caption and note paragraphs were rewritten with the academic-humanizer workflow; the original three numerical tables, four figures, display equation and 14 bibliography entries are preserved. The editable DOCX SHA-256 is `8f5f5d9879d8dcfdee4a80630547a40d782dbd9cc7c3526dd688c3c6c7d5c83f`. The full Word artifact remains a conversation attachment, **not a public GitHub binary**. The user-reported 56% AI-writing score relates to **v0.4**, not v0.5. See [the living manuscript review](docs/MANUSCRIPT_REVIEW.md). The preceding **v0.4 scientific-review Word manuscript** includes the additional association-coordinate audit and an evidence-preserving academic-prose pass and is available through the author's conversation, **not publicly uploaded here**. The 14-DOI [reference seed list](references/README.md) is checked against its bibliography; a finalized Zotero library is still pending. An editing/AI-writing audit does not determine authorship or scientific validity; human author/adviser review, appropriate AI-assistance disclosure, Zotero citation integrity and publication-fit approval are pending. See [manuscript review](docs/MANUSCRIPT_REVIEW.md).

Full historical investigation, including superseded 2D covariance toy simulations and original source-level audits, is preserved and indexed in [the document register](docs/REPORT_REGISTER.md). Do not use it as permission to reopen G15 without new physical evidence.
