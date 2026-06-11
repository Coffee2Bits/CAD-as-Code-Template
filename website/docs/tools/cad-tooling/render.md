---
sidebar_position: 3
---

# Render

Headless PNG previews via [Open CASCADE](/reference/open-cascade) (OCP). In CI and the devcontainer, Xvfb provides a virtual display when `DISPLAY` is unset.

## CLI

```bash
# Render model from main.py (uses @render from cad/ imports in build_model())
uv run python -m cad_tooling.render main.py -o dist/

# Use @render settings from matching artifact (STL stem = artifact name)
uv run python -m cad_tooling.render dist/sphere.stl -o dist/sphere.png

# Override camera for a one-off render
uv run python -m cad_tooling.render dist/sphere.stl -o dist/sphere-top.png --camera top
```

Or: `just render`, `just render dist/sphere.stl dist/sphere.png --camera top`

## CLI flags

| Flag | Purpose |
|------|---------|
| `--width` / `--height` | PNG size in pixels |
| `--background R,G,B` | Background color (0.0–1.0) |
| `--face-color R,G,B` | Solid face color |
| `--camera` | Preset (see below) |
| `--azimuth` / `--elevation` | Extra pose in degrees |
| `--fit-margin` | Passed to `V3d_View.FitAll` |

## `@render` decorator

Attach preview settings to an `@artifact` entry point:

```python
from cad_tooling.render_decorator import render
from mr import artifact

@artifact(short_desc="Demo sphere")
@render(camera="iso", face_color=(0.31, 0.63, 1.0))
def sphere() -> Part:
    return make_sphere()
```

Multiple release previews per artifact (filename encodes camera and size, e.g. `sphere_iso_800x600.png`):

```python
@render(renders=[
    {"camera": "iso", "width": 800, "height": 600},
    {"camera": "top", "width": 1024, "height": 768},
])
def bracket() -> Part:
    return make_bracket()
```

### Camera presets

`iso`, `top`, `bottom`, `front`, `back`, `left`, `right`, `axo_left`, `axo_right`

### Image size

Set `width` and `height` (pixels) on each render spec. Default: 800×600.

### Resolution order

At render time: defaults in `RenderConfig` → `@render` on the artifact → CLI flags on `cad_tooling.render` or `cad_tooling.export release`.

Example: [`cad/parts/sphere.py`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/cad/parts/sphere.py)
