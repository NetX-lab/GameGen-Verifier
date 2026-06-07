# Solitaire (Klondike) — Complete Game Specification

## 1. Game Overview

Klondike Solitaire is the most popular single-player card game. The player arranges
a standard 52-card deck into four foundation piles (one per suit, Ace to King) by
manipulating cards across seven tableau columns and a stock/waste pile.

- **Players**: 1 (single-player, no AI opponent)
- **Deck**: Standard 52-card deck (no jokers)
- **Objective**: Move all 52 cards to the four foundation piles
- **Win rate**: Approximately 79% of deals are solvable; typical win rate ~30% for average players
- **Variants**: Draw-1 (easier) and Draw-3 (standard)

## 2. Technical Foundation

### 2.1 Card Definitions

**Suits (4):**

| Suit     | Symbol | Color |
|----------|--------|-------|
| Hearts   | ♥      | Red   |
| Diamonds | ♦      | Red   |
| Clubs    | ♣      | Black |
| Spades   | ♠      | Black |

**Ranks (13, per suit):**

| Rank  | Value | Display |
|-------|-------|---------|
| Ace   | 1     | A       |
| Two   | 2     | 2       |
| Three | 3     | 3       |
| Four  | 4     | 4       |
| Five  | 5     | 5       |
| Six   | 6     | 6       |
| Seven | 7     | 7       |
| Eight | 8     | 8       |
| Nine  | 9     | 9       |
| Ten   | 10    | 10      |
| Jack  | 11    | J       |
| Queen | 12    | Q       |
| King  | 13    | K       |

**Total Cards**: 4 suits x 13 ranks = 52 cards

### 2.2 Card Representation

```
Card {
    suit: HEARTS | DIAMONDS | CLUBS | SPADES
    rank: 1-13 (Ace=1, Jack=11, Queen=12, King=13)
    faceUp: boolean
    color: RED | BLACK  // derived from suit
}
```

## 3. Game Layout

### 3.1 Layout Diagram (ASCII)

```
+------------------------------------------------------------------+
|                                                                  |
|  [STOCK]  [WASTE]      [♠ F1] [♥ F2] [♦ F3] [♣ F4]             |
|  +----+   +----+       +----+ +----+ +----+ +----+              |
|  |////|   | 5♥ |       | A♠ | |    | |    | |    |              |
|  |////|   +----+       +----+ +----+ +----+ +----+              |
|  +----+                                                          |
|                                                                  |
|    T1      T2      T3      T4      T5      T6      T7          |
|  +----+  +----+  +----+  +----+  +----+  +----+  +----+        |
|  | K♠ |  |////|  |////|  |////|  |////|  |////|  |////|        |
|  +----+  +----+  +----+  +----+  +----+  +----+  +----+        |
|          | J♦ |  |////|  |////|  |////|  |////|  |////|        |
|          +----+  +----+  +----+  +----+  +----+  +----+        |
|                  | 9♣ |  |////|  |////|  |////|  |////|        |
|                  +----+  +----+  +----+  +----+  +----+        |
|                          | 7♥ |  |////|  |////|  |////|        |
|                          +----+  +----+  +----+  +----+        |
|                                  | 5♠ |  |////|  |////|        |
|                                  +----+  +----+  +----+        |
|                                          | 3♦ |  |////|        |
|                                          +----+  +----+        |
|                                                  | A♣ |        |
|                                                  +----+        |
|                                                                  |
|  Legend: //// = face-down card                                   |
+------------------------------------------------------------------+
```

### 3.2 Areas

| Area          | Location          | Description                           |
|---------------|-------------------|---------------------------------------|
| Stock         | Top-left          | Remaining undealt cards (face down)   |
| Waste         | Next to stock     | Cards drawn from stock (face up)      |
| Foundations   | Top-right (4)     | Build Ace to King per suit            |
| Tableau       | Bottom (7 cols)   | Main play area, columns 1-7          |

## 4. Initial Deal

### 4.1 Dealing Process

