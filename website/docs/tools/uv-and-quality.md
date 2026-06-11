---
sidebar_position: 5
---

# uv & quality

## Dependencies

```bash
just sync          # uv sync — all groups
just sync-frozen   # uv sync --group dev --frozen (matches CI/Dagger)
```

Dev dependencies include pytest, ruff, mypy, pre-commit, makerrepo-cli, MCP packages, and Dagger.

## Lint and format

```bash
just lint          # ruff check + format check + mypy
just format        # apply ruff formatting
just quality       # lint + pytest — local gate before pushing
```

Individual commands:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy cad cad_tooling tests cad_tooling_tests
uv run pytest
```

### mypy scope

`cad`, `cad_tooling`, `tests`, `cad_tooling_tests` — same as CI.

## Editor alignment

Ruff format-on-save must match CI. Settings in [`.vscode/settings.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.vscode/settings.json) and devcontainer customizations:

- `editor.defaultFormatter`: Ruff
- `ruff.importStrategy`: `fromEnvironment`
- `ruff.configuration`: `${workspaceFolder}/pyproject.toml`

Do not use Black, autopep8, or the built-in Python formatter — they drift from CI.

## Git hooks

```bash
just setup-hooks
```

Installs pre-commit (ruff check/format) and commit-msg (Conventional Commit subject validation).

Agents: full formatter rules in [AGENTS.md](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/AGENTS.md#formatter-and-linter-alignment).

## Full CI gate

```bash
just ci    # Dagger: lint + artifacts + test (Docker required)
```

See [CI & Dagger](/workflows/ci-and-dagger).
