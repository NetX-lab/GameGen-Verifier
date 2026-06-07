# Checkers (Draughts) — Complete Game Specification

## 1. Game Overview

Checkers (also known as Draughts) is a two-player strategy board game played on an
8x8 board using only the dark squares. Players move their pieces diagonally and
capture opponent pieces by jumping over them.

- **Players**: 2 (Human vs AI)
- **Board**: 8x8 grid, only dark squares used (32 playable squares)
- **Pieces per player**: 12
- **Objective**: Capture all opponent pieces or block them from moving
- **Variant**: American/British Checkers (English Draughts)

## 2. Technical Foundation

### 2.1 Display Requirements
- Board rendered with alternating light/dark squares
- Only dark squares are playable
- Pieces shown as filled circles (regular) or crowned circles (kings)
- Red pieces for one player, black/white for the other

### 2.2 Coordinate System
- Squares numbered 1-32 (traditional notation)
- Or use column-row coordinates on the 8x8 grid
- Row 1 is at the bottom (human's side), Row 8 at top (AI's side)

### 2.3 Board Layout (ASCII)

```
    1   2   3   4   5   6   7   8
  +---+---+---+---+---+---+---+---+
8 |   | b |   | b |   | b |   | b |  8   (AI pieces: black)
  +---+---+---+---+---+---+---+---+
7 | b |   | b |   | b |   | b |   |  7
  +---+---+---+---+---+---+---+---+
6 |   | b |   | b |   | b |   | b |  6
  +---+---+---+---+---+---+---+---+
5 |   |   |   |   |   |   |   |   |  5   (empty rows)
  +---+---+---+---+---+---+---+---+
4 |   |   |   |   |   |   |   |   |  4
  +---+---+---+---+---+---+---+---+
3 | r |   | r |   | r |   | r |   |  3
  +---+---+---+---+---+---+---+---+
2 |   | r |   | r |   | r |   | r |  2   (Human pieces: red)
  +---+---+---+---+---+---+---+---+
1 | r |   | r |   | r |   | r |   |  1
  +---+---+---+---+---+---+---+---+
    1   2   3   4   5   6   7   8

Legend: r = red piece, b = black piece
        R = red king, B = black king
        Playable squares are dark-colored
```

## 3. Piece Definitions

### 3.1 Regular Piece (Man)

| Property          | Value                                      |
|-------------------|--------------------------------------------|
| Movement          | Forward diagonal only, 1 square             |
| Capture           | Forward diagonal jump, 1 square over enemy  |
| Multiple capture  | Yes, must continue jumping if possible      |
| Promotion         | Reaches opponent's back row becomes King     |

### 3.2 King Piece

| Property          | Value                                      |
|-------------------|--------------------------------------------|
| Movement          | Any diagonal direction, 1 square            |
| Capture           | Any diagonal jump, 1 square over enemy      |
| Multiple capture  | Yes, must continue jumping if possible      |
| Visual            | Crown symbol or double-stacked piece        |

### 3.3 Starting Position
- Red (Human): 12 pieces on dark squares of rows 1-3
- Black (AI): 12 pieces on dark squares of rows 6-8
- Rows 4-5 are empty at start

## 4. Movement Rules

### 4.1 Regular Moves
- A man moves one square diagonally forward
- Can only move to an empty dark square
- Cannot move backward (only Kings can)
- Cannot move to occupied squares

### 4.2 Capture (Jump) Moves
- A piece jumps over an adjacent opponent piece to an empty square beyond
- The jumped piece is removed from the board
- The jump must be diagonal
- Regular pieces can only jump forward
- Kings can jump in any diagonal direction

### 4.3 Multiple Jumps
- If after a jump, the piece can make another jump, it MUST continue
- Multiple jumps in a single turn
- The piece can change direction during multiple jumps (Kings only for backward)
- All captured pieces are removed after the complete sequence

### 4.4 Mandatory Capture Rule
- If a capture is available, the player MUST capture
- If multiple captures are available, the player may choose which one
- This is strictly enforced — no optional captures
- If a multi-jump is available, the player must complete the entire sequence

### 4.5 Promotion (Kinging)
- When a regular piece reaches the opponent's back row, it becomes a King
- In American checkers: if a piece reaches the back row during a multi-jump,
  it is promoted BUT its turn ends (it cannot continue jumping as a king
  in the same turn)
- Kings are marked with a crown or double-stack

## 5. Win/Loss/Draw Conditions

### 5.1 Win Conditions
A player wins when:
1. The opponent has no pieces remaining on the board
2. The opponent has pieces but cannot make any legal move (blocked)

