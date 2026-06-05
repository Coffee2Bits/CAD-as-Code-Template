#!/usr/bin/env bash
set -euo pipefail

mkdir -p .devcontainer/vsix

VSIX_URL="https://github.com/bernhard-42/vscode-ocp-cad-viewer/releases/download/v3.4.0/ocp-cad-viewer-3.4.0.vsix"
VSIX_PATH=".devcontainer/vsix/ocp-cad-viewer-3.4.0.vsix"

if [ ! -f "$VSIX_PATH" ]; then
  curl -L "$VSIX_URL" -o "$VSIX_PATH"
fi

echo "Downloaded OCP CAD Viewer VSIX to $VSIX_PATH"

if command -v code >/dev/null 2>&1; then
  code --install-extension "$VSIX_PATH" || true
elif command -v cursor >/dev/null 2>&1; then
  cursor --install-extension "$VSIX_PATH" || true
else
  echo "No code/cursor CLI found inside container."
  echo "Install manually from Cursor: Extensions -> Install from VSIX -> $VSIX_PATH"
fi
