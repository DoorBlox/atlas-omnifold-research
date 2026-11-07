"""Reference-aligned bootstrap sample-covariance audit on frozen four-cell ATLAS data.

The historical v1 source matrices use 1/R (population). Independent ATLAS-style
implementations use 1/(R-1) for replica sample covariance. This code applies
the exact R/(R-1) rescaling without rereading event-level data. The primary
CERN source and 2D nuisance model remain unverified; no real-data p-values.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import numpy as np

from src.phase7_snapshot import verify as verify_snapshot

FAMILY_PREFIX = {
    "data_bootstrap": "weights_bootstrap_data",
    "mc_training_bootstrap": "weights_bootstrap_mc",
    "nn_ensemble": "weights_ensemble",
}
CELLS = ("LL", "LH", "HL", "HH")
CONTRAST = np.array([[1., 0., 0., -1.],
                     [0., 1., 0., -1.],
                     [0., 0., 1., -1.]])


def manifest_replica_counts(path: Path) -> dict[str, int]:
    with Path(path).open(newline="", encoding="utf-8") as stream:
        records = list(csv.DictReader(stream))
    counts = {}
    for family, prefix in FAMILY_PREFIX.items():
        rows = [r for r in records if r.get("source") == family]
        if len(rows) != 1 or rows[0].get("family") != "replica_family":
            raise ValueError(f"Expected one declared replica family {family}")
        cols = rows[0]["input"].split(",")
        ids = []
        for col in cols:
            match = re.fullmatch(re.escape(prefix) + r"_(\d+)", col)
            if match is None:
                raise ValueError(f"Unexpected replica name: {col}")
            ids.append(int(match.group(1)))
        if len(ids) < 2 or sorted(ids) != list(range(len(ids))):
            raise ValueError(f"Invalid replica indices for {family}")
        counts[family] = len(ids)
    return counts


def sample_from_population_covariance(
        components: dict[str, np.ndarray],
        counts: dict[str, int],
) -> tuple[dict[str, np.ndarray], dict[str, float]]:
    """Return exact candidate C_sample = C_population * R/(R-1)."""
    if set(counts) != set(FAMILY_PREFIX):
        raise ValueError("Missing/extra replica families")
    if not components or any(f not in components for f in FAMILY_PREFIX):
        raise ValueError("Missing replica covariance source matrices")
    factors = {}
    corrected = {k: np.asarray(v, dtype=float).copy() for k, v in components.items()}
    for name, original in components.items():
        matrix = np.asarray(original, dtype=float)
        if matrix.shape != (4, 4) or not np.isfinite(matrix).all():
            raise ValueError(f"Invalid source covariance {name}")
        if not np.allclose(matrix, matrix.T, atol=1e-12, rtol=1e-10):
            raise ValueError(f"Non-symmetric source {name}")
        if not np.allclose(matrix @ np.ones(4), 0., atol=1e-11):
            raise ValueError(f"Missing normalization null for source {name}")
        if np.linalg.eigvalsh(matrix).min() < -1e-12:
            raise ValueError(f"Non-PSD covariance {name}")
    for family in FAMILY_PREFIX:
        count = counts[family]
        if type(count) is not int or count < 2:
            raise ValueError(f"Invalid replica count: {family}")
        factor = count / (count - 1)
        factors[family] = factor
        corrected[family] *= factor
    for family in set(components) - set(FAMILY_PREFIX):
        np.testing.assert_array_equal(corrected[family], components[family])
    return corrected, factors


def read_shape(path: Path, column: str) -> np.ndarray:
    with Path(path).open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if tuple(r.get("cell") for r in rows) != CELLS:
        raise ValueError("Wrong 2x2 cell order")
    data = np.array([float(r[column]) for r in rows], dtype=float)
    if not np.isfinite(data).all() or np.min(data) < 0 or not np.isclose(data.sum(), 1., atol=1e-8):
        raise ValueError("Invalid normalized four-cell shape")
    return data


def diagnostics(components: dict[str, np.ndarray], measurement: np.ndarray,
                reference: np.ndarray) -> dict:
    cov = np.sum(list(components.values()), axis=0)
    c3 = CONTRAST @ cov @ CONTRAST.T
    eig = np.linalg.eigvalsh(c3)
    if eig[0] <= max(eig[-1], 1e-300) * 1e-10:
        raise ValueError("Rank-deficient contrast covariance")
    z = CONTRAST @ (measurement - reference)
    q = float(z @ np.linalg.solve(c3, z))
    p = measurement
    if (p <= 0).any():
        raise ValueError("Log-odds gradient requires positive cell fractions")
    gradient = np.array([1/p[0], -1/p[1], -1/p[2], 1/p[3]])
    odds_variance = float(gradient @ cov @ gradient)
    if odds_variance < 0:
        raise ValueError("Negative log-odds variance")
    return {
        "uncalibrated_quadratic_not_a_pvalue": q,
        "trace": float(np.trace(cov)),
        "contrast_rank": int(np.linalg.matrix_rank(c3)),
        "condition_number": float(np.linalg.cond(c3)),
        "contrast_eigenvalues": eig.tolist(),
        "log_odds_provisional_se_measurement_only": float(np.sqrt(odds_variance)),
        "normalization_null_residual": float(np.max(np.abs(cov @ np.ones(4)))),
    }


def one_sample(source_dir: Path, kind: str) -> tuple[dict, dict[str, np.ndarray]]:
    if kind not in ("real", "pseudo"):
        raise ValueError("Unknown sample")
    manifest = source_dir / ("source_manifest.csv" if kind == "real" else "pseudo_source_manifest.csv")
    matrix = source_dir / ("source_covariances.npz" if kind == "real" else "pseudo_source_covariances.npz")
    csv_path = source_dir / ("real_2x2_cells.csv" if kind == "real" else "pseudo_closure_cells.csv")
    mcol, rcol = (("unfolded_fraction", "generator_fraction") if kind == "real" else
                  ("pseudo_unfolded_fraction", "independent_target_truth_fraction"))
    counts = manifest_replica_counts(manifest)
    with np.load(matrix, allow_pickle=False) as archive:
        original = {name: archive[name] for name in archive.files}
    if len(original) != 29:
        raise ValueError("Expected 29 archived provisional covariance sources")
    corrected, factors = sample_from_population_covariance(original, counts)
    p, q = read_shape(csv_path, mcol), read_shape(csv_path, rcol)
    orig, new = diagnostics(original, p, q), diagnostics(corrected, p, q)
    if orig["contrast_rank"] != 3 or new["contrast_rank"] != 3:
        raise ValueError("Covariance correction changed contrast support")
    expected_change = sum((factors[k] - 1) * np.trace(original[k]) for k in factors)
    if not np.isclose(new["trace"] - orig["trace"], expected_change, rtol=1e-8, atol=1e-12):
        raise ValueError("Unexpected covariance-trace change")
    report = {
        "sample": kind,
        "source_count": len(original),
        "replica_counts": counts,
        "population_to_sample_factors": factors,
        "original_population_recipe": orig,
        "reference_aligned_sample_recipe_CANDIDATE": new,
        "delta_covariance_trace": float(new["trace"] - orig["trace"]),
        "relative_covariance_trace_change_percent": float(100 * (new["trace"] / orig["trace"] - 1)),
        "scientific_status": "CANDIDATE_SAMPLE_DENOMINATOR_NOT_VALIDATED_OFFICIAL_2D",
        "G15": "NO_GO",
    }
    return report, corrected


def run(snapshot: Path, out: Path) -> dict:
    evidence = verify_snapshot(snapshot)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    result = {
        "status": "EXECUTED_REFERENCE_COVARIANCE_DENOMINATOR_AUDIT",
        "input_provenance": evidence,
        "primary_CERN_helper_verified": False,
        "reference_note": "Independent 1D helper ports use 1/(R-1); this is an unapproved 2D candidate",
        "samples": {},
        "inference_permission": "NO_GO",
        "G5": "UNVERIFIED_UNTIL_PRIMARY_HELPER_AND_2D_PROTOCOL_AUDITED",
        "G8": "MODEL_CONDITIONAL_ONLY",
        "G15": "NO_GO",
    }
    for kind in ("real", "pseudo"):
        item, corrected = one_sample(Path(snapshot) / kind, kind)
        result["samples"][kind] = item
        np.savez_compressed(out / f"{kind}_sample_denominator_candidate.npz", **corrected)
    (out / "divisor_audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--snapshot", type=Path, default=Path("data/derived/phase7-v1"))
    p.add_argument("--out", type=Path, default=Path("outputs"))
    args = p.parse_args()
    result = run(args.snapshot, args.out)
    print(json.dumps({"status": result["status"], "G15": result["G15"],
                      "samples": result["samples"]}, indent=2))


if __name__ == "__main__":
    main()
