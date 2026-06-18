---
sidebar_position: 3
---

# Testing strategy

Testing in this template is meant to protect design intent, not just code style. A good test should make it clear what physical or workflow promise would break if it failed: a part became invalid, a clearance changed, an artifact stopped exporting, or a repository command no longer worked for a new user.

Most day-to-day CAD changes should start with a focused test group and end with the normal quality gate. Broader workflow and export checks are there for changes that affect artifact registration, release output, or the template machinery itself.

Repo contract: [AGENTS.md](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/AGENTS.md) owns agent-only rules such as isolated `just` tests, completion gates, and cutout alignment. This page owns markers, test groups, and the daily test loop for humans and agents.

## Test layout

| Path | Role |
|------|------|
| `tests/` | CAD models, MakerRepo discovery/export, template identity, functional `just` recipes |
| `cad_tooling_tests/` | Export, render, and release-notes tooling that mirrors `cad_tooling/` |
| `conftest.py` | Shared session fixtures such as `registry` and `release_artifacts`, plus marker enforcement |
| `pytest_support.py` | Shared constants and registry helpers importable from tests |
| `tests/functional/` | Destructive `just` recipe tests; always use `isolated_repo` and `run_just()` |

## Run the normal test suite

```bash
just test
just test -v tests/test_sphere.py   # pass extra pytest args
```

`just test` runs `uv run pytest` across the project test suites.

Use narrower commands while editing:

| Command | Scope |
|---------|-------|
| `just test-unit` | Unit tests for config, discovery, pure logic, template replacement, and commit-message validation |
| `just test-integration` | CAD geometry, export round-trips, release artifact behavior, and viewer script loading |
| `just test-render` | Headless OCP PNG rendering subset |
| `just test-functional` | Real `just` CLI recipes in isolated temporary copies of the repo |
| `just test-v` | Full suite with verbose pytest output |
| `just quality` | Lint plus the full pytest suite; use before opening a PR |

## Test categories and markers

Every test declares exactly one primary marker: `unit`, `integration`, or `functional`. Render paths also carry `render` alongside `integration`.

