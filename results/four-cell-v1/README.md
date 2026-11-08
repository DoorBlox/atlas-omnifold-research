# ATLAS 2024 OmniFold KTI — four-cell descriptive release (v1)

Actual, checksum-verified normalized 2×2 results from frozen ATLAS 2024
derived moments. This is a descriptive secondary analysis, not an
ATLAS-approved 2D covariance model or a calibrated compatibility test.

## Reproduce without downloading the original multi-GB ATLAS archive

    python -m pytest -q tests/test_phase7_kti_bundle.py
    python -m src.phase7_kti_bundle --v1 data/derived/phase7-v1 --v2 data/derived/phase7-v2 --out outputs/four-cell-v1

Inputs: checksum-pinned data/derived/phase7-v1 and phase7-v2.
Output: 5 machine-readable CSV tables, 4 SVG vector figures,
MANUSCRIPT_RESULTS.md, checks.json, results.json and manifest.json.
All output hashes are recorded in manifest.json for exact rebuild comparison.

See MANUSCRIPT_RESULTS.md for all numerical values, captions and limitations.
G5 PROVISIONAL; G8/G12 UNVERIFIED; G15 NO-GO. No real-data p-value.
