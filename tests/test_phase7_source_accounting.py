"""Independent regression checks for the paper-25 vs project-29 accounting.

The official one-dimensional notebook selects 15 source terms; neither that
selection nor the paper's 25 systematic components is an approved 2D test.
"""
import csv
import json
from pathlib import Path

import numpy as np
import pytest

from src.phase7_reference_audit import PSEUDO_1D_FAMILIES
from src.phase7_source_accounting import (
    STOCHASTIC_SOURCES, audit_components, read_manifest, run,
)

ROOT = Path(__file__).resolve().parents[1] / "data" / "derived" / "phase7-v1"
REAL = ROOT / "real" / "source_manifest.csv"


def _write_manifest(path, rows):
    with path.open("w", newline="", encoding="utf-8") as out:
        writer = csv.DictWriter(out, fieldnames=("source", "family", "input"))
        writer.writeheader()
        writer.writerows(rows)


def _rows():
    with REAL.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def _synthetic_components(names):
    p = np.eye(4) - np.ones((4, 4)) / 4
    return {name: p * (i + 1) * 1e-5 for i, name in enumerate(names)}


def test_published_25_is_project_25_systematic_plus_four_statistical_terms():
    sources = read_manifest(REAL)
    assert len(sources) == 29
    assert len(set(sources) - STOCHASTIC_SOURCES) == 25
    assert STOCHASTIC_SOURCES == {
        "finite_evaluation_mc", "data_bootstrap",
        "mc_training_bootstrap", "nn_ensemble",
    }
    assert len(PSEUDO_1D_FAMILIES) == 15
    assert set(PSEUDO_1D_FAMILIES) & STOCHASTIC_SOURCES == STOCHASTIC_SOURCES
    assert len(set(sources) - set(PSEUDO_1D_FAMILIES)) == 14


def test_manifest_duplicate_source_fails_closed(tmp_path):
    rows = _rows()
    _write_manifest(tmp_path / "dup.csv", rows + [rows[-1]])
    with pytest.raises(ValueError, match="Duplicate"):
        read_manifest(tmp_path / "dup.csv")


def test_manifest_wrong_stochastic_taxonomy_fails_closed(tmp_path):
    rows = _rows()
    for row in rows:
        if row["source"] == "data_bootstrap":
            row["family"] = "one_shift_nuisance"
    _write_manifest(tmp_path / "wrong.csv", rows)
    with pytest.raises(ValueError, match="stochastic|family"):
        read_manifest(tmp_path / "wrong.csv")


def test_manifest_missing_family_fails_closed(tmp_path):
    rows = _rows()
    _write_manifest(tmp_path / "missing.csv", rows[:-1])
    with pytest.raises(ValueError, match="29|25|Missing"):
        read_manifest(tmp_path / "missing.csv")


def test_1d_reference_15_is_not_equal_to_all_29_2d_components():
    manifest = read_manifest(REAL)
    components = _synthetic_components(manifest)
    audit = audit_components(components, manifest)
    assert audit["source_counts"] == {
        "all_project_components": 29,
        "paper_systematic_count_arithmetic": 25,
        "stochastic_components": 4,
        "pseudo_notebook_1d_included_components": 15,
        "pseudo_notebook_1d_omitted_systematics": 14,
    }
    assert 0 < audit["pseudo_notebook_1d_trace_share"] < 1
    assert audit["pseudo_notebook_1d_excluded_trace"] > 0
    assert set(audit["pseudo_notebook_1d_omitted_names"]) == set(manifest) - set(PSEUDO_1D_FAMILIES)
    assert audit["exact_paper_to_project_systematic_mapping_verified"] is False
    assert audit["official_2d_covariance_prescription_verified"] is False


def test_component_name_mismatch_or_non_psd_fails_closed():
    manifest = read_manifest(REAL)
    components = _synthetic_components(manifest)
    del components["nonDY"]
    with pytest.raises(ValueError, match="Missing|mismatch"):
        audit_components(components, manifest)
    components = _synthetic_components(manifest)
    components["nonDY"] = -np.eye(4)
    with pytest.raises(ValueError, match="PSD|normalization"):
        audit_components(components, manifest)


def test_frozen_real_and_pseudodata_source_accounting_is_evidence_not_inference(tmp_path):
    result = run(ROOT / "real", ROOT / "pseudo", tmp_path)
    assert result["G15"] == "NO_GO"
    assert result["inference_permission"] == "NO_GO"
    assert list(result["samples"]) == ["pseudo", "real"]
    assert result["samples"]["real"]["replica_counts"] == {
        "data_bootstrap": 100, "mc_training_bootstrap": 25, "nn_ensemble": 100,
    }
    assert result["samples"]["pseudo"]["replica_counts"] == {
        "data_bootstrap": 25, "mc_training_bootstrap": 25, "nn_ensemble": 100,
    }
    for sample in result["samples"].values():
        assert sample["source_counts"]["all_project_components"] == 29
        assert sample["source_counts"]["paper_systematic_count_arithmetic"] == 25
        assert sample["source_counts"]["pseudo_notebook_1d_included_components"] == 15
        assert sample["pseudo_notebook_1d_excluded_trace"] > 0
        assert sample["official_2d_covariance_prescription_verified"] is False
    assert "p_value" not in json.dumps(result)
    assert json.loads((tmp_path / "source_family_accounting.json").read_text()) == result
