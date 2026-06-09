from build123d import Align, BuildPart, Part, Sphere
from cad_tooling.render_decorator import render
from mr import artifact, customizable
from pydantic import BaseModel, Field


def make_sphere(radius: float = 10) -> Part:
    """Build a centered sphere with the given radius."""
    with BuildPart() as part:
        Sphere(radius=radius, align=(Align.CENTER, Align.CENTER, Align.CENTER))

    return part.part


@artifact(cover=True, short_desc="Demo sphere for workspace smoke tests")
@render(camera="iso", face_color=(0.31, 0.63, 1.0))
def sphere() -> Part:
    """Default-radius sphere published as a MakerRepo artifact."""
    return make_sphere()


class SphereParameters(BaseModel):
    radius: float = Field(default=10, gt=0, description="Sphere radius in mm")


@customizable(sample_parameters=SphereParameters())
def sphere_generator(parameters: SphereParameters) -> Part:
    """Parametric sphere — customize radius via MakerRepo generators or CLI."""
    return make_sphere(radius=parameters.radius)
