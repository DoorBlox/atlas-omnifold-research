"""Regression for fixed-format Pandas HDF5 and guarded 2x2 projection."""
import pandas as pd
from src.projection import inspect_columns, read_fixed_columns, run


def test_fixed_format_projection(tmp_path):
    df = pd.DataFrame({
        "pT_trackj1": [10., 10., 10., 10., 10., 10., 10., 10., 2.],
        "m_trackj1": [1., 1., 1., 1., 3., 3., 3., 3., 0.],
        "Ntracks_trackj1": [1, 1, 1, 3, 1, 3, 3, 3, 1],
        "weight_mc": [1.] * 9,
        "weights_nominal": [2., 1., 1., 1., 1., 1., 2., 1., 1.],
        "weights_theoryQCD": [2., 1., 1., 1., 1., 1., 2., 1., 1.],
    })
    real = tmp_path / "real.h5"
    pseudo = tmp_path / "pseudo.h5"
    df.to_hdf(real, key="df", format="fixed")
    df.to_hdf(pseudo, key="df", format="fixed")
    assert len(inspect_columns(real)["columns"]) == 6
    assert read_fixed_columns(real, ("weight_mc",))["weight_mc"].shape == (9,)
    out = tmp_path / "outputs"
    result = run(real, pseudo, out)
    assert result["G15_real_data_p_value"] == "BLOCKED"
    assert result["sum_generator_fractions"] == 1.0
    assert (out / "column_inventory.json").exists()
    assert (out / "bin_spec.json").exists()
    assert (out / "cell_support.csv").exists()
