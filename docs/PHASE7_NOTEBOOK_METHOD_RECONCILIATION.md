# Official ATLAS notebook 1D covariance: exact-scope reconciliation

**2026-11-08 supersession notice:** This document records the original notebook-only audit. Its historical statement below that the CERN helper was inaccessible is **superseded** by the [primary hash-pinned source-level audit](PHASE7_PRIMARY_SOURCE_COVARIANCE_AUDIT.md) (CI 42390285792). The 1D helper's Hessian, R−1 replica covariance, DD raw shift, and optional 1D Sherpa smoother are now verified for that pinned snapshot. **No 2D source-correlation model or calibrated real-data p-value is thereby verified.** See the [Deep Research adjudication](PHASE7_DEEP_RESEARCH_ADJUDICATION_2026_11_08.md).

**Reference actually inspected:** user's supplied official ATLAS `2_pseudo_results.ipynb`, code **cell 26** (117 lines), plus cell 11 (uncertainty plotting). The notebook downloads `multifold_util.py` from CERN GitLab:
`https://gitlab.cern.ch/atlas-physics/public/sm-z-jets-omnifold-2024/-/raw/master/multifold_util.py`.

**Access boundary:** The notebook itself was inspected, but the *external* body of `fill_cov_matrix` and `smooth_uncertainty` was not retrievable through the available automated network access (GitLab refused access). Do **not** call their exact internal normalization, smoothing, or source correlation implementation verified.

## Verifiable formula map from the notebook

| 1D notebook (cell 26 line references) | What it actually does | Relevance for our normalized 2×2 analysis |
|---|---|---|
| 23–28 | Histogram known pseudodata target using `target.weight_mc`; nominal unfolded sample using `weights_nominal`; evaluation-MC squared-weight sums | Independent target mapping verified. For **normalized** four-cell shape, raw squared weights need Jacobian projection, not a diagonal raw-count covariance |
| 30–48 | Form MC-training bootstrap, data bootstrap, and NN initialization histograms | Our 4-cell source matrices are constructed from released variation weights; verify the helper's covariance estimator denominator and whether different replica sets share fluctuations |
| 50–58 | Theory source variation expressed as `syst - nom` | A per-source signed four-cell shift is relevant; uncorrelated source assumptions are not automatically justified |
| 60–63 | DD uncertainty is a **binwise raw-count** shift: `(counts_dd - target_dd)*(nom/target_dd)` | Normalizing a resulting 2D shape changes the form through the normalization Jacobian. This is our **explicitly provisional** extension, not verbatim ATLAS |
| 65–67 | Sherpa hidden-variable shift is `smooth_uncertainty(sherpa_counts - nom, bin_centers)` | **1D bin-center smoothing** is not uniquely defined in a 2×2 joint table. Our unsmoothed Sherpa shape shift should remain labelled provisional |
| 69–75 | Background shifts from top-background and non-DY alternative supports | Separate source terms, with common nominal support and source-specific interpretation |
| 77–99 | Builds raw-count covariance from evaluation-MC diagonal, bootstraps, NN ensemble divided by 100, theory, DD, HV, and backgrounds | This chi-square covariance is not the same as the **full** experimental uncertainty group calculation in cell 11. Our 29-family 2D model and 15-family inclusion counterfactual must be kept distinct |
| 101–106 | Raw 1D difference `D = nom - target_counts` and nominal `dof = len(bins)-1` | Cannot simply import its `dof` to normalized 4-cell shapes: our normalization induces a null mode, with 3 independent contrasts |
| 108–115 | For initial 1D `p_value < 0.01`, re-evaluates with **diagonal DD and HV covariance** | This is a **data-dependent procedure** in a public 1D example, not a pre-registered 2D model selection rule. We must not pick a new 2D covariance because it yields preferable real-data compatibility |

The cell 11 **uncertainty plotting** section calculates experimental track, muon, luminosity, event, and theory contributions for uncertainty bands. The cell 26 *chi-square code path* includes a narrower family set. This is an actual scope distinction in the reference materials, **not proof** that the real-data uncertainty should exclude experimental sources.

## Where our code currently differs, deliberately and provisionally

1. The four joint cells are **generator-only frozen** at mass 10.594606399536133 GeV and multiplicity 11, with `pT_trackj1 > 5 GeV`, rather than the notebook's variable-specific 1D binning.
2. We work in **normalized** shape space. A four-cell distribution has three independent contrasts. The original 1D count-style covariance and degree-of-freedom rules therefore do not carry over unchanged.
3. We initially formed **29 provisional 2D source terms**. A counterfactual 15-term inclusion based on the notebook's 1D chi-square code changes the *uncalibrated* real-data quadratic from 1.608 to 12.437. That is a strong warning about inference sensitivity, **not** evidence for selecting either model.
4. Our provisional DD and Sherpa source matrices do not reproduce 1D `smooth_uncertainty` at the event level. The archived `data/derived/phase7-v1` matrices preserve the calculated covariances **exactly**, but they cannot reconstruct signed per-cell source shifts or an alternative smoothing prescription.
5. The original analysis uses source-relative counts; our data and nominal generator share support, so conditional-on-generator estimands and cross-covariance assumptions require explicit treatment.

## Required methodological decision **before final inferential testing**

- Independently obtain and record the **exact GitLab revision** and function bodies of `multifold_util.py`, particularly `fill_cov_matrix` and `smooth_uncertainty`.
- State a **pre-specified 2D target estimand and covariance protocol**, including each source family, signed shifts, correlation assumptions, DD/HV normalization and whether smoothing is defensible on a 2×2 grid. Do not optimize it against real-data fit.
- Test the protocol using an independent pseudodata target. One known-target pseudo experiment is available; repeated-unfolding coverage is **not** yet established.
- If new raw per-source four-cell weight sums are required, plan **one targeted extraction** from the original 3.65 GB archive to a separately versioned sufficient-statistics file. Avoid repeated full downloads while reviewing hypotheses. The current snapshot is intentionally *not* advertised as sufficient for arbitrary rebinning or method reconstruction.
- G5/G8/G12 unresolved; **G15 NO-GO**. No real-data chi-square p-value or sigma claim should be emitted.

**Execution optimization verified:** Committed derived snapshot in `data/derived/phase7-v1` contains 33,594 bytes of original four-cell result files, SHA-256 checked. [Archival workflow 42380892986](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42380892986) succeeded; [zero-download sensitivity workflow 42380984689](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42380984689) passed 29 tests and reproduced the analysis without a multi-GB dataset transfer.
