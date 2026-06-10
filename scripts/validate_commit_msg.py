"""Validate git commit messages against this repo's Conventional Commits rules."""

from __future__ import annotations

import re
import sys
from pathlib import Path

COMMIT_TYPES: frozenset[str] = frozenset(
    {
        "feat",
        "fix",
        "deps",
        "docs",
        "chore",
        "build",
        "ci",
        "refactor",
        "test",
        "style",
        "perf",
    }
)

AUTOSQUASH_PREFIX = re.compile(r"^(?:fixup!|squash!)\s+")
COMMIT_SUBJECT = re.compile(
    rf"^(?P<type>{'|'.join(sorted(COMMIT_TYPES))})"
    r"(?P<scope>\([^)]+\))?"
    r"(?P<breaking>!)?"
    r": (?P<description>.+)$"
)


def is_skipped_commit_message(message: str) -> bool:
    """Return True for merge/revert subjects that should not be validated."""
    first_line = message.splitlines()[0].strip() if message else ""
    return first_line.startswith(("Merge ", "Revert "))


def validate_subject(subject: str) -> str | None:
    """Return an error string when invalid, otherwise None."""
    subject = AUTOSQUASH_PREFIX.sub("", subject.strip())
    if not subject:
        return "commit subject is empty"

    if COMMIT_SUBJECT.match(subject) is None:
        allowed = ", ".join(sorted(COMMIT_TYPES))
        return (
            "commit subject must use Conventional Commits "
            f"(<type>[scope][!]: description). Allowed types: {allowed}"
        )
    return None


def validate_commit_message(message: str) -> str | None:
    """Return an error string when invalid, otherwise None."""
    if is_skipped_commit_message(message):
        return None

    first_line = message.splitlines()[0] if message else ""
    return validate_subject(first_line)


def main(argv: list[str] | None = None) -> int:
    paths = argv if argv is not None else sys.argv[1:]
    if not paths:
        print("usage: validate_commit_msg.py <commit-msg-file>", file=sys.stderr)
        return 1

    for path in paths:
        message = Path(path).read_text(encoding="utf-8")
        error = validate_commit_message(message)
        if error is not None:
            print(error, file=sys.stderr)
            print("Example: feat(sphere): add embossed label", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
