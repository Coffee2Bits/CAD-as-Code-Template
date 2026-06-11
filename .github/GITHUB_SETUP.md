# Set up GitHub for your repository

One-time settings for **CAD-as-Code-Template** (and repos created from it). Configure these on GitHub.com — they are not stored in git.

**Full guide (checklist, fork vs template, customization, troubleshooting):**  
https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/github-setup

**Releases (first release + day-to-day versioning):**  
https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/releases

## Quick checklist

| Setting | Location | Value |
|---------|----------|-------|
| Actions enabled | Settings → Actions → General | Allow workflows for this repo |
| Workflow permissions | Settings → Actions → General | **Read and write** + **Allow GitHub Actions to create and approve pull requests** |
| GitHub Pages | Settings → Pages | Source: **GitHub Actions** |
| Branch protection | Settings → Branches | Protect `main`; require **Dagger CI** (optional: **build** for docs PRs) |
| Merge method | Settings → General → Pull Requests | **Squash** default; disable merge commits (recommended) |
| Template identity | `template.repo.toml` + `just template-apply` | Your org, repo name, Pages URL, docs title |

## Workflows (committed)

- `ci.yml` — Dagger lint + artifacts + test
- `release-please.yml` — Release PRs + publish on `chore: release X.Y.Z` merge
- `release.yml` — Manual tag `v*.*.*` fallback
- `docs.yml` — Deploy Docusaurus to Pages
- `docs-pr.yml` — Docs build on PRs

See the [full GitHub setup guide](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/github-setup) for links, status check names, and verification steps.
