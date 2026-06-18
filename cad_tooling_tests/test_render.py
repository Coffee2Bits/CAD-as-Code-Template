from pathlib import Path
from unittest.mock import patch
import shutil

import pytest

from cad_tooling.release_notes import (
    ReleaseAsset,
    RenderPreview,
    collect_release_assets,
    release_download_url,
    render_release_body,
)
from cad_tooling.render import CAMERA_PRESETS, _main, load_viewer_script, render_input, render_stl
from pytest_support import (
    TEST_RENDER_OVERRIDES,
    TEST_RENDER_SIZE_TOKEN,
    artifacts_list,
)


@pytest.mark.unit
def test_release_download_url():
    url = release_download_url("acme/widgets", "v1.2.3", "sphere.stl")
    assert url == "https://github.com/acme/widgets/releases/download/v1.2.3/sphere.stl"


@pytest.mark.unit
def test_render_release_body_lists_artifacts_with_previews(registry):
    artifact = next(item for item in artifacts_list(registry) if item.name == "sphere")
    assets = [
        ReleaseAsset.from_png_paths(
            artifact,
            Path("sphere.stl"),
            (
                Path("sphere_front_800x600.png"),
                Path("sphere_iso_800x600.png"),
            ),
        )
    ]

    body = render_release_body("acme/cad-template", "v0.0.1", assets)

    assert "# Release artifacts" in body
    assert "## sphere" in body
    assert "Demo sphere for workspace smoke tests" in body
    assert '<p align="center">' in body
    assert (
        'src="https://github.com/acme/cad-template/releases/download/v0.0.1/sphere_front_800x600.png"'
        in body
    )
    assert (
        'src="https://github.com/acme/cad-template/releases/download/v0.0.1/sphere_iso_800x600.png"'
        in body
    )
    assert (
        "- [front (800×600)]"
        "(https://github.com/acme/cad-template/releases/download/v0.0.1/sphere_front_800x600.png)"
        in body
    )
    assert (
        "- [iso (800×600)]"
        "(https://github.com/acme/cad-template/releases/download/v0.0.1/sphere_iso_800x600.png)"
        in body
    )
    assert (
        "[sphere.stl](https://github.com/acme/cad-template/releases/download/v0.0.1/sphere.stl)"
        in body
    )


@pytest.mark.unit
def test_render_release_body_sorts_cover_artifact_first(registry):
    artifact_a = next(item for item in artifacts_list(registry) if item.name == "sphere")

    class FakeArtifact:
        name = "alpha"
        cover = False
        short_desc = None
        desc = None

    class CoverArtifact:
        name = "cover"
        cover = True
        short_desc = "Cover assembly"
        desc = None

    assets = [
        ReleaseAsset(
            FakeArtifact(),
            Path("alpha.stl"),
            (RenderPreview("alpha iso 800x600", Path("alpha_iso_800x600.png")),),
        ),
        ReleaseAsset.from_png_paths(
            artifact_a,
            Path("sphere.stl"),
            (Path("sphere_front_800x600.png"), Path("sphere_iso_800x600.png")),
        ),
        ReleaseAsset(
            CoverArtifact(),
            Path("cover.stl"),
            (RenderPreview("front (800×600)", Path("cover_front_800x600.png")),),
        ),
    ]
    body = render_release_body("acme/repo", "v1.0.0", assets)
    assert body.index("## cover") < body.index("## alpha")
    assert body.index("## cover") < body.index("## sphere")


@pytest.mark.unit
def test_camera_presets_cover_all_config_choices():
    from cad_tooling.render_config import CAMERA_PRESET_CHOICES

    assert set(CAMERA_PRESET_CHOICES) == set(CAMERA_PRESETS.keys())


