---
sidebar_position: 1
---

# Daily development

## Edit loop

1. Change geometry in `cad/parts/` or `cad/assemblies/`
2. Point `main.py` at the model if needed
3. `just view` — visual verify in OCP CAD Viewer ([agents](/workflows/visual-verification#agent-loop-live-updates): start in the **background** right after step 1–2)
4. `just test-unit` — fast feedback while editing ([Testing strategy](/modeling/testing)); independent of viewer refresh
5. `just test-integration` or `just test-render` when your change touches CAD export or PNG release paths
6. `just quality` — lint + **full** pytest before pushing

## When to run the full CI/CD pipeline

```bash
just ci    # requires Docker socket in devcontainer
```

Use before merging significant changes or when touching the CI/CD pipeline or tooling.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`). See [Releases](/workflows/releases).
