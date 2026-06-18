---
sidebar_position: 5
---

# Releases

:::tip New repository from the template?
Start with [Releases in Getting started](/getting-started/releases) for the first-release checklist and GitHub prerequisites, then return here for reference detail.
:::

```mermaid
flowchart LR
  CC["Conventional Commits"] --> RP["release-please"]
  RP --> RPR["Release PR"]
  RPR --> TAG["tag v{version}"]
  TAG --> DREL["Dagger release-artifact"]
  DREL --> GHR["GitHub Release STL + PNG"]
```

## release-please flow

1. Merge PRs to `main` with [Conventional Commit](https://www.conventionalcommits.org/) squash titles (`feat:`, `fix:`, `docs:`, `deps:`)
2. [`release-please.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/release-please.yml) opens or updates a **Release PR** (`chore: release X.Y.Z`)
3. Merge the Release PR → `release-please.yml` creates the tag and GitHub Release, then exports STL/PNG assets in the same workflow run

Config: [`release-please-config.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/release-please-config.json) (`release-type: python`).

## Set up GitHub first

Before release-please can open Release PRs, configure workflow permissions, squash merge, and branch protection on GitHub.com:

- [Set up GitHub for your repository](/getting-started/github-setup) — full checklist for template clones
- [Releases (getting started)](/getting-started/releases) — first release walkthrough

## Conventional Commits (summary)

| Prefix | Release impact |
|--------|----------------|
| `feat:` | Minor bump |
| `fix:` | Patch bump |
| `feat!:` / `fix!:` / `BREAKING-CHANGE:` | Major bump |
| `docs:`, `deps:` | Releasable (Python strategy) |
| `chore:`, `ci:`, `test:` | No Release PR entry on their own |

Squash-merge PRs — the **PR title** becomes the changelog entry release-please parses.

## Version commands

| Command | Purpose |
|---------|---------|
| `just version-bump` | Local patch bump (`uv version --bump`) |
| `just version-bump minor` | Local minor bump |
| `just version-tag` | Manual tag push (triggers `release.yml`) |

Version lives in `pyproject.toml`; tags use `v` prefix (`0.1.1` → `v0.1.1`).

## What gets published

**Release PR merge** — tag, changelog release, then `release-assets.yml` export/upload (no Dagger `check` in that workflow; `ci.yml` already ran on the PR).

**Manual tag or repair** — Dagger `check`, then the same export/upload job:

1. **Quality gate** — Dagger `check` (lint, artifact export verification, pytest)
2. **Export** — `@artifact` models that declare `@render` as STL + PNG
3. **GitHub Release** — `dist/*.stl`, `dist/*.png`; artifact notes appended to the release body

Release notes format: [`.github/release_template.md`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/release_template.md)

## Local dry-run

Set [`template.repo.toml`](/getting-started/template-and-init#replace-the-template-identity) first, then:

```bash
just release dist/
just release-notes v0.1.0
```

Or with explicit repo slug:

```bash
uv run python -m cad_tooling.export release -o dist/
uv run python -m cad_tooling.export release-notes \
  --assets-dir dist \
  --repo YOUR_ORG/YOUR_REPO \
  --tag v0.1.0 \
  -o dist/RELEASE_BODY.md
```

## Manual tag fallback

`just version-tag` or push a strict semver tag (`vX.Y.Z` only) triggers [`release.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/release.yml). Tags with suffixes (for example `v0.1.0-test`) are ignored by the publish job.

## Publish flow

1. `release-please.yml` — Release PRs; on merge, git tag, GitHub Release, and STL/PNG export/upload (`release-assets.yml`)
2. `release.yml` — manual semver tag push or `workflow_dispatch` repair: quality gate, then the same asset publish job

Release-please creates tags through the GitHub API, which does **not** emit a tag `push` event. Asset publishing must run inside `release-please.yml` (or via `workflow_dispatch` on `release.yml`), not rely on tag push alone.

Do not use `gh release create` for normal publishes. Release assets should come from the configured CI/CD pipeline so exports stay reproducible.

**Troubleshooting:** [Release Please & GitHub Releases](/troubleshooting/release-please) — missing assets, untagged merges, workflow errors, and `workflow_dispatch` repair.

## Release note URLs

Use absolute `releases/download/{tag}/` URLs — see [Release notes](/tools/cad-tooling/release-notes).

Force a specific version: empty commit with `Release-As: x.y.z` in body ([release-please docs](https://github.com/googleapis/release-please#how-do-i-change-the-version-number)).
