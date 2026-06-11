---
sidebar_position: 7
title: Releases
---

# Releases

This template ships **automated GitHub Releases**: STL and PNG assets for every `@artifact`, plus a generated release body. The flow is driven by [release-please](https://github.com/googleapis/release-please) and [Conventional Commits](https://www.conventionalcommits.org/) on `main`.

**Prerequisite:** complete [Set up GitHub for your repository](/getting-started/github-setup) first — workflow permissions and squash merge are required before release-please can open Release PRs or publish assets.

## How it works

```mermaid
flowchart LR
  CC["Conventional Commits on main"] --> RP["release-please"]
  RP --> RPR["Release PR\nchore: release X.Y.Z"]
  RPR --> MERGE["Squash-merge Release PR"]
  MERGE --> TAG["Tag vX.Y.Z"]
  TAG --> DREL["Dagger release-artifact"]
  DREL --> GHR["GitHub Release\nSTL + PNG"]
```

| Step | What happens |
|------|----------------|
| 1 | You merge feature/fix PRs to `main` with **squash** titles like `feat(sphere): add label` |
| 2 | [`release-please.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/release-please.yml) opens or updates a **Release PR** (`chore: release 0.2.0`) |
| 3 | You review the Release PR (version bump in `pyproject.toml`, `CHANGELOG.md`) and merge it |
| 4 | The squash subject `chore: release X.Y.Z` triggers export + [`cad_tooling`](/tools/cad-tooling/) release notes + GitHub Release upload |

Version tracking: [`release-please-config.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/release-please-config.json) and [`.release-please-manifest.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.release-please-manifest.json) (starts at `0.1.0` in the template).

## First release on a new repository

After [using the template](/getting-started/github-setup#using-the-template) and [GitHub setup](/getting-started/github-setup):

1. **Confirm Actions settings** — Settings → Actions → General: **Read and write permissions** and **Allow GitHub Actions to create and approve pull requests** (see [workflow permissions](/getting-started/github-setup#actions-workflow-permissions)).
2. **Merge a releasable change** — open a PR with a Conventional Commit squash title, e.g. `feat: initial customization`, and merge to `main`.
3. **Wait for release-please** — within a few minutes, a Release PR should appear (title `chore: release 0.2.0` or similar). If it does not, see [troubleshooting](#troubleshooting).
4. **Merge the Release PR** — use the default squash title (`chore: release X.Y.Z`); do not edit it.
5. **Verify the GitHub Release** — Repository → **Releases** → new tag `vX.Y.Z` with `dist/*.stl`, `dist/*.png`, and generated notes.

You do not need repository secrets — workflows use `GITHUB_TOKEN`.

## Day-to-day versioning

| Squash PR title prefix | Release impact |
|------------------------|----------------|
| `feat:` | Minor semver bump |
| `fix:` | Patch bump |
| `feat!:` / `fix!:` / `BREAKING-CHANGE:` footer | Major bump |
| `docs:`, `deps:` | Releasable (Python release-type) |
| `chore:`, `ci:`, `test:` | No changelog entry on their own |

The **PR title** becomes the squash commit subject on `main` — that is what release-please parses. Full commit guide: [Releases workflow](/workflows/releases#conventional-commits-summary) and [AGENTS.md](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/AGENTS.md#commit-messages-release-please).

## What gets published

On each release (Release PR merge or manual tag):

1. **Quality gate** — Dagger `check` (ruff, mypy, artifact smoke, pytest)
2. **Export** — all `@artifact` models as STL + PNG (via `@render` where configured)
3. **GitHub Release** — assets attached; body from [`cad_tooling.export release-notes`](/tools/cad-tooling/release-notes)

Release notes template: [`.github/release_template.md`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/release_template.md).

## Local dry-run

`just release-notes` reads `owner/repo` from [`template.repo.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/template.repo.toml) — set that file first (see [Replace template identity](/getting-started/github-setup#replace-template-identity-in-your-repo)).

```bash
just release dist/
just release-notes v0.1.0
```

Override the repo slug explicitly: `just release-notes v0.1.0 repo=acme/my-widget`

Inspect `dist/` for STL/PNG and `dist/RELEASE_BODY.md` before trusting CI output.

## Manual tag fallback

If you need a release without a Release PR:

```bash
just version-bump        # optional — bumps pyproject.toml locally
just version-tag         # creates and pushes v{version}
```

Pushing a **strict semver** tag (`v1.2.3` only — no suffixes) runs [`release.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/release.yml). Prefer the release-please path for changelog discipline.

### Single publish path

| Step | Workflow | What it does |
|------|----------|--------------|
| Day-to-day merges | `release-please.yml` | Opens/updates Release PRs |
| Merge Release PR | `release-please.yml` | Creates git tag (`skip-github-release: true`) |
| Tag push `vX.Y.Z` | `release.yml` | Quality gate → export STL/PNG → GitHub Release |

Do **not** run `gh release create` for normal releases — that bypasses export and can duplicate tags. Use `gh release list` / `gh release view` to inspect only.

## GitHub CLI

The dev container ships [`gh`](https://cli.github.com/) — see [Dev container → GitHub CLI](/getting-started/dev-container#github-cli) for authentication:

```bash
gh release list --repo OWNER/REPO
gh release view v0.1.0 --repo OWNER/REPO
```

## Cleaning up mistaken releases

If debugging created extra tags (for example `v0.1.0-dup-test`), delete the release and tag:

```bash
gh release delete v0.1.0-dup-test --repo OWNER/REPO --yes
git push origin :refs/tags/v0.1.0-dup-test
```

Keep one canonical release per version (for this repo: **`v0.1.0`** with STL/PNG assets). Optional: delete early CI test releases (`v0.0.1`, `v0.0.2`) the same way if you do not need them.

## Fork vs your own repo

| Scenario | Release automation |
|----------|-------------------|
| **Use this template** → new repository | Follow this page and [GitHub setup](/getting-started/github-setup) |
| **Fork** to contribute upstream | Usually **disable or ignore** release-please on your fork; open PRs to the upstream repo instead |
| **Fork** as a starting point for a separate product | Treat like a template: rename/customize, then configure GitHub settings on **your** fork |

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| No Release PR after merging `feat:` / `fix:` | [Workflow permissions](/getting-started/github-setup#actions-workflow-permissions); check Actions tab for failed `Release Please` run |
| Release PR exists but will not update | Stale `autorelease: pending` label on an old Release PR — remove label and re-run workflow ([release-please docs](https://github.com/googleapis/release-please#why-are-there-multiple-release-prs)) |
| Merge Release PR but no GitHub Release | Squash subject must match `chore: release X.Y.Z` exactly |
| Extra duplicate releases | Manual `gh release create` or non-semver test tags (`v0.1.0-dup-test`) — delete extras; only push strict `vX.Y.Z` tags; see [Cleaning up mistaken releases](#cleaning-up-mistaken-releases) |
| `Resource not accessible by integration` on create-a-release | Usually duplicate publish paths or pushing workflow changes without `workflow` OAuth scope locally — use release-please + `release.yml` only; refresh `gh auth` with `-s workflow` when editing workflows |
| Release workflow fails on assets | Ensure at least one `@artifact` exports; run `just export-smoke` locally |
| Wrong asset URLs in notes | Published notes need absolute `releases/download/{tag}/` URLs — see [release notes](/tools/cad-tooling/release-notes) |

More detail: [Releases workflow](/workflows/releases) · [GitHub setup troubleshooting](/getting-started/github-setup#troubleshooting) · [Export & CI troubleshooting](/troubleshooting/export-and-ci).
