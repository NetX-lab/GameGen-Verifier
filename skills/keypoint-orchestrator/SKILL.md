---
name: keypoint-orchestrator
description: Orchestrate normal keypoint testing with bounded concurrency.
---

# Keypoint Orchestrator

Use this skill when `games/{game_name}/keypoints.md` exists and a normal
evaluation run must execute one isolated worker per keypoint.

## Inputs

- `game_name`
- `run_id`
- `game_url`
- `max_concurrent`
- `screenshot_mode`
- `screenshot_interval`

## Contract

Each keypoint worker writes artifacts under:

```text
runs/{game_name}/{run_id}/keypoint_{id}/
```

Required files per keypoint:

- `result.json`
- `test_config.json`
- `test_script.mjs` or `test_script.js`
- `test_result.json`

The orchestrator should collect all completed keypoint results and write:

- `runs/{game_name}/{run_id}/summary.json`
- `runs/{game_name}/{run_id}/summary.md`

## Validation

Use the bundled validators:

```bash
python3 skills/keypoint-orchestrator/scripts/check_keypoint_count.py \
  --keypoints-file "games/${GAME_NAME}/keypoints.md" \
  --min-count 30

python3 skills/keypoint-orchestrator/scripts/validate_artifacts.py \
  --run-root "runs/${GAME_NAME}/${RUN_ID}" \
  --test-mode normal
```

Validation failure means the run is incomplete and must not be reported as a
successful evaluation.