1. Shuffle the 52-card deck
2. Deal cards to the 7 tableau columns:
   - Column 1: 1 card (face up)
   - Column 2: 2 cards (1 face down + 1 face up)
   - Column 3: 3 cards (2 face down + 1 face up)
   - Column 4: 4 cards (3 face down + 1 face up)
   - Column 5: 5 cards (4 face down + 1 face up)
   - Column 6: 6 cards (5 face down + 1 face up)
   - Column 7: 7 cards (6 face down + 1 face up)
3. Total dealt to tableau: 28 cards (7 face up, 21 face down)
4. Remaining 24 cards go to the stock pile (face down)

### 4.2 Card Count Summary

| Area          | Cards  | Face Up | Face Down |
|---------------|--------|---------|-----------|
| Tableau       | 28     | 7       | 21        |
| Stock         | 24     | 0       | 24        |
| Waste         | 0      | 0       | 0         |
| Foundations   | 0      | 0       | 0         |
| **Total**     | **52** | **7**   | **45**    |

## 5. Rules of Play

### 5.1 Tableau Rules

**Building on tableau columns:**
- Cards are placed in descending rank order
- Cards must alternate colors (red on black, black on red)
- Example valid sequence: K♠, Q♥, J♣, 10♦, 9♠, 8♥, 7♣...
- Only Kings can be placed on empty tableau columns
- Multiple face-up cards can be moved as a group if they form a valid sequence

**Revealing cards:**
- When a face-down card is exposed (all cards above it removed), it is automatically turned face up

### 5.2 Foundation Rules

**Building on foundations:**
- Each foundation starts with an Ace
- Cards are placed in ascending rank order within the same suit
- Order: A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K
- Each foundation holds exactly one suit
- Cards cannot be moved back from foundations (in standard rules)
- Optional rule: Allow moving cards back from foundations to tableau

### 5.3 Stock and Waste Rules

**Draw-1 mode:**
- Click stock to draw 1 card to the waste pile (face up)
- Only the top waste card is playable
- When stock is empty, turn the entire waste pile over to become the new stock
- Unlimited stock recycling

**Draw-3 mode (standard):**
- Click stock to draw 3 cards to the waste pile
- Only the top card of the waste is playable
- If fewer than 3 cards remain in stock, draw all remaining
- When stock is empty, turn the entire waste pile over (maintaining order)
- Unlimited stock recycling (or limit to 3 passes for harder variant)

### 5.4 Move Types

| Move Type               | From          | To           | Rule                          |
|--------------------------|---------------|--------------|-------------------------------|
| Tableau to Tableau       | Tableau col   | Tableau col  | Descending, alternating color |
| Tableau to Foundation    | Tableau top   | Foundation   | Ascending, same suit          |
| Waste to Tableau         | Waste top     | Tableau col  | Descending, alternating color |
| Waste to Foundation      | Waste top     | Foundation   | Ascending, same suit          |
| Foundation to Tableau    | Foundation top| Tableau col  | (Optional) Descending, alt color |
| Stock to Waste           | Stock top     | Waste        | Draw 1 or 3 cards             |
| Recycle Waste to Stock   | Waste (all)   | Stock        | Flip entire waste pile        |

### 5.5 Moving Sequences

When moving cards within the tableau:
- Any face-up card and all cards on top of it can be moved as a group
- The bottom card of the group must be placeable on the destination column
- The group must form a valid descending, alternating-color sequence

Example:
```
Source column: [////] [////] [J♠] [10♥] [9♣]
                              ^^^^^^^^^^^^^^^^^^^
                              This group can move

Destination column: [...] [Q♦]

Valid: J♠ (black) on Q♦ (red), descending. Entire group moves.
```

## 6. Win and Loss Conditions

### 6.1 Win
- All 52 cards are moved to the four foundation piles
- Each foundation has a complete suit from Ace to King
- The tableau, stock, and waste are all empty

### 6.2 Loss (No Moves Remaining)
- No legal moves are available
- Stock is empty (or recycling limit reached)
- The game is stuck — player must start a new game or undo

### 6.3 Auto-Complete
- When all remaining cards are face up (no face-down cards in tableau),
  the game can be auto-completed
- Automatically move all cards to foundations in the correct order
- Show a rapid card-flying animation

## 7. Scoring Systems

### 7.1 Standard Scoring

