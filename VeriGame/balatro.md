# Balatro - Complete Game Specification

> A comprehensive specification for recreating Balatro (LocalThunk / Playstack, 2024), the single-player poker roguelike deckbuilder. This document focuses on rules, scoring, deck manipulation, shop economy, jokers, and run progression in a form suitable for an AI game-generation agent.

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Balatro |
| Developer | LocalThunk |
| Publisher | Playstack |
| Initial Release | February 20, 2024 |
| Source Store | Steam, App Store |
| Genre | Roguelike deckbuilder / poker score attack |
| Perspective | 2D tabletop UI |
| Input | Mouse or touch, drag-and-click card controls |
| Session Length | 20-45 minutes per winning run |
| Primary Objective | Beat escalating blind score requirements by playing poker hands enhanced by jokers, card modifiers, vouchers, and consumables |
| Lose Condition | Fail to reach the current blind's target score within the available hands |
| Win Condition | Defeat the Ante 8 boss blind; endless mode may continue after |
| Online Requirement | None for core gameplay |

## 2. AI-Generation Scope

Build the game as a deterministic single-player card engine with polished 2D UI. A faithful implementation should prioritize the scoring engine, blind loop, shop loop, and readable card interactions over exact visual branding.

Minimum viable clone:

- Standard 52-card deck with suits, ranks, chips, and poker-hand detection.
- Ante progression with Small Blind, Big Blind, and Boss Blind.
- Money, shop, booster packs, rerolls, jokers, and consumable cards.
- At least 40 jokers, 10 boss blind effects, all poker hand categories, and core card modifiers.
- Seeded random generation so a run can be reproduced.

High-fidelity target:

- 150+ joker effects, hand-level upgrades, vouchers, editions, seals, enhanced cards, spectral cards, challenge decks, and unlock tracking.
- Smooth card tweening, scoring callouts, hand sorting, hover tooltips, and fast-forwardable animations.

## 3. Technical Foundation

| System | Requirement |
|--------|-------------|
| Rendering | 2D sprite/cards over a static tabletop background |
| Aspect Ratio | Works at 16:9 desktop and portrait mobile with responsive card rows |
| Frame Rate | 60 FPS target |
| State Model | Run state is pure data: deck, hand, discard pile, jokers, shop, money, ante, blind, score |
| Randomness | All deck shuffles, shop rolls, booster contents, and blind choices use one seed |
| Save | Auto-save at start of each blind and shop phase |

Core update loop:

```text
1. Wait for player action: select cards, play hand, discard, use consumable, buy shop item
2. Validate action against phase, hand limits, discard limits, and card ownership
3. If playing a hand, detect best poker hand and initialize chips/mult
4. Apply card scoring, enhancements, seals, editions, joker triggers, and hand-level bonuses
5. Animate scoring in trigger order and add total to blind score
6. Move played cards to discard, draw back to hand size, decrement hand count
7. Check blind success or failure
8. If blind cleared, pay rewards and transition to shop or next ante
```

## 4. Core Run Structure

Each run is divided into antes. Each ante contains three blinds:

| Blind | Function | Reward |
|-------|----------|--------|
| Small Blind | Easier target score | Low cash |
| Big Blind | Higher target score | Medium cash |
| Boss Blind | Highest target plus a rule modifier | Ante completion and larger cash |

The player may skip a blind to gain a tag reward. Skipping forfeits the blind payout and moves directly to the next blind. Boss blinds cannot be skipped in the base rules unless a special tag or challenge allows it.

Blind target formula:

- Ante 1 starts very low so a normal pair or two pair can clear early blinds.
- Each ante multiplies score requirements sharply.
- Boss blinds add restrictions such as debuffing one suit, reducing hand size, forcing one hand type, or hiding drawn cards.

## 5. Card And Deck System

### Standard Cards

| Rank | Base Chips |
|------|------------|
| 2-10 | Numeric value |
| Jack, Queen, King | 10 |
| Ace | 11 |

Suits are Hearts, Diamonds, Clubs, and Spades. Suits matter for flush detection and suit-specific joker effects.

### Hand Area

- The default hand size is 8 cards.
- The player can select up to 5 cards for a played hand.
- The player can select up to 5 cards for a discard action.
- Played cards and discarded cards move into the discard pile until the deck is exhausted, then discard pile is shuffled into a new draw pile.

### Poker Hand Ranking

Detect the highest valid hand from selected cards:

| Hand | Detection | Base Chips | Base Mult |
|------|-----------|------------|-----------|
| High Card | No stronger pattern | 5 | 1 |
| Pair | 2 same rank | 10 | 2 |
| Two Pair | Two distinct pairs | 20 | 2 |
| Three of a Kind | 3 same rank | 30 | 3 |
| Straight | 5 sequential ranks | 30 | 4 |
| Flush | 5 same suit | 35 | 4 |
| Full House | Three of a kind plus pair | 40 | 4 |
| Four of a Kind | 4 same rank | 60 | 7 |
| Straight Flush | Straight and flush | 100 | 8 |
| Five of a Kind | 5 same rank after deck modification | 120 | 12 |
| Flush House | Full house and all same suit | 140 | 14 |
| Flush Five | Five of a kind and all same suit | 160 | 16 |

