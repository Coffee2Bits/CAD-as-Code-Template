"""Headless preview rendering via Open CASCADE (OCP)."""

from __future__ import annotations

import argparse
import atexit
import math
import os
import shutil
import subprocess
import time
from pathlib import Path

from build123d import Compound, Part, import_stl
from OCP.AIS import AIS_InteractiveContext, AIS_Shape, AIS_Shaded
from OCP.Aspect import Aspect_DisplayConnection
from OCP.Graphic3d import Graphic3d_MaterialAspect, Graphic3d_NOM_PLASTIC
from OCP.OpenGl import OpenGl_GraphicDriver
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCP.TopoDS import TopoDS_Shape
from OCP.V3d import V3d_TypeOfAxe, V3d_TypeOfOrientation, V3d_Viewer
from OCP.Xw import Xw_Window

from cad_tooling.render_config import (
    CameraConfig,
    RenderConfig,
    add_render_config_arguments,
    render_config_from_namespace,
    resolve_render_config,
    resolve_render_config_for_artifact_name,
)

# Maps friendly preset names to OCCT V3d_TypeOfOrientation values.
CAMERA_PRESETS: dict[str, V3d_TypeOfOrientation] = {
    "iso": V3d_TypeOfOrientation.V3d_XposYnegZpos,
    "top": V3d_TypeOfOrientation.V3d_Zpos,
    "bottom": V3d_TypeOfOrientation.V3d_Zneg,
    "front": V3d_TypeOfOrientation.V3d_Ypos,
    "back": V3d_TypeOfOrientation.V3d_Yneg,
    "left": V3d_TypeOfOrientation.V3d_Xneg,
    "right": V3d_TypeOfOrientation.V3d_Xpos,
    "axo_left": V3d_TypeOfOrientation.V3d_TypeOfOrientation_Zup_AxoLeft,
    "axo_right": V3d_TypeOfOrientation.V3d_TypeOfOrientation_Zup_AxoRight,
}

_xvfb_proc: subprocess.Popen[bytes] | None = None


def _display_connection_works() -> bool:
    display = os.environ.get("DISPLAY")
    if not display:
        return False
    try:
        Aspect_DisplayConnection()
    except Exception:
        return False
    return True


def _ensure_display(width: int, height: int) -> None:
    if _display_connection_works():
        return
    if shutil.which("Xvfb") is None:
        raise RuntimeError(
            "Headless OCP rendering requires DISPLAY or Xvfb "
            "(Xvfb is installed in this project's devcontainer)."
        )

    global _xvfb_proc
    if _xvfb_proc is not None and _xvfb_proc.poll() is None:
        _xvfb_proc.terminate()
        _xvfb_proc.wait(timeout=5)

    screen = max(width, height, 1024)
    display = ":99"
    _xvfb_proc = subprocess.Popen(
        ["Xvfb", display, "-screen", "0", f"{screen}x{screen}x24"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    atexit.register(_terminate_xvfb)
    os.environ["DISPLAY"] = display

    if _xvfb_proc.poll() is not None:
        raise RuntimeError("Failed to start Xvfb for headless OCP rendering")

    for _ in range(20):
        if _display_connection_works():
            return
        time.sleep(0.1)
    raise RuntimeError("Xvfb started but OCP could not connect to the display")


def _terminate_xvfb() -> None:
    global _xvfb_proc
    if _xvfb_proc is not None and _xvfb_proc.poll() is None:
        _xvfb_proc.terminate()
        _xvfb_proc.wait(timeout=5)
    _xvfb_proc = None


def _shape_wrapped(shape: Part | Compound | TopoDS_Shape) -> TopoDS_Shape:
    if isinstance(shape, TopoDS_Shape):
        return shape
    return shape.wrapped


def _apply_camera(view, camera: CameraConfig) -> None:
    """Set view orientation from preset plus optional azimuth/elevation pose tweaks."""
    view.SetProj(CAMERA_PRESETS[camera.preset])
    if camera.azimuth:
        view.Turn(V3d_TypeOfAxe.V3d_Z, math.radians(camera.azimuth), True)
    if camera.elevation:
        view.Turn(V3d_TypeOfAxe.V3d_X, math.radians(camera.elevation), True)


def render_shape(
    shape: Part | Compound | TopoDS_Shape,
    output: Path,
    *,
    config: RenderConfig | None = None,
) -> None:
    """Render a build123d or OCP shape to a PNG preview using OCCT."""
    settings = config or RenderConfig()
    _ensure_display(settings.width, settings.height)
    output.parent.mkdir(parents=True, exist_ok=True)
    topo = _shape_wrapped(shape)

    display_connection = Aspect_DisplayConnection()
    driver = OpenGl_GraphicDriver(display_connection)
    viewer = V3d_Viewer(driver)
    viewer.SetDefaultLights()
    viewer.SetLightOn()

    context = AIS_InteractiveContext(viewer)
    view = viewer.CreateView()
    window = Xw_Window(
        display_connection,
        "cad-render",
        0,
        0,
        settings.width,
        settings.height,
    )
    window.SetVirtual(True)
    view.SetWindow(window)
    window.Map()
    view.MustBeResized()
    view.SetBackgroundColor(Quantity_Color(*settings.background, Quantity_TOC_RGB))

    ais = AIS_Shape(topo)
    ais.SetMaterial(Graphic3d_MaterialAspect(Graphic3d_NOM_PLASTIC))
    ais.SetColor(Quantity_Color(*settings.face_color, Quantity_TOC_RGB))
    context.Display(ais, AIS_Shaded, 0, True)

    view.FitAll(settings.fit_margin, False)
    view.ZFitAll(settings.fit_margin)
    _apply_camera(view, settings.camera)
    view.Redraw()

    if not view.Dump(str(output)):
        raise RuntimeError(f"Failed to render preview: {output}")


def render_stl(
    stl_path: Path,
    output: Path,
    *,
    config: RenderConfig | None = None,
) -> None:
    """Render an exported STL file to a PNG preview using OCCT."""
    render_shape(import_stl(stl_path).wrapped, output, config=config)


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m cad_tooling.render",
        description="Render an STL preview PNG using Open CASCADE (OCP).",
    )
    parser.add_argument("stl", type=Path, help="Input STL file")
    parser.add_argument("-o", "--output", type=Path, required=True, help="Output PNG path")
    add_render_config_arguments(parser)

    args = parser.parse_args(argv)
    overrides = render_config_from_namespace(args)
    artifact_name = args.artifact or args.stl.stem
    try:
        config = resolve_render_config_for_artifact_name(
            artifact_name,
            overrides=overrides,
        )
    except ValueError:
        config = resolve_render_config(overrides=overrides)
    render_stl(args.stl.resolve(), args.output.resolve(), config=config)
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
