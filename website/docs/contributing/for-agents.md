---
sidebar_position: 2
---

# For agents

:::info Read the repo contract first

**[AGENTS.md](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/AGENTS.md)** is the authoritative agent guide. This page is a pointer — do not treat the docs site as a substitute.

:::

## Summary

1. **Structure** — parts in `cad/parts/`, assemblies in `cad/assemblies/`, three-layer pattern (`make_*` → `@artifact` / `@customizable`)
2. **Completion gate** — `just ci` or `just quality && just export-smoke` before marking work done
3. **Visual verify** — `just view` after geometry edits to `cad/`
4. **MakerRepo** — `from mr import artifact, customizable, cached`; decorators on entry points only
5. **External libs** — use bd_warehouse, bd-vslot, etc. for catalog geometry; thin-wrap in `cad/parts/`
6. **`just` command tests** — destructive recipes (`just init`, `just template-apply`, …) only in [`tests/functional/`](https://github.com/Coffee2Bits/CAD-as-Code-Template/tree/main/tests/functional) via `isolated_repo` + `run_just()` — never on the real repo root ([AGENTS.md → Testing just commands](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/AGENTS.md#testing-just-commands-agents))

## Documentation work

Follow [`website/DOCS_ROLLOUT_PLAN.md`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/website/DOCS_ROLLOUT_PLAN.md) and the **Documentation** section in AGENTS.md.

### No doc drift (mandatory)

Whenever you change code, config, `justfile`, or workflows:

1. Open the matching guide under [`website/docs/`](https://github.com/Coffee2Bits/CAD-as-Code-Template/tree/main/website/docs) and confirm it still describes **current** behavior.
2. **Search** `website/docs/`, `README.md`, `.github/GITHUB_SETUP.md`, and `cad_tooling/README.md` for the **old** command names, paths, and strings you replaced.
3. **Update every reference** in the same change — links, tables, and examples included.

Full rules: **[Keep docs in sync (mandatory)](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/AGENTS.md#keep-docs-in-sync-mandatory)** in AGENTS.md.

**Template identity:** edit [`template.repo.toml`](https://github.com/Coffee2Bits/CAD-as-Code-Template/blob/main/template.repo.toml), then `just init` — or pass `just init --owner … --repo …`. [Replace template identity](/getting-started/github-setup#replace-template-identity-in-your-repo).
