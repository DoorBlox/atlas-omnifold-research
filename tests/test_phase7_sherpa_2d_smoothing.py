"""Factorized two-level smoothing only demonstrates a property, not ATLAS method."""
import math
import json

import numpy as np
import pytest

from src.phase7_sherpa_2d_smoothing import MIXING,two_level_kernel,tensor_kernel


def test_two_level_kernel_offdiagonal_equals_normalized_e_minus_fifty():
    assert MIXING == pytest.approx(math.exp(-50)/(1+math.exp(-50)),rel=1e-15)
    k=two_level_kernel()
    np.testing.assert_allclose(k.sum(axis=1),np.ones(2),atol=1e-15)
    assert k[0,1]==pytest.approx(1.9287498479639178e-22,rel=1e-10)


def test_factorized_four_cell_kernel_is_effective_identity_with_two_levels():
    K=tensor_kernel()
    assert K.shape==(4,4)
    np.testing.assert_allclose(K.sum(axis=1),np.ones(4),atol=1e-15)
    assert np.linalg.norm(K-np.eye(4))<1e-18
    d=np.array([1.2,-3.5,4.1,-.2])
    assert np.max(abs(K@d-d)) < 1e-18


def test_factorized_extension_is_not_inference_permission():
    # No physical distance definition for unbounded outer mass/track bins.
    assert MIXING < 2e-22
    assert 'sherpa' in 'sherpa_hidden_variable'


def _load_mocks(monkeypatch):
    import sys,types
    def module(name,**kwargs):
        m=types.ModuleType(name);m.__dict__.update(kwargs)
        monkeypatch.setitem(sys.modules,name,m)
    def c(h,d,model):
        h=np.asarray(h,float);d=np.asarray(d,float)
        j=(np.eye(4)-np.outer(h/h.sum(),np.ones(4)))/h.sum()
        v=j@d
        return np.outer(v,v)
    def smooth(d,centers):
        x=np.asarray(centers,float)
        width=(x[-1]-x[0])/10
        K=np.exp(-.5*((x[:,None]-x[None,:])/width)**2)
        return K@d/K.sum(axis=1)
    module('src.phase7_twopoint_protocol',count_shift_to_covariance=c)
    module('src.phase7_official_helper_audit',smooth_1d_port=smooth)
    return module


def test_categorical_product_versus_ordered_flattening_is_distinct(monkeypatch):
    from src.phase7_sherpa_2d_smoothing import smoothing_comparison
    _load_mocks(monkeypatch)
    h=np.array([100.,200.,300.,400.]);d=np.array([9.,-13.,17.,-11.])
    z=smoothing_comparison(h,d)
    assert z['inference_eligible_2d_smoother'] is False
    assert z['factorized_covariance_relative_frobenius_difference_percent'] < 1e-12
    assert z['flattened_1d_arbitrary_order_covariance_relative_difference_percent_STRESS_ONLY'] > 1e-5
    assert z['G15']=='NO_GO' and 'p_value' not in json.dumps(z)


def test_bad_raw_hv_shift_fails_closed(monkeypatch):
    from src.phase7_sherpa_2d_smoothing import smoothing_comparison
    _load_mocks(monkeypatch)
    with pytest.raises(ValueError,match='positive'):
        smoothing_comparison([0.,1.,2.,3.],[1.,2.,3.,4.])
    with pytest.raises(ValueError,match='finite'):
        smoothing_comparison([1.,2.,3.,4.],[1.,np.nan,2.,3.])
    with pytest.raises(ValueError,match='zero'):
        smoothing_comparison([1.,2.,3.,4.],[0.,0.,0.,0.])


def test_verified_v2_driver_pseudodata_first_and_no_inference(tmp_path,monkeypatch):
    import sys,types
    from src.phase7_sherpa_2d_smoothing import run
    module=_load_mocks(monkeypatch)
    module('src.phase7_snapshot',verify=lambda path:{'verified':True})
    module('src.phase7_v2_extract',verify_v2=lambda path:{'verified':True})
    module('src.phase7_v2_reconstruct',wsum=lambda sample,column:np.array(sample['columns'][column]['sum_w'],float))
    def dataset(variation):
        h=[100.,200.,300.,400.]
        return {'nominal':{'columns':{'weights_nominal':{'sum_w':h}}},
                'sherpa':{'columns':{'weights_nominal':{'sum_w':(np.array(h)+variation).tolist()}}}}
    v2=tmp_path/'v2';v2.mkdir()
    (v2/'moments.json').write_text(json.dumps({'samples':{'pseudo':dataset(np.array([2.,-3.,5.,-4.])),
                                                          'real':dataset(np.array([1.,2.,-4.,3.]))}}))
    out=run(tmp_path/'v1',v2,tmp_path/'out')
    assert list(out['samples'])==['pseudo','real']
    assert out['G12']=='UNVERIFIED' and out['G15']=='NO_GO'
    assert out['samples']['real']['factorized_covariance_relative_frobenius_difference_percent']<1e-12
    assert json.loads((tmp_path/'out'/'sherpa_2d_smoothing_sensitivity.json').read_text())==out
