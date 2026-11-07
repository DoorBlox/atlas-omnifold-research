"""Bounded 2x2 Sherpa HV smoothing sensitivity, not an official prescription.

CERN smooth_uncertainty is 1D, with Gaussian width full ordered-bin-center
coordinate range / 10. Any chosen two distinct centers on a single axis
therefore give a 2x2 row-normalized Gaussian kernel with off-diagonal
mixing e^-50/(1+e^-50). Its factorized mass-by-track extension is near
identity for our 2x2 *categories*, but is NOT defined/recommended by ATLAS.
The four-category one-dimensional flattening is arbitrary and prohibited
as inferential input; we only report it as an ordering stress example.
"""
from __future__ import annotations

import argparse
import json
from math import exp
from pathlib import Path

import numpy as np


MIXING = exp(-50.0)/(1.0+exp(-50.0))


def two_level_kernel():
    """Dimensionless two-level Gaussian analogue of official Nsig=10 width."""
    return np.array([[1.-MIXING, MIXING], [MIXING, 1.-MIXING]],dtype=float)


def tensor_kernel():
    """Row-major LL,LH,HL,HH two-axis factorized hypothesis."""
    return np.kron(two_level_kernel(),two_level_kernel())


def smoothing_comparison(nominal, raw_sherpa_shift):
    """Quantify factorized axis smoothing; no model selection or p-values."""
    from src.phase7_twopoint_protocol import count_shift_to_covariance
    from src.phase7_official_helper_audit import smooth_1d_port
    h=np.asarray(nominal,float)
    delta=np.asarray(raw_sherpa_shift,float)
    if h.shape!=(4,) or delta.shape!=(4,) or not np.isfinite(h).all() or not np.isfinite(delta).all() or np.any(h<=0):
        raise ValueError('Expected positive nominal and finite signed four-cell shift')
    original=count_shift_to_covariance(h,delta,'fully_correlated')
    factorized_delta=tensor_kernel()@delta
    factorized=count_shift_to_covariance(h,factorized_delta,'fully_correlated')
    # Four-cell flattened 1D ordered-bin centers are *not* physical, but
    # demonstrate that an arbitrary ordering defines a different smoothing.
    flattened_delta=smooth_1d_port(delta,np.arange(4,dtype=float))
    flattened=count_shift_to_covariance(h,flattened_delta,'fully_correlated')
    base=np.linalg.norm(original)
    if base<=0:
        raise ValueError('Source covariance has zero amplitude')
    return {
        'single_axis_offdiagonal_kernel_mixing':MIXING,
        'max_absolute_factorized_minus_raw_shift':float(np.max(np.abs(factorized_delta-delta))),
        'factorized_covariance_relative_frobenius_difference_percent':float(100*np.linalg.norm(factorized-original)/base),
        'flattened_1d_arbitrary_order_covariance_relative_difference_percent_STRESS_ONLY':float(100*np.linalg.norm(flattened-original)/base),
        'inference_eligible_2d_smoother':False,
        'G12':'NO_UNIQUE_OFFICIAL_2D_SMOOTHING','G15':'NO_GO',
    }


def run(v1:Path,v2:Path,out:Path)->dict:
    from src.phase7_snapshot import verify as verify_v1
    from src.phase7_v2_extract import verify_v2
    from src.phase7_v2_reconstruct import wsum
    verify_v1(v1);verify_v2(v2)
    store=json.loads((Path(v2)/'moments.json').read_text(encoding='utf-8'))
    samples={}
    for kind in ('pseudo','real'):
        s=store['samples'][kind]
        h=wsum(s['nominal'],'weights_nominal')
        sherpa=wsum(s['sherpa'],'weights_nominal')
        samples[kind]=smoothing_comparison(h,sherpa-h)
    output={'status':'2D_SHERPA_GAUSSIAN_PRODUCT_KERNEL_IS_A_HYPOTHESIS_NOT_OFFICIAL',
            'source':'official CERN multifold_util.smooth_uncertainty Nsig=10 is defined on ordered 1D bin centers only',
            'physical_bin_center_limitation':'two categories per axis are threshold-defined; no source-specified finite physical 2D bin centers or bandwidth',
            'scenario':'two-level axis kernel product; alternate flattened 4-vector for non-inferential stress only',
            'samples':samples,'G5':'PROVISIONAL','G8':'UNVERIFIED','G12':'UNVERIFIED','G15':'NO_GO',
            'inference_permission':'NO_GO'}
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    (out/'sherpa_2d_smoothing_sensitivity.json').write_text(json.dumps(output,indent=2,sort_keys=True)+'\n')
    return output


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--v1',type=Path,default=Path('data/derived/phase7-v1'))
    parser.add_argument('--v2',type=Path,default=Path('data/derived/phase7-v2'))
    parser.add_argument('--out',type=Path,default=Path('outputs/sherpa-2d-smoothing'))
    args=parser.parse_args()
    result=run(args.v1,args.v2,args.out)
    print(json.dumps({'status':result['status'],'samples':result['samples'],'G15':result['G15']},indent=2))


if __name__=='__main__':
    main()
