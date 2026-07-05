# CAD-as-Code, in a box

<!-- template:pages-badge:start -->
[![Documentation](https://img.shields.io/github/deployments/Coffee2Bits/CAD-as-Code-Template/github-pages?label=docs)](https://coffee2bits.github.io/CAD-as-Code-Template/)
<!-- template:pages-badge:end -->

If you are new to software-style workflows, that is the point of this template: all of the tools and automation is here and configured so your CAD work is repeatable, inspectable, and automated so that you can focus on design and modeling.

This is a low-effort, turnkey workspace that packages up software tools and practices like linting, testing, containerized workspaces, and CI/CD pipeline practices to give you versioned source files, repeatable builds, tests, reviewable changes, and release artifacts with the benefits of automation.

This repo uses [Dev Containers](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/dev-container). On your own machine, install [Docker](https://www.docker.com/) or [Podman](https://podman.io/) and start it before you reopen the project in a container ([setup notes](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/dev-container#host-container-runtime)). [GitHub Codespaces](https://github.com/features/codespaces) and other [cloud workspaces](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/ide-and-workspaces#cloud-workspaces) run the container for you. See [quick start: local setup](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/quick-start#option-b-local-vs-code-or-cursor).

You write models in Python with [build123d](https://build123d.readthedocs.io/), preview them in the [OCP CAD Viewer](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/ocp-viewer), and run pytest before you merge. CI exports STEP, STL, and GLB and publishes releases.

Edit the code under `cad/`. Meshes, renders, and release bundles are generated from that source.



![Dev environment: VS Code-based IDE with build123d code, OCP CAD Viewer, and AI agent showing a parametric sphere with embossed text](website/static/img/repo_preview.png)
<small><em>The default workspace: source code, live model preview, and agent assistance sharing the same containerized CAD environment.</em></small>


![OCP CAD Viewer clip view: Z-axis section through the demo sphere showing the nut pocket and embedded hardware](website/static/img/ocp_clip_y_object_color_cap.png)
<small><em>A Z-axis section cut through the demo sphere, showing how the viewer exposes embedded hardware, pockets, and interior clearances.</em></small>

## Start here

- [Use this template](https://github.com/Coffee2Bits/CAD-as-Code-Template/generate) to create your own CAD repo.
- [Open the docs](https://coffee2bits.github.io/CAD-as-Code-Template/) for the full guide.
- [Follow the quick start](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/quick-start) if you want the shortest path from clone to working model.

## Why CAD-as-Code?

 Parametric CAD captures models as structured text, a perfect format for LLM agents to interact and reason with, but parametric CAD by itself can still be quite limiting and difficult to interact with, like OpenSCAD. We decided to take advantage of the build123d library and to give our parametric CAD the "as-Code" approach to improve the modeling functionality, to add AI agent feedback surfaces, and to automate the production and release of model artifacts. We're now able to use the same approaches for our models that make software projects reliable:

- [Source control tracks every change to the model.](https://github.com/Coffee2Bits/CAD-as-Code-Template/blame/main/cad/parts/sphere.py)
- Linting and type checks keep the codebase maintainable.
- [Tests to catch broken geometry are always being run.](https://github.com/Coffee2Bits/CAD-as-Code-Template/actions)
- The CI/CD pipeline runs the same checks locally and on GitHub.
- [Release jobs regenerate manufacturing artifacts from source.](https://github.com/Coffee2Bits/CAD-as-Code-Template/releases)
- Agents can inspect the code, run commands, and use viewer feedback without guessing at hidden CAD state.

This repo is not just a quick AI CAD sandbox. It is an opinionated starter kit for treating parametric CAD as a software project.

## What you get

- Python parametric CAD with [build123d](https://github.com/gumyr/build123d) on [Open CASCADE](https://coffee2bits.github.io/CAD-as-Code-Template/reference/open-cascade).
- A portable [Dev Container](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/dev-container) for VS Code, Cursor, Codespaces, and other compatible workspaces.
- Live model preview through [OCP CAD Viewer](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/ocp-viewer).
- Repeatable commands through [just](https://coffee2bits.github.io/CAD-as-Code-Template/tools/just).
- Geometry tests, linting, type checks, and dead-code detection.
- STEP, STL, GLB, and release artifact workflows.
- [MakerRepo](https://coffee2bits.github.io/CAD-as-Code-Template/tools/makerrepo) decorators and CLI support for artifact discovery and export.
- [Dagger + GitHub Actions](https://coffee2bits.github.io/CAD-as-Code-Template/workflows/ci-and-dagger) for a portable CI/CD pipeline.
- Agent-ready hooks through [MCP servers](https://coffee2bits.github.io/CAD-as-Code-Template/tools/mcp-servers) inside the container.

## One-click get started

Fastest path:

1. Click [Use this template](https://github.com/Coffee2Bits/CAD-as-Code-Template/generate).
2. Open the repo in GitHub Codespaces, VS Code, Cursor, or another [Dev Containers-compatible workspace](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/ide-and-workspaces).
3. Let the container build. Dependencies and local docs start automatically.
4. Run the first checks:

```bash
just test
just view
just mr-artifacts
```

What should happen:

- `just test` runs the Python test suite.
- `just view` opens the demo sphere in the OCP CAD Viewer.
- `just mr-artifacts` lists the exportable MakerRepo artifacts.

**Cursor and some other VS Code forks:** install OCP CAD Viewer from the patched VSIX at the workspace root: **F1** → **Install from VSIX** → `ocp-cad-viewer-3.4.0.vsix`. See [OCP CAD Viewer setup](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/ocp-viewer#manual-vsix-install-cursor-and-other-forks).

Full setup, container runtime notes, MCP, and first-release setup: [quick start](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/quick-start).

## Where to go next

- [Quick start](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/quick-start): open the workspace, run the model, export artifacts.
- [Project layout](https://coffee2bits.github.io/CAD-as-Code-Template/getting-started/project-layout): where models, tests, tooling, and docs live.
- [Modeling conventions](https://coffee2bits.github.io/CAD-as-Code-Template/modeling/conventions): source-of-truth rules for `cad/`.
- [Parts and assemblies](https://coffee2bits.github.io/CAD-as-Code-Template/modeling/parts-and-assemblies): reusable parts and composed models.
- [Testing](https://coffee2bits.github.io/CAD-as-Code-Template/modeling/testing): validate geometry instead of eyeballing every change.
- [Export and formats](https://coffee2bits.github.io/CAD-as-Code-Template/workflows/export-and-formats): STEP, STL, GLB, and release outputs.
- [CI/CD pipeline and Dagger](https://coffee2bits.github.io/CAD-as-Code-Template/workflows/ci-and-dagger): same pipeline locally and on GitHub Actions.
- [Troubleshooting](https://coffee2bits.github.io/CAD-as-Code-Template/troubleshooting/): container, viewer, export, and CI problems.

## Where this can go

The template starts small so the first model is easy to understand. The same workflow can grow into a much richer CAD automation stack:

- Topology optimization tools, such as [dl4to4ocp](https://github.com/yeicor-3d/dl4to4ocp/), wired into the same repeatable CI/CD pipeline.
- Manufacturing export profiles that tune the same model for different processes: tighter clearances for CNC machining, printer-specific margins for Bambu or Prusa workflows, and shop defaults that can be regenerated instead of edited by hand.
- Import helpers that turn STEP, STL, or other mesh references into reference objects for easier modeling.

These are deliberately future-facing. The point is to show that CAD-as-Code is not only a cleaner way to write one part; it is a path toward repeatable, reviewable, automated design systems.

## For agents

Agent-facing rules belong in [AGENTS.md](AGENTS.md). The short version: keep `cad/` as the source of truth, test geometry changes, visually verify models, and use docs links for 1st class project references.

## License

See [LICENSE](LICENSE).
