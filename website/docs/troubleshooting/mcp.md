---
sidebar_position: 4
---

# MCP troubleshooting

MCP servers run **inside the dev container**. Confirm you are attached via **Reopen in Container**, not editing on the host without the container.

| Issue | Fix |
|-------|-----|
| build123d-mcp won't start | Run inside the dev container; ensure `uv` on PATH. First launch may fetch the pinned `uv tool` environment (network required). |
| ocp-viewer-mcp won't start | Run `just sync` in the container so `ocp-viewer-mcp` is in `.venv` |
| ocp-viewer connection failed | Install OCP extension (devcontainer script), reload window, open viewer panel before `show_object` |
| Tools missing after rebuild | `just sync`; reload MCP in **Settings → MCP** |
| IDE shows servers but tools fail | Launchers must run in container context — check `.cursor/mcp.json` points at `.cursor/run-*.sh` |

See [MCP servers](/tools/mcp-servers) for architecture and version pins.
