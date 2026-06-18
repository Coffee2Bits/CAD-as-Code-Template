import math

import pytest

from cad.parts.m3_hex_nut import hex_nut_pocket_seat, positioned_m3_hex_nut_at_seat
from cad.parts.m3_socket_head_cap_screw import (
    CLEARANCE_FIT,
    M3_SCREW_SIZE,
    SCREW_AXIS_ROTATION,
    SCREW_LENGTH_MM,
    make_m3_socket_head_cap_screw,
    make_m3_screw_clearance_hole_cutter,
    positioned_m3_screw_at_seat,
    screw_clearance_hole_origin_x,
    screw_entry_x,
    screw_head_height_mm,
    screw_head_outward_relief_mm,
    screw_hole_depth,
    screw_length_for_seat,
)


pytestmark = pytest.mark.integration


def test_m3_socket_head_cap_screw_is_valid():
    assert make_m3_socket_head_cap_screw().is_valid


def test_m3_socket_head_cap_screw_has_length_along_x():
    screw = make_m3_socket_head_cap_screw()
    bbox = screw.bounding_box()

    assert bbox.size.X == pytest.approx(SCREW_LENGTH_MM + screw_head_height_mm(), abs=0.05)
    assert bbox.size.Y == pytest.approx(bbox.size.Z, abs=0.05)


def test_m3_socket_head_cap_screw_uses_bd_warehouse_size():
    assert M3_SCREW_SIZE == "M3-0.5"
    assert CLEARANCE_FIT == "Close"


def test_positioned_screw_axis_passes_through_pocket_seat():
    cut_offset = 1.5
    radius = 10.0
    cut_x, center_y, center_z = hex_nut_pocket_seat(cut_offset=cut_offset, radius=radius)
    screw = positioned_m3_screw_at_seat(cut_offset=cut_offset, radius=radius)
    bbox = screw.bounding_box()

    assert bbox.min.X == pytest.approx(
        screw_entry_x(cut_offset=cut_offset, radius=radius), abs=0.05
    )
    assert bbox.max.X == pytest.approx(cut_x, abs=0.05)
    assert (bbox.min.Y + bbox.max.Y) / 2 == pytest.approx(center_y, abs=0.05)
    assert (bbox.min.Z + bbox.max.Z) / 2 == pytest.approx(center_z, abs=0.05)


def test_positioned_screw_tip_flush_with_nut_opening():
    cut_offset = 1.5
    radius = 10.0
    cut_x, _, _ = hex_nut_pocket_seat(cut_offset=cut_offset, radius=radius)
    screw = positioned_m3_screw_at_seat(cut_offset=cut_offset, radius=radius)
    nut = positioned_m3_hex_nut_at_seat(cut_offset=cut_offset, radius=radius)

    assert screw.bounding_box().max.X == pytest.approx(cut_x, abs=0.05)
    assert screw.bounding_box().max.X == pytest.approx(nut.bounding_box().max.X, abs=0.05)


def test_screw_length_matches_seat_span():
    cut_offset = 1.5
    radius = 10.0
    cut_x, _, _ = hex_nut_pocket_seat(cut_offset=cut_offset, radius=radius)
    entry_x = screw_entry_x(cut_offset=cut_offset, radius=radius)

    assert screw_length_for_seat(cut_offset=cut_offset, radius=radius) == pytest.approx(
        cut_x - entry_x - screw_head_height_mm(),
        abs=0.01,
    )


def test_clearance_hole_cutter_extends_outward_for_head_travel():
    cut_offset = 1.5
    radius = 10.0
    entry_x = screw_entry_x(cut_offset=cut_offset, radius=radius)
    origin_x = screw_clearance_hole_origin_x(cut_offset=cut_offset, radius=radius)
    cutter = make_m3_screw_clearance_hole_cutter(cut_offset=cut_offset, radius=radius)

    assert origin_x == pytest.approx(entry_x - screw_head_outward_relief_mm(), abs=0.01)
    assert cutter.bounding_box().min.X == pytest.approx(origin_x, abs=0.05)


def test_clearance_hole_depth_spans_to_nut_opening():
    cut_offset = 1.5
    radius = 10.0
    cut_x, _, _ = hex_nut_pocket_seat(cut_offset=cut_offset, radius=radius)
    origin_x = screw_clearance_hole_origin_x(cut_offset=cut_offset, radius=radius)
    cutter = make_m3_screw_clearance_hole_cutter(cut_offset=cut_offset, radius=radius)
    expected_depth = screw_hole_depth(cut_offset=cut_offset, radius=radius)

    assert expected_depth == pytest.approx(cut_x - origin_x, abs=0.01)
    assert cutter.bounding_box().max.X >= cut_x


def test_reference_screw_passes_through_clearance_hole_in_sphere():
    from cad.parts.sphere import northeast_quadrant_cut_offset
    from pytest_support import cached_make_sphere

    radius = 10
    cut_offset = northeast_quadrant_cut_offset(radius=radius)
    sphere = cached_make_sphere(hex_nut_margin=0.2, radius=radius)
    screw = positioned_m3_screw_at_seat(cut_offset=cut_offset, radius=radius)

    overlap = sphere.intersect(screw)
    assert overlap.volume == pytest.approx(0, abs=0.5)

    _, center_y, center_z = hex_nut_pocket_seat(cut_offset=cut_offset, radius=radius)
    bbox = screw.bounding_box()
    assert (bbox.min.Y + bbox.max.Y) / 2 == pytest.approx(center_y, abs=0.05)
    assert (bbox.min.Z + bbox.max.Z) / 2 == pytest.approx(center_z, abs=0.05)
    assert SCREW_AXIS_ROTATION == (0, -90, 0)
    assert math.isclose(bbox.size.Y, bbox.size.Z, rel_tol=0.02)


def test_screw_can_retract_outward_without_sphere_overlap():
    from cad.parts.sphere import northeast_quadrant_cut_offset
    from pytest_support import cached_make_sphere

    radius = 10
    cut_offset = northeast_quadrant_cut_offset(radius=radius)
    sphere = cached_make_sphere(hex_nut_margin=0.2, radius=radius)
    screw = positioned_m3_screw_at_seat(cut_offset=cut_offset, radius=radius)
    retracted = screw.translate((-screw_head_outward_relief_mm(), 0, 0))

    overlap = sphere.intersect(retracted)
    assert overlap.volume == pytest.approx(0, abs=0.5)
