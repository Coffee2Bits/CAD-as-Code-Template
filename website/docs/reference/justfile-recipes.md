---
sidebar_position: 1
---

# justfile recipes

Canonical reference. Run `just --list` in the repo for the live list.

## Setup

| Command | What it runs |
|---------|--------------|
| `just sync` | `uv sync` |
| `just sync-frozen` | `uv sync --group dev --frozen` (matches CI) |
| `just setup-hooks` | pre-commit install (commit + commit-msg hooks) |

## Development

| Command | What it runs |
|---------|--------------|
| `just view` | Display `main.py` in OCP CAD Viewer |
| `just test` | `uv run pytest` (extra args: `just test -v tests/test_sphere.py`) |
| `just test-v` | `uv run pytest -v` |

## Quality

| Command | What it runs |
|---------|--------------|
| `just lint` | ruff check + format check + mypy |
| `just format` | `uv run ruff format .` |
| `just quality` | lint + test |

## MakerRepo

| Command | What it runs |
|---------|--------------|
| `just mr-artifacts` | List `@artifact` functions |
| `just mr-generators` | List `@customizable` functions |
| `just mr-export sphere /tmp/out step` | Export one artifact |
| `just mr-view sphere` | Send artifact to OCP CAD Viewer |
| `just mr-export-generator sphere_generator /tmp/out '{"radius": 15}'` | Export with parameters |

## Export & render

| Command | What it runs |
|---------|--------------|
| `just export-smoke` | Discover and export all artifacts (CI smoke) |
| `just export dist/export step sphere` | Export via `cad_tooling.export` |
| `just release dist/` | STL + PNG release bundle |
| `just template-apply` | Apply `template.repo.toml` to docs site, README links, `pyproject.toml` |
| `just release-notes v0.0.1` | Generate `dist/RELEASE_BODY.md` (repo from `template.repo.toml`) |
| `just render` | Headless PNG from `main.py` to `dist/` |
| `just render dist/sphere.stl dist/sphere.png --camera top` | Headless PNG from STL |
| `just render-artifact sphere /tmp/out` | Export STL + headless PNG for one artifact |

## Release versioning

| Command | What it runs |
|---------|--------------|
| `just version-bump` | Bump patch via `uv version --bump` |
| `just version-bump minor` | Bump minor (also `major`, `alpha`, `beta`, `rc`, …) |
| `just version-tag` | Create and push `v{version}` tag |

:::warning Version bump syntax

Use `just version-bump minor` — not `just version-bump part=patch` (`just` treats `part=patch` as a literal string).

:::

## Documentation

| Command | What it runs |
|---------|--------------|
| `just docs-install` | `npm ci` in `website/` |
| `just docs-serve` | Docusaurus dev server (alias: `just docs-start`; auto-started in devcontainer on port 3000) |
| `just docs-serve-bg` | Background dev server via `.devcontainer/start-docs.sh` (idempotent) |
| `just docs-build` | Production docs build |

## CI (Dagger)

| Command | What it runs |
|---------|--------------|
| `just ci` | Full Dagger pipeline (lint + artifacts + test) |
| `just ci-test` | Dagger pytest only |
| `just ci-lint` | Dagger ruff + mypy only |
| `just ci-artifacts` | Dagger artifact smoke export |
| `just ci-release dist/` | Dagger release STL + PNG export |

See [just](/tools/just) for grouped overview and common workflows.
