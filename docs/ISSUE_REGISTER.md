# Scientific and editorial issue register

**Snapshot:** 8 November 2026. This file distinguishes **a problem resolved for a descriptive KTI** from **scientific validation still impossible with the frozen public inputs**. A work unit marked *done* is not permission to inflate a claim.

| ID | Concern | Disposition | Evidence and next action |
| --- | --- | --- | --- |
| SCI-01 | Historical four-variable C2ST generator compatibility ambition lacks full joint 2D null | **SCOPE RESOLVED**: no inferential claim in the present KTI; the earlier classifier project is archived | [status](RESEARCH_STATUS.md), [historic source audit](PHASE7_GO_EVIDENCE_REQUIREMENTS.md) |
| SCI-02 | Correct provenance and distinct comparison supports | **COMPUTATION VERIFIED**: real vs shared generator uses paired finite MC; pseudo vs independent truth includes independent target precision | [source code](../src/phase7_joint_reference.py), [fixed evidence](../results/README.md) |
| SCI-03 | Normalized four-cell covariance algebra | **NUMERICALLY VERIFIED**, not physical model validation: 4×4 rank three, sum-to-one null mode, R−1 and NN mean /R conventions | [tests](../tests/test_phase7_kti_bundle.py), [source audit](PHASE7_PRIMARY_SOURCE_COVARIANCE_AUDIT.md) |
| SCI-04 | DD/Sherpa 2D source-correlation prescription | **OPEN FOR FORMAL INFERENCE**: four predeclared *sensitivity* models suffice for the descriptive paper only | [protocol](PHASE7_CORRELATION_PROTOCOL_V2.md), [GO requirements](PHASE7_GO_EVIDENCE_REQUIREMENTS.md) |
| SCI-05 | Physical frequentist coverage and generator p-value | **BLOCKED**: a single pseudodata target and model-conditional toys cannot establish repeated-unfolding calibration | [requirements](PHASE7_GO_EVIDENCE_REQUIREMENTS.md). G8/G15 not passed |
| SCI-06 | Manuscript assumes a log-odds difference means strong standalone association shift | **SOURCE-COMPUTED AND DOCUMENTED**: D/path counterfactual added to v0.3 and automated in `src/joint_association_audit.py`; independent scientific review remains pending | [exact supplementary algebra](JOINT_ASSOCIATION_AUDIT.md) |
| SCI-07 | Novelty for a specialist HEP journal | **NOT ESTABLISHED**; limited, defensible novelty is reproducible, transparent reuse and sensitivity case study | [bibliography and novelty audit](KTI_BIBLIOGRAPHY_AND_NOVELTY_AUDIT_2026_11_08.md) |
| ED-01 | Citation/reference consistency | **PENDING**: bibliography DOI checks were partial; Zotero library and every in-text/reference bidirectional match still require audit | [manuscript review](MANUSCRIPT_REVIEW.md) |
| ED-02 | Complete school/journal template, author identity and AI disclosure | **PENDING HUMAN SIGNOFF**; school/adviser/venue policies have not been confirmed | [writing/integrity review](MANUSCRIPT_REVIEW.md) |
| ED-03 | Language repetitive / academic voice | **PARTIALLY ADDRESSED**: 64 passages edited; separate Turnitin score unchanged 69%, not an objective proxy for authorship | [manuscript review](MANUSCRIPT_REVIEW.md) |
| OPS-01 | `kti-nov18` misleading future-looking folder | **DOCUMENTATION RESOLVED**: a target *milestone label* assigned to a completed 8-Nov evidence bundle; stable `results/README.md` entry | [stable evidence index](../results/README.md) |
| OPS-02 | Append-only 60-kB handoff and duplicate blueprints | **DOCUMENTATION RESOLVED**: short handoff, status, issues and roadmap as current docs; original preserved for audit | [history](HANDOFF_HISTORY.md), [document map](REPORT_REGISTER.md), [roadmap](../plans/RESEARCH_PLAN.md) |

### Epistemic rule

Do **not** close SCI-04 or SCI-05 by choosing the most favorable of four models, setting a broad uncertainty range, assuming independent pseudo trials from bootstrap replicas, or extrapolating a 1D ATLAS helper to an official 2D covariance. The available evidence does not permit this. A valid descriptive paper can still be completed with explicit limitation statements.

For any issue reopened or resolved later, record the **exact source file, change in claim, test result and reviewer approval**, and update [RESEARCH_STATUS.md](RESEARCH_STATUS.md). Never backfill a scientific “PASS” from a software build badge.
