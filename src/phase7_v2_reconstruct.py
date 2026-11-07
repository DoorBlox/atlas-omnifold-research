"""Continuity audit: reconstruct v1 provisional 2x2 covariances from signed v2 moments.

No new uncertainty prescription, unfolding, p-value or significance is inferred.
The pseudodata-vs-generator diagnostic here is NOT the independent truth closure.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import numpy as np

from src.phase7_snapshot import verify as verify_v1
from src.phase7_v2_extract import verify_v2

SYST = ('pileup','lumi','topBackground','trackEffMain','trackEffJet','trackFake','trackPtScale',
        'muEffReco','muEffIso','muEffTrack','muEffTrig','muCalID','muCalMS','muCalResBias',
        'muCalScale','theoryPSjet','theoryPSsoft','theoryMPI','theoryPSscale',
        'theoryAlphaS','theoryQCD','theoryPDF')
REPLICAS = {'data_bootstrap':'weights_bootstrap_data',
            'mc_training_bootstrap':'weights_bootstrap_mc','nn_ensemble':'weights_ensemble'}


def norm(w):
    w = np.asarray(w,dtype=float)
    if w.shape != (4,) or not np.isfinite(w).all() or w.sum()<=0:
        raise ValueError('Invalid four-cell weighted sums')
    return w/w.sum()


def wsum(stat,column,key='sum_w'):
    try:
        return np.asarray(stat['columns'][column][key],dtype=float)
    except KeyError as e:
        raise KeyError(f'Missing required source moment: {column}/{key}') from e


def jac(h):
    h=np.asarray(h,dtype=float)
    return (np.eye(4)-np.outer(norm(h),np.ones(4)))/h.sum()


def old_covariance_and_shifts(samples):
    """Reproduce historical v1 29-source recipe; NOT endorse it as official 2D."""
    base,s,n=(samples[k] for k in ('nominal','sherpa','nonDY'))
    nominal=wsum(base,'weights_nominal')
    p=norm(nominal)
    parts={}
    shifts={}
    J=jac(nominal)
    parts['finite_evaluation_mc']=J@np.diag(wsum(base,'weights_nominal','sum_w2'))@J.T
    for family,prefix in REPLICAS.items():
        names=sorted(x for x in base['columns'] if x.startswith(prefix))
        if len(names)<2:
            raise ValueError(f'Missing replica family: {family}')
        arr=np.stack([norm(wsum(base,name)) for name in names])
        centered=arr-arr.mean(axis=0)
        parts[family]=centered.T@centered/(len(names)*(len(names) if family=='nn_ensemble' else 1))
    for name in SYST:
        shift=norm(wsum(base,'weights_'+name))-p
        shifts[name]=shift
        parts[name]=np.outer(shift,shift)
    target=wsum(base,'target_dd')
    if np.any(target<=0):
        raise ValueError('DD target has nonpositive cells')
    raw_delta=(wsum(base,'weights_dd')-target)*nominal/target
    shift=norm(nominal+raw_delta)-p
    shifts['dd_unfolding']=shift
    parts['dd_unfolding']=np.outer(shift,shift)
    for key,stat in (('sherpa_hidden_variable',s),('nonDY',n)):
        shift=norm(wsum(stat,'weights_nominal'))-p
        shifts[key]=shift
        parts[key]=np.outer(shift,shift)
    if len(parts)!=29:
        raise ValueError('Wrong reconstructed source count')
    return parts,shifts


def shared_weighted_mc_covariance(nominal):
    """Poisson-weighted-cell covariance for normalized p-q with shared events."""
    hp=wsum(nominal,'weights_nominal')
    hq=wsum(nominal,'weight_mc')
    Jp,Jq=jac(hp),jac(hq)
    spp=wsum(nominal,'weights_nominal','sum_w2')
    sqq=wsum(nominal,'weight_mc','sum_w2')
    spq=wsum(nominal,'weight_mc','sum_w_times_nominal')
    spq2=wsum(nominal,'weights_nominal','sum_w_times_mc')
    if not np.allclose(spq,spq2,rtol=1e-10,atol=1e-11):
        raise ValueError('Mixed event-weight products disagree')
    matrix=Jp@np.diag(spp)@Jp.T+Jq@np.diag(sqq)@Jq.T-Jp@np.diag(spq)@Jq.T-Jq@np.diag(spq)@Jp.T
    matrix=(matrix+matrix.T)/2
    vals=np.linalg.eigvalsh(matrix)
    if vals.min() < -1e-10*max(vals.max(),1e-24):
        raise ValueError('Shared-event finite-MC covariance is non-PSD')
    if not np.allclose(matrix@np.ones(4),0,atol=1e-11):
        raise ValueError('Shared finite-MC covariance violates normalization')
    return matrix


def observable_gradients(p,q):
    if np.any(p<=0) or np.any(q<=0):
        raise ValueError('Nonpositive shape cells for log odds')
    return {
        'mass_low':(np.array([1,1,0,0],float),np.array([1,1,0,0],float)),
        'multiplicity_low':(np.array([1,0,1,0],float),np.array([1,0,1,0],float)),
        'log_odds_ratio':(np.array([1/p[0],-1/p[1],-1/p[2],1/p[3]]),
                          np.array([1/q[0],-1/q[1],-1/q[2],1/q[3]])),
    }


def run(v1:Path,v2:Path,out:Path):
    v1,v2,out=Path(v1),Path(v2),Path(out)
    verify_v1(v1)
    verify_v2(v2)
    mom=json.loads((v2/'moments.json').read_text())
    out.mkdir(parents=True,exist_ok=True)
    report={'status':'SIGNED_MOMENTS_V1_RECONSTRUCTION_VERIFIED','G15':'NO_GO',
            'scientific_status':'old provisional 2D recipe reproduced; new 2D method NOT validated',
            'samples':{}}
    signed={}
    for kind in ('real','pseudo'):
        samples=mom['samples'][kind]
        reconstructed,shifts=old_covariance_and_shifts(samples)
        npz='source_covariances.npz' if kind=='real' else 'pseudo_source_covariances.npz'
        with np.load(v1/kind/npz,allow_pickle=False) as saved:
            if set(saved.files)!=set(reconstructed):
                raise ValueError(f'Missing/extra source family for {kind}')
            errors={name:float(np.max(np.abs(reconstructed[name]-saved[name]))) for name in saved.files}
            for name in saved.files:
                if not np.allclose(reconstructed[name],saved[name],rtol=1e-6,atol=3e-10):
                    raise ValueError(f'V2 does not reproduce {kind} covariance {name}: {errors[name]}')
            total=np.sum(list(reconstructed.values()),axis=0)
            old_total=np.sum([saved[name] for name in saved.files],axis=0)
        if not np.allclose(total,old_total,rtol=1e-6,atol=3e-10):
            raise ValueError(f'V2 total covariance drift for {kind}')
        nominal=samples['nominal']
        shared=shared_weighted_mc_covariance(nominal)
        other=total-reconstructed['finite_evaluation_mc']
        p,q=norm(wsum(nominal,'weights_nominal')),norm(wsum(nominal,'weight_mc'))
        diagnostics={}
        for observable,(gp,gq) in observable_gradients(p,q).items():
            old_se=float(np.sqrt(max(gp@total@gp,0)))
            if observable=='log_odds_ratio':
                d=float(np.log(p[0]*p[3]/(p[1]*p[2]))-np.log(q[0]*q[3]/(q[1]*q[2])))
            elif observable=='mass_low':
                d=float((p[0]+p[1])-(q[0]+q[1]))
            else:
                d=float((p[0]+p[2])-(q[0]+q[2]))
            # Individual source terms for the shared p-q comparison use the
            # correct separate p and q observable gradients.
            hp=wsum(nominal,'weights_nominal')
            hq=wsum(nominal,'weight_mc')
            ep=jac(hp).T@gp
            eq=jac(hq).T@gq
            diagpp=wsum(nominal,'weights_nominal','sum_w2')
            diagqq=wsum(nominal,'weight_mc','sum_w2')
            diagpq=wsum(nominal,'weight_mc','sum_w_times_nominal')
            mixed_var=float(np.dot(ep*ep,diagpp)+np.dot(eq*eq,diagqq)-2*np.dot(ep*eq,diagpq))
            other_var=float(gp@other@gp)
            if mixed_var < -1e-12 or other_var < -1e-12:
                raise ValueError('Negative component variance')
            vp=float(np.dot(ep*ep,diagpp))
            vq=float(np.dot(eq*eq,diagqq))
            low=other_var+(np.sqrt(max(vp,0))-np.sqrt(max(vq,0)))**2
            high=other_var+(np.sqrt(max(vp,0))+np.sqrt(max(vq,0)))**2
            if mixed_var+other_var < low-1e-11 or mixed_var+other_var > high+1e-11:
                raise ValueError('Event-level mixed moments violate Cauchy covariance bound')
            candidate_se=float(np.sqrt(max(mixed_var+other_var,0)))
            diagnostics[observable]={'delta':d,'original_measurement_only_provisional_se':old_se,
                                    'shared_event_finite_mc_candidate_se':candidate_se}
        report['samples'][kind]={'sources_reconstructed':29,
                                'reference':'nominal_generator_not_independent_pseudodata_target',
                                'max_abs_source_covariance_error':max(errors.values()),
                                'max_abs_source_errors':errors,
                                'signed_nuisance_shifts_count':len(shifts),
                                'shared_finite_mc_trace':float(np.trace(shared)),
                                'observables':diagnostics}
        signed[kind]={k:v.tolist() for k,v in shifts.items()}
    (out/'signed_source_shifts.json').write_text(json.dumps({'G15':'NO_GO','shifts':signed},indent=2)+'\n')
    (out/'v2_reconstruction_status.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--v1',type=Path,default=Path('data/derived/phase7-v1'))
    p.add_argument('--v2',type=Path,default=Path('data/derived/phase7-v2'))
    p.add_argument('--out',type=Path,default=Path('outputs/v2-audit'))
    args=p.parse_args()
    result=run(args.v1,args.v2,args.out)
    print(json.dumps({'status':result['status'],'G15':result['G15'],
                      'samples':{k:{'max_abs_source_covariance_error':v['max_abs_source_covariance_error'],
                                    'observables':v['observables']} for k,v in result['samples'].items()}},indent=2))


if __name__=='__main__':
    main()
