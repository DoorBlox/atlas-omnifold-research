# Phase 7 execution runbook

## Current scope

This repository starts with a **real, downloadable official archive / HDF5 schema preflight**, followed by audited mathematics primitives and tests. It does **not** implement the official heterogeneous covariance source mapping, 2D pseudodata closure, or ATLAS final test yet. These are scientific blocker gates, not TODOs to hide.

## Actions instructions

1. Go to the repository's **Actions** tab.
2. Select **ATLAS Phase 7 preflight**.
3. Choose **Run workflow**, stage **smoke**. This tests the Python environment without downloading data.
4. Once that succeeds, run again with stage **schema**. This downloads the official ~3.6 GB archive, verifies the published MD5, selectively extracts the real and pseudodata central HDF5 files and audits the schema.
5. Open the run's **Artifacts** section and download `phase7-preflight-...` containing `schema_preflight.json`. Share that file for reconciliation with the official ATLAS source code.

Do not enable **include_target** on the standard runner without checking free space first. The standard Linux runner has a nominal 14 GB disk allowance, and pre-installed software and archive extraction share that space.

## Interpretation rules

- Smoke PASS = software primitives are testable, **not ATLAS scientific validation**.
- Schema PASS = official archive MD5 and actual HDF5 structure were read, **not 2D measurement inference**.
- G5 (source-wise uncertainty family mapping), G8 (calibration), and G11 (official 2D closure) remain unresolved.
- G15 remains **NO-GO** until all critical gates pass.
- Never upload or commit the Zenodo archive or large HDF5 datasets to GitHub.
- GitHub Actions usage for a private repository can consume billing minutes.

## Official dataset

Zenodo: https://zenodo.org/records/11507450

Published archive MD5: `9b838510f41e1d5a8b26d7f3c5b2ca42`.

## Next scientific coding stage

After a schema run, map actual measured/generator weight columns and uncertainty families to the official ATLAS implementation. Construct the *nominal-generator-only* frozen thresholds and four-cell support before projecting all source-specific variations. Only run 2D closure with the official pseudodata target once this mapping is verified.

A successful setup is not a physics finding.
