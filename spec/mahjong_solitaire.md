# Mahjong Solitaire — Complete Game Specification

## 1. Game Overview

Mahjong Solitaire (also called Shanghai or simply Mahjong) is a single-player tile
matching game using a set of Mahjong tiles. Tiles are stacked in a specific layout
and the player must remove matching pairs of "free" tiles until all tiles are cleared
or no more moves are possible.

- **Players**: 1 (single-player puzzle)
- **Tiles**: 144 Mahjong tiles (36 types, 4 copies each)
- **Objective**: Remove all tiles by matching free pairs
- **Win rate**: ~3% of layouts are unsolvable; typical win rate varies by layout

## 2. Technical Foundation

### 2.1 Tile Definitions

**Suited Tiles (3 suits x 9 ranks = 27 types, 4 copies each = 108 tiles):**

| Suit       | Ranks    | Symbol | Count |
|-----------|----------|--------|-------|
| Characters | 1-9     | 一-九   | 36    |
| Bamboo     | 1-9     | 🎋 1-9 | 36    |
| Circles    | 1-9     | ⊙ 1-9  | 36    |

**Honor Tiles (7 types, 4 copies each = 28 tiles):**

| Type    | Tiles                       | Count |
|---------|------------------------------|-------|
| Winds   | East, South, West, North    | 16    |
| Dragons | Red, Green, White            | 12    |

**Bonus Tiles (8 tiles, treated as 4 matching pairs):**

| Type    | Tiles                       | Matching Rule           |
|---------|------------------------------|-------------------------|
| Flowers | Plum, Orchid, Chrysanthemum, Bamboo | Any flower matches any flower |
| Seasons | Spring, Summer, Autumn, Winter | Any season matches any season |

**Total: 108 + 28 + 8 = 144 tiles**

### 2.2 Tile Visual (ASCII)

```
Single tile:        Stacked tiles:
+--------+          +--------+
| Char 1 |          |+------+|
| 一     |          || Bam 5||
|        |          ||      ||
+--------+          |+------+|
                    +--------+
```

### 2.3 Matching Rules

| Tile Category | Matching Rule                              |
|---------------|---------------------------------------------|
| Characters 1  | Matches only with other Characters 1        |
| Bamboo 5      | Matches only with other Bamboo 5            |
| Circle 9      | Matches only with other Circle 9            |
| East Wind     | Matches only with other East Wind           |
| Red Dragon    | Matches only with other Red Dragon          |
| Any Flower    | Matches with ANY other Flower tile          |
| Any Season    | Matches with ANY other Season tile          |

## 3. Tile Layout (Turtle Formation — Standard)

### 3.1 Overview

The standard "Turtle" layout consists of tiles arranged in a pyramid-like structure
with multiple layers. The layout is viewed from above.

### 3.2 Layer Structure

| Layer  | Name    | Tiles | Description                         |
|--------|---------|-------|-------------------------------------|
| 1      | Base    | 86    | Largest layer, forms the foundation |
| 2      | Second  | 40    | Centered on top of base             |
| 3      | Third   | 14    | Centered on top of second           |
| 4      | Fourth  | 2     | Two tiles side by side              |
| 5      | Cap     | 1     | Single tile on very top             |
| Special| Wings   | 1     | Single tile extending left of base  |
| **Total** |      | **144** |                                   |

### 3.3 Base Layer (Layer 1) — Top View

```
Layer 1 (base):
              Col: 1 2 3 4 5 6 7 8 9 10 11 12
        Row 1:             [T][T][T][T][T][T]
        Row 2:         [T][T][T][T][T][T][T][T]
        Row 3:     [T][T][T][T][T][T][T][T][T][T]
        Row 4: [T][T][T][T][T][T][T][T][T][T][T][T] [T]  <- wing
        Row 5:     [T][T][T][T][T][T][T][T][T][T]
        Row 6:         [T][T][T][T][T][T][T][T]
        Row 7:             [T][T][T][T][T][T]
        Row 8:             [T][T][T][T][T][T]
```

### 3.4 Upper Layers

