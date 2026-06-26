---
sidebar_position: 4
---

# OCP CAD Viewer

Live 3D visualization for build123d models via `show_object()` and the [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer) extension.

![Dev environment with OCP CAD Viewer](/img/repo_preview.png)

<small><em>The OCP CAD Viewer runs beside the model source so changes can be inspected without leaving the workspace.</em></small>

## VSIX install

The VSIX is **not committed**. Devcontainer hooks download and patch it to the workspace root as `ocp-cad-viewer-3.4.0.vsix` (gitignored).

### VS Code and Codespaces

[Visual Studio Code](https://code.visualstudio.com/) and **GitHub Codespaces** usually install OCP CAD Viewer from the Marketplace — accept the extension recommendation on first open, or search Extensions for **`bernhard-42.ocp-cad-viewer`**.

### Manual VSIX install (Cursor and other forks)

**[Cursor](https://cursor.com/)**, [Windsurf](https://windsurf.com/), [VSCodium](https://vscodium.com/), and some other VS Code derivatives **often do not auto-install** the extension. Plan on installing the **patched** workspace VSIX by hand the first time you open the project — and again if Cursor disables the extension after an activation crash.

Use the file at the **workspace root**, not an unpatched copy from the Marketplace (see [Cursor ESM patch](#cursor-esm-patch) below).

**From the Command Palette (typical Cursor workflow):**

1. Ensure the VSIX exists — container create/start runs the download. If the file is missing:

   ```bash
   bash .devcontainer/install-ocp-cad-viewer.sh download
   ```

2. Press **F1** (Command Palette) → **`Extensions: Install from VSIX...`**
3. Select the patched file, for example:

   `/workspaces/<your-repo-folder>/ocp-cad-viewer-3.4.0.vsix`

   In a Dev Container the workspace is usually mounted under `/workspaces/`; the folder name matches your clone (e.g. `cad-as-code-project`). You can also browse to `${workspaceFolder}/ocp-cad-viewer-3.4.0.vsix` from the file picker.

4. **Developer: Reload Window**
5. Open the **OCP CAD Viewer** panel (activity bar icon)
6. `just view` or `uv run python main.py`

**From a terminal (Cursor only):**

```bash
bash .devcontainer/install-ocp-cad-viewer.sh install-cli
```

Then reload the window and open the viewer panel before running `just view`.

### Cursor ESM patch

v3.4.0 ships an ESM-only `proper-lockfile` dependency that crashes in Cursor's extension host (`ERR_REQUIRE_ESM`). Devcontainer scripts patch the VSIX before install. VS Code and unpatched Marketplace installs are unaffected — **Cursor must use the patched workspace VSIX**.

## Automated setup

| Hook | Action |
|------|--------|
| `onCreateCommand` | `install-ocp-cad-viewer.sh download` — fetch and patch VSIX to workspace root |
| `postCreateCommand` | download again (after `uv sync`) |
| `postStartCommand` | `post-start.sh` — optional `install-cli` via Cursor CLI (non-fatal), `just view` to push the demo model, then `start-docs.sh` |

Automated CLI install only runs when the **Cursor** command-line tool is available inside the container. The startup `just view` step is also non-fatal; it prepares the demo model for the OCP CAD Viewer when the extension is available, but you can always open the viewer panel and run `just view` again manually. If the extension is still missing after attach, use [manual VSIX install](#manual-vsix-install-cursor-and-other-forks) above.

## Manual recovery

If the extension is missing or commands disappeared after reopening the container:

1. [Install from the patched VSIX](#manual-vsix-install-cursor-and-other-forks) (Cursor and forks), **or** run:

   ```bash
   bash .devcontainer/install-ocp-cad-viewer.sh install-cli
   ```

   (Cursor terminal path only)

2. **Developer: Reload Window**
3. Open the **OCP CAD Viewer** panel (activity bar icon)
4. `just view` or `uv run python main.py`

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
| [**Use object color caps**](#use-object-color-caps) | Color cut faces with each object's material instead of the default cap highlight. |
| **Reset** (Clip tab) | Restore default slider positions and options. |

### Use object color caps

By default, clipping planes paint every cut face with one **cap highlight** color. That makes the slice easy to spot, but every part on the section reads as the same material — in the [Y-axis clip](#open-the-clip-tab) above, the sphere shell, nut pocket, screw, and legs all appear green on the cut.

Enable **Use object color caps** when you need to see *which object* each cut face belongs to — especially in multi-part assemblies where [`Part.color`](https://build123d.readthedocs.io/) already encodes identity (body, reference hardware, tripod legs, and so on).

1. Open the **Clip** tab and position your slice (a **Y** cut through [`demo_sphere`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/cad/assemblies/demo_sphere.py) is a good practice view for nut pockets and screw seats).
2. Check **Use object color caps**.

![Clip along Y with object color caps — sphere body, nut, screw, and legs each keep their part color on the cut faces](/img/ocp_clip_y_object_color_cap.png)

With the option on, the yellow sphere shell, black nut, silver screw, and orange tripod legs each keep their own color on the section. You can trace a pocket wall or seat without hiding reference parts in the **Tree** tab — the slice itself shows which solid owns each face.

To restore the uniform cap highlight, uncheck the option or use **Reset** on the Clip tab.

### Tips

- **Clipping vs hiding** — Clip removes geometry from the *render* so you can see through a shell; it does not delete objects from the scene tree. To hide a whole part (e.g. a reference nut), use the eye icon on that node in the **Tree** tab instead.
- **Measurement mode** — Clipping is disabled while measuring; exit measure mode to adjust planes again.
- **Keep settings while iterating** — The viewer reuses the same panel across repeated `show_object` / `just view` runs, so Clip slider positions often persist while you edit and re-run — useful when tuning a pocket or seat.
- **From Python** — Pass clip kwargs to `show()` / `show_object()` (via [ocp-vscode](https://github.com/bernhard-42/ocp_vscode)): `clip_slider_0`, `clip_normal_0`, …, `clip_intersection`, `clip_planes`, `clip_object_colors`. See upstream [show command docs](https://github.com/bernhard-42/vscode-ocp-cad-viewer/blob/main/docs/show.md).

## Troubleshooting

See [OCP viewer troubleshooting](/troubleshooting/ocp-viewer).
