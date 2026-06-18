import pytest

from cad.parts.sphere_tripod_support import (
    DEFAULT_INNER_CLEARANCE_MM,
    DEFAULT_LEG_DIAMETER_MM,
    DEFAULT_LEG_LENGTH_MM,
    DEFAULT_LEG_SPLAY_DEG,
    DEFAULT_SEAT_HEIGHT_MM,
    DEFAULT_SEAT_YAW_DEG,
    DEFAULT_WALL_THICKNESS_MM,
    PART_COLOR,
    _leg_attach_xy,
    foot_plane_z,
    make_sphere_tripod_support,
    sphere_horiz_radius_at_z,
    sphere_seat_sixth_line_z,
)

pytestmark = pytest.mark.integration


class TestSphereTripodSupportGeometry:
    @pytest.fixture(scope="class")
    def default_support(self):
        return make_sphere_tripod_support(sphere_radius=10)

    def test_support_is_valid(self, default_support):
        assert default_support.is_valid

    def test_seat_sized_for_sphere_sixth_line(self, default_support):
        sphere_radius = 10
        seat_z = sphere_seat_sixth_line_z(sphere_radius)
        seat_bottom = seat_z - DEFAULT_SEAT_HEIGHT_MM
        bbox = default_support.bounding_box()
        assert bbox.max.Z == pytest.approx(seat_z, abs=0.1)
        expected_ground = foot_plane_z(
            seat_bottom,
            DEFAULT_LEG_LENGTH_MM,
            DEFAULT_LEG_SPLAY_DEG,
            leg_radius=DEFAULT_LEG_DIAMETER_MM / 2,
        )
        assert bbox.min.Z == pytest.approx(expected_ground, abs=0.1)

    def test_feet_trimmed_to_common_ground_plane(self, default_support):
        sphere_radius = 10
        seat_z = sphere_seat_sixth_line_z(sphere_radius)
        seat_bottom = seat_z - DEFAULT_SEAT_HEIGHT_MM
        expected_ground = foot_plane_z(
            seat_bottom,
            DEFAULT_LEG_LENGTH_MM,
            DEFAULT_LEG_SPLAY_DEG,
            leg_radius=DEFAULT_LEG_DIAMETER_MM / 2,
        )
        bbox = default_support.bounding_box()
        assert bbox.min.Z == pytest.approx(expected_ground, abs=0.05)

    def test_legs_fuse_with_seat(self, default_support):
        assert len(list(default_support.solids())) == 1

    def test_rear_leg_on_y_axis_and_front_legs_frame_text(self):
        sphere_radius = 10
        seat_z = sphere_seat_sixth_line_z(sphere_radius)
        outer_r = (
            sphere_horiz_radius_at_z(sphere_radius, seat_z)
            + DEFAULT_INNER_CLEARANCE_MM
            + DEFAULT_WALL_THICKNESS_MM
        )
        rear_x, rear_y = _leg_attach_xy(0, outer_r, seat_yaw_deg=DEFAULT_SEAT_YAW_DEG)
        left_x, left_y = _leg_attach_xy(1, outer_r, seat_yaw_deg=DEFAULT_SEAT_YAW_DEG)
        right_x, right_y = _leg_attach_xy(2, outer_r, seat_yaw_deg=DEFAULT_SEAT_YAW_DEG)

        assert rear_x == pytest.approx(0.0, abs=0.05)
        assert rear_y > 0
        assert left_x < 0 and left_y < 0
        assert right_x > 0 and right_y < 0

    def test_legs_splay_outward_from_center(self, default_support):
        bbox = default_support.bounding_box()
        seat_z = sphere_seat_sixth_line_z(10)
        expected_inner = sphere_horiz_radius_at_z(10, seat_z)
        expected_outer = expected_inner + DEFAULT_WALL_THICKNESS_MM + 0.2
        xy_extent = max(bbox.size.X, bbox.size.Y)
        assert xy_extent / 2 > expected_outer + 1.0

    def test_support_has_part_color(self, default_support):
        assert tuple(default_support.color)[:3] == tuple(PART_COLOR)[:3]

    def test_default_dimensions(self):
        assert DEFAULT_LEG_LENGTH_MM == 12.0
        assert DEFAULT_SEAT_HEIGHT_MM == 2.5
        assert DEFAULT_WALL_THICKNESS_MM == 1.5
        assert DEFAULT_LEG_DIAMETER_MM == 2.5
        assert DEFAULT_SEAT_YAW_DEG == 90.0

    def test_seat_sixth_line_z(self):
        assert sphere_seat_sixth_line_z(10) == pytest.approx(-20 / 3, abs=0.01)
