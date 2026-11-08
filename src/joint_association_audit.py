"""Descriptive joint-association audit for frozen 2x2 ATLAS mass/track cells.

This is algebra on published four-cell fractions, not experimental covariance,
coverage, significance, or a generator-compatibility test.

Usage:
    python -m src.joint_association_audit --cells results/four-cell-v1/tables/joint_cells.csv
"""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from typing import Mapping

CELLS = ("LL", "LH", "HL", "HH")


def coordinates(fractions: Mapping[str, float]) -> dict[str, float]:
    """Return low-category marginals, binary-indicator covariance D and log odds."""
    if set(fractions) != set(CELLS):
        raise ValueError("Expected exactly LL, LH, HL, HH cells")
    p = {cell: float(fractions[cell]) for cell in CELLS}
    if not all(math.isfinite(x) and x > 0 for x in p.values()):
        raise ValueError("Cell fractions must be finite and strictly positive")
    if not math.isclose(sum(p.values()), 1.0, rel_tol=0, abs_tol=1e-10):
        raise ValueError("Four-cell distribution must be normalized")
    m = p["LL"] + p["LH"]
    n = p["LL"] + p["HL"]
    d = p["LL"] - m*n
    log_odds = math.log(p["LL"]*p["HH"]/(p["LH"]*p["HL"]))
    return {"mass_low":m, "multiplicity_low":n,
            "indicator_covariance_D":d, "log_odds_L":log_odds}


def cells_from_coordinates(m: float, n: float, d: float) -> dict[str, float]:
    """Recover a positive four-cell shape from marginals and indicator covariance."""
    p = {"LL":m*n+d, "LH":m*(1-n)-d,
         "HL":n*(1-m)-d, "HH":(1-m)*(1-n)+d}
    coordinates(p)
    return p


def compare(measurement: Mapping[str,float], reference: Mapping[str,float]) -> dict:
    """Calculate descriptive deltas and a path-dependent counterfactual."""
    p = coordinates(measurement)
    q = coordinates(reference)
    # Change reference marginals to measurement marginals with D_q held fixed;
    # then change D_q to D_p. This ordering is NOT unique or causal.
    middle = coordinates(cells_from_coordinates(
        p["mass_low"], p["multiplicity_low"], q["indicator_covariance_D"]))
    delta = {k:p[k]-q[k] for k in p}
    marg_path = middle["log_odds_L"]-q["log_odds_L"]
    d_path = p["log_odds_L"]-middle["log_odds_L"]
    assert math.isclose(marg_path+d_path, delta["log_odds_L"], abs_tol=1e-14)
    return {"measurement":p, "reference":q,
            "unfolded_minus_reference":delta,
            "log_odds_counterfactual":{
                "marginal_change_at_reference_D":marg_path,
                "D_change_at_measurement_marginals":d_path,
                "sum":delta["log_odds_L"],
                "interpretation":"path-dependent descriptive arithmetic, not causal attribution or a p-value"}}


def analyze_csv(csv_path: Path) -> dict[str,dict]:
    """Read frozen cells and keep real and pseudodata comparators separate."""
    keyed: dict[str,dict[str,dict[str,float]]] = {}
    with Path(csv_path).open(newline="",encoding="utf-8") as stream:
        for row in csv.DictReader(stream):
            sample,cell = row["sample"],row["cell"]
            if sample not in ("real","pseudo") or cell not in CELLS:
                raise ValueError(f"Unsupported sample or cell: {sample}, {cell}")
            entry = keyed.setdefault(sample, {"measurement":{}, "reference":{}})
            if cell in entry["measurement"]:
                raise ValueError(f"Duplicate {sample}/{cell} row")
            entry["measurement"][cell] = float(row["measurement_fraction"])
            entry["reference"][cell] = float(row["reference_fraction"])
    if set(keyed) != {"real","pseudo"}:
        raise ValueError("Both real and pseudo sample labels are required")
    return {s:compare(v["measurement"],v["reference"]) for s,v in sorted(keyed.items())}


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cells",type=Path,
                        default=Path("results/four-cell-v1/tables/joint_cells.csv"))
    parser.add_argument("--out",type=Path,default=None)
    args=parser.parse_args()
    out={"status":"DESCRIPTIVE_ARITHMETIC_ONLY",
         "data":analyze_csv(args.cells),
         "scope":"No physical covariance calibration, p-value, coverage or generator inference"}
    message=json.dumps(out,indent=2,sort_keys=True)+"\n"
    if args.out is None:
        print(message,end="")
    else:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(message,encoding="utf-8")


if __name__ == "__main__":
    main()
