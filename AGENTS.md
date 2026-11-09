# ATLAS research: instructions for ChatGPT and contributors

**Start:** [CHATGPT_HANDOFF.md](CHATGPT_HANDOFF.md) → [current state](docs/CURRENT_STATE.md) → [research plan](plans/RESEARCH_PLAN.md) → [artifact registry](docs/ARTIFACT_REGISTRY.md). Verify live GitHub branch, PRs and checked evidence before editing. Historical reports are useful evidence, not current instructions.

## Locked science

- The study is a **descriptive secondary analysis** of [ATLAS 2024 OmniFold Z+jets](https://doi.org/10.1103/PhysRevLett.133.261803) and the distinct [2024 Zenodo event-weight release](https://doi.org/10.5281/zenodo.11507450).
- Leading charged jet `pT_trackj1 > 5 GeV`; mass threshold `10.594606399536133 GeV`, charged-constituent multiplicity threshold `11`; cell order **LL, LH, HL, HH** (mass first).
- Real unfolded data compare with the **shared-event nominal generator**; unfolded pseudodata compare with **independent known-target truth**.
- The authoritative results are [five CSVs, four figures and SHA-256 checksums](results/four-cell-v1/README.md) from frozen source moments. Never silently edit the release, data/derived inputs, selection or test claims.
- Scientific gate states: **G5 PROVISIONAL; G8 UNVERIFIED; G11 one known-target case; G12 UNVERIFIED; G15 NO-GO** calibrated significance/compatibility. A passing software test does not change scientific inference.

## Operating loop

1. Recover current state from handoff, the live repo, relevant code/docs and the *actual* author-approved DOCX identified by hash.
2. Pick one READY work unit, describe expected output, evidence and acceptance criteria; carry out routine scoped source/docs work without making the owner supervise GitHub.
3. Use focused branches/PRs, review the changes, run targeted tests and exact-head CI once where sufficient, and report actual PASS/FAIL/NOT RUN.
4. Update the single short [handoff](CHATGPT_HANDOFF.md) and [current state](docs/CURRENT_STATE.md) after completing the task, with an explicit next file-level action. Put detailed history in its named archive.

## Authorship and safeguards

The author's **self-rewritten, science-checked, Word-equation-formatted manuscript** is the current selected draft. Its filename/hash and location are in [ARTIFACT_REGISTRY](docs/ARTIFACT_REGISTRY.md). The older assistant v0.6 and Google Doc ARTICLE tab are historical drafts. Preserve the author's voice and **one question per paragraph**; use [WRITING_WORKFLOW](docs/WRITING_WORKFLOW.md) and [RESEARCH_WORKFLOW](docs/RESEARCH_WORKFLOW.md). Do not chase an AI-detector score or invent sources, physics, DOI records, permissions, reviewer decisions or publication results.

No public manuscript upload, manuscript submission, scientific claim expansion, destructive operation or human sign-off is authorized by routine documentation maintenance. The assistant cannot work between chats without an explicit automation. [Documentation protocol](docs/DOCUMENTATION_PROTOCOL.md) governs preservation and precedence.
