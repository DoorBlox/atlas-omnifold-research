# START HERE — ATLAS OmniFold Z+jets KTI research handoff


## Phase 7 v2: all required frozen-bin signed moments captured (2026-11-07)

**Primary source:** ATLAS 2024 OmniFold dataset DOI [10.5281/zenodo.11507450](https://doi.org/10.5281/zenodo.11507450), original archive MD5 `9b838510f41e1d5a8b26d7f3c5b2ca42`. **[One-time v2 extraction run 42386487963](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42386487963) PASSED.** Its pre-download synthetic and v1 SHA-256 checks passed; it fetched the official 3.65 GB archive once, extracted only **six** relevant HDF5 inputs, omitted the 2.68 GB pseudodata target HDF5 (known truth moments already in v1), and committed **only** `data/derived/phase7-v2/moments.json` (~188 KB) and `provenance.json` (no raw events). V2 records 251 nominal real weight columns, 176 nominal pseudodata weight columns, plus Sherpa/nonDY alternative supports, each with signed per-cell `sum_w`, `sum_w2`, `sum_w_times_mc`, `sum_w_times_nominal`. Both nominal samples exactly reproduce v1's four cell fractions (max difference **0.0**) and 417,401 selected rows.

**[V2 continuity CI run 42388030573](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42388030573) PASSED, 38 regression tests.** Reconstructed **all 29 original source covariances in real and pseudo with max absolute source-matrix error = 0.0**, from signed v2 moments; the v1 byte-pinned snapshot remains immutable. The **real-data conditional shared-event finite-evaluation-MC** candidate joint log-odds SE is **0.09186243**, versus previously reference-fixed **0.09242250**; corresponding real mass-low SE **0.01833270**, track-low SE **0.01162379**. This is **not** a full generator-vs-unfolded covariance or a significance test.

**Primary-method breakthrough:** The paper's [Supplemental User Guide](https://cds.cern.ch/record/2899105/files/2405.20041.pdf?version=5), section 2 item 5, recommends **fully correlated systematics by default** and explicitly describes **four independent nuisance components for a four-bin two-point uncertainty** as an alternative, provided its assumptions are checked on pseudodata before real conclusions. This is stronger source support than our earlier arbitrary Helmert decorrelation, but it does not define a complete approved 2D uncertainty model. Implemented in `src/phase7_twopoint_protocol.py`, with signed DD and Sherpa four-cell count-level shifts propagated via the normalization Jacobian. Four *pre-specified* choices retain all other 29-source components: both full, DD-only four independent, Sherpa-only four independent, both four independent.

**[Two-point protocol CI run 42388258968](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42388258968) PASSED, 43 tests.** Its uncalibrated pseudodata-vs-independent-truth quadratic diagnostics for those four models are respectively **1.79046, 1.74531, 2.14771, 2.56622**; for real data **1.60365, 1.42726, 1.56755, 1.32140**. These are **NOT p-values**, do not select a model based on real-data agreement and do not establish pseudodata frequentist coverage. The first-order normalized-shift Jacobian was cross-checked using exact count normalization on the pinned signed moments: relative nonlinearity **below 1%** for both DD and Sherpa in real and pseudo. See [PHASE7_CORRELATION_PROTOCOL_V2.md](PHASE7_CORRELATION_PROTOCOL_V2.md).

**Updated repository README:** [README.md](../README.md) now links the v2 verified scientific evidence, no-download reproduction and primary publication. **GitHub About/repository description is still empty**: the available GitHub connector can edit files but **cannot perform repo metadata settings writes**. The suggested description for manual entry in GitHub About is: "Reproducible 2D ATLAS OmniFold Z+jets research: joint jet-mass and multiplicity shapes, uncertainty validation, and efficient open-data analysis." Do not claim it is updated.

**Current critical gap:** Although v2 now stores the required *per-cell signed first/second/mixed moments for the frozen bins*, full 2D Sherpa/DD source correlation, true unfolding/systematic cross-correlations, and repeated-sampling null calibration remain open. The exact CERN `multifold_util.fill_cov_matrix` / `smooth_uncertainty` implementation remains inaccessible from our tools; do not invent its behavior. **G5/G8/G12 incomplete and G15 NO-GO**; no validated real-data compatibility p-value or sigma claim.

**Next action for a fresh chat:** use `data/derived/phase7-v2` and the two new CI-tested modules to refine an *a priori* source-correlation model; perform additional pseudodata validation before real-data interpretation. Avoid any further 3.65 GB download for this frozen 2x2 grid. Update this handoff after the next meaningful verified scientific milestone.

---


## Latest finite-MC cross-covariance envelope and CI routing (2026-11-07)

**Verified scientific run:** [42384589187](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42384589187) — **46 tests passed**, frozen 33,594-byte snapshot verified, **no ATLAS archive download**, `src/phase7_crosscov_bounds.py` executed and existing sample-denominator audit completed. The **real-data mass–multiplicity log-odds conditional finite-evaluation-MC** standard-error range is **0.091636–0.094311**, compared with **0.092422** when treating the generator as fixed. The interval uses Cauchy–Schwarz for the **finite-MC cross-covariance only**, with all other provisional source families assumed reference-independent. **This is not a bound on the full real measurement covariance.**

**Verified CI optimization:** [lightweight run 42384751385](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42384751385) — **34 tests passed** with only NumPy/pytest. `.github/workflows/atlas-phase7-lite.yml` now owns derived-only analysis/test changes; the heavy workflow's `on.push.paths` is narrowed to event-level code and explicit triggers. This workflow change incurred one-time verification runs but prevents routine duplicate heavy CI on future derived-source edits. The original `data/derived/phase7-v1` and all real/pseudo central measurements remain unchanged.

**Denominator sensitivity:** changing the prototype replica covariance divisor from `R` to `R-1` (a **candidate**, not independently confirmed in CERN's helper) changes provisional covariance trace by **+0.02676% real** and **+0.05247% pseudo**. Both changes are much smaller than 2D Sherpa/DD source-model dependence. No real-data p-values were calculated.

**Full report:** [PHASE7_SHARED_MC_BOUNDS_AND_CI_OPTIMIZATION.md](PHASE7_SHARED_MC_BOUNDS_AND_CI_OPTIMIZATION.md). **Next:** source-level verification of `multifold_util.fill_cov_matrix` and `smooth_uncertainty`; pre-specified 2D uncertainty model and calibration. If a signed-weight/cross-product extraction is needed, plan a single targeted 3.65 GB source pass into versioned `phase7-v2` **only after fixing the required summaries**. **G15 NO-GO**.

---


## Latest verified no-download methodology advances (2026-11-07)

**Run [42384082085](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42384082085):** 12 regression tests passed on a new **NumPy-only lightweight Actions workflow**; the historical full-data workflow was **skipped**. An independent ATLAS-style reference comparison found that our provisional bootstrap source matrices used population `1/R`, whereas two accessible secondary implementations use sample `1/(R-1)`. The original CERN helper body is still not independently accessible. The algebraic candidate correction uses `R/(R-1)` on the saved matrices and changes the real covariance trace by **+0.02676%** and pseudodata by **+0.05247%**. The original 33,594-byte `phase7-v1` remains immutable. See [PHASE7_REPLICA_DENOMINATOR_AUDIT.md](PHASE7_REPLICA_DENOMINATOR_AUDIT.md); do **not** report corrected candidate matrices as officially validated.

**Run [42384337294](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42384337294):** 16 regression tests passed with no original-data download. [`src/phase7_target_mc.py`](../src/phase7_target_mc.py) now reconstructs the independent pseudodata truth finite-MC covariance from archived four-cell fractions and effective counts and evaluates the target log-odds gradient at **q**, not measurement **p**. Target-only log-odds SE is now **0.001342336** (earlier approximation **0.001415537**), and the independent-target model conditional combined SE is **0.056412160**. See [PHASE7_REFERENCE_MC_COVARIANCE_AUDIT.md](PHASE7_REFERENCE_MC_COVARIANCE_AUDIT.md). This does **not** validate shared-event generator/measurement covariance or full ATLAS coverage.

**Next priority:** independently verify CERN `multifold_util.py` against the secondary-reference sample covariance, lock an **a priori** 2D Sherpa/DD/source-family protocol, then (only if needed) make **one** targeted full-archive pass for signed source-cell sums and shared-event mixed moments. Avoid repeated 3.65 GB downloads. **G5/G8/G12 unresolved; G15 NO-GO.**

---


## Latest verified scientific progress — separate marginals vs joint association (2026-11-07)

**GitHub Actions [run 42383898975](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42383898975) PASSED, with 33 regression tests**, checksum-pinned derived snapshot verification and the new `src/phase7_interaction.py` stage. No original ATLAS download or old Actions-artifact retrieval. See [PHASE7_ASSOCIATION_DECOMPOSITION.md](PHASE7_ASSOCIATION_DECOMPOSITION.md).

The diagnostic separates low-mass and low-multiplicity fractions from the joint **log odds ratio**, using the **provisional** 29-source measurement covariance and *fixed* generator/target reference. Real unfolded minus generator log odds = **-0.05973348** (provisional measurement-only SE **0.09242250**); pseudodata minus target = **+0.05223614** (provisional measurement-only SE **0.05639619**). The Sherpa hidden-variable covariance term accounts for **94.86%** (real) and **87.93%** (pseudodata) of the *modelled joint-association variance*. This is a **variance decomposition, not a significance test**. Sherpa/DD 2D treatment still has no independently verified official prescription; **G15 NO-GO**.

**Further no-download feasibility finding:** [PHASE7_REFERENCE_MC_COVARIANCE_AUDIT.md](PHASE7_REFERENCE_MC_COVARIANCE_AUDIT.md) derives independent known-target finite-MC shape covariance from the existing four cell fractions and effective counts, verified algebraically with 100 synthetic weighted samples. Its contribution to the provisional pseudodata log-odds difference variance is **~0.05662%** under the stated independent-target model. However, real nominal generator and unfolded weights share event support. A future *unconditional* comparison requires their per-cell cross-product moment `sum(weight_mc * weights_nominal)`, **not saved in v1**. Do not add nominal-generator covariance as if it were independent.

**Next priority:** independently obtain exact official CERN `multifold_util.py` helper definitions or specify a defensible a priori two-dimensional source-correlation protocol. Only then plan **one** targeted v2 count-moment/sign-preserving extraction if necessary. Do **not** download 3.65 GB for current snapshot-based diagnostics. G5/G8/G12 remain unresolved and G15 stays **NO-GO**.

---


## Latest optimization milestone — permanent derived results (2026-11-07)

**Verified:** [one-time archival CI 42380892986](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42380892986) committed `data/derived/phase7-v1/`, preserving **33,594 bytes** in 12 original four-cell result files with pinned SHA-256 hashes, both covariance `.npz` archives, signed source *covariance matrices* (not raw shifts), real/pseudo cell summaries, original uncertainty manifests and provenance. No raw HDF5 data were copied. This survives the original Actions artifact expiration. The default analysis pipeline now calls `python -m src.phase7_snapshot verify` against **local committed files**, with no Zenodo or GitHub artifact download for `sensitivity`, `calibration`, or `audit`.

**Independent confirmation:** [zero-download sensitivity CI run 42380984689](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42380984689) succeeded: **29 Python tests passed**, checksum verification passed and all nine model sensitivity scenarios executed. These are provisional statistical diagnostics; **G15 NO-GO** is unchanged.

**New method audit:** [PHASE7_NOTEBOOK_METHOD_RECONCILIATION.md](PHASE7_NOTEBOOK_METHOD_RECONCILIATION.md) maps line-by-line official `2_pseudo_results.ipynb` cell 26 formulas to our normalized 2x2 extension. The external CERN GitLab helper bodies `fill_cov_matrix` / `smooth_uncertainty` remain inaccessible and **unverified**; do not present our 2D covariance recipe as official. For signed per-cell variations or new selection/binning, the current summary is insufficient; plan a **single additional targeted original-data extraction**, only after deciding required fields. See [DERIVED_SNAPSHOT.md](DERIVED_SNAPSHOT.md).

**Next action for the new assistant:** confirm new HEAD and CI on GitHub, read the two new documents, and continue obtaining/verifying official `multifold_util.py` or designing a defensible pre-specified source-correlation 2D treatment. **Do not repeat the 3.65 GB archive download** merely to rerun existing covariance sensitivity or toy calibration.

---


**Checkpoint date:** 2026-11-07 (Asia/Jakarta).  
**Purpose:** preserve the complete actionable project context if the original ChatGPT conversation reaches its context/length limit. Read this before editing or making physics claims.  
**Repository:** https://github.com/DoorBlox/atlas-omnifold-research — branch `main`, GitHub account **DoorBlox**.  
**Important access note:** GitHub reported this repository as **public** when this handoff was written. Do not add private data, tokens, or unlicensed data.  
**Source of truth:** current GitHub source files and completed Actions artifacts outrank this static handoff; check for newer commits and successful runs when resuming.  
**Current scientific gate:** **G15 = NO-GO. Do not report a real-data generator-compatibility p-value, sigma significance, exclusion, or calibrated confidence level.**

## 1. What the user wants

The user is conducting a reproducible KTI (scientific research) study based on the official ATLAS 2024 OmniFold unfolded Z+jets dataset. The working research task is a **joint two-dimensional charged-jet mass × charged-track multiplicity shape comparison** of the unfolded real ATLAS measurement with the nominal MadGraph5_aMC@NLO+Pythia8 generator. This is a 2×2 four-cell downstream analysis, not a new unfolding training run, event classifier, or discovery claim.

The user prefers the assistant to **execute GitHub code changes and inspect CI logs autonomously**, without repeatedly requesting manual screenshots or run links. We have GitHub connector access to the **DoorBlox** account. On the available connector, there is no direct workflow dispatch or listing of push runs. A safe way to initiate a run is to commit a specially tagged file change; after the job finishes it posts its run URL to [issue #1](https://github.com/DoorBlox/atlas-omnifold-research/issues/1). Look up the **specific run** with the connector's `fetch_workflow_run_jobs`, `fetch_workflow_job_logs`, `fetch_workflow_run_artifacts`, and `download_workflow_artifact`. Do not infer success from a legacy commit status of `statuses: []`.

**Research integrity:** favor a defensible descriptive, covariance-aware KTI over an unjustified p-value. Do not pick uncertainty treatments after looking at which agrees better with the data.

## 2. Official sources and frozen analysis design

- Official paper: DOI **10.1103/PhysRevLett.133.261803**.
- Official public archive: **10.5281/zenodo.11507450**; https://zenodo.org/records/11507450
- Download URL used by CI: `https://zenodo.org/records/11507450/files/files.zip?download=1`
- Verified archive size: **3,648,703,812 bytes**.
- Verified official archive MD5: `9b838510f41e1d5a8b26d7f3c5b2ca42`.
- Fiducial selection: `pT_trackj1 > 5 GeV` (417,401 selected nominal event rows).
- Fixed boundaries derived **only from the nominal generator weighted distribution**, never optimized on real-data agreement: mass **10.594606399536133 GeV** and charged multiplicity **11 tracks**.
- Four ordered cells: **LL**: mass < threshold, N <= 11; **LH**: mass < threshold, N > 11; **HL**: mass >= threshold, N <= 11; **HH**: mass >= threshold, N > 11.
- Normalize each measurement, generator, nuisance-variation, and truth distribution independently to unit four-cell sum before a shape comparison. The resulting four-cell covariance has a normalization-null direction; analyze three independent contrasts.
- Nominal real `files/data/multifold.h5`, pseudodata `files/pseudodata/multifold.h5`; alternative-support Sherpa/non-DY HDF5 datasets; independent pseudodata `files/pseudodata/target.h5`.
- Nominal generator weight `weight_mc`; unfolded measurement/pseudodata `weights_nominal`. The **known pseudodata truth** is the `target.h5` `weight_mc`, **not** `weights_nominal`.
- Do not quietly drop negative mass observations from the selected support. No optimization of thresholds after seeing real differences.

## 3. Executed results — verified, but descriptive

### 3.1 Real ATLAS 2×2 central fractions

Verified via [Actions run 42324639484](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42324639484), artifact `phase7-preflight-12` (artifact ID 13555355269); see [actual-data checkpoint](PHASE7_ACTUAL_DATA_CHECKPOINT.md).

| Cell | Selected raw rows | Generator fraction | Unfolded real fraction | Unfolded - generator |
|---|---:|---:|---:|---:|
| LL | 130,852 | 0.434162588 | 0.428715216 | -0.005447371 |
| LH | 20,175 | 0.065835988 | 0.074963445 | +0.009127457 |
| HL | 62,569 | 0.141995627 | 0.132752746 | -0.009242881 |
| HH | 203,805 | 0.358005797 | 0.363568593 | +0.005562796 |

All four cells passed implemented nominal-generator `Neff >= 5000` and data-bootstrap relative-precision <15% support gates. The 29-source **provisional** covariance has contrast rank 3, positive definite, condition number **14.7533**, eigenvalues approximately [0.00004244, 0.00020035, 0.00062609]; covariance normalization-null residual approximately 2.7e-19. The dominant trace contributors are main tracking efficiency ~27.99%, Sherpa hidden-variable ~26.58%, DD unfolding ~24.45%. These trace fractions **are not** individual statistical significances.

### 3.2 Official pseudodata known-target projection

Verified via [Actions run 42327464929](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42327464929), artifact `phase7-preflight-17` (ID 13555517492): 417,401 selected pseudodata rows and **23,888,304 selected independent target rows**. Same frozen real-generator thresholds.

Approximate percentages from executed output (precise values in artifact's `pseudo_closure_cells.csv`):

| Cell | Known truth | Unfolded pseudodata | Difference (percentage points) |
|---|---:|---:|---:|
| LL | 44.90% | 43.66% | -1.24 |
| LH | 8.31% | 7.25% | -1.06 |
| HL | 10.97% | 12.01% | +1.04 |
| HH | 35.82% | 37.07% | +1.26 |

Pseudodata provisional contrast rank 3; condition number **58.6007**. A single known-truth projection is **not** repeated-sampling closure/coverage validation. Its original uncalibrated squared Mahalanobis diagnostic is approximately **1.803**, **not a p-value**.

### 3.3 Two-dimensional uncertainty-model sensitivity

Source-family covariance currently has **29 components** (22 named one-shift systematics; three replica families; finite evaluation-MC; DD unfolding; Sherpa hidden-variable; non-DY). The source covariance assumptions for some 2D model alternatives have not been established from the official ATLAS 1D code.

Nine alternative **stress scenarios** (including source omission, source amplitude scaling, and project-defined contrast/Helmert decorrelation) were run using the two archived official-data results. The independently verified GitHub Actions sensitivity run is [42328332652](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42328332652); read [sensitivity checkpoint](PHASE7_MODEL_SENSITIVITY_CHECKPOINT.md).

Selected illustrative **uncalibrated** quadratic statistics:

| Source model | Real ATLAS | Pseudodata |
|---|---:|---:|
| Original provisional full 29-source model | 1.607910 | 1.802996 |
| Both DD and Sherpa contrast-decorrelated stress model | 1.436672 | 2.041870 |
| Sherpa source excluded — **extreme stress only** | 7.004018 | 16.781815 |

Association-only log odds difference, real minus generator: approximately **-0.05973**, with provisional standard error **0.09242**. Pseudodata minus target: approximately **+0.05224**, with provisional standard error **0.05640**. These are descriptive and covariance-model-conditional, not final significance claims.

### 3.4 Most recent independent reference-family audit and corrected toy experiment

**Latest scientifically meaningful verified run at checkpoint:** [42377662887](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42377662887). Artifact `phase7-preflight-32`, ID 13576476538. **25 Python regression tests passed**; both the reference-family audit and the corrected toy calculation steps passed. Canonical detailed note: [PHASE7_REFERENCE_AUDIT_CORRECTED_CALIBRATION.md](PHASE7_REFERENCE_AUDIT_CORRECTED_CALIBRATION.md).

**Correction discovered:** real data have **100** data-bootstrap replicas; pseudodata have **25**. Both have 25 MC-training bootstraps and 100 NN ensemble members. An earlier toy implementation erroneously assumed 25 data-bootstraps for *real data*; the calibration code now obtains counts from the source manifests, validates indices, and fails closed. **The earlier real 5.25% simulation result is SUPERSEDED.** The four-cell fractions and the source-wise covariance construction were not changed by this *toy-only* correction.

10,000 simulated Gaussian toys per scenario, at nominal three-degree-of-freedom chi-square 95th threshold 7.814727903251179:

| Model treated as known | Corrected rejection fraction with re-estimated replica-family covariance |
|---|---:|
| Real ATLAS **provisional** covariance | **4.60%** |
| Pseudodata **provisional** covariance | **4.78%** |
| Pseudodata without Sherpa — stress only | **4.40%** |

This is **model-conditional Gaussian calibration**, not ATLAS detector-level, generator-level, or true repeated-unfolding frequentist coverage. All non-replica source terms stayed fixed in these toys.

**Important reference difference:** the public ATLAS one-dimensional pseudodata chi-square notebook example selects a narrower 15-family covariance subset than our 29-source 2D prototype. On our own saved **provisional 2D** matrices:

| Four-cell uncalibrated statistic | Full 29-source prototype | Restricted 15-family inclusion counterfactual |
|---|---:|---:|
| Real data vs nominal generator | **1.607910** | **12.437212** |
| Pseudodata vs independent target | **1.802996** | **3.356626** |

The 15-family numbers are **not an official ATLAS 2D prescription or a p-value**. The official 1D Sherpa uncertainty includes smoothing along 1D ordered histogram bins, which does not define a unique two-dimensional smoothing rule; the DD 1D shift implementation also needs source-level scrutiny. The `multifold_util.fill_cov_matrix` body has **not** been independently audited. Do not adopt the official 1D notebook's conditional decorrelation choice, which changes source treatment after examining an initial 1D p-value, as a post-hoc 2D decision.

## 4. Research gate register

| Gate | Latest defensible status |
|---|---|
| G3 — nominal generator-only mass/N thresholds | **PASS** using official data |
| G4 — 2×2 support / implemented precision checks | **PASS**, under stated implementation |
| G5 — full source inclusion, source correlation, DD/Sherpa 2D prescription | **PROVISIONAL / BLOCKER** |
| G6 — numerical rank-three positive-definite covariance | **PASS** for provisional matrices |
| G8 — null calibration | **conditional Gaussian toy executed**; actual ATLAS coverage **UNVERIFIED** |
| G11 — known-truth pseudodata check | **single official comparison executed**; repeated-sampling closure/coverage **UNVERIFIED** |
| G12 — correlation-model robustness | **stress sensitivities executed**; official 2D model **UNVERIFIED** |
| G15 — final real-data p-value / significance | **NO-GO** |

**Do not convert any uncalibrated quadratic to a chi-square p-value or infer real-data agreement/disagreement with ATLAS confidence levels.** Shared generator/measurement support and its possible cross-covariance must be considered before interpreting an unconditional comparison. Source inclusion/correlation must be set **a priori**, not based on which statistic is smallest.

## 5. Files and workflow map

### Repository Python source

- `src/atlas_preflight.py` — official download, MD5, selective extraction, HDF5 inventory (downloads ~3.65 GB when needed).
- `src/shape.py` — weighted medians, four cells, fractions, effective counts, contrast matrix.
- `src/projection.py` — nominal generator thresholds and descriptive four-cell weights.
- `src/phase7_covariance.py` — 29-component provisional covariance; real HDF5 streaming.
- `src/phase7_closure.py` — pseudodata known-target projection and original sensitivity scenarios.
- `src/phase7_model_sensitivity.py` — nine no-download alternative model diagnostics from stored artifacts.
- `src/phase7_calibration.py` — **corrected** replica-manifest-aware conditional Gaussian toys.
- `src/phase7_reference_audit.py` — compares official *1D family inclusion* with provisional 2D usage; still not a 2D official model.

### Tests, documentation and GitHub Actions

- `tests/test_*.py` — Python regression suite. Latest verified audit CI: **25 passed**; re-run tests against HEAD before changing code.
- `.github/workflows/atlas-phase7.yml` — stages `smoke`, `schema`, `projection`, `covariance`, `closure`, `sensitivity`, `calibration`, `audit`. On tagged push it selects the requested stage. Default push **runs smoke only**.
- `ops/schema-request.txt` — safe text-only trigger file. To initiate a stage without workflow-dispatch, **update this file with a commit message** containing the exact stage tag: `[atlas-closure]`, `[atlas-covariance]`, `[atlas-sensitivity]`, `[atlas-calibration]` or `[atlas-audit]`. Tag controls which job executes; check the exact steps. Avoid unnecessary repeated multi-GB downloads.
- [GitHub issue #1](https://github.com/DoorBlox/atlas-omnifold-research/issues/1) — the workflow posts run URLs and `job.status` here. Do **not** trust a generic “success” unless the intended stage step completed.
- `docs/RUNBOOK.md` — background runbook, **partly outdated at its beginning**; use this handoff as the current entry point.
- `docs/PHASE7_ACTUAL_DATA_CHECKPOINT.md` — original real 2×2 checkpoint.
- `docs/PHASE7_MODEL_SENSITIVITY_CHECKPOINT.md` — original nine-scenario table and association diagnostics.
- `docs/PHASE7_GAUSSIAN_CALIBRATION_CHECKPOINT.md` — **historical; superseded real toy counts**.
- `docs/PHASE7_REFERENCE_AUDIT_CORRECTED_CALIBRATION.md` — latest verified correction + 15-family contrast.
- `docs/PHASE7_GAUSSIAN_CALIBRATION_CHECKPOINT.md` explicitly links the corrected report.

### Reproduction commands

Run from the repository root with Python 3.11, sufficient disk for heavy stages:

```bash
python -m pip install -r requirements.txt
python -m pytest -q tests
python -m src.atlas_preflight --stage smoke --out outputs
```

Small-artifact sensitivity/audit work does **not** require redownloading ATLAS event files. With authenticated `gh` access to the repository:

```bash
mkdir -p derived_input/real derived_input/pseudo
gh run download 42324639484 --name phase7-preflight-12 --dir derived_input/real
gh run download 42327464929 --name phase7-preflight-17 --dir derived_input/pseudo
python -m src.phase7_model_sensitivity --real-dir derived_input/real --pseudo-dir derived_input/pseudo --out outputs
python -m src.phase7_reference_audit --real-dir derived_input/real --pseudo-dir derived_input/pseudo --out outputs
python -m src.phase7_calibration --real-dir derived_input/real --pseudo-dir derived_input/pseudo --out outputs --toys 10000
```

These commands require the saved artifacts to still exist, and GitHub Actions artifacts have **14-day retention** in this workflow. If they expire, restore saved copies or rerun the relevant stage. The large raw ATLAS archive and HDF5 files are intentionally **not** uploaded as GitHub artifacts or committed. The small output files contain saved covariances, tables and metadata.

## 6. Exact run and artifact provenance

| Purpose | GitHub Actions run | Artifact | Verification |
|---|---|---|---|
| Official archive/schema preflight | 42252529591 | `phase7-preflight-3` | MD5/HDF5 audit succeeded |
| Real four-cell provisional covariance | [42324639484](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42324639484) | `phase7-preflight-12` | 8 tests, covariance step passed |
| Pseudodata known target | [42327464929](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42327464929) | `phase7-preflight-17` | 12 tests, closure step passed |
| Nine source-correlation scenarios | [42328332652](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42328332652) | `phase7-preflight-21` | sensitivity step passed |
| **Superseded** toy calibration | [42331285712](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42331285712) | `phase7-preflight-25` | 19 tests; real replica count wrong |
| **Current** reference audit + corrected 10k toys | [42377662887](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42377662887) | `phase7-preflight-32` | **25 tests**, both scientific steps passed |

At checkpoint time, latest repository HEAD prior to this handoff was `cd7773d1790aed9de82443a36a7fa67daa683071`. This handoff commit, and any newer commits, supersede that SHA. Check GitHub `main` rather than relying on this static SHA.

## 7. Open scientific questions and prioritized next actions

1. **Highest priority: independently inspect official `multifold_util.py` / notebook covariance helper source**: bootstrap covariance convention, 1D `fill_cov_matrix`, DD treatment, how Sherpa smoothing is defined, full systematic inclusion for real data. Link to exact reference code version/line references and record a method-by-method reconciliation.
2. **Pre-register/lock a defensible 2D covariance protocol** before looking at its resulting physics compatibility statistic: source-family inclusion, effect of a 2×2 table on Sherpa/hidden-variable smoothing, DD count-level versus normalized shift, nuisance correlation and alternative-support assumptions, which terms are conditional-on-generator, and cross-covariances if applicable.
3. Test any model choice against independent pseudodata **without selecting the favorable result post hoc**. If possible design repeated pseudodata/closure experiments and null calibration; clearly distinguish toy-model simulation from full experimental coverage.
4. Add reproducible final result/report generation with provenance and scientific caveats only after gates are satisfied. A **descriptive, uncertainty-model sensitivity KTI** is a valid alternative endpoint if formal inferential gates cannot be met.
5. Maintain data security and cost discipline. Do not commit raw files, tokens or user secrets, and check the present repository visibility (reported public at checkpoint).

### Guardrail for the next assistant

**Never silently transform a source-dependent 1D covariance convention into an “official ATLAS 2D” prescription. Never run an unvalidated real-data p-value. Always inspect CI artifacts, not just a green workflow badge.**

## 8. Copy-and-paste continuation prompt for a fresh ChatGPT chat

> Continue my ATLAS 2024 OmniFold Z+jets KTI in `DoorBlox/atlas-omnifold-research` on the `main` branch. First read `docs/START_HERE_HANDOFF.md` and `docs/PHASE7_REFERENCE_AUDIT_CORRECTED_CALIBRATION.md`, inspect the current `.github/workflows/atlas-phase7.yml` and latest completed GitHub Actions run, and check issue #1 for run IDs. The latest verified audit as of 2026-11-07 was run 42377662887 (25 tests passed); it corrected real vs pseudodata data-bootstrap replica counts to 100 vs 25. Our 2×2 central fractions and provisional covariance are available from run 42324639484, pseudodata closure from 42327464929. G15 is **NO-GO**: no real-data p-value. Please continue with the **official source-level covariance implementation audit** (`multifold_util.fill_cov_matrix`, DD and Sherpa 1D smoothing, and 2D modelling decisions), make independently testable repository changes, run tests, record actual evidence, and update the handoff. Do not ask me to perform GitHub tasks that the connected DoorBlox tools can do. If official source code is unavailable, document exactly which function remains unverified rather than guessing.

---

**Maintenance rule:** at the end of each substantial new milestone, update THIS document's top-level status, last successful run, superseded findings, and next actions. Keep historical evidence in the linked checkpoints. This handoff is a snapshot, not permission to bypass verification.
