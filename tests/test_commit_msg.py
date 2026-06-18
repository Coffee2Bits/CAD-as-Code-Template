"""Tests for Conventional Commit message validation."""

import pytest

from scripts.validate_commit_msg import validate_commit_message, validate_subject

pytestmark = pytest.mark.unit


def test_valid_releasable_subjects() -> None:
    assert validate_subject("feat(sphere): add embossed label") is None
    assert validate_subject("fix(render): fit wide assemblies") is None
    assert validate_subject("deps: bump makerrepo-cli to 0.4.0") is None
    assert validate_subject("docs: update readme release section") is None


def test_valid_non_releasable_subjects() -> None:
    assert validate_subject("chore: reorganize cad_tooling modules") is None
    assert validate_subject("ci: pin dagger version in workflow") is None
    assert validate_subject("test(sphere): assert embossed text bbox") is None


def test_valid_breaking_and_autosquash_subjects() -> None:
    assert validate_subject("feat(export)!: drop stl from default bundle") is None
    assert validate_subject("fixup! feat(sphere): add embossed label") is None
    assert validate_subject("squash! fix(render): fit margin") is None


def test_invalid_subjects() -> None:
    assert validate_subject("Added 3d party part libs") is not None
    assert validate_subject("feat:") is not None
    assert validate_subject("feature: add sphere") is not None


def test_merge_and_revert_messages_are_skipped() -> None:
    merge = "Merge branch 'feature' into main\n"
    revert = 'Revert "feat(sphere): add embossed label"\n'
    assert validate_commit_message(merge) is None
    assert validate_commit_message(revert) is None
