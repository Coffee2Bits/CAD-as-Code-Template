---
sidebar_position: 3
---

# OCP viewer troubleshooting

| Issue | Fix |
|-------|-----|
| Extension missing | `bash .devcontainer/install-ocp-cad-viewer.sh install-cli` |
| Commands still missing | **Developer: Reload Window** after install |
| Blank viewer | Open OCP CAD Viewer panel **before** running `just view` |
| Cursor ESM crash | Devcontainer patches VSIX — rebuild container; VS Code unaffected |

## Recovery sequence

1. `bash .devcontainer/install-ocp-cad-viewer.sh install-cli`
2. **Developer: Reload Window**
3. Open OCP CAD Viewer panel (activity bar)
4. `just view`

See [OCP CAD Viewer setup](/getting-started/ocp-viewer).
