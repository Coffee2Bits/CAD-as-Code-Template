#!/usr/bin/env bash
# OCP CAD Viewer 3.4.0 ships proper-lockfile as ESM-only, but the extension
# loads it with CommonJS require(). Cursor's extension host fails to activate.
#
# Cursor devcontainers reinstall the workspace VSIX on attach, so we must patch
# the VSIX file itself (not only the extracted extension directory).
set -euo pipefail

VSIX_VERSION="3.4.0"
VSIX_NAME="ocp-cad-viewer-${VSIX_VERSION}.vsix"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
VSIX_PATH="${WORKSPACE_ROOT}/${VSIX_NAME}"
LOCKFILE_URL="https://registry.npmjs.org/proper-lockfile/-/proper-lockfile-4.1.2.tgz"

needs_lockfile_patch() {
  local pkg_json="$1"
  [ -f "$pkg_json" ] && grep -q '"type"[[:space:]]*:[[:space:]]*"module"' "$pkg_json"
}

install_cjs_lockfile() {
  local dest_dir="$1"
  local tmp
  tmp="$(mktemp -d)"
  curl -fsSL "$LOCKFILE_URL" -o "$tmp/proper-lockfile.tgz"
  rm -rf "$dest_dir"
  mkdir -p "$dest_dir"
  tar -xzf "$tmp/proper-lockfile.tgz" -C "$dest_dir" --strip-components=1
  rm -rf "$tmp"
}

patch_extension_dir() {
  local ext_dir="$1"
  local lockfile_dir="$ext_dir/node_modules/proper-lockfile"
  local pkg_json="$lockfile_dir/package.json"

  if [ ! -f "$pkg_json" ]; then
    echo "OCP CAD Viewer: proper-lockfile not found under $ext_dir"
    return 1
  fi

  if ! needs_lockfile_patch "$pkg_json"; then
    echo "OCP CAD Viewer: proper-lockfile already CommonJS-compatible in $ext_dir"
    return 0
  fi

  echo "Patching proper-lockfile (ESM -> CJS) in $ext_dir..."
  install_cjs_lockfile "$lockfile_dir"
}

patch_vsix() {
  local vsix_path="$1"

  if [ ! -f "$vsix_path" ]; then
    echo "OCP CAD Viewer VSIX not found: $vsix_path"
    return 1
  fi

  local tmp extract_dir ext_dir marker
  tmp="$(mktemp -d)"
  extract_dir="$tmp/vsix"
  ext_dir="$extract_dir/extension"
  marker="$ext_dir/node_modules/proper-lockfile/package.json"

  unzip -q "$vsix_path" -d "$extract_dir"
  if [ ! -f "$marker" ]; then
    echo "OCP CAD Viewer: could not locate proper-lockfile inside $vsix_path"
    rm -rf "$tmp"
    return 1
  fi

  if needs_lockfile_patch "$marker"; then
    echo "Patching OCP CAD Viewer VSIX for Cursor: $vsix_path"
    patch_extension_dir "$ext_dir"
    rm -f "$vsix_path"
    (cd "$extract_dir" && zip -qr "$vsix_path" .)
    echo "Patched VSIX ready for Cursor install."
  else
    echo "OCP CAD Viewer VSIX already patched: $vsix_path"
  fi

  rm -rf "$tmp"
}

find_extension_dir() {
  local candidate
  for candidate in \
    "$HOME/.cursor-server/extensions"/bernhard-42.ocp-cad-viewer-* \
    "$HOME/.vscode-server/extensions"/bernhard-42.ocp-cad-viewer-*; do
    if [ -d "$candidate" ]; then
      echo "$candidate"
      return 0
    fi
  done
  return 1
}

patch_installed_extension() {
  local ext_dir
  ext_dir="$(find_extension_dir)" || {
    echo "OCP CAD Viewer extension not installed yet."
    return 0
  }
  patch_extension_dir "$ext_dir"
}

usage() {
  echo "Usage: $0 [--vsix | --installed | --all]" >&2
}

main() {
  case "${1:---all}" in
    --vsix)
      patch_vsix "$VSIX_PATH"
      ;;
    --installed)
      patch_installed_extension
      ;;
    --all)
      patch_vsix "$VSIX_PATH"
      patch_installed_extension
      ;;
    -h | --help)
      usage
      ;;
    *)
      usage
      return 1
      ;;
  esac
}

main "$@"
