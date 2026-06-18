"""M3 socket head cap screw reference geometry from bd_warehouse."""

import math

from bd_warehouse.fastener import (
    ClearanceHole,
    SocketHeadCapScrew,
    _make_fastener_hole,
)
from build123d import (
    BuildPart,
    Color,
    Cylinder,
    Locations,
    Mode,
    Part,
    Rot,
    add,
)
from mr import artifact

from cad.parts.m3_hex_nut import hex_nut_pocket_seat

M3_SCREW_SIZE = "M3-0.5"
# Default length for the standalone artifact export only.
SCREW_LENGTH_MM = 8.0
SCREW_AXIS_ROTATION = (0, -90, 0)
CLEARANCE_FIT = "Close"
SCREW_HEAD_CLEARANCE_MARGIN_MM = 0.1
PART_COLOR = Color(0.72, 0.72, 0.76)


def _rotated_screw_bbox(*, length: float = SCREW_LENGTH_MM):
    screw = SocketHeadCapScrew(M3_SCREW_SIZE, length=length, simple=True)
    with BuildPart() as builder:
        add(Rot(*SCREW_AXIS_ROTATION) * screw)
    return builder.part.bounding_box()


def screw_head_height_mm() -> float:
    """Axial height of the socket head measured along the +X thread axis."""
    bbox = _rotated_screw_bbox()
    return -bbox.min.X


def screw_head_diameter_mm() -> float:
    """Outer diameter of the socket head in the pocket plane."""
    bbox = _rotated_screw_bbox()
    return max(bbox.size.Y, bbox.size.Z)


def screw_head_outward_relief_mm() -> float:
    """Counterbore extension past the sphere exterior so the head can exit freely."""
    return screw_head_height_mm()


def screw_head_travel_length_mm() -> float:
    """Axial span of the outward relief plus the seated head envelope."""
    return screw_head_outward_relief_mm() + screw_head_height_mm()


def make_m3_socket_head_cap_screw(
    *,
    rotation: tuple[float, float, float] = SCREW_AXIS_ROTATION,
    length: float = SCREW_LENGTH_MM,
) -> Part:
    """Build an ISO 4762 M3 socket head cap screw from bd_warehouse."""
    screw = SocketHeadCapScrew(M3_SCREW_SIZE, length=length, simple=True)
    with BuildPart() as builder:
        add(Rot(*rotation) * screw)
    part = builder.part
    part.color = PART_COLOR
    return part


def screw_entry_x(*, cut_offset: float, radius: float) -> float:
    """Return the -X sphere entry coordinate for the screw axis through the pocket seat."""
    _, center_y, center_z = hex_nut_pocket_seat(cut_offset=cut_offset, radius=radius)
    return -math.sqrt(radius**2 - center_y**2 - center_z**2)


def screw_length_for_seat(*, cut_offset: float, radius: float) -> float:
    """Grip length so the shaft tip is flush with the nut opening at +X."""
    cut_x, _, _ = hex_nut_pocket_seat(cut_offset=cut_offset, radius=radius)
    entry_x = screw_entry_x(cut_offset=cut_offset, radius=radius)
    return cut_x - entry_x - screw_head_height_mm()


def screw_clearance_hole_origin_x(*, cut_offset: float, radius: float) -> float:
    """Entry plane for the head counterbore, extended outward past the sphere skin."""
    return screw_entry_x(cut_offset=cut_offset, radius=radius) - screw_head_outward_relief_mm()


def screw_hole_depth(*, cut_offset: float, radius: float) -> float:
    """Bore depth from the outward head relief through the nut opening face."""
    cut_x, _, _ = hex_nut_pocket_seat(cut_offset=cut_offset, radius=radius)
    origin_x = screw_clearance_hole_origin_x(cut_offset=cut_offset, radius=radius)
    return cut_x - origin_x


def screw_clearance_hole_location(
    *, cut_offset: float, radius: float
) -> tuple[float, float, float]:
    """Shared origin for the clearance bore — outward of the sphere for head travel."""
    _, center_y, center_z = hex_nut_pocket_seat(cut_offset=cut_offset, radius=radius)
    origin_x = screw_clearance_hole_origin_x(cut_offset=cut_offset, radius=radius)
    return origin_x, center_y, center_z


