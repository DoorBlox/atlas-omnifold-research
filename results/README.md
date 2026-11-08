# Frozen four-cell evidence: canonical release v1

The original GitHub folder [`results/kti-nov18/`](kti-nov18/README.md) is an **immutable historical publication artifact**. Its name refers to the **planned November 18, 2026 school milestone**, **not** a release or analysis date. The entire numerical evidence bundle was generated, checked, and committed on **November 8, 2026**, ten days before that milestone. There is no claim about what will happen on November 18.

**This `results/README.md` is the stable, date-independent results entry point.** The pinned artifact is the version-one four-cell descriptive release; retain the original directory name to preserve Git history, internal provenance, and the checksums in `manifest.json`. Do not rename individual manifest-covered files in place, regenerate them merely to change typography, or silently substitute new results.

## Read the evidence

| Evidence | Versioned path | Purpose |
| --- | --- | --- |
| Four-cell fractions | [joint_cells.csv](kti-nov18/tables/joint_cells.csv) | Normalized LL/LH/HL/HH real and pseudo distributions and signed contrasts |
| Marginals and association | [marginal_association.csv](kti-nov18/tables/marginal_association.csv) | Low-mass/low-multiplicity marginals, log odds, conditional standard errors |
| Four correlation assumptions | [scenario_sensitivity.csv](kti-nov18/tables/scenario_sensitivity.csv) | DD/Sherpa full-vs-four-bin sensitivity |
| Source contribution decomposition | [source_variance.csv](kti-nov18/tables/source_variance.csv) | Modeled variance shares, not physical probabilities |
| Normalized covariance elements | [covariance_matrix.csv](kti-nov18/tables/covariance_matrix.csv) | Rank-three, normalization-null four-by-four matrices |
| Figure sources | [figures](kti-nov18/figures/) | Four SVG figures |
| Generated reporting | [MANUSCRIPT_RESULTS.md](kti-nov18/MANUSCRIPT_RESULTS.md) | Generated prose from frozen inputs, not a standalone peer-reviewed manuscript |
| Check and reproducibility evidence | [checks.json](kti-nov18/checks.json), [manifest.json](kti-nov18/manifest.json), [results.json](kti-nov18/results.json) | Twelve true QA checks, hashes, and machine-readable metadata |

The six corresponding model coordinates are described and independently recomputed in [the association audit](../docs/JOINT_ASSOCIATION_AUDIT.md). CI evidence is [run 42442490666](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42442490666) (**107 tests passed in the historical frozen numerical workflow**), not a guarantee of physical model coverage or a new test run after documentation changes.

### Rebuild the historical release

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests/test_phase7_kti_bundle.py
python -m src.phase7_kti_bundle --v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 --out outputs/kti-nov18
```

The `outputs/kti-nov18` CLI convention also reflects the historical deliverable name. It is not the calendar date of execution. **Do not change generator output filenames or manifest-covered paths without a new evidence version and regression tests.** The primary measurements and parent OmniFold release remain ATLAS's work; this is an independent secondary analysis.

**Interpretation:** G5 provisional; G8 physical repeated-unfolding validation not demonstrated; G11 one known-target comparison; G12 accepted two-dimensional source model not established; G15 calibrated generator p-value **NO-GO**. See [status](../docs/RESEARCH_STATUS.md) and [issues](../docs/ISSUE_REGISTER.md).
