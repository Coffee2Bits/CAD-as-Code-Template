---
sidebar_position: 2
---

# MakerRepo

[MakerRepo](https://docs.makerrepo.com/makerrepo-library/) adds Manufacturing-as-Code metadata to build123d functions. Decorators are **non-intrusive** — they register metadata for discovery and export without changing builder behavior.

```python
from mr import artifact, customizable, cached
```

Import from `mr`, not `makerrepo`.

## Decorators

| Annotation | Applies to | Purpose |
|------------|------------|---------|
| `@artifact` | Fixed publishable models | Discovery, export, release. `short_desc=` for listings; `cover=True` for repo thumbnail (at most one) |
| `@customizable` | Parametric generators | Single Pydantic parameter model; `sample_parameters=` required |
| `@cached` | Expensive sub-builds | Cache repeated builds — use on costly helpers, not simple geometry |

`@artifact` and `@customizable` sit on entry points in `cad/parts/` or `cad/assemblies/` — not on bare `make_*` builders and not in `main.py`.

## Three-layer pattern

See [Parts & assemblies](/modeling/parts-and-assemblies): `make_*` → `@artifact` / `@customizable`.

## `@render` (workspace tooling)

Not a MakerRepo decorator — lives in `cad_tooling` for release PNG settings. Place directly below `@artifact`:

```python
from cad_tooling.render_decorator import render
from mr import artifact

@artifact(short_desc="Demo sphere")
@render(camera="iso", face_color=(0.31, 0.63, 1.0))
def sphere() -> Part:
    return make_sphere()
```

MakerRepo discovery ignores `@render`; release export reads it for matching STL and PNG assets. See [CAD tooling render](/tools/cad-tooling/render).

## Repository config

[`.makerrepo/config.yaml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.makerrepo/config.yaml):

```yaml
artifacts:
  default_config:
    export_step: true
    export_3mf: false
```

| Field | Purpose |
|-------|---------|
| `artifacts.default_config.export_step` | Export STEP when decorator omits `export_step` |
| `artifacts.default_config.export_3mf` | Export 3MF when decorator omits `export_3mf` |
| `pythonpaths` | Optional list — prepend paths to `sys.path` before discovery (for `src/` layouts) |

## CLI cookbook

```bash
uv run mr artifacts list
uv run mr artifacts export sphere -o /tmp/out
uv run mr artifacts export sphere -o /tmp/out --format step
uv run mr artifacts view sphere
uv run mr artifacts snapshot sphere -o /tmp/out/sphere.png
uv run mr generators list
uv run mr generators export sphere_generator -o /tmp/out -p '{"radius": 15}'
```

Or via `just`:

```bash
just mr-artifacts
just mr-export sphere /tmp/out step
just mr-view sphere
just mr-export-generator sphere_generator /tmp/out '{"radius": 15}'
```

Full reference: [MakerRepo CLI docs](https://docs.makerrepo.com/makerrepo-cli/).

## Worked example (sphere)

```python
from build123d import Align, BuildPart, Part, Sphere
from cad_tooling.render_decorator import render
from mr import artifact, customizable
from pydantic import BaseModel, Field

def make_sphere(radius: float = 10) -> Part:
    with BuildPart() as part:
        Sphere(radius=radius, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    return part.part

@artifact(cover=True, short_desc="Demo sphere for workspace smoke tests")
@render(camera="iso", face_color=(0.31, 0.63, 1.0))
def sphere() -> Part:
    return make_sphere()

class SphereParameters(BaseModel):
    radius: float = Field(default=10, gt=0)

@customizable(sample_parameters=SphereParameters())
def sphere_generator(parameters: SphereParameters) -> Part:
    return make_sphere(radius=parameters.radius)
```

Live implementation: [`cad/parts/sphere.py`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/cad/parts/sphere.py)

## MakerRepo.com (optional)

Create a repository on [MakerRepo.com](https://makerrepo.com), push this code, and platform CI builds `@artifact` and `@customizable` functions. Local `mr` workflow works without an account.

## `mr` vs `cad_tooling`

| Task | Prefer |
|------|--------|
| List / export / view artifacts locally | `mr` CLI |
| Parametric generator export | `mr generators …` |
| CI smoke, release STL+PNG, pytest helpers | `cad_tooling.export` |
| Headless PNG from STL | `cad_tooling.render` |
| Per-artifact release camera/color | `@render` decorator |
