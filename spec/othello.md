# Othello (Reversi) — Complete Game Specification

## 1. Game Overview

Othello (also marketed as Reversi) is a two-player strategy board game played on
an 8x8 board. Players take turns placing discs that are black on one side and white
on the other. When a disc is placed, all opponent discs flanked between the new disc
and existing friendly discs are flipped.

- **Players**: 2 (Human vs AI)
- **Board**: 8x8 grid
- **Pieces**: 64 double-sided discs (black/white)
- **Objective**: Have the most discs of your color when the board is full or no moves remain
- **Starting discs**: 4 (2 black, 2 white in center)

## 2. Technical Foundation

### 2.1 Display Requirements
- 8x8 board typically displayed with a green background
- Discs shown as filled circles (black or white)
- Valid move positions highlighted
- Disc count displayed for each player

### 2.2 Board Layout (ASCII — Starting Position)

```
     A   B   C   D   E   F   G   H
   +---+---+---+---+---+---+---+---+
 8 |   |   |   |   |   |   |   |   | 8
   +---+---+---+---+---+---+---+---+
 7 |   |   |   |   |   |   |   |   | 7
   +---+---+---+---+---+---+---+---+
 6 |   |   |   |   |   |   |   |   | 6
   +---+---+---+---+---+---+---+---+
 5 |   |   |   | ○ | ● |   |   |   | 5
   +---+---+---+---+---+---+---+---+
 4 |   |   |   | ● | ○ |   |   |   | 4
   +---+---+---+---+---+---+---+---+
 3 |   |   |   |   |   |   |   |   | 3
   +---+---+---+---+---+---+---+---+
 2 |   |   |   |   |   |   |   |   | 2
   +---+---+---+---+---+---+---+---+
 1 |   |   |   |   |   |   |   |   | 1
   +---+---+---+---+---+---+---+---+
     A   B   C   D   E   F   G   H

Legend: ● = Black disc   ○ = White disc
```

### 2.3 Initial Configuration

| Position | Color |
|----------|-------|
| D4       | Black |
| E4       | White |
| D5       | White |
| E5       | Black |

Note: Some variants swap D4/E5 with D5/E4. The above is the standard Othello setup.

## 3. Core Rules

### 3.1 Turn Order
- Black always moves first
- Players alternate turns
- If a player has no valid moves, their turn is skipped (opponent plays again)
- If neither player can move, the game ends

### 3.2 Placing a Disc
A valid move must satisfy:
1. The target square is empty
2. The placed disc must flank at least one line of opponent discs between itself
   and another disc of the same color
3. Flanking can occur in any of 8 directions: horizontal (left/right),
   vertical (up/down), diagonal (4 diagonal directions)

### 3.3 Flipping Discs
After placing a disc:
1. Check all 8 directions from the placed disc
2. In each direction, look for a continuous line of opponent discs followed by
   a friendly disc
3. If found, flip all opponent discs in that line to the current player's color
4. Multiple directions can be flipped in a single move

### 3.4 Direction Vectors

| Direction       | Row Delta | Col Delta |
|----------------|-----------|-----------|
| Up             | -1        | 0         |
| Down           | +1        | 0         |
| Left           | 0         | -1        |
| Right          | 0         | +1        |
| Up-Left        | -1        | -1        |
| Up-Right       | -1        | +1        |
| Down-Left      | +1        | -1        |
| Down-Right     | +1        | +1        |

### 3.5 Flanking Example

```
Before Black places at A:
  . . ○ ○ ○ ● . .
        ^     ^
      opponent  friendly

After Black places at A:
  ● ● ● ● ● ● . .
  ^             ^
  placed       existing
  All white discs between are flipped to black
```

### 3.6 Valid Move Detection Algorithm

```
function getValidMoves(board, color):
    validMoves = []
    for each empty square (r, c):
        for each direction (dr, dc):
            if canFlipInDirection(board, r, c, dr, dc, color):
                validMoves.add((r, c))
                break  // no need to check more directions for this square
    return validMoves

function canFlipInDirection(board, r, c, dr, dc, color):
    opponent = oppositeColor(color)
    nr, nc = r + dr, c + dc
    foundOpponent = false

    while inBounds(nr, nc):
        if board[nr][nc] == opponent:
            foundOpponent = true
        elif board[nr][nc] == color:
            return foundOpponent  // true only if we passed opponent discs
        else:
            return false  // empty square breaks the line
        nr += dr
        nc += dc

    return false  // reached edge without finding friendly disc
```

