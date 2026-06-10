from build123d import Part
from ocp_vscode import show_object

from cad.parts.sphere import make_sphere


def build_model() -> Part:
    """Geometry shown in OCP CAD Viewer — also used by cad_tooling.render."""
    return make_sphere()


def main() -> None:
    show_object(build_model(), name="sphere")


if __name__ == "__main__":
    main()