```
Layer 2 (centered on base):
        Row 2:         [T][T][T][T][T][T]
        Row 3:         [T][T][T][T][T][T]
        Row 4:         [T][T][T][T][T][T]
        Row 5:         [T][T][T][T][T][T]
        Row 6:         [T][T][T][T]

Layer 3:
        Row 3:             [T][T][T][T]
        Row 4:             [T][T][T][T]
        Row 5:             [T][T][T][T]

Layer 4:
        Row 4:               [T][T]

Layer 5 (cap):
        Row 4:                [T]
```

### 3.5 3D Visualization (Side View)

```
Side view (looking from the left):

   Layer 5:     [5]
   Layer 4:    [4][4]
   Layer 3:   [3][3][3]
   Layer 2:  [2][2][2][2]
   Layer 1: [1][1][1][1][1][1]
```

## 4. Core Rules

### 4.1 Free Tile Definition

A tile is "free" (selectable/removable) if it meets BOTH conditions:

1. **Not blocked from above**: No tile is sitting on top of it (partially or fully)
2. **Free on left OR right side**: At least one side (left or right) has no adjacent
   tile at the same layer

```
function isFree(tile):
    // Check if blocked from above
    for each tile above:
        if overlapsHorizontally(tile, tileAbove):
            return false

    // Check if left side is free
    leftFree = no tile at (tile.row, tile.col - 1, tile.layer)
    // Check if right side is free
    rightFree = no tile at (tile.row, tile.col + 1, tile.layer)

    return leftFree or rightFree
```

### 4.2 Overlap Detection (Above)

A tile on layer N+1 blocks a tile on layer N if their positions overlap. Each tile
occupies a 2x1 grid unit. A tile above blocks the tile below if the above tile
overlaps ANY part of the below tile.

```
function isBlockedFromAbove(tile):
    layer = tile.layer
    for each tile T on layer+1:
        if T.row overlaps tile.row and T.col overlaps tile.col:
            return true
    return false
```

### 4.3 Move Rules

1. Select a free tile (click)
2. Select a second free tile that matches the first
3. Both tiles are removed from the layout
4. This may make previously blocked tiles free
5. If no matching pairs of free tiles exist, the game is stuck

### 4.4 Valid Move

```
function isValidMove(tile1, tile2):
    return tile1 != tile2           // not the same tile
       and isFree(tile1)            // first tile is free
       and isFree(tile2)            // second tile is free
       and tilesMatch(tile1, tile2) // tiles are a matching pair
```

## 5. Game State

| State Variable         | Type              | Description                          |
|------------------------|-------------------|--------------------------------------|
| layout                 | 3D array          | Tiles arranged in layers/rows/cols   |
| tilesRemaining         | integer           | Number of tiles left (starts at 144) |
| pairsRemaining         | integer           | Matching pairs still available       |
| freeTiles              | list              | Currently free tiles                 |
| matchablePairs         | integer           | Free tiles that have a matching free partner |
| selectedTile           | Tile/null         | Currently selected tile              |
| moveHistory            | list              | All pairs removed                    |
| score                  | integer           | Current score                        |
| elapsedTime            | seconds           | Game timer                           |
| shufflesRemaining      | integer           | Reshuffles available                 |
| hintsRemaining         | integer           | Hints available                      |

## 6. Scoring

### 6.1 Standard Scoring

| Action                        | Points     |
|-------------------------------|------------|
| Match a pair                  | +100       |
| Match bonus tiles (flowers/seasons) | +150 |
| Consecutive matches (combo)   | +50 per combo level |
| Speed bonus (match within 5s) | +25        |
| Complete the game             | +5000      |
| Time bonus                    | +max(0, 30000 - elapsed_seconds * 10) |

### 6.2 Combo System

| Combo Level | Consecutive Matches | Bonus per Match |
|-------------|---------------------|-----------------|
| 1           | 1                   | 0               |
| 2           | 2                   | +50             |
| 3           | 3                   | +100            |
| 4           | 4                   | +150            |
| 5+          | 5+                  | +200            |

Combo resets after 10 seconds without a match.

## 7. Tile Shuffling and Dealing

