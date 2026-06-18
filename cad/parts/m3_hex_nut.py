"""M3 hex nut reference geometry from bd_warehouse."""

import math

from bd_warehouse.fastener import HexNut, read_fastener_parameters_from_csv
from build123d import (
    BuildPart,
    BuildSketch,
    Color,
    Part,
    Plane,
    RegularPolygon,
    Rot,
    extrude,
)
from mr import artifact

M3_HEX_NUT_SIZE = "M3-0.5"
_NUT_DATA = read_fastener_parameters_from_csv("hex_nut_parameters.csv")[M3_HEX_NUT_SIZE]
WIDTH_ACROSS_FLATS_MM = float(_NUT_DATA["iso4032:s"])
NUT_THICKNESS_MM = float(_NUT_DATA["iso4032:m"])

POCKET_AXIS_ROTATION = (0, 90, 0)
# RegularPolygon rotation that matches bd_warehouse HexNut in the pocket plane.
POCKET_HEX_ROTATION_DEG = 30.0
PART_COLOR = Color(0.1, 0.1, 0.1)


def make_m3_hex_nut(
    *,
    rotation: tuple[float, float, float] = (0, 0, 0),
    simple: bool = False,
) -> Part:
    """Build an ISO 4032 M3 hex nut from bd_warehouse."""
    nut = Part(Rot(*rotation) * HexNut(M3_HEX_NUT_SIZE, simple=simple))
    nut.color = PART_COLOR
    return nut


def make_m3_hex_nut_for_pocket(*, simple: bool = False) -> Part:
    """Return an M3 nut oriented for flush seating in the sphere +X pocket."""
    return make_m3_hex_nut(rotation=POCKET_AXIS_ROTATION, simple=simple)


def hex_nut_pocket_seat(*, cut_offset: float, radius: float) -> tuple[float, float, float]:
    """Shared origin for the pocket cut and flush reference nut placement."""
    return cut_offset, 0.0, (cut_offset + radius) / 2


def position_flush_in_x_pocket(
    nut: Part,
    *,
    cut_x: float,
    center_y: float,
    center_z: float,
) -> Part:
    """Translate a pocket-axis nut so its opening face is flush with cut_x."""
    nut_bbox = nut.bounding_box()
    nut_center = (
        (nut_bbox.min.X + nut_bbox.max.X) / 2,
        (nut_bbox.min.Y + nut_bbox.max.Y) / 2,
        (nut_bbox.min.Z + nut_bbox.max.Z) / 2,
    )
    return nut.translate(
        (
            cut_x - nut_bbox.max.X,
            center_y - nut_center[1],
            center_z - nut_center[2],
        )
    )


def positioned_m3_hex_nut_at_seat(
    *,
    cut_offset: float,
    radius: float,
    simple: bool = False,
) -> Part:
    """Return a reference nut flush in the pocket defined by the shared seat."""
    cut_x, center_y, center_z = hex_nut_pocket_seat(
        cut_offset=cut_offset,
        radius=radius,
    )
    return position_flush_in_x_pocket(
        make_m3_hex_nut_for_pocket(simple=simple),
        cut_x=cut_x,
        center_y=center_y,
        center_z=center_z,
    )


def _nut_opening_face(nut: Part):
    """Return the pocket opening face on the positioned reference nut."""
    return max(
        (face for face in nut.faces() if face.normal_at().X > 0.9),
        key=lambda face: face.area,
    )


def _nut_hex_envelope_across_flats(nut: Part) -> float:
    """Across-flats span of the positioned nut profile in the pocket plane."""
    bbox = nut.bounding_box()
    return max(bbox.size.Y, bbox.size.Z)


def hex_margin_to_across_flats(*, base_across_flats: float, hex_nut_margin: float) -> float:
    """Convert a radial clearance margin in mm to a larger hex across-flats size."""
    return base_across_flats + 2 * hex_nut_margin


def hex_margin_to_profile_scale(*, base_across_flats: float, hex_nut_margin: float) -> float:
    """Scale factor for the hex profile when margin is applied in millimetres."""
    return (
        hex_margin_to_across_flats(
            base_across_flats=base_across_flats,
            hex_nut_margin=hex_nut_margin,
        )
        / base_across_flats
    )


def principal_hex_wall_angles(part: Part) -> list[float]:
    walls: list[tuple[float, float]] = []
    for face in part.faces():
        normal = face.normal_at()
        if abs(normal.X) > 0.01:
            continue
        angle = round(math.degrees(math.atan2(normal.Z, normal.Y)), 1)
        walls.append((face.area, angle))

    walls.sort(reverse=True)
    angles: list[float] = []
    for _, angle in walls:
        if angle not in angles:
            angles.append(angle)
        if len(angles) == 6:
            break
    return sorted(angles)


def pocket_cut_plane_from_nut(nut: Part) -> Plane:
    """Sketch plane on the positioned nut opening, normal pointing into the void."""
    opening = _nut_opening_face(nut)
    center = opening.center()
    return Plane(origin=center, x_dir=(0, 1, 0), z_dir=(1, 0, 0))


def make_m3_hex_nut_pocket_cutter(
    *,
    cut_offset: float,
    radius: float,
    hex_nut_margin: float,
) -> Part:
    """Hex prism cutter in the same pose as the reference nut, enlarged by margin."""
    nut = positioned_m3_hex_nut_at_seat(
        cut_offset=cut_offset,
        radius=radius,
        simple=True,
    )
    base_across_flats = _nut_hex_envelope_across_flats(nut)
    cutter_across_flats = hex_margin_to_across_flats(
        base_across_flats=base_across_flats,
        hex_nut_margin=hex_nut_margin,
    )
    plane = pocket_cut_plane_from_nut(nut)

    with BuildPart() as cutter:
        with BuildSketch(plane):
            RegularPolygon(
                radius=cutter_across_flats / 2,
                side_count=6,
                major_radius=False,
                rotation=POCKET_HEX_ROTATION_DEG,
            )
        extrude(amount=-NUT_THICKNESS_MM)

    return cutter.part


@artifact(short_desc="ISO 4032 M3 hex nut reference solid")
def m3_hex_nut() -> Part:
    """Reference nut geometry from bd_warehouse for pocket fit checks."""
    return make_m3_hex_nut()
