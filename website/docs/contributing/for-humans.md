---
sidebar_position: 1
---

# Contributing (humans)

## Before opening a PR

```bash
just quality          # lint + pytest
just ci               # full gate when touching CI or broadly
```

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `deps:`. Squash-merge to `main`.

## Documentation changes

If you change `justfile`, CI workflows, MCP launchers, or export behavior, update the matching page under `website/docs/` in the same PR.

Local docs preview:

```bash
just docs-install
just docs-start
just docs-build
```

Rollout tracker: [`website/DOCS_ROLLOUT_PLAN.md`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/website/DOCS_ROLLOUT_PLAN.md)
