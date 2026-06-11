---
sidebar_position: 2
---

# Dev container troubleshooting

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
