"""Unit tests for compaction landlab component."""
import os
import shutil
import subprocess
import tempfile

import numpy as np
import pandas
import yaml
from pytest import approx, fixture, mark, raises
from six import StringIO

from compaction.landlab import Compact
from landlab import RasterModelGrid


@fixture()
def grid():
    return RasterModelGrid((3, 5))


def test_init_without_layers_added(grid):
    compact = Compact(grid)
    compact.run_one_step()

    assert grid.event_layers.dz == approx(0.0)


def test_init_with_layers_added(grid):
    for layer in range(5):
        grid.event_layers.add(100.0, porosity=0.7)
    compact = Compact(grid, porosity_min=0.1, porosity_max=0.7)
    compact.run_one_step()

    assert np.all(grid.event_layers["porosity"][1:] < 0.7)
    assert grid.event_layers["porosity"][0] == approx(0.7)

    assert np.all(grid.event_layers.dz[0] == approx(100.))
    assert np.all(grid.event_layers.dz[1:] < 100.)


def test_layers_compact_evenly(grid):
    for layer in range(1):
        grid.event_layers.add(100.0, porosity=0.7)
    compact = Compact(grid, porosity_min=0.1, porosity_max=0.7)
    compact.run_one_step()

    assert grid.event_layers["porosity"].ptp(axis=1) == approx(0.)


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
    ],
)
def test_init_with_bad_param(grid, param, value):
    params = {param: value}
    with raises(ValueError):
        Compact(grid, **params)
