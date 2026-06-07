# Connect Four — Complete Game Specification

## 1. Game Overview

Connect Four is a two-player connection board game where players take turns dropping
colored discs into a vertical grid. The first player to form a horizontal, vertical,
or diagonal line of four discs wins.

- **Players**: 2 (Human vs AI)
- **Board**: 7 columns x 6 rows (vertical standing grid)
- **Pieces**: Red and Yellow discs (21 each, 42 total)
- **Objective**: Be the first to connect four of your discs in a row
- **Complexity**: Connect Four is a solved game — first player wins with perfect play

## 2. Technical Foundation

### 2.1 Display Requirements
- Vertical grid displayed as a blue frame with circular slots
- Discs shown as colored circles inside the grid
- Discs drop from the top and stack from the bottom
- Column selection indicators at the top

### 2.2 Board Layout (ASCII)

```
  Column:  1   2   3   4   5   6   7
         +---+---+---+---+---+---+---+
         | v | v | v | v | v | v | v |  <- Drop indicators
         +===+===+===+===+===+===+===+
  Row 6  |   |   |   |   |   |   |   |  (top)
         +---+---+---+---+---+---+---+
  Row 5  |   |   |   |   |   |   |   |
         +---+---+---+---+---+---+---+
  Row 4  |   |   |   |   |   |   |   |
         +---+---+---+---+---+---+---+
  Row 3  |   |   | ○ |   |   |   |   |
         +---+---+---+---+---+---+---+
  Row 2  |   | ● | ● | ○ |   |   |   |
         +---+---+---+---+---+---+---+
  Row 1  | ● | ○ | ● | ○ | ○ |   |   |  (bottom)
         +---+---+---+---+---+---+---+

Legend: ● = Red (Player 1/Human)
        ○ = Yellow (Player 2/AI)
```

### 2.3 Grid Dimensions

| Property        | Value  |
|----------------|--------|
| Columns         | 7      |
| Rows            | 6      |
| Total cells     | 42     |
| Discs per player| 21     |
| Win condition   | 4 in a line |

## 3. Core Rules

### 3.1 Turn Order
- Red (Player 1) always goes first
- Players alternate turns
- Each turn consists of dropping one disc into any non-full column

### 3.2 Disc Placement
1. Player selects a column (1-7)
2. The disc falls to the lowest available row in that column
3. If the column is full (all 6 rows occupied), the move is invalid
4. Gravity: discs always fall to the bottom of the selected column

### 3.3 Win Condition
A player wins by connecting four of their discs in a line:

**Horizontal (4 consecutive in a row):**
```
| ● | ● | ● | ● |
```

**Vertical (4 consecutive in a column):**
```
| ● |
| ● |
| ● |
| ● |
```

**Diagonal (ascending, 4 consecutive):**
```
|   |   |   | ● |
|   |   | ● |   |
|   | ● |   |   |
| ● |   |   |   |
```

**Diagonal (descending, 4 consecutive):**
```
| ● |   |   |   |
|   | ● |   |   |
|   |   | ● |   |
|   |   |   | ● |
```

### 3.4 Draw Condition
- The board is completely filled (42 discs placed) with no four-in-a-row
- The game ends in a draw (tie)

### 3.5 Win Detection Algorithm

```
function checkWin(board, lastRow, lastCol, color):
    directions = [(0,1), (1,0), (1,1), (1,-1)]  // horizontal, vertical, 2 diagonals

    for (dr, dc) in directions:
        count = 1  // count the placed disc

        // Check positive direction
        r, c = lastRow + dr, lastCol + dc
        while inBounds(r, c) and board[r][c] == color:
            count += 1
            r += dr
            c += dc

        // Check negative direction
        r, c = lastRow - dr, lastCol - dc
        while inBounds(r, c) and board[r][c] == color:
            count += 1
            r -= dr
            c -= dc

        if count >= 4:
            return true

    return false
```

## 4. Game State

