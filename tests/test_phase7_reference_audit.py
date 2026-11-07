"""Guard the distinction between 1D source inclusion and 2D inference."""
import numpy as np
import pytest
from src.phase7_reference_audit import pseudo_1d_reference_families, compare_family_projection


def fake_sources():
    V=np.vstack([np.eye(3),-np.ones(3)])
    C=V@V.T*.0001
    names=['finite_evaluation_mc','data_bootstrap','mc_training_bootstrap','nn_ensemble',
           'dd_unfolding','sherpa_hidden_variable','topBackground','nonDY']
    names += ['theory'+n for n in ['PSjet','PSsoft','MPI','PSscale','AlphaS','QCD','PDF']]
    names += ['muEffReco','muEffIso','muEffTrack','muEffTrig','muCalID','muCalMS',
              'muCalResBias','muCalScale','pileup','lumi','trackEffMain','trackEffJet',
              'trackFake','trackPtScale']
    return {n:C.copy() for n in names}


def test_reference_is_15_family_subset_of_29():
    components=fake_sources()
    subset=pseudo_1d_reference_families(components)
    assert len(components)==29 and len(subset)==15
    assert 'trackEffMain' not in subset
    assert 'lumi' not in subset
    assert {'dd_unfolding','sherpa_hidden_variable'} <= set(subset)


def test_reference_family_counterfactual_does_not_return_a_pvalue():
    result=compare_family_projection(fake_sources(),np.array([.01,-.02,.03,-.02]))
    assert result['family_subset']['uncalibrated_quadratic'] > result['full_2d']['uncalibrated_quadratic']
    assert np.isclose(result['family_subset']['source_trace_share'],15/29)
    assert result['G15']=='NO-GO'
    assert 'p_value' not in str(result)


def test_missing_reference_source_fails_closed():
    components=fake_sources()
    del components['dd_unfolding']
    with pytest.raises(ValueError,match='Missing'):
        pseudo_1d_reference_families(components)
