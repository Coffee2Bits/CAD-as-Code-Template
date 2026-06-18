#!/usr/bin/env python3
"""CLI entry point for `just init`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.template_identity import IdentityOverrides, init_project, prepare_identity


def _optional(value: str | None) -> str | None:
    if value is None or value == "":
        return None
    return value


def _build_overrides(args: argparse.Namespace) -> IdentityOverrides:
    return IdentityOverrides(
        github_owner=_optional(args.owner),
        github_repo=_optional(args.repo),
        pages_url=_optional(args.pages_url),
        docs_title=_optional(args.docs_title),
        navbar_title=_optional(args.navbar_title),
        tagline=_optional(args.tagline),
        python_package_name=_optional(args.package_name),
        copyright_holder=_optional(args.copyright),
        initial_version=_optional(args.initial_version),
        docs_npm_package_name=_optional(args.npm_package_name),
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Initialize the repo from template.repo.toml (optional CLI overrides per field)."
        ),
    )
    parser.add_argument("--owner", help="GitHub org or user ([github] owner).")
    parser.add_argument("--repo", help="GitHub repository name ([github] repo).")
    parser.add_argument(
        "--pages-url",
        help="GitHub Pages host URL ([pages] url; default https://<owner>.github.io).",
    )
    parser.add_argument(
        "--docs-title", help="Docusaurus site title ([docs] title; default repo name)."
    )
    parser.add_argument(
        "--navbar-title",
        help="Navbar label ([docs] navbar_title; default repo name).",
    )
    parser.add_argument("--tagline", help="Docusaurus tagline ([docs] tagline).")
    parser.add_argument(
        "--package-name",
        help="pyproject.toml [project] name ([python] package_name; default repo kebab-case).",
    )
    parser.add_argument(
        "--copyright",
        help="Docs footer copyright holder ([copyright] holder; default owner).",
    )
    parser.add_argument(
        "--initial-version",
        help="Semver for pyproject.toml and release-please ([init] initial_version).",
    )
    parser.add_argument(
        "--npm-package-name",
        help="website/package.json name ([docs] npm_package_name; default <repo>-docs).",
    )
    parser.add_argument(
        "--sync-docs",
        action="store_true",
        default=True,
        help="Rewrite README, docs pages, and related markdown (default: on).",
    )
    parser.add_argument(
        "--no-sync-docs",
        action="store_false",
        dest="sync_docs",
        help="Skip README and docs markdown (integration files only).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print files that would change without writing.",
    )
    args = parser.parse_args()

    overrides = _build_overrides(args)
    identity, _explicit = prepare_identity(overrides)
    changed = init_project(dry_run=args.dry_run, sync_docs=args.sync_docs, overrides=overrides)

    if args.dry_run:
        if changed:
            print("Would update:")
            for path in changed:
                print(f"  {path}")
        else:
            print("No changes needed.")
        return 0

    if changed:
        print(f"Initialized {identity.github_repo_slug}:")
        for path in changed:
            print(f"  updated {path}")
        if not args.sync_docs:
            print(
                "Skipped README and docs — re-run `just init` or `just template-apply` to rebrand prose."
            )
    else:
        print(f"Already initialized for {identity.github_repo_slug}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
