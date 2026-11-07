"""Audit official pseudodata notebook's 1D *family inclusion*, not a 2D ATLAS prescription."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping
import numpy as np
from src.phase7_model_sensitivity import load_components, read_shape, quadratic_description, verify_bin_spec

THEORY = ('theoryPSjet','theoryPSsoft','theoryMPI','theoryPSscale','theoryAlphaS','theoryQCD','theoryPDF')
PSEUDO_1D_FAMILIES = (
    'finite_evaluation_mc','mc_training_bootstrap','data_bootstrap','nn_ensemble',
    *THEORY, 'dd_unfolding','sherpa_hidden_variable','topBackground','nonDY'
)


def pseudo_1d_reference_families(components: Mapping[str,np.ndarray]) -> dict[str,np.ndarray]:
    missing = set(PSEUDO_1D_FAMILIES) - set(components)
    if missing:
        raise ValueError(f'Missing families used by official 1D example: {sorted(missing)}')
    return {key:components[key] for key in PSEUDO_1D_FAMILIES}


def compare_family_projection(components: Mapping[str,np.ndarray], residual: np.ndarray) -> dict:
    full = quadratic_description(components, residual)
    sub = pseudo_1d_reference_families(components)
    restricted = quadratic_description(sub, residual)
    trace_full = float(np.trace(sum(components.values())))
    trace_sub = float(np.trace(sum(sub.values())))
    if trace_full <= 0 or trace_sub <= 0:
        raise ValueError('Non-positive source trace')
    full['source_trace_share'] = 1.0
    restricted['source_trace_share'] = trace_sub / trace_full
    return {
        'source_count_full_2d': len(components),
        'source_count_pseudo_1d_family_subset': len(sub),
        'full_2d': full, 'family_subset': restricted,
        'G5': 'INCOMPLETE, family list only; NOT an ATLAS 2D covariance replication',
        'G12': 'FAMILY_INCLUSION_SENSITIVITY_ONLY', 'G15':'NO-GO'
    }


def run(real_dir:Path, pseudo_dir:Path, out:Path)->dict:
    real_dir,pseudo_dir,out=Path(real_dir),Path(pseudo_dir),Path(out)
    out.mkdir(parents=True,exist_ok=True)
    spec = verify_bin_spec(real_dir,pseudo_dir)
    observations = {
        'real': (load_components(real_dir/'source_covariances.npz'),
                 read_shape(real_dir/'real_2x2_cells.csv','unfolded_fraction') -
                 read_shape(real_dir/'real_2x2_cells.csv','generator_fraction')),
        'pseudodata': (load_components(pseudo_dir/'pseudo_source_covariances.npz'),
                       read_shape(pseudo_dir/'pseudo_closure_cells.csv','pseudo_unfolded_fraction') -
                       read_shape(pseudo_dir/'pseudo_closure_cells.csv','independent_target_truth_fraction')),
    }
    data = {key:compare_family_projection(comp,res) for key,(comp,res) in observations.items()}
    payload = {
        'status':'EXECUTED_REFERENCE_FAMILY_AUDIT_NOT_ATLAS_2D_PRESCRIPTION',
        'source':'ATLAS 2_pseudo_results.ipynb cell 26 (official public example)',
        'frozen_generator_bins':spec,
        'family_names_matching_1d_pseudo_example':list(PSEUDO_1D_FAMILIES),
        'critical_non_equivalences':[
            'Official example 1D histograms are not normalized 2x2 shapes or rank-three contrasts.',
            'Official Sherpa hidden-variable term applies smooth_uncertainty to 1D ordered bin centers.',
            'There is no source-verified 2D replacement for that 1D smoothing.',
            'Official 1D DD count shift is (counts_dd-target_dd)*(nom/target_dd); current 2D implementation normalizes a shifted shape.',
            'Official pseudo 1D chi-square example excludes event/track/muon/luminosity families which our full 2D prototype includes.',
            'Official example conditionally decorrelates DD/HV after a low initial p value. This data-dependent switch must NOT be used as a 2D inference selection rule.',
            'The exact body of multifold_util.fill_cov_matrix was not independently inspected in this audit.'
        ],
        'runs':{'real_covariance':42324639484,'pseudodata_closure':42327464929},
        'comparisons':data,'G5':'PROVISIONAL','G12':'STRESS_TEST_ONLY','G15':'NO-GO',
        'inference_permission':'NO-GO',
    }
    (out/'reference_1d_family_audit.json').write_text(json.dumps(payload,indent=2))
    print(json.dumps(payload,indent=2))
    return payload


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--real-dir',type=Path,required=True)
    ap.add_argument('--pseudo-dir',type=Path,required=True)
    ap.add_argument('--out',type=Path,default=Path('outputs'))
    args=ap.parse_args()
    run(args.real_dir,args.pseudo_dir,args.out)


if __name__=='__main__':
    main()
