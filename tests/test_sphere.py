import math

import pytest

from cad.parts.sphere import make_sphere


def test_sphere_is_valid():
    part = make_sphere()
    assert part.is_valid


def test_sphere_radius_matches_bounding_box():
    part = make_sphere(radius=10)
    bbox = part.bounding_box()

    assert bbox.size.X == pytest.approx(20, abs=0.01)
    assert bbox.size.Z == pytest.approx(20, abs=0.01)
    assert bbox.min.Y == pytest.approx(-10.52, abs=0.05)


def test_sphere_volume_exceeds_base_sphere():
    radius = 8
    part = make_sphere(radius=radius)
    base_volume = (4 / 3) * math.pi * radius**3

    assert part.volume > base_volume


def test_sphere_has_embossed_text_faces():
    part = make_sphere()
    assert len(part.faces()) > 1
