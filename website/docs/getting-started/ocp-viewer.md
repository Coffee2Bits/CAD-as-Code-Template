---
sidebar_position: 4
---

# OCP CAD Viewer

Live 3D visualization for build123d models via `show_object()` and the [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer) extension.

![Dev environment with OCP CAD Viewer](/img/repo_preview.png)

<small><em>The OCP CAD Viewer runs beside the model source so changes can be inspected without leaving the workspace.</em></small>

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

## Clip view (section cuts)

Use the **Clip** tab when you need to see inside a solid — nut pockets, screw seats, bore depth, or any feature hidden behind an outer shell. The [`demo_sphere`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/cad/assemblies/demo_sphere.py) assembly is a good model to practice on: load it via `main.py`, then slice along each axis.

### Open the Clip tab

1. Display a model (`just view` or `uv run python main.py`).
2. In the OCP CAD Viewer sidebar, select **Clip** (tab order: Tree · **Clip** · Zebra · Material · Studio).
3. Drag the three sliders to move clipping planes along **X** (red), **Y** (green), and **Z** (blue). Each slider shows its plane normal `N=(…)` and position.

![Clip along X — screw head and socket section](/img/ocp_clip_x.png)

<small><em>X-axis clipping exposes the screw head and socket profile through the side of the demo sphere.</em></small>

![Clip along Y — nut pocket and clearance bore](/img/ocp_clip_y.png)

<small><em>Y-axis clipping shows the nut pocket and clearance bore alignment against the embedded hardware reference parts.</em></small>

![Clip along Z — sphere quadrant cut and embedded hardware](/img/ocp_clip_z.png)

<small><em>Z-axis clipping cuts away a sphere quadrant so the internal hardware stack and pocket depth are visible.</em></small>

### Clip options

| Control | Effect |
|---------|--------|
| **Intersection** | Keep only the volume inside all active planes (narrower slice). Off by default — planes remove geometry on their negative side independently. |
| **Planes** | Show semi-transparent grid helpers for each active plane. |
| **Use object color caps** | Color cut faces with each object's material instead of the default cap highlight. |
| **Reset** (Clip tab) | Restore default slider positions and options. |

### Tips

- **Clipping vs hiding** — Clip removes geometry from the *render* so you can see through a shell; it does not delete objects from the scene tree. To hide a whole part (e.g. a reference nut), use the eye icon on that node in the **Tree** tab instead.
- **Measurement mode** — Clipping is disabled while measuring; exit measure mode to adjust planes again.
- **Keep settings while iterating** — The viewer reuses the same panel across repeated `show_object` / `just view` runs, so Clip slider positions often persist while you edit and re-run — useful when tuning a pocket or seat.
- **From Python** — Pass clip kwargs to `show()` / `show_object()` (via [ocp-vscode](https://github.com/bernhard-42/ocp_vscode)): `clip_slider_0`, `clip_normal_0`, …, `clip_intersection`, `clip_planes`, `clip_object_colors`. See upstream [show command docs](https://github.com/bernhard-42/vscode-ocp-cad-viewer/blob/main/docs/show.md).

## Troubleshooting

See [OCP viewer troubleshooting](/troubleshooting/ocp-viewer).
