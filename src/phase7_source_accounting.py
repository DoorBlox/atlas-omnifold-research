"""Reconcile ATLAS paper's 25 systematics with 29 frozen project components.

ATLAS PRL 133 (2024) 261803 describes 25 systematic components.
Our frozen 2x2 manifest has 25 *systematic-labelled* components plus four
stochastic components (finite evaluation MC, data/MC bootstrap, NN ensemble).
The public 1D pseudodata chi-square example uses only 15 of the 29 entries.
This arithmetic is NOT proof of one-to-one official source identity, a 2D
covariance prescription, an inferential null or detector-level coverage.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Mapping

import numpy as np

from src.phase7_calibration import manifest_replica_counts
from src.phase7_joint_reference import validate_covariance
from src.phase7_reference_audit import PSEUDO_1D_FAMILIES
from src.phase7_v2_reconstruct import SYST

STOCHASTIC_SOURCES = frozenset({
    "finite_evaluation_mc", "data_bootstrap",
    "mc_training_bootstrap", "nn_ensemble",
})
STOCHASTIC_FAMILIES = {
    "finite_evaluation_mc": "evaluation_MC_stat",
    "data_bootstrap": "replica_family",
    "mc_training_bootstrap": "replica_family",
    "nn_ensemble": "replica_family",
}
SPECIAL_SYSTEMATIC_FAMILIES = {
    "dd_unfolding": "two_point_dd_provisional",
    "sherpa_hidden_variable": "independent_alternative_provisional",
    "nonDY": "independent_alternative_provisional",
}
EXPECTED_SYSTEMATICS = frozenset(SYST) | frozenset(SPECIAL_SYSTEMATIC_FAMILIES)
EXPECTED_ALL = EXPECTED_SYSTEMATICS | STOCHASTIC_SOURCES


def read_manifest(path: Path) -> dict[str, str]:
    """Read and fail closed on missing, duplicate, or retaxonomized sources."""
    with Path(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != ["source", "family", "input"]:
            raise ValueError("Unexpected source manifest columns")
        rows = list(reader)
    sources: dict[str, str] = {}
    for row in rows:
        source = (row["source"] or "").strip()
        family = (row["family"] or "").strip()
        if not source or not family or not (row["input"] or "").strip():
            raise ValueError("Missing source, family or input in manifest")
        if source in sources:
            raise ValueError(f"Duplicate source in manifest: {source}")
        if source in STOCHASTIC_FAMILIES:
            expected = STOCHASTIC_FAMILIES[source]
        elif source in SPECIAL_SYSTEMATIC_FAMILIES:
            expected = SPECIAL_SYSTEMATIC_FAMILIES[source]
        elif source in SYST:
            expected = "one_shift_nuisance"
        else:
            raise ValueError(f"Unknown source family: {source}")
        if family != expected:
            raise ValueError(f"Incorrect family for {source}: expected {expected}, got {family}")
        sources[source] = family
    if set(sources) != EXPECTED_ALL or len(sources) != 29 or len(set(sources) - STOCHASTIC_SOURCES) != 25:
        missing = sorted(EXPECTED_ALL - set(sources))
        extra = sorted(set(sources) - EXPECTED_ALL)
        raise ValueError(f"Expected 29 total = 25 systematic + 4 stochastic; Missing={missing}; extra={extra}")
    if len(PSEUDO_1D_FAMILIES) != 15 or not set(PSEUDO_1D_FAMILIES) <= set(sources):
        raise ValueError("Official 1D example's 15 source names no longer match the frozen manifest")
    if set(PSEUDO_1D_FAMILIES) & STOCHASTIC_SOURCES != STOCHASTIC_SOURCES:
        raise ValueError("Official 1D example must retain all four stochastic source names")
    return sources


def audit_components(components: Mapping[str, np.ndarray], manifest: Mapping[str, str]) -> dict:
    """Compare source *inclusion* and trace, never infer official 2D equivalence."""
    if set(components) != set(manifest):
        raise ValueError(f"Missing or extra source covariance mismatch: "
                         f"missing={sorted(set(manifest)-set(components))}, "
                         f"extra={sorted(set(components)-set(manifest))}")
    traces: dict[str, float] = {}
    for name in manifest:
        try:
            matrix = validate_covariance(components[name])
        except ValueError as exc:
            raise ValueError(f"Source {name}: invalid PSD/normalization covariance: {exc}") from exc
        trace = float(np.trace(matrix))
        if trace < -1e-14:
            raise ValueError(f"Source {name}: negative covariance trace")
        traces[name] = trace
    full = float(sum(traces.values()))
    subset = float(sum(traces[name] for name in PSEUDO_1D_FAMILIES))
    omitted = sorted(set(manifest) - set(PSEUDO_1D_FAMILIES))
    excluded = float(sum(traces[name] for name in omitted))
    if full <= 0 or subset <= 0 or excluded <= 0 or not np.isclose(subset + excluded, full, rtol=1e-12, atol=1e-18):
        raise ValueError("Non-positive or inconsistent source trace partition")
    return {
        "source_counts": {
            "all_project_components": len(manifest),
            "paper_systematic_count_arithmetic": len(set(manifest) - STOCHASTIC_SOURCES),
            "stochastic_components": len(STOCHASTIC_SOURCES),
            "pseudo_notebook_1d_included_components": len(PSEUDO_1D_FAMILIES),
            "pseudo_notebook_1d_omitted_systematics": len(omitted),
        },
        "stochastic_source_names": sorted(STOCHASTIC_SOURCES),
        "systematic_source_names": sorted(set(manifest) - STOCHASTIC_SOURCES),
        "pseudo_notebook_1d_included_names": list(PSEUDO_1D_FAMILIES),
        "pseudo_notebook_1d_omitted_names": omitted,
        "all_project_trace": full,
        "pseudo_notebook_1d_included_trace": subset,
        "pseudo_notebook_1d_excluded_trace": excluded,
        "pseudo_notebook_1d_trace_share": subset / full,
        "exact_paper_to_project_systematic_mapping_verified": False,
        "official_2d_covariance_prescription_verified": False,
        "G12": "FAMILY_INCLUSION_SENSITIVITY_ONLY",
    }


def run(real_dir: Path, pseudo_dir: Path, out: Path) -> dict:
    """Read checksum-pinned four-cell products; no event data or new toys."""
    from src.phase7_snapshot import verify as verify_v1

    real_dir, pseudo_dir, out = Path(real_dir), Path(pseudo_dir), Path(out)
    if real_dir.parent != pseudo_dir.parent or real_dir.name != "real" or pseudo_dir.name != "pseudo":
        raise ValueError("Expected paired real/pseudo directories under one frozen v1 root")
    verify_v1(real_dir.parent)
    samples = {}
    manifests = {}
    expected_replicas = {
        "pseudo": {"data_bootstrap": 25, "mc_training_bootstrap": 25, "nn_ensemble": 100},
        "real": {"data_bootstrap": 100, "mc_training_bootstrap": 25, "nn_ensemble": 100},
    }
    for kind, directory, prefix in (
        ("pseudo", pseudo_dir, "pseudo_"),
        ("real", real_dir, ""),
    ):
        manifest_path = directory / f"{prefix}source_manifest.csv"
        manifest = read_manifest(manifest_path)
        counts = manifest_replica_counts(manifest_path)
        if counts != expected_replicas[kind]:
            raise ValueError(f"Frozen {kind} replica manifest count drift: {counts}")
        with np.load(directory / f"{prefix}source_covariances.npz", allow_pickle=False) as matrices:
            audit = audit_components({name: matrices[name] for name in matrices.files}, manifest)
        audit["replica_counts"] = counts
        samples[kind] = audit
        manifests[kind] = manifest
    if manifests["pseudo"] != manifests["real"]:
        raise ValueError("Real/pseudodata source taxonomy differs")
    result = {
        "status": "PAPER_25_SYSTEMATICS_PLUS_FOUR_STOCHASTIC_PROJECT_TERMS_RECONCILED",
        "scope": "Source-count and 1D notebook family-inclusion audit on frozen 4x4 normalized 2x2 source matrices",
        "primary_paper": "https://doi.org/10.1103/PhysRevLett.133.261803",
        "official_1d_example": "2_pseudo_results.ipynb cell 26, not a normalized 2D prescription",
        "count_interpretation": (
            "Paper: 25 systematic components. Project manifest: 25 systematic-labelled "
            "source terms plus 4 stochastic terms = 29 matrices. The 1D example selects "
            "15 project source names (4 stochastic + 11 systematic), omitting 14 systematic "
            "names. Exact physical one-to-one mapping to ATLAS's 25 is not independently proven."
        ),
        "samples": samples,
        "G5": "PROVISIONAL",
        "G8": "UNVERIFIED_PHYSICAL_COVERAGE",
        "G12": "UNVERIFIED_2D_SOURCE_CORRELATIONS",
        "G15": "NO_GO",
        "inference_permission": "NO_GO",
    }
    out.mkdir(parents=True, exist_ok=True)
    (out / "source_family_accounting.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--real-dir", type=Path, default=Path("data/derived/phase7-v1/real"))
    parser.add_argument("--pseudo-dir", type=Path, default=Path("data/derived/phase7-v1/pseudo"))
    parser.add_argument("--out", type=Path, default=Path("outputs/source-accounting"))
    args = parser.parse_args()
    result = run(args.real_dir, args.pseudo_dir, args.out)
    print(json.dumps({
        "status": result["status"],
        "samples": {kind: {
            "source_counts": audit["source_counts"],
            "pseudo_notebook_1d_trace_share": audit["pseudo_notebook_1d_trace_share"],
            "replica_counts": audit["replica_counts"],
        } for kind, audit in result["samples"].items()},
        "G15": result["G15"],
    }, indent=2))


if __name__ == "__main__":
    main()
