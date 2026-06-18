import argparse

import pytest

from cad_tooling.render_config import (
    CAMERA_PRESET_CHOICES,
    LIGHTING_PRESETS,
    CameraConfig,
    LightingConfig,
    LightingPreset,
    RenderConfig,
    add_render_config_arguments,
    render_config_from_namespace,
    render_filename_token,
    render_output_filename,
    render_preview_label,
    resolve_render_config,
    resolve_render_configs,
    resolve_render_config_for_artifact_name,
)
from cad_tooling.render_decorator import (
    get_render_config_from_func,
    get_render_configs_from_func,
    render,
)


pytestmark = pytest.mark.unit


def test_render_decorator_stores_config():
    @render(width=640, camera="top", azimuth=10)
    def demo_part():
        return None

    config = get_render_config_from_func(demo_part)
    assert config is not None
    assert config.width == 640
    assert config.camera.preset == "top"
    assert config.camera.azimuth == 10


def test_resolve_render_config_merges_defaults_and_overrides():
    @render(camera="top")
    def demo_part():
        return None

    config = resolve_render_config(
        artifact_func=demo_part,
        overrides=RenderConfig.model_validate({"width": 1024}),
    )

    assert config.width == 1024
    assert config.height == 600
    assert config.camera.preset == "top"


def test_merge_preserves_unset_base_fields():
    base = RenderConfig.model_validate({"width": 800, "camera": {"preset": "top"}})
    overrides = RenderConfig.model_validate({"width": 1024})
    merged = base.merge(overrides)
    assert merged.width == 1024
    assert merged.camera.preset == "top"


def test_merge_deep_merges_nested_camera():
    base = RenderConfig.model_validate({"camera": {"preset": "iso", "azimuth": 5}})
    overrides = RenderConfig.model_validate({"camera": {"azimuth": 15}})
    merged = base.merge(overrides)
    assert merged.camera.preset == "iso"
    assert merged.camera.azimuth == 15


def test_merge_deep_merges_nested_lighting():
    base = RenderConfig.model_validate({"lighting": {"preset": "studio", "intensity": 1.0}})
    overrides = RenderConfig.model_validate({"lighting": {"preset": "bright"}})
    merged = base.merge(overrides)
    assert merged.lighting.preset == "bright"
    assert merged.lighting.intensity == 1.0


def test_lighting_config_resolved_profile():
    lighting = LightingConfig.model_validate({"preset": "studio", "intensity": 2.0})
    profile = lighting.resolved_profile()
    assert profile.light_scale == pytest.approx(3.2)
    assert profile.ambient_factor == pytest.approx(1.0)
    assert profile.diffuse_factor == pytest.approx(1.0)


def test_lighting_config_default_preset_uses_preset_table():
    lighting = LightingConfig.model_validate({"preset": "default"})
    profile = lighting.resolved_profile()
    light_scale, ambient_factor, diffuse_factor, specular, shininess = LIGHTING_PRESETS[
        LightingPreset.DEFAULT
    ]
    assert profile.light_scale == pytest.approx(light_scale)
    assert profile.ambient_factor == pytest.approx(ambient_factor)
    assert profile.diffuse_factor == pytest.approx(diffuse_factor)
    assert profile.specular == pytest.approx(specular)
    assert profile.shininess == pytest.approx(shininess)


def test_render_config_edge_defaults():
    config = RenderConfig()
    assert config.show_edges is True
    assert config.edge_color == (0.0, 0.0, 0.0)
    assert config.edge_width == pytest.approx(1.0)


def test_render_decorator_stores_edges():
    @render(show_edges=False, edge_color=(0.2, 0.2, 0.2), edge_width=2.0)
    def demo_part():
        return None

    config = get_render_config_from_func(demo_part)
    assert config is not None
    assert config.show_edges is False
    assert config.edge_color == (0.2, 0.2, 0.2)
    assert config.edge_width == pytest.approx(2.0)


def test_render_config_from_namespace_edge_fields():
    parser = argparse.ArgumentParser()
    add_render_config_arguments(parser)
    args = parser.parse_args(
        [
            "--no-show-edges",
            "--edge-color",
            "0.1,0.2,0.3",
            "--edge-width",
            "2.5",
        ]
    )
    config = render_config_from_namespace(args)
    assert config is not None
    assert config.show_edges is False
    assert config.edge_color == (0.1, 0.2, 0.3)
    assert config.edge_width == pytest.approx(2.5)


def test_render_decorator_stores_lighting():
    @render(lighting={"preset": "flat", "ambient": 0.9})
    def demo_part():
        return None

    config = get_render_config_from_func(demo_part)
    assert config is not None
    assert config.lighting.preset == "flat"
    assert config.lighting.ambient == pytest.approx(0.9)


def test_camera_config_defaults():
    camera = CameraConfig()
    assert camera.preset == "iso"
    assert camera.azimuth == 0
    assert camera.elevation == 0


def test_render_config_from_namespace_all_fields():
    parser = argparse.ArgumentParser()
    add_render_config_arguments(parser)
    args = parser.parse_args(
        [
            "--width",
            "640",
            "--height",
            "480",
            "--background",
            "0.1,0.2,0.3",
            "--face-color",
            "0.4,0.5,0.6",
            "--fit-margin",
            "0.05",
            "--camera",
            "front",
            "--azimuth",
            "12",
            "--elevation",
            "8",
        ]
    )
    config = render_config_from_namespace(args)
    assert config is not None
    assert config.width == 640
    assert config.height == 480
    assert config.background == (0.1, 0.2, 0.3)
    assert config.face_color == (0.4, 0.5, 0.6)
    assert config.fit_margin == 0.05
    assert config.camera.preset == "front"
    assert config.camera.azimuth == 12
    assert config.camera.elevation == 8


