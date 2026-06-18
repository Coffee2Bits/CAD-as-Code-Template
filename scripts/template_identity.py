"""Load and apply template repository identity from template.repo.toml."""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

DocsSyncMode = Literal["none", "init", "template"]

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "template.repo.toml"
APPLIED_PATH = REPO_ROOT / ".template.repo.applied.json"
REPO_IDENTITY_TS = REPO_ROOT / "website" / "repo-identity.ts"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
PACKAGE_JSON_PATH = REPO_ROOT / "website" / "package.json"
RELEASE_PLEASE_MANIFEST_PATH = REPO_ROOT / ".release-please-manifest.json"
CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"
README_PATH = REPO_ROOT / "README.md"
PAGES_BADGE_START = "<!-- template:pages-badge:start -->"
PAGES_BADGE_END = "<!-- template:pages-badge:end -->"

INITIAL_CHANGELOG = "# Changelog\n"

DEFAULT_TAGLINE = "Turnkey parametric CAD in Python"
DEFAULT_INITIAL_VERSION = "0.0.0"

INTEGRATION_SYNC_GLOBS = ("AGENTS.md",)

DOCS_SYNC_GLOBS = (
    "README.md",
    "CHANGELOG.md",
    "website/README.md",
    "website/docs/**/*.md",
)

# cad_tooling/ is an embedded library — never included in identity sync.

ALL_SYNC_GLOBS = INTEGRATION_SYNC_GLOBS + DOCS_SYNC_GLOBS

TEMPLATE_DEFAULTS: dict[str, str] = {
    "github_owner": "Coffee2Bits",
    "github_repo": "CAD-as-Code-Template",
    "pages_url": "https://coffee2bits.github.io",
    "docs_title": "CAD-as-Code Template",
    "navbar_title": "CAD-as-Code",
    "tagline": "Turnkey parametric CAD in Python",
    "python_package_name": "programmatic-cad-workspace",
    "copyright_holder": "Coffee2Bits",
}


def derived_pages_url(owner: str) -> str:
    return f"https://{owner.lower()}.github.io"


def derived_package_name(repo: str) -> str:
    return repo.lower().replace("_", "-")


def derived_docs_title(repo: str) -> str:
    return repo


def derived_navbar_title(repo: str) -> str:
    return repo


def derived_docs_npm_package_name(repo: str) -> str:
    return f"{derived_package_name(repo)}-docs"


def derived_copyright_holder(owner: str) -> str:
    return owner


_GITHUB_REMOTE_RE = re.compile(
    r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+?)(?:\.git)?/?$",
)


def parse_github_remote_url(url: str) -> tuple[str, str] | None:
    """Parse owner/repo from a GitHub HTTPS or SSH remote URL."""
    match = _GITHUB_REMOTE_RE.search(url.strip())
    if match is None:
        return None
    return match.group("owner"), match.group("repo")


