#! /usr/bin/env python
import numpy as np
from scipy.constants import g


def compact(
    dz,
    porosity,
    c=5e-8,
    rho_grain=2650.0,
    excess_pressure=0.0,
    porosity_min=0.0,
    porosity_max=1.0,
    rho_void=1000.0,
    gravity=g,
    return_dz=False,
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
    gravity : float, optional
        Acceleration due to gravity [m / s^2].
    return_dz : bool, optional
        If *True*, return compacted thickness array along with compacted porosities
        as a tuple of *(porosity, dz)*.

    Returns
    -------
    porosity : ndarray
        New porosities after compaction.
    """
    dz, porosity = np.asarray(dz, dtype=float), np.asarray(porosity, dtype=float)

    load = (rho_grain - rho_void) * dz * (1.0 - porosity) * gravity
    overlying_load = np.cumsum(load, axis=0) - load - excess_pressure

    porosity_new = porosity_min + (porosity_max - porosity_min) * np.exp(
        -c * overlying_load
    )

    np.minimum(porosity_new, porosity, out=porosity_new)

    if return_dz:
        return porosity_new, dz * (1.0 - porosity) / (1.0 - porosity_new)
    else:
        return porosity_new
