"""Synthetic tests for source-verified R-1 applied before versus after normalization."""
import json

import numpy as np
import pytest

from src.phase7_replica_projection_audit import (
    normalized_shape_covariances, raw_replica_stack, covariance_comparison, run)


def test_constant_total_exactly_matches_first_order_jacobian():
    h=np.array([10.,20.,30.,40.])
    x=np.array([[11.,19.,29.,41.],[9.,21.,31.,39.],[10.5,19.5,29.5,40.5]])
    assert np.all(x.sum(axis=1)==h.sum())
    nonlinear,projected=normalized_shape_covariances(h,x)
    np.testing.assert_allclose(nonlinear,projected,atol=1e-16)


def test_varying_replica_normalization_shows_real_difference():
    h=np.array([10.,20.,30.,40.])
    x=np.array([[16.,21.,33.,42.],[8.,18.,29.,31.],[10.,18.,32.,40.]],float)
    nonlinear,projected=normalized_shape_covariances(h,x)
    assert np.linalg.norm(projected-nonlinear)>1e-9
    assert np.linalg.eigvalsh(nonlinear).min()>=-1e-15
    assert np.linalg.eigvalsh(projected).min()>=-1e-15
    for c in (nonlinear,projected):
        np.testing.assert_allclose(c@np.ones(4),0,atol=1e-15)


def test_nn_division_by_r_is_independent_of_convention():
    h=np.array([10.,20.,30.,40.]);x=np.array([[11.,19.,28.,42.],[9.,21.,33.,37.],[10.,20.,29.,41.]])
    n,p=normalized_shape_covariances(h,x)
    nn,pn=normalized_shape_covariances(h,x,ensemble=True)
    np.testing.assert_allclose(nn,n/len(x),atol=1e-18)
    np.testing.assert_allclose(pn,p/len(x),atol=1e-18)


def test_stack_rejects_replica_gaps_extra_and_malformed():
    p='weights_bootstrap_data'
    cols={f'{p}_{i}':{'sum_w':[1.,2.,3.,4.]} for i in range(3)}
    assert raw_replica_stack(cols,p,3).shape==(3,4)
    del cols[f'{p}_1']
    with pytest.raises(ValueError,match='Missing or extra'):
        raw_replica_stack(cols,p,3)
    cols[f'{p}_1']={'sum_w':[1.,2.,3.,4.]}
    cols[f'{p}_3']={'sum_w':[1.,2.,3.,4.]}
    with pytest.raises(ValueError,match='Missing or extra'):
        raw_replica_stack(cols,p,3)
    del cols[f'{p}_3'];cols[f'{p}_bad']={'sum_w':[1.,2.,3.,4.]}
    with pytest.raises(ValueError,match='Malformed'):
        raw_replica_stack(cols,p,3)


def test_invalid_replica_totals_and_malformed_covariance_fail_closed():
    h=np.array([10.,20.,30.,40.]);x=np.array([[1.,2.,3.,4.],[-1.,-2.,-3.,-4.]])
    with pytest.raises(ValueError,match='positive'):
        normalized_shape_covariances(h,x)
    with pytest.raises(ValueError,match='four-cell'):
        normalized_shape_covariances([1.,2.],np.ones((3,4)))
    with pytest.raises(ValueError,match='Nonpositive'):
        covariance_comparison(np.zeros((4,4)),np.zeros((4,4)),np.ones(4))
    with pytest.raises(ValueError,match='4x4'):
        covariance_comparison(np.ones((3,3)),np.zeros((4,4)),np.ones(4))


def test_correction_report_values_are_numeric_only_and_no_inference():
    h=np.array([10.,20.,30.,40.])
    x=np.array([[11.,19.,28.,42.],[9.,21.,33.,37.],[10.,20.,29.,41.]])
    a,b=normalized_shape_covariances(h,x)
    p=h/h.sum();grad=np.array([1/p[0],-1/p[1],-1/p[2],1/p[3]])
    z=covariance_comparison(a,b,grad)
    assert z['relative_frobenius_difference_percent']>=0
    assert z['trace_nonlinear_normalize_each']>0
    assert z['trace_linearized_raw_projection']>0
    assert 'p_value' not in json.dumps(z)


def test_pinned_real_and_pseudo_v2_projection_conventions(tmp_path):
    from pathlib import Path
    result=run(Path('data/derived/phase7-v1'),Path('data/derived/phase7-v2'),tmp_path)
    assert result['G15']=='NO_GO'
    assert list(result['samples'])==['pseudo','real']
    assert result['samples']['real']['actual_replica_counts']['data_bootstrap']==100
    assert result['samples']['pseudo']['actual_replica_counts']['data_bootstrap']==25
    assert all(len(s['three_replica_family_comparisons'])==3 for s in result['samples'].values())
    assert all(len(s['four_prespecified_source_model_comparisons'])==4 for s in result['samples'].values())
    assert 'p_value' not in json.dumps(result)


