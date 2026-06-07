# Tic-Tac-Toe — Complete Game Specification

## 1. Game Overview

Tic-Tac-Toe (also known as Noughts and Crosses or Xs and Os) is a two-player game
played on a 3x3 grid. Players take turns placing their symbol (X or O) in empty
cells. The first player to get three in a row wins.

- **Players**: 2 (Human vs AI)
- **Board**: 3x3 grid
- **Symbols**: X and O
- **Objective**: Get three of your symbols in a horizontal, vertical, or diagonal line
- **Complexity**: Tic-Tac-Toe is a solved game — perfect play always results in a draw

## 2. Technical Foundation

### 2.1 Board Layout (ASCII)

```
         Col 1   Col 2   Col 3
       +-------+-------+-------+
       |       |       |       |
Row 1  |   X   |   O   |   X   |
       |       |       |       |
       +-------+-------+-------+
       |       |       |       |
Row 2  |       |   X   |       |
       |       |       |       |
       +-------+-------+-------+
       |       |       |       |
Row 3  |   O   |       |       |
       |       |       |       |
       +-------+-------+-------+
```

### 2.2 Cell Numbering

**Position-based (row, col):**
```
  (1,1) | (1,2) | (1,3)
  ------+-------+------
  (2,1) | (2,2) | (2,3)
  ------+-------+------
  (3,1) | (3,2) | (3,3)
```

**Numpad-style (alternative input):**
```
    7  |  8  |  9
   ----+-----+----
    4  |  5  |  6
   ----+-----+----
    1  |  2  |  3
```

### 2.3 Grid Dimensions

| Property        | Value  |
|----------------|--------|
| Rows            | 3      |
| Columns         | 3      |
| Total cells     | 9      |
| Max moves       | 9      |
| Winning lines   | 8      |

## 3. Core Rules

### 3.1 Turn Order
- X always goes first
- Players alternate turns
- Each turn: place your symbol in one empty cell

### 3.2 Valid Moves
- Only empty cells are valid targets
- Clicking an occupied cell is rejected
- Once placed, symbols cannot be moved or removed

### 3.3 Win Conditions
A player wins by placing three of their symbols in a line:

**Three Horizontal Lines:**
```
Row 1: (1,1), (1,2), (1,3)
Row 2: (2,1), (2,2), (2,3)
Row 3: (3,1), (3,2), (3,3)
```

**Three Vertical Lines:**
```
Col 1: (1,1), (2,1), (3,1)
Col 2: (1,2), (2,2), (3,2)
Col 3: (1,3), (2,3), (3,3)
```

**Two Diagonal Lines:**
```
Main diagonal:  (1,1), (2,2), (3,3)
Anti-diagonal:  (1,3), (2,2), (3,1)
```

**Total: 8 possible winning lines**

### 3.4 Win Detection Algorithm

```
function checkWin(board, symbol):
    // Check rows
    for row in 1..3:
        if board[row][1] == symbol and board[row][2] == symbol and board[row][3] == symbol:
            return { won: true, line: [(row,1), (row,2), (row,3)] }

    // Check columns
    for col in 1..3:
        if board[1][col] == symbol and board[2][col] == symbol and board[3][col] == symbol:
            return { won: true, line: [(1,col), (2,col), (3,col)] }

    // Check main diagonal
    if board[1][1] == symbol and board[2][2] == symbol and board[3][3] == symbol:
        return { won: true, line: [(1,1), (2,2), (3,3)] }

    // Check anti-diagonal
    if board[1][3] == symbol and board[2][2] == symbol and board[3][1] == symbol:
        return { won: true, line: [(1,3), (2,2), (3,1)] }

    return { won: false }
```

### 3.5 Draw Condition
- All 9 cells are filled and no player has three in a row
- The game is a draw (also called a "cat's game")
- With perfect play, the game always ends in a draw

## 4. Game State

| State Variable         | Type          | Description                          |
|------------------------|---------------|--------------------------------------|
| board[3][3]            | enum          | EMPTY, X, O                         |
| currentPlayer          | enum          | X or O                               |
| moveCount              | integer       | Number of moves made (0-9)           |
| gameOver               | boolean       | Whether the game has ended           |
| winner                 | enum/null     | X, O, or null (draw/ongoing)        |
| winningLine            | list/null     | The 3 cells forming the winning line |
| moveHistory            | list          | All moves in order                   |

