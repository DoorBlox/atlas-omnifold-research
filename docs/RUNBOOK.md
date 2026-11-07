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


## Provisional real 2×2 covariance stage (2026-11-07)

On the Actions tab, manually choose `covariance`, or commit a change with `[atlas-covariance]` in the message. This stage downloads the checked official archive, extracts **only** the nominal real-data file plus the real-data Sherpa and non-DY alternative samples, and runs `python -m src.phase7_covariance`.

It exports `real_2x2_cells.csv`, `source_manifest.csv`, `source_covariances.npz`, `covariance_total.npy`, `bin_spec_covariance.json`, and `provisional_covariance_status.json`. These are measurements and **provisional** uncertainty results, NOT an ATLAS-calibrated p-value. The 2D treatment of two-point modelling is not yet independently validated. Do not infer generator agreement/disagreement from the sign or size of uncalibrated differences.

The workflow posts a run link and completion status to [research issue #1](../issues/1) through the connected GitHub Actions bot so run IDs can be discovered without manual copying. A successful software-only CI does not mean the tagged covariance stage was executed: inspect each individual job step.

The official high-statistics pseudodata target is not extracted by this covariance stage. Its 2D closure, source correlation sensitivity and finite-covariance calibration remain outstanding (G8, G11, G12). The research-wide G15 stays **NO-GO**.
