---
sidebar_position: 5
---

# uv & quality

## Dependencies

```bash
just sync          # uv sync — all groups
just sync-frozen   # uv sync --group dev --frozen (matches Dagger)
```

Dev dependencies include pytest, ruff, mypy, vulture, pre-commit, makerrepo-cli, MCP packages, and Dagger.

## Lint and format

```bash
just lint          # ruff check + format check + mypy + vulture
just format        # apply ruff formatting
just quality       # lint + pytest — local gate before pushing
```

Individual commands:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy cad cad_tooling tests cad_tooling_tests
uv run vulture
uv run pytest
```

### Dead code (vulture)

[`vulture`](https://github.com/jendrikseipp/vulture) scans for unused functions, classes, and variables. Configuration lives in [`pyproject.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/pyproject.toml) under `[tool.vulture]`:

- **paths** — `cad`, `cad_tooling`, `tests`, `cad_tooling_tests`, `main.py`, `scripts`, `ci/src`
- **ignore_decorators** — MakerRepo (`@artifact`, `@customizable`, `@cached`, `@render`), Dagger (`@function`), pytest (`@pytest.fixture`)
- **min_confidence** — `80` (default threshold; lowers false positives from framework entry points)

If vulture reports a false positive, add the name to `ignore_names` or create a `whitelist.py` entry — do not delete real dead code to silence the check.

### mypy scope

`cad`, `cad_tooling`, `tests`, `cad_tooling_tests` — same as the CI/CD pipeline.

## Editor alignment

Ruff format-on-save must match the CI/CD pipeline. Settings in [`.vscode/settings.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.vscode/settings.json) and devcontainer customizations:

- `editor.defaultFormatter`: Ruff
- `ruff.importStrategy`: `fromEnvironment`
- `ruff.configuration`: `${workspaceFolder}/pyproject.toml`

Do not use Black, autopep8, or the built-in Python formatter — they drift from the CI/CD pipeline.

## Git hooks

```bash
just setup-hooks
```

Installs pre-commit (ruff check/format, vulture) and commit-msg (Conventional Commit subject validation).

Agents: full formatter rules in [AGENTS.md](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/AGENTS.md#formatter-and-linter-alignment).

## Full CI/CD pipeline gate

```bash
just ci    # Dagger: lint + artifacts + test (Docker required)
```

See [CI/CD pipeline and Dagger](/workflows/ci-and-dagger).