## 5. AI Opponent — Multiple Difficulty Levels

### 5.1 Difficulty Overview

| Level        | Strategy                                   | Win Rate vs Perfect |
|-------------|--------------------------------------------|--------------------|
| Beginner     | Pure random move selection                 | ~0% (loses often)  |
| Easy         | Random + block immediate wins              | ~10%               |
| Medium       | Win/Block + center/corner preference       | ~50% (draws often) |
| Hard         | Minimax — near-perfect play                | ~95% (draws mostly)|
| Impossible   | Perfect minimax — never loses              | 100% draws         |

### 5.2 Beginner AI — Random

```
function beginnerMove(board):
    emptyCells = getAllEmptyCells(board)
    return random(emptyCells)
```

- Selects any random empty cell
- No strategy at all
- Loses frequently to any player who knows the rules

### 5.3 Easy AI — Random with Blocking

```
function easyMove(board):
    // 1. Win if possible (70% chance of noticing)
    if random() < 0.7:
        winMove = findWinningMove(board, AI_SYMBOL)
        if winMove: return winMove

    // 2. Block opponent win (60% chance of noticing)
    if random() < 0.6:
        blockMove = findWinningMove(board, HUMAN_SYMBOL)
        if blockMove: return blockMove

    // 3. Random move
    return random(getAllEmptyCells(board))
```

### 5.4 Medium AI — Strategic with Occasional Mistakes

```
function mediumMove(board):
    // 1. Win if possible (always)
    winMove = findWinningMove(board, AI_SYMBOL)
    if winMove: return winMove

    // 2. Block opponent win (always)
    blockMove = findWinningMove(board, HUMAN_SYMBOL)
    if blockMove: return blockMove

    // 3. Take center (90% of the time)
    if board[2][2] == EMPTY and random() < 0.9:
        return (2, 2)

    // 4. Take a corner (80% of the time)
    corners = [(1,1), (1,3), (3,1), (3,3)]
    emptyCorners = filter(corners, cell -> board[cell] == EMPTY)
    if emptyCorners and random() < 0.8:
        return random(emptyCorners)

    // 5. Take a side
    sides = [(1,2), (2,1), (2,3), (3,2)]
    emptySides = filter(sides, cell -> board[cell] == EMPTY)
    if emptySides:
        return random(emptySides)

    // 6. Any empty cell
    return random(getAllEmptyCells(board))
```

### 5.5 Hard AI — Minimax

```
function hardMove(board):
    bestScore = -infinity
    bestMove = null

    for each empty cell (r, c):
        board[r][c] = AI_SYMBOL
        score = minimax(board, 0, false)
        board[r][c] = EMPTY

        if score > bestScore:
            bestScore = score
            bestMove = (r, c)

    return bestMove

function minimax(board, depth, isMaximizing):
    if checkWin(board, AI_SYMBOL):
        return 10 - depth  // AI wins (prefer faster wins)
    if checkWin(board, HUMAN_SYMBOL):
        return depth - 10  // Human wins (prefer slower losses)
    if isBoardFull(board):
        return 0            // Draw

    if isMaximizing:
        bestScore = -infinity
        for each empty cell (r, c):
            board[r][c] = AI_SYMBOL
            score = minimax(board, depth + 1, false)
            board[r][c] = EMPTY
            bestScore = max(bestScore, score)
        return bestScore
    else:
        bestScore = +infinity
        for each empty cell (r, c):
            board[r][c] = HUMAN_SYMBOL
            score = minimax(board, depth + 1, true)
            board[r][c] = EMPTY
            bestScore = min(bestScore, score)
        return bestScore
```

### 5.6 Impossible AI — Perfect Minimax with Alpha-Beta

```
function impossibleMove(board):
    bestScore = -infinity
    bestMove = null

    for each empty cell (r, c):
        board[r][c] = AI_SYMBOL
        score = minimaxAB(board, 0, -infinity, +infinity, false)
        board[r][c] = EMPTY

        if score > bestScore:
            bestScore = score
            bestMove = (r, c)

    return bestMove

function minimaxAB(board, depth, alpha, beta, isMaximizing):
    if checkWin(board, AI_SYMBOL): return 10 - depth
    if checkWin(board, HUMAN_SYMBOL): return depth - 10
    if isBoardFull(board): return 0

    if isMaximizing:
        maxEval = -infinity
        for each empty cell (r, c):
            board[r][c] = AI_SYMBOL
            eval = minimaxAB(board, depth+1, alpha, beta, false)
            board[r][c] = EMPTY
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha: break
        return maxEval
    else:
        minEval = +infinity
        for each empty cell (r, c):
            board[r][c] = HUMAN_SYMBOL
            eval = minimaxAB(board, depth+1, alpha, beta, true)
            board[r][c] = EMPTY
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            if beta <= alpha: break
        return minEval
```

