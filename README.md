# CAD-as-Code, in a box

📖 **[Full documentation](https://coffee2bits.github.io/CAD-as-Code-Template/)** — tools, workflows, troubleshooting, and reference.

A turnkey workspace for **parametric CAD in Python**. Reopen this repo in any **Dev Containers–capable editor or cloud workspace** — VS Code, Cursor, GitHub Codespaces, GitHub Copilot in VS Code, and [other compatible clients](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/ide-and-workspaces) — and you get a complete modeling environment: IDE, live 3D viewer, automated tests, export tooling, and CI, already wired together.

Define geometry with [build123d](https://build123d.readthedocs.io/), preview it in the [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer), validate with pytest, and export to STEP, STL, and GLB. Publish artifacts through [MakerRepo](https://docs.makerrepo.com/makerrepo-library/) (`mr`). Python is the source of truth; mesh files are generated, not hand-edited.

![Dev environment: VS Code-based IDE with build123d code, OCP CAD Viewer, and AI agent showing a parametric sphere with embossed text](repo_preview.png)

## **What's in the box:**

| Layer | What you get |
|-------|--------------|
| **IDE** | Dev container (`.devcontainer/`) — portable across VS Code, Cursor, Codespaces, Copilot, and [more](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/ide-and-workspaces); dependencies sync on start |
| **Modeling** | build123d parts and assemblies under `cad/` |
| **Visualization** | OCP CAD Viewer + `ocp-vscode` bridge for `show_object` |
| **Quality** | pytest geometry tests, ruff, mypy |
| **Make** | [just](https://github.com/casey/just) command runner (`justfile`) for dev, export, and CI |
| **CI** | [Dagger](https://dagger.io/) — portable CI from local to GitHub Actions to any other pipeline tool; same checks everywhere |
| **Agents** | AI coding assistants — Cursor, VS Code, Claude, GitHub Copilot |
| **MCP** | Agent tools in the dev container (build123d-mcp, ocp-viewer-mcp) — `uv sync` + `.cursor/mcp.json` launchers; see [MCP servers](https://coffee2bits.github.io/CAD-as-Code-Template/tools/mcp-servers) |
| **Publish** | MakerRepo decorators and `mr` CLI for artifact discovery and export |

**AI agents:** see [AGENTS.md](AGENTS.md) for repo structure, parts/assemblies conventions, and MakerRepo usage.

## Stack

| Tool | Role |
|------|------|
| [build123d](https://github.com/gumyr/build123d) | Parametric CAD-as-code on [Open CASCADE](https://coffee2bits.github.io/CAD-as-Code-Template/reference/open-cascade) |
| [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer) | Live 3D visualization in VS Code-based IDEs |
| [ocp-vscode](https://github.com/bernhard-42/ocp_vscode) | Python bridge for `show_object` |
| [uv](https://docs.astral.sh/uv/) | Dependency and virtualenv management |
| [just](https://github.com/casey/just) | Command runner for common dev, export, and CI tasks (`justfile`) |
| [pytest](https://docs.pytest.org/) | Geometry and export tests |
| [ruff](https://docs.astral.sh/ruff/) / [mypy](https://mypy-lang.org/) | Linting and type checking |
| [Dagger](https://dagger.io/) | Portable CI pipeline (local + GitHub Actions) |
| [build123d-mcp](https://github.com/pzfreo/build123d-mcp) | MCP interface — sandboxed geometry execution for AI agents |
| [ocp-viewer-mcp](https://github.com/dmilad/ocp-viewer-mcp) | MCP interface — viewer screenshots for agent visual feedback |
| [MakerRepo](https://docs.makerrepo.com/makerrepo-library/) | Manufacturing-as-code decorators (`@artifact`, `@customizable`, `@cached`) |
| [makerrepo-cli](https://docs.makerrepo.com/makerrepo-cli/) | Local artifact discovery, export, and viewer integration (`mr`) |

## Quick start

1. Open this repo in **VS Code**, **Cursor**, **GitHub Codespaces**, or another [Dev Containers–compatible IDE or workspace](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/ide-and-workspaces), then choose **Reopen in Container** (uses `.devcontainer/`).
2. Dependencies sync and the documentation site start automatically on container start (`postStartCommand` runs `post-start.sh` — docs at http://localhost:3000). Run manually if needed:

   ```bash
   just sync
   just docs-serve-bg                 # background (idempotent)
   bash .devcontainer/start-docs.sh   # same script
   ```

3. Run tests:

   ```bash
   just test
   ```

   Or directly: `uv run pytest`

4. View the sphere in the OCP CAD Viewer:

   ```bash
   just view
   ```

   Or directly: `uv run python main.py`

5. Export the sphere (MakerRepo CLI — preferred for published artifacts):

   ```bash
   just mr-artifacts
   just mr-export sphere /tmp/out step
   just mr-export-generator sphere_generator /tmp/out '{"radius": 15}'
   ```

   For ad-hoc exports in tests or scripts, use `cad_tooling.export.export_part(make_sphere(), "sphere", tmp_path)` — see [`tests/test_exports.py`](tests/test_exports.py).

6. **MCP servers** run in the dev container (no host install). **Cursor:** reload MCP in **Settings → MCP** after a container rebuild. **VS Code / Copilot:** import entries from [`.cursor/mcp.json`](.cursor/mcp.json). See [MCP servers](https://coffee2bits.github.io/CAD-as-Code-Template/tools/mcp-servers).

### Set up GitHub and releases (template / new repo)

If you used **[Use this template](https://github.com/Coffee2Bits/CAD-as-Code-Template/generate)**, configure one-time settings on GitHub.com, then run your first automated release:

1. [Set up GitHub for your repository](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/github-setup) — Actions permissions, Pages, branch protection, squash merge; edit `template.repo.toml` then `just template-apply`
2. [Releases](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/releases) — release-please flow and published STL/PNG assets

In-repo summary: [`.github/GITHUB_SETUP.md`](.github/GITHUB_SETUP.md).

### OCP CAD Viewer extension

The VSIX is downloaded and patched automatically in the dev container (not committed). Setup, Cursor ESM patch notes, and recovery steps: [OCP CAD Viewer](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/ocp-viewer).

## Project layout

```text
.
├── template.repo.toml            # Org/repo identity — edit after "Use this template", then just template-apply
├── AGENTS.md                     # Agent conventions (parts, assemblies, MakerRepo)
├── LICENSE
├── .cursor/
│   ├── mcp.json                  # MCP server config for Cursor (committed)
│   ├── run-build123d-mcp.sh
│   └── run-ocp-viewer-mcp.sh
├── .makerrepo/
│   └── config.yaml               # MakerRepo repo config (export defaults, pythonpaths)
├── .github/
│   ├── GITHUB_SETUP.md           # One-time GitHub.com settings checklist
│   └── workflows/
│       ├── ci.yml                # Dagger CI on push/PR
│       ├── docs.yml              # Deploy Docusaurus to Pages
│       ├── release-please.yml    # Release PRs + publish
│       └── release.yml           # Manual tag fallback
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
│   └── assemblies/               # Composed models
├── cad_tooling/                  # Export, render, release helpers (see cad_tooling/README.md)
├── justfile                      # Common dev, export, and CI commands (`just --list`)
├── main.py                       # Entry point — builds and displays a sphere
├── tests/                        # CAD model and integration tests
├── cad_tooling_tests/            # Unit tests for cad_tooling
└── pyproject.toml
```

## Development workflow

Common local gates: `just quality` (lint + test) before pushing; `just ci` for the full Dagger pipeline (Docker required).

| Topic | Documentation |
|-------|---------------|
| **just** recipes | [just commands](https://coffee2bits.github.io/CAD-as-Code-Template/tools/just) · [recipe reference](https://coffee2bits.github.io/CAD-as-Code-Template/reference/justfile-recipes) |
| Modeling | [Conventions](https://coffee2bits.github.io/CAD-as-Code-Template/modeling/conventions) · [Parts & assemblies](https://coffee2bits.github.io/CAD-as-Code-Template/modeling/parts-and-assemblies) |
| Testing & quality | [Testing](https://coffee2bits.github.io/CAD-as-Code-Template/modeling/testing) · [uv & quality](https://coffee2bits.github.io/CAD-as-Code-Template/tools/uv-and-quality) |
| Export | [Export & formats](https://coffee2bits.github.io/CAD-as-Code-Template/workflows/export-and-formats) · [CAD tooling](https://coffee2bits.github.io/CAD-as-Code-Template/tools/cad-tooling/) |
| CI & releases | [CI & Dagger](https://coffee2bits.github.io/CAD-as-Code-Template/workflows/ci-and-dagger) · [Releases](https://coffee2bits.github.io/CAD-as-Code-Template/workflows/releases) |
| Daily loop | [Daily development](https://coffee2bits.github.io/CAD-as-Code-Template/workflows/daily-development) |

## MakerRepo

[MakerRepo](https://docs.makerrepo.com/makerrepo-library/) decorates build123d entry points for discovery and export (`@artifact`, `@customizable`, `@cached`). Import from `mr`. Full guide, sphere example, and CLI cookbook: [MakerRepo](https://coffee2bits.github.io/CAD-as-Code-Template/tools/makerrepo).

**AI agents:** [AGENTS.md](AGENTS.md) for repo conventions; [for agents](https://coffee2bits.github.io/CAD-as-Code-Template/contributing/for-agents) on the docs site.

## MCP servers

MCP servers run **inside the dev container** (`uv sync` installs `ocp-viewer-mcp`; `build123d-mcp` via pinned launchers in `.cursor/`). Your IDE connects through [`.cursor/mcp.json`](.cursor/mcp.json) — they help agents interact with geometry and the viewer alongside direct editing. They do not replace the **CAD/** tree (`cad/`) as source of truth. Full architecture and troubleshooting: [MCP servers](https://coffee2bits.github.io/CAD-as-Code-Template/tools/mcp-servers).

## Future work Roadmap

Order may shift based on project needs.

- Additional parts and real assemblies (constraints, patterns)
- Import [build123d part libraries](https://coffee2bits.github.io/CAD-as-Code-Template/modeling/external-libraries)
- [PartCAD](https://partcad.org/) integration — import and publish packaged CAD models
- Bill of materials (BOM) generation from assemblies
- 3MF, SVG, and DXF export helpers where models need them
- Import helpers (STEP → build123d) with human/agent review workflow
- Export regression tests with golden STEP/STL fixtures under `tests/fixtures/`
- Printer-specific export profiles (e.g. Bambu) if `3dp-mcp-server` or similar is adopted
- Pre-commit hooks (optional ruff format/check on commit; pytest left to CI)
- `pytest-cov` coverage threshold on `cad/` once the library grows
- CI demonstration of topology optimization (e.g. [dl4to4ocp](https://github.com/yeicor-3d/dl4to4ocp/))

### CI, releases, and GitHub

- [Set up GitHub](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/github-setup) — template clone settings (Actions, Pages, branch protection)
- [Releases (getting started)](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/releases) — first release and versioning
- [CI & Dagger](https://coffee2bits.github.io/CAD-as-Code-Template/workflows/ci-and-dagger) — path filters, `just ci`, Dagger functions
- [Releases (reference)](https://coffee2bits.github.io/CAD-as-Code-Template/workflows/releases) — Conventional Commits detail, dry-run, manual tags

## Known limitations

See [Troubleshooting](https://coffee2bits.github.io/CAD-as-Code-Template/troubleshooting/) for known limitations and fixes.

## Additional resources

- [Documentation site](https://coffee2bits.github.io/CAD-as-Code-Template/) — full guides
- [Open CASCADE](https://coffee2bits.github.io/CAD-as-Code-Template/reference/open-cascade) — kernel under build123d
- [External part libraries](https://coffee2bits.github.io/CAD-as-Code-Template/modeling/external-libraries) — bd_warehouse, bd-vslot, and more
- [CAD tooling](https://coffee2bits.github.io/CAD-as-Code-Template/tools/cad-tooling/) — export, render, release notes

## License

See [LICENSE](LICENSE).
