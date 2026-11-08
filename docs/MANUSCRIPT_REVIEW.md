# Manuscript: current review and writing integrity

**Latest draft:** `Manuscript_Four_Cell_Question_Driven_v0.6.docx` (8 November 2026).  
**SHA-256:** `df2e459445bc753da113298512c7962c7e716860b255edf24d8a5a9edc245bdc`.  
**Delivery:** editable Word file in the original conversation; the public GitHub repository retains the supporting numerical evidence and this review record. The school's Google Doc ARTICLE tab remains an earlier working draft.

## What changed in v0.6

The author identified an unhelpful writing pattern in v0.5: each scientific claim was often followed by a defensive 'X, not Y' statement. The 8 November Turnitin report additionally classified **64% of v0.5** as likely AI-written. Those observations prompted a structural rewrite focused on **paragraph purpose**, supported by the installed `academic-humanizer` skill.

- A question map assigns one answerable scientific question to each of **67 edited prose, caption and heading paragraphs**; the underlying structure remains Abstract, Introduction, Methods, Results, Discussion, Conclusion, and References.
- Abstract and Introduction establish the joint-distribution question. Methods define the estimands and covariance assumptions. Results present the cell, marginal and sensitivity numbers. Discussion interprets them and consolidates scientific limits in Section 4.5.
- The editorial audit counted **95 repeated negation markers** across v0.5 body/notes versus **one** in v0.6, while retaining the required scientific limitations.
- The body/prose word count decreased from **4,866** to **4,223** whitespace-delimited words. This excludes the reference list and table cell contents.
- Final render: **11 pages**. Table 1 follows the Results introduction; original figure placements and caption associations were inspected. Accessibility audit: **0 high, 0 medium, 0 low** issues.

### Scientific integrity tests

- **Three original numerical tables:** all cell texts verified identical to v0.5.
- **Four embedded scientific figures:** identical media bytes.
- **14 bibliography paragraphs:** identical.
- **Displayed log-odds equation:** identical.
- **In-text author/year citation identities:** original fingerprint preserved.
- **Numerical outputs and experimental assumptions:** the frozen four-cell comparison and DD/Sherpa conditional estimates retain their reported values. Repeated mentions of numbers were condensed where they added no analysis.
- Data/code availability now uses the canonical [`results/four-cell-v1`](../results/four-cell-v1/README.md) path and `outputs/four-cell-v1` generator output directory, reflecting the [release migration](RELEASE_MIGRATION.md).

The rewrite was reviewed for coherence and visual integrity. Scientific interpretation, journal fit and author declarations still require a human author/adviser decision.

## How to interpret the Turnitin report

The supplied Turnitin PDF for **v0.5** reports **64%** likely AI-generated or AI-revised writing. The previous user-reported score for **v0.4** was 56%. Earlier reports on v0.2 showed 69% AI-writing and 2% text similarity. These percentages refer to different text versions; **v0.6 has no new Turnitin result**. A classifier score is an uncertain screening outcome. Editorial work is evaluated by evidence, precision, paragraph organization and transparent author responsibility, alongside the institution's disclosure policy.

## Scientific boundaries still requiring review

The work remains a descriptive secondary use of the [2024 ATLAS OmniFold release](https://doi.org/10.5281/zenodo.11507450). An accepted physical two-dimensional DD/Sherpa source-correlation prescription, a complete source-label mapping and independent full-unfolding coverage have yet to be verified. Formal generator acceptance/rejection remains outside the present study (**G15 NO-GO**). See [research status](RESEARCH_STATUS.md), [issue register](ISSUE_REGISTER.md), and [joint association audit](JOINT_ASSOCIATION_AUDIT.md).

## Prior working files

| Version | Purpose | Editable file |
| --- | --- | --- |
| v0.5 | Full initial rewrite; source of the supplied 64% Turnitin report | `Manuscript_Four_Cell_Full_Rewrite_v0.5.docx` |
| v0.4 | Earlier evidence-focused editing | `Manuscript_Four_Cell_Review_v0.4.docx` |
| v0.3 | Added D and counterfactual association calculations | `Manuscript_Four_Cell_Review_v0.3.docx` |
| v0.2 | Initial scientific/editorial pass | `Manuscript_Revised_Scientific_Editorial.docx` |
| v0.1 | First full manuscript | `Manuscript_Draft(1).docx` |

The version table documents chronology; each binary document remains a separately supplied conversation artifact. The repo retains the earlier checkpoints and historical handoff for reconstruction.

## Next author actions

Confirm every sentence and technical interpretation, including the exploratory D/log-odds decomposition. Complete Zotero metadata and bidirectional claim/citation checks, affiliation and contributions, funding and conflicts, the required AI-assistance disclosure, and final submission formatting. Adviser/independent scientific review must precede any journal submission.
