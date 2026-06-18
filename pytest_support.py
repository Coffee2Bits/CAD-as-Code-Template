"""Shared helpers and constants for pytest (importable from test modules)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from build123d import Part
from mr.registry import Registry

from cad_tooling.export import _items_flat
from cad_tooling.render_config import RenderConfig

REPO_ROOT = Path(__file__).resolve().parent

PRIMARY_TEST_MARKERS = frozenset({"unit", "integration", "functional"})

TEST_RENDER_WIDTH = 256
TEST_RENDER_HEIGHT = 192
TEST_RENDER_OVERRIDES = RenderConfig.model_validate(
    {"width": TEST_RENDER_WIDTH, "height": TEST_RENDER_HEIGHT}
)
TEST_RENDER_SIZE_TOKEN = f"{TEST_RENDER_WIDTH}x{TEST_RENDER_HEIGHT}"

_sphere_cache: dict[tuple[tuple[str, Any], ...], Part] = {}


def cached_make_sphere(**kwargs: Any) -> Part:
    """Session-wide memo of ``make_sphere`` for integration tests."""
    key = tuple(sorted(kwargs.items()))
    if key not in _sphere_cache:
        from cad.parts.sphere import make_sphere

        _sphere_cache[key] = make_sphere(**kwargs)
    return _sphere_cache[key]


def artifact_names(registry: Registry) -> set[str]:
    return {item.name for _, _, item in _items_flat(registry, "artifacts")}


def generator_names(registry: Registry) -> set[str]:
    return {item.name for _, _, item in _items_flat(registry, "customizables")}


def artifacts_list(registry: Registry) -> list:
    return [item for _, _, item in _items_flat(registry, "artifacts")]
