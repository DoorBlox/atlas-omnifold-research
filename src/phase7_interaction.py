"""Descriptive joint mass-multiplicity contrasts from frozen ATLAS 2x2 matrices.

Only measurement-side covariance is propagated. Generator/target is *treated
as fixed*; no inference, p-values, exclusion, or detector-level coverage.
These source matrices are provisional and lack official 2D DD/HV validation.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np


OBSERVABLES = ('mass_low', 'multiplicity_low', 'log_odds_ratio')
CELLS = ('LL', 'LH', 'HL', 'HH')


def verify_matrices(parts: dict[str, np.ndarray]) -> np.ndarray:
    if not parts:
        raise ValueError('No source covariance components')
    total = np.zeros((4, 4), dtype=float)
    for name, raw in parts.items():
        c = np.asarray(raw, dtype=float)
        if c.shape != (4, 4) or not np.isfinite(c).all():
            raise ValueError(f'Invalid 4x4 source matrix: {name}')
        if not np.allclose(c, c.T, atol=1e-12, rtol=1e-10):
            raise ValueError(f'Asymmetric source covariance: {name}')
        if not np.allclose(c @ np.ones(4), 0., atol=1e-10, rtol=0.):
            raise ValueError(f'Covariance normalization mode not null: {name}')
        eig = np.linalg.eigvalsh(c)
        if eig.min() < -1e-10 * max(float(eig.max()), 1e-20):
            raise ValueError(f'Non-positive-semidefinite source: {name}')
        total += c
    return total


def _shape(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=float)
    if a.shape != (4,) or not np.isfinite(a).all() or np.any(a < 0):
        raise ValueError('Invalid four-cell normalized shape')
    if not np.isclose(a.sum(), 1.0, rtol=0., atol=1e-8):
        raise ValueError('Four-cell fractions must sum to one')
    return a


def load_fractions(path: Path, col: str) -> np.ndarray:
    with Path(path).open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 4 or tuple(r['cell'] for r in rows) != CELLS:
        raise ValueError('Expected exactly LL, LH, HL, HH in that order')
    return _shape(np.array([float(row[col]) for row in rows], dtype=float))


def summaries(sample: str, measurement: np.ndarray, reference: np.ndarray,
              parts: dict[str, np.ndarray]) -> tuple[list[dict], list[dict]]:
    p, q = _shape(measurement), _shape(reference)
    total = verify_matrices(parts)
    gradients = {
        'mass_low': np.array([1., 1., 0., 0.]),
        'multiplicity_low': np.array([1., 0., 1., 0.]),
    }
    measurements = {
        'mass_low': float(p[0]+p[1]),
        'multiplicity_low': float(p[0]+p[2]),
    }
    references = {
        'mass_low': float(q[0]+q[1]),
        'multiplicity_low': float(q[0]+q[2]),
    }
    if np.min(p) <= 0 or np.min(q) <= 0:
        raise ValueError('Log odds ratio needs strictly positive four-cell fractions')
    gradients['log_odds_ratio'] = np.array([1/p[0], -1/p[1], -1/p[2], 1/p[3]])
    measurements['log_odds_ratio'] = float(np.log((p[0]*p[3])/(p[1]*p[2])))
    references['log_odds_ratio'] = float(np.log((q[0]*q[3])/(q[1]*q[2])))
    metrics = []
    rows = []
    for observable in OBSERVABLES:
        gradient = gradients[observable]
        variance = float(gradient @ total @ gradient)
        if variance <= 0 or not np.isfinite(variance):
            raise ValueError(f'Nonpositive or invalid variance: {observable}')
        by_source = []
        for name, matrix in parts.items():
            partvar = float(gradient @ matrix @ gradient)
            if partvar < -1e-12:
                raise ValueError(f'Negative source contribution: {name}')
            by_source.append((name, max(0., partvar)))
        if not np.isclose(sum(v for _, v in by_source), variance, rtol=1e-8, atol=1e-12):
            raise ValueError('Source variances do not sum to total')
        ranking = sorted(by_source, key=lambda x: x[1], reverse=True)
        for name, value in ranking:
            rows.append({'sample': sample, 'observable': observable, 'source': name,
                         'variance': value, 'fraction_of_variance': value/variance})
        metrics.append({'sample': sample, 'observable': observable,
                        'measurement_value': measurements[observable],
                        'reference_value': references[observable],
                        'difference': measurements[observable]-references[observable],
                        'variance': variance, 'provisional_standard_error': float(np.sqrt(variance)),
                        'top_source': ranking[0][0], 'top_source_fraction': ranking[0][1]/variance,
                        'reference_covariance_included': False})
    return metrics, rows


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def analyze_snapshot(snapshot: Path, out: Path) -> dict:
    snapshot, out = Path(snapshot), Path(out)
    # Verifies original derived files are still bit-for-bit identical to the
    # official-result artifact and preserves 2x2 source-family provenance.
    from src.phase7_snapshot import verify as verify_snapshot
    evidence = verify_snapshot(snapshot)
    all_metrics, all_sources = [], []
    for sample in ('real','pseudo'):
        base = snapshot / sample
        if sample == 'real':
            csvpath = base/'real_2x2_cells.csv'
            nominal = 'unfolded_fraction'
            target = 'generator_fraction'
            archive_path = base/'source_covariances.npz'
        else:
            csvpath = base/'pseudo_closure_cells.csv'
            nominal = 'pseudo_unfolded_fraction'
            target = 'independent_target_truth_fraction'
            archive_path = base/'pseudo_source_covariances.npz'
        with np.load(archive_path, allow_pickle=False) as arr:
            parts = {k:arr[k] for k in arr.files}
        if len(parts) != 29:
            raise ValueError('Expected exactly 29 provisional covariance sources')
        measurement, reference = load_fractions(csvpath,nominal), load_fractions(csvpath,target)
        metrics, sources = summaries(sample,measurement,reference,parts)
        all_metrics.extend(metrics)
        all_sources.extend(sources)
    out.mkdir(parents=True, exist_ok=True)
    _write_csv(out/'interaction_metrics.csv',all_metrics)
    _write_csv(out/'interaction_sources.csv',all_sources)
    result = {
        'status':'DESCRIPTIVE_SOURCE_DECOMPOSITION_ONLY',
        'input_provenance':evidence,
        'metrics':all_metrics,
        'scientific_scope':'2x2 normalized shapes; mass/track marginals and joint log odds',
        'reference_covariance':'CONDITIONED_FIXED; cross-covariance and reference MC uncertainty excluded',
        'uncertainty_model':'PROVISIONAL 29-source 2D covariance; Sherpa/DD model not validated',
        'G5':'UNVERIFIED', 'G8':'UNVERIFIED', 'G11':'SINGLE_PSEUDODATA_TARGET_ONLY',
        'G12':'SENSITIVITY_NOT_A_PRIORI_PRESCRIPTION',
        'G15':'NO_GO', 'inference_permission':'NO_GO',
    }
    (out/'interaction_status.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--snapshot',type=Path,default=Path('data/derived/phase7-v1'))
    parser.add_argument('--out',type=Path,default=Path('outputs'))
    args = parser.parse_args()
    result = analyze_snapshot(args.snapshot,args.out)
    print(json.dumps({'status':result['status'], 'G15':result['G15'],
                      'metrics':result['metrics']},indent=2))


if __name__ == '__main__':
    main()