The Impossible AI:
- Never loses — always draws or wins
- Takes winning moves immediately
- Blocks all opponent threats
- Plays optimally from any position

### 5.7 Strategic Knowledge

**Opening move priorities (when AI goes first):**
1. Center (2,2) — best opening move
2. Any corner — second best
3. Sides are weakest opening moves

**Opening response (when AI goes second):**
- If opponent took center: take a corner
- If opponent took a corner: take center
- If opponent took a side: take center

**Fork detection:** A fork creates two threats simultaneously, guaranteeing a win.
```
function findFork(board, symbol):
    for each empty cell (r, c):
        board[r][c] = symbol
        threats = countThreats(board, symbol)  // lines with 2 symbols + 1 empty
        board[r][c] = EMPTY
        if threats >= 2:
            return (r, c)  // this creates a fork
    return null
```

**Cell priority ranking:**

| Position | Type    | Strategic Value |
|----------|---------|----------------|
| (2,2)    | Center  | Highest — part of 4 lines |
| Corners  | Corner  | High — part of 3 lines each |
| Sides    | Edge    | Low — part of 2 lines each |

## 6. User Interface

### 6.1 Main Game Screen

```
+--------------------------------------------------+
|  TIC-TAC-TOE  vs  AI (Medium)                    |
+--------------------------------------------------+
|                                                  |
|  You: X        AI: O        Move: 5              |
|                                                  |
|          +-------+-------+-------+               |
|          |       |       |       |               |
|          |   X   |       |   O   |               |
|          |       |       |       |               |
|          +-------+-------+-------+               |
|          |       |       |       |               |
|          |       |   X   |       |               |
|          |       |       |       |               |
|          +-------+-------+-------+               |
|          |       |       |       |               |
|          |   O   |       |       |               |
|          |       |       |       |               |
|          +-------+-------+-------+               |
|                                                  |
|  Status: Your turn (X)                           |
|                                                  |
+--------------------------------------------------+
|  [New Game]  [Undo]  [Settings]                  |
+--------------------------------------------------+
```

### 6.2 Interaction Model
1. Click an empty cell to place your symbol
2. Symbol appears with a brief drawing animation
3. AI responds after a short delay (200ms - 1s depending on difficulty)
4. Occupied cells show a "no" cursor on hover
5. Empty cells highlight on hover

### 6.3 Win Animation
```
+-------+-------+-------+
|       |       |       |
|  [X]  |  [X]  |  [X]  |  <-- winning line highlighted
|       |       |       |
+-------+-------+-------+
|       |       |       |
|       |   O   |       |
|       |       |       |
+-------+-------+-------+
|       |       |       |
|   O   |       |       |
|       |       |       |
+-------+-------+-------+

A line is drawn through the winning three cells.
Non-winning cells fade slightly.
```

### 6.4 Draw Animation
```
+-------+-------+-------+
|       |       |       |
|   X   |   O   |   X   |
|       |       |       |
+-------+-------+-------+
|       |       |       |
|   O   |   X   |   X   |
|       |       |       |
+-------+-------+-------+
|       |       |       |
|   O   |   X   |   O   |
|       |       |       |
+-------+-------+-------+

All cells pulse once.
"Draw!" text appears.
```

### 6.5 New Game Dialog

```
+---------------------------+
|     TIC-TAC-TOE           |
|                           |
|  Play as: [X] [O]         |
|  (X goes first)           |
|                           |
|  AI Difficulty:           |
|  ( ) Beginner             |
|  ( ) Easy                 |
|  (•) Medium               |
|  ( ) Hard                 |
|  ( ) Impossible           |
|                           |
|  Board Size:              |
|  (•) 3x3 (Classic)       |
|  ( ) 4x4 (Connect 4-TT)  |
|  ( ) 5x5 (Connect 4-TT)  |
|                           |
|  [Start Game]             |
+---------------------------+
```

