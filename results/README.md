# Frozen four-cell evidence: canonical release v1

The permanent evidence directory is [`results/four-cell-v1/`](four-cell-v1/README.md). It contains normalized four-cell shapes and conditional sensitivity results derived from the 2024 ATLAS event-weight release. The inputs were originally verified on **8 November 2026**. The rename preserves the numerical CSV and scientific SVG files; changed reporting labels receive new SHA-256 hashes. See [release provenance](../docs/RELEASE_MIGRATION.md).

## Read the evidence

| Evidence | Versioned path | Purpose |
| --- | --- | --- |
| Four-cell fractions | [joint_cells.csv](four-cell-v1/tables/joint_cells.csv) | Normalized LL/LH/HL/HH real and pseudo distributions and signed contrasts |
| Marginals and association | [marginal_association.csv](four-cell-v1/tables/marginal_association.csv) | Low-mass/low-multiplicity marginals, log odds, conditional standard errors |
| Four correlation assumptions | [scenario_sensitivity.csv](four-cell-v1/tables/scenario_sensitivity.csv) | DD/Sherpa full-vs-four-bin sensitivity |
| Source contribution decomposition | [source_variance.csv](four-cell-v1/tables/source_variance.csv) | Modeled variance shares, not physical probabilities |
| Normalized covariance elements | [covariance_matrix.csv](four-cell-v1/tables/covariance_matrix.csv) | Rank-three, normalization-null four-by-four matrices |
| Figure sources | [figures](four-cell-v1/figures/) | Four SVG figures |
| Generated reporting | [MANUSCRIPT_RESULTS.md](four-cell-v1/MANUSCRIPT_RESULTS.md) | Generated prose from frozen inputs, not a standalone peer-reviewed manuscript |
| Check and reproducibility evidence | [checks.json](four-cell-v1/checks.json), [manifest.json](four-cell-v1/manifest.json), [results.json](four-cell-v1/results.json) | Twelve true QA checks, hashes, and machine-readable metadata |

The separate binary-indicator covariance coordinate and path-dependent log-odds calculation are documented in [the association audit](../docs/JOINT_ASSOCIATION_AUDIT.md) and implemented in [`src/joint_association_audit.py`](../src/joint_association_audit.py). This new calculation runs **outside the immutable bundle** and does not change the pinned manifest. CI evidence is [run 42442490666](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42442490666) (**107 tests passed in the historical frozen numerical workflow**), not a guarantee of physical model coverage or a new test run after documentation changes.

### Rebuild the historical release

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests/test_phase7_kti_bundle.py
python -m src.phase7_kti_bundle --v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 --out outputs/four-cell-v1
```

The standard output directory is `outputs/four-cell-v1`. The regression test verifies the committed SHA-256 manifest, regenerates ten files byte-for-byte, and compares three derived floating-point CSVs to machine precision (relative tolerance 1e-12). Their committed numerical data and hashes are preserved.

**Interpretation:** G5 provisional; G8 physical repeated-unfolding validation not demonstrated; G11 one known-target comparison; G12 accepted two-dimensional source model not established; G15 calibrated generator p-value **NO-GO**. See [status](../docs/RESEARCH_STATUS.md) and [issues](../docs/ISSUE_REGISTER.md).
