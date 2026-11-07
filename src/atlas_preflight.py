"""Fail-closed official ATLAS archive acquisition and HDF5 schema audit.

No physics inference is performed by this module.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import sys
import urllib.request
import zipfile

import h5py

ARCHIVE_URL = "https://zenodo.org/records/11507450/files/files.zip?download=1"
EXPECTED_MD5 = "9b838510f41e1d5a8b26d7f3c5b2ca42"
ALLOWED = {
    "files/data/multifold.h5",
    "files/data/multifold_sherpa.h5",
    "files/data/multifold_nonDY.h5",
    "files/pseudodata/multifold.h5",
    "files/pseudodata/multifold_sherpa.h5",
    "files/pseudodata/multifold_nonDY.h5",
    "files/pseudodata/target.h5",
}
SMALL_SET = {"files/data/multifold.h5", "files/pseudodata/multifold.h5"}
COVARIANCE_SET = SMALL_SET | {"files/data/multifold_sherpa.h5", "files/data/multifold_nonDY.h5"}
CHUNK = 8 * 1024 * 1024


def file_md5(path: Path) -> str:
    digest = hashlib.md5()  # noqa: S324 - official archive integrity checksum, not authentication
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(CHUNK), b""):
            digest.update(block)
    return digest.hexdigest()


def acquire(root: Path, archive_url: str = ARCHIVE_URL) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    archive = root / "files.zip"
    if archive.exists() and file_md5(archive) == EXPECTED_MD5:
        return archive
    if archive.exists():
        archive.unlink()
    part = root / "files.zip.partial"
    if part.exists():
        part.unlink()  # avoid corrupt resumes when upstream does not support HTTP Range
    request = urllib.request.Request(archive_url, headers={"User-Agent": "atlas-omnifold-kti/0.1"})
    with urllib.request.urlopen(request, timeout=90) as source, part.open("wb") as target:
        while block := source.read(CHUNK):
            target.write(block)
    received = file_md5(part)
    if received != EXPECTED_MD5:
        part.unlink(missing_ok=True)
        raise RuntimeError(f"Archive MD5 mismatch: got {received}; expected {EXPECTED_MD5}")
    part.rename(archive)
    return archive


def extract_selected(archive: Path, root: Path, include_target: bool = False, include_alternatives: bool = False) -> list[str]:
    wanted = ALLOWED if include_target else (COVARIANCE_SET if include_alternatives else SMALL_SET)
    extracted = []
    with zipfile.ZipFile(archive) as container:
        members = {entry.filename: entry for entry in container.infolist()}
        for filename in sorted(wanted):
            entry = members.get(filename)
            if entry is None:
                raise RuntimeError(f"Official archive missing expected member: {filename}")
            normalized = PurePosixPath(entry.filename)
            if normalized.is_absolute() or ".." in normalized.parts:
                raise RuntimeError(f"Invalid archive member: {filename}")
            destination = root.joinpath(*normalized.parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            free_bytes = shutil.disk_usage(destination.parent).free
            if free_bytes < entry.file_size + 512 * 1024 * 1024:
                raise RuntimeError(f"Not enough free disk to unpack {filename}")
            with container.open(entry) as src, destination.open("wb") as dest:
                shutil.copyfileobj(src, dest, length=CHUNK)
            if destination.stat().st_size != entry.file_size:
                raise RuntimeError(f"Uncompressed size mismatch: {filename}")
            extracted.append(filename)
    return extracted


def inspect_hdf5(path: Path) -> dict:
    record = {"path": str(path), "bytes": path.stat().st_size, "objects": []}
    with h5py.File(path, "r") as handle:
        def visitor(name, obj):
            if len(record["objects"]) >= 5000:
                return
            item = {"name": name, "kind": "dataset" if isinstance(obj, h5py.Dataset) else "group"}
            if isinstance(obj, h5py.Dataset):
                item["shape"] = list(obj.shape)
                item["dtype"] = str(obj.dtype)
                if obj.dtype.names:
                    item["fields"] = list(obj.dtype.names)
            record["objects"].append(item)
        handle.visititems(visitor)
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["smoke", "schema"], required=True)
    parser.add_argument("--root", type=Path, default=Path("work"))
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    parser.add_argument("--include-target", action="store_true",
                        help="Also extract large target and alternative HDF5 files")
    parser.add_argument("--include-alternatives", action="store_true",
                        help="Include nominal + independent real-data alternative HDF5 for covariance")
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    if args.stage == "smoke":
        print(json.dumps({"status": "PASS", "stage": "software-smoke", "python": sys.version}))
        return 0
    archive = acquire(args.root)
    extracted = extract_selected(archive, args.root, include_target=args.include_target, include_alternatives=args.include_alternatives)
    report = {
        "stage": "official-schema-preflight",
        "status": "EXECUTED",
        "zenodo_doi": "10.5281/zenodo.11507450",
        "archive_md5": file_md5(archive),
        "archive_bytes": archive.stat().st_size,
        "extracted": extracted,
        "hdf5": [inspect_hdf5(args.root / name) for name in extracted],
        "inference": "BLOCKED: uncertainty source mapping/covariance/closure not validated",
    }
    (args.out / "schema_preflight.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Official schema audit saved to", args.out / "schema_preflight.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
