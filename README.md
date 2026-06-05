# Programmatic CAD Modeling Workspace

Python-based parametric CAD modeling using [build123d](https://build123d.readthedocs.io/), with live visualization in Cursor, automated geometry tests, and export to standard CAD formats.

**Status:** Devcontainer scaffolding is in place. Core library, tests, exports, and documentation are being built out toward the [first milestone](#first-milestone). See [Roadmap](#roadmap) for planned CI and MCP integration.

Detailed agent/setup specification: [`build123d-cursor-project-brief.md`](build123d-cursor-project-brief.md).

## Stack

| Tool | Role |
|------|------|
| [build123d](https://github.com/gumyr/build123d) | Parametric CAD-as-code (Open CASCADE) |
| [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer) | Live 3D visualization in Cursor/VS Code |
| [ocp-vscode](https://github.com/bernhard-42/ocp_vscode) | Python bridge for `show_object` |
| [uv](https://docs.astral.sh/uv/) | Dependency and virtualenv management |
| [pytest](https://docs.pytest.org/) | Geometry and export tests |
| [ruff](https://docs.astral.sh/ruff/) / [mypy](https://mypy-lang.org/) | Linting and type checking |

## Quick start

1. Open this repo in **Cursor** and choose **Reopen in Container** (uses `.devcontainer/`).
2. After the container builds, sync dependencies:

   ```bash
   uv sync
   ```

3. Run tests:

   ```bash
   uv run pytest
   ```

4. View the example part in the OCP CAD Viewer:

   ```bash
   uv run python examples/view_example_plate.py
   ```

5. Export STEP, STL, and GLB:

   ```bash
   uv run python -c "from cad.export import export_part; from cad.parts.example_plate import make_example_plate; export_part(make_example_plate(), 'example_plate')"
   ```

   Outputs land in `exports/` (gitignored).

### OCP CAD Viewer extension

The devcontainer downloads the VSIX during `postCreateCommand`. If the extension is not active:

1. Open **Extensions** in Cursor.
2. Choose **Install from VSIX**.
3. Select `.devcontainer/vsix/ocp-cad-viewer-3.4.0.vsix`.

## Project layout

```text
.
├── .cursor/
│   └── mcp.json.example          # MCP opt-in template (not installed by default)
├── .devcontainer/
│   ├── devcontainer.json
│   ├── Dockerfile
│   └── install-ocp-cad-viewer.sh
├── cad/
│   ├── parts/                    # Reusable parametric parts
│   │   └── example_plate.py
│   ├── assemblies/               # Composed models (minimal demo first)
│   │   └── example_assembly.py
│   └── export.py                 # STEP / STL / GLB helpers
├── examples/
│   └── view_example_plate.py
├── exports/                      # Generated artifacts (gitignored)
├── tests/
│   ├── test_example_plate.py
│   └── test_exports.py
├── pyproject.toml
└── build123d-cursor-project-brief.md
```

## Development workflow

### Modeling conventions

- **Source of truth:** Python model code — not STL meshes.
- **Parts** live in `cad/parts/`; **assemblies** in `cad/assemblies/`.
- Expose dimensions as function parameters with sensible defaults.
- Return `Part` or `Compound` from builder functions.
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

### Assemblies

`cad/assemblies/example_assembly.py` is intentionally **minimal** — enough to prove that parts compose correctly (e.g. two plates positioned relative to each other). More complex assemblies, constraints, and BOM-style structure will be added as real models require them.

### Quality checks (local)

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy cad tests
uv run pytest
```

## MCP servers (candidates — vet before enabling)

MCP integration is **optional** and **not installed by default**. Copy `.cursor/mcp.json.example` to `.cursor/mcp.json` only after vetting a server. Real `mcp.json` is gitignored.

Review each repo for maintenance, install method, PyPI availability, and security before enabling.

### build123d / OCP (primary candidates)

| Repository | Description | Notes for vetting |
|------------|-------------|-------------------|
| [pzfreo/build123d-mcp](https://github.com/pzfreo/build123d-mcp) | MCP server for build123d model generation | Check PyPI/`uvx` support, tool surface, and pin commit |
| [dmilad/ocp-viewer-mcp](https://github.com/dmilad/ocp-viewer-mcp) | Screenshots from OCP CAD Viewer for agent vision | Requires OCP viewer running; verify Cursor compatibility |
| [brs077/3dp-mcp-server](https://github.com/brs077/3dp-mcp-server) | 3D-printable CAD with build123d (Bambu Lab X1C focus) | Evaluate if printer-specific tooling is in scope |
| [jdilla1277/agentcad](https://github.com/jdilla1277/agentcad) | CAD CLI and MCP server for AI agents | Broader agent CAD toolkit — check overlap with build123d-mcp |

### CadQuery alternatives

Useful if cross-framework agent tooling is needed; this repo standardizes on build123d.

| Repository | Description |
|------------|-------------|
| [rishigundakaram/cadquery-mcp-server](https://github.com/rishigundakaram/cadquery-mcp-server) | CadQuery MCP server |
| [mikekuniavsky/mcp-cadquery-server-public](https://github.com/mikekuniavsky/mcp-cadquery-server-public) | Public CadQuery MCP server |

### FreeCAD alternatives

For GUI-driven or FreeCAD-native workflows, not the default for this codebase.

| Repository | Description |
|------------|-------------|
| [blwfish/freecad-mcp](https://github.com/blwfish/freecad-mcp) | FreeCAD MCP integration |
| [lucygoodchild/freecad-mcp-server](https://github.com/lucygoodchild/freecad-mcp-server) | FreeCAD MCP server |

### Enabling MCP (after vetting)

1. Inspect the chosen repo: install docs, dependencies, last commit, open issues.
2. Pin a version or commit hash in install instructions.
3. Copy and edit the example config:

   ```bash
   cp .cursor/mcp.json.example .cursor/mcp.json
   ```

4. Restart Cursor or reload MCP servers.
5. Document the chosen server and pin in this README (future step once vetted).

Placeholder shape (adjust per server after inspection):

```json
{
  "mcpServers": {
    "build123d": {
      "command": "uvx",
      "args": ["build123d-mcp"]
    },
    "ocp-viewer": {
      "command": "uvx",
      "args": ["ocp-viewer-mcp"]
    }
  }
}
```

If a server is not on PyPI, use `uv run` against a cloned repo — see `.cursor/mcp.json.example` and the brief for local-development patterns.

## Roadmap

Work planned after the first milestone. Order may shift based on project needs.

### Near term (first milestone)

- [ ] `pyproject.toml`, `.gitignore`, and package scaffold
- [ ] `cad/parts/example_plate.py`
- [ ] Minimal `cad/assemblies/example_assembly.py`
- [ ] `cad/export.py` and viewer example
- [ ] pytest suite for geometry and exports
- [ ] `.cursor/mcp.json.example`
- [ ] End-to-end verification in devcontainer

### CI and automation (planned)

Goal: every push/PR runs the same checks as local dev, inside an environment that matches the devcontainer.

**Proposed GitHub Actions workflow:**

| Job | Steps |
|-----|-------|
| **test** | Checkout → build or reuse devcontainer image → `uv sync` → `uv run pytest` |
| **lint** | `uv run ruff check .` → `uv run ruff format --check .` → `uv run mypy cad tests` |
| **export-smoke** (optional) | Run export one-liner in CI `tmp_path`; assert non-empty STEP/STL/GLB (no committed artifacts) |

**Tooling options under consideration:**

- **Devcontainer CI** — `devcontainers/ci` or equivalent so CI uses the same Dockerfile as local dev (best parity for Open CASCADE / GL libs).
- **uv in CI** — `astral-sh/setup-uv` with cached `.venv` for speed once base image is stable.
- **Pre-commit** (optional) — ruff format/check on commit; pytest left to CI to keep commits fast.
- **Coverage** — `pytest-cov` threshold on `cad/` once the library grows.
- **Export regression** (later) — golden STEP/STL fixtures under `tests/fixtures/` with `.gitignore` exceptions for intentional baselines.

**Not in initial CI scope:** MCP server installs, OCP viewer UI, or headless 3D rendering screenshots (unless `ocp-viewer-mcp` is vetted and scripted).

### Future modeling and library work

- Additional parts and real assemblies (constraints, patterns, hardware library)
- 3MF, SVG, and DXF export helpers where models need them
- Import helpers (STEP → build123d) with human/agent review workflow
- Golden fixture tests for export stability
- Printer-specific export profiles (e.g. Bambu) if `3dp-mcp-server` or similar is adopted

## First milestone

The repo is “working” when all of the following hold inside the devcontainer:

- `uv sync` succeeds
- OCP CAD Viewer VSIX is present under `.devcontainer/vsix/`
- `uv run python examples/view_example_plate.py` runs (viewer panel may need manual VSIX install)
- `uv run pytest` passes
- Export one-liner produces non-empty files in `exports/`
- `.cursor/mcp.json.example` exists; no unvetted MCP server is installed silently

## Known limitations

- build123d is code-first — not a full GUI CAD application.
- OCP CAD Viewer visualizes Python-defined geometry; the model source remains code.
- Selector-based operations (faces, edges) can break if topology changes unexpectedly.
- STEP is the reliable interchange format; STL is lossy.
- Rebuilding clean parametric code from imported STL usually requires human or agent interpretation.
- MCP servers in this space are experimental until vetted and pinned.
- VSIX extension install may require a manual step in Cursor if the CLI is unavailable in the container.

## License

Add a license file when the project scope is finalized.
