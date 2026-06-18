"""Three-legged hollow-cylinder support for the demo sphere."""

import math

from build123d import (
    Align,
    Box,
    BuildPart,
    Color,
    Cylinder,
    Locations,
    Mode,
    Part,
    Pos,
    Rot,
    add,
)
from mr import artifact, customizable
from pydantic import BaseModel, Field

from cad_tooling.render_decorator import render

PART_COLOR = Color(0.82, 0.33, 0.14)

DEFAULT_LEG_LENGTH_MM = 12.0
DEFAULT_SEAT_HEIGHT_MM = 2.5
DEFAULT_WALL_THICKNESS_MM = 1.5
DEFAULT_INNER_CLEARANCE_MM = 0.2
DEFAULT_LEG_DIAMETER_MM = 2.5
DEFAULT_LEG_SPLAY_DEG = 18.0
# Rotate seat/legs so the rear leg is on +Y (x = 0) and the front pair frame -Y text.
DEFAULT_SEAT_YAW_DEG = 90.0


def sphere_seat_sixth_line_z(sphere_radius: float) -> float:
    """Z of the bottom-sixth circle (1/6 up from the sphere bottom)."""
    return -sphere_radius + (2 * sphere_radius) / 6


def sphere_horiz_radius_at_z(sphere_radius: float, z: float) -> float:
    """Horizontal cross-section radius of a centered sphere at Z."""
    return math.sqrt(max(sphere_radius**2 - z**2, 0.0))


def foot_plane_z(
    seat_bottom_z: float,
    leg_length: float,
    leg_splay_deg: float,
    *,
    leg_radius: float,
) -> float:
    """Ground plane Z where splayed legs are trimmed to flat feet."""
    axis_tip_z = seat_bottom_z + leg_length * (-math.cos(math.radians(leg_splay_deg)))
    return axis_tip_z + leg_radius * (1.0 + math.sin(math.radians(leg_splay_deg)))


def _leg_rotation(azimuth_deg: float, splay_deg: float):
    """Orient a +Z cylinder along the splayed leg direction."""
    return Rot(0, 0, azimuth_deg) * Rot(0, 180 - splay_deg, 0)


def _leg_direction(azimuth_deg: float, splay_deg: float) -> tuple[float, float, float]:
    """Unit vector for a leg pointing down and away from center."""
    azimuth = math.radians(azimuth_deg)
    splay = math.radians(splay_deg)
    return (
        math.cos(azimuth) * math.sin(splay),
        math.sin(azimuth) * math.sin(splay),
        -math.cos(splay),
    )


def _leg_attach_xy(
    leg_index: int,
    outer_r: float,
    *,
    seat_yaw_deg: float,
) -> tuple[float, float]:
    """Return the seat-rim attachment point for a leg index."""
    azimuth = math.radians(leg_index * 120 + seat_yaw_deg)
    return outer_r * math.cos(azimuth), outer_r * math.sin(azimuth)


