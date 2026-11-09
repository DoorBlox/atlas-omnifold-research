# Current research, manuscript and verification state

**Checked:** 9 November 2026. [Root handoff](../CHATGPT_HANDOFF.md) holds the immediate next action. The evidence and writing artifacts have **different** custodians and validation gates.

| Track | Status | Authoritative source | Remaining decision |
| --- | --- | --- | --- |
| Numerical analysis | **REPRODUCED, VERSION 1** | [five CSVs, four SVGs and SHA-256 manifest](../results/four-cell-v1/README.md); [generator](../src/phase7_kti_bundle.py) | Freeze v1; version separately if changing analysis |
| Physical covariance/coverage | **PROVISIONAL / UNVERIFIED** | [issue register](ISSUE_REGISTER.md), [joint audit](JOINT_ASSOCIATION_AUDIT.md) | G5/G8/G12 scientific validation required before inference |
| Manuscript | **AUTHOR-SELECTED, EDITORIAL CHECKED** | [artifact registry](ARTIFACT_REGISTRY.md); [manuscript review](MANUSCRIPT_REVIEW.md) | Adviser scientific and author final approval |
| Reference/submission | **IN PROGRESS** | [14 DOI seeds](../references/README.md), [research plan](../plans/RESEARCH_PLAN.md) | Claim checks, Zotero export, declarations, actual venue rules |

**Selected manuscript:** `ATLAS_Four_Cell_Science_Checked_Formatted_Equations.docx`, SHA-256 `e4d3e49b19e0c683bff7340769d4c646f2c1b13791551a941308aeb0182f8e62`. This is the author's own rewrite with science corrections and proper Word equation formatting. Older v0.6 is a **prior draft**. The current DOCX is a private downloadable file, **not committed to GitHub**.

The study uses [ATLAS 2024 data](https://doi.org/10.5281/zenodo.11507450) to describe leading charged-jet mass vs charged multiplicity on an LL/LH/HL/HH grid. Real unfolded comparisons share event support with the nominal generator; the pseudodata truth reference is independent. Recorded differences (unfolded minus reference): real low-mass **+0.0036800854**, low-multiplicity **−0.0146902523**, log odds **−0.0597334776**, covariance `D` **−0.0001685161**; pseudodata **−0.0229756608**, **−0.0019636003**, **+0.0522361448**, **+0.0014603768**, respectively.

**Scientific gates:** G5 PROVISIONAL; G8 UNVERIFIED; G11 ONE known-target pseudodata case; G12 UNVERIFIED; **G15 NO-GO** calibrated real-data generator significance. GitHub [PR #5](https://github.com/DoorBlox/atlas-omnifold-research/pull/5) passed 116 software tests for release migration; that evidence does not validate physical coverage.

**Next:** W4 source/citation audit on exact author file, then W1/W2 adviser scientific/scope review and W5–W7 declarations/independent review/submission. [Plan](../plans/RESEARCH_PLAN.md) · [Issues](ISSUE_REGISTER.md) · [Decisions](DECISIONS.md) · [History](PROJECT_HISTORY.md).
