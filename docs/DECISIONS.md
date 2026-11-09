# Binding research and writing decisions

**Checked 9 November 2026.** Historical exploratory decisions remain in [HANDOFF_HISTORY](HANDOFF_HISTORY.md). A new scientific or authorial decision must identify its owner, evidence, date and affected files.

| ID | Decision | Why / effect |
| --- | --- | --- |
| R-01 | Current KTI is a two-RQ descriptive secondary study | Full physical 2D source model and null calibration unavailable; formal generator inference deferred |
| R-02 | Use ATLAS 2024 PRL and 2024 Zenodo event-weight release | Correct source attribution; 2026 CERN Open Data set is distinct |
| R-03 | Fix four-cell selection and LL/LH/HL/HH order | Reproducible frozen projected fractions; three independent shape coordinates |
| R-04 | Real vs paired nominal generator; pseudo vs independent truth | Preserve the distinct finite-MC covariance and statistical relationships |
| R-05 | Four DD/Sherpa scenarios are conditional sensitivity | No validated physical coverage or calibrated generator test (G15 NO-GO) |
| R-06 | `results/four-cell-v1` is the canonical release | Stable naming, versioned hashes; historical date-name retained only in migration/history |
| W-01 | Author-selected science-checked equation-formatted DOCX is current | The user rewrote the manuscript and selected this file; previous v0.6 is historical |
| W-02 | One question per paragraph with minimal filler | Preserve authorial language and keep consequential limitations together |
| O-01 | Root ChatGPT handoff + separate state/plan/history | Prevent context loss, stale status and unbounded append-only documentation |
| O-02 | Unpublished manuscript stays private by default | Public GitHub contains source and verified evidence; file hash alone is not backup |

All changes to these decisions require a dated reason, evidence, human authorization when needed and a verification consequence. [ARTIFACT_REGISTRY](ARTIFACT_REGISTRY.md) tracks exact Word versions.
