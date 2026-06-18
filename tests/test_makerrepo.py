from pathlib import Path

import pytest
import trimesh

from cad_tooling.export import export_artifacts
from cad.parts.sphere import make_sphere
from pytest_support import TEST_RENDER_SIZE_TOKEN, artifact_names, generator_names


@pytest.mark.unit
class TestArtifactDiscovery:
    def test_artifacts_discovered(self, registry):
        names = artifact_names(registry)

        assert "sphere" in names
        assert "sphere_with_nut" in names
        assert "m3_hex_nut" in names
        assert "m3_socket_head_cap_screw" in names

    def test_generators_discovered(self, registry):
        names = generator_names(registry)

        assert "sphere_generator" in names


@pytest.mark.integration
class TestArtifactExport:
    def test_artifact_export_step(self, tmp_path: Path, repo_root: Path):
        export_artifacts(tmp_path, "step", ("sphere",), root=repo_root)

        step_files = list(tmp_path.glob("*.step"))
        assert len(step_files) == 1
        assert step_files[0].stat().st_size > 0

    def test_artifact_export_stl(self, tmp_path: Path):
        stl_path = tmp_path / "sphere.stl"
        export_artifacts(stl_path, "stl", ("sphere",))

        mesh = trimesh.load_mesh(stl_path)
        expected = make_sphere()

        assert len(mesh.vertices) > 0
        assert mesh.volume == pytest.approx(expected.volume, rel=0.02)


@pytest.mark.integration
@pytest.mark.render
class TestReleaseIntegration:
    def test_release_export_includes_previews(self, release_artifacts: Path):
        """End-to-end guard: session release dir has STL + PNG previews at test resolution."""
        stl_paths = list(release_artifacts.glob("*.stl"))
        png_paths = list(release_artifacts.glob("*.png"))
        stl_names = {path.stem for path in stl_paths}

        assert stl_names == {"sphere", "sphere_with_nut"}
        assert "m3_hex_nut" not in stl_names
        assert len(png_paths) >= len(stl_paths)

        for stl_path in stl_paths:
            assert stl_path.exists() and stl_path.stat().st_size > 0
            artifact_pngs = [
                path
                for path in png_paths
                if path.name.startswith(f"{stl_path.stem}_") and TEST_RENDER_SIZE_TOKEN in path.name
            ]
            assert artifact_pngs, f"No preview PNGs found for {stl_path.name}"
            for png_path in artifact_pngs:
                assert png_path.exists() and png_path.stat().st_size > 1_000
                assert png_path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"
