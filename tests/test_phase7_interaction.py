"""Tests for non-inferential source-wise marginal / association diagnostics."""
import csv
from pathlib import Path
import json
import numpy as np
import pytest

from src.phase7_interaction import (
    summaries, verify_matrices, load_fractions, analyze_snapshot
)


def toy_matrices():
    A = np.vstack([np.eye(3), -np.ones(3)])
    return {"finite_mc": 0.0002 * (A @ A.T),
            "sherpa_model": np.outer([1., -1., -1., 1.], [1., -1., -1., 1.]) * 0.00003}


def test_identity_and_source_variances_sum():
    p=np.array([0.4,0.1,0.2,0.3]); q=np.array([0.39,0.11,0.21,0.29]);
    ans, table=summaries('real',p,q,toy_matrices())
    assert len(ans)==3 and len(table)==3*2
    assert {x['observable'] for x in ans}=={'mass_low','multiplicity_low','log_odds_ratio'}
    assert abs(ans[0]['difference']-0.0)<1e-12
    assert np.isclose(ans[1]['difference'],.6-.6)
    for row in ans:
        selected=[x for x in table if x['observable']==row['observable']]
        assert np.isclose(sum(x['variance'] for x in selected),row['variance'],atol=1e-12)
        assert np.isclose(sum(x['fraction_of_variance'] for x in selected),1.,atol=1e-10)
        assert row['provisional_standard_error']>=0
        assert 'p_value' not in row
    assert np.isclose(ans[2]['measurement_value'],np.log(0.4*0.3/(0.1*0.2)))


def test_near_zero_cells_and_invalid_covariance_fail_closed():
    p=np.array([.4,.1,.2,.3]); q=np.array([.4,.1,.2,.3])
    with pytest.raises(ValueError,match='strictly positive'):
        summaries('pseudo',np.array([.5,0,.2,.3]),q,toy_matrices())
    corrupted=toy_matrices(); corrupted['finite_mc']=np.ones((4,4))
    with pytest.raises(ValueError,match='normalization'):
        verify_matrices(corrupted)
    with pytest.raises(ValueError,match='sum to one'):
        summaries('pseudo',p,2*q,toy_matrices())


def test_numerical_delta_method_logodds_gradient():
    p=np.array([.4,.1,.2,.3]); q=np.array([.39,.11,.21,.29]);
    C=sum(toy_matrices().values())
    expected=np.array([1/p[0],-1/p[1],-1/p[2],1/p[3]])
    ans,_=summaries('real',p,q,toy_matrices())
    assert np.isclose(ans[-1]['variance'],expected@C@expected)
    assert np.isclose(ans[-1]['difference'],np.log(p[0]*p[3]/(p[1]*p[2]))-np.log(q[0]*q[3]/(q[1]*q[2])))


def test_frozen_official_2x2_snapshot(tmp_path):
    repo = Path(__file__).resolve().parents[1]
    frozen = repo / 'data/derived/phase7-v1'
    if not frozen.exists():
        frozen = repo / '_frozen'
    r = analyze_snapshot(frozen, tmp_path)
    assert r['inference_permission']=='NO_GO'
    assert len(r['metrics'])==6
    real=[x for x in r['metrics'] if x['sample']=='real' and x['observable']=='log_odds_ratio'][0]
    assert 0.94<real['top_source_fraction']<0.96
    assert real['top_source']=='sherpa_hidden_variable'
    assert (tmp_path/'interaction_metrics.csv').is_file()
    assert (tmp_path/'interaction_sources.csv').is_file()
    assert (tmp_path/'interaction_status.json').is_file()
    assert 'p_value' not in json.dumps(r)
