---
sidebar_position: 4
---

# OCP CAD Viewer

Live 3D visualization for build123d models via `show_object()` and the [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer) extension.

![Dev environment with OCP CAD Viewer](/img/repo_preview.png)

## VSIX install

The VSIX is **not committed**. It is downloaded to the workspace root as `ocp-cad-viewer-3.4.0.vsix` (gitignored).

### Cursor ESM patch

v3.4.0 ships an ESM-only `proper-lockfile` dependency that crashes in Cursor's extension host (`ERR_REQUIRE_ESM`). Devcontainer scripts patch the VSIX before install. VS Code is unaffected.

## Automated setup

| Hook | Action |
|------|--------|
| `onCreateCommand` | `install-ocp-cad-viewer.sh download` |
| `postCreateCommand` | download (again after `uv sync`) |
| `postStartCommand` | `post-start.sh` — OCP viewer CLI install (non-fatal) and `start-docs.sh` for Docusaurus |

## Manual recovery

If commands are missing after reopening the container:

```bash
bash .devcontainer/install-ocp-cad-viewer.sh install-cli
```

Then:

1. **Developer: Reload Window**
2. Open the **OCP CAD Viewer** panel (activity bar icon)
3. `just view` or `uv run python main.py`

## Troubleshooting

See [OCP viewer troubleshooting](/troubleshooting/ocp-viewer).
