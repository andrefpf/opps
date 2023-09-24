import vtk

from opps.model.flange import Flange
import numpy as np


class FlangeActor(vtk.vtkActor):
    def __init__(self, flange: Flange):
        self.flange = flange
        self.create_geometry()
        
    def create_geometry(self):
        bigger_radius = max(self.flange.start_radius, self.flange.end_radius)
        width = 0.3 * bigger_radius
        y_vector = np.array((0,1,0))

        disk_source = vtk.vtkDiskSource()
        disk_source.SetCenter((0,0,0) - y_vector * width / 2)
        disk_source.SetNormal(y_vector)
        disk_source.SetInnerRadius(self.flange.start_radius)
        disk_source.SetOuterRadius(bigger_radius + width)
        disk_source.SetCircumferentialResolution(50)
        disk_source.Update()

        extrusion_filter = vtk.vtkLinearExtrusionFilter()
        extrusion_filter.SetInputData(disk_source.GetOutput())
        extrusion_filter.SetExtrusionTypeToNormalExtrusion()
        extrusion_filter.SetVector(y_vector)
        extrusion_filter.SetScaleFactor(width)
        extrusion_filter.Update()

        append_polydata = vtk.vtkAppendPolyData()
        append_polydata.AddInputData(extrusion_filter.GetOutput())

        number_of_bolts = 8
        for i in range(number_of_bolts):
            angle = i * 2 * np.pi / number_of_bolts
            nut = vtk.vtkCylinderSource()
            nut.SetHeight(width * 3 / 2)
            nut.SetRadius(width / 3)
            nut.SetCenter(
                (bigger_radius + width / 2) * np.sin(angle), 
                0, 
                (bigger_radius + width / 2) * np.cos(angle),
            )
            nut.Update()
            append_polydata.AddInputData(nut.GetOutput())
        append_polydata.Update()
    
        unit_normal = self.flange.normal / np.linalg.norm(self.flange.normal)
        angle_x = np.arccos(np.dot(y_vector, unit_normal))
        angle_y = np.arccos(np.dot((0,0,1), unit_normal))
        transform = vtk.vtkTransform()
        transform.Translate(self.flange.position)
        transform.RotateY(np.degrees(angle_y))
        transform.RotateX(np.degrees(angle_x))
        transform.Update()

        transform_filter = vtk.vtkTransformFilter()
        transform_filter.SetInputData(append_polydata.GetOutput())
        transform_filter.SetTransform(transform)
        transform_filter.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(transform_filter.GetOutput())
        self.SetMapper(mapper)
