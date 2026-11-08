# Independent audit: what changed in joint association?

**Status:** new algebraic, descriptive secondary calculation from the already-frozen four-cell fractions, completed **8 November 2026**. The analysis below is **not** a new ATLAS measurement, an experiment, a new systematic error determination, a significance test, or a statement of experimental uncertainty coverage.

## Why this check matters

The manuscript's central joint-statistics claim is correct: two marginal probabilities do not uniquely fix a normalized two-by-two table. However, the difference between **log odds ratios** need not isolate a numerically large change in every other measure of association. In particular, different marginal distributions can alter the log odds even when the covariance of the corresponding binary indicators stays fixed. The paper should not casually equate its reported `ΔL` with a uniquely marginal-independent physical correlation shift.

For a four-cell shape `(LL, LH, HL, HH)` with cell fractions `p`, define

- `M = p_LL + p_LH`: low-mass marginal;
- `N = p_LL + p_HL`: low-multiplicity marginal;
- `D = p_LL - M*N`: *covariance of the two binary low-category indicators*, a distinct association coordinate;
- `L = ln(p_LL*p_HH/(p_LH*p_HL))`: natural log odds ratio, defined here because each cell is positive.

Any legal distribution can be reconstructed from `(M,N,D)` as:

```text
LL = M*N + D
LH = M*(1-N) - D
HL = N*(1-M) - D
HH = (1-M)*(1-N) + D
```

This representation shows exactly which part of a **four-cell joint distribution** is not determined by its marginals. `D` is *not* the same coordinate as `L`; the two are related through `M,N`.

## Exact observed descriptive calculations

Inputs: [versioned fractions](../results/kti-nov18/tables/joint_cells.csv), **real unfolded versus shared nominal generator** and, independently, **unfolded pseudodata versus independently sampled known truth**. Source inputs and distinctions remain unchanged.

| Quantity | Real unfolded | Real nominal generator | Pseudo unfolded | Independent target |
| --- | ---: | ---: | ---: | ---: |
| Low-mass `M` | 0.5036786612 | 0.4999985758 | 0.5091590618 | 0.5321347226 |
| Low-multiplicity `N` | 0.5614679626 | 0.5761582149 | 0.5567186560 | 0.5586822563 |
| Binary-indicator covariance `D` | 0.1459157847 | 0.1460843008 | 0.1531656005 | 0.1517052237 |
| Log odds `L` | 2.7512719070 | 2.8110053846 | 2.9222386989 | 2.8700025541 |

Derived unfolded-minus-reference changes:

| Measure | Real versus generator | Pseudodata versus truth |
| --- | ---: | ---: |
| `ΔM` | +0.0036800854 | -0.0229756608 |
| `ΔN` | -0.0146902523 | -0.0019636003 |
| `ΔD` | **-0.0001685161** | **+0.0014603768** |
| `ΔL` | -0.0597334776 | +0.0522361448 |

**Important:** `D` is a covariance of *binary threshold indicators*, not the originally reconstructed experimental four-by-four covariance matrix of the *estimator*. Do not conflate these different uses of the word *covariance*. A small `ΔD` is not a statistically insignificant result; no sampling significance of `D` has been established.

## Illustrative counterfactual decomposition of `ΔL`

This is a **path-dependent arithmetic diagnostic**, not a unique causal, physical, or statistical decomposition. For each pair, start at the reference `(M_q,N_q,D_q)`, change the marginals to their unfolded `(M_p,N_p)` **while holding `D=D_q`**, then change `D` to `D_p` at the unfolded marginals. All intermediate cells are positive.

| Component in the specified order | Real versus generator | Pseudodata versus truth |
| --- | ---: | ---: |
| Log-odds change with marginals adjusted, reference `D` fixed | -0.0553563718 | +0.0129187899 |
| Remaining log-odds change from `D_q` to `D_p` at unfolded marginals | -0.0043771058 | +0.0393173549 |
| Sum, equal to actual `ΔL` | **-0.0597334776** | **+0.0522361448** |

These numbers depend on which coordinate is held fixed and the order of changes. The real-data log-odds contrast in this counterfactual is therefore **largely reproduced by the marginal adjustment** under fixed binary-indicator covariance. In pseudodata, the pattern differs. **Neither result should be elevated to a tested physics effect or a proof of no association difference.**

## Automated calculation and regression tests

The same computations are implemented in [`src/joint_association_audit.py`](../src/joint_association_audit.py), with pinned expectations and invalid-shape checks in [`tests/test_joint_association_audit.py`](../tests/test_joint_association_audit.py). The lightweight GitHub workflow runs these tests and generates a separate JSON diagnostic. That diagnostic is **outside** the immutable version-one result manifest and is **not** additional ATLAS evidence.

```bash
python -m pytest -q tests/test_joint_association_audit.py
python -m src.joint_association_audit --cells results/kti-nov18/tables/joint_cells.csv --out outputs/joint-association-audit.json
```

## Reproduce from the immutable joint fractions

```python
import csv, math
from pathlib import Path
rows = list(csv.DictReader(Path("results/kti-nov18/tables/joint_cells.csv").open()))
for sample in ("real", "pseudo"):
    selected = {r["cell"]: r for r in rows if r["sample"] == sample}
    def coords(key):
        x = {c: float(selected[c][key]) for c in ("LL", "LH", "HL", "HH")}
        m, n = x["LL"] + x["LH"], x["LL"] + x["HL"]
        d = x["LL"] - m*n
        log_odds = math.log(x["LL"]*x["HH"]/(x["LH"]*x["HL"]))
        return m, n, d, log_odds
    p = coords("measurement_fraction")
    q = coords("reference_fraction")
    m, n, d, L = p
    mq, nq, dq, Lq = q
    ll = m*n + dq
    middle = (ll, m-ll, n-ll, 1-m-n+ll)
    Lmiddle = math.log(middle[0]*middle[3]/(middle[1]*middle[2]))
    print(sample, "delta D", d-dq, "delta L", L-Lq,
          "marginal-only path", Lmiddle-Lq, "D remainder", L-Lmiddle)
```

## Manuscript action

Add `D` and the decomposition as a **clearly labeled additional descriptive check** if the student and adviser agree it improves the paper. If adopted, update the abstract, Methods, Results, Discussion, tables/figures as appropriate, keeping existing quantities and all citations intact. **Do not silently replace the published `L` figures**; the measures capture different aspects of the same table.

A validated uncertainty estimate for `ΔD` would require a separately audited gradient and covariance propagation across the appropriate source model. It **has not been calculated here**. This check does not change G5/G8/G11/G12/G15.
