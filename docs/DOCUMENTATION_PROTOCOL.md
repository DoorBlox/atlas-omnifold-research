# ATLAS research — documentation and handoff protocol

**Adopted 9 November 2026.** Adapted from [ORBIT's documentation protocol](https://github.com/DoorBlox/orbit/blob/main/docs/DOCUMENTATION_PROTOCOL.md). This protocol prevents lost context, contradictory manuscript versions and inflated scientific claims.

## One owner for each kind of information

| Question | Authoritative location |
| --- | --- |
| What does the current session need to do? | [root CHATGPT_HANDOFF](../CHATGPT_HANDOFF.md), *replace in place* |
| What has actually been verified? | [CURRENT_STATE](CURRENT_STATE.md), live GitHub SHA/PR/CI and [frozen numerical evidence](../results/four-cell-v1/README.md) |
| What work is ready, blocked or requires consent? | [RESEARCH_PLAN](../plans/RESEARCH_PLAN.md) and [ISSUE_REGISTER](ISSUE_REGISTER.md) |
| What scientific design and method is accepted? | [DECISIONS](DECISIONS.md), [RESEARCH_WORKFLOW](RESEARCH_WORKFLOW.md) |
| Which author DOCX is current? | [ARTIFACT_REGISTRY](ARTIFACT_REGISTRY.md), checked SHA and [WRITING_WORKFLOW](WRITING_WORKFLOW.md) |
| How are calculations reproduced? | [RUNBOOK](RUNBOOK.md), scripts/tests and frozen results |
| What happened earlier? | [PROJECT_HISTORY](PROJECT_HISTORY.md), [REPORT_REGISTER](REPORT_REGISTER.md), [HANDOFF_HISTORY](HANDOFF_HISTORY.md) |

The original 3.7-kB handoff is retained as [historical text](START_HERE_PRE_CHATGPT_2026-11-09.md). The prior append-only source is untouched. Scientific source precedence: frozen source weights/moments and hashes → verified code/CI → generated results → editable manuscript and external reports. **For authorial wording**, the current SHA-identified author DOCX takes precedence over older prose.

## Update contract

| Event | Update | Avoid |
| --- | --- | --- |
| Start a chat | Read root handoff/state/AGENTS/plan/manifest; verify live GitHub main/PR and author manuscript hash | Assume prior conversation state remains live |
| Change analysis | Record hypothesis, comparisons, input checksums, mathematical method, expected figures/tables and scientific gates | Overwrite `results/four-cell-v1` or call untested covariance “validated” |
| Edit Word | Record parent SHA, new SHA, changed sections, tables/figures/equations/citation integrity and render outcome | Substitute assistant-written v0.6 for the author's selected text |
| Check bibliography | Match DOI metadata, actual cited claim and both directions of in-text/reference links | Equate 14 DOI seeds with completed Zotero verification |
| Run CI | Capture exact PR head SHA, job/check name, count, failures and what was **NOT RUN** | Extrapolate numerical tests to experimental coverage |
| Finish a task | Update CURRENT_STATE/plan/issues as needed, replace the root handoff once, preserve detailed evidence in named reports | Append another multi-page checkpoint to five files |
| Adviser / submission decision | Record human decision, dated guideline, version identity and consequences | Invent approval, journal indexing, funding or AI disclosure |

## Status language

- Software/numbers: `IMPLEMENTED`, `REPRODUCED`, `VERIFIED` (only against declared tests).
- Scientific inference: `PROVISIONAL`, `UNVERIFIED`, `VALIDATED`; **G15 remains NO-GO** until justified 2D covariance and physical null/coverage are established.
- Manuscript: `AUTHOR DRAFT`, `EDITORIAL CHECKED`, `ADVISER REVIEWED`, `SUBMITTED`; version/hash-specific.
- Work items: `READY`, `IN PROGRESS`, `BLOCKED`, `DONE`, `DEFERRED`.

## Execution and permission boundaries

Routine source/docs/testing work may proceed in focused GitHub PRs. Use one bounded task and one inspectable diff. For docs-only work run the [lightweight validator](../scripts/validate_research_docs.py); retain the existing scientific workflow for source/data updates. Do not rerun the original multi-gigabyte event extraction merely to update prose.

Publishing an author DOCX to public GitHub, submitting to a journal, modifying scientific scope, approving declarations, changing private files or claiming validated inference require separate author/adviser decisions. A file hash is **identity evidence, not a recoverable backup**. Keep the author's private ZIP in a durable user-controlled location. No invisible background work or persistent shell state is assumed.

**Handoff template:** objective and authorization; frozen decisions; branch/PR/tested SHA and actual PASS/FAIL/NOT RUN; selected manuscript filename/hash and storage; unresolved scientific gates; a **single next file-level action**. Keep the handoff concise (prefer under 150 lines) and put history elsewhere.
