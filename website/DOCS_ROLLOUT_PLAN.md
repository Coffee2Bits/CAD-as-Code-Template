# Documentation cleanup backlog

This file is the current docs backlog for agents and humans. The original rollout checklist was useful while the Docusaurus site was being created, but most scaffold work is now complete. Treat this file as the active source for remaining docs cleanup work.

## Current direction

The documentation should follow an iceberg shape:

1. README sells the project, explains the CAD-as-Code idea, and gives the shortest start path.
2. Docs intro explains the concept and routes readers by intent.
3. Quick start gets users to a running model with clear success states.
4. Deeper docs cover modeling, export, automation, CI/CD pipeline, troubleshooting, and agent workflows.

Avoid duplicating whole sections across pages. Repeat only what helps a reader choose the next link.

## Guiding lights

- Write for readers who may not know software workflows, Dev Containers, CI/CD, linting, MCP, or parametric CAD-as-code.
- Treat CAD-as-Code as the core project identity. This is not only a turnkey AI CAD workspace; it is CAD treated as software.
- Explain why the non-CAD pieces exist: repeatability, review, tests, automation, release artifacts, and collaboration.
- Link heavily between README, docs pages, examples, troubleshooting, and external references.
- Keep prose direct. Avoid generic hype, padded summaries, and LLM-sounding section patterns.

## Completed scaffold

- Docusaurus site exists under `website/`.
- Sidebar is wired in `website/sidebars.ts`.
- GitHub Pages docs workflow exists.
- README links to the docs site.
- `cad_tooling/README.md` points to the docs site.
- Published docs URL: `https://coffee2bits.github.io/CAD-as-Code-Template/`.
- Docusaurus build has been verified locally.

## Active cleanup items

### 1. README as landing page

Status: in progress.

Goal: sales pitch → one-click get started → docs.

Acceptance:

- README explains CAD-as-Code in terms a non-software CAD user can follow.
- README does not try to be the full manual.
- Detailed setup, stack, workflow, and troubleshooting content links into docs.
- Screenshot, template link, docs link, and quick-start path are prominent.

### 2. Quick start as first success path

Status: in progress.

Goal: split cloud and local setup, then converge on the same first commands.

Acceptance:

- Codespaces path is clear.
- Local VS Code/Cursor + Dev Containers path is clear.
- `just test`, `just view`, and `just mr-artifacts` each include a success state.
- GitHub template setup is linked, not mixed into the first-run path.

### 3. Docs intro as concept map

Status: in progress.

Goal: make the docs homepage explain the approach and route readers deeper.

Acceptance:

- Intro is not a second README.
- It explains why CAD-as-Code includes software-style tooling.
- It preserves the architecture map.
- It links readers by intent: try, understand, build, automate, troubleshoot.

### 4. De-duplicate entry pages

Status: open.

Review these overlaps after the README/intro/quick-start pass:

- README vs `website/docs/intro.md`.
- README quick-start summary vs `website/docs/getting-started/quick-start.md`.
- Intro stack explanation vs individual tool pages.
- Agent notes in README/docs vs `AGENTS.md`.

Acceptance:

- Each page has a clear role.
- Repeated content is short and intentional.
- Long details have one canonical home.

### 5. Link and navigation pass

Status: open.

Acceptance:

- Every entry page links to the next deeper page.
- Important terms link to glossary/reference/tool pages when useful.
- Docusaurus build passes with broken links treated as errors.
- External links are kept where they help readers leave the repo for primary docs.

### 6. Dependency maintenance issue

Status: separate issue recommended.

`npm ci` previously reported audit findings in the docs dependencies. This should be tracked separately from prose and information-architecture cleanup.

Acceptance:

- Create or update a maintenance issue for the audit findings.
- Do not mix dependency upgrades into a focused docs rewrite PR unless the docs build requires it.

## Historical note

The prior phase-by-phase rollout checklist was replaced because it had become stale: many unchecked items were already implemented or intentionally superseded by Mermaid diagrams and existing pages. Future agents should work from the active cleanup items above instead of chasing old rollout tasks.
