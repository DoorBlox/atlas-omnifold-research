"""Conditional toy validation; synthetic data never labeled physical ATLAS coverage."""
import numpy as np
import pytest
from src.phase7_calibration import CHI2_3_95, study, _sqrt_psd
COUNTS = {'data_bootstrap':25, 'mc_training_bootstrap':25, 'nn_ensemble':100}


def synthetic_sources():
    basis = np.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[-1.,-1.,-1.]])
    c = basis @ basis.T * .0001
    return {
        'data_bootstrap': c, 'mc_training_bootstrap': c * .4,
        'nn_ensemble': c * .1, 'one_shift_fixed': c * .7
    }


def test_known_covariance_rejection_near_nominal():
    result = study(synthetic_sources(), replica_counts=COUNTS, toys=3000, seed=141)
    assert 0.035 < result['known_cov_rejection_at_chi2_3_95'] < 0.065
    assert result['G15'] == 'NO-GO'
    assert 'p_value' not in result
    assert result['plugin_cov_empirical_95th_percentile'] > 0
    assert result['nominal_chi2_3_95_threshold_reference'] == CHI2_3_95


def test_gaussian_replica_conditional_model_is_deterministic():
    a = study(synthetic_sources(), replica_counts=COUNTS, toys=512, seed=42, batch=32)
    b = study(synthetic_sources(), replica_counts=COUNTS, toys=512, seed=42, batch=128)
    c = study(synthetic_sources(), replica_counts=COUNTS, toys=512, seed=42, batch=32)
    assert a == c
    assert a['plugin_cov_rejection_at_chi2_3_95'] >= 0
    assert b['known_cov_empirical_95th_percentile'] > 0


def test_non_psd_fails_closed():
    with pytest.raises(ValueError, match='Non-PSD'):
        _sqrt_psd(np.diag([1.,1.,-1.]))
    with pytest.raises(ValueError, match='At least 500'):
        study(synthetic_sources(), replica_counts=COUNTS,toys=20)
    with pytest.raises(KeyError):
        study({'data_bootstrap':np.eye(4)}, replica_counts=COUNTS, toys=500)
