# Author-led scientific writing and editorial workflow

**Active 9 November 2026.** This procedure preserves the student's own voice, research evidence and the recovery path for future ChatGPT sessions.

## 0. Select the actual source file

Find [ARTIFACT_REGISTRY](ARTIFACT_REGISTRY.md) and verify the approved input DOCX SHA. Current: `ATLAS_Four_Cell_Science_Checked_Formatted_Equations.docx`, SHA-256 `e4d3e49b19e0c683bff7340769d4c646f2c1b13791551a941308aeb0182f8e62`. It follows the **author's own rewriting** and focused scientific/Word-equation corrections. **v0.6 and the Google Doc ARTICLE tab are earlier drafts.**

If the exact Word bytes are missing, request the author-owned copy. Never reconstruct a newer version from an older document, a summary, or a hash.

## 1. One paragraph answers one question

For any requested edit, map each affected paragraph to **the question it answers, evidence or method supporting it, and why it is in that section**. The Introduction establishes the scientific gap; Methods define data and estimands; Results report observed numbers; Discussion interprets patterns and alternatives; Limitations collect consequential unresolved boundaries. Avoid repetitive generic transitions and repeated “X, not Y” caveats after every finding. Preserve the author’s idiom, including when it is simpler than conventional generated prose.

The user approves major rewriting; default to precise, local edits. The installed academic-humanizer guidance concerns evidence and scholarly voice, **not evading Turnitin or targeting a detector score**.

## 2. Claim-to-evidence audit

For every empirical sentence, record `section / paragraph → claim → exact CSV, script, paper or DOI → numeric/terminology check → outcome`. Confirm **four cells vs marginals**, real vs pseudodata comparator, percentage points vs fractions, conditional SE, and citation identity. [Four-cell tables](../results/four-cell-v1/tables/joint_cells.csv), [marginal/association table](../results/four-cell-v1/tables/marginal_association.csv), [scenario table](../results/four-cell-v1/tables/scenario_sensitivity.csv), [source-variance table](../results/four-cell-v1/tables/source_variance.csv) are the preferred numeric sources.

Preserve three numerical Word tables, four scientific figures, captions and editable equations. Format subscripts/superscripts as real Word typography rather than raw underscores. Compare the original and revised tables/captions/embedded media, and note every deliberate scientific change.

## 3. References and declarations

The [14 DOI seeds](../references/README.md) are **import candidates**, not a verified Zotero bibliography. Check publisher metadata and the exact sentence each reference supports; reconcile in-text citations to reference list **both directions**, then apply school/journal style. Keep the ATLAS 2024 paper and Zenodo dataset citations distinct. Do not invent a verified source or claim that Zotero was run if it was not.

Author, affiliation, funding, contributions, conflicts, licensing/permissions and AI assistance declarations depend on author/adviser/institutional rules. Record those as `PENDING HUMAN DECISION` until resolved.

## 4. Review, render, deliver

Before calling a version ready:
- Check scientific claims against [CURRENT_STATE](CURRENT_STATE.md), [ISSUE_REGISTER](ISSUE_REGISTER.md) and the G5/G8/G11/G12/G15 gates. A major-revision reviewer decision for an old version does not automatically pass on a new version.
- Identify parent/new filename and SHA-256. Produce a section-level edit ledger with what changed and why, plus actual `PASS / FAIL / NOT RUN` checks.
- Render all DOCX pages. Inspect equations, tables, image positions, captions, bibliography and page breaks. State actual results.
- Keep the original approved DOCX; deliver the new file separately and store it privately. Update [ARTIFACT_REGISTRY](ARTIFACT_REGISTRY.md), [CURRENT_STATE](CURRENT_STATE.md) and [CHATGPT_HANDOFF](../CHATGPT_HANDOFF.md) after the author accepts the version.

**Completion:** author-approved text, claim-supported results, complete citations/declarations, render-verified manuscript and adviser/venue requirements satisfied. A publication decision is independent of the GitHub numerical CI.
