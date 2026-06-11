from __future__ import annotations

from pathlib import Path

import pytest

from scripts.template_identity import (
    RepoIdentity,
    apply_text_replacements,
    load_identity,
    render_pages_badge_md,
    render_repo_identity_ts,
    replacement_pairs,
    update_pages_badge_block,
    update_pyproject_name,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_load_identity_matches_template_config() -> None:
    identity = load_identity(REPO_ROOT / "template.repo.toml")
    assert identity.github_owner == "Coffee2Bits"
    assert identity.github_repo == "CAD-as-Code-Template"
    assert identity.docs_site_url == "https://coffee2bits.github.io/CAD-as-Code-Template/"
    assert identity.base_url == "/CAD-as-Code-Template/"


def test_replacement_pairs_prefers_longest_matches_first() -> None:
    old = RepoIdentity(
        github_owner="Coffee2Bits",
        github_repo="CAD-as-Code-Template",
        pages_url="https://coffee2bits.github.io",
        docs_title="CAD-as-Code Template",
        navbar_title="CAD-as-Code",
        tagline="Turnkey parametric CAD in Python",
        python_package_name="programmatic-cad-workspace",
        copyright_holder="Coffee2Bits",
    )
    new = RepoIdentity(
        github_owner="acme",
        github_repo="widget-cad",
        pages_url="https://acme.github.io",
        docs_title="Widget CAD",
        navbar_title="Widget CAD",
        tagline="Widgets in Python",
        python_package_name="widget-cad",
        copyright_holder="acme",
    )
    pairs = replacement_pairs(old, new)
    assert pairs[0][0] == old.docs_site_url
    assert pairs[0][1] == new.docs_site_url


def test_apply_text_replacements_updates_docs_url() -> None:
    old = load_identity(REPO_ROOT / "template.repo.toml")
    new = RepoIdentity(
        github_owner="acme",
        github_repo="widget-cad",
        pages_url="https://acme.github.io",
        docs_title="Widget CAD",
        navbar_title="Widget CAD",
        tagline="Widgets",
        python_package_name="widget-cad",
        copyright_holder="acme",
    )
    pairs = replacement_pairs(old, new)
    sample = "See https://coffee2bits.github.io/CAD-as-Code-Template/tools/just"
    updated = apply_text_replacements(sample, pairs)
    assert updated == "See https://acme.github.io/widget-cad/tools/just"


def test_update_pyproject_name() -> None:
    content = '[project]\nname = "old-name"\nversion = "0.1.0"\n'
    assert update_pyproject_name(content, "new-name") == (
        '[project]\nname = "new-name"\nversion = "0.1.0"\n'
    )


def test_render_pages_badge_md_uses_repo_slug_and_docs_url() -> None:
    identity = load_identity(REPO_ROOT / "template.repo.toml")
    badge = render_pages_badge_md(identity)
    assert "Coffee2Bits/CAD-as-Code-Template/github-pages" in badge
    assert "https://coffee2bits.github.io/CAD-as-Code-Template/" in badge


def test_update_pages_badge_block_replaces_marker_region() -> None:
    identity = load_identity(REPO_ROOT / "template.repo.toml")
    sample = (
        "# Title\n\n"
        "<!-- template:pages-badge:start -->\n"
        "old badge\n"
        "<!-- template:pages-badge:end -->\n\n"
        "body\n"
    )
    updated = update_pages_badge_block(sample, identity)
    assert "old badge" not in updated
    assert "Coffee2Bits/CAD-as-Code-Template/github-pages" in updated


def test_render_repo_identity_ts_contains_slug() -> None:
    identity = load_identity(REPO_ROOT / "template.repo.toml")
    rendered = render_repo_identity_ts(identity)
    assert "Coffee2Bits/CAD-as-Code-Template" in rendered
    assert "export const repoIdentity" in rendered


@pytest.mark.parametrize(
    "pages_url,repo,expected",
    [
        ("https://acme.github.io", "widget-cad", "https://acme.github.io/widget-cad/"),
        ("https://acme.github.io/", "widget-cad", "https://acme.github.io/widget-cad/"),
    ],
)
def test_docs_site_url_normalization(pages_url: str, repo: str, expected: str) -> None:
    identity = RepoIdentity(
        github_owner="acme",
        github_repo=repo,
        pages_url=pages_url,
        docs_title="t",
        navbar_title="t",
        tagline="t",
        python_package_name="pkg",
        copyright_holder="acme",
    )
    assert identity.docs_site_url == expected
