---
name: distill-verified-keypoints
description: Extract discrete, verifiable, specification-first keypoints from a game description for subsequent evaluation of game logic correctness. Use when preparing `games/{game_name}/keypoints.md` from a description file.
---

## Input

1. **Game description file path from the user request**

**Processing Steps:**
- Resolve description path in this order:
  1. Use the path explicitly provided by the user request.
  2. If missing and `game_name` is known, prefer `descriptions_example/{game_name}.md` when it exists.
  3. If still missing and there is exactly one candidate under `descriptions_example/**/*.md`, use that file.
  4. Ask the user only when multiple candidates remain ambiguous.
- Read the resolved game description file content
- Extract the game name from the file path (removing the .md extension) to use as the game project identifier

## Task Overview
Reference `skills/distill-verified-keypoints/references/keypoint.md` for the extraction principles and categories.
You are a professional game development expert, and you are now tasked with evaluating the correctness of game logic for a generated game. Game logic correctness is derived from the game description and common sense. Based on the game description file and the assumption that "critical nodes determine global correctness", your task is to decompose the complex task of verifying game logic correctness into a set of discrete and verifiable keypoints. Subsequent automatic evaluation will verify the logical correctness of each individual keypoint.

Important: this is a **specification-first** extraction step, not a feature checklist. The goal is not to prove that the game has obvious controls or a visible basic loop. The goal is to choose the keypoints that are most likely to separate a shallow implementation from a faithful implementation.

## Contract Alignment

This skill produces the description-layer keypoint artifact consumed by orchestrator:

- File output: `games/{game_name}/keypoints.md`
- Logical fields (parsed downstream):
  - `prestate_from_game_description`
  - `instruction_from_game_description`
  - `expected_result_from_game_description`

These three fields are fuzzy semantic text from the game description layer.

Contract references:
- Canonical API contract: `docs/inter_skills_structure.md`
- Workflow graph and orchestration semantics: `docs/agentic_workflow_graph_api.md` (non-canonical)

The first line of `games/{game_name}/keypoints.md` must be:
- `<!-- KEYPOINT_POLICY_VERSION: 2026-04-21-spec-v3 -->`

## Process

### 1. Read and Understand Game Description
* Read the game description file content
* Identify the game's core mechanics, rules, and interactions
* Note important state variables, win/loss conditions, and interaction behaviors

### 1.2 Core Mechanic Planning

Before writing keypoints, internally list the game's core mechanic families and ensure the final file covers them.

For each important mechanic, prefer a **family** of keypoints instead of a single isolated check:
- one success case
- one nearby failure / forbidden / boundary case
- one persistence / order / precedence / resource-consequence case when the specification supports it

Do not emit only the easiest observable behavior for a mechanic when a stronger nearby contrast exists in the description.

Also ask, for each proposed keypoint:
- what bug pattern would this catch?
- what nearby incorrect behavior must be ruled out?
- what concrete observation would make the verdict defensible?

### 1.1 Scope Control

Keep the extraction scoped to the current game only.

Allowed inputs:
- the resolved target description file
- `skills/distill-verified-keypoints/references/keypoint.md`
- the current game's own files under `games/{game_name}/` only when the description is ambiguous and a local game artifact is strictly needed to disambiguate a mechanic

Do not:
- inspect `keypoints.md` from other games
- use other games as templates
- copy headings, phrasing, or mechanics from unrelated game artifacts
- search the repo broadly for arbitrary `keypoints.md` files
- browse the current game directory broadly by default when the description already specifies the mechanic

The goal is to avoid cross-game contamination. Every keypoint must be grounded in the current game's specification, not in examples from another title.

### 2. Extract Keypoints

* Read `skills/distill-verified-keypoints/references/keypoint.md` first, then extract keypoints accordingly
* **Keypoint Format Standard**: `## Keypoint {ID}: [{Category}] {Description}`
* **Minimum Count Requirement**: Produce **at least 60 keypoints** per substantial game description unless the specification is genuinely sparse
* For substantial games, target roughly **30-40** keypoints
* Ensure comprehensive coverage across all four keypoint categories (State Transition, Boundary Condition, Interaction Logic, Game Rule)
* Prioritize keypoints that represent critical game logic
* Aim for atomic keypoints that can be verified independently
* Prefer keypoints that require **specific state construction plus short interaction**, not just idle observation

### 2.1 Difficulty and Coverage Budget

Your keypoint set must not be dominated by trivial checks.

Aim for this distribution:
- **At most 15%** may be "basic sanity" keypoints such as obvious start-up behavior or single-input existence checks
- **At least 50%** should be branch-sensitive negative/exception/boundary/forbidden cases
- **At least 45%** should involve multi-step logic, carry-over state, resource preservation, ordering, or interaction between multiple mechanics/entities
- **At least 85%** overall should be hard/discriminative: either contrastive or multi-step

Good high-value keypoints usually test one of these:
- failure vs recovery
- allowed vs forbidden action under a modifier state
- resource accounting or persistence
- state carry-over across phases, rooms, deaths, retries, or chapter transitions
- precedence between two competing rules
- multi-entity coupling
- "works in one setup but must not work in the nearby counterexample"
- exact consequence after the trigger, not just trigger detection
- observability strong enough for a short-horizon verifier to defend the verdict

### 2.2 Anti-Patterns to Avoid

