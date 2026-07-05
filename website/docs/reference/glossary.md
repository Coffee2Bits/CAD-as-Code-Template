---
sidebar_position: 3
---

# Glossary

Short definitions for terms that show up across the template. These are intentionally brief. Follow the linked pages when you need setup steps or implementation details.

## CAD-as-Code

Parametric CAD treated like a software project. The model lives in readable source files, changes are reviewed in Git, checks run locally and in the CI/CD pipeline, and manufacturing artifacts are regenerated from source instead of hand-managed.

See [Modeling conventions](/modeling/conventions), [Testing strategy](/modeling/testing), and [CI/CD pipeline and Dagger](/workflows/ci-and-dagger).

## Source of truth

The file or directory that should be edited directly. In this template, source CAD belongs under `cad/`. STEP, STL, GLB, screenshots, and release bundles are generated outputs.

See [Project layout](/getting-started/project-layout) and [Export and formats](/workflows/export-and-formats).

## Dev Container

A containerized development environment that carries the project tools with the repo. It keeps Python, build123d, OCP viewer support, Node docs tooling, and command-line tools consistent across Codespaces, VS Code, Cursor, and compatible IDEs. On a laptop you need Docker or Podman; see [host container runtime](/getting-started/dev-container#host-container-runtime). Cloud hosts run the container for you.

See [Dev Container](/getting-started/dev-container) and [IDEs and workspaces](/getting-started/ide-and-workspaces).

## Builder

A `make_*()` function returning a build123d `Part` or `Compound`. Builders should be pure geometry: inputs in, CAD object out.

See [Parts and assemblies](/modeling/parts-and-assemblies).

## Artifact

A MakerRepo `@artifact` entry point with a fixed default configuration for publish and export workflows.

See [MakerRepo](/tools/makerrepo).

## Generator

A MakerRepo `@customizable` entry point that accepts parameters, usually through a Pydantic model.

See [MakerRepo](/tools/makerrepo).

## Smoke export

A quick export check that discovers artifacts and writes formats such as STEP and STL. It catches broken export paths before a release.

See [Export and formats](/workflows/export-and-formats) and [Export and CI/CD pipeline troubleshooting](/troubleshooting/export-and-ci).

## Release bundle

The generated files attached to a GitHub Release, such as STL and PNG outputs per artifact.

See [Releases](/workflows/releases).

## CI/CD pipeline

The repeatable automation that runs checks and publish steps outside a developer's editor. In this repo, Dagger provides the portable pipeline and GitHub Actions runs it on GitHub.

See [CI/CD pipeline and Dagger](/workflows/ci-and-dagger).

## Linting

Automated checks that flag code style, typing, and dead-code problems before they turn into harder-to-debug modeling issues.

See [uv and quality](/tools/uv-and-quality).

## MCP

Model Context Protocol. MCP servers give AI agents controlled tools for running geometry code and inspecting viewer feedback while the source files remain under version control.

See [MCP servers](/tools/mcp-servers).

## build123d

A Python CAD library built on Open CASCADE. The template uses build123d for parametric model code.

See [Open CASCADE](/reference/open-cascade) and the [build123d docs](https://build123d.readthedocs.io/).

## OCCT

Open CASCADE Technology, the C++ boundary-representation geometry kernel under build123d.

See [Open CASCADE](/reference/open-cascade).

## OCP

Open CASCADE Python bindings used for visualization and export.

See [OCP CAD Viewer](/getting-started/ocp-viewer) and [OCP on GitHub](https://github.com/CadQuery/OCP).

## MakerRepo

Decorators and CLI tools for discovering, describing, and exporting manufacturing artifacts from code.

See [MakerRepo](/tools/makerrepo).
