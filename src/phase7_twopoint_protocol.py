"""Pre-registered ATLAS two-point correlation sensitivities for normalized 2x2 bins.

ATLAS 2024 supplemental User Guide, section 2, recommendation 5:
default fully correlated; for few bins an alternative is separate nuisances
per bin. This code is a documented two-dimensional Jacobian extension, NOT
the official CERN 2D helper, calibrated significance, or a p-value.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np

SCENARIOS=(
    ('both_fully_correlated','fully_correlated','fully_correlated'),
    ('dd_decorrelated_sherpa_correlated','four_bin_decorrelated','fully_correlated'),
    ('dd_correlated_sherpa_decorrelated','fully_correlated','four_bin_decorrelated'),
    ('both_four_bin_decorrelated','four_bin_decorrelated','four_bin_decorrelated'),
)


def _four(values, positive=False):
    x=np.asarray(values,dtype=float)
    if x.shape!=(4,) or not np.isfinite(x).all():
        raise ValueError('Expected four finite cell values')
    if positive and np.any(x<=0):
        raise ValueError('Nominal counts must be strictly positive')
    return x


def check_covariance(c):
    c=np.asarray(c,dtype=float)
    if c.shape!=(4,4) or not np.isfinite(c).all():
        raise ValueError('Expected a finite 4x4 covariance')
    if not np.allclose(c,c.T,rtol=1e-10,atol=1e-12):
        raise ValueError('Asymmetric covariance')
    if not np.allclose(c@np.ones(4),0,atol=1e-11):
        raise ValueError('Normalization null mode lost')
    eig=np.linalg.eigvalsh(c)
    if eig.min() < -1e-10*max(float(np.max(np.abs(eig))),1e-20):
        raise ValueError('Non-PSD source covariance')
    return {'is_psd':True,'normalization_null_residual':float(np.max(np.abs(c@np.ones(4))))}


def count_shift_to_covariance(nominal,delta,model):
    if model not in ('fully_correlated','four_bin_decorrelated'):
        raise ValueError('Unknown a priori source-correlation model')
    h=_four(nominal,positive=True)
    shift=_four(delta)
    J=(np.eye(4)-np.outer(h/h.sum(),np.ones(4)))/h.sum()
    c=(np.outer(J@shift,J@shift) if model=='fully_correlated' else
       J@np.diag(shift*shift)@J.T)
    c=(c+c.T)/2
    check_covariance(c)
    return c


def _sum(sample,column):
    try:
        return _four(sample['columns'][column]['sum_w'])
    except (KeyError,TypeError) as exc:
        raise ValueError(f'Missing source-weight sums: {column}') from exc


def sample_two_point_inputs(samples):
    h=_sum(samples['nominal'],'weights_nominal')
    dd=_sum(samples['nominal'],'weights_dd')
    target=_sum(samples['nominal'],'target_dd')
    alternative=_sum(samples['sherpa'],'weights_nominal')
    if np.any(target<=0):
        raise ValueError('DD target must have positive cell counts')
    return (dd-target)*h/target, alternative-h


def build_two_point_scenarios(components,nominal,delta_dd,delta_sherpa):
    required={'dd_unfolding','sherpa_hidden_variable'}
    if not required<=set(components):
        raise ValueError('Missing DD/Sherpa source')
    for c in components.values():
        check_covariance(c)
    out={}
    for name,d_model,s_model in SCENARIOS:
        parts={k:np.asarray(v,dtype=float).copy() for k,v in components.items()}
        parts['dd_unfolding']=count_shift_to_covariance(nominal,delta_dd,d_model)
        parts['sherpa_hidden_variable']=count_shift_to_covariance(nominal,delta_sherpa,s_model)
        check_covariance(sum(parts.values()))
        out[name]=parts
    return out


def analyze(v1:Path,v2:Path)->dict:
    from src.phase7_snapshot import verify as verify_v1
    from src.phase7_v2_extract import verify_v2
    from src.phase7_v2_reconstruct import old_covariance_and_shifts,wsum,norm
    verify_v1(v1)
    verify_v2(v2)
    stored=json.loads((Path(v2)/'moments.json').read_text())
    results={}
    # Pseudodata is analyzed first, independent of real-data model selection.
    for kind in ('pseudo','real'):
        data=stored['samples'][kind]
        nominal=data['nominal']
        h=wsum(nominal,'weights_nominal')
        p=norm(h)
        # The real nominal generator and the independent pseudodata target are
        # DIFFERENT comparators; never substitute pseudo weight_mc for truth.
        import csv
        if kind=='pseudo':
            path=Path(v1)/'pseudo'/'pseudo_closure_cells.csv'
            reference_column='independent_target_truth_fraction'
        else:
            path=Path(v1)/'real'/'real_2x2_cells.csv'
            reference_column='generator_fraction'
        with path.open(newline='',encoding='utf-8') as stream:
            records=list(csv.DictReader(stream))
        if [r['cell'] for r in records]!=['LL','LH','HL','HH']:
            raise ValueError('Wrong frozen reference cell order')
        q=norm(np.array([float(r[reference_column]) for r in records]))
        dd,sherpa=sample_two_point_inputs(data)
        original,_=old_covariance_and_shifts(data)
        if len(original)!=29:
            raise ValueError('Expected 29 frozen source covariances')
        models=build_two_point_scenarios(original,h,dd,sherpa)
        models_out=[]
        B=np.array([[1.,0.,0.,-1.],[0.,1.,0.,-1.],[0.,0.,1.,-1.]])
        grad=np.array([1/p[0],-1/p[1],-1/p[2],1/p[3]])
        for label,parts in models.items():
            c=sum(parts.values())
            c3=B@c@B.T
            eigen=np.linalg.eigvalsh(c3)
            if eigen[0]<=max(float(eigen[-1]),1e-300)*1e-10:
                raise ValueError('Numerically rank deficient 2x2 contrast covariance')
            residual=p-q
            z=B@residual
            # Only a raw, UNCALIBRATED descriptive quadratic. Not a chi2
            # sampling distribution, significance, or p-value.
            quad=float(z@np.linalg.solve(c3,z))
            models_out.append({
                'scenario':label,
                'total_provisional_trace':float(np.trace(c)),
                'measurement_only_joint_logodds_provisional_se':float(np.sqrt(max(grad@c@grad,0))),
                'uncalibrated_closure_quadratic_not_a_pvalue':quad,
                'rank_three_contrast':int(np.linalg.matrix_rank(c3)),
                'contrast_condition':float(np.linalg.cond(c3)),
            })
        results[kind]={'models':models_out,'source_count':len(original)}
    return {
        'status':'PRESPECIFIED_FOUR_CELL_TWO_POINT_STRESS_TEST',
        'source':'ATLAS 2024 PRL 133 261803 supplemental User Guide, section 2, item 5',
        'scope':'one fully correlated nuisance per source vs four independent count-bin nuisances',
        'prespecified_model_order':['pseudo','real'],
        'method':'linearized Jacobian of the normalized four-bin count shape',
        'limitations':[
            'Project-defined 2D extension, not CERN verified covariance helper',
            'No independently validated 2D Sherpa smoothing',
            'Alternative correlations must be tested on pseudodata before real-data interpretation',
            'One pseudodata target does not establish frequentist coverage',
            'Do not choose the model based on observed real-data agreement',
        ],
        'samples':results,'G5':'PROVISIONAL','G8':'UNVERIFIED',
        'G12':'FOUR_CORRELATION_SCENARIOS_NOT_COVERAGE_VALIDATED',
        'G15':'NO_GO','inference_permission':'NO_GO',
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--v1',type=Path,default=Path('data/derived/phase7-v1'))
    parser.add_argument('--v2',type=Path,default=Path('data/derived/phase7-v2'))
    parser.add_argument('--out',type=Path,default=Path('outputs/twopoint'))
    args=parser.parse_args()
    r=analyze(args.v1,args.v2)
    args.out.mkdir(parents=True,exist_ok=True)
    (args.out/'twopoint_protocol.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({'status':r['status'],'G15':r['G15'],'samples':r['samples']},indent=2))


if __name__=='__main__':
    main()
