"""Load and apply template repository identity from template.repo.toml."""

from __future__ import annotations

import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "template.repo.toml"
APPLIED_PATH = REPO_ROOT / ".template.repo.applied.json"
REPO_IDENTITY_TS = REPO_ROOT / "website" / "repo-identity.ts"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"

SYNC_GLOBS = (
    "README.md",
    "AGENTS.md",
    "CHANGELOG.md",
    "cad_tooling/README.md",
    ".github/GITHUB_SETUP.md",
    "website/README.md",
    "website/docs/**/*.md",
)

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
        )


def load_identity(path: Path = CONFIG_PATH) -> RepoIdentity:
    with path.open("rb") as handle:
        data = tomllib.load(handle)

    github = data["github"]
    owner = str(github["owner"])
    repo = str(github["repo"])
    pages = data.get("pages", {})
    docs = data.get("docs", {})
    python = data.get("python", {})
    copyright_section = data.get("copyright", {})

    return RepoIdentity(
        github_owner=owner,
        github_repo=repo,
        pages_url=str(pages.get("url", f"https://{owner.lower()}.github.io")).rstrip("/"),
        docs_title=str(docs.get("title", "CAD-as-Code Template")),
        navbar_title=str(docs.get("navbar_title", "CAD-as-Code")),
        tagline=str(docs.get("tagline", "Turnkey parametric CAD in Python")),
        python_package_name=str(python.get("package_name", "programmatic-cad-workspace")),
        copyright_holder=str(copyright_section.get("holder", owner)),
    )


def load_applied_identity() -> RepoIdentity:
    if APPLIED_PATH.is_file():
        data = json.loads(APPLIED_PATH.read_text(encoding="utf-8"))
        return RepoIdentity.from_dict(data)
    return RepoIdentity.from_dict(TEMPLATE_DEFAULTS)


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


def iter_sync_files() -> list[Path]:
    files: list[Path] = []
    for pattern in SYNC_GLOBS:
        files.extend(REPO_ROOT.glob(pattern))
    return sorted({path for path in files if path.is_file()})


def apply_text_replacements(content: str, pairs: list[tuple[str, str]]) -> str:
    updated = content
    for old_value, new_value in pairs:
        updated = updated.replace(old_value, new_value)
    return updated


def render_repo_identity_ts(identity: RepoIdentity) -> str:
    return f"""// Auto-generated from ../template.repo.toml by `just template-apply`. Do not edit manually.

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


def write_if_changed(path: Path, content: str) -> bool:
    existing = path.read_text(encoding="utf-8") if path.is_file() else None
    if existing == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def apply_template_identity(*, dry_run: bool = False) -> list[str]:
    """Apply identity from template.repo.toml. Returns paths that changed."""
    new_identity = load_identity()
    old_identity = load_applied_identity()
    pairs = replacement_pairs(old_identity, new_identity)
    changed: list[str] = []

    repo_identity_ts = render_repo_identity_ts(new_identity)
    if dry_run:
        if REPO_IDENTITY_TS.read_text(encoding="utf-8") != repo_identity_ts:
            changed.append(str(REPO_IDENTITY_TS.relative_to(REPO_ROOT)))
    elif write_if_changed(REPO_IDENTITY_TS, repo_identity_ts):
        changed.append(str(REPO_IDENTITY_TS.relative_to(REPO_ROOT)))

    pyproject = PYPROJECT_PATH.read_text(encoding="utf-8")
    updated_pyproject = update_pyproject_name(pyproject, new_identity.python_package_name)
    if updated_pyproject != pyproject:
        rel = str(PYPROJECT_PATH.relative_to(REPO_ROOT))
        changed.append(rel)
        if not dry_run:
            PYPROJECT_PATH.write_text(updated_pyproject, encoding="utf-8")

    if pairs:
        for path in iter_sync_files():
            original = path.read_text(encoding="utf-8")
            updated = apply_text_replacements(original, pairs)
            if updated != original:
                rel = str(path.relative_to(REPO_ROOT))
                changed.append(rel)
                if not dry_run:
                    path.write_text(updated, encoding="utf-8")

    if not dry_run:
        APPLIED_PATH.write_text(
            json.dumps(new_identity.to_dict(), indent=2) + "\n",
            encoding="utf-8",
        )

    return changed