### 6.6 Game Over Screens

**Win:**
```
+---------------------------+
|      YOU WIN!             |
|                           |
|  X wins in 5 moves        |
|                           |
|  [Play Again] [New Setup] |
+---------------------------+
```

**Lose:**
```
+---------------------------+
|      YOU LOSE!            |
|                           |
|  O wins in 6 moves        |
|  Try a lower difficulty   |
|                           |
|  [Play Again] [New Setup] |
+---------------------------+
```

**Draw:**
```
+---------------------------+
|        DRAW!              |
|                           |
|  The game is a tie        |
|  Well played!             |
|                           |
|  [Play Again] [New Setup] |
+---------------------------+
```

## 7. Game Flow

### 7.1 Turn Sequence
1. Display current board
2. If human's turn:
   a. Wait for cell click
   b. Validate cell is empty
   c. Place symbol with animation
   d. Check for win or draw
3. If AI's turn:
   a. Brief thinking delay (varies by difficulty)
   b. Calculate move based on difficulty algorithm
   c. Place symbol with animation
   d. Check for win or draw
4. If game not over, switch player
5. Update move counter

### 7.2 Thinking Delay by Difficulty

| Difficulty   | Delay (ms) | Purpose                               |
|-------------|------------|---------------------------------------|
| Beginner     | 200-400    | Quick, feels instant                  |
| Easy         | 300-600    | Slight pause                          |
| Medium       | 500-1000   | Noticeable thinking                   |
| Hard         | 700-1200   | Feels like consideration              |
| Impossible   | 300-500    | Quick — AI knows the answer instantly |

## 8. Extended Game Modes (Optional)

### 8.1 4x4 Grid (Connect 4 in a line)

```
+----+----+----+----+
|    |    |    |    |
+----+----+----+----+
|    |    |    |    |
+----+----+----+----+
|    |    |    |    |
+----+----+----+----+
|    |    |    |    |
+----+----+----+----+
```
- Win condition: 4 in a row
- Total cells: 16
- Not a solved game at this level — much more complex

### 8.2 5x5 Grid (Connect 4 in a line)

```
+----+----+----+----+----+
|    |    |    |    |    |
+----+----+----+----+----+
|    |    |    |    |    |
+----+----+----+----+----+
|    |    |    |    |    |
+----+----+----+----+----+
|    |    |    |    |    |
+----+----+----+----+----+
|    |    |    |    |    |
+----+----+----+----+----+
```
- Win condition: 4 in a row (not 5)
- Total cells: 25
- Much deeper game tree

### 8.3 Ultimate Tic-Tac-Toe (Advanced Variant)

A 3x3 grid of 3x3 tic-tac-toe boards:
```
+-------+-------+-------+
| X . O | . . . | . . . |
| . X . | . . . | . . . |
| . . X | . . . | . . . |
+-------+-------+-------+
| . . . | . . . | . . . |
| . . . | . . . | . . . |
| . . . | . . . | . . . |
+-------+-------+-------+
| . . . | . . . | . . . |
| . . . | . . . | . . . |
| . . . | . . . | . . . |
+-------+-------+-------+
```
- Each move sends the opponent to a specific sub-board
- Win a sub-board by getting 3-in-a-row within it
- Win the game by getting 3 sub-boards in a row

## 9. Score Tracking

### 9.1 Session Score

```
+---------------------------+
|  SCOREBOARD               |
|                           |
|  You (X):    IIIII  = 5   |
|  AI (O):     III    = 3   |
|  Draws:      IIII   = 4   |
|                           |
|  Total games: 12          |
+---------------------------+
```

### 9.2 Statistics

| Statistic              | Description                     |
|------------------------|---------------------------------|
| Games played           | Per difficulty level            |
| Wins/Losses/Draws      | Per difficulty                  |
| Win rate               | Percentage per difficulty       |
| Win streak             | Current and best                |
| Average game length    | Moves per game                  |
| First-move advantage   | Win rate as X vs O              |

## 10. Sound Effects

| Event              | Sound                          |
|--------------------|--------------------------------|
| Place X            | Pencil scratch / marker sound  |
| Place O            | Different pitch marker sound   |
| Win                | Victory chime                  |
| Lose               | Defeat tone                    |
| Draw               | Neutral "done" sound           |
| Invalid move       | Soft error                     |
| Hover cell         | Subtle click                   |
| New game           | Reset sound                    |

