# GameGen-Verifier: State-Grounded Verification for Game Generation

This repository is the reference implementation of **GameGen-Verifier** and
its execution substrate **GGV-Harness**. It contains the experiment pipeline
used to generate, evaluate, and aggregate browser-game verification tasks.
This is an anonymized code release for double-blind review: generated games,
run outputs, logs, screenshots, cached dependencies, and private
configuration files are intentionally not included.

## Repository Layout

Core artifacts (the two halves of GGV-Harness):

- `harness/`: GGV-Harness Python implementation -- evaluation drivers, backend abstraction, queue/quota control.
- `skills/`: worker-side prompts (verifier contracts) consumed by both backends -- see [docs/skills.md](docs/skills.md). Codex finds them via the `.codex/skills` symlink; Claude Code finds them via the top-level `.claude-plugin/plugin.json` (the repo registers itself as the `gamegen-verifier` plugin).

Pipeline glue:

- `scripts/run_all_experiments.py`: one-command launcher for the end-to-end pipeline.
- `scripts/prepare/`: generate games, distill keypoints, and export hook-stripped copies.
- `scripts/ablation/`: parallel-vs-sequential keypoint ablation.
- `scripts/common/`: cross-cutting utilities (game catalog, keypoint policy).

Inputs and (git-ignored) outputs:

- `games/`: generated evaluation-enabled game projects (not committed).
- `games_clean/`: generated copies with the evaluation adapter stripped (not committed).
- `runs/`: generated evaluation outputs (not committed).
- `experiments/`: per-launch summary directories written by the launcher (not committed).
- `tools/playwright/`: shared Playwright dependency declaration.
- `tests/`: unit tests for the pipeline code.
- `docs/harness.md`: tour of the harness substrate (where each piece lives).
- `docs/pipeline.md`: end-to-end data flow.

## Quickstart

Three steps from a fresh clone to a verified install (no backend calls
needed for steps 1 and 2):

```bash
# 1. Install Python and Playwright dependencies
python3 -m pip install -r requirements.txt
( cd tools/playwright && npm install && npm run install:chromium )

# 2. Verify the install (runs unit tests + --help on every entry point)
python3 scripts/run_all_experiments.py --smoke

# 3. Authenticate the coding-agent backend, then launch one game
codex login                                 # one-time, only for --backend codex
python3 scripts/run_all_experiments.py --games tetris
```

Step 3 launches the full pipeline (`prepare -> ours -> recheck`) for one
game. End-to-end runtime is roughly **5–15 minutes per game** depending on
backend latency and keypoint count. Outputs land under `runs/tetris/`
and `experiments/all_runs/launch_<timestamp>/summary.json`.

## Available Example Games

`descriptions_example/` ships with 10 game descriptions in the input format
the pipeline expects. Pick any of them as `--games <name>`:

```text
neon_maze_escape       card_battle_coliseum    monument_valley
tetris                 block_world_frontier    plants_vs_zombies
orbital_invaders       property_tycoon_3d
gem_match_temple       temple_run_2
```

Drop a new `<game_name>.md` into `descriptions_example/` to add your own;
no other registration is required.

## Requirements

- Python 3.11 or newer
- Node.js 20 or newer, npm
- A coding-agent CLI backend for full runs -- one of `codex` or `claude`
  must be on your `PATH`. Authenticate it once before launching:
  - `codex` -> `codex login` (uses your OpenAI account)
  - `claude` -> `claude login` (uses your Anthropic account)
  - Pass `--backend <name>` to select between them.

Generated games are Vite/TypeScript projects. Their per-game dependencies
are installed automatically by the evaluation lifecycle script when a game
is run.

## One-Click Run

```bash
# Full pipeline for one or more games
python3 scripts/run_all_experiments.py --games neon_maze_escape tetris

# Pick phases explicitly (default is "prepare ours")
python3 scripts/run_all_experiments.py \
  --games tetris \
  --phases prepare ours ablation \
  --repeats 3 \
  --backend codex

# Local smoke check (no backend calls)
python3 scripts/run_all_experiments.py --smoke
```

See `python3 scripts/run_all_experiments.py --help` for the full flag list.

## Manual Pipeline

If you want finer control than the launcher, the same steps run as
individual scripts:

```bash
# 1. Prepare (one-time per game)
python3 scripts/prepare/generate_games.py --games <game_name> --skip-export
python3 scripts/prepare/distill_keypoints.py --games <game_name>
python3 scripts/prepare/export_clean_games.py --games <game_name> --force

# 2. Evaluate
python3 harness/run_normal_eval.py \
  --workspace "$(pwd)" --game-name <game_name> --run-id demo_normal
python3 harness/run_recheck_eval.py \
  --workspace "$(pwd)" --game-name <game_name> --run-id demo_normal

# 3. Optional: parallel-vs-sequential ablation
python3 scripts/ablation/parallel_keypoints.py \
  --games <game_name> --repeats 3
```

Expected files after `prepare`:

```text
games/<game_name>/{src/, package.json, data.md, state_injection_api.md, keypoints.md}
games_clean/<game_name>/package.json
```

## Expected Output

Normal evaluation (`harness/run_normal_eval.py`) writes:

```text
runs/<game_name>/<run_id>/summary_report.md      # per-keypoint PASS/FAIL listing
runs/<game_name>/<run_id>/evaluation_report.md   # tabular summary
runs/<game_name>/<run_id>/keypoint_<id>/result.json
runs/<game_name>/<run_id>/keypoint_<id>/screenshots/{before,after}.png
```

Recheck (`harness/run_recheck_eval.py`) writes:

```text
runs/<game_name>/<run_id>/recheck_summary.md
runs/<game_name>/<run_id>/recheck_comparison.json
runs/<game_name>/<run_id>/keypoint_<id>/recheck_result.json
```

The launcher (`scripts/run_all_experiments.py`) additionally writes a
per-launch summary at:

```text
experiments/all_runs/launch_<timestamp>/summary.json
```

`runs/` and `experiments/` are git-ignored.

## Documentation

- `docs/harness.md` -- where the harness substrate lives across
  `harness/`, `scripts/common/`, and `skills/`.
- `docs/skills.md` -- skill format, install, and how Codex / Claude Code each
  discover and consume them.
- `docs/pipeline.md` -- end-to-end data flow.
- `scripts/README.md` -- per-directory script guide and resume protocol.

## Anonymization Notes

This release ships as a single **`Initial anonymized release`** commit on
`main`, authored by `Anonymous Authors <anonymous@example.invalid>`. No
modification history, no real author email, no real author name.

Generated artifacts, local paths, personal agent configuration, cached
dependencies, notebooks, paper figures, and result files are intentionally
not included.

**If you redistribute this release as a tarball or zip rather than a fresh
git clone**, regenerate the `.git/` directory first (e.g. `rm -rf .git &&
git init && git add -A && git -c user.name='Anonymous Authors' -c
user.email='anonymous@example.invalid' commit -m 'Initial anonymized
release'`) -- otherwise the bundled `.git/config` would carry the source
clone URL and the local reflog might carry interim commits.

Before uploading to an anonymous hosting service, also verify that the
hosting account name, repository URL, license / CITATION files, and any
added data files do not reveal author identity.
