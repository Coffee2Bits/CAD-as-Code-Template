---
sidebar_position: 3
---

# Testing strategy

Tests in this repo are layered. They start with small assertions about individual CAD models, then move through MakerRepo discovery and `cad_tooling`, and finally exercise user-facing workflows in isolated copies of the template.

The goal is not to test the CI/CD pipeline for its own sake. The goal is to prove that a change still produces valid, discoverable, exportable CAD artifacts.

## Run the tests

```bash
just test
just test -v tests/test_sphere.py   # pass extra pytest args
```

`just test` runs `uv run pytest`. Pytest collects both configured suites:

| Suite | What it covers |
|-------|----------------|
| [`tests/`](https://github.com/Coffee2Bits/CAD-as-Code-Template/tree/main/tests) | CAD models, MakerRepo registration, exports, template identity, commit-message rules, and functional `just init` behavior. |
| [`cad_tooling_tests/`](https://github.com/Coffee2Bits/CAD-as-Code-Template/tree/main/cad_tooling_tests) | The reusable `cad_tooling` library: export helpers, render config, render discovery, release-note rendering, and asset collection. |

## Test layers

| Layer | Files | What it proves | When to add one |
|-------|-------|----------------|-----------------|
| Model unit tests | `tests/test_sphere.py`, `tests/test_m3_hex_nut.py`, `tests/test_sphere_hex_nut_pocket.py` | A specific part or assembly is valid and still has the expected dimensions, volume, orientation, clearances, or feature count. | Add or change a model, parameter, sketch, boolean operation, clearance, or imported library part. |
| Artifact registration tests | `tests/test_makerrepo.py`, `tests/test_sphere_with_nut.py` | MakerRepo can discover published `@artifact` entries and release filtering still selects the intended outputs. | Add, rename, remove, or reclassify an artifact or generator. |
| Export behavior tests | `tests/test_exports.py`, export checks in `tests/test_makerrepo.py` | The export code can write manufacturing/viewer formats and read back key geometry where appropriate. | Change STEP/STL/GLB behavior, artifact output names, or export options. |
| CAD tooling unit tests | `cad_tooling_tests/*.py` | The helper library behaves correctly without depending on one specific demo model. | Change `cad_tooling/export.py`, render config, release notes, discovery, or release asset collection. |
| Functional tests | `tests/functional/test_just_init.py` | User-facing recipes work against an isolated copy of the repository and do not mutate the real checkout. | Change `just init`, template identity, generated docs, release state, or repo-initialization behavior. |
| Dagger artifacts stage | `ci artifacts`, `just ci-artifacts`, `just export-smoke` | Every registered artifact can be discovered, realized, and exported as STEP and STL in the CI container. | Keep this green for publishable CAD changes; use it when a change might affect global artifact export, not just one model. |

## Model unit tests

Model tests should focus on the CAD contract for one part or assembly. Good assertions are concrete and observable:

| Assert | Why it matters |
|--------|----------------|
| `shape.is_valid()` or equivalent validity checks | Catches broken solids before export or release. |
| Bounding box dimensions | Catches accidental size, axis, or orientation changes. |
| Volume changes | Catches missing cuts, added material, or failed booleans. |
| Feature counts or face checks | Catches missing embossing, holes, pockets, or patterned details. |
| Clearance relationships | Catches fit regressions between parts, fasteners, pockets, and assemblies. |

Prefer targeted tests over broad snapshots. A good model test should tell the next person what physical behavior changed.

## MakerRepo and artifact tests

MakerRepo is the publishable-artifact registry. Tests around it answer different questions from model unit tests:

| Question | Example check |
|----------|---------------|
| Is the artifact discoverable? | `assert "sphere" in names` |
| Is the release set correct? | release artifacts require render metadata and intended release flags |
| Can a named artifact export? | export one artifact to STEP or STL and check the output exists |

Avoid exclusive discovery assertions such as `assert names == {...}` unless the point of the test is to lock the entire registry. Most tests should allow unrelated artifacts to be added later.

## CAD tooling tests

`cad_tooling_tests/` protects the library code that makes this template behave like a CAD-as-Code workspace. These tests are lower-level than the Dagger artifacts stage.

They check things like:

- artifact and generator resolution
- format-to-extension mapping
- render decorator configuration
- render-target discovery from `main.py`
- release asset collection
- release-note Markdown/HTML output

Use these tests when the behavior belongs to the tooling layer itself. Do not hide a tooling regression inside a model-specific test unless the model is only a small fixture for the tooling behavior.

## Functional tests

Functional tests are for workflows a user or agent runs from the command line. They should use temporary isolated workspaces and prove side effects, not just helper return values.

Current examples cover `just init`:

- dry-run output
- docs sync behavior
- rebranding from edited `template.repo.toml`
- refusal to infer identity from git remotes
- protection against modifying the real repo during functional test runs

Add a functional test when a bug only appears after recipes, scripts, generated files, and repo layout interact.

## Artifact export verification

The Dagger `artifacts` function currently runs:

```bash
uv run python -m cad_tooling.export smoke
```

Despite the `smoke` name, this is not a test that CI itself can call a stage. It is the artifacts-stage verification step. It proves that every registered `@artifact` can be discovered, realized, and exported to both STEP and STL inside the same container family used by CI.

That gives coverage that ordinary unit tests may not have:

- a newly added artifact is not missing from discovery
- a release artifact does not crash during realization
- an artifact that is not mentioned by a narrow model test still exports
- STEP and STL export paths both work for the full registered artifact set

Keep the artifacts stage when you want CI to protect releasable geometry. If the command name feels confusing, rename or document it, but do not remove the all-artifacts export invariant unless equivalent coverage exists somewhere else.

## What to assert

- Model validity: no invalid solids.
- Dimensions, volume, feature counts, and clearances that represent design intent.
- Export success for formats the artifact promises to produce.
- MakerRepo discovery with inclusion checks, not brittle full-set checks.
- Functional side effects in temp workspaces for user-facing recipes.

## Golden fixtures

Commit STEP/STL under `tests/fixtures/` only when an intentional regression fixture is needed. Generated release artifacts, routine exports, screenshots, and local render outputs should stay out of git.

## Test design

| Prefer | Avoid |
|--------|-------|
| `assert "sphere" in names` | `assert names == {"sphere"}` |
| Scoped export checks per artifact | Requiring every artifact in unrelated model tests |
| Explicit geometry assertions | Loosening unrelated bounds to pass |
| CAD tooling tests for library behavior | Repeating the same helper assertions in every model test |
| Functional tests in temp copies | Functional tests that mutate the working checkout |

## Choosing the right gate

| Situation | Run |
|-----------|-----|
| Editing one model or model test | `just test -v tests/test_<model>.py` |
| Changing `cad_tooling` behavior | `uv run pytest cad_tooling_tests -q` |
| Changing artifact registration or export behavior | `just export-smoke` or `just ci-artifacts` |
| Changing recipe/init behavior | `uv run pytest tests/functional -q` |
| Before pushing code or CAD changes | `just quality` |
| Before merging tooling, CI, or release changes | `just ci` |

Related pages: [uv and quality tools](/tools/uv-and-quality), [CAD tooling export](/tools/cad-tooling/export), and [CI/CD pipeline and Dagger](/workflows/ci-and-dagger).
