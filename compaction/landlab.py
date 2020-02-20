"""Compact layers of sediment due to overlying load."""
from typing import Dict

from landlab import Component  # type: ignore
from scipy.constants import g  # type: ignore

from .compaction import compact


class Compact(Component):

    _name = "Compaction"
    _time_units = ""
    _input_var_names = ("sediment_layer_thickness", "sediment_layer_porority")
    _output_var_names = ("sediment_layer_porosity",)
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
        c: float = 5e-8,
        rho_grain: float = 2650.0,
        excess_pressure: float = 0.0,
        porosity_min: float = 0.0,
        porosity_max: float = 1.0,
        rho_void: float = 1000.0,
        gravity: float = g,
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
        gravity : float
            Acceleration due to gravity [m / s^2].

        Examples
        --------
        >>> import numpy as np
        >>> from landlab import RasterModelGrid

        >>> grid = RasterModelGrid((3, 5))
        >>> for layer in range(5):
        ...     grid.event_layers.add(100.0, porosity=0.7)

        >>> compact = Compact(grid, porosity_min=0.1, porosity_max=0.7)
        >>> compact.run_one_step()
        RasterModelGrid((3, 5), xy_spacing=(1.0, 1.0), xy_of_lower_left=(0.0, 0.0))

        >>> compact.grid.event_layers["porosity"] < 0.7
        array([[ True,  True,  True],
               [ True,  True,  True],
               [ True,  True,  True],
               [ True,  True,  True],
               [False, False, False]], dtype=bool)
        >>> compact.grid.event_layers.dz < 100.0
        array([[ True,  True,  True],
               [ True,  True,  True],
               [ True,  True,  True],
               [ True,  True,  True],
               [False, False, False]], dtype=bool)
        """
        self._compaction_params: Dict[str, float] = {}

        super(Compact, self).__init__(grid)

        self.c = c
        self.rho_grain = rho_grain
        self.excess_pressure = excess_pressure
        self.porosity_min = porosity_min
        self.porosity_max = porosity_max
        self.rho_void = rho_void
        self.gravity = gravity

    def run_one_step(self, dt=None):
        if self.grid.event_layers.number_of_layers == 0:
            return self.grid

        dz = self._grid.event_layers.dz[-1::-1, :]
        porosity = self._grid.event_layers["porosity"][-1::-1, :]

        porosity[:] = compact(dz, porosity, return_dz=dz, **self._compaction_params)

        return self.grid

    def calculate(self):
        return self.run_one_step()

    @property
    def params(self):
        return tuple(self._compaction_params.items())

    @property
    def c(self) -> float:
        return self._compaction_params["c"]

    @c.setter
    def c(self, new_val: float):
        if new_val >= 0.0:
            self._compaction_params["c"] = new_val
        else:
            raise ValueError("c must be >= 0.")

    @property
    def rho_grain(self) -> float:
        return self._compaction_params["rho_grain"]

    @rho_grain.setter
    def rho_grain(self, new_val: float):
        if new_val > 0.0:
            self._compaction_params["rho_grain"] = new_val
        else:
            raise ValueError("rho_grain must be positive")

    @property
    def excess_pressure(self) -> float:
        return self._compaction_params["excess_pressure"]

    @excess_pressure.setter
    def excess_pressure(self, new_val: float):
        self._compaction_params["excess_pressure"] = new_val

    @property
    def porosity_min(self) -> float:
        return self._compaction_params["porosity_min"]

    @porosity_min.setter
    def porosity_min(self, new_val: float):
        if 0.0 <= new_val <= 1.0:
            self._compaction_params["porosity_min"] = new_val
        else:
            raise ValueError("porosity_min must be between [0, 1]")

    @property
    def porosity_max(self) -> float:
        return self._compaction_params["porosity_max"]

    @porosity_max.setter
    def porosity_max(self, new_val: float):
        if 0.0 <= new_val <= 1.0:
            self._compaction_params["porosity_max"] = new_val
        else:
            raise ValueError("porosity_max must be between [0, 1]")

    @property
    def rho_void(self) -> float:
        return self._compaction_params["rho_void"]

    @rho_void.setter
    def rho_void(self, new_val: float):
        if new_val > 0.0:
            self._compaction_params["rho_void"] = new_val
        else:
            raise ValueError("rho_void must be positive")

    @property
    def gravity(self) -> float:
        return self._compaction_params["gravity"]

    @gravity.setter
    def gravity(self, new_val: float):
        if new_val > 0.0:
            self._compaction_params["gravity"] = new_val
        else:
            raise ValueError("gravity must be positive")
