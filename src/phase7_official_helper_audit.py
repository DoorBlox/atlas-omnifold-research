"""Fail-closed primary-source probe and independently testable 1D reference ports.

The ports below reproduce formulas claimed by an *independent* GitHub port,
not an authenticated revision of CERN's multifold_util.py. They are NOT a
validated two-dimensional covariance prescription or a significance test.
Only the remote source's text/AST is inspected; downloaded code is NEVER run.
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
from pathlib import Path
from typing import Callable
from urllib.request import Request, urlopen

import numpy as np

OFFICIAL_URLS = (
    "https://gitlab.cern.ch/atlas-physics/public/sm-z-jets-omnifold-2024/-/raw/master/multifold_util.py",
    "https://gitlab.cern.ch/api/v4/projects/atlas-physics%2Fpublic%2Fsm-z-jets-omnifold-2024/repository/files/multifold_util.py/raw?ref=master",
)
SECONDARY_PORT = (
    "https://github.com/aashirvad08/omnifold-publication/blob/"
    "c7ffa31628eb88b0a8b987d7e89c10ea29fb4624/"
    "omnifold_publication/uncertainty.py"
)
FUNCTIONS = ("fill_cov_matrix", "smooth_uncertainty", "corr_matrix")


def covariance_port(differences, mean=None):
    """SECONDARY-port hypothesis: Hessian sum or unbiased replica covariance."""
    arr = np.asarray(differences, dtype=float)
    if arr.ndim != 2 or arr.shape[0] == 0 or arr.shape[1] == 0:
        raise ValueError("Expected a nonempty 2D source-by-bin matrix")
    if not np.isfinite(arr).all():
        raise ValueError("Nonfinite source matrix")
    if mean is None:
        return arr.T @ arr
    center = np.asarray(mean, dtype=float)
    if arr.shape[0] < 2 or center.shape != (arr.shape[1],) or not np.isfinite(center).all():
        raise ValueError("Sample covariance requires two replicas and finite bin means")
    x = arr - center
    return x.T @ x / (arr.shape[0] - 1)


def smooth_1d_port(signed_shift, bin_centers):
    """SECONDARY-port 1D Gaussian smoothing; *never* flatten 2D for inference.

    The secondary implementation uses coordinate log(centers) if the first
    center is positive, otherwise linear centers; kernel sigma = range/10.
    The operation acts on a SIGNED 1D shift prior to forming its outer product.
    These are secondary claims until the CERN function body is retrieved.
    """
    y = np.asarray(signed_shift, dtype=float)
    centers = np.asarray(bin_centers, dtype=float)
    if (y.ndim != 1 or centers.ndim != 1 or y.size != centers.size or y.size < 2
            or not np.isfinite(y).all() or not np.isfinite(centers).all()
            or not np.all(np.diff(centers) > 0)):
        raise ValueError("Needs signed 1D values with strictly increasing finite centers")
    x = np.log(centers) if centers[0] > 0 else centers
    width = (x[-1] - x[0]) / 10.
    kernel = np.exp(-0.5 * ((x[:, None] - x[None, :]) / width)**2)
    return kernel @ y / kernel.sum(axis=1)


def audit_source_text(content: str) -> dict:
    """Capture exact Python function locations/hashes; do not execute remote code."""
    if not isinstance(content, str):
        raise TypeError("Expected UTF-8 source text")
    result = {
        "official_source_retrieved": True,
        "source_sha256": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "parse_status": "PARSED_PYTHON",
        "functions": {},
        "official_source_semantics_verified": False,
        "G5": "PROVISIONAL",
        "G8": "UNVERIFIED",
        "G12": "UNVERIFIED",
        "G15": "NO_GO",
        "inference_permission": "NO_GO",
    }
    try:
        tree = ast.parse(content)
    except (SyntaxError, ValueError):
        result["parse_status"] = "INVALID_PYTHON"
        result["functions"] = {name: {"status": "SYNTAX_UNAVAILABLE"} for name in FUNCTIONS}
        return result
    source_lines = content.splitlines(keepends=True)
    functions = {node.name: node for node in tree.body
                 if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for name in FUNCTIONS:
        node = functions.get(name)
        if node is None:
            result["functions"][name] = {"status": "FUNCTION_NOT_FOUND"}
            continue
        body = "".join(source_lines[node.lineno - 1:node.end_lineno])
        calls = sorted({n.func.id if isinstance(n.func, ast.Name) else n.func.attr
                        for n in ast.walk(node) if isinstance(n, ast.Call)
                        and isinstance(n.func, (ast.Name, ast.Attribute))})
        result["functions"][name] = {
            "status": "BODY_RETRIEVED_NOT_SEMANTICALLY_VALIDATED",
            "start_line": node.lineno,
            "end_line": node.end_lineno,
            "body_sha256": hashlib.sha256(body.encode("utf-8")).hexdigest(),
            "calls": calls,
        }
    return result


def fetch_source(url: str) -> str:
    req = Request(url, headers={"User-Agent": "atlas-phase7-method-audit/1.0",
                                "Accept": "text/plain"})
    with urlopen(req, timeout=12) as resp:
        body = resp.read(600_001)
        if len(body) > 600_000:
            raise ValueError("Official Python source exceeds bounded text fetch")
    return body.decode("utf-8")


def run(out: Path, fetcher: Callable[[str], str] = fetch_source) -> dict:
    """Best-effort retrieval; network errors never convert into verified physics."""
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    errors = []
    data = None
    used_url = None
    for url in OFFICIAL_URLS:
        try:
            data = fetcher(url)
            used_url = url
            break
        except (OSError, ValueError, UnicodeError) as exc:
            errors.append(f"{type(exc).__name__}: {str(exc)[:200]}")
    if data is None:
        report = {
            "official_source_retrieved": False,
            "parse_status": "SOURCE_UNAVAILABLE",
            "functions": {name: {"status": "SOURCE_UNAVAILABLE"} for name in FUNCTIONS},
            "fetch_error": "; ".join(errors),
            "official_source_semantics_verified": False,
            "G5": "PROVISIONAL", "G8": "UNVERIFIED", "G12": "UNVERIFIED",
            "G15": "NO_GO", "inference_permission": "NO_GO",
        }
    else:
        report = audit_source_text(data)
        report["source_url_used"] = used_url
    report.update({
        "official_source_urls_tried": list(OFFICIAL_URLS if data is None else OFFICIAL_URLS[:OFFICIAL_URLS.index(used_url)+1]),
        "source_ref": "master (mutable; use SHA-256 to track retrieved content)",
        "secondary_reference_port": SECONDARY_PORT,
        "secondary_port_is_official": False,
        "dd_1d_model": "Notebook uses signed (weights_dd-target_dd)*nominal/target_dd before Hessian covariance; no DD smoothing claimed",
        "sherpa_1d_model": "Notebook smooths signed Sherpa shift over ordered 1D bin centers before Hessian covariance; kernel parameters from secondary port, not primary verified",
        "two_dimensional_decision": "No prescribed 2D smoothing coordinate or validated 2D source correlation; preserve four prespecified DD/Sherpa models, never flatten the 2x2 table or select by observed real data fit",
        "coverage_status": "Single pseudodata truth comparison and conditional toys are not experimental frequentist coverage",
    })
    (out / "official_helper_source_audit.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("outputs/official-helper"))
    args = parser.parse_args()
    result = run(args.out)
    print(json.dumps({
        "source_retrieved": result["official_source_retrieved"],
        "parse_status": result["parse_status"],
        "source_sha256": result.get("source_sha256"),
        "function_status": {name: value["status"] for name, value in result["functions"].items()},
        "G15": result["G15"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
