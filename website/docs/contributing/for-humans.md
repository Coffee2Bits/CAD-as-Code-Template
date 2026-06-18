---
sidebar_position: 1
---

# Contributing (humans)

## Before opening a PR

```bash
just test-unit        # quick loop while editing (see Testing strategy)
just quality          # lint + full pytest — run before opening a PR
just ci               # full gate when touching the CI/CD pipeline or broad behavior
```

See [Testing strategy](/modeling/testing) for markers and test groups.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `deps:`. Squash-merge to `main`.

## Documentation changes

If you change `justfile`, pipeline workflows, MCP launchers, or export behavior, update the matching page under `website/docs/` in the same PR.

Local docs preview:

```bash
just docs-install
just docs-start
just docs-build
```
