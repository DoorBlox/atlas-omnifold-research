"""Conservative finite-evaluation-MC covariance sensitivity from frozen ATLAS 2x2 data.

The bounds apply ONLY to the shared-event *finite-evaluation-MC* covariance.
All other provisional measurement-source covariances are treated as independent
of the nominal reference. No detector-level covariance or inference is claimed.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from src.phase7_snapshot import verify as verify_snapshot
from src.phase7_interaction import load_fractions, verify_matrices

CELLS = ('LL', 'LH', 'HL', 'HH')


def finite_mc_shape_covariance(q: np.ndarray, neff: np.ndarray) -> np.ndarray:
    """Poisson-weighted normalized-shape covariance from q and per-cell Neff.

    Under independent weighted count sums, Var(h_i) = sum_{events in i} w^2.
    J diag(w2) J.T is scale-free and equals M diag(q_i**2 / Neff_i) M.T.
    """
    q = np.asarray(q, dtype=float)
    neff = np.asarray(neff, dtype=float)
    if q.shape != (4,) or not np.isfinite(q).all() or np.any(q < 0) or not np.isclose(q.sum(), 1., atol=1e-8):
        raise ValueError('Reference fractions must be normalized four-cell values')
    if neff.shape != (4,) or not np.isfinite(neff).all() or np.any(neff <= 0):
        raise ValueError('Reference effective counts must be positive and finite')
    projection = np.eye(4) - np.outer(q, np.ones(4))
    cov = projection @ np.diag(q * q / neff) @ projection.T
    if not np.allclose(cov @ np.ones(4), 0., atol=1e-13):
        raise ValueError('Normalization null mode violated')
    return (cov + cov.T) / 2


def scalar_covariance_envelope(vp: float, vq: float, other: float) -> dict:
    """Cauchy-Schwarz sharp scalar bounds for any unknown finite-MC covariance.

    Var(P - Q) = other + vp + vq - 2 Cov(P,Q),
    |Cov(P,Q)| <= sqrt(vp vq).  This is NOT a bound on cross-covariances
    involving other experimental/unfolding systematics.
    """
    values = np.array([vp, vq, other], dtype=float)
    if not np.isfinite(values).all() or np.any(values < 0):
        raise ValueError('Covariance component variances cannot be negative or nonfinite')
    a, b = np.sqrt(vp), np.sqrt(vq)
    return {
        'measurement_finite_mc_variance': float(vp),
        'generator_finite_mc_variance': float(vq),
        'other_measurement_variance_assumed_reference_independent': float(other),
        'maximum_absolute_finite_mc_cross_covariance': float(a * b),
        'reference_fixed_variance': float(other + vp),
        'independent_variance': float(other + vp + vq),
        'minimum_variance': float(other + (a - b) ** 2),
        'maximum_variance': float(other + (a + b) ** 2),
    }


def log_odds_gradient(p: np.ndarray) -> np.ndarray:
    p = np.asarray(p, dtype=float)
    if p.shape != (4,) or not np.isfinite(p).all() or np.any(p <= 0) or not np.isclose(p.sum(), 1., atol=1e-8):
        raise ValueError('Log odds requires strictly positive normalized fractions')
    return np.array([1/p[0], -1/p[1], -1/p[2], 1/p[3]], dtype=float)


def _read_neff(path: Path) -> np.ndarray:
    with path.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    if tuple(row['cell'] for row in rows) != CELLS:
        raise ValueError('Unexpected generator effective-count cell ordering')
    return np.array([float(row['generator_neff']) for row in rows])


def _observable_gradients(p: np.ndarray, q: np.ndarray):
    return (
        ('mass_low', np.array([1., 1., 0., 0.]), np.array([1., 1., 0., 0.]), float(p[:2].sum() - q[:2].sum())),
        ('multiplicity_low', np.array([1., 0., 1., 0.]), np.array([1., 0., 1., 0.]), float((p[0]+p[2])-(q[0]+q[2]))),
        ('log_odds_ratio', log_odds_gradient(p), log_odds_gradient(q), float(
            np.log((p[0]*p[3])/(p[1]*p[2])) - np.log((q[0]*q[3])/(q[1]*q[2])))),
    )


def evaluate_real_snapshot(snapshot: Path) -> dict:
    snapshot = Path(snapshot)
    evidence = verify_snapshot(snapshot)
    real = snapshot / 'real'
    cells = real / 'real_2x2_cells.csv'
    p = load_fractions(cells, 'unfolded_fraction')
    q = load_fractions(cells, 'generator_fraction')
    c_q = finite_mc_shape_covariance(q, _read_neff(cells))
    with np.load(real / 'source_covariances.npz', allow_pickle=False) as archive:
        components = {name: archive[name] for name in archive.files}
    c_p = verify_matrices(components)
    if 'finite_evaluation_mc' not in components or len(components) != 29:
        raise ValueError('Missing expected 29-source provisional measurement covariance')
    c_eval = components['finite_evaluation_mc']
    c_other = (c_p - c_eval + (c_p - c_eval).T) / 2
    if np.linalg.eigvalsh(c_other).min() < -1e-11:
        raise ValueError('Other covariance terms unexpectedly non-positive-semidefinite')
    observables = []
    for name, gp, gq, delta in _observable_gradients(p, q):
        vp = float(gp @ c_eval @ gp)
        vq = float(gq @ c_q @ gq)
        other = float(gp @ c_other @ gp)
        params = scalar_covariance_envelope(vp, vq, other)
        values = {
            'observable': name,
            'measured_minus_reference': delta,
            'reference_fixed_standard_error': float(np.sqrt(params['reference_fixed_variance'])),
            'independent_reference_standard_error': float(np.sqrt(params['independent_variance'])),
            'minimum_standard_error': float(np.sqrt(params['minimum_variance'])),
            'maximum_standard_error': float(np.sqrt(params['maximum_variance'])),
            'se_max_over_reference_fixed_ratio': float(np.sqrt(params['maximum_variance'] / params['reference_fixed_variance'])),
        }
        observables.append({**values, **params})
    return {
        'status': 'CONDITIONAL_FINITE_MC_CROSS_COVARIANCE_ENVELOPE',
        'snapshot_provenance': evidence,
        'source': 'real ATLAS measurement compared to nominal generator with shared event support',
        'observable_gradient_rule': 'separate reference gradient for nonlinear log odds',
        'scope': 'Cauchy-Schwarz bounds only the finite-evaluation-MC cross-covariance; all other source families assumed reference-independent',
        'limitations': [
            'Provisional 29-source experimental covariance is not an official validated two-dimensional model.',
            'This is NOT a bound on unknown generator correlations with other uncertainty families.',
            'Counts and sum of weighted squares use an independent-Poisson-cell approximation.',
            'No detector-level repeated-unfolding calibration, no real-data inference.',
        ],
        'observables': observables,
        'G5': 'PROVISIONAL', 'G8': 'UNVERIFIED', 'G12': 'PARTIAL_FINITE_MC_SENSITIVITY',
        'G15': 'NO_GO', 'inference_permission': 'NO_GO',
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, default=Path('data/derived/phase7-v1'))
    ap.add_argument('--out', type=Path, default=Path('outputs'))
    args = ap.parse_args()
    result = evaluate_real_snapshot(args.snapshot)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'finite_mc_crosscov_envelope.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': result['status'], 'G15': result['G15'], 'observables': result['observables']}, indent=2))


if __name__ == '__main__':
    main()
