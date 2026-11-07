"""Hybrid conditional null: empirical released replica offsets + fixed Gaussian sources.

The actual ATLAS replica vectors are bootstraps/ensembles of ONE unfolded
measurement, NOT independent detector-level pseudo-experiments. This is a
non-Gaussian sensitivity probe only, with no real-data p-value or G15 GO.
"""
from __future__ import annotations

import argparse
import json
from math import sqrt
from pathlib import Path
import numpy as np

from src.phase7_joint_reference import (
    CONTRAST, FAMILIES, expected_replica_covariances, validate_covariance,
)
from src.phase7_conditional_null import CHI3_95, _sqrt_psd, wilson_interval


def replica_shape_arrays(columns, counts):
    """Produce normalized four-cell shape vectors, validating exact replica IDs."""
    if set(counts)!=set(FAMILIES):
        raise ValueError('Unexpected replica family names')
    # Integrity guard also catches stray, skipped or duplicate numeric indices.
    expected_replica_covariances(columns, counts)
    output={}
    for name,prefix in FAMILIES.items():
        values=[]
        for i in range(counts[name]):
            v=np.asarray(columns[f'{prefix}_{i}']['sum_w'],dtype=float)
            values.append(v/v.sum())
        output[name]=np.stack(values)
    return output


def replicate_diagnostics(arrays):
    """Descriptive skew and excess kurtosis in three contrast coordinates.

    These sample moments (especially with only 25 replicas) are NOT formal
    tests of normality and MUST NOT select the nuisance-correlation model.
    """
    out={}
    for name,x in arrays.items():
        x=np.asarray(x,float)
        if x.ndim!=2 or x.shape[1]!=4 or len(x)<2 or not np.isfinite(x).all():
            raise ValueError('Invalid four-cell replica shapes')
        z=(x-x.mean(axis=0))@CONTRAST.T
        m2=np.mean(z*z,axis=0)
        with np.errstate(divide='ignore',invalid='ignore'):
            skew=np.divide(np.mean(z**3,axis=0),m2**1.5,out=np.zeros(3),where=m2>0)
            kurt=np.divide(np.mean(z**4,axis=0),m2*m2,out=np.zeros(3),where=m2>0)-3
        out[name]={'replicas':len(x),
                   'contrast_skewness':skew.tolist(),
                   'contrast_excess_kurtosis':kurt.tolist(),
                   'normality_claim':'NONE_DESCRIPTIVE_SMALL_REPLICA_SAMPLE'}
    return out


