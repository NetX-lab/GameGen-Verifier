# Blackjack (21) — Complete Game Specification

## 1. Game Overview

Blackjack (also known as Twenty-One) is a casino card game where the player competes
against the dealer (AI). The goal is to get a hand value as close to 21 as possible
without exceeding it, while beating the dealer's hand.

- **Players**: 1 Human vs 1 AI Dealer
- **Deck**: 1-8 standard 52-card decks (default: 6 decks)
- **Objective**: Beat the dealer by having a hand value closer to 21 without busting
- **House Edge**: ~0.5% with basic strategy (varies by rules)

## 2. Technical Foundation

### 2.1 Card Values

| Card     | Value     | Notes                                    |
|----------|-----------|------------------------------------------|
| 2        | 2         | Fixed value                              |
| 3        | 3         | Fixed value                              |
| 4        | 4         | Fixed value                              |
| 5        | 5         | Fixed value                              |
| 6        | 6         | Fixed value                              |
| 7        | 7         | Fixed value                              |
| 8        | 8         | Fixed value                              |
| 9        | 9         | Fixed value                              |
| 10       | 10        | Fixed value                              |
| Jack (J) | 10        | Face card                                |
| Queen (Q)| 10        | Face card                                |
| King (K) | 10        | Face card                                |
| Ace (A)  | 1 or 11   | Soft value = 11, Hard value = 1          |

### 2.2 Hand Value Calculation

```
function handValue(cards):
    total = 0
    aceCount = 0

    for card in cards:
        if card.rank == ACE:
            aceCount += 1
            total += 11
        elif card.rank in [JACK, QUEEN, KING]:
            total += 10
        else:
            total += card.rank

    // Reduce Aces from 11 to 1 as needed
    while total > 21 and aceCount > 0:
        total -= 10
        aceCount -= 1

    return total
```

### 2.3 Hand Types

| Hand Type      | Definition                           | Example          |
|---------------|--------------------------------------|------------------|
| Hard hand      | No Ace, or all Aces count as 1      | 10+7 = 17        |
| Soft hand      | At least one Ace counts as 11       | A+6 = soft 17    |
| Blackjack      | Ace + 10-value card on initial deal | A+K = 21 (BJ)    |
| Bust           | Hand value exceeds 21               | 10+8+5 = 23 BUST |
| Push           | Player and dealer have same value   | Both have 18     |

## 3. Game Rules

### 3.1 Initial Deal
1. Player places a bet
2. Dealer deals two cards to the player (both face up)
3. Dealer deals two cards to themselves (one face up, one face down — "hole card")

### 3.2 Natural Blackjack
- If player's initial two cards total 21 (Ace + 10-value), it's a "Blackjack"
- If dealer also has Blackjack: Push (bet returned)
- If dealer doesn't have Blackjack: Player wins, typically paid 3:2

### 3.3 Insurance
- If dealer's face-up card is an Ace, player is offered "Insurance"
- Insurance costs half the original bet
- If dealer has Blackjack: Insurance pays 2:1
- If dealer doesn't: Insurance bet is lost
- Insurance is generally a bad bet for the player

### 3.4 Player Actions

| Action     | Condition                               | Effect                          |
|------------|----------------------------------------|----------------------------------|
| Hit        | Hand < 21                              | Receive one more card            |
| Stand      | Any time                               | End turn, keep current hand      |
| Double Down| Initial two cards only (some variants)  | Double bet, receive exactly 1 card, then stand |
| Split      | Initial two cards of same rank          | Split into two separate hands, each gets 1 new card |
| Surrender  | Initial two cards only (if allowed)    | Forfeit half the bet, hand ends  |

### 3.5 Splitting Rules
- Split only on initial deal when both cards have the same rank
- Each split hand receives one additional card
- Player plays each hand independently
- May split up to 3 times (creating up to 4 hands) — configurable
- Aces: when splitting Aces, each hand receives only one card and cannot hit further
- Blackjack after split pays 1:1 (not 3:2) — house rule variant

### 3.6 Double Down Rules
- Player doubles their bet and receives exactly one more card
- Available on initial two cards (some variants allow on any hand)
- After receiving the card, player must stand
- Double after split: allowed in most variants

### 3.7 Dealer Rules
The dealer follows fixed rules (no decisions):
1. Dealer reveals hole card
2. Dealer hits on 16 or less
3. Dealer stands on 17 or more
4. **Soft 17 rule** (configurable):
   - H17: Dealer HITS on soft 17 (slightly favors house)
   - S17: Dealer STANDS on soft 17 (standard)

