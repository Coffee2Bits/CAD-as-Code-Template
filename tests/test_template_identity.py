from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.template_identity import (
    INITIAL_CHANGELOG,
    IdentityOverrides,
    RepoIdentity,
    apply_template_identity,
    apply_text_replacements,
    derived_pages_url,
    detect_git_identity,
    template_init_prompt,
    init_project,
    load_identity,
    parse_github_remote_url,
    prepare_identity,
    render_pages_badge_md,
    render_release_please_manifest,
    render_repo_identity_ts,
    render_template_repo_toml,
    replacement_pairs,
    reset_project_versions,
    update_package_json_name,
    update_pages_badge_block,
    update_pyproject_name,
    update_pyproject_version,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.unit


def test_parse_github_remote_url_accepts_https_and_ssh() -> None:
    assert parse_github_remote_url("https://github.com/acme/widget-cad.git") == (
        "acme",
        "widget-cad",
    )
    assert parse_github_remote_url("git@github.com:acme/widget-cad.git") == (
        "acme",
        "widget-cad",
    )


def test_template_init_prompt_suggests_git_remote(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.template_identity.CONFIG_PATH", tmp_path / "template.repo.toml")
    (tmp_path / "template.repo.toml").write_text(
        """
[github]
owner = "Coffee2Bits"
repo = "CAD-as-Code-Template"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "scripts.template_identity.detect_git_identity",
        lambda: ("acme", "widget-cad"),
    )
    prompt = template_init_prompt()
    assert prompt is not None
    assert "acme/widget-cad" in prompt
    assert "edit template.repo.toml" in prompt
    assert "git remote" in prompt


def test_template_init_prompt_none_after_custom_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.template_identity.CONFIG_PATH", tmp_path / "template.repo.toml")
    (tmp_path / "template.repo.toml").write_text(
        """
[github]
owner = "acme"
repo = "widget-cad"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    assert template_init_prompt() is None


def test_prepare_identity_ignores_git_remote(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config = tmp_path / "template.repo.toml"
    config.write_text(
        """
[github]
owner = "Coffee2Bits"
repo = "CAD-as-Code-Template"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(
        "scripts.template_identity.detect_git_identity",
        lambda: ("acme", "widget-cad"),
    )
    identity, _explicit = prepare_identity(config_path=config)
    assert identity.github_repo_slug == "Coffee2Bits/CAD-as-Code-Template"


def test_detect_git_identity_returns_none_without_origin(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _fail(*_args: object, **_kwargs: object) -> None:
        msg = "no remote"
        raise OSError(msg)

    monkeypatch.setattr("scripts.template_identity.subprocess.run", _fail)
    assert detect_git_identity() is None


def test_load_identity_matches_template_config() -> None:
    identity = load_identity(REPO_ROOT / "template.repo.toml")
    assert identity.github_owner == "Coffee2Bits"
    assert identity.github_repo == "CAD-as-Code-Template"
    assert identity.pages_url == derived_pages_url("Coffee2Bits")
    assert identity.copyright_holder == "Coffee2Bits"
    assert identity.docs_site_url == "https://coffee2bits.github.io/CAD-as-Code-Template/"
    assert identity.base_url == "/CAD-as-Code-Template/"
    assert identity.initial_version == "0.0.0"
    assert identity.resolved_docs_npm_package_name == "cad-as-code-template-docs"


def test_copyright_defaults_to_owner_when_omitted(tmp_path: Path) -> None:
    config = tmp_path / "template.repo.toml"
    config.write_text(
        """
[github]
owner = "acme"
repo = "widget-cad"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    identity = load_identity(config)
    assert identity.copyright_holder == "acme"
    assert identity.pages_url == "https://acme.github.io"
    assert identity.python_package_name == "widget-cad"
    assert identity.docs_title == "widget-cad"


def test_render_template_repo_toml_omits_linked_defaults() -> None:
    identity = load_identity(REPO_ROOT / "template.repo.toml")
    rendered = render_template_repo_toml(identity, frozenset())
    assert "\n[copyright]\n" not in rendered
    assert 'url = "https://coffee2bits.github.io"' not in rendered
    assert "holder =" not in rendered


def test_prepare_identity_cli_overrides_owner_and_repo(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.template_identity.CONFIG_PATH", tmp_path / "template.repo.toml")
    (tmp_path / "template.repo.toml").write_text(
        """
[github]
owner = "Coffee2Bits"
repo = "CAD-as-Code-Template"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    identity, explicit = prepare_identity(
        IdentityOverrides(github_owner="acme", github_repo="widget-cad"),
        config_path=tmp_path / "template.repo.toml",
    )
    assert identity.github_repo_slug == "acme/widget-cad"
    assert identity.copyright_holder == "acme"
    assert "github_owner" in explicit
    assert "github_repo" in explicit


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


def test_update_pyproject_version() -> None:
    content = '[project]\nname = "pkg"\nversion = "0.1.1"\n'
    assert update_pyproject_version(content, "0.0.0") == (
        '[project]\nname = "pkg"\nversion = "0.0.0"\n'
    )


def test_render_release_please_manifest() -> None:
    assert render_release_please_manifest("0.0.0") == '{\n  ".": "0.0.0"\n}\n'


def test_update_package_json_name() -> None:
    content = '{\n  "name": "old-docs",\n  "version": "0.0.0"\n}\n'
    assert update_package_json_name(content, "widget-cad-docs") == (
        '{\n  "name": "widget-cad-docs",\n  "version": "0.0.0"\n}\n'
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


def test_reset_project_versions_dry_run_reports_changes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.template_identity.REPO_ROOT", tmp_path)
    monkeypatch.setattr("scripts.template_identity.PYPROJECT_PATH", tmp_path / "pyproject.toml")
    monkeypatch.setattr(
        "scripts.template_identity.RELEASE_PLEASE_MANIFEST_PATH",
        tmp_path / ".release-please-manifest.json",
    )
    monkeypatch.setattr("scripts.template_identity.CHANGELOG_PATH", tmp_path / "CHANGELOG.md")

    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "pkg"\nversion = "0.1.1"\n',
        encoding="utf-8",
    )
    (tmp_path / ".release-please-manifest.json").write_text(
        json.dumps({".": "0.1.0"}) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "CHANGELOG.md").write_text("# Changelog\n\n## [0.1.0]\n", encoding="utf-8")

    identity = RepoIdentity(
        github_owner="acme",
        github_repo="widget-cad",
        pages_url="https://acme.github.io",
        docs_title="t",
        navbar_title="t",
        tagline="t",
        python_package_name="widget-cad",
        copyright_holder="acme",
        initial_version="0.0.0",
    )
    changed = reset_project_versions(identity, dry_run=True)
    assert "pyproject.toml" in changed
    assert ".release-please-manifest.json" in changed
    assert "CHANGELOG.md" in changed
    assert (tmp_path / "pyproject.toml").read_text(encoding="utf-8").endswith('version = "0.1.1"\n')


def test_init_project_skips_docs_by_default(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.template_identity.REPO_ROOT", tmp_path)
    monkeypatch.setattr("scripts.template_identity.CONFIG_PATH", tmp_path / "template.repo.toml")
    monkeypatch.setattr(
        "scripts.template_identity.APPLIED_PATH", tmp_path / ".template.repo.applied.json"
    )
    monkeypatch.setattr(
        "scripts.template_identity.REPO_IDENTITY_TS", tmp_path / "website" / "repo-identity.ts"
    )
    monkeypatch.setattr("scripts.template_identity.PYPROJECT_PATH", tmp_path / "pyproject.toml")
    monkeypatch.setattr(
        "scripts.template_identity.PACKAGE_JSON_PATH", tmp_path / "website" / "package.json"
    )
    monkeypatch.setattr(
        "scripts.template_identity.RELEASE_PLEASE_MANIFEST_PATH",
        tmp_path / ".release-please-manifest.json",
    )
    monkeypatch.setattr("scripts.template_identity.CHANGELOG_PATH", tmp_path / "CHANGELOG.md")
    monkeypatch.setattr("scripts.template_identity.README_PATH", tmp_path / "README.md")

    (tmp_path / "template.repo.toml").write_text(
        """
[github]
owner = "acme"
repo = "widget-cad"

[pages]
url = "https://acme.github.io"

[docs]
title = "Widget CAD"
navbar_title = "Widget CAD"
tagline = "Widgets"

[python]
package_name = "widget-cad"

[init]
initial_version = "0.0.0"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "programmatic-cad-workspace"\nversion = "0.1.1"\n',
        encoding="utf-8",
    )
    (tmp_path / "website").mkdir()
    (tmp_path / "website" / "package.json").write_text(
        '{\n  "name": "cad-as-code-template-docs",\n  "version": "0.0.0"\n}\n',
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "Docs at https://coffee2bits.github.io/CAD-as-Code-Template/\n",
        encoding="utf-8",
    )

    changed = init_project(dry_run=False, sync_docs=False)

    assert "README.md" not in changed
    assert (
        (tmp_path / "README.md")
        .read_text(encoding="utf-8")
        .startswith("Docs at https://coffee2bits")
    )
    assert (tmp_path / "pyproject.toml").read_text(encoding="utf-8") == (
        '[project]\nname = "widget-cad"\nversion = "0.0.0"\n'
    )
    assert (tmp_path / "CHANGELOG.md").read_text(encoding="utf-8") == INITIAL_CHANGELOG
    assert (tmp_path / ".release-please-manifest.json").read_text(encoding="utf-8") == (
        render_release_please_manifest("0.0.0")
    )


def test_identity_sync_never_touches_cad_tooling_readme(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("scripts.template_identity.REPO_ROOT", tmp_path)
    monkeypatch.setattr("scripts.template_identity.CONFIG_PATH", tmp_path / "template.repo.toml")
    monkeypatch.setattr(
        "scripts.template_identity.APPLIED_PATH", tmp_path / ".template.repo.applied.json"
    )
    monkeypatch.setattr(
        "scripts.template_identity.REPO_IDENTITY_TS", tmp_path / "website" / "repo-identity.ts"
    )
    monkeypatch.setattr("scripts.template_identity.PYPROJECT_PATH", tmp_path / "pyproject.toml")
    monkeypatch.setattr(
        "scripts.template_identity.PACKAGE_JSON_PATH", tmp_path / "website" / "package.json"
    )
    monkeypatch.setattr(
        "scripts.template_identity.RELEASE_PLEASE_MANIFEST_PATH",
        tmp_path / ".release-please-manifest.json",
    )
    monkeypatch.setattr("scripts.template_identity.CHANGELOG_PATH", tmp_path / "CHANGELOG.md")
    monkeypatch.setattr("scripts.template_identity.README_PATH", tmp_path / "README.md")

    (tmp_path / "template.repo.toml").write_text(
        """
[github]
owner = "acme"
repo = "widget-cad"
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text(
        '[project]\nname = "programmatic-cad-workspace"\nversion = "0.1.1"\n',
        encoding="utf-8",
    )
    (tmp_path / "website").mkdir()
    (tmp_path / "website" / "package.json").write_text(
        '{\n  "name": "cad-as-code-template-docs",\n  "version": "0.0.0"\n}\n',
        encoding="utf-8",
    )
    (tmp_path / "cad_tooling").mkdir()
    cad_readme = tmp_path / "cad_tooling" / "README.md"
    cad_readme.write_text(
        "See https://coffee2bits.github.io/CAD-as-Code-Template/tools/cad-tooling/render\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "Docs at https://coffee2bits.github.io/CAD-as-Code-Template/\n",
        encoding="utf-8",
    )

    changed = init_project(
        dry_run=False,
        sync_docs=True,
        overrides=IdentityOverrides(github_owner="acme", github_repo="widget-cad"),
    )

    assert "cad_tooling/README.md" not in changed
    assert (
        cad_readme.read_text(encoding="utf-8")
        == "See https://coffee2bits.github.io/CAD-as-Code-Template/tools/cad-tooling/render\n"
    )
    assert "README.md" in changed

    (tmp_path / ".template.repo.applied.json").write_text(
        json.dumps(RepoIdentity.template_defaults().to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )
    apply_changed = apply_template_identity(dry_run=False, sync_docs=True)
    assert "cad_tooling/README.md" not in apply_changed
    assert (
        cad_readme.read_text(encoding="utf-8")
        == "See https://coffee2bits.github.io/CAD-as-Code-Template/tools/cad-tooling/render\n"
    )