| State Variable         | Type          | Description                          |
|------------------------|---------------|--------------------------------------|
| board[6][7]            | enum          | EMPTY, RED, YELLOW                   |
| columnHeights[7]       | integer       | Next available row in each column    |
| currentPlayer          | enum          | RED or YELLOW                        |
| moveHistory            | list          | Column numbers of all moves          |
| moveCount              | integer       | Total moves made                     |
| gameOver               | boolean       | Whether the game has ended           |
| winner                 | enum/null     | RED, YELLOW, or null (draw/ongoing)  |
| winningCells           | list          | The 4 cells forming the winning line |

## 5. AI Opponent

### 5.1 Difficulty Levels

| Level      | Depth  | Strategy                                    |
|------------|--------|---------------------------------------------|
| Beginner   | 1      | Random column selection, avoids giving 4    |
| Easy       | 2-3    | Basic threat detection                      |
| Medium     | 4-6    | Minimax with alpha-beta pruning             |
| Hard       | 8-10   | Full minimax + move ordering + heuristics   |
| Perfect    | Full   | Solved game — never loses as either color   |

### 5.2 Evaluation Function

```
function evaluate(board, aiColor):
    score = 0
    humanColor = opposite(aiColor)

    // Check all possible 4-in-a-row windows
    for each window of 4 consecutive cells (horizontal, vertical, diagonal):
        aiCount = count(window, aiColor)
        humanCount = count(window, humanColor)
        emptyCount = count(window, EMPTY)

        if humanCount == 0:  // only AI discs and empty
            score += windowScore(aiCount)
        if aiCount == 0:  // only human discs and empty
            score -= windowScore(humanCount)

    // Center column preference
    centerColumn = board[*][3]  // column index 3
    centerCount = count(centerColumn, aiColor)
    score += centerCount * 3

    return score

function windowScore(count):
    switch count:
        case 4: return 1000000   // win
        case 3: return 50        // strong threat
        case 2: return 5         // developing
        case 1: return 1         // weak
        default: return 0
```

### 5.3 Threat Detection

| Threat Type              | Description                              | Priority |
|--------------------------|------------------------------------------|----------|
| Immediate win            | 3 in a row with open 4th position        | 1 (highest) |
| Block opponent win       | Opponent has 3 in a row                  | 2        |
| Double threat            | Creating two 3-in-a-rows simultaneously  | 3        |
| Fork                     | Move creating multiple threats           | 4        |
| Forced sequence          | Series of threats forcing opponent       | 5        |

### 5.4 Minimax with Alpha-Beta

```
function minimax(board, depth, alpha, beta, isMaximizing):
    if checkWin(board, opponent): return -1000000 + (maxDepth - depth)
    if checkWin(board, ai): return 1000000 - (maxDepth - depth)
    if isBoardFull(board): return 0
    if depth == 0: return evaluate(board, aiColor)

    validColumns = getValidColumns(board)
    orderColumns(validColumns)  // center first: 3,2,4,1,5,0,6

    if isMaximizing:
        maxEval = -infinity
        for col in validColumns:
            row = dropDisc(board, col, aiColor)
            eval = minimax(board, depth-1, alpha, beta, false)
            removeDisc(board, col)
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha: break
        return maxEval
    else:
        minEval = +infinity
        for col in validColumns:
            row = dropDisc(board, col, humanColor)
            eval = minimax(board, depth-1, alpha, beta, true)
            removeDisc(board, col)
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            if beta <= alpha: break
        return minEval
```

### 5.5 Column Ordering

For better pruning, evaluate columns in this order:
```
Center first: 3, 2, 4, 1, 5, 0, 6
```
Center columns are statistically stronger moves.

### 5.6 Perfect Play (Solved Game)

Connect Four was solved in 1988 by Victor Allis. With perfect play:
- First player (Red) always wins
- Key opening: Column 4 (center) is the only winning first move
- The implementation can optionally include a solution database

### 5.7 AI Personality by Difficulty

**Beginner:**
- 40% chance of random move
- Always blocks immediate opponent win (if it notices — 80% detection rate)
- Prefers center columns slightly
- Does not plan ahead

**Easy:**
- 15% chance of suboptimal move
- Always blocks immediate threats
- Looks 1 move ahead for own winning moves
- Mild center preference

