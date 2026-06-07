# Dominoes — Complete Game Specification

## 1. Game Overview

Dominoes is a classic tile-based game where players take turns placing rectangular
tiles with numbered ends onto a shared layout, matching the numbers on adjacent tile
ends. This specification covers the most popular variant: Draw Dominoes (Block/Draw).

- **Players**: 2 (Human vs AI) or 4 (Human + 3 AI)
- **Tile set**: Standard double-six set (28 tiles)
- **Objective**: Be the first to play all your tiles, or have the lowest pip count
  when the game is blocked
- **Variants covered**: Draw Dominoes, Block Dominoes, All Fives (Muggins)

## 2. Technical Foundation

### 2.1 Tile Definitions

Each domino tile has two halves, each showing 0-6 pips (dots). A standard
double-six set contains every unique combination.

**Complete Double-Six Set (28 tiles):**

| Tile   | Pips | Total | Type      |
|--------|------|-------|-----------|
| [0|0]  | 0+0  | 0     | Double    |
| [0|1]  | 0+1  | 1     | Regular   |
| [0|2]  | 0+2  | 2     | Regular   |
| [0|3]  | 0+3  | 3     | Regular   |
| [0|4]  | 0+4  | 4     | Regular   |
| [0|5]  | 0+5  | 5     | Regular   |
| [0|6]  | 0+6  | 6     | Regular   |
| [1|1]  | 1+1  | 2     | Double    |
| [1|2]  | 1+2  | 3     | Regular   |
| [1|3]  | 1+3  | 4     | Regular   |
| [1|4]  | 1+4  | 5     | Regular   |
| [1|5]  | 1+5  | 6     | Regular   |
| [1|6]  | 1+6  | 7     | Regular   |
| [2|2]  | 2+2  | 4     | Double    |
| [2|3]  | 2+3  | 5     | Regular   |
| [2|4]  | 2+4  | 6     | Regular   |
| [2|5]  | 2+5  | 7     | Regular   |
| [2|6]  | 2+6  | 8     | Regular   |
| [3|3]  | 3+3  | 6     | Double    |
| [3|4]  | 3+4  | 7     | Regular   |
| [3|5]  | 3+5  | 8     | Regular   |
| [3|6]  | 3+6  | 9     | Regular   |
| [4|4]  | 4+4  | 8     | Double    |
| [4|5]  | 4+5  | 9     | Regular   |
| [4|6]  | 4+6  | 10    | Regular   |
| [5|5]  | 5+5  | 10    | Double    |
| [5|6]  | 5+6  | 11    | Regular   |
| [6|6]  | 6+6  | 12    | Double    |

**Total pips in set**: 168 (sum of all tile values)
**Number of doubles**: 7 ([0|0] through [6|6])
**Number of regular tiles**: 21

### 2.2 Tile Visual (ASCII)

```
Regular tile (horizontal):    Double tile (vertical):
+-----+-----+                 +-----+
|  *  |     |                 |  *  |
| * * | * * |                 |  *  |
|  *  |     |                 |  *  |
+-----+-----+                 +-----+
  [3]   [2]                    +-----+
                               |  *  |
Face-down tile:                |  *  |
+-----+-----+                 |  *  |
|/////|/////|                  +-----+
|/////|/////|                    [3]
|/////|/////|                    [3]
+-----+-----+
```

### 2.3 Pip Layouts

```
0 pips:  |     |    1 pip:   |  *  |    2 pips:  | *   |
         |     |             |     |             |     |
         |     |             |     |             |   * |

3 pips:  | *   |    4 pips:  | * * |    5 pips:  | * * |
         |  *  |             |     |             |  *  |
         |   * |             | * * |             | * * |

6 pips:  | * * |
         | * * |
         | * * |
```

## 3. Game Variants

### 3.1 Draw Dominoes (Default)

