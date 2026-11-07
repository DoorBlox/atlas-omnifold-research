"""Official ATLAS pseudodata-versus-known-target closure (provisional).

This stage is deliberately **descriptive**. Its input is the ATLAS public
pseudodata event release and *independent* known target (not real collision data).
It never reports a p-value, confidence level, or a validated acceptance verdict.
2D two-point covariance conventions still require experimental validation.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import h5py
import numpy as np

from src.phase7_covariance import (
    OBS, covariance_parts, diagnostics, hdf_layout, norm, project, save_csv
)
from src.projection import read_fixed_columns
from src.shape import A, four_cells, multiplicity_threshold, weighted_median

LABELS = ('LL','LH','HL','HH')
TWO_POINT = ('dd_unfolding','sherpa_hidden_variable')


def truth_projection(path, thresholds, chunksize=16384):
    """Stream target truth with its own weight_mc; never treat it as unfolded events."""
    path = Path(path)
    if chunksize < 1:
        raise ValueError('chunksize must be positive')
    h = np.zeros(4)
    w2 = np.zeros(4)
    counts = np.zeros(4, dtype=np.int64)
    with h5py.File(path, 'r') as file:
        if 'df' not in file:
            raise KeyError(f'Target HDF5 missing Pandas df key: {path}')
        group = file['df']
        mapping = hdf_layout(group)
        for col in (*OBS,'weight_mc'):
            if col not in mapping:
                raise KeyError(f'Target {path} missing required column: {col}')
        n = len(group['axis1'])
        for start in range(0,n,chunksize):
            stop = min(n,start+chunksize)
            cols = {key: np.asarray(group[mapping[key][0]][start:stop,mapping[key][1]],dtype=float)
                    for key in (*OBS,'weight_mc')}
            keep = cols['pT_trackj1'] > 5
            if not keep.any():
                continue
            if any(not np.isfinite(values[keep]).all() for values in cols.values()):
                raise ValueError('Non-finite selected target observations or weights')
            cells = four_cells(cols['m_trackj1'][keep],cols['Ntracks_trackj1'][keep],
                               thresholds['mass_star'],thresholds['tracks_star'])
            w = cols['weight_mc'][keep]
            counts += np.bincount(cells,minlength=4)
            h += np.bincount(cells,weights=w,minlength=4)
            w2 += np.bincount(cells,weights=w*w,minlength=4)
    effective = [float(h[k]**2/w2[k]) if w2[k]>0 else None for k in range(4)]
    return {'rows':int(sum(counts)), 'counts':counts.tolist(), 'sum_weights':h.tolist(),
            'shape':norm(h).tolist(), 'effective_count':effective}


def _quadratic(delta, C):
    z = A @ delta
    Cz = A @ ((C+C.T)/2) @ A.T
    eig = np.linalg.eigvalsh(Cz)
    scale = max(float(np.max(np.abs(eig))),1e-300)
    if eig[0] <= 1e-10*scale:
        return None, int(np.linalg.matrix_rank(Cz)), float(np.linalg.cond(Cz)), None
    val = float(z @ np.linalg.solve(Cz,z))
    # A second 3D basis must give the same physical test statistic.
    B = np.array([[1.,-1.,0.,0.],[0.,1.,-1.,0.],[0.,0.,1.,-1.]])
    z2 = B @ delta
    C2 = B @ C @ B.T
    alternate = float(z2 @ np.linalg.solve(C2,z2))
    if not np.isclose(val,alternate,rtol=1e-8,atol=1e-8):
        raise ValueError('Contrast basis invariance failed')
    return val, 3, float(np.linalg.cond(Cz)), abs(val-alternate)


def evaluate_closure(target, pseudo, parts):
    t,p = norm(target),norm(pseudo)
    C,diag = diagnostics(parts)
    diff = p-t
    val,rank,cond,basis_err = _quadratic(diff,C)
    log_odds = None
    if np.min(t)>0 and np.min(p)>0:
        log_odds=float(np.log(p[0]*p[3]/(p[1]*p[2]))-
                       np.log(t[0]*t[3]/(t[1]*t[2])))
    return {'target_fraction':t.tolist(), 'pseudo_unfolded_fraction':p.tolist(),
            'pseudodata_minus_truth':diff.tolist(),
            'squared_mahalanobis_UNCALIBRATED':val,
            'contrast_rank':rank, 'contrast_condition_number':cond,
            'basis_invariance_absolute_error':basis_err,
            'log_odds_difference_UNCALIBRATED':log_odds,
            'covariance_eigenvalues':diag['contrast_eigenvalues'],
            'scientific_status':'single official-target projection, not repeated-ensemble closure',
            'warning':'An uncalibrated quadratic IS NOT a p-value and does not establish empirical coverage'}


def scenario_sensitivity(target,pseudo,parts):
    """Stress-test provisional two-point *amplitudes*; not alternative ATLAS prescriptions."""
    scenarios = [
        ('all_components_provisional',1.,1.),
        ('both_two_points_half_amplitude',.5,.5),
        ('both_two_points_1p5_amplitude',1.5,1.5),
        ('exclude_dd_diagnostic_only',0.,1.),
        ('exclude_sherpa_diagnostic_only',1.,0.),
        ('exclude_both_diagnostic_only',0.,0.),
    ]
    rows=[]
    for name,dd_amp,sherpa_amp in scenarios:
        components = {k:v * (dd_amp**2 if k==TWO_POINT[0] else
                             sherpa_amp**2 if k==TWO_POINT[1] else 1.)
                      for k,v in parts.items()}
        summary = evaluate_closure(target,pseudo,components)
        rows.append({'scenario':name, 'dd_amplitude_scale':dd_amp,
                     'sherpa_amplitude_scale':sherpa_amp,
                     'uncalibrated_quadratic':summary['squared_mahalanobis_UNCALIBRATED'],
                     'contrast_rank':summary['contrast_rank'],
                     'condition_number':summary['contrast_condition_number']})
    return rows


def run(root,out):
    root,out=Path(root),Path(out)
    out.mkdir(parents=True,exist_ok=True)
    real=root/'files/data/multifold.h5'
    fields=read_fixed_columns(real,(*OBS,'weight_mc'))
    sel=fields['pT_trackj1']>5
    gw=fields['weight_mc'][sel]
    thresholds={'mass_star':weighted_median(fields['m_trackj1'][sel],gw),
                'tracks_star':multiplicity_threshold(fields['Ntracks_trackj1'][sel],gw),
                'selection':'pT_trackj1 > 5 GeV',
                'threshold_source':'REAL nominal MC only; independent of pseudodata target'}
    spec=out/'pseudo_bin_spec.json'
    if spec.exists() and json.loads(spec.read_text())!=thresholds:
        raise ValueError('Frozen bin specification drifted')
    spec.write_text(json.dumps(thresholds,indent=2))

    base,w2,mc2,counts = project(root/'files/pseudodata/multifold.h5',thresholds)
    sherpa,_,_,_ = project(root/'files/pseudodata/multifold_sherpa.h5',thresholds)
    nondy,_,_,_ = project(root/'files/pseudodata/multifold_nonDY.h5',thresholds)
    truth=truth_projection(root/'files/pseudodata/target.h5',thresholds)
    parts,manifest,unmapped=covariance_parts(base,w2,sherpa,nondy)
    total,diag=diagnostics(parts)
    p,q=norm(base['weights_nominal']),norm(base['weight_mc'])
    t=np.asarray(truth['shape'])
    result=evaluate_closure(t,p,parts)
    sens=scenario_sensitivity(t,p,parts)
    if unmapped:
        raise RuntimeError(f'Unmapped pseudodata weights: {unmapped}')

    np.save(out/'pseudo_covariance_total.npy',total)
    np.savez_compressed(out/'pseudo_source_covariances.npz',**parts)
    save_csv(out/'pseudo_source_manifest.csv',manifest)
    save_csv(out/'pseudo_covariance_sensitivity.csv',sens)
    rows=[]
    for k,name in enumerate(LABELS):
        rows.append({'cell':name,'pseudo_rows':int(counts[k]),
                     'target_rows':truth['counts'][k],
                     'pseudo_unfolded_fraction':float(p[k]),
                     'pseudo_generator_fraction':float(q[k]),
                     'independent_target_truth_fraction':float(t[k]),
                     'pseudodata_minus_truth':float(p[k]-t[k]),
                     'target_truth_neff':truth['effective_count'][k],
                     'pseudo_generator_neff':float(base['weight_mc'][k]**2/mc2[k]) if mc2[k]>0 else None})
    save_csv(out/'pseudo_closure_cells.csv',rows)
    support=all(r['pseudo_generator_neff'] is not None and r['pseudo_generator_neff']>=5000
                for r in rows)
    status={'status':'EXECUTED_PROVISIONAL_PSEUDODATA_CLOSURE',
            'analysis':'frozen real-generator-defined 2x2 mass by charged multiplicity',
            'official_reference':'ATLAS 2_pseudo_results.ipynb, target.weight_mc and pseudo.weights_nominal',
            'pseudo_selected_rows':int(counts.sum()),'target_selected_rows':truth['rows'],
            'number_uncertainty_sources':len(parts),
            'unmapped_weight_columns':unmapped,
            'G3':'PASS frozen real nominal-generator binning',
            'G4':'PSEUDO_SUPPORT_PASS' if support else 'PSEUDO_SUPPORT_FAIL',
            'G5':'PROVISIONAL: source-specific 2D covariance and two-point modelling not independently audited',
            'G6':'NUMERICAL_PASS' if diag['contrast_rank']==3 and diag['positive_definite'] and diag['null_mode_valid'] else 'NUMERICAL_FAIL',
            'G8':'UNVERIFIED: calibrated null reference still absent',
            'G11':'SINGLE_TARGET_CLOSURE_EXECUTED_NOT_COVERAGE_VALIDATION',
            'G12':'AMPLITUDE_STRESS_TEST_ONLY, no source-correlation validation',
            'G15':'NO_GO',
            'inference_permission':'NO_GO',
            'closure':result,
            'covariance_diagnostics':diag,
            'target_truth_support_neff':truth['effective_count'],
            'sensitivity_variants':len(sens)}
    (out/'pseudo_closure_status.json').write_text(json.dumps(status,indent=2))
    print(json.dumps(status,indent=2))
    return status


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',default='work')
    parser.add_argument('--out',default='outputs')
    args=parser.parse_args()
    run(args.root,args.out)

if __name__=='__main__':
    main()