| Action                        | Points     |
|-------------------------------|------------|
| Waste to Tableau              | +5         |
| Waste to Foundation           | +10        |
| Tableau to Foundation         | +10        |
| Turn over tableau card        | +5         |
| Foundation to Tableau         | -15        |
| Recycle waste (Draw-3 only)   | -20        |

### 7.2 Vegas Scoring

| Action                        | Points     |
|-------------------------------|------------|
| Initial cost                  | -$52       |
| Card to Foundation            | +$5        |
| Maximum per game              | +$260 (52 x $5) |
| Net max profit                | +$208      |

- Stock recycling limited to 1 pass (Draw-1) or 3 passes (Draw-3)
- No undo allowed in Vegas mode

### 7.3 Time Bonus (Standard)

```
Time Bonus = max(0, 700000 / time_in_seconds)
```

Added to the final score if the game is won. Encourages faster play.

## 8. Game State

| State Variable         | Type              | Description                          |
|------------------------|-------------------|--------------------------------------|
| stock                  | list of Card      | Face-down cards in stock             |
| waste                  | list of Card      | Face-up cards in waste               |
| foundations[4]         | list of Card      | Each foundation pile                 |
| tableau[7]             | list of Card      | Each tableau column                  |
| score                  | integer           | Current score                        |
| moves                  | integer           | Move counter                         |
| elapsedTime            | seconds           | Game timer                           |
| drawMode               | 1 or 3            | Cards drawn per stock click          |
| stockRecycles           | integer           | Number of times stock was recycled   |
| undoStack              | list of GameState | For undo functionality               |
| gameWon                | boolean           | Whether the game is won              |

## 9. User Interface

### 9.1 Main Game Screen

```
+------------------------------------------------------------------+
|  SOLITAIRE (Klondike)         Score: 145   Time: 04:32   Moves: 47|
+------------------------------------------------------------------+
|                                                                  |
|  +------+  +------+     +------+ +------+ +------+ +------+     |
|  |//////|  |  5   |     |  A   | |      | |      | |      |     |
|  |//////|  |  ♥   |     |  ♠   | |  ♥   | |  ♦   | |  ♣   |     |
|  |//////|  |      |     |      | |      | |      | |      |     |
|  +------+  +------+     +------+ +------+ +------+ +------+     |
|   Stock     Waste        Foundation 1-4                          |
|   (18)                                                           |
|                                                                  |
|  +------+ +------+ +------+ +------+ +------+ +------+ +------+ |
|  |  K   | |//////| |//////| |//////| |//////| |//////| |//////| |
|  |  ♠   | |//////| |//////| |//////| |//////| |//////| |//////| |
|  +------+ +------+ +------+ +------+ +------+ +------+ +------+ |
|           |  J   | |//////| |//////| |//////| |//////| |//////| |
|           |  ♦   | |//////| |//////| |//////| |//////| |//////| |
|           +------+ +------+ +------+ +------+ +------+ +------+ |
|                    |  9   | |//////| |//////| |//////| |//////| |
|                    |  ♣   | |//////| |//////| |//////| |//////| |
|                    +------+ +------+ +------+ +------+ +------+ |
|                             |  7   | |//////| |//////| |//////| |
|                             |  ♥   | |//////| |//////| |//////| |
|                             +------+ +------+ +------+ +------+ |
|                                      |  5   | |//////| |//////| |
|                                      |  ♠   | |//////| |//////| |
|                                      +------+ +------+ +------+ |
|                                               |  3   | |//////| |
|                                               |  ♦   | |//////| |
|                                               +------+ +------+ |
|                                                        |  A   | |
|                                                        |  ♣   | |
|                                                        +------+ |
|                                                                  |
+------------------------------------------------------------------+
|  [Undo] [New Game] [Hint] [Auto-Complete] [Settings]             |
+------------------------------------------------------------------+
```

### 9.2 Interaction Model

**Clicking Stock:**
- Draws 1 or 3 cards to the waste pile
- If stock is empty, recycles waste to stock

**Moving Cards:**
- Click a card to select it, then click the destination
- Or: drag and drop cards
- Double-click a card to auto-move it to the foundation (if valid)
- Double-click or right-click for auto-play

