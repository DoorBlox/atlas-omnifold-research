"""Regression tests for the frozen, descriptive four-cell descriptive evidence release (v1).

All numeric expectations below come from checksum-pinned ATLAS-derived CSVs,
not illustrative values in an external Deep Research report.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
import pytest

from src.phase7_joint_reference import validate_covariance
from src.phase7_kti_bundle import generate

ROOT = Path(__file__).resolve().parents[1]
V1 = ROOT / "data/derived/phase7-v1"
V2 = ROOT / "data/derived/phase7-v2"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    out = tmp_path_factory.mktemp("four-cell-v1") / "bundle"
    result = generate(V1, V2, out)
    return out, result


def test_frozen_four_cell_fractions_are_real_not_report_examples(bundle):
    out, result = bundle
    rows = read_rows(out / "tables/joint_cells.csv")
    assert len(rows) == 8
    assert [(r["sample"], r["cell"]) for r in rows] == [
        (sample, cell) for sample in ("real", "pseudo")
        for cell in ("LL", "LH", "HL", "HH")
    ]
    values = {(r["sample"], r["cell"]): r for r in rows}
    assert float(values["real", "LL"]["measurement_fraction"]) == pytest.approx(0.4287152163666504, abs=1e-14)
    assert float(values["real", "LL"]["reference_fraction"]) == pytest.approx(0.43416258768444055, abs=1e-14)
    assert float(values["pseudo", "LL"]["measurement_fraction"]) == pytest.approx(0.4366239490795071, abs=1e-14)
    assert float(values["pseudo", "LL"]["reference_fraction"]) == pytest.approx(0.4489994511773743, abs=1e-14)
    for sample in ("real", "pseudo"):
        subset = [r for r in rows if r["sample"] == sample]
        assert sum(float(r["measurement_fraction"]) for r in subset) == pytest.approx(1., abs=1e-12)
        assert sum(float(r["reference_fraction"]) for r in subset) == pytest.approx(1., abs=1e-12)
        assert sum(float(r["delta_fraction"]) for r in subset) == pytest.approx(0., abs=1e-12)
    assert result["bin_spec"]["mass_star_GeV"] == pytest.approx(10.594606399536133)
    assert result["bin_spec"]["tracks_star"] == 11
    assert result["bin_spec"]["selection"] == "pT_trackj1 > 5 GeV"


def test_joint_association_and_marginals_are_independently_recomputable(bundle):
    out, _ = bundle
    rows = read_rows(out / "tables/marginal_association.csv")
    keyed = {(r["sample"], r["observable"]): r for r in rows}
    expected = {
        ("real", "mass_low"): 0.00368008536697409,
        ("real", "multiplicity_low"): -0.014690252323100367,
        ("real", "joint_log_odds"): -0.05973347757838,
        ("pseudo", "mass_low"): -0.022975660813095905,
        ("pseudo", "multiplicity_low"): -0.001963600271194299,
        ("pseudo", "joint_log_odds"): 0.0522361447975217,
    }
    assert set(keyed) == set(expected)
    for key, delta in expected.items():
        row = keyed[key]
        assert float(row["difference"]) == pytest.approx(delta, abs=1e-11)
        assert float(row["conditional_standard_error_full_full"]) > 0
        assert float(row["conditional_standard_error_min"]) <= float(row["conditional_standard_error_full_full"]) + 1e-12
        assert float(row["conditional_standard_error_max"]) >= float(row["conditional_standard_error_full_full"]) - 1e-12
    assert keyed["real", "joint_log_odds"]["reference_kind"] == "shared_nominal_generator"
    assert keyed["pseudo", "joint_log_odds"]["reference_kind"] == "independent_known_truth"


def test_source_contributions_close_under_comparator_aware_covariance(bundle):
    out, result = bundle
    rows = read_rows(out / "tables/source_variance.csv")
    assert len(rows) == 3 * (29 + 30)
    for sample in ("real", "pseudo"):
        for obs in ("mass_low", "multiplicity_low", "joint_log_odds"):
            selected = [r for r in rows if r["sample"] == sample and r["observable"] == obs]
            assert len(selected) == (29 if sample == "real" else 30)
            assert all(float(r["variance"]) >= 0 for r in selected)
            assert sum(float(r["fraction_of_total_conditional_variance"]) for r in selected) == pytest.approx(1., abs=1e-9)
    assert any(r["sample"] == "real" and r["source"] == "finite_evaluation_mc"
               and r["covariance_scope"] == "paired_generator_and_unfolded" for r in rows)
    assert any(r["sample"] == "pseudo" and r["source"] == "independent_truth_finite_mc"
               and r["covariance_scope"] == "independent_target_truth" for r in rows)
    assert result["source_accounting"]["real"]["systematic_labelled"] == 25
    assert result["source_accounting"]["real"]["stochastic"] == 4
    assert result["source_accounting"]["pseudo"]["notebook_1d_selected"] == 15


def test_four_scenarios_and_shape_covariance_constraints(bundle):
    out, result = bundle
    rows = read_rows(out / "tables/scenario_sensitivity.csv")
    matrices = read_rows(out / "tables/covariance_matrix.csv")
    assert len(rows) == 8
    assert len(matrices) == 2 * 4 * 16
    assert set(r["sample"] for r in rows) == {"real", "pseudo"}
    for r in rows:
        assert int(r["contrast_rank"]) == 3
        assert float(r["normalization_null_residual"]) < 1e-10
        assert float(r["joint_log_odds_conditional_standard_error"]) > 0
        assert float(r["uncalibrated_quadratic_not_a_pvalue"]) >= 0
    for sample in ("real", "pseudo"):
        for scenario in result["scenario_order"]:
            subset = [r for r in matrices if r["sample"] == sample and r["scenario"] == scenario]
            c = np.zeros((4, 4))
            names = ("LL", "LH", "HL", "HH")
            for row in subset:
                c[names.index(row["row_cell"]), names.index(row["col_cell"])] = float(row["shape_covariance"])
            validate_covariance(c)
            assert np.linalg.matrix_rank(c, tol=1e-12) == 3


def test_four_vector_figures_are_well_formed_and_data_backed(bundle):
    out, _ = bundle
    figures = sorted((out / "figures").glob("*.svg"))
    assert len(figures) == 4
    for path in figures:
        content = path.read_text(encoding="utf-8")
        root = ET.fromstring(content)
        assert root.tag.endswith("svg")
        assert "<title>" in content
        assert "illustrative" not in content.lower()
        assert "p-value" not in content.lower()
    heatmap = (out / "figures/fig1_joint_shapes.svg").read_text(encoding="utf-8")
    assert "42.87%" in heatmap
    assert "44.90%" in heatmap


def test_manifest_hashes_and_deterministic_rebuild(bundle, tmp_path):
    out, result = bundle
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["status"] == "CHECKSUM_PINNED_DESCRIPTIVE_BUNDLE"
    assert "manifest.json" not in manifest["files"]
    for relative, digest in manifest["files"].items():
        assert hashlib.sha256((out / relative).read_bytes()).hexdigest() == digest
    other = tmp_path / "rebuilt"
    second = generate(V1, V2, other)
    assert result == second
    assert json.loads((other / "manifest.json").read_text()) == manifest


def test_fail_closed_when_snapshot_or_v2_is_tampered(tmp_path):
    copied = tmp_path / "v1"
    shutil.copytree(V1, copied)
    csv_path = copied / "real/real_2x2_cells.csv"
    csv_path.write_text(csv_path.read_text(encoding="utf-8").replace(
        "0.4287152163666504", "0.3000000000000000"), encoding="utf-8")
    with pytest.raises((ValueError, OSError), match="checksum|digest|SHA|hash|Mismatch|mismatch"):
        generate(copied, V2, tmp_path / "tampered")
    with pytest.raises((FileNotFoundError, OSError, ValueError)):
        generate(V1, tmp_path / "missing-v2", tmp_path / "missing-output")


def test_fabricated_positive_offdiagonal_covariance_is_rejected():
    bogus = np.array([[1.2, .25, .15, .05],
                      [.25, 1., .10, .08],
                      [.15, .10, 1.5, .12],
                      [.05, .08, .12, 1.1]]) * 1e-6
    with pytest.raises(ValueError, match="Normalization"):
        validate_covariance(bogus)


def test_no_real_data_significance_or_go_permission(bundle):
    out, result = bundle
    assert result["G5"] == "PROVISIONAL"
    assert result["G8"] == "UNVERIFIED"
    assert result["G12"] == "UNVERIFIED"
    assert result["G15"] == "NO_GO"
    assert result["inference_permission"] == "NO_GO"
    assert "p_value" not in json.dumps(result).lower()
    assert "sigma" not in json.dumps(result).lower()
    report = (out / "MANUSCRIPT_RESULTS.md").read_text(encoding="utf-8")
    assert "not a calibrated" in report.lower()
    assert "G15 NO-GO" in report


def test_repository_four_cell_release_matches_generated_manifest(bundle):
    """The renamed permanent release must equal a fresh v1 rebuild byte for byte."""
    out, _ = bundle
    stored = ROOT / "results" / "four-cell-v1"
    manifest = json.loads((stored / "manifest.json").read_text(encoding="utf-8"))
    rebuilt = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    if rebuilt != manifest:
        differences = []
        for rel in sorted(set(manifest["files"]) | set(rebuilt["files"])):
            if manifest["files"].get(rel) == rebuilt["files"].get(rel):
                continue
            stored_lines = (stored / rel).read_text(encoding="utf-8").splitlines()
            rebuilt_lines = (out / rel).read_text(encoding="utf-8").splitlines()
            examples = [(i + 1, a, b) for i, (a, b) in
                        enumerate(zip(stored_lines, rebuilt_lines)) if a != b]
            differences.append(f"{rel}: {len(examples)} differing lines; first 3 = {examples[:3]}")
        pytest.fail("Repository/regen differences: " + "; ".join(differences))
    for relative, expected_digest in manifest["files"].items():
        assert hashlib.sha256((out / relative).read_bytes()).hexdigest() == expected_digest
        assert hashlib.sha256((stored / relative).read_bytes()).hexdigest() == expected_digest


def test_no_retired_release_paths_in_active_project_files():
    """Keep active project instructions tied to the canonical four-cell version."""
    exempt = {ROOT / "docs" / "HANDOFF_HISTORY.md",
              ROOT / "docs" / "RELEASE_MIGRATION.md"}
    for parent in ("docs", "plans", "results", "src", "tests", ".github"):
        for path in (ROOT / parent).rglob("*"):
            if not path.is_file() or path in exempt:
                continue
            if path.suffix.lower() not in {".md", ".txt", ".py", ".yml", ".yaml", ".json"}:
                continue
            assert ("kti-" + "nov18") not in path.read_text(encoding="utf-8"), str(path)
