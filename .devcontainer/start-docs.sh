#!/usr/bin/env bash
# Start the Docusaurus dev server in the background (idempotent, portable).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PORT="${DOCS_PORT:-3000}"
LOG_FILE="${DOCS_LOG_FILE:-/tmp/cad-docs-serve.log}"
PID_FILE="${DOCS_PID_FILE:-/tmp/cad-docs-serve.pid}"

port_listening() {
  if command -v ss >/dev/null 2>&1; then
    ss -tlnH "sport = :${PORT}" 2>/dev/null | grep -q .
    return
  fi
  if command -v lsof >/dev/null 2>&1; then
    lsof -nP -iTCP:"${PORT}" -sTCP:LISTEN >/dev/null 2>&1
    return
  fi
  if command -v nc >/dev/null 2>&1; then
    nc -z 127.0.0.1 "${PORT}" >/dev/null 2>&1
    return
  fi
  curl -fsS --max-time 1 "http://127.0.0.1:${PORT}/" >/dev/null 2>&1
}

pid_running() {
  local pid="$1"
  [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

if [ -f "$PID_FILE" ]; then
  old_pid="$(tr -d '[:space:]' <"$PID_FILE")"
  if pid_running "$old_pid" && port_listening; then
    echo "Docs dev server already running (pid ${old_pid}) — http://localhost:${PORT}"
    exit 0
  fi
  rm -f "$PID_FILE"
fi

if port_listening; then
  echo "Docs dev server already listening on port ${PORT} — http://localhost:${PORT}"
  exit 0
fi

cd "$WORKSPACE_ROOT"

if [ ! -d website/node_modules ]; then
  echo "Installing docs dependencies (website/node_modules missing)…"
  just docs-install
fi

cd website
: >"$LOG_FILE"

start_server() {
  export BROWSER=none
  export PORT="${PORT}"
  if command -v setsid >/dev/null 2>&1; then
    setsid npm run start >>"$LOG_FILE" 2>&1 &
  else
    nohup npm run start >>"$LOG_FILE" 2>&1 </dev/null &
    disown 2>/dev/null || true
  fi
  echo $!
}

docs_pid="$(start_server)"
echo "$docs_pid" >"$PID_FILE"

echo "Started Docusaurus docs dev server (pid ${docs_pid}) — http://localhost:${PORT}"
echo "Logs: ${LOG_FILE}"
