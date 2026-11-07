"""Independent small-number reference-port tests and fail-closed source provenance."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from src.phase7_official_helper_audit import (
    audit_source_text,
    covariance_port,
    run,
    smooth_1d_port,
)


def test_signed_hessian_off_diagonals_are_retained():
    shifts = np.array([[1., 2.], [3., -1.]])
    expected = np.array([[10., -1.], [-1., 5.]])
    np.testing.assert_array_equal(covariance_port(shifts), expected)


def test_replica_covariance_sample_divisor_and_ensemble_count():
    replicas = np.array([[1., 2.], [3., 6.], [2., 4.]])
    sample = covariance_port(replicas, replicas.mean(axis=0))
    np.testing.assert_array_equal(sample, [[1., 2.], [2., 4.]])
    np.testing.assert_array_equal(sample / len(replicas),
                                  [[1./3, 2./3], [2./3, 4./3]])
    assert not np.allclose(sample, np.cov(replicas.T, ddof=0))


def test_reference_port_uses_signed_1d_gaussian_weights():
    x = np.array([-2., -1., 0., 1.])
    d = np.array([2., -1., -3., 1.])
    width = (x[-1] - x[0]) / 10.
    matrix = np.exp(-.5 * ((x[:, None] - x[None, :]) / width)**2)
    expected = matrix @ d / matrix.sum(axis=1)
    np.testing.assert_allclose(smooth_1d_port(d, x), expected, rtol=1e-14)
    assert np.any(smooth_1d_port(d, x) < 0)


def test_positive_centers_use_logarithmic_coordinate():
    x = np.array([1., 2., 4., 16.])
    d = np.array([1., -2., 4., -3.])
    lx = np.log(x)
    k = np.exp(-.5 * ((lx[:, None]-lx[None, :]) / ((lx[-1]-lx[0])/10.))**2)
    np.testing.assert_allclose(smooth_1d_port(d, x), k @ d / k.sum(axis=1))


@pytest.mark.parametrize("values,centers", [
    ([[1., 2.], [3., 4.]], [1., 2.]),
    ([1., 2., 3.], [1., 2.]),
    ([1., 2.], [1., 1.]),
    ([1., np.nan], [1., 2.]),
    ([1., 2.], [2., 1.]),
])
def test_1d_port_rejects_invalid_shape_centers(values, centers):
    with pytest.raises(ValueError):
        smooth_1d_port(values, centers)


def test_flattening_2d_into_1d_changes_with_arbitrary_cell_order():
    physical = np.array([3., -4., 2., -1.])
    centers = np.array([1., 2., 3., 4.])
    original = smooth_1d_port(physical, centers)
    perm = np.array([0, 2, 1, 3])
    reordered = smooth_1d_port(physical[perm], centers)[np.argsort(perm)]
    assert np.max(np.abs(original-reordered)) > 1e-3


def test_ast_extracts_exact_functions_and_reports_missing():
    source = "def fill_cov_matrix(a):\n    return a\n\ndef smooth_uncertainty(b,c):\n    return b\n"
    result = audit_source_text(source)
    assert result['source_sha256'] == hashlib.sha256(source.encode()).hexdigest()
    assert result['functions']['fill_cov_matrix']['status'] == 'BODY_RETRIEVED_NOT_SEMANTICALLY_VALIDATED'
    assert result['functions']['smooth_uncertainty']['start_line'] == 4
    assert result['functions']['corr_matrix']['status'] == 'FUNCTION_NOT_FOUND'
    assert result['official_source_semantics_verified'] is False
    assert result['G15'] == 'NO_GO'


def test_fetch_failure_is_no_go_and_names_each_unverified_function(tmp_path):
    def unavailable(_):
        raise PermissionError('HTTP 403 Forbidden')
    result = run(tmp_path, fetcher=unavailable)
    assert result['official_source_retrieved'] is False
    assert '403' in result['fetch_error']
    for name in ('fill_cov_matrix','smooth_uncertainty','corr_matrix'):
        assert result['functions'][name]['status'] == 'SOURCE_UNAVAILABLE'
    assert result['G15'] == 'NO_GO' and result['inference_permission'] == 'NO_GO'
    saved = json.loads((tmp_path/'official_helper_source_audit.json').read_text())
    assert saved == result
    assert 'p_value' not in json.dumps(result)


def test_retrieved_syntax_failure_does_not_claim_verified(tmp_path):
    result = run(tmp_path, fetcher=lambda _: 'def fill_cov_matrix(:\n')
    assert result['official_source_retrieved'] is True
    assert result['parse_status'] == 'INVALID_PYTHON'
    assert result['functions']['fill_cov_matrix']['status'] == 'SYNTAX_UNAVAILABLE'
    assert result['G15'] == 'NO_GO'
