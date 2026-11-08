"""Fail-closed primary CERN-source probe and independent 1D numerical ports.

The Hessian, R-1 sample covariance and 1D smoothing formulas were reconciled
against a SHA-256-pinned CERN multifold_util.py source snapshot in CI run
42390285792. The mutable upstream master URL is NOT an immutable CERN commit,
and none of these ports defines an official 2D covariance or p-value.
Only fetched source text/AST is inspected; remote Python is NEVER executed.
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

# CERN master content fetched in GitHub CI run 42390199178 on 2026-11-07.
# Function bodies examined in the CI logs. Hash pinning authenticates this
# reviewed source snapshot, not a release tag or an approved 2D covariance.
REVIEWED_PRIMARY_SHA256 = "cf43074fb3635b5c484dd1f35b9dc95cea938d86d206b4a2e83ab1f739e73d7f"
REVIEWED_FUNCTION_SHA256 = {
    "fill_cov_matrix": "3783c2b851eabe440b95b629a048c4b575b82400c0e6185e662f06fe816530b4",
    "smooth_uncertainty": "86484ad56858e46a4082d98446aea1ce4c01ef07cd11fa5f41ac36d2870d3429",
    "corr_matrix": "77f617b0639f3ae012a6e3a2469860251de9d12cb192c1fa29de746da305a4f2",
}


def matches_reviewed_primary_source(result: dict) -> bool:
    """Require exact full-file and all three function-body hashes."""
    return (result.get("parse_status") == "PARSED_PYTHON"
            and result.get("source_sha256") == REVIEWED_PRIMARY_SHA256
            and all(result.get("functions", {}).get(name, {}).get("body_sha256") == digest
                    for name, digest in REVIEWED_FUNCTION_SHA256.items()))



def covariance_port(differences, mean=None):
    """Numerical port of pinned CERN Hessian sum or R-1 replica covariance."""
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
    """Source-aligned signed 1D Gaussian smoother; NEVER flatten 2D for inference.

    The hash-pinned CERN function uses log(centers) when the first center is
    positive, otherwise linear centers; Gaussian width is coordinate range/10.
    This port is independently tested against the inspected function formula,
    but no physical two-dimensional bin-center kernel is source-specified.
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
    result["reviewed_primary_source_hash_match"] = matches_reviewed_primary_source(result)
    result["official_source_semantics_verified"] = result["reviewed_primary_source_hash_match"]
    if result["reviewed_primary_source_hash_match"]:
        for name in FUNCTIONS:
            result["functions"][name]["status"] = "REVIEWED_PRIMARY_SOURCE_BODY_HASH_MATCH"
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
