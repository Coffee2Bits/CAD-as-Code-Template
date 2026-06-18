"""Demo sphere assembly with flush M3 hex nut and screw references."""

from build123d import Compound
from mr import artifact

from cad.parts.m3_hex_nut import positioned_m3_hex_nut_at_seat
from cad.parts.m3_socket_head_cap_screw import positioned_m3_screw_at_seat
from cad.parts.sphere import make_sphere, northeast_quadrant_cut_offset
from cad.parts.sphere_tripod_support import make_sphere_tripod_support
from cad_tooling.render_decorator import render

SPHERE_RADIUS = 10


def make_demo_sphere(*, radius: float = SPHERE_RADIUS) -> Compound:
    """Assemble the demo sphere with flush M3 nut and screw references."""
    sphere = make_sphere(radius=radius)
    sphere.label = "sphere"

    cut_offset = northeast_quadrant_cut_offset(radius=radius)
    nut = positioned_m3_hex_nut_at_seat(cut_offset=cut_offset, radius=radius)
    nut.label = "m3_hex_nut_reference"

    screw = positioned_m3_screw_at_seat(cut_offset=cut_offset, radius=radius)
    screw.label = "m3_socket_head_cap_screw_reference"

    support = make_sphere_tripod_support(sphere_radius=radius)
    support.label = "sphere_tripod_support"

    return Compound(
        label="demo_sphere",
        children=[sphere, nut, screw, support],
    )


@artifact(cover=True, short_desc="Demo sphere with M3 nut and screw references")
@render(
    renders=[
        {"camera": "front", "width": 800, "height": 600},
        {"camera": "iso", "width": 800, "height": 600},
    ]
)
def demo_sphere() -> Compound:
    """Main project assembly published for release previews."""
    return make_demo_sphere()
