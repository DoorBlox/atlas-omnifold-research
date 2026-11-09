# Repository map and data provenance

The codebase retains historical `phase7_` module names for compatibility; the present research is a fixed 2×2 descriptive projection, **not an inferential 'Phase 7 PASS'**.

| Area | Current function | Change policy |
| --- | --- | --- |
| [data/derived/phase7-v1](../data/derived/phase7-v1) | Frozen early real/pseudo cells and covariance source snapshots | Pinned evidence: don't silently change |
| [data/derived/phase7-v2](../data/derived/phase7-v2) | Signed and mixed weight moments from verified earlier extraction | Pinned evidence: don't silently change |
| [src/phase7_kti_bundle.py](../src/phase7_kti_bundle.py) | Deterministic CSV/SVG bundle generator | Changes must have tests, updated manifest, and actual CI evidence |
| [src/joint_association_audit.py](../src/joint_association_audit.py) | Additional algebraic description D and path-sensitive log-odds decomposition | Non-inferential; numerical test only |
| [tests/test_joint_association_audit.py](../tests/test_joint_association_audit.py) | Reproducibility expectations for the additional D and log-odds arithmetic | Does not validate experimental coverage |
| [src/phase7_joint_reference.py](../src/phase7_joint_reference.py) | Paired real reference covariance and four source model scenarios | Mathematical model prototype, **not official ATLAS 2D recipe** |
| [src/phase7_source_accounting.py](../src/phase7_source_accounting.py) | 29 archived component inventory | Source names are project-side labels, not a proven exact paper mapping |
| [tests/test_phase7_kti_bundle.py](../tests/test_phase7_kti_bundle.py) | Frozen numeric expectations and model invariants | Existing tests are numerical checks |
| [results/README.md](../results/README.md) | Stable result index | Stable pointer to the pinned scientific release |
| [results/four-cell-v1](../results/four-cell-v1) | Version-one four-cell numerical evidence | CSV/SVG contents retained, new release labels and manifest hashes verified |
| [.github/workflows/atlas-phase7-lite.yml](../.github/workflows/atlas-phase7-lite.yml) | No-download derived regression workflow | Uses current four-cell-v1 output path and frozen v1/v2 inputs |
| [.github/workflows/atlas-phase7.yml](../.github/workflows/atlas-phase7.yml) | Expensive full original-event workflow | Avoid without an explicit reason requiring new event moments |
| [../CHATGPT_HANDOFF.md](../CHATGPT_HANDOFF.md) | One active ChatGPT continuation checkpoint | Replace after verified task, archive details |
| [ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md) | Identity, custody and recovery for current author DOCX | Private bytes remain outside GitHub |
| [docs/REPORT_REGISTER.md](REPORT_REGISTER.md) | Classifies 20+ historical method and manuscript reports | New issues belong in short current register |
| [plans/RESEARCH_PLAN.md](../plans/RESEARCH_PLAN.md) | Current forward research plan | Keep binding scope and editorial tasks here |

**Reproducibility sequence:** 2024 ATLAS published event-weight release → frozen v1/v2 signed moments and provenance → deterministic four-cell aggregation → permanent five tables and four SVG figures → manuscript tables/figures. Real unfolded vs generator share simulation support; pseudodata known-target truth is independent. Source code and CI test these computations; they do **not** verify that a chosen 2D nuisance model describes physical repeated experiments.

**Source precedence** when two manuscripts or external reports disagree: (1) immutable four-cell CSVs and SHA-256 manifest; (2) checked generator code + source snapshots; (3) previous numerical CI logs; (4) generated Methods/Results; (5) editable Word/Google Doc; (6) external Deep Research/example reports. A PDF report from Turnitin is evidence about that document's text matching/classification, **not physics evidence**.

Repository history is public and should not be rewritten just to improve names. Historical documents are readable via the [report register](REPORT_REGISTER.md).
