# Documentation site

[Docusaurus](https://docusaurus.io/) site for **CAD-as-Code-Template**.

**Published:** https://coffee2bits.github.io/CAD-as-Code-Template/

## Local development

Requires Node.js 20 (included in the dev container via `node` feature).

```bash
just docs-install   # npm ci (also runs on container postCreate)
just docs-serve     # dev server at http://localhost:3000
just docs-build     # production build → website/build/
```

Rollout tracker: [DOCS_ROLLOUT_PLAN.md](./DOCS_ROLLOUT_PLAN.md)
