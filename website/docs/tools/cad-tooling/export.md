---
sidebar_position: 2
---

# Export

Programmatic export for tests, CI, and release automation. Prefer [`mr` CLI](/tools/makerrepo) for interactive local export.

## CLI

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
  --repo Coffee2Bits/CAD-as-Code-Template \
  --tag v0.1.0 \
  -o dist/RELEASE_BODY.md
```

Or via `just`:

```bash
just export-smoke
just export                            # STL + PNG release bundle to dist/
just export /tmp/out step sphere       # single-artifact STEP export
just release-notes v0.1.0
just render-artifact sphere /tmp/out   # STL + PNG — see render doc
```

Headless PNG previews use [Render](/tools/cad-tooling/render) (`cad_tooling.render`), not `mr artifacts snapshot`.

## Supported formats

| Format | Notes |
|--------|-------|
| `step` | CAD interchange (preferred) |
| `stl` | Mesh export |
| `brep` | Open CASCADE native |
| `gltf` | Web preview |
| `3mf` | Manufacturing mesh |

Ad-hoc `export_part()` also writes STEP, STL, and GLB in one call.

## Python API

```python
from pathlib import Path
from cad_tooling.export import (
    export_artifacts,
    export_part,
    list_artifacts,
    list_generators,
)

artifacts = list_artifacts(Path("."))
export_artifacts(Path("/tmp/out"), "step", ("sphere",))
export_part(make_sphere(), "sphere", "/tmp/out")
```

`export_artifacts()` and `list_artifacts()` power CI smoke and [`tests/test_makerrepo.py`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/tests/test_makerrepo.py).

## CI integration

| Dagger function | Command |
|-----------------|---------|
| `artifacts` | `python -m cad_tooling.export smoke` |
| `release-artifact` | `python -m cad_tooling.export release -o /tmp/release-artifacts` |

See [CI functions](/reference/ci-functions) and [CI & Dagger](/workflows/ci-and-dagger).
