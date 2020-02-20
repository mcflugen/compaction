"""Unit tests for compaction landlab component."""
import numpy as np  # type: ignore
from landlab import RasterModelGrid  # type: ignore
from numpy.testing import assert_array_almost_equal  # type: ignore
from pytest import approx, fixture, mark, raises  # type: ignore

import compaction
from compaction.landlab import Compact


@fixture()
def grid():
    return RasterModelGrid((3, 5))


def test_matches_module(grid):
    dz = np.full((100, 3), 1.0)
    phi = np.full((100, 3), 0.5)
    phi_expected = compaction.compact(dz, phi, porosity_max=0.5)

    for layer in range(100):
        grid.event_layers.add(1.0, porosity=0.5)
    compact = Compact(grid, porosity_min=0.0, porosity_max=0.5)
    compact.calculate()

    assert_array_almost_equal(grid.event_layers["porosity"][-1::-1, :], phi_expected)


def test_init_without_layers_added(grid):
    compact = Compact(grid)
    compact.run_one_step()
    assert grid.event_layers.number_of_layers == 0
    # assert grid.event_layers.dz == approx(0.0)


@mark.parametrize("size", (10, 100, 1000, 10000))
@mark.benchmark(group="landlab")
def test_grid_size(benchmark, size):
    grid = RasterModelGrid((3, 101))
    for layer in range(size):
        grid.event_layers.add(1.0, porosity=0.5)

    compact = Compact(grid, porosity_min=0.0, porosity_max=0.5)
    benchmark(compact.calculate)

    assert np.all(grid.event_layers["porosity"][:-1] < 0.5)
    assert grid.event_layers["porosity"][-1] == approx(0.5)

    assert np.all(grid.event_layers.dz[-1] == approx(1.0))
    assert np.all(grid.event_layers.dz[:-1] < 1.0)


def test_init_with_layers_added(grid):
    for layer in range(5):
        grid.event_layers.add(100.0, porosity=0.7)
    compact = Compact(grid, porosity_min=0.1, porosity_max=0.7)
    compact.run_one_step()

    assert np.all(grid.event_layers["porosity"][:-1] < 0.7)
    assert grid.event_layers["porosity"][-1] == approx(0.7)

    assert np.all(grid.event_layers.dz[-1] == approx(100.0))
    assert np.all(grid.event_layers.dz[:-1] < 100.0)


def test_layers_compact_evenly(grid):
    for layer in range(1):
        grid.event_layers.add(100.0, porosity=0.7)
    compact = Compact(grid, porosity_min=0.1, porosity_max=0.7)
    compact.run_one_step()

    assert grid.event_layers["porosity"].ptp(axis=1) == approx(0.0)


@mark.parametrize(
    "param,value",
    [
        ("c", -1),
        ("rho_grain", -1),
        ("rho_grain", 0.0),
        ("porosity_min", -1e-6),
        ("porosity_min", 1 + 1e-6),
        ("porosity_max", -1e-6),
        ("porosity_max", 1 + 1e-6),
        ("rho_void", -1),
        ("rho_void", 0.0),
        ("gravity", 0.0),
        ("gravity", -1.0),
    ],
)
def test_init_with_bad_param(grid, param, value):
    params = {param: value}
    with raises(ValueError):
        Compact(grid, **params)


@mark.parametrize(
    "property,value",
    [
        ("c", 0.5),
        ("rho_grain", 3300.0),
        ("excess_pressure", 1.0),
        ("porosity_min", 0.1),
        ("porosity_max", 0.8),
        ("rho_void", 1030.0),
        ("gravity", 3.711),
    ],
)
def test_property_getter_setter(grid, property, value):
    compact = Compact(grid, **{property: value})
    assert getattr(compact, property) == approx(value)
    assert dict(compact.params)[property] == approx(value)

    compact = Compact(grid)
    setattr(compact, property, value)
    assert getattr(compact, property) == approx(value)
    assert dict(compact.params)[property] == approx(value)
