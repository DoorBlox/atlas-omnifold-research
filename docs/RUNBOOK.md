# Current ATLAS research reproducibility and recovery runbook

**Use this page for current work.** The former Phase 7 preflight guide is preserved [verbatim](RUNBOOK_PHASE7_HISTORY.md). It includes optional 3.6 GB archive downloads and historical inference work; those steps are unnecessary for current manuscript or documentation tasks. Read [root handoff](../CHATGPT_HANDOFF.md) and [current state](CURRENT_STATE.md) first.

## Check the frozen four-cell release

The canonical release is [`results/four-cell-v1/`](../results/four-cell-v1/README.md), backed by [derived v1](../data/derived/phase7-v1) and [v2](../data/derived/phase7-v2) input moments. Verify/rebuild with:

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests/test_phase7_kti_bundle.py tests/test_joint_association_audit.py
python -m src.phase7_kti_bundle --v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 --out outputs/four-cell-v1
```

This tests numerical consistency and source-dependent covariance arithmetic. Historic [PR #5](https://github.com/DoorBlox/atlas-omnifold-research/pull/5) passed 116 code tests. Recheck live main and CI before citing a result for later changes. Preserve the committed five CSVs, four figures and SHA-256 manifest; a new projection belongs in a **new release version**.

## Validate current documentation

```bash
python scripts/validate_research_docs.py
```

The dependency-free validator verifies active Markdown links, the selected author DOCX hash as metadata, and all 13 permanently pinned release file hashes. The [research-docs-integrity workflow](../.github/workflows/research-docs-integrity.yml) runs this check for relevant PRs. This is a **documentation and byte-integrity test**, not proof of physical covariance or publisher compliance.

## Recover the manuscript

1. Read [ARTIFACT_REGISTRY](ARTIFACT_REGISTRY.md): selected `ATLAS_Four_Cell_Science_Checked_Formatted_Equations.docx` with recorded SHA-256.
2. Locate the **private user-owned** Word file or downloadable private ZIP from the ChatGPT conversation. The public GitHub repository does **not** hold the manuscript's bytes.
3. Check the file hash (for example, `sha256sum filename.docx`) and preserve its original before editing.
4. Use [WRITING_WORKFLOW](WRITING_WORKFLOW.md) to verify paragraph purpose, exact source claims, 3 tables, 4 figures, editable Word equations, citation consistency and actual page rendering.

## Scientific and execution boundaries

**G5 PROVISIONAL, G8 UNVERIFIED, G11 ONE known-target example, G12 UNVERIFIED, G15 NO-GO.** The four DD/Sherpa scenarios are model-conditional. A passing software test cannot establish experimental repeated-unfolding coverage.

Use a full original Zenodo archive extraction only for a justified new source question after checking storage and CI cost. Old preflight commands and historical caveats remain in [RUNBOOK_PHASE7_HISTORY](RUNBOOK_PHASE7_HISTORY.md); original deep-research reports remain in [REPORT_REGISTER](REPORT_REGISTER.md). No invisible background work is implied.
