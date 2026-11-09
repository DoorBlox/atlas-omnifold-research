# Document register and naming policy

The research accumulated many append-only phase-7 reports during debugging. **This is the canonical index.** Existing detailed filenames have deliberately not been destructively renamed: many are cited from code, old PRs, issue #1, manuscript drafts, and SHA-linked history. The current research status is in [RESEARCH_STATUS.md](RESEARCH_STATUS.md); legacy filenames remain stable, classified references.

## Current working entry points

| Path | Use |
| --- | --- |
| [README.md](../README.md) | 1-page public project overview |
| [../CHATGPT_HANDOFF.md](../CHATGPT_HANDOFF.md) | Active short ChatGPT handoff; former START_HERE is a pointer |
| [CURRENT_STATE.md](CURRENT_STATE.md) | Four-track research, science, writing and submission status |
| [ARTIFACT_REGISTRY.md](ARTIFACT_REGISTRY.md) | SHA-identified author DOCX and private backup/recovery |
| [DOCUMENTATION_PROTOCOL.md](DOCUMENTATION_PROTOCOL.md) | File ownership and update rules |
| [RESEARCH_WORKFLOW.md](RESEARCH_WORKFLOW.md) / [WRITING_WORKFLOW.md](WRITING_WORKFLOW.md) | Research and author-led manuscript checklists |
| [CHATGPT_TOOL_PLAYBOOK.md](CHATGPT_TOOL_PLAYBOOK.md) | Connected services and task-specific skills |
| [DECISIONS.md](DECISIONS.md) / [PROJECT_HISTORY.md](PROJECT_HISTORY.md) | Binding decisions and concise chronological index |
| [RESEARCH_STATUS.md](RESEARCH_STATUS.md) | Current verified scientific and writing state |
| [ISSUE_REGISTER.md](ISSUE_REGISTER.md) | Open issues, resolved-scope decisions, blocked inference |
| [JOINT_ASSOCIATION_AUDIT.md](JOINT_ASSOCIATION_AUDIT.md) | New marginal-vs-association algebra audit |
| [MANUSCRIPT_REVIEW.md](MANUSCRIPT_REVIEW.md) | Current author-selected DOCX identity, source-supported review and remaining scientific issues |
| [../references/README.md](../references/README.md) | 14 DOI Zotero import seeds and pending metadata verification |
| [REPOSITORY_MAP.md](REPOSITORY_MAP.md) | Where data, scripts, tests, reports and workflows live |
| [../plans/RESEARCH_PLAN.md](../plans/RESEARCH_PLAN.md) | Forward roadmap without fictitious deadline |
| [../results/README.md](../results/README.md) | Stable versioned numerical evidence entry |
| [HANDOFF_HISTORY.md](HANDOFF_HISTORY.md) | Unabridged prior append-only handoff, preserved as historical evidence |

## Archived continuity and manuscript-review snapshots

- [START_HERE_PRE_CHATGPT_2026-11-09.md](START_HERE_PRE_CHATGPT_2026-11-09.md) — original short research handoff, unchanged.
- [MANUSCRIPT_REVIEW_V06_HISTORY.md](MANUSCRIPT_REVIEW_V06_HISTORY.md) — complete older v0.6 editorial review, unchanged.
- [RUNBOOK_PHASE7_HISTORY.md](RUNBOOK_PHASE7_HISTORY.md) — original expensive-preflight operations runbook, unchanged.

## Scientific method audit reports (historical but potentially useful)

