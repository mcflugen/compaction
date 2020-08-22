#!/usr/bin/env python
import shutil

import numpy as np  # type: ignore
import pandas  # type: ignore
import pytest  # type: ignore
import tomlkit  # type: ignore
from click.testing import CliRunner
from numpy.testing import assert_array_almost_equal  # type: ignore

from compaction import cli, compact


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.compaction, ["--help"])
    assert result.exit_code == 0

    result = runner.invoke(cli.compaction, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.stdout

    result = runner.invoke(cli.compaction)
    assert result.exit_code == 0
    assert "Compact layers of sediment" in result.stdout


def test_dry_run(tmpdir, datadir):
    with tmpdir.as_cwd():
        shutil.copy(datadir / "compaction.toml", ".")
        shutil.copy(datadir / "porosity.csv", ".")

        runner = CliRunner()
        result = runner.invoke(cli.run, ["--dry-run"],)
        assert result.exit_code == 0
        assert "Nothing to do" in result.output
        assert not (tmpdir / "porosity-out.csv").exists()


def test_verbose(tmpdir, datadir):
    with tmpdir.as_cwd():
        shutil.copy(datadir / "compaction.toml", ".")
        shutil.copy(datadir / "porosity.csv", ".")

        runner = CliRunner()
        result = runner.invoke(cli.run, ["--verbose"],)
        assert result.exit_code == 0
        assert (tmpdir / "porosity-out.csv").exists()


def test_constant_porosity(tmpdir, datadir):
    data = pandas.read_csv(
        datadir / "porosity.csv", names=("dz", "porosity"), dtype=float
    )
    phi_expected = compact(data["dz"], data["porosity"], porosity_max=0.6)
    with tmpdir.as_cwd():
        shutil.copy(datadir / "compaction.toml", ".")
        shutil.copy(datadir / "porosity.csv", ".")

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(cli.run)

        assert result.exit_code == 0
        assert "Output written to porosity-out.csv" in result.stderr
        phi_actual = pandas.read_csv(
            "porosity-out.csv", names=("dz", "porosity"), dtype=float, comment="#"
        )

    assert_array_almost_equal(phi_actual["porosity"], phi_expected)


def test_setup(tmpdir):
    with tmpdir.as_cwd():
        runner = CliRunner()
        result = runner.invoke(cli.setup)

        assert result.exit_code == 0
        assert (tmpdir / "compaction.toml").exists()
        assert (tmpdir / "porosity.csv").exists()


@pytest.mark.parametrize(
    "files",
    (("compaction.toml",), ("porosity.csv",), ("compaction.toml", "porosity.csv")),
)
def test_setup_with_existing_files(tmpdir, files):
    runner = CliRunner(mix_stderr=False)
    with tmpdir.as_cwd():
        for name in files:
            with open(name, "w"):
                pass

        result = runner.invoke(cli.setup)

        assert result.exit_code == len(files)
        assert result.stdout == ""
        for name in files:
            assert name in result.stderr


def test_generate(tmpdir):
    with tmpdir.as_cwd():
        result = CliRunner(mix_stderr=False).invoke(cli.generate, ["compaction.toml"])
        assert result.exit_code == 0
        with open("compaction.toml", "w") as fp:
            fp.write(result.stdout)

        result = CliRunner(mix_stderr=False).invoke(cli.generate, ["porosity.csv"])
        assert result.exit_code == 0
        with open("porosity.csv", "w") as fp:
            fp.write(result.stdout)

        result = CliRunner(mix_stderr=False).invoke(cli.run)

        assert (tmpdir / "porosity-out.csv").exists()
        assert result.exit_code == 0


def test_generate_toml(tmpdir):
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.generate, ["compaction.toml"])

    assert result.exit_code == 0

    params = tomlkit.parse(result.stdout)
    assert isinstance(params, dict)


def test_generate_porosity(tmpdir):
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.generate, ["porosity.csv"])

    assert result.exit_code == 0

    with open(tmpdir / "porosity.csv", "w") as fp:
        fp.write(result.stdout)

    data = pandas.read_csv(
        tmpdir / "porosity.csv", names=("dz", "porosity"), dtype=float, comment="#"
    )
    assert np.all(data.dz.values > 0.0)
    assert np.all(data.porosity.values >= 0.0)
