import pathlib
import sys
from typing import Optional, TextIO

import click
import numpy as np  # type: ignore
import pandas  # type: ignore
import yaml

from ._version import get_versions
from .compaction import compact as _compact

__version__ = get_versions()["version"]
del get_versions


def load_config(file: Optional[TextIO] = None):
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
        conf.update(yaml.safe_load(file))
    return conf


def _contents_of_input_file(infile: str) -> str:
    params = load_config()

    def as_csv(data, header=None):
        with StringIO() as fp:
            np.savetxt(fp, data, header=header, delimiter=",", fmt="%.1f")
            contents = fp.getvalue()
        return contents

    contents = {
        "config": yaml.dump(params, default_flow_style=False),
        "porosity": as_csv(
            [[1.0, 0.4], [1.0, 0.4], [1.0, 0.2]],
            header="Layer Thickness [m], Porosity [-]",
        ),
    }

    return contents[infile]


def run_compaction(
    src: Optional[TextIO] = None, dest: Optional[TextIO] = None, **kwds
) -> None:
    src = src or sys.stdin
    dest = dest or sys.stdout

    init = pandas.read_csv(src, names=("dz", "porosity"), dtype=float, comment="#")

    porosity_new = _compact(init.dz.values, init.porosity.values, **kwds)

    dz_new = init.dz * (1 - init.porosity) / (1 - porosity_new)

    out = pandas.DataFrame.from_dict({"dz": dz_new, "porosity": porosity_new})
    out.to_csv(dest, index=False, header=False)


@click.group()
@click.version_option()
def compact() -> None:
    """Compact layers of sediment.

    \b
    Examples:

      Create a folder with example input files,

        $ compact setup compact-example

      Run a simulation using the examples input files,

        $ compact run compact-example/porosity.csv
    """
    pass


@compact.command()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", is_flag=True, help="Emit status messages to stderr.")
@click.option("--dry-run", is_flag=True, help="Do not actually run the model")
# @click.option(
#     "--config", default="config.yaml", type=click.File(mode="r"), help="Configuration file"
# )
@click.option(
    "--config",
    type=click.Path(
        exists=False, file_okay=True, dir_okay=False, readable=True, allow_dash=False
    ),
    default="config.yaml",
    is_eager=True,
    help="Read configuration from PATH.",
)
@click.argument("src", type=click.File(mode="r"))
@click.argument("dest", default="-", type=click.File(mode="w"))
def run(src: TextIO, dest: TextIO, config: str, dry_run: bool, verbose: bool) -> None:

    config_path = pathlib.Path(config)
    if src.name is not None:
        rundir = pathlib.Path(src.name).parent.resolve()
    else:
        rundir = pathlib.Path(".")

    with open(rundir / config_path) as fp:
        params = load_config(fp)
    if verbose:
        click.secho(yaml.dump(params, default_flow_style=False), err=True)

    if dry_run:
        click.secho("Nothing to do. 😴", err=True, fg="green")
    else:
        run_compaction(src, dest, **params)

        click.secho("💥 Finished! 💥", err=True, fg="green")
        click.secho("Output written to {0}".format(dest.name), err=True, fg="green")


@compact.command()
@click.argument(
    "infile",
    type=click.Choice(["config", "porosity"]),
)
def show(infile: str) -> None:
    """Show example input files."""
    click.secho(_contents_of_input_file(infile), err=False)


@compact.command()
@click.argument(
    "dest",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
)
def setup(dest: str) -> None:
    """Setup a folder of input files for a simulation."""
    folder = pathlib.Path(dest)

    files = [pathlib.Path(fname) for fname in ["porosity.csv", "config.yaml"]]

    existing_files = [folder / name for name in files if (folder / name).exists()]
    if existing_files:
        for name in existing_files:
            click.secho(
                f"{name}: File exists. Either remove and then rerun or choose a different destination folder",
                err=True,
            )
    else:
        for fname in files:
            with open(folder / fname, "w") as fp:
                print(_contents_of_input_file(fname.stem), file=fp)
        click.secho(str(folder / "porosity.csv"), err=False)

    sys.exit(len(existing_files))
