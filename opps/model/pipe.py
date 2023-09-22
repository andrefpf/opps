from dataclasses import dataclass


@dataclass
class Pipe:
    start: tuple[float, float, float]
    end: tuple[float, float, float]
    diameter: float = 0.1

    def as_vtk(self):
        from opps.interface.viewer_3d.actors.pipe_actor import PipeActor

        return PipeActor(self)
