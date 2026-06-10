"""MakerRepo-aware and ad-hoc export helpers."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Literal

from build123d import Compound, Mesher, Part, export_brep, export_gltf, export_step, export_stl
from cad_tooling.release_notes import ReleaseAsset, RenderPreview
from cad_tooling.render_config import render_output_filename, render_preview_label
from cad_tooling.render import render_stl
from cad_tooling.render_config import (
    RenderConfig,
    add_render_config_arguments,
    render_config_from_namespace,
    resolve_render_configs,
)
from mr import Result
from mr.data_types import Artifact, Customizable
from mr.registry import Registry, collect
from mr.utils import (
    apply_pythonpaths,
    find_python_modules,
    find_python_packages,
    load_module,
    load_repo_config,
)

logger = logging.getLogger(__name__)

ExportFormat = Literal["step", "stl", "brep", "gltf", "3mf"]
EXPORT_FORMATS: tuple[ExportFormat, ...] = ("step", "stl", "brep", "gltf", "3mf")
DEFAULT_EXPORT_FORMAT: ExportFormat = "step"


def _scan_onerror(name: str) -> None:
    exc_type, exc, _ = sys.exc_info()
    if exc_type is not None and issubclass(exc_type, ImportError):
        logger.warning("ImportError while importing %s: %s", name, exc)
        return
    raise


def load_registry(root: Path | None = None) -> Registry:
    """Discover @artifact / @customizable functions under a repo root."""
    cwd = (root or Path.cwd()).resolve()
    packages = find_python_packages(cwd)
    modules = find_python_modules(cwd)

    path_inserted = False
    cwd_str = str(cwd)
    if cwd_str not in sys.path:
        path_inserted = True
        sys.path.insert(0, cwd_str)
    try:
        config = load_repo_config(cwd / ".makerrepo" / "config.yaml")
        with apply_pythonpaths(config, repo_root=cwd):
            return collect(
                [load_module(str(source)) for source in packages + modules],
                onerror=_scan_onerror,
            )
    finally:
        if path_inserted:
            del sys.path[0]


def _items_flat(registry: Registry, attr: str) -> list[tuple[str, str, Artifact | Customizable]]:
    items_dict = getattr(registry, attr, {})
    return [
        (module_name, item_name, item)
        for module_name, module_items in items_dict.items()
        for item_name, item in module_items.items()
    ]


def list_artifacts(root: Path | None = None) -> list[Artifact]:
    registry = load_registry(root)
    return [item for _, _, item in _items_flat(registry, "artifacts")]


def list_generators(root: Path | None = None) -> list[Customizable]:
    registry = load_registry(root)
    return [item for _, _, item in _items_flat(registry, "customizables")]


def _resolve_items(
    registry: Registry,
    names: tuple[str, ...] | None,
    attr: str,
    kind: str,
) -> list[Artifact | Customizable]:
    flat = _items_flat(registry, attr)
    if not flat:
        raise ValueError(f"No {kind}s found in repository")

    if not names:
        return [item for _, _, item in flat]

    by_module = getattr(registry, attr, {})
    name_to_items: dict[str, list[tuple[str, Artifact | Customizable]]] = {}
    for module_name, item_name, item in flat:
        name_to_items.setdefault(item_name, []).append((module_name, item))

    resolved: list[Artifact | Customizable] = []
    for name in names:
        if "/" in name:
            module_name, item_name = name.split("/", 1)
            module_items = by_module.get(module_name, {})
            if item_name not in module_items:
                raise ValueError(f"{kind.capitalize()} not found: {name}")
            resolved.append(module_items[item_name])
            continue

        candidates = name_to_items.get(name, [])
        if not candidates:
            raise ValueError(f"{kind.capitalize()} not found: {name}")
        if len(candidates) > 1:
            options = ", ".join(
                f"{module}/{getattr(item, 'name', '')}" for module, item in candidates
            )
            raise ValueError(f"Ambiguous {kind} name '{name}'; use module/{kind}_name: {options}")
        resolved.append(candidates[0][1])
    return resolved


def _artifact_label(artifact: Artifact) -> str:
    return f"{artifact.module}/{artifact.name}"


def realize_artifact(artifact: Artifact, *, use_versioned: bool = False):
    """Build geometry for a MakerRepo artifact."""
    value = artifact.func()
    if isinstance(value, Result):
        if use_versioned:
            if value.versioned is None:
                raise ValueError(f"Versioned model not available for {_artifact_label(artifact)}")
            return value.versioned
        return value.model
    if use_versioned:
        raise ValueError(f"Versioned model not available for {_artifact_label(artifact)}")
    return value


def _shape(obj) -> Part | Compound:
    return getattr(obj, "part", obj)


def export_shape(shape: Part | Compound, path: Path, fmt: ExportFormat | str) -> None:
    """Export a build123d shape to a single file."""
    fmt_lower = fmt.lower()
    path.parent.mkdir(parents=True, exist_ok=True)

    if fmt_lower == "step":
        export_step(shape, path)
    elif fmt_lower == "stl":
        export_stl(shape, path)
    elif fmt_lower == "brep":
        export_brep(shape, path)
    elif fmt_lower == "gltf":
        export_gltf(shape, path)
    elif fmt_lower == "3mf":
        mesher = Mesher()
        mesher.add_shape(shape)
        mesher.write(path)
    else:
        supported = ", ".join(EXPORT_FORMATS)
        raise ValueError(f"Unsupported export format: {fmt}. Supported: {supported}")


def _format_extension(fmt: str) -> str:
    return ".step" if fmt.lower() == "step" else f".{fmt.lower()}"


def export_artifacts(
    output: Path,
    fmt: ExportFormat | str,
    names: tuple[str, ...] | None = None,
    *,
    root: Path | None = None,
    use_versioned: bool = False,
) -> list[Path]:
    """Export MakerRepo artifacts without invoking the mr CLI."""
    fmt_lower = fmt.lower()
    if fmt_lower not in EXPORT_FORMATS:
        supported = ", ".join(EXPORT_FORMATS)
        raise ValueError(f"Unsupported export format: {fmt}. Supported: {supported}")

    registry = load_registry(root)
    targets = _resolve_items(registry, names, "artifacts", "artifact")
    shapes = [
        _shape(realize_artifact(artifact, use_versioned=use_versioned)) for artifact in targets
    ]
    ext = _format_extension(fmt_lower)
    output = output.resolve()

    if len(shapes) == 1 and output.suffix:
        export_shape(shapes[0], output, fmt_lower)
        return [output]

    if len(shapes) > 1 and output.suffix:
        export_shape(Compound(children=shapes), output, fmt_lower)
        return [output]

    out_dir = output
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for artifact, shape in zip(targets, shapes):
        path = out_dir / f"{artifact.name}{ext}"
        export_shape(shape, path, fmt_lower)
        written.append(path)
    return written


def export_part(part: Part | Compound, name: str, out_dir: str | Path) -> None:
    """Export ad-hoc geometry to STEP, STL, and GLB (scripts and geometry tests)."""
    out = Path(out_dir)
    export_shape(part, out / f"{name}.step", "step")
    export_shape(part, out / f"{name}.stl", "stl")
    export_shape(part, out / f"{name}.glb", "gltf")


def ci_smoke(root: Path | None = None) -> None:
    """Discover artifacts and export STEP + STL for CI smoke tests."""
    if not list_artifacts(root):
        raise RuntimeError("No artifacts discovered")
    out_dir = Path("/tmp/mr-artifacts")
    export_artifacts(out_dir, "step", root=root)
    export_artifacts(out_dir, "stl", root=root)


def export_release_assets(
    out_dir: Path | None = None,
    root: Path | None = None,
    *,
    render_overrides: RenderConfig | None = None,
) -> list[ReleaseAsset]:
    """Export all artifacts as STL with matching PNG previews."""
    out = out_dir or Path("/tmp/release-artifacts")
    registry = load_registry(root)
    targets = _resolve_items(registry, None, "artifacts", "artifact")

    assets: list[ReleaseAsset] = []
    for artifact in targets:
        shape = _shape(realize_artifact(artifact))
        stl_path = out / f"{artifact.name}.stl"
        preview_configs = resolve_render_configs(
            artifact_func=artifact.func,
            overrides=render_overrides,
        )
        export_shape(shape, stl_path, "stl")
        render_previews: list[RenderPreview] = []
        for preview_config in preview_configs:
            png_path = out / render_output_filename(artifact.name, preview_config)
            render_stl(stl_path, png_path, config=preview_config)
            render_previews.append(
                RenderPreview(label=render_preview_label(preview_config), png_path=png_path)
            )
        assets.append(
            ReleaseAsset(
                artifact=artifact,
                stl_path=stl_path,
                render_previews=tuple(render_previews),
            )
        )
    return assets


def export_release(
    out_dir: Path | None = None,
    root: Path | None = None,
    *,
    render_overrides: RenderConfig | None = None,
) -> list[Path]:
    """Export all artifacts as STL and PNG previews for GitHub release publishing."""
    paths: list[Path] = []
    for asset in export_release_assets(out_dir, root, render_overrides=render_overrides):
        paths.append(asset.stl_path)
        paths.extend(asset.png_paths)
    return paths


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m cad_tooling.export")
    sub = parser.add_subparsers(dest="command", required=True)

    smoke = sub.add_parser("smoke", help="Run CI artifact export smoke test")
    smoke.add_argument("--root", type=Path, default=None)

    release = sub.add_parser("release", help="Export release STL and PNG preview artifacts")
    release.add_argument("-o", "--output", type=Path, default=Path("/tmp/release-artifacts"))
    release.add_argument("--root", type=Path, default=None)
    add_render_config_arguments(release)

    notes = sub.add_parser("release-notes", help="Write GitHub Release notes markdown")
    notes.add_argument("-o", "--output", type=Path, required=True)
    notes.add_argument("--assets-dir", type=Path, required=True)
    notes.add_argument("--repo", required=True, help="GitHub repository (owner/name)")
    notes.add_argument("--tag", required=True, help="Release tag (e.g. v0.0.1)")
    notes.add_argument("--root", type=Path, default=None)

    export_cmd = sub.add_parser("export", help="Export artifacts by name (default: all)")
    export_cmd.add_argument("-o", "--output", type=Path, required=True)
    export_cmd.add_argument("-f", "--format", default=DEFAULT_EXPORT_FORMAT)
    export_cmd.add_argument("names", nargs="*", default=())
    export_cmd.add_argument("--root", type=Path, default=None)

    args = parser.parse_args(argv)
    if args.command == "smoke":
        ci_smoke(args.root)
    elif args.command == "release":
        render_overrides = render_config_from_namespace(args)
        for path in export_release(args.output, args.root, render_overrides=render_overrides):
            print(path)
    elif args.command == "release-notes":
        from cad_tooling.release_notes import collect_release_assets, render_release_body

        assets = collect_release_assets(args.assets_dir.resolve(), args.root)
        args.output.write_text(render_release_body(args.repo, args.tag, assets))
    else:
        names = tuple(args.names) or None
        for path in export_artifacts(args.output, args.format, names, root=args.root):
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