- If a player cannot play, they draw from the boneyard (stock)
- Keep drawing until a playable tile is found or boneyard is empty
- When boneyard has 2 or fewer tiles, it is closed (no more drawing)

### 3.2 Block Dominoes

- If a player cannot play, they pass (no drawing)
- Game blocks when no player can play
- Player with lowest total pip count wins

### 3.3 All Fives (Muggins)

- Same as Draw Dominoes but with scoring during play
- Points scored when the exposed ends sum to a multiple of 5
- First to reach 100 (or 150/200) points wins

## 4. Core Rules (Draw Dominoes)

### 4.1 Setup

**2 players**: Each draws 7 tiles
**3 players**: Each draws 7 tiles (7 in boneyard)
**4 players**: Each draws 7 tiles (0 in boneyard — no drawing possible)

The remaining tiles form the boneyard (face down).

### 4.2 Starting the Game
- Player with the highest double goes first and plays that double
- If no one has a double, the player with the highest-value tile goes first
- The first tile is placed in the center of the play area

### 4.3 Turn Sequence

1. Player must play a tile that matches one of the open ends of the layout
2. If no matching tile in hand:
   a. Draw one tile from the boneyard
   b. If it can be played, play it (or keep and pass)
   c. If it cannot be played, draw again
   d. Continue until a playable tile is drawn or boneyard has <= 2 tiles
3. If boneyard is exhausted and no playable tile: pass

### 4.4 Placement Rules

- A tile can be placed at either open end of the layout (the chain)
- The matching number on the played tile must touch the matching open end
- Doubles are placed perpendicular to the chain
- Non-doubles are placed in line with the chain

### 4.5 Layout Example

```
Starting tile:
                [3|3]

After several plays:
         [5|3]-[3|3]-[3|1]-[1|6]
                 |
               [3|4]
                 |
               [4|2]

Open ends: 5, 6, 2 (three open ends because of the double)
```

Wait — standard dominoes only has two open ends (the chain goes left and right).
Doubles are played crosswise but do not create branches. Let me correct:

### 4.5 Layout (Corrected)

The layout is a single chain with two open ends. Doubles are placed crosswise
but do not create branches (except in certain variants).

```
Simple chain:
[2|5]-[5|3]-[3|3]-[3|1]-[1|6]-[6|4]

Open ends: 2 (left) and 4 (right)

With doubles displayed crosswise:
                      +---+
[2|5]-[5|3]-[3|  ]-[  |1]-[1|6]-[6|4]
                |3|
                +---+

The chain still has two open ends: 2 and 4.
```

When the chain gets long, it snakes around the play area:
```
[2|5]-[5|3]-[3|3]-[3|1]-[1|6]-[6|4]-[4|4]-[4|0]+
                                                 |
     +[2|2]-[2|6]-[6|1]-[1|5]-[5|5]-[5|0]-[0|0]+
     |
[6|2]+

Open ends: 6 (bottom-left) and 2 (top-left)
```

### 4.6 Matching Rule

```
function canPlay(tile, openEnd):
    return tile.left == openEnd or tile.right == openEnd

function placeTile(tile, end):
    if tile.left == openEndValue:
        // Place tile with left side touching
        // Right side becomes new open end
    elif tile.right == openEndValue:
        // Place tile with right side touching
        // Left side becomes new open end
```

## 5. Scoring

### 5.1 Draw/Block Dominoes Scoring

**Round winner**: First player to empty their hand, OR the player with
the lowest total pip count when the game is blocked.

**Points awarded**: Sum of all pips in opponents' hands.

**Example:**
- Player A empties hand
- Player B has: [3|5], [2|4] = 14 pips
- AI has: [6|6], [1|0] = 13 pips
- Player A scores: 14 + 13 = 27 points

### 5.2 All Fives Scoring

Points earned during play when open ends total a multiple of 5:

| Open End Sum | Points |
|-------------|--------|
| 5           | 5      |
| 10          | 10     |
| 15          | 15     |
| 20          | 20     |
| 25          | 25     |
| 30          | 30     |

