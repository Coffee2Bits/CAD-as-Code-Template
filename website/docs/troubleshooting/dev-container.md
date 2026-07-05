---
sidebar_position: 2
---

# Dev container troubleshooting

## Reopen in Container fails or hangs

| Symptom | Fix |
|---------|-----|
| Build never starts | Install and start [Docker](https://www.docker.com/) or [Podman](https://podman.io/) on the host ([host container runtime](/getting-started/dev-container#host-container-runtime)) |
| `docker.sock` / permission errors | On Podman, expose a Docker-compatible socket at `/var/run/docker.sock` ([host container runtime](/getting-started/dev-container#host-container-runtime)) |
| Stale image after dependency changes | **Dev Containers: Rebuild Container** |

## `uv sync` fails

- Rebuild container: **Dev Containers: Rebuild Container**
- Run `just sync` manually from repo root
- Check network access for package downloads

## Permission / UID issues

If file permission errors appear between host and container, ensure devcontainer user UID aligns with host (configured via `common-utils` feature `uid: automatic`).

## Hooks not running

```bash
just setup-hooks
```

Verify `.git/hooks/` contains pre-commit and commit-msg hooks.
