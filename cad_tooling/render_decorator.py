"""@render decorator — per-artifact preview settings in Python source."""

from __future__ import annotations

import functools
from collections.abc import Callable, Mapping
from typing import TypeVar, cast, overload

from cad_tooling.render_config import CameraPreset, RenderConfig, RgbTriplet

# Stored on @render-wrapped functions; read by cad_tooling.render and export release.
RENDER_CONFIG_ATTR = "__cad_render_config__"

_F = TypeVar("_F", bound=Callable[..., object])


def _settings_to_partial_config(
    *,
    camera: CameraPreset | Mapping[str, object] | None = None,
    preset: CameraPreset | None = None,
    azimuth: float | None = None,
    elevation: float | None = None,
    width: int | None = None,
    height: int | None = None,
    background: RgbTriplet | None = None,
    face_color: RgbTriplet | None = None,
    fit_margin: float | None = None,
) -> RenderConfig:
    """Normalize @render keyword arguments into a partial RenderConfig."""
    payload: dict[str, object] = {}
    for key, value in (
        ("width", width),
        ("height", height),
        ("background", background),
        ("face_color", face_color),
        ("fit_margin", fit_margin),
    ):
        if value is not None:
            payload[key] = value

    camera_fields: dict[str, object] = {}
    if isinstance(camera, str):
        camera_fields["preset"] = camera
    elif isinstance(camera, Mapping):
        camera_fields.update(camera)

    if preset is not None:
        camera_fields["preset"] = preset
    if azimuth is not None:
        camera_fields["azimuth"] = azimuth
    if elevation is not None:
        camera_fields["elevation"] = elevation

    if camera_fields:
        payload["camera"] = camera_fields

    return RenderConfig.model_validate(payload)


def get_render_config_from_func(func: Callable[..., object] | None) -> RenderConfig | None:
    """Return @render settings attached to a function (searches __wrapped__ chain)."""
    current = func
    while current is not None:
        raw = getattr(current, RENDER_CONFIG_ATTR, None)
        if raw is not None:
            return raw if isinstance(raw, RenderConfig) else RenderConfig.model_validate(raw)
        current = getattr(current, "__wrapped__", None)
    return None


@overload
def render(func: _F, /) -> _F: ...


@overload
def render(
    func: None = None,
    *,
    camera: CameraPreset | Mapping[str, object] | None = None,
    preset: CameraPreset | None = None,
    azimuth: float | None = None,
    elevation: float | None = None,
    width: int | None = None,
    height: int | None = None,
    background: RgbTriplet | None = None,
    face_color: RgbTriplet | None = None,
    fit_margin: float | None = None,
) -> Callable[[_F], _F]: ...


def render(
    func: _F | None = None,
    *,
    camera: CameraPreset | Mapping[str, object] | None = None,
    preset: CameraPreset | None = None,
    azimuth: float | None = None,
    elevation: float | None = None,
    width: int | None = None,
    height: int | None = None,
    background: RgbTriplet | None = None,
    face_color: RgbTriplet | None = None,
    fit_margin: float | None = None,
) -> _F | Callable[[_F], _F]:
    """Attach release preview settings to an @artifact entry point.

    Place directly above the artifact function, below ``@artifact``:

        @artifact(short_desc="...")
        @render(camera="top", azimuth=15, face_color=(0.4, 0.7, 1.0), width=1024)
        def bracket() -> Part:
            ...

    At render time, unset fields inherit from :class:`~cad_tooling.render_config.RenderConfig`
    defaults. CLI flags on ``cad_tooling.render`` and ``cad_tooling.export release`` override
    these settings for one-off runs.
    """
    settings = _settings_to_partial_config(
        camera=camera,
        preset=preset,
        azimuth=azimuth,
        elevation=elevation,
        width=width,
        height=height,
        background=background,
        face_color=face_color,
        fit_margin=fit_margin,
    )

    def decorator(wrapped: _F) -> _F:
        @functools.wraps(wrapped)
        def wrapper(*args: object, **kwargs: object):
            return wrapped(*args, **kwargs)

        setattr(wrapper, RENDER_CONFIG_ATTR, settings)
        setattr(wrapped, RENDER_CONFIG_ATTR, settings)
        return cast(_F, wrapper)

    if func is not None:
        return decorator(func)
    return decorator
