# Release notes template

This repository generates GitHub Release notes automatically when you push a semver tag (`v*.*.*`). The workflow exports every `@artifact` as an STL, renders a matching PNG preview, and fills in a release body like the example below.

To preview locally after exporting assets:

```bash
uv run python -m cad_tooling.export release -o dist/
uv run python -m cad_tooling.export release-notes \
  --assets-dir dist \
  --repo YOUR_GITHUB_ORG/YOUR_REPO \
  --tag v0.0.1 \
  -o dist/RELEASE_BODY.md
```

Replace `YOUR_GITHUB_ORG/YOUR_REPO` and the tag with your values. Open `dist/RELEASE_BODY.md` to review before tagging.

**Preview renders:** add `@render(...)` on each `@artifact` in `cad/parts/` or `cad/assemblies/` (see [`cad/parts/sphere.py`](../cad/parts/sphere.py)).

---

<!-- Example output (generated dynamically; do not edit placeholders below) -->

# Release artifacts

Parametric CAD models exported as STL from `@artifact` functions in this repository.
Each entry includes an OCCT preview render and a downloadable mesh file.

## {{ARTIFACT_NAME}}

![{{ARTIFACT_NAME}}](https://github.com/{{GITHUB_REPOSITORY}}/releases/download/{{TAG}}/{{ARTIFACT_NAME}}.png)

{{ARTIFACT_SHORT_DESC}}

[{{ARTIFACT_NAME}}.stl](https://github.com/{{GITHUB_REPOSITORY}}/releases/download/{{TAG}}/{{ARTIFACT_NAME}}.stl)

<!-- Repeat the `## {{ARTIFACT_NAME}}` section for each discovered @artifact. -->
