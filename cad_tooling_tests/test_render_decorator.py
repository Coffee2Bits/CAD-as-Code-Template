import functools

import pytest

from cad_tooling.render_config import RenderConfig
from cad_tooling.render_decorator import RENDER_CONFIG_ATTR, get_render_config_from_func, render

pytestmark = pytest.mark.unit


def test_render_without_parens():
    @render
    def bare():
        return "ok"

    assert bare() == "ok"
    config = get_render_config_from_func(bare)
    assert config is not None
    assert config.width == 800


def test_render_with_camera_dict():
    @render(camera={"preset": "back", "azimuth": 30})
    def demo():
        return None

    config = get_render_config_from_func(demo)
    assert config is not None
    assert config.camera.preset == "back"
    assert config.camera.azimuth == 30


def test_render_preset_alias():
    @render(preset="left", elevation=5)
    def demo():
        return None

    config = get_render_config_from_func(demo)
    assert config is not None
    assert config.camera.preset == "left"
    assert config.camera.elevation == 5


def test_render_preserves_function_metadata():
    @render(width=512)
    def labeled():
        """Docstring preserved."""

    assert labeled.__name__ == "labeled"
    assert labeled.__doc__ == "Docstring preserved."


def test_get_render_config_walks_wrapped_chain():
    @render(width=900)
    def inner():
        return None

    @functools.wraps(inner)
    def outer():
        return inner()

    config = get_render_config_from_func(outer)
    assert config is not None
    assert config.width == 900


def test_render_config_on_both_wrapper_and_wrapped():
    @render(background=(0.2, 0.2, 0.2))
    def demo():
        return None

    assert hasattr(demo, RENDER_CONFIG_ATTR)
    wrapped = getattr(demo, "__wrapped__")
    assert getattr(wrapped, RENDER_CONFIG_ATTR) is not None
    assert isinstance(getattr(demo, RENDER_CONFIG_ATTR), RenderConfig)


def test_get_render_config_from_func_none():
    assert get_render_config_from_func(None) is None


def test_get_render_config_from_undecorated_function():
    def plain():
        return None

    assert get_render_config_from_func(plain) is None


def test_render_renders_list_stores_multiple_configs():
    @render(renders=[{"camera": "iso"}, {"camera": "top", "width": 1024}])
    def demo():
        return None

    from cad_tooling.render_decorator import get_render_configs_from_func

    configs = get_render_configs_from_func(demo)
    assert len(configs) == 2
    assert configs[0].camera.preset == "iso"
    assert configs[1].camera.preset == "top"
    assert configs[1].width == 1024


def test_render_rejects_mixed_renders_and_keywords():
    import pytest

    with pytest.raises(ValueError, match="not both"):
        render(renders=[{"camera": "iso"}], camera="top")
