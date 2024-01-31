from pathlib import Path
from typing import Generator

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QApplication

from opps.interface.main_window import MainWindow
from opps.io.cad_file.cad_handler import *
from opps.model import Pipeline
from opps.model.pipeline_editor import PipelineEditor
from opps.model.point import Point
from opps.model.structure import Structure
from opps.io.pcf.pcf_handler import PCFHandler
from opps.io.pcf.pcf_exporter import PCFExporter


class Application(QApplication):
    selection_changed = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.save_path = None

        self.selected_points = set()
        self.selected_structures = set()

        self.pipeline = Pipeline()
    
        self.editor = PipelineEditor(self.pipeline)


        self.main_window = MainWindow()
        self.main_window.show()

    def new(self):
        self.pipeline = Pipeline()
        self.editor = PipelineEditor(self.pipeline)
        self.main_window.render_widget.update_plot()

    def open(self, path):
        path = Path(path)
        file_format = path.suffix.lower().strip()

        if file_format == ".pcf":
            self._open_pcf(path)
        else:
            self._open_cad(path)

    def save(self, path):
        path = Path(path)
        self.save_path = path
        file_format = path.suffix.lower().strip()
        self._save_pcf(path)

        # if file_format == ".pcf":
        #     self._save_pcf(path)
        # else:
        #     self._save_cad(path)

    def _open_cad(self, path):
        print("Oppening CAD")

    def _open_pcf(self, path):
        self.pcf_handler = PCFHandler()
        self.pcf_handler.load(path,self.pipeline)
        self.update()

    def _save_cad(self, path):
        exporter = CADHandler()
        exporter.save(path, self.pipeline)
        print("Saving CAD")

    def _save_pcf(self, path):
        self.pcf_exporter = PCFExporter()
        self.pcf_exporter.save(path,self.pipeline)
        print("Saving PCF")

    def get_point(self, point_index) -> Point:
        return self.editor.points[point_index]

    def get_structure(self, structure_index) -> Structure:
        return self.pipeline.structures[structure_index]

    def get_selected_points(self) -> Generator[Point, None, None]:
        return self.selected_points

    def get_selected_structures(self) -> Generator[Structure, None, None]:
        return self.selected_structures

    def delete_selection(self):
        for structure in self.get_selected_structures():
            self.editor.remove_structure(structure, rejoin=True)

        for point in self.get_selected_points():
            self.editor.remove_point(point, rejoin=False)

        self.clear_selection()
        self.update()

    def select_points(self, points, join=False, remove=False):
        points = set(points)

        if join and remove:
            self.selected_points ^= points
        elif join:
            self.selected_points |= points
        elif remove:
            self.selected_points -= points
        else:
            self.clear_selection()
            self.selected_points = points

        self.selection_changed.emit()

    def select_structures(self, structures, join=False, remove=False):
        structures = set(structures)

        # clear all the selected flags
        for structure in self.pipeline.structures:
            structure.selected = False

        # handle the selection according to modifiers like ctrl, shift, etc.
        if join and remove:
            self.selected_structures ^= structures
        elif join:
            self.selected_structures |= structures
        elif remove:
            self.selected_structures -= structures
        else:
            self.clear_selection()
            self.selected_structures = structures

        # apply the selection flag again for selected structures
        for structure in self.selected_structures:
            structure.selected = True

        self.selection_changed.emit()

    def clear_selection(self):
        for structure in self.pipeline.structures:
            structure.selected = False
        self.selected_points.clear()
        self.selected_structures.clear()
        self.selection_changed.emit()

    def update(self):
        self.editor._update_joints()
        self.editor._update_points()
        self.main_window.render_widget.update_plot(reset_camera=False)
