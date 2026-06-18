"""Headless preview rendering via Open CASCADE (OCP)."""

from __future__ import annotations

import argparse
import atexit
import importlib.util
import math
import os
import shutil
import subprocess
import sys
import time
from collections.abc import Callable
from pathlib import Path

from build123d import Compound, Part, import_stl
from OCP.AIS import AIS_InteractiveContext, AIS_Shape, AIS_Shaded
from OCP.Aspect import Aspect_DisplayConnection, Aspect_TOL_SOLID
from OCP.Graphic3d import Graphic3d_MaterialAspect, Graphic3d_NOM_PLASTIC
from OCP.Prs3d import Prs3d_LineAspect
from OCP.OpenGl import OpenGl_GraphicDriver
from OCP.Quantity import Quantity_Color, Quantity_TOC_RGB
from OCP.TopoDS import TopoDS_Shape
from OCP.V3d import V3d_TypeOfAxe, V3d_TypeOfOrientation, V3d_Viewer
from OCP.Xw import Xw_Window
from cad_tooling.render_config import (
    CameraConfig,
    RenderConfig,
    ResolvedLighting,
    add_render_config_arguments,
    render_config_from_namespace,
    render_output_filename,
    resolve_render_config_for_artifact_name,
    resolve_render_configs,
)
from cad_tooling.render_discovery import discover_render_artifact, discover_viewer_render_targets

