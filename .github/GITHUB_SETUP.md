# Set up GitHub for your repository

One-time GitHub.com settings for repos created from **CAD-as-Code-Template**. These settings are not stored in git and are not applied by `just init`.

Create and initialize the repo first:
https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/template-and-init

Full GitHub setup guide:
https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/github-setup

Releases:
https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/releases

## Quick checklist

| Setting | Location | Value |
|---------|----------|-------|
| Actions enabled | Settings → Actions → General | Allow workflows for this repo |
| Workflow permissions | Settings → Actions → General | **Read and write** + **Allow GitHub Actions to create and approve pull requests** |
| GitHub Pages | Settings → Pages | Source: **GitHub Actions** |
| Branch protection | Settings → Branches | Protect `main`; require **Dagger CI** when CAD/code paths should gate merges |
| Merge method | Settings → General → Pull Requests | **Squash** default; disable merge commits if possible |

## Workflow order

1. Create the repo from the template.
2. Run `just init` or `just init --owner OWNER --repo REPO` in your generated repo.
3. Configure the GitHub settings above.
4. Merge a `feat:` or `fix:` PR.
5. Merge the Release PR to publish generated STL/PNG assets.

## Workflows committed by the template

- `ci.yml` — Dagger lint + artifact smoke + pytest
- `release-please.yml` — opens Release PRs and creates release tags
- `release.yml` — tag-triggered quality gate, export, and GitHub Release publishing
- `docs.yml` — deploys Docusaurus to Pages
- `docs-pr.yml` — verifies docs builds on PRs

See the full GitHub setup guide for links, status check names, and verification steps.

## GitHub CLI in the dev container

The dev container includes **`gh`**. In Codespaces it is pre-authenticated; locally run `gh auth login` once. See the dev container GitHub CLI guide and the releases guide for common commands.
