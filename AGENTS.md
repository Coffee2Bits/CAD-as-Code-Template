# Agent instructions

This file is the repo-level guide for AI agents working in this codebase. Read it before adding or changing CAD models, MakerRepo metadata, tests, or CI.

Human-oriented setup and stack overview live in [README.md](README.md).

---

## What this repo is

A **Manufacturing-as-Code** workspace: parametric CAD is defined in Python with [build123d](https://build123d.readthedocs.io/), validated with pytest, exported to standard formats, and published via [MakerRepo](https://docs.makerrepo.com/makerrepo-library/) (`mr`).

**Source of truth is always Python model code** — never committed mesh files (STL/STEP) except intentional golden fixtures under `tests/fixtures/`.

---

## Repository layout

```text
.
├── AGENTS.md                 # This file — agent conventions
├── README.md                 # Human setup, stack, and workflow
├── main.py                   # Thin viewer entry points (not model logic)
├── pyproject.toml            # Runtime + dev deps (makerrepo, makerrepo-cli)
├── .makerrepo/
│   └── config.yaml           # Repo-level MakerRepo defaults
├── cad/                      # All durable model code
│   ├── parts/                # Reusable parametric components
│   ├── assemblies/           # Composed products built from parts
│   └── export.py             # Shared export helpers (STEP/STL/GLB)
├── tests/                    # Geometry, export, and MR discovery tests
├── exports/                  # Generated output (gitignored)
├── ci/                       # Dagger CI module
├── .devcontainer/            # Dev container (Open CASCADE parity with CI)
└── .cursor/                  # MCP launcher scripts (not model code)
```

### Directory responsibilities

| Path | Purpose | Agent rules |
|------|---------|-------------|
| `cad/parts/` | Single reusable components (brackets, enclosures, fasteners helpers, etc.) | One module per part family. Put builders, MR decorators, and Pydantic parameter models here. |
| `cad/assemblies/` | Products composed from parts (positions, patterns, constraints) | Import from `cad.parts`; do not duplicate part geometry. Assemblies may define their own `@artifact` / `@customizable` entry points. |
| `cad/export.py` | Format export utilities shared by scripts and tests | Use for ad-hoc exports; prefer `mr artifacts export` for published artifacts. |
| `main.py` | Display / demo scripts for OCP CAD Viewer | Keep thin — import builders from `cad/`, call `show_object`. No MR decorators here. |
| `tests/` | pytest coverage | Mirror `cad/` structure: `test_<part>.py`, `test_makerrepo.py` for discovery smoke tests. |
| `.makerrepo/config.yaml` | MR repo config | Set export defaults and optional `pythonpaths`; do not put model logic here. |
| `exports/` | Local build output | Never commit. CI and tests use `tmp_path` or `/tmp`. |

---

## Parts vs assemblies

### Parts (`cad/parts/`)

A **part** is a reusable parametric component that makes sense on its own:

- Has a clear physical identity (e.g. `sphere`, `mounting_bracket`, `lid`).
- Exposes dimensions as function parameters with sensible defaults.
- Returns `Part` or `Compound` from build123d.
- Is tested for validity, key dimensions (bounding box, volume, holes), and export behavior.
- May expose MakerRepo entry points (see below).

**One module per part family**, named after the part: `cad/parts/sphere.py`, `cad/parts/enclosure.py`.

### Assemblies (`cad/assemblies/`)

An **assembly** combines parts into a product:

- Imports builders from `cad.parts` — never copy-paste part geometry.
- Handles placement (`Location`, `Pos`, patterns), mates, and product-level parameters.
- Returns a single `Compound` (or `Part` when fused intentionally).
- Has its own tests for overall bounds, part count, and critical interfaces.
- May define `@artifact` for the shipped product and `@customizable` for product-level params (e.g. overall width).

**One module per product or assembly family**: `cad/assemblies/demo_widget.py`.

### Layering rules

```text
cad/parts/<component>.py     →  pure geometry, reusable
        ↓ imported by
cad/assemblies/<product>.py  →  composition only
        ↓ referenced by
@artifact / @customizable    →  publishable entry points (on part or assembly)
```

Do **not**:

- Put assembly composition logic in `cad/parts/`.
- Put reusable part geometry in `cad/assemblies/`.
- Add `@artifact` to `main.py` — MR scans packages under `cad/` and top-level modules; keep publishable functions next to the model they build.

---

## Standard part module pattern

Every part module should follow this three-layer pattern (see [`cad/parts/sphere.py`](cad/parts/sphere.py)):

```python
# 1. Builder — plain function, used by tests, assemblies, and MR wrappers
def make_<part>(...) -> Part:
    ...

# 2. Artifact — fixed default configuration, no arguments
@artifact(cover=False, short_desc="...")
def <part>() -> Part:
    return make_<part>(...)

# 3. Generator (optional) — parametric via Pydantic
class <Part>Parameters(BaseModel):
    ...

@customizable(sample_parameters=<Part>Parameters())
def <part>_generator(parameters: <Part>Parameters) -> Part:
    return make_<part>(**parameters.model_dump())
```

| Layer | Function naming | Arguments | Used by |
|-------|-----------------|-----------|---------|
| Builder | `make_<name>` | Python params with defaults | Tests, assemblies, MR wrappers |
| Artifact | `<name>` (noun) | None | `mr artifacts *`, MakerRepo.com CI |
| Generator | `<name>_generator` | Single `BaseModel` param | `mr generators *`, user customization |

### When to add each MakerRepo decorator

| Decorator | Add when | Skip when |
|-----------|----------|-----------|
| `@artifact` | A fixed default build should be listed, exported, or published (demo, product SKU, cover image) | Internal helper geometry, intermediate construction steps, `sample=True` test cuts |
| `@customizable` | Users should vary dimensions/material choices via parameters | Fixed one-off geometry with no parametric intent |
| `@cached` | A sub-build is expensive and called repeatedly with the same args | Simple/fast builders |

### `@artifact` options (use deliberately)

| Argument | Guidance |
|----------|----------|
| `cover=True` | At most one per repo — repo thumbnail in MakerRepo.com |
| `sample=True` | Dev/test geometry not meant for end users |
| `short_desc` | Required for user-facing artifacts; keep under 128 chars |
| `export_step` / `export_3mf` | Omit to inherit from [`.makerrepo/config.yaml`](.makerrepo/config.yaml) |

### `@customizable` requirements

- Exactly **one** argument, typed as a Pydantic `BaseModel` subclass.
- Provide `sample_parameters=` with valid defaults.
- Validate ranges with `Field(gt=0, ...)` etc. — bad params should fail fast.

---

## MakerRepo in this repo

### Packages

| Package | Role | Install |
|---------|------|---------|
| `makerrepo` (`import mr`) | Decorators: `artifact`, `customizable`, `cached`, `BuildEnv`, `Result` | Runtime dep |
| `makerrepo-cli` (`mr`) | Discovery, export, view, snapshot | Dev dep |

Decorators are **non-intrusive**: they do not change builder behavior. They register metadata so `mr` (or MakerRepo.com) can find and run functions.

### Repo config

[`.makerrepo/config.yaml`](.makerrepo/config.yaml):

```yaml
artifacts:
  default_config:
    export_step: true
    export_3mf: false
```

Add `pythonpaths` only if the project moves to a `src/` layout.

### Discovery

From the repo root, `mr` scans Python packages (e.g. `cad/`) and top-level modules for decorated functions. After adding a new part or assembly with MR decorators, verify:

```bash
uv run mr artifacts list
uv run mr generators list
```

---

## MakerRepo CLI — expected use

Always run from the **repository root**. Use `uv run mr ...` so the project venv is used.

### Artifacts (fixed models)

```bash
# List discovered @artifact functions
uv run mr artifacts list
uv run mr artifacts list -o json

# Export — format from --format or file extension
uv run mr artifacts export sphere -o exports/ --format step
uv run mr artifacts export sphere -o exports/sphere.stl

# View in OCP CAD Viewer (extension must be running)
uv run mr artifacts view sphere

# Headless snapshot
uv run mr artifacts snapshot sphere -o exports/sphere.png
```

Refer to artifacts by **name** (`sphere`) or **module/name** (`cad.parts.sphere/sphere`) when names collide.

Supported export formats: `step`, `stl`, `brep`, `gltf`, `3mf`, `svg`, `dxf`.

### Generators (parametric models)

```bash
# List discovered @customizable functions
uv run mr generators list

# Export with a JSON parameter payload
uv run mr generators export sphere_generator -p '{"radius": 15}' -o exports/
uv run mr generators export sphere_generator -p @params.json -o exports/sphere.step

# View / snapshot (same pattern as artifacts)
uv run mr generators view sphere_generator -p '{"radius": 20}'
```

Payload forms: inline JSON string, `@path/to/file.json`, or `-` for stdin.

### Cache (when using `@cached`)

```bash
uv run mr cache list
uv run mr cache prune
```

### Agent workflow checklist

When adding or changing a published model:

1. Implement `make_*` builder in `cad/parts/` or `cad/assemblies/`.
2. Add `@artifact` and/or `@customizable` wrappers in the same module.
3. Add pytest tests (geometry + export).
4. Confirm MR discovery: `uv run mr artifacts list` / `generators list`.
5. Export smoke test: `uv run mr artifacts export <name> -o /tmp/mr-test --format step`.
6. Run full quality gate: `uv run pytest`, `uv run ruff check .`, `uv run mypy cad tests`.

---

## Testing expectations

| Change | Required tests |
|--------|----------------|
| New part | Validity, key dimensions, volume/bbox; export round-trip where applicable |
| New assembly | Overall bounds; confirms sub-parts are present; critical interfaces |
| New `@artifact` | Will be picked up by `tests/test_makerrepo.py` — ensure the artifact name appears in `mr artifacts list` |
| New `@customizable` | Same discovery test; consider a test that exports with non-default parameters |

Keep files under **300–400 lines**. Split large parts into submodules if needed.

---

## CI gates

GitHub Actions runs `dagger call -m ./ci check`, which executes:

1. **lint** — ruff + mypy
2. **artifacts** — `mr artifacts list` + export `sphere` to STEP
3. **test** — pytest (includes `test_makerrepo.py`)

Local equivalent:

```bash
dagger call -m ./ci check --source=.
```

Any new `@artifact` that replaces `sphere` as the CI smoke artifact requires updating [`ci/src/ci/main.py`](ci/src/ci/main.py) and possibly [`tests/test_makerrepo.py`](tests/test_makerrepo.py).

---

## Conventions summary

- **Units**: millimeters unless a part docstring says otherwise.
- **Return types**: `Part` or `Compound` from builders; MR wrappers return the same.
- **Imports**: `from mr import artifact, customizable, cached` — not `import makerrepo`.
- **Exports**: `exports/` locally; never commit generated meshes.
- **Prototyping**: use build123d-mcp `execute` for experiments; promote stable code into `cad/parts/` with tests.
- **Visualization**: `main.py` or `show_object()` for OCP CAD Viewer; `mr artifacts view` for MR-driven viewing.

---

## Reference

- [MakerRepo library](https://docs.makerrepo.com/makerrepo-library/)
- [MakerRepo CLI](https://docs.makerrepo.com/makerrepo-cli/)
- [MakerRepo artifacts](https://docs.makerrepo.com/makerrepo-library/artifacts/)
- [MakerRepo generators](https://docs.makerrepo.com/makerrepo-library/generators/)
- Live example: [`cad/parts/sphere.py`](cad/parts/sphere.py)
