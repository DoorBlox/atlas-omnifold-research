# ATLAS — ChatGPT continuation handoff

**Verified checkpoint:** 9 November 2026 (Asia/Jakarta). This is a **short, replace-in-place checkpoint**, inspired by [ORBIT's ChatGPT workflow](https://github.com/DoorBlox/orbit/blob/main/CHATGPT_HANDOFF.md). For previous progress use [history](docs/PROJECT_HISTORY.md) and [historical audits](docs/REPORT_REGISTER.md).

## Project and verified results

Independent four-cell descriptive reanalysis of [ATLAS 2024 OmniFold Z+jets](https://doi.org/10.1103/PhysRevLett.133.261803) using the [2024 event-weight release](https://doi.org/10.5281/zenodo.11507450). Locked mass threshold `10.594606399536133 GeV`, multiplicity threshold `11`, selection `pT_trackj1 > 5 GeV`. Real comparator **shared-event nominal generator**; pseudodata comparator **independent known truth**.

The numerical [`results/four-cell-v1/`](results/four-cell-v1/README.md) release contains 5 CSV tables, 4 SVG figures, hashes and tests. Former date-based naming migrated in [PR #5](https://github.com/DoorBlox/atlas-omnifold-research/pull/5), with **116 passing tests** at that PR's head. Last inspected pre-documentation `main` was `8a81798991e56dcba5da8b7d6c6bd34d67b76331`. **Recheck live SHA, open PRs and required checks**; this SHA is historical after any merge.

## Current human writing artifact

**Author-selected:** `ATLAS_Four_Cell_Science_Checked_Formatted_Equations.docx`  
**SHA-256:** `e4d3e49b19e0c683bff7340769d4c646f2c1b13791551a941308aeb0182f8e62`  
**Status:** self-rewritten by the author, followed by localized science checks and editable Word equation formatting; approximately 12 pages, 3 tables, 4 figures and 14 reference entries. It **supersedes assistant-written v0.6**. Word bytes are a user/conversation file, **not in public GitHub**. An independent review identifies major scientific/editorial matters still awaiting adviser consideration. See [artifact registry](docs/ARTIFACT_REGISTRY.md) and [manuscript review](docs/MANUSCRIPT_REVIEW.md).

Google Docs [RESEARCH PLAN tab](https://docs.google.com/document/d/1rTafCdT6ESCpH43HtrssArHpiUzVEhoYABzwQJewQ00/edit?tab=t.0) was recently updated. Other tabs are older working drafts; no automatic synchronization.

## Unresolved scientific gates

**G5 PROVISIONAL / G8 UNVERIFIED / G11 ONE known-target case / G12 UNVERIFIED / G15 NO-GO.** DD/Sherpa model options produce **conditional** sensitivity summaries; calibrated generator significance and physical repeated-unfolding coverage remain outside the completed analysis.

## Next safe action

**W4: claim-by-claim citation and Zotero audit** of the author-selected manuscript. Start with [DOI seeds](references/README.md), [bibliography audit](docs/KTI_BIBLIOGRAPHY_AND_NOVELTY_AUDIT_2026_11_08.md) and [writing workflow](docs/WRITING_WORKFLOW.md). Deliver a source-to-claim matrix and remaining questions **without overwriting the Word file**. Human-gated: adviser science decision, required school/journal policies, author declarations and submission. See [plan](plans/RESEARCH_PLAN.md) and [issues](docs/ISSUE_REGISTER.md).

## Resume in one pass

Read [AGENTS](AGENTS.md), [CURRENT_STATE](docs/CURRENT_STATE.md), [ARTIFACT_REGISTRY](docs/ARTIFACT_REGISTRY.md), [RESEARCH_PLAN](plans/RESEARCH_PLAN.md); fetch live GitHub; verify actual Word bytes; carry out next bounded action. After verification, replace this checkpoint with exact PR/head/check evidence and a single next task. No invisible work between conversations.
