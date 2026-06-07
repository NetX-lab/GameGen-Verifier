---
name: analyze-game-implementation
description: Analyze game source code and write a concise implementation summary for downstream testing. Use when keypoint verification needs implementation-aware controls, physics, and timing mapping.
---

## Overview

Reads game source code, extracts key insights, and **outputs a concise analysis to the conversation**.

Also writes the same analysis to a file under `runs/` so downstream worker runs (which may not inherit conversation context) can reuse it reliably.

Contract references:
- Canonical API contract: `docs/inter_skills_structure.md`
- Workflow graph and orchestration semantics: `docs/agentic_workflow_graph_api.md` (non-canonical)

## Input

Parse parameters from the user request (support both styles):
- Key/value: `game_name=mario_game run_id=20260207_235942`
- Positional: `mario_game 20260207_235942`

Required:
- `game_name`

Optional:
- `run_id` (default: generate `YYYYMMDD_HHMMSS` via `date +%Y%m%d_%H%M%S`)

Set:
- `output_dir = runs/{game_name}/{run_id}/`

## Files to Read

1. `games/{game_name}/src/` - ALL source files
2. `games/{game_name}/data.md` - state schema, controls, physics
3. `games/{game_name}/keypoints.md` - what to test

## Output

**Outputs:**
1. Write the analysis to the conversation (human-readable summary).
2. Write the same content to: `runs/{game_name}/{run_id}/implementation_analysis.md`

This avoids relying on context inheritance and keeps downstream testing deterministic.

## Workflow

1. Resolve `game_name` and `run_id` from the user request. If `run_id` is missing, compute it with Bash: `date +%Y%m%d_%H%M%S`.
2. Create `output_dir` with Bash: `mkdir -p runs/{game_name}/{run_id}`.
3. Read:
   - `games/{game_name}/src/**`
   - `games/{game_name}/data.md`
   - `games/{game_name}/keypoints.md`
4. Produce the analysis in the exact "Output Format" section below (markdown).
5. Write the analysis to `runs/{game_name}/{run_id}/implementation_analysis.md`.

## Analysis Content

Analyze and document:

### 1. Input → Code Mapping
```markdown
## Controls Mapping
| Action | Key | Code Effect |
|--------|-----|-------------|
| Move Right | ArrowRight | player.velocityX = 5 |
| Jump | Space | player.velocityY = -10 (if onGround) |
```

### 2. Physics & Timing
```markdown
## Physics
- Frame Rate: 60fps (16.67ms/frame)
- Player Speed: 5px/frame → 300px/second
- Gravity: 0.5px/frame²
- Jump Duration: ~40 frames to apex
```

### 3. Collision Detection
```markdown
## Collision
- Method: AABB rectangle overlap
- Check Frequency: Every frame after position update
- Player-Item: Immediate collection, item.active = false
- Player-Enemy: Side contact = damage, Top contact = kill enemy
```

### 4. State Transitions
```markdown
## State Transitions
| Trigger | Condition | Result |
|---------|-----------|--------|
| Collect Mushroom | player.state == 'small' | player.state = 'big', height = 40 |
| Take Damage | player.state == 'big' | player.state = 'small', height = 20 |
```

### 5. Keypoint-Specific Guidance
```markdown
## Keypoint Implementation Notes

### Keypoint 1: Player moves right
- Initial X: any valid position (e.g., 400)
- Action: ArrowRight for 1000ms = 60 frames × 5px = 300px
- Verify: finalState.player.x > initialState.player.x + 250

### Keypoint 2: Boundary collision
- Initial X: canvas.width - player.width - 10 (near right edge)
- Action: ArrowRight for 500ms
- Verify: finalState.player.x <= canvas.width - player.width
```

## Output Format (to conversation)

Output a condensed view in the following format:

```markdown
# Game Analysis: {game_name}

## Controls Mapping
| Action | Key | Code Effect |
|--------|-----|-------------|
| Move Right | ArrowRight | player.velocityX = 5 |
| Jump | Space | player.velocityY = -10 (if onGround) |

## Physics & Timing
- Frame Rate: 60fps
- Player Speed: 5px/frame → 300px/second
- Gravity: 0.5px/frame²

## Collision Detection
- Method: AABB
- Player-Item: Immediate collection
- Player-Enemy: Side = damage, Top = kill

## State Transitions
- Collect Mushroom: small → big
- Take Damage: big → small

## Keypoint Testing Guidance

### Keypoint 1: Player moves right
- Duration: 1000ms → ~300px movement
- Verify: x increased by ~250+

### Keypoint 2: Boundary collision
- Position near edge, move toward boundary
- Verify: x <= canvas.width - player.width
```

## Why This Design?

1. **Reusable**: Put the analysis to `runs/`, and downstream worker steps can read it directly
2. **More Robust**: Does not rely on context inheritance semantics
3. **Token saving**: worker steps read only the necessary summary instead of the complete source code
