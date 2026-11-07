"""Synthetic-only regression tests for normalized model sensitivity."""
import csv
import json
import numpy as np
import pytest
from src.phase7_model_sensitivity import (
    H, compare_sources, contrast_decorrelate, load_components,
    model_components, quadratic_description, read_shape, run
)


def positive_components():
    B = np.array([[1.,0.,0.],[0.,1.,0.],[0.,0.,1.],[-1.,-1.,-1.]])
    core = B @ B.T * .001
    out = {f'source_{i}': np.zeros((4,4)) for i in range(27)}
    out['dd_unfolding'] = .0003 * np.outer([1,0,-1,0],[1,0,-1,0])
    out['sherpa_hidden_variable'] = .0002 * np.outer([0,1,0,-1],[0,1,0,-1])
    out['source_0'] = core
    return out


def test_helmert_orthonormal_and_normalization():
    np.testing.assert_allclose(H @ H.T,np.eye(3),atol=1e-14)
    np.testing.assert_allclose(H @ np.ones(4),np.zeros(3),atol=1e-14)
    C = positive_components()['dd_unfolding']
    D = contrast_decorrelate(C)
    np.testing.assert_allclose(D @ np.ones(4),np.zeros(4),atol=1e-14)
    assert np.linalg.eigvalsh(D).min() >= -1e-14
    assert not np.allclose(C,D)


def test_all_scenarios_preserve_rank_without_pvalues():
    base = positive_components()
    scenarios = (
        'all_fully_correlated','dd_helmert_decorrelated','sherpa_helmert_decorrelated',
        'both_helmert_decorrelated','half_two_point_amplitude',
        'one_and_half_two_point_amplitude','exclude_dd_stress_only',
        'exclude_sherpa_stress_only','exclude_both_stress_only'
    )
    for scenario in scenarios:
        result=quadratic_description(model_components(base,scenario),
                                      np.array([.01,-.01,.02,-.02]))
        assert result['covariance_rank']==3
        assert result['uncalibrated_quadratic']>=0
        assert 'p_value' not in result
    assert len(compare_sources(base))==29
    with pytest.raises(ValueError):
        model_components(base,'invalid')


def test_invalid_artifact_rejected(tmp_path):
    np.savez(tmp_path/'bad.npz',foo=np.eye(4))
    with pytest.raises(ValueError,match='Expected 29'):
        load_components(tmp_path/'bad.npz')
    (tmp_path/'cells.csv').write_text('cell,q\nLH,0.4\nLL,0.6\n')
    with pytest.raises(ValueError,match='order'):
        read_shape(tmp_path/'cells.csv','q')


def release_fixture(tmp_path):
    a=tmp_path/'real'
    b=tmp_path/'pseudo'
    a.mkdir()
    b.mkdir()
    cov=positive_components()
    np.savez(a/'source_covariances.npz',**cov)
    np.savez(b/'pseudo_source_covariances.npz',**cov)
    np.save(a/'covariance_total.npy',sum(cov.values()))
    np.save(b/'pseudo_covariance_total.npy',sum(cov.values()))
    (a/'bin_spec_covariance.json').write_text(json.dumps({'mass_star':10.5,'tracks_star':11,'selection':'pT_trackj1 > 5 GeV'}))
    (b/'pseudo_bin_spec.json').write_text(json.dumps({'mass_star':10.5,'tracks_star':11,'selection':'pT_trackj1 > 5 GeV'}))
    for dst,left,right,columns in (
        (a,[.25]*4,[.26,.24,.27,.23],('generator_fraction','unfolded_fraction')),
        (b,[.25]*4,[.24,.26,.23,.27],('independent_target_truth_fraction','pseudo_unfolded_fraction')),
    ):
        filename='real_2x2_cells.csv' if dst == a else 'pseudo_closure_cells.csv'
        with (dst/filename).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=['cell',*columns])
            writer.writeheader()
            for i,cell in enumerate(('LL','LH','HL','HH')):
                writer.writerow({'cell':cell,columns[0]:left[i],columns[1]:right[i]})
    return a,b


def test_end_to_end_stays_no_go(tmp_path):
    real,pseudo=release_fixture(tmp_path)
    status=run(real,pseudo,tmp_path/'out')
    assert status['G15']=='NO-GO'
    assert status['scenarios']==9
    assert 'p_value' not in json.dumps(status)
    assert (tmp_path/'out'/'model_sensitivity.csv').exists()
    (pseudo/'pseudo_bin_spec.json').write_text(json.dumps({'mass_star':10.7,'tracks_star':11,'selection':'pT_trackj1 > 5 GeV'}))
    with pytest.raises(ValueError,match='thresholds differ'):
        run(real,pseudo,tmp_path/'out')