def detect_git_identity() -> tuple[str, str] | None:
    """Return owner/repo from ``git remote get-url origin``, or None if unavailable."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
            cwd=REPO_ROOT,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return parse_github_remote_url(result.stdout)


def is_upstream_template_identity(fields: IdentityFields) -> bool:
    return (
        fields.github_owner == TEMPLATE_DEFAULTS["github_owner"]
        and fields.github_repo == TEMPLATE_DEFAULTS["github_repo"]
    )


def template_init_prompt() -> str | None:
    """Devcontainer post-start hint when ``template.repo.toml`` still has upstream identity.

    Git remote is consulted only for this message — ``just init`` never reads it.
    """
    try:
        fields, _ = load_identity_fields()
    except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError):
        return None
    if not is_upstream_template_identity(fields):
        return None
    detected = detect_git_identity()
    if detected and detected != (fields.github_owner, fields.github_repo):
        owner, repo = detected
        return (
            f"Template identity: edit template.repo.toml for {owner}/{repo} "
            "(suggested from git remote), then run just init "
            "(see getting-started/github-setup)"
        )
    return (
        "Template identity: edit template.repo.toml for your org/repo, "
        "then run just init (see getting-started/github-setup)"
    )


@dataclass(frozen=True)
class IdentityOverrides:
    """CLI overrides for ``just init``. Each set field overrides ``template.repo.toml``."""

    github_owner: str | None = None
    github_repo: str | None = None
    pages_url: str | None = None
    docs_title: str | None = None
    navbar_title: str | None = None
    tagline: str | None = None
    python_package_name: str | None = None
    copyright_holder: str | None = None
    initial_version: str | None = None
    docs_npm_package_name: str | None = None

    def provided_fields(self) -> frozenset[str]:
        fields: set[str] = set()
        for name in (
            "github_owner",
            "github_repo",
            "pages_url",
            "docs_title",
            "navbar_title",
            "tagline",
            "python_package_name",
            "copyright_holder",
            "initial_version",
            "docs_npm_package_name",
        ):
            if getattr(self, name) is not None:
                fields.add(name)
        return frozenset(fields)


@dataclass(frozen=True)
class IdentityFields:
    github_owner: str
    github_repo: str
    pages_url: str | None = None
    docs_title: str | None = None
    navbar_title: str | None = None
    tagline: str | None = None
    python_package_name: str | None = None
    copyright_holder: str | None = None
    initial_version: str | None = None
    docs_npm_package_name: str | None = None


def _parse_identity_toml(data: dict[str, object]) -> tuple[IdentityFields, frozenset[str]]:
    explicit: set[str] = set()
    github_raw = data["github"]
    if not isinstance(github_raw, dict):
        msg = "template.repo.toml [github] section must be a table"
        raise TypeError(msg)
    owner = str(github_raw["owner"])
    repo = str(github_raw["repo"])

    pages = data.get("pages", {})
    pages_url: str | None = None
    if isinstance(pages, dict) and "url" in pages:
        pages_url = str(pages["url"]).rstrip("/")
        explicit.add("pages_url")

    docs = data.get("docs", {})
    docs_title: str | None = None
    navbar_title: str | None = None
    tagline: str | None = None
    docs_npm_package_name: str | None = None
    if isinstance(docs, dict):
        if "title" in docs:
            docs_title = str(docs["title"])
            explicit.add("docs_title")
        if "navbar_title" in docs:
            navbar_title = str(docs["navbar_title"])
            explicit.add("navbar_title")
        if "tagline" in docs:
            tagline = str(docs["tagline"])
            explicit.add("tagline")
        if "npm_package_name" in docs:
            docs_npm_package_name = str(docs["npm_package_name"])
            explicit.add("docs_npm_package_name")

    python = data.get("python", {})
    python_package_name: str | None = None
    if isinstance(python, dict) and "package_name" in python:
        python_package_name = str(python["package_name"])
        explicit.add("python_package_name")

    copyright_section = data.get("copyright", {})
    copyright_holder: str | None = None
    if isinstance(copyright_section, dict) and "holder" in copyright_section:
        copyright_holder = str(copyright_section["holder"])
        explicit.add("copyright_holder")

    init_section = data.get("init", {})
    initial_version: str | None = None
    if isinstance(init_section, dict) and "initial_version" in init_section:
        initial_version = str(init_section["initial_version"])
        explicit.add("initial_version")

    return (
        IdentityFields(
            github_owner=owner,
            github_repo=repo,
            pages_url=pages_url,
            docs_title=docs_title,
            navbar_title=navbar_title,
            tagline=tagline,
            python_package_name=python_package_name,
            copyright_holder=copyright_holder,
            initial_version=initial_version,
            docs_npm_package_name=docs_npm_package_name,
        ),
        frozenset(explicit),
    )


def merge_identity_fields(
    fields: IdentityFields,
    explicit: frozenset[str],
    overrides: IdentityOverrides | None,
) -> tuple[IdentityFields, frozenset[str]]:
    if overrides is None or not overrides.provided_fields():
        return fields, explicit

    merged_explicit = set(explicit)
    data = fields.__dict__.copy()
    for name in overrides.provided_fields():
        value = getattr(overrides, name)
        if value is not None:
            data[name] = value
            merged_explicit.add(name)
    return IdentityFields(**data), frozenset(merged_explicit)


def resolve_identity(fields: IdentityFields, explicit: frozenset[str]) -> "RepoIdentity":
    owner = fields.github_owner
    repo = fields.github_repo

    return RepoIdentity(
        github_owner=owner,
        github_repo=repo,
        pages_url=fields.pages_url if fields.pages_url is not None else derived_pages_url(owner),
        docs_title=fields.docs_title if fields.docs_title is not None else derived_docs_title(repo),
        navbar_title=fields.navbar_title
        if fields.navbar_title is not None
        else derived_navbar_title(repo),
        tagline=fields.tagline if fields.tagline is not None else DEFAULT_TAGLINE,
        python_package_name=fields.python_package_name
        if fields.python_package_name is not None
        else derived_package_name(repo),
        copyright_holder=fields.copyright_holder
        if fields.copyright_holder is not None
        else derived_copyright_holder(owner),
        initial_version=fields.initial_version
        if fields.initial_version is not None
        else DEFAULT_INITIAL_VERSION,
        docs_npm_package_name=fields.docs_npm_package_name or "",
    )


def _toml_value(value: str) -> str:
    return json.dumps(value)


def render_template_repo_toml(identity: "RepoIdentity", explicit: frozenset[str]) -> str:
    """Render template.repo.toml, omitting keys that match linked defaults."""
    owner = identity.github_owner
    repo = identity.github_repo
    pages_default = derived_pages_url(owner)
    package_default = derived_package_name(repo)
    docs_title_default = derived_docs_title(repo)
    navbar_default = derived_navbar_title(repo)
    copyright_default = derived_copyright_holder(owner)
    npm_default = derived_docs_npm_package_name(repo)

    lines = [
        "# Repository identity for this CAD-as-Code workspace.",
        "#",
        '# After "Use this template": edit this file for your org/repo, then run `just init`.',
        "# Or pass overrides without editing: `just init --owner acme --repo widget-cad`",
        "#",
        "# Linked defaults (omit keys to use them):",
        "#   [pages] url              -> https://<owner>.github.io",
        "#   [copyright] holder       -> [github] owner",
        "#   [python] package_name    -> repo name in kebab-case",
        "#   [docs] title             -> repo name",
        "#   [docs] navbar_title      -> repo name",
        "#   [docs] npm_package_name  -> <repo>-docs",
        "#   [docs] tagline           -> turnkey template tagline",
        "#   [init] initial_version   -> 0.0.0",
        "#",
        "# GitHub Actions workflows use ${{ github.repository }} automatically.",
        "",
        "[github]",
        f"owner = {_toml_value(owner)}",
        f"repo = {_toml_value(repo)}",
        "",
        "[pages]",
    ]
    if identity.pages_url.rstrip("/") != pages_default or "pages_url" in explicit:
        lines.append(f"url = {_toml_value(identity.pages_url.rstrip('/'))}")
    else:
        lines.append("# url defaults to https://<owner>.github.io")
    lines.append("")

    lines.append("[docs]")
    if identity.docs_title != docs_title_default or "docs_title" in explicit:
        lines.append(f"title = {_toml_value(identity.docs_title)}")
    else:
        lines.append("# title defaults to repo name")
    if identity.navbar_title != navbar_default or "navbar_title" in explicit:
        lines.append(f"navbar_title = {_toml_value(identity.navbar_title)}")
    else:
        lines.append("# navbar_title defaults to repo name")
    if identity.tagline != DEFAULT_TAGLINE or "tagline" in explicit:
        lines.append(f"tagline = {_toml_value(identity.tagline)}")
    else:
        lines.append(f"# tagline defaults to {_toml_value(DEFAULT_TAGLINE)}")
    resolved_npm = identity.resolved_docs_npm_package_name
    if resolved_npm != npm_default or "docs_npm_package_name" in explicit:
        lines.append(f"npm_package_name = {_toml_value(resolved_npm)}")
    else:
        lines.append("# npm_package_name defaults to <repo>-docs")
    lines.append("")

    lines.append("[python]")
    if identity.python_package_name != package_default or "python_package_name" in explicit:
        lines.append(f"package_name = {_toml_value(identity.python_package_name)}")
    else:
        lines.append("# package_name defaults to repo name in kebab-case")
    lines.append("")

    if identity.copyright_holder != copyright_default or "copyright_holder" in explicit:
        lines.extend(
            [
                "[copyright]",
                f"holder = {_toml_value(identity.copyright_holder)}",
                "",
            ]
        )

    lines.append("[init]")
    if identity.initial_version != DEFAULT_INITIAL_VERSION or "initial_version" in explicit:
        lines.append(f"initial_version = {_toml_value(identity.initial_version)}")
    else:
        lines.append(f"# initial_version defaults to {_toml_value(DEFAULT_INITIAL_VERSION)}")
    lines.append("")
    return "\n".join(lines)


def load_identity_from_data(data: dict[str, object]) -> "RepoIdentity":
    fields, explicit = _parse_identity_toml(data)
    return resolve_identity(fields, explicit)


def load_identity_fields(path: Path | None = None) -> tuple[IdentityFields, frozenset[str]]:
    config_path = CONFIG_PATH if path is None else path
    with config_path.open("rb") as handle:
        data = tomllib.load(handle)
    return _parse_identity_toml(data)


def prepare_identity(
    overrides: IdentityOverrides | None = None,
    *,
    config_path: Path | None = None,
) -> tuple["RepoIdentity", frozenset[str]]:
    path = CONFIG_PATH if config_path is None else config_path
    fields, explicit = load_identity_fields(path)
    fields, explicit = merge_identity_fields(fields, explicit, overrides)
    identity = resolve_identity(fields, explicit)
    return identity, explicit


def write_template_repo_toml(
    identity: "RepoIdentity",
    explicit: frozenset[str],
    *,
    dry_run: bool = False,
    config_path: Path | None = None,
) -> bool:
    path = CONFIG_PATH if config_path is None else config_path
    content = render_template_repo_toml(identity, explicit)
    if dry_run:
        existing = path.read_text(encoding="utf-8") if path.is_file() else ""
        return existing != content
    return write_if_changed(path, content)


@dataclass(frozen=True)
class RepoIdentity:
    github_owner: str
    github_repo: str
    pages_url: str
    docs_title: str
    navbar_title: str
    tagline: str
    python_package_name: str
    copyright_holder: str
    initial_version: str = DEFAULT_INITIAL_VERSION
    docs_npm_package_name: str = ""

    @property
    def github_repo_slug(self) -> str:
        return f"{self.github_owner}/{self.github_repo}"

    @property
    def github_url(self) -> str:
        return f"https://github.com/{self.github_repo_slug}"

    @property
    def base_url(self) -> str:
        return f"/{self.github_repo}/"

    @property
    def docs_site_url(self) -> str:
        host = self.pages_url.rstrip("/")
        return f"{host}/{self.github_repo}/"

    @property
    def pages_host(self) -> str:
        return self.pages_url.removeprefix("https://").removeprefix("http://").rstrip("/")

    @property
    def resolved_docs_npm_package_name(self) -> str:
        if self.docs_npm_package_name:
            return self.docs_npm_package_name
        return derived_docs_npm_package_name(self.github_repo)

    def to_dict(self) -> dict[str, str]:
        return {
            "github_owner": self.github_owner,
            "github_repo": self.github_repo,
            "pages_url": self.pages_url.rstrip("/"),
            "docs_title": self.docs_title,
            "navbar_title": self.navbar_title,
            "tagline": self.tagline,
            "python_package_name": self.python_package_name,
            "copyright_holder": self.copyright_holder,
            "initial_version": self.initial_version,
            "docs_npm_package_name": self.docs_npm_package_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> RepoIdentity:
        return cls(
            github_owner=data["github_owner"],
            github_repo=data["github_repo"],
            pages_url=data["pages_url"],
            docs_title=data["docs_title"],
            navbar_title=data["navbar_title"],
            tagline=data["tagline"],
            python_package_name=data["python_package_name"],
            copyright_holder=data["copyright_holder"],
            initial_version=data.get("initial_version", DEFAULT_INITIAL_VERSION),
            docs_npm_package_name=data.get("docs_npm_package_name", ""),
        )

    @classmethod
    def template_defaults(cls) -> RepoIdentity:
        return cls.from_dict(TEMPLATE_DEFAULTS)


def load_identity(path: Path | None = None) -> RepoIdentity:
    config_path = CONFIG_PATH if path is None else path
    with config_path.open("rb") as handle:
        data = tomllib.load(handle)
    return load_identity_from_data(data)


def load_applied_identity() -> RepoIdentity:
    if APPLIED_PATH.is_file():
        data = json.loads(APPLIED_PATH.read_text(encoding="utf-8"))
        return RepoIdentity.from_dict(data)
    return RepoIdentity.template_defaults()


def replacement_pairs(old: RepoIdentity, new: RepoIdentity) -> list[tuple[str, str]]:
    if old.to_dict() == new.to_dict():
        return []

    candidates = [
        (old.docs_site_url, new.docs_site_url),
        (old.github_url, new.github_url),
        (old.github_repo_slug, new.github_repo_slug),
        (old.pages_host, new.pages_host),
        (old.github_repo, new.github_repo),
        (old.github_owner, new.github_owner),
        (old.copyright_holder, new.copyright_holder),
        (old.docs_title, new.docs_title),
        (old.navbar_title, new.navbar_title),
        (old.tagline, new.tagline),
        (old.python_package_name, new.python_package_name),
    ]
    pairs: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for old_value, new_value in candidates:
        if not old_value or old_value == new_value:
            continue
        pair = (old_value, new_value)
        if pair in seen:
            continue
        seen.add(pair)
        pairs.append(pair)

    pairs.sort(key=lambda item: len(item[0]), reverse=True)
    return pairs


def iter_sync_files(*, docs_mode: DocsSyncMode) -> list[Path]:
    if docs_mode == "none":
        patterns = INTEGRATION_SYNC_GLOBS
    elif docs_mode == "init":
        patterns = INTEGRATION_SYNC_GLOBS + DOCS_SYNC_GLOBS
    else:
        patterns = ALL_SYNC_GLOBS

    files: list[Path] = []
    for pattern in patterns:
        files.extend(REPO_ROOT.glob(pattern))

    return sorted({path for path in files if path.is_file()})


def apply_text_replacements(content: str, pairs: list[tuple[str, str]]) -> str:
    updated = content
    for old_value, new_value in pairs:
        updated = updated.replace(old_value, new_value)
    return updated


def render_pages_badge_md(identity: RepoIdentity) -> str:
    """Markdown badge linking to the docs site; uses GitHub Pages deployment status."""
    badge_url = (
        f"https://img.shields.io/github/deployments/"
        f"{identity.github_repo_slug}/github-pages?label=docs"
    )
    return f"[![Documentation]({badge_url})]({identity.docs_site_url})"


def update_pages_badge_block(content: str, identity: RepoIdentity) -> str:
    block = f"{PAGES_BADGE_START}\n{render_pages_badge_md(identity)}\n{PAGES_BADGE_END}"
    pattern = re.compile(
        rf"{re.escape(PAGES_BADGE_START)}.*?{re.escape(PAGES_BADGE_END)}",
        re.DOTALL,
    )
    if pattern.search(content):
        return pattern.sub(block, content)
    return content


def render_repo_identity_ts(identity: RepoIdentity) -> str:
    return f"""// Auto-generated from ../template.repo.toml by `just template-apply` / `just init`. Do not edit manually.

