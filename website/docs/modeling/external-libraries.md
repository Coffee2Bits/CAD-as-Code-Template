---
sidebar_position: 4
---

# External part libraries

Community libraries extend [build123d](https://build123d.readthedocs.io/). Listed as **commented-out** optional dependencies in [`pyproject.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/pyproject.toml) — uncomment and run `uv sync` before importing.

Upstream index: [build123d external libraries](https://build123d.readthedocs.io/en/latest/external.html#part-libraries).

| Library | Scope | Source | Docs |
|---------|-------|--------|------|
| [bd_warehouse](https://github.com/gumyr/bd_warehouse) | Fasteners, bearings, flanges, pipes, threads, sprockets | [GitHub](https://github.com/gumyr/bd_warehouse) | [RTD](https://bd-warehouse.readthedocs.io/) |
| [bd_beams_and_bars](https://gitlab.com/experimentslabs/3d/bd_beams_and_bars) | Structural beams and bars (Git install) | [GitLab](https://gitlab.com/experimentslabs/3d/bd_beams_and_bars) | [Site](https://bd-beams-and-bars.3d.experimentslabs.com/) |
| [py_gearworks](https://github.com/GarryBGoode/py_gearworks) | Gears and drivetrains | [GitHub](https://github.com/GarryBGoode/py_gearworks) | [README](https://github.com/GarryBGoode/py_gearworks) |
| [bd-vslot](https://github.com/keeeal/bd-vslot) | V-Slot extrusion profiles | [GitHub](https://github.com/keeeal/bd-vslot) | [RTD](https://bd-vslot.readthedocs.io/) |

## Enable in this repo

```toml
# "bd_warehouse>=0.2.0",
# "bd-vslot",
# "bd_beams_and_bars @ git+https://gitlab.com/experimentslabs/3d/bd_beams_and_bars.git",
# "py_gearworks @ git+https://github.com/GarryBGoode/py_gearworks.git",
```

## Integration pattern

Add **thin wrappers** in `cad/parts/` that call library builders — do not reimplement ISO tables or catalog geometry.

- Use `simple=True` (default) on bd_warehouse fasteners in tests unless modeled threads are required
- Return `.part` (or equivalent) from `make_*` builders so tests and assemblies stay consistent

Agents: when to reach for each library — [AGENTS.md external part libraries](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/AGENTS.md#external-part-libraries).