```
function dealerPlay(hand):
    while true:
        value = handValue(hand)
        if value > 21:
            return BUST
        if value > 17:
            return STAND
        if value == 17:
            if isSoft(hand) and DEALER_HITS_SOFT_17:
                hit(hand)
            else:
                return STAND
        else:
            hit(hand)
```

## 4. Betting System

### 4.1 Chip Values

| Chip Color  | Value    |
|-------------|----------|
| White       | $1       |
| Red         | $5       |
| Green       | $25      |
| Black       | $100     |
| Purple      | $500     |
| Orange      | $1,000   |

### 4.2 Table Limits

| Setting      | Min Bet  | Max Bet   |
|-------------|----------|-----------|
| Low stakes   | $1       | $100      |
| Medium       | $5       | $500      |
| High stakes  | $25      | $5,000    |
| VIP          | $100     | $10,000   |

### 4.3 Starting Balance
Default: $1,000 (configurable)

### 4.4 Payout Table

| Outcome                      | Payout        |
|------------------------------|---------------|
| Player Blackjack             | 3:2 ($15 on $10 bet) |
| Player wins (no BJ)         | 1:1 ($10 on $10 bet) |
| Push (tie)                   | 0 (bet returned)     |
| Player loses                 | -1:1 (lose bet)      |
| Insurance win                | 2:1                  |
| Surrender                    | -0.5:1 (lose half)   |

### 4.5 Payout Variant: 6:5 Blackjack
Some tables pay 6:5 instead of 3:2 for Blackjack (worse for player):
- 3:2 payout on $10 bet = $15
- 6:5 payout on $10 bet = $12

## 5. Game State

| State Variable         | Type              | Description                          |
|------------------------|-------------------|--------------------------------------|
| shoe                   | list of Card      | Remaining cards in the shoe          |
| playerHands            | list of Hand      | Player's hand(s) — may have multiples after split |
| dealerHand             | Hand              | Dealer's hand                        |
| activeHandIndex        | integer           | Which player hand is active          |
| bets                   | list of int       | Bet amount for each hand             |
| playerBalance          | integer           | Player's chip balance                |
| phase                  | enum              | BETTING, DEALING, PLAYER_TURN, DEALER_TURN, RESOLUTION |
| insuranceBet           | integer           | Insurance bet amount (0 if none)     |
| roundHistory           | list              | History of all rounds                |
| decksInShoe            | integer           | Number of decks used                 |
| cutCardPosition        | integer           | When to reshuffle (e.g., 75% through)|
| handsPlayed            | integer           | Total hands played                   |
| runningCount           | integer           | Card counting running count          |

### 5.1 Hand Data Structure

```
Hand {
    cards: [Card]
    bet: integer
    status: PLAYING | STANDING | BUSTED | BLACKJACK | SURRENDERED
    isDoubledDown: boolean
    isSplit: boolean
    value: integer       // computed
    isSoft: boolean      // computed
}
```

## 6. Shoe and Shuffling

### 6.1 Multi-Deck Shoe

| Number of Decks | Total Cards | House Edge Impact |
|----------------|-------------|-------------------|
| 1              | 52          | Lowest house edge |
| 2              | 104         | Low               |
| 4              | 208         | Medium            |
| 6 (standard)   | 312         | Standard          |
| 8              | 416         | Highest           |

### 6.2 Cut Card
- A cut card is placed at approximately 75% depth in the shoe
- When the cut card is reached, the current round finishes
- The shoe is reshuffled before the next round
- This prevents card counting from being fully effective

### 6.3 Shuffle Algorithm
```
function createShoe(numDecks):
    shoe = []
    for d in 1..numDecks:
        for suit in [HEARTS, DIAMONDS, CLUBS, SPADES]:
            for rank in 1..13:
                shoe.append(Card(suit, rank))
    fisherYatesShuffle(shoe)
    return shoe
```

## 7. AI Dealer Behavior

The dealer is not an "AI opponent" making strategic decisions — it follows a fixed
algorithm. However, the game provides AI-assisted features:

### 7.1 Basic Strategy Advisor

The game can display optimal basic strategy recommendations:

**Hard Totals (no Ace counting as 11):**

