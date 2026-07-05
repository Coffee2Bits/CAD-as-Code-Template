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

## PR job summary missing previews

- Previews appear only on **pull_request** runs of [`ci.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/ci.yml), after the Dagger check succeeds
- Open the **Dagger CI** job and expand **Summary** — images are embedded from exported PNGs via `python -m cad_tooling.export pr-summary`
- If the summary is empty, confirm the artifact has `@render` and that `release-artifact` exported PNGs to `dist/`

Release workflow failures (missing STL/PNG on GitHub Releases, `workflow_dispatch` repair): [Release Please troubleshooting](/troubleshooting/release-please).
