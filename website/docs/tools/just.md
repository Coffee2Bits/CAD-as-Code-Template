---
sidebar_position: 1
---

# just

[just](https://github.com/casey/just) wraps common repo tasks. Preinstalled in the devcontainer — run `just` or `just --list` from the repo root.

## Recipe reference

| Group | Command | What it runs |
|-------|---------|--------------|
| **setup** | `just sync` | `uv sync` |
| | `just sync-frozen` | `uv sync --group dev --frozen` (matches CI) |
| | `just setup-hooks` | pre-commit install |
| **dev** | `just view` | Display `main.py` in OCP CAD Viewer |
| | `just test` | `uv run pytest` (extra args: `just test -v tests/test_sphere.py`) |
| **quality** | `just lint` | ruff check + format check + mypy |
| | `just format` | `uv run ruff format .` |
| | `just quality` | lint + test |
| **makerrepo** | `just mr-artifacts` | List `@artifact` functions |
| | `just mr-generators` | List `@customizable` functions |
| | `just mr-export sphere /tmp/out step` | Export one artifact |
| | `just mr-view sphere` | Send artifact to OCP CAD Viewer |
| | `just mr-snapshot sphere` | Headless artifact PNG via `mr` |
| | `just mr-export-generator sphere_generator /tmp/out '{"radius": 15}'` | Export with parameters |
| **export** | `just export-smoke` | Discover and export all artifacts (CI smoke) |
| | `just export dist/export step sphere` | Export via `cad_tooling.export` |
| | `just release dist/` | STL + PNG release bundle |
| **setup** | `just template-apply` | Apply `template.repo.toml` after "Use this template" |
| | `just release-notes v0.0.1` | Generate `dist/RELEASE_BODY.md` (repo from `template.repo.toml`) |
| | `just render` | Headless PNG from `main.py` to `dist/` |
| **release** | `just version-bump` | Bump patch via `uv version --bump` |
| | `just version-bump minor` | Bump minor (also `major`, `alpha`, `beta`, `rc`, …) |
| | `just version-tag` | Create and push `v{version}` tag |
| **ci** | `just ci` | Full Dagger pipeline |
| | `just ci-test` | Dagger pytest only |
| | `just ci-lint` | Dagger ruff + mypy only |
| | `just ci-artifacts` | Dagger artifact smoke |
| | `just ci-release dist/` | Dagger release STL + PNG |
| **docs** | `just docs-install` | `npm ci` in `website/` |
| | `just docs-serve` | Docusaurus dev server (alias: `just docs-start`) |
| | `just docs-build` | Production docs build |

## Common workflows

```bash
just quality          # before pushing
just ci               # full CI gate (Docker required)
just release dist/    # local release dry-run
```

## Pitfall: version bump

Pass the bump kind as a positional argument:

```bash
just version-bump minor   # correct
just version-bump part=patch   # wrong — just treats this as a literal string
```

See also [justfile recipes](/reference/justfile-recipes) (canonical table).
