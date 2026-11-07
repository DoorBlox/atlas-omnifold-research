# Phase 7 — finite-MC shared-event covariance bounds and replica-denominator audit

**Checkpoint:** 2026-11-07. **Scientific permission: G15 NO-GO.**
**Original data:** ATLAS 2024 Z+jets OmniFold, DOI 10.5281/zenodo.11507450.
**Source of numerical inputs:** immutable, SHA-256 verified four-cell summary snapshot `data/derived/phase7-v1` — originally derived from [real run 42324639484](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42324639484) and [pseudo run 42327464929](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42327464929).
**New verified execution:** [main workflow run 42384589187](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42384589187): **46 Python tests passed**; frozen snapshot verification and both new stages passed; `phase7-preflight-40` artifact contains JSON/NPZ outputs. [Minimal CI run 42384751385](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42384751385): **34 tests passed**, including the finite-MC bounds, using only NumPy/pytest.

## 1. Unknown shared-support finite-evaluation-MC covariance — conditional envelope

The unfolded nominal weights (`weights_nominal`) and generator weights (`weight_mc`) are defined on common simulated events. Their finite-evaluation-MC shape uncertainties may be correlated. The frozen v1 snapshot does **not** store the original cross products `sum_event(weights_nominal * weight_mc)`.

We can nevertheless bound the contribution to each *scalar* observable from the **finite-evaluation-MC component** using Cauchy–Schwarz, without extracting more events.

Let `p` be the four normalized unfolded fractions, `q` the normalized nominal generator fractions, and `Neff_q,i` the generator's per-cell effective counts. Under independent weighted-Poisson cell sums, the reference shape covariance is

```text
M_q = I - q * 1^T
C_q,finite_MC = M_q diag(q_i^2 / Neff_q,i) M_q^T
```

For the observable gradients `g_p` (measurement) and `g_q` (reference), compute `v_p = g_p^T C_p,finite_MC g_p`, `v_q = g_q^T C_q,finite_MC g_q`. The joint log-odds gradient uses **different** fractions for each sample: `g(p) = (1/p_LL, -1/p_LH, -1/p_HL, 1/p_HH)`.

With `v_other` the provisional *measurement-only* variance from the remaining 28 sources **assumed independent of the generator**,

```text
Var(delta) = v_other + v_p + v_q - 2 Cov(p_finite_MC, q_finite_MC)
|Cov(p_finite_MC, q_finite_MC)| <= sqrt(v_p*v_q)
v_other + (sqrt(v_p)-sqrt(v_q))^2
  <= Var(delta) <=
v_other + (sqrt(v_p)+sqrt(v_q))^2
```

**Executed values (no large dataset download):**

| Real-data observable | Previous reference-fixed provisional SE | Conditional finite-MC uncertainty minimum SE | Conditional maximum SE |
|---|---:|---:|---:|
| Mass-low fraction | 0.01835766 | 0.01832393 | 0.01844117 |
| Multiplicity-low fraction | 0.01166197 | 0.01160967 | 0.01178794 |
| Joint mass × multiplicity log odds | 0.09242250 | 0.09163604 | 0.09431054 |

This provides a *conditional sensitivity interval*, NOT a full statistical uncertainty bound. It assumes the other systematic/unfolding covariance components are unrelated to generator fluctuations. If Sherpa, DD, training, and generator effects have additional cross-covariances, they are **not** bounded by the table. The original 29-source covariance remains scientifically **provisional**.

The largest change in the joint log-odds SE under this finite-MC-only envelope is around 2.04% relative to the reference-fixed value. The official 2D Sherpa and DD correlation choices remain a more consequential unknown.

Source and tests: `src/phase7_crosscov_bounds.py`, `tests/test_phase7_crosscov_bounds.py`. Tests verify the full weighted-count Jacobian identity, Cauchy extremes, separate nonlinear gradients, frozen official input and fail-closed errors.

## 2. Replica covariance denominator sensitivity — candidate, not official

The archived prototype uses population-style `1/R` for the covariance of bootstrap and NN-ensemble source replicas; the common unbiased sample covariance convention uses `1/(R-1)`. Exact re-scaling on the existing four-cell source covariances requires only multiplying each replica-family matrix by `R/(R-1)`.

**Important:** The external CERN GitLab `multifold_util.fill_cov_matrix` body is still inaccessible and has **not** been independently verified; no claim that the second convention is the *official ATLAS implementation* is warranted.

| Quantity | Real ATLAS sample | Official pseudodata |
|---|---:|---:|
| Data bootstrap replica count | 100 | 25 |
| MC-training bootstrap count | 25 | 25 |
| Neural-network ensemble members | 100 | 100 |
| Provisional total covariance trace change when changing denominator | +0.02676% | +0.05247% |
| Uncalibrated quadratic, original `1/R` | 1.607910 | 1.802996 |
| Uncalibrated quadratic, sample `1/(R-1)` candidate | 1.606995 | 1.802570 |

These values are descriptive *covariance-construction sensitivity diagnostics*, **not p-values**, and do not establish official ATLAS statistical coverage. The small changes indicate that the denominator choice is less influential for these particular frozen source matrices than source inclusion, Sherpa smoothing and DD assumptions.

The exact original 29 source matrices and source names remain unchanged in immutable `data/derived/phase7-v1`. Code: `src/phase7_divisor_audit.py` (already included before this milestone). Diagnostic outputs do not replace v1.

## 3. CI-cost optimization: no duplicate heavy runs for ordinary derived-analysis changes

The repository now has two scoped workflows:

- [`atlas-phase7-lite.yml`](../.github/workflows/atlas-phase7-lite.yml): changes to **derived** covariance/snapshot/sensitivity/calibration sources and corresponding tests run the minimal Python + NumPy + pytest workflow, verifying the immutable local snapshot. Run 42384751385 passed all **34** lightweight tests and produced cross-covariance bounds without any Zenodo or Actions-artifact download.
- [`atlas-phase7.yml`](../.github/workflows/atlas-phase7.yml): changes to event-level HDF5/preflight/core shape code, explicit run-trigger files or the heavy workflow itself. A full official archive is fetched **only** for the relevant explicit data stages (`schema`, `projection`, `covariance`, `closure`), not for lightweight analyses.

The one-time CI workflow-file edit triggered both verification workflows, which completed successfully. Future ordinary derived-source edits should trigger only the **lightweight** workflow. The user should still inspect actual job steps rather than interpreting a generic green status.

## 4. Next scientific priority

1. Retrieve and inspect exact official CERN `multifold_util.fill_cov_matrix` and `smooth_uncertainty` source code with versioned provenance. The web retrieval to the GitLab public path returned HTTP 403. Do **not** invent those functions from memory.
2. Prespecify the **2D** Sherpa, DD, source-inclusion and correlation approach independently of observed real-data agreement. The original ATLAS 1D notebook does **not** define a unique normalized 2×2 covariance prescription.
3. Only if source-level signed four-cell shifts or shared weight cross products are indispensable, plan a **single** event-level extraction into a separate versioned `phase7-v2` summary; do not redownload the 3.65 GB dataset for existing uncertainty diagnostics.
4. Preserve G15 **NO-GO** and the existing descriptive scientific interpretation until methodological calibration/coverage are sufficiently justified.
