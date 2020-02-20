import pathlib
import sys
from functools import partial
from io import StringIO
from typing import Optional, TextIO

import click
import numpy as np  # type: ignore
import pandas  # type: ignore
import yaml

from ._version import get_versions
from .compaction import compact as _compact

__version__ = get_versions()["version"]
del get_versions

out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)


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
        "porosity_max": 0.5,
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
            [[100.0, 0.5], [100.0, 0.5], [100.0, 0.5]],
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

    dz_new = np.empty_like(init.dz)
    porosity_new = _compact(
        init.dz.values, init.porosity.values, return_dz=dz_new, **kwds
    )

    out = pandas.DataFrame.from_dict({"dz": dz_new, "porosity": porosity_new})
    print("# Layer Thickness [m], Porosity [-]", file=dest)
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
    pass  # pragma: no cover


@compact.command()
@click.version_option(version=__version__)
@click.option("-v", "--verbose", is_flag=True, help="Emit status messages to stderr.")
@click.option("--dry-run", is_flag=True, help="Do not actually run the model")
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
    """Run a simulation."""
    try:
        from_stdin = src.name == "<stdin>"
    except AttributeError:
        from_stdin = True
    try:
        from_stdout = dest.name == "<stdout>"
    except AttributeError:
        from_stdout = True

    config_path = pathlib.Path(config)
    if from_stdin:
        rundir = pathlib.Path(".")
    else:
        rundir = pathlib.Path(src.name).parent.resolve()

    with open(rundir / config_path, "r") as fp:
        params = load_config(fp)

    if verbose:
        out(yaml.dump(params, default_flow_style=False))

    if dry_run:
        out("Nothing to do. 😴")
    else:
        run_compaction(src, dest, **params)

        out("💥 Finished! 💥")
        out("Output written to {0}".format("<stdout>" if from_stdout else dest.name))

    sys.exit(0)


@compact.command()
@click.argument(
    "infile", type=click.Choice(["config", "porosity"]),
)
def show(infile: str) -> None:
    """Show example input files."""
    print(_contents_of_input_file(infile))


@compact.command()
@click.argument(
    "dest", type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
)
def setup(dest: str) -> None:
    """Setup a folder of input files for a simulation."""
    folder = pathlib.Path(dest)

    files = [pathlib.Path(fname) for fname in ["porosity.csv", "config.yaml"]]

    existing_files = [folder / name for name in files if (folder / name).exists()]
    if existing_files:
        for name in existing_files:
            err(
                f"{name}: File exists. Either remove and then rerun or choose a different destination folder",
            )
    else:
        for fname in files:
            with open(folder / fname, "w") as fp:
                print(_contents_of_input_file(fname.stem), file=fp)
        print(str(folder / "porosity.csv"))

    sys.exit(len(existing_files))