Do not fill the file with verifier-friendly but low-discriminative keypoints.

Avoid or strictly limit patterns like:
- "the game starts"
- "the player can move left/right"
- "tapping a reachable destination moves the character"
- "coins can be collected"
- "a dragger moves a platform"
- "a button changes something"

Those are acceptable only if they are necessary scaffolding for a more discriminative mechanic, and they must remain a minority.

Avoid keypoints that are:
- generic to the genre rather than specific to this specification
- obvious from a one-line smoke test
- pure UI presence checks
- duplicated variants of the same easy mechanic
- only positive-case checks with no nearby negative/counterexample check
- phrased as raw control existence ("can move", "can jump", "can swipe") without a mechanic-specific invariant or consequence
- so broad that a verifier would need long-horizon exploration or a full playthrough to judge it

### 2.3 Pairing Rule for Core Mechanics

For each core mechanic, prefer a **paired extraction**:
- one positive keypoint showing when the mechanic should work
- one negative or boundary keypoint showing when it must not work, must revert, or must preserve an invariant

When the mechanic is important to game faithfulness, go beyond a pair and add a third keypoint for:
- persistence across time
- order sensitivity
- precedence between competing rules
- resource accounting
- prerequisite gating

For rich mechanics, extend this into a **quartet**:
- success
- forbidden/boundary failure
- persistence/order/resource consequence
- nearby confounder that must not be mistaken for success

Examples:
- not just "Save Me revives the run", but also "Save Me preserves prior progress and does not reset the run"
- not just "a switch opens a door", but also "the door does not remain open after vacating a pressure plate"
- not just "Totem can move", but also "crow/Totem interaction blocks or reverses patrol as specified"

### 3. Create Keypoints Output File
* Create a `keypoints.md` file under `games/{game_name}/`
* Write all keypoints following the 'Keypoint Format Standard'
* Organize keypoints by category for clarity

### 4. Construct Short-term Interaction Verification Information for Each Keypoint
* Read `games/{game_name}/keypoints.md` and understand each keypoint's information
* For each keypoint, provide:
  - **Verification Focus**: one concise line describing what makes this keypoint discriminative, such as forbidden action, persistence, precedence, recovery, resource accounting, or confounder separation
  - **Precondition Game State Description**: A fuzzy natural language description of what game state should be set up before verification
    - Use semantic terms like "nearby", "far", "close" (without specific pixel values)
    - Describe states conceptually, not with specific parameter values
    - Example: "Mario is small, mushroom spawned nearby"

  - **Instruction Description**: A fuzzy natural language description of what action/interaction should be performed
    - Use generic action terms like "move right", "jump", "shoot"
    - Don't specify exact keys or durations
    - Example: "Move right to collect mushroom"

  - **Expected Result Description**: A fuzzy natural language description of what should happen after the instruction is executed
    - Describe expected outcomes conceptually
    - Don't specify exact parameter values
    - Example: "Mario becomes big, height increases"

* **Format Standard**: Write the above four pieces of information under each corresponding keypoint

**Key Principle**: Keep descriptions at the **game logic level**, not implementation level. The `generative-state-construction` stage will later translate these fuzzy descriptions into concrete test configurations, and `short-interaction-verification` will execute the verification.

### 5. Hard Constraints (Must Follow)

- The first line must be `<!-- KEYPOINT_POLICY_VERSION: 2026-04-21-spec-v3 -->`.
- Produce at least **60 keypoints** for a substantial game unless the specification is genuinely sparse.
- `Precondition Game State Description`, `Instruction Description`, `Expected Result Description` must come from game description semantics and common-sense game logic.
- `Verification Focus` must explain why the keypoint is discriminative and what nearby wrong behavior is being separated.
- Do not write implementation-specific details (no variable names, no function names, no code-level constants).
- Do not write executable test steps (no key codes, no frame counts, no fixed durations, no pixel-level numeric thresholds) unless those numbers are explicitly part of game description semantics.
- Do not pre-convert fuzzy text into structured machine config. That conversion belongs only to `generative-state-construction`.
- Do not let basic tutorial or smoke-test keypoints dominate the file.
- Headings and expected results must usually state the invariant, contrast, persistence, or consequence, not just the input action.
- Before finishing, self-audit the keypoint list and rewrite weak items until the set is centered on **critical, discriminative, specification-specific logic** rather than obvious functionality.

## Output

Keypoint information file: `games/{game_name}/keypoints.md`

**Output Format Example:**
```markdown
# Game Keypoints

## Keypoint 1: [State Transition] Player death triggers game over
**Verification Focus:**
Death must terminate the current run immediately instead of leaving the player controllable or silently respawning.

**Precondition Game State Description:**
Set player health to 1, position player near an enemy that can deal damage.

**Instruction Description:**
Trigger damage to the player to reduce health to 0.

**Expected Result Description:**
Game state should transition to GameOver, displaying game over screen.

---

## Keypoint 2: [Boundary Condition] Player cannot move beyond map boundaries
**Verification Focus:**
Crossing the edge must be clamped rather than wrapping, drifting out of bounds, or teleporting.

**Precondition Game State Description:**
Set player position near the right edge of the map (x coordinate close to maximum).

**Instruction Description:**
Attempt to move player to the right beyond the map boundary.

**Expected Result Description:**
Player position should remain clamped within valid map boundaries.

---

[Additional keypoints following the same format...]
```