### 5.2 Draw Conditions
1. Both players agree to a draw
2. The same position repeats three times
3. 40 consecutive moves by each player without a capture or promotion
4. Neither player can force a win (e.g., certain king vs king endgames)
5. One king vs one king with no other pieces

## 6. Game State Tracking

| State Variable         | Type          | Description                              |
|------------------------|---------------|------------------------------------------|
| board[8][8]            | Piece/null    | Current board position                   |
| activePlayer           | enum          | RED or BLACK                             |
| redPieces              | integer       | Number of red pieces remaining           |
| blackPieces            | integer       | Number of black pieces remaining         |
| redKings               | integer       | Number of red kings                      |
| blackKings             | integer       | Number of black kings                    |
| movesSinceCapture      | integer       | For 40-move draw rule                    |
| moveHistory            | list          | All moves made                           |
| positionHistory        | list          | For threefold repetition detection       |
| selectedPiece          | coords/null   | Currently selected piece                 |
| availableJumps         | list          | Mandatory jumps for current player       |
| isMultiJump            | boolean       | Whether in middle of multi-jump          |
| multiJumpPiece         | coords/null   | Piece performing multi-jump              |

## 7. AI Opponent

### 7.1 Difficulty Levels

| Level      | Search Depth | Strategy                                    |
|------------|-------------|---------------------------------------------|
| Beginner   | 1-2 ply     | Random legal move, occasional blunders      |
| Easy       | 3-4 ply     | Basic material evaluation                   |
| Medium     | 5-6 ply     | Material + position evaluation              |
| Hard       | 7-8 ply     | Full evaluation with alpha-beta pruning     |
| Expert     | 9-12 ply    | Full evaluation + endgame database          |

### 7.2 Evaluation Function

**Material Score:**

| Piece Type    | Value  |
|---------------|--------|
| Regular piece | 100    |
| King          | 160    |

**Positional Bonuses:**

1. **Center Control** (+15 per piece):
   - Pieces on center squares (rows 4-5, columns 3-6) get bonuses

2. **Advancement** (+5 per row):
   - Pieces closer to promotion row get bonuses (for regular pieces only)

3. **Back Row Defense** (+10):
   - Keeping pieces on the back row prevents opponent from getting kings

4. **King Mobility** (+3 per move):
   - Kings with more available moves score higher

5. **Edge Penalty** (-5):
   - Pieces on the edge of the board have fewer move options

6. **Formation Bonus** (+8):
   - Pieces that protect each other (diagonal support)

7. **Trapped King Penalty** (-20):
   - Kings that are boxed in with no moves

### 7.3 Search Algorithm

Alpha-beta pruning with iterative deepening:

```
function alphabeta(position, depth, alpha, beta, maximizing):
    if depth == 0 or game_over:
        return evaluate(position)

    moves = generate_legal_moves(position)
    order_moves(moves)  // captures first

    if maximizing:
        value = -infinity
        for move in moves:
            make_move(move)
            value = max(value, alphabeta(position, depth-1, alpha, beta, false))
            undo_move(move)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = +infinity
        for move in moves:
            make_move(move)
            value = min(value, alphabeta(position, depth-1, alpha, beta, true))
            undo_move(move)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value
```

### 7.4 AI Behavior by Difficulty

**Beginner:**
- 30% chance of making a random move instead of the best move
- Does not always take the longest jump chain
- No positional evaluation — material only

**Easy:**
- 10% chance of making a suboptimal move
- Basic positional awareness
- Does not plan ahead well

**Medium:**
- Always plays the best move found
- Considers positional factors
- Plans 2-3 moves ahead effectively

**Hard:**
- Deep search with good move ordering
- Recognizes tactical patterns (forks, traps)
- Strong endgame play

**Expert:**
- Maximum depth search
- Opening book of known good first moves
- Endgame database for perfect play with few pieces

### 7.5 Opening Strategy

The AI should know common opening principles:
1. Control the center early
2. Develop pieces toward the center
3. Keep back row pieces to prevent opponent kings
4. Avoid moving edge pieces early
5. Create strong pawn formations

## 8. User Interface Layout

### 8.1 Main Game Screen

