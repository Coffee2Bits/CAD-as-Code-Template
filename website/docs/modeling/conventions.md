---
sidebar_position: 1
---

# Modeling conventions

## Source of truth

Python model code is authoritative — not STL or STEP meshes. Generated exports stay out of version control except golden fixtures under `tests/fixtures/`. Committed **reference** files (texture masks, vendor STEP, SVG profiles) belong under [`cad/assets/`](/modeling/third-party-assets) with a manifest — not scattered in `cad/parts/`.

## Units and types

- **Units:** millimeters unless a part docstring says otherwise
- **Return types:** `Part` or `Compound` from build123d builders
- **Parameters:** expose dimensions as function arguments with sensible defaults

## `main.py`

Keep thin — import builders from `cad/`, call `show_object`. No MakerRepo decorators in `main.py`.

## Testing

Test validity, key dimensions, and export behavior for each reusable part. See [Testing strategy](/modeling/testing).
