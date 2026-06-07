# Chess — Complete Game Specification

## 1. Game Overview

Chess is a two-player strategy board game played on an 8x8 grid. One player controls
the white pieces, the other controls black. In this digital implementation, the human
plays as White and the AI plays as Black (with an option to swap sides).

- **Players**: 2 (Human vs AI)
- **Board**: 8x8 grid, alternating light/dark squares
- **Objective**: Checkmate the opponent's King
- **Average Game Length**: 40-60 moves per side

## 2. Technical Foundation

### 2.1 Display Requirements
- Minimum resolution: 800x600
- Board rendered as an 8x8 grid with alternating colors
- Pieces rendered as Unicode chess symbols or sprite images
- Sidebar showing captured pieces, move history, and game status

### 2.2 Coordinate System
- Columns labeled a-h (left to right from White's perspective)
- Rows labeled 1-8 (bottom to top from White's perspective)
- Square identified as column+row, e.g., "e4"

### 2.3 Board Layout (ASCII)

```
    a   b   c   d   e   f   g   h
  +---+---+---+---+---+---+---+---+
8 | r | n | b | q | k | b | n | r |  8   (Black pieces)
  +---+---+---+---+---+---+---+---+
7 | p | p | p | p | p | p | p | p |  7   (Black pawns)
  +---+---+---+---+---+---+---+---+
6 |   |   |   |   |   |   |   |   |  6
  +---+---+---+---+---+---+---+---+
5 |   |   |   |   |   |   |   |   |  5
  +---+---+---+---+---+---+---+---+
4 |   |   |   |   |   |   |   |   |  4
  +---+---+---+---+---+---+---+---+
3 |   |   |   |   |   |   |   |   |  3
  +---+---+---+---+---+---+---+---+
2 | P | P | P | P | P | P | P | P |  2   (White pawns)
  +---+---+---+---+---+---+---+---+
1 | R | N | B | Q | K | B | N | R |  1   (White pieces)
  +---+---+---+---+---+---+---+---+
    a   b   c   d   e   f   g   h
```

## 3. Piece Definitions

### 3.1 Piece Table

| Piece   | Symbol (W/B) | Unicode (W/B) | Value | Qty per side |
|---------|-------------|---------------|-------|--------------|
| King    | K / k       | ♔ / ♚        | ∞     | 1            |
| Queen   | Q / q       | ♕ / ♛        | 9     | 1            |
| Rook    | R / r       | ♖ / ♜        | 5     | 2            |
| Bishop  | B / b       | ♗ / ♝        | 3     | 2            |
| Knight  | N / n       | ♘ / ♞        | 3     | 2            |
| Pawn    | P / p       | ♙ / ♟        | 1     | 8            |

### 3.2 Starting Positions

**White (Row 1-2):**
- Row 1: Ra1, Nb1, Bc1, Qd1, Ke1, Bf1, Ng1, Rh1
- Row 2: Pa2, Pb2, Pc2, Pd2, Pe2, Pf2, Pg2, Ph2

**Black (Row 7-8):**
- Row 8: ra8, nb8, bc8, qd8, ke8, bf8, ng8, rh8
- Row 7: pa7, pb7, pc7, pd7, pe7, pf7, pg7, ph7

## 4. Movement Rules

### 4.1 King
- Moves exactly one square in any direction (horizontally, vertically, diagonally)
- Cannot move into a square attacked by an opponent's piece
- Special move: Castling (see Section 5.1)
- Move offsets: (±1, 0), (0, ±1), (±1, ±1)

### 4.2 Queen
- Moves any number of squares in any direction (horizontally, vertically, diagonally)
- Cannot jump over other pieces
- Combines the movement of Rook and Bishop

### 4.3 Rook
- Moves any number of squares horizontally or vertically
- Cannot jump over other pieces
- Participates in Castling (see Section 5.1)

### 4.4 Bishop
- Moves any number of squares diagonally
- Cannot jump over other pieces
- Always stays on the same color square throughout the game

### 4.5 Knight
- Moves in an "L" shape: 2 squares in one direction + 1 square perpendicular
- CAN jump over other pieces (only piece that can)
- Move offsets: (±1, ±2), (±2, ±1) — 8 possible destination squares

### 4.6 Pawn
- Moves forward one square (toward opponent's side)
- From starting position, may move forward two squares
- Captures diagonally forward one square
- Special moves: En Passant (5.2), Promotion (5.3)
- White pawns move from row 2 toward row 8
- Black pawns move from row 7 toward row 1

## 5. Special Rules

### 5.1 Castling

Castling moves the King two squares toward a Rook, and the Rook moves to the
square the King crossed. There are two types:

**Kingside Castling (O-O):**
- King moves from e1 to g1 (White) or e8 to g8 (Black)
- Rook moves from h1 to f1 (White) or h8 to f8 (Black)

**Queenside Castling (O-O-O):**
- King moves from e1 to c1 (White) or e8 to c8 (Black)
- Rook moves from a1 to d1 (White) or a8 to d8 (Black)

**Conditions (ALL must be true):**
1. Neither the King nor the chosen Rook has previously moved
2. No pieces between the King and Rook
3. The King is not currently in check
4. The King does not pass through a square attacked by an opponent
5. The King does not land on a square attacked by an opponent

### 5.2 En Passant

When a pawn advances two squares from its starting position and lands beside an
opponent's pawn, the opponent may capture it as if it had only moved one square.

**Conditions:**
1. The capturing pawn must be on its 5th rank (row 5 for White, row 4 for Black)
2. The opponent's pawn must have just moved two squares forward
3. The capture must be made immediately on the next move or the right is lost

**Mechanics:**
- The capturing pawn moves diagonally to the square behind the opponent's pawn
- The opponent's pawn is removed from the board

### 5.3 Pawn Promotion

When a pawn reaches the opposite end of the board (row 8 for White, row 1 for Black),
it must be promoted to a Queen, Rook, Bishop, or Knight of the same color.

- The player chooses the promotion piece
- The pawn is replaced immediately
- It is legal to have multiple Queens or other pieces through promotion
- Default AI choice: Queen (unless another piece forces checkmate)

## 6. Check, Checkmate, and Stalemate

### 6.1 Check
- A King is in check when it is attacked by at least one opponent piece
- The player whose King is in check MUST resolve the check on the next move
- Ways to resolve check:
  1. Move the King to a safe square
  2. Block the checking piece with another piece
  3. Capture the checking piece

### 6.2 Checkmate
- The King is in check AND there is no legal move to escape check
- The game ends immediately
- The player delivering checkmate wins

### 6.3 Stalemate
- The player to move has NO legal moves AND is NOT in check
- The game is a draw

### 6.4 Other Draw Conditions
- **Threefold Repetition**: The same position occurs three times with the same player to move
- **Fifty-Move Rule**: 50 consecutive moves by each player without a pawn move or capture
- **Insufficient Material**: Neither player has enough pieces to checkmate:
  - King vs King
  - King + Bishop vs King
  - King + Knight vs King
  - King + Bishop vs King + Bishop (same color bishops)
- **Agreement**: In human vs AI, the player can offer/accept a draw (AI will accept if evaluation is near 0)
- **Resignation**: A player can resign at any time

## 7. Game State Tracking

The implementation must track:

| State Variable         | Type          | Description                                  |
|------------------------|---------------|----------------------------------------------|
| board[8][8]            | Piece/null    | Current board position                       |
| activeColor            | enum          | WHITE or BLACK                               |
| castlingRights         | 4 booleans    | K, Q, k, q availability                     |
| enPassantTarget        | square/null   | Target square for en passant                 |
| halfmoveClock          | integer       | Moves since last pawn move or capture        |
| fullmoveNumber         | integer       | Incremented after Black's move               |
| moveHistory            | list          | All moves in algebraic notation              |
| positionHistory        | list          | All positions for threefold repetition check |
| capturedPieces         | list          | Pieces captured by each side                 |

### 7.1 FEN Notation Support

The game should support Forsyth-Edwards Notation for saving/loading positions.

**Starting position FEN:**
```
rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

**FEN fields:**
1. Piece placement (rank 8 to rank 1, "/" between ranks)
2. Active color: "w" or "b"
3. Castling availability: "KQkq" or subset, "-" if none
4. En passant target square or "-"
5. Halfmove clock
6. Fullmove number

### 7.2 Algebraic Notation

Moves recorded in Standard Algebraic Notation (SAN):
- Piece letter + destination: Nf3, Bb5, Qd7
- Pawn moves: e4, d5 (no piece letter)
- Captures: Nxf3, exd5 (x for capture)
- Castling: O-O (kingside), O-O-O (queenside)
- Check: + suffix (e.g., Bb5+)
- Checkmate: # suffix (e.g., Qxf7#)
- Promotion: e8=Q
- Disambiguation: Rae1 (file), R1e3 (rank), Qh4e1 (both)

## 8. AI Opponent

### 8.1 Difficulty Levels

| Level      | Search Depth | Evaluation | Features                              |
|------------|-------------|------------|---------------------------------------|
| Beginner   | 1-2 ply     | Material   | Random from top 5 moves, occasional blunders |
| Easy       | 2-3 ply     | Material + basic positional | Top 3 moves considered |
| Medium     | 3-4 ply     | Full evaluation | Alpha-beta pruning           |
| Hard       | 4-6 ply     | Full evaluation | Alpha-beta + move ordering   |
| Expert     | 6-8 ply     | Full evaluation | Alpha-beta + quiescence + transposition table |

### 8.2 Evaluation Function

**Material Score:**
| Piece  | Value (centipawns) |
|--------|--------------------|
| Pawn   | 100                |
| Knight | 320                |
| Bishop | 330                |
| Rook   | 500                |
| Queen  | 900                |
| King   | 20000              |

**Positional Factors:**

1. **Piece-Square Tables**: Each piece has a preferred position value
   - Knights prefer center squares (+20 for d4/d5/e4/e5)
   - Bishops prefer long diagonals
   - Rooks prefer open files and the 7th rank
   - King prefers corners in middlegame, center in endgame
   - Pawns prefer advancement and center control

2. **Pawn Structure** (±50 centipawns):
   - Doubled pawns: -20 per pair
   - Isolated pawns: -15 each
   - Passed pawns: +30 each (more if advanced)
   - Pawn chains: +10 per chain member

3. **King Safety** (±100 centipawns):
   - Pawn shield: +30 per pawn in front of castled king
   - Open files near king: -40 each
   - Castled: +50

4. **Mobility**: +3 per legal move available

5. **Center Control**: +10 per center square (d4, d5, e4, e5) controlled

### 8.3 Search Algorithm

```
function minimax(position, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or game_over:
        return evaluate(position)

    if maximizingPlayer:
        maxEval = -infinity
        for each move in ordered_legal_moves(position):
            make_move(move)
            eval = minimax(position, depth-1, alpha, beta, false)
            unmake_move(move)
            maxEval = max(maxEval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break  # Beta cutoff
        return maxEval
    else:
        minEval = +infinity
        for each move in ordered_legal_moves(position):
            make_move(move)
            eval = minimax(position, depth-1, alpha, beta, true)
            unmake_move(move)
            minEval = min(minEval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break  # Alpha cutoff
        return minEval
```

### 8.4 Move Ordering (for pruning efficiency)
1. Captures (MVV-LVA: Most Valuable Victim - Least Valuable Attacker)
2. Checks
3. Killer moves (moves that caused cutoffs at same depth)
4. History heuristic (moves that were good in other positions)
5. Remaining moves

### 8.5 Opening Book

The AI should include a small opening book with common openings:

| Opening Name      | Moves                          |
|-------------------|--------------------------------|
| Italian Game      | 1.e4 e5 2.Nf3 Nc6 3.Bc4       |
| Sicilian Defense  | 1.e4 c5                        |
| French Defense    | 1.e4 e6                        |
| Queen's Gambit    | 1.d4 d5 2.c4                   |
| King's Indian     | 1.d4 Nf6 2.c4 g6               |
| Ruy Lopez         | 1.e4 e5 2.Nf3 Nc6 3.Bb5       |
| Caro-Kann         | 1.e4 c6                        |
| English Opening   | 1.c4                           |

The AI selects from known book moves (with slight randomization) until the position
leaves the book, then switches to search.

## 9. User Interface Layout

### 9.1 Main Screen (ASCII)

```
+------------------------------------------------------------------+
|  CHESS  vs  AI (Medium)                          [New] [Undo]    |
+------------------------------------------------------------------+
|                                                                  |
|  Captured by You: ♟♟♞                                            |
|                                                                  |
|      a   b   c   d   e   f   g   h                              |
|    +---+---+---+---+---+---+---+---+                             |
|  8 |   |   |   |   | ♚ |   |   | ♜ |  8    Move History         |
|    +---+---+---+---+---+---+---+---+        +-----------+        |
|  7 | ♟ |   |   |   | ♟ | ♟ | ♟ | ♟ |  7    | 1. e4  e5 |        |
|    +---+---+---+---+---+---+---+---+        | 2. Nf3 Nc6|        |
|  6 |   |   |   |   |   | ♞ |   |   |  6    | 3. Bb5 a6 |        |
|    +---+---+---+---+---+---+---+---+        | 4. Ba4 Nf6|        |
|  5 |   |   |   |   |   |   |   |   |  5    | 5. O-O Be7|        |
|    +---+---+---+---+---+---+---+---+        | 6. ...    |        |
|  4 |   |   |   |   | ♙ |   |   |   |  4    |           |        |
|    +---+---+---+---+---+---+---+---+        +-----------+        |
|  3 |   |   |   |   |   | ♘ |   |   |  3                         |
|    +---+---+---+---+---+---+---+---+                             |
|  2 | ♙ | ♙ | ♙ | ♙ |   | ♙ | ♙ | ♙ |  2                         |
|    +---+---+---+---+---+---+---+---+                             |
|  1 | ♖ | ♘ | ♗ | ♕ | ♔ |   |   | ♖ |  1                         |
|    +---+---+---+---+---+---+---+---+                             |
|      a   b   c   d   e   f   g   h                              |
|                                                                  |
|  Captured by AI: ♙♗                                              |
|                                                                  |
|  Status: Your turn (White)                                       |
+------------------------------------------------------------------+
|  [Resign]  [Offer Draw]  [Settings]  [Save Game]                |
+------------------------------------------------------------------+
```

### 9.2 Interaction Model
- Click a piece to select it (highlight legal destination squares)
- Click a destination square to move
- Alternatively: drag and drop
- Right-click to deselect
- Illegal moves are rejected with visual feedback (flash red)

### 9.3 Visual Indicators
- **Selected piece**: Highlighted border
- **Legal moves**: Green dots on destination squares
- **Last move**: Highlighted source and destination squares (light yellow)
- **Check**: King square highlighted in red
- **Promotion dialog**: Popup with piece choices when pawn reaches last rank

### 9.4 Promotion Dialog
```
+---------------------+
|  Promote Pawn To:   |
|                     |
|  [♕] [♖] [♗] [♘]   |
|  Queen Rook Bishop Knight |
+---------------------+
```

## 10. Game Flow

### 10.1 New Game Setup
```
+---------------------------+
|     NEW CHESS GAME        |
|                           |
|  Play as: [White] [Black] |
|                           |
|  AI Difficulty:           |
|  ( ) Beginner             |
|  ( ) Easy                 |
|  (•) Medium               |
|  ( ) Hard                 |
|  ( ) Expert               |
|                           |
|  Time Control:            |
|  ( ) None                 |
|  ( ) 5 min                |
|  (•) 10 min               |
|  ( ) 15 min               |
|  ( ) 30 min               |
|                           |
|  [Start Game]             |
+---------------------------+
```

### 10.2 Turn Sequence
1. Display current board state
2. If human's turn:
   a. Wait for piece selection
   b. Show legal moves
   c. Wait for destination selection
   d. Validate and execute move
   e. Update board display
   f. Check for game-ending conditions
3. If AI's turn:
   a. Show "AI thinking..." indicator
   b. Run search algorithm
   c. Execute best move (with brief animation)
   d. Update board display
   e. Check for game-ending conditions
4. Record move in history
5. Toggle active player

### 10.3 Game End
```
+---------------------------+
|      GAME OVER            |
|                           |
|  Checkmate!               |
|  White wins               |
|                           |
|  Moves: 34                |
|  Duration: 12:45          |
|                           |
|  [New Game] [Review Game] |
+---------------------------+
```

## 11. Timer System (Optional)

- Each player has a countdown timer
- Timer runs during the active player's turn
- When a player's timer reaches 0, that player loses on time
- Display format: MM:SS (or M:SS.s when under 10 seconds)
- Increment option: Add N seconds after each move

| Time Control | Initial | Increment |
|-------------|---------|-----------|
| Bullet      | 1:00    | 0         |
| Blitz       | 5:00    | 0         |
| Rapid       | 10:00   | 5s        |
| Classical   | 30:00   | 10s       |
| None        | ∞       | N/A       |

## 12. Sound Effects

| Event          | Sound Description          |
|----------------|---------------------------|
| Move           | Soft "click" or "tap"      |
| Capture        | Slightly louder "clack"    |
| Check          | Alert tone                 |
| Checkmate      | Victory/defeat fanfare     |
| Castling       | Double "click"             |
| Illegal move   | Error buzz                 |
| Game start     | Brief chime                |

## 13. Keyboard Shortcuts

| Key         | Action                    |
|-------------|---------------------------|
| Ctrl+Z      | Undo last move            |
| Ctrl+N      | New game                  |
| Ctrl+S      | Save game                 |
| Ctrl+F      | Flip board                |
| Escape      | Deselect piece            |
| Arrow keys  | Navigate move history     |

## 14. Save/Load System

Games saved in PGN (Portable Game Notation) format:

```
[Event "Human vs AI"]
[Site "Digital Chess"]
[Date "2025.01.01"]
[White "Human"]
[Black "AI (Medium)"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 1-0
```

## 15. Data Structures (Implementation Guidance)

### 15.1 Board Representation
Use an 8x8 array or bitboard representation:
- Array: board[row][col] where each cell is null or {type, color}
- Bitboard: 12 64-bit integers (one per piece type per color) for faster move generation

### 15.2 Move Representation
```
Move {
    from: Square       // source square (0-63 or {row, col})
    to: Square         // destination square
    piece: PieceType   // piece being moved
    captured: PieceType | null  // piece captured (if any)
    promotion: PieceType | null // promotion piece (if pawn promotion)
    flags: {
        castleKingside: boolean
        castleQueenside: boolean
        enPassant: boolean
        doublePawnPush: boolean
    }
}
```

### 15.3 Legal Move Generation
For each piece, generate all pseudo-legal moves, then filter out moves that
leave the own King in check:

```
function generateLegalMoves(position):
    pseudoMoves = generatePseudoLegalMoves(position)
    legalMoves = []
    for move in pseudoMoves:
        makeMove(move)
        if not isKingInCheck(position.activeColor):
            legalMoves.append(move)
        unmakeMove(move)
    return legalMoves
```

## 16. Testing Requirements

The implementation should pass these test scenarios:

1. **Scholar's Mate**: 1.e4 e5 2.Bc4 Nc6 3.Qh5 Nf6 4.Qxf7# — White wins by checkmate
2. **Fool's Mate**: 1.f3 e5 2.g4 Qh4# — Black wins by checkmate
3. **Stalemate**: King with no legal moves and not in check results in draw
4. **Castling blocked by check**: Cannot castle through or out of check
5. **En Passant**: Correctly captures and removes opponent pawn
6. **Promotion**: Pawn reaching 8th rank must promote
7. **Insufficient material**: K vs K, K+B vs K, K+N vs K are draws
8. **Pin detection**: Pinned pieces cannot move (except along the pin line)
9. **Discovered check**: Moving a piece reveals check from another piece

## 17. Performance Requirements

| Metric                     | Target             |
|----------------------------|---------------------|
| Move generation            | < 10ms              |
| AI move (Easy)             | < 500ms             |
| AI move (Medium)           | < 2 seconds         |
| AI move (Hard)             | < 5 seconds         |
| AI move (Expert)           | < 10 seconds        |
| Board render               | < 16ms (60 FPS)     |
| Legal move validation      | < 1ms               |

## 18. Accessibility

- High contrast mode option for board colors
- Piece labels (text overlays showing piece letters)
- Screen reader support: announce moves in algebraic notation
- Color-blind friendly: use patterns in addition to colors for square distinction
- Keyboard-only navigation: arrow keys to select squares, Enter to confirm

## 19. Error Handling

| Error Condition              | Response                          |
|-----------------------------|-----------------------------------|
| Click on empty square       | Ignore (no selection)             |
| Click on opponent's piece   | Ignore or show "Not your piece"   |
| Illegal move attempt        | Highlight square red, show message|
| AI search timeout           | Return best move found so far     |
| Corrupted save file         | Show error, offer to start new    |
| Timer expired               | End game, opponent wins on time   |
