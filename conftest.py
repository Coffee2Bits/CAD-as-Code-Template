"""Shared pytest fixtures for ``tests/`` and ``cad_tooling_tests/``."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from mr.registry import Registry

from cad_tooling.export import export_release, load_registry
from pytest_support import PRIMARY_TEST_MARKERS, REPO_ROOT, TEST_RENDER_OVERRIDES


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    """Every test must declare exactly one primary type marker."""
    for item in items:
        names = {mark.name for mark in item.iter_markers()}
        primary = names & PRIMARY_TEST_MARKERS
        if len(primary) != 1:
            expected = ", ".join(sorted(PRIMARY_TEST_MARKERS))
            raise pytest.UsageError(
                f"{item.nodeid}: must have exactly one primary marker ({expected}); "
                f"found {sorted(primary) or 'none'}"
            )
        if "render" in names and "integration" not in names:
            raise pytest.UsageError(f"{item.nodeid}: render marker requires integration")


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def registry(repo_root: Path) -> Iterator[Registry]:
    reg = load_registry(repo_root)
    yield reg


@pytest.fixture(scope="session")
def release_artifacts(tmp_path_factory: pytest.TempPathFactory, repo_root: Path) -> Iterator[Path]:
    out = tmp_path_factory.mktemp("release")
    export_release(out, root=repo_root, render_overrides=TEST_RENDER_OVERRIDES)
    yield out