**Visual Feedback:**
- Selected card(s) highlighted with a border
- Valid drop targets highlighted in green
- Invalid drops snap the card back to its original position
- Cards being dragged are semi-transparent at source

### 9.3 Card Appearance

```
Face-up card:        Face-down card:
+--------+           +--------+
|  10    |           |////////|
|  ♥     |           |////////|
|        |           |////////|
|     ♥  |           |////////|
|    10  |           |////////|
+--------+           +--------+
```

### 9.4 Auto-Complete Trigger
When all tableau cards are face up, display:
```
+---------------------------+
|  All cards revealed!      |
|                           |
|  [Auto-Complete]          |
|  [Continue Playing]       |
+---------------------------+
```

## 10. Game Flow

### 10.1 New Game

```
+---------------------------+
|     NEW SOLITAIRE GAME    |
|                           |
|  Draw Mode:               |
|  (•) Draw 1 (easier)     |
|  ( ) Draw 3 (standard)   |
|                           |
|  Scoring:                 |
|  (•) Standard             |
|  ( ) Vegas                |
|  ( ) None                 |
|                           |
|  Allow Undo: [Yes]        |
|  Timed: [Yes]             |
|                           |
|  [Deal New Game]          |
|  [Choose Game #]          |
+---------------------------+
```

### 10.2 Game Numbered Deals
- Each deal is seeded with a number (1-1000000+)
- Players can replay the same deal by entering its number
- This allows comparing strategies on the same layout

### 10.3 Win Screen

```
+----------------------------------+
|         YOU WIN!                 |
|                                  |
|  Score: 735                      |
|  Time: 06:12                     |
|  Moves: 89                      |
|  Time Bonus: +112               |
|  Final Score: 847               |
|                                  |
|  [Play Again] [New Game] [Stats] |
+----------------------------------+
```

### 10.4 Win Animation
- Cards cascade off the foundation piles
- Cards bounce around the screen
- Fireworks or particle effects
- Classic "card waterfall" animation

## 11. Hint System

### 11.1 Hint Priority

When the player requests a hint, suggest moves in this order:

1. Move Ace to empty foundation
2. Move 2 to foundation (if Ace is there)
3. Move card from waste to foundation
4. Move card from tableau to foundation
5. Reveal a face-down card (move cards to enable flip)
6. Move card from waste to tableau
7. Move sequence between tableau columns to reveal face-down cards
8. Draw from stock

### 11.2 Hint Display
- Highlight the source card and destination with arrows
- Show for 3 seconds or until clicked
- If no hints available: "No moves available. Draw from stock or undo."

## 12. Undo System

- Unlimited undo (standard mode)
- No undo (Vegas mode)
- Each action is stored in the undo stack:
  - Card moves (from, to, face state)
  - Stock draws (which cards were drawn)
  - Stock recycles

```
UndoAction {
    type: MOVE | DRAW | RECYCLE
    cards: [Card]
    from: area
    to: area
    previousState: partial game state
}
```

## 13. Sound Effects

| Event                 | Sound                          |
|-----------------------|--------------------------------|
| Draw from stock       | Card flip sound                |
| Place card            | Soft "snap"                    |
| Invalid move          | Soft error/thud                |
| Card to foundation    | Satisfying "click"             |
| Turn over tableau card| Card flip                      |
| Auto-complete         | Rapid card flipping sounds     |
| Win                   | Victory fanfare + cards cascade|
| Stock empty           | Shuffle sound (recycle)        |
| Undo                  | Reverse swoosh                 |

## 14. Settings

| Setting              | Options                          | Default    |
|----------------------|----------------------------------|------------|
| Draw mode            | Draw 1, Draw 3                  | Draw 1     |
| Scoring              | Standard, Vegas, None           | Standard   |
| Card back design     | Classic, Geometric, Abstract    | Classic    |
| Card face style      | Standard, Large print, Modern   | Standard   |
| Background color     | Green, Blue, Red, Custom        | Green      |
| Animation speed      | Slow, Normal, Fast              | Normal     |
| Auto-play to foundation | On/Off                       | Off        |
| Sound effects        | On/Off                          | On         |
| Show timer           | On/Off                          | On         |
| Show move count      | On/Off                          | On         |
| Allow undo           | On/Off                          | On         |
| Right-click auto-play| On/Off                          | On         |

