"""Provisional source-aware 2x2 ATLAS shape covariance, never a final p-value.

Conventions follow official ATLAS public notebooks. Replica families, one-point
nuisance shifts and independent alternative supports remain separate. The 2D
two-point modelling and null calibration are NOT yet scientifically validated.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path
import h5py
import numpy as np
from src.projection import read_fixed_columns
from src.shape import A, four_cells, weighted_median, multiplicity_threshold

SYST = ('pileup','lumi','topBackground','trackEffMain','trackEffJet','trackFake','trackPtScale',
        'muEffReco','muEffIso','muEffTrack','muEffTrig','muCalID','muCalMS','muCalResBias',
        'muCalScale','theoryPSjet','theoryPSsoft','theoryMPI','theoryPSscale',
        'theoryAlphaS','theoryQCD','theoryPDF')
REPLICAS = {'data_bootstrap':'weights_bootstrap_data',
            'mc_training_bootstrap':'weights_bootstrap_mc','nn_ensemble':'weights_ensemble'}
OBS = ('pT_trackj1','m_trackj1','Ntracks_trackj1')


def norm(v):
    v = np.asarray(v, dtype=float)
    if v.shape != (4,) or not np.isfinite(v).all() or v.sum() <= 0:
        raise ValueError('Invalid four-cell weights or normalization')
    return v / v.sum()


def source_covariance(shift):
    return np.outer(shift, shift)


def replica_covariance(replicas, divisor=1.):
    r = np.asarray(replicas, float)
    if r.ndim != 2 or r.shape[1] != 4 or len(r) < 2 or divisor <= 0:
        raise ValueError('Invalid replica family')
    centered = r - r.mean(axis=0)
    # HISTORICAL v1: population 1/R. Do not attribute this to the official
    # CERN helper: independent implementations suggest sample 1/(R-1).
    # See phase7_divisor_audit.py for an exact post-hoc covariance candidate.
    # Keep this unchanged to reproduce the versioned Phase 7 v1 results.
    return (centered.T @ centered) / (len(r) * divisor)


def finite_mc_covariance(h, w2):
    h, w2 = np.asarray(h, float), np.asarray(w2, float)
    if np.any(w2 < 0):
        raise ValueError('Negative squared-weight sum')
    jac = (np.eye(4) - np.outer(norm(h), np.ones(4))) / h.sum()
    return jac @ np.diag(w2) @ jac.T


def hdf_layout(group):
    mapping = {}
    for key in group:
        if key.startswith('block') and key.endswith('_items'):
            stem = key[:-6]
            for i, raw in enumerate(group[key][:]):
                name = raw.decode() if isinstance(raw, bytes) else str(raw)
                if name in mapping:
                    raise ValueError(f'Duplicate HDF5 field: {name}')
                mapping[name] = (stem + '_values', i)
    return mapping


def project(path, thresholds, chunksize=16384):
    """Stream fixed-Pandas HDF5 blocks with bounded resident memory."""
    with h5py.File(path, 'r') as handle:
        g = handle['df']
        mapping = hdf_layout(g)
        for required in (*OBS, 'weight_mc', 'weights_nominal'):
            if required not in mapping:
                raise KeyError(f'{path}: required column {required} missing')
        n = len(g['axis1'])
        cells = np.full(n, -1, dtype=np.int8)
        for start in range(0, n, chunksize):
            stop = min(start+chunksize, n)
            features = {}
            for key in OBS:
                block, i = mapping[key]
                features[key] = np.asarray(g[block][start:stop, i], float)
            accept = features['pT_trackj1'] > 5
            if accept.any() and not all(np.isfinite(features[k][accept]).all() for k in OBS):
                raise ValueError('Invalid selected observables')
            loc = four_cells(features['m_trackj1'], features['Ntracks_trackj1'],
                             thresholds['mass_star'], thresholds['tracks_star'])
            cells[start:stop] = np.where(accept, loc, -1)
        counts = np.bincount(cells[cells >= 0], minlength=4)
        fields = sorted(x for x in mapping if x.startswith('weights_') or x in ('weight_mc','target_dd'))
        totals = {x:np.zeros(4) for x in fields}
        nominal_w2 = np.zeros(4)
        generator_w2 = np.zeros(4)
        for block in sorted({mapping[x][0] for x in fields}):
            cols = [x for x in fields if mapping[x][0] == block]
            indices = [mapping[x][1] for x in cols]
            accumulated = np.zeros((4,len(cols)))
            for start in range(0,n,chunksize):
                stop = min(start+chunksize,n)
                selected = cells[start:stop] >= 0
                if not selected.any():
                    continue
                arr = np.asarray(g[block][start:stop,:],float)[selected][:,indices]
                if not np.isfinite(arr).all():
                    raise ValueError(f'Nonfinite source weight: {block}')
                local_cells = cells[start:stop][selected]
                for k in range(4):
                    mask = local_cells == k
                    accumulated[k] += arr[mask].sum(axis=0, dtype=float)
                for name, buffer in (('weights_nominal',nominal_w2),('weight_mc',generator_w2)):
                    if name in cols:
                        w = arr[:,cols.index(name)]
                        buffer += np.bincount(local_cells, weights=w*w, minlength=4)
            for col, arr in zip(cols, accumulated.T):
                totals[col] = arr
        return totals, nominal_w2, generator_w2, counts


def covariance_parts(base, w2, sherpa, nondy):
    required = {'weight_mc','weights_nominal','weights_dd','target_dd'} | {'weights_'+s for s in SYST}
    missing = sorted(required - base.keys())
    if missing:
        raise ValueError(f'Missing named ATLAS covariance inputs: {missing}')
    if 'weights_nominal' not in sherpa or 'weights_nominal' not in nondy:
        raise ValueError('Alternative-support nominal weight missing')
    parts, manifest = {}, []
    def add(name, family, shift_or_matrix, source):
        matrix = np.asarray(shift_or_matrix, float)
        if matrix.shape == (4,):
            matrix = source_covariance(matrix)
        if matrix.shape != (4,4) or not np.isfinite(matrix).all():
            raise ValueError(f'Invalid source: {name}')
        parts[name] = matrix
        manifest.append({'source':name,'family':family,'input':source})
    nominal = base['weights_nominal']
    add('finite_evaluation_mc','evaluation_MC_stat',finite_mc_covariance(nominal,w2),'weights_nominal squared')
    for family, prefix in REPLICAS.items():
        names = sorted(x for x in base if x.startswith(prefix))
        if len(names) < 2:
            raise ValueError(f'Insufficient replicas for {family}')
        arr = np.stack([norm(base[n]) for n in names])
        add(family,'replica_family',replica_covariance(arr, divisor=len(arr) if family=='nn_ensemble' else 1), ','.join(names))
    for stem in SYST:
        col='weights_'+stem
        add(stem,'one_shift_nuisance',norm(base[col])-norm(nominal),col)
    target_dd = base['target_dd']
    if np.any(target_dd <= 0):
        raise ValueError('DD target has a zero/negative cell: fail closed')
    dd = (base['weights_dd']-target_dd)*nominal/target_dd
    add('dd_unfolding','two_point_dd_provisional',norm(nominal+dd)-norm(nominal),'weights_dd,target_dd')
    add('sherpa_hidden_variable','independent_alternative_provisional',norm(sherpa['weights_nominal'])-norm(nominal),'sherpa.h5')
    add('nonDY','independent_alternative_provisional',norm(nondy['weights_nominal'])-norm(nominal),'nonDY.h5')
    known = required | {n for n in base if any(n.startswith(pref) for pref in REPLICAS.values())}
    unmapped = sorted(n for n in base if n.startswith('weights_') and n not in known)
    return parts, manifest, unmapped


def diagnostics(parts):
    C = np.sum(list(parts.values()),axis=0)
    Cz = A@C@A.T
    eig = np.linalg.eigvalsh(Cz)
    scale = max(float(np.linalg.norm(Cz,ord=2)),1e-300)
    return C, {
        'normalisation_null_residual': float(np.max(np.abs(C@np.ones(4)))),
        'contrast_rank': int(np.linalg.matrix_rank(Cz)),
        'contrast_eigenvalues': eig.tolist(),
        'contrast_condition_number': float(np.linalg.cond(Cz)),
        'positive_definite':bool(np.all(eig>scale*1e-8)),
        'null_mode_valid':bool(np.max(np.abs(C@np.ones(4))) < scale*1e-8),
    }


def save_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        writer = csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def run(root, out):
    root, out=Path(root),Path(out)
    out.mkdir(parents=True,exist_ok=True)
    nominal_path=root/'files/data/multifold.h5'
    fields=read_fixed_columns(nominal_path,(*OBS,'weight_mc'))
    select=fields['pT_trackj1']>5
    w=fields['weight_mc'][select]
    thresholds={'mass_star':weighted_median(fields['m_trackj1'][select],w),
                'tracks_star':multiplicity_threshold(fields['Ntracks_trackj1'][select],w),
                'selection':'pT_trackj1 > 5 GeV', 'threshold_source':'nominal_generator_only'}
    spec=out/'bin_spec_covariance.json'
    if spec.exists() and json.loads(spec.read_text())!=thresholds:
        raise ValueError('Frozen nominal-generator binning has changed')
    spec.write_text(json.dumps(thresholds,indent=2))
    base, w2, q2, counts = project(nominal_path, thresholds)
    sherpa,_,_,_ = project(root/'files/data/multifold_sherpa.h5',thresholds)
    nondy,_,_,_ = project(root/'files/data/multifold_nonDY.h5',thresholds)
    parts,manifest,unmapped=covariance_parts(base,w2,sherpa,nondy)
    C,d=diagnostics(parts)
    np.savez_compressed(out/'source_covariances.npz',**parts)
    np.save(out/'covariance_total.npy',C)
    save_csv(out/'source_manifest.csv',manifest)
    p,q=norm(base['weights_nominal']),norm(base['weight_mc'])
    sig=np.sqrt(np.maximum(np.diag(parts['data_bootstrap']),0))
    rows=[]
    for k,name in enumerate(('LL','LH','HL','HH')):
        rows.append({'cell':name,'rows':int(counts[k]),'generator_fraction':float(q[k]),
                     'unfolded_fraction':float(p[k]),'descriptive_delta':float(p[k]-q[k]),
                     'generator_neff':float(base['weight_mc'][k]**2/q2[k]) if q2[k]>0 else None,
                     'data_bootstrap_relative_uncertainty':float(sig[k]/p[k]) if p[k]>0 else None})
    save_csv(out/'real_2x2_cells.csv',rows)
    valid_support=all(r['generator_neff'] is not None and r['generator_neff']>=5000 and
                      r['data_bootstrap_relative_uncertainty'] is not None and
                      r['data_bootstrap_relative_uncertainty']<0.15 for r in rows)
    status={'stage':'provisional_real_covariance','selected_rows':int(counts.sum()),
            'number_of_sources':len(parts),'source_manifest_unmapped':unmapped,
            'G3':'PASS (generator-only)',
            'G4':'PASS' if valid_support else 'FAIL: support/precision gate',
            'G5':'PROVISIONAL: 2D two-point and correlation assumptions need validation',
            'G6': 'NUMERICAL PASS' if d['contrast_rank']==3 and d['positive_definite'] and d['null_mode_valid'] else 'FAIL',
            'G8':'UNVERIFIED: no calibrated null',
            'G11':'UNVERIFIED: no official 2D pseudodata closure',
            'G15':'NO-GO: NEVER REPORT A REAL-DATA P-VALUE',
            'covariance_diagnostics':d}
    (out/'provisional_covariance_status.json').write_text(json.dumps(status,indent=2))
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
