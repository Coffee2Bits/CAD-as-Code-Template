import pytest

from cad.parts.m3_hex_nut import (
    NUT_THICKNESS_MM,
    WIDTH_ACROSS_FLATS_MM,
    make_m3_hex_nut_pocket_cutter,
    positioned_m3_hex_nut_at_seat,
)
from cad.parts.sphere import (
    largest_x_cut_face,
    northeast_quadrant_cut_offset,
    positioned_m3_hex_nut_reference,
)
from pytest_support import cached_make_sphere


@pytest.mark.integration
def test_hex_pocket_profile_aligned_with_reference_nut():
    radius = 10
    cut_offset = northeast_quadrant_cut_offset(radius=radius)
    reference = positioned_m3_hex_nut_at_seat(cut_offset=cut_offset, radius=radius)
    cutter = make_m3_hex_nut_pocket_cutter(
        cut_offset=cut_offset,
        radius=radius,
        hex_nut_margin=0.0,
    )

    outside_reference = reference - cutter
    assert outside_reference.volume == pytest.approx(0, abs=0.01)

    hex_walls = [
        face for face in cutter.faces() if abs(face.normal_at().X) < 0.01 and face.area > 5
    ]
    assert len(hex_walls) == 6


@pytest.mark.integration
def test_pocket_cutter_uses_same_seat_as_reference_nut():
    radius = 10
    cut_offset = northeast_quadrant_cut_offset(radius=radius)
    reference = positioned_m3_hex_nut_at_seat(cut_offset=cut_offset, radius=radius)
    cutter = make_m3_hex_nut_pocket_cutter(
        cut_offset=cut_offset,
        radius=radius,
        hex_nut_margin=0.0,
    )

    assert cutter.bounding_box().max.X == pytest.approx(reference.bounding_box().max.X, abs=0.01)


@pytest.mark.unit
def test_sphere_northeast_cut_offset_is_positive():
    offset = northeast_quadrant_cut_offset(radius=10)
    assert offset > 0


@pytest.mark.integration
class TestSphereHexNutPocket:
    RADIUS = 10

    @pytest.fixture(scope="class")
    def cut_offset(self):
        return northeast_quadrant_cut_offset(radius=self.RADIUS)

    @pytest.fixture(scope="class")
    def sphere_margins(self):
        return {
            "tight": cached_make_sphere(hex_nut_margin=0, radius=self.RADIUS),
            "loose": cached_make_sphere(hex_nut_margin=0.5, radius=self.RADIUS),
            "default": cached_make_sphere(hex_nut_margin=0.2, radius=self.RADIUS),
        }

    @pytest.fixture(scope="class")
    def sphere_default(self, sphere_margins):
        return sphere_margins["default"]

    def test_sphere_with_hex_nut_pocket_is_valid(self, sphere_default):
        assert sphere_default.is_valid

    def test_sphere_hex_nut_pocket_reduces_volume(self, sphere_margins):
        assert sphere_margins["default"].volume < sphere_margins["tight"].volume

    def test_sphere_hex_nut_margin_expands_pocket_volume(self, sphere_margins):
        assert sphere_margins["loose"].volume < sphere_margins["tight"].volume

    def test_sphere_hex_nut_pocket_depth_matches_nut_thickness(self, sphere_default):
        part = sphere_default
        cut_face = largest_x_cut_face(part)
        cut_x = cut_face.bounding_box().min.X

        pocket_floors = []
        for face in part.faces():
            normal = face.normal_at()
            if normal.X > 0.99 and abs(normal.Y) < 0.01 and abs(normal.Z) < 0.01:
                floor_x = face.bounding_box().min.X
                if floor_x < cut_x - 1:
                    pocket_floors.append(floor_x)

        assert pocket_floors, "expected a planar pocket floor inside the sphere"
        assert cut_x - max(pocket_floors) == pytest.approx(NUT_THICKNESS_MM, abs=0.1)

    def test_reference_m3_hex_nut_fits_flush_in_pocket(self, sphere_default, cut_offset):
        part = sphere_default
        positioned_nut = positioned_m3_hex_nut_at_seat(cut_offset=cut_offset, radius=self.RADIUS)

        overlap = part.intersect(positioned_nut)
        assert overlap.volume == pytest.approx(0, abs=0.5)

        assert positioned_nut.bounding_box().max.X == pytest.approx(cut_offset, abs=0.05)
        assert positioned_nut.bounding_box().size.X == pytest.approx(NUT_THICKNESS_MM, abs=0.05)
        assert positioned_nut.bounding_box().size.Y == pytest.approx(
            WIDTH_ACROSS_FLATS_MM,
            abs=0.15,
        )

    def test_positioned_m3_hex_nut_reference_uses_shared_seat(self, sphere_default, cut_offset):
        part = sphere_default
        reference = positioned_m3_hex_nut_reference(part, radius=self.RADIUS)
        expected = positioned_m3_hex_nut_at_seat(cut_offset=cut_offset, radius=self.RADIUS)

        assert reference.bounding_box().min == pytest.approx(expected.bounding_box().min, abs=0.05)
        assert reference.bounding_box().max == pytest.approx(expected.bounding_box().max, abs=0.05)
