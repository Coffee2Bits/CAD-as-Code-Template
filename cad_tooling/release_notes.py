"""GitHub Release notes for exported MakerRepo artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cad_tooling.render_config import (
    RenderConfig,
    render_output_filename,
    render_preview_label,
    resolve_render_configs,
)
from mr.data_types import Artifact


@dataclass(frozen=True)
class RenderPreview:
    """One exported PNG preview paired with its @render annotation label."""

    label: str
    png_path: Path


@dataclass(frozen=True)
class ReleaseAsset:
    artifact: Artifact
    stl_path: Path
    render_previews: tuple[RenderPreview, ...]

    @property
    def png_paths(self) -> tuple[Path, ...]:
        """PNG paths in @render declaration order."""
        return tuple(preview.png_path for preview in self.render_previews)

    @property
    def png_path(self) -> Path:
        """Primary preview image (first configured render)."""
        return self.render_previews[0].png_path

    @classmethod
    def from_png_paths(
        cls,
        artifact: Artifact,
        stl_path: Path,
        png_paths: tuple[Path, ...] | list[Path],
        *,
        render_overrides: RenderConfig | None = None,
    ) -> ReleaseAsset:
        """Build a release asset by pairing exported PNGs with @render labels."""
        previews = _render_previews_for_artifact(
            artifact,
            tuple(png_paths),
            render_overrides=render_overrides,
        )
        return cls(artifact=artifact, stl_path=stl_path, render_previews=previews)


def release_download_url(repo: str, tag: str, filename: str) -> str:
    """Build a GitHub Release asset download URL."""
    return f"https://github.com/{repo}/releases/download/{tag}/{filename}"


def _artifact_description(artifact: Artifact) -> str:
    return artifact.short_desc or artifact.desc or artifact.name


def _fallback_preview_label(artifact_name: str, png_path: Path) -> str:
    token = png_path.stem.removeprefix(f"{artifact_name}_")
    return token.replace("_", " ") if token else png_path.name


def _render_previews_for_artifact(
    artifact: Artifact,
    png_paths: tuple[Path, ...],
    *,
    render_overrides: RenderConfig | None = None,
) -> tuple[RenderPreview, ...]:
    """Pair exported PNG files with labels from @render annotations."""
    configs = resolve_render_configs(
        artifact_func=artifact.func,
        overrides=render_overrides,
    )
    if configs:
        previews: list[RenderPreview] = []
        missing: list[tuple[str, str]] = []
        for config in configs:
            expected_name = render_output_filename(artifact.name, config)
            png_path = next((path for path in png_paths if path.name == expected_name), None)
            if png_path is None:
                missing.append((render_preview_label(config), expected_name))
                continue
            previews.append(RenderPreview(label=render_preview_label(config), png_path=png_path))
        if not missing:
            return tuple(previews)
        if len(png_paths) == 1 and png_paths[0].name == f"{artifact.name}.png":
            return (
                RenderPreview(
                    label=_fallback_preview_label(artifact.name, png_paths[0]),
                    png_path=png_paths[0],
                ),
            )
        label, expected_name = missing[0]
        raise FileNotFoundError(
            f"Missing release preview for artifact '{artifact.name}' render "
            f"'{label}': {expected_name}"
        )

    return tuple(
        RenderPreview(label=_fallback_preview_label(artifact.name, png_path), png_path=png_path)
        for png_path in png_paths
    )


def _render_preview_images(
    repo: str,
    tag: str,
    artifact_name: str,
    render_previews: tuple[RenderPreview, ...],
) -> list[str]:
    """Render one markdown image or a side-by-side HTML row for multiple previews."""
    if len(render_previews) == 1:
        preview = render_previews[0]
        png_url = release_download_url(repo, tag, preview.png_path.name)
        return [f"![{preview.label}]({png_url})"]

    image_tags = []
    for preview in render_previews:
        png_url = release_download_url(repo, tag, preview.png_path.name)
        image_tags.append(f'<img src="{png_url}" alt="{preview.label}" width="390" />')
    return ['<p align="center">' + "\n".join(image_tags) + "</p>"]


def _render_preview_links(
    repo: str,
    tag: str,
    render_previews: tuple[RenderPreview, ...],
) -> list[str]:
    """Markdown download links for each @render preview."""
    lines = ["Previews:"]
    for preview in render_previews:
        png_url = release_download_url(repo, tag, preview.png_path.name)
        lines.append(f"- [{preview.label}]({png_url}) (`{preview.png_path.name}`)")
    return lines


def _release_asset_sort_key(asset: ReleaseAsset) -> tuple[int, str]:
    cover = bool(getattr(asset.artifact, "cover", False))
    return (0 if cover else 1, asset.artifact.name)


def render_release_body(repo: str, tag: str, assets: list[ReleaseAsset]) -> str:
    """Render markdown for a GitHub Release listing each artifact with previews."""
    lines = [
        "# Release artifacts",
        "",
        "Parametric CAD models exported as STL from `@artifact` functions with `@render` previews.",
        "Each entry includes OCCT preview renders and a downloadable mesh file.",
        "",
    ]

    for asset in sorted(assets, key=_release_asset_sort_key):
        name = asset.artifact.name
        stl_name = asset.stl_path.name
        stl_url = release_download_url(repo, tag, stl_name)

        lines.extend([f"## {name}", ""])
        lines.extend(_render_preview_images(repo, tag, name, asset.render_previews))
        lines.extend(
            [
                "",
                _artifact_description(asset.artifact),
                "",
            ]
        )
        if len(asset.render_previews) > 1:
            lines.extend(_render_preview_links(repo, tag, asset.render_previews))
            lines.append("")
        elif len(asset.render_previews) == 1:
            preview = asset.render_previews[0]
            png_url = release_download_url(repo, tag, preview.png_path.name)
            lines.append(f"[{preview.label}]({png_url}) (`{preview.png_path.name}`)")
            lines.append("")
        lines.extend([f"[{stl_name}]({stl_url})", ""])

    return "\n".join(lines).rstrip() + "\n"


def collect_release_assets(
    assets_dir: Path,
    root: Path | None = None,
    *,
    names: tuple[str, ...] | None = None,
    render_overrides: RenderConfig | None = None,
) -> list[ReleaseAsset]:
    """Pair discovered artifacts with exported STL and PNG files.

    When ``names`` is omitted, every discovered artifact must have release files
    in ``assets_dir``. Pass ``names`` to validate only specific artifacts — use
    this in tests that export a subset so other published parts do not break
    unrelated assertions.
    """
    from cad_tooling.export import list_release_artifacts

    discovered = list_release_artifacts(root)
    if names is not None:
        by_name = {artifact.name: artifact for artifact in discovered}
        missing = [name for name in names if name not in by_name]
        if missing:
            raise ValueError(f"Artifact(s) not discovered: {', '.join(missing)}")
        targets = [by_name[name] for name in names]
    else:
        targets = discovered

    assets: list[ReleaseAsset] = []
    for artifact in sorted(targets, key=lambda item: item.name):
        stl_path = assets_dir / f"{artifact.name}.stl"
        if not stl_path.is_file():
            raise FileNotFoundError(
                f"Missing release STL for artifact '{artifact.name}': {stl_path}"
            )

        png_paths = sorted(assets_dir.glob(f"{artifact.name}_*.png"))
        if not png_paths:
            legacy_png = assets_dir / f"{artifact.name}.png"
            if legacy_png.is_file():
                png_paths = [legacy_png]
        if not png_paths:
            raise FileNotFoundError(
                f"Missing release preview for artifact '{artifact.name}': "
                f"{assets_dir / f'{artifact.name}_*.png'}"
            )
        assets.append(
            ReleaseAsset.from_png_paths(
                artifact,
                stl_path,
                tuple(png_paths),
                render_overrides=render_overrides,
            )
        )
    if not assets:
        raise RuntimeError("No @render-decorated artifacts discovered for release notes")
    return assets
