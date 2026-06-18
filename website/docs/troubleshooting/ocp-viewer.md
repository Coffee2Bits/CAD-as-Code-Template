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

## Missing Model Render colors

Headless previews (`export release`, `cad_tooling.render`) read `Part.color` from **leaf** `Part` nodes only. Uncolored `Compound` wrappers do not inherit child colors — flattening that stops on one paints its sub-tree with the default face color `(0.31, 0.63, 1.0)`.

| Symptom | Likely cause |
|---------|----------------|
| Uniform blue sub-tree | Uncolored intermediate `Compound` not flattened to leaves |
| Sub-artifact OK, assembly wrong | Validated a nested part, not the top-level `@artifact` |
| Everything one color | Rendered from STL (no per-part color metadata) |
| `just view` OK, PNG wrong | Live viewer uses the scene tree; headless render uses `_colored_solids` |

Set `part.color` on every leaf `Part`, compose multi-color parts as nested compounds, and validate the **published** `@artifact` from Python geometry (not STL):

```bash
uv run python -c "
from cad_tooling.render import _build_artifact_shape, _colored_solids
name = 'ARTIFACT'
for i, (_, c) in enumerate(_colored_solids(_build_artifact_shape(name), (0.31, 0.63, 1.0))):
    print(i, tuple(round(x, 2) for x in c))
"
just render-artifact ARTIFACT /tmp/out
```

One printed line per leaf solid; `(0.31, 0.63, 1.0)` means a missing `part.color` or an unflattened wrapper.

See also [Render — Assembly colors](/tools/cad-tooling/render#assembly-colors) and [AGENTS.md — Part preview colors](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/AGENTS.md#part-preview-colors).
