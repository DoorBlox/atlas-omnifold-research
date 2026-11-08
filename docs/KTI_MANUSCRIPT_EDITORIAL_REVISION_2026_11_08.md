# Manuscript editorial revision checkpoint — 8 November 2026

**Status:** A substantial revised **standalone Word draft** was created from the existing manuscript after critical reading of the author's uploaded AI-writing screening report and scientific source record. **Not a journal-ready paper, new ATLAS result, or recalibrated uncertainty analysis.** The Word/PDF files were delivered through the conversation environment and **were not uploaded to this public GitHub repository**.

## Artifacts and source identity

- Input Word: `Manuscript_Draft(1).docx`, SHA-256 `c2b64c4e9eb19f9da9f9fdcd431b3255cf99be55256299c40dfbc32ac56e457d` (same manuscript recorded in [previous checkpoint](KTI_MANUSCRIPT_DRAFT_CHECKPOINT_2026_11_08.md)).
- Revised Word: `Manuscript_Revised_Scientific_Editorial.docx`, SHA-256 `5f972d10df7a4a683bf700a585ccf843d74467450c4c43af5746d2b3a1c5678e`.
- QA-rendered PDF preview: `Manuscript_Revised_Scientific_Editorial.pdf`, SHA-256 `135e0ccb9925f14703b4470dc6204ad0d8fbf7b56830d0009b3724dd9016ed70`.
- **12 pages** in the final Letter-sized layout; **192-word abstract**, three original numeric tables, four original images and **14 unchanged reference entries**.
- The revision edited **64 prose, heading and caption paragraphs**. Figure 2 was moved after the paragraph interpreting Table 2; Table 2 now begins on its own page and no longer splits across pages. Figures/tables and their numerical values were preserved.
- Image files inside the DOCX are byte-identical to those in the original. Every cell of all three tables was programmatically compared to the original and was unchanged; no source data, numerical model, physics plots, or GitHub analysis code were modified.
- DOCX was rendered and page PNGs inspected. Bounding-box scan found no text overflowing page margins. Accessibility audit: **0 high, 0 medium, 0 low** issues. **This is a document-integrity audit, not a scientific peer-review result.**

## Scientific/editorial changes

- Replaced repetitive generic caution statements with specific analysis of real LL/LH/HL/HH contrasts and why two marginals can conceal the cell pattern. Kept `ΔL = −0.059733`, conditional standard-error ranges and the distinct pseudodata comparator exact.
- Restated source-correlation sensitivity as conditional **model dependence**, and explicitly distinguished the 96.02% real Sherpa *modeled variance share* from a physical attribution.
- Preserved the reported source accounting (29 = 25 systematic-labelled + four stochastic), first-order count-to-shape covariance, shared-event generator mixed finite-MC term, independent truth precision, and the single known-target pseudodata check.
- More clearly separated the legitimate reproducible secondary-analysis contribution from novelty claims already supported by previous jet substructure literature.
- Removed repeated language that gave Results/Discussion an overly formulaic tone. Rewriting was for **clarity, provenance, and author-reviewable scientific prose**, not to promise a lower AI detection score. AI-writing screening scores are not reliable authorship determinations; the human author must review and take responsibility for the complete manuscript and follow institutional disclosure policy.

## Evidence limits — unchanged

- **G5 PROVISIONAL** source-model scope; **G8 UNVERIFIED** repeated-unfolding physical coverage; **G11 one known-target pseudodata check**; **G12 UNVERIFIED** primary validated 2D nuisance correlation; **G15 NO-GO** real-data p-value, significance or generator acceptance/rejection.
- The frozen source of truth remains [results/four-cell-v1](../results/four-cell-v1/README.md) (five CSV files, four figures, 12 checks, SHA-256 manifest), whose last relevant numerical CI run was **42442490666** with **107 passed tests**. **No fresh numerical CI was run in this editorial revision**.
- Bibliography identity was spot-checked against journal/publisher metadata for key ATLAS, Canelli and Desai publications, but final **Zotero-managed, bidirectional, journal-format reference review is still pending**.

## Next actions and safety

1. The **human author and adviser** should review the revised prose for authentic authorship, physics interpretation and accurate citations before reuse; the earlier draft remains available separately.
2. Independently validate whether the method's exact correlation and source-family interpretation is appropriate for a school KTI; obtain qualified statistics/HEP review as feasible.
3. Complete Zotero references and school or venue formatting, author/affiliation/AI/funding/conflict declarations, and an independent final visual proof.
4. **Do not** publish or overwrite the Google Doc ARTICLE tab or place the Word artifact in the public repo without the user's request.
5. Any follow-up session should request/locate the exact Word artifact by SHA. This checkpoint itself does **not** contain the revised full manuscript.

**Current handoff:** [START_HERE_HANDOFF.md](START_HERE_HANDOFF.md) and [scope blueprint](../plans/KTI_DESCRIPTIVE_SCOPE_BLUEPRINT_2026_11_08.md).
