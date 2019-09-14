#!/usr/bin/env python
import os

import pandas
import pytest
import yaml
from click.testing import CliRunner
from numpy.testing import assert_array_almost_equal

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
    runner = CliRunner()
    result = runner.invoke(cli.main, ["--help"])
    assert result.exit_code == 0

    result = runner.invoke(cli.main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output


def test_dry_run(tmpdir, datadir):
    with tmpdir.as_cwd():
        runner = CliRunner()
        result = runner.invoke(
            cli.main,
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
            cli.main,
            [
                "--verbose",
                "--config={0}".format(datadir / "config.yaml"),
                str(datadir / "porosity_profile.txt"),
                "out.txt",
            ],
        )
        assert result.exit_code == 0
        assert (tmpdir / "out.txt").exists()

        conf = yaml.load(os.linesep.join(result.output.splitlines()[:5]))
        assert isinstance(conf, dict)


def test_constant_porosity(tmpdir, datadir):
    data = pandas.read_csv(
        datadir / "porosity_profile.txt", names=("dz", "porosity"), dtype=float
    )
    phi_expected = compact(data["dz"], data["porosity"], porosity_max=0.6)
    with tmpdir.as_cwd():
        runner = CliRunner()
        result = runner.invoke(
            cli.main,
            [
                "--config={0}".format(datadir / "config.yaml"),
                str(datadir / "porosity_profile.txt"),
                "out.txt",
            ],
        )

        assert result.exit_code == 0
        assert "Output written to out.txt" in result.output
        phi_actual = pandas.read_csv("out.txt", names=("dz", "porosity"), dtype=float)

    assert_array_almost_equal(phi_actual["porosity"], phi_expected)
