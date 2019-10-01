.. compaction documentation master file, created by
   sphinx-quickstart on Tue Sep 24 12:30:54 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to compaction's documentation!
======================================

Generate compacted porosity profiles.

*Compaction* is a Python package that, given an initial porosity profile with
depth, generates a new porosity profile based on the exponential approximation
described in [Bahr2001]_. The change in porosity depends both on sediment
lithology (e.g. sediment compaction coeffienct, sediment porosity under
zero load, etc.) and overlying load.

The *Compaction* package provides three utilities for compacting sediment:

* The :py:class:`~compaction.AnalyticalCompactor` provides a solution for
  sediment profiles of constant lithology.

  .. code:: python

      >>> from compaction import AnalyticalCompactor
      >>> compact = AnalyticalCompactor(rho_void=1030.0)
      >>> compact([100.0, 200.0, 300.0], 0.6)

* The :py:class:`~compaction.Compactor` solves the more general solution of
  sediment profiles that vary with lithology. For example, changing
  compaction coefficients or excess pressures with depth.

  .. code:: python

      >>> from compaction import Compactor
      >>> compact = Compactor(c=[5e-8, 3e-8, 5e-8])
      >>> compact([0.0, 100.0, 200.0, 300.0], [0.6, 0.5, 0.4])

* :py:class:`~compaction.Compact` is a `landlab`_ component that compacts `landlab`_
  :py:class:`landlab.EventLayers`, intended to be coupled with other
  Earth-system models

  .. code:: python

      >>> from landlab.components import Compaction
      >>> for layer in range(3):
      ...     grid.event_layers.add(100.0, porosity=0.6)

      >>> compact = Compaction(grid, porosity_min=0.1, porosity_max=0.6)
      >>> compact.run_one_step()

.. _landlab: https://landlab.github.io


.. toctree::
   :maxdepth: 2

   install/index
   api/index

..
   user_guide/index
   whatsnew/index
   getting_started/index
   development/index


References
==========

.. [Bahr2001] `Computers & Geosciences <https://doi.org/10.1016/S0098-3004(00)00140-0>`_

  Bahr, D.B., Hutton, E.W., Syvitski, J.P. and Pratson, L.F., 2001.
  *Exponential approximations to compacted sediment porosity profiles*.
  Computers & Geosciences, 27(6), pp.691-700.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
