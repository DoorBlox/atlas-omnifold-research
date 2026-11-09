# ATLAS OmniFold Z+jets: reproducible four-cell analysis

**Continue in ChatGPT:** [active handoff](CHATGPT_HANDOFF.md) · [current state](docs/CURRENT_STATE.md) · [research workflow](docs/RESEARCH_WORKFLOW.md) · [author-led writing workflow](docs/WRITING_WORKFLOW.md) · [artifact registry](docs/ARTIFACT_REGISTRY.md).

[![ATLAS Phase 7 lightweight scientific checks](https://github.com/DoorBlox/atlas-omnifold-research/actions/workflows/atlas-phase7-lite.yml/badge.svg)](https://github.com/DoorBlox/atlas-omnifold-research/actions/workflows/atlas-phase7-lite.yml)

This independent student project examines the **joint distribution of leading charged-jet mass and charged-constituent multiplicity** using the [2024 ATLAS OmniFold Z+jets measurement](https://doi.org/10.1103/PhysRevLett.133.261803) and [its public event-weight release](https://doi.org/10.5281/zenodo.11507450). The analysis reconstructs four normalized cells and compares unfolded real data with a shared-event nominal generator. A second example compares unfolded pseudodata with independent known-target truth.

## Numerical evidence

The verified and versioned release is **[`results/four-cell-v1/`](results/four-cell-v1/README.md)**. It contains five machine-readable CSV tables, four SVG figures, source accounting, a SHA-256 manifest and reproduction checks. The numerical release was completed **8 November 2026**. See the [path migration record](docs/RELEASE_MIGRATION.md).

Selection: `pT_trackj1 > 5 GeV`, mass boundary `10.594606399536133 GeV`, leading-jet constituent multiplicity boundary `11`. Cell order: LL, LH, HL, HH, mass first.

| Unfolded minus reference | Real vs shared generator | Pseudodata vs independent truth |
| --- | ---: | ---: |
| Low-mass fraction | +0.0036800854 | −0.0229756608 |
| Low-multiplicity fraction | −0.0146902523 | −0.0019636003 |
| Joint log odds | −0.0597334776 | +0.0522361448 |
| Binary-indicator covariance `D` | −0.0001685161 | +0.0014603768 |

Four DD/Sherpa within-source correlation models assign **conditional** standard errors to the log-odds differences. The real-data range is `0.092321–0.146783` and the pseudodata range is `0.056651–0.112847`. The [association audit](docs/JOINT_ASSOCIATION_AUDIT.md) derives `D` and its path-dependent relation to log odds.

## Reproduce

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests/test_phase7_kti_bundle.py tests/test_joint_association_audit.py
python -m src.phase7_kti_bundle --v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 --out outputs/four-cell-v1
```

The repository stores frozen derived moments and a compact result release. The source generator and regression test compare regenerated output files with the checked-in SHA-256 manifest. [Repository map](docs/REPOSITORY_MAP.md).

## Manuscript

**Current author-selected draft:** `ATLAS_Four_Cell_Science_Checked_Formatted_Equations.docx` (SHA-256 `e4d3e49b19e0c683bff7340769d4c646f2c1b13791551a941308aeb0182f8e62`). This is the author's rewritten prose, with focused scientific checking and proper Word equations; it contains three numerical tables, four figures and 14 reference entries. Older assistant v0.6 is preserved as history. [File identity and recovery](docs/ARTIFACT_REGISTRY.md) · [review](docs/MANUSCRIPT_REVIEW.md).

The full editable manuscript remains a conversation artifact. The school Google Doc ARTICLE tab contains an earlier working draft.

## Scientific status and navigation

This is a **descriptive secondary analysis**. The DD/Sherpa source model remains provisional (G5), repeated-unfolding coverage and a validated two-dimensional model remain unverified (G8/G12), and only one known-target pseudodata case has been checked (G11). **G15 stays NO-GO** for calibrated generator-compatibility significance.

Read [current status](docs/RESEARCH_STATUS.md), [open issues](docs/ISSUE_REGISTER.md), [research plan](plans/RESEARCH_PLAN.md), [short handoff](docs/START_HERE_HANDOFF.md), and the [historical report index](docs/REPORT_REGISTER.md). Final citation management, author declarations and school or journal review require human sign-off.
