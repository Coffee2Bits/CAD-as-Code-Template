import pytest

from cad.parts.m3_hex_nut import (
    M3_HEX_NUT_SIZE,
    NUT_THICKNESS_MM,
    WIDTH_ACROSS_FLATS_MM,
    hex_margin_to_across_flats,
    hex_margin_to_profile_scale,
    make_m3_hex_nut,
    make_m3_hex_nut_for_pocket,
    make_m3_hex_nut_pocket_cutter,
    POCKET_HEX_ROTATION_DEG,
    positioned_m3_hex_nut_at_seat,
)


@pytest.mark.integration
def test_m3_hex_nut_is_valid():
    assert make_m3_hex_nut().is_valid


@pytest.mark.integration
def test_m3_hex_nut_width_across_flats():
    nut = make_m3_hex_nut()
    bbox = nut.bounding_box()

    assert bbox.size.Y == pytest.approx(WIDTH_ACROSS_FLATS_MM, abs=0.05)


@pytest.mark.integration
def test_m3_hex_nut_thickness():
    nut = make_m3_hex_nut()
    bbox = nut.bounding_box()

    assert bbox.size.Z == pytest.approx(NUT_THICKNESS_MM, abs=0.05)


@pytest.mark.integration
def test_m3_hex_nut_for_pocket_has_thickness_along_x():
    nut = make_m3_hex_nut_for_pocket()
    bbox = nut.bounding_box()

    assert bbox.size.X == pytest.approx(NUT_THICKNESS_MM, abs=0.05)
    assert bbox.size.Y == pytest.approx(WIDTH_ACROSS_FLATS_MM, abs=0.05)


@pytest.mark.unit
def test_m3_hex_nut_uses_bd_warehouse_size():
    assert M3_HEX_NUT_SIZE == "M3-0.5"


@pytest.mark.unit
def test_hex_margin_to_across_flats_adds_clearance_in_mm():
    base = 6.35
    assert hex_margin_to_across_flats(base_across_flats=base, hex_nut_margin=0.2) == pytest.approx(
        6.75
    )
    assert hex_margin_to_profile_scale(base_across_flats=base, hex_nut_margin=0.2) == pytest.approx(
        6.75 / 6.35
    )


@pytest.mark.unit
def test_pocket_hex_rotation_matches_reference_nut():
    assert POCKET_HEX_ROTATION_DEG == 30.0


@pytest.mark.integration
def test_pocket_cutter_is_hex_prism_not_scaled_nut():
    cut_offset = 1.5
    radius = 10.0
    reference = positioned_m3_hex_nut_at_seat(cut_offset=cut_offset, radius=radius)
    cutter = make_m3_hex_nut_pocket_cutter(
        cut_offset=cut_offset,
        radius=radius,
        hex_nut_margin=0.0,
    )

    hex_walls = [
        face for face in cutter.faces() if abs(face.normal_at().X) < 0.01 and face.area > 5
    ]
    assert len(hex_walls) == 6
    assert cutter.volume != pytest.approx(reference.volume, rel=0.01)


@pytest.mark.integration
def test_pocket_cutter_encloses_reference_nut_when_margin_increases():
    cut_offset = 1.5
    radius = 10.0
    reference = positioned_m3_hex_nut_at_seat(cut_offset=cut_offset, radius=radius)
    cutter = make_m3_hex_nut_pocket_cutter(
        cut_offset=cut_offset,
        radius=radius,
        hex_nut_margin=0.2,
    )

    assert (reference - cutter).volume == pytest.approx(0, abs=0.01)
    assert cutter.bounding_box().max.X == pytest.approx(reference.bounding_box().max.X, abs=0.01)


@pytest.mark.integration
def test_pocket_cutter_grows_with_margin_in_mm():
    cut_offset = 1.5
    radius = 10.0
    tight = make_m3_hex_nut_pocket_cutter(
        cut_offset=cut_offset,
        radius=radius,
        hex_nut_margin=0.0,
    )
    loose = make_m3_hex_nut_pocket_cutter(
        cut_offset=cut_offset,
        radius=radius,
        hex_nut_margin=0.5,
    )

    assert loose.bounding_box().max.X == pytest.approx(tight.bounding_box().max.X, abs=0.01)
    assert max(loose.bounding_box().size.Y, loose.bounding_box().size.Z) > max(
        tight.bounding_box().size.Y,
        tight.bounding_box().size.Z,
    )
