---
sidebar_position: 2
---

# Visual verification

**Required** after any edit to `cad/parts/` or `cad/assemblies/` (or `main.py` display wiring).

## Steps

1. Import the changed builder in `main.py` (keep `main.py` thin)
2. `just view` or `uv run python main.py`
3. Confirm geometry in OCP CAD Viewer panel

## Agent loop (live updates)

When an agent edits model geometry, it should refresh the viewer **on every iteration** so you can watch changes in real time:

1. Update `main.py` if the displayed model changed
2. Start `just view` in the **background** (non-blocking — do not wait for the script to exit)
3. Run `just test-unit` (or a targeted integration/render group) in the foreground

Re-launch `just view` in the background before each test run after a geometry edit. Each invocation re-executes `main.py` and pushes the latest solid to OCP CAD Viewer while tests run.

## Alternatives

- `just mr-view sphere` — view a published `@artifact`
- MCP `capture_ocp_screenshot` — agent visual confirmation

Skip only for non-geometry edits (docstrings, comments).
