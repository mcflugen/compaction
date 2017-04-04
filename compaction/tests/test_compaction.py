"""Unit tests for compaction."""
import numpy as np
from numpy.testing import assert_array_less, assert_array_equal
from nose.tools import assert_almost_equal

from compaction import compact


def test_decreasing_porosity():
    """Test porosity decreases with depth."""
    dz = np.full(100, 1.)
    phi = np.full(100, .5)
    phi_new = compact(dz, phi, porosity_max=.5)

    assert_almost_equal(phi_new[0], phi[0])
    assert_array_less(phi_new[1:], phi[1:])
    assert_array_less(np.diff(phi_new), 0.)


def test_equilibrium_compaction():
    """Test steady-state compaction."""
    dz_0 = np.full(100, 1.)
    phi_0 = np.full(100, .5)

    phi_1 = compact(dz_0, phi_0, porosity_max=.5)
    dz_1 = dz_0 * (1 - phi_0) / (1 - phi_1)

    phi_2 = compact(dz_1, phi_1, porosity_max=.5)

    assert_array_equal(phi_2, phi_1)


def test_no_decompaction():
    """Test removing sediment does not cause decompaction."""
    dz_0 = np.full(100, 1.)
    phi_0 = np.full(100, .5)

    phi_1 = compact(dz_0, phi_0, porosity_max=.5)
    dz_1 = dz_0 * (1 - phi_0) / (1 - phi_1)
    dz_1[0] /= 2.

    phi_2 = compact(dz_1, phi_1, porosity_max=.5)
    assert_array_equal(phi_2, phi_1)


def test_increasing_load():
    """Test adding sediment increases compaction."""
    dz_0 = np.full(100, 1.)
    phi_0 = np.full(100, .5)

    phi_1 = compact(dz_0, phi_0, porosity_max=.5)
    dz_1 = dz_0 * (1 - phi_0) / (1 - phi_1)
    dz_1[0] *= 2.

    phi_2 = compact(dz_1, phi_1, porosity_max=.5)
    assert_array_less(phi_2[1:], phi_1[1:])


def test_zero_compaction():
    """Test compaction coefficient of zero."""
    dz_0 = np.full(100, 1.)
    phi_0 = np.full(100, .5)

    phi_1 = compact(dz_0, phi_0, porosity_max=.5, c=0.)
    assert_array_equal(phi_1, phi_0)


def test_increasing_compactability():
    """Test large compaction coefficient leads to more compaction."""
    dz_0 = np.full(100, 1.)
    phi_0 = np.full(100, .5)

    phi_1 = compact(dz_0, phi_0, porosity_max=.5, c=1e-6)
    phi_2 = compact(dz_0, phi_0, porosity_max=.5, c=1e-3)
    assert_array_less(phi_2[1:], phi_1[1:])


def test_void_is_air():
    """Test empty void space."""
    dz_0 = np.full(100, 1.)
    phi_0 = np.full(100, .5)

    phi_1 = compact(dz_0, phi_0, porosity_max=.5, rho_void=0.)
    phi_2 = compact(dz_0, phi_0, porosity_max=.5, rho_void=1000.)
    assert_array_less(phi_1[1:], phi_2[1:])
