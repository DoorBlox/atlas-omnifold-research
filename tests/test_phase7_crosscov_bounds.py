"""A conservative finite-event covariance envelope without shared-event raw data."""
from pathlib import Path

import numpy as np
import pytest

from src.phase7_crosscov_bounds import (
    finite_mc_shape_covariance, scalar_covariance_envelope,
    evaluate_real_snapshot, log_odds_gradient,
)


def test_weighted_count_formula_matches_explicit_jacobian():
    h = np.array([12., 5., 9., 16.])
    w2 = np.array([5., 2., 4., 7.])
    q = h / h.sum()
    neff = h**2 / w2
    computed = finite_mc_shape_covariance(q, neff)
    J = (np.eye(4) - np.outer(q, np.ones(4))) / h.sum()
    np.testing.assert_allclose(computed, J @ np.diag(w2) @ J.T, atol=1e-16, rtol=1e-12)
    np.testing.assert_allclose(computed @ np.ones(4), 0., atol=1e-15)


def test_cauchy_envelope_contains_extreme_and_zero_correlation():
    bounds = scalar_covariance_envelope(4., 1., 9.)
    assert bounds['reference_fixed_variance'] == 13.
    assert bounds['minimum_variance'] == 10.
    assert bounds['maximum_variance'] == 18.
    assert bounds['independent_variance'] == 14.
    assert bounds['minimum_variance'] <= bounds['independent_variance'] <= bounds['maximum_variance']
    assert bounds['minimum_variance'] <= bounds['reference_fixed_variance'] <= bounds['maximum_variance']


def test_frozen_real_nominal_generator_envelope_has_expected_conclusions():
    root = Path(__file__).resolve().parents[1] / 'data/derived/phase7-v1'
    result = evaluate_real_snapshot(root)
    assert result['status'] == 'CONDITIONAL_FINITE_MC_CROSS_COVARIANCE_ENVELOPE'
    assert result['G15'] == 'NO_GO'
    assert len(result['observables']) == 3
    odds = next(x for x in result['observables'] if x['observable'] == 'log_odds_ratio')
    assert .091 < odds['minimum_standard_error'] < .093
    assert .093 < odds['maximum_standard_error'] < .095
    assert odds['reference_fixed_standard_error'] > odds['minimum_standard_error']
    assert odds['reference_fixed_standard_error'] < odds['maximum_standard_error']
    assert odds['se_max_over_reference_fixed_ratio'] < 1.03
    assert odds['measured_minus_reference'] < 0
    assert 'p_value' not in str(result)


def test_log_odds_uses_reference_gradient_not_measurement_gradient():
    p = np.array([.40, .10, .20, .30])
    q = np.array([.45, .10, .15, .30])
    g1, g2 = log_odds_gradient(p), log_odds_gradient(q)
    assert not np.array_equal(g1,g2)
    assert np.isclose(g2[0], 1/.45) and np.isclose(g2[2], -1/.15)


def test_invalid_inputs_fail_closed():
    with pytest.raises(ValueError, match='positive'):
        finite_mc_shape_covariance(np.array([.25]*4), np.array([10., 0., 10., 10.]))
    with pytest.raises(ValueError, match='normalized'):
        finite_mc_shape_covariance(np.ones(4), np.ones(4))
    with pytest.raises(ValueError, match='negative'):
        scalar_covariance_envelope(-1., 1., 1.)
    with pytest.raises(ValueError, match='positive'):
        log_odds_gradient(np.array([.2,0,.3,.5]))
