# CAD-as-Code workspace commands — https://github.com/casey/just
# Run `just` or `just --list` to see available recipes.

set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

default:
    @just --list --unsorted

# --- Setup ---

[group('setup')]
sync:
    uv sync

[group('setup')]
sync-frozen:
    uv sync --group dev --frozen

# --- Development ---

[group('dev')]
view:
    # Display the model configured in main.py in OCP CAD Viewer.
    uv run python main.py

[group('dev')]
test *args:
    uv run pytest {{args}}

[group('dev')]
test-v:
    uv run pytest -v

# --- Local quality (same checks as Dagger lint + pytest) ---

[group('quality')]
lint:
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy cad cad_tooling tests cad_tooling_tests

[group('quality')]
format:
    uv run ruff format .

[group('quality')]
quality: lint test
    @echo "Local quality gate passed."

# --- MakerRepo CLI ---

[group('makerrepo')]
mr-artifacts:
    uv run mr artifacts list

[group('makerrepo')]
mr-generators:
    uv run mr generators list

[group('makerrepo')]
mr-export name out='/tmp/out' format='step':
    mkdir -p {{out}}
    uv run mr artifacts export {{name}} -o {{out}} --format {{format}}

[group('makerrepo')]
mr-view name:
    uv run mr artifacts view {{name}}

[group('makerrepo')]
mr-snapshot name out='/tmp/out/{{name}}.png':
    mkdir -p "$(dirname '{{out}}')"
    uv run mr artifacts snapshot {{name}} -o {{out}}

[group('makerrepo')]
mr-export-generator name out='/tmp/out' params='{}':
    mkdir -p {{out}}
    uv run mr generators export {{name}} -p '{{params}}' -o {{out}}

# --- Export & render (cad_tooling) ---

[group('export')]
export-smoke:
    uv run python -m cad_tooling.export smoke

[group('export')]
export out='dist/export' format='step' *names:
    mkdir -p {{out}}
    uv run python -m cad_tooling.export export -o {{out}} --format {{format}} {{names}}

[group('export')]
release out='dist':
    mkdir -p {{out}}
    uv run python -m cad_tooling.export release -o {{out}}

[group('export')]
release-notes repo tag out='dist/RELEASE_BODY.md' assets='dist':
    uv run python -m cad_tooling.export release-notes \
        --assets-dir {{assets}} \
        --repo {{repo}} \
        --tag {{tag}} \
        -o {{out}}

[group('export')]
render script='main.py' out='dist' *camera:
    uv run python -m cad_tooling.render {{script}} -o {{out}} {{camera}}

# --- Release versioning ---

# Bump pyproject.toml version. Usage: just version-bump [patch|minor|major|…]
[group('release')]
version-bump component='patch':
    #!/usr/bin/env bash
    set -euo pipefail
    component="{{component}}"
    if [[ "$component" == *"="* ]]; then
        echo "usage: just version-bump [patch|minor|major|…]" >&2
        exit 1
    fi
    uv version --bump "$component"

# Create and push git tag v{version} from the current package version.
[group('release')]
version-tag:
    #!/usr/bin/env bash
    set -euo pipefail
    version="$(uv version --short)"
    tag="v${version}"
    if git rev-parse "$tag" >/dev/null 2>&1; then
        echo "Tag already exists: $tag" >&2
        exit 1
    fi
    git tag "$tag"
    git push origin "$tag"
    echo "Created and pushed $tag"

# --- Dagger CI (requires Docker; run inside devcontainer) ---

[group('ci')]
ci:
    dagger call -m ./ci check --source=.

[group('ci')]
ci-test:
    dagger call -m ./ci test --source=.

[group('ci')]
ci-lint:
    dagger call -m ./ci lint --source=.

[group('ci')]
ci-artifacts:
    dagger call -m ./ci artifacts --source=.

[group('ci')]
ci-release out='dist':
    mkdir -p {{out}}
    dagger call -m ./ci release-artifact --source=. export --path={{out}}
