---
sidebar_position: 6
title: Create and initialize your repository
---

# Create and initialize your repository

This page covers the part that happens before GitHub settings: make your own repository from the template, clone it, and replace the template identity with your project identity.

After this page, continue in order:

1. [Set up GitHub](/getting-started/github-setup) — Actions, Pages, branch protection, and merge settings.
2. [Releases](/getting-started/releases) — release-please and generated release artifacts.

## Use the template

Use this path for a new CAD project, product repo, lab repo, or internal part library.

1. Open [Coffee2Bits/CAD-as-Code-Template](https://github.com/Coffee2Bits/CAD-as-Code-Template).
2. Click [Use this template](https://github.com/Coffee2Bits/CAD-as-Code-Template/generate).
3. Choose your owner, repository name, and visibility.
4. Create the repository from the `main` branch.
5. Clone your new repository and open it in the [Dev Container](/getting-started/dev-container) or [Codespaces](/getting-started/quick-start#option-a-codespaces).

Success state: you have your own repository with the template files, and your editor terminal is running inside the container.

## Template or fork?

| Approach | Use it when | What to configure |
|----------|-------------|-------------------|
| Use this template | You are starting a new CAD project from this workspace | Run `just init`, then configure GitHub settings on the new repo |
| Fork to contribute upstream | You want to improve Coffee2Bits/CAD-as-Code-Template itself | Usually skip release automation on the fork; open PRs upstream |
| Fork as a product starting point | You want template history but a separate product repo | Rename/remap the remote, run `just init`, then configure GitHub settings on the fork |

Most users should choose Use this template.

## Replace the template identity

A generated repository still contains upstream names until you initialize it. `just init` reads `template.repo.toml`, updates project identity, and resets release state for your repo.

You have two options:

1. Edit `template.repo.toml`, then run `just init`.
2. Pass CLI overrides, such as `just init --owner acme --repo widget-cad`. Overrides are saved back to `template.repo.toml`.

```bash
# Use values from template.repo.toml:
just init

# Or set identity from the command line:
just init --owner acme --repo widget-cad

# Preview without writing files:
just init-dry-run

# Integration files only; skip README/docs markdown:
just init --no-sync-docs
```

After the first initialization, use `just template-apply` when `template.repo.toml` changes again. Use `just template-apply-integration` if you only want integration files updated.

:::warning Do not run init in the upstream template checkout
`just init` is for your generated repository. It rewrites identity, versions, docs, and release state. If you are contributing to the upstream template, test init behavior only through the functional tests or an isolated copy.
:::

## `template.repo.toml` fields

| Section | Keys | Purpose |
|---------|------|---------|
| `[github]` | `owner`, `repo` | GitHub org/user and repository name. These are the important required values. |
| `[pages]` | `url` | GitHub Pages host. Defaults to `https://<owner>.github.io`. |
| `[docs]` | `title`, `navbar_title`, `tagline`, `npm_package_name` | Docusaurus branding. Defaults are based on the repo name. |
| `[python]` | `package_name` | Python project name in `pyproject.toml`. Defaults to the repo name. |
| `[copyright]` | `holder` | Docs footer. Defaults to the GitHub owner. |
| `[init]` | `initial_version` | Starting semver for the generated repository. Defaults to `0.0.0`. |

Example for `acme/widget-cad` published at `https://acme.github.io/widget-cad/`:

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

## What `just init` updates

| Output | Source |
|--------|--------|
| `pyproject.toml` | Project name and initial version |
| `.release-please-manifest.json` | Current version pointer for release-please |
| `CHANGELOG.md` | Reset to a clean changelog header |
| `website/repo-identity.ts` | Generated identity imported by Docusaurus |
| `website/package.json` | Docs package name |
| `AGENTS.md` | Template identity strings |
| README and docs pages | Updated by default unless `--no-sync-docs` is used |
| `.github/GITHUB_SETUP.md` | Short in-repo GitHub setup pointer |

The embedded `cad_tooling/` library is never modified by `just init` or `just template-apply`.

## Commit the initialization

After `just init`:

```bash
git status --short
git diff --check
git add .
git commit -m "chore: initialize CAD workspace"
git push
```

Use whatever branch policy your repo requires. If this is a brand-new private repo with no branch protection yet, pushing the initialization commit to `main` is common. Once GitHub is configured, prefer pull requests for normal work.

## Next step

Continue to [Set up GitHub](/getting-started/github-setup). That page covers the GitHub.com settings that cannot be copied by the template or written by `just init`.