export const repoIdentity = {{
  githubOwner: {json.dumps(identity.github_owner)},
  githubRepo: {json.dumps(identity.github_repo)},
  githubRepoSlug: {json.dumps(identity.github_repo_slug)},
  githubUrl: {json.dumps(identity.github_url)},
  pagesUrl: {json.dumps(identity.pages_url.rstrip("/"))},
  baseUrl: {json.dumps(identity.base_url)},
  docsSiteUrl: {json.dumps(identity.docs_site_url)},
  docsTitle: {json.dumps(identity.docs_title)},
  navbarTitle: {json.dumps(identity.navbar_title)},
  tagline: {json.dumps(identity.tagline)},
  copyrightHolder: {json.dumps(identity.copyright_holder)},
  pythonPackageName: {json.dumps(identity.python_package_name)},
}} as const;
"""


def update_pyproject_name(content: str, package_name: str) -> str:
    return re.sub(
        r'(?m)^name = ".*"$',
        f'name = "{package_name}"',
        content,
        count=1,
    )


def update_pyproject_version(content: str, version: str) -> str:
    return re.sub(
        r'(?m)^version = ".*"$',
        f'version = "{version}"',
        content,
        count=1,
    )


def render_release_please_manifest(version: str) -> str:
    return json.dumps({".": version}, indent=2) + "\n"


def update_package_json_name(content: str, package_name: str) -> str:
    return re.sub(
        r'(?m)^  "name": ".*",$',
        f'  "name": "{package_name}",',
        content,
        count=1,
    )


def write_if_changed(path: Path, content: str) -> bool:
    existing = path.read_text(encoding="utf-8") if path.is_file() else None
    if existing == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def _record_change(changed: list[str], path: Path) -> None:
    rel = str(path.relative_to(REPO_ROOT))
    if rel not in changed:
        changed.append(rel)


def _apply_generated_files(
    new_identity: RepoIdentity,
    *,
    dry_run: bool,
    changed: list[str],
) -> None:
    repo_identity_ts = render_repo_identity_ts(new_identity)
    if dry_run:
        if REPO_IDENTITY_TS.read_text(encoding="utf-8") != repo_identity_ts:
            _record_change(changed, REPO_IDENTITY_TS)
    elif write_if_changed(REPO_IDENTITY_TS, repo_identity_ts):
        _record_change(changed, REPO_IDENTITY_TS)

    pyproject = PYPROJECT_PATH.read_text(encoding="utf-8")
    updated_pyproject = update_pyproject_name(pyproject, new_identity.python_package_name)
    if updated_pyproject != pyproject:
        _record_change(changed, PYPROJECT_PATH)
        if not dry_run:
            PYPROJECT_PATH.write_text(updated_pyproject, encoding="utf-8")

    package_json = PACKAGE_JSON_PATH.read_text(encoding="utf-8")
    updated_package_json = update_package_json_name(
        package_json,
        new_identity.resolved_docs_npm_package_name,
    )
    if updated_package_json != package_json:
        _record_change(changed, PACKAGE_JSON_PATH)
        if not dry_run:
            PACKAGE_JSON_PATH.write_text(updated_package_json, encoding="utf-8")


def _apply_text_sync(
    pairs: list[tuple[str, str]],
    *,
    docs_mode: DocsSyncMode,
    update_readme_badge: bool,
    new_identity: RepoIdentity,
    dry_run: bool,
    changed: list[str],
) -> None:
    if pairs:
        for path in iter_sync_files(docs_mode=docs_mode):
            original = path.read_text(encoding="utf-8")
            updated = apply_text_replacements(original, pairs)
            if updated != original:
                _record_change(changed, path)
                if not dry_run:
                    path.write_text(updated, encoding="utf-8")

    if update_readme_badge and README_PATH.is_file():
        readme = README_PATH.read_text(encoding="utf-8")
        updated_readme = update_pages_badge_block(readme, new_identity)
        if updated_readme != readme:
            _record_change(changed, README_PATH)
            if not dry_run:
                README_PATH.write_text(updated_readme, encoding="utf-8")


def _write_applied_identity(new_identity: RepoIdentity, *, dry_run: bool) -> None:
    if dry_run:
        return
    APPLIED_PATH.write_text(
        json.dumps(new_identity.to_dict(), indent=2) + "\n",
        encoding="utf-8",
    )


def apply_template_identity(*, dry_run: bool = False, sync_docs: bool = True) -> list[str]:
    """Apply identity from template.repo.toml. Returns paths that changed."""
    new_identity = load_identity()
    old_identity = load_applied_identity()
    pairs = replacement_pairs(old_identity, new_identity)
    changed: list[str] = []

    _apply_generated_files(new_identity, dry_run=dry_run, changed=changed)
    _apply_text_sync(
        pairs,
        docs_mode="template" if sync_docs else "none",
        update_readme_badge=sync_docs,
        new_identity=new_identity,
        dry_run=dry_run,
        changed=changed,
    )
    _write_applied_identity(new_identity, dry_run=dry_run)

    return changed


def reset_project_versions(
    identity: RepoIdentity,
    *,
    dry_run: bool = False,
) -> list[str]:
    """Reset release-tracking version files to the configured initial version."""
    changed: list[str] = []
    version = identity.initial_version

    pyproject = PYPROJECT_PATH.read_text(encoding="utf-8")
    updated_pyproject = update_pyproject_version(pyproject, version)
    if updated_pyproject != pyproject:
        _record_change(changed, PYPROJECT_PATH)
        if not dry_run:
            PYPROJECT_PATH.write_text(updated_pyproject, encoding="utf-8")

    manifest = render_release_please_manifest(version)
    if dry_run:
        existing = (
            RELEASE_PLEASE_MANIFEST_PATH.read_text(encoding="utf-8")
            if RELEASE_PLEASE_MANIFEST_PATH.is_file()
            else ""
        )
        if existing != manifest:
            _record_change(changed, RELEASE_PLEASE_MANIFEST_PATH)
    elif write_if_changed(RELEASE_PLEASE_MANIFEST_PATH, manifest):
        _record_change(changed, RELEASE_PLEASE_MANIFEST_PATH)

    if dry_run:
        existing_changelog = (
            CHANGELOG_PATH.read_text(encoding="utf-8") if CHANGELOG_PATH.is_file() else ""
        )
        if existing_changelog != INITIAL_CHANGELOG:
            _record_change(changed, CHANGELOG_PATH)
    elif write_if_changed(CHANGELOG_PATH, INITIAL_CHANGELOG):
        _record_change(changed, CHANGELOG_PATH)

    return changed


def init_project(
    *,
    dry_run: bool = False,
    sync_docs: bool = False,
    overrides: IdentityOverrides | None = None,
) -> list[str]:
    """Apply identity from ``template.repo.toml`` plus optional CLI overrides.

    Resets semver to ``[init] initial_version``, updates integration files, and
    optionally rewrites README/docs. Overrides are merged back into the TOML.
    """
    new_identity, explicit = prepare_identity(overrides)
    old_identity = RepoIdentity.template_defaults()
    pairs = replacement_pairs(old_identity, new_identity)
    changed: list[str] = []

    if write_template_repo_toml(new_identity, explicit, dry_run=dry_run):
        _record_change(changed, CONFIG_PATH)

    changed.extend(reset_project_versions(new_identity, dry_run=dry_run))
    _apply_generated_files(new_identity, dry_run=dry_run, changed=changed)
    _apply_text_sync(
        pairs,
        docs_mode="init" if sync_docs else "none",
        update_readme_badge=sync_docs,
        new_identity=new_identity,
        dry_run=dry_run,
        changed=changed,
    )
    _write_applied_identity(new_identity, dry_run=dry_run)

    return changed
