---
name: recheck-orchestrator
description: Run cross-verification on an existing evaluation run and generate recheck_summary.md plus recheck_comparison.json.
---

## Overview

This skill is the `.codex` entrypoint for rechecking a completed run.

It should use the stable direct script instead of rebuilding orchestration logic inline:

```bash
python3 scripts/run_recheck_direct.py \
  --workspace "$(pwd)" \
  --game-name "{game_name}" \
  --run-id "{run_id}" \
  --max-concurrent "{max_concurrent}"
```

The direct script launches fresh Codex sessions for each keypoint recheck, normalizes `recheck_result.json`, and writes the final comparison reports.

## Input

Parse parameters from the user request:
- `game_name` (required)
- `run_id` (required)
- `max_concurrent` (optional, current direct runner still executes sequentially for stability)
- `model` (optional)
- `reasoning_effort` (optional, default `low`)
- `step_timeout` (optional, default `600`)

## Required Behavior

1. Verify `runs/{game_name}/{run_id}/summary_report.md` exists.
2. Run the direct recheck script.
3. Report the generated artifact paths:
   - `runs/{game_name}/{run_id}/recheck_summary.md`
   - `runs/{game_name}/{run_id}/recheck_comparison.json`
4. Do not rerun Playwright.
5. Do not overwrite original `result.json`, `test_result.json`, or screenshots.

## Example

```bash
python3 scripts/run_recheck_direct.py \
  --workspace "$(pwd)" \
  --game-name tetris \
  --run-id run_tetris_normal_t300 \
  --max-concurrent 1
```
