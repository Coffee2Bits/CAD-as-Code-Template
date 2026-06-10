from pathlib import Path

from cad_tooling.render_discovery import (
    cad_modules_referenced_by_build_model,
    discover_render_artifact,
)


def test_cad_modules_referenced_by_main(repo_root: Path):
    modules = cad_modules_referenced_by_build_model(repo_root / "main.py")
    assert modules == {"cad.parts.sphere"}


def test_discover_render_artifact_from_main(repo_root: Path):
    artifact = discover_render_artifact(repo_root / "main.py", root=repo_root)
    assert artifact is not None
    assert artifact.name == "sphere"
    assert artifact.module == "cad.parts.sphere"


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
