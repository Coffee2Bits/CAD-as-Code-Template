#!/usr/bin/env bash
set -euo pipefail

EXTENSION_ID="bernhard-42.ocp-cad-viewer"
VSIX_VERSION="3.4.0"
VSIX_NAME="ocp-cad-viewer-${VSIX_VERSION}.vsix"
VSIX_URL="https://github.com/bernhard-42/vscode-ocp-cad-viewer/releases/download/v${VSIX_VERSION}/${VSIX_NAME}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VSIX_PATH="${WORKSPACE_ROOT}/${VSIX_NAME}"
PATCH_SCRIPT="${SCRIPT_DIR}/patch-ocp-cad-viewer.sh"

download_vsix() {
  if [ -f "$VSIX_PATH" ]; then
    echo "Using existing OCP CAD Viewer VSIX: $VSIX_PATH"
    return 0
  fi

  echo "Downloading OCP CAD Viewer VSIX to workspace root: $VSIX_PATH"
  curl -fsSL "$VSIX_URL" -o "$VSIX_PATH"
}

prepare_vsix_for_cursor() {
  download_vsix
  bash "$PATCH_SCRIPT" --vsix
}

find_cursor_cli() {
  local candidate

  if command -v cursor >/dev/null 2>&1 && cursor --version >/dev/null 2>&1; then
    echo "cursor"
    return 0
  fi

  for candidate in "$HOME/.cursor-server/bin/"*/bin/remote-cli/cursor; do
    if [ -x "$candidate" ] && "$candidate" --version >/dev/null 2>&1; then
      echo "$candidate"
      return 0
    fi
  done

  return 1
}

install_with_cursor() {
  local cli
  cli="$(find_cursor_cli)" || return 1

  prepare_vsix_for_cursor

  echo "Installing patched OCP CAD Viewer for Cursor (${cli})..."
  "$cli" --install-extension "$VSIX_PATH"
  bash "$PATCH_SCRIPT" --installed
  echo "Reload the Cursor window if commands are still missing."
}

case "${1:-}" in
  download)
    prepare_vsix_for_cursor
    echo "Patched VSIX ready for Cursor devcontainer install: $VSIX_PATH"
    ;;
  install-cli)
    install_with_cursor
    ;;
  "")
    prepare_vsix_for_cursor
    echo "Patched VSIX ready for Cursor devcontainer install: $VSIX_PATH"
    echo "Cursor installs it from customizations.vscode.extensions on devcontainer attach."
    echo "To reinstall manually from a connected terminal, run:"
    echo "  bash .devcontainer/install-ocp-cad-viewer.sh install-cli"
    ;;
  *)
    echo "Usage: $0 [download|install-cli]" >&2
    exit 1
    ;;
esac