# Maps friendly preset names to OCCT V3d_TypeOfOrientation values.
CAMERA_PRESETS: dict[str, V3d_TypeOfOrientation] = {
    "iso": V3d_TypeOfOrientation.V3d_XposYnegZpos,
    "top": V3d_TypeOfOrientation.V3d_Zpos,
    "bottom": V3d_TypeOfOrientation.V3d_Zneg,
    "front": V3d_TypeOfOrientation.V3d_Yneg,
    "back": V3d_TypeOfOrientation.V3d_Ypos,
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
        display_connection = Aspect_DisplayConnection()
        driver = OpenGl_GraphicDriver(display_connection)
        viewer = V3d_Viewer(driver)
        view = viewer.CreateView()
        window = Xw_Window(display_connection, "display-test", 0, 0, 64, 64)
        window.SetVirtual(True)
        view.SetWindow(window)
        window.Map()
        view.MustBeResized()
    except Exception:
        return False
    return True


def _reset_display() -> None:
    _terminate_xvfb()
    os.environ.pop("DISPLAY", None)


def _ensure_display(width: int, height: int) -> None:
    if _display_connection_works():
        return
    _reset_display()
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


def _face_color_from_shape(
    shape: Part | Compound,
    default_face_color: tuple[float, float, float],
) -> tuple[float, float, float]:
    """Read build123d ``Part.color`` / ``Shape.color`` when set on the solid."""
    color = getattr(shape, "color", None)
    if color is None:
        return default_face_color
    red, green, blue, *_alpha = tuple(color)
    return (float(red), float(green), float(blue))


def _colored_solids(
    shape: Part | Compound | TopoDS_Shape,
    default_face_color: tuple[float, float, float],
) -> list[tuple[TopoDS_Shape, tuple[float, float, float]]]:
    """Split build123d assemblies into per-child solids with native colors."""
    if isinstance(shape, TopoDS_Shape):
        return [(shape, default_face_color)]
    if isinstance(shape, Compound) and shape.children:
        solids: list[tuple[TopoDS_Shape, tuple[float, float, float]]] = []
        for child in shape.children:
            if isinstance(child, Compound) and child.children:
                solids.extend(_colored_solids(child, default_face_color))
            else:
                solids.append(
                    (
                        _shape_wrapped(child),
                        _face_color_from_shape(child, default_face_color),
                    )
                )
        return solids
    return [(_shape_wrapped(shape), _face_color_from_shape(shape, default_face_color))]


def _apply_camera(view, camera: CameraConfig) -> None:
    """Set view orientation from preset plus optional azimuth/elevation pose tweaks."""
    view.SetProj(CAMERA_PRESETS[camera.preset])
    if camera.azimuth:
        view.Turn(V3d_TypeOfAxe.V3d_Z, math.radians(camera.azimuth), True)
    if camera.elevation:
        view.Turn(V3d_TypeOfAxe.V3d_X, math.radians(camera.elevation), True)


def _scale_default_lights(viewer: V3d_Viewer, scale: float) -> None:
    """Scale OCCT stock directional lights; required for visible preset differences."""
    if scale == 1.0:
        return
    viewer.InitActiveLights()
    while viewer.MoreActiveLights():
        light = viewer.ActiveLight()
        light.SetIntensity(light.Intensity() * scale)
        viewer.NextActiveLights()
    viewer.UpdateLights()


def _apply_lighting(viewer: V3d_Viewer, profile: ResolvedLighting) -> None:
    """Configure OCCT stock lights and scale them to the resolved profile."""
    viewer.SetDefaultLights()
    viewer.SetLightOn()
    _scale_default_lights(viewer, profile.light_scale)


def _apply_face_boundaries(ais: AIS_Shape, settings: RenderConfig) -> None:
    """Enable OCCT face-boundary edges on a shaded AIS_Shape."""
    if not settings.show_edges:
        return
    drawer = ais.Attributes()
    drawer.SetFaceBoundaryDraw(True)
    aspect = Prs3d_LineAspect(
        Quantity_Color(*settings.edge_color, Quantity_TOC_RGB),
        Aspect_TOL_SOLID,
        settings.edge_width,
    )
    drawer.SetFaceBoundaryAspect(aspect)


def _material_for_shape(
    face_color: tuple[float, float, float],
    profile: ResolvedLighting,
) -> Graphic3d_MaterialAspect:
    """Build a shaded material tuned for headless PNG brightness."""
    material = Graphic3d_MaterialAspect(Graphic3d_NOM_PLASTIC)
    ambient = tuple(min(1.0, channel * profile.ambient_factor) for channel in face_color)
    diffuse = tuple(min(1.0, channel * profile.diffuse_factor) for channel in face_color)
    material.SetAmbientColor(Quantity_Color(*ambient, Quantity_TOC_RGB))
    material.SetDiffuseColor(Quantity_Color(*diffuse, Quantity_TOC_RGB))
    material.SetSpecularColor(
        Quantity_Color(profile.specular, profile.specular, profile.specular, Quantity_TOC_RGB)
    )
    material.SetShininess(profile.shininess)
    return material


def _render_shape_once(
    shape: Part | Compound | TopoDS_Shape,
    output: Path,
    settings: RenderConfig,
) -> None:
    display_connection = Aspect_DisplayConnection()
    driver = OpenGl_GraphicDriver(display_connection)
    viewer = V3d_Viewer(driver)
    lighting_profile = settings.lighting.resolved_profile()
    _apply_lighting(viewer, lighting_profile)

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

    for topo, face_color in _colored_solids(shape, settings.face_color):
        ais = AIS_Shape(topo)
        ais.SetMaterial(_material_for_shape(face_color, lighting_profile))
        ais.SetColor(Quantity_Color(*face_color, Quantity_TOC_RGB))
        _apply_face_boundaries(ais, settings)
        context.Display(ais, AIS_Shaded, 0, True)

    view.FitAll(settings.fit_margin, False)
    view.ZFitAll(settings.fit_margin)
    _apply_camera(view, settings.camera)
    view.Redraw()

    if not view.Dump(str(output)):
        raise RuntimeError(f"Failed to render preview: {output}")


def render_shape(
    shape: Part | Compound | TopoDS_Shape,
    output: Path,
    *,
    config: RenderConfig | None = None,
) -> None:
    """Render a build123d or OCP shape to a PNG preview using OCCT."""
    settings = config or RenderConfig()
    output.parent.mkdir(parents=True, exist_ok=True)

    for attempt in range(2):
        _ensure_display(settings.width, settings.height)
        try:
            _render_shape_once(shape, output, settings)
            return
        except Exception:
            if attempt == 1:
                raise
            _reset_display()


def render_stl(
    stl_path: Path,
    output: Path,
    *,
    config: RenderConfig | None = None,
) -> None:
    """Render an exported STL file to a PNG preview using OCCT."""
    render_shape(import_stl(stl_path).wrapped, output, config=config)


def _resolve_input_path(path: Path) -> Path:
    """Resolve an STL or viewer script path, inferring .stl / .py when omitted."""
    resolved = path.resolve()
    if resolved.exists():
        return resolved
    for suffix in (".py", ".stl"):
        candidate = resolved.with_suffix(suffix)
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"Input not found: {path}")


