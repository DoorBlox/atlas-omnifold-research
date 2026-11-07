# Phase 7 — mass, multiplicity and joint association diagnostic

**Source:** Existing, checksum-verified official ATLAS four-cell summaries in `data/derived/phase7-v1`. **No raw-data download, new binning or parameter tuning.** The Python implementation is `src/phase7_interaction.py`, with synthetic and official-snapshot regression checks in `tests/test_phase7_interaction.py`.

**Scientific status:** exploratory **descriptive** decomposition using the **provisional** 29-source covariance. The nominal generator or independent pseudodata truth is **treated as fixed**; generator finite-MC variance and measurement–reference cross-covariance have NOT been propagated. No p-values, significance estimates, agreement claims or validated detector-level coverage are calculated. **G15 NO-GO.**

## Exact definitions

Cells are ordered **LL, LH, HL, HH** for mass below/above 10.594606399536133 GeV and leading charged-track multiplicity at most/above 11, using `pT_trackj1 > 5 GeV`.

- **Mass-low marginal:** `p_LL + p_LH`, gradient `(1, 1, 0, 0)`.
- **Multiplicity-low marginal:** `p_LL + p_HL`, gradient `(1, 0, 1, 0)`.
- **Joint log-odds association:** `log[(p_LL p_HH)/(p_LH p_HL)]`. Its gradient is `(1/p_LL, -1/p_LH, -1/p_HL, 1/p_HH)`. Requires four strictly positive cells.

For each observable with gradient `g`, the **conditional, provisional** measurement variance is `g.T @ C_measurement @ g`. Each source-specific variance is `g.T @ C_source @ g`, and the source's variance fraction is that quantity divided by the sum across 29 sources. All matrices must be symmetric, finite, positive-semidefinite and annihilate the normalized four-cell sum direction. This is a *first-order delta-method* approximation for the nonlinear log-odds ratio.

## Computed decomposition from preserved official-data results

The following were computed **locally from the permanently pinned original result files** and are pending independent tagged GitHub CI confirmation.

| Study | Observable | Measurement minus reference | Provisional measurement-only standard error | Largest variance source | Fraction of observable variance |
|---|---|---:|---:|---|---:|
| Real ATLAS vs nominal generator | Mass-low fraction | +0.00368009 | 0.01835766 | DD unfolding | 31.20% |
| Real ATLAS vs nominal generator | Multiplicity-low fraction | -0.01469025 | 0.01166197 | Main tracking efficiency | 34.63% |
| Real ATLAS vs nominal generator | Joint log-odds ratio | -0.05973348 | 0.09242250 | **Sherpa hidden-variable** | **94.86%** |
| Pseudodata vs independent known target | Mass-low fraction | -0.02297566 | 0.01978204 | Sherpa hidden-variable | 35.83% |
| Pseudodata vs independent known target | Multiplicity-low fraction | -0.00196360 | 0.00840772 | DD unfolding | 21.68% |
| Pseudodata vs independent known target | Joint log-odds ratio | +0.05223614 | 0.05639619 | **Sherpa hidden-variable** | **87.93%** |

**Key interpretation:** The provisional 2D Sherpa assumption overwhelmingly determines the *modelled uncertainty* of the **joint association**, but is not similarly dominant for the 1D marginals. Thus the 2D association is where a correctly justified Sherpa/hidden-variable correlation model matters most. These percentages are **modelled variance shares**, not probabilities that a source caused an experimental discrepancy.

The diagnostic does **not** establish that a generator agrees/disagrees with the experiment, nor is it a license to remove the Sherpa component or to choose a model based on the size of the observed real-data discrepancy.

## Why this matters for the next stage

1. **Keep the three diagnostics distinct.** The joint log-odds probes the non-factorizable association beyond separately reporting the two marginals, but the observed difference is still descriptive.
2. **Do not claim official 2D covariance replication.** The public ATLAS 1D notebook uses `smooth_uncertainty(sherpa_counts - nominal_counts, bin_centers)`. The helper `multifold_util.smooth_uncertainty` source remained inaccessible through CERN GitLab during the audit; its unique 2D counterpart is not specified.
3. **Avoid wasted CI minutes.** This exact diagnostic is based solely on `data/derived/phase7-v1` (33,594 bytes of source results), requiring no 3.65 GB Zenodo download or GitHub artifact download. A future alternate 2D Sherpa protocol may require **signed** per-cell source shifts not recoverable from rank-one covariance outer products.
4. **Next methodological gate:** obtain/verify helper function bodies and pre-specify source inclusion and 2D Sherpa/DD handling independently of the real-data statistic. If required, plan one targeted run to emit versioned, signed 2x2 count-level source sums; do not attempt to reverse-engineer lost signs from the frozen covariance matrices.

**Source runs:** real [42324639484](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42324639484), pseudodata [42327464929](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42327464929), pinned snapshot [42380892986](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42380892986). This document is an analysis note, not a publication-ready claim.