```
+------------------------------------------------------------------+
|  CHECKERS  vs  AI (Medium)                       [New] [Undo]    |
+------------------------------------------------------------------+
|                                                                  |
|  AI Pieces: ●●●●●●●●●● (10 remaining, 1 king)                   |
|                                                                  |
|      1   2   3   4   5   6   7   8                              |
|    +---+---+---+---+---+---+---+---+                             |
|  8 |   | ● |   | ● |   | ● |   | ● |  8                         |
|    +---+---+---+---+---+---+---+---+                             |
|  7 | ● |   | ● |   | ★ |   | ● |   |  7    ★ = King             |
|    +---+---+---+---+---+---+---+---+                             |
|  6 |   | ● |   |   |   | ● |   |   |  6                         |
|    +---+---+---+---+---+---+---+---+                             |
|  5 |   |   |   | ○ |   |   |   |   |  5                         |
|    +---+---+---+---+---+---+---+---+                             |
|  4 |   |   |   |   |   |   |   |   |  4                         |
|    +---+---+---+---+---+---+---+---+                             |
|  3 | ○ |   | ○ |   | ○ |   |   |   |  3                         |
|    +---+---+---+---+---+---+---+---+                             |
|  2 |   | ○ |   | ○ |   | ○ |   | ○ |  2                         |
|    +---+---+---+---+---+---+---+---+                             |
|  1 | ○ |   | ○ |   | ○ |   | ○ |   |  1                         |
|    +---+---+---+---+---+---+---+---+                             |
|      1   2   3   4   5   6   7   8                              |
|                                                                  |
|  Your Pieces: ○○○○○○○○○○○ (11 remaining, 0 kings)               |
|                                                                  |
|  Status: Your turn — select a piece to move                      |
|  [Must capture: pieces at (3,1) and (3,3) can jump]             |
+------------------------------------------------------------------+
|  [Resign]  [Offer Draw]  [Settings]  [Hint]                     |
+------------------------------------------------------------------+
```

### 8.2 Interaction Model

1. Click a piece to select it
   - Highlight the selected piece
   - Show legal move destinations as green dots
   - Show legal jump destinations as red dots
2. Click a destination to move
3. If multi-jump available, piece stays selected for next jump
4. If mandatory capture exists, only jumpable pieces are selectable

### 8.3 Visual Indicators

| Indicator                | Visual                              |
|--------------------------|-------------------------------------|
| Selected piece           | Bright highlight/glow               |
| Legal moves              | Green dots on destination squares   |
| Legal jumps              | Red dots on destination squares     |
| Last move                | Light yellow highlight on squares   |
| Mandatory capture        | Pulsing border on pieces that must jump |
| King piece               | Crown symbol or "K" overlay         |
| Captured piece animation | Fade out / slide off board          |

### 8.4 Piece Appearance

```
Regular piece:     King piece:
  +-----+           +-----+
  | ○○○ |           | ♛♛♛ |
  | ○○○ |           | ○○○ |
  | ○○○ |           | ○○○ |
  +-----+           +-----+
```

## 9. Game Flow

### 9.1 New Game Setup

```
+---------------------------+
|     NEW CHECKERS GAME     |
|                           |
|  Play as: [Red] [Black]   |
|                           |
|  AI Difficulty:           |
|  ( ) Beginner             |
|  (•) Easy                 |
|  ( ) Medium               |
|  ( ) Hard                 |
|  ( ) Expert               |
|                           |
|  Rules Variant:           |
|  (•) American/British     |
|  ( ) International        |
|                           |
|  [Start Game]             |
+---------------------------+
```

### 9.2 Turn Sequence

1. Check for mandatory captures
2. If human's turn:
   a. Highlight pieces that can move (or must jump)
   b. Wait for piece selection
   c. Show legal moves/jumps
   d. Execute selected move
   e. If multi-jump: repeat until no more jumps
   f. Check for promotion
   g. Check for win/draw
3. If AI's turn:
   a. Show "AI thinking..." indicator
   b. Run search algorithm
   c. Execute move with animation
   d. Check for promotion
   e. Check for win/draw
4. Switch active player

### 9.3 Game End Screen

```
+---------------------------+
|       GAME OVER           |
|                           |
|  You Win!                 |
|                           |
|  Red: 5 pieces remaining  |
|  Black: 0 pieces          |
|                           |
|  Moves: 47                |
|  Duration: 8:32           |
|                           |
|  [New Game] [Review]      |
+---------------------------+
```

## 10. Move Notation

Standard checkers notation uses square numbers 1-32:

```
Square numbering (dark squares only):

     1       2       3       4
  5       6       7       8
     9      10      11      12
 13      14      15      16
    17      18      19      20
 21      22      23      24
    25      26      27      28
 29      30      31      32
```

