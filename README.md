# ATLAS OmniFold Z+jets KTI

Reproducible downstream 2×2 charged-jet mass × charged-multiplicity analysis of the official ATLAS public data.

## Resume this project here

**[START HERE — complete research and ChatGPT handoff](docs/START_HERE_HANDOFF.md)**

This is the single master checkpoint for resuming after a ChatGPT conversation reaches its length/context limit. It includes the full execution history, fixed research decisions, verified numerical results, GitHub run/artifact IDs, code map, corrected mistakes, scientific validation gates, next tasks, and a copy-paste prompt for a fresh chat.

**Current verified checkpoint (2026-11-07):** [Phase 7 reference-family audit and corrected calibration run #42377662887](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42377662887) — **25 regression tests passed**. Real data and pseudodata have different data-bootstrap replica counts (100 versus 25), and the corrected Gaussian toy simulation is documented. The research has authentic 2D ATLAS/pseudodata results, covariance model sensitivity, and an official known-target projection.

**Scientific status: G15 NO-GO.** The final real-data generator compatibility p-value is blocked pending a defensible a priori 2D source-correlation prescription and stronger validation. The published ATLAS one-dimensional chi-square source families must not be silently repurposed as an official 2D model.

For detailed commands see [docs/RUNBOOK.md](docs/RUNBOOK.md); its initial historical preflight description predates the newer analysis stages, so prefer the master handoff for up-to-date status. Large ATLAS binaries must not be committed or uploaded as CI artifacts.

[GitHub Actions](https://github.com/DoorBlox/atlas-omnifold-research/actions) · [Automated run index (issue #1)](https://github.com/DoorBlox/atlas-omnifold-research/issues/1)
