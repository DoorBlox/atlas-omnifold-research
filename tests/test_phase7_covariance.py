"""Synthetic-only tests for ATLAS source-aware 2x2 covariance; no physics claims."""
import numpy as np
import pandas as pd
import pytest
from src.phase7_covariance import SYST, norm, replica_covariance, finite_mc_covariance, project, covariance_parts, diagnostics


def test_normalized_shape_covariance_null_mode():
    replicas = np.array([[.2,.3,.2,.3],[.3,.2,.3,.2],[.25,.25,.25,.25]])
    cov = replica_covariance(replicas)
    np.testing.assert_allclose(cov.sum(axis=0), 0, atol=1e-15)
    np.testing.assert_allclose(replica_covariance(replicas,3), cov/3)
    mc = finite_mc_covariance([10,20,30,40],[1,4,9,16])
    np.testing.assert_allclose(mc.sum(axis=0), 0, atol=1e-15)
    assert diagnostics({'mc':mc})[1]['contrast_rank']==3
    np.testing.assert_allclose(norm([1,2,3,4]),norm([2,4,6,8]))


def test_fixed_pandas_hdf5_source_families(tmp_path):
    n=80
    mass=np.tile([1.,1.,3.,3.],n//4)
    tracks=np.tile([1,3,1,3],n//4)
    data={'pT_trackj1':[10.]*n,'m_trackj1':mass,'Ntracks_trackj1':tracks,
          'weight_mc':np.ones(n),'weights_nominal':np.ones(n),
          'weights_dd':1+.01*(mass==1), 'target_dd':np.ones(n)}
    for i,name in enumerate(SYST):
        data['weights_'+name]=1+.001*(i+1)*(mass==1)
    for prefix in ('weights_bootstrap_data','weights_bootstrap_mc','weights_ensemble'):
        for i in range(4):
            data[f'{prefix}{i}']=1+.01*(i-2)*(tracks==1)
    path=tmp_path/'synthetic.h5'
    pd.DataFrame(data).to_hdf(path,key='df',format='fixed')
    thresholds={'mass_star':2,'tracks_star':2}
    projected,w2,q2,counts=project(path,thresholds,chunksize=9)
    assert counts.tolist()==[20]*4
    assert len(projected)==4+22+12
    np.testing.assert_allclose(q2,[20]*4)
    parts,manifest,unmapped=covariance_parts(projected,w2,
         {'weights_nominal':np.array([19.,21.,20.,20.])},
         {'weights_nominal':np.array([20.,20.,19.,21.])})
    assert len(parts)==29
    assert len(manifest)==29
    assert unmapped==[]
    total,info=diagnostics(parts)
    assert total.shape==(4,4)
    assert info['contrast_rank']==3 and info['null_mode_valid']
    with pytest.raises(ValueError,match='Missing named'):
        covariance_parts({'weights_nominal':np.ones(4)},np.ones(4),{}, {})
