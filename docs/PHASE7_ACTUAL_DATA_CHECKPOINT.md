# Phase 7 actual-data checkpoint — official run 42324639484

**Execution date:** 2026-11-07 UTC. **Source commit:** `d0a2255720762713dcac1ed866a6a23850bd5868`.

**Evidence:** [GitHub Actions run #42324639484](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42324639484), artifact `phase7-preflight-12` (ID 13555355269). The job reported **8 Python tests passed** and completed the ATLAS archive, selective extraction, and provisional source-wise covariance steps successfully.

## Verified raw measurement processing

- Zenodo data: DOI 10.5281/zenodo.11507450, downloaded archive 3,648,703,812 bytes and verified MD5 `9b838510f41e1d5a8b26d7f3c5b2ca42`.
- Leading charged jet selection: `pT_trackj1 > 5 GeV`, leaving **417,401 rows**.
- Frozen nominal-generator thresholds: `m_star = 10.594606399536133` GeV; `N_star = 11` charged tracks.
- Cells are LL (mass below threshold, tracks <= 11), LH (mass below threshold, tracks > 11), HL (mass >= threshold, tracks <= 11), HH (mass >= threshold, tracks > 11).

| Cell | Raw selected rows | Nominal generator fraction | ATLAS unfolded fraction | ATLAS minus generator | Nominal generator Neff | Relative data-bootstrap uncertainty |
|:--|--:|--:|--:|--:|--:|--:|
| LL | 130,852 | 0.434162588 | 0.428715216 | -0.005447371 | 103,600.24 | 0.00297810 |
| LH | 20,175 | 0.065835988 | 0.074963445 | +0.009127457 | 16,218.03 | 0.00642203 |
| HL | 62,569 | 0.141995627 | 0.132752746 | -0.009242881 | 41,682.62 | 0.00412288 |
| HH | 203,805 | 0.358005797 | 0.363568593 | +0.005562796 | 116,283.12 | 0.00359314 |

All four cells meet the implemented `Neff >= 5000` and `data-bootstrap fractional uncertainty < 0.15` checks, conditional on the released weights and the chosen 2×2 projection.

## Provisional covariance checks

The job assembled **29 source components** (22 named one-shift nuisance variations, three replica families, finite nominal evaluation-MC, DD unfolding, Sherpa modelling and non-DY). No `weights_*` columns remained unassigned in the implemented source inventory.

- Four-cell covariance normalisation-null residual: `2.710505431213761e-19`.
- Three-dimensional contrast covariance: **rank 3** and positive definite.
- Contrast-space eigenvalues: `[0.0000424373966994, 0.000200347102097, 0.000626091099931]`.
- Contrast condition number: **14.7532871624**.
- Sourcewise covariance sum exactly equals the stored total covariance (verified from archive matrices).
- Dominant fractional contributions to total covariance trace: `trackEffMain` ~27.99%, `sherpa_hidden_variable` ~26.58%, `dd_unfolding` ~24.45% (combined **~79.02%**). These are covariance-trace contributions, **not** individual statistical significance or uncertainty percentages.

## Scientific gates and explicit limitations

| Gate | Current status |
|:--|:--|
| G3 generator-only bin thresholds | PASS, executed on official data |
| G4 2×2 effective support and bootstrap precision | PASS under implemented checks |
| G5 official source mapping, correlations and two-point systematics | **PROVISIONAL / needs independent reference-code audit** |
| G6 positive-definite, stable rank-three contrast covariance | NUMERICAL PASS |
| G8 empirical null/reference calibration | UNVERIFIED |
| G11 official 2×2 pseudodata closure against known target | UNVERIFIED |
| G12 sensitivity to source-correlation prescriptions | UNVERIFIED |
| G15 final inferential compatibility p-value | **NO-GO** |

**Interpretation restriction:** The observed differences are **descriptive ATLAS-weighted fractions**. They are not presently licensed as a `sigma` or p-value. The alternative-support contributions and DD two-point prescription are currently *provisional* and must be checked against ATLAS's official implementation. The measurement and nominal generator share MC support, so a conditional-on-generator interpretation should be retained unless cross-covariance is established.

**Next executable milestone:** create official 2×2 pseudodata closure against `files/pseudodata/target.h5`, then validate the two-point correlation model and null calibration. No new hypothesis or bin optimization after inspecting the real residual.
