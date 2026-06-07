---
name: game-gen-with-data
description: Generate a runnable TypeScript game from a game description file, plus data.md and a state injection API for evaluation. Use when converting `descriptions_example/*.md` into a playable game project under `games/`.
---

## Input

**Game description file path from the user request**

**Processing Steps:**
1. Resolve description path in this order:
   - Use the explicit path provided in the request.
   - If missing and there is exactly one candidate under `descriptions_example/**/*.md`, use it.
   - Ask the user only when multiple candidates remain ambiguous.
2. Read the resolved `.md` file content
3. Extract the game name from the file path (removing the .md extension) to use as the game project folder name
4. Create the folder under the `games/` directory (e.g., `games/shooter_game/`)
5. Implement the entire game project within that folder

## Task Overview

You are a professional game development expert. Your task is to generate a complete, runnable game based on the user's description. Additionally, to support automated evaluation, you need to document the game's state parameters and provide an API in the code to modify these parameters.

Contract references:
- Canonical API contract: `docs/inter_skills_structure.md`
- Workflow graph and orchestration semantics: `docs/agentic_workflow_graph_api.md` (non-canonical)

The generated game must be:
1. **Fully functional** - All features described in the game description must work correctly
2. **Runnable** - The game can be launched and played immediately without additional setup
3. **Testable** - State parameters are accessible and modifiable for automated testing

## Architectural Requirement: Pluggable Eval Adapter

The evaluation-facing hooks MUST be implemented as a removable adapter layer instead of being deeply mixed into the core gameplay code.

Required shape:
- Keep gameplay/runtime logic in normal game modules
- Put evaluation-specific globals in a dedicated module such as:
  - `src/eval_adapter.ts`
  - `src/eval_hooks.ts`
  - `src/testing/eval_bridge.ts`
- `src/main.ts` should only mount this adapter from one narrow integration point
- The runtime should still work if the adapter module is removed

The goal is that a developer can later remove evaluation support by deleting the adapter module and one small integration call, without rewriting the game itself.

## CRITICAL: File Creation Rules

You MUST follow these rules when creating game files:
1. **Create files ONE AT A TIME** — never attempt to create multiple files in a single response
2. **Always provide absolute file paths** when creating files (e.g., `games/shooter_game/src/main.ts`)
3. **Always provide complete file content** when creating each file
4. **Follow this creation order:** index.html → package.json → tsconfig.json → vite.config.ts → src/main.ts → other source files → data.md → state_injection_api.md → README.md
5. **Verify each file** was created successfully before moving to the next one
6. **If a Write call fails:** STOP retrying the same call. Re-examine your tool parameters, ensure both `file_path` and `content` are provided, then try again with corrected parameters.

## Process

### 1. Project Structure and Game Code Generation

* **Directory Structure:** Create a folder under the `games/` directory named after the game description file (without the .md extension)
  - Example: `descriptions_example/shooter_game.md` → `games/shooter_game/`
  - All game-related files (code, assets, configuration, etc.) should be placed in this folder

* **Game Implementation:**
  - Develop the game using TypeScript and appropriate frameworks (e.g., Phaser, PixiJS, or vanilla Canvas)
  - Ensure the code is complete, well-structured, and can run directly in a browser or Node.js environment
  - Implement all game mechanics, rules, and features described in the game description
  - Include proper error handling and edge case management

* **Architecture Note:** You do not need to over-engineer the codebase, but you MUST isolate the evaluation-facing APIs from the core gameplay logic. The game's core state parameters (such as score, player coordinates, health, enemy states, level, game status, etc.) should be accessible through a runtime object or state container. The eval adapter should wrap that runtime object rather than scattering test-only globals throughout the gameplay code.

### 2. Extract Game State Parameters Table (`data.md`)

* **Identify State Variables:** Analyze the code you generate and extract all variables that determine the current game "state", including:
  - Player state (position, health, inventory, abilities)
  - Game progress (score, level, time, objectives)
  - Game objects (enemies, items, projectiles)
  - Game status (paused, running, game over, victory)
  - Environment state (map configuration, weather, time of day)

* **Generate data.md:** Create a file named `data.md` within the game project folder (e.g., `games/shooter_game/data.md`) containing:
  1. **Game Metadata** section - Game configuration and constants
  2. **State Parameters** section - Detailed parameter table

