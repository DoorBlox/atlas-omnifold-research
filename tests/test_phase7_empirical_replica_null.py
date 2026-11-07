"""Hybrid null samples official bootstrap shape offsets, not independent unfoldings."""
import json
import numpy as np
import pytest

from src.phase7_empirical_replica_null import (
    replica_shape_arrays,
    replicate_diagnostics,
    hybrid_toy,
    run,
)
from src.phase7_joint_reference import expected_replica_covariances

COUNTS={'data_bootstrap':5,'mc_training_bootstrap':5,'nn_ensemble':8}


def _columns():
    h=np.array([10.,20.,30.,40.])
    cols={}
    for family,prefix in {'data_bootstrap':'weights_bootstrap_data',
                          'mc_training_bootstrap':'weights_bootstrap_mc',
                          'nn_ensemble':'weights_ensemble'}.items():
        for i in range(COUNTS[family]):
            shift=np.array([i%3-1,(-1)**i, (i%4)-1.5, -(i%5)/4])*.15
            cols[f'{prefix}_{i}']={'sum_w':(h+shift).tolist()}
    return cols


def _sources():
    cols=_columns()
    parts=expected_replica_covariances(cols,COUNTS)
    P=np.eye(4)-np.ones((4,4))/4
    parts.update({'fixed_gaussian':P*0.00002})
    return cols,parts


def test_shapes_are_normalized_and_sources_match_corrected_covariance():
    cols,parts=_sources()
    arrays=replica_shape_arrays(cols,COUNTS)
    for name,x in arrays.items():
        np.testing.assert_allclose(x.sum(axis=1),1.,atol=1e-14)
        sample=np.cov(x,rowvar=False,ddof=1)
        expected=sample/(len(x) if name=='nn_ensemble' else 1)
        np.testing.assert_allclose(parts[name],expected,atol=1e-17)
    stats=replicate_diagnostics(arrays)
    assert all(x['replicas']>=5 for x in stats.values())
    assert all(len(x['contrast_skewness'])==3 for x in stats.values())
    assert all(len(x['contrast_excess_kurtosis'])==3 for x in stats.values())


def test_empirical_null_runs_without_observed_statistic_or_pvalue():
    cols,parts=_sources()
    x=replica_shape_arrays(cols,COUNTS)
    a=hybrid_toy(parts,x,toys=1000,seed=17,batch=128)
    b=hybrid_toy(parts,x,toys=1000,seed=17,batch=128)
    assert a==b
    assert a['replica_sampling']=='EMPIRICAL_CENTERED_WITH_REPLICA_SAMPLE_COVARIANCE_SCALING'
    assert 0<=a['hybrid_null_rejection_fraction']<=1
    assert a['G15']=='NO_GO'
    assert 'p_value' not in json.dumps(a)


def test_wrong_replica_family_and_covariance_fail_closed():
    cols,parts=_sources();arrays=replica_shape_arrays(cols,COUNTS)
    with pytest.raises(ValueError,match='replica'):
        replica_shape_arrays({k:v for k,v in cols.items() if not k.endswith('_0')},COUNTS)
    with pytest.raises(ValueError,match='covariance'):
        hybrid_toy({**parts,'data_bootstrap':(np.eye(4)-np.ones((4,4))/4)*.1},arrays,toys=500)
    with pytest.raises(ValueError,match='500'):
        hybrid_toy(parts,arrays,toys=2)


def test_hybrid_driver_writes_pseudodata_first_and_remains_no_go(tmp_path,monkeypatch):
    import src.phase7_joint_reference as joint
    cols,parts=_sources()
    (tmp_path/'v2').mkdir()
    samples={k:{'nominal':{'columns':cols}} for k in ('pseudo','real')}
    (tmp_path/'v2'/'moments.json').write_text(json.dumps({'samples':samples}))
    state={'samples':{k:{'replica_counts':COUNTS} for k in ('pseudo','real')}}
    models={k:{'both_fully_correlated':parts} for k in ('pseudo','real')}
    monkeypatch.setattr(joint,'analyze',lambda *a,**k:(state,models))
    result=run(tmp_path/'v1',tmp_path/'v2',tmp_path/'out',toys=500,seed=31)
    assert list(result['samples'])==['pseudo','real']
    assert all(x['models']['both_fully_correlated']['G15']=='NO_GO' for x in result['samples'].values())
    assert result['G8']=='HYBRID_SOURCE_REPLICA_NULL_ONLY'
    assert 'p_value' not in json.dumps(result)
    assert json.loads((tmp_path/'out'/'empirical_replica_null.json').read_text())==result
