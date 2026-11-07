"""Test-first regression protection for descriptive official pseudodata closure."""
import json
import numpy as np
import pandas as pd
import pytest
from src.phase7_covariance import SYST
from src.phase7_closure import truth_projection, evaluate_closure, scenario_sensitivity, run


def _synthetic_frame(n=80):
    m = np.tile([1.0, 1.0, 2.0, 2.0, 3.0, 3.0, 4.0, 4.0], n // 8)
    tr = np.tile([1, 3, 1, 3, 1, 3, 1, 3], n // 8)
    data = {
        'pT_trackj1': np.full(n, 10.), 'm_trackj1': m,
        'Ntracks_trackj1': tr, 'weight_mc': np.ones(n),
        'weights_nominal': 1.0 + 0.015 * (m < 2),
        'weights_dd': 1.0 + 0.01 * (m < 2),
        'target_dd': np.ones(n),
    }
    for i, name in enumerate(SYST):
        data['weights_' + name] = np.array(data['weights_nominal']) * (1 + .001 * (i + 1) * (tr < 2))
    for prefix in ('weights_bootstrap_data', 'weights_bootstrap_mc', 'weights_ensemble'):
        for i in range(4):
            data[f'{prefix}{i}'] = np.array(data['weights_nominal']) * (1 + .02 * (i - 1.5) * (m < 2))
    return pd.DataFrame(data)


def test_truth_uses_target_mc_weight_and_selection(tmp_path):
    df = pd.DataFrame({
        'pT_trackj1': [10.,10.,10.,10.,2.],
        'm_trackj1': [1.,1.,3.,3.,1.],
        'Ntracks_trackj1': [1,3,1,3,1],
        'weight_mc': [1.,2.,3.,4.,100.],
    })
    path = tmp_path / 'target.h5'
    df.to_hdf(path, key='df', format='fixed')
    data = truth_projection(path, {'mass_star':2., 'tracks_star':2}, chunksize=2)
    np.testing.assert_allclose(data['shape'], [.1,.2,.3,.4])
    np.testing.assert_allclose(data['effective_count'], [1.,1.,1.,1.])
    assert data['rows'] == 4
    assert 'weights_nominal' not in data


def test_missing_target_weight_fails_closed(tmp_path):
    path = tmp_path / 'bad.h5'
    pd.DataFrame({'pT_trackj1': [10], 'm_trackj1':[1], 'Ntracks_trackj1':[1],
                  'weights_nominal':[1]}).to_hdf(path,key='df',format='fixed')
    with pytest.raises(KeyError,match='weight_mc'):
        truth_projection(path, {'mass_star':2,'tracks_star':2})


def test_closure_contrast_and_sensitivity_are_not_pvalues():
    target = np.array([.25,.25,.25,.25])
    p = np.array([.27,.23,.24,.26])
    B = np.vstack([np.eye(3), -np.ones(3)])
    C = .0004*(B@B.T)
    parts = {'data_bootstrap':C, 'dd_unfolding':C*.1,
             'sherpa_hidden_variable':C*.1}
    result = evaluate_closure(target,p,parts)
    assert result['squared_mahalanobis_UNCALIBRATED'] > 0
    assert result['contrast_rank'] == 3
    assert 'p_value' not in result
    scenarios = scenario_sensitivity(target,p,parts)
    assert len(scenarios) >= 4
    assert all('p_value' not in row for row in scenarios)
    assert scenarios[0]['scenario'] == 'all_components_provisional'


def test_synthetic_end_to_end_no_physics_pvalue(tmp_path):
    root=tmp_path/'work'/'files'
    (root/'data').mkdir(parents=True)
    (root/'pseudodata').mkdir(parents=True)
    df=_synthetic_frame()
    df.to_hdf(root/'data'/'multifold.h5',key='df',format='fixed')
    df.to_hdf(root/'pseudodata'/'multifold.h5',key='df',format='fixed')
    df.to_hdf(root/'pseudodata'/'multifold_sherpa.h5',key='df',format='fixed')
    df.to_hdf(root/'pseudodata'/'multifold_nonDY.h5',key='df',format='fixed')
    target=df[['pT_trackj1','m_trackj1','Ntracks_trackj1','weight_mc']].copy()
    target['weight_mc'] *= 2
    target.to_hdf(root/'pseudodata'/'target.h5',key='df',format='fixed')
    out=tmp_path/'output'
    res=run(tmp_path/'work',out)
    assert res['status']=='EXECUTED_PROVISIONAL_PSEUDODATA_CLOSURE'
    assert res['inference_permission']=='NO_GO'
    assert 'p_value' not in json.dumps(res)
    for path in ('pseudo_closure_cells.csv','pseudo_covariance_total.npy',
                 'pseudo_closure_status.json','pseudo_source_manifest.csv',
                 'pseudo_covariance_sensitivity.csv','pseudo_bin_spec.json'):
        assert (out/path).exists()
    assert json.loads((out/'pseudo_bin_spec.json').read_text())['tracks_star']==1
