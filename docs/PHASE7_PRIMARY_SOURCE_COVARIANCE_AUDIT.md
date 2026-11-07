# Phase 7: primary CERN covariance helper source-level audit (2026-11-07)

**Scope:** exact upstream Python source, not merely notebook calls or an independent port. **G15 remains NO-GO; no real-data p-value.** The official GitLab raw source was fetched successfully **in GitHub Actions CI** after direct local retrieval failed with DNS/network restrictions.

## Primary source and reproducibility

- Official file: [CERN ATLAS public `multifold_util.py`](https://gitlab.cern.ch/atlas-physics/public/sm-z-jets-omnifold-2024/-/raw/master/multifold_util.py).
- GitHub Actions [42390105795](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42390105795): succeeded, **56 regression tests passed**; AST-extracted the three primary function bodies and uploaded `official-helper/official_helper_source_audit.json` in artifact `phase7-lite-audits-6` (artifact ID **13581156453**).
- GitHub Actions [42390199178](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42390199178): succeeded; printed exact source functions (including `corr_matrix` assembly) with original line numbers in the job log for independent inspection. **The source hash matched the earlier retrieval.**
- Full official raw-file SHA-256: `cf43074fb3635b5c484dd1f35b9dc95cea938d86d206b4a2e83ab1f739e73d7f`. The upstream URL points to mutable `master`, so this is a **content hash**, not a guaranteed official commit ID.
- Function body SHA-256 pins: `fill_cov_matrix` (lines 49–58) `3783c2b851eabe440b95b629a048c4b575b82400c0e6185e662f06fe816530b4`; `smooth_uncertainty` (621–644) `86484ad56858e46a4082d98446aea1ce4c01ef07cd11fa5f41ac36d2870d3429`; `corr_matrix` (307–434) `77f617b0639f3ae012a6e3a2469860251de9d12cb192c1fa29de746da305a4f2`.
- The audit is **read-only** with respect to fetched code (AST inspection; never `exec` or import arbitrary remote code). `src/phase7_official_helper_audit.py` now requires exact full-file and all three reviewed-body hashes to mark the pinned source verified; any drift or failure leaves it unverified. The synthetic numerical port remains independently testable.

## Exact verified implementation findings

### `fill_cov_matrix` (primary source lines 49–58)

The source's three nested loops accumulate, for supplied difference vectors `d_k` when `uncerts_mean is None`,
`V[i,j] = sum_k d[k,i] * d[k,j]`. Thus **the signed shift matters**; a single two-point source gives a rank-one outer product. When `uncerts_mean` is supplied, it instead accumulates `sum_k (x[k,i]-mean[i]) * (x[k,j]-mean[j]) / (K-1)`, the **sample** replica covariance. Both formulas are now confirmed directly from the primary source rather than inferred solely from secondary implementations.

The official file's `corr_matrix` builds `mc_stat_bs` and `data_stat_bs` from whatever replica columns are present and passes their means to `fill_cov_matrix` (lines 348–359, 410–412). Although local variable `n_bootstraps = 25` appears at line 404, it is **not used** by the covariance formula; do not misinterpret it as the actual real-data data-bootstrap count. The **manifest-verified 100 real vs 25 pseudodata data-bootstrap** columns remain the relevant counts. NN ensemble covariance is separately divided by **100** at line 415. The historical provisional v1 construction used `1/R`; the candidate `R/(R-1)` scaling in `src/phase7_divisor_audit.py` is thus reference-**aligned for the replica covariance estimator**, but does **not** by itself validate the complete normalized 2D source covariance.

### DD unfolding (primary lines 378–381 and 420)

The source computes `(counts_dd - target_dd) * (nominal / target_dd)` **binwise as a signed raw-count shift**, and gives this shift to `fill_cov_matrix` in Hessian mode. **No DD smoothing** is applied in `corr_matrix`. The repository's signed `phase7-v2` DD four-cell moments allow a project-defined normalization-Jacobian projection, but this 2D extension is not declared by ATLAS as an approved covariance method.

### Sherpa hidden-variable 1D smoothing (primary lines 383–388, 621–644)

When `smooth=True` (the `corr_matrix` default), the source smooths `sherpa_counts - nom` **before** passing the result to `fill_cov_matrix` (line 421). When `smooth=False`, it uses the raw signed difference. The `smooth_uncertainty` source uses `Nsig=10`, kernel width = **one-tenth of the full ordered bin-center coordinate range**, and Gaussian weights `norm.pdf((x_j-x_i)/kernel_width)` normalized by their sum. If the first bin center is positive, **log bin-centers** are used. This matches the separately tested vectorized `smooth_1d_port` formula. There is **no source-specified canonical ordering or joint 2D smoothing kernel** for the four mass×multiplicity cells. The synthetic permutation test proves that treating the four cells as an arbitrary ordered 1D vector changes the output.

### `corr_matrix` family inclusion (primary lines 335–341, 390–425)

The primary 1D correlation builder includes a diagonal finite evaluation-MC term, MC and data bootstrap terms, the NN ensemble term, theory shifts, DD, Sherpa HV, **luminosity**, top-background and non-DY. Its `v_total` at line 425 does **not** include the separately enumerated experimental event/track/muon nuisance group families, despite earlier collecting their column names. The inspected public pseudodata notebook's *cell-26 chi-square path* has an **even narrower** inclusion than `corr_matrix` (notably no luminosity). Neither is a source-authorized choice for a **new 2D normalized compatibility test**. The already documented 15-vs-29 family counterfactual demonstrates material sensitivity; it is not a model-selection criterion.

## Decisions and unresolved physics

1. **Source-level 1D helper verification completed for this pinned snapshot**: `fill_cov_matrix`, `smooth_uncertainty`, and `corr_matrix` were obtained from the official file and their formulas/assembly inspected. This is not an independent upstream commit-tag verification; it is reproducible using exact file/function SHA-256.
2. Maintain four **a priori** DD/Sherpa scenarios from `PHASE7_CORRELATION_PROTOCOL_V2.md` (both full; DD-only four-bin; Sherpa-only four-bin; both four-bin). Do **not** choose by real-data fit. Do **not** silently impose 1D smoothing on flattened 2D cells.
3. The normalized four-cell Jacobian, signed shifts and conditional shared-event finite-MC candidate are mathematically testable and versioned; the official `corr_matrix` is a **1D raw-count prescription**, not a verified complete 2D generator-minus-unfolded covariance.
4. G5: **PROVISIONAL** (2D source family inclusion, bin-to-bin nuisance correlations and correlations between unfolding and generator reference unresolved). G8: **UNVERIFIED frequentist coverage**; Gaussian toys are conditional model checks. G12: **UNVERIFIED 2D model validity**; one known-target pseudodata experiment is not repeated-sampling calibration. G15: **NO-GO**: do not calculate or report a real-data generator-compatibility p-value/sigma.
5. Next meaningful scientific action is an independently motivated **fixed 2D uncertainty source-family and cross-covariance protocol**, followed by null/pseudodata validation using the existing frozen v1/v2 moments; **do not re-download the 3.65 GB archive** for unchanged four-cell summaries.

## Reproduction

```bash
python -m pytest -q tests/test_phase7_official_helper_audit.py
python -m src.phase7_official_helper_audit --out outputs/official-helper
python -m src.phase7_official_excerpts  # prints bounded primary functions; only when CERN reachable
```

Local before source-pin integration: **13 tests passed, 82% module statement coverage**; after adding the hash-drift guard: **14 tests passed, 82% coverage**. The lightweight CI workflow exercises the full existing derived-only suite with no ATLAS archive download. The source probe's `SOURCE_UNAVAILABLE` result must not be mistaken for source mismatch; the audited source is explicitly version-hash pinned.
