# data.md Format Example

Use this as a reference for the expected format of the `data.md` file.

```markdown
# Game State Parameters

## Game Metadata

### Controls
| Action | Key |
|--------|-----|
| Move Left | ArrowLeft |
| Move Right | ArrowRight |
| Jump | Space |
| Shoot | KeyX |

### Physics
- Player Speed: 5 pixels/frame
- Jump Velocity: -10 pixels/frame
- Gravity: 0.5 pixels/frame²
- Bullet Speed: 8 pixels/frame

### Canvas
- Width: 800px
- Height: 600px

### Spatial Definitions
- nearby: within 50 pixels
- far: more than 200 pixels
- close: within 20 pixels

## State Parameters

| Parameter Name | Type | Description | Value Range/Constraints |
|---------------|------|-------------|------------------------|
| playerX | number | Player's X coordinate | 0-800 (canvas width) |
| playerY | number | Player's Y coordinate | 0-600 (canvas height) |
| playerHealth | number | Player's current health | 0-100 |
| score | number | Current game score | >= 0 |
| gameState | string | Current game state | "menu", "playing", "paused", "gameOver", "victory" |
| enemies | Array<Enemy> | Array of active enemies | Array of enemy objects with {x, y, type, health, alive} |
```
