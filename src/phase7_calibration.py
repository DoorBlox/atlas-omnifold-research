"""Conditional Gaussian source-wise finite-replica null study.

A toy calibration under explicit assumed Gaussian source covariances, NOT
experimental frequentist coverage or an approved ATLAS p-value. The three
replica families are re-estimated per toy; all other ATLAS source covariances
remain fixed at their observed estimates.
"""
from __future__ import annotations

import argparse
import csv
import re
import json
from pathlib import Path
import numpy as np
from src.phase7_model_sensitivity import load_components, model_components
from src.shape import A

REPLICA_PREFIXES = {'data_bootstrap': 'weights_bootstrap_data',
                    'mc_training_bootstrap': 'weights_bootstrap_mc',
                    'nn_ensemble': 'weights_ensemble'}
CHI2_3_95 = 7.814727903251179


def _sym(a):
    return (a + a.T) / 2.0


def _sqrt_psd(c):
    vals, vecs = np.linalg.eigh(_sym(c))
    if vals[0] < -1e-10 * max(vals[-1], 1e-300):
        raise ValueError('Non-PSD covariance')
    return (vecs * np.sqrt(np.maximum(vals, 0.0))) @ vecs.T


def manifest_replica_counts(path: Path) -> dict[str, int]:
    """Read the actual source manifest: real data have 100 data bootstraps; pseudo 25."""
    counts = {}
    with Path(path).open(newline='', encoding='utf-8') as stream:
        for row in csv.DictReader(stream):
            source = row.get('source')
            if source not in REPLICA_PREFIXES:
                continue
            if source in counts:
                raise ValueError(f'Duplicate source family: {source}')
            prefix = REPLICA_PREFIXES[source]
            names = [x.strip() for x in row['input'].split(',') if x.strip()]
            indices = []
            for name in names:
                matched = re.fullmatch(rf'{re.escape(prefix)}_(\d+)', name)
                if matched is None:
                    raise ValueError(f'Invalid replica name in {source}: {name}')
                indices.append(int(matched.group(1)))
            if len(indices) < 2 or sorted(indices) != list(range(len(indices))):
                raise ValueError(f'{source} requires unique contiguous replica indices 0..N-1')
            counts[source] = len(indices)
    if set(counts) != set(REPLICA_PREFIXES):
        raise ValueError(f'Missing replica families from {path}: {sorted(set(REPLICA_PREFIXES)-set(counts))}')
    return counts


