# state_injection_api.md Format Example

Use this as a reference for the expected format of the `state_injection_api.md` file.

```markdown
# State Injection API Documentation

## Overview
This document describes the state injection and retrieval APIs for automated testing.

## API Methods

### `window.injectGameState(state: GameState): void`
Injects a complete or partial game state into the running game.

**Parameters:**
- `state: Partial<GameState>` - Game state object with parameters to inject

**Behavior:**
- All provided fields are applied immediately
- Unprovided fields retain their current values
- State persists until changed by game logic or another injection
- Triggers necessary re-renders automatically

### `window.getGameState(): GameState`
Retrieves the current complete game state.

**Returns:**
- `GameState` - Complete game state object with all parameters

## Type Definitions

```typescript
interface GameState {
  // Player state
  playerX: number;           // Player X coordinate (0-800)
  playerY: number;           // Player Y coordinate (0-600)
  playerHealth: number;      // Player health (0-100)

  // Game progress
  score: number;             // Current score (>= 0)
  level: number;             // Current level (>= 1)

  // Game objects
  enemies: Array<{
    x: number;               // Enemy X coordinate
    y: number;               // Enemy Y coordinate
    type: 'goomba' | 'koopa'; // Enemy type
    health: number;          // Enemy health
    alive: boolean;          // Whether enemy is alive
  }>;

  items: Array<{
    x: number;               // Item X coordinate
    y: number;               // Item Y coordinate
    type: 'coin' | 'powerup'; // Item type
    active: boolean;         // Whether item is active
  }>;

  // Game status
  gameState: 'menu' | 'playing' | 'paused' | 'gameOver' | 'victory';
}
```

## Example Usage

### Minimal State Injection
```javascript
// Set player position only
window.injectGameState({
  playerX: 100,
  playerY: 200
});
```

### Complete State Injection
```javascript
// Set up a complete test scenario
window.injectGameState({
  playerX: 100,
  playerY: 200,
  playerHealth: 50,
  score: 0,
  level: 1,
  enemies: [
    { x: 300, y: 200, type: 'goomba', health: 10, alive: true }
  ],
  items: [
    { x: 150, y: 200, type: 'coin', active: true }
  ],
  gameState: 'playing'
});
```

### State Retrieval
```javascript
// Get current state
const currentState = window.getGameState();
console.log('Player position:', currentState.playerX, currentState.playerY);
```

## Required vs Optional Fields

**For Complete State Injection (recommended):**
All top-level fields should be provided to ensure consistent test state:
- `playerX`, `playerY`, `playerHealth` - Required
- `score`, `level` - Required
- `enemies` - Required (can be empty array `[]`)
- `items` - Required (can be empty array `[]`)
- `gameState` - Required

**For Partial State Injection:**
Any subset of fields can be provided. Unprovided fields retain current values.

## Notes
- Arrays must be provided as complete arrays, not individual elements
- Empty arrays are valid (e.g., `enemies: []` for no enemies)
- State injection does not trigger game events (e.g., collision detection)
- State is applied synchronously before the next frame render
```
