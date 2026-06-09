import pytest

from cad.parts.example_ocp_text import make_example_ocp_text


def test_ocp_text_is_valid():
    part = make_example_ocp_text()
    assert part.is_valid


def test_ocp_text_depth_matches_bounding_box():
    part = make_example_ocp_text(depth=5)
    bbox = part.bounding_box()

    assert bbox.size.Z == pytest.approx(5, abs=0.01)


def test_ocp_text_depth_scales_with_parameter():
    part = make_example_ocp_text(depth=8)
    bbox = part.bounding_box()

    assert bbox.size.Z == pytest.approx(8, abs=0.01)


def test_ocp_text_volume_is_positive():
    part = make_example_ocp_text()
    assert part.volume > 0


def test_ocp_text_larger_font_increases_bounding_box():
    small = make_example_ocp_text(font_size=12)
    large = make_example_ocp_text(font_size=24)

    small_bbox = small.bounding_box()
    large_bbox = large.bounding_box()

    assert large_bbox.size.X > small_bbox.size.X
    assert large_bbox.size.Y > small_bbox.size.Y