def study(components: dict, *, replica_counts: dict[str, int], toys=10000, seed=20261107, batch=512) -> dict:
    if toys < 500 or batch < 1:
        raise ValueError('At least 500 toys and a positive batch size required')
    if set(replica_counts) != set(REPLICA_PREFIXES) or any(not isinstance(n, int) or n < 2 for n in replica_counts.values()):
        raise ValueError("Replica counts must identify all three actual families with >=2 replicas")
    if any(key not in components for key in REPLICA_PREFIXES):
        raise KeyError('Missing replica covariance families')
    c_source = {name: _sym(A @ c4 @ A.T) for name, c4 in components.items()}
    total = _sym(sum(c_source.values()))
    eig = np.linalg.eigvalsh(total)
    if eig[0] <= 1e-10 * eig[-1]:
        raise ValueError('Total covariance not positive definite in contrast space')
    chol_total = _sqrt_psd(total)
    stable = _sym(total - sum(c_source[n] for n in REPLICA_PREFIXES))
    replicator = {}
    for name, count in replica_counts.items():
        # Stored ensemble covariance includes division by the actual ensemble count.
        divisor = count if name == 'nn_ensemble' else 1
        replicator[name] = (count, divisor, _sqrt_psd(c_source[name] * divisor))
    random = np.random.default_rng(seed)
    known_T, plugin_T = [], []
    inv_total = np.linalg.inv(total)
    for start in range(0, toys, batch):
        n = min(batch, toys - start)
        z = random.normal(size=(n, 3)) @ chol_total.T
        known_T.append(np.einsum('bi,ij,bj->b', z, inv_total, z))
        estimated = np.broadcast_to(stable, (n, 3, 3)).copy()
        for count, div, sqrt_individual in replicator.values():
            draws = random.normal(size=(n, count, 3)) @ sqrt_individual.T
            centered = draws - draws.mean(axis=1, keepdims=True)
            estimated += np.einsum('bri,brj->bij', centered, centered) / (count * div)
        if np.any(np.linalg.eigvalsh(estimated)[:, 0] <= 0):
            raise RuntimeError('Toy estimated covariance became non-PD')
        # NumPy 2 requires explicit [..., None] for batched vector solve.
        solution = np.linalg.solve(estimated, z[..., None])[..., 0]
        plugin_T.append(np.einsum('bi,bi->b', z, solution))
    known_T, plugin_T = np.concatenate(known_T), np.concatenate(plugin_T)
    return {
        'model': 'CONDITIONAL_GAUSSIAN_TOY_REESTIMATED_REPLICA_COVARIANCE',
        'toys': int(toys), 'seed': int(seed),
        'replica_counts': dict(replica_counts),
        'nn_ensemble_divisor': replica_counts['nn_ensemble'],
        'nominal_chi2_3_95_threshold_reference': CHI2_3_95,
        'known_cov_rejection_at_chi2_3_95': float(np.mean(known_T > CHI2_3_95)),
        'plugin_cov_rejection_at_chi2_3_95': float(np.mean(plugin_T > CHI2_3_95)),
        'known_cov_empirical_95th_percentile': float(np.quantile(known_T, .95)),
        'plugin_cov_empirical_95th_percentile': float(np.quantile(plugin_T, .95)),
        'fixed_components': sorted(set(components) - set(REPLICA_PREFIXES)),
        'limitations': (
            'Gaussian independent-source approximation; observed source covariances assumed true; '
            'all non-replica components fixed; shared generator support and source correlations '
            'not calibrated; no repeated physical ATLAS unfolding; not a real-data p-value.'
        ),
        'G8': 'CONDITIONAL_GAUSSIAN_TOY_ONLY_NOT_ATLAS_COVERAGE',
        'G15': 'NO-GO',
    }


def run(real_dir: Path, pseudo_dir: Path, out: Path, *, toys: int, seed: int) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    all_outputs = {
        'real_original': study(load_components(real_dir / 'source_covariances.npz'),
                               replica_counts=manifest_replica_counts(real_dir / 'source_manifest.csv'),
                               toys=toys, seed=seed),
        'pseudo_original': study(load_components(pseudo_dir / 'pseudo_source_covariances.npz'),
                                 replica_counts=manifest_replica_counts(pseudo_dir / 'pseudo_source_manifest.csv'),
                                 toys=toys, seed=seed + 1),
    }
    # Secondary scenario is a predefined extreme stress test; never select the
    # model yielding the most favorable apparent real-data statistic.
    all_outputs['pseudo_without_sherpa_STRESS_ONLY'] = study(
        model_components(load_components(pseudo_dir / 'pseudo_source_covariances.npz'),
                         'exclude_sherpa_stress_only'),
        replica_counts=manifest_replica_counts(pseudo_dir / 'pseudo_source_manifest.csv'),
        toys=toys, seed=seed + 2
    )
    payload = {'status': 'TOY_EXECUTED_NOT_EXPERIMENTAL_COVERAGE', 'studies': all_outputs,
               'G8': 'CONDITIONAL_MODEL_TOY_ONLY', 'G15': 'NO-GO'}
    (out / 'finite_covariance_toy_calibration.json').write_text(json.dumps(payload, indent=2))
    print(json.dumps(payload, indent=2))
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--real-dir', type=Path, required=True)
    parser.add_argument('--pseudo-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=Path('outputs'))
    parser.add_argument('--toys', type=int, default=10000)
    parser.add_argument('--seed', type=int, default=20261107)
    args = parser.parse_args()
    run(args.real_dir, args.pseudo_dir, args.out, toys=args.toys, seed=args.seed)


if __name__ == '__main__':
    main()
