from pathlib import Path

import pytest

from cad_tooling.export import (
    DEFAULT_EXPORT_FORMAT,
    EXPORT_FORMATS,
    _format_extension,
    _main,
    _resolve_items,
    export_artifacts,
    export_part,
    export_shape,
    list_artifacts,
    list_generators,
    list_release_artifacts,
    load_registry,
)


def test_export_formats_constant():
    assert DEFAULT_EXPORT_FORMAT == "step"
    assert "stl" in EXPORT_FORMATS
    assert "step" in EXPORT_FORMATS


def test_format_extension():
    assert _format_extension("step") == ".step"
    assert _format_extension("stl") == ".stl"
    assert _format_extension("STEP") == ".step"


def test_list_artifacts_discovers_sphere(repo_root: Path):
    names = {artifact.name for artifact in list_artifacts(repo_root)}
    assert "sphere" in names


def test_list_release_artifacts_requires_render(repo_root: Path):
    all_names = {artifact.name for artifact in list_artifacts(repo_root)}
    release_names = {artifact.name for artifact in list_release_artifacts(repo_root)}
    assert "sphere" in release_names
    assert "sphere_with_nut" in release_names
    assert "m3_hex_nut" in all_names
    assert "m3_socket_head_cap_screw" in all_names
    assert "m3_hex_nut" not in release_names
    assert "m3_socket_head_cap_screw" not in release_names


def test_list_generators_discovers_sphere_generator(repo_root: Path):
    names = {generator.name for generator in list_generators(repo_root)}
    assert "sphere_generator" in names


def test_resolve_items_by_simple_name(repo_root: Path):
    registry = load_registry(repo_root)
    items = _resolve_items(registry, ("sphere",), "artifacts", "artifact")
    assert len(items) == 1
    assert items[0].name == "sphere"


def test_resolve_items_by_module_slash_name(repo_root: Path):
    registry = load_registry(repo_root)
    items = _resolve_items(registry, ("cad.parts.sphere/sphere",), "artifacts", "artifact")
    assert len(items) == 1
    assert items[0].name == "sphere"


def test_resolve_items_not_found(repo_root: Path):
    registry = load_registry(repo_root)
    with pytest.raises(ValueError, match="Artifact not found"):
        _resolve_items(registry, ("missing-part",), "artifacts", "artifact")


def test_export_artifacts_to_directory(tmp_path: Path, repo_root: Path):
    written = export_artifacts(tmp_path, "step", ("sphere",), root=repo_root)
    assert len(written) == 1
    assert written[0].name == "sphere.step"
    assert written[0].stat().st_size > 0


def test_export_artifacts_to_single_file(tmp_path: Path, repo_root: Path):
    out = tmp_path / "sphere.step"
    written = export_artifacts(out, "step", ("sphere",), root=repo_root)
    assert written == [out]
    assert out.exists()


def test_export_artifacts_unsupported_format(tmp_path: Path, repo_root: Path):
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_artifacts(tmp_path, "obj", root=repo_root)


def test_export_shape_unsupported_format(tmp_path: Path):
    from build123d import Sphere

    with pytest.raises(ValueError, match="Unsupported export format"):
        export_shape(Sphere(5), tmp_path / "x.obj", "obj")


def test_export_part_writes_step_stl_glb(tmp_path: Path):
    from build123d import Align, BuildPart, Sphere

    with BuildPart() as part:
        Sphere(radius=5, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    export_part(part.part, "demo", tmp_path)

    assert (tmp_path / "demo.step").exists()
    assert (tmp_path / "demo.stl").exists()
    assert (tmp_path / "demo.glb").exists()


def test_main_export_command(tmp_path: Path, repo_root: Path):
    out = tmp_path / "sphere.step"
    assert _main(["export", "-o", str(out), "-f", "step", "sphere", "--root", str(repo_root)]) == 0
    assert out.exists()


def test_main_release_notes_command(tmp_path: Path, repo_root: Path):
    from cad_tooling.export import export_release

    export_release(tmp_path, root=repo_root)
    notes_path = tmp_path / "RELEASE_BODY.md"
    assert (
        _main(
            [
                "release-notes",
                "-o",
                str(notes_path),
                "--assets-dir",
                str(tmp_path),
                "--repo",
                "acme/cad-template",
                "--tag",
                "v0.0.1",
                "--root",
                str(repo_root),
            ]
        )
        == 0
    )
    assert "## sphere" in notes_path.read_text()


def test_export_release_uses_default_lighting_preset(repo_root: Path):
    from cad_tooling.export import list_release_artifacts
    from cad_tooling.render_config import LIGHTING_PRESETS, LightingPreset, resolve_render_configs

    artifact = list_release_artifacts(repo_root)[0]
    config = resolve_render_configs(artifact_func=artifact.func)[0]
    assert config.lighting.preset == LightingPreset.DEFAULT
    profile = config.lighting.resolved_profile()
    light_scale, ambient_factor, diffuse_factor, _, _ = LIGHTING_PRESETS[LightingPreset.DEFAULT]
    assert profile.light_scale == pytest.approx(light_scale)
    assert profile.ambient_factor == pytest.approx(ambient_factor)
    assert profile.diffuse_factor == pytest.approx(diffuse_factor)


def test_main_release_applies_render_overrides(tmp_path: Path, repo_root: Path):
    assert (
        _main(
            [
                "release",
                "-o",
                str(tmp_path),
                "--root",
                str(repo_root),
                "--width",
                "400",
                "--height",
                "300",
            ]
        )
        == 0
    )
    assert (tmp_path / "sphere_front_400x300.png").exists()
    assert (tmp_path / "sphere_iso_400x300.png").exists()
