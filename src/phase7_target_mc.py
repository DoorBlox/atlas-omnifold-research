"""Independent pseudodata truth finite-MC covariance from frozen sufficient stats.

Assumes independent weighted-Poisson target-cell counts, with the reference
and unfolded pseudodata treated independent for an illustrative combined SE.
Uses separate log-odds gradients at measured and truth shapes; no p-values.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import numpy as np

from src.phase7_snapshot import verify as verify_snapshot

NAMES = ("mass_low","multiplicity_low","log_odds_ratio")


def _shape(x: np.ndarray) -> np.ndarray:
    v=np.asarray(x,dtype=float)
    if v.shape!=(4,) or not np.isfinite(v).all() or np.min(v)<0 or not np.isclose(v.sum(),1.,atol=1e-8):
        raise ValueError("Invalid normalized shape")
    return v


def normalized_target_covariance(shape: np.ndarray, neff: np.ndarray) -> np.ndarray:
    """C=(I-q1^T) diag(q_i^2/N_eff,i) (I-1q^T)."""
    q=_shape(shape)
    n=np.asarray(neff,dtype=float)
    if n.shape!=(4,) or not np.isfinite(n).all() or np.min(n)<=0:
        raise ValueError("Target effective counts must be strictly positive")
    m=np.eye(4)-np.outer(q,np.ones(4))
    result=m@np.diag(q*q/n)@m.T
    if not np.allclose(result@np.ones(4),0.,atol=1e-12):
        raise ValueError("Normalized covariance null-mode violated")
    return result


def gradients(shape:np.ndarray)->dict[str,np.ndarray]:
    p=_shape(shape)
    if np.min(p)<=0:
        raise ValueError("Log-odds requires strictly positive four-cell fractions")
    return {"mass_low":np.array([1.,1.,0.,0.]),
            "multiplicity_low":np.array([1.,0.,1.,0.]),
            "log_odds_ratio":np.array([1/p[0],-1/p[1],-1/p[2],1/p[3]])}


def analyze_target(snapshot:Path,out:Path)->dict:
    snapshot,out=Path(snapshot),Path(out)
    proof=verify_snapshot(snapshot)
    with (snapshot/'pseudo'/'pseudo_closure_cells.csv').open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    if [r['cell'] for r in rows]!=['LL','LH','HL','HH']:
        raise ValueError('Unexpected four-cell order')
    p=_shape(np.array([float(r['pseudo_unfolded_fraction']) for r in rows]))
    q=_shape(np.array([float(r['independent_target_truth_fraction']) for r in rows]))
    ne=np.array([float(r['target_truth_neff']) for r in rows])
    Ct=normalized_target_covariance(q,ne)
    with np.load(snapshot/'pseudo'/'pseudo_source_covariances.npz',allow_pickle=False) as z:
        if len(z.files)!=29:
            raise ValueError('Missing provisional unfolded measurement source families')
        Cp=sum((z[name] for name in z.files),np.zeros((4,4)))
    if not np.allclose(Cp@np.ones(4),0.,atol=1e-10):
        raise ValueError('Unfolded covariance null mode violated')
    gp,gq=gradients(p),gradients(q)
    outputs=[]
    for name in NAMES:
        vp=float(gp[name]@Cp@gp[name])
        vt=float(gq[name]@Ct@gq[name])
        if not np.isfinite(vp+vt) or vp<=0 or vt<0:
            raise ValueError('Invalid delta-method variance')
        outputs.append({
            'observable':name,
            'measurement_provisional_se':float(np.sqrt(vp)),
            'target_mc_se':float(np.sqrt(vt)),
            'combined_se_independence_model':float(np.sqrt(vp+vt)),
            'target_share_of_combined_variance_percent':float(100*vt/(vp+vt)),
            'measurement_and_target_gradients_evaluated_separately':True,
        })
    odds=next(x for x in outputs if x['observable']=='log_odds_ratio')
    exact=np.sqrt(np.sum(1./ne))
    if not np.isclose(odds['target_mc_se'],exact,rtol=1e-12,atol=1e-14):
        raise ValueError('Independent-cell log-odds effective-count identity failed')
    report={
        'status':'CORRECTED_TRUTH_GRADIENT_CONDITIONAL_FINITE_MC_ONLY',
        'input_provenance':proof,
        'selected_target_rows':int(sum(int(r['target_rows']) for r in rows)),
        'target_truth_neff_by_cell':ne.tolist(),
        'metrics':outputs,
        'important_assumption':'Independent weighted Poisson truth-bin sums; unfolded pseudodata and truth treated independent for the illustrative combined SE',
        'limitations':'Other measurement systematics provisional; no joint cross-covariance or repeated-sampling experimental closure',
        'G5':'UNVERIFIED','G8':'MODEL_CONDITIONAL_ONLY',
        'G11':'SINGLE_TRUTH_COMPARISON_ONLY','G15':'NO_GO',
        'inference_permission':'NO_GO',
    }
    out.mkdir(parents=True,exist_ok=True)
    (out/'target_mc_precision.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def main()->None:
    parser=argparse.ArgumentParser()
    parser.add_argument('--snapshot',type=Path,default=Path('data/derived/phase7-v1'))
    parser.add_argument('--out',type=Path,default=Path('outputs'))
    args=parser.parse_args()
    report=analyze_target(args.snapshot,args.out)
    print(json.dumps({'status':report['status'],'metrics':report['metrics'],'G15':report['G15']},indent=2))


if __name__=='__main__':
    main()
