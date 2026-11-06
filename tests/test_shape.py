import numpy as np
import pytest
from src.shape import weighted_median, multiplicity_threshold, four_cells, fractions, neff, contrast_diagnostics


def test_weighted_thresholds_are_generator_only_functions():
    assert weighted_median([1, 2, 3], [1, 5, 1]) == 2.0
    assert multiplicity_threshold([1, 2, 2, 3], [1, 1, 4, 1]) == 2


def test_four_cell_order_and_normalisation():
    cells = four_cells([1, 1, 3, 3], [1, 3, 1, 3], 2, 2)
    np.testing.assert_array_equal(cells, [0, 1, 2, 3])
    np.testing.assert_allclose(fractions(cells, [1, 2, 3, 4]), [0.1, 0.2, 0.3, 0.4])
    np.testing.assert_allclose(neff(cells, [1, 2, 3, 4]), [1, 1, 1, 1])


def test_normalization_independent_of_global_weight_scale():
    cells = np.array([0, 1, 1, 2, 3])
    weights = np.array([4., 3., 3., 8., 2.])
    np.testing.assert_allclose(fractions(cells, weights), fractions(cells, weights * 25))


def test_invalid_median_rejected():
    with pytest.raises(ValueError):
        weighted_median([1, 2], [1, -2])


def test_covariance_normalization_mode():
    B = np.array([[2., 0., 0.], [0., 2., 0.], [0., 0., 2.], [-2., -2., -2.]])
    C = B @ B.T
    d = contrast_diagnostics(C)
    assert d["rank"] == 3
    assert d["positive_definite"]
