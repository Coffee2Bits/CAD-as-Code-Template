---
sidebar_position: 5
---

# Third-party assets

Python model code in `cad/` remains the [source of truth](/reference/glossary#source-of-truth). Some workflows still need **committed reference files** that are not generated from build123d — raster masks for emboss sampling, imported STEP shells, SVG profiles, or mesh inputs for boolean or visualization helpers.

Those files live under **`cad/assets/`**, separate from:

- **Generated exports** (STEP/STL/PNG from `@artifact` functions) — never commit these except golden fixtures under `tests/fixtures/`.
- **[External part libraries](/modeling/external-libraries)** — catalog geometry from bd_warehouse and similar packages, installed via `pyproject.toml`, not checked into the repo.

## Directory layout

```text
cad/assets/
├── images/       # Raster inputs (PNG, JPEG, alpha masks, height maps)
├── meshes/       # Triangle meshes (STL, OBJ, PLY) used as reference or cutters
├── svg/          # 2D vector profiles and logos for sketch import
├── step/         # B-rep reference solids (vendor STEP, legacy CAD imports)
└── manifests/    # One YAML file per asset — license, source, and usage notes
```

Each subdirectory contains an empty **`.gitignore`** so Git keeps the folder in the tree even before you add files. Drop new assets in the matching type folder and add a manifest alongside them.

| Folder | Typical formats | Use in models |
|--------|-----------------|---------------|
| `images/` | `.png`, `.jpg`, `.jpeg` | Texture sampling, bump maps, alpha masks |
| `meshes/` | `.stl`, `.obj`, `.ply` | Reference geometry, mesh-to-BRep workflows |
| `svg/` | `.svg` | Imported sketches, logos, 2D cut profiles |
| `step/` | `.step`, `.stp` | Vendor parts, legacy imports, fixed reference solids |
| `manifests/` | `.yaml` | Provenance and license for every committed asset |

## Manifest format

Every file under `images/`, `meshes/`, `svg/`, or `step/` should have a sibling manifest in `manifests/` named after the asset (without extension):

```yaml
# cad/assets/manifests/circle_alpha.yaml
id: circle_alpha
path: images/circle_alpha.jpg
type: image
format: jpeg
used_by:
  - cad.parts.sphere_texture_emboss
description: Tileable alpha mask for seigaiha-style radial bump embossing on the demo sphere
license: CC0-1.0
source_url: https://example.com/original
notes: Dark pixels become surface bumps; white pixels are skipped
```

| Field | Required | Purpose |
|-------|----------|---------|
| `id` | yes | Stable identifier (matches filename stem) |
| `path` | yes | Relative path from `cad/assets/` |
| `type` | yes | `image`, `mesh`, `svg`, or `step` |
| `format` | yes | File extension or MIME hint |
| `used_by` | yes | Python modules that load the asset |
| `description` | yes | Short human-readable summary |
| `license` | yes | SPDX identifier or plain-text license name |
| `source_url` | recommended | Where the file was obtained |
| `notes` | optional | Sampling rules, units, or caveats |

## Loading assets from model code

Resolve paths relative to the `cad/` package so tests and CI find files regardless of working directory:

```python
from pathlib import Path

ASSETS = Path(__file__).resolve().parents[1] / "assets"
TEXTURE_PATH = ASSETS / "images" / "circle_alpha.jpg"
```

Pass `texture_path` as an optional parameter when tests need overrides; assert the default file exists in unit tests.

## Live example: texture emboss on the demo sphere

The demo sphere applies a **seigaiha-style surface pattern** by sampling an alpha JPEG and fusing radial bumps onto the sphere shell before the NE quadrant cut and hardware pockets.

| Piece | Location |
|-------|----------|
| Asset | [`cad/assets/images/circle_alpha.jpg`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/cad/assets/images/circle_alpha.jpg) |
| Manifest | [`cad/assets/manifests/circle_alpha.yaml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/cad/assets/manifests/circle_alpha.yaml) |
| Builder | [`cad/parts/sphere_texture_emboss.py`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/cad/parts/sphere_texture_emboss.py) |
| Integration | [`cad/parts/sphere.py`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/cad/parts/sphere.py) (`make_textured_sphere_solid`) |
| Tests | [`tests/test_sphere_texture_emboss.py`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/tests/test_sphere_texture_emboss.py) |

Dark pixels in the texture (luminance below a threshold) become outward radial bumps; white pixels are skipped. The emboss depth is half the depth of the embossed label text so both features read clearly in the viewer and release PNG.

## Agent and contributor rules

**Do:**

- Place third-party or reference files only under `cad/assets/<type>/`.
- Add a manifest in `manifests/` with license and `used_by` before merging.
- Load assets via `Path(__file__).resolve().parents[1] / "assets" / ...`.
- Add a unit test that the default asset path exists when the builder depends on it.

**Do not:**

- Commit generated STEP/STL exports from `@artifact` functions (except `tests/fixtures/` golden files).
- Scatter assets under `cad/parts/` or the repo root.
- Reference assets by hard-coded absolute paths or paths relative to the repo root without anchoring to `cad/`.

Agents: summary in [AGENTS.md — Third-party assets](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/AGENTS.md#third-party-assets).

## Related guides

- [Modeling conventions](/modeling/conventions) — Python as source of truth
- [External part libraries](/modeling/external-libraries) — catalog geometry via PyPI/Git deps
- [Export and formats](/workflows/export-and-formats) — generated artifact outputs
