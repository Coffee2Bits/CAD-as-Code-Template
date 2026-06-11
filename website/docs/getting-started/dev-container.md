---
sidebar_position: 3
---

# Dev container

The `.devcontainer/` directory provides an [Open CASCADE](/reference/open-cascade) environment that matches CI.

This folder is **editor-agnostic**: the same `devcontainer.json` is used by VS Code, Cursor, GitHub Codespaces, DevPod, and other [spec-compatible clients](/getting-started/ide-and-workspaces). Pick any supported IDE — the container contents stay the same.

## Lifecycle

From [`devcontainer.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.devcontainer/devcontainer.json):

| Hook | Command |
|------|---------|
| `onCreateCommand` | `bash .devcontainer/install-ocp-cad-viewer.sh download` |
| `postCreateCommand` | `uv sync && just setup-hooks &&` VSIX download |
| `postStartCommand` | `uv sync && just setup-hooks &&` VSIX `install-cli` |

`uv sync` installs dev dependencies including **ocp-viewer-mcp**. **build123d-mcp** runs via pinned [`.cursor/run-*.sh`](https://github.com/Coffee2Bits/CAD-as-Code-Template/tree/main/.cursor) launchers (Python 3.12 in the container image). Both MCP servers execute **inside** this container — see [MCP servers](/tools/mcp-servers).

## Common commands

```bash
just sync          # uv sync
just sync-frozen   # frozen lockfile — matches CI
just setup-hooks   # pre-commit + Conventional Commit subject on commit-msg
```

## Docker for Dagger CI

`devcontainer.json` mounts `/var/run/docker.sock` so `just ci` can run Dagger inside the container. **Host Docker must be running.**

```json
"mounts": [
  "source=/var/run/docker.sock,target=/var/run/docker.sock,type=bind"
]
```

## Node.js (docs)

Node 20 is installed via the devcontainer `node` feature for `just docs-serve` / `just docs-build`. `postCreateCommand` runs `just docs-install`.

## Editor setup

Extensions: Python, Pylance, Ruff.

Format-on-save uses Ruff from the project venv (`importStrategy: fromEnvironment` in `.vscode/settings.json`). Mismatched formatters cause CI regressions — see [uv & quality](/tools/uv-and-quality).

## Features

- `common-utils` — zsh, automatic UID/GID alignment with host
- `docker-outside-of-docker` — Dagger CI from inside the container
- `node:20` — Docusaurus documentation site

## Troubleshooting

See [Dev container troubleshooting](/troubleshooting/dev-container).
