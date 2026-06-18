---
sidebar_position: 1
---

# Quick start

This page gets the template from GitHub to a running model. It assumes you are new to at least some of the tooling, so it keeps the first path narrow. If a technical term is new, check the [glossary](/reference/glossary).

[CAD-as-Code](/reference/glossary#cad-as-code) means the model is source code. You edit Python in `cad/`, then use tests, viewer feedback, exports, and the CI/CD pipeline to prove the model still works.

:::tip Created your own repo from the template?
Edit [`template.repo.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/template.repo.toml), then run `just init`. Or run `just init --owner acme --repo widget-cad`. See [Create and initialize your repository](/getting-started/template-and-init).
:::

## Choose a workspace

### Option A: Online Codespaces

Use this when you want the least local setup.

1. Open [CAD-as-Code-Template](https://github.com/Coffee2Bits/CAD-as-Code-Template) or your generated repo on GitHub.
2. Click Code, then Codespaces, then Create codespace.
3. Wait for the Dev Container build to finish.

You should have a browser-based VS Code window with a terminal inside the container.

### Option B: Local VS Code or Cursor

Use this when you want files on your machine.

Prerequisites:

- [Docker](https://www.docker.com/) running on the host.
- [VS Code](https://code.visualstudio.com/), [Cursor](https://cursor.com/), or another [Dev Containers-compatible IDE](/getting-started/ide-and-workspaces).

Steps:

1. Clone or open the repo.
2. Choose Reopen in Container when prompted.
3. Wait for the Dev Container build to finish.

Your editor should be attached to the container, not just the host folder.

## First commands

The container syncs dependencies and starts the docs site automatically. If that did not happen, run:

```bash
just sync
just docs-serve-bg
```

Dependencies should be installed and the local docs site should be available on localhost. Your IDE should show the forwarded docs port.

### 1. Run the tests

```bash
just test
```

Pytest should run and report passing tests, proving the demo model and export checks are working.

If you prefer the direct command:

```bash
uv run pytest
```

### 2. View the demo model

Open the OCP CAD Viewer panel in the activity bar, then run:

```bash
just view
```

The demo sphere should appear in the OCP CAD Viewer panel.

If the panel or extension is missing, use the [OCP CAD Viewer guide](/getting-started/ocp-viewer). Because we install from VSIX on cursor, if the extension crashes as often happens then cursor will uninstall the extension; you will need to reinstall the extension in order to run it again.

### 3. List and export artifacts

```bash
just mr-artifacts
just mr-export sphere /tmp/out step
just mr-export-generator sphere_generator /tmp/out '{"radius": 15}'
```

MakerRepo should list exportable artifacts and write generated files under `/tmp/out`.

For programmatic exports in tests or scripts, use `cad_tooling.export.export_part()`. See [CAD tooling export](/tools/cad-tooling/export).

## MCP servers

The container includes [build123d-mcp](/tools/mcp-servers) and [ocp-viewer-mcp](/tools/mcp-servers). They let AI agents run geometry code and inspect viewer feedback while the Python files remain the source of truth.

- Cursor: servers connect from [`.cursor/mcp.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.cursor/mcp.json). After a rebuild, reload MCP in Settings → MCP.
- VS Code / Codespaces: copy the server entries from `.cursor/mcp.json` into your [MCP settings](https://code.visualstudio.com/docs/copilot/chat/mcp-servers) if you use an MCP-capable assistant in that workspace.

If an MCP server fails to connect, see [MCP troubleshooting](/troubleshooting/mcp).

## Set up GitHub for your own repo

If you clicked [Use this template](https://github.com/Coffee2Bits/CAD-as-Code-Template/generate), a few settings live on GitHub.com and cannot be configured by the Dev Container alone:

1. [Create and initialize your repository](/getting-started/template-and-init) — Use this template, `template.repo.toml`, and `just init`.
2. [Set up GitHub](/getting-started/github-setup) — Actions permissions, Pages, branch protection, and squash merge.
3. [Releases](/getting-started/releases) — first automated GitHub Release with exported assets.


## Next steps

- [Project layout](/getting-started/project-layout) — where models, tests, docs, and tooling live.
- [Daily development](/workflows/daily-development) — the normal edit/test/view loop.
- [Modeling conventions](/modeling/conventions) — how to keep `cad/` clean and reusable.
- [Export and formats](/workflows/export-and-formats) — choose STEP, STL, GLB, or release bundles.
- [Troubleshooting](/troubleshooting/) — container, viewer, MCP, export, and CI/CD pipeline fixes.
