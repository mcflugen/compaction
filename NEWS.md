# Release Notes

<!-- towncrier-draft-entries:: Not yet released -->

<!-- towncrier release notes start -->

## [0.2.3](https://github.com/mcflugen/compaction/tree/0.2.3) - 2023-11-21


### Other Changes and Additions

- Set up [towncrier](https://towncrier.readthedocs.io/en/stable/index.html)
  to manage the changelog. [#16](https://github.com/mcflugen/compaction/issues/16)
- Added a [pre-commit](https://pre-commit.com/) hook file for running
  the linters. [#16](https://github.com/mcflugen/compaction/issues/16)
- Added a [nox](https://nox.thea.codes/en/stable/) file for routine
  project management like running the tests and linting. [#16](https://github.com/mcflugen/compaction/issues/16)
- Added GitHub Actions for running the continuous integration tests, which
  includes running the tests and linters. [#16](https://github.com/mcflugen/compaction/issues/16)
- Moved static project metadata from *setup.py* to the now standard
  *pyproject.toml*. [#16](https://github.com/mcflugen/compaction/issues/16)
- Added support for Python 3.12 and dropped support for Python 3.9. [#19](https://github.com/mcflugen/compaction/issues/19)