* **Game Metadata Section:** Include the following subsections:
  - **Controls** - Keyboard/mouse mappings for game actions
  - **Physics** - Movement speeds, gravity, acceleration constants
  - **Canvas** - Game canvas dimensions
  - **Spatial Definitions** - Semantic distance definitions (nearby, far, close)

* **State Parameters Table Columns:**
  - `Parameter Name` - The exact variable name as it appears in code
  - `Type` - Data type (number, string, boolean, object, array, etc.)
  - `Description` - Clear explanation of what this parameter represents
  - `Value Range/Constraints` - Valid values, min/max bounds, or constraints

* **Purpose:** This file serves as:
  1. Parameter definitions for constructing specific test states
  2. Game configuration reference for test automation
  3. Semantic mapping for natural language test instructions

**Example data.md format:** See `references/data_md_example.md` for the expected format. The file must include Game Metadata (Controls, Physics, Canvas, Spatial Definitions) and a State Parameters table with columns: Parameter Name, Type, Description, Value Range/Constraints.

### 3. Provide State Injection Method (Setter API)

* **Implementation:** Based on the parameters in `data.md`, **add** a State Injection API through a dedicated eval adapter module
  - Function name: `injectGameState(stateData)` or similar
  - Location: Accessible from the global scope or exported as a module function
  - Comment the function clearly for future reference

* **Pluggable Adapter Constraint:**
  - Prefer a structure like:
    - core runtime in `src/runtime.ts` or `src/game.ts`
    - eval adapter in `src/eval_adapter.ts`
    - `src/main.ts` only wires them together
  - `window.injectGameState`, `window.getGameState`, `window.pauseGame`, `window.resumeGame`, `window.isGamePaused`, and `window.gameReady` should be attached inside the adapter module
  - The adapter should expose a single mounting function, for example:

```typescript
mountEvalAdapter(window, runtime);
```

  - The runtime itself should remain usable even if the adapter module is removed

* **Functionality:** This function receives a data object containing state parameters and directly assigns these values to the corresponding variables in the game, thereby achieving "state injection"
  - Accept a JavaScript object with parameter names as keys
  - Validate parameter types and constraints before injection
  - Update all relevant game variables atomically
  - **Automatically pause game loop** before injection to prevent state being overwritten
  - Trigger any necessary re-renders or updates after state injection

* **Requirements:**
  - This API should be an additional feature (Hook) used to directly navigate/jump to a specified game state at runtime
  - Ensure that value assignments take effect immediately without affecting the game's original runtime logic
  - The injected state should persist until changed by game logic or another injection
  - Include error handling for invalid state parameters

* **Required Game Lifecycle APIs:** The game MUST implement these APIs for test automation:

```typescript
// === REQUIRED: Game Ready Signal ===
window.gameReady = false;  // Set to true when game is fully initialized

// === REQUIRED: Pause/Resume Control ===
let gamePaused = false;
window.pauseGame = () => { gamePaused = true; };
window.resumeGame = () => { gamePaused = false; };
window.isGamePaused = () => gamePaused;

// Game loop MUST respect pause state
function gameLoop() {
  if (gamePaused) {
    requestAnimationFrame(gameLoop);
    return;  // Skip update when paused
  }
  update();
  render();
  requestAnimationFrame(gameLoop);
}

// Initialization
function init() {
  // ... load assets, setup game ...
  window.gameReady = true;  // Signal ready AFTER full init
  gameLoop();
}
```

Recommended integration pattern:

```typescript
// src/main.ts
import { createRuntime } from "./runtime";
import { mountEvalAdapter } from "./eval_adapter";

const runtime = createRuntime();
mountEvalAdapter(window, runtime);
runtime.start();
```

