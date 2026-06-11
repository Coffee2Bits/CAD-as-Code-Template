# Documentation rollout plan (Docusaurus)

**Status tracker for agents and humans.** Work phases in order. Mark `[x]` when done.

| Item | Value |
|------|-------|
| Repo | `Coffee2Bits/CAD-as-Code-Template` |
| Site URL | `https://coffee2bits.github.io/CAD-as-Code-Template/` |
| Stack | Docusaurus 3.x, TypeScript config, Mermaid theme |
| Source branch | `main` (build + deploy on push) |
| Content root | `website/docs/` |
| Agent rules | [`AGENTS.md`](../AGENTS.md#documentation-docusaurus--github-pages) |

---

## Phase 0 — Scaffold (do first)

- [x] **0.1** Run `npx create-docusaurus@latest website classic --typescript` *into existing* `website/` or merge manually if folder already exists
- [x] **0.2** Set `docusaurus.config.ts`:
  - `url: 'https://coffee2bits.github.io'`
  - `baseUrl: '/CAD-as-Code-Template/'`
  - `organizationName: 'Coffee2Bits'`
  - `projectName: 'CAD-as-Code-Template'`
  - `editUrl: 'https://github.com/Coffee2Bits/CAD-as-Code-Template/tree/main/website/'`
  - Enable `@docusaurus/theme-mermaid` in themes + `markdown.mermaid: true`
- [x] **0.3** Create `website/sidebars.ts` with placeholder sidebar matching structure below
- [x] **0.4** Add `website/.gitignore` entries: `node_modules/`, `build/`, `.docusaurus/`
- [x] **0.5** Add `just` recipes: `docs-install`, `docs-start`, `docs-build` (npm in `website/`)
- [x] **0.6** Add `.github/workflows/docs.yml` + `docs-pr.yml` — build on push to `main`, deploy via GitHub Actions Pages
- [x] **0.7** Document GitHub.com settings in `getting-started/github-setup.md` + `.github/GITHUB_SETUP.md` (Pages source: **GitHub Actions** — still a one-time manual step on GitHub)
- [x] **0.8** Add docs link to `README.md` (stack / what's-in-the-box retained)
- [x] **0.9** Verify `just docs-build` passes locally
- [ ] **0.9b** Merge to `main`; confirm site loads at published URL
- [x] **0.10** Shorten `cad_tooling/README.md` to pointer + link

**Phase 0 workflow file sketch:** see AGENTS.md and parent plan in chat; path filter `website/**`, `.github/workflows/docs.yml`.

---

## Phase 1 — Diagrams (`website/static/img/`)

Create before or alongside pages that reference them.

- [ ] **1.1** `stack-layers.svg` — optional; mermaid in `intro.md` covers this
- [ ] **1.2** `stack-data-flow.svg` — optional; mermaid in `export-and-formats.md`
- [ ] **1.3** `ci-pipeline.svg` — optional; mermaid in `ci-and-dagger.md`
- [ ] **1.4** `mcp-architecture.svg` — optional; mermaid in `mcp-servers.md`
- [ ] **1.5** `release-pipeline.svg` — optional; mermaid in `releases.md`
- [x] **1.6** Copy or reference `repo_preview.png` from repo root (`static/img/repo_preview.png`)

**Mermaid fallback:** embedded on intro, MCP, CI, releases, export, github-setup, open-cascade pages.

---

## Phase 2 — Page-by-page checklist

Each file: create MDX/markdown → add to `sidebars.ts` → run `npm run build` → check links → mark `[x]`.

### Home

#### `website/docs/intro.md` (slug: `/`)

- [ ] **2.1.1** Front matter: `sidebar_position: 1`, `slug: /`
- [ ] **2.1.2** Hero: turnkey template pitch (from README opening)
- [ ] **2.1.3** Embed `stack-layers.svg` + link to Stack reference
- [ ] **2.1.4** "What's in the box" table (from README)
- [ ] **2.1.5** Card grid / links: Quick start, Tools, Troubleshooting, Contributing
- [ ] **2.1.6** Short roadmap bullet list (from README future work)
- [ ] **2.1.7** Link to GitHub template repo (correct slug)

---

### Getting started (`website/docs/getting-started/`)

#### `quick-start.md`

- [ ] **2.2.1** Prerequisites: Dev Containers-capable IDE, Docker (for CI)
- [ ] **2.2.2** Steps 1–6 from README quick start (reopen container, sync, test, view, export, MCP reload)
- [ ] **2.2.3** "Next steps" links: dev-container, ocp-viewer, daily-development
- [ ] **2.2.4** Admonition: first container open may take several minutes

#### `dev-container.md`

- [ ] **2.2.5** What `.devcontainer/` provides (Open CASCADE parity with CI)
- [ ] **2.2.6** Lifecycle table: `onCreateCommand`, `postCreateCommand`, `postStartCommand` — quote from `devcontainer.json`
- [ ] **2.2.7** `just sync`, `just sync-frozen`, `just setup-hooks`
- [ ] **2.2.8** Docker socket mount for Dagger (`devcontainer.json` mounts)
- [ ] **2.2.9** Editor extensions: Python, Pylance, Ruff; format-on-save settings
- [ ] **2.2.10** Troubleshooting cross-link

#### `ocp-viewer.md`

- [ ] **2.2.11** VSIX not committed; download path `ocp-cad-viewer-3.4.0.vsix`
- [ ] **2.2.12** Cursor ESM / `proper-lockfile` patch explanation
- [ ] **2.2.13** Install flow: download → patch → `install-cli` → reload window → open panel → `just view`
- [ ] **2.2.14** Manual recovery commands from `install-ocp-cad-viewer.sh`
- [ ] **2.2.15** Screenshot or `repo_preview.png`

#### `github-setup.md`

- [x] **2.2.15b** GitHub.com checklist: workflow permissions, Pages, branch protection, squash merge
- [x] **2.2.15c** Workflows inventory + mermaid settings diagram
- [x] **2.2.15d** In-repo pointer `.github/GITHUB_SETUP.md`
- [x] **2.2.15e** Links from README, intro, quick-start, releases, troubleshooting

#### `project-layout.md`

- [ ] **2.2.16** Full directory tree from README
- [ ] **2.2.17** Directory responsibility table (from AGENTS.md, human tone)
- [ ] **2.2.18** "Where to add a new part" decision tree (parts vs assemblies vs tooling)

---

### Modeling (`website/docs/modeling/`)

#### `conventions.md`

- [ ] **2.3.1** Source of truth = Python; mm units; no committed meshes
- [ ] **2.3.2** Builder return types `Part` / `Compound`
- [ ] **2.3.3** Parameter defaults pattern
- [ ] **2.3.4** `main.py` is viewer-only — no MR decorators

#### `parts-and-assemblies.md`

- [ ] **2.3.5** Three-layer pattern diagram (mermaid): `make_*` → `@artifact` / `@customizable`
- [ ] **2.3.6** Layering rules (do / don't from AGENTS.md)
- [ ] **2.3.7** Cutout / reference alignment section (shared seat, hex prism cutter, margin)
- [ ] **2.3.8** Link to `cad/parts/sphere.py` on GitHub

#### `testing.md`

- [ ] **2.3.9** pytest commands; `just test` with extra args
- [ ] **2.3.10** What to assert: validity, bbox, volume, holes, export
- [ ] **2.3.11** Discovery tests pattern (`assert "sphere" in names`)
- [ ] **2.3.12** Golden fixtures policy under `tests/fixtures/`
- [ ] **2.3.13** Test design table from AGENTS.md (prefer / avoid)

#### `external-libraries.md`

- [ ] **2.3.14** Full library table from README references section
- [ ] **2.3.15** Enable instructions (`pyproject.toml` commented lines + `uv sync`)
- [ ] **2.3.16** When to thin-wrap in `cad/parts/` (link AGENTS.md external libs)
- [ ] **2.3.17** Upstream build123d index link

---

### Tools (`website/docs/tools/`)

#### `just.md`

- [ ] **2.4.1** What `just` is; `just --list`
- [ ] **2.4.2** Full recipe table by group (from README) — consider auto-sync script later
- [ ] **2.4.3** Common workflows: `just quality`, `just ci`, `just release dist/`
- [ ] **2.4.4** Pitfall: `just version-bump part=patch` vs `just version-bump minor`
- [ ] **2.4.5** Link each group to deeper docs (makerrepo, export, ci)

#### `makerrepo.md`

- [ ] **2.4.6** Decorators table: `@artifact`, `@customizable`, `@cached`
- [ ] **2.4.7** Import rule: `from mr import …`
- [ ] **2.4.8** `.makerrepo/config.yaml` field reference
- [ ] **2.4.9** CLI cookbook (artifacts + generators)
- [ ] **2.4.10** Sphere worked example (code from README / `sphere.py`)
- [ ] **2.4.11** MakerRepo.com optional path
- [ ] **2.4.12** `mr` vs `cad_tooling` decision table
- [ ] **2.4.13** Link official MakerRepo docs (external)

#### `cad-tooling/index.md`

- [ ] **2.4.14** Package layout diagram
- [ ] **2.4.15** When to use vs `mr` CLI
- [ ] **2.4.16** Links to export, render, release-notes subpages

#### `cad-tooling/export.md`

- [ ] **2.4.17** Migrate content from `cad_tooling/README.md` export section
- [ ] **2.4.18** CLI: smoke, export, release
- [ ] **2.4.19** Python API examples
- [ ] **2.4.20** Supported formats table
- [ ] **2.4.21** CI integration table (Dagger functions)

#### `cad-tooling/render.md`

- [ ] **2.4.22** Migrate render section from `cad_tooling/README.md`
- [ ] **2.4.23** Xvfb / headless OCP behavior
- [ ] **2.4.24** CLI flags table
- [ ] **2.4.25** `@render` decorator: single + multi-render
- [ ] **2.4.26** Camera presets list
- [ ] **2.4.27** Resolution order: defaults → `@render` → CLI

#### `cad-tooling/release-notes.md`

- [ ] **2.4.28** `release-notes` CLI usage
- [ ] **2.4.29** Absolute `releases/download/{tag}/` URL requirement
- [ ] **2.4.30** Example markdown with `Coffee2Bits/CAD-as-Code-Template` placeholder pattern
- [ ] **2.4.31** Local dry-run vs published release

#### `mcp-servers.md`

- [ ] **2.4.32** Embed `mcp-architecture.svg`
- [ ] **2.4.33** Server table (package, pin, role)
- [ ] **2.4.34** `.cursor/mcp.json` example
- [ ] **2.4.35** Launcher script behavior + version bump procedure
- [ ] **2.4.36** Tool catalog per server
- [ ] **2.4.37** Typical agent workflow (4 steps)
- [ ] **2.4.38** Other MCP candidates table (not endorsed)
- [ ] **2.4.39** Cross-link troubleshooting/mcp

#### `uv-and-quality.md`

- [ ] **2.4.40** `uv sync` / `sync-frozen` / dev group
- [ ] **2.4.41** ruff + mypy scope and commands
- [ ] **2.4.42** Format-on-save alignment with CI (`.vscode/settings.json`)
- [ ] **2.4.43** pre-commit / `just setup-hooks`
- [ ] **2.4.44** Link formatter section in AGENTS.md for agents

---

### Workflows (`website/docs/workflows/`)

#### `daily-development.md`

- [ ] **2.5.1** Edit loop: `cad/` → `just view` → `just test` → `just quality`
- [ ] **2.5.2** When to run `just ci` vs `just quality`
- [ ] **2.5.3** Commit conventions summary + link to releases page

#### `visual-verification.md`

- [ ] **2.5.4** Required after geometry edits (AGENTS.md rule)
- [ ] **2.5.5** `main.py` pattern — thin viewer
- [ ] **2.5.6** `just mr-view <artifact>`
- [ ] **2.5.7** MCP `capture_ocp_screenshot` option

#### `export-and-formats.md`

- [ ] **2.5.8** Format matrix from README
- [ ] **2.5.9** STEP vs STL tradeoffs
- [ ] **2.5.10** `just mr-export` vs `just export` vs `cad_tooling.export`
- [ ] **2.5.11** Embed `stack-data-flow.svg`

#### `ci-and-dagger.md`

- [ ] **2.5.12** Embed `ci-pipeline.svg`
- [ ] **2.5.13** Path filters from `.github/workflows/ci.yml`
- [ ] **2.5.14** Dagger function table + exact commands
- [ ] **2.5.15** Local `just ci` requirements (Docker socket)
- [ ] **2.5.16** Devcontainer Dockerfile parity note
- [ ] **2.5.17** What CI does *not* cover (VSIX, MCP)

#### `releases.md`

- [ ] **2.5.18** Embed `release-pipeline.svg`
- [ ] **2.5.19** release-please flow + GitHub Actions permissions (one-time setup)
- [ ] **2.5.20** Conventional Commits table (summary)
- [ ] **2.5.21** `just release`, `just release-notes` dry-run
- [ ] **2.5.22** Manual tag fallback (`release.yml`)
- [ ] **2.5.23** Release note URL rules (`OWNER/REPO` = `Coffee2Bits/CAD-as-Code-Template`)
- [ ] **2.5.24** Link `.github/release_template.md` on GitHub

---

### Troubleshooting (`website/docs/troubleshooting/`)

#### `index.md`

- [ ] **2.6.1** Symptom → page routing table
- [ ] **2.6.2** Known limitations from README (relocated or duplicated)
- [ ] **2.6.3** "Still stuck?" → open GitHub issue link (template repo)

#### `dev-container.md`

- [ ] **2.6.4** uv sync failures
- [ ] **2.6.5** Permission / UID issues
- [ ] **2.6.6** Hooks not running

#### `ocp-viewer.md`

- [ ] **2.6.7** Extension missing / commands not found
- [ ] **2.6.8** Cursor ESM crash
- [ ] **2.6.9** Reload window ordering
- [ ] **2.6.10** Panel not open before `show_object`

#### `mcp.md`

- [ ] **2.6.11** build123d-mcp first-start / network
- [ ] **2.6.12** ocp-viewer connection failed
- [ ] **2.6.13** MCP missing after rebuild

#### `dagger-and-docker.md`

- [ ] **2.6.14** Docker not running
- [ ] **2.6.15** Socket not mounted — rebuild devcontainer
- [ ] **2.6.16** Dagger version pin mismatch

#### `export-and-ci.md`

- [ ] **2.6.17** Artifact not in `mr artifacts list`
- [ ] **2.6.18** Export format errors
- [ ] **2.6.19** ruff format check drift
- [ ] **2.6.20** Release PNG missing (`@render`)

---

### Reference (`website/docs/reference/`)

#### `justfile-recipes.md`

- [ ] **2.7.1** Full searchable recipe table (duplicate of tools/just or canonical copy)
- [ ] **2.7.2** Optional: note future `scripts/sync-just-docs.sh`

#### `ci-functions.md`

- [ ] **2.7.3** Dagger module layout (`ci/src/ci/main.py`)
- [ ] **2.7.4** Per-function inputs/outputs
- [ ] **2.7.5** Equivalent `dagger call` invocations

#### `glossary.md`

- [ ] **2.7.6** artifact vs generator vs builder
- [ ] **2.7.7** smoke vs release bundle
- [ ] **2.7.8** OCP vs build123d vs Open CASCADE

---

### Contributing (`website/docs/contributing/`)

#### `for-humans.md`

- [ ] **2.8.1** PR flow; completion gate
- [ ] **2.8.2** Conventional Commits summary
- [ ] **2.8.3** Docs PR checklist (update matching page)

#### `for-agents.md`

- [ ] **2.8.4** "Read AGENTS.md in the repo" prominent callout
- [ ] **2.8.5** 5-bullet summary: parts/assemblies, completion gate, visual verify, MR pattern, external libs
- [ ] **2.8.6** Link to raw AGENTS.md on GitHub (correct repo slug)
- [ ] **2.8.7** Do not duplicate full agent rules on site

---

## Phase 3 — README migration (after pages exist)

Do **not** strip template identity. For each row, shorten README only after the doc page is live.

| README section | Keep in README | Move detail to |
|----------------|----------------|----------------|
| Opening pitch | Yes (short) | `intro.md` |
| What's in the box | Yes | `intro.md` (duplicate OK) |
| Stack table | **Yes** | `intro.md` + glossary links |
| Quick start | Yes (steps) | `quick-start.md` (expanded) |
| OCP viewer setup | Summary + link | `ocp-viewer.md` |
| Project layout | Yes (tree) | `project-layout.md` (expanded) |
| `just` full table | Link to docs | `tools/just.md` |
| Modeling conventions | Bullets + link | `modeling/conventions.md` |
| MakerRepo | Summary + link | `tools/makerrepo.md` |
| MCP servers | Summary + link | `tools/mcp-servers.md` |
| CI / releases | Summary + link | `workflows/ci-and-dagger.md`, `releases.md` |
| Troubleshooting tables | Link | `troubleshooting/*` |
| External libraries | Table OK in README | `modeling/external-libraries.md` |
| Known limitations | Link | `troubleshooting/index.md` |

- [x] **3.1** Add "Documentation" section near top of README with site link
- [x] **3.2** Replace migrated sections with links (dev workflow, MakerRepo, MCP, CI/releases, limitations, libraries)
- [x] **3.3** Keep `repo_preview.png` in README; also use in `intro.md` and `ocp-viewer.md`

---

## Phase 4 — Hardening

- [x] **4.1** PR workflow: `docs-pr.yml` runs `npm run build` on PRs touching `website/**`
- [x] **4.2** Add `onBrokenLinks: 'throw'` in Docusaurus config
- [x] **4.3** Add search (enabled by default in classic)
- [ ] **4.4** Optional: `scripts/sync-just-docs.sh` to regenerate recipe table from `just --list`
- [ ] **4.5** CI path filter: add `website/**` to main CI if docs start referencing live commands? (optional — docs build is separate)
- [x] **4.6** Final review: no `cad_as_code_project` strings in `website/docs/` (clean)

---

## `sidebars.ts` target structure

```typescript
const sidebars = {
  docsSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Getting started',
      items: [
        'getting-started/quick-start',
        'getting-started/dev-container',
        'getting-started/ocp-viewer',
        'getting-started/project-layout',
        'getting-started/github-setup',
      ],
    },
    {
      type: 'category',
      label: 'Modeling',
      items: [
        'modeling/conventions',
        'modeling/parts-and-assemblies',
        'modeling/testing',
        'modeling/external-libraries',
      ],
    },
    {
      type: 'category',
      label: 'Tools',
      items: [
        'tools/just',
        'tools/makerrepo',
        {
          type: 'category',
          label: 'CAD tooling',
          items: [
            'tools/cad-tooling/index',
            'tools/cad-tooling/export',
            'tools/cad-tooling/render',
            'tools/cad-tooling/release-notes',
          ],
        },
        'tools/mcp-servers',
        'tools/uv-and-quality',
      ],
    },
    {
      type: 'category',
      label: 'Workflows',
      items: [
        'workflows/daily-development',
        'workflows/visual-verification',
        'workflows/export-and-formats',
        'workflows/ci-and-dagger',
        'workflows/releases',
      ],
    },
    {
      type: 'category',
      label: 'Troubleshooting',
      items: [
        'troubleshooting/index',
        'troubleshooting/dev-container',
        'troubleshooting/ocp-viewer',
        'troubleshooting/mcp',
        'troubleshooting/dagger-and-docker',
        'troubleshooting/export-and-ci',
      ],
    },
    {
      type: 'category',
      label: 'Reference',
      items: [
        'reference/justfile-recipes',
        'reference/ci-functions',
        'reference/glossary',
      ],
    },
    {
      type: 'category',
      label: 'Contributing',
      items: [
        'contributing/for-humans',
        'contributing/for-agents',
      ],
    },
  ],
};
```

---

## `just` recipes to add (Phase 0)

```just
[group('docs')]
docs-install:
    npm ci
    cwd := 'website'

[group('docs')]
docs-start:
    npm run start
    cwd := 'website'

[group('docs')]
docs-build:
    npm run build
    cwd := 'website'
```

(Use `cd website && …` if your just version lacks `cwd`.)

---

## Progress log

| Date | Phase | Notes |
|------|-------|-------|
| 2026-06-10 | 0 | Docusaurus scaffold, all sidebar pages (initial content), workflows, `just docs-*`, Node 20 devcontainer feature |
| 2026-06-10 | 2 | Initial content for all 28 doc pages; Mermaid diagrams embedded inline (static SVGs pending Phase 1) |
| 2026-06-10 | 2–3 | Expanded tools, workflows, reference, modeling pages; README slimmed to ~185 lines with doc links |
| 2026-06-10 | — | Added `github-setup.md`, `open-cascade.md` reference pages |
