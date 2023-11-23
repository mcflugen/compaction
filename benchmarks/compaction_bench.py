import numpy as np

from compaction.compaction import compact


class TimeCompaction:
    param_names = ["layers", "columns"]
    params = [[10, 100, 1000, 10000], [10, 100, 1000, 10000]]

    def setup(self, layers, columns):
        self.dz = np.full((layers, columns), 1.0)
        self.phi = np.full((layers, columns), 0.5)
        self.dz_new = np.empty_like(self.dz)

    def time_without_dz(self, layers, columns):
        compact(self.dz, self.phi, porosity_max=0.5)

    def time_with_dz(self, layers, columns):
        compact(self.dz, self.phi, porosity_max=0.5, return_dz=self.dz_new)
