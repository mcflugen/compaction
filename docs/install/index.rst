.. _install:

=========================
Installation Instructions
=========================

If you want to use *compaction*, this is almost
certainly the correct place to get install instruction. If you want to change
the *compaction* source code go to the
:ref:`developer install instructions <developer_install>`.

In order to run *compaction* you will need a python distribution. We recommend the
`Anaconda distribution <https://www.anaconda.com/distribution/>`_
(version 3.6 or higher).

You can install *compaction* using either the pip or conda package management tools.
We distribute *compaction* through `PyPI <https://pypi.org/project/compaction/>`_
and `conda-forge <https://anaconda.org/conda-forge/compaction>`_.

Conda instructions
------------------

Installation
````````````
In a terminal type:

.. code-block:: bash

  $ conda install compaction -c conda-forge

If you work with many different packages that require conflicting dependencies,
consider reading about (and using)
`conda environments <https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html#managing-environments>`_.


Updating
````````

In a terminal type:

.. code-block:: bash

  $ conda update compaction

Uninstall
`````````

In a terminal type:

.. code-block:: bash

    $ conda uninstall compaction

Pip Instructions
----------------

Installation
````````````
In a terminal type:

.. code-block:: bash

  $ pip install compaction

Updating
````````

In a terminal type:

.. code-block:: bash

  $ pip update compaction

Uninstall
`````````

In a terminal type:

.. code-block:: bash

    $ pip uninstall compaction


.. _developer_install:

Install from source
-------------------

If you would like the very latest development version of *compaction* or would
like to modify the code, you will want to install from source. To do so, once
you've downloadd the source, You only need run the following in the base
folder for *compaction* (the one with *setup.py*)

.. code-block:: bash

    $ pip install -e .
