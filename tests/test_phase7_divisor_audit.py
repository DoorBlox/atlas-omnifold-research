"""Test sample covariance R-1 correction without event-level files."""
import json
from pathlib import Path

import numpy as np
import pytest

from src.phase7_divisor_audit import (
    sample_from_population_covariance, diagnostics, run
)


def test_sample_rescaling_matches_exact_unbiased_covariance():
    replicas = np.array([[.2, .3, .2, .3], [.3, .2, .3, .2],
                         [.25, .25, .25, .25]])
    centered = replicas - replicas.mean(axis=0)
    population = centered.T @ centered / len(replicas)
    parts = {"data_bootstrap": population, "mc_training_bootstrap": population,
             "nn_ensemble": population/3, "untouched": population*0.25}
    counts = {"data_bootstrap":3, "mc_training_bootstrap":3, "nn_ensemble":3}
    corrected, factors = sample_from_population_covariance(parts, counts)
    np.testing.assert_allclose(corrected["data_bootstrap"],
                               np.cov(replicas, rowvar=False, ddof=1), atol=1e-16)
    np.testing.assert_allclose(corrected["nn_ensemble"],
                               np.cov(replicas, rowvar=False, ddof=1)/3, atol=1e-16)
    assert factors == {family:1.5 for family in counts}
    np.testing.assert_array_equal(corrected["untouched"], parts["untouched"])


def test_invalid_counts_and_normalization_fail_closed():
    basis = np.vstack([np.eye(3), -np.ones(3)])
    matrix = basis @ basis.T * .001
    parts = {key:matrix for key in ("data_bootstrap", "mc_training_bootstrap", "nn_ensemble")}
    with pytest.raises(ValueError, match="Missing/extra"):
        sample_from_population_covariance(parts, {"data_bootstrap":25, "nn_ensemble":100})
    with pytest.raises(ValueError, match="Invalid replica count"):
        sample_from_population_covariance(parts, {"data_bootstrap":1,
            "mc_training_bootstrap":25, "nn_ensemble":100})
    with pytest.raises(ValueError, match="Missing normalization null"):
        sample_from_population_covariance({**parts, "bad":np.ones((4,4))},
            {"data_bootstrap":25, "mc_training_bootstrap":25, "nn_ensemble":100})


def test_diagnostic_does_not_generate_a_pvalue():
    basis = np.vstack([np.eye(3), -np.ones(3)])
    matrix = basis @ basis.T * .0001
    result = diagnostics({"c":matrix}, np.array([.3, .2, .2, .3]), np.full(4,.25))
    assert result["contrast_rank"] == 3
    assert result["uncalibrated_quadratic_not_a_pvalue"] > 0
    assert "p_value" not in result


def test_official_frozen_snapshot_requires_no_download(tmp_path):
    snapshot = Path("data/derived/phase7-v1")
    result = run(snapshot,tmp_path)
    assert result["G15"] == "NO_GO"
    assert result["samples"]["real"]["replica_counts"] == {
        "data_bootstrap":100, "mc_training_bootstrap":25, "nn_ensemble":100}
    assert result["samples"]["pseudo"]["replica_counts"]["data_bootstrap"] == 25
    assert result["samples"]["real"]["relative_covariance_trace_change_percent"] > 0
    assert result["samples"]["pseudo"]["relative_covariance_trace_change_percent"] > 0
    assert "p_value" not in json.dumps(result)
    for kind in ("real","pseudo"):
        with np.load(tmp_path/f"{kind}_sample_denominator_candidate.npz",allow_pickle=False) as z:
            assert len(z.files) == 29
