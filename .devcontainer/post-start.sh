#!/usr/bin/env bash
# Devcontainer post-start hook — run optional setup steps without blocking docs.
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$WORKSPACE_ROOT"

run_step() {
  local label="$1"
  shift
  echo "==> ${label}"
  if "$@"; then
    echo "==> ${label}: OK"
  else
    echo "==> ${label}: skipped or failed (continuing)" >&2
  fi
}

run_step "uv sync" uv sync
run_step "pre-commit hooks" just setup-hooks
run_step "OCP CAD Viewer CLI install" bash .devcontainer/install-ocp-cad-viewer.sh install-cli
run_step "OCP CAD Viewer demo model" timeout 45s just view
run_step "Docusaurus docs server" bash .devcontainer/start-docs.sh

prompt="$(uv run python -c 'from scripts.template_identity import template_init_prompt; print(template_init_prompt() or "", end="")' 2>/dev/null || true)"
if [[ -n "$prompt" ]]; then
  echo "==> ${prompt}"
fi
