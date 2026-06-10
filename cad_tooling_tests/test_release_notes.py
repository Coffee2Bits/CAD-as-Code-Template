from pathlib import Path
from types import SimpleNamespace

from cad_tooling.release_notes import (
    ReleaseAsset,
    RenderPreview,
    _render_preview_images,
    _render_preview_links,
    render_release_body,
)


def _fake_artifact(name: str, *, short_desc: str | None = None, desc: str | None = None):
    return SimpleNamespace(name=name, short_desc=short_desc, desc=desc)


def test_artifact_description_prefers_short_desc():
    artifact = _fake_artifact("part", short_desc="Short", desc="Long description")
    body = render_release_body(
        "acme/repo",
        "v1.0.0",
        [
            ReleaseAsset(
                artifact,
                Path("part.stl"),
                (RenderPreview("iso (800×600)", Path("part_iso_800x600.png")),),
            )
        ],
    )
    assert "Short" in body
    assert "Long description" not in body


def test_artifact_description_falls_back_to_desc():
    artifact = _fake_artifact("part", desc="Fallback description")
    body = render_release_body(
        "acme/repo",
        "v1.0.0",
        [
            ReleaseAsset(
                artifact,
                Path("part.stl"),
                (RenderPreview("iso (800×600)", Path("part_iso_800x600.png")),),
            )
        ],
    )
    assert "Fallback description" in body


def test_render_preview_images_single_uses_markdown():
    previews = (RenderPreview("front (800×600)", Path("widget_front_800x600.png")),)
    lines = _render_preview_images("acme/repo", "v1.0.0", "widget", previews)
    assert len(lines) == 1
    assert lines[0].startswith("![front (800×600)]")


def test_render_preview_images_multiple_uses_side_by_side_html():
    previews = (
        RenderPreview("front (800×600)", Path("sphere_front_800x600.png")),
        RenderPreview("iso (800×600)", Path("sphere_iso_800x600.png")),
    )
    lines = _render_preview_images("acme/repo", "v1.0.0", "sphere", previews)
    assert len(lines) == 1
    assert lines[0].startswith('<p align="center">')
    assert "sphere_front_800x600.png" in lines[0]
    assert "sphere_iso_800x600.png" in lines[0]


def test_render_preview_links_lists_each_annotation():
    previews = (
        RenderPreview("front (800×600)", Path("sphere_front_800x600.png")),
        RenderPreview("iso (800×600)", Path("sphere_iso_800x600.png")),
    )
    lines = _render_preview_links("acme/repo", "v1.0.0", previews)
    assert lines[0] == "Previews:"
    assert "sphere_front_800x600.png" in lines[1]
    assert "sphere_iso_800x600.png" in lines[2]


def test_artifact_description_falls_back_to_name():
    artifact = _fake_artifact("widget")
    body = render_release_body(
        "acme/repo",
        "v1.0.0",
        [
            ReleaseAsset(
                artifact,
                Path("widget.stl"),
                (RenderPreview("iso (800×600)", Path("widget_iso_800x600.png")),),
            )
        ],
    )
    assert "## widget" in body
    assert body.count("widget") >= 2
