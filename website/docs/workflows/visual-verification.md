---
sidebar_position: 2
---

# Visual verification

**Required** after any edit to `cad/parts/` or `cad/assemblies/`.

## Steps

1. Import the changed builder in `main.py` (keep `main.py` thin)
2. `just view` or `uv run python main.py`
3. Confirm geometry in OCP CAD Viewer panel

## Alternatives

- `just mr-view sphere` — view a published `@artifact`
- MCP `capture_ocp_screenshot` — agent visual confirmation

Skip only for non-geometry edits (docstrings, comments).
