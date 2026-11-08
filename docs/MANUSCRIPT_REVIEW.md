# Manuscript review, writing integrity and submission readiness

**Reviewed 8 November 2026.** The user provided the full revised Word draft and two Turnitin report PDFs. The reports refer to **the revised draft**, not a newly trained physics model. The actual manuscript is an attached conversation file, not a repository file.

## Version identification

- **Original** `Manuscript_Draft(1).docx`: SHA-256 `c2b64c4e9eb19f9da9f9fdcd431b3255cf99be55256299c40dfbc32ac56e457d`, 13-page first draft per earlier document rendering.
- **Previous editorial v0.2** `Manuscript_Revised_Scientific_Editorial.docx`: SHA-256 `5f972d10df7a4a683bf700a585ccf843d74467450c4c43af5746d2b3a1c5678e`, 12 pages.
- **Preceding scientific review v0.3** `Manuscript_Four_Cell_Review_v0.3.docx`: SHA-256 **`53683d2136bc758a69e5384afe430adb7f92330b0393b7d74eb30d84f0b13cfd`**, 13-page reviewed render. It adds the D association-coordinate and path-dependent counterfactual analysis; all three tables, four byte-identical figures, and fourteen bibliography entries are unchanged. DOCX render and accessibility audit completed (0 high/medium/low issues). Files live in the conversation, not GitHub.
- **Important distinction:** The uploaded PDF `Manuscript_Revised_Scientific_Editorial.pdf` and `Manuscript_Revised_Scientific_Editorial.docx.pdf` are **not the same file** (different hashes and purposes; the second is a Turnitin similarity-report wrapper). Do not use a previous checkpoint's PDF hash to identify an edited DOCX. The **DOCX hash** is the correct identity of the editable manuscript.
- **Google Doc ARTICLE** at [school document](https://docs.google.com/document/d/1rTafCdT6ESCpH43HtrssArHpiUzVEhoYABzwQJewQ00/edit) is **older working text**, not the final Word version. Do not overwrite without author direction.

## Turnitin reports: observed results, not a revision goal

- **AI-writing report:** `69%` marked as likely AI-generated/AI-revised text in the revised manuscript (same score as the earlier 13-page first-draft report).
- **Similarity report:** **`2%` overall similarity**, bibliographic text excluded. A low similarity percentage says little about authorship or novelty.
- The report itself and [Turnitin's guidance](https://guides.turnitin.com/hc/en-us/articles/22774058814093-Using-the-AI-Writing-Report) caution that AI classification can misidentify human/AI writing and **must not be the sole basis of misconduct decisions**.
- The project has openly used AI to research and draft scientific prose. **Do not present AI assistance as absent, claim a detector pass, or optimize prose merely to manipulate a score.** The author must inspect every technical claim and apply the institution's disclosure policy.

## Assessment of the scientific narrative

**Strengths:** all reported central four-cell fractions and three-scalar contrasts were traced to the immutable CSVs; the paper distinguishes real-generator from independent pseudodata truth; 29 source families, count-to-shape normalization and four DD/Sherpa sensitivity models are stated; numerical caveats prevent unsupported p-values.

**Scientific correction now required:** The original Discussion treats `ΔL=-0.059733` as the third association coordinate. This is a valid parameterization, **but** the separate binary-indicator covariance `D=p_LL-MN` changes by only `-0.0001685161` in the real comparison. A specified counterfactual path attributes `-0.0553563718` of the log-odds difference to adjusted marginals with reference `D` held fixed; the remainder is `-0.0043771058`. That does not establish significance or a mechanism. See [joint association audit](JOINT_ASSOCIATION_AUDIT.md). The new v0.3 Word draft includes this as an explicitly exploratory descriptive supplementary result; human author/adviser validation remains pending.

**What remains genuinely unresolved:** source covariance for full physical experimental inference, independent repeated-unfolding validation, rigorous novelty for specialist physics journals, and final school/venue policy fit. The first two cannot be solved just by rewriting, changing filenames or selecting a preferred model; see [issue register](ISSUE_REGISTER.md).

## Editing standards for the next manuscript revision

Follow the user's requested [academic-humanizer skill](https://github.com/AIScientists-Dev/academic-humanizer): precise, restrained academic wording; explicit evidence next to claims; eliminate generic hype, repetitive limitations, vague connectives and excess clause stacking. Preserve formal statistical terms and all equations, numerical values, citation identities and genuine scientific hedging. Prefer original reasoning about a particular result over generic discussion.

**A scholarly voice is not an AI-detector score.** Any edits should be justified by clarity, factual traceability and author control, with a transparent edit history. Retain author/adviser review and AI-use disclosure as required.

## Submission checklist

- [x] Working full Word draft exists (not in GitHub).
- [x] Three numerical tables and four figures in the revised DOCX preserved during the earlier editorial pass.
- [x] Separate numerical source and pseudodata comparator distinctions recorded.
- [x] Added D and path-dependent counterfactual to v0.3 and checked arithmetic against frozen fractions.
- [ ] Author/adviser approve additional D association decomposition and interpretation.
- [ ] Independently review scientific uncertainty methods with qualified HEP/statistics adviser.
- [x] Extracted 14 unique manuscript DOIs into [reference import seeds](../references/README.md).
- [ ] Import/verify references with Zotero, bidirectional in-text/reference checks, correct venue style.
- [ ] Verify all figure/table captions, labels, pages, unit symbols and attribution in final PDF.
- [ ] Confirm school deadline, manuscript language, permitted AI assistance, author contributions, funding/conflicts, license.
- [ ] Human author and adviser approve and sign off on actual final submission.

**No journal acceptance, novelty-first claim, calibrated generator verdict or improved detection score is claimed.**

## Latest manuscript: evidence-preserving academic editing (v0.4)

**`Manuscript_Four_Cell_Review_v0.4.docx`** (SHA-256 `6b29850f47da86417de50d1ea872f13e6066a6618ca7974e4bccaa3a6fab79f6`), 12 pages after removal of an unnecessary forced break before Table 2. Thirteen passages were rewritten under the `academic-humanizer` skill's academic criteria: specific claims backed by tables/figures, shorter sentences, less repeated caveat language, no em-dash sentence constructions and no unsupported novelty. Per-paragraph automated checks found all numeric tokens and author–year citations preserved; all 3 table matrices, 4 embedded images and 14 bibliography paragraphs are unchanged from v0.3. The final DOCX was rendered to 12 page images and visually reviewed; the accessibility audit recorded 0 high/medium/low issues. All 14 bibliography works have in-text author–year mentions. This is not a final claim-to-source audit or Zotero-generated bibliography.

The **Turnitin 69% AI-writing** and **2% similarity** results refer to **v0.2**, not the new v0.4. No new detector result or reduced score is claimed. Author/adviser review and any required AI-use disclosure remain outstanding.
