"""One-pass Phase 7 v2 signed-bin sufficient-statistics tests (synthetic only)."""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.phase7_v2_extract import extract_one, build, verify_v2, frozen_thresholds, extract_mode


def sample_frame(variation=1.0):
    return pd.DataFrame({
        "pT_trackj1": [10.,10.,10.,10.,10.,10.,10.,10.,2.],
        "m_trackj1": [1.,1.,1.,1.,3.,3.,3.,3.,1.],
        "Ntracks_trackj1": [1,1,3,3,1,1,3,3,1],
        "weight_mc": [1.,2.,3.,4.,1.,2.,3.,4.,999.],
        "weights_nominal": [1.,2.,3.,4.,1.,2.,3.,4.,999.],
        "weights_dd": np.array([1.,2.,3.,4.,1.,2.,3.,4.,999.]) * variation,
        "target_dd": [1.,2.,3.,4.,1.,2.,3.,4.,999.],
        "weights_theoryQCD": np.array([1.,2.,3.,4.,1.,2.,3.,4.,999.])*1.01,
        "weights_bootstrap_data_0": [1.,2.,3.,4.,1.,2.,3.,4.,999.],
        "weights_bootstrap_data_1": [2.,2.,3.,4.,1.,2.,3.,4.,999.],
    })


def write_tree(root):
    root=Path(root)
    for kind in ("data","pseudodata"):
        d=root/"files"/kind
        d.mkdir(parents=True)
        frame=sample_frame(variation=1.1 if kind=="data" else .9)
        frame.to_hdf(d/"multifold.h5",key="df",format="fixed")
        for alt in ("multifold_sherpa.h5","multifold_nonDY.h5"):
            frame.to_hdf(d/alt,key="df",format="fixed")


def test_extract_signed_sums_and_shared_event_products(tmp_path):
    path=tmp_path/"synthetic.h5"
    sample_frame().to_hdf(path,key="df",format="fixed")
    result=extract_one(path,{"mass_star":2., "tracks_star":2},chunk_size=3)
    assert result["rows_selected"]==8 and result["rows_total"]==9
    assert result["counts"]==[2,2,2,2]
    mc=result["columns"]["weight_mc"]
    assert mc["sum_w"]==[3.,7.,3.,7.]
    assert mc["sum_w2"]==[5.,25.,5.,25.]
    assert mc["sum_w_times_mc"]==mc["sum_w2"]
    assert mc["sum_w_times_nominal"]==mc["sum_w2"]
    assert result["columns"]["weights_bootstrap_data_1"]["sum_w"]==[4.,7.,3.,7.]
    q=np.array(mc["sum_w"])
    np.testing.assert_allclose(q/q.sum(),[.15,.35,.15,.35])
    assert sum(mc["sum_w"])==20
    assert set(result["columns"]) >= {"weights_dd","target_dd","weight_mc","weights_nominal"}


def test_chunk_size_invariance(tmp_path):
    path=tmp_path/"synthetic.h5"
    sample_frame().to_hdf(path,key="df",format="fixed")
    small=extract_one(path,{"mass_star":2.,"tracks_star":2},chunk_size=2)
    large=extract_one(path,{"mass_star":2.,"tracks_star":2},chunk_size=512)
    assert small["counts"]==large["counts"]
    for name in small["columns"]:
        for key in ("sum_w","sum_w2","sum_w_times_mc","sum_w_times_nominal"):
            np.testing.assert_allclose(small["columns"][name][key],large["columns"][name][key],rtol=1e-12)


def test_nonfinite_selected_event_fails_closed(tmp_path):
    df=sample_frame()
    df.loc[0,"weights_nominal"]=np.nan
    path=tmp_path/"bad.h5"
    df.to_hdf(path,key="df",format="fixed")
    with pytest.raises(ValueError,match="[Nn]onfinite"):
        extract_one(path,{"mass_star":2.,"tracks_star":2})


def test_missing_weight_or_observable_fails(tmp_path):
    path=tmp_path/"missing.h5"
    sample_frame().drop(columns=["weight_mc"]).to_hdf(path,key="df",format="fixed")
    with pytest.raises((KeyError,ValueError),match="weight_mc"):
        extract_one(path,{"mass_star":2.,"tracks_star":2})


def test_build_verify_and_refuse_overwrite(tmp_path):
    root=tmp_path/"source"
    write_tree(root)
    dest=tmp_path/"derived"/"v2"
    result=build(root,dest,{"mass_star":2.,"tracks_star":2},archive_md5="synthetic-only",enforce_v1=False)
    assert result["status"]=="DERIVED_SIGNED_MOMENTS_NOT_INFERENCE"
    assert result["G15"]=="NO_GO"
    assert result["samples"]["real"]["nominal"]["rows_selected"]==8
    assert result["samples"]["pseudo"]["nominal"]["rows_selected"]==8
    assert verify_v2(dest)["verified"]
    assert len(result["samples"]["real"]["nominal"]["columns"])>=6
    assert not any(p.suffix in (".h5",".hdf5",".zip") for p in dest.rglob("*"))
    with pytest.raises(ValueError,match="exists|overwrite|nonempty"):
        build(root,dest,{"mass_star":2.,"tracks_star":2},archive_md5="synthetic-only",enforce_v1=False)


def test_tampering_detected(tmp_path):
    root=tmp_path/"source"
    write_tree(root)
    dest=tmp_path/"out"
    build(root,dest,{"mass_star":2.,"tracks_star":2},archive_md5="synthetic-only",enforce_v1=False)
    path=dest/"moments.json"
    path.write_text(path.read_text()+" ")
    with pytest.raises(ValueError,match="checksum"):
        verify_v2(dest)


