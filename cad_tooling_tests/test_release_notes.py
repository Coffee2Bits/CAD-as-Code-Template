from pathlib import Path
from types import SimpleNamespace

from cad_tooling.release_notes import ReleaseAsset, render_release_body


def _fake_artifact(name: str, *, short_desc: str | None = None, desc: str | None = None):
    return SimpleNamespace(name=name, short_desc=short_desc, desc=desc)


def test_artifact_description_prefers_short_desc():
    artifact = _fake_artifact("part", short_desc="Short", desc="Long description")
    body = render_release_body(
        "acme/repo",
        "v1.0.0",
        [ReleaseAsset(artifact, Path("part.stl"), Path("part.png"))],
    )
    assert "Short" in body
    assert "Long description" not in body


def test_artifact_description_falls_back_to_desc():
    artifact = _fake_artifact("part", desc="Fallback description")
    body = render_release_body(
        "acme/repo",
        "v1.0.0",
        [ReleaseAsset(artifact, Path("part.stl"), Path("part.png"))],
    )
    assert "Fallback description" in body


def test_artifact_description_falls_back_to_name():
    artifact = _fake_artifact("widget")
    body = render_release_body(
        "acme/repo",
        "v1.0.0",
        [ReleaseAsset(artifact, Path("widget.stl"), Path("widget.png"))],
    )
    assert "## widget" in body
    assert body.count("widget") >= 2
