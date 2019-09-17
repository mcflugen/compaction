"""Unit tests for compaction."""
import numpy as np
import pandas
import yaml
from pytest import approx, mark
from six import StringIO

from compaction import compact
from compaction.cli import load_config, run_compaction


def test_to_analytical():
    c = 3.68e-8
    rho_s = 2650.0
    rho_w = 1000.0
    phi_0 = 0.6
    g = 9.81

    dz = np.full(2000, 10.0)
    phi = np.full(len(dz), phi_0)

    phi_numerical = compact(
        dz,
        phi,
        porosity_min=0.0,
        porosity_max=phi_0,
        c=c,
        gravity=g,
        rho_grain=rho_s,
        rho_void=rho_w,
    )

    z = np.cumsum(dz * (1 - phi) / (1 - phi_numerical))
    phi_analytical = np.exp(-c * g * (rho_s - rho_w) * z) / (
        np.exp(-c * g * (rho_s - rho_w) * z) + (1.0 - phi_0) / phi_0
    )

    sup_norm = np.max(np.abs(phi_numerical - phi_analytical) / phi_analytical)

    assert sup_norm < 0.01


def test_spatially_distributed():
    """Test with spatially distributed inputs."""
    dz = np.full((100, 10), 1.0)
    phi = np.full((100, 10), 0.5)
    phi_new = compact(dz, phi, porosity_max=0.5)

    assert phi_new[0] == approx(phi[0])
    assert np.all(phi_new[1:] < phi[1:])
    assert np.all(np.diff(phi_new, axis=0) < 0.0)


@mark.parametrize("size", (10, 100, 1000, 10000))
@mark.benchmark(group="compaction")
def test_grid_size(benchmark, size):
    dz = np.full((size, 100), 1.0)
    phi = np.full((size, 100), 0.5)
    phi_new = compact(dz, phi, porosity_max=0.5)

    phi_new = benchmark(compact, dz, phi, porosity_max=0.5)

    assert phi_new[0] == approx(phi[0])
    assert np.all(phi_new[1:] < phi[1:])
    assert np.all(np.diff(phi_new, axis=0) < 0.0)


@mark.parametrize("size", (10, 100, 1000, 10000))
@mark.benchmark(group="compaction-with-dz")
def test_grid_size_with_dz(benchmark, size):
    dz = np.full((size, 100), 1.0)
    phi = np.full((size, 100), 0.5)
    phi_new = compact(dz, phi, porosity_max=0.5)

    phi_new, dz_new = benchmark(compact, dz, phi, porosity_max=0.5, return_dz=True)

    assert phi_new[0] == approx(phi[0])
    assert np.all(phi_new[1:] < phi[1:])
    assert np.all(np.diff(phi_new, axis=0) < 0.0)

    assert dz_new[0] == approx(dz[0])
    assert np.all(dz_new[1:] < dz[1:])
    assert np.all(np.diff(dz_new, axis=0) < 0.0)


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
