"""Deterministic checks of additional descriptive association algebra, not G15."""
import csv
from pathlib import Path
import pytest
from src.joint_association_audit import analyze_csv,cells_from_coordinates,compare,coordinates

FROZEN={
 "real":{
  "measurement":(.4287152163666504,.07496344481873442,.13275274626019576,.3635685925544194),
  "reference":(.43416258768444055,.06583598813397021,.141995627265506,.35800579691608325),
  "D":-.00016851611111462494, "L":-.05973347757837999,"path":-.05535637180734421},
 "pseudo":{
  "measurement":(.4366239490795071,.07253511268549338,.12009470690534266,.3707462313296568),
  "reference":(.4489994511773743,.0831352714007221,.10968280507866973,.35818247234323386),
  "D":.0014603767959295855, "L":.0522361447975217,"path":.012918789940997044},
}
def four(items):return dict(zip(("LL","LH","HL","HH"),items))

@pytest.mark.parametrize("sample",("real","pseudo"))
def test_frozen_coordinate_and_path(sample):
    item=FROZEN[sample]
    result=compare(four(item["measurement"]),four(item["reference"]))
    delta=result["unfolded_minus_reference"]
    path=result["log_odds_counterfactual"]
    assert delta["indicator_covariance_D"]==pytest.approx(item["D"],abs=1e-14)
    assert delta["log_odds_L"]==pytest.approx(item["L"],abs=1e-14)
    assert path["marginal_change_at_reference_D"]==pytest.approx(item["path"],abs=1e-14)
    assert path["D_change_at_measurement_marginals"]+path["marginal_change_at_reference_D"]==pytest.approx(delta["log_odds_L"],abs=1e-14)

def test_reconstruction_exact():
    for pair in FROZEN.values():
        for kind in ("measurement","reference"):
            p=four(pair[kind]); c=coordinates(p)
            q=cells_from_coordinates(c["mass_low"],c["multiplicity_low"],c["indicator_covariance_D"])
            for cell in p:assert q[cell]==pytest.approx(p[cell],abs=1e-14)

def test_invalid_shapes_fail_closed():
    with pytest.raises(ValueError,match="normalized"):coordinates(four((.2,.2,.2,.2)))
    with pytest.raises(ValueError,match="positive"):coordinates(four((.5,0,.25,.25)))
    with pytest.raises(ValueError,match="Expected"):coordinates({"LL":.5,"LH":.5})
    with pytest.raises(ValueError,match="positive"):cells_from_coordinates(.5,.5,.30)

def test_duplicate_rows_rejected(tmp_path):
    path=tmp_path/"bad.csv"
    path.write_text("sample,cell,measurement_fraction,reference_fraction\nreal,LL,.5,.5\nreal,LL,.5,.5\n")
    with pytest.raises(ValueError,match="Duplicate"):analyze_csv(path)

def test_frozen_csv_roundtrip(tmp_path):
    path=tmp_path/"cells.csv"
    with path.open("w",newline="",encoding="utf-8") as stream:
        w=csv.DictWriter(stream,fieldnames=["sample","cell","measurement_fraction","reference_fraction"])
        w.writeheader()
        for sample,pair in FROZEN.items():
            for cell,p,q in zip(("LL","LH","HL","HH"),pair["measurement"],pair["reference"]):
                w.writerow({"sample":sample,"cell":cell,"measurement_fraction":p,"reference_fraction":q})
    res=analyze_csv(path)
    assert len(res)==2
    assert res["real"]["unfolded_minus_reference"]["indicator_covariance_D"]==pytest.approx(FROZEN["real"]["D"],abs=1e-14)
    assert "p_value" not in str(res)

def test_repository_pinned_csv_if_present():
    path=Path(__file__).resolve().parents[1]/"results/kti-nov18/tables/joint_cells.csv"
    if not path.exists():pytest.skip("Frozen repository CSV unavailable in standalone test")
    res=analyze_csv(path)
    for sample in FROZEN:
        assert res[sample]["unfolded_minus_reference"]["indicator_covariance_D"]==pytest.approx(FROZEN[sample]["D"],abs=1e-14)
        assert res[sample]["unfolded_minus_reference"]["log_odds_L"]==pytest.approx(FROZEN[sample]["L"],abs=1e-14)
