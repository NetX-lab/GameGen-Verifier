# Wingspan - Complete Game Specification

> A comprehensive specification for recreating Wingspan Digital (Monster Couch / Stonemaier Games adaptation, 2020), the single-player-friendly board-game engine builder. This spec covers bird cards, habitats, food dice, eggs, action economy, round goals, bonus cards, AI opponents, and scoring.

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Wingspan |
| Developer | Monster Couch |
| Original Board Game Designer | Elizabeth Hargrave |
| Digital Release | 2020 |
| Source Store | Steam, App Store |
| Genre | Board game / strategy / engine builder |
| Perspective | 2D board and card UI |
| Input | Mouse/touch card and board interaction |
| Session Length | 30-60 minutes |
| Primary Objective | Attract birds to habitats, build an efficient engine, and score the most points after four rounds |
| Lose Condition | No hard fail; player ranks by final score |
| Win Condition | Highest score against AI or Automa at game end |
| Online Requirement | None for solo vs AI/Automa |

## 2. AI-Generation Scope

Minimum viable clone:

- 1 human vs 1-4 AI or solo Automa, 4 rounds, 3 habitats, food dice, bird cards, eggs, bonus cards, round goals, action cubes, and final scoring.
- Use a curated 60-card bird deck for implementation convenience while preserving card types and powers.

High-fidelity target:

- 170+ base bird cards, full Automa, multiple expansions, online-independent AI, animated bird tray, detailed compendium, and tutorial.

## 3. Technical Foundation

| System | Requirement |
|--------|-------------|
| Rendering | 2D board/card interface with readable text |
| Turn Model | Sequential player turns using action cubes |
| Players | 1-5 total; AI can be deterministic heuristic |
| Randomness | Shuffled bird deck, bonus deck, food dice, round goals |
| Save | Full match state, settings, statistics |
| Rules Engine | Data-driven cards and powers |

Turn loop:

```text
1. Active player chooses one available action row or plays a bird
2. Pay required food/egg costs
3. Resolve selected action from right to left through habitat slots
4. Trigger brown powers in that habitat
5. Update hand, food, eggs, tucked cards, cached food, and action cubes
6. Pass turn to next player
7. At round end, score round goal, clear action cubes, reduce cubes for next round
8. After round 4, calculate final score
```

## 4. Board Layout

Each player board has three habitats:

| Habitat | Main Action | Typical Resource |
|---------|-------------|------------------|
| Forest | Gain food | Food tokens |
| Grassland | Lay eggs | Eggs |
| Wetland | Draw bird cards | Hand cards |

Each habitat has 5 bird slots. Birds are played from left to right into their matching habitat(s). Later slots require egg payments as an additional cost.

Action strength increases as more birds occupy the habitat.

## 5. Bird Cards

Bird card fields:

```text
id, name, habitats, food_cost, points, nest_type, egg_limit,
wingspan_cm, power_color, power_text, power_script, predator_flag,
flocking_flag, bonus_tags
```

Habitats:

- Forest.
- Grassland.
- Wetland.
- Some birds support multiple habitats.

Food types:

- Invertebrate.
- Seed.
- Fish.
- Fruit.
- Rodent.
- Wild.

Nest types:

- Platform.
- Bowl.
- Cavity.
- Ground.
- Star/wild.

Power colors:

| Color | Timing |
|-------|--------|
| Brown | Activates when habitat action passes over bird |
| Pink | Activates once between turns when condition occurs |
| White | Activates immediately when played |
| No Power | Scores points only |

## 6. Core Actions

### Play A Bird

Rules:

1. Choose bird from hand.
2. Choose legal habitat.
3. Pay food cost.
4. Pay egg cost if placing in later columns.
5. Place bird in next open slot.
6. Resolve white "when played" power if present.

### Gain Food

Rules:

- Roll or use visible birdfeeder dice.
- Choose dice matching allowed food count from current forest action strength.
- Optional conversions may allow spending cards for extra food.
- Activate brown powers in forest from right to left.

### Lay Eggs

Rules:

