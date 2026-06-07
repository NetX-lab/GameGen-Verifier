# Go (Weiqi) — Complete Game Specification

## 1. Game Overview

Go is an abstract strategy board game originating from China over 2,500 years ago.
Two players alternately place black and white stones on vacant intersections of a
grid. The objective is to surround more territory than the opponent.

- **Players**: 2 (Human vs AI)
- **Board sizes**: 9x9, 13x13, and 19x19
- **Pieces**: Black and white stones (unlimited supply)
- **Objective**: Control more territory (empty intersections) than the opponent
- **Ruleset**: Chinese rules (with Japanese rules option)

## 2. Technical Foundation

### 2.1 Display Requirements
- Grid rendered as intersecting horizontal and vertical lines
- Stones placed on intersections (not in squares)
- Star points (hoshi) marked as small dots on specific intersections
- Coordinate labels on edges (A-T for columns, 1-19 for rows, skipping I)

### 2.2 Board Sizes and Star Points

**9x9 Board Star Points:**
| Point   | Coordinates |
|---------|-------------|
| Center  | (5,5)       |
| Corners | (3,3), (3,7), (7,3), (7,7) |

**13x13 Board Star Points:**
| Point   | Coordinates |
|---------|-------------|
| Center  | (7,7)       |
| Corners | (4,4), (4,10), (10,4), (10,10) |
| Edges   | (4,7), (7,4), (7,10), (10,7) |

**19x19 Board Star Points:**
| Point   | Coordinates  |
|---------|-------------|
| Center  | (10,10)     |
| Corners | (4,4), (4,16), (16,4), (16,16) |
| Edges   | (4,10), (10,4), (10,16), (16,10) |
| Mid     | (10,10) (tengen) |

### 2.3 Board Layout (9x9 ASCII)

```
     A   B   C   D   E   F   G   H   J
   +---+---+---+---+---+---+---+---+---+
 9 |   |   |   |   |   |   |   |   |   | 9
   +---+---+---+---+---+---+---+---+---+
 8 |   |   |   |   |   |   |   |   |   | 8
   +---+---+---+---+---+---+---+---+---+
 7 |   |   | * |   |   |   | * |   |   | 7
   +---+---+---+---+---+---+---+---+---+
 6 |   |   |   |   |   |   |   |   |   | 6
   +---+---+---+---+---+---+---+---+---+
 5 |   |   |   |   | * |   |   |   |   | 5
   +---+---+---+---+---+---+---+---+---+
 4 |   |   |   |   |   |   |   |   |   | 4
   +---+---+---+---+---+---+---+---+---+
 3 |   |   | * |   |   |   | * |   |   | 3
   +---+---+---+---+---+---+---+---+---+
 2 |   |   |   |   |   |   |   |   |   | 2
   +---+---+---+---+---+---+---+---+---+
 1 |   |   |   |   |   |   |   |   |   | 1
   +---+---+---+---+---+---+---+---+---+
     A   B   C   D   E   F   G   H   J

Legend: * = star point (hoshi)
        ● = black stone
        ○ = white stone
```

### 2.4 Board Layout (19x19 ASCII — corner only)

```
     A   B   C   D   E   F   G   ...
   +---+---+---+---+---+---+---+---
19 |   |   |   |   |   |   |   | ...  19
   +---+---+---+---+---+---+---+---
18 |   |   |   |   |   |   |   | ...  18
   +---+---+---+---+---+---+---+---
17 |   |   |   |   |   |   |   | ...  17
   +---+---+---+---+---+---+---+---
16 |   |   |   | * |   |   |   | ...  16
   +---+---+---+---+---+---+---+---
15 |   |   |   |   |   |   |   | ...  15
   ...
```

## 3. Core Concepts

### 3.1 Intersections and Adjacency

