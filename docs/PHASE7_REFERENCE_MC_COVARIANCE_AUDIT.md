# Phase 7 — Reference finite-MC uncertainty and shared-sample covariance audit

**Status:** mathematical reconstruction checked locally against 100 synthetic weighted samples; values calculated from the **checksum-pinned** `data/derived/phase7-v1` official result snapshot. This is a source-aware **provisional** covariance audit, not a detector-level ATLAS validation or a p-value. **G15 NO-GO.**

## 1. Known-target finite-MC statistics can be recovered without event data

The official known pseudodata target HDF5 was previously processed in run [42327464929](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42327464929). The archived `pseudo_closure_cells.csv` retains the normalized truth fraction `q_i` and target truth effective count `N_eff,i` in each of four disjoint cells.

For target weighted cell sum `h_i = sum_event w_event`, squared-weight sum `s_i = sum_event w_event**2`, total `H = sum_i h_i`, and `q_i = h_i/H`,

```text
N_eff,i = h_i^2 / s_i
s_i / H^2 = q_i^2 / N_eff,i

M = I - q 1^T
C_target,finiteMC = M diag(q_i^2 / N_eff,i) M^T
```

The second line means the **normalized truth covariance can be reconstructed from the retained fractions and effective counts**. This is algebraically identical to the direct unnormalized-count Jacobian `J = (I - q 1^T)/H` times `diag(s)` times `J.T`, assuming independent weighted Poisson cell sums, finite second moments and no correlations between target-event weights beyond this model. It does not require the high-statistics ~23.9-million-event file again.

The identity was independently checked with 100 synthetic positive-weight event samples and agreed numerically with the direct sum-of-squares/Jacobian calculation.

### Exact calculation from saved values

For the provisional unfolded pseudodata measurement covariance `C_p`, we evaluated the added target term `C_t` and reported `sqrt(g^T (C_p + C_t) g)` **assuming the known target and unfolded pseudodata are independent and treating all remaining covariance assumptions as fixed**.

| Observable | Pseudodata-only provisional SE | Target finite-MC SE | Combined provisional SE | Target share of combined variance |
|---|---:|---:|---:|---:|
| Mass-low fraction | 0.0197820428 | 0.0001296555 | 0.0197824677 | 0.00430% |
| Multiplicity-low fraction | 0.0084077168 | 0.0001288166 | 0.0084087035 | 0.02347% |
| Joint log-odds association | 0.0563961869 | 0.0013423359 | 0.0564121597 | 0.05662% |

The target sampling term is **small under this model**. These are **not** validated coverage statements; the 2D Sherpa/DD measurement covariance remains provisional. The log-odds gradient for the **target** uses `1/q_i` values (not measurement `1/p_i`), a distinction that matters in the correct delta-method propagation. For the table above, the independent target contribution to the log-odds difference uses its own **target gradient** `(1/q_LL,-1/q_LH,-1/q_HL,1/q_HH)`, rather than the unfolded measurement's gradient. The combined number remains **provisional** because the measurement covariance and source-correlation assumptions are not independently validated.

## 2. A distinct open question: covariance shared by real ATLAS weights and nominal generator

Real unfolded weights `w_p = weights_nominal` and generator weights `w_q = weight_mc` live on the **same event support**. For a future unconditional real measurement–generator comparison, naively adding independently estimated covariances may be incorrect.

For each cell `i`, define
- `S_pp,i = sum_event (w_p)^2`,
- `S_qq,i = sum_event (w_q)^2`,
- `S_pq,i = sum_event (w_p)(w_q)`, and `H_p = sum_i sum_event w_p`, `H_q` analog;
- `J_p = (I - p 1^T) / H_p`, `J_q = (I - q 1^T) / H_q`.

Under a shared-event, independent-Poisson-weighted-bin model,

```text
Cov_eval(p - q) =
    J_p diag(S_pp) J_p^T
  + J_q diag(S_qq) J_q^T
  - J_p diag(S_pq) J_q^T
  - J_q diag(S_pq) J_p^T
```

This is a **candidate finite-evaluation-MC shared-support correction**, not the full detector/unfolding cross-covariance. It would replace, not duplicate, the current evaluation-MC term if an unconditional comparison were adopted. The generator estimate's dependence on the same training/evaluation data and other source families needs separate expert treatment.

The existing `phase7-v1` snapshot retains the generator effective counts, which can reconstruct the standalone generator finite-MC shape covariance under the same approximation. It **does not** retain `S_pq` or separate signed source shifts: these missing moments cannot be reconstructed uniquely from rank-one covariance outer products.

