"""Source-backed, pre-specified 2x2 two-point alternatives; never a p-value."""
import numpy as np
import pytest
from src.phase7_twopoint_protocol import (
    count_shift_to_covariance,sample_two_point_inputs,
    build_two_point_scenarios,check_covariance,analyze
)


def test_linearized_fully_correlated_and_four_independent_nuisances():
    h=np.array([20.,30.,40.,50.])
    delta=np.array([2.,-1.,3.,1.])
    J=(np.eye(4)-np.outer(h/h.sum(),np.ones(4)))/h.sum()
    full=count_shift_to_covariance(h,delta,'fully_correlated')
    four=count_shift_to_covariance(h,delta,'four_bin_decorrelated')
    np.testing.assert_allclose(full,np.outer(J@delta,J@delta),atol=1e-18)
    np.testing.assert_allclose(four,J@np.diag(delta*delta)@J.T,atol=1e-18)
    assert check_covariance(full)['is_psd'] and check_covariance(four)['is_psd']
    np.testing.assert_allclose(four@np.ones(4),np.zeros(4),atol=1e-14)


def test_all_scenarios_keep_sources_and_never_remove_sherpa():
    h=np.array([20.,30.,40.,50.])
    delta=np.array([2.,-1.,3.,1.])
    M=np.eye(4)-np.ones((4,4))/4
    parts={'dd_unfolding':np.zeros((4,4)),
           'sherpa_hidden_variable':np.zeros((4,4)),
           'finite_evaluation_mc':(M@np.eye(4)@M)*1e-5}
    models=build_two_point_scenarios(parts,h,delta,np.array([0.,2.,1.,-2.]))
    assert list(models)==[
       'both_fully_correlated','dd_decorrelated_sherpa_correlated',
       'dd_correlated_sherpa_decorrelated','both_four_bin_decorrelated']
    assert all(set(model)==set(parts) for model in models.values())
    assert all(check_covariance(sum(model.values()))['is_psd'] for model in models.values())
    assert not np.allclose(models['both_fully_correlated']['dd_unfolding'],
                           models['both_four_bin_decorrelated']['dd_unfolding'])


def test_dd_is_signed_count_shift_before_normalization():
    h=np.array([10.,20.,30.,40.])
    d=np.array([12.,17.,33.,42.])
    t=np.array([9.,19.,31.,39.])
    alt=np.array([11.,18.,34.,42.])
    dd,sherpa=sample_two_point_inputs({
       'nominal':{'columns':{
         'weights_nominal':{'sum_w':h.tolist()},
         'weights_dd':{'sum_w':d.tolist()},
         'target_dd':{'sum_w':t.tolist()}}},
       'sherpa':{'columns':{'weights_nominal':{'sum_w':alt.tolist()}}},
    })
    np.testing.assert_allclose(dd,(d-t)*h/t)
    np.testing.assert_allclose(sherpa,alt-h)
    assert not np.isclose(dd.sum(),0)


def test_invalid_or_data_adaptive_model_rejected():
    h=np.array([10.,20.,30.,40.])
    shift=np.array([2.,1.,1.,-1.])
    with pytest.raises(ValueError,match='Unknown'):
        count_shift_to_covariance(h,shift,'choose_by_lowest_real_chi2')
    with pytest.raises(ValueError,match='positive'):
        count_shift_to_covariance(np.array([0.,20.,30.,40.]),shift,'fully_correlated')
    with pytest.raises(ValueError,match='finite'):
        count_shift_to_covariance(h,np.array([1.,np.nan,2.,1.]),'fully_correlated')
    with pytest.raises(ValueError,match='Missing DD/Sherpa'):
        build_two_point_scenarios({'finite_evaluation_mc':np.zeros((4,4))},h,shift,shift)


def test_saved_official_data_correlation_scenarios_are_exploratory():
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]/'data/derived'
    if not (root/'phase7-v2'/'moments.json').exists():
        pytest.skip('Real official signed v2 statistics not yet present')
    res=analyze(root/'phase7-v1',root/'phase7-v2')
    assert res['G15']=='NO_GO' and res['inference_permission']=='NO_GO'
    assert list(res['samples'])==['pseudo','real']
    assert all(len(item['models'])==4 for item in res['samples'].values())
    assert all(x['rank_three_contrast']==3 for item in res['samples'].values() for x in item['models'])
    assert 'p_value' not in str(res)