**Example implementation:**
```typescript
/**
 * State Injection API for automated testing
 * @param stateData - Object containing state parameters to inject
 */
function injectGameState(stateData: Partial<GameState>): void {
  // IMPORTANT: Pause game loop to prevent state being overwritten
  gamePaused = true;
  
  if (stateData.playerX !== undefined) playerX = stateData.playerX;
  if (stateData.playerY !== undefined) playerY = stateData.playerY;
  if (stateData.playerHealth !== undefined) playerHealth = stateData.playerHealth;
  if (stateData.score !== undefined) score = stateData.score;
  if (stateData.gameState !== undefined) gameState = stateData.gameState;
  // ... additional parameters

  // Trigger re-render with new state (while paused)
  render();
  
  // NOTE: Game stays paused until test calls window.resumeGame()
}

// Expose to global scope for testing
(window as any).injectGameState = injectGameState;

/**
 * State Getter API for automated testing
 * @returns Current game state object
 */
function getGameState(): GameState {
  return {
    playerX,
    playerY,
    playerHealth,
    score,
    gameState,
    // ... all state parameters
  };
}

// Expose to global scope for testing
(window as any).getGameState = getGameState;
```

### 4. Generate State Injection API Documentation (`state_injection_api.md`)

* **Create state_injection_api.md:** Generate a file named `state_injection_api.md` within the game project folder (e.g., `games/shooter_game/state_injection_api.md`)

* **Content Requirements:**
  - API method signatures
  - Complete TypeScript interface definitions
  - Parameter descriptions and constraints
  - Example usage with complete state objects
  - Notes on required vs optional fields

* **Purpose:** This documentation enables test automation to:
  1. Understand the exact format of state objects
  2. Know which fields are required vs optional
  3. Construct valid state objects for injection
  4. Validate state objects before injection

**Example state_injection_api.md format:** See `references/state_injection_api_example.md` for the expected format. The file must include API method signatures, TypeScript interface definitions, example usage (minimal and complete injection), and notes on required vs optional fields.

### 5. Documentation and Verification

* **Create README.md:** Include in `games/{game_name}/README.md`:
  - Game description and mechanics
  - How to run the game
  - How to use the state injection API
  - Where the eval adapter module lives and how to remove it
  - List of dependencies

* **Verify Implementation:**
  - Test that the game runs correctly
  - Verify that all described features work as expected
  - Test the state injection API with sample state data
  - Ensure `data.md` accurately reflects all state parameters
  - Ensure `state_injection_api.md` documents the complete API

## Output

A complete game project under `games/{game_name}/` containing:
1. **Game code** - All TypeScript/JavaScript files, HTML, CSS
2. **data.md** - Comprehensive state parameters table with Game Metadata section
3. **state_injection_api.md** - Complete API documentation with type definitions and examples
4. **README.md** - Documentation and usage instructions
5. **State injection API** - Implemented `window.injectGameState()` and `window.getGameState()` functions
6. **Assets** - Any necessary images, sounds, or other resources (or placeholders)
7. **Pluggable eval adapter module** - A dedicated file that owns the evaluation-specific globals

## File Structure Example

```
games/{game_name}/
├── src/
│   ├── main.ts              # Runtime bootstrap + adapter mounting
│   ├── eval_adapter.ts      # Removable evaluation hook layer
│   ├── components/          # Game components
│   └── types.ts             # TypeScript type definitions
├── index.html               # Game entry point
├── package.json             # Dependencies
├── tsconfig.json            # TypeScript configuration
├── vite.config.ts           # Build configuration
├── data.md                  # State parameters + Game Metadata
├── state_injection_api.md   # API documentation
└── README.md                # Project documentation
```

## Error Recovery

If you encounter a tool error:
- **Do NOT retry the same failed call** — this will loop forever
- Re-read the error message carefully
- Ensure `file_path` is a string path and `content` is a string with the full file contents
- If the file is very large, break it into a smaller initial version and then use Edit to add more content
- If stuck after 2 failures, switch to a minimal runnable scaffold first and continue iterating; ask the user only if required inputs are still missing or ambiguous

## Critical Requirements Checklist

Before completing this task, verify:
- [ ] Game runs without errors
- [ ] All features from game description are implemented
- [ ] `data.md` includes both Game Metadata and State Parameters sections
- [ ] `state_injection_api.md` is complete with type definitions and examples
- [ ] `window.injectGameState()` is implemented and accessible
- [ ] `window.getGameState()` is implemented and accessible
- [ ] State injection works correctly with test data
- [ ] Eval hooks are isolated in a dedicated removable adapter module
- [ ] All state parameters in `data.md` match the actual code
- [ ] Game Metadata (controls, physics, canvas, spatial) is accurate
