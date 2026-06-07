---
name: generative-state-construction
description: Convert fuzzy keypoint text into concrete short interaction data for executable verification. Use as the normal-mode `keypoint-tester` pre-step, not as a standalone top-level workflow.
---

## Overview

Subagent pre-step for ONE keypoint in normal mode.

This skill converts fuzzy keypoint text (`prestate/instruction/expected`) into concrete, machine-usable test data and writes the canonical artifacts consumed by `short-interaction-verification`.

The goal is not only to produce a target end state, but also to make the verdict defensible against nearby false positives. Build a compact verification contract that states what must be observed and what must not be mistaken for success.

This skill is preloaded into `keypoint-tester` and should run before `short-interaction-verification`.

## Contract Alignment

Follow `docs/inter_skills_structure.md` strictly:

- Input contract: `GenerativeStateConstructionInput = NormalSubagentInfo`
- Output data contract: `ShortInteractionInfo`
- Output artifacts:
  - `{output_dir}/short_interaction_info.json`
  - `{output_dir}/test_config.json`

Naming and graph reference:
- Canonical API contract: `docs/inter_skills_structure.md`
- Workflow graph and orchestration semantics: `docs/agentic_workflow_graph_api.md` (non-canonical)

## Input (Task Prompt)

Parse parameters from Task prompt (`key=value`, one per line):
- `game_name`
- `keypoint_id`
- `category`
- `description`
- `output_dir`
- `game_url`
- `project_root`
- `analysis_path` (optional)
- `prestate` (fuzzy, from game description)
- `instruction` (fuzzy, from game description)
- `expected` (fuzzy, from game description)

Important:
- These three text fields are semantic descriptions from the game description layer, not implementation-ready values.
- Preserve their original meaning in `traceability.*_from_game_description`.

## Read Files

Read the following files:
- `games/{game_name}/data.md`
- `games/{game_name}/state_injection_api.md`
- `{analysis_path}` (optional, if exists)

## Workflow

### 1. Parse and Normalize Input

- Parse all prompt fields.
- Keep exact raw strings of `prestate`, `instruction`, `expected` for traceability.
- Validate required fields are non-empty (`game_name`, `keypoint_id`, `category`, `description`, `output_dir`, `game_url`).

### 2. Build Concrete `ShortInteractionInfo`

Translate fuzzy text into concrete structures based on `data.md` schema and implementation notes in `state_injection_api.md` (and `analysis_path` if provided):

```json
{
  "keypoint_id": "1",
  "category": "State Transition",
  "description": "Player collects mushroom and becomes big",
  "prestate": {},
  "instruction": { "actions": [] },
  "expected_result": {},
  "verification_contract": {
    "precondition_checks": [],
    "required_observations": [],
    "forbidden_observations": [],
    "decision_rule": "all required, none forbidden"
  },
  "traceability": {
    "prestate_from_game_description": "...",
    "instruction_from_game_description": "...",
    "expected_result_from_game_description": "..."
  }
}
```

Rules:
- `prestate` must be data-level and injectable.
- `instruction.actions` must be executable and ordered (`keypress`, `keydown`, `keyup`, `wait`, `type`).
- `expected_result` must be checkable from `window.getGameState()`.
- `verification_contract` should make the keypoint harder to game:
  - `precondition_checks`: how to tell the localized scenario was actually established
  - `required_observations`: positive evidence required for PASS
  - `forbidden_observations`: nearby wrong behaviors or confounders that must remain absent
  - `decision_rule`: usually `all required, none forbidden`
- If fuzzy text is ambiguous, choose one reasonable mapping and keep the original fuzzy text in `traceability`.
- Prefer fields that exist in `data.md` and are injectable via `state_injection_api.md`.
- For boundary-condition, warning, pause, or transient-feedback keypoints, prefer a near-threshold injectable state that starts close to the target scenario instead of requiring the verifier to play from the main menu or an unrelated baseline state.
- For verification-strengthening, do not stop at "what should happen"; also encode "what nearby incorrect outcome must not count as success".

### 3. Write `{output_dir}/short_interaction_info.json`

Write the full `ShortInteractionInfo` structure to disk.

### 4. Build Canonical `test_config.json`

Convert `ShortInteractionInfo` into executable config with canonical field names:

```json
{
  "game_url": "http://localhost:3000",
  "precondition_state": {},
  "interaction": { "actions": [] },
  "expected_state": {},
  "verification_contract": {
    "precondition_checks": [],
    "required_observations": [],
    "forbidden_observations": [],
    "decision_rule": "all required, none forbidden"
  },
  "metadata": {
    "keypoint_id": "1",
    "category": "State Transition",
    "description": "..."
  }
}
```

Mapping rules:
- `precondition_state = short_interaction_info.prestate`
- `interaction = short_interaction_info.instruction`
- `expected_state = short_interaction_info.expected_result`
- `verification_contract = short_interaction_info.verification_contract`
- `metadata.keypoint_id/category/description` must match top-level keypoint metadata

### 5. Validate Output Consistency (Required)

Before finishing, verify:
- Both files exist in `{output_dir}`.
- `test_config.precondition_state` equals `short_interaction_info.prestate`.
- `test_config.interaction.actions` equals `short_interaction_info.instruction.actions`.
- `test_config.expected_state` equals `short_interaction_info.expected_result`.
- `verification_contract` exists and contains at least one non-empty `required_observations` item plus one non-empty `forbidden_observations` item for strong keypoints whenever the mechanic admits a nearby confounder.
- `traceability` fields are present and non-empty.

## Output

```
{output_dir}/
├── short_interaction_info.json
└── test_config.json
```

This skill only constructs data and config. It does not run Playwright or produce `result.json`.
