"""A corrected R-1 conditional Gaussian toy does NOT grant 2D experimental coverage."""
import json
import numpy as np
import pytest

from src.phase7_conditional_null import toy_study, wilson_interval, run

COUNTS={'data_bootstrap':25,'mc_training_bootstrap':25,'nn_ensemble':100}


def synthetic_sources():
    P=np.eye(4)-np.ones((4,4))/4
    return {'data_bootstrap':P*3e-5,'mc_training_bootstrap':P*1e-5,
            'nn_ensemble':P*8e-6,'finite_evaluation_mc':P*8e-5,
            'dd_unfolding':P*1e-5,'sherpa_hidden_variable':P*2e-5}


def test_sample_covariance_toy_is_reproducible_no_inference():
    a=toy_study(synthetic_sources(),COUNTS,toys=1000,seed=42,batch=125)
    b=toy_study(synthetic_sources(),COUNTS,toys=1000,seed=42,batch=125)
    assert a==b
    assert a['covariance_estimator']=='SAMPLE_DIVISOR_R_MINUS_ONE'
    assert a['simulated_rejection_fraction']>=0
    assert a['G8']=='CONDITIONAL_GAUSSIAN_ONLY'
    assert a['G15']=='NO_GO'
    assert 'p_value' not in json.dumps(a)


def test_known_covariance_null_has_expected_type_i_error():
    output=toy_study(synthetic_sources(),COUNTS,toys=3000,seed=11,batch=400)
    assert .035 < output['simulated_known_cov_rejection_fraction'] < .065
    assert output['simulated_plugin_cov_95th_percentile'] > 0
    assert output['simulated_plugin_cov_95th_percentile'] <= 15
    lo,hi=output['simulated_plugin_rejection_95pct_mc_interval']
    assert 0<=lo<=hi<=1


def test_invalid_covariance_count_and_simulations_fail_closed():
    base=synthetic_sources()
    with pytest.raises(ValueError,match='500'):
        toy_study(base,COUNTS,toys=1)
    with pytest.raises(ValueError,match='replica'):
        toy_study(base,{'data_bootstrap':100},toys=500)
    with pytest.raises(ValueError,match='count'):
        toy_study(base,{**COUNTS,'data_bootstrap':1},toys=500)
    v=np.array([1.,-1.,0.,0.])
    bad={**base,'negative':-np.outer(v,v)}
    with pytest.raises(ValueError,match='PSD'):
        toy_study(bad,COUNTS,toys=500)
    with pytest.raises(ValueError,match='Missing'):
        toy_study({'data_bootstrap':base['data_bootstrap']},COUNTS,toys=500)


def test_wilson_interval_is_bounded_and_tightens_with_n():
    assert wilson_interval(0,100)[0]==0
    assert wilson_interval(100,100)[1]==1
    small=wilson_interval(5,100)
    large=wilson_interval(50,1000)
    assert small[1]-small[0]>large[1]-large[0]


def test_full_scenario_driver_only_reports_toy_fractions(tmp_path,monkeypatch):
    import src.phase7_joint_reference as joint
    report={'samples':{'pseudo':{'replica_counts':COUNTS},'real':{'replica_counts':COUNTS}},
            'G15':'NO_GO'}
    matrices={k:{'both_fully_correlated':synthetic_sources()} for k in ('pseudo','real')}
    monkeypatch.setattr(joint,'analyze',lambda *_args,**kw: (report,matrices))
    out=run(tmp_path/'v1',tmp_path/'v2',tmp_path/'out',toys=500,seed=31)
    assert list(out['scenarios'])==['pseudo','real']
    assert all(len(x)==1 for x in out['scenarios'].values())
    assert out['G15']=='NO_GO'
    assert 'p_value' not in json.dumps(out)
    assert json.loads((tmp_path/'out'/'conditional_gaussian_toys.json').read_text())==out