def hybrid_toy(components,replica_shapes,*,toys=10000,seed=20261107,batch=512):
    """Bootstrap measured shapes under centered conditional null.

    Empirical sampling covariance matches R-1 source matrices exactly after
    scaling by sqrt(R/(R-1)). NN mean samples R draws, then gets the same
    finite-population correction; all other components use Gaussian draws.
    """
    if toys<500 or batch<1:
        raise ValueError('At least 500 toys and positive batch required')
    if set(replica_shapes)!=set(FAMILIES) or not set(FAMILIES)<=set(components):
        raise ValueError('Missing replica family')
    comps={k:CONTRAST@validate_covariance(c)@CONTRAST.T for k,c in components.items()}
    total=sum(comps.values())
    eig=np.linalg.eigvalsh(total)
    if eig[0]<=1e-10*max(eig[-1],1e-20):
        raise ValueError('Rank-deficient contrast covariance')
    inv_total=np.linalg.inv(total)
    centered={}
    for name,arr in replica_shapes.items():
        arr=np.asarray(arr,float)
        if arr.ndim!=2 or arr.shape[1]!=4 or len(arr)<2 or not np.isfinite(arr).all():
            raise ValueError('Invalid replica-shape array')
        if not np.allclose(arr.sum(axis=1),1.,atol=1e-10):
            raise ValueError('Unnormalized replica-shape array')
        n=len(arr);div=n if name=='nn_ensemble' else 1
        actual=np.cov(arr,rowvar=False,ddof=1)/div
        if not np.allclose(actual,components[name],atol=1e-14,rtol=1e-8):
            raise ValueError(f'Empirical replica covariance does not equal reference-aligned source: {name}')
        centered[name]=(arr-arr.mean(axis=0))@CONTRAST.T
    fixed=sum((c for k,c in comps.items() if k not in FAMILIES),np.zeros((3,3)))
    root=_sqrt_psd(fixed)
    rng=np.random.default_rng(seed)
    stat=[]
    for start in range(0,toys,batch):
        n=min(toys-start,batch)
        z=rng.standard_normal(size=(n,3))@root.T
        for name,x in centered.items():
            R=len(x)
            if name=='nn_ensemble':
                idx=rng.integers(R,size=(n,R))
                pert=x[idx].mean(axis=1)*sqrt(R/(R-1))
            else:
                idx=rng.integers(R,size=n)
                pert=x[idx]*sqrt(R/(R-1))
            z=z+pert
        stat.append(np.einsum('bi,ij,bj->b',z,inv_total,z))
    statistics=np.concatenate(stat)
    hits=int(np.sum(statistics>CHI3_95))
    return {'model':'FIXED_GAUSSIAN_NONREPLICA_PLUS_ACTUAL_CENTERED_ATLAS_REPLICA_SHAPES',
            'replica_sampling':'EMPIRICAL_CENTERED_WITH_REPLICA_SAMPLE_COVARIANCE_SCALING',
            'simulations':int(toys),'seed':int(seed),
            'hybrid_null_rejection_fraction':hits/toys,
            'hybrid_null_95th_percentile':float(np.quantile(statistics,.95)),
            'hybrid_null_rejection_95pct_mc_interval':wilson_interval(hits,toys),
            'reference_three_contrast_threshold':CHI3_95,
            'G8':'HYBRID_CONDITIONAL_NOT_PHYSICAL_COVERAGE','G15':'NO_GO',
            'limitations':'Replica vectors re-use one real/pseudodata unfolding; fixed Gaussian non-replica sources; NN empirical mean approximation; not independent full detector-level experiments or real-data p-value'}


def run(v1:Path,v2:Path,out:Path,*,toys=10000,seed=20261107):
    from src.phase7_joint_reference import analyze
    state,models=analyze(v1,v2,return_components=True)
    moments=json.loads((Path(v2)/'moments.json').read_text(encoding='utf-8'))
    results={}
    for k,kind in enumerate(('pseudo','real')):
        counts=state['samples'][kind]['replica_counts']
        arrays=replica_shape_arrays(moments['samples'][kind]['nominal']['columns'],counts)
        current={}
        for j,(name,parts) in enumerate(models[kind].items()):
            current[name]=hybrid_toy(parts,arrays,toys=toys,seed=seed+10*k+j)
        results[kind]={'replica_moments':replicate_diagnostics(arrays),'models':current}
    result={'status':'EXECUTED_HYBRID_EMPIRICAL_REPLICA_CONDITIONAL_NULL_NOT_ATLAS_COVERAGE',
            'source':'official frozen v2 independent 100/25 bootstrap and 100 NN ensemble shapes',
            'sample_order':['pseudo','real'],'samples':results,
            'limitations':'No independent unfolding repetitions; cannot establish ATLAS coverage or choose source model based on real data',
            'G5':'PROVISIONAL','G8':'HYBRID_SOURCE_REPLICA_NULL_ONLY',
            'G12':'UNVERIFIED','G15':'NO_GO','inference_permission':'NO_GO'}
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'empirical_replica_null.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--v1',type=Path,default=Path('data/derived/phase7-v1'))
    parser.add_argument('--v2',type=Path,default=Path('data/derived/phase7-v2'))
    parser.add_argument('--out',type=Path,default=Path('outputs/replica-null'))
    parser.add_argument('--toys',type=int,default=10000)
    args=parser.parse_args()
    result=run(args.v1,args.v2,args.out,toys=args.toys)
    print(json.dumps({'status':result['status'],'G15':result['G15'],
                      'hybrid_rejection':{kind:{name:round(stat['hybrid_null_rejection_fraction'],4)
                          for name,stat in obj['models'].items()}
                          for kind,obj in result['samples'].items()}},indent=2))


if __name__=='__main__':
    main()
