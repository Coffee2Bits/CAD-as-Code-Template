from ocp_vscode import show

from cad.assemblies.demo_sphere import make_demo_sphere


def build_model():
    """Geometry shown in OCP CAD Viewer and used by cad_tooling.render."""
    return make_demo_sphere()


def main() -> None:
    show(build_model())


if __name__ == "__main__":
    main()
