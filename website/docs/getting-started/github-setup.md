---
sidebar_position: 6
title: Set up GitHub for your repository
---

# Set up GitHub for your repository

After you **[use this template](https://github.com/Coffee2Bits/CAD-as-Code-Template/generate)** or fork the repo, several settings live **only on GitHub.com** — they are not in git. Configure them once per repository so CI, releases, and documentation deploy correctly.

This page is for **your** repository after you use the template or fork — not for configuring the upstream [Coffee2Bits/CAD-as-Code-Template](https://github.com/Coffee2Bits/CAD-as-Code-Template) source repo itself.

## Setup checklist

| # | Setting | Where in GitHub | Required for |
|---|---------|-----------------|--------------|
| 1 | [Actions enabled](#enable-github-actions) | Settings → Actions → General | all workflows |
| 2 | [Actions workflow permissions](#actions-workflow-permissions) | Settings → Actions → General | release-please Release PRs |
| 3 | [GitHub Pages source](#github-pages) | Settings → Pages | Docusaurus docs site |
| 4 | [Branch protection on `main`](#branch-protection) | Settings → Branches (or Rules → Rulesets) | CI gate before merge |
| 5 | [Squash merge as default](#merge-settings) | Settings → General → Pull Requests | release-please changelog parsing |
| 6 | [Replace template identity](#replace-template-identity-in-your-repo) | [`template.repo.toml`](/getting-started/github-setup#replace-template-identity-in-your-repo) + `just template-apply` | correct Pages URL and links |
| 7 | [Workflows present in repo](#workflows-inventory) | `.github/workflows/` (committed) | automation itself |

After GitHub settings, follow [Releases](/getting-started/releases) for the first automated GitHub Release.

## Using the template

1. Open [CAD-as-Code-Template](https://github.com/Coffee2Bits/CAD-as-Code-Template) on GitHub → [**Use this template**](https://github.com/Coffee2Bits/CAD-as-Code-Template/generate) → **Create a new repository** (pick visibility and name; **`main` only** is enough).
2. **Clone** your new repo (HTTPS or SSH) and complete [Quick start](/getting-started/quick-start) in a Dev Container.
3. Work through the [setup checklist](#setup-checklist) on **your** repository — GitHub settings are per-repo and are **not** copied from the template.
4. Edit [`template.repo.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/template.repo.toml) for your org/repo, then run `just template-apply` — see [Replace template identity](#replace-template-identity-in-your-repo).
5. Merge a `feat:` or `fix:` PR, then follow [First release](/getting-started/releases#first-release-on-a-new-repository).

### Fork vs template

| Approach | When to use | GitHub setup |
|----------|-------------|--------------|
| **Use this template** | New product or lab repo under your org | Full checklist on **your** new repo |
| **Fork** | Contributing changes back to [Coffee2Bits/CAD-as-Code-Template](https://github.com/Coffee2Bits/CAD-as-Code-Template) | Usually skip release automation on the fork; use upstream's releases |
| **Fork** as a starting point | You want git history from the template but a separate remote | Rename remote, [replace template identity](#replace-template-identity-in-your-repo), then full checklist on the fork |

### Replace template identity in your repo

Your new repository is a copy of the template — it still contains upstream names until you rebrand it. CI workflows use `${{ github.repository }}` — **no edits** under [`.github/workflows/`](https://github.com/Coffee2Bits/CAD-as-Code-Template/tree/main/.github/workflows).

Edit **one config file** at the repo root, then apply:

```bash
# 1. Edit template.repo.toml (github owner/repo, Pages URL, docs title, package name)
# 2. Propagate to Docusaurus, README, docs cross-links, pyproject.toml
just template-apply
```

Preview without writing: `just template-apply-dry-run`

#### `template.repo.toml` fields

| Section | Keys | Purpose |
|---------|------|---------|
| `[github]` | `owner`, `repo` | GitHub org/user and repository name |
| `[pages]` | `url` | GitHub Pages host (usually `https://<owner>.github.io`) |
| `[docs]` | `title`, `navbar_title`, `tagline` | Docusaurus site branding |
| `[python]` | `package_name` | `pyproject.toml` `[project] name` |
| `[copyright]` | `holder` | Docs footer copyright |

**Example** — repo `acme/widget-cad` at `https://acme.github.io/widget-cad/`:

```toml
[github]
owner = "acme"
repo = "widget-cad"

[pages]
url = "https://acme.github.io"

[docs]
title = "Widget CAD"
navbar_title = "Widget CAD"
tagline = "Parametric widgets in Python"

[python]
package_name = "widget-cad"

[copyright]
holder = "acme"
```

#### What `just template-apply` updates

| Output | Source |
|--------|--------|
| `website/repo-identity.ts` | Generated — imported by `website/docusaurus.config.ts` |
| `pyproject.toml` | `[project] name` from `[python] package_name` |
| README, docs pages, `AGENTS.md`, etc. | Replaces previous identity strings with values from `template.repo.toml` |
| README GitHub Pages badge | Regenerated between `<!-- template:pages-badge:* -->` markers — deployment shield + link to docs site |

You can re-run `just template-apply` after changing `template.repo.toml` (for example if you rename the repository again). Local state in `.template.repo.applied.json` (gitignored) keeps replacements idempotent.

`just release-notes` reads `owner/repo` from `template.repo.toml` by default — see [Releases local dry-run](/getting-started/releases#local-dry-run).

---

## Enable GitHub Actions

**Path:** Repository → **Settings** → **Actions** → **General**

| Option | Value |
|--------|-------|
| Actions permissions | **Allow all actions and reusable workflows** (default) or allow listed actions your org permits |
| Workflow permissions | See [next section](#actions-workflow-permissions) |

Forks and new template repos sometimes inherit org policies that restrict Actions. If the **Actions** tab shows no runs, confirm Actions are allowed for this repository.

Direct link: `https://github.com/YOUR_ORG/YOUR_REPO/settings/actions`

---

## Customize after clone

1. Edit [`template.repo.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/template.repo.toml) and run `just template-apply` — see [Replace template identity](#replace-template-identity-in-your-repo).
2. Commit the updated files and push to `main`.
3. Enable [GitHub Pages](#github-pages) (Actions source) if you have not already.

Release automation ([`release-please.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/release-please.yml), [`release.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/release.yml)) does **not** need hardcoded owner/repo — assets and notes use the repository that runs the workflow.

---

## Actions workflow permissions

**Path:** Repository → **Settings** → **Actions** → **General** → **Workflow permissions**

| Option | Value |
|--------|-------|
| Workflow permissions | **Read and write permissions** |
| Allow GitHub Actions to create and approve pull requests | **Enabled** |

### Why

[release-please](https://github.com/googleapis/release-please) ([`.github/workflows/release-please.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/release-please.yml)) must:

- Open and update **Release PRs** (`pull-requests: write`)
- Commit version bumps to branches (`contents: write`)
- Create GitHub **Releases** and upload STL/PNG assets after a merged Release PR

Without repo-level read/write + PR approval, the workflow fails when creating the release branch or PR.

### Workflow-level permissions (committed)

Some workflows also declare job permissions explicitly:

| Workflow | Job permissions |
|----------|-----------------|
| `release-please.yml` | `contents: write`, `pull-requests: write`, `issues: write`, `workflows: write`, `actions: read` |
| `release.yml` | `contents: write`, `workflows: write`, `actions: read` (release job only) |

`workflows: write` is required when a release targets a commit that changed files under `.github/workflows/` — without it, `create-a-release` returns **Resource not accessible by integration** even when repo Settings → Actions → General is set to read/write. See [GitHub CLI issue #9514](https://github.com/cli/cli/issues/9514).
| `docs.yml` | `contents: read`, `pages: write`, `id-token: write` |
| `ci.yml` | Default `GITHUB_TOKEN` (read) |

Direct link (replace owner/repo): `https://github.com/YOUR_ORG/YOUR_REPO/settings/actions`

---

## GitHub Pages

**Path:** Repository → **Settings** → **Pages**

| Option | Value |
|--------|-------|
| **Build and deployment → Source** | **GitHub Actions** |

Do **not** use “Deploy from a branch” (`gh-pages`). The site is built by [`.github/workflows/docs.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/docs.yml) and published with `actions/deploy-pages`.

### Published URL

For a **project site** (repo name `CAD-as-Code-Template`):

`https://YOUR_ORG.github.io/CAD-as-Code-Template/`

Derived from `[github] repo` in [`template.repo.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/template.repo.toml) (`baseUrl: '/CAD-as-Code-Template/'` in the upstream template). Run `just template-apply` after editing — see [Replace template identity](#replace-template-identity-in-your-repo).

### `github-pages` environment

The deploy job uses the **`github-pages`** environment. On first deploy, GitHub may prompt you to approve environment creation — accept it. No environment secrets are required for public template repos.

### Trigger

Docs deploy on push to `main` when `website/**` or `.github/workflows/docs.yml` changes. PRs run [docs-pr.yml](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/docs-pr.yml) (build only, no deploy).

Direct link: `https://github.com/YOUR_ORG/YOUR_REPO/settings/pages`

---

## Branch protection

**Path:** Repository → **Settings** → **Branches** → **Branch protection rules**  
(or **Rules** → **Rulesets** if your org uses rulesets)

Apply to branch: **`main`**

### Recommended rules

| Rule | Setting | Why |
|------|---------|-----|
| Require a pull request before merging | Enabled | Keeps `main` stable; pairs with CI |
| Required status checks | **`Dagger CI`** (required) | Matches job name in `ci.yml` |
| | **`build`** from Documentation PR check (optional) | When changing `website/` — job name in `docs-pr.yml` |
| Require branches to be up to date before merging | Enabled (recommended) | Avoid merging stale green PRs |
| Require conversation resolution | Enabled (recommended) | Review hygiene |
| Require linear history | Optional | Complements squash-only merge |
| Do not allow bypassing the above settings | Your choice | Stricter for shared repos |
| Restrict who can push to matching branches | Optional | Prevent direct pushes to `main` |
| Allow force pushes | **Disabled** | Protect release history |
| Allow deletions | **Disabled** | Protect `main` |

### Status check names

GitHub shows exact check names on a merged PR’s **Checks** tab. If protection does not list **Dagger CI**, open a PR, wait for CI, then pick the check from the dropdown when editing the rule.

`ci.yml` path filters — CI runs only when these paths change:

- `cad/**`, `tests/**`, `ci/**`, `.github/workflows/**`, `pyproject.toml`, `uv.lock`, `.makerrepo/**`

Docs-only or README-only PRs may not run Dagger CI; that is intentional.

Direct link: `https://github.com/YOUR_ORG/YOUR_REPO/settings/branches`

---

## Merge settings

**Path:** Repository → **Settings** → **General** → **Pull Requests**

| Option | Value |
|--------|-------|
| Allow squash merging | **Enabled** |
| Allow merge commits | Disabled (recommended) |
| Allow rebase merging | Disabled (optional) |
| Default merge method | **Squash** |

### Why squash

release-please parses the **squash commit subject** on `main` (e.g. `feat(sphere): add label`). Merge commits make changelog and version detection unreliable.

Release PRs use subject pattern `chore: release X.Y.Z` — detected in `release-please.yml` to publish GitHub Release assets.

---

## Workflows inventory

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| [`ci.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/ci.yml) | PR + push to `main` (path filters) | Dagger `check`: lint, artifact smoke, pytest |
| [`release-please.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/release-please.yml) | Push to `main` | Open/update Release PR; on merged `chore: release …`, tag + release assets |
| [`release.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/release.yml) | Push tag `v*.*.*` | Manual tag fallback: quality gate + release assets |
| [`docs.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/docs.yml) | Push to `main` (`website/**`) | Build + deploy Docusaurus to Pages |
| [`docs-pr.yml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/workflows/docs-pr.yml) | PR to `main` (`website/**`) | Verify docs build |

No repository secrets are required for these workflows — they use `GITHUB_TOKEN` and Dagger against the repo source.

### Release automation config (in git)

| File | Role |
|------|------|
| [`release-please-config.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/release-please-config.json) | Semver + changelog for Python package |
| [`.release-please-manifest.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.release-please-manifest.json) | Current version pointer |

---

## Verification

After configuration:

1. Open a test PR → confirm **Dagger CI** runs (touch `cad/` or `tests/`).
2. Merge with a `feat:` or `fix:` squash title → confirm release-please opens or updates a Release PR.
3. Merge the Release PR → confirm a **GitHub Release** with STL/PNG assets ([releases guide](/getting-started/releases#first-release-on-a-new-repository)).
4. Push a change under `website/` → confirm **Deploy documentation** succeeds; site loads at your Pages URL.
5. Repository → **Settings** → **Actions** → **General** — confirm read/write + PR checkbox.

## Troubleshooting

| Symptom | Likely fix |
|---------|------------|
| release-please does not open Release PR | Workflow permissions (read/write + allow PRs) |
| Release PR merge does not create GitHub Release | Squash title must be `chore: release X.Y.Z`; check workflow run on `main` |
| Docs site 404 | Pages source must be **GitHub Actions**; wait for first `docs.yml` deploy |
| Cannot merge PR — missing check | Add **Dagger CI** to branch protection; or push a commit that triggers `ci.yml` paths |
| Wrong docs URL | Fix `[github] repo` and `[pages] url` in `template.repo.toml`, then `just template-apply` |

## Related docs

- [Releases](/getting-started/releases) — first release and day-to-day versioning
- [Releases workflow](/workflows/releases) — deeper reference (Conventional Commits, dry-run, manual tags)
- [CI & Dagger](/workflows/ci-and-dagger)
- [Documentation site](/) (local: `just docs-build`)

**In-repo copy:** [`.github/GITHUB_SETUP.md`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.github/GITHUB_SETUP.md)