def render_viewer_script(
    script: Path,
    output: Path,
    *,
    artifact_name: str | None = None,
    overrides: RenderConfig | None = None,
    root: Path | None = None,
) -> list[Path]:
    """Render a viewer script's assembly and @render sub-parts from its composition chain."""
    script = script.resolve()
    module_name = f"_cad_render_{script.stem}"
    spec = importlib.util.spec_from_file_location(module_name, script)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load script: {script}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    build_model = getattr(module, "build_model", None)
    if not callable(build_model):
        raise ValueError(
            f"Script {script} must define build_model() -> Part | Compound for rendering"
        )

    targets = discover_viewer_render_targets(script, root=root)
    if not targets:
        shape = build_model()
        label = artifact_name or script.stem
        artifact_func = _artifact_func_for_name(label, root) if label != script.stem else None
        return render_model(
            shape,
            output,
            label,
            artifact_func=artifact_func,
            overrides=overrides,
        )

    written: list[Path] = []
    primary_shape = build_model()
    for index, artifact in enumerate(targets):
        shape = primary_shape if index == 0 else artifact.func()
        label = artifact.name
        if index == 0 and artifact_name is not None:
            label = artifact_name
        written.extend(
            render_model(
                shape,
                output,
                label,
                artifact_func=artifact.func,
                overrides=overrides,
            )
        )
    return written


def load_viewer_script(
    script: Path,
    *,
    root: Path | None = None,
) -> tuple[Part | Compound, str | None, Callable[..., object] | None]:
    """Load a viewer script and discover its @render artifact from cad/ imports."""
    script = script.resolve()
    module_name = f"_cad_render_{script.stem}"
    spec = importlib.util.spec_from_file_location(module_name, script)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load script: {script}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    build_model = getattr(module, "build_model", None)
    if not callable(build_model):
        raise ValueError(
            f"Script {script} must define build_model() -> Part | Compound for rendering"
        )
    shape = build_model()
    artifact = discover_render_artifact(script, root=root)
    if artifact is None:
        return shape, None, None
    return shape, artifact.name, artifact.func


def _artifact_for_name(
    name: str,
    root: Path | None = None,
):
    from cad_tooling.export import list_artifacts

    matches = [item for item in list_artifacts(root) if item.name == name]
    if not matches:
        return None
    if len(matches) > 1:
        options = ", ".join(f"{item.module}/{item.name}" for item in matches)
        raise ValueError(f"Ambiguous artifact name '{name}'; use module/name: {options}")
    return matches[0]


def _artifact_func_for_name(
    name: str,
    root: Path | None = None,
) -> Callable[..., object] | None:
    artifact = _artifact_for_name(name, root)
    return None if artifact is None else artifact.func


def _build_artifact_shape(name: str, root: Path | None = None) -> Part | Compound:
    """Build a MakerRepo artifact shape with native part colors intact."""
    from cad_tooling.export import _shape, realize_artifact

    artifact = _artifact_for_name(name, root)
    if artifact is None:
        raise ValueError(f"Artifact not found for render lookup: {name}")
    return _shape(realize_artifact(artifact))


