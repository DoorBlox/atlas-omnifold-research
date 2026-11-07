# Phase 7 v2 — One-time signed four-cell sufficient-statistics extraction

**Scientific status:** data-acquisition upgrade only; **G5/G8/G12 unresolved, G15 NO-GO**. This is not a new unfolding model or an endorsed ATLAS 2D covariance prescription.

## Why v2 is necessary

The immutable 33,594-byte [v1 snapshot](../data/derived/phase7-v1/) retains normalized four-cell fractions and 29 provisional covariance matrices, but **not the signed count-level shifts** from which alternative 2D DD/Sherpa prescriptions could be reconstructed, or the per-cell generator–unfolded **shared-event mixed weight sums**. An outer-product nuisance covariance generally loses the sign of the original shift, so the missing information cannot be recovered from v1.

A single repeat read of the official source is justified to capture precisely these sufficient statistics, then publish a compact, independently verifiable **v2** result without storing raw events.

## Input and frozen decisions

Original public archive: [ATLAS Zenodo 11507450](https://doi.org/10.5281/zenodo.11507450), verified archive MD5 `9b838510f41e1d5a8b26d7f3c5b2ca42`. The pipeline selects exactly six fixed-format Pandas HDF5 supports (real and pseudodata nominal, Sherpa, non-DY) and **does not unpack the 23.9-million-event pseudodata target again**: its known-truth fractions and effective counts are already archived in v1.

The analysis retains the v1 generator-defined `pT_trackj1 > 5 GeV` selection, mass threshold `10.594606399536133 GeV`, and charged-track threshold `11`, with **LL, LH, HL, HH** ordering. Do not tune any threshold using the unfolded measurement. The v2 extraction must reproduce both v1 nominal generator/measurement fraction vectors and selected-event row counts (417,401 in each nominal sample) before results can be committed.

## What is retained in small JSON

For **every named weight column** (including nominal, generator, 22 nuisance terms, bootstrap/NN replicas and DD terms where present), separately for every four-cell support:

- `sum_w`: **signed** weight sum, needed to preserve the direction of source shifts.
- `sum_w2`: sum of squared event weights.
- `sum_w_times_mc`: sum of the source weight times `weight_mc`.
- `sum_w_times_nominal`: sum of the source weight times `weights_nominal`.
- Selected and total row counts, the per-cell unweighted counts and exact names of all source columns.
- Each input HDF5 SHA-256, original archive MD5/DOI, output SHA-256, frozen bin definitions, and explicit `G15_NO_GO` status.

Outputs are **`data/derived/phase7-v2/moments.json` and `provenance.json` only**; the first file must be under 2 MB. Event-level records, raw HDF5 and the 3.65 GB ZIP are neither committed nor uploaded as artifacts.

This is sufficient to reconstruct **signed source-bin shapes** for the frozen grid and the particular independent-weighted-Poisson finite-MC shared-support products. It is **not** sufficient to change the binning/selection, reproduce event-level unfolding correlations, refit neural networks, reconstruct arbitrary source-to-source event-level cross-products, or validate the Sherpa/DD 2D correlation structure by itself.

## Safeguards before spending Actions time

The one-time workflow [`atlas-phase7-v2.yml`](../.github/workflows/atlas-phase7-v2.yml) runs its **synthetic test suite and v1 checksum verification before the expensive official-data download**. The extractor has 14 synthetic regression tests (84% local module coverage when developed), checking signed sums, mixed moments, chunk-size consistency, nonfinite input, immutable bin provenance, output hashes and overwrite refusal.

Heavy workflow triggering is **explicit only**: manual `workflow_dispatch` or a change to `ops/v2-request.txt` with commit message containing `[atlas-v2]`. It is not activated by editing the README or ordinary derived-analysis Python code.

After a successful run, the GitHub Actions bot commits the small v2 files to `main` with `[skip ci]` and records the run URL in [issue #1](https://github.com/DoorBlox/atlas-omnifold-research/issues/1). A failed v1 cross-check must **fail closed** and must not publish the output. Check the actual v2 run's steps and provenance rather than assuming a green build proves the science.

## How to use the acquired v2 information

First verify that the new signed moment tables reproduce v1 *exactly within the floating-point tolerance*. Then reproduce the old 29-source provisional covariance from v2 count sums, before testing any *new* model. With signs preserved, the analysis can define alternative **pre-specified** DD and Sherpa source treatments without re-downloading ATLAS. Shared-event moments allow a better finite-evaluation-MC cross covariance calculation under explicitly stated conditional assumptions.

The next scientific step is **not** to select the model with the most favorable real-data statistic. Obtain the official CERN helper source if possible, justify a source list and 2D correlation protocol a priori, evaluate the independent pseudodata target, and disclose any remaining calibration limitations. **G15 stays NO-GO until these gates are legitimately satisfied.**
