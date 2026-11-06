"""Small auditable primitives for normalized 2x2 shape projections.

These helpers are independent of the unresolved ATLAS HDF5 column mapping.
They are NOT a complete uncertainty reconstruction or calibrated physics test.
"""
from __future__ import annotations
import numpy as np

LABELS = ("LL", "LH", "HL", "HH")
A = np.array([[1., 0., 0., -1.], [0., 1., 0., -1.], [0., 0., 1., -1.]])


def _validate(x, w):
    x, w = np.asarray(x), np.asarray(w, dtype=float)
    if x.ndim != 1 or x.shape != w.shape:
        raise ValueError("Expected equal-length one-dimensional arrays")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(w)):
        raise ValueError("Non-finite value")
    if np.any(w < 0) or w.sum() <= 0:
        raise ValueError("Generator weighted-median requires nonnegative weights of positive total")
    return x, w


def weighted_median(x, w):
    x, w = _validate(x, w)
    order = np.argsort(x, kind="stable")
    x, w = x[order], w[order]
    idx = np.searchsorted(np.cumsum(w), 0.5 * np.sum(w), side="left")
    return float(x[idx])


def multiplicity_threshold(n, w):
    n, w = _validate(n, w)
    if not np.all(n == np.floor(n)):
        raise ValueError("Track multiplicity must be an integer count")
    order = np.argsort(n, kind="stable")
    n, w = n[order], w[order]
    idx = np.searchsorted(np.cumsum(w), 0.5 * np.sum(w), side="left")
    return int(n[idx])


def four_cells(mass, tracks, mass_star, tracks_star):
    mass = np.asarray(mass)
    tracks = np.asarray(tracks)
    if mass.shape != tracks.shape:
        raise ValueError("Mismatched variable shapes")
    return np.where(mass < mass_star, 0, 2) + np.where(tracks <= tracks_star, 0, 1)


def fractions(cells, weights):
    cells = np.asarray(cells)
    weights = np.asarray(weights, dtype=float)
    if cells.ndim != 1 or cells.shape != weights.shape:
        raise ValueError("Mismatched cells/weights")
    if not np.all(np.isin(cells, [0, 1, 2, 3])) or not np.all(np.isfinite(weights)):
        raise ValueError("Invalid cell index or weight")
    counts = np.bincount(cells.astype(int), weights=weights, minlength=4)
    if counts.sum() <= 0:
        raise ValueError("Non-positive four-cell normalization")
    return counts / counts.sum()


def neff(cells, weights):
    cells, weights = np.asarray(cells), np.asarray(weights, dtype=float)
    out = np.empty(4)
    for k in range(4):
        wk = weights[cells == k]
        den = np.sum(wk * wk)
        out[k] = (np.sum(wk) ** 2 / den) if den > 0 else np.nan
    return out


def contrast_diagnostics(C):
    C = np.asarray(C, dtype=float)
    if C.shape != (4, 4):
        raise ValueError("Expected four-cell covariance")
    C3 = A @ ((C + C.T) / 2) @ A.T
    eigenvalues = np.linalg.eigvalsh(C3)
    return {
        "rank": int(np.linalg.matrix_rank(C3)),
        "eigenvalues": eigenvalues.tolist(),
        "condition_number": float(np.linalg.cond(C3)),
        "positive_definite": bool(np.all(eigenvalues > 0)),
    }
