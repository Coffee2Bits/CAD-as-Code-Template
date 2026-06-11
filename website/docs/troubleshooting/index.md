---
slug: /troubleshooting/
sidebar_position: 1
---

# Troubleshooting

## Quick routing

| Symptom | Page |
|---------|------|
| Container won't sync / permission errors | [Dev container](/troubleshooting/dev-container) |
| OCP viewer missing / blank / ESM crash | [OCP viewer](/troubleshooting/ocp-viewer) |
| MCP won't start or connect | [MCP](/troubleshooting/mcp) |
| `just ci` / Dagger fails | [Dagger & Docker](/troubleshooting/dagger-and-docker) |
| Export / discovery / CI lint failures | [Export & CI](/troubleshooting/export-and-ci) |
| release-please / Pages / branch protection | [Set up GitHub](/getting-started/github-setup) |

## Known limitations

- build123d is code-first — not a full GUI CAD app
- OCP CAD Viewer visualizes Python geometry; source remains code
- Selector-based ops can break if topology changes unexpectedly
- STEP is reliable interchange; STL is lossy
- MCP agent tools are pinned in the dev container; upstream MCP/agent APIs may still change
- VSIX install may need manual step if `code`/`cursor` CLI unavailable

## Still stuck?

[Open an issue](https://github.com/Coffee2Bits/CAD-as-Code-Template/issues) on the template repo.