### 7.1 Initial Layout Generation

```
function generateLayout(layoutTemplate, seed):
    rng = SeededRandom(seed)
    tiles = createFullTileSet()  // 144 tiles
    shuffle(tiles, rng)

    positions = layoutTemplate.getAllPositions()  // 144 positions
    for i in 0..143:
        positions[i].tile = tiles[i]

    // Verify solvability (optional)
    if not isSolvable(layout):
        regenerate with different seed
```

### 7.2 Ensuring Solvability

To guarantee a solvable layout:
1. Start with an empty layout
2. Place pairs in reverse order (simulate solving backward)
3. Each pair placed must be in "free" positions

```
function generateSolvableLayout(template):
    layout = empty layout from template
    tiles = createFullTileSet()
    shuffle(tiles)

    while tiles not empty:
        pair = take next pair from tiles
        pos1, pos2 = findTwoFreePositions(layout)
        place pair at pos1 and pos2

    return layout
```

### 7.3 Reshuffle

When the player is stuck (or uses a reshuffle power-up):
1. Collect all remaining tiles from the layout
2. Shuffle them
3. Place them back in the same positions (maintaining layout structure)
4. Preferably ensure the reshuffled layout is solvable

## 8. Alternative Layouts

### 8.1 Layout Options

| Layout Name  | Tiles | Difficulty | Description                          |
|-------------|-------|------------|--------------------------------------|
| Turtle      | 144   | Standard   | Classic pyramid shape                |
| Fortress    | 144   | Hard       | Tall, narrow structure               |
| Pyramid     | 144   | Medium     | True pyramid shape                   |
| Bridge      | 144   | Medium     | Arch-shaped layout                   |
| Cat         | 144   | Easy       | Cat-shaped flat layout               |
| Spider      | 144   | Hard       | Spider web pattern                   |
| Arrow       | 144   | Medium     | Arrow pointing right                 |
| Cross       | 140   | Easy       | Plus/cross shape (fewer tiles)       |
| Diamond     | 144   | Medium     | Diamond shape                        |
| Ziggurat    | 144   | Hard       | Step pyramid                         |

### 8.2 Custom Layout Definition

Layouts defined as a list of (layer, row, col) positions:

```
Layout {
    name: string
    positions: [(layer, row, col)]  // exactly 144 positions
    difficulty: EASY | MEDIUM | HARD
    thumbnail: ASCII preview
}
```

## 9. User Interface

### 9.1 Main Game Screen

```
+------------------------------------------------------------------+
|  MAHJONG SOLITAIRE                Score: 1,250   Time: 05:42     |
+------------------------------------------------------------------+
|  Tiles: 98/144    Pairs Available: 12    Layout: Turtle          |
|                                                                  |
|                                                                  |
|                   +--+ +--+ +--+ +--+                            |
|                   |  | |  | |  | |  |     Layer 3               |
|                   +--+ +--+ +--+ +--+                            |
|                +--+--+--+--+--+--+--+--+                         |
|                |  |  |  |  |  |  |  |  |  Layer 2               |
|                +--+--+--+--+--+--+--+--+                         |
|           +--+--+--+--+--+--+--+--+--+--+--+                    |
|           |  |  |C3|B7|  |  |  |W |E |  |  |  Layer 1          |
|           +--+--+--+--+--+--+--+--+--+--+--+                    |
|        +--+--+--+--+--+--+--+--+--+--+--+--+--+                 |
|   +--+ |  |  |  |  |  |  |  |  |  |  |  |  |  |                |
|   |  | +--+--+--+--+--+--+--+--+--+--+--+--+--+                |
|        +--+--+--+--+--+--+--+--+--+--+--+                       |
|        |  |  |  |  |  |  |  |  |  |  |  |                       |
|        +--+--+--+--+--+--+--+--+--+--+--+                       |
|           +--+--+--+--+--+--+--+--+--+                           |
|           |  |  |  |  |  |  |  |  |  |                           |
|           +--+--+--+--+--+--+--+--+--+                           |
|              +--+--+--+--+--+--+--+                              |
|              |  |  |  |  |  |  |  |                              |
|              +--+--+--+--+--+--+--+                              |
|                                                                  |
|  Selected: [Bamboo 7]  (click a matching free tile)              |
+------------------------------------------------------------------+
|  [Hint (3)] [Shuffle (2)] [Undo] [New Game] [Settings]           |
+------------------------------------------------------------------+
```