| Player Hand | Dealer 2 | Dealer 3 | Dealer 4 | Dealer 5 | Dealer 6 | Dealer 7 | Dealer 8 | Dealer 9 | Dealer 10| Dealer A |
|-------------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|
| 8 or less   | H        | H        | H        | H        | H        | H        | H        | H        | H        | H        |
| 9           | H        | D        | D        | D        | D        | H        | H        | H        | H        | H        |
| 10          | D        | D        | D        | D        | D        | D        | D        | D        | H        | H        |
| 11          | D        | D        | D        | D        | D        | D        | D        | D        | D        | D        |
| 12          | H        | H        | S        | S        | S        | H        | H        | H        | H        | H        |
| 13          | S        | S        | S        | S        | S        | H        | H        | H        | H        | H        |
| 14          | S        | S        | S        | S        | S        | H        | H        | H        | H        | H        |
| 15          | S        | S        | S        | S        | S        | H        | H        | H        | R/H      | R/H      |
| 16          | S        | S        | S        | S        | S        | H        | H        | R/H      | R/H      | R/H      |
| 17+         | S        | S        | S        | S        | S        | S        | S        | S        | S        | S        |

**Key: H=Hit, S=Stand, D=Double, R=Surrender**

**Soft Totals (Ace counting as 11):**

| Player Hand | Dealer 2 | Dealer 3 | Dealer 4 | Dealer 5 | Dealer 6 | Dealer 7 | Dealer 8 | Dealer 9 | Dealer 10| Dealer A |
|-------------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|
| A,2 (13)    | H        | H        | H        | D        | D        | H        | H        | H        | H        | H        |
| A,3 (14)    | H        | H        | H        | D        | D        | H        | H        | H        | H        | H        |
| A,4 (15)    | H        | H        | D        | D        | D        | H        | H        | H        | H        | H        |
| A,5 (16)    | H        | H        | D        | D        | D        | H        | H        | H        | H        | H        |
| A,6 (17)    | H        | D        | D        | D        | D        | H        | H        | H        | H        | H        |
| A,7 (18)    | D/S      | D/S      | D/S      | D/S      | D/S      | S        | S        | H        | H        | H        |
| A,8 (19)    | S        | S        | S        | S        | D/S      | S        | S        | S        | S        | S        |
| A,9 (20)    | S        | S        | S        | S        | S        | S        | S        | S        | S        | S        |

**Pair Splitting:**

| Pair   | Dealer 2 | Dealer 3 | Dealer 4 | Dealer 5 | Dealer 6 | Dealer 7 | Dealer 8 | Dealer 9 | Dealer 10| Dealer A |
|--------|----------|----------|----------|----------|----------|----------|----------|----------|----------|----------|
| A,A    | SP       | SP       | SP       | SP       | SP       | SP       | SP       | SP       | SP       | SP       |
| 10,10  | S        | S        | S        | S        | S        | S        | S        | S        | S        | S        |
| 9,9    | SP       | SP       | SP       | SP       | SP       | S        | SP       | SP       | S        | S        |
| 8,8    | SP       | SP       | SP       | SP       | SP       | SP       | SP       | SP       | SP       | R/SP     |
| 7,7    | SP       | SP       | SP       | SP       | SP       | SP       | H        | H        | H        | H        |
| 6,6    | SP       | SP       | SP       | SP       | SP       | H        | H        | H        | H        | H        |
| 5,5    | D        | D        | D        | D        | D        | D        | D        | D        | H        | H        |
| 4,4    | H        | H        | H        | SP       | SP       | H        | H        | H        | H        | H        |
| 3,3    | SP       | SP       | SP       | SP       | SP       | SP       | H        | H        | H        | H        |
| 2,2    | SP       | SP       | SP       | SP       | SP       | SP       | H        | H        | H        | H        |

**Key: SP=Split, H=Hit, S=Stand, D=Double, R=Surrender**

### 7.2 Strategy Advisor Display

When enabled, show the recommended action before the player decides:
```
+-----------------------------------+
|  Recommended: STAND               |
|  Your hand: 18 (hard)            |
|  Dealer shows: 6                  |
|  Reason: Dealer likely busts      |
+-----------------------------------+
```

## 8. User Interface

### 8.1 Main Game Screen

