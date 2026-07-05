---
sidebar_position: 3
---

# Dev container

The `.devcontainer/` directory provides an [Open CASCADE](/reference/open-cascade) environment that matches the CI/CD pipeline.

This folder is **editor-agnostic**: the same `devcontainer.json` is used by VS Code, Cursor, GitHub Codespaces, DevPod, and other [spec-compatible clients](/getting-started/ide-and-workspaces). Pick any supported IDE — the container contents stay the same.

## Lifecycle

From [`devcontainer.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.devcontainer/devcontainer.json):

| Hook | Command |
|------|---------|
| `onCreateCommand` | `bash .devcontainer/install-ocp-cad-viewer.sh download` |
| `postCreateCommand` | `uv sync && just setup-hooks && just docs-install &&` VSIX download |
| `postStartCommand` | `post-start.sh` — `uv sync`, hooks, VSIX `install-cli` (non-fatal), then `start-docs.sh` |

`uv sync` installs dev dependencies including **ocp-viewer-mcp**. **build123d-mcp** runs via pinned [`.cursor/run-*.sh`](https://github.com/Coffee2Bits/CAD-as-Code-Template/tree/main/.cursor) launchers (Python 3.12 in the container image). Both MCP servers execute **inside** this container — see [MCP servers](/tools/mcp-servers).

## Host container runtime

**Reopen in Container** on a laptop needs Docker or Podman running on the host. Your editor builds the image from [`.devcontainer/Dockerfile`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.devcontainer/Dockerfile) and talks to that engine through the [Dev Containers](https://containers.dev/) tooling.

**Docker** is what most people use: [Docker Desktop](https://www.docker.com/products/docker-desktop/) on macOS or Windows, or [Docker Engine](https://docs.docker.com/engine/) on Linux. Follow [quick start: local setup](/getting-started/quick-start#option-b-local-vs-code-or-cursor).

**Podman** also works if you expose a Docker-compatible socket. On Linux, enable `podman.socket` and point `DOCKER_HOST` at it, or symlink it to `/var/run/docker.sock` (the path `devcontainer.json` mounts). On macOS or Windows, run [Podman Machine](https://podman.io/docs/installation) and use its socket.

**Codespaces** and other [cloud workspaces](/getting-started/ide-and-workspaces#cloud-workspaces) run the engine remotely. No local install. See [quick start: Codespaces](/getting-started/quick-start#option-a-online-codespaces).

Start the engine before **Reopen in Container**. The first build can take several minutes.

`just ci` uses the host socket at `/var/run/docker.sock` for Dagger. See [Docker for Dagger CI](#docker-for-dagger-ci) and [Dagger troubleshooting](/troubleshooting/dagger-and-docker).

## Common commands

```bash
just sync          # uv sync
just sync-frozen   # frozen lockfile — matches the CI/CD pipeline
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

Node 20 is installed via the devcontainer `node` feature for `just docs-serve` / `just docs-build`. `postCreateCommand` runs `just docs-install`; `postStartCommand` runs `post-start.sh`, which always starts the Docusaurus dev server in the background via `start-docs.sh` (even if the OCP viewer CLI install step fails).

Port **3000** is forwarded automatically and the browser opens when the server is ready (`forwardPorts` + `onAutoForward: openBrowser` in `devcontainer.json`). To restart manually:

```bash
just docs-serve-bg                 # background (idempotent)
bash .devcontainer/start-docs.sh # same script
just docs-serve                    # foreground with hot reload
```

## Editor setup

`devcontainer.json` recommends **Python**, **Pylance**, and **Ruff** only. **OCP CAD Viewer** is installed separately:

- **VS Code / Codespaces** — Marketplace extension `bernhard-42.ocp-cad-viewer` (recommendation or Extensions search).
- **Cursor and other forks** — manual install from the patched `ocp-cad-viewer-3.4.0.vsix` at the workspace root ([OCP CAD Viewer](/getting-started/ocp-viewer#manual-vsix-install-cursor-and-other-forks)).

Format-on-save uses Ruff from the project venv (`importStrategy: fromEnvironment` in `.vscode/settings.json`). Mismatched formatters cause CI/CD pipeline regressions — see [uv & quality](/tools/uv-and-quality).

## Features

- `common-utils` — zsh, automatic UID/GID alignment with host
- `docker-outside-of-docker` — run the Dagger CI/CD pipeline from inside the container
- `node:20` — Docusaurus documentation site
- `github-cli` — [GitHub CLI (`gh`)](https://cli.github.com/) for releases, PRs, and repo operations

## GitHub CLI

The dev container includes **`gh`**. In **GitHub Codespaces**, authentication is automatic. In a local Dev Container, log in once:

```bash
gh auth login
gh auth status
```

Common tasks (replace `OWNER/REPO` with your fork after [template initialization](/getting-started/template-and-init)):

```bash
gh pr create --fill
gh pr list
gh release list --repo OWNER/REPO
gh release view v0.1.0 --repo OWNER/REPO
```

Prefer the automated [release-please flow](/getting-started/releases) for publishing. Use `gh` to **inspect** releases only — do not `gh release create` for normal releases (that bypasses export and can duplicate tags). See [Single publish path](/getting-started/releases#single-publish-path).

## Troubleshooting

See [Dev container troubleshooting](/troubleshooting/dev-container).