### 9.2 Tile Appearance

```
Free tile:           Blocked tile:        Selected tile:
+--------+           +--------+           +========+
| Char 1 |           | Char 1 |           | Bam 7  |
| 一     |           | 一     |  (dimmed) || Bam 7 ||
|        |           |        |           ||       ||
+--------+           +--------+           +========+
  bright               darker              glowing border
```

### 9.3 3D Effect

Tiles on higher layers cast a shadow on tiles below, creating depth:
- Layer offset: Each layer is offset 2px right and 2px up
- Shadow: Tiles cast a soft shadow (3px, semi-transparent)
- Higher layer tiles appear on top visually

### 9.4 Interaction Model

1. Click a free tile to select it (highlights with a border)
2. Click a second free tile:
   - If it matches: both tiles are removed with animation
   - If it doesn't match: show brief error indicator, deselect
3. Click the same selected tile to deselect
4. Click a non-free tile: show "blocked" indicator (briefly)

### 9.5 Match Animation
- Both tiles glow
- Tiles slide toward each other and fade out (300ms)
- Or: tiles flip over and disappear
- Score popup appears briefly at the match location

### 9.6 Removal Animation
```
Step 1: Both tiles glow golden    (100ms)
Step 2: Tiles shrink and fade     (200ms)
Step 3: Tiles disappear           (100ms)
Step 4: Score "+100" floats up    (500ms)
```

## 10. Hint System

### 10.1 Hint Behavior
- Highlights one available matching pair of free tiles
- Tiles flash/pulse for 3 seconds
- Uses one hint charge
- Default: 3 hints per game (configurable)
- No hints available = "No hints remaining" message

### 10.2 Hint Algorithm

```
function findHint(layout):
    freeTiles = getAllFreeTiles(layout)
    for i in 0..freeTiles.length:
        for j in i+1..freeTiles.length:
            if tilesMatch(freeTiles[i], freeTiles[j]):
                return (freeTiles[i], freeTiles[j])
    return null  // no matches available
```

## 11. Game Flow

### 11.1 New Game Setup

```
+---------------------------+
|   MAHJONG SOLITAIRE      |
|                           |
|  Layout:                  |
|  (•) Turtle (Standard)   |
|  ( ) Fortress             |
|  ( ) Pyramid              |
|  ( ) Bridge               |
|  ( ) Cat                  |
|                           |
|  Difficulty:              |
|  ( ) Easy (more hints)    |
|  (•) Normal               |
|  ( ) Hard (no hints)      |
|                           |
|  Hints: [3]               |
|  Shuffles: [2]            |
|  Timed: [Yes]             |
|                           |
|  [Start Game]             |
|  [Game #: ________]       |
+---------------------------+
```

### 11.2 Game Loop

```
1. Generate layout and deal tiles
2. Display initial layout
3. Start timer
4. Main loop:
   a. Highlight free tiles (subtle indicator)
   b. Wait for player to select a free tile
   c. Wait for player to select a second free tile
   d. If match: remove pair, update score, check win
   e. If no match: deselect, show error
   f. Update free tiles list
   g. Check if any matches available
   h. If no matches and tiles remain: offer shuffle or end game
   i. If all tiles removed: WIN
5. Display results
```

### 11.3 No Moves Available

```
+---------------------------+
|  NO MOVES AVAILABLE       |
|                           |
|  Tiles remaining: 46      |
|                           |
|  Options:                 |
|  [Shuffle (2 left)]       |
|  [Undo Last 5 Moves]      |
|  [New Game]                |
+---------------------------+
```

### 11.4 Win Screen