Plus end-of-round scoring as in standard Draw Dominoes.

**Target score**: First to 100, 150, or 200 points (configurable).

### 5.3 Blocked Game

When no player can play and the boneyard is empty (or closed):
- The player with the lowest total pip count in hand wins the round
- Winner scores the difference between all opponents' pips and their own
- In case of a tie in pip count, the player with fewer tiles wins

## 6. Game State

| State Variable         | Type              | Description                          |
|------------------------|-------------------|--------------------------------------|
| tiles (per player)     | list of Tile      | Player's hand                        |
| boneyard               | list of Tile      | Undrawn tiles                        |
| chain                  | linked list       | Played tiles in order                |
| openEnds               | [int, int]        | Values at each end of the chain      |
| currentPlayer          | integer           | Active player index                  |
| scores                 | list of int       | Cumulative score per player          |
| targetScore            | integer           | Score to win                         |
| roundNumber            | integer           | Current round                        |
| passCount              | integer           | Consecutive passes (for block detect)|
| variant                | enum              | DRAW, BLOCK, ALL_FIVES              |
| boneyardOpen           | boolean           | Whether drawing is still allowed     |

### 6.1 Tile Data Structure

```
Tile {
    left: integer (0-6)   // one half
    right: integer (0-6)  // other half
    isDouble: boolean     // left == right
    totalPips: integer    // left + right
}
```

## 7. AI Opponent

### 7.1 Difficulty Levels

| Level    | Strategy                                          |
|----------|---------------------------------------------------|
| Easy     | Plays random valid tile                           |
| Medium   | Prefers doubles first, blocks opponent ends       |
| Hard     | Tracks tiles, blocks strategically, optimizes ends|
| Expert   | Full tile tracking, probability-based decisions   |

### 7.2 Easy AI
```
function easyAITurn(hand, openEnds):
    playableTiles = getPlayable(hand, openEnds)
    if playableTiles is empty:
        drawFromBoneyard()
        return
    tile = random(playableTiles)
    end = random valid end for tile
    play(tile, end)
```

### 7.3 Medium AI
```
function mediumAITurn(hand, openEnds):
    playableTiles = getPlayable(hand, openEnds)
    if playableTiles is empty:
        drawFromBoneyard()
        return

    // Priority: play doubles first (get rid of them)
    doubles = filter(playableTiles, tile -> tile.isDouble)
    if doubles:
        tile = highestDouble(doubles)
    else:
        // Play highest pip count tile
        tile = highestPipTile(playableTiles)

    // Choose end that blocks opponent (if possible)
    end = chooseEnd(tile, openEnds, hand)
    play(tile, end)
```

### 7.4 Hard AI
```
function hardAITurn(hand, openEnds, gameState):
    playableTiles = getPlayable(hand, openEnds)
    if playableTiles is empty:
        drawFromBoneyard()
        return

    bestScore = -infinity
    bestMove = null

    for tile in playableTiles:
        for end in validEnds(tile, openEnds):
            score = evaluateMove(tile, end, hand, gameState)
            if score > bestScore:
                bestScore = score
                bestMove = (tile, end)

    play(bestMove.tile, bestMove.end)

function evaluateMove(tile, end, hand, gameState):
    score = 0

    // Prefer playing doubles early
    if tile.isDouble: score += 10

    // Prefer high pip count (reduces hand value)
    score += tile.totalPips * 2

    // Prefer ends that match other tiles in hand
    newEnd = otherSide(tile, end)
    matchingTiles = count(hand, tile -> hasValue(tile, newEnd))
    score += matchingTiles * 5

    // Penalize leaving an end where opponent likely has tiles
    knownOpponentValues = estimateOpponentValues(gameState)
    if newEnd in knownOpponentValues: score -= 8

    // In All Fives: prefer moves that score multiples of 5
    if variant == ALL_FIVES:
        newSum = calculateOpenEndSum(after playing tile at end)
        if newSum % 5 == 0: score += newSum

    return score
```

