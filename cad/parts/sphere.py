from build123d import (
    Align,
    Axis,
    Box,
    BuildPart,
    BuildSketch,
    Circle,
    Compound,
    Edge,
    Face,
    Locations,
    Mode,
    Part,
    Plane,
    Solid,
    Sphere,
    Vector,
    add,
)
from cad_tooling.render_decorator import render
from mr import artifact, customizable
from pydantic import BaseModel, Field

EMBOSSED_TEXT = "Example Text"
EMBOSS_DEPTH = 0.5
# -Y equator point on the XY great circle (OCCT back view)
TEXT_POSITION_ON_PATH = 0.75


def _equator_circle_edge(radius: float) -> Edge:
    """Equator circle edge lying on the sphere surface."""
    with BuildSketch(Plane.XY) as sketch:
        Circle(radius)
    return sketch.sketch.edges()[0]


def _letter_face_on_sphere_surface(
    face: Face,
    *,
    path: Edge,
    path_length: float,
    position_on_path: float,
) -> tuple[Face, Vector]:
    """Place a letter on the equator and tip it outward along the surface normal."""
    bbox = face.bounding_box()
    face_bottom_center = Vector((bbox.min.X + bbox.max.X) / 2, 0, 0)
    relative_position = position_on_path + face_bottom_center.X / path_length
    wire_tangent = path.tangent_at(relative_position)
    wire_angle = Vector(1, 0, 0).get_signed_angle(wire_tangent)
    wire_position = path.position_at(relative_position)

    oriented = face.translate(wire_position - face_bottom_center).rotate(
        Axis(wire_position, (0, 0, 1)),
        -wire_angle,
    )
    oriented = oriented.rotate(Axis(wire_position, wire_tangent), 90)
    return oriented, wire_position.normalized()


def _embossed_letter_solids(
    *,
    radius: float,
    path: Edge,
    path_length: float,
) -> list[Solid]:
    """Extruded letter solids wrapped on the front equator."""
    font_size = radius * 0.3
    letter_faces = Compound.make_text(
        EMBOSSED_TEXT,
        font_size=font_size,
        font="DejaVu Sans",
    ).faces()
    solids: list[Solid] = []

    for face in letter_faces:
        wrapped_face, radial = _letter_face_on_sphere_surface(
            face,
            path=path,
            path_length=path_length,
            position_on_path=TEXT_POSITION_ON_PATH,
        )
        solids.append(Solid.extrude(wrapped_face, radial * EMBOSS_DEPTH))

    return solids


def _northeast_cut_offset(embossed_solids: list[Solid]) -> float:
    """Offset for the inner corner of the NE cut, above the embossed text."""
    text_top_z = max(solid.bounding_box().max.Z for solid in embossed_solids)
    return text_top_z + EMBOSS_DEPTH * 0.2


def _subtract_northeast_quadrant(
    part: Part,
    *,
    radius: float,
    offset: float,
) -> Part:
    """Remove the front-view NE wedge (+X, +Z), spanning full depth (-Y to +Y)."""
    cutter_size = radius * 2
    with BuildPart() as cut:
        add(part)
        with Locations((offset, 0, offset)):
            Box(
                cutter_size,
                cutter_size,
                cutter_size,
                align=(Align.MIN, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
    return cut.part


def make_sphere(radius: float = 10) -> Part:
    """Build a centered sphere with embossed text and the NE quadrant removed."""
    path = _equator_circle_edge(radius)
    path_length = path.length
    embossed_solids = _embossed_letter_solids(
        radius=radius,
        path=path,
        path_length=path_length,
    )
    cut_offset = _northeast_cut_offset(embossed_solids)

    with BuildPart() as part:
        Sphere(radius=radius, align=(Align.CENTER, Align.CENTER, Align.CENTER))

        for embossed_solid in embossed_solids:
            add(embossed_solid, mode=Mode.ADD)

    return _subtract_northeast_quadrant(
        part.part,
        radius=radius,
        offset=cut_offset,
    )


@artifact(cover=True, short_desc="Demo sphere for workspace smoke tests")
@render(
    renders=[
        {
            "camera": "front",
            "width": 800,
            "height": 600,
            "face_color": (0.31, 0.63, 1.0),
        },
        {
            "camera": "iso",
            "width": 800,
            "height": 600,
            "face_color": (0.31, 0.63, 1.0)},
    ]
)
def sphere() -> Part:
    """Default-radius sphere published as a MakerRepo artifact."""
    return make_sphere()


class SphereParameters(BaseModel):
    radius: float = Field(default=10, gt=0, description="Sphere radius in mm")


@customizable(sample_parameters=SphereParameters())
def sphere_generator(parameters: SphereParameters) -> Part:
    """Parametric sphere — customize radius via MakerRepo generators or CLI."""
    return make_sphere(radius=parameters.radius)
