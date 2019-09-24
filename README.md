[![Build Status](https://travis-ci.org/mcflugen/compaction.svg?branch=master)](https://travis-ci.org/mcflugen/compaction)
[![Build status](https://ci.appveyor.com/api/projects/status/yle29j1hl6a8yu8p?svg=true)](https://ci.appveyor.com/project/mcflugen/compaction)
[![Coverage Status](https://coveralls.io/repos/github/mcflugen/compaction/badge.svg?branch=mcflugen%2Fadd-unit-tests)](https://coveralls.io/github/mcflugen/compaction?branch=mcflugen%2Fadd-unit-tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/b1a1b9f1091044faace5879171ce3020)](https://www.codacy.com/manual/mcflugen/compaction?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=mcflugen/compaction&amp;utm_campaign=Badge_Grade)
[![PyPI version](https://badge.fury.io/py/compaction.svg)](https://badge.fury.io/py/compaction)
[![Conda Recipe](https://img.shields.io/badge/recipe-compaction-green.svg)](https://anaconda.org/conda-forge/compaction)
[![Conda Downloads](https://img.shields.io/conda/dn/conda-forge/compaction.svg)](https://anaconda.org/conda-forge/compaction)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/compaction.svg)](https://anaconda.org/conda-forge/compaction)

# Compaction

Compact columns of sediment based on Bahr et al., 2001.

Sediment compaction and corresponding porosity variations are modeled
by a simple exponential with depth. The porosity solution is derived
analytically as a complicated function of pore water pressure, but the
underlying form is shown to approximate an exponential except near the
surface where the behavior is linear.
Compact a column of sediment based on the Bahr et al., 2001.

Cite as:

    @article{bahr2001exponential,
      title={Exponential approximations to compacted sediment porosity profiles},
      author={Bahr, David B and Hutton, Eric WH and Syvitski, James PM and Pratson, Lincoln F},
      journal={Computers \& Geosciences},
      volume={27},
      number={6},
      pages={691--700},
      year={2001},
      publisher={Pergamon}
    }

## Install

Install with *pip*,

    $ pip install compaction

Install with *conda*,

    $ conda install compaction -c conda-forge

## Run

After you've installed *compaction*, you will have the command line
program, ``compact``. For help,

    $ compact --help

To run you'll need to first create a porosity profile file. This file
consists of two columns of comma-separated values. The first column
is the thickness of sediment and the second the porosity of that sediment.
The first row is the top of the sediment column. For example, the
following file describes three sediment layers (each one meter thick)
with decreasing porosity.

    1., .4
    1., .3
    1., .2

Now run ``compact`` with this file.

    $ compact porosity_profile.csv --set porosity_max=0.4 -

This will then print the new porosity profile in the same format.
