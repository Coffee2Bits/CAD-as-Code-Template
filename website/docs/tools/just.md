---
sidebar_position: 1
---

# just

[just](https://github.com/casey/just) wraps common repo tasks. Preinstalled in the devcontainer — run `just` or `just --list` from the repo root.

## Recipe reference

| Group | Command | What it runs |
|-------|---------|--------------|
| **setup** | `just sync` | `uv sync` |
| | `just sync-frozen` | `uv sync --group dev --frozen` (matches the CI/CD pipeline) |
| | `just setup-hooks` | pre-commit install |
| **dev** | `just view` | Display `main.py` in OCP CAD Viewer |
| | `just test` | `uv run pytest` (extra args: `just test -v tests/test_sphere.py`) |
| | `just test-unit` | `uv run pytest -m unit` |
| | `just test-integration` | `uv run pytest -m integration` |
| | `just test-render` | `uv run pytest -m render` |
| | `just test-functional` | `uv run pytest -m functional` |
| **quality** | `just lint` | ruff check + format check + mypy + vulture |
| | `just format` | `uv run ruff format .` |
| | `just quality` | lint + test |
| **makerrepo** | `just mr-artifacts` | List `@artifact` functions |
| | `just mr-generators` | List `@customizable` functions |
| | `just mr-export sphere /tmp/out step` | Export one artifact |
| | `just mr-view sphere` | Send artifact to OCP CAD Viewer |
| | `just mr-export-generator sphere_generator /tmp/out '{"radius": 15}'` | Export with parameters |
| **export** | `just export-smoke` | Discover and export all artifacts (CI/CD pipeline smoke) |
| | `just export` | STL + PNG release bundle to `dist/` (ready for `just release-notes`) |
| | `just export /tmp/out step sphere` | Export one artifact in a given format |
| | `just release dist/` | Alias for `just export dist/` |
| **setup** | `just init` | Apply `template.repo.toml` — reset versions, rebrand workspace |
| | `just init --owner acme --repo widget-cad` | Same, with CLI overrides instead of editing the TOML |
| | `just init --no-sync-docs` | Integration files only (skip README/docs) |
| | `just template-apply` | Re-apply `template.repo.toml` (includes README/docs) |
| | `just template-apply-integration` | Re-apply integration files only |
| | `just release-notes v0.0.1` | Generate `dist/RELEASE_BODY.md` (repo from `template.repo.toml`) |
| | `just render` | Headless PNG from `main.py` to `dist/` |
| | `just render-artifact sphere /tmp/out` | Export STL + headless PNG via `cad_tooling` |
| **release** | `just version-bump` | Bump patch via `uv version --bump` |
| | `just version-bump minor` | Bump minor (also `major`, `alpha`, `beta`, `rc`, …) |
| | `just version-tag` | Create and push `v{version}` tag |
| **ci** | `just ci` | Full Dagger pipeline |
| | `just ci-test` | Dagger pytest only |
| | `just ci-lint` | Dagger ruff + mypy + vulture only |
| | `just ci-artifacts` | Dagger artifact smoke |
| | `just ci-release dist/` | Dagger release STL + PNG |
| **docs** | `just docs-install` | `npm ci` in `website/` |
| | `just docs-serve` | Docusaurus dev server (alias: `just docs-start`; auto-started in devcontainer on port 3000) |
| | `just docs-serve-bg` | Background dev server via `.devcontainer/start-docs.sh` (idempotent) |
| | `just docs-build` | Production docs build |

## Common workflows

```bash
just quality          # before pushing
just ci               # full CI/CD pipeline gate (Docker required)
just export           # local release dry-run (STL + PNG in dist/)
just release-notes v0.1.0
```

## Pitfall: version bump

Pass the bump kind as a positional argument:

```bash
just version-bump minor   # correct
just version-bump part=patch   # wrong — just treats this as a literal string
```

See also [justfile recipes](/reference/justfile-recipes) (canonical table).