### 7.5 Expert AI — Tile Tracking

The Expert AI tracks which tiles have been played and can infer which tiles
opponents hold:

```
function trackTiles(gameState):
    allTiles = set of all 28 tiles
    playedTiles = tiles on the chain
    myTiles = tiles in my hand
    knownTiles = playedTiles + myTiles
    unknownTiles = allTiles - knownTiles

    // Track what opponents drew and passed on
    for each opponent:
        if opponent passed on value X:
            opponent definitely has no tiles with value X
            remove those possibilities

    return probability distribution of opponent hands
```

## 8. User Interface

### 8.1 Main Game Screen

```
+------------------------------------------------------------------+
|  DOMINOES (Draw)  Round 3          Score: You-45  AI-38          |
+------------------------------------------------------------------+
|                                                                  |
|  AI Hand: [?][?][?][?][?]  (5 tiles)    Boneyard: 8 tiles       |
|                                                                  |
|  +-----------+                                                   |
|  |  PLAYING  |                                                   |
|  |   FIELD   |                                                   |
|  |           |                                                   |
|  | [5|3]-[3|3]-[3|1]-[1|6]-[6|4]-[4|2]                          |
|  |                                                               |
|  |  Open ends: [5] and [2]                                      |
|  +-----------+                                                   |
|                                                                  |
|  YOUR HAND:                                                      |
|  +-----+ +-----+ +-----+ +-----+ +-----+ +-----+ +-----+      |
|  |2 | 5| |0 | 2| |6 | 6| |1 | 4| |5 | 5| |3 | 6| |0 | 4|      |
|  +-----+ +-----+ +-----+ +-----+ +-----+ +-----+ +-----+      |
|   Play✓   Play✓   Play✗   Play✗   Play✓   Play✗   Play✗        |
|                                                                  |
|  Select a tile, then choose which end to play it on              |
+------------------------------------------------------------------+
|  [Draw from Boneyard]  [Pass]  [Settings]                        |
+------------------------------------------------------------------+
```

### 8.2 Tile Selection and Placement

1. Click a playable tile in your hand to select it
2. If tile can play on both ends, choose which end:
   ```
   +-----------------------------------+
   |  Play [2|5] on which end?         |
   |                                   |
   |  [Left end (5)]  [Right end (2)]  |
   +-----------------------------------+
   ```
3. Tile slides from hand to the chain with animation

### 8.3 Chain Display

When the chain gets too long, it wraps:
```
[2|5]-[5|3]-[3|3]-[3|1]-[1|6]-[6|4]-[4|4]-[4|0]+
                                                 |
            +[2|6]-[6|1]-[1|5]-[5|5]-[5|0]-[0|0]+
            |
       [6|2]+
```

Alternatively, use scrolling/zoom for very long chains.

### 8.4 All Fives Score Display

```
+------------------------------------------------------------------+
|  You played [3|2] on the left end                                |
|  Open ends: 2 + 6 + 3 = 11  (no score)                         |
|                                                                  |
|  AI played [6|4] on the right end                                |
|  Open ends: 2 + 4 + 3 = 9  (no score)                          |
|                                                                  |
|  You played [2|3] on the left end                                |
|  Open ends: 3 + 4 + 3 = 10  → SCORE 10 POINTS!                 |
+------------------------------------------------------------------+
```

## 9. Game Flow

### 9.1 Round Sequence

```
1. Shuffle all 28 tiles
2. Deal 7 tiles to each player
3. Remaining tiles go to boneyard
4. Determine first player (highest double)
5. First player places their starting tile
6. Main loop:
   a. Current player checks for playable tiles
   b. If playable: select and place tile
   c. If not playable:
      - Draw: draw from boneyard until playable or empty
      - Block: pass turn
   d. Check for round end:
      - Player emptied hand → wins round
      - All players passed consecutively → blocked game
   e. Advance to next player
7. Score the round
8. Check for game win (target score)
9. If not won, start new round
```

