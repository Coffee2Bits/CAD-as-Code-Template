from pathlib import Path

import pytest
import trimesh

from cad_tooling.export import export_artifacts, export_release, list_artifacts, list_generators
from cad.parts.sphere import make_sphere

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_artifacts_discovered():
    names = {artifact.name for artifact in list_artifacts(REPO_ROOT)}

    assert "sphere" in names
    assert "sphere_with_nut" in names
    assert "m3_hex_nut" in names


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


def test_release_export_includes_previews(tmp_path: Path):
    paths = export_release(tmp_path, root=REPO_ROOT)
    stl_paths = [path for path in paths if path.suffix == ".stl"]
    png_paths = [path for path in paths if path.suffix == ".png"]
    stl_names = {path.stem for path in stl_paths}

    assert stl_names == {"sphere", "sphere_with_nut"}
    assert "m3_hex_nut" not in stl_names
    assert len(png_paths) >= len(stl_paths)

    for stl_path in stl_paths:
        assert stl_path.exists() and stl_path.stat().st_size > 0
        artifact_pngs = [path for path in png_paths if path.name.startswith(f"{stl_path.stem}_")]
        assert artifact_pngs, f"No preview PNGs found for {stl_path.name}"
        for png_path in artifact_pngs:
            assert png_path.exists() and png_path.stat().st_size > 5_000
            assert png_path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