## 11. Settings

| Setting              | Options                          | Default    |
|----------------------|----------------------------------|------------|
| Player symbol        | X or O                          | X          |
| AI difficulty        | 5 levels                        | Medium     |
| Board size           | 3x3, 4x4, 5x5                  | 3x3        |
| Theme                | Classic, Chalk, Neon, Paper     | Classic    |
| Sound effects        | On/Off                          | On         |
| Show move numbers    | On/Off                          | Off        |
| AI delay             | None, Short, Normal, Long       | Normal     |
| Undo allowed         | On/Off                          | On         |

## 12. Data Structures

### 12.1 Board Representation

```
// Simple 2D array
board[3][3] = EMPTY | X | O

// Alternative: flat array
board[9] = EMPTY | X | O
// Index mapping: index = row * 3 + col

// Alternative: bitmask (very efficient)
xBoard = 9-bit integer  // bit set = X placed
oBoard = 9-bit integer  // bit set = O placed
// Win masks: 0b111000000, 0b000111000, 0b000000111 (rows)
//            0b100100100, 0b010010010, 0b001001001 (columns)
//            0b100010001, 0b001010100 (diagonals)
```

### 12.2 Win Masks (Bitmask Approach)

```
WINNING_MASKS = [
    0b111000000,  // Row 1
    0b000111000,  // Row 2
    0b000000111,  // Row 3
    0b100100100,  // Column 1
    0b010010010,  // Column 2
    0b001001001,  // Column 3
    0b100010001,  // Main diagonal
    0b001010100   // Anti-diagonal
]

function checkWin(playerBoard):
    for mask in WINNING_MASKS:
        if (playerBoard & mask) == mask:
            return true
    return false
```

## 13. Testing Scenarios

1. **X wins row**: X places 3 in a row — win detected
2. **O wins column**: O places 3 in a column — win detected
3. **X wins diagonal**: X gets main diagonal — win detected
4. **O wins anti-diagonal**: O gets anti-diagonal — win detected
5. **Draw**: All 9 cells filled, no winner — draw detected
6. **Invalid move**: Clicking occupied cell rejected
7. **AI blocks (Easy+)**: AI prevents opponent from winning
8. **AI takes win**: AI takes winning move when available
9. **Impossible AI never loses**: Play 100 games — AI never loses
10. **First move X**: X always goes first
11. **Center preference**: Medium+ AI takes center when available
12. **Fork creation**: Hard+ AI creates forks when possible
13. **Fork blocking**: Hard+ AI blocks opponent forks

## 14. Complete Game Tree Analysis

### 14.1 Game Complexity

| Metric                   | Value           |
|--------------------------|-----------------|
| Total possible games     | 255,168         |
| Unique positions         | 5,478           |
| Games won by X           | 131,184 (51.4%) |
| Games won by O           | 77,904 (30.5%)  |
| Games drawn              | 46,080 (18.1%)  |
| Average game length      | ~7 moves        |
| Minimum moves to win     | 5 (3 by winner) |
| Maximum game length      | 9 moves         |

### 14.2 Optimal Play Result
With perfect play by both sides, the game always ends in a draw.

## 15. Performance Requirements

| Metric                     | Target             |
|----------------------------|---------------------|
| Move validation            | < 0.1ms            |
| Win detection              | < 0.1ms            |
| Minimax (full tree)        | < 10ms             |
| AI move (any difficulty)   | < 50ms (computation)|
| Board render               | < 16ms             |
| Animation frame rate       | 60 FPS             |

## 16. Accessibility

- Large click targets (cells should be at least 80x80 pixels)
- Keyboard input: numpad 1-9 or arrow keys + Enter
- Screen reader: announce cell position and symbol
- High contrast mode
- Symbol display: clear X and O with sufficient thickness
- Color-blind safe: relies on shape (X vs O), not color alone
- Tab navigation between cells

## 17. Easter Eggs (Optional)

- **War Games reference**: When AI difficulty is "Impossible" and the game ends in a draw, display: "A strange game. The only winning move is not to play."
- **Streak bonus**: After winning 5 games in a row, show a congratulatory animation
- **Speed challenge**: Timer mode — complete a game in under 10 seconds
- **Reverse mode**: Try to LOSE (force the opponent to get 3 in a row)
