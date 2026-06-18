---
sidebar_position: 7
title: Set up GitHub for your repository
---

# Set up GitHub for your repository

This page is only about GitHub.com settings for your generated repository. It assumes you already created the repo and ran `just init` from [Create and initialize your repository](/getting-started/template-and-init).

These settings live outside git. The template can provide workflows, docs, and scripts, but it cannot enable Actions, set Pages to GitHub Actions, or protect your `main` branch for you.

After this page, continue to [Releases](/getting-started/releases) to publish generated STL/PNG assets through the CI/CD pipeline.

## Setup checklist

| # | Setting | Where in GitHub | Required for |
|---|---------|-----------------|--------------|
| 1 | [Actions enabled](#enable-github-actions) | Settings → Actions → General | all workflows |
| 2 | [Workflow permissions](#actions-workflow-permissions) | Settings → Actions → General | release-please Release PRs and tags |
| 3 | [GitHub Pages source](#github-pages) | Settings → Pages | Docusaurus docs deploy |
| 4 | [Branch protection](#branch-protection) | Settings → Branches or Rules → Rulesets | PR review and CI/CD pipeline gate |
| 5 | [Merge settings](#merge-settings) | Settings → General → Pull Requests | clean release-please changelog parsing |
| 6 | [Workflow inventory](#workflow-inventory) | `.github/workflows/` | know what automation is already committed |

## Enable GitHub Actions

Path: Repository → Settings → Actions → General

| Option | Value |
|--------|-------|
| Actions permissions | Allow all actions and reusable workflows, unless your org restricts this |
| Workflow permissions | Configure in the next section |

New template repos and forks can inherit org policies that restrict Actions. If the Actions tab shows no runs after a push, check this page first.

Direct link pattern:

```text
https://github.com/YOUR_ORG/YOUR_REPO/settings/actions
```

## Actions workflow permissions

Path: Repository → Settings → Actions → General → Workflow permissions

| Option | Value |
|--------|-------|
| Workflow permissions | Read and write permissions |
| Allow GitHub Actions to create and approve pull requests | Enabled |

### Why this matters

[release-please](https://github.com/googleapis/release-please) needs to open Release PRs, update release branches, tag releases, and hand off generated release assets. Without these repo-level permissions, the workflow can build fine but fail when it tries to create a PR, update labels, or publish a release.

The workflows also declare job-level permissions in git:

| Workflow | Job permissions |
|----------|-----------------|
| `release-please.yml` | `contents: write`, `pull-requests: write`, `issues: write` |
| `release.yml` | `contents: write` for release asset publishing |
| `docs.yml` | `contents: read`, `pages: write`, `id-token: write` |
| `ci.yml` | default read token for the Dagger check |

## GitHub Pages

Path: Repository → Settings → Pages

| Option | Value |
|--------|-------|
| Build and deployment → Source | GitHub Actions |

Do not use Deploy from a branch or a `gh-pages` branch. The docs site is built by [`docs.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/docs.yml) and deployed with `actions/deploy-pages`.

For a project site, the URL is usually:

```text
https://YOUR_ORG.github.io/YOUR_REPO/
```

The repo segment comes from `[github] repo` in `template.repo.toml`, which is applied by `just init`. If the docs URL is wrong, fix the template identity in [Create and initialize your repository](/getting-started/template-and-init#replace-the-template-identity), then run `just template-apply`.

The deploy job uses the `github-pages` environment. On first deploy, GitHub may ask you to approve environment creation. No environment secrets are required for a public template repo.

Docs deploy on push to `main` when `website/**` or `.github/workflows/docs.yml` changes. Pull requests run [`docs-pr.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/docs-pr.yml), which builds the docs without deploying them.

Direct link pattern:

```text
https://github.com/YOUR_ORG/YOUR_REPO/settings/pages
```

## Branch protection

Path: Repository → Settings → Branches → Branch protection rules

Some orgs use Rules → Rulesets instead. The goal is the same: protect `main` and require the checks that prove CAD changes still build.

Apply to branch: `main`

| Rule | Setting | Why |
|------|---------|-----|
| Require a pull request before merging | Enabled | Keeps `main` stable and reviewable |
| Required status checks | `Dagger CI` | Runs linting, artifact export verification, and tests for CAD/code changes |
| Optional docs check | `build` from Documentation PR check | Useful when protecting docs-heavy repos |
| Require branches to be up to date before merging | Recommended | Avoids merging stale green PRs |
| Require conversation resolution | Recommended | Keeps review feedback explicit |
| Require linear history | Optional | Pairs well with squash-only merge |
| Restrict who can push to matching branches | Optional | Prevents direct pushes to `main` |
| Allow force pushes | Disabled | Protects release history |
| Allow deletions | Disabled | Protects `main` |

GitHub only offers a status check after that check has run at least once. If `Dagger CI` is missing from the dropdown, open a small PR that touches `cad/` or `tests/`, wait for the CI/CD pipeline to run, then return to branch protection.

`ci.yml` is path-filtered. It runs for changes under `cad/**`, `tests/**`, `ci/**`, `.github/workflows/**`, `pyproject.toml`, `uv.lock`, and `.makerrepo/**`. Docs-only PRs may not run `Dagger CI`; that is intentional.

Direct link pattern:

```text
https://github.com/YOUR_ORG/YOUR_REPO/settings/branches
```

## Merge settings

Path: Repository → Settings → General → Pull Requests

| Option | Value |
|--------|-------|
| Allow squash merging | Enabled |
| Default merge method | Squash |
| Allow merge commits | Disabled, recommended |
| Allow rebase merging | Optional |

release-please reads the commit subject that lands on `main`. Squash titles like `feat(bracket): add mounting tabs` produce clean changelog entries and semver bumps. Merge commits make release notes noisy and harder to predict.

Release PRs use the title pattern `chore: release X.Y.Z`. Do not rewrite that squash title when merging a Release PR.

## Workflow inventory

These workflows are already committed by the template. GitHub settings decide whether they are allowed to run and publish.

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| [`ci.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/ci.yml) | PR + push to `main` with path filters | Dagger `check`: lint, artifact export verification, pytest |
| [`release-please.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/release-please.yml) | Push to `main` | Open/update Release PR; create tags for releases |
| [`release.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/release.yml) | Push tag `v*.*.*` | Quality gate → export STL/PNG → GitHub Release |
| [`docs.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/docs.yml) | Push to `main` with docs paths | Build and deploy Docusaurus to Pages |
| [`docs-pr.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/docs-pr.yml) | PR to `main` with docs paths | Verify docs build |

No repository secrets are required for the default workflows. They use GitHub's `GITHUB_TOKEN` and the repository source.

Release automation config lives in git:

| File | Role |
|------|------|
| [`release-please-config.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/release-please-config.json) | Semver and changelog rules |
| [`.release-please-manifest.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.release-please-manifest.json) | Current version pointer, reset by `just init` |

## Verify the setup

After configuration:

1. Push a docs change to `main` or merge a docs PR. Confirm Deploy documentation succeeds and the Pages site loads.
2. Open a PR that touches `cad/` or `tests/`. Confirm `Dagger CI` runs.
3. Merge with a `feat:` or `fix:` squash title. Confirm release-please opens or updates a Release PR.
4. Merge the Release PR with the default `chore: release X.Y.Z` squash title. Confirm a GitHub Release appears with STL/PNG assets.
5. Re-check Settings → Actions → General if release-please cannot create a PR or tag.

## Troubleshooting

| Symptom | Likely fix |
|---------|------------|
| Actions tab is empty | Enable Actions for the repository or check org policy |
| release-please does not open a Release PR | Set workflow permissions to read/write and enable Action-created PRs |
| Docs site is 404 | Set Pages source to GitHub Actions and wait for the first docs deploy |
| Branch protection cannot find `Dagger CI` | Run a PR that touches `cad/` or `tests/`, then add the check after it appears |
| Cannot merge because a required check is missing | Check the branch protection rule against `ci.yml` path filters |
| Wrong docs URL | Fix `template.repo.toml`, then run `just template-apply` |
| Release PR merge does not publish assets | Keep the squash title as `chore: release X.Y.Z`; then check the tag-triggered `release.yml` run |

## Related docs

- [Create and initialize your repository](/getting-started/template-and-init) — Use this template, `template.repo.toml`, and `just init`
- [Releases](/getting-started/releases) — first release and day-to-day versioning
- [Release workflow reference](/workflows/releases) — deeper release mechanics
- [CI/CD pipeline and Dagger](/workflows/ci-and-dagger) — what the required check runs
- [Dev container GitHub CLI](/getting-started/dev-container#github-cli) — `gh` authentication inside the container

In-repo copy: [`.github/GITHUB_SETUP.md`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/GITHUB_SETUP.md)
