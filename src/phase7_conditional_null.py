"""Source-aligned R-1 conditional Gaussian null simulation, with NO real p-value.

This simulates *assumed* independent Gaussian source families and a Gaussian
normalized three-contrast residual; it is not a detector-level repeated
OmniFold closure/coverage study. The replica covariance is re-estimated from
an unbiased R-1 sample estimator in every toy, and NN covariance divided by R.
Fixed nuisance-source covariances (including Sherpa/DD assumptions) and
shared event-weight finite-MC terms are held at measured estimates.
"""
from __future__ import annotations

import argparse
import json
from math import sqrt
from pathlib import Path

import numpy as np

from src.phase7_joint_reference import CONTRAST, FAMILIES, validate_covariance

CHI3_95 = 7.814727903251179


def wilson_interval(successes, total, z=1.959963984540054):
    """Monte Carlo binomial interval only, NOT a physical coverage interval."""
    if not isinstance(total,int) or total<1 or not isinstance(successes,int) or not 0<=successes<=total:
        raise ValueError('Invalid Monte Carlo counts')
    p=successes/total
    d=1+z*z/total
    center=(p+z*z/(2*total))/d
    half=z*sqrt(p*(1-p)/total+z*z/(4*total*total))/d
    return [0.0 if successes==0 else float(max(0,center-half)),
            1.0 if successes==total else float(min(1,center+half))]


def _sqrt_psd(matrix):
    c=(matrix+matrix.T)/2
    eigen, vectors=np.linalg.eigh(c)
    if eigen[0]<-1e-10*max(abs(eigen).max(),1e-20):
        raise ValueError('PSD violation in conditional source covariance')
    return (vectors*np.sqrt(np.maximum(eigen,0.)))@vectors.T


def toy_study(components,replica_counts,*,toys=5000,seed=20261107,batch=256):
    """Null draws are independent of simulated replica covariance estimates.

    The supplied C_replica includes the actual sample R-1 estimator and NN /R,
    so the true per-replica Gaussian covariance is C_replica*(R for NN else 1).
    Plug-in covariance estimates divide the centered sum by (R-1), NOT R.
    """
    if toys<500 or batch<1:
        raise ValueError('At least 500 toys and positive batch required')
    if set(replica_counts)!=set(FAMILIES):
        raise ValueError('Incorrect replica families')
    if any(type(n) is not int or n<2 for n in replica_counts.values()):
        raise ValueError('Invalid replica count')
    if not set(FAMILIES)<=set(components):
        raise ValueError('Missing replica covariance component(s)')
    if not components:
        raise ValueError('Missing source covariance')
    comp={name:CONTRAST@validate_covariance(matrix)@CONTRAST.T
          for name,matrix in components.items()}
    total=sum(comp.values())
    eig=np.linalg.eigvalsh(total)
    if eig[0]<=1e-10*max(eig[-1],1e-20):
        raise ValueError('Rank deficient three-contrast model')
    stable=sum((v for k,v in comp.items() if k not in FAMILIES),np.zeros((3,3)))
    sqrt_total=_sqrt_psd(total)
    inv_total=np.linalg.inv(total)
    replica_samplers={name:(replica_counts[name],
                            (replica_counts[name] if name=='nn_ensemble' else 1),
                            _sqrt_psd(comp[name]*(replica_counts[name] if name=='nn_ensemble' else 1)))
                      for name in FAMILIES}
    rng=np.random.default_rng(seed)
    known=[]; plug=[]
    for start in range(0,toys,batch):
        n=min(batch,toys-start)
        z=rng.normal(size=(n,3))@sqrt_total.T
        known.append(np.einsum('ni,ij,nj->n',z,inv_total,z))
        estimated=np.broadcast_to(stable,(n,3,3)).copy()
        for R,div,root in replica_samplers.values():
            draws=rng.normal(size=(n,R,3))@root.T
            centered=draws-draws.mean(axis=1,keepdims=True)
            estimated+=np.einsum('bri,brj->bij',centered,centered)/((R-1)*div)
        if np.any(np.linalg.eigvalsh(estimated)[:,0]<=0):
            raise ValueError('Rank deficient re-estimated plugin covariance')
        solved=np.linalg.solve(estimated,z[...,None])[...,0]
        plug.append(np.einsum('ni,ni->n',z,solved))
    known=np.concatenate(known); plug=np.concatenate(plug)
    hits=int(np.count_nonzero(plug>CHI3_95))
    return {'model':'INDEPENDENT_GAUSSIAN_SOURCE_AND_REPLICA_TOY',
            'covariance_estimator':'SAMPLE_DIVISOR_R_MINUS_ONE',
            'nn_ensemble_mean_covariance_divisor':replica_counts['nn_ensemble'],
            'replica_counts':dict(replica_counts),
            'toys':int(toys),'seed':int(seed),'batch':int(batch),
            'reference_chi3_95_threshold':CHI3_95,
            'simulated_known_cov_rejection_fraction':float(np.mean(known>CHI3_95)),
            'simulated_rejection_fraction':hits/toys,
            'simulated_plugin_cov_95th_percentile':float(np.quantile(plug,.95)),
            'simulated_known_cov_95th_percentile':float(np.quantile(known,.95)),
            'simulated_plugin_rejection_95pct_mc_interval':wilson_interval(hits,toys),
            'G8':'CONDITIONAL_GAUSSIAN_ONLY','G15':'NO_GO',
            'limitations':'Gaussian assumed true; estimator independent of observed residual; fixed non-replica components; no repeated physical unfolding, detector-level validation, or real-data p-value'}


def run(v1:Path,v2:Path,out:Path,*,toys=5000,seed=20261107):
    from src.phase7_joint_reference import analyze
    state,scenarios=analyze(v1,v2,return_components=True)
    # Pre-specified pseudodata models first; observed discrepancies are never
    # fed into toy generation or used for post-hoc model selection.
    results={}
    for index,kind in enumerate(('pseudo','real')):
        counts=state['samples'][kind]['replica_counts']
        results[kind]={}
        for j,(scenario,parts) in enumerate(scenarios[kind].items()):
            results[kind][scenario]=toy_study(parts,counts,toys=toys,seed=seed+10*index+j)
    report={'status':'EXECUTED_GAUSSIAN_MODEL_CONDITIONAL_CALIBRATION_NOT_ATLAS_COVERAGE',
            'scientific_observation':'No comparison statistic or real-data p-value computed in this module',
            'model_order':['pseudo','real'],
            'source_covariance':'direct v2 sample R-1; shared real event support; independent pseudo truth',
            'scenarios':results,
            'G5':'PROVISIONAL','G8':'CONDITIONAL_TOYS_ONLY','G12':'UNVERIFIED','G15':'NO_GO',
            'inference_permission':'NO_GO'}
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'conditional_gaussian_toys.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--v1',type=Path,default=Path('data/derived/phase7-v1'))
    p.add_argument('--v2',type=Path,default=Path('data/derived/phase7-v2'))
    p.add_argument('--out',type=Path,default=Path('outputs/conditional-toys'))
    p.add_argument('--toys',type=int,default=5000)
    p.add_argument('--seed',type=int,default=20261107)
    args=p.parse_args()
    res=run(args.v1,args.v2,args.out,toys=args.toys,seed=args.seed)
    print(json.dumps({'status':res['status'],'G15':res['G15'],
        'toy_rejection_rates':{k:{name:round(v['simulated_rejection_fraction'],4)
             for name,v in scenarios.items()} for k,scenarios in res['scenarios'].items()}},indent=2))


if __name__=='__main__':
    main()
