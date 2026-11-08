> **Historical detailed scope blueprint (8 Nov 2026).** The currently maintained roadmap is [RESEARCH_PLAN.md](RESEARCH_PLAN.md), the current scientific status is [RESEARCH_STATUS.md](../docs/RESEARCH_STATUS.md), and the version-one numerical evidence is [results/README.md](../results/README.md). This historical blueprint remains intact for audit; status checkboxes below may predate the subsequent Word manuscript revision and joint-association recheck.

# KTI scope-change blueprint — reproducible ATLAS four-cell joint analysis
**Decision date:** 2026-11-08  
**Status:** Adopted project working direction for the *descriptive* KTI; independent scientific/adviser and publication review pending.  
**Canonical public-facing title:** **A Reproducible Four-Cell Analysis of Leading Charged-Jet Mass and Track Multiplicity in ATLAS 2024 OmniFold Z+Jets Data**.  
**Project:** [DoorBlox/atlas-omnifold-research](https://github.com/DoorBlox/atlas-omnifold-research).  
**Living school document:** [79_Muhammad Wahid Hisyam, RESEARCH PLAN / IMRAD / ARTICLE tabs](https://docs.google.com/document/d/1rTafCdT6ESCpH43HtrssArHpiUzVEhoYABzwQJewQ00/edit).
**Manuscript progress update (8 Nov 2026):** Full standalone Word draft achieved (202-word abstract, 3 tables, 4 figures, 14 references); **not yet final or copied to the Google Doc**. Read [the manuscript checkpoint](../docs/KTI_MANUSCRIPT_DRAFT_CHECKPOINT_2026_11_08.md) for file SHA-256, remaining audit, and manuscript-versus-ARTICLE distinction.

## 1. Binding scope decision and change rationale

The former exploratory four-variable, cross-fitted classifier two-sample test (C2ST) is **not the primary study**. The revised study is a quantitative, reproducible **secondary analysis** of released ATLAS 2024 OmniFold Z+jets event weights: a fixed normalized **2×2** joint projection of leading charged-particle jet mass and charged-track multiplicity. It reports real unfolded vs nominal-generator **descriptive differences**, marginal and joint log-odds summaries, source-wise *model-conditional* uncertainty sensitivity, and one independent known-target pseudodata comparison. This is not a new ATLAS measurement, not an official 2D uncertainty prescription, not a generator-validation experiment, and not a calibrated hypothesis test.

**Why change?** The earlier classifier/omnibus goodness-of-fit ambition required a defensible full two-dimensional systematic covariance, joint nuisance-dependence and null-sampling model, and experimental coverage evidence not established by the public released replicas. Claiming a real-data generator p-value would be unjustified. The narrower project can finish reproducibly, answer a precise question, and document the boundary of the evidence without manipulating tests or cherry-picking correlations.

**Research questions (exactly two):**
- **RQ1:** What four-cell joint-shape, mass-low and track-low marginal, and joint log-odds differences are observed between the released unfolded real-data distribution and the shared-event nominal generator, using frozen generator-defined thresholds?
- **RQ2:** How sensitive are *conditional* uncertainty summaries for those differences to four pre-specified DD-unfolding and Sherpa hidden-variable correlation assumptions, and what does the single independent known-target pseudodata comparison check—and fail to establish?

**Objectives:** (O1) Reconstruct and document the frozen four-cell/marginal/association results and provenance; (O2) quantify and transparently delimit conditional uncertainty-source sensitivity and known-target pseudodata comparison. **No significance, physical coverage, causal mechanism, or generator rejection is an objective.**

## 2. Immutable numerical source of truth

- Primary ATLAS publication: [PRL 133, 261803 (2024)](https://doi.org/10.1103/PhysRevLett.133.261803); released data: [Zenodo 11507450](https://doi.org/10.5281/zenodo.11507450); official User Guide Section 2 recommendation 5.
- Frozen v1/v2 moments and provenance: [data/derived/phase7-v1](../data/derived/phase7-v1), [data/derived/phase7-v2](../data/derived/phase7-v2). Real source run **42324639484**, pseudo source run **42327464929**, signed v2 run **42386487963**. No re-download of 3.6 GB archive required to rebuild this package.
- Selection: **pT_trackj1 > 5 GeV**. Generator-only frozen mass threshold **10.594606399536133 GeV**, track-multiplicity threshold **11**. Ordered cells **LL, LH, HL, HH** (mass first, multiplicity second). Four normalized fractions sum to one.
- Real unfolded four cells: **0.4287152164 / 0.0749634448 / 0.1327527463 / 0.3635685926**; shared-event nominal generator **0.4341625877 / 0.0658359881 / 0.1419956273 / 0.3580057969**.
- Pseudodata unfolded four cells: **0.4366239491 / 0.0725351127 / 0.1200947069 / 0.3707462313**; **independent known-target truth** **0.4489994512 / 0.0831352714 / 0.1096828051 / 0.3581824723**. Never substitute a pseudo nominal generator for the known target.
- Real unfolded − nominal differences: **mass-low +0.0036800854**, **track-low −0.0146902523**, **joint log-odds −0.0597334776**. Pseudo unfolded − independent truth: **−0.0229756608**, **−0.0019636003**, **+0.0522361448**, respectively.
- Source inventory: **29 project covariance components = 25 systematic-labelled + 4 stochastic** (finite evaluation MC, data bootstrap, MC-training bootstrap, NN ensemble); the official **1D** pseudo example selects **15 project-equivalent families**, not an official 2D 15-source prescription. Exact 25-label-to-paper identity mapping is **not independently verified**.
- Four *prespecified* DD/Sherpa source-correlation sensitivity models (both full, DD four-bin only, Sherpa four-bin only, both four-bin). Model-conditional joint log-odds SE: **real 0.092321–0.146783**, **pseudo 0.056651–0.112847**. Under the full/full model, Sherpa hidden-variable contributes **~96.02%** of real and **~87.85%** of pseudo *modelled joint log-odds variance*; not a physical probability or verified uncertainty.
- Real generator and unfolded measurement share event support: use **paired** finite-evaluation-MC covariance. Pseudo known-target truth is **independent**: include its finite-MC precision. The normalized four-cell covariance is **4×4, rank three in the contrast subspace**. Replicas use **R−1** sample covariance; real/pseudo data-bootstrap counts **100/25**; NN ensemble covariance of mean includes **/R**.
- Permanent results: [results/kti-nov18](../results/kti-nov18) (5 CSV tables, 4 SVG figures, Methods/Results draft, 12 true QA checks, JSON and SHA-256 manifest), merged [PR #3](https://github.com/DoorBlox/atlas-omnifold-research/pull/3). [CI 42442490666](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42442490666) **107 tests passed**; full derived workflow steps succeeded. The last three commits after that run touched documentation only; do not imply a new code rerun.
- Primary result table is [joint_cells.csv](../results/kti-nov18/tables/joint_cells.csv), not the illustrative tables in the external Deep Research report. [Fact-check](../docs/PHASE7_DEEP_RESEARCH_REPORT_10_FACTCHECK.md). For future conflicts, precedence is **frozen CSV + checksums → source code and CI → generated manuscript results → editable Google Doc → external report examples**.

## 3. Claim ladder, boundaries, and internal scientific gates

| Evidence level | Allowed statement | Forbidden escalation |
|---|---|---|
| **Observed and checksum-verified** | Four normalized fractions, marginal fractions, log-odds, their signed differences, fixed selection and binning | “ATLAS discovered a new correlation”, causal physics, statistical agreement/disagreement |
| **Computed under declared assumptions** | Source-decomposed conditional standard errors, four DD/Sherpa correlation sensitivity scenarios, modeled source variance shares | “Official ATLAS 2D error”, validated 68% coverage, measured source causal fraction |
| **One known-target pseudo comparison** | Released unfolded pseudodata and independent truth were compared once | “Passed repeated experimental closure”, “25 independent pseudoexperiments” |
| **Not established** | No unique approved 2D nuisance correlation or full repeated-unfolding null model | Real-data p-value, sigma, confidence-level claim, generator acceptance/rejection |

**Internal gates, for engineering traceability only** (translate to plain scientific limitations in the KTI manuscript):
- **G5 PROVISIONAL:** numerical source covariance verified, but family inclusion, 2D DD/Sherpa correlations, and training/systematic/reference dependencies not independently validated.
- **G8 UNVERIFIED:** conditional Gaussian/hybrid toys executed, but independent detector-level repeat-unfolding coverage not established.
- **G11 EXECUTED AS ONE KNOWN-TARGET COMPARISON:** not a repeated-experiment coverage or blanket “closure passed” claim.
- **G12 UNVERIFIED:** four a priori 2D correlation scenarios evaluated; no independently justified unique primary source model.
- **G15 NO-GO:** no calibrated real-data generator-compatibility p-value, sigma, or rejection verdict.

**Other limitations:** one coarse threshold-based 2×2 partition loses within-cell detail and cannot characterize all 24 observables; generator-defined thresholds are an analysis choice, not an optimal/unique binning; publicly released trained-weight variations are not independent full-detector-level experiments; 29 project labels are not independently one-to-one mapped to all 25 ATLAS publication systematics; source families and learned weights can be dependent; neither an official 2D smoother nor independent retraining checkpoints/large physical pseudodata ensembles have been verified. No new detector measurement, generator tune, new-particle claim, or primary C2ST result.

## 4. Publication and KTI readiness (do not conflate)

**School KTI / descriptive research report:** a defensible, meaningful *working* study with reproducible numerical results; still needs adviser review, a complete correctly attributed bibliography, figure/table insertion, discussion grounded in prior literature, format and language edits, and final approval. A green CI does **not** certify scientific novelty, external validity, physical coverage, or manuscript acceptance.

**Specialist HEP peer-reviewed journal:** **high editorial-fit/novelty risk at the current scope**. A four-cell projection of public unfolded data, with conditional sensitivity but no new calibrated physics inference, is unlikely *by itself* to meet the novelty expectations of flagship research journals. This is a reason to assess editorial fit honestly, **not** to fabricate significance or expand the scope without evidence. Potentially more suitable categories are a carefully reviewed reproducibility/education or transparent methodological case study, subject to actual journal aims and editorial policies. Do not promise acceptance.

**Journal candidates in the original school document:** EPJ C, SciPost Physics Core, and Physical Review D are **unverified prospects**, not approved targets. Before selecting any: check current aims/scope and article types, independent indexing records (Scopus or SINTA), current APC/waiver/SCOAP3 conditions, original contribution threshold, open-data/code policies, reference style, and whether an independent student secondary-analysis note is in scope. No blanket “no APC” or “diamond” assertion without official verification.

**Minimum publication-readiness gates:** (P1) demonstrate a bounded, literature-checked contribution rather than claiming “first-ever”; (P2) verify all paper/DOI metadata and in-text/reference cross-links in Zotero; (P3) insert actual four figures and essential tables with captions/units and distinguish real from pseudo; (P4) independent physics/statistics adviser review of covariance language; (P5) independent manuscript QA and reproducibility check against pinned files; (P6) journal-specific fit, indexing and fees verified; (P7) permissions/credit/ATLAS affiliation and dataset attribution checked. The last item is not an assertion of ATLAS endorsement.

**Optional improvement track (only after adviser/publication-fit review):** add one defensible, *predeclared* descriptive robustness check or physics-motivated discussion if it genuinely strengthens the argument and is supported by the released data. Do not make data-dependent threshold changes or convert unvalidated toy statistics to p-values to chase publishability. A full inferential extension is a separate research project with its own prerequisites.

## 5. Executable work units, dependencies, evidence, rollback

Each work unit is self-contained enough for a new session; no new raw extraction is required for the main descriptive track.

### B00 — Freeze the new scientific contract [DONE]
- **Goal:** align title, RQ1/RQ2, estimands, sources, and prohibited claims.
- **Prerequisites:** verified frozen v1/v2 and Nov-18 results bundle.
- **Files:** this blueprint; [docs/PHASE7_GO_EVIDENCE_REQUIREMENTS.md](../docs/PHASE7_GO_EVIDENCE_REQUIREMENTS.md); [results/kti-nov18/results.json](../results/kti-nov18/results.json).
- **Implementation:** adopt Section 1–3 scope and source hierarchy; archive C2ST as historical.
- **Acceptance/evidence:** exact source IDs, fractions, fixed thresholds and gate wording agree with results.json; no real p-value.
- **Rollback:** restore prior plan through Git history; never silently alter pinned numerical data.

### B01 — Reconcile the four-tab school Google Doc [DONE FOR WORKING DRAFT; ADVISER REVIEW PENDING]
- **Goal:** RESEARCH PLAN, TIMELINE, IMRAD, ARTICLE, and journal/reading tabs all describe *one* descriptive study without internal gate jargon in publishable prose.
- **Prerequisites:** B00. **Affected interface:** [school Google Doc](https://docs.google.com/document/d/1rTafCdT6ESCpH43HtrssArHpiUzVEhoYABzwQJewQ00/edit) (tab IDs RESEARCH PLAN t.0; JOURNALS t.o0j30s19884j; IMRAD t.eh0d0wgxdlkt; ARTICLE t.ehvbmc6f60r1).
- **Implementation:** preserve template questions/tables and historical context; replace 12 plan answer cells; correct September/October attribution (source extractions were **7–8 November**, not October); update November status and next actions; add plain-language limitations, publishability assessment and source hierarchy; add a specific IMRAD outline; remove G-code jargon from article-facing text; mark journal fees/indexing provisional.
- **Acceptance/evidence:** read back all four tabs; title/RQ/objective/method/limits agree; original table dimensions and template instructions preserved; exact source numbers and references consistent; no false acceptance/closure claim.
- **8 Nov readback:** RESEARCH PLAN retained the original 13×4 and 4×3 tables, with two RQs and two matched objectives; IMRAD uses the same 17-word title; ARTICLE has a 154-word abstract, five keywords, four source-backed figure links, plain-language limitations and no internal G-code labels; journal candidates are explicitly unverified. References, actual embedded figures, final page layout and adviser approval remain pending.
- **Rollback:** Google Docs version history; apply scoped edits only and record revision. Do not delete original research-plan tab.

### B02 — Preserve numerical and figure evidence [DONE for descriptive milestone]
- **Goal:** immutable, recomputable source-backed tables/figures.
- **Prerequisites:** B00. **Files:** [results/kti-nov18](../results/kti-nov18), [src/phase7_kti_bundle.py](../src/phase7_kti_bundle.py), [tests/test_phase7_kti_bundle.py](../tests/test_phase7_kti_bundle.py), frozen v1/v2.
- **Implementation:** use existing five CSVs, four SVGs, manifest and checks. No re-extraction or arbitrary simulation.
- **Acceptance/evidence:** [CI 42442490666](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42442490666): 107 tests; bundle 12 true checks, 5 tables, 4 figures. Rebuild from pinned moments if code changes.
- **Rollback:** restore source code/data to frozen commit; do not mutate published outputs without updated hashes and review.

### B03 — DOI and bounded novelty audit [COMPLETED]; Zotero import and journal-policy check [PENDING]
- **Goal:** trustworthy bibliography, bounded prior-work novelty positioning, then a realistic venue decision. **8 Nov evidence:** [13 verified DOI-backed papers and related-work map](../docs/KTI_BIBLIOGRAPHY_AND_NOVELTY_AUDIT_2026_11_08.md) and [full 7-page Executive Summary claim audit](../docs/KTI_EXECUTIVE_SUMMARY_FACTCHECK_2026_11_08.md). School's B. Citation List now has **12** candidates, each with a paraphrased cited idea, in-text citation, and APA-style source identity. They are **not yet imported into Zotero or proven to be cited in the final manuscript.**
- **Prerequisites:** B00; may proceed **in parallel with B02**, but not with conflicting edits to the Google Doc.
- **Files/interfaces:** Google Doc JOURNALS tab; Zotero (user-managed unless connector available); ATLAS PRL and supplement, Zenodo, OmniFold PRL, selected jet-substructure reviews; official journal sites/Scopus/SINTA.
- **Implementation:** DOI/publisher identity check and **bounded** close-prior-work search completed: established that 24D derived projections and other 2D charged-jet substructure are prior art; no identical paper was located in this search, but global priority is **not** proven. Removed misleading 2018 ATLAS Z+jets citation: DOI 10.1007/JHEP07(2018)159 is an unrelated Higgs-decay paper. Corrected ATLAS 2011 track-jet citation and Buckley et al. 2011 author metadata. Retained the original ATLAS **2024 Zenodo 3.6 GB HDF5** source and rejected conflation with the distinct **2026 CERN Open Data** release. **Still pending:** actual Zotero import/export, APA field generation, bidirectional in-text reference verification, independently checked journal scope/indexing/APCs, and adviser appraisal of novelty.
- **Acceptance/evidence:** **DOI/claim mapping DONE:** 13 peer-reviewed sources independently matched to their subjects and DOI records; 12 are listed in the school's required three-part citation-entry format, plus the 2024 dataset DOI and a separate novelty comparator. **NOT YET COMPLETE:** Zotero-managed records, confirmed manuscript citation placements, and independent authoritative journal fit/indexing/fee checks. Do not mark this entire B03 stage done before those tasks and adviser review.
- **Rollback:** keep a previous bibliography version; do not replace uncertain references with plausible fabricated citations.

### B04 — Full standalone manuscript draft PRODUCED; integration and visual QA PENDING
- **Goal:** school-ready IMRAD narrative whose Results exactly reproduce the pinned numbers and whose Discussion interprets without overclaiming.
- **Prerequisites:** **B01 + B02 + B03**. **Files/interfaces:** Google Doc ARTICLE tab; [MANUSCRIPT_RESULTS.md](../results/kti-nov18/MANUSCRIPT_RESULTS.md); four SVG figures; school/journal style guide.
- **Implementation:** unify title/abstract/objectives/conclusion; strengthen literature-supported introduction and physics motivation; insert 4 figures/essential tables with captions, units and provenance; present real and pseudo separately; remove internal gate codes; explicitly state model-conditional uncertainty and lack of calibrated p-values; check originality/attribution and rendering.
- **Acceptance/evidence:** adviser can trace every numerical sentence to a table; each figure/table cited in Results; no unsupported “significant”, “agreement”, “closure passed” or “ATLAS-approved”; PDF/page inspection and peer review.
- **Rollback:** preserve working article revision and previous image/table placements; revert only edited sections.

**8 November 2026 checkpoint:** The later Word artifact `Manuscript_Draft(1).docx` contains the full abstract-through-references draft, 3 tables, 4 figures and 14 reference entries. Its file hash and exact status are documented [here](../docs/KTI_MANUSCRIPT_DRAFT_CHECKPOINT_2026_11_08.md). This closes the *initial full-draft writing* subtask but **does not close B04**: numerical/citation verification, figure and final PDF-layout inspection, adviser edits, and any user-approved Google Doc ARTICLE integration remain.

### B05 — Independent scientific/editorial publishability review [PENDING]
- **Goal:** decide whether the *current* descriptive paper is appropriate for school KTI, reproducibility/education outlet, or specialist HEP research journal.
- **Prerequisites:** **B02 + B03 + B04 draft**. **Files/interfaces:** reviewer checklist in Google Doc / GitHub; venue policies; independent adviser notes.
- **Implementation:** ask a particle-physics/statistics reviewer to examine joint-vs-marginal contribution, conditional covariance wording, exact known-target diagnostic, novelty relative to existing multidimensional ATLAS analyses, journal fit, and attribution. Categorize blocking vs optional improvements.
- **Acceptance/evidence:** written critique and disposition; realistic venue and contribution statement; no unverified “publishable” guarantee.
- **Rollback:** if editorial fit fails, revise venue or framing, not numerical thresholds or inferential claims.

### B06 — Optional inferential extension [BLOCKED; OUT OF CURRENT KTI SCOPE]
- **Goal:** *only if explicitly chosen later*, justify and validate a primary 2D nuisance/null model for a calibrated compatibility claim.
- **Prerequisites:** independent source-level 2D correlation justification (G5/G12), sampling model and repeat-unfolding coverage or independently justified limited conditional interpretation (G8), pseudodata-first validation, preregistration; **must not depend on observed real residual**.
- **Files:** [docs/PHASE7_GO_EVIDENCE_REQUIREMENTS.md](../docs/PHASE7_GO_EVIDENCE_REQUIREMENTS.md) and new protocol/tests; preserve old results.
- **Implementation:** obtain missing physical ensembles/checkpoints or an independently defensible narrower model; validate on pseudo before real; only then reconsider G15.
- **Acceptance/evidence:** reviewer-approved primary model, full method and null calibration appropriate to claimed interpretation, independent validation, no post-hoc selection. **Currently NO-GO**.
- **Rollback:** keep all results descriptive and do not publish inferential outputs.

### B07 — School submission and presentation package [PENDING]
- **Goal:** a complete reviewed KTI report and presentation, not merely a green CI.
- **Prerequisites:** **B04 + B05**, plus school format requirements.
- **Files/interfaces:** Google Doc final article, figure exports, reference manager bibliography, presentation and final submission copy.
- **Implementation:** adviser sign-off, cover/author/affiliation accuracy, 150–250-word abstract, 3–5 keywords, accessible captions, final proof, source acknowledgment, oral-defense narrative distinguishing what was measured from what is assumed.
- **Acceptance/evidence:** approved manuscript and checked final PDF/slides, references synchronized, deadline and venue requirements verified. No external submission without user's explicit approval.
- **Rollback:** retain draft and final versions, correct before submitting.

### B08 — Reproducibility handoff and audit [PARTIAL; COMPLETE AFTER B04]
- **Goal:** a future student can reproduce and critique the descriptive result without the chat history.
- **Prerequisites:** **B02 + B04**. **Files:** [docs/START_HERE_HANDOFF.md](../docs/START_HERE_HANDOFF.md), [README.md](../README.md), this blueprint, manifest.
- **Implementation:** record exact final title, source provenance, commit, commands, result/figure paths, bibliography version, limitations, adviser decisions and any approved scope changes.
- **Acceptance/evidence:** fresh reader can reproduce numerical bundle and locate all claims; software checks pass; editorial checks documented separately.
- **Rollback:** revert documentation changes without modifying frozen source outputs.

**Dependency graph:** B00 → (B01, B02, B03); (B01, B02, B03) → B04; (B02, B03, B04) → B05; (B04, B05) → B07; (B02, B04) → B08. B06 is optional and blocked on external methodological evidence; it is **not** a prerequisite for B07. Parallelizable only where files do not overlap: numerical B02 and external-source B03; B01 Google Doc edits are sequential and revision-guarded.

## 6. Timeline and decisions requiring human review

- **By 8 November 2026 — completed:** numerical bundle, four figures, five tables, 12 QA checks, 107-test CI; first working article draft. No calibrated p-value.
- **9–18 November — next review window:** confirm rewritten school plan, reconcile IMRAD and ARTICLE, verify primary references, ask adviser for scientific and school-format feedback, inspect figures. **Nov 18 numerical deliverable already complete**, not synonymous with final submission.
- **19–24 November — target, not guaranteed:** complete Zotero bibliography, manuscript figure/table integration, independent source and physics review, abstract/conclusion alignment.
- **25–30 November — target, subject to adviser approval:** final proof, defense slides, choose realistic venue; do not submit or claim journal acceptance automatically.
- **Unresolved decisions:** school submission template and exact due date; adviser reviewer and feedback; whether publication means school KTI, preprint, or peer-reviewed journal; whether optional robustness/novelty improvement is warranted; verified journal indexing/fees. None of these should block presenting the completed descriptive results accurately.

## 7. Blueprint self-review / failure modes

- **No circular dependencies:** B06 is deliberately off the school-KTI critical path. B04 depends on verified references and Google plan, not on journal acceptance.
- **No hidden numerical migration:** the analysis uses pinned v1/v2; new publication-facing wording must not silently alter thresholds, source count, reference sample or figure values.
- **No phantom validation:** 107 software tests and 12 bundle checks do not imply independent physics validation or coverage. One known-target pseudo comparison is not an ensemble.
- **No retrospective date laundering:** real/pseudo extraction source runs occurred in November; September/October are historical planning only unless separately evidenced.
- **No false journal assurances:** indexing, fees, acceptance, novelty and authorship require source-level verification and human editorial judgment.
- **No silent source drift:** if external research conflicts with frozen numerical results, inspect primary data and code before editing; never copy illustrative tables.
- **No permission to submit:** plan authorizes drafting and editing requested files, not external journal submission, public preprint posting, or claims of ATLAS endorsement.

**Next executable step:** **PAUSE manuscript writing at user request.** The supplied PDF was fact-checked and a bounded novelty/DOI audit completed. Remaining B03 tasks are actual Zotero import/export, cross-reference placement when writing resumes, and independent venue/indexing/APC checks; obtain adviser confirmation of the precise novelty claim. B04 manuscript figure integration is deliberately deferred. B01 Google Doc answered all twelve school table rows in place, retained both original tables, updated November status, and populated twelve three-part citation entries. G15 NO-GO remains unchanged.

## 8. Manuscript content map and publication ethics

**Binding title:** *A Reproducible Four-Cell Analysis of Leading Charged-Jet Mass and Track Multiplicity in ATLAS 2024 OmniFold Z+Jets Data* (17 words). A 2×2 analysis of an unbinned **release** is itself a four-cell binned projection; do not misleadingly call the downstream analysis “unbinned.” The Google Doc ARTICLE tab currently contains a **working** draft, not a final submitted manuscript.

**Front matter:** Abstract 150–250 words, one paragraph, no citations; include the actual observed real/pseudo mass-low, track-low and log-odds differences and the conditional DD/Sherpa sensitivity range, ending with the absence of calibrated inference. Use 3–5 relevant keywords, confirmed author names, school affiliation and contact information. No invented collaborators or email.

**Introduction:** establish ATLAS 2024 PRL and public release, OmniFold methodology, jet-substructure motivation, and the mathematical information lost in separate marginals. A positive normalized 2×2 table has three independent coordinates: two marginals **plus one association parameter**. State RQ1/RQ2 and a bounded contribution. Independently verify whether closely related mass–multiplicity projections already exist; do **not** assert “first” without a literature search. Each physics/method claim needs a traceable primary citation.

**Methods:** observational quantitative secondary analysis; official data DOI and immutable derived source hashes; pT_trackj1 > 5 GeV, mass threshold 10.594606399536133 GeV, multiplicity threshold 11, LL/LH/HL/HH (mass first); p_i=h_i/Σh, mass-low=p_LL+p_LH, track-low=p_LL+p_HL, L=ln[(p_LL p_HH)/(p_LH p_HL)]; shared real-generator paired finite-MC vs independent pseudo-target finite-MC; 29 project components (25 systematic-labelled + four stochastic), 15-source 1D notebook subset; R−1 replicas; normalized 4×4 covariance with null mode/three contrasts; four **project-fixed** DD/Sherpa full/four-bin sensitivity models; one known-target pseudo diagnostic; deterministic source-backed code and checks. Distinguish verified arithmetic from unverified physical source correlations.

**Results:** Table 1 four joint cells and signed percentage-point differences for real and pseudo; Table 2 two marginals and joint log-odds with correctly labeled conditional SE; Table 3 four DD/Sherpa scenario SEs; Table 4 selected conditional source-variance shares. The fifth CSV (full 4×4 covariance) belongs in the supplement until its assumptions and caption are reviewed. Figure 1 four actual shapes, Figure 2 signed cell/marginal contrasts, Figure 3 source contributions, Figure 4 scenario sensitivity. Place all four figures, cite them in Results, use legible legends/units and verify every plotted number against the frozen CSV. **No real-data p-value, sigma or claim of significant agreement/disagreement.**

**Discussion:** explain why the joint association is not determined by two marginals; do not overstate the modest real-versus-generator descriptive difference. Discuss material DD/Sherpa conditional uncertainty sensitivity and why large model-dependent source shares are not physical probabilities. Explain the one-target pseudo diagnostic without declaring repeated closure, the coarse generator-defined 2×2 binning, lack of rebinning robustness from frozen moments, one nominal generator, 25-source identity mapping and potential training/systematic dependencies, and the absence of independently retrained pseudo-experiment coverage. Compare with verified ATLAS/OmniFold and jet-substructure literature. The contribution is **transparent joint-data reuse and uncertainty-scope discipline**, not a new physics discrepancy.

**Conclusion:** directly answer RQ1 and RQ2 without new data or a formal generator verdict. Distinguish what was computed, what is assumption-conditional and what remains unknown. Keep G5/G8/G11/G12/G15 **internal**; public manuscript prose should explain actual limitations rather than gate acronyms.

**Statements:** public Zenodo DOI; repository and exact SHA-256 manifest/CI; provenance of original ATLAS measurement and independent student analysis; confirmed human authorship and adviser contributions; school/journal funding/conflict statements; data/software reuse rights; AI assistance disclosure as applicable. Public particle-physics data do not imply new human-subject recruitment. Verify license/credit rather than asserting blanket permission or ATLAS endorsement.

**References:** the school template requests at least **ten genuinely relevant, actually cited** sources managed with Zotero. Verify each DOI/title/author/year from publisher or official record and map every scientific claim to its source. Two imported older ATLAS references in the Google Doc appear to have incomplete titles; repair metadata before citing. Classification-based tests, Cowan asymptotics, boosting and generic ML papers are **historical reading**, not necessarily methods used in this four-cell analysis.

**Publication reality:** a transparent school KTI/competition report is feasible with review; specialist journals EPJ C, SciPost Physics Core and Physical Review D remain **aspirational unverified candidates**. Do not assume that a descriptive four-cell secondary analysis satisfies their novelty threshold. Confirm school SINTA/Scopus requirement, official current indexing, article types, APC/SCOAP³ policy, author guidelines and novelty fit. Consider a reproducibility/education/technical-note or conference route **only if** an appropriate verified venue exists. Journal acceptance is not promised; external submission requires human author/adviser approval.

**Editorial acceptance:** (a) title <20 words; (b) 150–250-word abstract; (c) 3–5 keywords; (d) exactly two RQs and two matched objectives; (e) real and pseudo references never swapped; (f) all four source-backed SVG figures and the necessary numerical tables (currently three in the Word draft) integrated and visually inspected in PDF; (g) no internal gate codes or unsupported significance in ARTICLE; (h) at least ten verified Zotero sources if school rule stands; (i) data/code/AI/author statements complete; (j) reviewer-approved final text. Passing 107 code tests does not certify any of (f)–(j).

**Publication decision questions for adviser:** Is the revised descriptive scope acceptable as the complete KTI? Does the school require an actual indexed journal publication, only a target venue, or a school competition report? What are the required language, length, format, and actual deadline? The numerical package is finished; these editorial decisions are still pending.

## 9. November 2026 independent source and novelty audit (completed, Zotero pending)

- [Detailed source-by-source fact check of user-supplied seven-page Executive Summary PDF](../docs/KTI_EXECUTIVE_SUMMARY_FACTCHECK_2026_11_08.md): discovered that LL cell and mass-low marginal contrasts were confused, the 2024 Zenodo HDF5 release was conflated with a different 2026 CERN full-phase-space dataset, incorrect claims were made about 1D smoothing, cross sections, statistical coverage, p-values, software paths and licenses. **Do not use that PDF as a KTI results source.**
- [Verified 13-paper DOI bibliography and bounded novelty map](../docs/KTI_BIBLIOGRAPHY_AND_NOVELTY_AUDIT_2026_11_08.md): related ATLAS 24D derived observables and previous 2D charged-jet studies limit priority claims. A direct published match for this exact threshold-defined projection was **not located in the bounded search**; this does not prove novelty globally.
- Google Doc **RESEARCH PLAN** Table A (13×4) now gives direct numbered answers to the template guiding questions in all twelve rows; Table B remains 4×3 and records the November audits as finished. **TARGET JOURNALS AND READING SOURCES** section B now has 12 candidate citations each with an original idea, in-text citation, and APA-style source identity; exact Zotero-generated APA output is still pending. **ARTICLE tab was not edited during this audit** by explicit user instruction.
- Current permitted research claim: transparent and reproducible secondary-data application and an **assumption-conditional** source/correlation sensitivity exercise. No first-ever 2D ATLAS result, new detector measurement, official 2D covariance approval, validated physical coverage, calibrated real-data generator p-value or external-journal acceptance.