```
+----------------------------------+
|      CONGRATULATIONS!            |
|                                  |
|  All tiles cleared!              |
|                                  |
|  Score: 12,450                   |
|  Time: 08:23                     |
|  Pairs matched: 72               |
|  Hints used: 1                   |
|  Shuffles used: 0                |
|  Best combo: 5x                  |
|                                  |
|  [Play Again] [New Layout]       |
+----------------------------------+
```

## 12. Sound Effects

| Event                 | Sound                          |
|-----------------------|--------------------------------|
| Select tile           | Soft "click" / tile tap        |
| Match found           | Pleasant chime                 |
| Bonus tile match      | Special chime                  |
| No match              | Soft thud                      |
| Tile blocked          | Muted error tone               |
| Combo (2x+)           | Escalating chimes              |
| Hint used             | Soft bell                      |
| Shuffle               | Tiles rattling / shuffling     |
| Win                   | Triumphant fanfare             |
| No moves              | Warning tone                   |
| Game start            | Tiles being dealt sound        |

## 13. Settings

| Setting              | Options                          | Default    |
|----------------------|----------------------------------|------------|
| Layout               | Turtle, Fortress, Pyramid, etc. | Turtle     |
| Tile style           | Traditional, Modern, Simple     | Traditional|
| Background           | Green felt, Wood, Dark, Custom  | Green      |
| 3D depth effect      | On/Off                          | On         |
| Highlight free tiles | On/Off                          | Off        |
| Sound effects        | On/Off                          | On         |
| Music                | On/Off                          | Off        |
| Hint count           | 0, 1, 3, 5, Unlimited          | 3          |
| Shuffle count        | 0, 1, 2, 3, Unlimited          | 2          |
| Show timer           | On/Off                          | On         |
| Animation speed      | Slow, Normal, Fast              | Normal     |

## 14. Data Structures

### 14.1 Tile

```
Tile {
    id: unique integer
    type: enum (CHARACTER, BAMBOO, CIRCLE, WIND, DRAGON, FLOWER, SEASON)
    rank: integer or string
    matchGroup: integer  // tiles with same matchGroup can match
    layer: integer       // 0-4
    row: integer
    col: integer
    removed: boolean
}
```

### 14.2 Layout

```
Layout {
    name: string
    positions: [(layer, row, col)]  // 144 positions
    tiles: [Tile]                    // tiles at each position
}
```

### 14.3 Free Tile Detection

```
function getFreeTiles(layout):
    freeTiles = []
    for each tile in layout.tiles:
        if tile.removed: continue
        if not isBlockedAbove(tile, layout) and
           (isLeftFree(tile, layout) or isRightFree(tile, layout)):
            freeTiles.add(tile)
    return freeTiles
```

## 15. Testing Scenarios

1. **Free tile detection**: Correctly identifies all free tiles
2. **Blocked tile**: Tile under another tile is not free
3. **Side-blocked tile**: Tile with tiles on both sides is not free
4. **Matching pairs**: Same type tiles match correctly
5. **Flower/Season matching**: Any flower matches any flower
6. **Removal updates**: Removing a pair makes new tiles free
7. **Win detection**: All 144 tiles removed = win
8. **No moves detection**: Correctly identifies when no free matches exist
9. **Shuffle works**: Reshuffled layout is playable
10. **Layout generation**: All 144 tiles placed correctly
11. **Layer stacking**: Upper layers correctly block lower layers
12. **Undo**: Correctly restores removed tiles
13. **Solvable generation**: Generated layouts are solvable

## 16. Performance Requirements

| Metric                     | Target             |
|----------------------------|---------------------|
| Free tile calculation      | < 5ms              |
| Match detection            | < 1ms              |
| Full board render          | < 16ms (60 FPS)   |
| Tile removal animation     | 60 FPS             |
| Shuffle operation          | < 100ms            |
| Layout generation          | < 500ms            |
| Hint calculation           | < 10ms             |

## 17. Accessibility

- Tile labels with text (suit and rank always visible)
- Color-blind mode: use distinct patterns for each suit
- Keyboard navigation: Tab between free tiles, Enter to select
- Screen reader: announce tile type, position, and whether free
- Zoom capability for small tiles
- High contrast tile borders
- Large tile option
- "Show matches" mode: highlight all tiles matching the selected one
