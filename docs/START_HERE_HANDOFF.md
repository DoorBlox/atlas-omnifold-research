# START HERE: four-cell OmniFold KTI

**Current checkpoint: 8 November 2026.** This is the short continuation brief. The previous long discussion and development history remain in [HANDOFF_HISTORY.md](HANDOFF_HISTORY.md).

## Study

Working title: *A Reproducible Four-Cell Analysis of Leading Charged-Jet Mass and Track Multiplicity in ATLAS 2024 OmniFold Z+Jets Data*.

This is an independent descriptive secondary analysis of the [ATLAS 2024 PRL](https://doi.org/10.1103/PhysRevLett.133.261803) using [Zenodo 2024 HDF5 event weights](https://doi.org/10.5281/zenodo.11507450).

- Selection: `pT_trackj1 > 5 GeV`, mass boundary `10.594606399536133 GeV`, leading-jet charged-constituent multiplicity boundary `11`.
- Cell order: LL, LH, HL, HH (mass first).
- Real comparator: shared-event nominal generator. Pseudodata comparator: independent known-target truth.
- Real unfolded-minus-generator: `Δmass-low = +0.0036800854`, `Δmultiplicity-low = −0.0146902523`, `Δlog odds = −0.0597334776`, `ΔD = −0.0001685161`.
- Pseudodata unfolded-minus-target: `−0.0229756608`, `−0.0019636003`, `+0.0522361448`, `+0.0014603768`, respectively.

The canonical numerical release is [`results/four-cell-v1/`](../results/four-cell-v1/README.md): five CSV tables, four scientific SVG figures, reproducibility and SHA-256 checks. Its former date-based folder name was retired; [release migration record](RELEASE_MIGRATION.md) documents the preserved inputs and re-hashed reporting files.

## Manuscript

**Latest editable draft:** `Manuscript_Four_Cell_Question_Driven_v0.6.docx`, SHA-256 `df2e459445bc753da113298512c7962c7e716860b255edf24d8a5a9edc245bdc`.

- Rewritten around **one question per paragraph**. An editorial question map covers 67 edited prose, caption and heading paragraphs.
- Removed redundant defensive qualifications: 95 explicit negation markers in v0.5 versus one in v0.6 across manuscript body and notes.
- Three numerical tables, four embedded scientific figures, formal log-odds equation and 14 reference entries are unchanged.
- Page-verified Word artifact, 11 pages; DOCX accessibility audit: zero reported issues.
- The latest uploaded Turnitin AI-writing report gives **64% for v0.5**. The v0.6 draft has **no independent Turnitin result**. Detector outputs do not replace human review or permitted-AI disclosure.

The Word manuscript and question-by-question edit report are conversation artifacts; the binary file is **not stored in this public repository**. The school's Google Doc ARTICLE tab is an earlier working draft.

## Scientific gate status

| Gate | State |
| --- | --- |
| G5 | PROVISIONAL source-family assumptions |
| G8 | UNVERIFIED physical repeated-unfolding coverage |
| G11 | ONE known-target pseudodata comparison executed |
| G12 | UNVERIFIED accepted 2D nuisance-correlation prescription |
| G15 | NO-GO calibrated generator significance or acceptance/rejection |

Four DD/Sherpa scenarios quantify *conditional uncertainty sensitivity*. The reproducible numerical result and the experimental validation problem remain distinct.

## Read next and act

Read [research status](RESEARCH_STATUS.md), [issues](ISSUE_REGISTER.md), [manuscript review](MANUSCRIPT_REVIEW.md), [joint-association audit](JOINT_ASSOCIATION_AUDIT.md), and [current plan](../plans/RESEARCH_PLAN.md). Use the frozen CSVs over editable prose whenever a number disagrees.

**Next task:** obtain author/adviser scientific and editorial sign-off on v0.6, complete Zotero citation and source-to-claim review, verify school/journal requirements and declarations, then prepare the final submission. Any formal inference extension requires independent covariance and repeated-unfolding validation.
