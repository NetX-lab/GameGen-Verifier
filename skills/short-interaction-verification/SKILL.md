---
name: short-interaction-verification
description: Execute Playwright verification for one concrete short interaction and write result artifacts. Use as the normal-mode `keypoint-tester` verification step after `generative-state-construction`, not as a standalone top-level workflow.
---

## Overview

Subagent execution step for ONE keypoint. This skill consumes concrete interaction data (prefer `short_interaction_info.json` + `test_config.json`), injects the game into the target precondition, runs a short visual interaction, and writes a hybrid verification bundle.

This skill is preloaded into `keypoint-tester` and should run after `generative-state-construction`.

Contract references:
- Canonical API contract: `docs/inter_skills_structure.md`
- Workflow graph and orchestration semantics: `docs/agentic_workflow_graph_api.md` (non-canonical)

## Input (from Task prompt)

Parse parameters from Task prompt (`key=value`, one per line):
- `game_name`
- `keypoint_id`
- `category`
- `description`
- `output_dir`
- `game_url`
- `project_root`
- `analysis_path` (optional)
- `screenshot_mode` (optional: `standard` or `sequence`, default: `sequence`)
- `screenshot_interval` (optional: interval in ms for sequence mode, default: `200`)
- `prestate`
- `instruction`
- `expected`

## Required Inputs on Disk

Prefer reading:
- `{output_dir}/short_interaction_info.json`
- `{output_dir}/test_config.json`

Fallback (if missing):
- reconstruct `test_config.json` using prompt + `games/{game_name}/data.md` + `games/{game_name}/state_injection_api.md`

## Workflow

### 1. Validate/Prepare Files

Ensure:
- `{output_dir}/`
- `{output_dir}/screenshots/`
- `{output_dir}/test_config.json`

### 2. Create `test_script.mjs`

Write `{output_dir}/test_script.mjs` and run it to produce:
- `{output_dir}/test_result.json`
- `{output_dir}/screenshots/before.png`
- `{output_dir}/screenshots/after.png`
- optional `{output_dir}/screenshots/frame_*.png` when `screenshot_mode=sequence`

Script requirements:
- wait for `window.gameReady === true`
- inject state via `window.injectGameState(...)`
- take `screenshots/before.png` before the first action
- if `screenshot_mode=sequence`, arm the capture loop before the first action and capture frames in chronological order:
  - `frame_000.png` must be an immediate pre-action anchor at interaction time `0 ms`
  - `frame_001.png+` must be subsequent samples captured every `screenshot_interval` ms while interactions execute
  - do not start the first action before the sequence capture loop is armed
- execute configured interactions
- take `screenshots/after.png` after all actions and any planned settling wait complete
- pause and read `window.getGameState()`
- write raw result to `test_result.json`

When sequence screenshots are enabled, include screenshot metadata in `test_result.json`:
- `screenshots.before`
- `screenshots.after`
- `screenshots.changed`
- `screenshots.sequence = { mode, interval_ms, frames, frame_times_ms }`
  - `frames` must remain a chronological list of relative paths
  - `frame_times_ms[0]` must be `0` for `frame_000.png`

Playwright resolution order:
1. `{project_root}/games/{game_name}/node_modules/playwright/index.mjs`
2. `{project_root}/tools/playwright/node_modules/playwright/index.mjs`

Hard browser constraint:
- Launch only Playwright-bundled Chromium in headless mode
- Use `chromium.launch({ headless: true })`
- Do not use `channel`
- Do not use `executablePath`
- Do not fall back to system Chrome, Edge, Brave, or any other installed browser
- Do not open a headed browser window for fallback or debugging in this workflow
- If bundled Chromium launch fails, write an `INCOMPLETE` result with the browser launch error instead of trying another browser

Run command:
- `node {output_dir}/test_script.mjs`

### 3. Verify Injected State + Visual Outcome and Write `result.json`

Normal mode is a hybrid workflow:
- use injected state to position the run close to the requested precondition
- use short visual interaction plus sequence screenshots to exercise the target behavior
- use runtime state as supporting evidence for final judgment
- use `verification_contract` to distinguish true success from nearby false positives

Always write:
- `prestate`, `instruction`, `expected`
- `actual_before_state`, `actual_after_state`
- `status` (`PASS`, `FAIL`, or `INCOMPLETE`)
- `reasoning` (3-5 concise strings)
- `explanation` (complete natural-language explanation)

Decision policy (binary verdict required; INCOMPLETE is reserved for infrastructure failure only):
- `PASS`: the injected precondition is visibly/runtime-consistently established, the interaction executes, required runtime fields match expectation, required observations in `verification_contract` are supported by the evidence, and forbidden observations are not supported by the evidence
- `FAIL`: the run produced any usable observation that contradicts the expected behavior, OR the implementation could not sustain/expose the precondition state needed to test the keypoint, OR a required observation was not visibly satisfied. Per the falsification-oriented evaluation paradigm: failure to instantiate or observe the keypoint scenario is itself evidence against the specification.
- `INCOMPLETE`: ONLY when the verification harness itself failed (Playwright/Chromium crash, server unreachable, worker timeout before any observation, OS-level resource exhaustion). NOT for "the game didn't behave clearly" — that's `FAIL`.

