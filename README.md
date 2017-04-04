# compaction

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

To install,

    $ python setup.py install

## Run

The installation will create the command line program, ``compact``. For
help,

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

    $ compact porosity_profile.csv -

This will then print the new porosity profile in the same format.
