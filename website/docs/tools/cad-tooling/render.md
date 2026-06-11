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

Or via `just`:

```bash
just render                                    # main.py → dist/
just render dist/sphere.stl dist/sphere.png --camera top
just render-artifact sphere /tmp/out           # export STL + PNG for one @artifact
```

### Headless PNG for a named artifact

Export STL, then render (or use the combined recipe):

```bash
just export /tmp/out stl sphere
just render /tmp/out/sphere.stl /tmp/out/
# equivalent:
just render-artifact sphere /tmp/out
```

`@render` settings on the artifact apply automatically when the STL stem matches the artifact name.

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

## Alternative: `mr artifacts snapshot`

The [MakerRepo CLI](https://docs.makerrepo.com/makerrepo-cli/) can capture headless PNGs via a browser-based viewer (`mr artifacts snapshot`). This workspace **does not** wire that into `just` or CI — the devcontainer does not install Playwright, and release previews use the OCP pipeline above instead.

If you prefer `mr snapshot` locally:

```bash
# Requires Playwright browser install (not in the default devcontainer)
uv run playwright install chromium
uv run mr artifacts snapshot sphere -o /tmp/out/sphere.png
```

Trade-offs:

| | `cad_tooling.render` (default here) | `mr artifacts snapshot` |
|---|-------------------------------------|-------------------------|
| Runtime | Open CASCADE (OCP) + optional Xvfb | Playwright + browser viewer |
| Devcontainer | Works out of the box | Extra `playwright install` step |
| `@render` decorator | Honored via STL stem / artifact name | Not used — viewer defaults |
| CI / release | Used by `export release` and GitHub Actions | Not used |

For template users: either approach is valid; this repo standardizes on OCP rendering so headless previews work in CI without a browser stack.
