---
sidebar_position: 1
---

# Quick start

Get the turnkey template running in a Dev Container in a few minutes.

:::tip Created your own repo from the template?
Edit [`template.repo.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/template.repo.toml) for your GitHub org and repo name, run `just template-apply`, then finish [Set up GitHub](/getting-started/github-setup). See [Replace template identity](/getting-started/github-setup#replace-template-identity-in-your-repo).
:::

## Prerequisites

- **IDE or cloud workspace** with [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers) support — e.g. [VS Code](https://code.visualstudio.com/), [Cursor](https://cursor.com/), [GitHub Codespaces](https://github.com/features/codespaces), [DevPod](https://devpod.sh/), or another [spec-compatible client](/getting-started/ide-and-workspaces)
- **Docker** on the host when developing locally (for the dev container and for `just ci` via Dagger). Cloud workspaces may provide Docker on the remote VM instead.

See [IDEs and workspaces](/getting-started/ide-and-workspaces) for a full compatibility table (Copilot, Codespaces, VSCodium, Ona, and more).

## Steps

### 1. Open in a dev container

Open [CAD-as-Code-Template](https://github.com/Coffee2Bits/CAD-as-Code-Template) in your IDE or create a **Codespace**, then choose **Reopen in Container** (desktop) or let the service build from `.devcontainer/` (cloud). The first build may take several minutes.

### 2. Sync dependencies

Dependencies sync automatically on container start. Run manually if needed:

```bash
just sync
```

### 3. Run tests

```bash
just test
```

Or: `uv run pytest`

### 4. View the demo sphere

```bash
just view
```

Or: `uv run python main.py`

Open the **OCP CAD Viewer** panel in the activity bar before running. See [OCP CAD Viewer](/getting-started/ocp-viewer) if the extension is missing.

### 5. Export via MakerRepo

```bash
just mr-artifacts
just mr-export sphere /tmp/out step
just mr-export-generator sphere_generator /tmp/out '{"radius": 15}'
```

For ad-hoc exports in tests, use `cad_tooling.export.export_part()` — see [CAD tooling export](/tools/cad-tooling/export).

### 6. MCP servers (included in the container)

**build123d-mcp** and **ocp-viewer-mcp** run inside the dev container — installed by `uv sync` and wired through [`.cursor/mcp.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.cursor/mcp.json). No host-side setup.

- **Cursor** — servers connect automatically when you reopen in container; after a **rebuild**, reload MCP in **Settings → MCP**.
- **VS Code / Codespaces + Copilot** — copy the server entries from `.cursor/mcp.json` into your [MCP settings](https://code.visualstudio.com/docs/copilot/chat/mcp-servers) (launchers still execute in the container).

See [MCP servers](/tools/mcp-servers).

## Set up GitHub (template / new repo)

If you created this repo from **[Use this template](https://github.com/Coffee2Bits/CAD-as-Code-Template/generate)** (or forked it as your own project), configure settings that live **only on GitHub.com**:

1. [Set up GitHub for your repository](/getting-started/github-setup) — Actions permissions, Pages, branch protection, squash merge; edit `template.repo.toml` + `just template-apply` for your org/repo name
2. [Releases](/getting-started/releases) — first automated GitHub Release (STL + PNG) via release-please

Forking to contribute upstream? You usually only need local [Quick start](#steps) steps — skip release automation on your fork.

## Next steps

- [IDEs and workspaces](/getting-started/ide-and-workspaces) — portability across VS Code, Cursor, Codespaces, Copilot, and more
- [Set up GitHub](/getting-started/github-setup) — one-time repository settings for clones and template repos
- [Releases](/getting-started/releases) — versioning and published assets
- [Dev container](/getting-started/dev-container) — lifecycle and Docker socket for CI
- [Project layout](/getting-started/project-layout) — where code lives
- [Daily development](/workflows/daily-development) — edit loop
