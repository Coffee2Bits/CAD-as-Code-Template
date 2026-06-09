from pathlib import Path
from unittest.mock import patch

import pytest

from cad_tooling.export import export_release, list_artifacts
from cad_tooling.release_notes import (
    ReleaseAsset,
    collect_release_assets,
    release_download_url,
    render_release_body,
)
from cad_tooling.render import CAMERA_PRESETS, _main, render_stl


def test_release_download_url():
    url = release_download_url("acme/widgets", "v1.2.3", "sphere.stl")
    assert url == "https://github.com/acme/widgets/releases/download/v1.2.3/sphere.stl"


def test_render_release_body_lists_artifacts_with_previews(repo_root: Path):
    artifact = next(item for item in list_artifacts(repo_root) if item.name == "sphere")
    assets = [
        ReleaseAsset(
            artifact=artifact,
            stl_path=Path("sphere.stl"),
            png_path=Path("sphere.png"),
        )
    ]

    body = render_release_body("acme/cad-template", "v0.0.1", assets)

    assert "# Release artifacts" in body
    assert "## sphere" in body
    assert "Demo sphere for workspace smoke tests" in body
    assert (
        "![sphere](https://github.com/acme/cad-template/releases/download/v0.0.1/sphere.png)"
        in body
    )
    assert "|" not in body
    assert (
        "[sphere.stl](https://github.com/acme/cad-template/releases/download/v0.0.1/sphere.stl)"
        in body
    )


def test_render_release_body_sorts_artifacts():
    artifact_a = next(item for item in list_artifacts() if item.name == "sphere")

    class FakeArtifact:
        name = "alpha"
        short_desc = None
        desc = None

    assets = [
        ReleaseAsset(FakeArtifact(), Path("alpha.stl"), Path("alpha.png")),
        ReleaseAsset(artifact_a, Path("sphere.stl"), Path("sphere.png")),
    ]
    body = render_release_body("acme/repo", "v1.0.0", assets)
    assert body.index("## alpha") < body.index("## sphere")


def test_collect_release_assets(tmp_path: Path, repo_root: Path):
    export_release(tmp_path, root=repo_root)
    assets = collect_release_assets(tmp_path, root=repo_root)
    assert len(assets) >= 1
    assert any(asset.artifact.name == "sphere" for asset in assets)


def test_collect_release_assets_missing_stl(tmp_path: Path, repo_root: Path):
    from cad_tooling.export import export_artifacts

    export_artifacts(tmp_path, "stl", ("sphere",), root=repo_root)
    (tmp_path / "sphere.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    (tmp_path / "sphere.stl").unlink()
    with pytest.raises(FileNotFoundError, match="Missing release STL"):
        collect_release_assets(tmp_path, root=repo_root)


def test_collect_release_assets_missing_png(tmp_path: Path, repo_root: Path):
    from cad_tooling.export import export_artifacts

    export_artifacts(tmp_path, "stl", ("sphere",), root=repo_root)
    with pytest.raises(FileNotFoundError, match="Missing release preview"):
        collect_release_assets(tmp_path, root=repo_root)


def test_camera_presets_cover_all_config_choices():
    from cad_tooling.render_config import CAMERA_PRESET_CHOICES

    assert set(CAMERA_PRESET_CHOICES) == set(CAMERA_PRESETS.keys())


def test_render_stl_writes_png(tmp_path: Path, repo_root: Path):
    export_release(tmp_path, root=repo_root)
    stl_path = tmp_path / "sphere.stl"
    png_path = tmp_path / "custom.png"
    render_stl(stl_path, png_path)
    assert png_path.exists()
    assert png_path.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_render_cli(tmp_path: Path, repo_root: Path):
    export_release(tmp_path, root=repo_root)
    stl_path = tmp_path / "sphere.stl"
    png_path = tmp_path / "cli.png"
    assert _main([str(stl_path), "-o", str(png_path), "--artifact", "sphere"]) == 0
    assert png_path.exists()


def test_render_cli_without_artifact_lookup(tmp_path: Path, repo_root: Path):
    export_release(tmp_path, root=repo_root)
    stl_path = tmp_path / "sphere.stl"
    png_path = tmp_path / "fallback.png"
    assert _main([str(stl_path), "-o", str(png_path), "--camera", "top"]) == 0
    assert png_path.exists()


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