- [PHASE7_PRIMARY_SOURCE_COVARIANCE_AUDIT.md](PHASE7_PRIMARY_SOURCE_COVARIANCE_AUDIT.md) — official-helper 1D treatment and open 2D transfer.
- [PHASE7_REFERENCE_MC_COVARIANCE_AUDIT.md](PHASE7_REFERENCE_MC_COVARIANCE_AUDIT.md) and [PHASE7_SHARED_MC_BOUNDS_AND_CI_OPTIMIZATION.md](PHASE7_SHARED_MC_BOUNDS_AND_CI_OPTIMIZATION.md) — generator shared-event finite MC cross moments.
- [PHASE7_REPLICA_DENOMINATOR_AUDIT.md](PHASE7_REPLICA_DENOMINATOR_AUDIT.md), [PHASE7_NOTEBOOK_METHOD_RECONCILIATION.md](PHASE7_NOTEBOOK_METHOD_RECONCILIATION.md) — R−1 and source extraction reconciliation.
- [PHASE7_CORRELATION_PROTOCOL_V2.md](PHASE7_CORRELATION_PROTOCOL_V2.md), [PHASE7_SOURCE_ALIGNED_JOINT_AND_CONDITIONAL_TOYS.md](PHASE7_SOURCE_ALIGNED_JOINT_AND_CONDITIONAL_TOYS.md) — correlation hypotheses and toy diagnostics; the Sherpa smoothing implementation lives in [src/phase7_sherpa_2d_smoothing.py](../src/phase7_sherpa_2d_smoothing.py).
- [PHASE7_MODEL_SENSITIVITY_CHECKPOINT.md](PHASE7_MODEL_SENSITIVITY_CHECKPOINT.md), [PHASE7_ASSOCIATION_DECOMPOSITION.md](PHASE7_ASSOCIATION_DECOMPOSITION.md), [PHASE7_REFERENCE_AUDIT_CORRECTED_CALIBRATION.md](PHASE7_REFERENCE_AUDIT_CORRECTED_CALIBRATION.md) — supplementary sensitivity and conditional model discussion.
- [PHASE7_GO_EVIDENCE_REQUIREMENTS.md](PHASE7_GO_EVIDENCE_REQUIREMENTS.md) — historical formal-inference gate checklist. It remains a reference, not the present research objective.
- [PHASE7_GAUSSIAN_CALIBRATION_CHECKPOINT.md](PHASE7_GAUSSIAN_CALIBRATION_CHECKPOINT.md) — **conditional** toy simulation, not physical coverage.
- [DERIVED_SNAPSHOT.md](DERIVED_SNAPSHOT.md), [PHASE7_V2_EXTRACTION_PLAN.md](PHASE7_V2_EXTRACTION_PLAN.md), [PHASE7_ACTUAL_DATA_CHECKPOINT.md](PHASE7_ACTUAL_DATA_CHECKPOINT.md), [RUNBOOK.md](RUNBOOK.md) — data extracts, scripts and reproducibility operations.

## Writing/source checks (preserved history; not current source of truth)

- [KTI_EXECUTIVE_SUMMARY_FACTCHECK_2026_11_08.md](KTI_EXECUTIVE_SUMMARY_FACTCHECK_2026_11_08.md) — errors in external executive-summary PDF.
- [KTI_BIBLIOGRAPHY_AND_NOVELTY_AUDIT_2026_11_08.md](KTI_BIBLIOGRAPHY_AND_NOVELTY_AUDIT_2026_11_08.md) — bounded DOI and originality audit.
- [PHASE7_DEEP_RESEARCH_ADJUDICATION_2026_11_08.md](PHASE7_DEEP_RESEARCH_ADJUDICATION_2026_11_08.md) and [PHASE7_DEEP_RESEARCH_REPORT_10_FACTCHECK.md](PHASE7_DEEP_RESEARCH_REPORT_10_FACTCHECK.md) — reject unsupported example results and misidentified sources.
- [KTI_MANUSCRIPT_DRAFT_CHECKPOINT_2026_11_08.md](KTI_MANUSCRIPT_DRAFT_CHECKPOINT_2026_11_08.md) and [KTI_MANUSCRIPT_EDITORIAL_REVISION_2026_11_08.md](KTI_MANUSCRIPT_EDITORIAL_REVISION_2026_11_08.md) — earlier writing checkpoints, **superseded by** [MANUSCRIPT_REVIEW.md](MANUSCRIPT_REVIEW.md) for current status.

## Name policy from now on

- **Current living documents:** short semantic names in upper snake case, without dates: `RESEARCH_STATUS.md`, `ISSUE_REGISTER.md`, `RESEARCH_PLAN.md`.
- **Versioned evidence:** the canonical release is `results/four-cell-v1/`, protected by an updated SHA-256 manifest and reproduction tests. The former path and its commit remain in Git history, with [migration details](RELEASE_MIGRATION.md).
- **Historical reports:** retain original dated or `PHASE7_` names for provenance, index them here, and do not promote them as current working instructions.
- **Git commits:** one coherent change per commit, e.g. `docs(research): consolidate current state and legacy handoff`, `docs(science): audit joint association parameterization`, `fix(repro): verify frozen release manifest`. Do not rewrite old public commit messages or force-push shared history to change their prose.
- **New numerical releases:** `results/four-cell-v2/` only after changed inputs, equations, model, or figure source need a truly new release; explain the delta, produce new hashes and tests. Do not create a v2 merely because a school date has passed.
