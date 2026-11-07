# Phase 7 reference covariance audit and corrected bootstrap calibration

**Verified execution:** [GitHub Actions run 42377662887](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42377662887). Artifact `phase7-preflight-32`, ID 13576476538. **25 tests passed in CI.** Both audit and corrected Gaussian-toy scripts completed successfully. Input real covariance: run 42324639484; input official pseudodata closure: run 42327464929.

## Finding A — Source bootstrap replication mismatch corrected

The input source manifests report:

| Replica family | Real ATLAS weighted events | Official pseudodata |
|---|---:|---:|
| Data-bootstrap | **100** | **25** |
| MC-training bootstrap | 25 | 25 |
| Neural-network ensemble | 100 | 100 |

The previous toy calibration run 42331285712 incorrectly assumed **25 data-bootstrap replicas for the real sample**. The source-wise covariance artifacts themselves used the actual saved column families; **this mismatch affected the subsequent Gaussian toy calibration, not the previously reported four-cell central fractions or the original source-wise covariance construction**. The calibration code now reads and validates counts from `source_manifest.csv` and `pseudo_source_manifest.csv`; noncontiguous or duplicate replica indices cause failure.

### Corrected conditional Gaussian null toys

10,000 independent toy trials per scenario; fixed source-wise Gaussian covariance, with replica-family covariance estimated anew for each toy. Non-replica source matrices remain fixed. Reference threshold 7.814727903251179 is the 95th percentile of chi-square with three degrees of freedom.

| Assumed covariance | Known-covariance toy rejection | Plug-in-replica covariance toy rejection |
|---|---:|---:|
| Real ATLAS provisional 2D | 4.60% | **4.60%** |
| Pseudodata provisional 2D | 4.79% | **4.78%** |
| Pseudodata excluding Sherpa (stress-only) | 4.37% | **4.40%** |

The variation in the real simulated rejection fraction compared with the original run reflects both the corrected replica count and a changed simulation random-number sequence. These are **not** measured ATLAS false-positive rates, not validation of detector-level coverage, and do not permit a real-data p-value.

## Finding B — Exact family-inclusion difference from public ATLAS 1D pseudodata notebook

Reference: supplied `2_pseudo_results.ipynb`, statistical comparison cell 26.

This example constructs covariance from:
1. finite evaluation-MC,
2. MC-training and data bootstrap,
3. NN initialization ensemble,
4. theory nuisance family,
5. DD unfolding shift,
6. Sherpa hidden-variable shift (after **1D ordered-bin smoothing**),
7. top-background and non-DY terms.

The one-dimensional example does **not** include the full experimental muon/track/pileup/luminosity family list in its chi-square `v_total`, although another notebook section calculates uncertainties for those groups. Our earlier provisional 2D covariance included all 29 source components.

Reusing the same **provisional** four-cell covariance matrices, but selecting just the 15 component names present in the 1D comparison recipe, yields:

| Uncalibrated contrast quadratic | All 29 prototype components | Restricted 15-family comparison |
|---|---:|---:|
| Real ATLAS vs nominal generator | 1.607910 | 12.437212 |
| Unfolded pseudodata vs known truth | 1.802996 | 3.356626 |

The restricted family accounts for 55.89% of the full real-data covariance trace and 61.73% of pseudodata covariance trace. **This is only a family-inclusion counterfactual**, not a verified 2D reproduction of the official 1D recipe. The public example also uses a conditional decorrelation rule for the DD/HV terms after examining an initial 1D p-value; **such a post-hoc model switch must not be carried into the 2D KTI inference**. ATLAS's 1D Sherpa smoothing does not define a unique analogous two-dimensional smoothing operator. The `multifold_util.fill_cov_matrix` source body was not independently verified in this audit.

## Status / decisions

- G3/G4: nominal-generator frozen bins and four-cell support verified.
- G5: **PROVISIONAL / INCOMPLETE**: full source inclusion, Sherpa smoothing, DD and the 2D correlation model require an a priori justified decision.
- G6: passed numerical rank / conditioning of provisional three-dimensional contrast covariance.
- G8: corrected Gaussian toy **EXECUTED**, ATLAS experimental coverage **UNVERIFIED**.
- G11: single known-target closure executed, repeated coverage **UNVERIFIED**.
- G12: sensitivity demonstrated, validated 2D source-correlation prescription **UNVERIFIED**.
- G15: **NO-GO**, no final generator-compatibility p-value.

The defensible research outcome at this stage is an audited **descriptive 2D comparison with quantified uncertainty-model dependence**, pending source-method justification. Never report the above quadratic numbers as chi-square significance or infer that the generator agrees/disagrees with the data at a specified confidence level.

## Files

- `src/phase7_calibration.py`: reads actual manifest replica counts and executes the conditional Gaussian model.
- `src/phase7_reference_audit.py`: explicitly compares 15 reference-family inclusions against the 29-source provisional 2D system.
- `tests/test_phase7_replica_manifest.py`, `tests/test_phase7_reference_audit.py`: guard against source drift and unsupported inference.
- GitHub Actions workflow stage `audit`: downloads existing small artifacts, runs the reference comparison and corrected toys, and uploads JSON outputs.
