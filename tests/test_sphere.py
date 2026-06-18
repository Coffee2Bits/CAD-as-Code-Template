import math

import pytest

from cad.parts.sphere import EMBOSSED_TEXT_COLOR
from pytest_support import cached_make_sphere

pytestmark = pytest.mark.integration


class TestSphereGeometry:
    @pytest.fixture(scope="class")
    def default_sphere(self):
        return cached_make_sphere()

    @pytest.fixture(scope="class")
    def radius_ten_sphere(self):
        return cached_make_sphere(radius=10)

    @pytest.fixture(scope="class")
    def radius_eight_sphere(self):
        return cached_make_sphere(radius=8)

    def test_sphere_is_valid(self, default_sphere):
        assert default_sphere.is_valid

    def test_sphere_radius_matches_bounding_box(self, radius_ten_sphere):
        bbox = radius_ten_sphere.bounding_box()

        assert bbox.size.X == pytest.approx(20, abs=0.01)
        assert bbox.size.Z == pytest.approx(20, abs=0.01)
        assert bbox.min.Y == pytest.approx(-10.52, abs=0.05)

    def test_sphere_volume_below_full_sphere_with_emboss(self, radius_eight_sphere):
        radius = 8
        full_sphere_volume = (4 / 3) * math.pi * radius**3

        assert radius_eight_sphere.volume < full_sphere_volume

    def test_sphere_has_embossed_text_faces(self, default_sphere):
        assert len(default_sphere.faces()) > 1

    def test_embossed_text_is_dark_blue(self, default_sphere):
        embossed_text = default_sphere.children[1]
        assert embossed_text.label == "embossed_text"
        assert tuple(embossed_text.color)[:3] == tuple(EMBOSSED_TEXT_COLOR)[:3]
