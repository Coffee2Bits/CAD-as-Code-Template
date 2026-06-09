from build123d import *


def make_example_ocp_text(
    text: str = "OCP",
    font_size: float = 20,
    depth: float = 5,
) -> Part:
    with BuildPart() as part:
        with BuildSketch():
            Text(text, font_size=font_size, align=(Align.CENTER, Align.CENTER))
        extrude(amount=depth)

    return part.part
