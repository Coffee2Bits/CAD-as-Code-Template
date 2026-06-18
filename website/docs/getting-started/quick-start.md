---
sidebar_position: 1
---

# Quick start

This page gets the template from GitHub to a running model. It assumes you are new to at least some of the tooling, so it keeps the first path narrow.

CAD-as-Code means the model is source code. You edit Python in `cad/`, then use tests, viewer feedback, exports, and CI to prove the model still works.

:::tip Created your own repo from the template?
Edit [`template.repo.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/template.repo.toml), then run `just init`. Or run `just init --owner acme --repo widget-cad`. See [Replace template identity](/getting-started/github-setup#replace-template-identity-in-your-repo).
:::

## Choose a workspace

### Option A: Codespaces

Use this when you want the least local setup.

1. Open [CAD-as-Code-Template](https://github.com/Coffee2Bits/CAD-as-Code-Template) or your generated repo on GitHub.
2. Click Code, then Codespaces, then Create codespace.
3. Wait for the Dev Container build to finish.

Success state: you have a browser-based VS Code window with a terminal inside the container.

### Option B: Local VS Code or Cursor

Use this when you want files on your machine.

Prerequisites:

- [Docker](https://www.docker.com/) running on the host.
- [VS Code](https://code.visualstudio.com/), [Cursor](https://cursor.com/), or another [Dev Containers-compatible IDE](/getting-started/ide-and-workspaces).

Steps:

1. Clone or open the repo.
2. Choose Reopen in Container when prompted.
3. Wait for the Dev Container build to finish.

Success state: your editor is attached to the container, not just the host folder.

## First commands

The container syncs dependencies and starts the docs site automatically. If that did not happen, run:

```bash
just sync
just docs-serve-bg
```

Success state: dependencies are installed and the local docs site is available at [http://localhost:3000](http://localhost:3000).

### 1. Run the tests

```bash
just test
```

Success state: pytest runs and reports passing tests. This proves the demo model and export checks are working.

If you prefer the direct command:

```bash
uv run pytest
```

### 2. View the demo model

Open the OCP CAD Viewer panel in the activity bar, then run:

```bash
just view
```

Success state: the demo sphere appears in the viewer.

If the panel or extension is missing, use the [OCP CAD Viewer guide](/getting-started/ocp-viewer).

### 3. List and export artifacts

```bash
just mr-artifacts
just mr-export sphere /tmp/out step
just mr-export-generator sphere_generator /tmp/out '{"radius": 15}'
```

Success state: MakerRepo lists exportable artifacts and writes generated files under `/tmp/out`.

For programmatic exports in tests or scripts, use `cad_tooling.export.export_part()`. See [CAD tooling export](/tools/cad-tooling/export).

## MCP servers

The container includes [build123d-mcp](/tools/mcp-servers) and [ocp-viewer-mcp](/tools/mcp-servers). They let AI agents run geometry code and inspect viewer feedback while the Python files remain the source of truth.

- Cursor: servers connect from [`.cursor/mcp.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.cursor/mcp.json). After a rebuild, reload MCP in Settings → MCP.
- VS Code / Codespaces + Copilot: copy the server entries from `.cursor/mcp.json` into your [MCP settings](https://code.visualstudio.com/docs/copilot/chat/mcp-servers).

If an MCP server fails to connect, see [MCP troubleshooting](/troubleshooting/mcp).

## Set up GitHub for your own repo

If you clicked [Use this template](https://github.com/Coffee2Bits/CAD-as-Code-Template/generate), a few settings live on GitHub.com and cannot be configured by the Dev Container alone:

1. [Set up GitHub](/getting-started/github-setup) — Actions permissions, Pages, branch protection, squash merge, and template identity.
2. [Releases](/getting-started/releases) — first automated GitHub Release with exported assets.

If you are only contributing back to this template repo, you can usually skip release automation on your fork.

## Next steps

- [Project layout](/getting-started/project-layout) — where models, tests, docs, and tooling live.
- [Daily development](/workflows/daily-development) — the normal edit/test/view loop.
- [Modeling conventions](/modeling/conventions) — how to keep `cad/` clean and reusable.
- [Export and formats](/workflows/export-and-formats) — choose STEP, STL, GLB, or release bundles.
- [Troubleshooting](/troubleshooting/) — container, viewer, MCP, export, and CI fixes.
