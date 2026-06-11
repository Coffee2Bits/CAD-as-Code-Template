---
sidebar_position: 3
---

# Glossary

| Term | Meaning |
|------|---------|
| **Builder** | `make_*()` function returning `Part`/`Compound` — pure geometry |
| **Artifact** | `@artifact` entry point — fixed default configuration for publish/export |
| **Generator** | `@customizable` entry point — parametric via Pydantic model |
| **Smoke export** | Discover all artifacts, export STEP + STL — CI gate |
| **Release bundle** | STL + PNG per artifact for GitHub Releases |
| **build123d** | Python CAD library on [Open CASCADE](/reference/open-cascade) |
| **OCCT** | Open CASCADE Technology — the C++ B-rep kernel under build123d |
| **OCP** | [Open CASCADE Python](https://github.com/CadQuery/OCP) bindings — visualization and export |
| **MakerRepo** | Decorators + CLI for manufacturing-as-code metadata |
