# START HERE: ATLAS four-cell KTI

**Latest verified research snapshot: 8 November 2026.** This is an actively maintained, short handoff, not a running transcript. The former **60-kB** handoff (including outdated instructions and old run IDs) is preserved in [HANDOFF_HISTORY.md](HANDOFF_HISTORY.md).

## Fast start (read in order)

1. [Research status and gate register](RESEARCH_STATUS.md)
2. [Immutable numerical evidence entry point](../results/README.md)
3. [Current research and editorial issue register](ISSUE_REGISTER.md)
4. [New joint-association arithmetic audit](JOINT_ASSOCIATION_AUDIT.md)
5. [Current research plan](../plans/RESEARCH_PLAN.md)
6. [Manuscript and AI/similarity report review](MANUSCRIPT_REVIEW.md)
7. [Repository map](REPOSITORY_MAP.md) and [full document register](REPORT_REGISTER.md)

The selected 2024 ATLAS dataset is **Zenodo 11507450 (HDF5)**, **not** a distinct 2026 CERN dataset. Original ATLAS PRL DOI 10.1103/PhysRevLett.133.261803. Selected charged leading jet `pT_trackj1 > 5 GeV`, mass threshold `10.594606399536133 GeV`, leading-jet charged multiplicity threshold 11. Four cells LL/LH/HL/HH, mass first.

Frozen results were **completed 8 November**, though output folder `results/kti-nov18` references a November 18 target milestone. Existing source CI [42442490666](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42442490666) passed 107 tests; this should not be represented as new CI activity after the docs reorganization.

Real `Δmass-low = +0.0036800854`, `Δmultiplicity-low = -0.0146902523`, `Δlog-odds = -0.0597334776`. The separate pseudodata known-target comparator yields `-0.0229756608`, `-0.0019636003`, `+0.0522361448`. **New secondary algebra:** binary-indicator association covariance `D` changes `-0.0001685161` real and `+0.0014603768` pseudo; this modifies *interpretation*, not pinned results. Details and a reproducible standalone snippet in the [association audit](JOINT_ASSOCIATION_AUDIT.md).

The **preceding** Word manuscript is `Manuscript_Four_Cell_Review_v0.3.docx`, SHA-256 **`53683d2136bc758a69e5384afe430adb7f92330b0393b7d74eb30d84f0b13cfd`** (13-page render, 3 unchanged numerical tables, 4 unchanged figures, new D and explicitly path-dependent log-odds recheck). **Current v0.4**: `Manuscript_Four_Cell_Review_v0.4.docx`, SHA-256 **`6b29850f47da86417de50d1ea872f13e6066a6618ca7974e4bccaa3a6fab79f6`**, rendered and visually inspected at **12 pages**, retaining the 3 original numerical tables, 4 byte-identical figures and 14 bibliography entries. Thirteen paragraphs were revised following the academic-humanizer guidance without modifying numbers or citations in edited paragraphs. The 69% AI-writing and 2% similarity reports refer to **v0.2**, not v0.4. The prior v0.2 is `Manuscript_Revised_Scientific_Editorial.docx`, SHA-256 `5f972d10df7a4a683bf700a585ccf843d74467450c4c43af5746d2b3a1c5678e`. **The DOCX is not in public GitHub and Google Doc ARTICLE is older text.** The revised Turnitin report states 69% AI-writing likelihood and 2% text similarity; neither number proves authorship or scientific validity. See [manuscript review](MANUSCRIPT_REVIEW.md).

**G5 provisional, G8/G12 unverified, G11 one check, G15 NO-GO.** Never claim real-data calibrated significance, a model-validated experimental interval, ATLAS 2D approval, generator acceptance/rejection, or future journal acceptance. A descriptive KTI with transparent limitations is the currently adopted scope; specialist-journal originality is unconfirmed.

**Next action:** review and approve v0.3's inserted D and counterfactual interpretation, obtain adviser decision on acceptable descriptive KTI scope, then finish citation verification, declarations and final review. Do not start new multi-GB extraction merely to edit the document. Do not overwrite Google Doc ARTICLE or upload binary manuscripts to public GitHub without an explicit request.

**Reusable continuation prompt:** Continue the descriptive 2024 ATLAS OmniFold KTI in `DoorBlox/atlas-omnifold-research`. Read `docs/START_HERE_HANDOFF.md`, `docs/RESEARCH_STATUS.md`, `docs/JOINT_ASSOCIATION_AUDIT.md`, `docs/ISSUE_REGISTER.md`, and `results/README.md`. Inspect current main and the latest CI independently. The Word draft is a conversation attachment, not in GitHub. Prioritize scientific manuscript review and the newly discovered distinction between `ΔL` and binary-indicator `ΔD`; no calibrated p-values. Preserve frozen data and scientific limitations.