def test_frozen_thresholds_from_verified_v1():
    snapshot=Path(__file__).resolve().parents[1]/"data/derived/phase7-v1"
    thresholds=frozen_thresholds(snapshot)
    assert thresholds["mass_star"]==10.594606399536133
    assert thresholds["tracks_star"]==11
    assert thresholds["selection"]=="pT_trackj1 > 5 GeV"


def test_field_mapping_and_identity_guards(tmp_path):
    root=tmp_path/"source"
    write_tree(root)
    dest=tmp_path/"out"
    build(root,dest,{"mass_star":2.,"tracks_star":2},archive_md5="synthetic-only",enforce_v1=False)
    assert extract_mode("files/data/multifold_nonDY.h5")==("real","nonDY")
    assert extract_mode("files/pseudodata/multifold_sherpa.h5")==("pseudo","sherpa")
    with pytest.raises(ValueError,match="Unexpected"):
        extract_mode("files/pseudodata/target.h5")
    proof=dest/"provenance.json"
    doc=json.loads(proof.read_text())
    doc["scientific_gate"]="G15_PASS"
    proof.write_text(json.dumps(doc))
    with pytest.raises(ValueError,match="Invalid version"):
        verify_v2(dest)


def test_extraction_requires_all_four_bins_and_positive_chunks(tmp_path):
    path=tmp_path/"synthetic.h5"
    sample_frame().to_hdf(path,key="df",format="fixed")
    with pytest.raises(ValueError,match="chunk_size"):
        extract_one(path,{"mass_star":2.,"tracks_star":2},chunk_size=0)
    with pytest.raises(ValueError,match="empty 2x2"):
        extract_one(path,{"mass_star":100.,"tracks_star":100},chunk_size=2)
    with pytest.raises(ValueError,match="Invalid frozen"):
        extract_one(path,{"mass_star":float("nan"),"tracks_star":2})


def test_independent_nominal_and_generator_second_moments(tmp_path):
    df=sample_frame()
    df["weights_nominal"]=2*df["weight_mc"]
    path=tmp_path/"scaled.h5"
    df.to_hdf(path,key="df",format="fixed")
    result=extract_one(path,{"mass_star":2.,"tracks_star":2})
    for k in range(4):
        mc=result["columns"]["weight_mc"]
        nom=result["columns"]["weights_nominal"]
        assert nom["sum_w"][k]==2*mc["sum_w"][k]
        assert nom["sum_w2"][k]==4*mc["sum_w2"][k]
        assert nom["sum_w_times_mc"][k]==2*mc["sum_w2"][k]
        assert mc["sum_w_times_nominal"][k]==2*mc["sum_w2"][k]


def test_bad_group_and_no_selected_rows_fail_closed(tmp_path):
    import h5py
    path=tmp_path/"empty.h5"
    with h5py.File(path,"w") as f:
        f.create_dataset("not_df",data=[1,2])
    with pytest.raises(KeyError,match="df"):
        extract_one(path,{"mass_star":2.,"tracks_star":2})
    df=sample_frame()
    df["pT_trackj1"]=2.
    path=tmp_path/"noselection.h5"
    df.to_hdf(path,key="df",format="fixed")
    with pytest.raises(ValueError,match="empty 2x2"):
        extract_one(path,{"mass_star":2.,"tracks_star":2})


def test_official_mode_rejects_unfrozen_source(tmp_path):
    root=tmp_path/"source"
    write_tree(root)
    snapshot=Path(__file__).resolve().parents[1]/"data/derived/phase7-v1"
    with pytest.raises(ValueError,match="MD5 or immutable"):
        build(root,tmp_path/"out",{"mass_star":2.,"tracks_star":2},
              archive_md5="synthetic-only",enforce_v1=True,snapshot=snapshot)


def test_fractions_match_locked_reference_or_fail(tmp_path,monkeypatch):
    import src.phase7_v2_extract as mod
    root=tmp_path/"source"
    write_tree(root)
    groups={k:{} for k in ("real","pseudo")}
    for kind in groups:
        folder=root/"files"/("data" if kind=="real" else "pseudodata")
        result=extract_one(folder/"multifold.h5",{"mass_star":2.,"tracks_star":2})
        result["rows_selected"]=417401  # exercise provenance guard on synthetic weights
        groups[kind]["nominal"]=result
    def fake_read(path,col):
        kind="real" if "real" in Path(path).parts else "pseudo"
        name="weights_nominal" if col in ("unfolded_fraction","pseudo_unfolded_fraction") else "weight_mc"
        w=np.array(groups[kind]["nominal"]["columns"][name]["sum_w"])
        return w/w.sum()
    monkeypatch.setattr(mod,"_read_csv",fake_read)
    proof=mod._check_against_v1(groups,tmp_path)
    assert proof["real"]["fraction_check"]=="PASS"
    assert proof["pseudo"]["max_abs_error"]==0
    groups["real"]["nominal"]["rows_selected"]=8
    with pytest.raises(ValueError,match="rows"):
        mod._check_against_v1(groups,tmp_path)


def test_verified_content_validation_even_with_matching_hash(tmp_path):
    import hashlib
    root=tmp_path/"source"
    write_tree(root)
    dest=tmp_path/"out"
    build(root,dest,{"mass_star":2.,"tracks_star":2},archive_md5="synthetic-only",enforce_v1=False)
    mom=dest/"moments.json"
    data=json.loads(mom.read_text())
    data["samples"]["real"]["nominal"]["counts"]=[0,0,0,0]
    mom.write_text(json.dumps(data))
    proof=dest/"provenance.json"
    p=json.loads(proof.read_text())
    p["moments_sha256"]=hashlib.sha256(mom.read_bytes()).hexdigest()
    proof.write_text(json.dumps(p))
    with pytest.raises(ValueError,match="row-count"):
        verify_v2(dest)