- Place eggs on birds up to egg limits.
- Number of eggs depends on grassland action strength.
- Optional conversion may allow spending food for extra eggs.
- Activate brown powers in grassland from right to left.

### Draw Bird Cards

Rules:

- Draw face-up cards from tray or face-down deck.
- Number of cards depends on wetland action strength.
- Refill tray after card selection.
- Optional conversion may allow spending eggs for extra cards.
- Activate brown powers in wetland from right to left.

## 7. Bird Powers

Power templates:

| Template | Example Effect |
|----------|----------------|
| Gain Food | Take one food from supply or birdfeeder |
| Lay Egg | Lay egg on specific nest/habitat |
| Draw Card | Draw from deck or tray |
| Tuck Card | Place card under bird for points |
| Cache Food | Store food token on bird for points |
| Predator Hunt | Roll die or check wingspan to tuck/cache |
| Flock | Tuck from hand behind bird |
| Repeat | Copy another brown power |
| Opponent Trigger | Pink power when another player takes action |

Use scripts or structured effect definitions rather than parsing text.

## 8. Food Dice And Birdfeeder

Birdfeeder:

- Contains dice faces showing food symbols.
- Player selecting food chooses from available dice.
- If all remaining dice show the same face or feeder is empty, player may reroll all dice.
- Some powers reroll dice or take food directly from supply.

Dice faces can include single food or combined food icons.

## 9. Round Structure

Four rounds. Action cubes decrease each round because one cube is used for round goal scoring.

Typical cube counts:

- Round 1: 8 turns.
- Round 2: 7 turns.
- Round 3: 6 turns.
- Round 4: 5 turns.

Round end:

1. Remove action cubes from board.
2. Score round goal.
3. Discard or refresh face-up bird tray as rules require.
4. Pass first player marker if using multiplayer rules.

## 10. Goals And Bonus Cards

Round goals:

- Most birds in a habitat.
- Most eggs in a nest type.
- Most birds with specific nest.
- Most sets of eggs in habitats.
- Most birds with certain food cost.

Bonus cards:

```text
id, name, scoring_condition, points_table, related_tags
```

Examples:

- Birds with geographic names.
- Birds that eat fish.
- Birds with platform nests.
- Birds with wingspan above threshold.
- Birds worth low/high printed points.

## 11. Scoring

Final score categories:

| Category | Points |
|----------|--------|
| Bird Points | Printed points on played birds |
| Bonus Cards | Points from completed bonus conditions |
| Round Goals | Points from each round's competition |
| Eggs | 1 point each |
| Food Cached On Birds | 1 point each |
| Cards Tucked Under Birds | 1 point each |

Winner is highest total score. Ties can be broken by remaining food or shared.

## 12. AI Opponents

AI heuristic:

- Prefer playing birds with high points and low food cost early.
- Build at least one bird in each habitat.
- Choose actions based on current shortage: food if playable birds need food, cards if hand low, eggs if egg cost/score needed.
- Consider round goals and bonus tags.
- Trigger powers automatically with best available legal choice.

Automa solo:

- Use a simplified deck of Automa cards to determine blocking, goal scoring, and point gain without simulating a full board.

## 13. UI Layout

- Center: active player's three-habitat board.
- Bottom: hand cards.
- Top/side: opponents, round, action cubes, food supply, birdfeeder, tray.
- Right panel: selected card zoom and legal action prompts.
- Score pad accessible anytime.

## 14. Visual And Audio Direction

- Bird cards must be readable at zoom and summarized at board scale.
- Use calm natural sounds and habitat ambience.
- Actions should animate cards, eggs, food, and tucked cards to their destinations.
- Avoid excessive animation length; board games need fast turn flow.

## 15. Validation Checklist

- Birds can only be played into legal habitats with paid costs.
- Habitat action strength increases with occupied slots.
- Brown powers resolve right-to-left after base action.
- Egg limits prevent overfilling birds.
- Round goals score at each round end.
- Final score includes birds, bonuses, goals, eggs, cached food, and tucked cards.
- AI can complete a full four-round game without illegal moves.

