import os
import pathlib
import shutil
import tempfile

import nox

PYTHON_VERSION = "3.12"
PROJECT = "compaction"
ROOT = pathlib.Path(__file__).parent


@nox.session(python=PYTHON_VERSION, venv_backend="conda")
def test(session: nox.Session) -> None:
    """Run the tests."""
    os.environ["WITH_OPENMP"] = "1"

    # session.conda_install("c-compiler", "cxx-compiler")
    session.log(f"CC = {os.environ.get('CC', 'NOT FOUND')}")
    session.install("-r", "requirements.in")
    session.install("-r", "requirements-testing.in")
    session.install("-e", ".", "--no-deps")

    args = [
        "--mypy",
        "--cov",
        PROJECT,
        "-vvv",
    ] + session.posargs

    if "CI" in os.environ:
        args.append(f"--cov-report=xml:{ROOT.absolute()!s}/coverage.xml")
    session.run("pytest", *args)

    if "CI" not in os.environ:
        session.run("coverage", "report", "--ignore-errors", "--show-missing")


@nox.session(name="test-cli", python=PYTHON_VERSION, venv_backend="conda")
def test_cli(session: nox.Session) -> None:
    """Test the command line interface."""
    session.install(".")
    session.run("compaction", "--help")
    session.run("compaction", "--version")
    session.run("compaction", "generate", "--help")
    session.run("compaction", "run", "--help")
    session.run("compaction", "setup", "--help")


@nox.session
def lint(session: nox.Session) -> None:
    """Look for lint."""
    skip_hooks = [] if "--no-skip" in session.posargs else ["check-manifest", "pyroma"]

    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", env={"SKIP": ",".join(skip_hooks)})


@nox.session
def towncrier(session: nox.Session) -> None:
    """Check that there is a news fragment."""
    session.install("towncrier")
    session.run("towncrier", "check", "--compare-with", "origin/master")


@nox.session(name="build-index")
def build_index(session: nox.Session) -> None:
    session.install("sphinx")
    session.install(".")


# @nox.session(name="build-docs", venv_backend="conda")
@nox.session(name="build-docs")
def build_docs(session: nox.Session) -> None:
    """Build the docs."""
    build_dir = ROOT / "build"
    docs_dir = ROOT / "docs"

    session.install("-r", docs_dir / "requirements.in")
    session.install("-e", ".")

    build_dir.mkdir(exist_ok=True)
    session.run(
        "sphinx-build",
        "-b",
        "html",
        "-W",
        "--keep-going",
        docs_dir / "source",
        build_dir / "html",
    )
    session.log(f"generated docs at {build_dir / 'html'!s}")


@nox.session
def build(session: nox.Session) -> None:
    """Build sdist and wheel dists."""
    session.install("pip")
    session.install("build")
    session.run("python", "--version")
    session.run("pip", "--version")
    session.run("python", "-m", "build", "--outdir", "./build/wheelhouse")


@nox.session
def release(session):
    """Tag, build and publish a new release to PyPI."""
    session.install("zest.releaser[recommended]")
    session.install("zestreleaser.towncrier")
    session.run("fullrelease")


@nox.session(name="publish-testpypi")
def publish_testpypi(session):
    """Publish wheelhouse/* to TestPyPI."""
    session.run("twine", "check", "build/wheelhouse/*")
    session.run(
        "twine",
        "upload",
        "--skip-existing",
        "--repository-url",
        "https://test.pypi.org/legacy/",
        "build/wheelhouse/*.tar.gz",
    )


@nox.session(name="publish-pypi")
def publish_pypi(session):
    """Publish wheelhouse/* to PyPI."""
    session.run("twine", "check", "build/wheelhouse/*")
    session.run(
        "twine",
        "upload",
        "--skip-existing",
        "build/wheelhouse/*.tar.gz",
    )


@nox.session(python=False)
def clean(session):
    """Remove all .venv's, build files and caches in the directory."""
    for folder in _args_to_folders(session.posargs):
        with session.chdir(folder):
            shutil.rmtree("build", ignore_errors=True)
            shutil.rmtree("build/wheelhouse", ignore_errors=True)
            shutil.rmtree(f"src/{PROJECT}.egg-info", ignore_errors=True)
            shutil.rmtree(".pytest_cache", ignore_errors=True)
            shutil.rmtree(".venv", ignore_errors=True)

            for pattern in ["*.py[co]", "__pycache__"]:
                _clean_rglob(pattern)


@nox.session(python=False, name="clean-checkpoints")
def clean_checkpoints(session):
    """Remove jupyter notebook checkpoint files."""
    for folder in _args_to_folders(session.posargs):
        with session.chdir(folder):
            _clean_rglob("*-checkpoint.ipynb")
            _clean_rglob(".ipynb_checkpoints")


@nox.session(python=False, name="clean-docs")
def clean_docs(session: nox.Session) -> None:
    """Clean up the docs folder."""
    build_dir = ROOT / "build"

    if (build_dir / "html").is_dir():
        with session.chdir(build_dir):
            shutil.rmtree("html")

    if (ROOT / "build").is_dir():
        session.chdir(ROOT / "build")
        if os.path.exists("html"):
            shutil.rmtree("html")


@nox.session(python=False, name="clean-ext")
def clean_ext(session: nox.Session) -> None:
    """Clean shared libraries for extension modules."""
    for folder in _args_to_folders(session.posargs):
        with session.chdir(folder):
            _clean_rglob("*.so")


@nox.session(python=False)
def nuke(session):
    """Run all clean sessions."""
    clean_checkpoints(session)
    clean_docs(session)
    clean(session)
    clean_ext(session)


@nox.session(name="list-wheels")
def list_wheels(session):
    print(os.linesep.join(_get_wheels(session)))


@nox.session(name="list-ci-matrix")
def list_ci_matrix(session):
    def _os_from_wheel(name):
        if "linux" in name:
            return "linux"
        elif "macos" in name:
            return "macos"
        elif "win" in name:
            return "windows"

    for wheel in _get_wheels(session):
        print(f"- cibw-only: {wheel}")
        print(f"  os: {_os_from_wheel(wheel)}")


def _get_wheels(session):
    platforms = session.posargs or ["linux", "macos", "windows"]
    session.install("cibuildwheel")

    wheels = []
    for platform in platforms:
        with tempfile.TemporaryFile("w+") as fp:
            session.run(
                "cibuildwheel",
                "--print-build-identifiers",
                "--platform",
                platform,
                stdout=fp,
            )
            fp.seek(0)
            wheels += fp.read().splitlines()
    return wheels


def _args_to_folders(args):
    return [ROOT] if not args else [pathlib.Path(f) for f in args]


def _clean_rglob(pattern):
    nox_dir = pathlib.Path(".nox")

    for p in pathlib.Path(".").rglob(pattern):
        if nox_dir in p.parents:
            continue
        if p.is_dir():
            p.rmdir()
        else:
            p.unlink()