- Stones are placed on intersections of grid lines
- Each intersection has up to 4 orthogonally adjacent intersections (not diagonal)
- Corner intersections have 2 neighbors
- Edge intersections have 3 neighbors
- Interior intersections have 4 neighbors

### 3.2 Liberties

A **liberty** is an empty intersection orthogonally adjacent to a stone or group of stones.

| Position     | Maximum Liberties |
|-------------|-------------------|
| Corner       | 2                 |
| Edge         | 3                 |
| Interior     | 4                 |

A group's liberties are the union of all empty intersections adjacent to any stone
in the group.

### 3.3 Groups (Chains/Strings)

A **group** is a set of one or more same-colored stones connected orthogonally.
- All stones in a group share liberties
- If a group's liberty count reaches 0, all stones in the group are captured

### 3.4 Territory

**Territory** consists of empty intersections completely surrounded by one color's
stones (no path to the edge of the board through empty intersections without
crossing that color's stones).

### 3.5 Eyes

An **eye** is a single empty intersection completely surrounded by stones of one
color. A group with two separate eyes cannot be captured (it is "alive").

## 4. Rules of Play

### 4.1 Basic Rules

1. Black plays first
2. Players alternate placing one stone on an empty intersection
3. A player may pass instead of placing a stone
4. Once placed, stones do not move (they may only be captured and removed)
5. The game ends when both players pass consecutively

### 4.2 Capture Rule

After a stone is placed:
1. Check if any opponent groups have 0 liberties — if so, remove them (captured)
2. Then check if any friendly groups have 0 liberties — if so, the move is illegal
   (suicide rule), UNLESS the placement first captures opponent stones

### 4.3 Ko Rule

A player may not make a move that returns the board to the exact position of the
previous turn. This prevents infinite loops of capture-recapture.

**Superko** (optional, used in Chinese rules): No board position may be repeated
during the entire game with the same player to move.

### 4.4 Suicide Rule

Under Chinese rules: Suicide (placing a stone that immediately has 0 liberties
without capturing any opponent stones) is illegal.

Under some rulesets: Suicide is legal but the placed stones are immediately removed
as captures for the opponent.

**Default implementation**: Suicide is illegal.

### 4.5 Passing

- A player may pass on any turn
- When both players pass consecutively, the game moves to scoring
- A pass does not count as a move for ko purposes

## 5. Scoring

### 5.1 Chinese Scoring (Area Scoring)

```
Score = Stones on board + Territory (empty intersections surrounded)
```

- Count all friendly stones on the board
- Count all empty intersections surrounded by friendly stones
- The player with the higher score wins
- Komi is added to White's score to compensate for Black going first

### 5.2 Japanese Scoring (Territory Scoring)

```
Score = Territory + Captures (prisoners)
```

- Count empty intersections surrounded by friendly stones (territory)
- Add the number of opponent stones captured during the game
- Komi is added to White's score

### 5.3 Komi Values

| Board Size | Standard Komi |
|-----------|---------------|
| 9x9       | 5.5 or 6.5    |
| 13x13     | 6.5            |
| 19x19     | 6.5 (Chinese) or 6.5 (Japanese) |

The 0.5 ensures no ties (draws).

### 5.4 Dead Stone Removal

After both players pass:
1. Players agree on which stones are "dead" (stones that would inevitably be captured)
2. Dead stones are removed and counted as captures
3. If players disagree, play resumes to resolve the dispute

**AI Implementation**: The AI should automatically identify dead stones using
life-and-death analysis.

## 6. Game State Tracking

| State Variable         | Type              | Description                          |
|------------------------|-------------------|--------------------------------------|
| board[N][N]            | enum              | EMPTY, BLACK, WHITE                  |
| currentPlayer          | enum              | BLACK or WHITE                       |
| koPoint                | coord/null        | Intersection forbidden by ko rule    |
| blackCaptures          | integer           | Stones captured by Black             |
| whiteCaptures          | integer           | Stones captured by White             |
| moveHistory            | list              | All moves (including passes)         |
| positionHistory        | list              | All board positions (for superko)    |
| consecutivePasses      | integer           | 0, 1, or 2                          |
| moveNumber             | integer           | Current move number                  |
| blackTerritory         | set of coords     | Calculated during scoring            |
| whiteTerritory         | set of coords     | Calculated during scoring            |

## 7. AI Opponent

### 7.1 Difficulty Levels

| Level      | Algorithm          | Board Sizes   | Approximate Rank    |
|------------|--------------------|---------------|---------------------|
| Beginner   | Random + patterns  | 9x9 only      | ~25 kyu             |
| Easy       | Basic MCTS (1K)   | 9x9, 13x13   | ~15 kyu             |
| Medium     | MCTS (10K sims)   | All           | ~5 kyu              |
| Hard       | MCTS (50K sims)   | All           | ~1 dan              |
| Expert     | MCTS + neural net  | All           | ~5 dan              |

(MCTS = Monte Carlo Tree Search, K = thousand simulations)

### 7.2 Monte Carlo Tree Search (MCTS)

The primary AI algorithm for Go:

```
function MCTS(rootState, numSimulations):
    root = Node(rootState)

    for i in 1..numSimulations:
        node = root
        state = rootState.copy()

        // Selection: traverse tree using UCB1
        while node is fully expanded and not terminal:
            node = bestChild(node, explorationConstant=1.414)
            state.applyMove(node.move)

        // Expansion: add a new child node
        if node is not terminal:
            move = randomUntriedMove(node)
            state.applyMove(move)
            node = node.addChild(move, state)

        // Simulation (Rollout): play random moves to end
        while state is not terminal:
            move = randomLegalMove(state)
            state.applyMove(move)

        // Backpropagation: update statistics
        result = state.getResult()
        while node is not null:
            node.visits += 1
            node.wins += result
            node = node.parent

    return mostVisitedChild(root).move
```

### 7.3 UCB1 Formula

```
UCB1(node) = wins/visits + C * sqrt(ln(parent.visits) / visits)
```

Where C is the exploration constant (typically sqrt(2) or 1.414).

### 7.4 Pattern-Based Evaluation

Common patterns the AI should recognize:

**Life and Death Patterns:**
- Two eyes = alive (unconditionally)
- One eye = vulnerable
- No eyes = dead (if surrounded)
- Seki = mutual life (both groups alive with shared liberties)

**Tactical Patterns:**
- Ladder (shicho): Sequential atari that captures a group
- Net (geta): Surrounding a group with a loose net
- Snapback: Allowing capture then recapturing
- Ko threats: Moves that threaten enough to force ko response

**Strategic Patterns:**
- Influence vs Territory
- Thickness and wall building
- Corner, side, center priorities
- Invasion and reduction timing

### 7.5 Opening Principles (Fuseki)

For 9x9:
1. Play near the center first (tengen or near star points)
2. Approach opponent's stones
3. Secure corner territory

For 19x19:
1. Occupy empty corners first (3-4, 4-4, 3-3 points)
2. Approach or enclose opponent's corners
3. Extend along sides
4. Fight for center influence last

### 7.6 AI Behavior Per Difficulty

**Beginner (9x9):**
- Plays legal random moves with basic pattern filters
- Avoids filling own eyes
- Prefers moves near existing stones
- Responds to immediate atari
- Does not plan ahead

**Easy:**
- MCTS with 1,000 simulations
- Knows basic life-and-death patterns
- Captures groups in atari
- Avoids obvious self-atari

**Medium:**
- MCTS with 10,000 simulations
- Evaluates territory during rollouts
- Applies joseki (corner patterns) knowledge
- Balances territory and influence

**Hard:**
- MCTS with 50,000 simulations
- Strong tactical reading (ladders, nets)
- Good positional judgment
- Effective invasion timing

**Expert:**
- MCTS with neural network policy/value heads (if feasible)
- Or MCTS with 100,000+ simulations
- Near-professional level play on 9x9
- Strong amateur level on 19x19

## 8. User Interface Layout

### 8.1 Main Game Screen (9x9)

```
+------------------------------------------------------------------+
|  GO (9x9)  vs  AI (Medium)   Black: ● 14    White: ○ 12         |
+------------------------------------------------------------------+
|                                                                  |
|  Captures — Black: 3    White: 2    Komi: 6.5                    |
|                                                                  |
|       A   B   C   D   E   F   G   H   J                         |
|     +---+---+---+---+---+---+---+---+---+                        |
|  9  |   |   |   | ● | ○ |   |   |   |   | 9                     |
|     +---+---+---+---+---+---+---+---+---+                        |
|  8  |   |   | ● | ● | ○ | ○ |   |   |   | 8                     |
|     +---+---+---+---+---+---+---+---+---+                        |
|  7  |   |   | ● | ○ | ○ |   | * |   |   | 7                     |
|     +---+---+---+---+---+---+---+---+---+                        |
|  6  |   | ● |   | ● | ○ |   |   |   |   | 6                     |
|     +---+---+---+---+---+---+---+---+---+                        |
|  5  |   |   |   |   | * |   |   |   |   | 5                     |
|     +---+---+---+---+---+---+---+---+---+                        |
|  4  |   |   |   |   |   |   |   | ○ |   | 4                     |
|     +---+---+---+---+---+---+---+---+---+                        |
|  3  |   |   | * |   |   |   | * |   |   | 3                     |
|     +---+---+---+---+---+---+---+---+---+                        |
|  2  |   |   |   |   |   | ○ |   |   |   | 2                     |
|     +---+---+---+---+---+---+---+---+---+                        |
|  1  |   |   |   |   |   |   |   |   |   | 1                     |
|     +---+---+---+---+---+---+---+---+---+                        |
|       A   B   C   D   E   F   G   H   J                         |
|                                                                  |
|  Move: 26   Current: ● Black's turn                              |
|  Last move: ○ White D9                                           |
|                                                                  |
+------------------------------------------------------------------+
|  [Pass] [Resign] [Undo] [Score Estimate] [Settings]              |
+------------------------------------------------------------------+
```

### 8.2 Score Estimation Display

```
+------------------------------------------------------------------+
|  TERRITORY ESTIMATE                                              |
|                                                                  |
|       A   B   C   D   E   F   G   H   J                         |
|     +---+---+---+---+---+---+---+---+---+                        |
|  9  | ▓ | ▓ | ▒ | ● | ○ | ░ | ░ | ░ | ░ | 9                     |
|     +---+---+---+---+---+---+---+---+---+                        |
|  8  | ▓ | ▓ | ● | ● | ○ | ○ | ░ | ░ | ░ | 8                     |
|     ...                                                          |
|                                                                  |
|  Legend: ▓ = Black territory  ░ = White territory                |
|          ▒ = Neutral/Contested                                   |
|                                                                  |
|  Black: 15 (territory) + 14 (stones) = 29                       |
|  White: 18 (territory) + 12 (stones) + 6.5 (komi) = 36.5       |
|                                                                  |
|  Estimate: White leads by 7.5 points                             |
+------------------------------------------------------------------+
```

### 8.3 Interaction Model

1. Click an intersection to place a stone
2. Invalid moves are rejected with explanation:
   - "Occupied intersection"
   - "Suicide — this move would capture your own group"
   - "Ko — cannot retake immediately"
3. Ghost stone shown on hover (semi-transparent)
4. Last move marked with a small dot or square on the stone

### 8.4 Dead Stone Marking (End of Game)

```
+------------------------------------------------------------------+
|  DEAD STONE REMOVAL                                              |
|  Click stones to mark as dead. Click again to unmark.            |
|                                                                  |
|  (Board displayed with dead stones marked as X)                  |
|                                                                  |
|  [Accept] [Resume Play] [AI Suggest Dead Stones]                 |
+------------------------------------------------------------------+
```

## 9. Game Flow

### 9.1 New Game Setup

```
+---------------------------+
|     NEW GO GAME           |
|                           |
|  Board Size:              |
|  ( ) 9x9 (beginner)      |
|  ( ) 13x13 (intermediate)|
|  (•) 19x19 (standard)    |
|                           |
|  Play as: [Black] [White] |
|                           |
|  Handicap Stones:         |
|  [0] (no handicap)        |
|  Available: 0-9           |
|                           |
|  Komi: [6.5]              |
|                           |
|  AI Difficulty:           |
|  ( ) Beginner             |
|  (•) Medium               |
|  ( ) Hard                 |
|  ( ) Expert               |
|                           |
|  Ruleset:                 |
|  (•) Chinese              |
|  ( ) Japanese             |
|                           |
|  [Start Game]             |
+---------------------------+
```

### 9.2 Handicap Stones

Fixed handicap placement positions (19x19):

| Handicap | Positions                                                    |
|----------|--------------------------------------------------------------|
| 2        | D4, Q16                                                      |
| 3        | D4, Q16, Q4                                                  |
| 4        | D4, Q16, Q4, D16                                             |
| 5        | D4, Q16, Q4, D16, K10                                        |
| 6        | D4, Q16, Q4, D16, D10, Q10                                   |
| 7        | D4, Q16, Q4, D16, D10, Q10, K10                              |
| 8        | D4, Q16, Q4, D16, D10, Q10, K4, K16                          |
| 9        | D4, Q16, Q4, D16, D10, Q10, K4, K16, K10                     |

When handicap stones are used, komi is typically set to 0.5 (to prevent ties).

### 9.3 Turn Sequence

1. Display current board state
2. Active player's turn:
   a. Player places stone or passes
   b. Check for captures (remove dead opponent groups)
   c. Validate move (no suicide, no ko violation)
   d. Update board and captures
3. Check for consecutive passes (game end)
4. Switch active player
5. Record move

### 9.4 End Game Sequence

1. Both players pass consecutively
2. Dead stone removal phase
3. Territory counting
4. Apply komi
5. Display final score and winner

## 10. SGF File Format Support

Games should be savable/loadable in SGF (Smart Game Format):

```
(;GM[1]FF[4]SZ[9]KM[6.5]
PB[Human]PW[AI (Medium)]
;B[ee];W[gc];B[cg];W[gg];B[ce])
```

**SGF properties:**
- GM[1]: Game type (1 = Go)
- FF[4]: File format version
- SZ[9]: Board size
- KM[6.5]: Komi
- PB/PW: Player names
- B[xy]/W[xy]: Black/White move at column x, row y (a=1)

## 11. Group Management Algorithm

### 11.1 Finding Groups (Flood Fill)

```
function findGroup(board, x, y):
    color = board[x][y]
    if color == EMPTY: return null

    group = new Set()
    liberties = new Set()
    stack = [(x, y)]

    while stack not empty:
        cx, cy = stack.pop()
        if (cx, cy) in group: continue
        if board[cx][cy] != color: continue

        group.add((cx, cy))

        for each neighbor (nx, ny) of (cx, cy):
            if board[nx][ny] == EMPTY:
                liberties.add((nx, ny))
            elif board[nx][ny] == color and (nx, ny) not in group:
                stack.push((nx, ny))

    return { stones: group, liberties: liberties, color: color }
```

### 11.2 Capture Detection

```
function processCaptures(board, lastMove):
    capturedStones = []
    opponentColor = opposite(lastMove.color)

    for each neighbor of lastMove.position:
        if board[neighbor] == opponentColor:
            group = findGroup(board, neighbor)
            if group.liberties.size == 0:
                capturedStones.extend(group.stones)
                removeStones(board, group.stones)

    return capturedStones
```

## 12. Territory Scoring Algorithm

```
function scoreTerritory(board):
    visited = new Set()
    blackTerritory = 0
    whiteTerritory = 0

    for each intersection (x, y):
        if (x, y) in visited or board[x][y] != EMPTY:
            continue

        region = new Set()
        borders = new Set()
        floodFillEmpty(board, x, y, region, borders, visited)

        if borders == {BLACK}:
            blackTerritory += region.size
        elif borders == {WHITE}:
            whiteTerritory += region.size
        // else: neutral (borders both colors)

    return { black: blackTerritory, white: whiteTerritory }
```

## 13. Performance Requirements

| Metric                     | 9x9          | 19x19          |
|----------------------------|-------------- |----------------|
| Move validation            | < 1ms         | < 5ms          |
| Capture processing         | < 5ms         | < 20ms         |
| AI move (Easy)             | < 1 second    | < 3 seconds    |
| AI move (Medium)           | < 3 seconds   | < 10 seconds   |
| AI move (Hard)             | < 10 seconds  | < 30 seconds   |
| Board render               | < 16ms        | < 16ms         |
| Territory estimation       | < 100ms       | < 500ms        |

## 14. Sound Effects

| Event              | Sound                          |
|--------------------|---------------------------------|
| Stone placement    | Crisp "clack" (like stone on wood) |
| Capture            | Soft rattling (stones removed)  |
| Pass               | Subtle chime                    |
| Game end           | Gong or bell                    |
| Invalid move       | Soft error tone                 |
| Ko violation       | Distinctive warning tone        |

## 15. Settings

| Setting              | Options                          | Default    |
|----------------------|----------------------------------|------------|
| Board size           | 9x9, 13x13, 19x19              | 9x9        |
| Board theme          | Wood, Dark, Paper, Minimalist   | Wood       |
| Stone style          | Flat, 3D, Shell/Slate           | Flat       |
| Show coordinates     | On/Off                          | On         |
| Show move numbers    | None, Last, All                 | Last       |
| Show territory est.  | On/Off                          | Off        |
| Sound effects        | On/Off                          | On         |
| Ruleset              | Chinese, Japanese               | Chinese    |
| Komi                 | Adjustable                      | 6.5        |

## 16. Testing Scenarios

1. **Basic capture**: Surround a single stone and capture it
2. **Group capture**: Surround a group of connected stones
3. **Ko detection**: Verify ko rule prevents immediate recapture
4. **Suicide prevention**: Verify suicide moves are rejected
5. **Snap-back**: Legal self-atari that captures opponent group first
6. **Seki detection**: Mutual life situation scored correctly
7. **Handicap placement**: Correct positions for 2-9 handicap stones
8. **Scoring**: Chinese and Japanese scoring produce correct results
9. **Dead stone identification**: AI correctly identifies dead groups
10. **Pass and game end**: Two consecutive passes end the game
11. **Large group liberty counting**: Efficient for groups with many stones
12. **Edge and corner captures**: Correct behavior at board boundaries
13. **Superko**: If enabled, catches long-cycle repetitions

## 17. Educational Features (Optional)

- **Tutorial mode**: Step-by-step introduction to rules
- **Life-and-death problems**: Tsumego puzzles
- **Move suggestions**: Show AI's top 3 candidate moves with evaluation
- **Post-game analysis**: Review with AI commentary on key moves
- **Liberty counter**: Display liberty count for any group on hover
- **Influence map**: Visual overlay showing territorial influence

## 18. Accessibility

- High contrast stone colors
- Coordinate readout on hover
- Keyboard navigation: arrow keys to move cursor, Enter to place stone
- Screen reader: announce stone placement and captures
- Zoom capability for 19x19 board on small screens
- Adjustable grid line thickness
