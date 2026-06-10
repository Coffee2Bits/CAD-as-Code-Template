"""Render preview settings models and resolution."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Callable, Literal, Self

from pydantic import BaseModel, Field, field_validator, model_validator

CameraPreset = Literal[
    "iso",
    "top",
    "bottom",
    "front",
    "back",
    "left",
    "right",
    "axo_left",
    "axo_right",
]

RgbTriplet = tuple[float, float, float]

CAMERA_PRESET_CHOICES: tuple[str, ...] = (
    "iso",
    "top",
    "bottom",
    "front",
    "back",
    "left",
    "right",
    "axo_left",
    "axo_right",
)


class CameraConfig(BaseModel):
    """View orientation for OCCT offscreen renders."""

    preset: CameraPreset = "iso"
    azimuth: float = Field(default=0, description="Extra rotation around Z in degrees")
    elevation: float = Field(default=0, description="Extra rotation around X in degrees")


class RenderConfig(BaseModel):
    """PNG preview settings used by release export and cad_tooling.render CLI."""

    name: str | None = Field(
        default=None,
        description="Optional filename label when the camera preset does not match the intended view name",
    )
    width: int = Field(default=800, gt=0)
    height: int = Field(default=600, gt=0)
    background: tuple[float, float, float] = (0.12, 0.12, 0.12)
    face_color: tuple[float, float, float] = (0.31, 0.63, 1.0)
    fit_margin: float = Field(default=0.01, ge=0)
    camera: CameraConfig = Field(default_factory=CameraConfig)

    @field_validator("background", "face_color", mode="before")
    @classmethod
    def _rgb_triplet(cls, value: object) -> tuple[float, float, float]:
        if not isinstance(value, (list, tuple)) or len(value) != 3:
            raise ValueError("Expected an RGB triplet [r, g, b] with values in 0.0–1.0")
        rgb = tuple(float(channel) for channel in value)
        if any(channel < 0 or channel > 1 for channel in rgb):
            raise ValueError("RGB channels must be between 0.0 and 1.0")
        return rgb  # type: ignore[return-value]

    @model_validator(mode="after")
    def _validate_camera_preset(self) -> Self:
        if self.camera.preset not in CAMERA_PRESET_CHOICES:
            choices = ", ".join(CAMERA_PRESET_CHOICES)
            raise ValueError(f"Unknown camera preset '{self.camera.preset}'. Choose: {choices}")
        return self

    def merge(self, overrides: RenderConfig | None) -> RenderConfig:
        """Return a copy with non-default override fields applied."""
        if overrides is None:
            return self.model_copy(deep=True)
        base = self.model_dump()
        patch = overrides.model_dump(exclude_unset=True, exclude_defaults=True)
        return RenderConfig.model_validate(_deep_merge(base, patch))


def _deep_merge(base: dict, patch: dict) -> dict:
    merged = dict(base)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _format_angle_token(prefix: str, degrees: float) -> str:
    """Compact angle suffix for render filenames (e.g. az15, el7.5)."""
    if degrees == int(degrees):
        return f"{prefix}{int(degrees)}"
    return f"{prefix}{degrees:g}"


def render_filename_token(config: RenderConfig) -> str:
    """Build a stable filename token from resolved camera and image size."""
    parts: list[str] = [config.name or config.camera.preset]
    if config.camera.azimuth:
        parts.append(_format_angle_token("az", config.camera.azimuth))
    if config.camera.elevation:
        parts.append(_format_angle_token("el", config.camera.elevation))
    parts.append(f"{config.width}x{config.height}")
    return "_".join(parts)


def render_output_filename(artifact_name: str, config: RenderConfig) -> str:
    """Return a PNG filename encoding view direction and image dimensions."""
    return f"{artifact_name}_{render_filename_token(config)}.png"


def render_preview_label(config: RenderConfig) -> str:
    """Human-readable label for a @render spec (used in release notes links)."""
    view = (config.name or config.camera.preset).replace("_", " ")
    label = f"{view} ({config.width}×{config.height})"
    if config.camera.azimuth:
        label += f", azimuth {config.camera.azimuth:g}°"
    if config.camera.elevation:
        label += f", elevation {config.camera.elevation:g}°"
    return label


def resolve_render_configs(
    *,
    artifact_func: Callable[..., object] | None = None,
    overrides: RenderConfig | None = None,
) -> list[RenderConfig]:
    """Merge defaults, @render settings on artifact_func, and CLI overrides."""
    from cad_tooling.render_decorator import get_render_configs_from_func

    partials = get_render_configs_from_func(artifact_func) if artifact_func is not None else []
    if not partials:
        partials = [RenderConfig()]
    return [RenderConfig().merge(partial).merge(overrides) for partial in partials]


def resolve_render_config(
    *,
    artifact_func: Callable[..., object] | None = None,
    overrides: RenderConfig | None = None,
) -> RenderConfig:
    """Resolve the first (or only) render config for an artifact."""
    configs = resolve_render_configs(artifact_func=artifact_func, overrides=overrides)
    return configs[0]


def add_render_config_arguments(parser: argparse.ArgumentParser) -> None:
    """Register CLI render override flags (applied on top of @render settings)."""
    parser.add_argument(
        "--artifact",
        default=None,
        help="Artifact name for @render lookup (default: STL filename stem)",
    )
    parser.add_argument("--width", type=int, default=None, help="PNG width in pixels")
    parser.add_argument("--height", type=int, default=None, help="PNG height in pixels")
    parser.add_argument(
        "--background",
        default=None,
        metavar="R,G,B",
        help="Background RGB in 0.0–1.0",
    )
    parser.add_argument(
        "--face-color",
        default=None,
        metavar="R,G,B",
        help="Part color RGB in 0.0–1.0",
    )
    parser.add_argument("--fit-margin", type=float, default=None, help="V3d_View.FitAll margin")
    parser.add_argument(
        "--camera",
        choices=CAMERA_PRESET_CHOICES,
        default=None,
        help="Camera preset",
    )
    parser.add_argument("--azimuth", type=float, default=None, help="Extra Z rotation in degrees")
    parser.add_argument(
        "--elevation",
        type=float,
        default=None,
        help="Extra X rotation in degrees",
    )


def render_config_from_namespace(args: argparse.Namespace) -> RenderConfig | None:
    """Build override RenderConfig from argparse namespace (unset fields omitted)."""
    camera_fields: dict[str, object] = {}
    if args.camera is not None:
        camera_fields["preset"] = args.camera
    if args.azimuth is not None:
        camera_fields["azimuth"] = args.azimuth
    if args.elevation is not None:
        camera_fields["elevation"] = args.elevation

    fields: dict[str, object] = {}
    if args.width is not None:
        fields["width"] = args.width
    if args.height is not None:
        fields["height"] = args.height
    if args.background is not None:
        fields["background"] = tuple(float(v) for v in args.background.split(","))
    if args.face_color is not None:
        fields["face_color"] = tuple(float(v) for v in args.face_color.split(","))
    if getattr(args, "fit_margin", None) is not None:
        fields["fit_margin"] = args.fit_margin
    if camera_fields:
        fields["camera"] = camera_fields

    if not fields:
        return None
    return RenderConfig.model_validate(fields)


def resolve_render_config_for_artifact_name(
    name: str,
    *,
    root: Path | None = None,
    overrides: RenderConfig | None = None,
) -> RenderConfig:
    """Resolve render settings for a named @artifact (includes @render if present)."""
    from cad_tooling.export import list_artifacts

    matches = [item for item in list_artifacts(root) if item.name == name]
    if not matches:
        raise ValueError(f"Artifact not found for render lookup: {name}")
    if len(matches) > 1:
        options = ", ".join(f"{item.module}/{item.name}" for item in matches)
        raise ValueError(f"Ambiguous artifact name '{name}'; use module/name: {options}")
    return resolve_render_config(artifact_func=matches[0].func, overrides=overrides)
