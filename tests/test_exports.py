from pathlib import Path

import pytest
import trimesh
from build123d import import_step

from cad.export import export_part
from cad.parts.example_ocp_text import make_example_ocp_text


def test_stl_export(tmp_path: Path):
    part = make_example_ocp_text()
    export_part(part, "example_ocp_text", tmp_path)

    stl_path = tmp_path / "example_ocp_text.stl"
    step_path = tmp_path / "example_ocp_text.step"
    glb_path = tmp_path / "example_ocp_text.glb"

    assert stl_path.exists()
    assert stl_path.stat().st_size > 0
    assert step_path.exists()
    assert step_path.stat().st_size > 0
    assert glb_path.exists()
    assert glb_path.stat().st_size > 0

    mesh = trimesh.load_mesh(stl_path)
    assert mesh.volume > 0


def test_step_round_trip_preserves_volume(tmp_path: Path):
    part = make_example_ocp_text(font_size=16, depth=6)
    export_part(part, "round_trip_ocp_text", tmp_path)

    step_path = tmp_path / "round_trip_ocp_text.step"
    reimported = import_step(step_path)

    assert reimported.volume == pytest.approx(part.volume, rel=0.02)
