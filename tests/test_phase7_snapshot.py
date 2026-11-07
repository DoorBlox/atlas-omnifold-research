"""Unit tests for fail-closed lightweight frozen ATLAS result storage."""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from src import phase7_snapshot as snapshot


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture(tmp_path, monkeypatch):
    origin = tmp_path / 'origin'
    sources = {}
    for kind in ('real', 'pseudo'):
        folder = origin / kind
        folder.mkdir(parents=True)
        names = list(snapshot.SOURCE[kind]['files'])
        prefix = '' if kind == 'real' else 'pseudo_'
        b = np.vstack((np.eye(3), -np.ones((1, 3))))
        C = b @ b.T * .0001
        components = {f'source_{i}': np.zeros((4, 4)) for i in range(28)}
        components['data_bootstrap'] = C
        matrix = folder / ('source_covariances.npz' if kind == 'real' else 'pseudo_source_covariances.npz')
        np.savez_compressed(matrix, **components)
        np.save(folder / ('covariance_total.npy' if kind == 'real' else 'pseudo_covariance_total.npy'), C)
        (folder / ('bin_spec_covariance.json' if kind == 'real' else 'pseudo_bin_spec.json')).write_text(
            json.dumps({'mass_star': 10.594606399536133, 'tracks_star': 11}))
        (folder / ('provisional_covariance_status.json' if kind == 'real' else 'pseudo_closure_status.json')).write_text(
            json.dumps({'G15': 'NO-GO'}))
        cellname = 'real_2x2_cells.csv' if kind == 'real' else 'pseudo_closure_cells.csv'
        cols = ['generator_fraction', 'unfolded_fraction'] if kind == 'real' else ['independent_target_truth_fraction', 'pseudo_unfolded_fraction']
        with (folder / cellname).open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['cell', *cols])
            writer.writeheader()
            for name in ('LL', 'LH', 'HL', 'HH'):
                writer.writerow({'cell': name, **{col: 0.25 for col in cols}})
        manname = 'source_manifest.csv' if kind == 'real' else 'pseudo_source_manifest.csv'
        with (folder / manname).open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['source', 'family', 'input'])
            writer.writeheader()
            for family, prefix, count in zip(('data_bootstrap', 'mc_training_bootstrap', 'nn_ensemble'),
                                              snapshot.FAMILIES, snapshot.COUNT_EXPECTED[kind]):
                writer.writerow({'source':family, 'family':'replica_family',
                                 'input': ','.join(f'{prefix}_{i}' for i in range(count))})
        assert set(names) == {p.name for p in folder.iterdir()}
        sources[kind] = {'run_id': snapshot.SOURCE[kind]['run_id'], 'artifact':snapshot.SOURCE[kind]['artifact'],
                         'files': {p.name: _sha(p) for p in folder.iterdir()}}
    monkeypatch.setattr(snapshot, 'SOURCE', sources)
    return origin


def test_frozen_snapshot_roundtrip_and_no_events(tmp_path, monkeypatch):
    origin = _fixture(tmp_path, monkeypatch)
    out = tmp_path / 'frozen'
    result = snapshot.build(origin/'real',origin/'pseudo',out)
    assert result['verified'] is True
    assert result['inference'] == 'NO_GO'
    assert all(p.suffix not in ('.h5','.hdf5') for p in out.rglob('*') if p.is_file())
    assert snapshot.verify(out) == result
    with pytest.raises(ValueError,match='non-empty'):
        snapshot.build(origin/'real',origin/'pseudo',out)


def test_tamper_detected_in_build_and_verify(tmp_path, monkeypatch):
    origin = _fixture(tmp_path, monkeypatch)
    out = tmp_path/'frozen'
    snapshot.build(origin/'real',origin/'pseudo',out)
    path = out/'real'/'real_2x2_cells.csv'
    path.write_text(path.read_text() + 'malicious extra row\n')
    with pytest.raises(ValueError, match='checksum mismatch'):
        snapshot.verify(out)
    original = origin/'real'/'real_2x2_cells.csv'
    original.write_text(original.read_text() + 'malicious extra row\n')
    with pytest.raises(ValueError, match='checksum mismatch'):
        snapshot.build(origin/'real',origin/'pseudo',tmp_path/'oops')


def test_no_extra_files_or_raw_hdf5(tmp_path, monkeypatch):
    origin = _fixture(tmp_path, monkeypatch)
    out = tmp_path / 'frozen'
    snapshot.build(origin/'real',origin/'pseudo',out)
    (out/'real'/'raw_events.h5').write_bytes(b'not allowed')
    with pytest.raises(ValueError, match='Unexpected/missing derived files'):
        snapshot.verify(out)


def test_manifest_missing_family_rejected(tmp_path, monkeypatch):
    origin = _fixture(tmp_path, monkeypatch)
    path = origin/'pseudo'/'pseudo_source_manifest.csv'
    rows = path.read_text().splitlines()
    path.write_text('\n'.join(rows[:2]) + '\n')
    monkeypatch.setitem(snapshot.SOURCE['pseudo']['files'],path.name,_sha(path))
    with pytest.raises(ValueError, match='Missing/duplicate family'):
        snapshot.build(origin/'real',origin/'pseudo',tmp_path/'out')
