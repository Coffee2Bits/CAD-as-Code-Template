# CAD tooling

Workspace helpers for exporting MakerRepo artifacts, rendering PNG previews, and generating GitHub Release notes.

**Full documentation:** [CAD tooling on the docs site](https://coffee2bits.github.io/CAD-as-Code-Template/tools/cad-tooling/)

- [Export](https://coffee2bits.github.io/CAD-as-Code-Template/tools/cad-tooling/export)
- [Render](https://coffee2bits.github.io/CAD-as-Code-Template/tools/cad-tooling/render)
- [Release notes](https://coffee2bits.github.io/CAD-as-Code-Template/tools/cad-tooling/release-notes)

For day-to-day modeling, prefer the [`mr` CLI](https://docs.makerrepo.com/makerrepo-cli/). Use `cad_tooling` for programmatic export in tests/CI, headless renders, and release automation. This workspace uses OCP rendering instead of `mr artifacts snapshot` (which needs Playwright) — see the [render docs](https://coffee2bits.github.io/CAD-as-Code-Template/tools/cad-tooling/render).

Run from the repository root:

```bash
uv run python -m cad_tooling.export smoke
uv run python -m cad_tooling.render main.py -o dist/
just render-artifact sphere /tmp/out
```