**Notation format:**
- Simple move: `11-15` (from square 11 to square 15)
- Jump: `11x18` (from square 11, jumping to square 18)
- Multiple jump: `11x18x25` (double jump)

## 11. Hint System

When the player requests a hint:
1. Run the AI evaluation at current difficulty level
2. Highlight the recommended piece and destination
3. Show the evaluation score change
4. Fade hint after 3 seconds or on any click

## 12. Undo System

- Undo takes back the last complete move (including AI's response)
- Undo is unlimited on Beginner/Easy
- Limited to 3 undos on Medium
- Limited to 1 undo on Hard
- No undo on Expert

## 13. Statistics Tracking

| Statistic              | Description                         |
|------------------------|-------------------------------------|
| Games played           | Total games at each difficulty      |
| Win/Loss/Draw record   | Per difficulty level                |
| Win rate               | Percentage per difficulty           |
| Average game length    | Moves per game                      |
| Longest win streak     | Consecutive wins                    |
| Most pieces captured   | In a single game                    |
| Fastest win            | Fewest moves to win                 |

## 14. Sound Effects

| Event              | Sound                           |
|--------------------|---------------------------------|
| Piece move         | Soft slide sound                |
| Single jump        | "Pop" or "click"                |
| Multiple jump      | Rapid successive "pops"         |
| Promotion to King  | Royal fanfare/chime             |
| Win                | Victory music                   |
| Lose               | Defeat sound                    |
| Invalid move       | Error buzz                      |
| Select piece       | Soft click                      |

## 15. Settings

| Setting              | Options                          | Default    |
|----------------------|----------------------------------|------------|
| Board theme          | Classic, Wood, Dark, Neon        | Classic    |
| Piece style          | Flat, 3D, Traditional            | Flat       |
| Show legal moves     | On/Off                           | On         |
| Show forced captures | On/Off                           | On         |
| Sound effects        | On/Off                           | On         |
| Animation speed      | Slow, Normal, Fast               | Normal     |
| Board orientation    | Fixed, Flip each game            | Fixed      |
| Undo enabled         | On/Off                           | On         |

## 16. Data Structures

### 16.1 Board Representation

```
// 8x8 array, only dark squares used
board[row][col] = {
    null,                    // empty or light square
    { color: 'red', king: false },
    { color: 'black', king: true }
}

// Alternative: 32-element array for dark squares only
darkSquares[32] = { EMPTY, RED, RED_KING, BLACK, BLACK_KING }
```

### 16.2 Move Representation

```
Move {
    from: { row, col }
    to: { row, col }
    captures: [{ row, col }]     // list of captured piece positions
    isJump: boolean
    isMultiJump: boolean
    promotion: boolean           // piece was promoted
}
```

## 17. Testing Scenarios

1. **Forced capture**: Player must jump when available
2. **Multi-jump**: Chain of 3+ jumps in one turn
3. **Promotion**: Piece reaching back row becomes king
4. **King movement**: King moves backward correctly
5. **Blocked position**: Player with pieces but no moves loses
6. **Draw by repetition**: Same position 3 times is a draw
7. **40-move rule**: Draw after 40 moves without capture or promotion
8. **Edge cases**: Pieces on board edges have correct move options
9. **Mandatory capture choice**: When multiple captures available, player chooses
10. **Promotion during multi-jump**: Turn ends at back row in American rules

## 18. Performance Requirements

| Metric                     | Target             |
|----------------------------|---------------------|
| Move generation            | < 5ms               |
| AI move (Easy)             | < 200ms             |
| AI move (Medium)           | < 1 second          |
| AI move (Hard)             | < 3 seconds         |
| AI move (Expert)           | < 5 seconds         |
| Animation frame rate       | 60 FPS              |
| Board render               | < 16ms              |

## 19. International Draughts Variant (Optional Extension)

If implementing International Draughts as an option:

| Feature                    | American           | International       |
|----------------------------|--------------------|---------------------|
| Board size                 | 8x8                | 10x10               |
| Pieces per player          | 12                 | 20                  |
| King movement              | 1 square           | Any distance (flying king) |
| Capture rule               | Must capture       | Must capture maximum |
| Backward capture (men)     | No                 | Yes                 |
| Promotion during jump      | Stops at back row  | Continues jumping   |

## 20. Accessibility Features

- High contrast mode for piece colors
- Large piece option for visibility
- Text labels showing piece positions
- Keyboard navigation: arrow keys + Enter
- Screen reader: announce moves and board state
- Color-blind mode: use shapes (circle vs triangle) instead of colors only
