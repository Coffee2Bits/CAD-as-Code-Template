# Agent instructions

This file is the repo-level guide for AI agents working in this codebase. Read it before adding or changing CAD models, MakerRepo metadata, tests, or CI.

Human-oriented setup and stack overview live in [README.md](README.md).

**Before marking any task or plan complete**, run the [task completion gate](#task-completion-gate) and fix failures introduced by your changes.

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
│   └── assemblies/           # Composed products built from parts
├── cad_tooling/              # Export, render, and release helpers — see cad_tooling/README.md
│   ├── export.py
│   ├── render.py
│   ├── render_config.py
│   ├── render_decorator.py
│   └── release_notes.py
├── justfile                  # Common dev, export, and CI commands — run `just --list`
├── tests/                    # CAD model and integration tests
├── cad_tooling_tests/        # Unit tests for cad_tooling (mirrors package layout)
├── ci/                       # Dagger CI module
├── .devcontainer/            # Dev container (Open CASCADE parity with CI)
└── .cursor/                  # MCP launcher scripts (not model code)
```

### Directory responsibilities

| Path | Purpose | Agent rules |
|------|---------|-------------|
| `cad/parts/` | Single reusable components (brackets, enclosures, product-specific geometry) | One module per part family. Put builders, MR decorators, and Pydantic parameter models here. Prefer [external part libraries](#external-part-libraries) for catalog fasteners, structural sections, gears, and V-Slot — thin-wrap here, do not reimplement ISO tables. |
| `cad/assemblies/` | Products composed from parts (positions, patterns, constraints) | Import from `cad.parts`; do not duplicate part geometry. Assemblies may define their own `@artifact` / `@customizable` entry points. |
| `cad_tooling/` | MakerRepo-aware export, OCP rendering, release notes | See [cad_tooling/README.md](cad_tooling/README.md). Use `export_artifacts()` / `list_artifacts()` in tests and CI; use `export_part()` for non-MR scripts. Import `@render` from `cad_tooling.render_decorator`. |
| `main.py` | Display / demo scripts for OCP CAD Viewer | Keep thin — import builders from `cad/`, call `show_object`. No MR decorators here. **Always run after editing `cad/parts/` or `cad/assemblies/`** (see [Visual verification](#visual-verification-after-cad-edits)). |
| `tests/` | pytest coverage for CAD models and MR integration | Mirror `cad/` structure: `test_<part>.py`, `test_makerrepo.py` for discovery smoke tests. |
| `cad_tooling_tests/` | pytest coverage for workspace tooling | Mirror `cad_tooling/` module layout; keep detached from `tests/`. |
| `.makerrepo/config.yaml` | MR repo config | Set export defaults and optional `pythonpaths`; do not put model logic here. |

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
- Reimplement standard catalog geometry (ISO fasteners, beam tables, gear tooth math, V-Slot profiles) when an [external part library](#external-part-libraries) already provides it.

---

## External part libraries

Optional [build123d](https://build123d.readthedocs.io/) extensions are **commented out** in [`pyproject.toml`](pyproject.toml). Uncomment the package you need and run `uv sync` before importing. Human-oriented links and install lines: [README — References](README.md#references--build123d-part-libraries).

Use the **one-line scope** below as the first categorizer — if the task fits a row, reach for that library instead of hand-building catalog geometry in `cad/parts/`.

| Library | One-line scope | Reach for it when the task involves… |
|---------|----------------|--------------------------------------|
| [bd_warehouse](https://github.com/gumyr/bd_warehouse) | Catalog mechanical parts: fasteners, bearings, flanges, pipes, threads, and sprockets. | Metric/imperial **nuts, screws, washers**; **clearance, tap, threaded, or captive-nut holes**; **bearings** and press-fit holes; **pipe/flange** runs; **helical threads**; **sprockets**; basic **OpenBuilds** fasteners (see also bd-vslot for extrusion). Docs: [bd-warehouse.readthedocs.io](https://bd-warehouse.readthedocs.io/). |
| [bd_beams_and_bars](https://gitlab.com/experimentslabs/3d/bd_beams_and_bars) | Standard structural beams and bars for frames and welded assemblies. | **I-beams, angles, channels**, and other **construction/structural profiles**; welded or bolted **frames** where section tables matter. Git install only. Docs: [bd-beams-and-bars.3d.experimentslabs.com](https://bd-beams-and-bars.3d.experimentslabs.com/). |
| [py_gearworks](https://github.com/GarryBGoode/py_gearworks) | Parametric gears, gear pairs, and drive trains. | **Spur, helical, bevel, planetary, rack** geometry; **meshing gear pairs** and drivetrain layout (prefer over bd_warehouse’s simpler gear helpers for dedicated gear work). |
| [bd-vslot](https://github.com/keeeal/bd-vslot) | V-Slot extrusion profiles and linear-frame components. | **V-Slot / OpenBuilds-style extrusion** rails, gantry **linear frames**, and slot-compatible **frame hardware** (PyPI: `bd-vslot`). Docs: [bd-vslot.readthedocs.io](https://bd-vslot.readthedocs.io/). |

**Integration rules**

- Add a **thin wrapper** in `cad/parts/` (e.g. `make_m5_hex_nut` calling `bd_warehouse.fastener.HexNut`) when the repo needs a stable builder API or MakerRepo entry points — not a fork of library internals.
- Keep **`simple=True`** (default) on bd_warehouse fasteners in tests and CI unless the task explicitly needs modeled threads.
- Library objects are build123d solids/`BasePartObject` — return `.part` (or equivalent) from `make_*` builders so tests and assemblies stay consistent.
- New `@artifact` wrappers around library-backed parts still need pytest geometry checks and the [agent workflow checklist](#agent-workflow-checklist).

---

## Standard part module pattern

Every part module should follow this three-layer pattern (see [`cad/parts/sphere.py`](cad/parts/sphere.py)):

```python
# 1. Builder — plain function, used by tests, assemblies, and MR wrappers
def make_<part>(...) -> Part:
    ...

# 2. Artifact — fixed default configuration, no arguments
@artifact(cover=False, short_desc="...")
@render(camera="iso")  # optional — per-artifact release PNG settings
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
| `@render` | Release PNG previews and inclusion in `export release` / GitHub Release notes | Omit when the artifact should not appear in release bundles (MR discovery and ad-hoc export still work) |
| `@customizable` | Users should vary dimensions/material choices via parameters | Fixed one-off geometry with no parametric intent |
| `@cached` | A sub-build is expensive and called repeatedly with the same args | Simple/fast builders |

### `@artifact` options (use deliberately)

| Argument | Guidance |
|----------|----------|
| `cover=True` | At most one per repo — repo thumbnail in MakerRepo.com |
| `sample=True` | Dev/test geometry not meant for end users |
| `short_desc` | Required for user-facing artifacts; keep under 128 chars |
| `export_step` / `export_3mf` | Omit to inherit from [`.makerrepo/config.yaml`](.makerrepo/config.yaml) |

### `@render` (release previews)

Place `@render` directly above the function, with `@artifact` above it:

```python
@artifact(short_desc="Mounting bracket")
@render(camera="top", azimuth=15, face_color=(0.4, 0.7, 1.0), width=1024)
def bracket() -> Part:
    return make_bracket()
```

| Field | Purpose |
|-------|---------|
| `camera` | Preset: `iso`, `top`, `bottom`, `front`, `back`, `left`, `right`, `axo_left`, `axo_right` |
| `azimuth` / `elevation` | Extra pose in degrees (after preset) |
| `width` / `height` | PNG size |
| `background` / `face_color` | RGB triplets in 0.0–1.0 |
| `fit_margin` | Passed to `V3d_View.FitAll` |
| `show_edges` / `edge_color` / `edge_width` | OCCT face-boundary edges on BRep solids (default on, black, 1 px); not on STL imports |
| `lighting` | Lighting preset and intensities — see below |

**Lighting** (`lighting={...}` or nested :class:`~cad_tooling.render_config.LightingConfig`):

| Field | Purpose |
|-------|---------|
| `preset` | `default` (global default), `studio`, `bright`, `flat` — see `LIGHTING_PRESETS` in `render_config.py` |
| `intensity` | Global multiplier for directional lights and material reflectance (default `1.0`) |
| `ambient` | Material ambient reflectance override (0.0–2.0) |
| `headlight` | OCCT directional light scale override (0.0–2.0) |
| `fill` | Material diffuse reflectance override (0.0–2.0) |

```python
@render(camera="iso", lighting={"preset": "bright", "intensity": 1.2})
def bracket() -> Part:
    return make_bracket()
```

CLI overrides: `--show-edges` / `--no-show-edges`, `--edge-color`, `--edge-width`,
`--lighting-preset`, `--light-intensity`, `--ambient-intensity`,
`--headlight-intensity`, `--fill-intensity`.

Resolution order at render time: **defaults** → **`@render` on the artifact** → **CLI flags** (`cad_tooling.render` / `cad_tooling.export release`).

**Release export:** `export release`, release notes, and GitHub Release uploads include only `@artifact` functions that also declare `@render`. Artifacts without `@render` remain discoverable via `mr artifacts list` and `cad_tooling.export export`, but are omitted from release PNG/STL bundles.

### Part preview colors

Assign build123d's native **`Part.color`** (inherited from `Shape`) in each part's `make_*` builder — not in assemblies:

```python
# cad/parts/sphere.py
PART_COLOR = Color(0.31, 0.63, 1.0)

def make_sphere(...) -> Part:
    part = ...  # geometry
    part.color = PART_COLOR
    return part
```

- **`Compound` assemblies** compose already-colored parts with `Compound(children=[...])`. Do not set colors in `cad/assemblies/` — release and OCP renders read each child's `shape.color`.
- **`@render`** on an artifact controls cameras and PNG size for release export. Omit `face_color` when the builder sets `part.color`; keep `face_color` only as a fallback for artifacts whose geometry has no color.
- Assemblies that need a sub-part's color constant may import `PART_COLOR` from `cad.parts.<name>` for tests or docs, not for re-assigning on assembly children.

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
| `makerrepo-cli` (`mr`) | Discovery, export, view (headless PNG via `cad_tooling.render`, not `mr snapshot`) | Dev dep |

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
uv run mr artifacts export sphere -o /tmp/out --format step
uv run mr artifacts export sphere -o /tmp/out/sphere.stl

# View in OCP CAD Viewer (extension must be running)
uv run mr artifacts view sphere
```

Headless PNG previews use `cad_tooling.render` (OCP + Xvfb), not `mr artifacts snapshot` (Playwright). See `website/docs/tools/cad-tooling/render.md`.

```bash
just render-artifact sphere /tmp/out
# or: export STL then render
just export /tmp/out stl sphere
just render /tmp/out/sphere.stl /tmp/out/
```

Refer to artifacts by **name** (`sphere`) or **module/name** (`cad.parts.sphere/sphere`) when names collide.

Supported export formats: `step`, `stl`, `brep`, `gltf`, `3mf`, `svg`, `dxf`.

### Generators (parametric models)

```bash
# List discovered @customizable functions
uv run mr generators list

# Export with a JSON parameter payload
uv run mr generators export sphere_generator -p '{"radius": 15}' -o /tmp/out/
uv run mr generators export sphere_generator -p @params.json -o /tmp/out/sphere.step

# View in OCP CAD Viewer (extension must be running)
uv run mr generators view sphere_generator -p '{"radius": 20}'
```

Payload forms: inline JSON string, `@path/to/file.json`, or `-` for stdin.

### Cache (when using `@cached`)

```bash
uv run mr cache list
uv run mr cache prune
```

### Visual verification after CAD edits

**Required:** after any edit to a file under `cad/parts/` or `cad/assemblies/`, always run `main.py` so the change is displayed in OCP CAD Viewer.

1. Point `main.py` at the part or assembly you changed — import its `make_*` builder (or assembly builder) and call `show_object`. Keep one focused demo per run.
2. From the repo root:

```bash
just view
# or: uv run python main.py
```

3. Confirm the model appears in the OCP CAD Viewer panel (extension must be open). Use ocp-viewer-mcp `capture_ocp_screenshot` when you need visual confirmation in the agent session.

Skip this only for edits that do not touch model geometry or display behavior (e.g. docstring-only changes).

### Test-driven development

Follow this order for feature work — do not weaken or delete tests just to land an implementation:

1. **Define desired behavior first** — write or update tests that describe what the feature should do (geometry, discovery, export, margins, fit) before or alongside the model change.
2. **Diagnose incongruent tests** — when a test fails, decide whether the test or the product is wrong. If the test encodes brittle assumptions (fixed counts, closed sets, or incidental repo state) instead of the behavior under change, update the test — do not weaken the product or delete coverage just to make a bad test pass.
3. **Implement** — change model or tooling code until behavior matches the tests.

**Cutout / reference alignment (required when embedding hardware):**

- Use one **shared seat** (origin + axis) for the pocket cutter and the visual/reference solid — never compute placement from different faces or formulas.
- Prefer a **hex prism cutter** in the same pose as the reference hardware: derive plane and rotation from the positioned reference nut, then convert margin in millimetres to a larger hex profile (`across_flats + 2 × margin` or an equivalent scale factor). Never scale or offset the visual reference solid; never use face offset if it rounds the hex into a circular pocket.
- Add tests that the zero-margin cutter matches the reference pose, and that the positioned reference fits inside the cutout with no solid overlap.
- After geometry edits, run `just view` and confirm the reference part sits flush inside its margin cutout in OCP CAD Viewer.

**Test design rules for this repo:**

| Pattern | Prefer | Avoid |
|---------|--------|-------|
| Artifact discovery | `assert "sphere" in names` (required part present) | `assert names == {"sphere"}` (breaks when unrelated parts are added) |
| Partial export / release checks | Scope to the artifact under test, e.g. `collect_release_assets(..., names=("sphere",))` | Requiring every discovered artifact in a test that only exported one STL |
| Geometry changes | Explicit assertions for the new behavior (pocket depth, fit, margin) | Loosening unrelated bounds so old inequalities still pass |
| Cutouts vs reference parts | Assert profile alignment (shared seat origin, matched hex rotation, wall-normal angles) and flush fit; use the same plane/orientation helpers for the cutter and the reference solid | Hand-drawn pocket sketches with separate placement math from the reference part |
| Reference / library parts | Keep `@artifact` when the part should be discoverable; use `sample=True` only for throwaway dev geometry | Dropping publish metadata to silence discovery tests |
| Destructive `just` recipes (`init`, `template-apply`, …) | `tests/functional/` — copy repo to `tmp_path`, run `just` only in the copy via `run_just()` | Running `just init` or similar against the real workspace root |

### Testing just commands (agents)

Recipes that rewrite the workspace (`just init`, `just init-dry-run`, `just template-apply`, and similar) **must never be run against the real repository root** to “check” behavior — that mutates `template.repo.toml`, `README.md`, versions, and docs in place.

Instead:

1. Add or extend tests under [`tests/functional/`](tests/functional/) (see [`tests/functional/conftest.py`](tests/functional/conftest.py)).
2. Use the `isolated_repo` fixture — it `copytree`s the repo into `tmp_path` (excluding `.venv`, `.git`, `node_modules`, etc.).
3. Invoke recipes only via `run_just(isolated_repo, "init", "--owner", "acme", …)` — it refuses to run when `cwd` is `REPO_ROOT`.
4. Assert on files inside the isolated copy and, when relevant, that the real repo paths are unchanged.

```bash
uv run pytest tests/functional/ -v          # just-command functional suite only
uv run pytest tests/functional/test_just_init.py -v
```

Unit tests for init logic without the `just` CLI stay in [`tests/test_template_identity.py`](tests/test_template_identity.py) (monkeypatched `REPO_ROOT` / `tmp_path`). New `just` recipe coverage belongs in `tests/functional/`.

### Agent workflow checklist

When adding or changing a published model:

1. Implement `make_*` builder in `cad/parts/` or `cad/assemblies/` (or wrap an [external part library](#external-part-libraries) when the geometry is catalog-standard).
2. Add `@artifact` and/or `@customizable` wrappers in the same module.
3. Add pytest tests (geometry + export).
4. **Visual verify:** update `main.py` if needed, then `just view` (see [Visual verification](#visual-verification-after-cad-edits)).
5. Confirm MR discovery: `just mr-artifacts` / `just mr-generators`.
6. **Completion gate:** run `just ci` (or the [local equivalent](#task-completion-gate)) and do not finish until it passes.

For any other code change (tooling, tests, CI, config), skip steps 1–5 as applicable but **always** [sync documentation](#keep-docs-in-sync-mandatory) when behavior, commands, paths, or names change, then run the completion gate before reporting done.

---

## Formatter and linter alignment

**Ruff is the single toolchain** for Python lint (`ruff check`) and format (`ruff format`). CI enforces both via `just lint` / Dagger `lint`. Editor format-on-save, pre-commit, and agents must use the **same** Ruff binary and `pyproject.toml` config — never a different formatter or linter.

### Required alignment

| Layer | Must use |
|-------|----------|
| CI / `just lint` | `uv run ruff check .` + `uv run ruff format --check .` + `uv run mypy …` + `uv run vulture` |
| Editor format-on-save | Ruff extension (`charliermarsh.ruff`), `importStrategy: fromEnvironment` |
| Pre-commit | `uv run ruff check --fix` + `uv run ruff format` + `uv run vulture` (see [`.pre-commit-config.yaml`](.pre-commit-config.yaml)) |
| Agents after Python edits | `just format` (or `uv run ruff format .`) before the completion gate |

Workspace settings live in [`.vscode/settings.json`](.vscode/settings.json); the dev container mirrors them in [`.devcontainer/devcontainer.json`](.devcontainer/devcontainer.json).

### Do not use

- Black, autopep8, yapf, isort standalone, or the built-in Python formatter for this repo.
- A Ruff extension version bundled with the IDE instead of the project venv — `fromEnvironment` is required.
- Hand-edited formatting that skips `ruff format` when CI will check it.

### When format-on-save disagrees with CI

That is a **configuration bug**, not a reason to weaken CI or skip `ruff format --check`. Fix editor/MCP settings so save-time formatting matches `uv run ruff format`. Leaving them misaligned causes an endless regression loop: auto-format rewrites files, CI rejects them, agents “fix” them, auto-format breaks them again.

Before marking Python work complete, confirm:

```bash
uv run ruff format --check .
```

---

## Task completion gate

**Required:** do not consider a task or plan complete until the CI gate passes locally. Run it yourself — do not assume prior green runs still apply after your edits.

Preferred command (matches GitHub Actions):

```bash
just ci
```

Local equivalent when Dagger is unavailable or for a faster loop:

```bash
just quality && just export-smoke
```

This runs the same three stages as CI:

1. **lint** — ruff check, ruff format check, mypy, vulture
2. **artifacts** — export smoke for all `@artifact` functions
3. **test** — pytest (including `tests/test_makerrepo.py`)

If the gate fails, fix the failures and re-run until it passes. Report the command you ran and that it succeeded in your final summary.

Skip only when the change cannot affect CI (e.g. typo in a comment with no tooling impact). When in doubt, run the gate.

---

## Testing expectations

| Change | Required tests |
|--------|----------------|
| New part | Validity, key dimensions, volume/bbox; export round-trip where applicable |
| Part wrapping an [external library](#external-part-libraries) | Same as new part; assert fit/clearance against the library instance (e.g. nut in pocket), not duplicated ISO constants |
| New assembly | Overall bounds; confirms sub-parts are present; critical interfaces |
| New `@artifact` | Will be picked up by `tests/test_makerrepo.py` — ensure the artifact name appears in `mr artifacts list`; do not require exclusive discovery (other artifacts may coexist) |
| New `@customizable` | Same discovery test; consider a test that exports with non-default parameters |
| `justfile` init / template / setup recipes | Add functional tests in [`tests/functional/`](tests/functional/) using `isolated_repo` + `run_just()` — never run destructive recipes on the real repo to verify behavior |

Keep files under **300–400 lines**. Split large parts into submodules if needed.

---

## CI gates

GitHub Actions runs `dagger call -m ./ci check`, which executes:

1. **lint** — ruff, mypy, vulture
2. **artifacts** — `python -m cad_tooling.export smoke` (discover all `@artifact` functions, export STEP + STL)
3. **test** — pytest (includes `test_makerrepo.py`)

Local equivalent:

```bash
just ci
# or: dagger call -m ./ci check --source=.
```

Common `just` recipes: `just quality` (lint + pytest), `just export-smoke`, `just release dist/`, `just ci-release dist/`. Run `just --list` for the full set — see [README.md](README.md#make-commands-just).

Any new `@artifact` is picked up automatically by `cad_tooling.export` and `tests/test_makerrepo.py`. No CI edits required when adding artifacts.

---

## Commit messages (release-please)

[release-please](https://github.com/googleapis/release-please) reads **Conventional Commits** on `main` to decide semver bumps, fill `CHANGELOG.md`, and open Release PRs. Agents should write commit and PR titles in this format so releases stay predictable.

### Format

```text
<type>[optional scope][optional !]: <short description>

[optional body — blank line after subject]

[optional footers]
```

- **Subject line** — imperative mood, lowercase after the colon, no trailing period, ~72 chars or less.
- **Scope** (optional) — area touched, e.g. `sphere`, `export`, `ci`.
- **`!` before the colon** — breaking change (major semver bump).

Follow [Conventional Commits](https://www.conventionalcommits.org/) and the [release-please commit guide](https://github.com/googleapis/release-please#how-should-i-write-my-commits).

### SemVer mapping

| Prefix / signal | Version bump | Example |
|-----------------|--------------|---------|
| `fix:` | patch | `fix(sphere): correct embossed text depth` |
| `feat:` | minor | `feat(sphere): add optional embossed label` |
| `feat!:`, `fix!:`, `refactor!:`, … | major | `feat(export)!: drop STL from default release bundle` |
| `BREAKING-CHANGE:` footer | major | see [breaking changes](#breaking-changes) |

### Releasable commits (Python)

This repo uses `release-type: python` in [`release-please-config.json`](release-please-config.json). Only commits whose **subject** starts with one of these types create changelog entries and can trigger a Release PR:

| Type | Use for |
|------|---------|
| `feat` | New user-facing behavior, new `@artifact`, new part/assembly |
| `fix` | Bug fixes, broken exports, incorrect geometry |
| `deps` | Dependency version changes (`pyproject.toml`, lockfile) |
| `docs` | Documentation-only changes (Python strategy treats these as releasable) |

These types **do not** open or extend a Release PR on their own: `chore`, `build`, `ci`, `refactor`, `test`, `style`, `perf` (unless marked breaking). Use them for internal work, CI, refactors, and tests.

### Breaking changes

Prefer `type!:` in the subject:

```text
feat(export)!: require explicit format for release smoke
```

Or a footer in the commit body (must appear **after** the main description):

```text
feat(export): change default release bundle

BREAKING-CHANGE: STL is no longer exported unless --format stl is passed.
```

### Pull requests and merge strategy

- **Squash-merge PRs to `main`.** The squash commit message (usually the PR title) becomes the entry release-please parses.
- Write the **PR title** in Conventional Commit form — same rules as commit subjects.
- Keep PR bodies for context; release notes come from the title unless you use [footers](#multiple-changes-in-one-commit) or [overrides](#fixing-release-notes-after-merge).
- Prefer a **linear `main` history** so changelog entries match merged work, bisect stays usable, and WIP commits inside a PR do not land on `main`.

### Multiple changes in one commit

When one squash commit covers several releasable items, add **footer lines at the bottom** of the commit body (release-please reads these as separate changelog entries):

```text
feat(sphere): add embossed text and fix export scale

feat(sphere): add optional surface label
fix(export): correct STL units on release smoke
```

Footers must come **after** the main body text.

### Forcing a version

To request a specific semver in the next Release PR, add to the commit body (case insensitive):

```text
chore: release 1.2.0

Release-As: 1.2.0
```

Empty commits are fine: `git commit --allow-empty -m "chore: release 1.2.0" -m "Release-As: 1.2.0"`.

### Fixing release notes after merge

If a merged PR title or squash message was wrong, edit the **merged PR description** and add:

```text
BEGIN_COMMIT_OVERRIDE
feat(sphere): add embossed label parameter
fix(export): correct STL scale on release smoke
END_COMMIT_OVERRIDE
```

Re-run release-please (or wait for the next push to `main`). Works reliably with **squash merge**; plain merge commits are harder to override.

### Examples for this repo

```text
feat(sphere): add embossed text on default artifact
fix(render): fit margin for wide assemblies in release PNGs
docs: document release-please commit conventions in AGENTS.md
deps: bump makerrepo-cli to 0.4.0
chore: reorganize cad_tooling modules          # no Release PR entry
ci: pin Dagger version in workflow             # no Release PR entry
test(sphere): assert embossed text bbox        # no Release PR entry
```

When the user asks for a git commit, use the same Conventional Commit subject line.

---

## Releases

Releases are automated with [release-please](https://github.com/googleapis/release-please). Configuration lives in [`release-please-config.json`](release-please-config.json) and [`.release-please-manifest.json`](.release-please-manifest.json).

**Typical release flow:**

1. Merge PRs to `main` with [Conventional Commit](#commit-messages-release-please) titles (squash merge).
2. [`.github/workflows/release-please.yml`](.github/workflows/release-please.yml) opens or updates a **Release PR** (`chore: release ${version}`) that bumps `pyproject.toml`, updates `CHANGELOG.md`, and proposes the next semver.
3. Merge the Release PR when ready. The workflow tags `v{version}` and publishes a GitHub Release with STL/PNG assets and generated artifact notes.

Published assets use the same pipeline as manual releases: Dagger `check`, `release-artifact`, then `release-notes` for the GitHub Release body.

**Manual tag fallback:** pushing a semver tag (`v*.*.*`) still triggers [`.github/workflows/release.yml`](.github/workflows/release.yml) for ad-hoc releases.

**Release PR labels:** `autorelease: pending` (open Release PR), `autorelease: tagged` (merged and tagged). If release-please stops opening Release PRs, check for a stale `autorelease: pending` label on an old Release PR and remove it before re-running the workflow.

Keep `pyproject.toml` `version` aligned with the tag. Local dry-run:

```bash
uv run python -m cad_tooling.export release -o dist/
uv run python -m cad_tooling.export release-notes \
  --assets-dir dist --repo OWNER/REPO --tag v0.0.1 -o dist/RELEASE_BODY.md
dagger call -m ./ci release-artifact --source=. export --path=./dist
```

Release notes format: [`.github/release_template.md`](.github/release_template.md). New `@artifact` functions are picked up automatically — no workflow edits required.

### Release preview configuration

Per-artifact PNG settings live on the `@render` decorator next to each `@artifact` (see [`cad/parts/sphere.py`](cad/parts/sphere.py)). Full CLI and preset reference: [cad_tooling/README.md](cad_tooling/README.md).

---

## Conventions summary

- **Commits and PRs**: use [Conventional Commits](#commit-messages-release-please) (`feat:`, `fix:`, `deps:`, `docs:` for releasable work; squash-merge to `main`).
- **Formatter and linter**: keep [Ruff aligned](#formatter-and-linter-alignment) across editor, pre-commit, and CI — mismatches cause endless format regressions.
- **Completion gate**: run `just ci` (or `just quality && just export-smoke`) and confirm success before marking any task complete.
- **Doc sync**: when changing behavior, names, or commands, search docs for stale references and update them in the same change — see [Keep docs in sync (mandatory)](#keep-docs-in-sync-mandatory).
- **Troubleshooting**: when a task debugs a tool with a troubleshooting page, document new reproducible failures and fixes there — see [Troubleshooting documentation](#troubleshooting-documentation).
- **Units**: millimeters unless a part docstring says otherwise.
- **Return types**: `Part` or `Compound` from builders; MR wrappers return the same.
- **Imports**: `from mr import artifact, customizable, cached` — not `import makerrepo`.
- **Exports**: write to `/tmp` or pytest `tmp_path`; never commit generated meshes (except golden fixtures under `tests/fixtures/`).
- **Prototyping**: use build123d-mcp `execute` for experiments; promote stable code into `cad/parts/` with tests. For catalog parts, prototype with the matching [external library](#external-part-libraries) rather than one-off ISO dimensions.
- **Visualization**: after every `cad/parts/` or `cad/assemblies/` edit, run `just view` (update imports in `main.py` first if the displayed model changed). Use `just mr-view <name>` for MR-driven viewing of `@artifact` entry points.

---

## Reference

- [MakerRepo library](https://docs.makerrepo.com/makerrepo-library/)
- [MakerRepo CLI](https://docs.makerrepo.com/makerrepo-cli/)
- [MakerRepo artifacts](https://docs.makerrepo.com/makerrepo-library/artifacts/)
- [MakerRepo generators](https://docs.makerrepo.com/makerrepo-library/generators/)
- [CAD tooling](cad_tooling/README.md) — export, render, release notes
- Live example: [`cad/parts/sphere.py`](cad/parts/sphere.py)
- [build123d external part libraries](https://build123d.readthedocs.io/en/latest/external.html#part-libraries) — upstream index

### External part libraries (optional deps)

See [External part libraries](#external-part-libraries) for when to use each. Install via commented lines in `pyproject.toml`.

| Library | One-line scope |
|---------|----------------|
| [bd_warehouse](https://github.com/gumyr/bd_warehouse) | Catalog mechanical parts: fasteners, bearings, flanges, pipes, threads, and sprockets. |
| [bd_beams_and_bars](https://gitlab.com/experimentslabs/3d/bd_beams_and_bars) | Standard structural beams and bars for frames and welded assemblies. |
| [py_gearworks](https://github.com/GarryBGoode/py_gearworks) | Parametric gears, gear pairs, and drive trains. |
| [bd-vslot](https://github.com/keeeal/bd-vslot) | V-Slot extrusion profiles and linear-frame components. |

---

## Documentation (Docusaurus / GitHub Pages)

Human-oriented documentation lives in [`website/`](website/) (Docusaurus). The published site is built from `main` and deployed via [`.github/workflows/docs.yml`](.github/workflows/docs.yml).

**Published URL:** `https://coffee2bits.github.io/CAD-as-Code-Template/`  
**Source repo:** `Coffee2Bits/CAD-as-Code-Template` — never hardcode the old `cad_as_code_project` slug in docs or config.

### What goes where

| Location | Role |
|----------|------|
| [`README.md`](README.md) | Turnkey template landing: pitch, CAD-as-Code concept, shortest start path, and links into the docs. Keep it focused on orientation, not full-manual detail. |
| [`website/docs/`](website/docs/) | Deep guides: tools, workflows, troubleshooting, reference, and contributing docs. This is the canonical home for detailed user documentation. |
| [`AGENTS.md`](AGENTS.md) | Agent contract only. Do **not** duplicate agent rules on the docs site; [`website/docs/contributing/for-agents.md`](website/docs/contributing/for-agents.md) summarizes and links here. |
| [`cad_tooling/README.md`](cad_tooling/README.md) | Short pointer to `website/docs/tools/cad-tooling/` once that section exists. |
| [`.github/GITHUB_SETUP.md`](.github/GITHUB_SETUP.md) | Short checklist; canonical guide at `website/docs/getting-started/github-setup.md`. |
| [`template.repo.toml`](template.repo.toml) | **Source of truth** for repo identity. `just init` reads this file (plus optional CLI overrides); `just template-apply` re-applies after edits. See [github-setup](website/docs/getting-started/github-setup.md#replace-template-identity-in-your-repo). **`cad_tooling/` is never modified.** |

### Keep docs in sync (mandatory)

**Doc drift is a serious defect.** The docs site (`website/docs/`), README, and in-repo pointers must describe **current** behavior. When you change any file whose name, path, command, API, workflow, or default appears in documentation, you **must** update every doc reference in the same change — do not leave follow-up “doc TODOs.”

**Before marking work complete:**

1. **Read the canonical doc** for the area you touched (Getting started, Tools, Workflows, Troubleshooting, or Reference under `website/docs/`). If no page exists, add or extend the closest matching page before claiming the behavior is documented.
2. **Search for stale references** to anything you renamed, removed, or changed. At minimum search:
   - `website/docs/` (all `.md` files)
   - [`README.md`](README.md)
   - [`.github/GITHUB_SETUP.md`](.github/GITHUB_SETUP.md)
   - [`cad_tooling/README.md`](cad_tooling/README.md)
   Use ripgrep for the **old** command string, recipe name, file path, env var, workflow name, status check name, config key, and any prose you replaced in code comments or docstrings.
3. **Update every hit** — links, tables, mermaid labels, code blocks, and “jump to line” examples. Prefer relative links between Docusaurus pages; keep GitHub blob links pointed at the correct path on `main`.
4. **Verify behavior matches prose** — commands in docs must match `justfile` / CLI flags; checklist items must match real GitHub settings; diagrams must match architecture you implemented.
5. **Template identity** — if the change involves org/repo URLs, Pages `baseUrl`, or package naming, update [`template.repo.toml`](template.repo.toml) and run `just init` or `just template-apply` (or document that users must), rather than hand-editing `website/docusaurus.config.ts` or scattering owner/repo strings.
6. **Build check** — run `just docs-build` when `website/**`, `README.md`, or doc-linked config changes; fix broken links (`onBrokenLinks: throw`).

| You change… | Also update… |
|-------------|--------------|
| `justfile` recipe | `website/docs/tools/just.md`, `website/docs/reference/justfile-recipes.md`, any page that cites the command |
| Export / release / render | `website/docs/tools/cad-tooling/`, `website/docs/workflows/export-and-formats.md`, `website/docs/workflows/releases.md` |
| CI / Dagger / workflows | `website/docs/workflows/ci-and-dagger.md`, `website/docs/reference/ci-functions.md`, `website/docs/getting-started/github-setup.md`, `.github/GITHUB_SETUP.md` |
| Dev container / viewer / MCP | Matching page under `website/docs/getting-started/` or `website/docs/tools/` |
| New template-user setup step | `website/docs/getting-started/` (usually `quick-start.md`, `github-setup.md`, or `releases.md`) and `.github/GITHUB_SETUP.md` |
| Novel failure mode or fix for a tool below | Matching page under `website/docs/troubleshooting/` (see [Troubleshooting documentation](#troubleshooting-documentation)); add a row to [`troubleshooting/index.md`](website/docs/troubleshooting/index.md) quick-routing table when the symptom is new |

### Troubleshooting documentation

When a task involves **diagnosing, fixing, or working around** a tool or workflow failure, check whether it maps to a troubleshooting page **before** marking work complete. If you discover a **new** symptom, root cause, or fix that future users or agents are likely to hit again, document it in the same change.

**When to update**

- You debugged a non-obvious error and found a reproducible fix.
- You changed setup, config, or commands that make an existing troubleshooting entry wrong or incomplete.
- You added or removed a failure mode (new MCP launcher behavior, CI gate, export format, container mount, etc.).

**When to skip**

- One-off environment issues (typo, wrong directory, transient network) with no template-wide lesson.
- The entry already exists on the matching page — improve it only if your fix adds missing steps or corrects stale prose.

**Routing table** — match the task area to the canonical troubleshooting page:

| Task touches… | Troubleshooting page |
|---------------|----------------------|
| Dev container, `uv sync`, permissions, hooks, rebuild | [`website/docs/troubleshooting/dev-container.md`](website/docs/troubleshooting/dev-container.md) |
| OCP CAD Viewer extension, `just view`, blank panel, ESM crash | [`website/docs/troubleshooting/ocp-viewer.md`](website/docs/troubleshooting/ocp-viewer.md) |
| MCP servers, `.cursor/mcp.json`, agent tools in container | [`website/docs/troubleshooting/mcp.md`](website/docs/troubleshooting/mcp.md) |
| `just ci`, Dagger, Docker socket, CI module | [`website/docs/troubleshooting/dagger-and-docker.md`](website/docs/troubleshooting/dagger-and-docker.md) |
| Export, `mr artifacts`, release PNGs, ruff/mypy/vulture in CI, artifact discovery | [`website/docs/troubleshooting/export-and-ci.md`](website/docs/troubleshooting/export-and-ci.md) |
| release-please, GitHub Pages, branch protection, repo identity | [`website/docs/getting-started/github-setup.md`](website/docs/getting-started/github-setup.md) (`## Troubleshooting`) |

Index and cross-links: [`website/docs/troubleshooting/index.md`](website/docs/troubleshooting/index.md). Tool guides link here from their own **Troubleshooting** sections — keep those links; put detailed fixes on the troubleshooting page, not duplicated in long form on tool pages.

**How to write entries**

- Match existing style: short `##` headings, symptom → fix tables, or numbered recovery sequences.
- State the **symptom** first, then the **fix** (commands must match current `justfile` / scripts).
- One row or bullet per distinct failure mode; link to the canonical guide (e.g. [MCP servers](website/docs/tools/mcp-servers.md)) for architecture, not the reverse.
- If the symptom is new, add a row to the quick-routing table in `troubleshooting/index.md`.
- Keep each troubleshooting page under ~300–400 lines; split if a topic grows.

Run `just docs-build` when you change `website/docs/troubleshooting/**` or pages that link to it.

### Agent rules when editing docs

1. **Respect the documentation shape** — README is the tip of the iceberg, `website/docs/intro.md` is the concept map, quick start is the first-success path, and deeper pages hold technical detail. Avoid duplicating long sections across entry pages.
2. **Linking** — prefer Docusaurus doc IDs (`/tools/just`) or relative paths between pages. For the GitHub repo, use `https://github.com/Coffee2Bits/CAD-as-Code-Template` (or a path suffix like `/tree/main/cad/parts/sphere.py`). Never link to `cad_as_code_project`.
3. **Diagrams** — stack and architecture diagrams live under `website/static/img/` (SVG/PNG) or as Mermaid fenced blocks in markdown (enabled in `docusaurus.config.ts`). Regenerate static SVGs when the stack changes.
4. **Code examples** — copy from working repo sources (`justfile`, `cad/parts/sphere.py`, workflows); verify commands against the current tree before publishing.
5. **README sync** — when moving a README section to the site, replace it with a short paragraph + link to the new doc page. Do not delete template stack/quick-start content from README.
6. **Tooling changes** — follow [Keep docs in sync (mandatory)](#keep-docs-in-sync-mandatory): same PR, same search-and-update pass for every doc reference. GitHub.com settings changes must update [`website/docs/getting-started/github-setup.md`](website/docs/getting-started/github-setup.md) and [`.github/GITHUB_SETUP.md`](.github/GITHUB_SETUP.md).
7. **Local preview** — from `website/`: `npm ci && npm run start` (dev) or `npm run build` (production check). Fix broken links before merging.
8. **Completion gate for doc-only work** — `npm run build` in `website/` must pass. For doc + code changes, still run `just ci` (or `just quality && just export-smoke`) per the [task completion gate](#task-completion-gate).
9. **Deploy** — merging to `main` triggers the docs workflow when `website/**` or `.github/workflows/docs.yml` changes. No manual `gh-pages` branch commits.
10. **File size** — keep each doc page under ~300–400 lines; split into sub-pages if a topic grows.
