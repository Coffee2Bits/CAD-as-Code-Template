---
sidebar_position: 1
---

# CAD tooling overview

Workspace helpers for exporting MakerRepo artifacts, rendering PNG previews, and generating GitHub Release notes. Lives **alongside** `cad/` — model geometry stays in `cad/parts/` and `cad/assemblies/`.

```text
cad_tooling/
├── export.py           # Discovery, export, CLI
├── render.py           # Headless OCP PNG rendering
├── render_config.py    # RenderConfig / CameraConfig
├── render_decorator.py # @render decorator
└── release_notes.py    # GitHub Release markdown
```

## When to use

| Task | Tool |
|------|------|
| Day-to-day artifact export | [`mr` CLI](/tools/makerrepo) |
| CI smoke, release STL+PNG | [Export](/tools/cad-tooling/export) |
| Headless preview PNG | [Render](/tools/cad-tooling/render) |
| Release body markdown | [Release notes](/tools/cad-tooling/release-notes) |

Tests mirror this package in `cad_tooling_tests/`.
