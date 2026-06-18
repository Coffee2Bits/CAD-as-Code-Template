# Documentation site

[Docusaurus](https://docusaurus.io/) site for **CAD-as-Code-Template**.

**Published:** https://coffee2bits.github.io/CAD-as-Code-Template/

## Local development

Requires Node.js 20 (included in the dev container via `node` feature).

```bash
just docs-install   # npm ci (also runs on container postCreate)
just docs-serve     # dev server at http://localhost:3000 (foreground)
just docs-serve-bg  # background dev server (idempotent; auto-started in devcontainer)
just docs-build     # production build → website/build/
```

In the dev container, `postStartCommand` runs `post-start.sh`, which starts the Docusaurus dev server in the background via `start-docs.sh` and opens port **3000** in your browser.
