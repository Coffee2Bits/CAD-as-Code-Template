from pathlib import Path

import pytest

from cad_tooling.render_discovery import (
    cad_modules_referenced_by_build_model,
    discover_render_artifact,
    discover_viewer_render_targets,
    expand_composition_modules,
)


pytestmark = pytest.mark.unit


def test_cad_modules_referenced_by_main(repo_root: Path):
    modules = cad_modules_referenced_by_build_model(repo_root / "main.py")
    assert modules == {"cad.assemblies.sphere_with_nut"}


def test_discover_render_artifact_from_main(repo_root: Path):
    artifact = discover_render_artifact(repo_root / "main.py", root=repo_root)
    assert artifact is not None
    assert artifact.name == "sphere_with_nut"
    assert artifact.module == "cad.assemblies.sphere_with_nut"


def test_expand_composition_modules_includes_assembly_parts(repo_root: Path):
    modules = expand_composition_modules(
        cad_modules_referenced_by_build_model(repo_root / "main.py"),
        root=repo_root,
    )
    assert "cad.assemblies.sphere_with_nut" in modules
    assert "cad.parts.sphere" in modules
    assert "cad.parts.m3_hex_nut" in modules
    assert "cad.parts.m3_socket_head_cap_screw" in modules


def test_discover_viewer_render_targets_includes_sub_parts(repo_root: Path):
    targets = discover_viewer_render_targets(repo_root / "main.py", root=repo_root)
    assert [artifact.name for artifact in targets] == ["sphere_with_nut", "sphere"]


def test_discover_render_artifact_returns_none_without_cad_imports(tmp_path: Path):
    script = tmp_path / "viewer.py"
    script.write_text(
        "from build123d import Sphere\ndef build_model():\n    return Sphere(5)\n",
        encoding="utf-8",
    )
    assert discover_render_artifact(script) is None


def test_discover_render_artifact_ambiguous(tmp_path: Path, repo_root: Path):
    script = tmp_path / "viewer.py"
    script.write_text(
        "from cad.parts.sphere import make_sphere, sphere\n"
        "def build_model():\n"
        "    return make_sphere()\n",
        encoding="utf-8",
    )
    # Only one @render artifact in cad.parts.sphere, so still unambiguous.
    artifact = discover_render_artifact(script, root=repo_root)
    assert artifact is not None
    assert artifact.name == "sphere"


def test_discover_render_artifact_returns_none_for_unpublished_module(
    tmp_path: Path, repo_root: Path
):
    script = tmp_path / "viewer.py"
    script.write_text(
        "from cad.parts.not_published import make_widget\n"
        "def build_model():\n"
        "    return make_widget()\n",
        encoding="utf-8",
    )
    assert discover_render_artifact(script, root=repo_root) is None
