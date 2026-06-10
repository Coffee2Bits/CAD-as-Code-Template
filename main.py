from build123d import Part
from ocp_vscode import show_object

from cad.parts.m3_hex_nut import VISUAL_REFERENCE_COLOR
from cad.parts.sphere import make_sphere, positioned_m3_hex_nut_reference

SPHERE_RADIUS = 10


def build_model() -> Part:
    """Geometry shown in OCP CAD Viewer — also used by cad_tooling.render."""
    return make_sphere(radius=SPHERE_RADIUS)


def main() -> None:
    sphere = build_model()
    reference_nut = positioned_m3_hex_nut_reference(sphere, radius=SPHERE_RADIUS)

    show_object(sphere, name="sphere")
    show_object(
        reference_nut,
        name="m3_hex_nut_reference",
        options={"color": VISUAL_REFERENCE_COLOR, "alpha": 1.0},
    )


if __name__ == "__main__":
    main()