```
+------------------------------------------------------------------+
|  BLACKJACK                         Balance: $1,450               |
+------------------------------------------------------------------+
|                                                                  |
|                    DEALER                                        |
|              +------+  +------+                                  |
|              |  7   |  |//////|                                  |
|              |  ♣   |  |//////|   Dealer: 7 + ?                  |
|              +------+  +------+                                  |
|                                                                  |
|  ============================================================== |
|                                                                  |
|                    PLAYER                                        |
|              +------+  +------+                                  |
|              |  K   |  |  5   |                                  |
|              |  ♠   |  |  ♥   |   Your hand: 15                  |
|              +------+  +------+                                  |
|                                                                  |
|                    Bet: $25                                       |
|                                                                  |
|  [HIT] [STAND] [DOUBLE DOWN] [SURRENDER]                        |
|                                                                  |
+------------------------------------------------------------------+
|  Shoe: 234/312 cards    Hands played: 14    [Settings]           |
+------------------------------------------------------------------+
```

### 8.2 Betting Screen

```
+------------------------------------------------------------------+
|  PLACE YOUR BET                      Balance: $1,450             |
+------------------------------------------------------------------+
|                                                                  |
|  Chip values:                                                    |
|  [  $1 ] [ $5  ] [ $25 ] [ $100] [ $500]                       |
|                                                                  |
|  Current bet: $25                                                |
|                                                                  |
|  +---+---+---+                                                   |
|  |$25|   |   |  Click chips to add to bet                       |
|  +---+---+---+                                                   |
|                                                                  |
|  [Clear Bet] [Repeat Last ($25)] [DEAL]                         |
|                                                                  |
+------------------------------------------------------------------+
```

### 8.3 Split Hand Display

```
+------------------------------------------------------------------+
|                    DEALER                                        |
|              +------+  +------+                                  |
|              |  10  |  |  6   |   Dealer: 16                     |
|              |  ♦   |  |  ♣   |                                  |
|              +------+  +------+                                  |
|                                                                  |
|  ============================================================== |
|                                                                  |
|       HAND 1 ($25)              HAND 2 ($25)                    |
|   +------+  +------+       +------+  +------+                   |
|   |  8   |  |  3   |       |  8   |  |  K   |                   |
|   |  ♠   |  |  ♥   |       |  ♠   |  |  ♦   |                   |
|   +------+  +------+       +------+  +------+                   |
|   Value: 11                 Value: 18  STANDING                  |
|   >> ACTIVE <<                                                   |
|                                                                  |
|  [HIT] [STAND] [DOUBLE DOWN]                                    |
+------------------------------------------------------------------+
```

### 8.4 Round Resolution

```
+------------------------------------------------------------------+
|  ROUND RESULT                                                    |
+------------------------------------------------------------------+
|                                                                  |
|  Dealer: 7♣ 10♦ = 17                                            |
|                                                                  |
|  Your hand: K♠ 9♥ = 19    WIN!    +$25                          |
|                                                                  |
|  Balance: $1,475 (+$25)                                         |
|                                                                  |
|  [Deal Again ($25)] [Change Bet] [Quit]                         |
+------------------------------------------------------------------+
```

### 8.5 Blackjack Screen

```
+------------------------------------------------------------------+
|                                                                  |
|              BLACKJACK!                                          |
|              A♠ + K♥ = 21                                        |
|                                                                  |
|              You win $37.50! (3:2 payout)                        |
|                                                                  |
+------------------------------------------------------------------+
```

## 9. Game Flow

### 9.1 Round Sequence

```
1. BETTING PHASE
   - Player places bet (within table limits)
   - Confirm bet

2. DEALING PHASE
   - Deal player card 1 (face up)
   - Deal dealer card 1 (face up)
   - Deal player card 2 (face up)
   - Deal dealer card 2 (face down — hole card)

3. BLACKJACK CHECK
   - If dealer shows Ace: offer Insurance
   - Check for dealer Blackjack (peek at hole card)
   - Check for player Blackjack
   - If both: Push
   - If player only: pay 3:2 and end round
   - If dealer only: player loses and end round

4. PLAYER TURN
   - For each hand (including splits):
     a. Display available actions
     b. Player chooses: Hit, Stand, Double Down, Split, Surrender
     c. If Hit: deal card, check for bust
     d. If bust: hand loses immediately
     e. Continue until Stand or Bust

5. DEALER TURN
   - Reveal hole card
   - Dealer hits or stands per fixed rules
   - If dealer busts: all remaining player hands win

6. RESOLUTION
   - Compare each player hand to dealer hand
   - Pay/collect bets
   - Display results
   - Update balance

7. Check if shoe needs reshuffling (cut card reached)
```

## 10. Card Counting Feature (Educational)

### 10.1 Hi-Lo Count