def _subtract_below_plane(part: Part, *, plane_z: float, span: float) -> Part:
    """Trim geometry below a horizontal plane so angled legs stand flat."""
    with BuildPart() as cutter:
        add(part)
        with Locations((0, 0, plane_z - span)):
            Box(
                span * 2,
                span * 2,
                span,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
    return cutter.part


def _subtract_interior_bore(
    part: Part,
    *,
    inner_r: float,
    center_z: float,
    height: float,
) -> Part:
    """Remove leg material that clips through the hollow seat interior."""
    with BuildPart() as cutter:
        add(part)
        with Locations((0, 0, center_z)):
            Cylinder(
                inner_r,
                height,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                mode=Mode.SUBTRACT,
            )
    return cutter.part


def _clip_above_seat(part: Part, *, seat_z: float, span: float) -> Part:
    """Keep leg tops inside the seat ring by trimming above the seat rim."""
    with BuildPart() as cutter:
        add(part)
        with Locations((0, 0, seat_z)):
            Box(
                span * 2,
                span * 2,
                span,
                align=(Align.CENTER, Align.CENTER, Align.MIN),
                mode=Mode.SUBTRACT,
            )
    return cutter.part


def make_sphere_tripod_support(
    sphere_radius: float = 10.0,
    *,
    seat_height: float = DEFAULT_SEAT_HEIGHT_MM,
    wall_thickness: float = DEFAULT_WALL_THICKNESS_MM,
    inner_clearance: float = DEFAULT_INNER_CLEARANCE_MM,
    leg_length: float = DEFAULT_LEG_LENGTH_MM,
    leg_diameter: float = DEFAULT_LEG_DIAMETER_MM,
    leg_splay_deg: float = DEFAULT_LEG_SPLAY_DEG,
    seat_yaw_deg: float = DEFAULT_SEAT_YAW_DEG,
) -> Part:
    """Build a hollow seat and three splayed legs sized for a centered sphere."""
    seat_z = sphere_seat_sixth_line_z(sphere_radius)
    inner_r = sphere_horiz_radius_at_z(sphere_radius, seat_z) + inner_clearance
    outer_r = inner_r + wall_thickness
    seat_bottom_z = seat_z - seat_height
    seat_center_z = (seat_z + seat_bottom_z) / 2
    leg_radius = leg_diameter / 2
    trim_span = sphere_radius * 10

    with BuildPart() as builder:
        with Locations((0, 0, seat_center_z)):
            Cylinder(
                outer_r,
                seat_height,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
            )
            Cylinder(
                inner_r,
                seat_height + 0.2,
                align=(Align.CENTER, Align.CENTER, Align.CENTER),
                mode=Mode.SUBTRACT,
            )

        for leg_index in range(3):
            azimuth_deg = leg_index * 120 + seat_yaw_deg
            attach_x, attach_y = _leg_attach_xy(
                leg_index,
                outer_r,
                seat_yaw_deg=seat_yaw_deg,
            )
            leg_dx, leg_dy, leg_dz = _leg_direction(azimuth_deg, leg_splay_deg)
            start_x = attach_x - leg_dx * seat_height
            start_y = attach_y - leg_dy * seat_height
            start_z = seat_bottom_z - leg_dz * seat_height
            rotation = _leg_rotation(azimuth_deg, leg_splay_deg)
            with Locations(Pos(start_x, start_y, start_z) * rotation):
                Cylinder(
                    leg_radius,
                    leg_length + seat_height,
                    align=(Align.CENTER, Align.CENTER, Align.MIN),
                )

    part = builder.part
    part = _subtract_interior_bore(
        part,
        inner_r=inner_r,
        center_z=seat_center_z,
        height=seat_height + leg_radius * 4,
    )
    part = _clip_above_seat(part, seat_z=seat_z, span=trim_span)
    ground_z = foot_plane_z(
        seat_bottom_z,
        leg_length,
        leg_splay_deg,
        leg_radius=leg_radius,
    )
    part = _subtract_below_plane(part, plane_z=ground_z, span=trim_span)
    part.color = PART_COLOR
    return part


@artifact(short_desc="Three-legged hollow seat for the demo sphere")
@render(
    renders=[
        {"camera": "front", "width": 800, "height": 600},
        {"camera": "top", "width": 800, "height": 600},
        {"camera": "iso", "width": 800, "height": 600},
    ]
)
def sphere_tripod_support() -> Part:
    """Default tripod support published as a MakerRepo artifact."""
    return make_sphere_tripod_support()


class SphereTripodSupportParameters(BaseModel):
    sphere_radius: float = Field(default=10, gt=0, description="Target sphere radius (mm)")
    seat_height: float = Field(default=DEFAULT_SEAT_HEIGHT_MM, gt=0)
    wall_thickness: float = Field(default=DEFAULT_WALL_THICKNESS_MM, gt=0)
    inner_clearance: float = Field(default=DEFAULT_INNER_CLEARANCE_MM, ge=0)
    leg_length: float = Field(default=DEFAULT_LEG_LENGTH_MM, gt=0)
    leg_diameter: float = Field(default=DEFAULT_LEG_DIAMETER_MM, gt=0)
    leg_splay_deg: float = Field(default=DEFAULT_LEG_SPLAY_DEG, gt=0, lt=90)
    seat_yaw_deg: float = Field(default=DEFAULT_SEAT_YAW_DEG)


@customizable(sample_parameters=SphereTripodSupportParameters())
def sphere_tripod_support_generator(
    parameters: SphereTripodSupportParameters,
) -> Part:
    """Parametric tripod support — customize via MakerRepo generators or CLI."""
    return make_sphere_tripod_support(**parameters.model_dump())
