---
name: auto-eval
description: Run the full game-gen-eval pipeline in normal mode (state injection + visual interaction verification) from a generated game. Use when you want an end-to-end evaluation that produces summary_report.md and evaluation_report.md.
---

## Input

Parse parameters from the user request (support both styles):
- Key/value: `game_name=shooter_game run_id=20260301_120000 max_concurrent=3`
- Positional: `shooter_game 20260301_120000`

Required:
- `game_name`

Optional:
- `run_id` (default: timestamp `YYYYMMDD_HHMMSS`)
- `max_concurrent` (default: 3)
- `game_url` (if provided, skip starting the dev server and use this URL)
- `screenshot_mode` (`sequence` by default, use `standard` only for an explicit low-storage override)
- `screenshot_interval` (default: 200 ms when `screenshot_mode=sequence`)

## Prerequisites

Verify required files exist:
- `descriptions_example/{game_name}.md`
- `games/{game_name}/src/`
- `games/{game_name}/data.md`
- `games/{game_name}/state_injection_api.md`
- `games/{game_name}/package.json`

If any are missing, stop and report which files are missing.

## Pipeline (Normal Mode)

### Step 0: Resolve run_id and output dir

If `run_id` is missing, generate with:
```bash
run_id=$(date +%Y%m%d_%H%M%S)
```
Output root: `runs/{game_name}/{run_id}/`

### Step 1: Distill keypoints

Run the `distill-verified-keypoints` skill on `descriptions_example/{game_name}.md`.

### Step 2: Analyze implementation

Run `analyze-game-implementation` with:
```
game_name={game_name}
run_id={run_id}
```

### Step 3: Start game server (unless game_url provided)

Use the bundled lifecycle script (deterministic and reusable):

If `game_url` is provided:
```bash
REPO_ROOT="$(pwd)"
eval "$("$REPO_ROOT/skills/auto-eval/scripts/dev_server_lifecycle.sh" start \
  --repo-root "$REPO_ROOT" \
  --game-name "{game_name}" \
  --game-url "{game_url}")"
```

If `game_url` is not provided:
```bash
REPO_ROOT="$(pwd)"
eval "$("$REPO_ROOT/skills/auto-eval/scripts/dev_server_lifecycle.sh" start \
  --repo-root "$REPO_ROOT" \
  --game-name "{game_name}" \
  --bootstrap-playwright)"
```

### Step 4: Keypoint orchestration (normal)

Run `keypoint-orchestrator` with:
```
game_name={game_name}
run_id={run_id}
max_concurrent={max_concurrent}
test_mode=normal
game_url={GAME_URL or game_url}
screenshot_mode={screenshot_mode}
screenshot_interval={screenshot_interval}
```

### Step 4.5: Validate artifact contract (required before final report)

```bash
python3 "$REPO_ROOT/skills/keypoint-orchestrator/scripts/validate_artifacts.py" \
  --repo-root "$REPO_ROOT" \
  --game-name "{game_name}" \
  --run-id "{run_id}" \
  --test-mode normal \
  --json-output "$REPO_ROOT/runs/{game_name}/{run_id}/validation_report.json"
```

If validation fails, stop and repair missing/invalid artifacts before generating `evaluation_report.md`.

### Step 5: Stop server (if started here)

```bash
"$REPO_ROOT/skills/auto-eval/scripts/dev_server_lifecycle.sh" stop \
  --state-file "${SERVER_STATE_FILE:-}" \
  --server-pid "${SERVER_PID:-}" >/dev/null
```

### Step 6: Generate final report

Summarize `summary_report.md` and write:
- `runs/{game_name}/{run_id}/evaluation_report.md`

Suggested format:
```markdown
# Evaluation Report: {game_name}

## Summary
- Total: X
- Passed: Y
- Failed: Z
- Pass Rate: Y/X%

## Results
| Keypoint | Status | Confidence |
|----------|--------|------------|
| 1        | PASS   | 95%        |
```

## Output Structure

```
runs/{game_name}/{run_id}/
├── keypoint_1/
│   ├── test_config.json
│   ├── test_script.mjs
│   ├── test_result.json
│   ├── screenshots/
│   │   ├── before.png
│   │   └── after.png
│   └── result.json
├── keypoint_2/
│   └── ...
├── summary_report.md
└── evaluation_report.md
```
