---
sidebar_position: 3
---

# Testing strategy

This page is the guide for how tests are organized, classified, and run in this repo. Agents and humans should follow the same workflow.

**Repo contract:** [AGENTS.md](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/AGENTS.md) still owns agent-only rules (isolated `just` tests, completion gate, cutout alignment). This page owns **markers, test groups, and the daily test loop**.

## Layout

| Path | Role |
|------|------|
| `tests/` | CAD models, MakerRepo discovery/export, template identity, functional `just` recipes |
| `cad_tooling_tests/` | Export, render, and release-notes tooling (mirrors `cad_tooling/` layout) |
| `conftest.py` | Shared session fixtures (`registry`, `release_artifacts`) and marker enforcement |
| `pytest_support.py` | Shared constants and registry helpers importable from tests |
| `tests/functional/` | Destructive `just` recipe tests — always use `isolated_repo` + `run_just()` |

## Test categories (pytest markers)

Every test declares **exactly one primary marker**: `unit`, `integration`, or `functional`. Render paths also carry `render` alongside `integration`.

Markers are registered in [`pyproject.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/pyproject.toml) and enforced in [`conftest.py`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/conftest.py) at collection time — unmarked or doubly-marked tests fail immediately.

| Marker | When to use | Examples |
|--------|-------------|----------|
| **`unit`** | Fast logic with no CAD solid builds and no subprocess-isolated `just` runs | Render config merge, decorator metadata, MR discovery lists, template string replacement, commit-msg validation |
| **`integration`** | CAD geometry, export round-trips, release smoke, viewer script loading | `make_sphere()` validity, STL/STEP export, `export_artifacts()`, assembly bounds |
| **`render`** | Headless OCP PNG rendering (always **with** `integration`) | `render_stl()`, `export release`, release preview PNG names |
| **`functional`** | Real `just` CLI in a **temp copy** of the repo | `just init`, `just init-dry-run` in `tests/functional/` |

### Choosing a marker for new tests

```text
Touches just CLI in isolated copy?     → functional
Builds CAD / exports meshes / release? → integration (+ render if PNG path runs)
Otherwise                              → unit
```

Mixed modules (e.g. discovery + export in one file) mark **per class or per function** — do not use a file-level `pytestmark` when types differ.

### Examples

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

## Running tests

| Command | Scope |
|---------|--------|
| `just test` | Full suite (169 tests) |
| `just test-unit` | `pytest -m unit` — default loop while implementing |
| `just test-integration` | `pytest -m integration` — CAD and export paths |
| `just test-render` | `pytest -m render` — headless PNG subset |
| `just test-functional` | `pytest -m functional` — isolated `just` recipes |
| `just test -v tests/test_sphere.py` | Pass extra pytest args through |
| `just quality` | `lint` + **full** pytest — use before merge / completion gate |

CI and the completion gate always run the **full** suite (`just test` via `just quality` or Dagger `check`).

## Recommended workflow

### While implementing

Use the **smallest relevant group** for fast feedback:

1. **Default:** `just test-unit` after logic, config, or discovery changes.
2. **CAD / export edits:** `just test-integration` (add `-k` or a file path to narrow).
3. **Render / release PNG edits:** `just test-render`.
4. **`justfile` init / template recipes:** `just test-functional` — never run those recipes on the real repo root to “check” behavior.

Do **not** run the full suite on every iteration unless you are finishing work.

### Before marking work complete

Run the [completion gate](/tools/uv-and-quality#full-cicd-pipeline-gate):

```bash
just quality && just export-smoke
# or: just ci
```

That runs lint, **all** pytest groups, and artifact export smoke — same stages as CI.

### Agents

This is the standard agent pattern:

| Phase | Command |
|-------|---------|
| During implementation | `just test-unit` (plus targeted `test-integration` / `test-render` / `test-functional` when the change touches those areas) |
| Final check before done | `just quality && just export-smoke` or `just ci` |

See also [For agents](/contributing/for-agents) and [AGENTS.md → Task completion gate](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/AGENTS.md#task-completion-gate).

## What to assert

- Model validity (no invalid solids)
- Bounding box, volume, hole counts, critical interfaces
- Export round-trip where applicable
- MakerRepo discovery: `assert "sphere" in names` (not exclusive sets)
- Cutout / reference alignment: shared seat, hex cutter pose, flush fit (see AGENTS.md cutout rules)

## Test design

| Prefer | Avoid |
|--------|-------|
| `assert "sphere" in names` | `assert names == {"sphere"}` |
| Scoped export checks per artifact | Requiring every artifact in unrelated tests |
| Explicit geometry assertions for the behavior under change | Loosening unrelated bounds to pass |
| `@pytest.mark.functional` + `isolated_repo` for destructive `just` recipes | Running `just init` on the real workspace root |
| One primary marker per test | Relying on directory location instead of explicit markers |

## Functional `just` tests

Destructive recipes (`just init`, `just template-apply`, …) belong in [`tests/functional/`](https://github.com/Coffee2Bits/CAD-as-Code-Template/tree/main/tests/functional):

1. Use the `isolated_repo` fixture (full repo copy under `tmp_path`).
2. Invoke recipes only via `run_just(isolated_repo, "init", …)` — refuses `REPO_ROOT`.
3. Mark the module or tests with `@pytest.mark.functional`.

Unit tests for init logic **without** the `just` CLI stay in `tests/test_template_identity.py`.

## Golden fixtures

Commit STEP/STL under `tests/fixtures/` only when intentional regression fixtures are needed. Never commit ad-hoc export output from pytest `tmp_path`.
