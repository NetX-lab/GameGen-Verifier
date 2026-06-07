# Battleship — Complete Game Specification

## 1. Game Overview

Battleship is a two-player guessing game where each player places a fleet of ships
on a grid and then takes turns calling out coordinates to try to sink the opponent's
ships. The first player to sink all opponent ships wins.

- **Players**: 2 (Human vs AI)
- **Boards**: Two 10x10 grids per player (own ships + tracking opponent)
- **Ships**: 5 per player
- **Objective**: Sink all of the opponent's ships
- **Phases**: Ship placement, then alternating attack turns

## 2. Technical Foundation

### 2.1 Display Requirements
- Two grids displayed simultaneously
- Top grid: tracking board (opponent's ocean — shows hits/misses)
- Bottom grid: own board (shows your ships and opponent's attacks)
- Clear distinction between hits, misses, ships, and empty water

### 2.2 Grid Layout (ASCII)

```
  OPPONENT'S OCEAN (Tracking Board)
       A   B   C   D   E   F   G   H   I   J
    +---+---+---+---+---+---+---+---+---+---+
  1 | ~ | ~ | ~ | X | ~ | ~ | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  2 | ~ | ~ | ~ | X | ~ | ~ | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  3 | ~ | O | ~ | X | ~ | ~ | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  4 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  5 | ~ | ~ | ~ | ~ | O | ~ | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  6 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  7 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  8 | ~ | ~ | X | X | X | ~ | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  9 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | O | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
 10 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+

  YOUR OCEAN (Ship Board)
       A   B   C   D   E   F   G   H   I   J
    +---+---+---+---+---+---+---+---+---+---+
  1 | ~ | S | S | S | S | S | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  2 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  3 | ~ | ~ | ~ | D | ~ | ~ | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  4 | ~ | ~ | ~ | D | ~ | ~ | ~ | B | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  5 | O | ~ | ~ | ~ | ~ | ~ | ~ | B | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  6 | ~ | ~ | ~ | ~ | C | C | C | B | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  7 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | B | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  8 | ~ | X | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
  9 | ~ | ~ | ~ | ~ | ~ | ~ | P | P | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+
 10 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |
    +---+---+---+---+---+---+---+---+---+---+

Legend: ~ = Water (empty)    S = Ship segment
        X = Hit              O = Miss
        Letters on own board show ship types
```

## 3. Ship Definitions

### 3.1 Fleet Composition

| Ship Name       | Size | Symbol | Qty | Description            |
|----------------|------|--------|-----|------------------------|
| Carrier        | 5    | C      | 1   | Largest ship           |
| Battleship     | 4    | B      | 1   | Second largest         |
| Cruiser        | 3    | R      | 1   | Medium ship            |
| Submarine      | 3    | S      | 1   | Medium ship (same size as Cruiser) |
| Destroyer      | 2    | D      | 1   | Smallest ship          |

**Total ship cells**: 5 + 4 + 3 + 3 + 2 = 17 cells out of 100

### 3.2 Ship Placement Rules
1. Ships occupy consecutive cells in a straight line (horizontal or vertical)
2. Ships cannot overlap
3. Ships cannot be placed diagonally
4. Ships must be entirely within the 10x10 grid
5. Ships cannot extend beyond the grid boundaries
6. Ships may touch each other (no spacing required in standard rules)
7. Optional rule: ships must have at least 1 cell gap between them

### 3.3 Ship Visual (Horizontal Carrier Example)

```
+---+---+---+---+---+
| C | C | C | C | C |
+---+---+---+---+---+
 bow                stern
```

## 4. Game Phases

### 4.1 Phase 1: Ship Placement

**Human placement:**
1. Select a ship from the fleet panel
2. Click on a grid cell to set the bow (front) position
3. Choose orientation (horizontal or vertical)
4. Confirm placement
5. Repeat for all 5 ships
6. "Ready" button to confirm fleet placement

**AI placement:**
- AI places ships randomly following placement rules
- Higher difficulty AI may use strategic placement

**Random placement algorithm:**
```
function placeShipsRandomly(board, ships):
    for ship in ships (sorted by size, largest first):
        placed = false
        while not placed:
            orientation = random(HORIZONTAL, VERTICAL)
            if orientation == HORIZONTAL:
                row = random(1, 10)
                col = random(1, 10 - ship.size + 1)
            else:
                row = random(1, 10 - ship.size + 1)
                col = random(1, 10)

            if canPlace(board, ship, row, col, orientation):
                placeShip(board, ship, row, col, orientation)
                placed = true
```

### 4.2 Phase 2: Battle

Players alternate calling out coordinates to attack:
1. Active player selects a cell on the tracking board
2. Opponent reports "Hit" or "Miss"
3. If all cells of a ship are hit, it is "Sunk" — announce which ship
4. Mark the result on the tracking board
5. Switch turns
6. Continue until one player's entire fleet is sunk

## 5. Attack Rules

### 5.1 Attack Results

| Result    | Condition                              | Display |
|-----------|----------------------------------------|---------|
| Miss      | No ship at targeted cell               | O (white circle) |
| Hit       | Ship segment at targeted cell          | X (red cross) |
| Sunk      | All segments of a ship are hit         | X + announcement |
| Already   | Cell was previously attacked           | Invalid — reselect |

### 5.2 Attack Validation
- Cannot attack the same cell twice
- Must select a cell within the 10x10 grid
- Invalid attacks are rejected with a message

### 5.3 Sink Detection

```
function checkSunk(ship):
    for each cell in ship.cells:
        if cell.status != HIT:
            return false
    return true  // all cells hit — ship is sunk
```

### 5.4 Win Detection

```
function checkWin(fleet):
    for each ship in fleet:
        if not ship.sunk:
            return false
    return true  // all ships sunk — player wins
```

## 6. Game State

| State Variable          | Type              | Description                          |
|-------------------------|-------------------|--------------------------------------|
| humanBoard[10][10]      | enum              | WATER, SHIP, HIT, MISS              |
| aiBoard[10][10]         | enum              | WATER, SHIP, HIT, MISS              |
| humanTracking[10][10]   | enum              | UNKNOWN, HIT, MISS                  |
| aiTracking[10][10]      | enum              | UNKNOWN, HIT, MISS                  |
| humanFleet              | list of Ship      | Player's ships with positions        |
| aiFleet                 | list of Ship      | AI's ships with positions            |
| currentPhase            | enum              | PLACEMENT, BATTLE, GAME_OVER        |
| currentTurn             | enum              | HUMAN, AI                            |
| humanShipsRemaining     | integer           | Ships not yet sunk                   |
| aiShipsRemaining        | integer           | Ships not yet sunk                   |
| attackHistory           | list              | All attacks with results             |
| turnCount               | integer           | Number of turns elapsed              |

### 6.1 Ship Data Structure

```
Ship {
    name: string           // "Carrier", "Battleship", etc.
    size: integer          // 2-5
    cells: [(row, col)]    // list of occupied cells
    hits: [boolean]        // which cells have been hit
    sunk: boolean          // all cells hit
    orientation: H or V    // horizontal or vertical
}
```

## 7. AI Opponent

### 7.1 Difficulty Levels

| Level      | Placement       | Attack Strategy                        |
|------------|----------------|----------------------------------------|
| Beginner   | Random          | Pure random (no repeat)                |
| Easy       | Random          | Random with adjacent follow-up on hits |
| Medium     | Random          | Hunt/Target algorithm                  |
| Hard       | Strategic       | Hunt/Target + probability density      |
| Expert     | Strategic       | Probability density + ship tracking    |

### 7.2 Beginner AI
- Selects random untargeted cells
- No pattern or strategy
- Does not follow up on hits
- May "forget" where it hit

### 7.3 Easy AI — Simple Follow-Up
```
function easyAIAttack():
    if lastAttackWasHit and adjacentUntargeted(lastHit):
        target = randomAdjacent(lastHit)
    else:
        target = randomUntargetedCell()
    return target
```

### 7.4 Medium AI — Hunt/Target Algorithm

Two modes:

**Hunt Mode** (searching for ships):
- Attack random cells (or use checkerboard pattern for efficiency)
- When a hit occurs, switch to Target Mode

**Target Mode** (destroying a found ship):
- Try adjacent cells (up, down, left, right) of the hit
- When a second hit occurs, determine ship orientation
- Continue in that direction
- If miss, try the opposite direction
- When ship is sunk, return to Hunt Mode

```
function huntTargetAI():
    if targetStack is not empty:
        // TARGET MODE
        target = targetStack.pop()
        while target is already attacked:
            target = targetStack.pop()
        return target
    else:
        // HUNT MODE
        return huntModeSelect()

function onHit(row, col):
    // Add adjacent cells to target stack
    for (dr, dc) in [(0,1), (0,-1), (1,0), (-1,0)]:
        nr, nc = row + dr, col + dc
        if inBounds(nr, nc) and not attacked(nr, nc):
            targetStack.push((nr, nc))
```

### 7.5 Hard AI — Probability Density

Calculates the probability that each cell contains a ship:

```
function probabilityDensity(board, remainingShips):
    density = array[10][10] initialized to 0

    for each ship in remainingShips:
        for each valid placement of ship on board:
            // placement must not overlap with misses or sunk ships
            for each cell in placement:
                density[cell.row][cell.col] += 1

    // Boost cells adjacent to existing hits (unsunk)
    for each hit that is part of unsunk ship:
        for each adjacent cell:
            density[adjacent.row][adjacent.col] *= 2

    return density
```

The AI attacks the cell with the highest probability density.

### 7.6 Expert AI — Full Tracking

In addition to probability density:
- Tracks which ships have been sunk
- Only considers placements for remaining ship sizes
- Uses parity optimization (ships of size 2+ can only be on certain cells)
- Achieves near-optimal play (average ~42 shots to win on 10x10)

### 7.7 Checkerboard Pattern (Hunt Mode Optimization)

```
Checkerboard pattern for smallest remaining ship (size 2):
  X . X . X . X . X .
  . X . X . X . X . X
  X . X . X . X . X .
  . X . X . X . X . X
  X . X . X . X . X .
  . X . X . X . X . X
  X . X . X . X . X .
  . X . X . X . X . X
  X . X . X . X . X .
  . X . X . X . X . X

Only need to check 50 cells to find all ships of size >= 2.
```

For remaining ships of size 3+, use every-3rd-cell pattern (34 cells needed).

### 7.8 Strategic Ship Placement (Hard/Expert)

- Avoid placing ships at edges (predictable)
- Spread ships across the board
- Avoid clusters (one hit reveals multiple ships)
- Place smaller ships in harder-to-find positions
- Vary placement between games (randomize with constraints)

## 8. User Interface

### 8.1 Ship Placement Screen

```
+------------------------------------------------------------------+
|  BATTLESHIP — Place Your Fleet                                   |
+------------------------------------------------------------------+
|                                                                  |
|  FLEET:                         YOUR OCEAN:                      |
|  +------------------+           A B C D E F G H I J              |
|  | [■■■■■] Carrier  |        1  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~             |
|  | [■■■■] Battleship|        2  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~             |
|  | [■■■] Cruiser    |        3  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~             |
|  | [■■■] Submarine  |        4  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~             |
|  | [■■] Destroyer   |        5  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~             |
|  +------------------+        6  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~             |
|                              7  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~             |
|  Selected: Carrier (5)       8  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~             |
|  Orientation: [H] [V]        9  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~             |
|                             10  ~ ~ ~ ~ ~ ~ ~ ~ ~ ~             |
|                                                                  |
|  Click a cell to place the bow of the selected ship              |
|                                                                  |
|  [Auto Place]  [Clear All]  [Ready!]                             |
+------------------------------------------------------------------+
```

### 8.2 Battle Screen

```
+------------------------------------------------------------------+
|  BATTLESHIP  vs AI (Medium)    You: 5/5 ships    AI: 3/5 ships   |
+------------------------------------------------------------------+
|                                                                  |
|  OPPONENT'S OCEAN — Click to attack:                             |
|       A   B   C   D   E   F   G   H   I   J                    |
|    +---+---+---+---+---+---+---+---+---+---+                    |
|  1 | ~ | ~ | ~ | X | ~ | ~ | ~ | ~ | ~ | ~ |                    |
|  2 | ~ | ~ | ~ | X | ~ | ~ | ~ | ~ | ~ | ~ |                    |
|  3 | ~ | O | ~ | X | ~ | ~ | ~ | ~ | ~ | ~ |                    |
|  4 | ~ | ~ | ~ | X | ~ | ~ | ~ | ~ | ~ | ~ |                    |
|  5 | ~ | ~ | ~ | X | ~ | ~ | ~ | ~ | ~ | ~ |  SUNK!            |
|  6 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |                    |
|  7 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |                    |
|  8 | ~ | ~ | X | X | X | ~ | ~ | ~ | ~ | ~ |  Cruiser SUNK     |
|  9 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | O | ~ | ~ |                    |
| 10 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |                    |
|    +---+---+---+---+---+---+---+---+---+---+                    |
|                                                                  |
|  YOUR OCEAN — opponent's attacks:                                |
|       A   B   C   D   E   F   G   H   I   J                    |
|    +---+---+---+---+---+---+---+---+---+---+                    |
|  1 | ~ | C | C | C | C | C | ~ | ~ | ~ | ~ |                    |
|  2 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |                    |
|  3 | ~ | ~ | ~ | D | ~ | ~ | ~ | ~ | ~ | ~ |                    |
|  4 | ~ | ~ | ~ | D | ~ | ~ | ~ | B | ~ | ~ |                    |
|  5 | O | ~ | ~ | ~ | ~ | ~ | ~ | X | ~ | ~ |  <-- hit!         |
|  6 | ~ | ~ | ~ | ~ | R | R | R | B | ~ | ~ |                    |
|  7 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | B | ~ | ~ |                    |
|  8 | ~ | O | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |                    |
|  9 | ~ | ~ | ~ | ~ | ~ | ~ | S | S | S | ~ |                    |
| 10 | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ | ~ |                    |
|    +---+---+---+---+---+---+---+---+---+---+                    |
|                                                                  |
|  AI Fleet Status:       Your Fleet Status:                       |
|  Carrier    [SUNK]      Carrier    [  OK  ]                      |
|  Battleship [?????]     Battleship [1 HIT ]                      |
|  Cruiser    [SUNK]      Cruiser    [  OK  ]                      |
|  Submarine  [?????]     Submarine  [  OK  ]                      |
|  Destroyer  [?????]     Destroyer  [  OK  ]                      |
|                                                                  |
|  Turn: 24   Last: You attacked D5 — HIT!                        |
+------------------------------------------------------------------+
|  [Resign]  [Settings]                                            |
+------------------------------------------------------------------+
```

### 8.3 Attack Interaction
1. Hover over opponent's grid shows crosshair
2. Already-attacked cells show a "no" cursor
3. Click to attack
4. Brief animation:
   - Miss: Splash animation, white circle appears
   - Hit: Explosion animation, red X appears
   - Sunk: All cells of ship revealed + sinking animation
5. Result text displayed ("Miss!", "Hit!", "You sunk the Battleship!")
6. After animation, AI takes its turn

### 8.4 AI Attack Display
- Brief pause before AI attacks (500ms-1s for dramatic effect)
- Show targeting reticle animation on your board
- Reveal result with animation
- Announce result ("AI attacks B5 — Miss!" or "AI attacks H5 — Hit!")

### 8.5 Game Over Screen

```
+-----------------------------+
|       GAME OVER             |
|                             |
|  YOU WIN!                   |
|                             |
|  Turns taken: 52            |
|  Accuracy: 17/52 = 32.7%   |
|  Ships sunk: 5/5            |
|  Your ships remaining: 3    |
|                             |
|  AI's hidden fleet:         |
|  (show full AI board)       |
|                             |
|  [Play Again] [New Setup]   |
+-----------------------------+
```

## 9. Game Flow

### 9.1 Complete Flow

```
1. New Game Setup
   - Select difficulty
   - Choose who goes first (human or random)

2. Ship Placement Phase
   a. Human places 5 ships on their board
   b. AI places 5 ships (instant, hidden)
   c. Confirm placement

3. Battle Phase (loop)
   a. Active player selects attack coordinate
   b. Check result: Hit, Miss, or Sunk
   c. Update boards
   d. Check for win (all opponent ships sunk)
   e. Switch turns

4. Game Over
   - Reveal both boards
   - Show statistics
   - Option to play again
```

## 10. Sound Effects

| Event              | Sound                          |
|--------------------|--------------------------------|
| Ship placement     | Anchor drop / horn             |
| Attack (miss)      | Water splash                   |
| Attack (hit)       | Explosion                      |
| Ship sunk          | Large explosion + horn         |
| Win                | Victory fanfare                |
| Lose               | Defeat sound + sinking         |
| Hover              | Soft sonar ping                |
| Invalid action     | Error buzz                     |
| AI thinking        | Sonar ping / radar sweep       |

## 11. Settings

| Setting              | Options                          | Default    |
|----------------------|----------------------------------|------------|
| Board theme          | Classic, Modern, Military, Ocean | Classic    |
| Attack animation     | On/Off                          | On         |
| Sound effects        | On/Off                          | On         |
| Show grid coordinates| On/Off                          | On         |
| AI attack delay      | 0.5s, 1s, 2s                    | 1s         |
| Auto place ships     | Button available                | Yes        |
| Ship gap rule        | Required/Not required           | Not required |

## 12. Statistics

| Statistic              | Description                     |
|------------------------|---------------------------------|
| Games played           | Per difficulty                  |
| Win/Loss record        | Per difficulty                  |
| Average shots to win   | Efficiency metric               |
| Best game (fewest shots)| Personal record                |
| Hit accuracy           | Hits / total shots              |
| Fastest sink           | Fewest shots to sink first ship |
| Perfect games          | Won without losing a ship       |

## 13. Keyboard Support

| Key          | Action                         |
|-------------|--------------------------------|
| A-J          | Select column                  |
| 1-0          | Select row (0 = row 10)       |
| Enter        | Confirm attack                 |
| R            | Rotate ship (placement phase)  |
| Space        | Fire / confirm                 |
| Ctrl+Z       | Undo placement                 |
| Ctrl+N       | New game                       |

## 14. Testing Scenarios

1. **Ship placement**: All 5 ships placed without overlap
2. **Out of bounds**: Ships cannot extend beyond grid
3. **Overlap detection**: Ships cannot overlap
4. **Hit detection**: Attacking a ship cell registers as hit
5. **Miss detection**: Attacking empty water registers as miss
6. **Sink detection**: All cells of a ship hit triggers sunk status
7. **Win detection**: All 5 opponent ships sunk triggers win
8. **No repeat attacks**: Same cell cannot be attacked twice
9. **AI hunt/target**: AI follows up hits correctly
10. **AI all ships found**: AI eventually sinks all ships
11. **Auto-place**: Random placement creates valid non-overlapping layout
12. **Full game**: Complete game from placement to victory runs correctly

## 15. Performance Requirements

| Metric                     | Target             |
|----------------------------|---------------------|
| Ship placement validation  | < 1ms              |
| Hit/Miss detection         | < 0.1ms            |
| AI move calculation        | < 100ms            |
| Attack animation           | 60 FPS             |
| Board render               | < 16ms             |
| AI probability density     | < 50ms             |

## 16. Accessibility

- Keyboard-only play fully supported
- High contrast colors for hits (red) and misses (white on blue)
- Screen reader: announce coordinates and results
- Magnification support for grid cells
- Color-blind mode: use shapes (X for hit, O for miss) in addition to colors
- Audio cues distinguish hits from misses clearly