@pytest.mark.integration
class TestCollectReleaseAssets:
    @pytest.fixture(scope="class")
    def sphere_stl_export(self, tmp_path_factory, repo_root: Path) -> Path:
        from cad_tooling.export import export_artifacts

        out = tmp_path_factory.mktemp("sphere_stl_export")
        export_artifacts(out, "stl", ("sphere",), root=repo_root)
        return out

    @pytest.fixture
    def sphere_stl_workdir(self, sphere_stl_export: Path, tmp_path: Path) -> Path:
        shutil.copytree(sphere_stl_export, tmp_path, dirs_exist_ok=True)
        return tmp_path

    def test_collect_release_assets(self, release_artifacts: Path, repo_root: Path):
        assets = collect_release_assets(
            release_artifacts,
            root=repo_root,
            render_overrides=TEST_RENDER_OVERRIDES,
        )
        assert len(assets) >= 1
        assert any(asset.artifact.name == "sphere" for asset in assets)

    def test_collect_release_assets_can_scope_to_one_artifact(
        self, sphere_stl_workdir: Path, repo_root: Path
    ):
        (sphere_stl_workdir / "sphere.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        assets = collect_release_assets(sphere_stl_workdir, root=repo_root, names=("sphere",))
        assert [asset.artifact.name for asset in assets] == ["sphere"]

    def test_collect_release_assets_missing_stl(self, sphere_stl_workdir: Path, repo_root: Path):
        (sphere_stl_workdir / "sphere.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        (sphere_stl_workdir / "sphere.stl").unlink()
        with pytest.raises(FileNotFoundError, match="Missing release STL"):
            collect_release_assets(sphere_stl_workdir, root=repo_root, names=("sphere",))

    def test_collect_release_assets_missing_png(self, sphere_stl_workdir: Path, repo_root: Path):
        with pytest.raises(FileNotFoundError, match="Missing release preview"):
            collect_release_assets(sphere_stl_workdir, root=repo_root, names=("sphere",))

    def test_collect_release_assets_accepts_legacy_png_name(
        self, sphere_stl_workdir: Path, repo_root: Path
    ):
        (sphere_stl_workdir / "sphere.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        assets = collect_release_assets(sphere_stl_workdir, root=repo_root, names=("sphere",))
        sphere_asset = next(asset for asset in assets if asset.artifact.name == "sphere")
        assert sphere_asset.png_path.name == "sphere.png"


@pytest.mark.integration
@pytest.mark.render
class TestReleaseRender:
    def test_render_stl_writes_png(self, release_artifacts: Path, tmp_path: Path):
        stl_path = release_artifacts / "sphere.stl"
        png_path = tmp_path / "custom.png"
        render_stl(stl_path, png_path)
        assert png_path.exists()
        assert png_path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

    def test_lighting_presets_change_render_brightness(
        self, release_artifacts: Path, tmp_path: Path
    ):
        import numpy as np
        from PIL import Image

        from cad_tooling.render_config import LightingConfig, RenderConfig

        stl_path = release_artifacts / "sphere.stl"

        def _face_mean_luma(png_path: Path) -> float:
            pixels = np.array(Image.open(png_path).convert("RGB"), dtype=float)
            mask = pixels.mean(axis=2) > 35
            return float(pixels[mask].mean())

        dark_config = RenderConfig(
            lighting=LightingConfig.model_validate(
                {
                    "preset": "default",
                    "intensity": 0.35,
                    "ambient": 0.08,
                    "headlight": 0.35,
                    "fill": 0.15,
                }
            )
        )
        bright_config = RenderConfig(
            lighting=LightingConfig.model_validate({"preset": "bright", "intensity": 1.5})
        )

        dark_png = tmp_path / "dark.png"
        bright_png = tmp_path / "bright.png"
        render_stl(stl_path, dark_png, config=dark_config)
        render_stl(stl_path, bright_png, config=bright_config)

        dark_luma = _face_mean_luma(dark_png)
        bright_luma = _face_mean_luma(bright_png)
        assert bright_luma > dark_luma
        assert bright_luma - dark_luma > 12

    def test_render_input_artifact_uses_python_shape_not_stl(
        self, release_artifacts: Path, tmp_path: Path, repo_root: Path
    ):
        from cad_tooling.render import _build_artifact_shape, _colored_solids, render_input

        stl_path = release_artifacts / "sphere_with_nut.stl"
        written = render_input(
            stl_path,
            tmp_path / "previews",
            artifact_name="sphere_with_nut",
            root=repo_root,
        )
        assert written
        shape = _build_artifact_shape("sphere_with_nut", root=repo_root)
        assert len(_colored_solids(shape, (0.31, 0.63, 1.0))) == 3

    def test_render_cli(self, release_artifacts: Path, tmp_path: Path):
        stl_path = release_artifacts / "sphere.stl"
        png_path = tmp_path / "cli.png"
        assert _main([str(stl_path), "-o", str(png_path), "--artifact", "sphere"]) == 0
        assert png_path.exists()

    def test_render_cli_without_artifact_lookup(self, release_artifacts: Path, tmp_path: Path):
        stl_path = release_artifacts / "sphere.stl"
        png_path = tmp_path / "fallback.png"
        assert _main([str(stl_path), "-o", str(png_path), "--camera", "top"]) == 0
        assert png_path.exists()

    def test_export_release_writes_descriptive_png_names(self, release_artifacts: Path):
        size = TEST_RENDER_SIZE_TOKEN
        assert (release_artifacts / f"sphere_front_{size}.png").exists()
        assert (release_artifacts / f"sphere_iso_{size}.png").exists()
        assert (release_artifacts / f"sphere_with_nut_front_{size}.png").exists()
        assert (release_artifacts / f"sphere_with_nut_iso_{size}.png").exists()
        assert not (release_artifacts / "sphere.png").exists()


@pytest.mark.integration
@pytest.mark.render
class TestRenderArtifact:
    def test_show_edges_draws_face_boundaries(self, tmp_path: Path, repo_root: Path):
        from cad_tooling.render import render_artifact
        from cad_tooling.render_config import RenderConfig

        plain = RenderConfig.model_validate({"show_edges": False, "camera": {"preset": "front"}})
        edged = RenderConfig.model_validate(
            {
                "show_edges": True,
                "edge_color": (0.0, 0.0, 0.0),
                "edge_width": 1.5,
                "camera": {"preset": "front"},
            }
        )

        plain_png = tmp_path / "plain.png"
        edged_png = tmp_path / "edged.png"
        render_artifact("sphere", plain_png, overrides=plain, root=repo_root)
        render_artifact("sphere", edged_png, overrides=edged, root=repo_root)

        assert plain_png.read_bytes() != edged_png.read_bytes()

    def test_render_artifact_preserves_part_colors(self, repo_root: Path):
        from cad_tooling.render import _build_artifact_shape, _colored_solids

        shape = _build_artifact_shape("sphere_with_nut", root=repo_root)
        solids = _colored_solids(shape, (0.31, 0.63, 1.0))
        assert len(solids) == 3
        colors = {tuple(round(channel, 2) for channel in face_color) for _, face_color in solids}
        assert len(colors) == 3


@pytest.mark.integration
class TestViewerScript:
    def test_load_viewer_script_reads_main_py(self, repo_root: Path):
        shape, artifact_name, artifact_func = load_viewer_script(
            repo_root / "main.py", root=repo_root
        )
        assert artifact_name == "sphere_with_nut"
        assert artifact_func is not None
        assert artifact_func.__name__ == "sphere_with_nut"
        assert len(shape.children) == 3
        assert shape.volume > 0


@pytest.mark.integration
@pytest.mark.render
class TestRenderMainPy:
    @pytest.fixture(scope="class")
    def main_py_renders(self, tmp_path_factory, repo_root: Path):
        out = tmp_path_factory.mktemp("main_py_renders")
        written = render_input(
            repo_root / "main.py",
            out,
            overrides=TEST_RENDER_OVERRIDES,
            root=repo_root,
        )
        return written

    def test_render_main_py_to_directory(self, main_py_renders):
        size = TEST_RENDER_SIZE_TOKEN
        assert len(main_py_renders) == 4
        names = {path.name for path in main_py_renders}
        assert names == {
            f"sphere_with_nut_front_{size}.png",
            f"sphere_with_nut_iso_{size}.png",
            f"sphere_front_{size}.png",
            f"sphere_iso_{size}.png",
        }
        assert all(path.exists() for path in main_py_renders)
        assert all(path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n" for path in main_py_renders)


@pytest.mark.unit
def test_resolve_input_path_finds_main_py_without_extension(repo_root: Path):
    from cad_tooling.render import _resolve_input_path

    assert _resolve_input_path(repo_root / "main") == (repo_root / "main.py").resolve()


@pytest.mark.unit
def test_ensure_display_starts_xvfb_when_no_display():
    from cad_tooling.render import _ensure_display

    with patch.dict("os.environ", {}, clear=True):
        with patch("cad_tooling.render._display_connection_works", side_effect=[False, True]):
            with patch("cad_tooling.render.shutil.which", return_value="/usr/bin/Xvfb"):
                with patch("cad_tooling.render.subprocess.Popen") as popen:
                    proc = popen.return_value
                    proc.poll.return_value = None
                    _ensure_display(800, 600)
                    popen.assert_called_once()
