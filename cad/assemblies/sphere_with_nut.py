"""Sphere demo assembly with a flush M3 hex nut reference."""

from build123d import Compound
from mr import artifact

from cad.parts.m3_hex_nut import positioned_m3_hex_nut_at_seat
from cad.parts.sphere import make_sphere, northeast_quadrant_cut_offset
from cad_tooling.render_decorator import render

SPHERE_RADIUS = 10


def make_sphere_with_nut(*, radius: float = SPHERE_RADIUS) -> Compound:
    """Assemble the sphere and flush M3 nut reference."""
    sphere = make_sphere(radius=radius)
    sphere.label = "sphere"

    cut_offset = northeast_quadrant_cut_offset(radius=radius)
    nut = positioned_m3_hex_nut_at_seat(cut_offset=cut_offset, radius=radius)
    nut.label = "m3_hex_nut_reference"

    return Compound(label="sphere_with_nut", children=[sphere, nut])


@artifact(cover=True, short_desc="Sphere with flush M3 hex nut reference")
@render(
    renders=[
        {"camera": "front", "width": 800, "height": 600},
        {"camera": "iso", "width": 800, "height": 600},
    ]
)
def sphere_with_nut() -> Compound:
    """Main project assembly published for release previews."""
    return make_sphere_with_nut()
