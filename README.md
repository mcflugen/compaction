[![Build
Status](https://travis-ci.org/mcflugen/compaction.svg?branch=master)](https://travis-ci.org/mcflugen/compaction)

[![Build status](https://ci.appveyor.com/api/projects/status/yle29j1hl6a8yu8p?svg=true)](https://ci.appveyor.com/project/mcflugen/compaction)

[![Coverage
Status](https://coveralls.io/repos/github/mcflugen/compaction/badge.svg?branch=mcflugen%2Fadd-unit-tests)](https://coveralls.io/github/mcflugen/compaction?branch=master)

# compaction: Compact layers of sediment

Compact a column of sediment following Bahr et al., 2001.

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

## Requirements

*Compaction* requires Python 3.

Apart from Python, *Compaction* has a number of other requirements, all of which
can be obtained through either *pip* or *conda*, that will be automatically
installed when you install *Compaction*.

To see a full listing of the requirements, have a look at the project's
*requirements.txt* file.

If you are a developer of *Compaction* you will also want to install
additional dependencies for running *Compaction*'s tests to make sure
that things are working as they should. These dependencies are listed
in *requirements-testing.txt*.

## Installation

To install *Compaction*, first create a new environment in
which *Compaction* will be installed. This, although not necessary, will
isolate the installation so that there won't be conflicts with your
base *Python* installation. This can be done with *conda* as:

    $ conda create -n compaction python=3
    $ conda activate compaction

## Stable Release

*Compaction*, and its dependencies, can be installed either with *pip*
or *conda*. Using *pip*:

    $ pip install compaction

Using *conda*:

    $ conda install compaction -c conda-forge

### From Source

After downloading the *Compaction* source code, run the following from
*Compaction*'s top-level folder (the one that contains *setup.py*) to
install *Compaction* into the current environment:

    $ pip install -e .

## Input Files

### Configuration File

The main *Compaction* input file is a yaml-formatted text file that lists
constants used by *Compaction*. Running the following will print a sample
*Compaction* configuration file:

    $ compact show config
    c: 5.0e-08
    porosity_max: 0.5
    porosity_min: 0.0
    rho_grain: 2650.0
    rho_void: 1000.0

### Porosity File

The *Compaction* porosity file defines initial porosity of each of the
sediment layers to be compacted as a two-column CSV file. The first
column is layer thickness (in meters) and the second the porosity of
the sediment in that layer. A sample porosity file can be obtained with:

    $ compact show porosity
    # Layer Thickness [m], Porosity [-]
    100.0,0.5
    100.0,0.5
    100.0,0.5

## Output File

The output file of *Compaction* is a porosity file of the same form as
the input porosity file - a CSV file of layer thickness and porosity.

## Examples

To run a simulation using the sample input files described above, you first
need to create a set of sample files:

    $ sequence setup example
    example/sequence.yaml

You can now run the simulation:

    $ sequence run example/sequence.yaml
    # Layer Thickness [m], Porosity [-]
    100.0,0.5
    96.18666488709239,0.4801774231522433
    92.78860257194452,0.4611407154102571
