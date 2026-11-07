"""Freeze and verify small, immutable 2x2 ATLAS-derived statistics.

No raw events are included. Frozen covariance matrices are NOT enough to
change event selection/binning or reproduce a different unfolding treatment.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from pathlib import Path

import numpy as np

SOURCE = {
    "real": {
        "run_id": 42324639484, "artifact": "phase7-preflight-12",
        "files": {
            "bin_spec_covariance.json": "90c7bddf7bd5c61be63d18e3a8d9d3d80680ebcc09c398528a937010f25f8ab4",
            "covariance_total.npy": "b78c81356f88a2c6405e7e3221c9d7230991a020fd1a4ee6ac4fd2bb2629fb28",
            "provisional_covariance_status.json": "f1564bccc2b24c87d19193df09c07d63ef1e2aed4261bbeb39c061637a104b7e",
            "real_2x2_cells.csv": "89d84c06602793a6d5381f35d170034c19e8d8753854525465d3a4204d9da040",
            "source_covariances.npz": "2dfcbf303eef95e1dca17e31f064ac130c46a862d506122bc603103ce0595ec5",
            "source_manifest.csv": "592724253ea70dd03dda0c889d8dac456cefc05cf52d9d9249132344012c776d",
        },
    },
    "pseudo": {
        "run_id": 42327464929, "artifact": "phase7-preflight-17",
        "files": {
            "pseudo_bin_spec.json": "e372bebc46427a5b16007b5d9b846a6440caae0dac4cff1b404f3b5fcf652893",
            "pseudo_closure_status.json": "2dd2f646b6e97ab4fb8d1f3529f060d4dbf2c4fbccccdd2e8c434866ec07102f",
            "pseudo_closure_cells.csv": "e2dc66b6ca263efd3735978e97ebbae82c08a0b608a5e603c1407e8aa4961037",
            "pseudo_covariance_total.npy": "059e30bf98b122512cd2292a3821c449668ce70d1c26dd0df2e01d739a8bb653",
            "pseudo_source_covariances.npz": "7467c5725d943b368d124911357c3d522f1e3862e88b5d446f8bccea5b60305c",
            "pseudo_source_manifest.csv": "e3ad5b1de6f1eaf1652bcd89d0d620baadc31d014ec31beaf376d8256038988a",
        },
    },
}
FORMAT = "atlas-omnifold-derived-2x2/v1"
DOI = "10.5281/zenodo.11507450"
ARCHIVE_MD5 = "9b838510f41e1d5a8b26d7f3c5b2ca42"
COUNT_EXPECTED = {
    "real": (100, 25, 100), "pseudo": (25, 25, 100)
}
FAMILIES = ("weights_bootstrap_data", "weights_bootstrap_mc", "weights_ensemble")


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as f:
        for data in iter(lambda: f.read(1024 * 1024), b''):
            digest.update(data)
    return digest.hexdigest()


def _require_file(path: Path, digest: str) -> None:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"Missing or unsafe derived file: {path}")
    if path.stat().st_size > 65536:
        raise ValueError(f"Derived file too large; refuses event-level input: {path}")
    if _sha(path) != digest:
        raise ValueError(f"Official-run file checksum mismatch: {path}")


def _count_replicas(manifest: Path) -> tuple[int, int, int]:
    with manifest.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    counts = []
    for family in ("data_bootstrap", "mc_training_bootstrap", "nn_ensemble"):
        found = [x for x in rows if x['source'] == family]
        if len(found) != 1:
            raise ValueError(f"Missing/duplicate family: {family}")
        prefix = FAMILIES[len(counts)]
        names = found[0]['input'].split(',')
        indexes = []
        for x in names:
            m = re.fullmatch(re.escape(prefix) + r'_(\d+)', x)
            if not m:
                raise ValueError(f"Unexpected source column: {x}")
            indexes.append(int(m.group(1)))
        if sorted(indexes) != list(range(len(indexes))):
            raise ValueError(f"Noncontiguous or duplicate replica indices: {family}")
        counts.append(len(indexes))
    return tuple(counts)


def verify(root: Path) -> dict:
    root = Path(root)
    proof = json.loads((root / 'provenance.json').read_text(encoding='utf-8'))
    if proof.get('format') != FORMAT or proof.get('zenodo_doi') != DOI or proof.get('archive_md5') != ARCHIVE_MD5:
        raise ValueError("Invalid frozen-snapshot identity")
    if proof.get('sources') != SOURCE:
        raise ValueError("Frozen source manifest drifted")
    sizes = {}
    for kind, record in SOURCE.items():
        directory = root / kind
        if not directory.is_dir() or directory.is_symlink():
            raise ValueError(f"Expected derived directory missing: {directory}")
        actual = {p.name for p in directory.iterdir()}
        expected = set(record['files'])
        if actual != expected:
            raise ValueError(f"Unexpected/missing derived files: {kind} {actual ^ expected}")
        for name, digest in record['files'].items():
            _require_file(directory / name, digest)
        names = ('source_manifest.csv' if kind == 'real' else 'pseudo_source_manifest.csv')
        if _count_replicas(directory / names) != COUNT_EXPECTED[kind]:
            raise ValueError(f"Incorrect bootstrap/NN replica counts in {kind}")
        npzname = 'source_covariances.npz' if kind == 'real' else 'pseudo_source_covariances.npz'
        totalname = 'covariance_total.npy' if kind == 'real' else 'pseudo_covariance_total.npy'
        with np.load(directory / npzname, allow_pickle=False) as matrices:
            if len(matrices.files) != 29:
                raise ValueError(f"Expected 29 individual covariance sources in {kind}")
            components = [matrices[name] for name in matrices.files]
        if any(c.shape != (4, 4) or not np.isfinite(c).all() for c in components):
            raise ValueError("Invalid source covariance dimensions/finiteness")
        total = np.load(directory / totalname, allow_pickle=False)
        if total.shape != (4, 4) or not np.allclose(np.sum(components, axis=0), total, atol=1e-12, rtol=1e-10):
            raise ValueError(f"Source covariance sum inconsistent for {kind}")
        if not np.allclose(total @ np.ones(4), 0, atol=1e-11) or not np.allclose(total, total.T, atol=1e-12):
            raise ValueError("Covariance normalization null/symmetry check failed")
        spec_name = 'bin_spec_covariance.json' if kind == 'real' else 'pseudo_bin_spec.json'
        spec = json.loads((directory / spec_name).read_text())
        if not np.isclose(spec['mass_star'], 10.594606399536133, atol=1e-10) or spec['tracks_star'] != 11:
            raise ValueError("Generator-frozen thresholds differ from authoritative run")
        cellname = 'real_2x2_cells.csv' if kind == 'real' else 'pseudo_closure_cells.csv'
        with (directory / cellname).open(newline='', encoding='utf-8') as f:
            cells = list(csv.DictReader(f))
        if [x['cell'] for x in cells] != ['LL', 'LH', 'HL', 'HH']:
            raise ValueError("Incorrect 2x2 cell ordering")
        columns = ('generator_fraction', 'unfolded_fraction') if kind == 'real' else ('independent_target_truth_fraction', 'pseudo_unfolded_fraction')
        for col in columns:
            values = np.array([float(x[col]) for x in cells])
            if not np.isfinite(values).all() or (values < 0).any() or not np.isclose(values.sum(), 1., atol=1e-8):
                raise ValueError(f"Invalid normalized cell fractions in {kind}")
        status_name = 'provisional_covariance_status.json' if kind == 'real' else 'pseudo_closure_status.json'
        if 'NO_GO' not in (directory / status_name).read_text().replace('-', '_').upper():
            raise ValueError(f"Missing inferential NO-GO guard in {kind}")
        sizes[kind] = sum((directory / n).stat().st_size for n in record['files'])
    return {"verified": True, "format": FORMAT, "derived_bytes": sum(sizes.values()),
            "sources": {k: x['run_id'] for k, x in SOURCE.items()}, "inference": "NO_GO"}


def build(real_source: Path, pseudo_source: Path, out: Path) -> dict:
    out = Path(out)
    if out.exists() and any(out.iterdir()):
        raise ValueError(f"Output is non-empty; refusing overwrite: {out}")
    for kind, src in (("real", real_source), ("pseudo", pseudo_source)):
        for filename, digest in SOURCE[kind]['files'].items():
            _require_file(Path(src) / filename, digest)
    for kind, src in (("real", real_source), ("pseudo", pseudo_source)):
        (out / kind).mkdir(parents=True, exist_ok=True)
        for filename in SOURCE[kind]['files']:
            shutil.copyfile(Path(src) / filename, out / kind / filename)
    proof = {"format": FORMAT, "zenodo_doi": DOI, "archive_md5": ARCHIVE_MD5,
             "sources": SOURCE, "scientific_gate": "G15_NO_GO",
             "scope": "Lossless official 4-cell fractions, provisional covariances and manifests; no events"}
    (out / 'provenance.json').write_text(json.dumps(proof, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    return verify(out)


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest='command', required=True)
    freeze = sub.add_parser('build')
    freeze.add_argument('--real-source', type=Path, required=True)
    freeze.add_argument('--pseudo-source', type=Path, required=True)
    freeze.add_argument('--out', type=Path, default=Path('data/derived/phase7-v1'))
    test = sub.add_parser('verify')
    test.add_argument('--root', type=Path, default=Path('data/derived/phase7-v1'))
    args = parser.parse_args()
    result = build(args.real_source, args.pseudo_source, args.out) if args.command == 'build' else verify(args.root)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
