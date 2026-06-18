---
sidebar_position: 6
---

# Export and CI/CD pipeline troubleshooting

## Artifact not discovered

- `@artifact` must be on an entry point in `cad/parts/` or `cad/assemblies/`
- Not on `make_*` builders or `main.py`
- Run `just mr-artifacts` to verify

## Export format errors

- Check supported formats: `step`, `stl`, `brep`, `gltf`, `3mf`
- Use `mr artifacts export --format` or file extension

## ruff format check fails

```bash
just format
```

Ensure editor uses Ruff from project venv (`importStrategy: fromEnvironment`).

## Release PNG missing

- Add `@render` below `@artifact` on the published function
- Run `just release dist/` locally to verify
