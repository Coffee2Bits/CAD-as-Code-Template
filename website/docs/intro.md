---
slug: /
sidebar_position: 1
title: Introduction
---

# CAD-as-Code, in a box

A turnkey workspace for [parametric CAD as software](/reference/glossary#cad-as-code). Reopen this repo in any Dev Containers-capable editor or cloud workspace — [VS Code](https://code.visualstudio.com/), [Cursor](https://cursor.com/), [GitHub Codespaces](https://github.com/features/codespaces), GitHub Copilot in VS Code, and [many other clients](/getting-started/ide-and-workspaces) — and you get a complete modeling environment: IDE, live 3D viewer, automated tests, export tooling, and a CI/CD pipeline already wired together.

Define geometry with [build123d](https://build123d.readthedocs.io/), preview it in the [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer), validate it with pytest and quality checks, then export STEP, STL, GLB, and release assets from the same source. Python in `cad/` is the [source of truth](/reference/glossary#source-of-truth); generated files are outputs, not files you hand-manage.

If you are new to software-style workflows, that is the point of the template: the non-CAD pieces are all here and configured so your CAD work is repeatable, inspectable, and automated so that you can focus on design and modeling. If a term is unfamiliar, start with the [glossary](/reference/glossary) and follow the linked guide from there.

![Dev environment with build123d code, OCP CAD Viewer, and a parametric sphere](/img/repo_preview.png)

## What's in the box

| Layer | What you get |
|-------|--------------|
| IDE | Dev container (`.devcontainer/`) for [VS Code, Cursor, Codespaces, Copilot, and more](/getting-started/ide-and-workspaces); dependencies and docs site start with the workspace |
| Modeling | build123d parts and assemblies under `cad/` |
| Visualization | OCP CAD Viewer plus the `ocp-vscode` bridge for `show_object` |
| Quality | pytest geometry tests, ruff, mypy, and vulture |
| Commands | [just](/tools/just) command runner for development, export, and CI/CD pipeline tasks |
| CI/CD pipeline | [Dagger](/workflows/ci-and-dagger) plus GitHub Actions for repeatable checks and releases |
| Agents | AI coding assistants such as Cursor, VS Code, Claude, and GitHub Copilot |
| MCP | Agent tools in the dev container: [build123d-mcp](/tools/mcp-servers) and [ocp-viewer-mcp](/tools/mcp-servers) |
| Publish | [MakerRepo](/tools/makerrepo) decorators and `mr` CLI for artifact discovery and export |

## Stack architecture

The source of truth is always Python model code in `cad/`. AI agents and MCP servers can help inspect, execute, and view the model, but they do not replace the files under version control. The CI/CD pipeline and release tooling regenerate outputs from that source so changes can be reviewed instead of guessed at.

```mermaid
flowchart TB
  subgraph agents["AI coding agents"]
    CURSOR["Cursor"]
    VSCODE["VS Code"]
    CLAUDE["Claude"]
    COPILOT["GitHub Copilot"]
  end

  subgraph ide["Dev environment"]
    DC["Dev container"]
  end

  subgraph mcp["MCP — agent interface surface"]
    B123MCP["build123d-mcp"]
    OCPMCP["ocp-viewer-mcp"]
  end

  subgraph model["Modeling — source of truth"]
    CAD_SRC["cad/ Python code"]
    B123D["build123d on Open CASCADE"]
  end

  subgraph viz["Visualization"]
    OCP["OCP CAD Viewer"]
    BRIDGE["ocp-vscode"]
  end

  subgraph quality["Quality"]
    PYTEST["pytest"]
    RUFF["ruff + mypy + vulture"]
  end

  subgraph make["Commands"]
    JUST["just"]
    UV["uv"]
  end

  subgraph pipeline["CI/CD pipeline"]
    DAGGER["Dagger"]
    GHA["GitHub Actions"]
  end

  subgraph publish["Publish"]
    MR["MakerRepo"]
    MRCLI["mr CLI"]
    REL["GitHub Releases"]
  end

  agents --> ide
  agents -.->|"optional tool access"| mcp
  ide --> CAD_SRC
  mcp -.->|"execute and inspect"| CAD_SRC
  mcp -.->|"viewer feedback"| OCP
  CAD_SRC --> B123D
  B123D --> OCP
  BRIDGE --> OCP
  CAD_SRC --> PYTEST
  JUST --> UV
  DAGGER --> GHA
  MR --> MRCLI
  MR --> REL
```

## Stack

| Tool | Role |
|------|------|
| [build123d](https://github.com/gumyr/build123d) | Parametric CAD-as-Code on [Open CASCADE](/reference/open-cascade) |
| [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer) | Live 3D visualization in VS Code-based IDEs |
| [ocp-vscode](https://github.com/bernhard-42/ocp_vscode) | Python bridge for `show_object` |
| [uv](https://docs.astral.sh/uv/) | Dependency and virtualenv management |
| [just](https://github.com/casey/just) | Command runner for development, export, and CI/CD pipeline tasks |
| [pytest](https://docs.pytest.org/) | Geometry and export tests |
| [ruff](https://docs.astral.sh/ruff/) / [mypy](https://mypy-lang.org/) / [vulture](https://github.com/jendrikseipp/vulture) | Linting, type checking, and dead-code detection |
| [Dagger](https://dagger.io/) | Portable CI/CD pipeline from local runs to GitHub Actions |
| [build123d-mcp](https://github.com/pzfreo/build123d-mcp) | MCP interface for sandboxed geometry execution by agents |
| [ocp-viewer-mcp](https://github.com/dmilad/ocp-viewer-mcp) | MCP interface for viewer screenshots and visual feedback |
| [MakerRepo](https://docs.makerrepo.com/makerrepo-library/) | `@artifact`, `@customizable`, and `@cached` decorators |
| [makerrepo-cli](https://docs.makerrepo.com/makerrepo-cli/) | Artifact discovery, export, and viewer integration |

## New repo from the template?

If you used [Use this template](https://github.com/Coffee2Bits/CAD-as-Code-Template/generate):

1. Edit [`template.repo.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/template.repo.toml), then run `just init`.
2. Complete [Set up GitHub](/getting-started/github-setup) for Actions, Pages, branch protection, and release settings.
3. Read [Releases](/getting-started/releases) before publishing generated assets.

Details: [Replace template identity](/getting-started/github-setup#replace-template-identity-in-your-repo).

## Explore the docs

| Area | Start here |
|------|------------|
| Getting started | [Quick start](/getting-started/quick-start) · [GitHub setup](/getting-started/github-setup) · [Releases](/getting-started/releases) · [Project layout](/getting-started/project-layout) · [IDEs and workspaces](/getting-started/ide-and-workspaces) |
| Modeling | [Conventions](/modeling/conventions) · [Parts and assemblies](/modeling/parts-and-assemblies) · [Testing](/modeling/testing) · [External libraries](/modeling/external-libraries) |
| Tools | [just](/tools/just) · [uv and quality](/tools/uv-and-quality) · [MakerRepo](/tools/makerrepo) · [MCP servers](/tools/mcp-servers) · [CAD tooling](/tools/cad-tooling/) |
| Workflows | [Daily development](/workflows/daily-development) · [Export and formats](/workflows/export-and-formats) · [CI/CD pipeline and Dagger](/workflows/ci-and-dagger) · [Releases](/workflows/releases) |
| Reference and help | [Glossary](/reference/glossary) · [Troubleshooting](/troubleshooting/) · [Open CASCADE](/reference/open-cascade) · [For agents](/contributing/for-agents) |

## Roadmap

- Additional parts and real assemblies: constraints, patterns, and reusable project structure.
- [build123d part libraries](/modeling/external-libraries) and [PartCAD](https://partcad.org/) integration.
- Bills of materials from assemblies.
- 3MF, SVG, and DXF export helpers.
- Golden STEP/STL fixtures under `tests/fixtures/`.
- Topology optimization demos, for example [dl4to4ocp](https://github.com/yeicor-3d/dl4to4ocp/).

## Repository

[Coffee2Bits/CAD-as-Code-Template](https://github.com/Coffee2Bits/CAD-as-Code-Template)
