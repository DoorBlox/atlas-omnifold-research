"""Provisional v1 covariance continuity and shared finite-MC products."""
import numpy as np
import pytest

from src.phase7_v2_reconstruct import (
    old_covariance_and_shifts, shared_weighted_mc_covariance, jac, SYST, REPLICAS,
)


def column(w, *, sq=None, mixed_mc=None, mixed_nominal=None):
    w=np.asarray(w,dtype=float)
    return {
        'sum_w':w.tolist(),
        'sum_w2':np.asarray(sq if sq is not None else w*w).tolist(),
        'sum_w_times_mc':np.asarray(mixed_mc if mixed_mc is not None else w*w).tolist(),
        'sum_w_times_nominal':np.asarray(mixed_nominal if mixed_nominal is not None else w*w).tolist(),
    }


def test_proportional_shared_event_weights_cancel_normalized_finite_mc():
    q=np.array([1.,2.,3.,4.])
    sq=q*q
    nom={'columns':{
        'weight_mc':column(q,sq=sq,mixed_nominal=2*sq),
        'weights_nominal':column(2*q,sq=4*sq,mixed_mc=2*sq),
    }}
    np.testing.assert_allclose(shared_weighted_mc_covariance(nom),
                               np.zeros((4,4)),atol=1e-15)


def test_shared_event_covariance_equals_direct_event_sum():
    wq=np.array([[1.,2.],[2.,3.],[1.,4.],[3.,2.]])
    wp=np.array([[1.,4.],[3.,1.],[2.,2.],[3.,3.]])
    hq, hp=wq.sum(axis=1), wp.sum(axis=1)
    q2,p2=np.sum(wq*wq,axis=1),np.sum(wp*wp,axis=1)
    pq=np.sum(wp*wq,axis=1)
    nom={'columns':{
        'weight_mc':column(hq,sq=q2,mixed_nominal=pq),
        'weights_nominal':column(hp,sq=p2,mixed_mc=pq),
    }}
    got=shared_weighted_mc_covariance(nom)
    Jp,Jq=jac(hp),jac(hq)
    target=np.zeros((4,4))
    for cell in range(4):
        for event in range(2):
            v=Jp[:,cell]*wp[cell,event]-Jq[:,cell]*wq[cell,event]
            target+=np.outer(v,v)
    np.testing.assert_allclose(got,target,atol=1e-15)
    assert np.linalg.eigvalsh(got).min()>-1e-14


def test_reconstruct_29_provisional_sources_and_preserve_signed_shifts():
    h=np.array([10.,20.,30.,40.])
    cols={'weight_mc':column(h),'weights_nominal':column(h),
          'weights_dd':column(1.02*h),'target_dd':column(h)}
    for i,name in enumerate(SYST):
        cols['weights_'+name]=column(h*(1+.001*(i+1)*np.array([1.,0.,0.,0.])))
    for family,prefix in REPLICAS.items():
        for i in range(3):
            cols[f'{prefix}_{i}']=column(h*(1+.01*(i-1)*np.array([1.,0.,0.,0.])))
    parts,shifts=old_covariance_and_shifts({
        'nominal':{'columns':cols},
        'sherpa':{'columns':{'weights_nominal':column(h*np.array([1.01,.99,1.01,1]))}},
        'nonDY':{'columns':{'weights_nominal':column(h*np.array([1,.99,1.02,1]))}},
    })
    assert len(parts)==29 and len(shifts)==25
    np.testing.assert_allclose(shifts['theoryQCD'].sum(),0.,atol=1e-15)
    assert np.linalg.norm(shifts['sherpa_hidden_variable'])>0
    assert all(c.shape==(4,4) for c in parts.values())
    assert all(np.linalg.eigvalsh(c).min()>-1e-12 for c in parts.values())


def test_missing_source_fails_closed():
    with pytest.raises(KeyError,match='weights_nominal'):
        old_covariance_and_shifts({'nominal':{'columns':{}},'sherpa':{},'nonDY':{}})
