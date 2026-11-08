# KTI manuscript-draft checkpoint — 8 November 2026

**Project:** [DoorBlox/atlas-omnifold-research](https://github.com/DoorBlox/atlas-omnifold-research)  
**Canonical title:** *A Reproducible Four-Cell Analysis of Leading Charged-Jet Mass and Track Multiplicity in ATLAS 2024 OmniFold Z+Jets Data*  
**Stage:** full standalone Word **draft produced**; editorial integration, Zotero bibliography, independent review and submission approval **pending**. This checkpoint reports an achieved writing milestone, **not** a new physics-analysis result.

## 1. New manuscript achievement and artifact identity

The user-supplied ChatGPT-session file **`Manuscript_Draft(1).docx`** is the complete working Word manuscript produced after the earlier source/bibliography audit. Direct inspection of the DOCX in this checkpoint found:

- The canonical study title; a **202-word abstract**; keywords; Introduction; Materials and Methods (six subsections); Results; Discussion; Conclusion; Data and code availability; Acknowledgments and declarations; References.
- **Three numerical tables**, **four embedded scientific figures**, and **14 reference-list entries** (13 scholarly publications plus the original 2024 ATLAS dataset).
- Approximately **5,760 whitespace-delimited words when including tables and references**, which is an inventory, not a journal word-count certification. A previous local render reported **13 pages**; final journal/school page layout and source-to-figure visual review are still pending.
- **DOCX SHA-256:** `c2b64c4e9eb19f9da9f9fdcd431b3255cf99be55256299c40dfbc32ac56e457d` (local uploaded file `Manuscript_Draft(1).docx`, 551,763 bytes). This identifies the manuscript read at this checkpoint.
- **Storage boundary:** The binary Word file was provided as a conversation attachment, **not uploaded to this public GitHub repository**. Its content must not be assumed recoverable from this checkpoint alone. To continue editing its layout or prose in a fresh environment, locate the conversation attachment or obtain the exact DOCX; compare its SHA-256 before claiming it is the same version.

The Google Doc [79_Muhammad Wahid Hisyam](https://docs.google.com/document/d/1rTafCdT6ESCpH43HtrssArHpiUzVEhoYABzwQJewQ00/edit) has four tabs (RESEARCH PLAN, TARGET JOURNALS AND READING SOURCES, IMRAD, ARTICLE). Its **ARTICLE tab is an earlier working draft**, not a verified copy of this full Word manuscript. The prior bibliography/source audit deliberately did not overwrite ARTICLE. **No Google Doc edits were made for this GitHub checkpoint.**

## 2. Frozen numerical results — unchanged

The analysis is an independent descriptive secondary analysis of the **2024 ATLAS Z+jets OmniFold Zenodo HDF5 release**, [DOI 10.5281/zenodo.11507450](https://doi.org/10.5281/zenodo.11507450), **not** the different 2026 CERN Open Data release. The generator-defined normalized four-cell selection remains **leading charged-jet pT > 5 GeV**, **mass < 10.594606399536133 GeV** for the low-mass category, and **charged-constituent count < 11** for the low-multiplicity category; cells are **LL/LH/HL/HH, mass first**.

Observed unfolded-minus-reference contrasts:

| Summary | Real vs shared generator | Pseudodata vs independent known truth |
| --- | ---: | ---: |
| Mass-low marginal | +0.0036800854 | -0.0229756608 |
| Leading-jet multiplicity-low marginal | -0.0146902523 | -0.0019636003 |
| Joint log-odds | -0.0597334776 | +0.0522361448 |

Real DD/Sherpa correlation-scenario **model-conditional** log-odds standard errors span **0.092321–0.146783**, not an experimentally calibrated confidence interval. Frozen source of truth: [five CSV tables, four SVG figures, numerical manifest](../results/four-cell-v1/README.md); [CI 42442490666](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42442490666) reported **107 passing tests** for the numerical code; no numerical code or generated results were changed to create this manuscript checkpoint.

The research gate status is unchanged: **G5 provisional; G8 physical repeated-unfolding coverage unverified; G11 one known-target pseudodata comparison executed; G12 an accepted 2D correlation prescription unverified; G15 NO-GO**. **Never** describe the current numbers as a calibrated real-data p-value, significance, official ATLAS 2D covariance, or a generator acceptance/rejection conclusion.

## 3. Reconciled milestone status

| Workstream | Current evidence-based state |
| --- | --- |
| B00 scope, RQs and scientific nonclaims | DONE |
| B01 four-tab school document reconciliation | DONE as working material; independent adviser acceptance outstanding |
| B02 numerical reproduction / source-backed figures | DONE — checksum-pinned bundle and prior 107-test CI |
| B03 source/bibliography and bounded novelty audit | DOI/claim checks and 12 candidate school entries DONE; **Zotero generation, citation reconciliation and journal policies pending** |
| B04 full manuscript | **Standalone DOCX DRAFT PRODUCED**; Google Doc integration, figure/table and submission-format visual QA, final scientific edits pending |
| B05 independent reviewer/adviser assessment | PENDING |
| B06 inferential generator test | BLOCKED / OUT OF CURRENT DESCRIPTIVE SCOPE |
| B07 school submission and presentation | PENDING |
| B08 handoff | Manuscript milestone recorded in GitHub; final archived manuscript/submission audit PENDING |

The Word draft has **three** numerical tables, even though an earlier blueprint checklist referred to **four**. This is a *checklist mismatch*, not evidence of a missing fourth analysis table. Assess actual reporting needs with the adviser; do not insert a redundant table solely to satisfy an outdated count.

## 4. Next specific actions

1. Independently review the Word draft against [`results/four-cell-v1`](../results/four-cell-v1/README.md): every number, comparator, table and caption must trace to the frozen CSV/figure and source notes.
2. Obtain adviser feedback on whether a descriptive student reproducibility/secondary analysis satisfies the KTI's goals, and on the scientific novelty and source-assumption wording.
3. Complete Zotero import/output and a bidirectional citation–reference check. The repository's [13-paper DOI and novelty audit](KTI_BIBLIOGRAPHY_AND_NOVELTY_AUDIT_2026_11_08.md) is a verification basis, **not a finalized Zotero library**.
4. Resolve author/affiliation, acknowledgments, contributions, funding, conflicts, licensing/attribution, AI-assistance declaration and actual school/journal requirements.
5. Visually inspect the final exported document page by page. Confirm all **four** figures and the required tables have captions, legible labels, correct references, appropriate placement and traceable provenance.
6. Integrate the full draft into the Google Doc ARTICLE tab **only when the user authorizes that edit**; preserve the original school's tabs and template structure. Retain revision history and avoid silently overwriting the draft.
7. Verify candidate venues from official scope/indexing/fee policies and obtain author/adviser sign-off before any public submission. Do not imply publication is assured.

## 5. Resume / priority instructions

First read [master handoff](START_HERE_HANDOFF.md), the [canonical scope blueprint](../plans/KTI_DESCRIPTIVE_SCOPE_BLUEPRINT_2026_11_08.md), this checkpoint, and the [fixed evidence bundle](../results/four-cell-v1/README.md). **Work on manuscript review and submission readiness, not fresh large-scale extraction or an uncalibrated p-value.** If the Word attachment is unavailable, state that constraint and request the exact document rather than treating the older Google Doc ARTICLE as identical.

**Verification for this checkpoint:** manuscript inventory and SHA were checked locally; numerical results, repo source and prior CI were inspected. GitHub changes here are documentation only; **no fresh CI success is claimed**.
