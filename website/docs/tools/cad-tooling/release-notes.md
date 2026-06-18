---
sidebar_position: 4
---

# Release notes

Generate GitHub Release markdown from exported `@render` release assets.

```bash
just release-notes v0.1.0
```

Repo slug defaults from [`template.repo.toml`](/getting-started/template-and-init#replace-the-template-identity). Override: `just release-notes v0.1.0 repo=OWNER/REPO`

```bash
# explicit repo (without template.repo.toml)
just release-notes v0.1.0 repo=Coffee2Bits/CAD-as-Code-Template
```

Or:

```bash
uv run python -m cad_tooling.export release-notes \
  --assets-dir dist \
  --repo Coffee2Bits/CAD-as-Code-Template \
  --tag v0.1.0 \
  -o dist/RELEASE_BODY.md
```

## Absolute URLs required

Preview images and STL links must use `releases/download/{tag}/` URLs — GitHub does not resolve relative paths in release bodies:

```markdown
![sphere](https://github.com/Coffee2Bits/CAD-as-Code-Template/releases/download/v0.1.0/sphere.png)

[sphere.stl](https://github.com/Coffee2Bits/CAD-as-Code-Template/releases/download/v0.1.0/sphere.stl)
```

Local `dist/` paths work on disk only; the workflow uploads assets and the generated body references them by release URL.

See [Releases workflow](/workflows/releases).
