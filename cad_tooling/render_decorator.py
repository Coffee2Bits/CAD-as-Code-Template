"""@render decorator — per-artifact preview settings in Python source."""

from __future__ import annotations

import functools
from collections.abc import Callable, Mapping
from typing import TypeVar, cast, overload

from cad_tooling.render_config import CameraPreset, RenderConfig, RgbTriplet

RenderSpec = RenderConfig | Mapping[str, object]

# Stored on @render-wrapped functions; read by cad_tooling.render and export release.
RENDER_CONFIG_ATTR = "__cad_render_config__"

_F = TypeVar("_F", bound=Callable[..., object])


def _settings_to_partial_config(
    *,
    name: str | None = None,
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
        ("name", name),
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


def _spec_to_partial_config(spec: RenderSpec) -> RenderConfig:
    """Normalize one render spec (mapping or RenderConfig) into a partial RenderConfig."""
    if isinstance(spec, RenderConfig):
        return spec
    if isinstance(spec, Mapping):
        return _settings_to_partial_config(
            name=spec.get("name"),  # type: ignore[arg-type]
            camera=spec.get("camera"),  # type: ignore[arg-type]
            preset=spec.get("preset"),  # type: ignore[arg-type]
            azimuth=spec.get("azimuth"),  # type: ignore[arg-type]
            elevation=spec.get("elevation"),  # type: ignore[arg-type]
            width=spec.get("width"),  # type: ignore[arg-type]
            height=spec.get("height"),  # type: ignore[arg-type]
            background=spec.get("background"),  # type: ignore[arg-type]
            face_color=spec.get("face_color"),  # type: ignore[arg-type]
            fit_margin=spec.get("fit_margin"),  # type: ignore[arg-type]
        )
    raise TypeError(f"Expected RenderConfig or mapping in @render list, got {type(spec)}")


def _normalize_render_specs(raw: object) -> list[RenderConfig]:
    """Normalize stored @render payload to a list of partial RenderConfig objects."""
    if isinstance(raw, list):
        return [_spec_to_partial_config(item) for item in raw]
    if isinstance(raw, RenderConfig):
        return [raw]
    if isinstance(raw, Mapping):
        return [_spec_to_partial_config(raw)]
    raise TypeError(f"Unexpected @render payload type: {type(raw)}")


def get_render_configs_from_func(func: Callable[..., object] | None) -> list[RenderConfig]:
    """Return all @render settings attached to a function (searches __wrapped__ chain)."""
    current = func
    while current is not None:
        raw = getattr(current, RENDER_CONFIG_ATTR, None)
        if raw is not None:
            return _normalize_render_specs(raw)
        current = getattr(current, "__wrapped__", None)
    return []


def get_render_config_from_func(func: Callable[..., object] | None) -> RenderConfig | None:
    """Return the first @render settings attached to a function."""
    configs = get_render_configs_from_func(func)
    return configs[0] if configs else None


@overload
def render(func: _F, /) -> _F: ...


@overload
def render(
    func: None = None,
    *,
    renders: list[RenderSpec] | None = None,
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
    renders: list[RenderSpec] | None = None,
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

    Multiple previews per artifact::

        @render(renders=[
            {"camera": "iso", "width": 800, "height": 600},
            {"camera": "top", "width": 1024, "height": 768},
        ])

    At render time, unset fields inherit from :class:`~cad_tooling.render_config.RenderConfig`
    defaults. CLI flags on ``cad_tooling.render`` and ``cad_tooling.export release`` override
    these settings for one-off runs.
    """
    if renders is not None:
        if any(
            value is not None
            for value in (
                camera,
                preset,
                azimuth,
                elevation,
                width,
                height,
                background,
                face_color,
                fit_margin,
            )
        ):
            raise ValueError(
                "Use either @render(renders=[...]) or single-render keyword args, not both"
            )
        if not renders:
            raise ValueError("@render(renders=[...]) requires at least one render spec")
        settings: list[RenderConfig] | RenderConfig = [
            _spec_to_partial_config(item) for item in renders
        ]
    else:
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
