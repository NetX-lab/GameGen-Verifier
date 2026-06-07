# Minimal Context Principle

## Current Status: Future Optimization Direction

> **The current implementation uses the subagent's isolation context** (does not inherit the main session history).
> The main session writes key analysis information to disk (`implementation_analysis.md`), and the subagent reuses the information by reading the file.
> The Minimal Context solution described in this document is still the **future optimization direction**: further reducing the input/read range of each subagent and improving scalability.

## Current architecture: File-Based + Isolated Subagents

```
Main session:
analyze-game-implementation → write runs/{game}/{run_id}/implementation_analysis.md
keypoint-orchestrator → Read keypoints.md, spawn subagents in batches

subagent (Task):
Context isolation (main session history is not inherited)
+ Read data.md / state_injection_api.md / implementation_analysis.md(optional)
→ Execute test
```

**advantage**:
- Does not rely on context inheritance semantics, and the behavior is more certain
- Analysis can be reused (dropped to disk), and subagent can read on demand
- There is no need to stuff the complete source code into the subagent prompt in the main session

**shortcoming**:
- Each subagent still needs to read multiple files and perform "fuzzy → specific" conversion, and the token/time consumption increases linearly with the number of keypoints.
- Massive parallelization of 50+ keypoints may still be biased

## Future optimization: Minimal Context mode

When it is necessary to support large-scale parallel testing (50+ keypoints), the following optimizations can be considered:

### Core idea

Orchestrator reads complete information once and builds a minimal test package for each keypoint, and subagent only receives necessary information.

```
Current (File-Based):
Orchestrator: Read once and generate implementation_analysis.md (~8k tokens)
Agent 1..N: Each agent reads data.md/state_injection_api.md and constructs its own tests (~2k-6k tokens)
  Total: 8k + N × (2k-6k)

Future (Minimal Context):
Orchestrator: Read all files once (~8k tokens)
Agent 1: Receive test package (~2k tokens)
Agent 2: Receive test package (~2k tokens)
  ...
Agent 12: Receive test package (~2k tokens)
  Total: 8k + 12 × 2k = 32k tokens
```

### Test Package Structure (Reference Design)

```json
{
  "keypoint_id": "3",
  "keypoint_description": "Player moves left when ArrowLeft is pressed",
  "prestate": "Player at x=200, game state is 'playing'",
  "instruction": "Press ArrowLeft for 1 second",
  "expected_result": "Player x decreases by ~50px",
  "relevant_state_params": { "playerX": "number (0-800)", "gameState": "string" },
  "game_metadata": { "controls": {"moveLeft": "ArrowLeft"}, "physics": {"playerSpeed": 5} },
  "state_injection_api": { "method": "window.injectGameState", "getter": "window.getGameState" },
  "game_url": "http://localhost:3000",
  "output_dir": "runs/{game_name}/{run_id}/keypoint_3/"
}
```

### Migration conditions

Consider migrating to Minimal Context mode when the following conditions are met:
- The number of Keypoints > 20, the token consumption/time-consuming in the current mode is too high
- Game source code > 10k tokens, context close to limit
- Need to support large-scale automated testing in CI/CD

### Migration steps (to be implemented)

1. Modify `keypoint-orchestrator/SKILL.md`: orchestrator preprocesses the minimized test package of each keypoint
2. Modify `generative-state-construction/SKILL.md` + `short-interaction-verification/SKILL.md`: Execute from the prompt test package first (try not to read large files)
3. Update spawn template: embed test package (JSON) into prompt
4. Verify that the subagent no longer needs to read the game source code and minimize repeated reading of data.md/state_injection_api.md
