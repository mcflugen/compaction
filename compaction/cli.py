import os
import pathlib
import sys
import warnings
from functools import partial
from io import StringIO
from typing import Optional, TextIO

import click
import numpy as np  # type: ignore
import pandas  # type: ignore
import tomlkit as toml  # type: ignore

from .compaction import compact as _compact


out = partial(click.secho, bold=True, err=True)
err = partial(click.secho, fg="red", err=True)


def _tomlkit_to_popo(d):
    try:
        result = getattr(d, "value")
    except AttributeError:
        result = d

    if isinstance(result, list):
        result = [_tomlkit_to_popo(x) for x in result]
    elif isinstance(result, dict):
        result = {
            _tomlkit_to_popo(key): _tomlkit_to_popo(val) for key, val in result.items()
        }
    elif isinstance(result, toml.items.Integer):
        result = int(result)
    elif isinstance(result, toml.items.Float):
        result = float(result)
    elif isinstance(result, (toml.items.String, str)):
        result = str(result)
    elif isinstance(result, (toml.items.Bool, bool)):
        result = bool(result)
    else:
        if not isinstance(result, (int, float, str, bool)):
            warnings.warn(
                "unexpected type ({0!r}) encountered when converting toml to a dict".format(
                    result.__class__.__name__
                )
            )

    return result


def load_config(stream: Optional[TextIO] = None):
    """Load compaction config file.

    Parameters
    ----------
    stream : file-like, optional
        Opened config file or ``None``. If ``None``, return default
        values.

    Returns
    -------
    dict
        Config parameters.
    """
    conf = {
        "compact" : {
            "constants": {
                "c": 5e-8,
                "porosity_min": 0.0,
                "porosity_max": 0.5,
                "rho_grain": 2650.0,
                "rho_void": 1000.0,
            }
        }
    }
    if stream is not None:
        try:
            local_params = toml.parse(stream.read())["compact"]
        except KeyError:
            local_params = {"constants": {}}

        try:
            local_constants = local_params["constants"]
        except KeyError:
            local_constants = {}

        conf["compact"]["constants"].update(local_constants)

    return _tomlkit_to_popo(conf).pop("compact")


def _contents_of_input_file(infile: str) -> str:
    params = load_config()

    def as_csv(data, header=None):
        with StringIO() as fp:
            np.savetxt(fp, data, header=header, delimiter=",", fmt="%.1f")
            contents = fp.getvalue()
        return contents

    contents = {
        "compact.toml": toml.dumps(dict(compact=params)),
        "porosity.csv": as_csv(
            [[100.0, 0.5], [100.0, 0.5], [100.0, 0.5]],
            header="Layer Thickness [m], Porosity [-]",
        ),
    }

    return contents[infile]


def run_compaction(src: str, dest: str, **kwds) -> None:
    init = pandas.read_csv(src, names=("dz", "porosity"), dtype=float, comment="#")

    dz_new = np.empty_like(init.dz)
    porosity_new = _compact(
        init.dz.values, init.porosity.values, return_dz=dz_new, **kwds
    )

    result = pandas.DataFrame.from_dict({"dz": dz_new, "porosity": porosity_new})

    with open(dest, "w") as fp:
        print("# Layer Thickness [m], Porosity [-]", file=fp)
        result.to_csv(fp, index=False, header=False)


@click.group(chain=True)
@click.version_option()
@click.option(
    "--cd",
    default=".",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True),
    help="chage to directory, then execute",
)
def compact(cd) -> None:
    """Compact layers of sediment.

    \b
    Examples:

      Create a folder with example input files,

        $ mkdir compaction-example && cd compaction-example
        $ compact setup

      Run a simulation using the examples input files,

        $ compact run
    """
    os.chdir(cd)


@compact.command()
@click.version_option()
@click.option("-v", "--verbose", is_flag=True, help="Emit status messages to stderr.")
@click.option("--dry-run", is_flag=True, help="Do not actually run the model")
def run(dry_run: bool, verbose: bool) -> None:
    """Run a simulation."""
    with open("compact.toml", "r") as fp:
        params = load_config(fp)

    if verbose:
        out(toml.dumps(params))

    if dry_run:
        out("Nothing to do. 😴")
    else:
        run_compaction("porosity.csv", "porosity-out.csv", **params["constants"])

        out("💥 Finished! 💥")
        out("Output written to {0}".format("porosity-out.csv"))


@compact.command()
@click.argument(
    "infile", type=click.Choice(["compact.toml", "porosity.csv"]),
)
def generate(infile: str) -> None:
    """Show example input files."""
    print(_contents_of_input_file(infile))


@compact.command()
def setup() -> None:
    """Setup a folder of input files for a simulation."""
    files = [pathlib.Path(fname) for fname in ["porosity.csv", "compact.toml"]]

    existing_files = [str(file_) for file_ in files if file_.exists()]
    if existing_files:
        for name in existing_files:
            err(
                f"{name}: File exists. Either remove and then rerun or choose a different destination folder",
            )
    else:
        for file_ in files:
            with open(file_, "w") as fp:
                print(_contents_of_input_file(file_.name), file=fp)
        print(pathlib.Path.cwd())

    if existing_files:
        sys.exit(len(existing_files))
