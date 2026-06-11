from cad.parts.m3_hex_nut import PART_COLOR as NUT_PART_COLOR
from cad.parts.sphere import PART_COLOR as SPHERE_PART_COLOR
from cad.assemblies.sphere_with_nut import make_sphere_with_nut
from cad_tooling.export import export_artifacts, list_artifacts, list_release_artifacts


def test_sphere_with_nut_artifact_discovered():
    names = {artifact.name for artifact in list_artifacts()}
    assert "sphere_with_nut" in names


def test_release_artifacts_require_render():
    all_names = {artifact.name for artifact in list_artifacts()}
    release_names = {artifact.name for artifact in list_release_artifacts()}
    assert "sphere" in release_names
    assert "sphere_with_nut" in release_names
    assert "m3_hex_nut" in all_names
    assert "m3_hex_nut" not in release_names


def test_sphere_with_nut_assembly_has_colored_children():
    assembly = make_sphere_with_nut()
    assert assembly.label == "sphere_with_nut"
    assert len(assembly.children) == 2
    assert assembly.children[0].label == "sphere"
    assert assembly.children[1].label == "m3_hex_nut_reference"
    assert tuple(assembly.children[0].color)[:3] == tuple(SPHERE_PART_COLOR)[:3]
    assert tuple(assembly.children[1].color)[:3] == tuple(NUT_PART_COLOR)[:3]


def test_sphere_with_nut_exports(tmp_path):
    export_artifacts(tmp_path, "stl", ("sphere_with_nut",))
    stl_path = tmp_path / "sphere_with_nut.stl"
    assert stl_path.is_file()
    assert stl_path.stat().st_size > 0