## 15. Statistics Tracking

| Statistic              | Description                     |
|------------------------|---------------------------------|
| Games played           | Total across all modes          |
| Games won              | Total wins                      |
| Win percentage         | Won / played                    |
| Current win streak     | Consecutive wins                |
| Best win streak        | All-time record                 |
| Best score             | Highest score achieved          |
| Best time              | Fastest win                     |
| Fewest moves           | Win with fewest moves           |
| Average score          | Mean score across wins          |
| Average time           | Mean time across wins           |
| Average moves          | Mean moves across wins          |
| Games played (Draw 1)  | Separate per mode               |
| Games played (Draw 3)  | Separate per mode               |

## 16. Data Structures

### 16.1 Card

```
Card {
    suit: enum (HEARTS, DIAMONDS, CLUBS, SPADES)
    rank: integer (1-13)
    faceUp: boolean
    color: RED | BLACK  // derived: Hearts/Diamonds = RED, Clubs/Spades = BLACK
}
```

### 16.2 Game State

```
GameState {
    stock: Stack<Card>
    waste: Stack<Card>
    foundations: [Stack<Card>; 4]
    tableau: [List<Card>; 7]  // each column is a list, bottom to top
    score: integer
    moves: integer
    elapsed: Duration
    undoStack: Stack<UndoAction>
}
```

### 16.3 Shuffle Algorithm (Fisher-Yates)

```
function shuffle(deck):
    for i from 51 down to 1:
        j = random integer from 0 to i (inclusive)
        swap(deck[i], deck[j])
    return deck
```

### 16.4 Seeded Random for Numbered Deals

```
function seededShuffle(deck, seed):
    rng = SeededRandom(seed)
    for i from 51 down to 1:
        j = rng.nextInt(0, i)
        swap(deck[i], deck[j])
    return deck
```

## 17. Move Validation

```
function isValidTableauMove(card, destinationColumn):
    if destinationColumn is empty:
        return card.rank == 13  // only Kings on empty columns
    topCard = destinationColumn.top()
    return card.rank == topCard.rank - 1
           and card.color != topCard.color

function isValidFoundationMove(card, foundationPile):
    if foundationPile is empty:
        return card.rank == 1  // only Aces on empty foundations
    topCard = foundationPile.top()
    return card.suit == topCard.suit
           and card.rank == topCard.rank + 1
```

## 18. Testing Scenarios

1. **Deal correctly**: 28 cards in tableau (7 face up), 24 in stock
2. **Ace to foundation**: Ace moves to empty foundation
3. **Build on foundation**: 2 moves onto Ace of same suit
4. **Tableau alternating color**: Red on black, black on red
5. **King to empty column**: Only King can go on empty tableau column
6. **Sequence move**: Group of valid cards moves together
7. **Invalid move rejected**: Wrong color or rank rejected
8. **Reveal face-down card**: Automatically flips when exposed
9. **Stock draw 1**: Draws exactly 1 card
10. **Stock draw 3**: Draws exactly 3 cards (or fewer if less remain)
11. **Stock recycle**: Empty stock reloads from waste
12. **Win detection**: All 52 cards on foundations triggers win
13. **Auto-complete**: Works when all cards face up
14. **Undo**: Correctly reverses any action
15. **No moves detection**: Correctly identifies stuck state

## 19. Performance Requirements

| Metric                     | Target             |
|----------------------------|---------------------|
| Card render                | < 1ms per card     |
| Full board render          | < 16ms (60 FPS)   |
| Move validation            | < 1ms              |
| Hint computation           | < 100ms            |
| Auto-complete animation    | 60 FPS             |
| Shuffle + deal             | < 10ms             |
| Undo operation             | < 1ms              |

## 20. Accessibility

- Large card option for readability
- Color-blind mode: add suit symbols prominently, use patterns
- Keyboard navigation: Tab between areas, arrow keys within
- Screen reader: announce card rank, suit, and location
- Double-click shortcut for auto-foundation
- Right-click context menu for move options
- High contrast card faces
