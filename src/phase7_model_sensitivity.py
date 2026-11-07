"""Reproducible *uncalibrated* correlation-model sensitivity on real ATLAS artifacts.

Scientific intent: diagnose instability of G5/G12 assumptions, never infer a
real-data p-value, acceptance probability, confidence level, or significance.
The orthonormal-contrast decorrelation below is a PROJECT-DEFINED stress test,
NOT the published ATLAS prescription for 2D mass-multiplicity bins.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Mapping

import numpy as np

from src.shape import A

H = np.array([
    [1.0, -1.0, 0.0, 0.0],
    [1.0, 1.0, -2.0, 0.0],
    [1.0, 1.0, 1.0, -3.0],
], dtype=float) / np.array([np.sqrt(2.0), np.sqrt(6.0), np.sqrt(12.0)])[:, None]
POINTS = ('dd_unfolding', 'sherpa_hidden_variable')


def load_components(path: Path) -> dict[str, np.ndarray]:
    with np.load(path, allow_pickle=False) as archive:
        components = {name: np.asarray(archive[name], dtype=float) for name in archive.files}
    if len(components) != 29 or set(POINTS) - set(components):
        raise ValueError('Expected 29 source matrices including DD/Sherpa')
    for name, cov in components.items():
        if cov.shape != (4, 4) or not np.isfinite(cov).all():
            raise ValueError(f'Invalid covariance {name}')
        if not np.allclose(cov, cov.T, atol=1e-12, rtol=1e-10):
            raise ValueError(f'Asymmetric source covariance {name}')
        if not np.allclose(cov @ np.ones(4), 0, atol=1e-11):
            raise ValueError(f'Non-normalized source covariance {name}')
        if np.linalg.eigvalsh(cov).min() < -1e-11:
            raise ValueError(f'Non-positive-semidefinite source {name}')
    return components


def read_shape(path: Path, column: str) -> np.ndarray:
    with path.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    if [r['cell'] for r in rows] != ['LL', 'LH', 'HL', 'HH']:
        raise ValueError(f'Unexpected LL/LH/HL/HH order: {path}')
    shape = np.array([float(row[column]) for row in rows], dtype=float)
    if not np.isfinite(shape).all() or (shape < 0).any() or not np.isclose(shape.sum(), 1., atol=1e-8):
        raise ValueError(f'Unnormalized input distribution {path}:{column}')
    return shape


def contrast_decorrelate(cov: np.ndarray) -> np.ndarray:
    """Orthogonalize covariance in a fixed Helmert basis, preserving sum-to-zero.

    IMPORTANT: this is an exploratory countermodel, NOT an official ATLAS model.
    """
    transformed = H @ cov @ H.T
    return H.T @ np.diag(np.diag(transformed)) @ H


def model_components(base: Mapping[str, np.ndarray], scenario: str) -> dict[str, np.ndarray]:
    permitted = {
        'all_fully_correlated',
        'dd_helmert_decorrelated',
        'sherpa_helmert_decorrelated',
        'both_helmert_decorrelated',
        'exclude_dd_stress_only',
        'exclude_sherpa_stress_only',
        'exclude_both_stress_only',
        'half_two_point_amplitude',
        'one_and_half_two_point_amplitude',
    }
    if scenario not in permitted:
        raise ValueError(f'Unknown scenario: {scenario}')
    out = {key: value.copy() for key, value in base.items()}
    for source in POINTS:
        if ((source == 'dd_unfolding' and scenario in ('dd_helmert_decorrelated', 'both_helmert_decorrelated')) or
            (source == 'sherpa_hidden_variable' and scenario in ('sherpa_helmert_decorrelated', 'both_helmert_decorrelated'))):
            out[source] = contrast_decorrelate(out[source])
        if scenario in ('exclude_both_stress_only', f'exclude_{"dd" if source == "dd_unfolding" else "sherpa"}_stress_only'):
            out[source] *= 0.
        if scenario == 'half_two_point_amplitude':
            out[source] *= 0.25
        if scenario == 'one_and_half_two_point_amplitude':
            out[source] *= 2.25
    return out


def quadratic_description(components: Mapping[str, np.ndarray], residual: np.ndarray) -> dict:
    cov = np.sum(np.stack(list(components.values()), axis=0), axis=0)
    if not np.allclose(cov @ np.ones(4), 0., atol=1e-10):
        raise ValueError('Normalization null mode lost')
    z, c = A @ residual, A @ cov @ A.T
    eig = np.linalg.eigvalsh(c)
    scale = max(float(eig[-1]), 1e-300)
    rank = int(np.linalg.matrix_rank(c))
    if rank != 3 or eig[0] < 1e-10 * scale:
        raise ValueError('Model covariance is singular or poorly conditioned')
    value = float(z @ np.linalg.solve(c, z))
    return {'uncalibrated_quadratic': value,
            'covariance_rank': rank,
            'condition_number': float(np.linalg.cond(c)),
            'eigen_min': float(eig[0]),
            'eigen_max': float(eig[-1]),
            'normalization_null_residual': float(np.max(np.abs(cov @ np.ones(4))))}


def compare_sources(components: Mapping[str, np.ndarray]) -> list[dict]:
    total = float(np.trace(sum(components.values())))
    if total <= 0:
        raise ValueError('Non-positive covariance trace')
    return [{'source': key, 'trace_fraction': float(np.trace(cov) / total)}
            for key, cov in sorted(components.items(), key=lambda kv: -np.trace(kv[1]))]


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def verify_bin_spec(real_dir: Path, pseudo_dir: Path) -> dict:
    r = json.loads((real_dir / 'bin_spec_covariance.json').read_text())
    p = json.loads((pseudo_dir / 'pseudo_bin_spec.json').read_text())
    if not np.isclose(r['mass_star'], p['mass_star'], atol=1e-10, rtol=0.) or r['tracks_star'] != p['tracks_star']:
        raise ValueError('Frozen generator bin thresholds differ between runs')
    if r['selection'] != 'pT_trackj1 > 5 GeV' or p['selection'] != 'pT_trackj1 > 5 GeV':
        raise ValueError('Incorrect or non-matching jet selection')
    return {'mass_star_GeV': r['mass_star'], 'N_star': r['tracks_star'], 'selection': r['selection']}


def run(real_dir: Path, pseudo_dir: Path, out: Path) -> dict:
    real_dir, pseudo_dir, out = Path(real_dir), Path(pseudo_dir), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    spec = verify_bin_spec(real_dir, pseudo_dir)
    real = load_components(real_dir / 'source_covariances.npz')
    pseudo = load_components(pseudo_dir / 'pseudo_source_covariances.npz')
    if real.keys() != pseudo.keys():
        raise ValueError('Mismatched source families between real/pseudodata')
    for src, path in ((real, real_dir/'covariance_total.npy'), (pseudo, pseudo_dir/'pseudo_covariance_total.npy')):
        np.testing.assert_allclose(sum(src.values()), np.load(path, allow_pickle=False), rtol=1e-8, atol=1e-12)

    dreal = read_shape(real_dir/'real_2x2_cells.csv', 'unfolded_fraction') - read_shape(real_dir/'real_2x2_cells.csv', 'generator_fraction')
    dpseudo = read_shape(pseudo_dir/'pseudo_closure_cells.csv', 'pseudo_unfolded_fraction') - read_shape(pseudo_dir/'pseudo_closure_cells.csv', 'independent_target_truth_fraction')
    cases = (
        'all_fully_correlated', 'dd_helmert_decorrelated',
        'sherpa_helmert_decorrelated', 'both_helmert_decorrelated',
        'half_two_point_amplitude', 'one_and_half_two_point_amplitude',
        'exclude_dd_stress_only', 'exclude_sherpa_stress_only', 'exclude_both_stress_only'
    )
    table = []
    for case in cases:
        r = quadratic_description(model_components(real, case), dreal)
        p = quadratic_description(model_components(pseudo, case), dpseudo)
        table.append({'scenario': case,
                      'real_quadratic_UNCALIBRATED': r['uncalibrated_quadratic'],
                      'pseudo_quadratic_UNCALIBRATED': p['uncalibrated_quadratic'],
                      'real_cov_condition': r['condition_number'],
                      'pseudo_cov_condition': p['condition_number'],
                      'rank_real': r['covariance_rank'],
                      'rank_pseudo': p['covariance_rank']})
    write_csv(out/'model_sensitivity.csv', table)
    write_csv(out/'real_source_trace.csv', compare_sources(real))
    write_csv(out/'pseudo_source_trace.csv', compare_sources(pseudo))
    result = {
        'status': 'EXECUTED_UNCALIBRATED_MODEL_SENSITIVITY',
        'input_runs': {'real_covariance': 42324639484, 'official_pseudodata_closure': 42327464929},
        'frozen_generator_bin_spec': spec,
        'source_count': len(real),
        'scenarios': len(table),
        'main_model': table[0],
        'real_quadratic_range_UNCALIBRATED': [min(row['real_quadratic_UNCALIBRATED'] for row in table), max(row['real_quadratic_UNCALIBRATED'] for row in table)],
        'pseudo_quadratic_range_UNCALIBRATED': [min(row['pseudo_quadratic_UNCALIBRATED'] for row in table), max(row['pseudo_quadratic_UNCALIBRATED'] for row in table)],
        'G5': 'STILL PROVISIONAL: 2D Sherpa smoothing, DD source, nuisance correlations unverified',
        'G8': 'NO EMPIRICAL NULL CALIBRATION',
        'G11': 'OFFICIAL SINGLE-TARGET CLOSURE EXECUTED; NOT FREQUENTIST COVERAGE',
        'G12': 'MODEL-SENSITIVITY EXECUTED, NOT VERIFIED OFFICIAL CORRELATION MODEL',
        'G15': 'NO-GO',
        'inference_permission': 'NO-GO',
        'notes': ['Helmert decorrelation is project-defined, not a published ATLAS 2D prescription.',
                  'Source omission and amplitudes are stress tests, not legitimate automatic model choices.',
                  'Do NOT compute p-values or report compatibility/incompatibility from these quadratic values.']
    }
    (out/'model_sensitivity_status.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--real-dir',type=Path,required=True)
    ap.add_argument('--pseudo-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,default=Path('outputs'))
    args=ap.parse_args()
    run(args.real_dir,args.pseudo_dir,args.out)


if __name__=='__main__':
    main()
