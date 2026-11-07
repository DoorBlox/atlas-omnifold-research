"""First real-data 2x2 projection; descriptive only, with G15 explicitly blocked.

Reads only needed columns of the ATLAS fixed-format pandas HDF5 release.
Uncertainty covariance and pseudodata closure are intentionally not attempted here.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

from src.shape import four_cells, fractions, multiplicity_threshold, neff, weighted_median

COLUMNS = ("pT_trackj1", "m_trackj1", "Ntracks_trackj1", "weight_mc", "weights_nominal")


def _decode(array):
    return [x.decode("utf-8") if isinstance(x, bytes) else str(x) for x in array]


def inspect_columns(path: Path) -> dict:
    with h5py.File(path) as file:
        group = file["df"]
        columns = _decode(group["axis0"][:])
        blocks = {}
        for key in group:
            if key.startswith("block") and key.endswith("_items"):
                blocks[key.removesuffix("_items")] = _decode(group[key][:])
        return {"path": str(path), "nrows": len(group["axis1"]), "columns": columns, "blocks": blocks}


def read_fixed_columns(path: Path, names: list[str] | tuple[str, ...]) -> dict[str, np.ndarray]:
    with h5py.File(path) as file:
        group = file["df"]
        seen = {}
        for key in group:
            if key.startswith("block") and key.endswith("_items"):
                prefix = key.removesuffix("_items")
                items = _decode(group[key][:])
                values = group[prefix + "_values"]
                if values.ndim != 2 or values.shape[1] != len(items):
                    raise ValueError(f"Unexpected fixed-block shape in {path}: {prefix}")
                for item, index in zip(items, range(len(items))):
                    if item in names:
                        if item in seen:
                            raise ValueError(f"Duplicate column in HDF5: {item}")
                        seen[item] = np.asarray(values[:, index], dtype=np.float64)
        missing = set(names) - seen.keys()
        if missing:
            raise KeyError(f"Missing required HDF5 columns in {path}: {sorted(missing)}")
        return seen


def selected(table: dict[str, np.ndarray]) -> tuple[dict[str, np.ndarray], int]:
    mask = table["pT_trackj1"] > 5.0
    result = {name: values[mask] for name, values in table.items()}
    if any(not np.all(np.isfinite(x)) for x in result.values()):
        raise ValueError("Non-finite values in selected fiducial sample")
    return result, int(np.count_nonzero(mask))


def save_csv(path: Path, records: list[dict]):
    with path.open("w", newline="", encoding="utf-8") as stream:
        out = csv.DictWriter(stream, fieldnames=list(records[0]))
        out.writeheader()
        out.writerows(records)


def run(real_path: Path, pseudo_path: Path, output: Path) -> dict:
    output.mkdir(parents=True, exist_ok=True)
    inventory = {"real": inspect_columns(real_path), "pseudodata": inspect_columns(pseudo_path)}
    (output / "column_inventory.json").write_text(json.dumps(inventory, indent=2), encoding="utf-8")

    # Real measurement and nominal generator share the same nominal MadGraph event support.
    nominal, rows = selected(read_fixed_columns(real_path, COLUMNS))
    q_weights = nominal["weight_mc"]
    p_weights = nominal["weights_nominal"]
    mass = nominal["m_trackj1"]
    tracks = nominal["Ntracks_trackj1"]

    m_star = weighted_median(mass, q_weights)
    n_star = multiplicity_threshold(tracks, q_weights)
    bin_spec = {
        "definition": "post-exploratory frozen 2x2, generator-only thresholds",
        "selection": "pT_trackj1 > 5 GeV",
        "mass_column": "m_trackj1",
        "track_column": "Ntracks_trackj1",
        "generator_weight_column": "weight_mc",
        "measurement_weight_column": "weights_nominal",
        "mass_threshold": m_star,
        "multiplicity_threshold": n_star,
        "mass_negative_values_kept": True,
        "policy": "Never tune boundaries to unfolded data agreement",
    }
    spec_bytes = (json.dumps(bin_spec, sort_keys=True, indent=2) + "\n").encode("utf-8")
    (output / "bin_spec.json").write_bytes(spec_bytes)
    bin_hash = hashlib.sha256(spec_bytes).hexdigest()

    cells = four_cells(mass, tracks, m_star, n_star)
    q, p = fractions(cells, q_weights), fractions(cells, p_weights)
    effective_q, effective_p = neff(cells, q_weights), neff(cells, p_weights)
    pseudo, pseudo_rows = selected(read_fixed_columns(pseudo_path, COLUMNS))
    pseudo_cells = four_cells(pseudo["m_trackj1"], pseudo["Ntracks_trackj1"], m_star, n_star)
    pseudo_shape = fractions(pseudo_cells, pseudo["weights_nominal"])
    pseudo_mc = fractions(pseudo_cells, pseudo["weight_mc"])
    records = []
    for k, cell in enumerate(("LL", "LH", "HL", "HH")):
        records.append({
            "cell": cell,
            "raw_rows": int(np.count_nonzero(cells == k)),
            "generator_sum_fb": float(q_weights[cells == k].sum()),
            "measurement_sum_fb": float(p_weights[cells == k].sum()),
            "generator_neff": float(effective_q[k]),
            "measurement_neff": float(effective_p[k]),
            "generator_fraction": float(q[k]),
            "measurement_fraction": float(p[k]),
            "descriptive_difference": float(p[k] - q[k]),
            "pseudodata_fraction": float(pseudo_shape[k]),
            "pseudo_generator_fraction": float(pseudo_mc[k]),
        })
    save_csv(output / "cell_support.csv", records)
    source_columns = inventory["real"]["columns"]
    families = {
        "data_bootstrap": sorted(x for x in source_columns if x.startswith("weights_bootstrap_data")),
        "mc_training_bootstrap": sorted(x for x in source_columns if x.startswith("weights_bootstrap_mc")),
        "nn_ensemble": sorted(x for x in source_columns if x.startswith("weights_ensemble")),
        "other_weight_columns": sorted(x for x in source_columns if x.startswith("weights_") and not any(x.startswith(prefix) for prefix in ("weights_bootstrap_data", "weights_bootstrap_mc", "weights_ensemble"))),
    }
    (output / "weight_column_inventory.json").write_text(json.dumps({"source_families_NOT_COVARIANCES": families, "counts": {k: len(v) for k, v in families.items()}}, indent=2), encoding="utf-8")
    result = {
        "status": "EXECUTED DESCRIPTIVE CENTRAL SHAPES ONLY",
        "real_rows_selected": rows,
        "pseudo_rows_selected": pseudo_rows,
        "bin_spec_sha256": bin_hash,
        "sum_generator_fractions": float(q.sum()),
        "sum_measurement_fractions": float(p.sum()),
        "support_neff_at_least_5000": bool(np.all(effective_q >= 5000)),
        "data_stat_uncertainty_less_than_15_percent": "UNVERIFIED",
        "G3_generator_only_thresholds": "PASS",
        "G4_cell_support": "PARTIAL, effective MC computed; data-statistical uncertainty unverified",
        "G5_uncertainty_mapping": "UNVERIFIED",
        "G6_covariance": "UNVERIFIED",
        "G8_calibration": "UNVERIFIED",
        "G11_pseudodata_closure": "UNVERIFIED: known target not yet included",
        "G15_real_data_p_value": "BLOCKED",
        "warning": "The descriptive differences are not validated statistical significances.",
    }
    (output / "projection_status.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("work"))
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    result = run(args.root / "files/data/multifold.h5", args.root / "files/pseudodata/multifold.h5", args.out)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
