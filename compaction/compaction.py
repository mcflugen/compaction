#! /usr/bin/env python
import sys

import numpy as np
import pandas
import yaml
from scipy.constants import g as gravity


def compact(
    dz,
    porosity,
    c=5e-8,
    rho_grain=2650.0,
    excess_pressure=0.0,
    porosity_min=0.0,
    porosity_max=1.0,
    rho_void=1000.0,
):
    """Compact a column of sediment.

    Parameters
    ----------
    dz : ndarray
        Array of sediment thicknesses with depth (the first element is
        the top of the sediment column)[meters].
    porosity : ndarray or number
        Sediment porosity [-].
    c : ndarray or number, optional
        Compaction coefficient that describes how easily the sediment is to
        compact [Pa^-1].
    rho_grain : ndarray or number, optional
        Grain density of the sediment [kg / m^3].
    excess_pressure : ndarray or number, optional
        Excess pressure with depth [Pa].
    porosity_min : ndarray or number, optional
        Minimum porosity that can be achieved by the sediment. This is the
        porosity of the sediment in its closest-compacted state [-].
    porosity_max : ndarray or number, optional
        Maximum porosity of the sediment. This is the porosity of the sediment
        without any compaction [-].
    rho_void : ndarray or number, optional
        Density of the interstitial fluid [kg / m^3].

    Returns
    -------
    porosity : ndarray
        New porosities after compaction.
    """
    load = (rho_grain - rho_void) * dz * (1.0 - porosity) * gravity
    overlying_load = np.cumsum(load) - load - excess_pressure

    porosity_new = porosity_min + (porosity_max - porosity_min) * np.exp(
        -c * overlying_load
    )

    return np.minimum(porosity_new, porosity, out=porosity_new)


def load_config(file=None):
    """Load compaction config file.

    Parameters
    ----------
    fname : file-like, optional
        Opened config file or ``None``. If ``None``, return default
        values.

    Returns
    -------
    dict
        Config parameters.
    """
    conf = {
        "c": 5e-8,
        "porosity_min": 0.0,
        "porosity_max": 1.0,
        "rho_grain": 2650.0,
        "rho_void": 1000.0,
    }
    if file is not None:
        conf.update(yaml.load(file))
    return conf


def run_compaction(input=None, output=None, **kwds):
    input = input or sys.stdin
    output = output or sys.stdout

    init = pandas.read_csv(input, names=("dz", "porosity"), dtype=float)

    porosity_new = compact(init.dz.values, init.porosity.values, **kwds)

    dz_new = init.dz * (1 - init.porosity) / (1 - porosity_new)

    out = pandas.DataFrame.from_dict({"dz": dz_new, "porosity": porosity_new})
    out.to_csv(output, index=False, header=False)