def render_artifact(
    name: str,
    output: Path,
    *,
    overrides: RenderConfig | None = None,
    root: Path | None = None,
) -> list[Path]:
    """Render a named @artifact from Python (preserves per-part colors)."""
    artifact = _artifact_for_name(name, root)
    if artifact is None:
        raise ValueError(f"Artifact not found: {name}")
    shape = _build_artifact_shape(name, root)
    return render_model(
        shape,
        output,
        name,
        artifact_func=artifact.func,
        overrides=overrides,
    )


def _resolve_render_configs_for_label(
    label: str,
    *,
    artifact_func: Callable[..., object] | None,
    overrides: RenderConfig | None,
) -> list[RenderConfig]:
    if artifact_func is not None:
        return resolve_render_configs(artifact_func=artifact_func, overrides=overrides)
    try:
        return [
            resolve_render_config_for_artifact_name(label, overrides=overrides),
        ]
    except ValueError:
        return resolve_render_configs(overrides=overrides)


def _output_png_path(
    output: Path,
    label: str,
    config: RenderConfig,
    *,
    multi_render: bool,
) -> Path:
    if output.suffix.lower() == ".png":
        return output
    output.mkdir(parents=True, exist_ok=True)
    if multi_render:
        return output / render_output_filename(label, config)
    return output / f"{label}.png"


def render_model(
    shape: Part | Compound | TopoDS_Shape,
    output: Path,
    label: str,
    *,
    artifact_func: Callable[..., object] | None = None,
    overrides: RenderConfig | None = None,
) -> list[Path]:
    """Render a model to one or more PNG previews."""
    configs = _resolve_render_configs_for_label(
        label,
        artifact_func=artifact_func,
        overrides=overrides,
    )
    if output.suffix.lower() == ".png":
        configs = configs[:1]
    multi_render = len(configs) > 1

    written: list[Path] = []
    for config in configs:
        png_path = _output_png_path(output, label, config, multi_render=multi_render)
        render_shape(shape, png_path, config=config)
        written.append(png_path.resolve())
    return written


def render_input(
    input_path: Path,
    output: Path,
    *,
    artifact_name: str | None = None,
    overrides: RenderConfig | None = None,
    root: Path | None = None,
) -> list[Path]:
    """Render an artifact name, STL file, or viewer script to PNG preview(s)."""
    resolved: Path | None = None
    try:
        resolved = _resolve_input_path(input_path)
    except FileNotFoundError:
        resolved = None

    if resolved is not None and resolved.suffix.lower() == ".py":
        return render_viewer_script(
            resolved,
            output,
            artifact_name=artifact_name,
            overrides=overrides,
            root=root,
        )

    label = artifact_name or (resolved.stem if resolved is not None else input_path.stem)
    artifact = _artifact_for_name(label, root)
    if artifact is not None:
        shape = _build_artifact_shape(label, root)
        return render_model(
            shape,
            output,
            label,
            artifact_func=artifact.func,
            overrides=overrides,
        )

    if resolved is None:
        raise FileNotFoundError(
            f"Input not found and no artifact named '{input_path}': {input_path}"
        )

    configs = _resolve_render_configs_for_label(label, artifact_func=None, overrides=overrides)
    if output.suffix.lower() == ".png":
        configs = configs[:1]
    multi_render = len(configs) > 1

    written: list[Path] = []
    for config in configs:
        png_path = _output_png_path(output, label, config, multi_render=multi_render)
        render_stl(resolved, png_path, config=config)
        written.append(png_path.resolve())
    return written


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m cad_tooling.render",
        description="Render STL or viewer-script previews to PNG using Open CASCADE (OCP).",
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Input STL file or viewer script with build_model() (e.g. main.py)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        required=True,
        help="Output PNG path or directory for one or more previews",
    )
    add_render_config_arguments(parser)

    args = parser.parse_args(argv)
    overrides = render_config_from_namespace(args)
    written = render_input(
        args.input,
        args.output,
        artifact_name=args.artifact,
        overrides=overrides,
    )
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
