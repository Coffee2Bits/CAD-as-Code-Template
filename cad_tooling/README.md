# CAD tooling

Workspace helpers for exporting MakerRepo artifacts, rendering PNG previews, and generating GitHub Release notes. This package lives **alongside** `cad/` — model geometry stays in `cad/parts/` and `cad/assemblies/`; tooling lives here.

For day-to-day modeling, prefer the [`mr` CLI](https://docs.makerrepo.com/makerrepo-cli/) for artifact discovery and export. Use `cad_tooling` when you need programmatic export in tests/CI, headless OCP preview renders, or release automation.

## Package layout

```text
cad_tooling/
├── export.py           # MakerRepo discovery, export helpers, CLI
├── render.py           # Headless OCP PNG rendering, CLI
├── render_config.py    # RenderConfig / CameraConfig models and CLI flags
├── render_decorator.py # @render decorator for per-artifact preview settings
└── release_notes.py    # GitHub Release markdown generation
```

Unit tests mirror this layout in [`cad_tooling_tests/`](../cad_tooling_tests/).

## Export (`cad_tooling.export`)

### CLI

Run from the repository root:

```bash
# CI smoke — discover all @artifact functions, export STEP + STL
uv run python -m cad_tooling.export smoke

# Export one or all artifacts
uv run python -m cad_tooling.export export -o /tmp/out --format step
uv run python -m cad_tooling.export export -o /tmp/out/sphere.stl sphere

# Release bundle — STL + PNG preview per artifact (@render settings applied)
uv run python -m cad_tooling.export release -o dist/

# Generate GitHub Release notes from exported assets
uv run python -m cad_tooling.export release-notes \
  --assets-dir dist \
  --repo OWNER/REPO \
  --tag v0.0.1 \
  -o dist/RELEASE_BODY.md
```

Supported export formats: `step`, `stl`, `brep`, `gltf`, `3mf`.

### Python API

```python
from pathlib import Path

from cad_tooling.export import (
    export_artifacts,
    export_part,
    list_artifacts,
    list_generators,
)

# Discover published models
artifacts = list_artifacts(Path("."))

# Export by artifact name (or module/name when names collide)
export_artifacts(Path("/tmp/out"), "step", ("sphere",))

# Ad-hoc geometry — STEP, STL, and GLB in one call (tests and scripts)
export_part(make_sphere(), "sphere", "/tmp/out")
```

`export_artifacts()` and `list_artifacts()` power CI smoke tests and integration tests in [`tests/test_makerrepo.py`](../tests/test_makerrepo.py).

## Render (`cad_tooling.render`)

Headless PNG previews via Open CASCADE (OCP). In CI and the devcontainer, Xvfb provides a virtual display when `DISPLAY` is unset.

### CLI

```bash
# Use @render settings from the matching artifact (STL stem = artifact name)
uv run python -m cad_tooling.render dist/sphere.stl -o dist/sphere.png

# Override camera for a one-off render
uv run python -m cad_tooling.render dist/sphere.stl -o dist/sphere-top.png --camera top
```

Common flags: `--width`, `--height`, `--background R,G,B`, `--face-color R,G,B`, `--camera`, `--azimuth`, `--elevation`, `--fit-margin`.

<a id="render-decorator"></a>

### `@render` decorator

Attach preview settings to an `@artifact` entry point in `cad/`:

```python
from cad_tooling.render_decorator import render
from mr import artifact

@artifact(short_desc="Demo sphere")
@render(camera="iso", face_color=(0.31, 0.63, 1.0))
def sphere() -> Part:
    return make_sphere()
```

**Camera presets:** `iso`, `top`, `bottom`, `front`, `back`, `left`, `right`, `axo_left`, `axo_right`

**Resolution order at render time:** defaults in `RenderConfig` → `@render` on the artifact → CLI flags on `cad_tooling.render` or `cad_tooling.export release`.

See [`cad/parts/sphere.py`](../cad/parts/sphere.py) for a live example.

## Release notes (`cad_tooling.release_notes`)

`release-notes` pairs discovered artifacts with exported `*.stl` and `*.png` files and writes markdown for GitHub Releases. Preview images and download links use absolute `releases/download/{tag}/…` URLs so images render inline on the published release page.

## CI integration

| Dagger function | Command |
|-----------------|---------|
| `artifacts` | `python -m cad_tooling.export smoke` |
| `release-artifact` | `python -m cad_tooling.export release -o /tmp/release-artifacts` |

The GitHub Release workflow runs `release-notes` after exporting assets. See [`.github/workflows/release.yml`](../.github/workflows/release.yml).

## Testing

Tooling tests live in `cad_tooling_tests/` (separate from CAD model tests in `tests/`):

```bash
uv run pytest cad_tooling_tests
uv run pytest                    # runs both test directories
```

## When to use `mr` vs `cad_tooling`

| Task | Prefer |
|------|--------|
| List / export / view artifacts locally | `uv run mr artifacts …` |
| Parametric generator export | `uv run mr generators …` |
| CI artifact smoke, release STL+PNG, pytest helpers | `cad_tooling.export` |
| Headless PNG preview of an STL | `cad_tooling.render` |
| Per-artifact release camera/color in source | `@render` from `cad_tooling.render_decorator` |