def test_render_config_from_namespace_empty_returns_none():
    parser = argparse.ArgumentParser()
    add_render_config_arguments(parser)
    args = parser.parse_args([])
    assert render_config_from_namespace(args) is None


def test_cli_lighting_preset_studio_overrides_global_default(repo_root):
    from cad_tooling.export import list_artifacts

    parser = argparse.ArgumentParser()
    add_render_config_arguments(parser)
    args = parser.parse_args(["--lighting-preset", "studio"])
    overrides = render_config_from_namespace(args)
    artifact = next(item for item in list_artifacts(repo_root) if item.name == "sphere_with_nut")
    configs = resolve_render_configs(artifact_func=artifact.func, overrides=overrides)
    assert configs[0].lighting.preset == LightingPreset.STUDIO
    assert configs[0].lighting.resolved_profile().light_scale == pytest.approx(
        LIGHTING_PRESETS[LightingPreset.STUDIO][0]
    )


def test_invalid_rgb_rejected():
    with pytest.raises(ValueError, match="RGB"):
        RenderConfig.model_validate({"background": [1.5, 0, 0]})


def test_invalid_rgb_length_rejected():
    with pytest.raises(ValueError, match="RGB"):
        RenderConfig.model_validate({"face_color": [0.5, 0.5]})


def test_invalid_width_rejected():
    with pytest.raises(ValueError):
        RenderConfig.model_validate({"width": 0})


def test_camera_preset_choices_complete():
    assert set(CAMERA_PRESET_CHOICES) == {
        "iso",
        "top",
        "bottom",
        "front",
        "back",
        "left",
        "right",
        "axo_left",
        "axo_right",
    }


def test_resolve_render_config_for_artifact_name(repo_root):
    config = resolve_render_config_for_artifact_name("sphere", root=repo_root)
    assert config.camera.preset == "front"
    assert config.face_color == (0.31, 0.63, 1.0)


def test_resolve_render_config_for_unknown_artifact(repo_root):
    with pytest.raises(ValueError, match="Artifact not found"):
        resolve_render_config_for_artifact_name("missing-part", root=repo_root)


def test_sphere_artifact_has_render_config(repo_root):
    from cad_tooling.export import list_artifacts

    artifact = next(item for item in list_artifacts(repo_root) if item.name == "sphere")
    configs = get_render_configs_from_func(artifact.func)
    assert len(configs) == 2
    assert configs[0].camera.preset == "front"
    assert configs[1].camera.preset == "iso"
    assert configs[0].width == 800
    assert configs[0].height == 600
    assert configs[0].face_color == (0.31, 0.63, 1.0)


def test_render_filename_token_includes_camera_and_size():
    config = RenderConfig.model_validate(
        {"camera": {"preset": "top"}, "width": 1024, "height": 768}
    )
    assert render_filename_token(config) == "top_1024x768"


def test_render_filename_token_includes_pose_tweaks():
    config = RenderConfig.model_validate(
        {"camera": {"preset": "iso", "azimuth": 15, "elevation": 5}, "width": 800, "height": 600}
    )
    assert render_filename_token(config) == "iso_az15_el5_800x600"


def test_render_output_filename():
    config = RenderConfig.model_validate(
        {"camera": {"preset": "front"}, "width": 640, "height": 480}
    )
    assert render_output_filename("bracket", config) == "bracket_front_640x480.png"


def test_render_preview_label_uses_name_override():
    config = RenderConfig.model_validate(
        {"name": "front", "camera": {"preset": "back"}, "width": 800, "height": 600}
    )
    assert render_preview_label(config) == "front (800×600)"


def test_render_output_filename_uses_name_override():
    config = RenderConfig.model_validate(
        {"name": "front", "camera": {"preset": "back"}, "width": 800, "height": 600}
    )
    assert render_output_filename("sphere", config) == "sphere_front_800x600.png"


def test_resolve_render_configs_defaults_without_decorator():
    configs = resolve_render_configs()
    assert len(configs) == 1
    assert configs[0].width == 800
    assert configs[0].camera.preset == "iso"
    assert configs[0].lighting.preset == "default"


def test_resolve_render_configs_multiple_from_renders_list():
    @render(
        renders=[
            {"camera": "iso", "width": 800},
            {"camera": "top", "width": 1024, "height": 768},
        ]
    )
    def demo_part():
        return None

    configs = resolve_render_configs(artifact_func=demo_part)
    assert len(configs) == 2
    assert configs[0].camera.preset == "iso"
    assert configs[0].width == 800
    assert configs[0].height == 600
    assert configs[1].camera.preset == "top"
    assert configs[1].width == 1024
    assert configs[1].height == 768


def test_get_render_configs_from_func_returns_list():
    @render(renders=[{"camera": "left"}, {"camera": "right"}])
    def demo_part():
        return None

    configs = get_render_configs_from_func(demo_part)
    assert len(configs) == 2
    assert configs[0].camera.preset == "left"
    assert configs[1].camera.preset == "right"
