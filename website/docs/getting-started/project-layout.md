---
sidebar_position: 5
---

# Project layout

```text
.
├── template.repo.toml            # Org/repo identity — edit after "Use this template", then just init
├── AGENTS.md                     # Agent conventions
├── README.md                     # Template landing page
├── .cursor/                      # MCP wiring (IDE → in-container servers)
├── .makerrepo/config.yaml        # MakerRepo defaults
├── .github/
│   ├── GITHUB_SETUP.md           # One-time GitHub.com settings (branch protection, Pages, …)
│   └── workflows/                # CI, release, docs
├── ci/                           # Dagger module
├── .devcontainer/                # Dev container + OCP VSIX install
├── cad/
│   ├── parts/                    # Reusable parametric parts
│   └── assemblies/               # Composed products
├── cad_tooling/                  # Export, render, release helpers
├── justfile                      # Dev, export, CI commands
├── main.py                       # Viewer entry (not model logic)
├── tests/                        # CAD model tests
└── cad_tooling_tests/            # Tooling unit tests
```

## Directory responsibilities

| Path | Purpose |
|------|---------|
| `cad/parts/` | Single reusable components; builders + MR decorators |
| `cad/assemblies/` | Products composed from parts; placement and patterns |
| `cad_tooling/` | Export, headless render, release notes |
| `main.py` | Thin viewer demo — import builders, call `show_object` |
| `tests/` | Geometry, export, MakerRepo discovery tests |

## Where to add code

- **New reusable part** → `cad/parts/<name>.py`
- **New product** → `cad/assemblies/<name>.py` (import from `cad.parts`)
- **Export/CI helper** → `cad_tooling/` (not in `cad/`)

See [Parts & assemblies](/modeling/parts-and-assemblies) for the three-layer pattern.

## After cloning from the template

| Task | Guide |
|------|-------|
| One-time GitHub.com settings | [Set up GitHub](/getting-started/github-setup) |
| First GitHub Release | [Releases](/getting-started/releases) |
| Rename repo / fix docs URL | Edit `template.repo.toml`, then `just init` or `just template-apply` — [Replace template identity](/getting-started/github-setup#replace-template-identity-in-your-repo) |