Markers are registered in [`pyproject.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/pyproject.toml) and enforced in [`conftest.py`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/conftest.py) at collection time. Unmarked or doubly-marked tests fail immediately.

| Marker | When to use | Examples |
|--------|-------------|----------|
| `unit` | Fast logic with no CAD solid builds and no subprocess-isolated `just` runs. | Render config merge, decorator metadata, MakerRepo discovery lists, template string replacement, commit-message validation. |
| `integration` | CAD geometry, export round-trips, release artifact behavior, and viewer script loading. | `make_sphere()` validity, STL/STEP export, `export_artifacts()`, assembly bounds. |
| `render` | Headless OCP PNG rendering, always with `integration`. | `render_stl()`, release preview PNG names. |
| `functional` | Real `just` CLI behavior in a temporary copy of the repo. | `just init`, `just init-dry-run`, and template sync recipes under `tests/functional/`. |

Choosing a marker:

```text
Touches just CLI in an isolated copy?     -> functional
Builds CAD / exports meshes / release?   -> integration (+ render if PNG rendering runs)
Otherwise                                -> unit
```

Mixed modules should mark per class or per function. Do not use a file-level `pytestmark` when the file contains different test types.

Example:

```python
import pytest

pytestmark = pytest.mark.unit  # entire module is unit


@pytest.mark.integration
class TestSphereGeometry:
    ...


@pytest.mark.integration
@pytest.mark.render
class TestReleaseRender:
    ...
```

Functional suite module header:

```python
pytestmark = pytest.mark.functional
```

## Testing pyramid for this template

Use the narrowest test that proves the behavior you care about, then run the broader gate before pushing.

| Layer | Purpose | Add or update when |
|-------|---------|--------------------|
| Model tests | Prove a part or assembly still satisfies its design contract. | You change dimensions, parameters, sketches, booleans, orientation, clearances, or external library parts. |
| Artifact tests | Prove publishable models are discoverable and exported under the right names. | You add, rename, remove, or reclassify a MakerRepo `@artifact`. |
| Export tests | Prove STEP, STL, GLB, or related export behavior still works. | You change export options, file naming, release formats, or artifact output paths. |
| Tooling tests | Prove the reusable `cad_tooling` package works independently from one demo model. | You change export helpers, render metadata, release-note generation, or asset collection. |
| Functional tests | Prove command-line workflows work in isolated copies of the repository. | You change `just init`, template identity, generated docs, release state, or repo setup behavior. |
| CI/CD artifact verification | Prove the full registered artifact set can export in the CI/CD pipeline container. | You change publishable geometry, artifact discovery, export plumbing, or release automation. |

## Model tests

Model tests should describe the physical contract of one part or assembly. Prefer checks that a designer can understand later.

| Assert | Why it matters |
|--------|----------------|
| Solid validity | Catches broken geometry before export or release. |
| Bounding box dimensions | Catches accidental size, axis, or orientation changes. |
| Volume | Catches missing cuts, added material, or failed booleans. |
| Feature counts or face checks | Catches missing holes, pockets, embossing, patterns, or mounting features. |
| Clearances and fit relationships | Catches regressions between parts, fasteners, pockets, and assemblies. |

Prefer targeted assertions over broad snapshots. A failing test should point to the design intent that changed.

## Artifact and export tests

MakerRepo is the registry for publishable CAD outputs. Artifact tests answer questions that model tests usually do not:

| Question | Example check |
|----------|---------------|
| Is the artifact discoverable? | `assert "sphere" in names` |
| Is it included in the intended release set? | release artifacts have the expected render metadata and release flags |
| Can it export? | export one artifact to STEP or STL and check the output exists |

Avoid brittle full-registry assertions such as `assert names == {...}` unless the purpose of the test is to lock the entire registry. Most tests should allow unrelated artifacts to be added later.

## Tooling tests

`cad_tooling_tests/` protects the support library that makes this a CAD-as-Code workspace. These tests are for behavior that belongs to the tooling layer rather than to one model.

Examples include:

- artifact and generator resolution
- format-to-extension mapping
- render decorator configuration
- render-target discovery from `main.py`
- release asset collection
- release-note Markdown and HTML rendering

If a change is really about `cad_tooling`, test it there. Use a model only as a fixture when the tooling behavior needs one.

## Functional tests

Functional tests cover workflows a user or agent runs from the command line. They should use temporary isolated workspaces and prove side effects, not just helper return values.

Current functional coverage focuses on template initialization and `just` recipes:

- dry-run output
- docs sync behavior
- rebranding from edited `template.repo.toml`
- refusal to infer identity from git remotes
- protection against modifying the real checkout during tests

Destructive recipes such as `just init` and `just template-apply` belong in [`tests/functional/`](https://github.com/Coffee2Bits/CAD-as-Code-Template/tree/main/tests/functional):

1. Use the `isolated_repo` fixture, which copies the repo under `tmp_path`.
2. Invoke recipes only through `run_just(isolated_repo, "init", ...)`, which refuses the real repo root.
3. Mark the module or tests with `@pytest.mark.functional`.

Unit tests for init logic without the `just` CLI stay in `tests/test_template_identity.py`.

## Artifact export verification

Some commands use the word `smoke`, but the important idea is artifact export verification.

The Dagger `artifacts` stage runs:

```bash
uv run python -m cad_tooling.export smoke
```

That command verifies the registered artifact set. It discovers every `@artifact`, realizes each model, and exports STEP and STL in the same container family used by the CI/CD pipeline.

Keep this coverage because it catches failures that narrow model tests can miss:

- a new artifact is not discoverable
- a release artifact crashes during realization
- an artifact without a dedicated model test no longer exports
- STEP or STL export fails for part of the registered artifact set

If the command name changes later, preserve the invariant: the CI/CD pipeline should prove that publishable artifacts can be generated from source.

## Recommended workflow

While implementing, use the smallest relevant group for fast feedback:

1. Use `just test-unit` for pure logic, config, discovery, and template text changes.
2. Use `just test-integration` for CAD geometry, export paths, or release artifact behavior.
3. Use `just test-render` for render or release PNG changes.
4. Use `just test-functional` for `justfile`, initialization, or template recipe changes.

Do not run the full suite on every iteration unless you are finishing work.

Before marking work complete, run the completion gate:

```bash
just quality && just export-smoke
# or: just ci
```

That runs lint, all pytest groups, and artifact export verification.

## Golden fixtures

Commit STEP/STL fixtures under `tests/fixtures/` only when they are intentional regression fixtures. Generated release artifacts, routine exports, screenshots, and local render outputs should stay out of git.

## Choosing the right gate

| Situation | Run |
|-----------|-----|
| Editing pure logic, config, discovery, or template text | `just test-unit` |
| Editing one model or model test | `just test-integration -k <name>` or `just test -v tests/test_<model>.py` |
| Changing `cad_tooling` behavior | `uv run pytest cad_tooling_tests -q` |
| Changing artifact registration or export behavior | `just export-smoke` or `just ci-artifacts` |
| Changing repo initialization or command recipes | `just test-functional` |
| Before pushing code or CAD changes | `just quality` |
| Before merging tooling, CI/CD pipeline, or release changes | `just ci` |

Related pages: [uv and quality tools](/tools/uv-and-quality), [CAD tooling export](/tools/cad-tooling/export), [MakerRepo](/tools/makerrepo), and [CI/CD pipeline and Dagger](/workflows/ci-and-dagger).
