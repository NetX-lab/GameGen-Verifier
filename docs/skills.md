# Skills (Verifier Prompts)

The `skills/` directory at the repository root holds the worker-side prompts
that turn a generic coding-agent CLI into a verifier worker. The same files
are consumed by both Codex CLI and Claude Code, but each backend discovers
them via a different convention.

```
skills/
├── analyze-game-implementation/
│   └── SKILL.md
├── auto-eval/
│   ├── SKILL.md
│   └── scripts/
│       └── dev_server_lifecycle.sh
├── cross-verification/
│   └── SKILL.md
├── distill-verified-keypoints/
│   ├── SKILL.md
│   └── references/
│       └── keypoint.md
├── game-gen-with-data/
│   ├── SKILL.md
│   └── references/
│       ├── data_md_example.md
│       └── state_injection_api_example.md
├── generative-state-construction/
│   └── SKILL.md
├── keypoint-orchestrator/
│   ├── SKILL.md
│   ├── references/
│   │   ├── fixed_batch_concurrency_pattern.md
│   │   └── minimal_context_principle.md
│   └── scripts/
│       ├── check_keypoint_count.py
│       └── validate_artifacts.py
├── recheck-orchestrator/
│   └── SKILL.md
└── short-interaction-verification/
    └── SKILL.md
```

Every `SKILL.md` opens with a YAML front-matter block that both backends
parse:

```yaml
---
name: short-interaction-verification
description: ...
---
```

## Codex CLI

Codex auto-discovers skills from a `<workdir>/.codex/skills/<name>/SKILL.md`
directory when invoked with `--cd <workdir>`. The repository ships a directory
symlink so this happens automatically:

```text
.codex/skills -> ../skills
```

Verify:

```bash
$ codex exec --cd "$(pwd)" --sandbox read-only --skip-git-repo-check \
    "List the SKILL files under .codex/skills/. Names only."
analyze-game-implementation
auto-eval
cross-verification
distill-verified-keypoints
game-gen-with-data
generative-state-construction
keypoint-orchestrator
recheck-orchestrator
short-interaction-verification
```

After this, prompts like `Use the auto-eval skill with parameters: ...`
are auto-resolved by Codex to the corresponding `SKILL.md`. Nested skill
references inside a skill body are also resolved.

If your platform did not preserve the symlink (e.g. Windows without
symlink support), recreate it:

```bash
# Linux / macOS
ln -sfn ../skills .codex/skills
```

```powershell
# Windows PowerShell (Administrator or Developer Mode)
New-Item -ItemType SymbolicLink -Force -Path .codex\skills -Target ..\skills
```

For user-global install:

```bash
mkdir -p ~/.codex/skills
cp -r skills/* ~/.codex/skills/
```

## Claude Code

Claude Code uses the **plugin** convention: a directory with a
`.claude-plugin/plugin.json` manifest is treated as a plugin, and any
`skills/<name>/SKILL.md` inside it becomes a slash command of the form
`<plugin-name>:<skill-name>`.

The repository ships `.claude-plugin/plugin.json` at the top level,
declaring itself as the `gamegen-verifier` plugin. Use it per-session via
`--plugin-dir .` — local-path install via `claude plugin install` is not
supported by current Claude Code releases, so we do not document it.

```bash
# Per-session, no global registration:
claude --plugin-dir . -p "..."
```

Validate the manifest:

```bash
$ claude plugin validate .
Validating plugin manifest: .../.claude-plugin/plugin.json
✔ Validation passed
```

Verify the plugin loads:

```bash
$ claude --plugin-dir . -p \
    "List names of slash commands you have from the gamegen-verifier plugin. One per line."
gamegen-verifier:cross-verification
gamegen-verifier:recheck-orchestrator
gamegen-verifier:keypoint-orchestrator
gamegen-verifier:short-interaction-verification
gamegen-verifier:distill-verified-keypoints
gamegen-verifier:analyze-game-implementation
gamegen-verifier:game-gen-with-data
gamegen-verifier:generative-state-construction
gamegen-verifier:auto-eval
```

In an interactive Claude Code session opened with `claude --plugin-dir .`,
type `/gamegen-verifier:auto-eval` (tab-complete works) to invoke a skill.

## How each backend consumes a skill in this repo

- **Codex**: prompts in this repo say `Use the auto-eval skill ...`. Codex
  resolves the reference against `.codex/skills/auto-eval/SKILL.md` and
  loads it as worker context. Nested skill references inside a skill are
  recursively resolved.

- **Claude Code (interactive)**: with `--plugin-dir .` (or after a global
  install), users invoke skills explicitly via `/gamegen-verifier:auto-eval`.

- **Claude Code (driven by `harness/agent_runner.py`)**: the harness
  invokes `claude -p` with `--append-system-prompt <SKILL.md content>`,
  reading the outermost skill from `skills/<name>/SKILL.md` and inlining it
  as the session's system prompt. Single-skill flows match Codex behavior
  exactly. Deeply nested skill references inside a skill body are not
  recursively expanded by the harness today; if you need that for a Claude
  run, expand the references manually in the prompt or extend
  `agent_runner.py`.

## Adding a new skill

1. Create `skills/<my-skill>/SKILL.md` with the YAML front-matter shown
   above. Optional supporting files go under `skills/<my-skill>/references/`
   or `skills/<my-skill>/scripts/`.
2. Both backends pick it up immediately:
   - Codex via `.codex/skills/<my-skill>/SKILL.md` (the symlink).
   - Claude Code via the existing `.claude-plugin/plugin.json` (the new
     skill becomes `gamegen-verifier:<my-skill>`).
3. Add a row to `docs/harness.md` if the skill is part of the harness data
   flow.
