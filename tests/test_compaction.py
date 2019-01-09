"""Unit tests for compaction."""
import os
import shutil
import subprocess
import tempfile

import numpy as np
import pandas
import yaml
from pytest import approx
from six import StringIO

from compaction import compact, load_config
from compaction.compaction import run_compaction


def test_decreasing_porosity():
    """Test porosity decreases with depth."""
    dz = np.full(100, 1.0)
    phi = np.full(100, 0.5)
    phi_new = compact(dz, phi, porosity_max=0.5)

    assert phi_new[0] == approx(phi[0])
    assert np.all(phi_new[1:] < phi[1:])
    assert np.all(np.diff(phi_new) < 0.0)


def test_equilibrium_compaction():
    """Test steady-state compaction."""
    dz_0 = np.full(100, 1.0)
    phi_0 = np.full(100, 0.5)

    phi_1 = compact(dz_0, phi_0, porosity_max=0.5)
    dz_1 = dz_0 * (1 - phi_0) / (1 - phi_1)

    phi_2 = compact(dz_1, phi_1, porosity_max=0.5)

    assert np.all(phi_2 == approx(phi_1))


def test_no_decompaction():
    """Test removing sediment does not cause decompaction."""
    dz_0 = np.full(100, 1.0)
    phi_0 = np.full(100, 0.5)

    phi_1 = compact(dz_0, phi_0, porosity_max=0.5)
    dz_1 = dz_0 * (1 - phi_0) / (1 - phi_1)
    dz_1[0] /= 2.0

    phi_2 = compact(dz_1, phi_1, porosity_max=0.5)
    assert np.all(phi_2 == approx(phi_1))


def test_increasing_load():
    """Test adding sediment increases compaction."""
    dz_0 = np.full(100, 1.0)
    phi_0 = np.full(100, 0.5)

    phi_1 = compact(dz_0, phi_0, porosity_max=0.5)
    dz_1 = dz_0 * (1 - phi_0) / (1 - phi_1)
    dz_1[0] *= 2.0

    phi_2 = compact(dz_1, phi_1, porosity_max=0.5)
    assert np.all(phi_2[1:] < phi_1[1:])


def test_zero_compaction():
    """Test compaction coefficient of zero."""
    dz_0 = np.full(100, 1.0)
    phi_0 = np.full(100, 0.5)

    phi_1 = compact(dz_0, phi_0, porosity_max=0.5, c=0.0)
    assert np.all(phi_1 == approx(phi_0))


def test_increasing_compactability():
    """Test large compaction coefficient leads to more compaction."""
    dz_0 = np.full(100, 1.0)
    phi_0 = np.full(100, 0.5)

    phi_1 = compact(dz_0, phi_0, porosity_max=0.5, c=1e-6)
    phi_2 = compact(dz_0, phi_0, porosity_max=0.5, c=1e-3)
    assert np.all(phi_2[1:] < phi_1[1:])


def test_void_is_air():
    """Test empty void space."""
    dz_0 = np.full(100, 1.0)
    phi_0 = np.full(100, 0.5)

    phi_1 = compact(dz_0, phi_0, porosity_max=0.5, rho_void=0.0)
    phi_2 = compact(dz_0, phi_0, porosity_max=0.5, rho_void=1000.0)
    assert np.all(phi_1[1:] < phi_2[1:])


def test_load_config_defaults():
    """Test load_config without file name."""
    config = load_config()
    defaults = {
        "c": 5e-8,
        "porosity_min": 0.0,
        "porosity_max": 1.0,
        "rho_grain": 2650.0,
        "rho_void": 1000.0,
    }
    assert config == defaults


def test_load_config_from_file():
    """Test config vars from a file."""
    file_like = StringIO()
    yaml.dump(dict(c=3.14), file_like)
    file_like.seek(0)
    config = load_config(file_like)

    expected = {
        "c": 3.14,
        "porosity_min": 0.0,
        "porosity_max": 1.0,
        "rho_grain": 2650.0,
        "rho_void": 1000.0,
    }
    assert config == expected


def test_run():
    """Test running compaction with file-like objects."""
    dz_0 = np.full(100, 1.0)
    phi_0 = np.full(100, 0.5)
    phi_1 = compact(dz_0, phi_0, porosity_max=0.5)

    input = StringIO()
    output = StringIO()

    df = pandas.DataFrame.from_items([("dz", dz_0), ("porosity", phi_0)])
    df.to_csv(input, index=False, header=False)

    input.seek(0)
    run_compaction(input=input, output=output, porosity_max=0.5)
    output.seek(0)

    data = pandas.read_csv(output, names=("dz", "porosity"), dtype=float)

    assert np.all(data.porosity.values == approx(phi_1))


def test_cli():
    """Test the compaction command-line interface."""
    dz_0 = np.full(100, 1.0)
    phi_0 = np.full(100, 0.5)
    phi_1 = compact(dz_0, phi_0, porosity_max=0.5)

    tmpdir = tempfile.mkdtemp()
    os.chdir(tmpdir)

    df = pandas.DataFrame.from_items([("dz", dz_0), ("porosity", phi_0)])
    df.to_csv("porosity_in.csv", index=False, header=False)

    with open("config.yaml", "w") as fp:
        yaml.dump(dict(porosity_max=0.5), fp)

    subprocess.check_call(
        ["compact", "porosity_in.csv", "porosity_out.csv", "--config=config.yaml"]
    )
    data = pandas.read_csv("porosity_out.csv", names=("dz", "porosity"))

    shutil.rmtree(tmpdir)

    assert np.all(data.porosity.values == approx(phi_1))
