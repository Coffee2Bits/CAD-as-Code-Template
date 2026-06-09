from pathlib import Path

import pytest
import trimesh

from cad.export import export_artifacts, list_artifacts, list_generators
from cad.parts.sphere import make_sphere

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_artifacts_discovered():
    names = {artifact.name for artifact in list_artifacts(REPO_ROOT)}

    assert "sphere" in names


def test_generators_discovered():
    names = {generator.name for generator in list_generators(REPO_ROOT)}

    assert "sphere_generator" in names


def test_artifact_export_step(tmp_path: Path):
    export_artifacts(tmp_path, "step", ("sphere",), root=REPO_ROOT)

    step_files = list(tmp_path.glob("*.step"))
    assert len(step_files) == 1
    assert step_files[0].stat().st_size > 0


def test_artifact_export_stl(tmp_path: Path):
    stl_path = tmp_path / "sphere.stl"
    export_artifacts(stl_path, "stl", ("sphere",), root=REPO_ROOT)

    mesh = trimesh.load_mesh(stl_path)
    expected = make_sphere()

    assert len(mesh.vertices) > 0
    assert mesh.volume == pytest.approx(expected.volume, rel=0.02)
