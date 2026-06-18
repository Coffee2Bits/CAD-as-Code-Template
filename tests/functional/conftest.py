"""Fixtures for functional tests that run ``just`` in an isolated workspace copy.

Never run destructive recipes (``just init``, ``just template-apply``, …) against
the real repository root — always use :func:`isolated_repo` and :func:`run_just`.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

_COPY_IGNORE = shutil.ignore_patterns(
    ".venv",
    ".git",
    "node_modules",
    "__pycache__",
    "*.pyc",
    "website/node_modules",
    "website/build",
    "website/.docusaurus",
    "dist",
    ".template.repo.applied.json",
    "agent-transcripts",
)


def _assert_not_real_repo(workspace: Path) -> None:
    if workspace.resolve() == REPO_ROOT.resolve():
        msg = "refusing to run destructive just commands in the real repository root"
        raise RuntimeError(msg)


def run_just(
    workspace: Path,
    *args: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    """Run ``just`` in *workspace* (must be an isolated copy, not REPO_ROOT)."""
    _assert_not_real_repo(workspace)
    merged = os.environ.copy()
    merged["UV_PROJECT_ENVIRONMENT"] = str(REPO_ROOT / ".venv")
    if env:
        merged.update(env)
    return subprocess.run(
        ["just", *args],
        cwd=workspace,
        capture_output=True,
        text=True,
        check=False,
        env=merged,
    )


@pytest.fixture
def isolated_repo(tmp_path: Path) -> Path:
    """Full workspace copy under *tmp_path* — safe for destructive ``just`` recipes."""
    dest = tmp_path / "workspace"
    shutil.copytree(REPO_ROOT, dest, ignore=_COPY_IGNORE)
    _assert_not_real_repo(dest)
    return dest


@pytest.fixture
def assert_just_ok():
    def _check(result: subprocess.CompletedProcess[str], args: Sequence[str]) -> None:
        if result.returncode == 0:
            return
        msg = (
            f"just {' '.join(args)} failed (exit {result.returncode})\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
        raise AssertionError(msg)

    return _check
