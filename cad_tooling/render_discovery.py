"""Discover @render artifacts referenced by viewer scripts (main.py)."""

from __future__ import annotations

import ast
from pathlib import Path

from mr.data_types import Artifact


def _import_map(tree: ast.Module) -> dict[str, tuple[str, str]]:
    """Map local names to (cad package module, imported symbol)."""
    mapping: dict[str, tuple[str, str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.module is None or not node.module.startswith("cad."):
            continue
        for alias in node.names:
            local = alias.asname or alias.name
            mapping[local] = (node.module, alias.name)
    return mapping


def _build_model_call_names(tree: ast.Module) -> list[str]:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == "build_model":
            return [
                child.func.id
                for child in ast.walk(node)
                if isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
            ]
    return []


def cad_modules_referenced_by_build_model(script: Path) -> set[str]:
    """Return cad.* module paths whose symbols are called from build_model()."""
    tree = ast.parse(script.read_text(encoding="utf-8"))
    imports = _import_map(tree)
    return {imports[name][0] for name in _build_model_call_names(tree) if name in imports}


def discover_render_artifact(
    script: Path,
    *,
    root: Path | None = None,
) -> Artifact | None:
    """Find the @render-decorated artifact for a viewer script's build_model() imports."""
    from cad_tooling.export import list_artifacts
    from cad_tooling.render_decorator import get_render_configs_from_func

    modules = cad_modules_referenced_by_build_model(script)
    if not modules:
        return None

    tree = ast.parse(script.read_text(encoding="utf-8"))
    imports = _import_map(tree)
    call_names = _build_model_call_names(tree)

    candidates = [
        artifact
        for artifact in list_artifacts(root)
        if artifact.module in modules and get_render_configs_from_func(artifact.func)
    ]
    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]

    for name in call_names:
        if name not in imports:
            continue
        _module, symbol = imports[name]
        matched = [artifact for artifact in candidates if artifact.name in {name, symbol}]
        if len(matched) == 1:
            return matched[0]

    by_call_name = [artifact for artifact in candidates if artifact.name in call_names]
    if len(by_call_name) == 1:
        return by_call_name[0]

    options = ", ".join(f"{artifact.module}/{artifact.name}" for artifact in candidates)
    raise ValueError(
        f"Ambiguous @render artifact for {script.name}; "
        f"import one part module in build_model() or pass --artifact. Options: {options}"
    )
