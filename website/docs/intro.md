---
slug: /
sidebar_position: 1
title: Introduction
---

# CAD-as-Code, in a box

A turnkey workspace for **parametric CAD in Python**. Reopen this repo in any **Dev Containers–capable editor or cloud workspace** — [VS Code](https://code.visualstudio.com/), [Cursor](https://cursor.com/), [GitHub Codespaces](https://github.com/features/codespaces), [GitHub Copilot](https://github.com/features/copilot) in VS Code, and [many other clients](/getting-started/ide-and-workspaces) — and you get a complete modeling environment: IDE, live 3D viewer, automated tests, export tooling, and CI, already wired together.

Define geometry with [build123d](https://build123d.readthedocs.io/), preview it in the [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer), validate with pytest, and export to STEP, STL, and GLB. Publish artifacts through [MakerRepo](https://docs.makerrepo.com/makerrepo-library/) (`mr`). Python is the source of truth; mesh files are generated, not hand-edited.

![Dev environment with build123d code, OCP CAD Viewer, and a parametric sphere](/img/repo_preview.png)

## What's in the box

| Layer | What you get |
|-------|--------------|
| **IDE** | Dev container (`.devcontainer/`) — portable across [VS Code, Cursor, Codespaces, Copilot, and more](/getting-started/ide-and-workspaces); dependencies and docs site (port 3000) start on container start |
| **Modeling** | build123d parts and assemblies under `cad/` |
| **Visualization** | OCP CAD Viewer + `ocp-vscode` bridge for `show_object` |
| **Quality** | pytest geometry tests, ruff, mypy |
| **Make** | [just](https://github.com/casey/just) command runner (`justfile`) for dev, export, and CI |
| **CI** | [Dagger](https://dagger.io/) — portable CI from local to GitHub Actions |
| **Agents** | AI coding assistants — Cursor, VS Code, Claude, GitHub Copilot |
| **MCP** | Agent tools in the dev container ([build123d-mcp](/tools/mcp-servers), [ocp-viewer-mcp](/tools/mcp-servers)) — `uv sync` + committed launchers; IDE connects via [`.cursor/mcp.json`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/.cursor/mcp.json) |
| **Publish** | MakerRepo decorators and `mr` CLI for artifact discovery and export |

## Stack architecture

**Source of truth** is always Python model code in `cad/` (the **CAD/** tree) — parametric code that generates models. **AI agents** (Cursor, VS Code, Claude, GitHub Copilot) work in the IDE like any developer. **MCP servers** run in the dev container and give agents tools to execute geometry, measure results, and capture viewer screenshots — without replacing the code artifacts under version control.

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
    CAD_SRC["CAD/ Python code"]
    B123D["build123d on Open CASCADE"]
  end

  subgraph viz["Visualization"]
    OCP["OCP CAD Viewer"]
    BRIDGE["ocp-vscode"]
  end

  subgraph quality["Quality"]
    PYTEST["pytest"]
    RUFF["ruff + mypy"]
  end

  subgraph make["Make"]
    JUST["just"]
    UV["uv"]
  end

  subgraph ci["CI"]
    DAGGER["Dagger"]
    GHA["GitHub Actions"]
  end

  subgraph publish["Publish"]
    MR["MakerRepo"]
    MRCLI["mr CLI"]
    REL["GitHub Releases"]
  end

  agents --> ide
  agents -.->|"optional, alongside code"| mcp
  ide --> CAD_SRC
  mcp -.->|"access to artifacts"| CAD_SRC
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
| [build123d](https://github.com/gumyr/build123d) | Parametric CAD-as-code on [Open CASCADE](/reference/open-cascade) |
| [OCP CAD Viewer](https://github.com/bernhard-42/vscode-ocp-cad-viewer) | Live 3D visualization in VS Code-based IDEs |
| [ocp-vscode](https://github.com/bernhard-42/ocp_vscode) | Python bridge for `show_object` |
| [uv](https://docs.astral.sh/uv/) | Dependency and virtualenv management |
| [just](https://github.com/casey/just) | Command runner for dev, export, and CI |
| [pytest](https://docs.pytest.org/) | Geometry and export tests |
| [ruff](https://docs.astral.sh/ruff/) / [mypy](https://mypy-lang.org/) | Linting and type checking |
| [Dagger](https://dagger.io/) | Portable CI pipeline |
| [build123d-mcp](https://github.com/pzfreo/build123d-mcp) | MCP interface — sandboxed geometry execution for agents |
| [ocp-viewer-mcp](https://github.com/dmilad/ocp-viewer-mcp) | MCP interface — viewer screenshots for agent visual feedback |
| [MakerRepo](https://docs.makerrepo.com/makerrepo-library/) | `@artifact`, `@customizable`, `@cached` decorators |
| [makerrepo-cli](https://docs.makerrepo.com/makerrepo-cli/) | Artifact discovery, export, and viewer integration |

## New repo from the template?

If you used **[Use this template](https://github.com/Coffee2Bits/CAD-as-Code-Template/generate)** on GitHub:

1. Edit [`template.repo.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/template.repo.toml) for your org, repo name, and Pages URL.
2. Run `just template-apply` to update the docs site, README links, and `pyproject.toml`.
3. Complete [Set up GitHub](/getting-started/github-setup) (Actions permissions, Pages, branch protection) and [Releases](/getting-started/releases).

Details: [Replace template identity](/getting-started/github-setup#replace-template-identity-in-your-repo).

## Explore the docs

| | |
|---|---|
| **Getting started** | [Quick start](/getting-started/quick-start) · [GitHub setup](/getting-started/github-setup) · [Releases](/getting-started/releases) · [Project layout](/getting-started/project-layout) · [IDEs & workspaces](/getting-started/ide-and-workspaces) |
| **Modeling** | [Conventions](/modeling/conventions) · [Parts & assemblies](/modeling/parts-and-assemblies) · [Testing](/modeling/testing) |
| **Tools** | [just](/tools/just) · [MakerRepo](/tools/makerrepo) · [MCP servers](/tools/mcp-servers) · [CAD tooling](/tools/cad-tooling/) |
| **Workflows** | [Daily development](/workflows/daily-development) · [CI & Dagger](/workflows/ci-and-dagger) · [Releases](/workflows/releases) |
| **Help** | [Troubleshooting](/troubleshooting/) · [Open CASCADE](/reference/open-cascade) · [For agents](/contributing/for-agents) |

**Repository:** [Coffee2Bits/CAD-as-Code-Template](https://github.com/Coffee2Bits/CAD-as-Code-Template)

## Roadmap

- Additional parts and real assemblies (constraints, patterns)
- [build123d part libraries](/modeling/external-libraries)
- [PartCAD](https://partcad.org/) integration
- Bill of materials (BOM) from assemblies
- 3MF, SVG, and DXF export helpers
- Golden STEP/STL fixtures under `tests/fixtures/`
- Topology optimization demo (e.g. [dl4to4ocp](https://github.com/yeicor-3d/dl4to4ocp/))