## 4. Game End and Scoring

### 4.1 Game End Conditions
The game ends when:
1. The board is completely filled (64 discs)
2. Neither player has a valid move
3. A player resigns

### 4.2 Scoring
- Count all discs of each color on the board
- The player with more discs wins
- If equal, the game is a draw (rare)

### 4.3 Score Display

```
+------------------+
| BLACK: ●  34     |
| WHITE: ○  30     |
| EMPTY:     0     |
+------------------+
| Winner: BLACK    |
+------------------+
```

## 5. Strategic Concepts

### 5.1 Square Values (Positional Weight Map)

```
     A    B    C    D    E    F    G    H
  +----+----+----+----+----+----+----+----+
8 |+100| -20|+10 | +5 | +5 |+10 | -20|+100|
  +----+----+----+----+----+----+----+----+
7 | -20| -50| -2 | -2 | -2 | -2 | -50| -20|
  +----+----+----+----+----+----+----+----+
6 | +10|  -2| +1 | +1 | +1 | +1 |  -2| +10|
  +----+----+----+----+----+----+----+----+
5 |  +5|  -2| +1 |  0 |  0 | +1 |  -2|  +5|
  +----+----+----+----+----+----+----+----+
4 |  +5|  -2| +1 |  0 |  0 | +1 |  -2|  +5|
  +----+----+----+----+----+----+----+----+
3 | +10|  -2| +1 | +1 | +1 | +1 |  -2| +10|
  +----+----+----+----+----+----+----+----+
2 | -20| -50| -2 | -2 | -2 | -2 | -50| -20|
  +----+----+----+----+----+----+----+----+
1 |+100| -20|+10 | +5 | +5 |+10 | -20|+100|
  +----+----+----+----+----+----+----+----+
     A    B    C    D    E    F    G    H
```

**Key positions:**
- **Corners (+100)**: Most valuable — cannot be flipped once taken
- **C-squares (-20)**: Adjacent to corners — dangerous if corner is empty
- **X-squares (-50)**: Diagonal to corners — very dangerous if corner is empty
- **Edges (+10)**: Stable once anchored to a corner
- **Center (0 to +1)**: Neutral in positional value

### 5.2 Mobility

**Mobility** = number of valid moves available to a player.
- High mobility is generally good (more options)
- Forcing opponent into low mobility is a key strategy
- Having 0 mobility means passing (very bad)

### 5.3 Stability

A **stable disc** cannot be flipped for the rest of the game:
- Corner discs are always stable
- Discs adjacent to stable discs along edges become stable
- A full edge is entirely stable

### 5.4 Parity

In the endgame, the player who fills the last empty square in a region gains an
advantage. This is related to the parity (odd/even) of empty squares.

## 6. AI Opponent

### 6.1 Difficulty Levels

| Level      | Depth  | Evaluation                    | Features                    |
|------------|--------|-------------------------------|-----------------------------|
| Beginner   | 1      | Disc count only               | 30% random moves            |
| Easy       | 2-3    | Positional weights            | Basic corner awareness      |
| Medium     | 4-5    | Positional + mobility         | Alpha-beta pruning          |
| Hard       | 6-7    | Full evaluation               | Move ordering + endgame     |
| Expert     | 8-12   | Full eval + endgame solver    | Perfect endgame (last 12)   |

### 6.2 Evaluation Function

```
function evaluate(board, color):
    score = 0

    // Phase detection
    discCount = countDiscs(board)
    if discCount < 20:
        phase = OPENING
    elif discCount < 50:
        phase = MIDGAME
    else:
        phase = ENDGAME

    // 1. Disc difference (important in endgame)
    myDiscs = count(board, color)
    oppDiscs = count(board, opposite(color))
    if phase == ENDGAME:
        score += (myDiscs - oppDiscs) * 10

    // 2. Positional value
    for each disc on board:
        if disc.color == color:
            score += POSITION_WEIGHTS[disc.row][disc.col]
        else:
            score -= POSITION_WEIGHTS[disc.row][disc.col]

    // 3. Mobility
    myMobility = countValidMoves(board, color)
    oppMobility = countValidMoves(board, opposite(color))
    if phase != ENDGAME:
        score += (myMobility - oppMobility) * 5

    // 4. Corner occupancy
    myCorners = countCorners(board, color)
    oppCorners = countCorners(board, opposite(color))
    score += (myCorners - oppCorners) * 25

    // 5. Stability
    myStable = countStableDiscs(board, color)
    oppStable = countStableDiscs(board, opposite(color))
    score += (myStable - oppStable) * 15

    // 6. Frontier (discs adjacent to empty squares — fewer is better)
    myFrontier = countFrontierDiscs(board, color)
    oppFrontier = countFrontierDiscs(board, opposite(color))
    score -= (myFrontier - oppFrontier) * 3

    return score
```

