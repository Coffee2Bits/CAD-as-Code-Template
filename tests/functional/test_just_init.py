"""Functional tests for ``just init`` / ``just init-dry-run``.

These exercises the real ``just`` CLI in an isolated temp copy of the repo so the
working tree is never mutated.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests.functional.conftest import REPO_ROOT, run_just

pytestmark = pytest.mark.functional

UPSTREAM_DOCS_URL = "https://coffee2bits.github.io/CAD-as-Code-Template/"
ACME_DOCS_URL = "https://acme.github.io/widget-cad/"


@pytest.fixture
def git_acme_remote(isolated_repo: Path) -> Path:
    subprocess.run(["git", "init"], cwd=isolated_repo, check=True, capture_output=True)
    subprocess.run(
        ["git", "remote", "add", "origin", "https://github.com/acme/widget-cad.git"],
        cwd=isolated_repo,
        check=True,
        capture_output=True,
    )
    return isolated_repo


def test_just_init_dry_run_syncs_docs_by_default(
    isolated_repo: Path,
    assert_just_ok,
) -> None:
    result = run_just(
        isolated_repo,
        "init-dry-run",
        "--owner",
        "acme",
        "--repo",
        "widget-cad",
    )
    assert_just_ok(result, ("init-dry-run", "--owner", "acme", "--repo", "widget-cad"))
    assert "README.md" in result.stdout
    assert "website/docs/" in result.stdout


def test_just_init_dry_run_no_sync_docs_skips_readme(
    isolated_repo: Path,
    assert_just_ok,
) -> None:
    result = run_just(
        isolated_repo,
        "init-dry-run",
        "--owner",
        "acme",
        "--repo",
        "widget-cad",
        "--no-sync-docs",
    )
    assert_just_ok(
        result,
        ("init-dry-run", "--owner", "acme", "--repo", "widget-cad", "--no-sync-docs"),
    )
    assert "README.md" not in result.stdout
    assert "pyproject.toml" in result.stdout


def test_just_init_rebrands_isolated_workspace(
    isolated_repo: Path,
    assert_just_ok,
) -> None:
    cad_readme = isolated_repo / "cad_tooling" / "README.md"
    cad_before = cad_readme.read_text(encoding="utf-8")

    result = run_just(
        isolated_repo,
        "init",
        "--owner",
        "acme",
        "--repo",
        "widget-cad",
    )
    assert_just_ok(result, ("init", "--owner", "acme", "--repo", "widget-cad"))
    assert "Initialized acme/widget-cad" in result.stdout

    pyproject = (isolated_repo / "pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "0.0.0"' in pyproject

    toml = (isolated_repo / "template.repo.toml").read_text(encoding="utf-8")
    assert 'owner = "acme"' in toml
    assert 'repo = "widget-cad"' in toml

    readme = (isolated_repo / "README.md").read_text(encoding="utf-8")
    assert UPSTREAM_DOCS_URL not in readme
    assert ACME_DOCS_URL in readme

    assert cad_readme.read_text(encoding="utf-8") == cad_before
    assert "cad_tooling/README.md" not in result.stdout


def test_just_init_from_edited_toml(
    isolated_repo: Path,
    assert_just_ok,
) -> None:
    toml_path = isolated_repo / "template.repo.toml"
    toml_path.write_text(
        """
[github]
owner = "acme"
repo = "widget-cad"
""".strip()
        + "\n",
        encoding="utf-8",
    )

    result = run_just(isolated_repo, "init", "--no-sync-docs")
    assert_just_ok(result, ("init", "--no-sync-docs"))
    assert "Initialized acme/widget-cad" in result.stdout

    toml = toml_path.read_text(encoding="utf-8")
    assert 'owner = "acme"' in toml
    assert 'repo = "widget-cad"' in toml


def test_just_init_does_not_infer_git_remote(
    git_acme_remote: Path,
    assert_just_ok,
) -> None:
    result = run_just(git_acme_remote, "init", "--no-sync-docs")
    assert_just_ok(result, ("init", "--no-sync-docs"))
    assert "Initialized Coffee2Bits/CAD-as-Code-Template" in result.stdout

    toml = (git_acme_remote / "template.repo.toml").read_text(encoding="utf-8")
    assert 'owner = "Coffee2Bits"' in toml
    assert 'owner = "acme"' not in toml


def test_just_init_does_not_modify_real_repo(
    isolated_repo: Path,
    assert_just_ok,
) -> None:
    markers_before = {
        path: path.read_text(encoding="utf-8")
        for path in (
            REPO_ROOT / "pyproject.toml",
            REPO_ROOT / "template.repo.toml",
            REPO_ROOT / "README.md",
        )
    }
    result = run_just(
        isolated_repo,
        "init",
        "--owner",
        "acme",
        "--repo",
        "widget-cad",
    )
    assert_just_ok(result, ("init", "--owner", "acme", "--repo", "widget-cad"))
    for path, before in markers_before.items():
        assert path.read_text(encoding="utf-8") == before, f"{path.name} was modified in real repo"
