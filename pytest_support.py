"""Shared helpers and constants for pytest (importable from test modules)."""

from __future__ import annotations

from pathlib import Path

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


def artifact_names(registry: Registry) -> set[str]:
    return {item.name for _, _, item in _items_flat(registry, "artifacts")}


def generator_names(registry: Registry) -> set[str]:
    return {item.name for _, _, item in _items_flat(registry, "customizables")}


def artifacts_list(registry: Registry) -> list:
    return [item for _, _, item in _items_flat(registry, "artifacts")]
