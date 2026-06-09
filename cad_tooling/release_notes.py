"""GitHub Release notes for exported MakerRepo artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from mr.data_types import Artifact


@dataclass(frozen=True)
class ReleaseAsset:
    artifact: Artifact
    stl_path: Path
    png_path: Path


def release_download_url(repo: str, tag: str, filename: str) -> str:
    """Build a GitHub Release asset download URL."""
    return f"https://github.com/{repo}/releases/download/{tag}/{filename}"


def _artifact_description(artifact: Artifact) -> str:
    return artifact.short_desc or artifact.desc or artifact.name


def render_release_body(repo: str, tag: str, assets: list[ReleaseAsset]) -> str:
    """Render markdown for a GitHub Release listing each artifact with previews."""
    lines = [
        "# Release artifacts",
        "",
        "Parametric CAD models exported as STL from `@artifact` functions in this repository.",
        "Each entry includes an OCCT preview render and a downloadable mesh file.",
        "",
    ]

    for asset in sorted(assets, key=lambda item: item.artifact.name):
        name = asset.artifact.name
        stl_name = asset.stl_path.name
        png_name = asset.png_path.name
        stl_url = release_download_url(repo, tag, stl_name)
        png_url = release_download_url(repo, tag, png_name)

        lines.extend(
            [
                f"## {name}",
                "",
                f"![{name}]({png_url})",
                "",
                _artifact_description(asset.artifact),
                "",
                f"[{stl_name}]({stl_url})",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def collect_release_assets(assets_dir: Path, root: Path | None = None) -> list[ReleaseAsset]:
    """Pair discovered artifacts with exported STL and PNG files."""
    from cad_tooling.export import list_artifacts

    assets: list[ReleaseAsset] = []
    for artifact in sorted(list_artifacts(root), key=lambda item: item.name):
        stl_path = assets_dir / f"{artifact.name}.stl"
        png_path = assets_dir / f"{artifact.name}.png"
        if not stl_path.is_file():
            raise FileNotFoundError(
                f"Missing release STL for artifact '{artifact.name}': {stl_path}"
            )
        if not png_path.is_file():
            raise FileNotFoundError(
                f"Missing release preview for artifact '{artifact.name}': {png_path}"
            )
        assets.append(ReleaseAsset(artifact=artifact, stl_path=stl_path, png_path=png_path))
    if not assets:
        raise RuntimeError("No artifacts discovered for release notes")
    return assets