## 6. Scoring Engine

Final score for a played hand:

```text
hand_score = final_chips * final_mult
```

Scoring order:

1. Identify played hand and add its base chips and base mult.
2. Score individual cards that are part of the hand pattern.
3. Apply card enhancements.
4. Apply card editions.
5. Trigger held-card effects.
6. Trigger jokers from left to right unless an effect changes ordering.
7. Apply final multipliers and add result to current blind score.

Important distinction:

- `+chips` increases chips additively.
- `+mult` increases mult additively.
- `xmult` multiplies the current mult and should be applied after additive mult where specified.

## 7. Card Modifiers

| Modifier | Effect |
|----------|--------|
| Bonus Card | Adds extra chips when scored |
| Mult Card | Adds extra mult when scored |
| Wild Card | Counts as any suit for suit checks |
| Glass Card | Multiplies mult when scored, then may destroy itself |
| Steel Card | Multiplies mult while held in hand |
| Gold Card | Pays money if held at end of round |
| Lucky Card | Chance to add mult or money |
| Stone Card | Has no rank or suit but adds high chips |

Editions apply to cards or jokers:

| Edition | Effect |
|---------|--------|
| Foil | Adds chips |
| Holographic | Adds mult |
| Polychrome | Adds xmult |
| Negative | Increases joker capacity when on a joker |

## 8. Joker System

The player normally has 5 joker slots. Jokers are passive rule modifiers. Each joker must specify:

```text
id, name, rarity, cost, trigger_timing, trigger_condition, effect, display_text
```

Core trigger timings:

- Before hand scoring.
- When each card scores.
- When a card is held in hand.
- After hand scoring.
- End of blind.
- Shop entry.
- Sell event.

Representative joker effects:

| Joker Type | Example Behavior |
|------------|------------------|
| Flat Chip | Add chips for every scored card of a suit |
| Flat Mult | Add mult if hand contains a pair |
| Scaling Mult | Gain +1 mult permanently each time a condition is met |
| Economy | Earn extra dollars after blind clear |
| Deck Shape | Retrigger face cards, aces, or enhanced cards |
| Risk Reward | Large xmult but disabled by certain hands |
| Copy | Copies the effect of adjacent joker |

Joker ordering is part of strategy. The UI must allow dragging jokers horizontally to reorder them.

## 9. Consumables And Shop

Shop appears after each cleared blind unless the run directly moves to a boss or special reward.

Shop elements:

- 2 joker cards by default.
- 2 consumable slots by default.
- Booster packs.
- Reroll button with increasing reroll cost.
- Sell area for jokers and consumables.

Consumable classes:

| Class | Function |
|-------|----------|
| Tarot | Modify cards, money, editions, or selected cards |
| Planet | Upgrade a poker hand level |
| Spectral | High-risk deck transformation |
| Voucher | Permanent run-wide upgrade bought from shop |

Money rules:

- Blind payout pays a fixed reward plus remaining hands.
- Interest pays money based on held cash up to a cap.
- Spending is allowed only in shop phase.
- Selling returns partial value and may trigger effects.

## 10. Boss Blind Effects

Implement at least these boss effects:

| Boss | Effect |
|------|--------|
| The Club | All Clubs are debuffed |
| The Goad | All Spades are debuffed |
| The Head | All Hearts are debuffed |
| The Window | All Diamonds are debuffed |
| The Hook | Discards random cards after each hand |
| The Wall | Extra-large blind requirement |
| The Needle | Only one hand allowed |
| The Flint | Base chips and mult are reduced |
| The Psychic | Played hand must contain exactly 5 cards |
| The Arm | Played hand level is temporarily reduced |

Debuffed cards should still exist in hand but do not score chips, enhancements, or suit-specific effects unless a joker explicitly bypasses debuffs.

## 11. UI Layout

Main blind screen:

- Top left: ante number, current blind, target score, current score.
- Top center: animated scoring readout showing chips x mult.
- Top right: money, hands remaining, discards remaining.
- Center: selected cards and scoring effects.
- Bottom: hand row with sortable cards.
- Side row: jokers with hover tooltips.
- Buttons: Play Hand, Discard, Sort Rank, Sort Suit, Run Info.

Shop screen:

- Jokers and consumables in the center.
- Buy, sell, reroll, skip, next blind controls.
- Tooltips expose exact trigger timing and numerical effect.

## 12. Visual And Audio Direction

- Use high-contrast cards with readable ranks and suits.
- Scoring should feel mechanical and sequential: card pop, chip count, mult count, joker trigger, total burst.
- Each joker rarity can have a distinct border treatment.
- Audio should include card flicks, coin clinks, scoring ticks, boss blind stingers, and shop ambience.

## 13. Validation Checklist

- A legal pair, flush, straight, full house, and straight flush are detected correctly.
- Joker trigger order changes total score when jokers are reordered.
- A boss blind can disable cards without removing them from the deck.
- Running out of hands before reaching target ends the run.
- Winning Ante 8 enters victory state.
- Same seed reproduces initial deck order, shops, boosters, and blind sequence.

