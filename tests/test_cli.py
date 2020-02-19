#!/usr/bin/env python
import filecmp
import os

import pandas  # type: ignore
import pytest  # type: ignore
import numpy as np  # type: ignore
import yaml
from click.testing import CliRunner
from numpy.testing import assert_array_almost_equal  # type: ignore

from compaction import cli, compact


@pytest.fixture
def response():
    """Sample pytest fixture.

    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument."""
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.compact, ["--help"])
    assert result.exit_code == 0

    result = runner.invoke(cli.compact, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.stdout

    result = runner.invoke(cli.compact)
    assert result.exit_code == 0
    assert "Compact layers of sediment" in result.stdout


def test_dry_run(tmpdir, datadir):
    with tmpdir.as_cwd():
        runner = CliRunner()
        result = runner.invoke(
            cli.run,
            [
                "--dry-run",
                "--config={0}".format(datadir / "config.yaml"),
                str(datadir / "porosity_profile.txt"),
                "out.txt",
            ],
        )
        assert result.exit_code == 0
        assert "Nothing to do" in result.output
        assert not (tmpdir / "out.txt").exists()


def test_verbose(tmpdir, datadir):
    with tmpdir.as_cwd():
        runner = CliRunner()
        result = runner.invoke(
            cli.run,
            [
                "--verbose",
                "--config={0}".format(datadir / "config.yaml"),
                str(datadir / "porosity_profile.txt"),
                "out.txt",
            ],
        )
        assert result.exit_code == 0
        assert (tmpdir / "out.txt").exists()

        conf = yaml.safe_load(os.linesep.join(result.output.splitlines()[:5]))
        assert isinstance(conf, dict)


def test_constant_porosity(tmpdir, datadir):
    data = pandas.read_csv(
        datadir / "porosity_profile.txt", names=("dz", "porosity"), dtype=float
    )
    phi_expected = compact(data["dz"], data["porosity"], porosity_max=0.6)
    with tmpdir.as_cwd():
        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(
            cli.run,
            [
                "--config={0}".format(datadir / "config.yaml"),
                str(datadir / "porosity_profile.txt"),
                "out.txt",
            ],
        )

        assert result.exit_code == 0
        assert "Output written to out.txt" in result.stderr
        phi_actual = pandas.read_csv("out.txt", names=("dz", "porosity"), dtype=float)

    assert_array_almost_equal(phi_actual["porosity"], phi_expected)


def test_run_from_stdin(tmpdir, datadir):
    path_to_porosity = str(datadir / "porosity_profile.txt")
    with open(path_to_porosity) as fp:
        porosity_profile = fp.read()

    runner = CliRunner(mix_stderr=False)

    with tmpdir.as_cwd():
        result = runner.invoke(
            cli.run, [
                "--config={0}".format(datadir / "config.yaml"),
                path_to_porosity,
                "expected.txt",
            ],
        )
        assert result.exit_code == 0

        result = runner.invoke(
            cli.run,
            ["--config={0}".format(datadir / "config.yaml"), "-", "actual.txt"],
            input=porosity_profile,
        )
        assert result.exit_code == 0

        assert filecmp.cmp("actual.txt", "expected.txt")


def test_run_to_stdin(tmpdir, datadir):
    path_to_porosity = str(datadir / "porosity_profile.txt")

    runner = CliRunner(mix_stderr=False)

    with tmpdir.as_cwd():
        result = runner.invoke(
            cli.run, [
                "--config={0}".format(datadir / "config.yaml"),
                path_to_porosity,
                "actual.txt",
            ],
        )
        assert result.exit_code == 0
        with open("actual.txt") as fp:
            actual = fp.read()

        runner = CliRunner(mix_stderr=False)
        result = runner.invoke(
            cli.run, [
                "--config={0}".format(datadir / "config.yaml"),
                path_to_porosity,
            ],
        )
        assert result.exit_code == 0

        assert result.stdout.splitlines() == actual.splitlines()


def test_setup(tmpdir):
    with tmpdir.as_cwd():
        runner = CliRunner()
        result = runner.invoke(cli.setup, ["."])

        assert result.exit_code == 0
        assert (tmpdir / "config.yaml").exists()
        assert (tmpdir / "porosity.csv").exists()


@pytest.mark.parametrize(
    "files", (("config.yaml",), ("porosity.csv",), ("config.yaml", "porosity.csv"))
)
def test_setup_with_existing_files(tmpdir, files):
    runner = CliRunner(mix_stderr=False)
    with tmpdir.as_cwd():
        for name in files:
            with open(name, "w"):
                pass

        result = runner.invoke(cli.setup, ["."])

        assert result.exit_code == len(files)
        assert result.stdout == ""
        for name in files:
            assert name in result.stderr


def test_show(tmpdir):
    with tmpdir.as_cwd():
        result = CliRunner(mix_stderr=False).invoke(cli.show, ["config"])
        with open("config.yaml", "w") as fp:
            fp.write(result.stdout)

        result = CliRunner(mix_stderr=False).invoke(cli.show, ["porosity"])
        with open("porosity.csv", "w") as fp:
            fp.write(result.stdout)

        result = CliRunner(mix_stderr=False).invoke(cli.run, ["porosity.csv", "out.csv"])

        assert (tmpdir / "out.csv").exists()
        assert result.exit_code == 0


def test_show_config(tmpdir):
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.show, ["config"])

    assert result.exit_code == 0

    params = yaml.safe_load(result.stdout)
    assert isinstance(params, dict)


def test_show_porosity(tmpdir):
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(cli.show, ["porosity"])

    assert result.exit_code == 0

    with open(tmpdir / "porosity.csv", "w") as fp:
        fp.write(result.stdout)

    data = pandas.read_csv(
        tmpdir / "porosity.csv", names=("dz", "porosity"), dtype=float, comment="#"
    )
    assert np.all(data.dz.values > 0.0)
    assert np.all(data.porosity.values >= 0.0)