Important normal-mode rules:
- Do not judge only from final state equality when the keypoint depends on visible feedback, warning cues, animation phases, or transient interaction effects.
- If `precondition_state` did not actually place the game near the intended scenario, the implementation failed to support the keypoint's required state — write `FAIL` with `state_grounding_failed: true` in the explanation, not `INCOMPLETE`.
- If visual/runtime evidence is ambiguous after honest interpretation, default to `FAIL` (the implementation did not produce clear evidence of correctness). `INCOMPLETE` is only for harness-level breakage that the orchestrator should retry.
- `visual_verification` is not optional in spirit; populate it whenever screenshots were captured successfully, even if state verification is the stronger signal.
- When `verification_contract` is present, explicitly address:
  - whether the scenario-establishment checks were satisfied
  - which required observations were confirmed
  - whether any forbidden observation appeared
- Do not award `PASS` if the run merely reached a superficially similar state while violating a forbidden observation.

Write `{output_dir}/result.json`:

```json
{
  "keypoint_id": "1",
  "category": "State Transition",
  "description": "...",
  "prestate": "Player is one tile before the checkpoint.",
  "instruction": "Move right for one step.",
  "expected": "Checkpoint flag visibly activates and save state increments.",
  "actual_before_state": "Injected prestate shows the player immediately left of the checkpoint with no active checkpoint VFX.",
  "actual_after_state": "Player overlaps the checkpoint, the flag is lit, and runtime state reports checkpointIndex=3.",
  "status": "PASS",
  "passed": true,
  "confidence": 95,
  "state_verification": {
    "passed": true,
    "expected": {},
    "actual": {}
  },
  "verification_contract_review": {
    "precondition_checks": ["Checkpoint setup is visibly established before the action."],
    "required_observations": ["Checkpoint flag activates after overlap."],
    "forbidden_observations": ["Player simply passes through without activation."],
    "decision_rule": "all required, none forbidden",
    "required_satisfied": true,
    "forbidden_triggered": false
  },
  "visual_verification": {
    "passed": true,
    "before_observation": "...",
    "after_observation": "...",
    "reasoning": [
      "Before screenshot shows the player one tile before the checkpoint.",
      "After screenshot shows the checkpoint activated with the expected visual feedback.",
      "Sequence frames show the transition happening after the injected start state."
    ]
  },
  "reasoning": [
    "Injected prestate established the intended near-checkpoint setup.",
    "Sequence screenshots show the interaction progressing from the injected state into the checkpoint activation.",
    "Runtime verification matches the expected checkpoint index update.",
    "The required observation is present and the forbidden near-miss behavior is absent.",
    "State and visual evidence agree, so the judgment is high-confidence PASS."
  ],
  "explanation": "PASS judgment. The run starts from the intended injected precondition, the visual sequence shows the checkpoint activating after the scripted movement, and the recorded runtime state matches the expected post-action state. The behavior is therefore consistent with the keypoint."
}
```

If the run clearly misses the intended scenario or visual evidence is insufficient, write `FAIL` (the implementation could not produce clear evidence of correctness; this counts as a falsifying witness for the specification element). Write `INCOMPLETE` ONLY when the harness itself broke (browser launch error, server crash, worker timeout) — example template:

```json
{
  "keypoint_id": "1",
  "category": "State Transition",
  "description": "...",
  "prestate": "...",
  "instruction": "...",
  "expected": "...",
  "actual_before_state": "Injected precondition could not be validated from the available evidence.",
  "actual_after_state": "No defensible post-action observation is available because execution stopped early.",
  "status": "INCOMPLETE",
  "passed": false,
  "confidence": 0,
  "reasoning": [
    "The verification run did not complete successfully.",
    "The injected precondition or the interaction could not be validated from the saved evidence.",
    "The verification contract could not be satisfied from the available evidence.",
    "The error below explains where execution failed."
  ],
  "explanation": "INCOMPLETE judgment. The verification worker could not complete the injected interaction flow successfully, so the keypoint did not produce enough evidence for a defensible PASS or FAIL.",
  "error": {
    "type": "page_load_error",
    "message": "...",
    "step": "run_test_script"
  },
  "state_verification": null,
  "visual_verification": null
}
```

Use error types:
- `page_load_error`
- `game_init_error`
- `state_injection_error`
- `action_execution_error`
- `state_retrieval_error`
- `visual_evidence_insufficient`
- `assertion_error` (verification failed but execution succeeded; no `error` field required)

## Output Structure

```
{output_dir}/
├── short_interaction_info.json
├── test_config.json
├── test_script.mjs
├── test_result.json
├── screenshots/
│   ├── before.png
│   └── after.png
└── result.json
```