def test_mocked_end_to_end_reports_all_prespecified_models(tmp_path, monkeypatch):
    """Test wiring and source identity without external ATLAS files in local env."""
    import sys
    import types
    from src.phase7_replica_projection_audit import CONTRAST
    r=3
    h=np.array([10.,20.,30.,40.]);p=h/h.sum()
    columns={'weights_nominal':{'sum_w':h.tolist()}}
    for prefix in ('weights_bootstrap_data','weights_bootstrap_mc','weights_ensemble'):
        for i in range(r):
            x=h + (i-1)*np.array([.5,-.4,.2,-.1])
            columns[f'{prefix}_{i}']={'sum_w':x.tolist()}
    raw={family:raw_replica_stack(columns, prefix, r) for family,prefix in
         (('data_bootstrap','weights_bootstrap_data'),
          ('mc_training_bootstrap','weights_bootstrap_mc'),('nn_ensemble','weights_ensemble'))}
    parts={family:normalized_shape_covariances(h,stack,ensemble=(family=='nn_ensemble'))[0]
           for family,stack in raw.items()}
    P=np.eye(4)-np.ones((4,4))/4
    parts['finite_evaluation_mc']=P*1e-4
    models={kind:{scenario:{key:val.copy() for key,val in parts.items()}
                  for scenario in ('both_fully_correlated','dd_decorrelated_sherpa_correlated',
                                   'dd_correlated_sherpa_decorrelated','both_four_bin_decorrelated')}
            for kind in ('pseudo','real')}
    q=np.array([.13,.17,.27,.43]);assert q.sum()==1
    def diag(p,q,components):
        c=sum(components.values());c3=CONTRAST@c@CONTRAST.T
        z=CONTRAST@(p-q)
        val=float(z@np.linalg.solve(c3,z))
        return {'uncalibrated_quadratic_not_a_pvalue':val,'covariance_trace':float(np.trace(c)),
                'contrast_rank':3}
    state={'samples':{kind:{'replica_counts':{family:r for family in raw},
            'models':[{'scenario':name,
                       'uncalibrated_quadratic_not_a_pvalue':diag(p,q,components)['uncalibrated_quadratic_not_a_pvalue'],
                       'covariance_trace':diag(p,q,components)['covariance_trace']}
                      for name,components in models[kind].items()]}
            for kind in ('pseudo','real')}}
    source_dir=tmp_path/'v2';source_dir.mkdir()
    (source_dir/'moments.json').write_text(json.dumps({'samples':{kind:{'nominal':{'columns':columns}}
                                    for kind in ('pseudo','real')}}))
    v1=tmp_path/'v1'
    for kind in ('pseudo','real'):
        folder=v1/kind;folder.mkdir(parents=True)
        filename='pseudo_closure_cells.csv' if kind=='pseudo' else 'real_2x2_cells.csv'
        field='independent_target_truth_fraction' if kind=='pseudo' else 'generator_fraction'
        with (folder/filename).open('w') as f:
            f.write(f'cell,{field}\n')
            for label,x in zip(('LL','LH','HL','HH'),q):
                f.write(f'{label},{x}\n')
    m=types.ModuleType('src.phase7_joint_reference')
    m.analyze=lambda *args,**kwargs:(state,models)
    m.contrast_diagnostics=diag
    monkeypatch.setitem(sys.modules,'src.phase7_joint_reference',m)
    n=types.ModuleType('src.phase7_v2_reconstruct')
    n.wsum=lambda nominal,name:np.asarray(nominal['columns'][name]['sum_w'],float)
    n.norm=lambda x:np.asarray(x,float)/np.sum(x)
    monkeypatch.setitem(sys.modules,'src.phase7_v2_reconstruct',n)
    from src.phase7_replica_projection_audit import run
    report=run(v1,source_dir,tmp_path/'out')
    assert report['G15']=='NO_GO'
    assert len(report['samples']['pseudo']['four_prespecified_source_model_comparisons'])==4
    assert len(report['samples']['real']['three_replica_family_comparisons'])==3
    assert all(np.isfinite(fam['relative_trace_change_percent'])
               for item in report['samples'].values()
               for fam in item['three_replica_family_comparisons'].values())
    assert json.loads((tmp_path/'out'/'replica_projection_audit.json').read_text()) == report
