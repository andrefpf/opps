from opps.properties.cross_section import CrossSection


class PipeCrossSection(CrossSection):
    def __init__(self, diameter, thickness=0):
        self.diameter = diameter
        self.thickness = thickness

    def info(self):
        return f"diameter = {self.diameter}; thickness = {self.thickness}"
