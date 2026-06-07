# Scripts Guide

Scripts are organized by responsibility.

## Layout

- `harness/`
  GGV-Harness implementation. Evaluation drivers
  (`run_normal_eval.py`, `run_recheck_eval.py`) plus the orchestration
  substrate (`agent_runner.py`, `quota_control.py`, `runner_utils.py`).
- `common/`
  Cross-cutting utilities: `game_catalog.py` (description directory
  helpers), `keypoint_policy.py` (keypoint-quality policy header).
- `prepare/`
  Pre-experiment preparation: `generate_games.py`, `distill_keypoints.py`,
  `export_clean_games.py`, `lint_keypoints.py`.
- `ablation/`
  Parallel-vs-sequential keypoint ablation: `parallel_keypoints.py`.
- `run_all_experiments.py`
  One-command launcher for the end-to-end pipeline.

## Public Entry Points

```bash
# One-click full run
python3 scripts/run_all_experiments.py --games neon_maze_escape tetris
python3 scripts/run_all_experiments.py --smoke

# Direct evaluation entry points
python3 harness/run_normal_eval.py \
  --workspace "$(pwd)" --game-name neon_maze_escape --run-id demo_normal
python3 harness/run_recheck_eval.py \
  --workspace "$(pwd)" --game-name neon_maze_escape --run-id demo_normal

# Preparation
python3 scripts/prepare/generate_games.py --skip-existing --refresh-changed --parallel 4
python3 scripts/prepare/distill_keypoints.py --games neon_maze_escape
python3 scripts/prepare/export_clean_games.py --force

# Ablation
python3 scripts/ablation/parallel_keypoints.py --games neon_maze_escape --repeats 3
```

## Resume After Quota

When the backend coding-agent quota is exhausted, harness drivers return
`PAUSED` (a non-zero exit) instead of silently restarting. Resume the
underlying driver in place:

```bash
python3 harness/run_normal_eval.py \
  --workspace "$(pwd)" --game-name <game> --run-id <id> --resume-run

python3 harness/run_recheck_eval.py \
  --workspace "$(pwd)" --game-name <game> --run-id <id>
```

Notes:
- `generate_games.py --skip-existing --refresh-changed` skips games whose
  description hash still matches, so reruns only regenerate missing or stale
  outputs.
- `run_normal_eval.py --resume-run` reuses
  `runs/<game>/<run_id>/keypoints.snapshot.md` and skips already-resolved
  keypoints.
- `run_recheck_eval.py` skips keypoints that already have a
  `recheck_result.json` — pass the same `--run-id` to continue.
- The launcher (`run_all_experiments.py`) has no resume flag of its own;
  rerun it with the same `--games` and let each phase's per-game logic
  pick up where it left off (prepare phase is `--skip-existing` by default;
  ours phase will assign a fresh `run_id` per repeat).

## Context Flow

Normal evaluation passes context in this chain:

```text
run_all_experiments.py
  -> harness/run_normal_eval.py
  -> skills/auto-eval/scripts/dev_server_lifecycle.sh
  -> games/<game>/keypoints.md
  -> codex exec | claude -p (per --backend) for each keypoint worker
       loads skills/{generative-state-construction,short-interaction-verification}
  -> runs/<game>/<run_id>/keypoint_<id>/{result.json, screenshots/}
  -> runs/<game>/<run_id>/{summary_report.md, evaluation_report.md}
```

Explicit worker fields:
- `game_name`, `keypoint_id`, `category`, `description`, `output_dir`,
  `game_url`, `project_root`, `screenshot_mode`, `screenshot_interval`,
  `prestate`, `instruction`, `expected`.

Implicit worker context from the workspace:
- `games/<game>/src`, `games/<game>/data.md`,
  `games/<game>/state_injection_api.md`, `skills/...`.

## Design Rule

When adding a new script:

1. Harness driver / orchestration substrate -> `harness/`.
2. Cross-cutting utility (description catalog, keypoint policy) -> `common/`.
3. Generated-asset preparation -> `prepare/`.
4. Ablation-only flow -> `ablation/`.

If a new file does not fit one of those buckets, it probably should not be a
new top-level script. The one-click launcher (`run_all_experiments.py`) is
the only top-level entry point.
