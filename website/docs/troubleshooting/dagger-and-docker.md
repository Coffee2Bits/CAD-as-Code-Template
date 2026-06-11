---
sidebar_position: 5
---

# Dagger & Docker troubleshooting

## `just ci` fails immediately

1. **Host Docker** must be running
2. Rebuild devcontainer so `/var/run/docker.sock` is mounted (`devcontainer.json`)
3. Run from repo root inside the container

## Dagger version

CI pins Dagger `0.21.4` in `.github/workflows/ci.yml` and `.devcontainer/Dockerfile`. Local CLI should match.

## Equivalent invocation

```bash
dagger call -m ./ci check --source=.
```

See [CI & Dagger](/workflows/ci-and-dagger).
