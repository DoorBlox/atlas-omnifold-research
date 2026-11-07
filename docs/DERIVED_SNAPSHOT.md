# Frozen, lossless Phase 7 summary snapshot — no repeated 3.65 GB downloads

**Status:** The one-time archival workflow at `.github/workflows/archive-phase7.yml` populates `data/derived/phase7-v1/`. Verify a successful archival run before relying on the folder.

This snapshot freezes the **existing, already executed** official ATLAS *four-cell* results, without introducing new physics choices or recalculating weights. It is not a copy of the ATLAS event-level dataset. It stores the **exact original bytes**, including the NumPy-compressed `.npz` source covariance matrices, `.npy` total covariance, sample manifests, normalized four-cell CSVs, the generator bin thresholds and the original scientific status JSONs.

- Official ATLAS data DOI: `10.5281/zenodo.11507450` (archive MD5 `9b838510f41e1d5a8b26d7f3c5b2ca42`).
- Real source: GitHub run [42324639484](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42324639484), artifact `phase7-preflight-12`.
- Pseudodata source: run [42327464929](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42327464929), artifact `phase7-preflight-17`.
- Each of the **12 retained files** is pinned to a SHA-256 checksum computed from the corresponding original artifact. `provenance.json` records the pinned file digests, runs, DOI and original archive MD5.
- The raw HDF5 event data, complete original ZIP, `schema_preflight.json`, and unnecessary event columns are **not** retained. All retained files have an enforced 64 KiB per-file maximum.

## Cheap analyses using the permanent snapshot

For archived 2×2 bins, analysis needing only the 29 matrices and summary fractions can run with **no Zenodo download and no GitHub artifact download**. Once archived, verify and use:

```bash
python -m src.phase7_snapshot verify --root data/derived/phase7-v1
python -m src.phase7_model_sensitivity --real-dir data/derived/phase7-v1/real --pseudo-dir data/derived/phase7-v1/pseudo --out outputs
python -m src.phase7_reference_audit --real-dir data/derived/phase7-v1/real --pseudo-dir data/derived/phase7-v1/pseudo --out outputs
python -m src.phase7_calibration --real-dir data/derived/phase7-v1/real --pseudo-dir data/derived/phase7-v1/pseudo --out outputs --toys 10000
```

### What this snapshot **cannot** support

These matrices are **not sufficient for every future question**. In particular, frozen matrices **cannot** exactly reconstruct arbitrary event selections, new bin boundaries, raw per-event or per-bin **variation weight sums**, alternative density smoothing or a new unfolding fit. For these, the event-level original archive or a new, separately verified, versioned per-cell histogram extraction is necessary. Do not reconstruct missing signed systematic shifts from outer products by guessing a sign. A new source-correlation model applied to these provisional matrices remains **provisional**; persistence does not validate their modelling.

The original public ATLAS data must be credited, and no restricted/unlicensed event-level records should be copied into the repository. Do not overwrite `phase7-v1`: future improved analyses should use a new `phase7-v2` with its own provenance and gate documentation.

**Scientific gate:** **G15 NO-GO**. A cache hit or verified checksum is a computational-integrity result, not a statistical-inference endorsement.

## Independent no-download equivalence check (verified)

Two successfully executed GitHub Actions runs were compared file-by-file:

- Before snapshot: [run 42328332652](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42328332652), artifact `phase7-preflight-21`, based on historical downloaded artifacts.
- After snapshot: [run 42380984689](https://github.com/DoorBlox/atlas-omnifold-research/actions/runs/42380984689), artifact `phase7-preflight-35`, using **only** checksum-pinned `data/derived/phase7-v1` committed files.

**All four generated output files are byte-for-byte identical**, not merely numerically close:

| Output file | SHA-256 (both runs) |
|---|---|
| `model_sensitivity.csv` | `ce7c6aa745b0f4af67172a6ff207acabaa653ab8a4c08bd6e1a457beb972a951` |
| `model_sensitivity_status.json` | `117e31f02c6f2f342e84585238bd928f86ca6abc448f4d8ed1c9b43d892d0509` |
| `pseudo_source_trace.csv` | `e5f138ecbad7c7aba640eb6580794dc852967630bb681ac845270d33531d4d2d` |
| `real_source_trace.csv` | `d8795a6d3605f1d4763bf8f9e4cc241ccc46cc3602cb526b35e61cdc4a3e4183` |

The no-download run reported **29 passing Python regression tests**. The equivalence test verifies that the optimization did not change the archived analysis's outputs; it **does not** resolve the provisional scientific modelling of DD/Sherpa correlations or permit G15 inference.
