#!/usr/bin/env python3
"""CLI entry point for `just template-apply`."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.template_identity import apply_template_identity, load_identity


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply template.repo.toml across the workspace.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print files that would change without writing.",
    )
    parser.add_argument(
        "--integration-only",
        action="store_true",
        help="Skip README and docs markdown (same scope as `just init` without sync_docs).",
    )
    args = parser.parse_args()

    identity = load_identity()
    changed = apply_template_identity(
        dry_run=args.dry_run,
        sync_docs=not args.integration_only,
    )

    if args.dry_run:
        if changed:
            print("Would update:")
            for path in changed:
                print(f"  {path}")
        else:
            print("No changes needed.")
        return 0

    if changed:
        print(f"Applied {identity.github_repo_slug} from template.repo.toml:")
        for path in changed:
            print(f"  updated {path}")
    else:
        print(f"Already up to date for {identity.github_repo_slug}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
