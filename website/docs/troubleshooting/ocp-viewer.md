---
sidebar_position: 3
---

# OCP viewer troubleshooting

| Issue | Fix |
|-------|-----|
| Extension missing (Cursor / fork) | **F1** → **`Extensions: Install from VSIX...`** → workspace root `ocp-cad-viewer-3.4.0.vsix` ([steps](/getting-started/ocp-viewer#manual-vsix-install-cursor-and-other-forks)) |
| Extension missing (VS Code / Codespaces) | Install `bernhard-42.ocp-cad-viewer` from Marketplace |
| VSIX file missing | `bash .devcontainer/install-ocp-cad-viewer.sh download` then install from VSIX |
| Cursor CLI reinstall | `bash .devcontainer/install-ocp-cad-viewer.sh install-cli` then reload window |
| Commands still missing | **Developer: Reload Window** after install |
| Blank viewer | Open OCP CAD Viewer panel **before** running `just view` |
| Cursor ESM crash / extension removed | Reinstall **patched** workspace VSIX (not Marketplace); rebuild container if file is stale |
| Cursor keeps uninstalling after crash | Use patched VSIX only — `bash .devcontainer/install-ocp-cad-viewer.sh download` refreshes it |

## Recovery sequence (Cursor and forks)

1. `bash .devcontainer/install-ocp-cad-viewer.sh download` (if `ocp-cad-viewer-3.4.0.vsix` is missing)
2. **F1** → **`Extensions: Install from VSIX...`** → select `/workspaces/<your-repo-folder>/ocp-cad-viewer-3.4.0.vsix`
3. **Developer: Reload Window**
4. Open OCP CAD Viewer panel (activity bar)
5. `just view`

Alternative for Cursor: `bash .devcontainer/install-ocp-cad-viewer.sh install-cli`, then steps 3–5.

See [OCP CAD Viewer setup](/getting-started/ocp-viewer).
