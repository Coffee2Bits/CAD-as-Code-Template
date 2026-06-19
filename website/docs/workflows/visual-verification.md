---
sidebar_position: 2
---

# Visual verification

**Required** after any edit to `cad/parts/` or `cad/assemblies/` (or `main.py` display wiring).

## Steps

1. Import the changed builder in `main.py` (keep `main.py` thin)
2. `just view` or `uv run python main.py`
3. Confirm geometry in OCP CAD Viewer panel — rotate, zoom, and use the [Clip tab](/getting-started/ocp-viewer#clip-view-section-cuts) when you need to inspect pockets, bores, or embedded hardware

![Section cut through the demo sphere assembly in OCP CAD Viewer](/img/ocp_clip_z.png)

<small><em>Use section cuts to confirm interior features, not just the outside silhouette, when reviewing geometry changes.</em></small>

## Agent loop (live updates)

When an agent edits model geometry, it should refresh the viewer **immediately after each edit** so you can watch changes in real time:

1. Update `main.py` if the displayed model changed
2. Start `just view` in the **background** right after saving the geometry change (non-blocking — do not wait for the script to exit)
3. Continue implementation or run tests (`just test-unit`, targeted groups, etc.) — viewer refresh is **not** tied to test commands

Re-launch `just view` in the background on **every** geometry edit. Each invocation re-executes `main.py` and pushes the latest solid to OCP CAD Viewer.

## Alternatives

- `just mr-view sphere` — view a published `@artifact`
- MCP `capture_ocp_screenshot` — agent visual confirmation

Skip only for non-geometry edits (docstrings, comments).
