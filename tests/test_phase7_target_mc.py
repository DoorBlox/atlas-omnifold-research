"""Regression for weighted-Poisson truth precision from saved 2x2 summaries."""
from pathlib import Path
import json
import numpy as np
import pytest
from src.phase7_target_mc import normalized_target_covariance, gradients, analyze_target


def test_weighted_mc_jacobian_identity():
    h=np.array([2.5,4.0,1.2,6.0])
    s=np.array([1.5,2.0,.72,3.0])
    H=h.sum()
    q=h/H
    n=h*h/s
    jac=(np.eye(4)-np.outer(q,np.ones(4)))/H
    expected=jac@np.diag(s)@jac.T
    result=normalized_target_covariance(q,n)
    np.testing.assert_allclose(result,expected,atol=1e-16)
    np.testing.assert_allclose(result@np.ones(4),0,atol=1e-16)


def test_log_odds_truth_gradient_not_measurement_gradient():
    q=np.array([.40,.10,.20,.30])
    p=np.array([.38,.12,.21,.29])
    n=np.array([100.,200.,150.,300.])
    c=normalized_target_covariance(q,n)
    gt=gradients(q)['log_odds_ratio']
    gp=gradients(p)['log_odds_ratio']
    assert not np.allclose(gt,gp)
    np.testing.assert_allclose(gt@c@gt,sum(1/n),rtol=1e-12)
    assert not np.isclose(gp@c@gp,sum(1/n))


def test_invalid_neff_or_shape_is_rejected():
    with pytest.raises(ValueError,match='positive'):
        normalized_target_covariance(np.full(4,.25),np.array([10.,0.,10.,10.]))
    with pytest.raises(ValueError,match='shape'):
        normalized_target_covariance(np.full(4,.2),np.array([10.]*4))
    with pytest.raises(ValueError,match='strictly positive'):
        gradients(np.array([.5,0,.2,.3]))


def test_actual_snapshot_corrects_prior_target_log_odds_approximation(tmp_path):
    result=analyze_target(Path('data/derived/phase7-v1'),tmp_path)
    rows={x['observable']:x for x in result['metrics']}
    assert result['G15']=='NO_GO'
    assert np.isclose(rows['log_odds_ratio']['target_mc_se'],
                      .0013423359141068556,rtol=1e-11)
    assert np.isclose(rows['log_odds_ratio']['combined_se_independence_model'],
                      .05641215968226348,rtol=1e-11)
    assert rows['log_odds_ratio']['target_mc_se']<rows['log_odds_ratio']['measurement_provisional_se']
    assert 'p_value' not in json.dumps(result)
    assert json.loads((tmp_path/'target_mc_precision.json').read_text())['G15']=='NO_GO'
