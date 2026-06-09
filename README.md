# CAD-as-Code, in a box

A turnkey workspace for **parametric CAD in Python**. Reopen this repo in any **VS Code-based IDE** with [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers) support — VS Code, Cursor, and compatible forks — and you get a complete modeling environment: IDE, live 3D viewer, automated tests, export tooling, and CI, already wired together.

Define geometry with [build123d](https://build123d.readthedocs.io/), preview it in the [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer), validate with pytest, and export to STEP, STL, and GLB. Publish artifacts through [MakerRepo](https://docs.makerrepo.com/makerrepo-library/) (`mr`). Python is the source of truth; mesh files are generated, not hand-edited.

![Dev environment: VS Code-based IDE with build123d code and OCP CAD Viewer showing a parametric sphere](dev_preview.png)

## **What's in the box:**

| Layer | What you get |
|-------|--------------|
| **IDE** | Dev container (`.devcontainer/`) — VS Code, Cursor, or any compatible fork; dependencies sync on start |
| **Modeling** | build123d parts and assemblies under `cad/` |
| **Visualization** | OCP CAD Viewer + `ocp-vscode` bridge for `show_object` |
| **Quality** | pytest geometry tests, ruff, mypy |
| **CI** | [Dagger](https://dagger.io/) — portable CI from local to GitHub Actions to any other pipeline tool; same checks everywhere |
| **Agents** | MCP servers for build123d execution and OCP Viewer screenshots |
| **Publish** | MakerRepo decorators and `mr` CLI for artifact discovery and export |

**AI agents:** see [AGENTS.md](AGENTS.md) for repo structure, parts/assemblies conventions, and MakerRepo usage.

## Stack

| Tool | Role |
|------|------|
| [build123d](https://github.com/gumyr/build123d) | Parametric CAD-as-code (Open CASCADE) |
| [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer) | Live 3D visualization in VS Code-based IDEs |
| [ocp-vscode](https://github.com/bernhard-42/ocp_vscode) | Python bridge for `show_object` |
| [uv](https://docs.astral.sh/uv/) | Dependency and virtualenv management |
| [pytest](https://docs.pytest.org/) | Geometry and export tests |
| [ruff](https://docs.astral.sh/ruff/) / [mypy](https://mypy-lang.org/) | Linting and type checking |
| [Dagger](https://dagger.io/) | Portable CI pipeline (local + GitHub Actions) |
| [build123d-mcp](https://github.com/pzfreo/build123d-mcp) | MCP tools for interactive CAD generation and inspection |
| [ocp-viewer-mcp](https://github.com/dmilad/ocp-viewer-mcp) | MCP screenshots from OCP CAD Viewer for agent vision |
| [MakerRepo](https://docs.makerrepo.com/makerrepo-library/) | Manufacturing-as-code decorators (`@artifact`, `@customizable`, `@cached`) |
| [makerrepo-cli](https://docs.makerrepo.com/makerrepo-cli/) | Local artifact discovery, export, and viewer integration (`mr`) |

## Quick start

1. Open this repo in **VS Code**, **Cursor**, or another VS Code-based IDE with Dev Containers support, then choose **Reopen in Container** (uses `.devcontainer/`).
2. Dependencies sync automatically on container start (`postStartCommand`). Run manually if needed:

   ```bash
   uv sync
   ```

3. Run tests:

   ```bash
   uv run pytest
   ```

4. View the sphere in the OCP CAD Viewer:

   ```bash
   uv run python main.py
   ```

5. Export the sphere (MakerRepo CLI — preferred for published artifacts):

   ```bash
   uv run mr artifacts list
   uv run mr artifacts export sphere -o exports/ --format step
   uv run mr generators export sphere_generator -p '{"radius": 15}' -o exports/ --format step
   ```

   Outputs land in `exports/` (gitignored). For ad-hoc exports in tests or scripts, use `cad.export.export_part(make_sphere(), "sphere")` — see [`tests/test_exports.py`](tests/test_exports.py).

6. *(Cursor)* Reload MCP servers (**Settings → MCP**) — [`.cursor/mcp.json`](.cursor/mcp.json) is committed and ready to use. See [MCP servers](#mcp-servers).

### OCP CAD Viewer extension

The VSIX is **not committed** — it is downloaded to the workspace root as `ocp-cad-viewer-3.4.0.vsix` (gitignored).

**Cursor-specific note:** v3.4.0 ships an ESM-only `proper-lockfile` dependency that crashes on activation in Cursor's extension host (`ERR_REQUIRE_ESM`). The devcontainer scripts patch the VSIX before install. VS Code is unaffected.

Setup:

1. **Download + patch (container lifecycle):** `onCreateCommand` / `postCreateCommand` run `.devcontainer/install-ocp-cad-viewer.sh download`.
2. **Install patched VSIX (after attach):** `postStartCommand` runs `.devcontainer/install-ocp-cad-viewer.sh install-cli` via the editor remote CLI (`code` or `cursor`).

If commands are still missing after reopening the container:

1. Run `bash .devcontainer/install-ocp-cad-viewer.sh install-cli` from a connected terminal.
2. **Developer: Reload Window** in your editor (required after reinstall).
3. Open the OCP CAD Viewer panel (activity bar icon), then run `uv run python main.py`.

## Project layout

```text
.
├── AGENTS.md                     # Agent conventions (parts, assemblies, MakerRepo)
├── LICENSE
├── .cursor/
│   ├── mcp.json                  # MCP server config for Cursor (committed)
│   ├── run-build123d-mcp.sh
│   └── run-ocp-viewer-mcp.sh
├── .makerrepo/
│   └── config.yaml               # MakerRepo repo config (export defaults, pythonpaths)
├── .github/
│   └── workflows/
│       └── ci.yml                # Dagger CI on push/PR
├── ci/
│   ├── dagger.json               # Dagger module config
│   ├── pyproject.toml
│   └── src/ci/main.py            # test, lint, check functions
├── .devcontainer/
│   ├── devcontainer.json
│   ├── Dockerfile
│   └── install-ocp-cad-viewer.sh
├── cad/
│   ├── parts/                    # Reusable parametric parts (@artifact, @customizable)
│   ├── assemblies/               # Composed models
│   └── export.py                 # STEP / STL / GLB helpers
├── main.py                       # Entry point — builds and displays a sphere
├── exports/                      # Generated artifacts (gitignored)
├── tests/
│   ├── test_sphere.py
│   ├── test_exports.py
│   └── test_makerrepo.py
└── pyproject.toml
```

## Development workflow

### Modeling conventions

- **Source of truth:** Python model code — not STL meshes.
- **Parts** live in `cad/parts/`; **assemblies** in `cad/assemblies/`.
- Expose dimensions as function parameters with sensible defaults.
- Return `Part` or `Compound` from builder functions.
- Mark publishable models with MakerRepo decorators (see [MakerRepo](#makerrepo)).
- Test key dimensions, validity, and export behavior for each reusable part.
- Keep generated exports out of version control unless explicitly versioned under `tests/fixtures/`.

### Export formats

| Format | Use |
|--------|-----|
| STEP | CAD interchange (preferred for serious handoff) |
| STL / 3MF | 3D printing and manufacturing meshes |
| GLB / glTF | Lightweight preview and web |
| SVG / DXF | 2D profiles, laser cutting, documentation |

Initial implementation covers STEP, STL, and GLB. Additional formats will be added when a concrete model needs them.

### Testing

```bash
uv run pytest          # geometry and export tests
uv run pytest -v       # verbose output
```

Coverage includes validity, bounding boxes, volume checks, and STEP round-trip export.

### Quality checks (local)

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy cad tests
uv run pytest
```

Or run the same pipeline as CI (requires Docker on the host and a devcontainer rebuild so the socket is mounted):

```bash
dagger call -m ./ci check --source=.
dagger call -m ./ci test --source=.       # pytest only
dagger call -m ./ci lint --source=.       # ruff + mypy only
dagger call -m ./ci artifacts --source=.  # cad.export smoke
dagger call -m ./ci release-artifact --source=. export --path=./dist
```

The Dagger module builds the `.devcontainer/Dockerfile` image, runs `uv sync --group dev`, then executes checks inside that environment — matching GitHub Actions.

## MakerRepo

[MakerRepo](https://docs.makerrepo.com/makerrepo-library/) adds Manufacturing-as-Code metadata to build123d functions. Decorators are **non-intrusive** — they do not change how your builders run; they only annotate functions so [makerrepo-cli](https://docs.makerrepo.com/makerrepo-cli/) (or MakerRepo.com CI) can discover, build, and export them.

| Decorator | Purpose |
|-----------|---------|
| `@artifact` | Fixed CAD model published as a build artifact |
| `@customizable` | Parametric generator with a Pydantic parameter model |
| `@cached` | Cache expensive sub-builds by arguments |

### Example (sphere part)

```python
from build123d import Align, BuildPart, Part, Sphere
from mr import artifact, customizable
from pydantic import BaseModel, Field

def make_sphere(radius: float = 10) -> Part:
    with BuildPart() as part:
        Sphere(radius=radius, align=(Align.CENTER, Align.CENTER, Align.CENTER))
    return part.part

@artifact(cover=True, short_desc="Demo sphere for workspace smoke tests")
def sphere() -> Part:
    return make_sphere()

class SphereParameters(BaseModel):
    radius: float = Field(default=10, gt=0)

@customizable(sample_parameters=SphereParameters())
def sphere_generator(parameters: SphereParameters) -> Part:
    return make_sphere(radius=parameters.radius)
```

See [`cad/parts/sphere.py`](cad/parts/sphere.py) for the live implementation.

### Repository config

[`.makerrepo/config.yaml`](.makerrepo/config.yaml) holds repo-level defaults (e.g. whether artifacts export STEP or 3MF when the decorator omits those flags). Optional `pythonpaths` entries prepend paths to `sys.path` before discovery — useful for `src/` layouts.

### CLI commands

Run from the repo root (included in dev dependencies):

```bash
uv run mr artifacts list                          # discover @artifact functions
uv run mr artifacts export sphere -o exports/     # export STEP/STL/glTF/3MF/…
uv run mr artifacts view sphere                   # send to OCP CAD Viewer
uv run mr generators list                         # discover @customizable functions
uv run mr generators export sphere_generator -o exports/ -p '{"radius": 15}'
```

For full command reference, see the [MakerRepo CLI docs](https://docs.makerrepo.com/makerrepo-cli/).

### MakerRepo.com (optional)

To publish artifacts on [MakerRepo.com](https://makerrepo.com), create a repository there, push this code, and the platform CI will build `@artifact` and `@customizable` functions automatically. Local workflow with `mr` remains fully usable without an account.

## MCP servers

Two MCP servers are configured for agent-assisted CAD. [`.cursor/mcp.json`](.cursor/mcp.json) is committed for **Cursor**; launcher scripts resolve paths relative to the workspace so they work inside the devcontainer. Other editors may need equivalent MCP configuration.

In Cursor, reload MCP servers (**Settings → MCP**) after container rebuilds.

### Configured servers

| Server | Package | Pin | Role |
|--------|---------|-----|------|
| [build123d-mcp](https://github.com/pzfreo/build123d-mcp) | `build123d-mcp` | `0.3.36` | Run build123d code in a sandboxed session; measure, render, export, compare geometry |
| [ocp-viewer-mcp](https://github.com/dmilad/ocp-viewer-mcp) | `ocp-viewer-mcp` | `0.1.0` | Capture screenshots from OCP CAD Viewer so agents can see displayed models |

**build123d-mcp** runs in an isolated `uv tool` environment (Python 3.12 required for VTK/OCP wheels). Key tools: `execute`, `measure`, `render_view`, `export`, `session_state`.

**ocp-viewer-mcp** runs in this project's `.venv` (installed via `uv sync` dev dependencies). Requires the OCP CAD Viewer extension and a model displayed via `show_object()`.

### Workspace MCP config

```json
{
  "mcpServers": {
    "build123d-mcp": {
      "command": "bash",
      "args": [".cursor/run-build123d-mcp.sh"]
    },
    "ocp-viewer": {
      "command": "bash",
      "args": [".cursor/run-ocp-viewer-mcp.sh"]
    }
  }
}
```

Launcher scripts pin `build123d-mcp==0.3.36` (Python 3.12 via `uv tool run`) and run `ocp-viewer-mcp` from the project `.venv`. To bump versions, edit the launcher scripts and reload MCP.

### Typical agent workflow

1. Use **build123d-mcp** `execute` to prototype geometry incrementally; verify with `measure` and `render_view`.
2. Move stable parts into `cad/parts/` as normal Python modules with pytest coverage.
3. Run `uv run python main.py` and display in OCP CAD Viewer.
4. Use **ocp-viewer-mcp** `capture_ocp_screenshot` to let the agent visually confirm the viewer output.

### Troubleshooting

| Issue | Fix |
|-------|-----|
| build123d-mcp won't start | Ensure `uv` is on PATH; first launch downloads Python 3.12 + deps (network required) |
| ocp-viewer connection failed | Run `bash .devcontainer/install-ocp-cad-viewer.sh install-cli`, then **Developer: Reload Window**. Open OCP CAD Viewer panel before running `show_object()` scripts |
| MCP tools missing after container rebuild | Run `uv sync`; in Cursor, reload MCP (**Settings → MCP**) |

### Other MCP candidates (not configured and not an endorsement)

| Repository | Description |
|------------|-------------|
| [brs077/3dp-mcp-server](https://github.com/brs077/3dp-mcp-server) | 3D-printable CAD with build123d (Bambu Lab X1C focus) |
| [jdilla1277/agentcad](https://github.com/jdilla1277/agentcad) | CAD CLI and MCP server for AI agents |
| [rishigundakaram/cadquery-mcp-server](https://github.com/rishigundakaram/cadquery-mcp-server) | CadQuery MCP server |
| [blwfish/freecad-mcp](https://github.com/blwfish/freecad-mcp) | FreeCAD MCP integration |

## Roadmap

### First milestone (complete)

The turnkey workspace is in place. Shipped items:

- [x] `pyproject.toml`, `.gitignore`, and package scaffold
- [x] `main.py` sphere entry point (thin viewer script; geometry in `cad/parts/`)
- [x] `cad/parts/sphere.py` with `make_sphere`, `@artifact`, and `@customizable`
- [x] `cad/export.py` for ad-hoc STEP / STL / GLB bundles in tests and scripts
- [x] `.makerrepo/config.yaml` and MakerRepo dependencies (`makerrepo`, `makerrepo-cli`)
- [x] pytest suite — geometry, exports, and MakerRepo discovery (`tests/test_makerrepo.py`)
- [x] `.cursor/mcp.json` with build123d-mcp and ocp-viewer-mcp launcher scripts
- [x] Ephemeral OCP CAD Viewer VSIX via devcontainer lifecycle scripts
- [x] End-to-end verification in devcontainer
- [x] Dagger CI module (`ci/`) with lint, artifacts, and test gates
- [x] GitHub Actions release workflow (`.github/workflows/release.yml`) — sphere STL to Releases + GHCR
- [x] [AGENTS.md](AGENTS.md) — repo conventions for AI agents

Work planned after this milestone. Order may shift based on project needs.

### CI and automation

Pushes and pull requests to `main` run the Dagger pipeline when changes touch model code, tests, CI, dependencies, or agent docs — see path filters in [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

| Function | What it runs |
|----------|--------------|
| `check` | lint + artifacts + test (used in GitHub Actions) |
| `test` | `uv run pytest` |
| `lint` | `uv run ruff check .`, `ruff format --check .`, `mypy cad tests` |
| `artifacts` | `python -m cad.export smoke` (discover and export all artifacts as STEP + STL) |
| `release-artifact` | `python -m cad.export release` (export all artifacts as STL for release) |

The pipeline builds from [`.devcontainer/Dockerfile`](.devcontainer/Dockerfile) for Open CASCADE / Mesa parity with local dev. OCP viewer VSIX and MCP servers are not part of CI.

### Releases

Pushing a semver tag (e.g. `v0.0.1`) runs [`.github/workflows/release.yml`](.github/workflows/release.yml):

1. **Quality gate** — same Dagger `check` as CI (lint, artifact smoke, pytest).
2. **Export** — all `@artifact` models as STL via `cad.export`.
3. **GitHub Release** — attaches `dist/*.stl`.
4. **GHCR package** — publishes the same STL to `ghcr.io/<owner>/cad-sphere:<tag>` via [ORAS](https://oras.land/).

**Cut a release** (from `main`, after CI is green):

```bash
git tag v0.0.1
git push origin v0.0.1
```

**Download the STL:**

- **Releases page** — open the tag on GitHub and download `sphere.stl`.
- **GHCR (programmatic)** — after installing [ORAS](https://oras.land/docs/installation):

  ```bash
  oras pull ghcr.io/<owner>/cad-sphere:v0.0.1
  ```

Keep `pyproject.toml` `version` in sync with release tags. Local dry-run:

```bash
dagger call -m ./ci release-artifact --source=. export --path=./dist
```

**Local Dagger** (inside the devcontainer after rebuild):

1. Host Docker must be running and `/var/run/docker.sock` mounted (configured in `devcontainer.json`).
2. Run from the repo root: `dagger call -m ./ci check --source=.`

**Future CI additions:**

- **Pre-commit** (optional) — ruff format/check on commit; pytest left to CI to keep commits fast.
- **Coverage** — `pytest-cov` threshold on `cad/` once the library grows.
- ~~**Export-smoke** — export one-liner in CI `tmp_path`; assert non-empty STEP/STL/GLB.~~ (covered by `artifacts` + `test_makerrepo.py`)
- **Export regression** (later) — golden STEP/STL fixtures under `tests/fixtures/` with `.gitignore` exceptions for intentional baselines.

### Future modeling and library work

- Additional parts and real assemblies (constraints, patterns, hardware library)
- 3MF, SVG, and DXF export helpers where models need them
- Import helpers (STEP → build123d) with human/agent review workflow
- Golden fixture tests for export stability
- Printer-specific export profiles (e.g. Bambu) if `3dp-mcp-server` or similar is adopted

## Known limitations

- build123d is code-first — not a full GUI CAD application.
- OCP CAD Viewer visualizes Python-defined geometry; the model source remains code.
- Selector-based operations (faces, edges) can break if topology changes unexpectedly.
- STEP is the reliable interchange format; STL is lossy.
- Rebuilding clean parametric code from imported STL usually requires human or agent interpretation.
- MCP servers in this space are experimental until vetted and pinned.
- VSIX extension install may require a manual step if the editor remote CLI (`code` / `cursor`) is unavailable in the container.

## License

See [LICENSE](LICENSE).
