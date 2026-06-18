---
sidebar_position: 3
---

# Render

Headless PNG previews via [Open CASCADE](/reference/open-cascade) (OCP). In the CI/CD pipeline and the devcontainer, Xvfb provides a virtual display when `DISPLAY` is unset.

## CLI

```bash
# Render the main project scene (build_model()) plus @render sub-parts from its composition chain
uv run python -m cad_tooling.render main.py -o dist/

# Use @render settings from matching artifact (STL stem = artifact name)
uv run python -m cad_tooling.render dist/sphere.stl -o dist/sphere.png

# Override camera for a one-off render
uv run python -m cad_tooling.render dist/sphere.stl -o dist/sphere-top.png --camera top
```

Or via `just`:

```bash
just render                                    # main.py → dist/
just render --lighting-preset default          # flags before positionals OK
just render dist/sphere.stl dist/sphere.png --camera top
just render main.py dist --lighting-preset bright
just render-artifact sphere /tmp/out           # export STL + PNG for one @artifact
just render-artifact demo_sphere dist --lighting-preset bright

PNG previews for named `@artifact` functions are rendered from **Python geometry**
(same path as `export release`), not from the exported STL. STL meshes do not carry
per-part `Part.color` metadata, so STL-based previews would appear as a single default color.
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

### Viewer scripts (`main.py`)

Rendering a viewer script writes PNGs for:

1. The primary `@render` artifact discovered from `build_model()` imports (e.g. `demo_sphere_*.png`)
2. Any other `@render` artifacts from `cad/` modules in that composition chain (e.g. `sphere_*.png` from `cad.parts.sphere`)

Sub-parts without `@render` (such as `m3_hex_nut`) are omitted. Release export still uses `list_release_artifacts()` — only explicit `@render` artifacts — not this viewer expansion.

## CLI flags

| Flag | Purpose |
|------|---------|
| `--width` / `--height` | PNG size in pixels |
| `--background R,G,B` | Background color (0.0–1.0) |
| `--face-color R,G,B` | Solid face color |
| `--camera` | Preset (see below) |
| `--azimuth` / `--elevation` | Extra pose in degrees |
| `--fit-margin` | Passed to `V3d_View.FitAll` |
| `--show-edges` / `--no-show-edges` | OCCT face-boundary edges on shaded solids (default: on) |
| `--edge-color R,G,B` | Face-boundary edge RGB (0.0–1.0) |
| `--edge-width` | Face-boundary line width in pixels |
| `--lighting-preset` | `default` (global default), `studio`, `bright`, or `flat` |
| `--light-intensity` | Global multiplier for directional lights and material reflectance |
| `--ambient-intensity` | Material ambient reflectance override (0.0–2.0) |
| `--headlight-intensity` | OCCT directional light scale override |
| `--fill-intensity` | Material diffuse reflectance override |

## `@render` decorator

Attach preview settings to an `@artifact` entry point:

```python
from cad_tooling.render_decorator import render
from mr import artifact

@artifact(short_desc="Demo sphere")
@render(camera="iso", lighting={"preset": "bright"})
def sphere() -> Part:
    return make_sphere()
```

**Edges** — face-boundary lines on shaded solids (default on):

| Field | Purpose |
|-------|---------|
| `show_edges` | Enable OCCT face-boundary drawing (default `true`) |
| `edge_color` | RGB triplet for edge lines (default black) |
| `edge_width` | Line width in pixels (default `1.0`) |

**Lighting** — pass a `lighting` mapping on `@render` or per entry in `renders=[...]`:

| Field | Purpose |
|-------|---------|
| `preset` | `default` (global default), `studio`, `bright`, `flat` — coefficients in `LIGHTING_PRESETS` |
| `intensity` | Global multiplier for directional lights and material reflectance (default `1.0`) |
| `ambient` | Material ambient reflectance override (0.0–2.0) |
| `headlight` | OCCT directional light scale override |
| `fill` | Material diffuse reflectance override |

Headless renders scale OCCT's stock directional lights and tune per-shape plastic
material ambient/diffuse coefficients. Custom `AddLight` sources are not used because
they have little effect in the headless CI/CD pipeline PNG path.

Face-boundary edges use OCCT `Prs3d_Drawer.SetFaceBoundaryDraw` on BRep solids. They
apply when rendering from Python geometry (`render_artifact`, `export release`,
viewer scripts) but not when importing STL meshes — STL triangulation does not carry
the original face topology needed for boundary lines.

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

## Assembly colors

Set `part.color` in each part's `make_*` builder using a module-level `PART_COLOR` constant. Assemblies use `Compound(children=[...])` only — composite PNGs pick up each child's color automatically (see [AGENTS.md — Part preview colors](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/AGENTS.md#part-preview-colors)).

## Release export scope

`export release` and GitHub Release notes include only `@artifact` entry points that also declare `@render`. Artifacts without `@render` stay discoverable via `mr artifacts list` but are omitted from release PNG/STL bundles.

## Alternative: `mr artifacts snapshot`

The [MakerRepo CLI](https://docs.makerrepo.com/makerrepo-cli/) can capture headless PNGs via a browser-based viewer (`mr artifacts snapshot`). This workspace **does not** wire that into `just` or the CI/CD pipeline — the devcontainer does not install Playwright, and release previews use the OCP pipeline above instead.

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
| CI/CD pipeline / release | Used by `export release` and GitHub Actions | Not used |

For template users: either approach is valid; this repo standardizes on OCP rendering so headless previews work in the CI/CD pipeline without a browser stack.
