"""Unit tests for compaction."""
import tempfile
import subprocess

import pandas
import numpy as np
from numpy.testing import (assert_array_less, assert_array_equal,
                           assert_array_almost_equal)
from nose.tools import assert_almost_equal, assert_dict_equal, assert_is_none
import yaml
from six import StringIO

from compaction import compact, load_config
from compaction.compaction import run_compaction


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


def test_load_config_defaults():
    """Test load_config without file name."""
    config = load_config()
    defaults = {
        'c': 5e-8,
        'porosity_min': 0.,
        'porosity_max': 1.,
        'rho_grain': 2650.,
        'rho_void': 1000.,
    }
    assert_dict_equal(config, defaults)


def test_load_config_from_file():
    """Test config vars from a file."""
    file_like = StringIO()
    yaml.dump(dict(c=3.14), file_like)
    file_like.seek(0)
    config = load_config(file_like)

    expected = {
        'c': 3.14,
        'porosity_min': 0.,
        'porosity_max': 1.,
        'rho_grain': 2650.,
        'rho_void': 1000.,
    }
    assert_dict_equal(config, expected)


def test_run():
    """Test running compaction with file-like objects."""
    dz_0 = np.full(100, 1.)
    phi_0 = np.full(100, .5)
    phi_1 = compact(dz_0, phi_0, porosity_max=.5)

    input = StringIO()
    output = StringIO()

    df = pandas.DataFrame.from_items([('dz', dz_0), ('porosity', phi_0)])
    df.to_csv(input, index=False, header=False)

    input.seek(0)
    run_compaction(input=input, output=output, porosity_max=.5)
    output.seek(0)

    data = pandas.read_csv(output, names=('dz', 'porosity'), dtype=float)

    assert_array_almost_equal(data.porosity, phi_1)


def test_cli():
    """Test the compaction command-line interface."""
    dz_0 = np.full(100, 1.)
    phi_0 = np.full(100, .5)
    phi_1 = compact(dz_0, phi_0, porosity_max=.5)

    input = StringIO()
    df = pandas.DataFrame.from_items([('dz', dz_0), ('porosity', phi_0)])
    df.to_csv(input, index=False, header=False)

    with tempfile.NamedTemporaryFile(mode='w+') as fp:
        yaml.dump(dict(porosity_max=.5), fp)
        proc = subprocess.Popen(['compact', '-', '-', '--config=%s' % fp.name],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE)
        (output, err) = proc.communicate(input=str.encode(input.getvalue()))
        data = pandas.read_csv(StringIO(output), names=('dz', 'porosity'))

    assert_array_almost_equal(data.porosity, phi_1)
