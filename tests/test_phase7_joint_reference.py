"""Independent exact synthetic tests for the conditional 2x2 joint covariance.

No stochastic real-data inference is performed here.
"""
import json
import numpy as np
import pytest

from src.phase7_joint_reference import (
    expected_replica_covariances,
    shared_reference_covariance,
    shared_observable_variance,
    shape_jacobian,
    build_joint_scenarios,
    contrast_diagnostics,
)


def _column(values):
    return {'sum_w': np.asarray(values, dtype=float).tolist()}


def _columns_for_replicas():
    base = np.array([10., 20., 30., 40.])
    cols = {'weights_nominal': _column(base)}
    for family in ('weights_bootstrap_data', 'weights_bootstrap_mc', 'weights_ensemble'):
        for i in range(3):
            v = base * (1 + .01 * (i-1) * np.array([1., -1., 2., 0.]))
            cols[f'{family}_{i}'] = _column(v)
    return cols


def test_reference_replica_covariance_is_r_minus_one_and_nn_division():
    cols = _columns_for_replicas()
    counts = {'data_bootstrap': 3, 'mc_training_bootstrap': 3, 'nn_ensemble': 3}
    got = expected_replica_covariances(cols, counts)
    shapes = np.array([np.array(cols[f'weights_bootstrap_data_{i}']['sum_w'])
                       for i in range(3)])
    shapes /= shapes.sum(axis=1, keepdims=True)
    expected = np.cov(shapes, rowvar=False, ddof=1)
    np.testing.assert_allclose(got['data_bootstrap'], expected, rtol=1e-12, atol=1e-18)
    np.testing.assert_allclose(got['mc_training_bootstrap'], expected, rtol=1e-12, atol=1e-18)
    np.testing.assert_allclose(got['nn_ensemble'], expected / 3, rtol=1e-12, atol=1e-18)
    np.testing.assert_allclose(got['data_bootstrap'] @ np.ones(4), 0., atol=1e-14)
    assert not np.allclose(got['data_bootstrap'], expected * 2 / 3, rtol=1e-9, atol=1e-15)


def test_replica_family_rejects_missing_or_noncontiguous_members():
    cols = _columns_for_replicas()
    del cols['weights_bootstrap_data_1']
    with pytest.raises(ValueError, match='replica'):
        expected_replica_covariances(cols, {'data_bootstrap':3, 'mc_training_bootstrap':3, 'nn_ensemble':3})


def test_replica_family_rejects_extra_member_and_nonfinite_shapes():
    cols = _columns_for_replicas()
    cols['weights_ensemble_3'] = _column([10., 20., 30., 40.])
    with pytest.raises(ValueError, match='replica'):
        expected_replica_covariances(cols, {'data_bootstrap':3, 'mc_training_bootstrap':3, 'nn_ensemble':3})
    del cols['weights_ensemble_3']
    cols['weights_bootstrap_mc_0'] = _column([1., np.inf, 3., 4.])
    with pytest.raises(ValueError):
        expected_replica_covariances(cols, {'data_bootstrap':3, 'mc_training_bootstrap':3, 'nn_ensemble':3})


def test_shared_poisson_covariance_matches_event_level_outer_products():
    wp = np.array([[1., 4.], [3., 1.], [2., 2.], [3., 3.]])
    wq = np.array([[1., 2.], [2., 3.], [1., 4.], [3., 2.]])
    hp, hq = wp.sum(axis=1), wq.sum(axis=1)
    spp, sqq, spq = (wp*wp).sum(axis=1), (wq*wq).sum(axis=1), (wp*wq).sum(axis=1)
    actual = shared_reference_covariance(hp, hq, spp, sqq, spq)
    Jp, Jq = shape_jacobian(hp), shape_jacobian(hq)
    direct = np.zeros((4,4))
    for i in range(4):
        for j in range(2):
            v = Jp[:,i] * wp[i,j] - Jq[:,i] * wq[i,j]
            direct += np.outer(v, v)
    np.testing.assert_allclose(actual, direct, rtol=1e-13, atol=1e-15)
    np.testing.assert_allclose(actual @ np.ones(4), 0, atol=1e-15)


def test_shared_proportional_event_weights_cancel_to_zero():
    w = np.array([2., 4., 6., 8.])
    assert np.max(np.abs(shared_reference_covariance(2*w, w, 4*w*w, w*w, 2*w*w))) < 1e-14


