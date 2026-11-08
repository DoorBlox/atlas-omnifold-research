# Four-cell release path migration

**Date:** 8 November 2026  
**Canonical release:** [`results/four-cell-v1/`](../results/four-cell-v1/README.md)  
**Previous path (history only):** `results/kti-nov18/`

## Reason

The original directory name referred to a planned November 18 school milestone. The source-backed numerical bundle was already completed on 8 November 2026. Using a date-independent identifier makes future citations and automated reproduction less confusing. The new name identifies a **four-cell descriptive output release, version 1**.

## Preservation and verification

- The underlying released 2024 ATLAS data, frozen `data/derived/phase7-v1` and `phase7-v2` moments, selection, four cell fractions, source covariance values, five CSV tables, and four SVG scientific figures are unchanged. Their Git blob identities are retained by the folder move.
- Textual release artifacts (`README.md`, `MANUSCRIPT_RESULTS.md`, `results.json`) have the old output path and date-based status label replaced. The **SHA-256 manifest is recalculated for these textual changes** and remains anchored to the same source moments and original run IDs. The 5 numerical table digests and 4 SVG figure digests retain their values.
- The source generator, CLI default, tests, association audit and GitHub Actions workflow now use `outputs/four-cell-v1` and `results/four-cell-v1`.
- New test `test_repository_four_cell_release_matches_generated_manifest` compares **every regenerated file** with the committed release SHA-256 manifest. The result is versioned in Git and visible from the pull request's CI.
- The previous pathname is recoverable in Git history. Existing commit messages and original scientific gate statuses are preserved rather than force-rewritten.

## Current scientific boundaries

The calculations constitute a descriptive secondary analysis. Four DD/Sherpa within-source assumptions yield **conditional** uncertainty summaries. **G5 remains PROVISIONAL; G8 and G12 remain UNVERIFIED; G11 covers one known-target pseudodata comparison; G15 remains NO-GO** for a calibrated real-data generator significance claim. The directory rename and software tests cannot establish experimental coverage.

## Follow-on citation and document guidance

Use `results/four-cell-v1/` for all new links, source references, generated output paths, school reports and manuscript availability statements. The original GitHub data release is [Zenodo 11507450](https://doi.org/10.5281/zenodo.11507450); the parent ATLAS analysis is [PRL 133, 261803 (2024)](https://doi.org/10.1103/PhysRevLett.133.261803). The project is an independent downstream analysis.

The complete earlier handoff remains in [HANDOFF_HISTORY.md](HANDOFF_HISTORY.md) as historical context. Its older paths should be interpreted using this migration record.
