#! /usr/bin/env python
import numpy as np
import pandas
from scipy.constants import g as gravity

import yaml


def compact(dz, porosity, c=5e-8, rho_grain=2650., excess_pressure=0.,
            porosity_min=0., porosity_max=1., rho_void=1000.):
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
    load = (rho_grain - rho_void) * dz * (1. - porosity) * gravity
    overlying_load = np.cumsum(load) - load - excess_pressure
    
    porosity_new = (
        porosity_min +
        (porosity_max - porosity_min) * np.exp(- c * overlying_load))

    return np.minimum(porosity_new, porosity, out=porosity_new)


def load_config(fname=None):
    """Load compaction config file.

    Parameters
    ----------
    fname : str, optional
        Name of config file or ``None``. If ``None``, return default
        values.

    Returns
    -------
    dict
        Config parameters.
    """
    conf = {
        'c': 3.68e-8,
        'porosity_min': 0.,
        'porosity_max': .4,
        'rho_grain': 2650.,
        'rho_void': 1000.,
    }
    if fname is not None:
        with open(fname, 'r') as fp:
            conf.update(yaml.load(fp))
    return conf


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('input', type=argparse.FileType('r'),
                        help='Initial porosity profile')
    parser.add_argument('output', type=argparse.FileType('w'),
                        help='Output porosity profile')
    parser.add_argument('--config', type=str, default=None,
                        help='Config file')

    args = parser.parse_args()

    conf = load_config(args.config)
    init = pandas.read_csv(args.input, names=('dz', 'porosity'), dtype=float)

    porosity_new = compact(init.dz.values, init.porosity.values, **conf)

    dz_new = init.dz * (1 - init.porosity) / (1 - porosity_new)

    out = pandas.DataFrame.from_items(
        [('dz', dz_new), ('porosity', porosity_new)])
    out.to_csv(args.output, index=False, header=False)


if __name__ == '__main__':
    main()