def test_negative_or_invalid_mixed_moments_rejected():
    x = np.array([1.,2.,3.,4.])
    with pytest.raises(ValueError, match='Cauchy'):
        shared_reference_covariance(x,x,x*x,x*x,2*x*x)
    with pytest.raises(ValueError):
        shared_reference_covariance(x,x,x*x, x*x, np.array([np.nan,1,2,3]))
    with pytest.raises(ValueError):
        shape_jacobian([0.,0.,0.,0.])


def test_observable_gradient_uses_different_reference_shape_for_logodds():
    hp = np.array([13.,12.,9.,20.]); hq = np.array([11.,13.,14.,15.])
    spp = np.array([20.,18.,13.,25.]); sqq = np.array([19.,19.,23.,21.]); spq=np.array([12.,10.,12.,12.])
    p,q = hp/hp.sum(), hq/hq.sum()
    gp = np.array([1/p[0], -1/p[1], -1/p[2], 1/p[3]])
    gq = np.array([1/q[0], -1/q[1], -1/q[2], 1/q[3]])
    a,b = shape_jacobian(hp).T @ gp, shape_jacobian(hq).T @ gq
    expected = float(np.sum(a*a*spp+b*b*sqq-2*a*b*spq))
    result = shared_observable_variance(hp,hq,spp,sqq,spq,gp,gq)
    assert result == pytest.approx(expected,abs=1e-14)
    approximate = gp @ shared_reference_covariance(hp,hq,spp,sqq,spq) @ gp
    assert not np.isclose(approximate, result, rtol=1e-3)


def test_real_and_pseudodata_scenarios_are_distinct_and_never_generate_pvalue():
    I = np.eye(4)-np.ones((4,4))/4
    comps = {'data_bootstrap': I*1e-5, 'mc_training_bootstrap': I*2e-5,
             'nn_ensemble': I*1e-5,'finite_evaluation_mc': I*3e-5,
             'dd_unfolding': I*1e-6,'sherpa_hidden_variable':I*1e-6,
             'theoryQCD':I*2e-6}
    h = np.array([15., 25., 35., 45.]); q=np.array([.15,.25,.30,.30])
    models = build_joint_scenarios(comps,h,np.array([2.,-1.,3.,1.]),np.array([1.,2.,-3.,0.]),
                                   kind='pseudo', target_covariance=I*1e-7)
    assert len(models)==4
    assert all('independent_truth_finite_mc' in v for v in models.values())
    assert all(len(v)==len(comps)+1 for v in models.values())
    d = contrast_diagnostics(h/h.sum(),q,models['both_fully_correlated'])
    assert d['contrast_rank']==3 and d['uncalibrated_quadratic_not_a_pvalue'] >= 0
    assert 'p_value' not in json.dumps(d)
    with pytest.raises(ValueError, match='real'):
        build_joint_scenarios(comps,h,np.ones(4),np.ones(4),kind='real',target_covariance=I)
    with pytest.raises(ValueError, match='shared'):
        build_joint_scenarios(comps,h,np.ones(4),np.ones(4),kind='real')


def test_real_scenario_replaces_single_finite_mc_component_once():
    I = np.eye(4)-np.ones((4,4))/4
    parts={'finite_evaluation_mc':I*3e-4,'data_bootstrap':I*1e-5,
           'dd_unfolding':I*1e-6,'sherpa_hidden_variable':I*2e-6}
    h=np.array([10.,20.,30.,40.])
    shared=I*2e-5
    models=build_joint_scenarios(parts,h,np.array([1,1,-1,-1]),np.array([1,-2,2,-1]),
                                 kind='real', shared_finite_mc=shared)
    assert all(len(x)==len(parts) for x in models.values())
    np.testing.assert_array_equal(models['both_fully_correlated']['finite_evaluation_mc'],shared)
    assert not np.allclose(models['both_fully_correlated']['finite_evaluation_mc'],parts['finite_evaluation_mc'])
    assert all('independent_truth_finite_mc' not in v for v in models.values())