### 6.3 Endgame Perfect Play

When fewer than 12 empty squares remain, the AI at Expert level should solve
the game perfectly using exhaustive search:

```
function solveEndgame(board, color):
    if no valid moves for either player:
        return discCount(color) - discCount(opposite(color))

    bestScore = -infinity
    for each valid move:
        make_move(move)
        score = -solveEndgame(board, opposite(color))
        undo_move(move)
        bestScore = max(bestScore, score)

    return bestScore
```

### 6.4 Move Ordering

For alpha-beta efficiency:
1. Corner moves first
2. Edge moves (not C-squares or X-squares)
3. Moves that maximize disc flips
4. Interior moves
5. C-squares and X-squares last

### 6.5 Opening Book

First few moves of common openings:

| Opening Name | Sequence (Black first)         |
|-------------|--------------------------------|
| Diagonal    | D3, C5                         |
| Perpendicular | D3, C3                       |
| Parallel    | D3, E3                         |
| Tiger       | D3, C5, D6, C3                 |
| Rose        | D3, C5, F6, F5                 |
| Rabbit      | D3, C3, C4, B3                 |

## 7. Game State

| State Variable         | Type          | Description                          |
|------------------------|---------------|--------------------------------------|
| board[8][8]            | enum          | EMPTY, BLACK, WHITE                  |
| currentPlayer          | enum          | BLACK or WHITE                       |
| blackCount             | integer       | Number of black discs                |
| whiteCount             | integer       | Number of white discs                |
| validMoves             | list          | Current player's valid moves         |
| moveHistory            | list          | All moves with flipped discs         |
| consecutivePasses      | integer       | 0, 1, or 2 (2 = game over)          |
| gamePhase              | enum          | OPENING, MIDGAME, ENDGAME           |

## 8. User Interface

### 8.1 Main Game Screen

```
+------------------------------------------------------------------+
|  OTHELLO  vs  AI (Medium)                                        |
+------------------------------------------------------------------+
|                                                                  |
|  ● Black: 32          ○ White: 30          Empty: 2              |
|                                                                  |
|       A   B   C   D   E   F   G   H                             |
|     +---+---+---+---+---+---+---+---+                            |
|  8  | ● | ● | ● | ● | ● | ● | ○ | ○ |  8                       |
|     +---+---+---+---+---+---+---+---+                            |
|  7  | ● | ● | ● | ● | ○ | ○ | ○ | ○ |  7                       |
|     +---+---+---+---+---+---+---+---+                            |
|  6  | ● | ● | ● | ● | ● | ○ | ○ | ○ |  6                       |
|     +---+---+---+---+---+---+---+---+                            |
|  5  | ● | ● | ● | ● | ● | ○ | ○ | ○ |  5                       |
|     +---+---+---+---+---+---+---+---+                            |
|  4  | ● | ● | ● | ● | ● | ○ | ○ |   |  4                       |
|     +---+---+---+---+---+---+---+---+                            |
|  3  | ● | ● | ○ | ● | ● | ○ | ○ | ○ |  3                       |
|     +---+---+---+---+---+---+---+---+                            |
|  2  | ● | ○ | ○ | ○ | ● | ○ | ○ | ○ |  2                       |
|     +---+---+---+---+---+---+---+---+                            |
|  1  | ○ | ○ | ○ | ○ | ○ | ○ |   | ○ |  1                       |
|     +---+---+---+---+---+---+---+---+                            |
|       A   B   C   D   E   F   G   H                             |
|                                                                  |
|  Your turn (Black) — 2 valid moves: H4, G1                      |
|  Valid moves shown as: ◊                                         |
|                                                                  |
+------------------------------------------------------------------+
|  [New Game] [Undo] [Hint] [Settings]                             |
+------------------------------------------------------------------+
```

### 8.2 Valid Move Indicators
- Empty squares where the current player can legally place a disc
- Shown as small dots, crosses, or semi-transparent discs
- On hover, show which discs would be flipped (highlight them)

