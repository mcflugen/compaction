import sys

import click
import pandas
import yaml

from ._version import get_versions
from .compaction import compact

__version__ = get_versions()["version"]
del get_versions


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


@click.command()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", is_flag=True, help="Emit status messages to stderr.")
@click.option("--dry-run", is_flag=True, help="Do not actually run the model")
@click.option(
    "--config", default=None, type=click.File(mode="r"), help="Configuration file"
)
@click.argument("input", type=click.File(mode="r"))
@click.argument("output", default="-", type=click.File(mode="w"))
def main(input, output, config, dry_run, verbose):

    params = load_config(config)
    if verbose:
        click.secho(yaml.dump(params, default_flow_style=False), err=True)

    if dry_run:
        click.secho("Nothing to do. 😴", err=True, fg="green")
    else:
        run_compaction(input, output, **params)

        click.secho("💥 Finished! 💥", err=True, fg="green")
        click.secho("Output written to {0}".format(output.name), err=True, fg="green")
