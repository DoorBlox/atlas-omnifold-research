# Research execution workflow

**Current study:** the reproducible four-cell projection of leading charged-jet mass and multiplicity from the 2024 ATLAS Z+jets OmniFold release. This adapts ORBIT's bounded execution/checkpoint pattern to scientific source traceability.

## Work-unit contract

Every research task must specify: **RQ and precise estimand → source data and hashes → event selection → comparator → assumptions → computation → expected table/figure → acceptance checks → claim scope → reviewer/next decision**. Keep numerical verification and experimental validity as separate gates.

## Frozen v1 definition

ATLAS 2024 [paper](https://doi.org/10.1103/PhysRevLett.133.261803) and [Zenodo weights](https://doi.org/10.5281/zenodo.11507450); selection `pT_trackj1 > 5 GeV`, mass threshold `10.594606399536133 GeV`, multiplicity `11`, four cells LL/LH/HL/HH. Normalized fractions sum to one. Real unfolded vs **paired shared-event nominal generator**; unfolded pseudodata vs **independent known truth**. Four predeclared DD/Sherpa within-source correlation scenarios are **conditional sensitivity** results.

## Reproducibility ladder

1. Verify frozen [v1](../data/derived/phase7-v1) and [v2](../data/derived/phase7-v2) moments, published 2024 data DOI, input manifests and run IDs.
2. Reconstruct four-cell fractions, low marginals, log odds and binary-indicator covariance D; separate **cell differences** from marginal sums.
3. Inspect source covariance and normalized 4×4 rank-three structure, R−1 replica convention, network ensemble-of-mean scaling, shared-event paired moments and independent truth precision.
4. Apply fixed DD/Sherpa assumptions and record conditional SEs with the source-variance breakdown.
5. Run relevant [source tests](../tests/test_phase7_kti_bundle.py) and [CI](../.github/workflows/atlas-phase7-lite.yml) on the actual changed PR head. The [version-one numerical release](../results/four-cell-v1/README.md) holds five CSV tables, four SVGs and SHA-256 manifest. Preserve the release bytes.

**Scientific gates:** G5 PROVISIONAL, G8 UNVERIFIED physical repeated-unfolding coverage, G11 ONE target check, G12 UNVERIFIED validated 2D correlation, **G15 NO-GO** calibrated significance/generator acceptance. Passing software tests or conditional toy checks never closes these gates.

## New analysis and reporting

A materially different selection, comparator, statistic, covariance input or figure source deserves a new versioned release with a documented delta, independent checks and updated manifest. Explain source-to-claim support for every new statement; use the author's selected manuscript only when asked to edit it. Human scientific approval is recorded in [DECISIONS](DECISIONS.md) and [ISSUE_REGISTER](ISSUE_REGISTER.md), separate from computational completion.

After each bounded work unit, update the [plan](../plans/RESEARCH_PLAN.md), [current state](CURRENT_STATE.md) and the [single short handoff](../CHATGPT_HANDOFF.md); add a dated entry to [history](PROJECT_HISTORY.md) when material. Read [RUNBOOK](RUNBOOK.md) for execution details and historical cautions.
