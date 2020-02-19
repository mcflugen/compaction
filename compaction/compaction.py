#! /usr/bin/env python
from typing import Optional

import numpy as np  # type: ignore
from scipy.constants import g  # type: ignore


def compact(
    dz: np.ndarray,
    porosity: np.ndarray,
    c: float = 5e-8,
    rho_grain: float = 2650.0,
    excess_pressure: float = 0.0,
    porosity_min: float = 0.0,
    porosity_max: float = 1.0,
    rho_void: float = 1000.0,
    gravity: float = g,
    return_dz: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Compact a column of sediment.

    Parameters
    ----------
    dz : ndarray of float
        Array of sediment thicknesses with depth (the first element is
        the top of the sediment column) [meters].
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
    return_dz : ndarray of float, optional
        If provided, an output array into which to place the calculated
        compacted layer thicknesses.

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

    if return_dz is not None:
        if return_dz.dtype is dz.dtype and return_dz.shape == dz.shape:
            contains_sediment = porosity_new < 1.0
            np.divide(
                dz * (1.0 - porosity),
                1.0 - porosity_new,
                where=contains_sediment,
                out=return_dz,
            )
            return_dz[~contains_sediment] = 0.0
        else:
            raise TypeError(
                "size and shape of return_dz ({0}, {1}) must be that of dz ({2}, {3})".format(
                    return_dz.dtype, return_dz.shape, dz.dtype, dz.shape
                )
            )

    return porosity_new
