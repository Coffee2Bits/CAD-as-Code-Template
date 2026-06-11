from ocp_vscode import show

from cad.assemblies.sphere_with_nut import make_sphere_with_nut


def build_model():
    """Geometry shown in OCP CAD Viewer and used by cad_tooling.render."""
    return make_sphere_with_nut()


def main() -> None:
    show(build_model())


if __name__ == "__main__":
    main()
