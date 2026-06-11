---
sidebar_position: 3
---

# CI functions

Dagger module: [`ci/src/ci/main.py`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/ci/src/ci/main.py)

Builds from [`.devcontainer/Dockerfile`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.devcontainer/Dockerfile), runs `uv sync --group dev --frozen`, then executes checks — matching GitHub Actions and local `just ci`.

## Functions

| Function | What it runs |
|----------|--------------|
| `check` | `lint` → `artifacts` → `test` (GitHub Actions default) |
| `lint` | `uv run ruff check .`, `ruff format --check .`, `mypy cad cad_tooling tests cad_tooling_tests`, `vulture` |
| `test` | `uv run pytest` |
| `artifacts` | `uv run python -m cad_tooling.export smoke` |
| `release-artifact` | `uv run python -m cad_tooling.export release -o /tmp/release-artifacts` → returns `dist/` directory |

## Invocations

```bash
dagger call -m ./ci check --source=.
dagger call -m ./ci test --source=.
dagger call -m ./ci lint --source=.
dagger call -m ./ci artifacts --source=.
dagger call -m ./ci release-artifact --source=. export --path=./dist
```

Or: `just ci`, `just ci-test`, `just ci-lint`, `just ci-artifacts`, `just ci-release dist/`

## Source ignore

Dagger mounts the repo but ignores `.git`, `.venv`, `ci/.venv`, caches, VSIX, and `.cursor/` — see `SOURCE_IGNORE` in `ci/src/ci/main.py`.

## GitHub Actions path filters

[`ci.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/ci.yml) runs on changes to:

- `cad/**`, `tests/**`, `ci/**`
- `.github/workflows/**`
- `pyproject.toml`, `uv.lock`, `.makerrepo/**`

Docs-only changes do not trigger Dagger CI (separate `docs-pr.yml`).

## Not in CI

- OCP CAD Viewer VSIX install
- MCP servers

See [CI & Dagger](/workflows/ci-and-dagger).