### 8.3 Flip Animation
When discs are flipped:
1. Brief pause (200ms)
2. Discs rotate/flip to new color in sequence (50ms each)
3. Total flip animation: 200ms + N * 50ms where N is number of flipped discs
4. Or: all flipped simultaneously with a color transition (300ms)

### 8.4 New Game Dialog

```
+---------------------------+
|     NEW OTHELLO GAME      |
|                           |
|  Play as: [Black] [White] |
|                           |
|  AI Difficulty:           |
|  ( ) Beginner             |
|  ( ) Easy                 |
|  (•) Medium               |
|  ( ) Hard                 |
|  ( ) Expert               |
|                           |
|  Show valid moves: [Yes]  |
|  Show flip preview: [Yes] |
|                           |
|  [Start Game]             |
+---------------------------+
```

### 8.5 Game Over Screen

```
+-----------------------------+
|        GAME OVER            |
|                             |
|  ● Black: 38               |
|  ○ White: 26               |
|                             |
|  Winner: BLACK!             |
|  Margin: +12 discs          |
|                             |
|  [New Game] [Review Game]   |
+-----------------------------+
```

## 9. Game Flow

### 9.1 Turn Sequence
1. Calculate valid moves for current player
2. If no valid moves:
   a. Increment consecutivePasses
   b. If consecutivePasses == 2: end game
   c. Else: display "No valid moves — passing" and switch player
3. If valid moves exist:
   a. Reset consecutivePasses to 0
   b. If human: wait for click on valid square
   c. If AI: compute best move
   d. Place disc, flip opponent discs
   e. Update counts
4. Switch current player
5. Check for full board (game end)

### 9.2 Undo System
- Undo restores the board to the state before the last human move
- Also undoes the AI's response
- Store: board state, disc counts, current player
- Unlimited undos on Beginner/Easy
- Limited on higher difficulties

## 10. Data Structures

### 10.1 Board Representation
```
// Simple 2D array
board[8][8] = EMPTY | BLACK | WHITE

// Bitboard (efficient for move generation)
blackBoard = 64-bit integer  // bit set = black disc present
whiteBoard = 64-bit integer  // bit set = white disc present
// Valid moves computed via bitwise operations
```

### 10.2 Move Representation
```
Move {
    position: { row, col }
    color: BLACK or WHITE
    flippedDiscs: [{ row, col }]  // list of discs that were flipped
}
```

## 11. Testing Scenarios

1. **Starting position**: 4 initial discs correctly placed
2. **First move**: Black has exactly 4 valid moves from starting position (C4, D3, E6, F5)
3. **Multi-direction flip**: Single move flips discs in multiple directions
4. **Pass detection**: Player with no valid moves must pass
5. **Double pass**: Game ends when both players pass consecutively
6. **Full board**: Game ends when all 64 squares filled
7. **Corner capture**: Corner disc is never flipped
8. **Edge stability**: Full edge is stable
9. **Endgame scoring**: Correct disc count at game end
10. **Maximum flip**: A single move can flip up to 18 discs (verify this works)

## 12. Performance Requirements

| Metric                     | Target             |
|----------------------------|---------------------|
| Valid move calculation      | < 1ms              |
| Disc flip processing       | < 1ms              |
| AI move (Easy)             | < 200ms            |
| AI move (Medium)           | < 1 second         |
| AI move (Hard)             | < 3 seconds        |
| AI move (Expert)           | < 10 seconds       |
| Flip animation             | 60 FPS             |
| Board render               | < 16ms             |

## 13. Sound Effects

| Event              | Sound                          |
|--------------------|--------------------------------|
| Place disc         | Crisp "click"                  |
| Flip disc(s)       | Soft "whoosh" or rapid clicks  |
| Pass turn          | Subtle notification tone       |
| Win                | Victory fanfare                |
| Lose               | Defeat sound                   |
| Invalid move       | Error buzz                     |
| Corner captured    | Special satisfying sound       |

## 14. Keyboard Shortcuts

| Key         | Action                    |
|-------------|---------------------------|
| Ctrl+Z      | Undo last move            |
| Ctrl+N      | New game                  |
| H           | Show hint                 |
| V           | Toggle valid move display |
| Escape      | Cancel selection          |
| 1-5         | Quick difficulty change   |

## 15. Accessibility

- High contrast disc colors (not just black/white — use patterns)
- Large disc option
- Text labels showing disc color
- Keyboard grid navigation
- Screen reader: announce moves, flips, and score changes
- Color-blind mode: use symbols (X and O) in addition to colors
