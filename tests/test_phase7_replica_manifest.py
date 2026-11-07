"""Real and pseudodata have *different* bootstrap counts; detect manifest drift."""
import csv
import numpy as np
import pytest
from src.phase7_calibration import manifest_replica_counts, study

PREFIXES = {'data_bootstrap':'weights_bootstrap_data',
            'mc_training_bootstrap':'weights_bootstrap_mc',
            'nn_ensemble':'weights_ensemble'}


def write_manifest(tmp_path, counts):
    path = tmp_path / 'manifest.csv'
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['source','family','input'])
        writer.writeheader()
        for family,prefix in PREFIXES.items():
            writer.writerow({'source':family,'family':'replica_family',
                             'input':','.join(f'{prefix}_{i}' for i in range(counts[family]))})
    return path


def test_actual_replica_counts_are_manifest_defined(tmp_path):
    path = write_manifest(tmp_path, {'data_bootstrap':100, 'mc_training_bootstrap':25, 'nn_ensemble':100})
    assert manifest_replica_counts(path) == {'data_bootstrap':100, 'mc_training_bootstrap':25, 'nn_ensemble':100}
    path = write_manifest(tmp_path, {'data_bootstrap':25, 'mc_training_bootstrap':25, 'nn_ensemble':100})
    assert manifest_replica_counts(path)['data_bootstrap'] == 25


def test_noncontiguous_manifest_fails_closed(tmp_path):
    path = write_manifest(tmp_path, {'data_bootstrap':25, 'mc_training_bootstrap':25, 'nn_ensemble':100})
    path.write_text(path.read_text().replace('weights_bootstrap_data_1,','weights_bootstrap_data_4,'))
    with pytest.raises(ValueError,match='contiguous'):
        manifest_replica_counts(path)


def test_study_uses_explicit_counts_and_rejects_partial_input():
    B = np.vstack([np.eye(3),-np.ones(3)])
    C = B @ B.T * .001
    sources = {'data_bootstrap':C*.1,'mc_training_bootstrap':C*.1,'nn_ensemble':C*.1,'stable':C}
    for n in (25,100):
        counts = {'data_bootstrap':n,'mc_training_bootstrap':25,'nn_ensemble':100}
        result = study(sources,toys=512,seed=1024,replica_counts=counts)
        assert result['replica_counts']['data_bootstrap'] == n
    with pytest.raises(ValueError,match='all three'):
        study(sources,toys=512,seed=1024,replica_counts={'data_bootstrap':25})
