from cad.parts.m3_hex_nut import PART_COLOR as NUT_PART_COLOR
from cad.parts.m3_socket_head_cap_screw import PART_COLOR as SCREW_PART_COLOR
from cad.parts.sphere import EMBOSSED_TEXT_COLOR, PART_COLOR as SPHERE_PART_COLOR
from cad.parts.sphere_tripod_support import PART_COLOR as SUPPORT_PART_COLOR
import pytest

from cad.assemblies.demo_sphere import make_demo_sphere
from cad_tooling.export import export_artifacts
from cad_tooling.render_decorator import artifact_has_render
from pytest_support import artifact_names, artifacts_list


@pytest.mark.unit
class TestArtifactDiscovery:
    def test_demo_sphere_artifact_discovered(self, registry):
        names = artifact_names(registry)
        assert "demo_sphere" in names

    def test_release_artifacts_require_render(self, registry):
        all_artifacts = artifacts_list(registry)
        all_names = {artifact.name for artifact in all_artifacts}
        release_names = {
            artifact.name for artifact in all_artifacts if artifact_has_render(artifact.func)
        }
        assert "sphere" in release_names
        assert "demo_sphere" in release_names
        assert "m3_hex_nut" in all_names
        assert "m3_socket_head_cap_screw" in all_names
        assert "m3_hex_nut" not in release_names
        assert "m3_socket_head_cap_screw" not in release_names


@pytest.mark.integration
class TestDemoSphereAssembly:
    def test_demo_sphere_assembly_has_colored_children(self):
        assembly = make_demo_sphere()
        assert assembly.label == "demo_sphere"
        assert len(assembly.children) == 4
        assert assembly.children[0].label == "sphere"
        assert assembly.children[1].label == "m3_hex_nut_reference"
        assert assembly.children[2].label == "m3_socket_head_cap_screw_reference"
        assert assembly.children[3].label == "sphere_tripod_support"
        sphere_body, embossed_text = assembly.children[0].children
        assert sphere_body.label == "sphere_body"
        assert embossed_text.label == "embossed_text"
        assert tuple(sphere_body.color)[:3] == tuple(SPHERE_PART_COLOR)[:3]
        assert tuple(embossed_text.color)[:3] == tuple(EMBOSSED_TEXT_COLOR)[:3]
        assert tuple(assembly.children[1].color)[:3] == tuple(NUT_PART_COLOR)[:3]
        assert tuple(assembly.children[2].color)[:3] == tuple(SCREW_PART_COLOR)[:3]
        assert tuple(assembly.children[3].color)[:3] == tuple(SUPPORT_PART_COLOR)[:3]

    def test_demo_sphere_exports(self, tmp_path):
        export_artifacts(tmp_path, "stl", ("demo_sphere",))
        stl_path = tmp_path / "demo_sphere.stl"
        assert stl_path.is_file()
        assert stl_path.stat().st_size > 0
