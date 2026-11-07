"""Source-aligned CONDITIONAL joint-shape covariance for frozen ATLAS 2x2 bins.

Replicas use CERN multifold_util.fill_cov_matrix sample divisor R-1; our
per-replica normalized projection is a project-defined 2D shape extension.
The real nominal generator and unfolded weights share the *same* events:
their conditional weighted-Poisson covariance must include mixed products.
The pseudodata independent truth is separate, not the pseudo generator.

None of these finite-MC and Gaussian-linearized calculations validate the
2D two-point nuisance-correlation model, learned-weight fluctuations,
repeated pseudo-experiment coverage, or permit a real-data p-value.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import numpy as np

FAMILIES = {
    'data_bootstrap': 'weights_bootstrap_data',
    'mc_training_bootstrap': 'weights_bootstrap_mc',
    'nn_ensemble': 'weights_ensemble',
}
SCENARIOS = (
    ('both_fully_correlated', 'fully_correlated', 'fully_correlated'),
    ('dd_decorrelated_sherpa_correlated', 'four_bin_decorrelated', 'fully_correlated'),
    ('dd_correlated_sherpa_decorrelated', 'fully_correlated', 'four_bin_decorrelated'),
    ('both_four_bin_decorrelated', 'four_bin_decorrelated', 'four_bin_decorrelated'),
)
CONTRAST = np.array([[1., 0., 0., -1.],
                     [0., 1., 0., -1.],
                     [0., 0., 1., -1.]])


def _four(x, *, positive=False):
    v = np.asarray(x, dtype=float)
    if v.shape != (4,) or not np.isfinite(v).all():
        raise ValueError('Expected four finite cell values')
    if positive and np.any(v <= 0):
        raise ValueError('Expected positive four-cell totals')
    return v


def _shape(h):
    v = _four(h)
    if v.sum() <= 0:
        raise ValueError('Expected positive total weight')
    return v / v.sum()


def shape_jacobian(raw):
    h = _four(raw)
    H = h.sum()
    if H <= 0:
        raise ValueError('Expected positive normalization sum')
    return (np.eye(4) - np.outer(h/H, np.ones(4))) / H


def validate_covariance(c):
    c = np.asarray(c, dtype=float)
    if c.shape != (4, 4) or not np.isfinite(c).all():
        raise ValueError('Nonfinite/invalid 4x4 covariance')
    if not np.allclose(c, c.T, rtol=1e-10, atol=1e-12):
        raise ValueError('Non-symmetric covariance')
    if not np.allclose(c @ np.ones(4), 0., rtol=0, atol=1e-11):
        raise ValueError('Normalization-null mode violation')
    eig = np.linalg.eigvalsh(c)
    if eig[0] < -1e-10*max(abs(eig).max(), 1e-20):
        raise ValueError('Non-PSD covariance')
    return c


def expected_replica_covariances(columns, counts):
    """Reference R-1 formula on project-normalized 4-cell replica shapes.

    Compare directly to persisted historic 1/R matrices (R/(R-1) factor).
    NN replicas estimate variance of their mean, so divide sample cov by R.
    Fail closed when names, indices or declared counts disagree.
    """
    if set(counts) != set(FAMILIES):
        raise ValueError('Incorrect replica families')
    result = {}
    for family, prefix in FAMILIES.items():
        n = counts[family]
        if type(n) is not int or n < 2:
            raise ValueError(f'Invalid replica count: {family}')
        indexed = {}
        for name, stats in columns.items():
            if name.startswith(prefix+'_'):
                match = re.fullmatch(re.escape(prefix)+r'_(\d+)', name)
                if match is None:
                    raise ValueError(f'Unexpected replica column: {name}')
                number = int(match.group(1))
                if number in indexed:
                    raise ValueError(f'Duplicate replica index: {name}')
                indexed[number] = _shape(stats['sum_w'])
        if set(indexed) != set(range(n)):
            raise ValueError(f'Noncontiguous or missing replica indices in {family}: got {len(indexed)}, expected {n}')
        x = np.stack([indexed[i] for i in range(n)])
        centered = x - x.mean(axis=0)
        result[family] = validate_covariance((centered.T @ centered) / ((n-1)*(n if family=='nn_ensemble' else 1)))
    return result


def _check_weight_moments(hp,hq,spp,sqq,spq):
    hp = _four(hp, positive=True)
    hq = _four(hq, positive=True)
    spp,sqq,spq = _four(spp),_four(sqq),_four(spq)
    if np.any(spp < 0) or np.any(sqq < 0):
        raise ValueError('Negative squared-weight moment')
    bound = np.sqrt(spp*sqq)
    if np.any(np.abs(spq) > bound + 1e-10*np.maximum(bound, 1.)):
        raise ValueError('Mixed moments violate per-cell Cauchy-Schwarz bounds')
    return hp,hq,spp,sqq,spq


def shared_reference_covariance(hp,hq,spp,sqq,spq):
    """Poisson finite-MC covariance of normalized unfolded p minus generator q.

    Assumes per-event weights fixed and identical event support (not repeated
    retraining). The event-paired moments guarantee PSD when physically valid.
    """
    hp,hq,spp,sqq,spq = _check_weight_moments(hp,hq,spp,sqq,spq)
    Jp,Jq = shape_jacobian(hp),shape_jacobian(hq)
    c = Jp @ np.diag(spp) @ Jp.T + Jq @ np.diag(sqq) @ Jq.T
    cross = Jp @ np.diag(spq) @ Jq.T
    c -= cross+cross.T
    return validate_covariance((c+c.T)/2)


def shared_observable_variance(hp,hq,spp,sqq,spq,gradient_p,gradient_q):
    """Different p/q gradients are ESSENTIAL for log-odds comparison."""
    hp,hq,spp,sqq,spq = _check_weight_moments(hp,hq,spp,sqq,spq)
    a = shape_jacobian(hp).T @ _four(gradient_p)
    b = shape_jacobian(hq).T @ _four(gradient_q)
    ans = float(np.sum(a*a*spp + b*b*sqq - 2*a*b*spq))
    if ans < -1e-10*max(1.,np.sum(a*a*spp + b*b*sqq)):
        raise ValueError('Negative shared-event variance')
    return max(ans,0.)


def count_shift_covariance(h, delta, model):
    if model not in ('fully_correlated','four_bin_decorrelated'):
        raise ValueError('Unsupported two-point source model')
    J = shape_jacobian(_four(h,positive=True))
    d = _four(delta)
    c = (np.outer(J@d,J@d) if model=='fully_correlated' else
         J@np.diag(d*d)@J.T)
    return validate_covariance((c+c.T)/2)


def build_joint_scenarios(components,nominal,delta_dd,delta_sherpa,*,kind,
                          shared_finite_mc=None,target_covariance=None):
    if kind not in ('real','pseudo'):
        raise ValueError('Invalid sample kind')
    if not {'dd_unfolding','sherpa_hidden_variable','finite_evaluation_mc'} <= set(components):
        raise ValueError('Missing required source family')
    if kind=='real':
        if target_covariance is not None:
            raise ValueError('A real shared-reference model must not include independent truth')
        if shared_finite_mc is None:
            raise ValueError('A real shared-reference covariance is required')
        validate_covariance(shared_finite_mc)
    elif target_covariance is None or shared_finite_mc is not None:
        raise ValueError('Pseudo model requires independent truth covariance and no shared finite MC')
    if target_covariance is not None:
        validate_covariance(target_covariance)
    for v in components.values():
        validate_covariance(v)
    models = {}
    for name,dd_model,hv_model in SCENARIOS:
        parts = {k:np.asarray(c,float).copy() for k,c in components.items()}
        parts['dd_unfolding'] = count_shift_covariance(nominal,delta_dd,dd_model)
        parts['sherpa_hidden_variable'] = count_shift_covariance(nominal,delta_sherpa,hv_model)
        if kind=='real':
            # Critical: REPLACE measurement-only evaluation MC; never double-count.
            parts['finite_evaluation_mc'] = np.asarray(shared_finite_mc,float).copy()
        else:
            parts['independent_truth_finite_mc'] = np.asarray(target_covariance,float).copy()
        validate_covariance(sum(parts.values()))
        models[name] = parts
    return models


def contrast_diagnostics(p,q,components):
    p,q = _four(p,positive=True),_four(q,positive=True)
    if not np.isclose(p.sum(),1.,rtol=0,atol=1e-8) or not np.isclose(q.sum(),1.,rtol=0,atol=1e-8):
        raise ValueError('Normalized shapes required')
    c = validate_covariance(sum(components.values()))
    c3 = CONTRAST @ c @ CONTRAST.T
    eigen = np.linalg.eigvalsh(c3)
    if eigen[0] <= 1e-10*max(eigen[-1],1e-20):
        raise ValueError('Rank deficient contrast covariance')
    diff = CONTRAST@(p-q)
    quad = float(diff @ np.linalg.solve(c3,diff))
    return {'uncalibrated_quadratic_not_a_pvalue': quad,
            'contrast_rank':3,'contrast_condition':float(np.linalg.cond(c3)),
            'normalization_null_residual':float(np.max(np.abs(c@np.ones(4)))),
            'covariance_trace':float(np.trace(c)),
            'contrast_eigenvalues':eigen.tolist(),
            'G15':'NO_GO'}


def _observable_gradients(shape):
    p = _four(shape,positive=True)
    return {'mass_low':np.array([1.,1.,0.,0.]),
            'multiplicity_low':np.array([1.,0.,1.,0.]),
            'joint_log_odds':np.array([1/p[0],-1/p[1],-1/p[2],1/p[3]])}


def _read_reference(v1,kind):
    v1 = Path(v1)
    filename = 'pseudo/pseudo_closure_cells.csv' if kind=='pseudo' else 'real/real_2x2_cells.csv'
    col = 'independent_target_truth_fraction' if kind=='pseudo' else 'generator_fraction'
    with (v1/filename).open(newline='',encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    if [x['cell'] for x in rows]!=['LL','LH','HL','HH']:
        raise ValueError('Frozen cell order mismatch')
    q = np.array([float(row[col]) for row in rows])
    if np.any(q<=0) or not np.isclose(q.sum(),1.,atol=1e-8):
        raise ValueError('Invalid reference shape')
    return q,rows


def analyze(v1:Path,v2:Path) -> dict:
    """No new HDF5 downloads; G15 is hard-blocked for both samples."""
    from src.phase7_snapshot import verify as verify_v1
    from src.phase7_v2_extract import verify_v2
    from src.phase7_v2_reconstruct import old_covariance_and_shifts, wsum
    from src.phase7_divisor_audit import manifest_replica_counts
    from src.phase7_target_mc import normalized_target_covariance
    from src.phase7_twopoint_protocol import sample_two_point_inputs

    v1,v2 = Path(v1),Path(v2)
    proof1,proof2 = verify_v1(v1),verify_v2(v2)
    store=json.loads((v2/'moments.json').read_text(encoding='utf-8'))
    result = {'status':'SOURCE_ALIGNED_CONDITIONAL_2X2_COVARIANCE_AUDIT',
              'primary_helper_file_sha256':'cf43074fb3635b5c484dd1f35b9dc95cea938d86d206b4a2e83ab1f739e73d7f',
              'v1_verified':proof1,'v2_verified':proof2,
              'scenario_order':[row[0] for row in SCENARIOS],
              'sample_order':['pseudo','real'],'samples':{},
              'estimands':{'real':'joint weighted-Poisson finite-MC p-q with shared event support; all non-MC sources act on p only',
                           'pseudo':'independent pseudodata truth q with finite-MC target covariance; all 29 sources act on unfolded p'},
              'limitations':['CERN 1D raw-count estimator mapped to project-specific normalized replica shapes',
                             '2D source-family inclusion and Sherpa/DD correlations require independent validation',
                             'Fixed learned weights and independent source families are assumptions, not measured frequentist coverage',
                             'Single official pseudodata target is not a repeated-experiment calibration',
                             'No real-data p-value or generator-compatibility decision'],
              'G5':'PROVISIONAL','G8':'UNVERIFIED','G12':'UNVERIFIED',
              'G15':'NO_GO','inference_permission':'NO_GO'}
    for kind in ('pseudo','real'):
        sample = store['samples'][kind]
        nom = sample['nominal']
        h = wsum(nom,'weights_nominal')
        hp = _shape(h)
        q,rows = _read_reference(v1,kind)
        raw_parts,_ = old_covariance_and_shifts(sample)
        if len(raw_parts)!=29:
            raise ValueError('Expected 29 frozen sources')
        counts = manifest_replica_counts(v1/kind/('pseudo_source_manifest.csv' if kind=='pseudo' else 'source_manifest.csv'))
        correct = expected_replica_covariances(nom['columns'],counts)
        relative_errors={}
        parts = {k:v.copy() for k,v in raw_parts.items()}
        for family,matrix in correct.items():
            expected=raw_parts[family]*(counts[family]/(counts[family]-1))
            delta=float(np.max(np.abs(matrix-expected)))
            if not np.allclose(matrix,expected,rtol=1e-9,atol=1e-14):
                raise ValueError(f'Replica R-1 source correction disagreement: {kind}/{family} = {delta}')
            relative_errors[family]=delta
            parts[family]=matrix
        delta_dd, delta_hv = sample_two_point_inputs(sample)
        truth_C = None
        shared_C = None
        shared_inputs=None
        if kind=='pseudo':
            truth_C = normalized_target_covariance(q,np.array([float(row['target_truth_neff']) for row in rows]))
        else:
            hq = wsum(nom,'weight_mc')
            spp = wsum(nom,'weights_nominal','sum_w2')
            sqq = wsum(nom,'weight_mc','sum_w2')
            spq = wsum(nom,'weight_mc','sum_w_times_nominal')
            spq_copy = wsum(nom,'weights_nominal','sum_w_times_mc')
            if not np.allclose(spq,spq_copy,rtol=1e-10,atol=1e-11):
                raise ValueError('Stored cross-products are asymmetric')
            shared_C = shared_reference_covariance(h,hq,spp,sqq,spq)
            shared_inputs=(h,hq,spp,sqq,spq)
            if not np.allclose(_shape(hq),q,atol=1e-9,rtol=1e-7):
                raise ValueError('Generator reference no longer matches frozen moments')
        models=build_joint_scenarios(parts,h,delta_dd,delta_hv,kind=kind,
                                     shared_finite_mc=shared_C,target_covariance=truth_C)
        models_out=[]
        gp,gq = _observable_gradients(hp),_observable_gradients(q)
        for label,matrices in models.items():
            d=contrast_diagnostics(hp,q,matrices)
            metrics={}
            if kind=='real':
                other=sum([matrix for name,matrix in matrices.items() if name!='finite_evaluation_mc'])
            else:
                unfolded=sum([matrix for name,matrix in matrices.items() if name!='independent_truth_finite_mc'])
            for observable in gp:
                if kind=='real':
                    shared_var=shared_observable_variance(*shared_inputs,gp[observable],gq[observable])
                    source_var=float(gp[observable]@other@gp[observable])
                    var=shared_var+source_var
                else:
                    source_var=float(gp[observable]@unfolded@gp[observable])
                    truth_var=float(gq[observable]@truth_C@gq[observable])
                    var=source_var+truth_var
                if var < -1e-13:
                    raise ValueError('Negative observable variance')
                metrics[observable]={'conditional_standard_error':float(np.sqrt(max(var,0.))),
                                     'other_source_variance':float(source_var)}
                if kind=='real':
                    metrics[observable]['shared_evaluation_mc_variance']=float(shared_var)
                else:
                    metrics[observable]['independent_truth_mc_variance']=float(truth_var)
            models_out.append({'scenario':label,**d,'observables':metrics,
                               'source_count':len(matrices)})
        result['samples'][kind]={'replica_counts':counts,
            'direct_v2_R_minus_1_vs_rescaled_v1_max_abs_error_by_family':relative_errors,
            'reference_kind':'independent_known_truth' if kind=='pseudo' else 'shared_nominal_generator',
            'nuisance_source_count':29,
            'finite_reference_model':'independent_weighted_Poisson' if kind=='pseudo' else 'paired_weighted_Poisson_same_events',
            'models':models_out}
    return result


def run(v1:Path,v2:Path,out:Path)->dict:
    payload = analyze(v1,v2)
    out = Path(out)
    out.mkdir(parents=True,exist_ok=True)
    (out/'conditional_joint_covariance.json').write_text(json.dumps(payload,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return payload


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--v1',type=Path,default=Path('data/derived/phase7-v1'))
    parser.add_argument('--v2',type=Path,default=Path('data/derived/phase7-v2'))
    parser.add_argument('--out',type=Path,default=Path('outputs/joint-reference'))
    args=parser.parse_args()
    report=run(args.v1,args.v2,args.out)
    print(json.dumps({'status':report['status'],'G15':report['G15'],
        'samples':{k:{'replica_counts':v['replica_counts'],
                      'models':v['models']} for k,v in report['samples'].items()}},indent=2))


if __name__=='__main__':
    main()
