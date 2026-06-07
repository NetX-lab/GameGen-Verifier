# Playwright Tooling

This folder provides a shared Playwright installation for keypoint testing subagents.

## Setup

```bash
cd tools/playwright
npm install
npm run install:chromium
```

## Why

The `short-interaction-verification` skill resolves Playwright in this order:

1. `{project_root}/games/{game_name}/node_modules/playwright/index.mjs`
2. `{project_root}/tools/playwright/node_modules/playwright/index.mjs`

Keeping a shared install here avoids reinstalling Playwright for every generated game project.

## Reproducibility

- `tools/playwright/package.json` uses an exact Playwright version.
- Prefer committing `tools/playwright/package-lock.json` when generated.
