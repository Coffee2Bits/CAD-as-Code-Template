from pathlib import Path

import pytest
import trimesh
from build123d import import_step

from cad_tooling.export import export_part
from pytest_support import cached_make_sphere

pytestmark = pytest.mark.integration


class TestAdHocExport:
    def test_stl_export(self, tmp_path: Path):
        part = cached_make_sphere()
        export_part(part, "sphere", tmp_path)

        stl_path = tmp_path / "sphere.stl"
        step_path = tmp_path / "sphere.step"
        glb_path = tmp_path / "sphere.glb"

        assert stl_path.exists()
        assert stl_path.stat().st_size > 0
        assert step_path.exists()
        assert step_path.stat().st_size > 0
        assert glb_path.exists()
        assert glb_path.stat().st_size > 0

        mesh = trimesh.load_mesh(stl_path)
        assert mesh.volume > 0

    def test_step_round_trip_preserves_volume(self, tmp_path: Path):
        part = cached_make_sphere(radius=12)
        export_part(part, "round_trip_sphere", tmp_path)

        step_path = tmp_path / "round_trip_sphere.step"
        reimported = import_step(step_path)

        assert reimported.volume == pytest.approx(part.volume, rel=0.02)
