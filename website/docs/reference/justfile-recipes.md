---
sidebar_position: 1
---

# justfile recipes

Canonical reference. Run `just --list` in the repo for the live list.

## Setup

| Command | What it runs |
|---------|--------------|
| `just sync` | `uv sync` |
| `just sync-frozen` | `uv sync --group dev --frozen` (matches the CI/CD pipeline) |
| `just setup-hooks` | pre-commit install (commit + commit-msg hooks) |
| `just init` | Apply `template.repo.toml` — reset versions, rebrand workspace |
| `just init --owner acme --repo widget-cad` | CLI overrides instead of editing the TOML (all `--*` fields optional) |
| `just init --no-sync-docs` | Integration files only — skip README and docs markdown |
| `just init-dry-run` | Preview `just init` without writing |
| `just template-apply` | Re-apply `template.repo.toml` to README, docs, and integration files |
| `just template-apply-integration` | Re-apply identity to integration files only (skip README/docs) |

## Development

| Command | What it runs |
|---------|--------------|
| `just view` | Display `main.py` in OCP CAD Viewer |
| `just test` | `uv run pytest` (extra args: `just test -v tests/test_sphere.py`) |
| `just test-unit` | `uv run pytest -m unit` |
| `just test-integration` | `uv run pytest -m integration` |
| `just test-render` | `uv run pytest -m render` |
| `just test-functional` | `uv run pytest -m functional` |
| `just test-v` | `uv run pytest -v` |

## Quality

| Command | What it runs |
|---------|--------------|
| `just lint` | ruff check + format check + mypy + vulture |
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
| `just export-smoke` | Discover and export all artifacts as STEP and STL |
| `just export` | STL + PNG release bundle to `dist/` (ready for `just release-notes`) |
| `just export /tmp/out step sphere` | Export one artifact in a given format |
| `just release dist/` | Alias for `just export dist/` |
| `just release-notes v0.0.1` | Generate `dist/RELEASE_BODY.md` (repo from `template.repo.toml`) |
| `just render` | Headless PNG from `main.py` to `dist/` |
| `just render --lighting-preset default` | Same with CLI render overrides (flags may precede positionals) |
| `just render dist/sphere.stl dist/sphere.png --camera top` | Headless PNG from STL |
| `just render main.py dist --lighting-preset bright` | Viewer script with CLI render overrides |
| `just render-artifact sphere /tmp/out` | Export STL + headless PNG for one artifact |
| `just render-artifact demo_sphere dist --lighting-preset bright` | Artifact render with lighting override |

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

## CI/CD pipeline (Dagger)

| Command | What it runs |
|---------|--------------|
| `just ci` | Full Dagger pipeline (lint + artifacts + test) |
| `just ci-test` | Dagger pytest only |
| `just ci-lint` | Dagger ruff + mypy + vulture only |
| `just ci-artifacts` | Dagger artifact export verification |
| `just ci-release dist/` | Dagger release STL + PNG export |

See [just](/tools/just) for grouped overview and common workflows.
