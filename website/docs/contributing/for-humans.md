---
sidebar_position: 1
---

# Contributing

This template treats parametric CAD like software. A good contribution should leave the model, generated artifacts, and documentation in a state that another person can reproduce from source.

You do not need to be a CI/CD pipeline expert to contribute. Use the project commands, keep the change small, and make the pull request easy to review.

## Start from a focused change

Before editing, decide what kind of change you are making:

| Change | Start here | Run before opening a PR |
| --- | --- | --- |
| CAD geometry, parameters, or assemblies | [Parts and assemblies](/modeling/parts-and-assemblies), [Testing CAD models](/modeling/testing) | `just quality`, then `just view` for visual review |
| Export behavior or release artifacts | [Export and formats](/workflows/export-and-formats), [MakerRepo](/tools/makerrepo) | `just quality`, `just export-smoke` |
| Tooling, `justfile`, or quality checks | [uv and quality tools](/tools/uv-and-quality), [Just commands](/tools/just) | `just ci` |
| GitHub Actions, Dagger, or publishing | [CI/CD pipeline and Dagger](/workflows/ci-and-dagger), [Releases](/workflows/releases) | `just ci` |
| Documentation only | The page you are changing, plus nearby linked pages | `just docs-build` |

Small PRs are easier to review. Keep each one focused on a single model change, workflow change, or docs cleanup.

## Local checks

Run the fast gate for normal work:

```bash
just quality
```

That checks formatting, linting, type hints, dead code, and tests. If you changed model geometry, also open the viewer:

```bash
just view
```

If you changed export registration or artifact generation, run the export smoke check:

```bash
just export-smoke
```

If you changed broad behavior, project commands, dependencies, or the CI/CD pipeline, run the full local gate:

```bash
just ci
```

See [uv and quality tools](/tools/uv-and-quality) for what each check proves and how to fix common failures.

## Keep CAD changes reviewable

A CAD-as-Code PR should explain the design change and show that it still builds from source.

When relevant, include:

- the part or assembly you changed
- the parameter or dimension you intended to change
- screenshots from `just view` or generated preview images
- the commands you ran
- any export artifacts that should change

Avoid hand-editing generated files unless the docs for that workflow explicitly say to do so. The source model should remain the thing reviewers reason about.

## Keep documentation in sync

If you change behavior, update the docs in the same PR. Common examples:

- new or renamed `just` commands
- changed export formats or artifact names
- new workflow requirements
- GitHub Actions or release behavior changes
- model conventions or project layout changes

Useful places to check:

- [Quick start](/getting-started/quick-start)
- [Project layout](/getting-started/project-layout)
- [Daily development](/workflows/daily-development)
- [uv and quality tools](/tools/uv-and-quality)
- [Glossary](/reference/glossary)

Keep the docs layered. The README should sell the project and route people to the first step. The docs intro should map the system. Deeper pages should hold the technical detail.

## Commits and pull requests

Use [Conventional Commits](https://www.conventionalcommits.org/) for commit titles:

```text
feat: add adjustable bracket width
fix: correct enclosure wall clearance
docs: clarify release setup
deps: update docs dependencies
```

Before opening a PR:

1. Rebase or merge the latest `main`.
2. Run the checks that match your change.
3. Review your own diff for generated files, stale links, and accidental formatting churn.
4. Write a short PR description with the goal, the important changes, and the checks you ran.

PRs are squash-merged to `main`, so a clean final PR title matters more than a long commit stack.

## Documentation preview

For docs changes, run the site locally:

```bash
just docs-install
just docs-start
```

Before handing the PR off, build it:

```bash
just docs-build
```

A docs build can surface broken links and Mermaid syntax problems that are easy to miss in plain Markdown.

## When something fails

Do not work around a failing check by deleting the check or weakening the command. Fix the model, test, export registration, or documentation that caused the failure.

Start with the focused troubleshooting pages:

- [Export and CI/CD pipeline troubleshooting](/troubleshooting/export-and-ci)
- [Dagger and Docker troubleshooting](/troubleshooting/dagger-and-docker)
- [Dev Container troubleshooting](/troubleshooting/dev-container)
- [OCP viewer troubleshooting](/troubleshooting/ocp-viewer)

If the failure points to unfamiliar software terms, check the [glossary](/reference/glossary) first.
