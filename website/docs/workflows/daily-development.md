---
sidebar_position: 1
---

# Daily development

## Edit loop

1. Change geometry in `cad/parts/` or `cad/assemblies/`
2. Point `main.py` at the model if needed
3. `just view` — visual verify in OCP CAD Viewer
4. `just test` — geometry and export tests
5. `just quality` — lint + pytest before pushing

## When to run full CI

```bash
just ci    # requires Docker socket in devcontainer
```

Use before merging significant changes or when touching CI/tooling.

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/) (`feat:`, `fix:`, `docs:`). See [Releases](/workflows/releases).
