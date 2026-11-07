# Phase 7 covariance-model sensitivity — evidence checkpoint

**Date:** 2026-11-07. **Scientific status:** descriptive/model sensitivity only; **G15 NO-GO**.

## Provenance

This analysis used **executed official ATLAS result artifacts**, not a freshly simulated physics measurement:

- Real ATLAS source-wise covariance and normalized 2x2 cell fractions: [GitHub Actions run 42324639484](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42324639484), artifact `phase7-preflight-12`.
- Official pseudodata and 23,888,304-event known target: [run 42327464929](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42327464929), artifact `phase7-preflight-17`.
- Frozen nominal generator thresholds: `m_star=10.594606399536133 GeV`; `N_star=11`; selection `pT_trackj1 > 5 GeV`.
- The artifact-backed local calculation ran `python -m src.phase7_model_sensitivity`; project test suite reported **17 passed**. An independent GitHub Actions sensitivity stage was also committed; GitHub execution must be separately verified.

## Uncalibrated correlation-model sensitivity

| Provisional covariance treatment | Real-data quadratic | Pseudodata quadratic |
|---|---:|---:|
| All source covariances fully correlated as constructed | 1.607910 | 1.802996 |
| DD source decorrelated in fixed orthonormal contrast basis | 1.475683 | 1.569789 |
| Sherpa source decorrelated in fixed orthonormal contrast basis | 1.637457 | 2.485273 |
| DD and Sherpa both decorrelated | 1.436672 | 2.041870 |
| Both two-point amplitudes halved | 2.439395 | 5.103356 |
| Both two-point amplitudes multiplied by 1.5 | 1.380397 | 0.928533 |
| DD source excluded (stress test only) | 1.886707 | 1.941696 |
| Sherpa source excluded (stress test only) | 7.004018 | 16.781815 |
| DD and Sherpa excluded (stress test only) | 8.264883 | 16.874381 |

**All entries are uncalibrated squared Mahalanobis diagnostics. They are not chi-square p-values, exclusions, significance levels, or scientifically approved alternative ATLAS models.** The alternative source correlation model is a *project-defined contrast-space stress test* rather than a validated ATLAS prescription. Source omission is an extreme stress test only. The strong sensitivity to omitting Sherpa means G5/G12 cannot be declared validated.

## Secondary association diagnostics

The log odds ratio uses LL, LH, HL, HH in that order:

`L = log(p_LL*p_HH / (p_LH*p_HL))`.

- Real unfolded ATLAS minus nominal generator: `Delta L=-0.05973347757838`; provisional fully correlated delta-method standard error `0.09242249730943`.
- Official unfolded pseudodata minus independent target: `Delta L=+0.05223614479752`; provisional standard error `0.05639618687740`.

The calculations use the respective source-wise 4x4 shape covariances and the usual gradient; they are descriptive and conditional on the provisional uncertainty model. They must not be translated into final significance claims.

## Gate assessment

- G3/G4: executed with official weighted events; PASS under implemented thresholds and support checks.
- G5: **PROVISIONAL**. The published reference code's 1D Sherpa smoothing is not automatically defined for this 2D table. The DD source and nuisance correlation assumptions need independent methodological verification.
- G6: numerical contrast covariance PASS in the executed official-data jobs.
- G8: **UNVERIFIED**. Parametric Gaussian toys do not prove ATLAS calibration.
- G11: a single official pseudodata-versus-truth closure is executed; repeated-sampling coverage **not** established.
- G12: nine stress scenarios executed locally; *official correlation model* remains unverified.
- G15: **NO-GO**; no formal real-data p-value.

## Next methodological work

Independently verify how the official `multifold_util.py` and `2_pseudo_results.ipynb` handle the bootstrap sample covariance and 1D two-point terms; then specify and justify a 2D correlation prior **before** choosing any inference threshold. Design and execute a model-conditional null simulation with explicit covariance-estimation assumptions, and report it as such, without calling it measured ATLAS coverage.

Do not select a source-correlation scenario based on how favorable the resulting real-data statistic appears.