def position_screw_tip_at_nut_face(
    screw: Part,
    *,
    cut_x: float,
    center_y: float,
    center_z: float,
) -> Part:
    """Translate a pocket-axis screw so its thread tip is flush with the nut opening."""
    bbox = screw.bounding_box()
    return screw.translate(
        (
            cut_x - bbox.max.X,
            center_y - (bbox.min.Y + bbox.max.Y) / 2,
            center_z - (bbox.min.Z + bbox.max.Z) / 2,
        )
    )


def positioned_m3_screw_at_seat(*, cut_offset: float, radius: float) -> Part:
    """Return a reference screw with its tip flush on the nut's exterior +X face."""
    cut_x, center_y, center_z = hex_nut_pocket_seat(cut_offset=cut_offset, radius=radius)
    length = screw_length_for_seat(cut_offset=cut_offset, radius=radius)
    return position_screw_tip_at_nut_face(
        make_m3_socket_head_cap_screw(length=length),
        cut_x=cut_x,
        center_y=center_y,
        center_z=center_z,
    )


def _make_screw_head_travel_cutter(
    *,
    origin_x: float,
    center_y: float,
    center_z: float,
) -> Part:
    """Cylindrical pocket for head removal — wider than the bd_warehouse counterbore."""
    travel = screw_head_travel_length_mm()
    head_radius = screw_head_diameter_mm() / 2 + SCREW_HEAD_CLEARANCE_MARGIN_MM
    with BuildPart() as cutter:
        with Locations((origin_x + travel / 2, center_y, center_z)):
            Cylinder(head_radius, travel, rotation=(0, 90, 0))
    return cutter.part


def _make_screw_clearance_hole_solid(
    *,
    cut_offset: float,
    radius: float,
) -> Part:
    screw_obj = _socket_head_cap_screw_instance(cut_offset=cut_offset, radius=radius)
    origin_x, center_y, center_z = screw_clearance_hole_location(
        cut_offset=cut_offset,
        radius=radius,
    )
    hole_depth = screw_hole_depth(cut_offset=cut_offset, radius=radius)
    hole_solid = _make_fastener_hole(
        hole_diameters=screw_obj.clearance_hole_diameters,
        fastener=screw_obj,
        countersink_profile=screw_obj.countersink_profile(CLEARANCE_FIT),
        depth=hole_depth,
        fit=CLEARANCE_FIT,
        counter_sunk=True,
    )
    positioned_hole = (Rot(*SCREW_AXIS_ROTATION) * hole_solid).translate(
        (origin_x, center_y, center_z)
    )
    head_travel = _make_screw_head_travel_cutter(
        origin_x=origin_x,
        center_y=center_y,
        center_z=center_z,
    )
    with BuildPart() as combined:
        add(positioned_hole)
        add(head_travel, mode=Mode.ADD)
    return combined.part


def _socket_head_cap_screw_instance(*, cut_offset: float, radius: float) -> SocketHeadCapScrew:
    length = screw_length_for_seat(cut_offset=cut_offset, radius=radius)
    return SocketHeadCapScrew(M3_SCREW_SIZE, length=length, simple=True)


def make_m3_screw_clearance_hole_cutter(*, cut_offset: float, radius: float) -> Part:
    """Clearance bore, counterbore, and head-travel pocket for the reference screw."""
    return _make_screw_clearance_hole_solid(cut_offset=cut_offset, radius=radius)


def subtract_m3_screw_clearance_hole(
    part: Part,
    *,
    cut_offset: float,
    radius: float,
) -> Part:
    """Cut the M3 screw clearance hole into an existing solid using bd_warehouse."""
    screw_obj = _socket_head_cap_screw_instance(cut_offset=cut_offset, radius=radius)
    origin_x, center_y, center_z = screw_clearance_hole_location(
        cut_offset=cut_offset,
        radius=radius,
    )
    hole_depth = screw_hole_depth(cut_offset=cut_offset, radius=radius)
    head_travel = _make_screw_head_travel_cutter(
        origin_x=origin_x,
        center_y=center_y,
        center_z=center_z,
    )

    with BuildPart() as cut:
        add(part)
        add(head_travel, mode=Mode.SUBTRACT)
        with Locations((origin_x, center_y, center_z)):
            ClearanceHole(
                screw_obj,
                fit=CLEARANCE_FIT,
                depth=hole_depth,
                counter_sunk=True,
                rotation=SCREW_AXIS_ROTATION,
            )

    return cut.part


@artifact(short_desc="ISO 4762 M3 socket head cap screw reference solid")
def m3_socket_head_cap_screw() -> Part:
    """Reference screw geometry from bd_warehouse for assembly fit checks."""
    return make_m3_socket_head_cap_screw()