**Medium:**
- Always plays best found move
- Recognizes double threats
- Plans 3-4 moves ahead
- Good tactical play

**Hard:**
- Deep search (8+ ply)
- Creates forced winning sequences
- Recognizes all tactical patterns
- Near-perfect play

**Perfect:**
- Uses pre-computed solution or very deep search
- Never loses (wins as first player, draws as second)
- Instant responses from solution database

## 6. User Interface

### 6.1 Main Game Screen

```
+------------------------------------------------------------------+
|  CONNECT FOUR  vs  AI (Medium)                   [New] [Undo]    |
+------------------------------------------------------------------+
|                                                                  |
|  Red: ● (You)     Yellow: ○ (AI)     Move: 12                   |
|                                                                  |
|           1   2   3   4   5   6   7                              |
|         +---+---+---+---+---+---+---+                            |
|         | v |   |   | ▼ |   |   |   |  <- hover indicator        |
|         +===+===+===+===+===+===+===+                            |
|      6  |   |   |   |   |   |   |   |                            |
|         +---+---+---+---+---+---+---+                            |
|      5  |   |   |   |   |   |   |   |                            |
|         +---+---+---+---+---+---+---+                            |
|      4  |   |   |   | ○ |   |   |   |                            |
|         +---+---+---+---+---+---+---+                            |
|      3  |   |   | ○ | ● |   |   |   |                            |
|         +---+---+---+---+---+---+---+                            |
|      2  |   | ● | ● | ○ | ○ |   |   |                            |
|         +---+---+---+---+---+---+---+                            |
|      1  | ● | ○ | ● | ○ | ● | ○ |   |                            |
|         +---+---+---+---+---+---+---+                            |
|                                                                  |
|  Status: Your turn (Red) — click a column to drop a disc         |
+------------------------------------------------------------------+
|  [Resign]  [Settings]  [Hint]                                    |
+------------------------------------------------------------------+
```

### 6.2 Interaction Model
1. Hover over a column to see a preview disc at the top
2. Click to drop a disc into that column
3. Disc falls with animation from top to resting position
4. If column is full, hover shows "X" or no preview
5. Winning four cells are highlighted with a line through them

### 6.3 Drop Animation
- Disc appears at top of selected column
- Falls with gravity acceleration: y = y0 + 0.5 * g * t^2
- Bounces slightly at landing position (1-2 small bounces)
- Total animation time: 300-500ms depending on drop height
- Sound effect on landing

### 6.4 Win Animation
1. Game pauses
2. The four winning discs flash or pulse
3. A line is drawn through the winning four
4. Non-winning discs fade slightly
5. "Player X Wins!" banner appears

### 6.5 New Game Dialog

```
+---------------------------+
|     NEW CONNECT FOUR      |
|                           |
|  Play as:                 |
|  (•) Red (first move)    |
|  ( ) Yellow (second move) |
|                           |
|  AI Difficulty:           |
|  ( ) Beginner             |
|  (•) Easy                 |
|  ( ) Medium               |
|  ( ) Hard                 |
|  ( ) Perfect              |
|                           |
|  [Start Game]             |
+---------------------------+
```

### 6.6 Game Over Screen

```
+-----------------------------+
|        GAME OVER            |
|                             |
|  Red Wins!                  |
|  (connected diagonally)     |
|                             |
|  Moves: 23                  |
|  Duration: 3:45             |
|                             |
|  [Play Again] [New Setup]   |
+-----------------------------+
```

## 7. Game Flow

### 7.1 Turn Sequence
1. Display current board
2. If human's turn:
   a. Show hover preview on mouse movement
   b. Wait for column click
   c. Validate column is not full
   d. Drop disc with animation
   e. Check for win
   f. Check for draw (board full)
3. If AI's turn:
   a. Show "AI thinking..." indicator (brief)
   b. Run minimax/evaluation
   c. Drop disc with animation
   d. Check for win
   e. Check for draw
4. Switch player
5. Record move

### 7.2 Undo
- Undo removes the last human move AND the AI's response
- Board state is restored
- Move count decremented by 2

## 8. Data Structures

### 8.1 Board Representation

