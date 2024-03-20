from opps.properties.cross_section import CrossSection


class BeamCrossSection(CrossSection):
    def __init__(self, diameter):
        self.diameter = diameter
