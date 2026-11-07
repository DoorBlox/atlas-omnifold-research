"""Audit two distinct normalized-shape replica covariance constructions.

Source basis: CERN multifold_util.fill_cov_matrix uses sample (R-1) raw-count
covariance. 2D normalized shapes are project-defined; this audit exposes both
(1) covariance of individually normalized replicas (nonlinear), and
(2) normalized Jacobian projection of the raw-count sample covariance.
Neither is claimed to be official 2D inference or a calibrated p-value.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import numpy as np

PREFIXES = {
    "data_bootstrap": "weights_bootstrap_data",
    "mc_training_bootstrap": "weights_bootstrap_mc",
    "nn_ensemble": "weights_ensemble",
}
CONTRAST = np.array([[1.,0.,0.,-1.],[0.,1.,0.,-1.],[0.,0.,1.,-1.]])


def normalized_shape_covariances(raw_nominal, raw_replicas, *, ensemble=False):
    """Return nonlinear normalization and linearized raw-count covariance.

    Explicitly use the **same** sample covariance denominator R-1 for both
    constructions, and /R for NN-ensemble mean covariance. Independent
    normalization is not equivalent to projecting raw sample covariance
    whenever replica total weight changes or perturbations are nonlinear.
    """
    h = np.asarray(raw_nominal, dtype=float)
    x = np.asarray(raw_replicas, dtype=float)
    if (h.shape != (4,) or x.ndim != 2 or x.shape[1] != 4 or len(x) < 2
            or not np.isfinite(h).all() or not np.isfinite(x).all()
            or h.sum() <= 0 or np.any(x.sum(axis=1) <= 0)):
        raise ValueError("Require finite four-cell counts, >=2 replicas and positive totals")
    r = len(x)
    divisor = (r - 1) * (r if ensemble else 1)
    normalized = x / x.sum(axis=1, keepdims=True)
    centered_normalized = normalized - normalized.mean(axis=0)
    c_normalized = centered_normalized.T @ centered_normalized / divisor
    p = h / h.sum()
    j = (np.eye(4) - np.outer(p, np.ones(4))) / h.sum()
    raw_centered = x - x.mean(axis=0)
    c_raw = raw_centered.T @ raw_centered / divisor
    c_projected = j @ c_raw @ j.T
    for name, c in (("normalized", c_normalized), ("projected", c_projected)):
        if not np.allclose(c, c.T, rtol=1e-10, atol=1e-14):
            raise ValueError(f"Asymmetric {name} covariance")
        if not np.allclose(c @ np.ones(4), 0, atol=1e-12):
            raise ValueError(f"Normalization null violated: {name}")
        eig = np.linalg.eigvalsh(c)
        if eig[0] < -1e-10 * max(abs(eig).max(), 1e-20):
            raise ValueError(f"Non-PSD {name} covariance")
    return c_normalized, c_projected


def raw_replica_stack(columns, prefix, count):
    """Require unique, contiguous, *exact* family membership 0..count-1."""
    if type(count) is not int or count < 2:
        raise ValueError("Invalid declared replica count")
    indexed = {}
    for name, cell in columns.items():
        if not name.startswith(prefix + "_"):
            continue
        match = re.fullmatch(re.escape(prefix) + r"_(\d+)", name)
        if match is None:
            raise ValueError(f"Malformed replica family member {name}")
        index = int(match.group(1))
        if index in indexed:
            raise ValueError(f"Duplicate replica family index: {index}")
        indexed[index] = np.asarray(cell["sum_w"], dtype=float)
    if set(indexed) != set(range(count)):
        raise ValueError(f"Missing or extra replica index: {prefix}; expected {count}, found {len(indexed)}")
    return np.stack([indexed[i] for i in range(count)])


def covariance_comparison(c_normalized, c_projected, gradient):
    """Report relative changes, never select a model or output significance."""
    left = np.asarray(c_normalized, dtype=float)
    right = np.asarray(c_projected, dtype=float)
    grad = np.asarray(gradient, dtype=float)
    if left.shape != (4,4) or right.shape != (4,4) or grad.shape != (4,):
        raise ValueError("Expected 4x4 covariance and 4-vector gradient")
    if not np.isfinite(left).all() or not np.isfinite(right).all() or not np.isfinite(grad).all():
        raise ValueError("Nonfinite source matrix/gradient")
    fro = np.linalg.norm(left)
    trace = np.trace(left)
    var_left = float(grad @ left @ grad)
    var_right = float(grad @ right @ grad)
    if fro == 0 or trace <= 0 or var_left <= 0 or var_right < 0:
        raise ValueError("Nonpositive reference source covariance")
    delta = right - left
    return {
        "trace_nonlinear_normalize_each": float(trace),
        "trace_linearized_raw_projection": float(np.trace(right)),
        "relative_trace_change_percent": float(100*np.trace(delta)/trace),
        "relative_frobenius_difference_percent": float(100*np.linalg.norm(delta)/fro),
        "max_absolute_covariance_element_difference": float(np.abs(delta).max()),
        "log_odds_source_se_nonlinear": float(np.sqrt(var_left)),
        "log_odds_source_se_linearized_raw": float(np.sqrt(var_right)),
        "three_contrast_rank_nonlinear": int(np.linalg.matrix_rank(CONTRAST @ left @ CONTRAST.T)),
        "three_contrast_rank_linearized": int(np.linalg.matrix_rank(CONTRAST @ right @ CONTRAST.T)),
    }


def analyze(v1: Path, v2: Path) -> dict:
    from src.phase7_joint_reference import analyze as joint_analyze, contrast_diagnostics
    from src.phase7_v2_reconstruct import wsum, norm

    state, models = joint_analyze(v1, v2, return_components=True)
    data = json.loads((Path(v2)/"moments.json").read_text(encoding="utf-8"))
    result = {"status":"EXECUTED_TWO_REPLICA_NORMALIZATION_CONVENTION_AUDIT",
              "method_note":"Both use source-verified R-1 sample covariance; normalization choice is a project 2D extension",
              "sample_order":["pseudo","real"], "samples":{},
              "G5":"PROVISIONAL", "G8":"UNVERIFIED", "G12":"UNVERIFIED",
              "G15":"NO_GO", "inference_permission":"NO_GO"}
    for kind in ("pseudo", "real"):
        nominal = data["samples"][kind]["nominal"]
        h = wsum(nominal, "weights_nominal")
        p = norm(h)
        grad = np.array([1./p[0], -1./p[1], -1./p[2], 1./p[3]])
        counts = state["samples"][kind]["replica_counts"]
        per_family = {}
        alternative = {}
        for family, prefix in PREFIXES.items():
            raw = raw_replica_stack(nominal["columns"], prefix, counts[family])
            nonlinear, projected = normalized_shape_covariances(
                h, raw, ensemble=(family == "nn_ensemble"))
            saved = models[kind]["both_fully_correlated"][family]
            if not np.allclose(saved, nonlinear, rtol=1e-9, atol=1e-14):
                raise ValueError(f"Nonlinear source covariance continuity failed: {kind} {family}")
            per_family[family] = covariance_comparison(nonlinear, projected, grad)
            alternative[family] = projected
        comparison = []
        for model in state["samples"][kind]["models"]:
            scenario = model["scenario"]
            components = {k:v.copy() for k,v in models[kind][scenario].items()}
            for family,c in alternative.items():
                components[family] = c
            # Other source components, joint reference correction and observed
            # shape differences are FIXED. This is sensitivity, not model fit.
            q_file = (Path(v1)/kind/('pseudo_closure_cells.csv' if kind=='pseudo' else 'real_2x2_cells.csv'))
            q_field = 'independent_target_truth_fraction' if kind=='pseudo' else 'generator_fraction'
            import csv
            with q_file.open(newline='',encoding='utf-8') as f:
                rows=list(csv.DictReader(f))
            if [row['cell'] for row in rows] != ['LL','LH','HL','HH']:
                raise ValueError('Frozen reference cell ordering mismatch')
            q = np.array([float(row[q_field]) for row in rows],dtype=float)
            alternative_diag=contrast_diagnostics(p,q,components)
            baseline=model['uncalibrated_quadratic_not_a_pvalue']
            comparison.append({
                'scenario':scenario,
                'baseline_uncalibrated_quadratic_not_a_pvalue':float(baseline),
                'raw_projected_uncalibrated_quadratic_not_a_pvalue':alternative_diag['uncalibrated_quadratic_not_a_pvalue'],
                'relative_quadratic_change_percent':float(100*(alternative_diag['uncalibrated_quadratic_not_a_pvalue']/baseline-1)),
                'baseline_total_cov_trace':float(model['covariance_trace']),
                'raw_projected_total_cov_trace':alternative_diag['covariance_trace'],
                'rank':alternative_diag['contrast_rank']})
        result['samples'][kind]={'actual_replica_counts':counts,
            'three_replica_family_comparisons':per_family,
            'four_prespecified_source_model_comparisons':comparison}
    return result


def run(v1:Path,v2:Path,out:Path)->dict:
    result=analyze(v1,v2)
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'replica_projection_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--v1',type=Path,default=Path('data/derived/phase7-v1'))
    parser.add_argument('--v2',type=Path,default=Path('data/derived/phase7-v2'))
    parser.add_argument('--out',type=Path,default=Path('outputs/replica-projection'))
    args=parser.parse_args()
    result=run(args.v1,args.v2,args.out)
    print(json.dumps({'status':result['status'],'G15':result['G15'],
                      'samples':result['samples']},indent=2))


if __name__ == '__main__':
    main()