| Card  | Count Value |
|-------|------------|
| 2-6   | +1         |
| 7-9   | 0          |
| 10-A  | -1         |

```
Running Count: Sum of all card count values seen
True Count: Running Count / Decks Remaining
```

### 10.2 Display (Optional Educational Mode)

```
+---------------------------+
|  Running Count: +7        |
|  Decks Remaining: ~4      |
|  True Count: +1.75        |
|  Advantage: Player +0.5%  |
+---------------------------+
```

## 11. Sound Effects

| Event              | Sound                          |
|--------------------|--------------------------------|
| Deal card          | Card sliding sound             |
| Chip placed        | Chip clicking                  |
| Hit                | Card dealt sound               |
| Blackjack          | Celebratory chime              |
| Bust               | Sad horn / thud                |
| Win                | Cash register / coins          |
| Push               | Neutral tone                   |
| Lose               | Soft defeat sound              |
| Shuffle            | Card shuffling                 |
| Split              | Card separating                |
| Double down        | Extra chip sound               |

## 12. Settings

| Setting              | Options                          | Default    |
|----------------------|----------------------------------|------------|
| Number of decks      | 1, 2, 4, 6, 8                  | 6          |
| Blackjack payout     | 3:2, 6:5                        | 3:2        |
| Dealer soft 17       | Hit (H17), Stand (S17)          | S17        |
| Double down          | Any 2, 9-11 only, 10-11 only   | Any 2      |
| Double after split   | Yes/No                          | Yes        |
| Surrender            | None, Late, Early               | Late       |
| Max splits           | 1, 2, 3, 4                     | 3          |
| Re-split Aces        | Yes/No                          | No         |
| Hit split Aces       | Yes/No                          | No         |
| Insurance            | Yes/No                          | Yes        |
| Starting balance     | $100 - $100,000                 | $1,000     |
| Table limits         | Low/Medium/High/VIP             | Medium     |
| Strategy advisor     | On/Off                          | Off        |
| Card counting display| On/Off                          | Off        |
| Card style           | Standard, Large, Minimal        | Standard   |
| Animation speed      | Slow, Normal, Fast              | Normal     |
| Sound effects        | On/Off                          | On         |

## 13. Statistics

| Statistic              | Description                     |
|------------------------|---------------------------------|
| Hands played           | Total hands dealt               |
| Hands won              | Total wins                      |
| Hands lost             | Total losses                    |
| Pushes                 | Total ties                      |
| Blackjacks             | Natural 21s received            |
| Win rate               | Percentage                      |
| Total wagered          | Sum of all bets                 |
| Total won              | Net profit/loss                 |
| Return rate            | Won / wagered                   |
| Biggest single win     | Largest payout                  |
| Longest win streak     | Consecutive wins                |
| Longest loss streak    | Consecutive losses              |
| Average bet            | Mean bet size                   |
| Doubles won/lost       | Double down outcomes            |
| Splits won/lost        | Split hand outcomes             |

## 14. Testing Scenarios

1. **Blackjack payout**: A+K pays 3:2 (or 6:5 per settings)
2. **Bust**: Hand over 21 loses immediately
3. **Dealer bust**: All non-busted player hands win
4. **Push**: Equal values return the bet
5. **Ace soft/hard**: Ace correctly switches from 11 to 1
6. **Split**: Same rank creates two hands
7. **Double down**: Bet doubles, exactly one card dealt
8. **Insurance**: Pays 2:1 when dealer has Blackjack
9. **Surrender**: Returns half the bet
10. **Dealer rules**: Dealer hits on 16, stands on 17 (or soft 17)
11. **Shoe depletion**: Reshuffles when cut card reached
12. **Balance tracking**: Correct chip tracking across rounds
13. **Multi-deck**: Correct card distribution for 6 decks

## 15. Performance Requirements

| Metric                     | Target             |
|----------------------------|---------------------|
| Hand value calculation     | < 0.1ms            |
| Card deal animation        | 60 FPS             |
| Chip animation             | 60 FPS             |
| Shuffle                    | < 10ms             |
| Strategy lookup            | < 1ms              |
| Board render               | < 16ms             |

## 16. Accessibility

- Large card display option
- Announce hand values via screen reader
- Keyboard shortcuts: H=Hit, S=Stand, D=Double, P=Split, R=Surrender
- High contrast card faces
- Text-based card display option (no graphics needed)
- Chip values announced on placement
- Auto-read game results