## 3. Exact requirements for one future, targeted original-data pass (only when necessary)

Do **not** automatically redownload the 3.65 GB release just to calculate the already-published v1 diagnostics. If an a priori covariance protocol needs shared-event moments or signed DD/Sherpa treatment, first agree on a frozen extraction schema, then perform **one** official checksum-verified pass that writes a separate `phase7-v2` snapshot.

Minimal required four-cell summaries for each nominal real/pseudodata support:
1. Frozen selection and bin-spec checksum and original archive DOI/MD5.
2. `sum w` in each LL/LH/HL/HH cell for **every exact named nominal and source-variation weight column**, keeping signed count-level information and deterministic column order.
3. `sum w^2` for generator and nominal unfolded weights; `sum (w_nominal * w_mc)` for their **shared** selected events.
4. Raw selected cell counts, unselected counts, non-finite checks and full schema-name audit.
5. Independent Sherpa and non-DY alternative-support four-cell sums and the high-stat pseudodata known-target four-cell moments; preserve original source identities.
6. Versioned JSON schema, original-file hashes, per-output SHA-256 hashes, code commit, data extraction method, and a fail-closed comparison to frozen v1 normalized fractions and covariance outputs.
7. Re-run each measurement/source covariance under a pre-specified 2D prescription, with independent pseudodata validation **before** real-data inference.

These summaries would be much smaller than the raw event dataset and reusable across many source-correlation hypotheses. **Do not overwrite v1** or invent the sign of a shift from its stored outer product. No new event-level extraction was executed during this audit.

## 4. Open gate and exact next action

- The official one-dimensional notebook has been inspected, but CERN GitLab currently rejects retrieval of the external `multifold_util.py` helper; its `fill_cov_matrix` and `smooth_uncertainty` source bodies remain independently **unverified**.
- A physically justified **two-dimensional Sherpa/DD model** and a chosen reference-conditioned versus unconditional estimand must be documented *a priori*.
- Before reporting a final real-data generator p-value, resolve the relevant cross-covariances, 2D source inclusion, unfolding uncertainty and empirical calibration.
- **G5, G8, G12 unresolved; G15 NO-GO.**

### Reproducibility sketch (uses only pinned snapshot)

```python
import csv
import numpy as np
from pathlib import Path
root = Path('data/derived/phase7-v1/pseudo')
with (root / 'pseudo_closure_cells.csv').open() as f:
    rows = list(csv.DictReader(f))
q = np.array([float(row['independent_target_truth_fraction']) for row in rows])
neff = np.array([float(row['target_truth_neff']) for row in rows])
M = np.eye(4) - np.outer(q, np.ones(4))
C_target = M @ np.diag(q*q / neff) @ M.T
assert np.allclose(C_target @ np.ones(4), np.zeros(4), atol=1e-15)
```

## 5. Independently executed truth-gradient correction (2026-11-07)

The reusable code in [`src/phase7_target_mc.py`](../src/phase7_target_mc.py) now checks the weighted-MC Jacobian identity and computes the **log-odds target gradient at the target truth fractions**, rather than borrowing the unfolded measurement gradient. For four independent weighted-Poisson target cells, this produces the additional exact identity under the specified model:

```text
Var_target[log((q_LL*q_HH)/(q_LH*q_HL))]
    = 1/N_eff,LL + 1/N_eff,LH + 1/N_eff,HL + 1/N_eff,HH
```

**Verified GitHub Actions run:** [42384337294](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42384337294), artifact `phase7-lite-audits-2`. All **16 lightweight regression tests passed**, including tests with direct weighted histogram sums, distinct gradients, invalid inputs and the actual frozen official target summary. The 3.65 GB ATLAS dataset was **not** downloaded, and the full-data workflow was **skipped**.

- Target-only log-odds finite-MC standard error: **0.0013423359141068556** (previous approximation using the measurement gradient was **0.001415537090647602**).
- Measurement-only provisional log-odds standard error: **0.056396186877402374**.
- Combined model-conditional independent-shape standard error: **0.05641215968226347**.
- Target truth finite-MC represents **0.05662% of the combined variance** for this observable under the stated independent-target model.

The corrected values leave the original four-cell fractions and archived provisional source covariance unchanged. **The finite-MC target correction is not a substitute for 2D Sherpa/DD covariance validation, independent repeated-unfolding coverage, or the still-missing real shared-event `sum(w_nominal * weight_mc)` moments. G15 remains NO-GO.**
