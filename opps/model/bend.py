from dataclasses import dataclass

import numpy as np

from opps.model.point import Point
from opps.model.structure import Structure


def normalize(vector):
    return vector / np.linalg.norm(vector)


@dataclass
class Bend(Structure):
    start: Point
    end: Point
    corner: Point
    curvature: float
    start_diameter: float = 0.1
    end_diameter: float = 0.1
    color: tuple = (167, 223, 124)
    auto: bool = True

    @property
    def center(self):
        if self.is_colapsed():
            return self.corner

        a_vector = normalize(self.start.coords() - self.corner.coords())
        b_vector = normalize(self.end.coords() - self.corner.coords())

        if (a_vector == b_vector).all():
            return self.corner

        if np.dot(a_vector, b_vector) == 1:
            return self.corner

        sin_angle = np.linalg.norm(a_vector - b_vector) / 2
        angle = np.arcsin(sin_angle)
        center_distance = self.curvature / np.sin(angle)

        c_vector = normalize(a_vector + b_vector)
        return Point(*(self.corner.coords() + c_vector * center_distance))

    def normalize_values(self, start: Point, end: Point):
        if (start.coords() == self.corner.coords()).all():
            self.colapse()
            return

        if (end.coords() == self.corner.coords()).all():
            self.colapse()
            return

        a_vector = normalize(start.coords() - self.corner.coords())
        b_vector = normalize(end.coords() - self.corner.coords())

        if (a_vector == b_vector).all():
            self.colapse()
            return

        if np.dot(a_vector, b_vector) == 1:
            self.colapse()
            return

        sin_angle = np.linalg.norm(a_vector - b_vector) / 2
        angle = np.arcsin(sin_angle)

        corner_distance = np.cos(angle) * self.curvature / np.sin(angle)
        
        # if the curve is beyond its limits ignore it
        if corner_distance >= np.linalg.norm(start.coords() - self.corner.coords()):
            self.colapse()
            return
        
        if corner_distance >= np.linalg.norm(end.coords() - self.corner.coords()):
            self.colapse()
            return           

        self.start.set_coords(*(self.corner.coords() + corner_distance * a_vector))
        self.end.set_coords(*(self.corner.coords() + corner_distance * b_vector))

    def colapse(self):
        self.start.set_coords(*self.corner.coords())
        self.end.set_coords(*self.corner.coords())

    def divide(self):
        corner_coords = np.array([*self.corner])
        start_coords = np.array([*self.start])
        end_coords = np.array([*self.end])
        radius = self.curvature

        a_vector = start_coords - corner_coords
        b_vector = end_coords - corner_coords
        norm_a_vector = np.linalg.norm(a_vector)
        norm_b_vector = np.linalg.norm(b_vector)
        c_vector = a_vector + b_vector
        c_vector_normalized = c_vector / np.linalg.norm(c_vector)



        corner_distance = norm_a_vector / np.sqrt(0.5 * ((np.dot(a_vector, b_vector) / (norm_a_vector * norm_b_vector)) + 1))
        center_coords = corner_coords + c_vector_normalized * corner_distance

        point_one = corner_coords + a_vector * (corner_distance - radius) / corner_distance
        point_two = corner_coords + b_vector * (corner_distance - radius) / corner_distance

        corner_one = Point(*point_one)
        corner_two = Point(*point_two)

        middle_point = center_coords - (b_vector / np.linalg.norm(b_vector)) * radius
        



    def is_colapsed(self):
        return self.start == self.end == self.corner

    def set_diameter(self, diameter, point=None):
        if point is None:
            self.start_diameter = diameter
            self.end_diameter = diameter
            return

        if point == self.start:
            self.start_diameter = diameter

        if point == self.end:
            self.end_diameter = diameter

        if point == self.corner:
            self.start_diameter = diameter
            self.end_diameter = diameter

    def get_diameters(self):
        return [self.start_diameter, self.end_diameter]

    def get_points(self):
        return [
            self.start,
            self.end,
            self.corner,
        ]

    def as_vtk(self):
        from opps.interface.viewer_3d.actors.bend_actor import BendActor

        return BendActor(self)

    def __hash__(self) -> int:
        return id(self)
    
    def replace_point(self, old, new):
        if self.start == old:
            self.start = new
    
        elif self.end == old:
            self.end = new

