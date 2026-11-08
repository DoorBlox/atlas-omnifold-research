# KTI Methods and Results — frozen 2×2 joint shape

**Status: source-backed descriptive secondary analysis, G15 NO-GO.** This is not a calibrated generator-compatibility test.

## Data and prespecified method

We re-used the ATLAS Collaboration's 2024 unbinned Z+jets OmniFold release (PRL 133, 261803; Zenodo DOI 10.5281/zenodo.11507450), via the checksum-verified, four-cell derived snapshots. The selection is pT_trackj1 > 5 GeV; the leading charged-jet mass threshold is 10.5946063995 GeV and charged-track multiplicity threshold is 11. The thresholds were frozen from the nominal generator, not fitted to observed real-data differences. The cell order is LL, LH, HL, HH (mass category first).

For cell weights h_i, we define p_i=h_i/sum_j h_j. The mass-low marginal is p_LL+p_LH, the multiplicity-low marginal is p_LL+p_HL, and joint association is log[(p_LL p_HH)/(p_LH p_HL)]. The association statistic cannot be reconstructed from the two marginals alone. Real unfolded data are compared descriptively to the nominal generator using shared-event paired finite-MC moments; unfolded pseudodata are compared to their independent known target truth.

The conditional 4×4 normalized-shape covariance has a normalization null mode and three independent contrast directions. The source-wise prototype uses the official 1D helper's R−1 replica formula, a project-defined four-cell normalization and signed count-shift Jacobian, with four prespecified DD/Sherpa full-versus-independent-bin assumptions. The 2D nuisance correlations and learned-weight dependencies are not officially validated. The independent target-truth finite-MC term is included for pseudodata, whereas the paired finite-MC term replaces the measurement-only evaluation-MC term in the real comparison.

## Table 1. Actual normalized four-cell fractions

| Sample | Cell | Unfolded | Reference | Difference (percentage points) |
|---|---|---:|---:|---:|
| real | LL | 0.428715 | 0.434163 | -0.5447 |
| real | LH | 0.074963 | 0.065836 | +0.9127 |
| real | HL | 0.132753 | 0.141996 | -0.9243 |
| real | HH | 0.363569 | 0.358006 | +0.5563 |
| pseudo | LL | 0.436624 | 0.448999 | -1.2376 |
| pseudo | LH | 0.072535 | 0.083135 | -1.0600 |
| pseudo | HL | 0.120095 | 0.109683 | +1.0412 |
| pseudo | HH | 0.370746 | 0.358182 | +1.2564 |

The real reference is the nominal generator on shared events. The pseudodata reference is independent known target truth, not the pseudodata nominal generator. Four-cell differences sum to zero.

## Table 2. Marginals and joint association

| Sample | Observable | Unfolded | Reference | Difference | Conditional SE, full/full |
|---|---|---:|---:|---:|---:|
| real | mass_low | 0.503679 | 0.499999 | +0.003680 | 0.018401 |
| real | multiplicity_low | 0.561468 | 0.576158 | -0.014690 | 0.011648 |
| real | joint_log_odds | 2.751272 | 2.811005 | -0.059733 | 0.092321 |
| pseudo | mass_low | 0.509159 | 0.532135 | -0.022976 | 0.019862 |
| pseudo | multiplicity_low | 0.556719 | 0.558682 | -0.001964 | 0.008434 |
| pseudo | joint_log_odds | 2.922239 | 2.870003 | +0.052236 | 0.056651 |

The SE column is **conditional on the provisional full/full DD/Sherpa source model**, with appropriate comparator finite-MC terms. It is not a calibrated experimental uncertainty or a license to quote significance.

## Table 3. Correlation-model sensitivity (not inferential)

| DD/Sherpa assumption | Real log-odds conditional SE | Pseudo log-odds conditional SE |
|---|---:|---:|
| DD full / Sherpa full | 0.092321 | 0.056651 |
| DD four-bin / Sherpa full | 0.106422 | 0.078706 |
| DD full / Sherpa four-bin | 0.136904 | 0.098738 |
| DD four-bin / Sherpa four-bin | 0.146783 | 0.112847 |

The scenario-specific uncalibrated quadratic diagnostics and complete 4×4 covariances are retained in the machine-readable tables. They are **not** converted into a real-data p-value or a generator verdict.

## Table 4. Largest conditional joint-association variance contributors

| Sample | Source | Share of conditional log-odds variance |
|---|---|---:|
| real | sherpa_hidden_variable | 96.02% |
| real | dd_unfolding | 1.03% |
| real | data_bootstrap | 0.85% |
| real | finite_evaluation_mc | 0.53% |
| real | theoryQCD | 0.38% |
| pseudo | sherpa_hidden_variable | 87.85% |
| pseudo | finite_evaluation_mc | 4.17% |
| pseudo | dd_unfolding | 2.76% |
| pseudo | data_bootstrap | 1.44% |
| pseudo | theoryQCD | 1.01% |

The source shares sum to one within each observable, using the appropriate comparator-aware gradient and finite-MC covariance. They describe modeled variance, not probabilities of physical causes.

## Pseudodata validation and limitations

One released unfolded pseudodata sample was compared with its independent known target. This is a **single known-target closure**, not an ensemble of independently retrained pseudo-measurements. The public 1D example selects 15 project-equivalent covariance families, whereas the project's 2D prototype contains 29 (25 systematic-labelled and four stochastic); this is an inclusion-scope difference, not a numerical equality target. The correspondence of all 25 project systematic labels to the 25 published components is not proven one-to-one.

The 2D DD and Sherpa hidden-variable nuisance correlations, the full neural-network training dependence and experimental frequentist coverage remain unverified. Hence **G5 PROVISIONAL, G8 UNVERIFIED, G12 UNVERIFIED, G15 NO-GO**. This work supports descriptive joint-versus-marginal comparisons, not a calibrated generator-compatibility claim.

## Figure captions

**Figure 1:** Four actual normalized mass–multiplicity joint shapes: real unfolded, nominal generator, unfolded pseudodata, and independent target truth.

**Figure 2:** Signed differences of four joint-cell fractions and two derived marginals, in percentage points.

**Figure 3:** Five largest model-conditional joint log-odds variance contributors for each comparison.

**Figure 4:** Conditional log-odds standard-error sensitivity under the four prespecified DD/Sherpa source-correlation models.

## Primary references and reproducibility

- ATLAS Collaboration, *Physical Review Letters* 133, 261803 (2024), https://doi.org/10.1103/PhysRevLett.133.261803
- Official ATLAS release, https://doi.org/10.5281/zenodo.11507450
- Official supplemental User Guide, Section 2, recommendation 5; CERN 1D multifold_util.py source audit documented in the repository.
- Derived snapshot provenance and source-run IDs: data/derived/phase7-v1/provenance.json and data/derived/phase7-v2/provenance.json.
- Rebuild: python -m src.phase7_kti_bundle --v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 --out outputs/four-cell-v1
