---
sidebar_position: 3
---

# Testing

```bash
just test
just test -v tests/test_sphere.py   # extra pytest args
```

## What to assert

- Model validity (no invalid solids)
- Bounding box, volume, hole counts
- Export round-trip where applicable
- MakerRepo discovery: `assert "sphere" in names` (not exclusive sets)

## Golden fixtures

Commit STEP/STL under `tests/fixtures/` only when intentional regression fixtures are needed.

## Test design

| Prefer | Avoid |
|--------|-------|
| `assert "sphere" in names` | `assert names == {"sphere"}` |
| Scoped export checks per artifact | Requiring every artifact in unrelated tests |
| Explicit geometry assertions | Loosening unrelated bounds to pass |
