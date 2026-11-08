# KTI scope decision and publication blueprint — 8 November 2026

**Decision:** Freeze the primary paper as a **reproducible, descriptive secondary analysis** of a normalized 2×2 joint distribution of leading charged-jet mass and charged-track multiplicity in the public ATLAS 2024 unbinned Z+jets OmniFold release. Do **not** sell this as a calibrated generator-compatibility hypothesis test. The November 18 **numerical** milestone is completed ahead of schedule; manuscript, reference, expert-review and venue decisions remain open.

**Status authority:** [immutable November 18 evidence bundle](../results/kti-nov18/README.md), [machine-readable results](../results/kti-nov18/results.json), [12 checks](../results/kti-nov18/checks.json), [107-test successful CI](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42442490666), [source-accounting and GO requirements](../docs/PHASE7_GO_EVIDENCE_REQUIREMENTS.md), [ATLAS paper](https://doi.org/10.1103/PhysRevLett.133.261803), [ATLAS release](https://doi.org/10.5281/zenodo.11507450). No new numerical result is asserted in this blueprint. This is independent student research, not an ATLAS collaboration paper.

## 1. Canonical scope: one story across plan, methods, article and figures

**Working title (under 20 words):** *Reproducible Joint-Shape Analysis of Charged-Jet Mass and Track Multiplicity in ATLAS 2024 Unbinned Z+Jets Data.*

**Design:** quantitative, observational, reproducible **secondary analysis of public particle-physics measurement products**, not a new detector experiment, causal study, randomized trial, systematic literature review, or novel unfolding algorithm. The published ATLAS detector measurement and OmniFold algorithm are the data-producing methods; this project makes an independent downstream four-cell projection and audit.

**Problem:** Separate one-dimensional mass and multiplicity histograms cannot recover the dependence between the two observables. A positive normalized 2×2 joint table has three degrees of freedom: two marginals **plus one association parameter**. This is the conceptual contribution; the numerical result is a documented application to real released weights, with comparator-aware conditional uncertainty sensitivity and one known-target pseudodata comparison.

**Research questions (exactly two):**
- **RQ1 — structure:** How do the unfolded real-data four-cell mass–multiplicity shape, its two marginals, and its joint log-odds association differ descriptively from the shared nominal generator?
- **RQ2 — methodological robustness:** How sensitive are these descriptions to the four predeclared DD/Sherpa source-correlation assumptions, and what can the single unfolded-pseudodata-versus-independent-truth comparison establish?

**Objectives:** (O1) Reconstruct, compare and explain the four cells, two marginals and joint log-odds for real unfolded data versus the nominal generator. (O2) Quantify conditional source and scenario sensitivity, use the independent known-target pseudodata as a **single** closure example, and delimit what the released materials cannot validate.

**Supported contributions:** an auditable four-cell downstream projection; the joint association beyond two marginals; explicit distinction between paired real-generator and independent pseudo-truth reference statistics; signed source-family reconstruction and normalization-preserving 4×4 covariance; a transparent, **provisional** DD/Sherpa sensitivity exercise; machine-reproducible figures and tables. **Not claimed:** first-ever ATLAS joint study, new jet physics, generator exclusion, a significant discrepancy, a validated ATLAS 2D covariance prescription, or physical frequentist coverage. Independent novelty review remains pending.

## 2. Fixed data, definitions and provenance

- Source: ATLAS Collaboration (2024), PRL **133**, 261803; official Zenodo release DOI **10.5281/zenodo.11507450**; official supplemental User Guide Section 2 recommendation 5. Use the exact published title and metadata from the primary record when finalizing citations.
- Input: **checksum-pinned derived v1/v2** four-cell moments and signed source shifts; v1 real run **42324639484**, pseudo run **42327464929**, signed v2 extraction run **42386487963**. No raw event files or 3.6 GB ZIP in this repository; the frozen summaries cannot support arbitrary new thresholds or full OmniFold retraining.
- Selection: **pT_trackj1 > 5 GeV**. Mass threshold **10.594606399536133 GeV**; multiplicity threshold **11 tracks**. These thresholds were frozen from the nominal generator. Four-cell order **LL, LH, HL, HH**, with mass category first. Do not quietly optimize thresholds against real residuals. The project README records **417,401 selected nominal rows** and **23,888,304 selected independent pseudo-target rows**; event/weight rows are not independent repeated experiments.
- Four shape vectors (LL/LH/HL/HH), from the verified output:
  - **Real unfolded:** 0.4287152164 / 0.0749634448 / 0.1327527463 / 0.3635685926.
  - **Real nominal generator:** 0.4341625877 / 0.0658359881 / 0.1419956273 / 0.3580057969.
  - **Pseudo unfolded:** 0.4366239491 / 0.0725351127 / 0.1200947069 / 0.3707462313.
  - **Independent pseudo known truth:** 0.4489994512 / 0.0831352714 / 0.1096828051 / 0.3581824723.
- For signed cell weight totals h_i, normalized p_i=h_i/Σh_j. Marginals: mass-low=p_LL+p_LH, track-low=p_LL+p_HL. Association L=ln[(p_LL p_HH)/(p_LH p_HL)] for positive cells. The two marginals alone do not determine L.
- Real **unfolded-minus-nominal-generator** contrasts use shared-event **paired** finite-MC covariance. Pseudodata **unfolded-minus-independent-known-target** contrasts include independent truth precision. Do not interchange these comparators.
- The 4×4 normalized-shape covariance has a normalization-null direction and three independent contrasts. Signed count-level source shifts are normalized using J=(I−p1ᵀ)/H. Replica covariance uses R−1; the NN ensemble has an additional averaging divisor. Counts differ across real/pseudo replica families.

## 3. Results that are actually finished

| Observable | Real unfolded minus nominal generator | Pseudo unfolded minus independent truth |
|---|---:|---:|
| Mass-low fraction | +0.0036800854 | −0.0229756608 |
| Track-low fraction | −0.0146902523 | −0.0019636003 |
| Joint log-odds L | −0.0597334776 | +0.0522361448 |

- Four **predefined within this project** DD/Sherpa full-versus-independent-four-bin correlation scenarios produce **conditional** joint-log-odds SEs: real **0.092321 / 0.106422 / 0.136904 / 0.146783**; pseudo **0.056651 / 0.078706 / 0.098738 / 0.112847**, in full/full, DD-independent, Sherpa-independent, both-independent order. The alternatives are model sensitivity, **not** four calibrated confidence procedures.
- Under the full/full conditional model, Sherpa hidden-variable contributes approximately **96.02%** of modeled real joint-log-odds variance and **87.85%** of pseudo variance. These are model-dependent decomposition shares, not a probability of a causal mechanism.
- Archived project inventory: **29 = 25 systematic-labelled + four stochastic** source terms; the official **1D** pseudodata example selects 15 project-equivalent terms. Exact one-to-one mapping of all 25 project labels to the publication's 25 systematic components is **not independently established**.
- **One** unfolded-pseudodata sample is compared with its independent known truth. This does **not** establish repeated detector-level unfolding coverage. Conditional Gaussian and empirical-replica hybrid toys were run, but neither substitutes for independently retrained pseudo-experiments.
- Delivered: **5 numerical CSV tables**, **4 SVG figures**, Methods/Results text, results.json, checks.json (**12 true QA checks**), SHA-256 manifest; **107/107 CI tests passed**. See [results/kti-nov18](../results/kti-nov18/README.md). Generated vector graphics are machine-valid, **not yet visually/page-layout approved**.
- No real-data compatibility **p-value, sigma, confidence level, exclusion or verdict** is authorized. A small difference does not prove agreement; a nonzero difference does not prove disagreement.

## 4. Scientific limits and internal gate glossary

**Use plain-language limitations in the published paper; keep G labels in internal project notes only.**

| Internal gate | Status | Plain-language meaning |
|---|---|---|
| **G5** — source/covariance defensibility | **PROVISIONAL** | Source arithmetic and normalization work, but a uniquely justified two-dimensional source inclusion/dependence/correlation model has not been established. |
| **G8** — null calibration/coverage | **UNVERIFIED** | Assumed-model simulations exist; repeated detector-level independently retrained unfolding coverage is not demonstrated. |
| **G11** — known-target closure | **ONE EXERCISE EXECUTED** | One released pseudo-unfolded sample was compared with an independent truth sample; it is not an ensemble or a guarantee of unbiasedness. |
| **G12** — 2D nuisance correlations | **UNVERIFIED** | Four full/independent-bin DD/Sherpa choices are documented sensitivity scenarios, not an officially selected 2D model. |
| **G15** — real-data inferential release | **NO-GO** | No defensible calibrated generator-compatibility p-value or sigma claim can be published from this workflow as it stands. |

**Additional limitations to state or audit before submission:**
1. This is a **coarse, generator-threshold-defined** 2×2 projection, not a full continuous joint density; binning robustness is **not tested** from the frozen summaries, and any alternative binning requires a new raw-data extraction.
2. The single nominal generator is a **reference**, not a representative ensemble of all generator physics hypotheses; no tuning, causal mechanism, or all-24-observable survey is performed.
3. Choice of these two observables followed an exploratory project history. Do not claim independent preregistration or a fully blinded variable-selection protocol without records.
4. Weighted events and released replicas can share data/training dependence; the published 1D helper does not prescribe a unique 2D DD/Sherpa smoother or all cross-family dependencies.
5. Finite evaluation MC, data/MC training bootstraps and NN ensemble are distinct stochastic components; do not confuse source count with number of independent experiments.
6. The one known-target pseudodata comparison has finite reference precision and may differ from truth; neither its central closeness nor conditional toy behavior proves calibrated coverage.
7. Source-variance percentages are **conditional** on the chosen correlation assumptions; avoid presenting them as experimentally measured physical contributions.
8. The original raw HDF5 and full training checkpoints are **not archived in the project**; the current snapshot is sufficient for exact reproduction of the frozen projection, not arbitrary analyses.
9. A 2×2 descriptive analysis alone may offer **limited physics novelty** for specialist journals. Publication eligibility, licensing/attribution, literature priority, author roles, journal indexing, APC and target-journal fit are **not verified**.
10. AI-assisted writing/research/code, if used, must be verified by the student, disclosed if required by school/journal rules, and never treated as an author or substitute for human scientific accountability.

## 5. Paper architecture — what to write, show and not say

**Title:** the canonical title above, without a promise of a new test. **Abstract:** 150–250 words, no references; objective, public release, frozen 2×2, actual real/pseudo results, scenario sensitivity, no calibrated inference. **Keywords:** 3–5 meaningful terms (e.g. OmniFold; jet substructure; joint distributions; uncertainty modelling; reproducibility). **Author/affiliation:** supplied by the student and adviser; do not invent.

**1 Introduction (~700–1,000 words):** ATLAS 2024 release and OmniFold; what one-dimensional marginals miss; jet mass and track multiplicity as related observables; exact gap = *auditable downstream four-cell comparison and uncertainty sensitivity*, not claimed first discovery; RQ1/RQ2 and contribution. Verify citations for each technical claim.

**2 Methods (~1,200–1,700 words):** observational secondary analysis and source attribution; 2024 public data, v1/v2 hashes and selected support; generator-defined selection and thresholds; four-cell algebra and log-odds; explicit reference pairings; 29 family taxonomy versus official 1D 15-family example; R−1 bootstrap and paired finite-MC; normalization-preserving 4×4 covariance, three contrasts; four **project-prespecified** DD/Sherpa assumptions; single known-target pseudo comparison; deterministic code/tests. State that uncertainties are *model-conditional* and do not establish physical coverage. No unverified mathematical theorem or citation.

**3 Results (~800–1,100 words):** Table 1 all four real/pseudo cell fractions and signed percentage-point differences; Table 2 two marginals + L, references and conditional SE; Table 3 four model-sensitivity SE values; Table 4 selected source-variance shares; Figure 1 joint four shapes, Figure 2 signed cell/marginal contrasts, Figure 3 source variance shares, Figure 4 scenario SE sensitivity. Place captions and cross-references, report actual numbers only; reserve interpretation for Discussion. Fifth CSV = complete 4×4 covariance, recommended **supplementary**, not an unsupported journal-ready confidence region.

**4 Discussion (~900–1,300 words):** (a) two marginals + association give three independent normalized-table coordinates; (b) actual real association contrast is modest and **cannot be called significant or insignificant** without validated sampling; (c) source correlation materially affects conditional uncertainty; (d) independent pseudo known-target comparison supports a single transparent check but not repeated coverage; (e) compare with cited ATLAS/OmniFold/jet-substructure literature, without implying ATLAS endorsement; (f) honest limitations and what would enable stronger inference. The scientific result is the reproducible joint-versus-marginal *description* and demonstrated uncertainty-model sensitivity, not evidence of a new physics discrepancy.

**5 Conclusion (2–3 short paragraphs):** answer RQ1 and RQ2 without new numbers; reproducible contribution and calibrated limits; next step for genuinely validated inference. **Data/code availability:** source DOI, frozen v1/v2, GitHub commit/manifest, Python command, figure/table paths. **Acknowledgements/author contributions/funding/conflicts/AI-use:** fill with verified human information and applicable journal policy. **References:** APA 7 via Zotero per school instructions; verify every DOI/title/author and every in-text/reference pairing.

**Editorial quality gates:** title <20 words, abstract 150–250 words, 3–5 keywords, exactly two RQs matched to two objectives, all captions and units correct, equations and four-cell labels consistent, no internal G-code in public article, all source citations verified, no illustrative research-report values, no invented source shares, no real-data p-values. The current ARTICLE tab is a **working draft**, not an accepted manuscript.

## 6. Publication realism and two-track delivery

**Track A — school KTI / adviser / research competition:** achievable now after scientific wording, Zotero, layout and human review. Evaluate against the school's actual rubric and word/page rules. A transparent negative-or-inconclusive descriptive result is legitimate; do not manufacture significance to satisfy a competition narrative.

**Track B — external peer-reviewed journal:** **not publication-ready**. The three journals currently listed in the Google Doc (EPJ C, SciPost Physics Core, Physical Review D) are aspirational physics venues with a substantial novelty/impact bar. Their current indexing, scope, article types, acceptance standards, fee/SCOAP³ policies and submission rules have **not been independently checked in this blueprint**. Do not claim any venue will accept a four-cell descriptive reanalysis. Independently review prior joint ATLAS OmniFold projections and uncertainty-method papers, then decide with adviser whether the paper fits a specialist methods/data-reuse/physics-education outlet, a conference proceeding, a school competition, or a non-peer-reviewed reproducible technical note. Any SINTA/Scopus requirement must be checked against the school's actual rules and official current sources. Avoid predatory/guaranteed-acceptance promises and paying an APC before suitability is established.

**Potential journal-strengthening work (optional, never pretend already done):** independently verify novelty and existing related 2D studies; obtain an expert critique of the covariance model; test additional binning/selection or alternative generators **only if raw data and compute are available**; supply justified conditional inference only after a specific statistical model is validated; show the difference between 1D and joint information quantitatively without p-value inflation. The manuscript must stand as a complete descriptive KTI even if none of these extensions is feasible.

## 7. Executable blueprint: independent tasks, dependencies and rollback

**B0 — scope freeze and evidence inventory [DONE, 8 Nov].** Prerequisites: published ATLAS release, frozen v1/v2 and CI. Owners: student + code. Artifacts: results/kti-nov18/*, docs/PHASE7_GO_EVIDENCE_REQUIREMENTS.md. Acceptance: 12/12 source QA and 107/107 tests, manifest pinned; explicit G15 NO-GO. Rollback: retain immutable prior snapshot and Git commits; never overwrite evidence.

**B1 — reconcile all Google Doc tabs [IN PROGRESS, 8 Nov; prerequisite B0].** Edit RESEARCH PLAN answer cells, timeline, journal/source caveats, IMRAD article map and ARTICLE internal-gate wording. Acceptance: one identical title, two RQs/two objectives, one frozen dataset/selection/comparator definition, identical uncertainty caveat and Nov-18 milestone across tabs; original school guidance and tables preserved. Rollback: Google Docs revision history; update only scoped cells/paragraphs with revision guard.

**B2 — source and novelty bibliography audit [PENDING; B0].** Files: Google Doc reading tab, Zotero library, eventual article References. Work: verify ATLAS paper, Zenodo, OmniFold paper, user guide and relevant jet-substructure/unfolding/secondary-analysis precedents; record DOI, claim supported, exact page/section, and relevance; check whether similar mass×multiplicity joint projections have been published. Acceptance: >=10 **verified and actually cited** sources (school template requirement), no orphan citations, no false "first" claim. Rollback: remove unverified references, retain DOI audit log. Parallel with B3 and B4.

**B3 — scientific-method peer review [PENDING; B0].** Files: docs/PHASE7_GO_EVIDENCE_REQUIREMENTS.md, results/kti-nov18, adviser notes. Ask adviser/statistician to inspect event support, variable/bin choice, real-vs-pseudo comparator distinction, 29/15 family mapping, source dependence, closure wording and conditional variance shares. Acceptance: written list of accepted interpretations, revisions and unresolved limitations; no automatic change to frozen numbers. Rollback: revert prose-only overclaims, keep analysis immutable. Parallel with B2/B4.

**B4 — figures and table editorial QA [PENDING; B0].** Files: four committed SVGs, five CSVs, article captions. Inspect visually for readability, fonts, units, color accessibility, signed percentage points, source names, figure labels and legends; export test to PDF/page. Acceptance: every figure/table referenced in Results, no rasterization/overlap errors, numeric cross-check against CSV. Rollback: regenerate from pinned snapshots; do not hand-edit plotted values. Parallel with B2/B3.

**B5 — complete IMRAD manuscript [PENDING; B1+B2+B3+B4].** Files: Google Doc ARTICLE and optional DOCX/PDF export. Fill 150–250-word abstract, keywords, literature-supported Introduction, detailed Methods, numbered Results with tables/figures, critical Discussion, Conclusion, acknowledgements, data/code and transparency statements, Zotero references. Acceptance: school IMRAD checklist passed, adviser checks all physics claims, no G-code/p-value/ATLAS endorsement in article, title/abstract/conclusion agree. Rollback: preserve previous Google Docs revision and Git numerical bundle.

**B6 — journal/competition venue decision [PENDING; B2+B3].** Verify actual school requirement, journal scope/indexing/fees/peer-review integrity and originality threshold from official sources; consult adviser before submission. Acceptance: a documented realistic target and a **fallback**; journal submission only if manuscript and novelty meet its bar. Rollback: choose KTI competition/technical note, do not invent impact.

**B7 — Nov 18 handoff [NUMERICAL DONE; full editorial sign-off PENDING; B5].** Provide manuscript draft, actual data/figures, verification link, source/limitation statement and adviser question list. Acceptance: reviewer can reproduce the exact 2×2 from source files without downloading raw ZIP; no unvalidated inference. Rollback: label as draft and document unresolved items instead of claiming final publication.

**B8 — final submission package [PENDING; B5+B6+B7].** Generate journal/school-specific manuscript and slide deck after sign-off, inspect rendered pages, confirm source licensing and author/AI declarations, verify references and file integrity. Acceptance: all required files and metadata checked; human author explicitly approves any external submission. Rollback: keep working draft, do not submit.

**Dependency graph:** B0 → {B1, B2, B3, B4}; {B1,B2,B3,B4} → B5; {B2,B3} → B6; B5 → B7; {B5,B6,B7} → B8. B2/B3/B4 can run in parallel with separate ownership; B5 must wait for their scientific conclusions. No cyclic dependencies.

**Timeboxes (target, not invented completion):** 8 Nov B0/B1; 9–12 Nov B2/B3/B4; 13–16 Nov B5; by 18 Nov B7 adviser-ready package; 19–24 Nov revise manuscript and venue decision; 25–30 Nov final school package/presentation, and journal submission **only if** approved and appropriate. If a deadline slips, preserve accuracy and label outstanding work rather than filling with unverified claims.

## 8. Acceptance checklist and decisions requiring the student/adviser

- [x] Frozen four-cell real/pseudo fractions, independent truth, nominal reference and source checks.
- [x] Reproducible five CSV tables, four SVG figures, Methods/Results source draft and 107-test CI.
- [x] No unsupported real-data p-value, sigma or generator verdict.
- [ ] Two-RQ scope and wording approved by adviser.
- [ ] Official-source literature priority/novelty audit completed; at least ten verified Zotero entries used in text.
- [ ] All figure captions, plots, tables and manuscript page layout reviewed visually.
- [ ] Source inclusion/correlation limitations reviewed by someone competent in experimental HEP uncertainty modelling.
- [ ] Complete polished ARTICLE, author/affiliation/acknowledgements/AI disclosure, checked references and required formats.
- [ ] School submission rules, competition eligibility, and realistic journal venue/fees verified from official sources.
- [ ] Human author/adviser sign-off before public journal submission.

**Three decisions to request, not assume:** (1) Does the adviser accept a **descriptive secondary analysis** as a complete KTI, without a significance claim? (2) Does the school require a SINTA/Scopus journal **publication**, merely a journal **target**, or a competition manuscript? (3) What word/page, language, citation and submission deadlines actually apply? Until answered, the technically correct fallback is a polished school KTI with a truthful publication-readiness assessment.

**Change control:** Any proposal to revive a formal generator-compatibility test is a **separate, gated extension**, not a silent change to this paper. It requires an independently justified 2D source model and sampling interpretation, suitable pseudodata validation, and a reviewed release decision. Existing tests passing cannot waive these scientific conditions.
