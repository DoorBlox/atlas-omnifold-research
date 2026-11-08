# Research plan and decision boundaries

**Working scope locked 8 November 2026.** This is the stable, forward-looking roadmap. The detailed original 35-kB change blueprint remains archived under its original filename: [KTI_DESCRIPTIVE_SCOPE_BLUEPRINT_2026_11_08.md](KTI_DESCRIPTIVE_SCOPE_BLUEPRINT_2026_11_08.md). This plan supersedes its older to-do status, not its validated numerical evidence.

## Accepted scientific outcome

The present student KTI is a reproducible descriptive secondary analysis of leading charged-jet mass and constituent multiplicity using the 2024 ATLAS 24D OmniFold release. It has **two RQs**, one fixed 2×2 grid, marginal and joint association descriptions, one separately specified known-target pseudodata example, and four explicitly *conditional* DD/Sherpa correlation sensitivity models. There is **no approved calibrated generator p-value** and no official 2D covariance claim.

The selected numerical bundle was already completed on **8 Nov 2026** even though its historical directory says `kti-nov18`. **No November 18 future event, outcome, deadline, acceptance or activity is assumed** from that name.

## Remaining work, in priority order

| Work ID | Owner/review | Task | Completion evidence |
| --- | --- | --- | --- |
| W1 | Analysis + human HEP review | Reconcile the `D`-versus-log-odds algebra with the manuscript's Discussion; decide whether to include the exploratory coordinate check | Correctly reproduced source fractions; reviewer-approved interpretation |
| W2 | Student/adviser | Confirm descriptive KTI meets school's actual novelty, citation and writing criteria | Written adviser decision, documented requirements |
| W3 | Student/editor | Revise scientific prose based on W1; retain all original numerical values and explain conditional uncertainty succinctly | DOCX diff, line-by-line CSV and figure consistency check |
| W4 | Student/Zotero | Verify 14 reference-list entries, each in-text citation, source-to-claim support and legitimate venue formatting | Bidirectional citation inventory and exported Zotero bibliography |
| W5 | Student/adviser | Supply human authorship, affiliation, contributions, funding/conflict, data-license attribution and AI assistance disclosure | Author-approved declarations |
| W6 | Independent reviewer | Review domain novelty, DD/Sherpa assumptions and claim calibration | Signed/acknowledged scientific/editorial review record |
| W7 | Student | Produce submission-format Word/PDF and slides following real school instructions | Visually inspected manuscript and slide package |
| Optional later | Experimental-statistics collaborators | Acquire independent repeated-unfolding ensembles and justify validated 2D systematic correlation if formal generator inference becomes a *new project* | Independent ensemble protocol, evidence for physical null/coverage, source signoff |

W1 may be addressed from existing CSVs. **W2, W5, W6, and W7 require human or external evidence.** They cannot honestly be checked off from this conversation.

## Safety and rollback

Every new empirical quantity must be clearly separated from the released pinned numbers and labeled as derived or exploratory. Do not change `results/kti-nov18`, `data/derived`, the original HDF5 DOI, or the original main inference gate through editing. If a future analysis alters bins or uncertainty assumptions, create a versioned release with tests, provenance and manifest. A writing change never reopens G15 by implication.

Current [research status](../docs/RESEARCH_STATUS.md), [issues](../docs/ISSUE_REGISTER.md), [manuscript review](../docs/MANUSCRIPT_REVIEW.md), [results](../results/README.md).