def _synthetic_end_to_end(tmp_path, monkeypatch):
    """Instrument integration logic with deterministic data; no real-data fixture needed."""
    import sys
    import types
    from src.phase7_joint_reference import expected_replica_covariances

    v1,v2 = tmp_path/'v1',tmp_path/'v2'
    (v1/'pseudo').mkdir(parents=True)
    (v1/'real').mkdir()
    v2.mkdir()
    cells=['LL','LH','HL','HH']
    qreal=np.array([11.,19.,29.,41.])/100
    qpseudo=np.array([.12,.18,.29,.41])
    for kind,q in [('real',qreal),('pseudo',qpseudo)]:
        if kind=='real':
            name='real_2x2_cells.csv'
            body='cell,generator_fraction\n'+''.join(f'{c},{x}\n' for c,x in zip(cells,q))
        else:
            name='pseudo_closure_cells.csv'
            body='cell,independent_target_truth_fraction,target_truth_neff\n'+''.join(
                f'{c},{x},100000\n' for c,x in zip(cells,q))
        (v1/kind/name).write_text(body)

    data={}
    for kind in ('pseudo','real'):
        cols=_columns_for_replicas()
        cols['weight_mc']={'sum_w':[11.,19.,29.,41.], 'sum_w2':[16.,24.,36.,44.],
                           'sum_w_times_nominal':[12.,20.,30.,40.]}
        cols['weights_nominal'].update({'sum_w2':[15.,25.,35.,45.],
                                       'sum_w_times_mc':[12.,20.,30.,40.]})
        data[kind]={'nominal':{'columns':cols}}
    (v2/'moments.json').write_text(json.dumps({'samples':data}))

    def fake_module(name,**attrs):
        mod=types.ModuleType(name)
        mod.__dict__.update(attrs)
        monkeypatch.setitem(sys.modules,name,mod)

    counts={'data_bootstrap':3,'mc_training_bootstrap':3,'nn_ensemble':3}
    fake_module('src.phase7_snapshot',verify=lambda _: {'verified':True})
    fake_module('src.phase7_v2_extract',verify_v2=lambda _: {'verified':True})

    def fake_old(sample):
        replica=expected_replica_covariances(sample['nominal']['columns'],counts)
        projection=np.eye(4)-np.ones((4,4))/4
        parts={k:matrix*(2/3) for k,matrix in replica.items()}
        parts.update({'finite_evaluation_mc':projection*2e-4,
                      'dd_unfolding':projection*1e-7,
                      'sherpa_hidden_variable':projection*1e-7})
        for i in range(23):
            parts[f'source_{i}']=projection*1e-6
        assert len(parts)==29
        return parts,{}

    def fake_wsum(sample,col,key='sum_w'):
        return np.array(sample['columns'][col][key],dtype=float)

    fake_module('src.phase7_v2_reconstruct',old_covariance_and_shifts=fake_old,wsum=fake_wsum)
    fake_module('src.phase7_divisor_audit',manifest_replica_counts=lambda _:dict(counts))
    def fake_truth(q,n):
        J=np.eye(4)-np.outer(q,np.ones(4))
        return J@np.diag(q*q/n)@J.T
    fake_module('src.phase7_target_mc',normalized_target_covariance=fake_truth)
    fake_module('src.phase7_twopoint_protocol',sample_two_point_inputs=lambda sample:
                (np.array([2.,-1.,1.,0.]),np.array([0.,1.,-1.,1.])))
    return v1,v2


def test_integrated_reproduction_guards_and_no_go(tmp_path,monkeypatch):
    from src.phase7_joint_reference import run
    v1,v2=_synthetic_end_to_end(tmp_path,monkeypatch)
    result=run(v1,v2,tmp_path/'report')
    assert result['G15']=='NO_GO' and result['G8']=='UNVERIFIED'
    assert list(result['samples'])==['pseudo','real']
    assert all(len(item['models'])==4 for item in result['samples'].values())
    assert all(item['nuisance_source_count']==29 for item in result['samples'].values())
    assert [item['source_count'] for item in result['samples']['pseudo']['models']]==[30]*4
    assert [item['source_count'] for item in result['samples']['real']['models']]==[29]*4
    assert all(s['observables']['joint_log_odds']['conditional_standard_error']>0
               for x in result['samples'].values() for s in x['models'])
    assert 'p_value' not in json.dumps(result)
    assert json.loads((tmp_path/'report'/'conditional_joint_covariance.json').read_text())==result


def test_pinned_signed_moments_execute_full_independent_comparison():
    """Actual committed v1/v2 inputs: a scientific integration gate, never a p-value."""
    from src.phase7_joint_reference import analyze
    result=analyze(__import__('pathlib').Path('data/derived/phase7-v1'),
                   __import__('pathlib').Path('data/derived/phase7-v2'))
    assert result['G15']=='NO_GO'
    assert list(result['samples'])==['pseudo','real']
    assert result['samples']['real']['replica_counts']=={
        'data_bootstrap':100,'mc_training_bootstrap':25,'nn_ensemble':100}
    assert result['samples']['pseudo']['replica_counts']['data_bootstrap']==25
    assert all(v['contrast_rank']==3 for obj in result['samples'].values() for v in obj['models'])
    assert 'p_value' not in json.dumps(result)
