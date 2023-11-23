from landlab import RasterModelGrid

from compaction.landlab import Compact


class TimeLandlabComponent:
    param_names = ["layers", "columns"]
    params = [[10, 100, 1000, 10000], [10, 100, 1000, 10000]]

    def setup(self, layers, columns):
        self.grid = RasterModelGrid((3, columns))
        for _ in range(layers):
            self.grid.event_layers.add(1.0, porosity=0.5)

    def time_component(self, layers, columns):
        compact = Compact(self.grid, porosity_min=0.0, porosity_max=0.5)
        compact.calculate()