```
// 2D array (row 0 = bottom)
board[6][7] = EMPTY | RED | YELLOW

// Column heights array for efficient disc placement
heights[7] = next available row index (0-5, or 6 if full)
```

### 8.2 Move Representation

```
Move {
    column: 0-6       // which column
    row: 0-5           // where disc landed (computed from column height)
    color: RED | YELLOW
}
```

### 8.3 Bitboard (Optional Efficient Representation)

```
// Two 49-bit integers (7 columns x 7 rows, top row as buffer)
// Enables fast win detection via bitwise operations

function checkWin(bitboard):
    // Horizontal
    m = bitboard & (bitboard >> 1)
    if m & (m >> 2): return true
    // Vertical
    m = bitboard & (bitboard >> 7)
    if m & (m >> 14): return true
    // Diagonal /
    m = bitboard & (bitboard >> 6)
    if m & (m >> 12): return true
    // Diagonal \
    m = bitboard & (bitboard >> 8)
    if m & (m >> 16): return true
    return false
```

## 9. All Possible Four-in-a-Row Positions

Total number of possible winning lines:

| Direction    | Count |
|-------------|-------|
| Horizontal   | 24 (4 per row x 6 rows) |
| Vertical     | 21 (3 per column x 7 columns) |
| Diagonal /   | 12   |
| Diagonal \   | 12   |
| **Total**    | **69** |

## 10. Sound Effects

| Event              | Sound                          |
|--------------------|--------------------------------|
| Disc drop          | "Clunk" on landing             |
| Hover column       | Soft "tick"                    |
| Win                | Celebration jingle             |
| Draw               | Neutral tone                   |
| Invalid (full col) | Error buzz                     |
| Undo               | Reverse "swoosh"               |
| New game           | Brief chime                    |

## 11. Settings

| Setting              | Options                          | Default    |
|----------------------|----------------------------------|------------|
| Board theme          | Classic, Neon, Wood, Minimal    | Classic    |
| Disc colors          | Red/Yellow, Blue/Red, Custom    | Red/Yellow |
| Drop animation       | On/Off                          | On         |
| Sound effects        | On/Off                          | On         |
| Show hints           | On/Off                          | Off        |
| Show column numbers  | On/Off                          | On         |
| Animation speed      | Slow, Normal, Fast              | Normal     |

## 12. Testing Scenarios

1. **Horizontal win**: 4 in a row horizontally detected
2. **Vertical win**: 4 in a column vertically detected
3. **Diagonal win (/)**: Ascending diagonal detected
4. **Diagonal win (\)**: Descending diagonal detected
5. **Draw**: Full board with no winner
6. **Full column**: Dropping into full column rejected
7. **First move**: Disc lands at row 1 (bottom)
8. **Stacking**: Discs stack correctly in a column
9. **Gravity**: Disc falls to lowest available slot
10. **Win on move 7**: Earliest possible win (7 moves total, 4 by winner)
11. **AI blocks**: AI blocks imminent human win at all difficulty levels >= Easy
12. **AI wins**: AI takes winning move when available

## 13. Performance Requirements

| Metric                     | Target             |
|----------------------------|---------------------|
| Move validation            | < 0.1ms            |
| Win detection              | < 0.1ms            |
| AI move (Easy)             | < 100ms            |
| AI move (Medium)           | < 500ms            |
| AI move (Hard)             | < 2 seconds        |
| AI move (Perfect)          | < 1 second (DB)    |
| Drop animation             | 60 FPS             |
| Board render               | < 16ms             |

## 14. Statistics

| Statistic              | Description                     |
|------------------------|---------------------------------|
| Games played           | Total per difficulty            |
| Win/Loss/Draw          | Record per difficulty           |
| Win rate               | Percentage                      |
| Average game length    | Moves per game                  |
| Fastest win            | Fewest moves to win             |
| Win type breakdown     | Horizontal/Vertical/Diagonal %  |

## 15. Accessibility

- Keyboard input: number keys 1-7 to select column
- High contrast disc colors
- Pattern overlay on discs (stripes vs dots) for color-blind users
- Screen reader: announce column and row of each drop
- Tab navigation between columns
- Text labels on discs showing player indicator
