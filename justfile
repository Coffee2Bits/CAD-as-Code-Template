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

# Install git hooks (Conventional Commit subject validation on commit-msg).
[group('setup')]
setup-hooks:
    uv run pre-commit install --hook-type pre-commit --hook-type commit-msg

# Apply template.repo.toml to docs config, README links, and related files.
[group('setup')]
template-apply:
    uv run python scripts/apply_template_identity.py

[group('setup')]
template-apply-dry-run:
    uv run python scripts/apply_template_identity.py --dry-run

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
    uv run vulture

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
mr-export-generator name out='/tmp/out' params='{}':
    mkdir -p {{out}}
    uv run mr generators export {{name}} -p '{{params}}' -o {{out}}

# --- Export & render (cad_tooling) ---

[group('export')]
export-smoke:
    uv run python -m cad_tooling.export smoke

[group('export')]
export out='dist' format='release' *names:
    #!/usr/bin/env bash
    set -euo pipefail
    mkdir -p "{{out}}"
    if [[ "{{format}}" == "release" ]]; then
        uv run python -m cad_tooling.export release -o "{{out}}" --lighting-preset default
    else
        uv run python -m cad_tooling.export export -o "{{out}}" --format "{{format}}" {{names}}
    fi

[group('export')]
release out='dist':
    @just export {{out}}

[group('export')]
release-notes tag out='dist/RELEASE_BODY.md' assets='dist' repo='':
    #!/usr/bin/env bash
    set -euo pipefail
    repo="{{repo}}"
    if [[ -z "$repo" ]]; then
      repo="$(uv run python -c 'from scripts.template_identity import load_identity; print(load_identity().github_repo_slug)')"
    fi
    uv run python -m cad_tooling.export release-notes \
        --assets-dir "{{assets}}" \
        --repo "$repo" \
        --tag "{{tag}}" \
        -o "{{out}}"

[group('export')]
render *args:
    #!/usr/bin/env bash
    set -euo pipefail
    script="main.py"
    out="dist"
    positionals=()
    flags=()
    value_flags=(
        --artifact --width --height --background --face-color --fit-margin
        --camera --azimuth --elevation --lighting-preset --light-intensity
        --ambient-intensity --headlight-intensity --fill-intensity
    )
    takes_value() {
        local flag="$1"
        for candidate in "${value_flags[@]}"; do
            [[ "$flag" == "$candidate" ]] && return 0
        done
        return 1
    }
    is_input_file() {
        [[ "$1" =~ \.(py|stl)$ ]] || [[ -f "$1" ]]
    }
    for arg in {{args}}; do
        if [[ "$arg" == --* ]]; then
            flags+=("$arg")
            if takes_value "$arg"; then
                shift_flag_value=1
            fi
        elif [[ -n "${shift_flag_value:-}" ]]; then
            flags+=("$arg")
            unset shift_flag_value
        else
            positionals+=("$arg")
        fi
    done
    if [[ -n "${shift_flag_value:-}" ]]; then
        echo "error: missing value for ${flags[-1]}" >&2
        exit 1
    fi
    if ((${#positionals[@]} > 0)); then
        if is_input_file "${positionals[0]}"; then
            script="${positionals[0]}"
            if ((${#positionals[@]} > 1)); then out="${positionals[1]}"; fi
        else
            out="${positionals[0]}"
            if ((${#positionals[@]} > 1)); then
                echo "usage: just render [script] [outdir] [--render-flags...]" >&2
                exit 1
            fi
        fi
    fi
    uv run python -m cad_tooling.render "$script" -o "$out" "${flags[@]}"

[group('export')]
render-artifact *args:
    #!/usr/bin/env bash
    set -euo pipefail
    name=""
    out="/tmp/out"
    positionals=()
    flags=()
    value_flags=(
        --artifact --width --height --background --face-color --fit-margin
        --camera --azimuth --elevation --lighting-preset --light-intensity
        --ambient-intensity --headlight-intensity --fill-intensity
    )
    takes_value() {
        local flag="$1"
        for candidate in "${value_flags[@]}"; do
            [[ "$flag" == "$candidate" ]] && return 0
        done
        return 1
    }
    for arg in {{args}}; do
        if [[ "$arg" == --* ]]; then
            flags+=("$arg")
            if takes_value "$arg"; then
                shift_flag_value=1
            fi
        elif [[ -n "${shift_flag_value:-}" ]]; then
            flags+=("$arg")
            unset shift_flag_value
        else
            positionals+=("$arg")
        fi
    done
    if [[ -n "${shift_flag_value:-}" ]]; then
        echo "error: missing value for ${flags[-1]}" >&2
        exit 1
    fi
    if ((${#positionals[@]} == 0)); then
        echo "usage: just render-artifact <name> [outdir] [--render-flags...]" >&2
        exit 1
    fi
    name="${positionals[0]}"
    if ((${#positionals[@]} > 1)); then out="${positionals[1]}"; fi
    mkdir -p "$out"
    uv run python -m cad_tooling.export export -o "$out" --format stl "$name"
    uv run python -m cad_tooling.render "$name" -o "$out" --artifact "$name" "${flags[@]}"

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

# --- Documentation (Docusaurus) ---

[group('docs')]
docs-install:
    cd website && npm ci

[group('docs')]
docs-serve:
    # Docusaurus dev server with hot reload — http://localhost:3000
    cd website && npm run start

[group('docs')]
docs-serve-bg:
    # Background dev server (idempotent) — same script as devcontainer postStart
    bash .devcontainer/start-docs.sh

[group('docs')]
docs-start: docs-serve

[group('docs')]
docs-build:
    just template-apply
    cd website && npm run build

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
