"""Compact layers of sediment due to overlying load.

Examples
--------
>>> from landlab import RasterModelGrid
>>> grid = RasterModelGrid((3, 4))
>>> for _ in range(10):
...     grid.event_layers.add(100., porosity=.4)
>>> compact = Compact(grid)
>>> compact.run_one_step()
"""
from landlab import Component

from .compaction import compact


class Compact(Component):

    _name = "Compaction"
    _time_units = ""
    _input_var_names = ("sediment_layer_thickness", "sediment_layer_porority")
    _output_var_names = ()
    _var_units = {"sediment_layer_thickness": "m", "sediment_layer_porority": ""}
    _var_mapping = {
        "sediment_layer_thickness": "cell",
        "sediment_layer_porority": "cell",
    }
    _var_doc = {
        "sediment_layer_thickness": "Thickness of sediment layer to compact",
        "sediment_layer_porority": "Porosity of the sediment layer to compact",
    }

    def __init__(
        self,
        grid,
        c=5e-8,
        rho_grain=2650.0,
        excess_pressure=0.0,
        porosity_min=0.0,
        porosity_max=1.0,
        rho_void=1000.0,
    ):
        """Compact layers of sediment.

        Parameters
        ----------
        grid : RasterModelGrid
            A landlab grid.
        c : ndarray or number, optional
            Compaction coefficient that describes how easily the sediment is to
            compact [Pa^-1].
        rho_grain : ndarray or number, optional
            Grain density of the sediment [kg / m^3].
        excess_pressure : ndarray or number, optional
            Excess pressure with depth [Pa].
        porosity_min : ndarray or number, optional
            Minimum porosity that can be achieved by the sediment. This is the
            porosity of the sediment in its closest-compacted state [-].
        porosity_max : ndarray or number, optional
            Maximum porosity of the sediment. This is the porosity of the sediment
            without any compaction [-].
        rho_void : ndarray or number, optional
            Density of the interstitial fluid [kg / m^3].

        Examples
        --------
        >>> from landlab import RasterModelGrid
        >>> grid = RasterModelGrid((3, 4))
        >>> for _ in range(10):
        ...     grid.event_layers.add(100., porosity=.4)
        >>> compact = Compact(grid)
        >>> compact.run_one_step()
        """
        self._compaction_params = {}

        super(Compact, self).__init__(grid)

        self.c = c
        self.rho_grain = rho_grain
        self.excess_pressure = excess_pressure
        self.porosity_min = porosity_min
        self.porosity_max = porosity_max
        self.rho_void = rho_void

        grid.event_layers.add(0.0, porosity=0.0)

    def run_one_step(self, dt=None):
        dz = self._grid.event_layers.dz
        porosity = self._grid.event_layers["porosity"]

        porosity_new = compact(dz, porosity, **self._compaction_params)

        dz[:] = dz * (1 - porosity) / (1 - porosity_new)
        porosity[:] = porosity_new

    @property
    def params(self):
        return tuple(self._compaction_params.items())

    @property
    def c(self):
        return self._compaction_params["c"]

    @c.setter
    def c(self, new_val):
        if new_val >= 0.0:
            self._compaction_params["c"] = new_val
        else:
            raise ValueError("c must be >= 0.")

    @property
    def rho_grain(self):
        return self._compaction_params["rho_grain"]

    @rho_grain.setter
    def rho_grain(self, new_val):
        if new_val > 0.0:
            self._compaction_params["rho_grain"] = new_val
        else:
            raise ValueError("rho_grain must be positive")

    @property
    def excess_pressure(self):
        return self._compaction_params["excess_pressure"]

    @excess_pressure.setter
    def excess_pressure(self, new_val):
        self._compaction_params["excess_pressure"] = new_val

    @property
    def porosity_min(self):
        return self._compaction_params["porosity_min"]

    @porosity_min.setter
    def porosity_min(self, new_val):
        if 0.0 <= new_val <= 1.0:
            self._compaction_params["porosity_min"] = new_val
        else:
            raise ValueError("porosity_min must be between [0, 1]")

    @property
    def porosity_max(self):
        return self._compaction_params["porosity_max"]

    @porosity_max.setter
    def porosity_max(self, new_val):
        if 0.0 <= new_val <= 1.0:
            self._compaction_params["porosity_max"] = new_val
        else:
            raise ValueError("porosity_max must be between [0, 1]")

    @property
    def rho_void(self):
        return self._compaction_params["rho_void"]

    @rho_void.setter
    def rho_void(self, new_val):
        if new_val > 0.0:
            self._compaction_params["rho_void"] = new_val
        else:
            raise ValueError("rho_void must be positive")