### 9.2 New Game Setup

```
+---------------------------+
|     NEW DOMINOES GAME     |
|                           |
|  Players: [2] [3] [4]    |
|                           |
|  Variant:                 |
|  (•) Draw Dominoes        |
|  ( ) Block Dominoes       |
|  ( ) All Fives (Muggins)  |
|                           |
|  AI Difficulty:           |
|  ( ) Easy                 |
|  (•) Medium               |
|  ( ) Hard                 |
|  ( ) Expert               |
|                           |
|  Target Score: [100]      |
|                           |
|  [Start Game]             |
+---------------------------+
```

### 9.3 Round End Screen

```
+----------------------------------+
|      ROUND OVER                  |
|                                  |
|  You win this round!             |
|                                  |
|  Your remaining pips: 0          |
|  AI remaining pips: 18           |
|                                  |
|  Points earned: 18               |
|                                  |
|  Running score:                  |
|  You: 63    AI: 38               |
|                                  |
|  Target: 100                     |
|                                  |
|  [Next Round] [Quit]             |
+----------------------------------+
```

## 10. Sound Effects

| Event              | Sound                          |
|--------------------|--------------------------------|
| Place tile         | Clacking/clicking sound        |
| Draw from boneyard | Tile sliding sound             |
| Pass turn          | Subtle "knock" sound           |
| Double played      | Slightly louder clack          |
| Score (All Fives)  | Chime / coin sound             |
| Win round          | Victory jingle                 |
| Lose round         | Defeat tone                    |
| Blocked game       | Warning tone                   |
| Game start         | Tiles shuffling                |

## 11. Settings

| Setting              | Options                          | Default    |
|----------------------|----------------------------------|------------|
| Number of players    | 2, 3, 4                         | 2          |
| Variant              | Draw, Block, All Fives          | Draw       |
| AI difficulty        | Easy, Medium, Hard, Expert      | Medium     |
| Target score         | 50, 100, 150, 200              | 100        |
| Tile style           | Classic, Modern, Minimalist     | Classic    |
| Table color          | Green, Brown, Blue              | Green      |
| Sound effects        | On/Off                          | On         |
| Show pip count       | On/Off                          | On         |
| Auto-play singles    | On/Off                          | Off        |
| Animation speed      | Slow, Normal, Fast              | Normal     |

## 12. Testing Scenarios

1. **Starting player**: Highest double goes first
2. **Matching rule**: Tile placed matches open end value
3. **Double placement**: Double placed perpendicular
4. **Drawing**: Player draws until playable tile found
5. **Boneyard empty**: Player must pass when boneyard empty + no plays
6. **Blocked game**: All players pass → lowest pips wins
7. **Win by emptying hand**: First to 0 tiles wins round
8. **Scoring**: Winner gets sum of opponents' remaining pips
9. **All Fives scoring**: Correctly detects multiples of 5
10. **Chain integrity**: Open ends update correctly after each play
11. **Tile uniqueness**: No duplicate tiles in the set
12. **Full deal (4 players)**: All 28 tiles dealt, no boneyard

## 13. Performance Requirements

| Metric                     | Target             |
|----------------------------|---------------------|
| Tile matching check        | < 0.1ms            |
| AI move (all levels)       | < 500ms            |
| Tile animation             | 60 FPS             |
| Chain render               | < 16ms             |
| Shuffle                    | < 5ms              |

## 14. Accessibility

- Large tile display with clear pip markings
- Pip count shown as numbers alongside dots
- Color-blind safe (relies on shape/number, not color)
- Keyboard: arrow keys to browse hand, Enter to select, L/R for end choice
- Screen reader: announce tile values and open ends
- Zoom capability for the chain when it gets long
