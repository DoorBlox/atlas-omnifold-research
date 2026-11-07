"""One-time, lossless (for frozen bins) signed-weight sufficient-statistic extraction.

Preserves four-cell count-level sums and second/mixed moments from published
ATLAS HDF5. Does NOT prescribe 2D source correlations or authorize p-values.
Original frozen v1 normalized results remain untouched and are cross-checked.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

CELL_LABELS = ("LL", "LH", "HL", "HH")
FEATURES = ("pT_trackj1", "m_trackj1", "Ntracks_trackj1")
FILENAME_SET = (
    "files/data/multifold.h5",
    "files/data/multifold_sherpa.h5",
    "files/data/multifold_nonDY.h5",
    "files/pseudodata/multifold.h5",
    "files/pseudodata/multifold_sherpa.h5",
    "files/pseudodata/multifold_nonDY.h5",
)
RECORD_KEYS = ("sum_w", "sum_w2", "sum_w_times_mc", "sum_w_times_nominal")
FORMAT = "atlas-omnifold-phase7-signed-moments-v2"
OFFICIAL_MD5 = "9b838510f41e1d5a8b26d7f3c5b2ca42"


def _sha256(path: Path) -> str:
    out = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            out.update(chunk)
    return out.hexdigest()


def _layout(group):
    mapping = {}
    for name in group:
        if not (name.startswith("block") and name.endswith("_items")):
            continue
        stem = name[:-6]
        arr = group[stem + "_values"]
        items = group[name][:]
        if arr.ndim != 2 or arr.shape[1] != len(items):
            raise ValueError(f"Unsupported pandas fixed-format HDF5 block {stem}")
        for i, raw in enumerate(items):
            col = raw.decode("utf-8") if isinstance(raw, bytes) else str(raw)
            if col in mapping:
                raise ValueError(f"Duplicate HDF5 column: {col}")
            mapping[col] = (stem + "_values", i)
    return mapping


def _cell_codes(mass, tracks, mass_star, tracks_star):
    # Exact historical v1 cell convention.
    return (2 * (mass >= mass_star) + (tracks > tracks_star)).astype(np.int8)


def extract_one(path: Path, thresholds: dict, *, chunk_size: int = 16384) -> dict:
    """Chunked source-preserving summaries; no event records leave this process."""
    path = Path(path)
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    m_star = float(thresholds["mass_star"])
    n_star = int(thresholds["tracks_star"])
    if not np.isfinite(m_star) or n_star < 0:
        raise ValueError("Invalid frozen bin thresholds")
    with h5py.File(path, "r") as h5:
        if "df" not in h5:
            raise KeyError(f"Missing Pandas fixed df group: {path}")
        group = h5["df"]
        mapping = _layout(group)
        mandatory = (*FEATURES, "weight_mc", "weights_nominal")
        for col in mandatory:
            if col not in mapping:
                raise KeyError(f"Missing required HDF5 column: {col}")
        selected = sorted(x for x in mapping if x.startswith("weights_") or x in ("weight_mc", "target_dd"))
        nrows = len(group["axis1"])
        if nrows < 1:
            raise ValueError("Empty HDF5 input")
        counts = np.zeros(4, dtype=np.int64)
        accum = {name: np.zeros((4, 4), dtype=float) for name in selected}
        by_block = {}
        for col in selected:
            block, i = mapping[col]
            by_block.setdefault(block, []).append((col, i))
        if not by_block:
            raise ValueError("No weight columns available")
        for start in range(0, nrows, chunk_size):
            stop = min(start + chunk_size, nrows)
            pt, mass, tracks = (
                np.asarray(group[mapping[col][0]][start:stop, mapping[col][1]], dtype=float)
                for col in FEATURES
            )
            mask = pt > 5.0
            if not np.any(mask):
                continue
            if not (np.isfinite(pt[mask]).all() and np.isfinite(mass[mask]).all()
                    and np.isfinite(tracks[mask]).all()):
                raise ValueError("Nonfinite selected observables")
            cells = _cell_codes(mass[mask], tracks[mask], m_star, n_star)
            counts += np.bincount(cells, minlength=4)
            mc = np.asarray(group[mapping["weight_mc"][0]][start:stop, mapping["weight_mc"][1]], dtype=float)[mask]
            nom = np.asarray(group[mapping["weights_nominal"][0]][start:stop, mapping["weights_nominal"][1]], dtype=float)[mask]
            if not np.isfinite(mc).all() or not np.isfinite(nom).all():
                raise ValueError("Nonfinite selected nominal or MC weights")
            for block, cols in by_block.items():
                rows = np.asarray(group[block][start:stop, :], dtype=float)[mask]
                for name, i in cols:
                    w = rows[:, i]
                    if not np.isfinite(w).all():
                        raise ValueError(f"Nonfinite selected weight in {name}")
                    for k, v in enumerate((w, w*w, w*mc, w*nom)):
                        accum[name][:, k] += np.bincount(cells, weights=v, minlength=4)
        if counts.sum() == 0 or np.any(counts == 0):
            raise ValueError("Selected sample has empty 2x2 cell")
        return {
            "rows_total": int(nrows), "rows_selected": int(counts.sum()),
            "counts": counts.tolist(), "column_count": len(selected),
            "columns": {name: {key: accum[name][:, idx].tolist()
                               for idx, key in enumerate(RECORD_KEYS)} for name in selected},
        }


def _normalize(h):
    v = np.asarray(h, dtype=float)
    if v.shape != (4,) or not np.isfinite(v).all() or v.sum() <= 0:
        raise ValueError("Invalid weighted cell normalization")
    return v/v.sum()


def _read_csv(path, column):
    import csv
    with Path(path).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if tuple(row["cell"] for row in rows) != CELL_LABELS:
        raise ValueError(f"Frozen 2x2 cell order changed: {path}")
    return np.array([float(row[column]) for row in rows])


def frozen_thresholds(snapshot: Path) -> dict:
    from src.phase7_snapshot import verify
    verify(snapshot)
    real = json.loads((Path(snapshot)/"real"/"bin_spec_covariance.json").read_text())
    pseudo = json.loads((Path(snapshot)/"pseudo"/"pseudo_bin_spec.json").read_text())
    if not np.isclose(real["mass_star"], pseudo["mass_star"], rtol=0, atol=1e-12) or real["tracks_star"] != pseudo["tracks_star"]:
        raise ValueError("Real and pseudodata frozen bin specifications differ")
    if real.get("selection") != "pT_trackj1 > 5 GeV" or pseudo.get("selection") != "pT_trackj1 > 5 GeV":
        raise ValueError("Unexpected fiducial selection")
    return {"mass_star": float(real["mass_star"]), "tracks_star": int(real["tracks_star"]), "selection": real["selection"]}


def _check_against_v1(all_samples: dict, snapshot: Path) -> dict:
    snapshot = Path(snapshot)
    comparison = {}
    for key, folder, filename, pfield, qfield in (
        ("real", "real", "real_2x2_cells.csv", "unfolded_fraction", "generator_fraction"),
        ("pseudo", "pseudo", "pseudo_closure_cells.csv", "pseudo_unfolded_fraction", "pseudo_generator_fraction"),
    ):
        nominal = all_samples[key]["nominal"]
        cols = nominal["columns"]
        p, q = _normalize(cols["weights_nominal"]["sum_w"]), _normalize(cols["weight_mc"]["sum_w"])
        p_ref, q_ref = _read_csv(snapshot/folder/filename, pfield), _read_csv(snapshot/folder/filename, qfield)
        if not (np.allclose(p, p_ref, rtol=0, atol=2e-8) and np.allclose(q, q_ref, rtol=0, atol=2e-8)):
            raise ValueError(f"New signed sums do not reproduce frozen {key} v1 fractions")
        if nominal["rows_selected"] != 417401:
            raise ValueError(f"Unexpected official nominal rows in {key}")
        comparison[key] = {"nominal_rows_selected": nominal["rows_selected"], "fraction_check": "PASS",
                           "max_abs_error": float(max(np.max(np.abs(p-p_ref)), np.max(np.abs(q-q_ref))))}
    return comparison


def extract_mode(filename: str) -> tuple[str, str]:
    parts = Path(filename).parts
    if len(parts) != 3 or parts[0] != "files" or parts[1] not in ("data", "pseudodata"):
        raise ValueError(f"Unexpected official file path: {filename}")
    name = {"multifold.h5": "nominal", "multifold_sherpa.h5": "sherpa", "multifold_nonDY.h5": "nonDY"}.get(parts[2])
    if name is None:
        raise ValueError(f"Unexpected alternative name: {filename}")
    return ("real" if parts[1] == "data" else "pseudo"), name


def verify_v2(folder: Path) -> dict:
    folder = Path(folder)
    proof = json.loads((folder/"provenance.json").read_text(encoding="utf-8"))
    if proof.get("format") != FORMAT or proof.get("scientific_gate") != "G15_NO_GO":
        raise ValueError("Invalid version, identity or inference guard")
    expected = {"moments.json", "provenance.json"}
    if {p.name for p in folder.iterdir()} != expected:
        raise ValueError("Unexpected file(s) or missing expected v2 file(s)")
    if _sha256(folder/"moments.json") != proof["moments_sha256"]:
        raise ValueError("Frozen v2 checksum mismatch")
    summary = json.loads((folder/"moments.json").read_text(encoding="utf-8"))
    if summary["format"] != FORMAT or summary["G15"] != "NO_GO":
        raise ValueError("Changed v2 summary scope or inference status")
    if set(summary["samples"]) != {"real", "pseudo"}:
        raise ValueError("Missing real or pseudodata sample")
    for sample in summary["samples"].values():
        if set(sample) != {"nominal", "sherpa", "nonDY"}:
            raise ValueError("Missing alternative in v2")
        for item in sample.values():
            if sum(item["counts"]) != item["rows_selected"] or not item["columns"]:
                raise ValueError("Invalid row-count or weight source schema")
            for records in item["columns"].values():
                if set(records) != set(RECORD_KEYS) or any(len(records[key]) != 4 or not np.isfinite(records[key]).all() for key in RECORD_KEYS):
                    raise ValueError("Invalid four-cell moment")
    return {"verified": True, "moments_bytes": (folder/"moments.json").stat().st_size,
            "format": FORMAT, "G15": "NO_GO"}


def build(root: Path, out: Path, thresholds: dict, *, archive_md5: str = OFFICIAL_MD5,
          enforce_v1: bool = True, snapshot: Path = Path("data/derived/phase7-v1"),
          chunk_size: int = 16384) -> dict:
    root, out = Path(root), Path(out)
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"Output exists / refusing overwrite: {out}")
    if enforce_v1:
        locked = frozen_thresholds(snapshot)
        if locked != thresholds or archive_md5 != OFFICIAL_MD5:
            raise ValueError("Official archive MD5 or immutable v1 bin spec differs")
    samples = {"real": {}, "pseudo": {}}
    filenames = []
    for relative in FILENAME_SET:
        path = root/relative
        if not path.is_file():
            raise FileNotFoundError(path)
        kind, mode = extract_mode(relative)
        stats = extract_one(path, thresholds, chunk_size=chunk_size)
        samples[kind][mode] = stats
        filenames.append({"path": relative, "sha256": _sha256(path),
                          "size_bytes": path.stat().st_size, "rows_total": stats["rows_total"]})
    crosscheck = _check_against_v1(samples, snapshot) if enforce_v1 else {"synthetic": "NOT_OFFICIAL"}
    result = {"format": FORMAT, "status": "DERIVED_SIGNED_MOMENTS_NOT_INFERENCE", "G15": "NO_GO",
              "bin_spec": thresholds, "samples": samples, "v1_crosscheck": crosscheck,
              "scientific_scope": "frozen 2x2 signed per-column first/second/mixed moments; no event-level records",
              "limitations": ["No alternative rebinning or changes in event selection",
                              "Event-level NN/unfolding dependence not reconstructible from moments",
                              "Sherpa/DD 2D source-correlation prescription remains unverified",
                              "No calibrated real-data p-value"]}
    out.mkdir(parents=True, exist_ok=True)
    moments = out/"moments.json"
    moments.write_text(json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False)+"\n",
                       encoding="utf-8")
    proof = {"format": FORMAT, "scientific_gate": "G15_NO_GO",
             "original_archive_zenodo_doi": "10.5281/zenodo.11507450",
             "archive_md5": archive_md5, "source_files": filenames,
             "moments_sha256": _sha256(moments),
             "v1_source_runs": {"real": 42324639484, "pseudo": 42327464929},
             "v1_crosscheck": crosscheck}
    (out/"provenance.json").write_text(json.dumps(proof, sort_keys=True, indent=2)+"\n",
                                        encoding="utf-8")
    verified = verify_v2(out)
    if verified["moments_bytes"] > 2_000_000:
        raise ValueError("Output unexpectedly large; refusing to retain file")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("work"))
    parser.add_argument("--snapshot", type=Path, default=Path("data/derived/phase7-v1"))
    parser.add_argument("--out", type=Path, default=Path("data/derived/phase7-v2"))
    parser.add_argument("--chunk-size", type=int, default=16384)
    args = parser.parse_args()
    result = build(args.root, args.out, frozen_thresholds(args.snapshot),
                   snapshot=args.snapshot, chunk_size=args.chunk_size)
    print(json.dumps({"status": result["status"], "G15": result["G15"],
                      "v1_crosscheck": result["v1_crosscheck"],
                      "source_counts": {k: {name: item["column_count"] for name, item in value.items()}
                                        for k, value in result["samples"].items()}}, indent=2))


if __name__ == "__main__":
    main()
