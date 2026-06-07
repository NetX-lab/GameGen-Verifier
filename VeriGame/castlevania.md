# Castlevania (NES) — Complete Game Specification

> A comprehensive specification for faithfully recreating Castlevania (Konami, 1986 NES). This document covers every system, mechanic, entity, and interaction required for a full clone of Simon Belmont's quest through Dracula's Castle.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Player Character Mechanics](#3-player-character-mechanics)
4. [Weapon System](#4-weapon-system)
5. [Sub-Weapon System](#5-sub-weapon-system)
6. [Enemy Compendium](#6-enemy-compendium)
7. [Level Design — All 6 Stages](#7-level-design--all-6-stages)
8. [Boss Encounters](#8-boss-encounters)
9. [Item & Pickup System](#9-item--pickup-system)
10. [Scoring System](#10-scoring-system)
11. [UI Layout & HUD](#11-ui-layout--hud)
12. [Audio Design](#12-audio-design)
13. [Animation System](#13-animation-system)
14. [Lives & Continue System](#14-lives--continue-system)

---

## 1. Game Overview

- **Genre**: Action-platformer
- **Perspective**: 2D side-scrolling
- **Players**: 1 player
- **Input**: D-pad + 2 buttons (Attack, Jump) + Start (pause) + Up+Attack (use sub-weapon)
- **Objective**: Guide Simon Belmont through 6 stages (18 blocks) of Dracula's Castle to defeat Count Dracula.
- **Lose Condition**: Lose all lives. Limited continues.
- **Key feature**: Deliberate, weighty controls — once Simon jumps, the trajectory is committed. Whip combat with sub-weapons powered by hearts.

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| NES resolution | 256 x 240 pixels |
| Recommended implementation | 512 x 480 or 1024 x 960 |
| Frame rate | 60 FPS (NTSC) |
| Tile size | 16 x 16 pixels |
| Screen scroll | Horizontal, one direction only (no backtracking) |

### Coordinate System

- Origin (0, 0) at top-left.
- Each stage is divided into blocks (sub-sections).
- Screen scrolls horizontally following the player.
- Door transitions between blocks are instant screen wipes.

### Game Loop

```
1. Process input (D-pad, buttons)
2. Update Simon state (walking, jumping, attacking, knockback)
3. Apply gravity and ground collision
4. Update whip attack hitbox and timing
5. Update sub-weapon projectile
6. Update all enemy AI and movement
7. Update enemy projectiles
8. Check Simon vs enemy collisions
9. Check whip vs enemy/candle collisions
10. Check sub-weapon vs enemy collisions
11. Check Simon vs item pickups
12. Handle knockback physics
13. Update timer countdown
14. Render (background → candles → enemies → items → Simon → whip → UI)
```

---

## 3. Player Character Mechanics

### Simon Belmont Properties

| Property | Value |
|----------|-------|
| HP | 16 units (displayed as a health bar) |
| Hitbox | 12 x 30 pixels |
| Walk speed | 1 px/frame (60 px/s) |
| Jump velocity (initial) | -4 px/frame |
| Gravity | 0.3 px/frame^2 |
| Max fall speed | 5 px/frame |
| Jump height | ~48 pixels (approximately 3 blocks high) |
| Jump horizontal distance | ~64 pixels (~4 blocks wide) |

### Movement Characteristics

| Property | Description |
|----------|-------------|
| Walking | Constant speed, no acceleration/deceleration |
| Jumping | **Fixed trajectory** — once jump begins, horizontal direction CANNOT be changed |
| Stair walking | Fixed speed on stairs (0.75 px/frame), can only walk up or down |
| Crouching | D-pad down; reduces hitbox, cannot move |
| Knockback | On hit: knocked backward ~32 pixels with arc trajectory |
| Post-knockback | Brief stun; can fall into pits |
| Attack while crouching | Whip swings lower |
| Attack while jumping | Whip swings at standing height |
| No air control | Cannot change direction mid-jump |

### Stair Mechanics

| Property | Value |
|----------|-------|
| Entry | Walk to stair base, press Up (ascending) or Down (descending) |
| Speed | 0.75 px/frame diagonal |
| Controls on stairs | Up/Down only; cannot jump |
| Attack on stairs | Can whip while on stairs |
| Stepping off | Walk off the top or bottom of the staircase |
| Vulnerability | Fully vulnerable while on stairs; knockback sends Simon off stairs |
| Direction lock | While on stairs, Simon faces the direction of the staircase |

### Knockback System

| Property | Value |
|----------|-------|
| Horizontal distance | ~32 pixels backward |
| Arc height | ~16 pixels |
| Duration | ~20 frames (0.33 seconds) |
| Control | NO control during knockback |
| Pit death | Can be knocked into pits or off platforms |
| Invincibility after | 90 frames (1.5 seconds) of flickering invincibility |

---

## 4. Weapon System

### Vampire Killer Whip

The whip is Simon's primary weapon, with three upgrade levels.

| Level | Name | Damage | Range | Appearance | Upgrade Item |
|-------|------|--------|-------|-----------|-------------|
| 1 | Leather Whip | 1 | Short (~24 px) | Brown, thin whip | Default |
| 2 | Chain Whip | 2 | Medium (~32 px) | Grey chain whip | Morning Star upgrade (first) |
| 3 | Morning Star | 3 | Long (~48 px) | Blue/long chain with flail | Morning Star upgrade (second) |

### Whip Attack Properties

| Property | Value |
|----------|-------|
| Attack duration | 20 frames (~0.33 seconds) |
| Windup | ~8 frames (arm draws back) |
| Active hitbox | ~8 frames (whip extended) |
| Recovery | ~4 frames (whip retracts) |
| Direction | Always forward (left or right, based on facing) |
| Vertical position (stand) | Chest height |
| Vertical position (crouch) | Knee height |
| Can hit candles | Yes |
| Can hit destructible walls | Yes |
| Fire rate | Limited by attack animation (~3 attacks/second max) |

### Whip Downgrade

- Simon loses the whip upgrade on death (reverts to Leather Whip level 1).
- Must find Morning Star upgrades again in candles.

---

## 5. Sub-Weapon System

### Heart Currency

| Property | Value |
|----------|-------|
| Small heart | 1 heart |
| Large heart | 5 hearts |
| Starting hearts per life | 5 |
| Maximum hearts | 99 |
| Source | Candles, enemy drops |

### Sub-Weapons

Only one sub-weapon can be held at a time. Picking up a new one replaces the current one.

#### Dagger

| Property | Value |
|----------|-------|
| Heart cost | 1 |
| Damage | 1 |
| Speed | 4 px/frame |
| Trajectory | Straight horizontal |
| Max on screen | 1 (2 with Double, 3 with Triple) |
| Range | Full screen width |
| Best use | Long-range attacks |

#### Axe

| Property | Value |
|----------|-------|
| Heart cost | 1 |
| Damage | 2 |
| Speed | 2 px/frame horizontal, arcing trajectory |
| Trajectory | Upward arc then falls (parabolic) |
| Max arc height | ~80 pixels above throw point |
| Max on screen | 1 (2 with Double, 3 with Triple) |
| Best use | Hitting enemies above Simon, Medusa heads |

#### Holy Water (Fire Bomb)

| Property | Value |
|----------|-------|
| Heart cost | 1 |
| Damage | 1 per hit (multi-hit: burns for ~2 seconds) |
| Trajectory | Short forward arc, drops to ground |
| Ground fire duration | ~120 frames (2 seconds) |
| Ground fire hits | 6-8 hits during duration |
| Ground fire range | ~16 pixels wide |
| Effect | Stuns enemies caught in fire (they stop moving) |
| Max on screen | 1 (2 with Double, 3 with Triple) |
| Best use | Boss fights (stun-lock), Dracula fight |

#### Boomerang (Cross)

| Property | Value |
|----------|-------|
| Heart cost | 1 |
| Damage | 2 |
| Speed | 3 px/frame |
| Trajectory | Straight forward, then returns to Simon |
| Range | ~128 pixels forward before returning |
| Hits | Can hit on both outward and return trip |
| Max on screen | 1 (2 with Double, 3 with Triple) |
| Best use | Hitting enemies twice, safe ranged attack |

#### Stopwatch

| Property | Value |
|----------|-------|
| Heart cost | 5 |
| Damage | 0 (utility) |
| Effect | Freezes all enemies for ~5 seconds (300 frames) |
| Usage | Activated immediately (no projectile) |
| Best use | Difficult platforming sections with enemies |

### Shot Multipliers

| Item | Effect | Heart Cost Multiplier |
|------|--------|----------------------|
| Double Shot (II) | Can have 2 sub-weapons on screen simultaneously | x1 per shot (2 hearts for 2 shots) |
| Triple Shot (III) | Can have 3 sub-weapons on screen simultaneously | x1 per shot (3 hearts for 3 shots) |

---

## 6. Enemy Compendium

### Common Enemies

#### Zombie

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 2 |
| Speed | 0.5 px/frame |
| Behavior | Walks slowly toward player from right side of screen |
| Score | 100 |
| Stage | 1 (Block 1) |

#### Ghost (Phantom Bat)

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 2 |
| Speed | 1.5 px/frame (sine wave) |
| Behavior | Flies in sine wave pattern toward player |
| Score | 200 |
| Stage | 1, 3, 5 |

#### Medusa Head

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 2 |
| Speed | 1.5 px/frame horizontal |
| Behavior | Flies horizontally in a sine wave pattern (amplitude ~24 pixels, period ~64 pixels) |
| Spawn | Infinitely from screen edges, opposite direction of player |
| Score | 200 |
| Stage | 2, 4, 5, 6 |
| Note | One of the most dangerous common enemies due to knockback near pits |

#### Fishman (Merman)

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 2 |
| Speed | 1 px/frame |
| Behavior | Leaps from water, fires a fireball, walks forward |
| Fireball speed | 2 px/frame |
| Score | 200 |
| Stage | 1, 3 |

#### Raven (Eagle/Crow)

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 2 |
| Speed | 2 px/frame (dive) |
| Behavior | Perches until player approaches, then dives diagonally |
| Score | 200 |
| Stage | 2, 3 |

#### Skeleton

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 2 |
| Speed | 0.75 px/frame |
| Behavior | Walks forward, throws bones in an arc |
| Bone arc | Parabolic, similar to axe sub-weapon |
| Bone speed | 2 px/frame |
| Score | 200 |
| Stage | 2, 4, 5 |

#### Fleaman (Hunchback/Igor)

| Property | Value |
|----------|-------|
| HP | 1 |
| Damage | 2 |
| Speed | 2 px/frame horizontal, bouncing |
| Behavior | Bounces erratically toward player with high jumps |
| Jump height | 32-64 pixels (variable) |
| Score | 300 |
| Stage | 3, 4, 5, 6 |
| Note | Very difficult to hit due to erratic movement |

#### Bone Pillar

| Property | Value |
|----------|-------|
| HP | 2 |
| Damage | 2 (contact), 2 (fireball) |
| Speed | 0 (stationary) |
| Behavior | Stationary stack of skulls, fires 2 fireballs at regular intervals |
| Fire rate | 1 pair every 2 seconds |
| Fireball speed | 2 px/frame |
| Score | 300 |
| Stage | 3, 5, 6 |

#### Axe Knight

| Property | Value |
|----------|-------|
| HP | 3 |
| Damage | 3 |
| Speed | 0.5 px/frame |
| Behavior | Walks forward slowly, throws axes in high arc |
| Axe speed | 2 px/frame |
| Score | 500 |
| Stage | 4, 5, 6 |

#### Red Skeleton

| Property | Value |
|----------|-------|
| HP | Invincible (reassembles after 3 seconds) |
| Damage | 2 |
| Speed | 0.75 px/frame |
| Behavior | Same as skeleton but reassembles after being knocked down |
| Reassemble time | ~180 frames (3 seconds) |
| Score | 0 (cannot be permanently killed) |
| Stage | 5, 6 |

#### Armor Knight

| Property | Value |
|----------|-------|
| HP | 4 |
| Damage | 3 |
| Speed | 0.5 px/frame |
| Behavior | Walks forward, high HP, sometimes blocks with shield |
| Score | 700 |
| Stage | 5, 6 |

### Spawning Medusa Heads

- Medusa Heads spawn infinitely from screen edges.
- Spawn interval: approximately every 90 frames (1.5 seconds).
- They always fly from one side to the other.
- New ones spawn as long as the player is in a Medusa Head zone.
- Extremely dangerous near platforming sections with pits.

---

## 7. Level Design — All 6 Stages

Each stage consists of 3 blocks (sub-sections). Block transitions are door-entering animations.

### Stage 1: Entrance Hall

#### Block 1

| Property | Value |
|----------|-------|
| Setting | Castle exterior approach, courtyard |
| Enemies | Zombies, panthers |
| Hazards | None |
| Candles | Morning Star upgrade, hearts, dagger |
| Length | ~512 pixels |

#### Block 2

| Property | Value |
|----------|-------|
| Setting | Castle entrance hallway |
| Enemies | Zombies, ghosts, fishmen |
| Hazards | Water pits (cosmetic, fishmen jump from them) |
| Candles | Hearts, sub-weapons |
| Length | ~640 pixels |

#### Block 3

| Property | Value |
|----------|-------|
| Setting | Main hall, stairs to boss |
| Enemies | Ghosts, leopards |
| Boss | Giant Bat (Phantom Bat) |
| Length | ~384 pixels + boss room |

### Stage 2: Clock Tower Approach

#### Block 4

| Property | Value |
|----------|-------|
| Setting | Outdoor walkway, Medusa head zone |
| Enemies | Medusa heads, ravens, knights |
| Hazards | Pits with Medusa heads (knockback danger) |
| Length | ~640 pixels |

#### Block 5

| Property | Value |
|----------|-------|
| Setting | Interior corridors |
| Enemies | Skeletons, bone pillars |
| Hazards | Falling platforms |
| Length | ~640 pixels |

#### Block 6

| Property | Value |
|----------|-------|
| Setting | Upper corridors leading to boss |
| Boss | Medusa (dual Medusa heads) |
| Length | ~384 pixels + boss room |

### Stage 3: Underground Caverns

#### Block 7

| Property | Value |
|----------|-------|
| Setting | Cave/dungeon, underground waterway |
| Enemies | Fishmen, ravens, bats |
| Hazards | Water (cosmetic), falling stalactites |
| Length | ~768 pixels |

#### Block 8

| Property | Value |
|----------|-------|
| Setting | Deeper caverns |
| Enemies | Fleamen, bone pillars |
| Hazards | Moving platforms, pits |
| Length | ~768 pixels |

#### Block 9

| Property | Value |
|----------|-------|
| Setting | Cavern exit, upward climb |
| Boss | Mummy Pair |
| Length | ~512 pixels + boss room |

### Stage 4: Underground Passages

#### Block 10

| Property | Value |
|----------|-------|
| Setting | Stone passages |
| Enemies | Skeletons, axe knights, Medusa heads |
| Hazards | Pit jumps with Medusa heads |
| Length | ~768 pixels |

#### Block 11

| Property | Value |
|----------|-------|
| Setting | Laboratory/Alchemy room |
| Enemies | Fleamen, skeletons |
| Hazards | Crushing ceiling traps |
| Length | ~768 pixels |

#### Block 12

| Property | Value |
|----------|-------|
| Setting | Passage to boss |
| Boss | Frankenstein's Monster & Igor |
| Length | ~512 pixels + boss room |

### Stage 5: Castle Keep

#### Block 13

| Property | Value |
|----------|-------|
| Setting | Castle towers, outdoor bridges |
| Enemies | Medusa heads, axe knights, red skeletons |
| Hazards | Long pit sections with Medusa heads |
| Length | ~1024 pixels |

#### Block 14

| Property | Value |
|----------|-------|
| Setting | Upper castle corridors |
| Enemies | Armor knights, bone pillars, fleamen |
| Hazards | Spike pits, crumbling platforms |
| Length | ~768 pixels |

#### Block 15

| Property | Value |
|----------|-------|
| Setting | Approach to upper tower |
| Boss | Death (Grim Reaper) |
| Length | ~512 pixels + boss room |

### Stage 6: Dracula's Tower

#### Block 16

| Property | Value |
|----------|-------|
| Setting | Final tower ascent |
| Enemies | Axe knights, bone pillars, Medusa heads, red skeletons |
| Hazards | Pits, spikes, tightest platforming |
| Length | ~1024 pixels |

#### Block 17

| Property | Value |
|----------|-------|
| Setting | Inner sanctum |
| Enemies | Eagles, fleamen, armor knights |
| Hazards | Crumbling staircases |
| Length | ~768 pixels |

#### Block 18

| Property | Value |
|----------|-------|
| Setting | Dracula's throne room |
| Boss | Dracula (2 phases) |
| Length | Boss room only |

---

## 8. Boss Encounters

### Stage 1 Boss: Phantom Bat (Giant Bat)

| Property | Value |
|----------|-------|
| HP | 12 |
| Damage | 3 (contact) |
| Pattern | Flies in arc patterns across the room, swoops at Simon |
| Speed | 2 px/frame |
| Movement | Circular/arc pattern, periodically dives toward player |
| Arena | Single screen, flat floor |
| Weakness | Holy Water (stun-lock), Boomerang |
| Score | 3,000 |

### Stage 2 Boss: Medusa

| Property | Value |
|----------|-------|
| HP | 12 |
| Damage | 3 |
| Pattern | Head floats in sine wave, fires snakes that travel along the floor |
| Speed | 1.5 px/frame |
| Snake speed | 1 px/frame (along floor) |
| Snake spawn rate | Every 3 seconds |
| Arena | Single screen, flat floor |
| Weakness | Boomerang (hits on return), Holy Water |
| Score | 5,000 |

### Stage 3 Boss: Mummy Pair

| Property | Value |
|----------|-------|
| HP | 12 each |
| Damage | 3 |
| Pattern | Two mummies walk back and forth, throw bandage strips |
| Speed | 1 px/frame |
| Bandage speed | 2 px/frame |
| Bandage arc | Straight horizontal at varying heights |
| Arena | Single screen, flat floor |
| Strategy | Focus on one mummy at a time |
| Weakness | Holy Water (stun both) |
| Score | 5,000 each |

### Stage 4 Boss: Frankenstein's Monster & Igor

| Property | Value |
|----------|-------|
| Monster HP | 16 |
| Igor HP | N/A (infinite spawns) |
| Monster damage | 3 |
| Igor damage | 2 |
| Monster speed | 0.5 px/frame (slow walk) |
| Igor speed | 2 px/frame (bouncing) |
| Monster behavior | Walks slowly back and forth |
| Igor behavior | Bounces erratically around the room (like a Fleaman) |
| Igor respawn | If killed, another Igor spawns after 3 seconds |
| Arena | Single screen, flat floor |
| Weakness | Holy Water on monster (stun-lock) |
| Score | 7,000 |

### Stage 5 Boss: Death (Grim Reaper)

| Property | Value |
|----------|-------|
| HP | 16 |
| Damage | 3 (contact), 2 (sickle) |
| Pattern | Floats around room, summons flying sickles |
| Speed | 1.5 px/frame (floating, direction changes) |
| Sickle count | 2-3 flying sickles at a time |
| Sickle behavior | Float and orbit around Death, sometimes fly toward Simon |
| Sickle speed | 1.5 px/frame |
| Arena | Single screen, flat floor |
| Weakness | Holy Water (stun-lock if positioned correctly) |
| Score | 10,000 |
| Note | One of the hardest bosses — sickles are hard to avoid |

### Stage 6 Final Boss: Dracula

#### Phase 1: Count Dracula

| Property | Value |
|----------|-------|
| HP | 16 |
| Damage | 4 (contact), 3 (fireball) |
| Pattern | Teleports to random positions, fires 3 fireballs |
| Teleport interval | Every 3-4 seconds |
| Teleport positions | 5 preset positions across the room |
| Fireball pattern | 3 fireballs in a spread (high, mid, low) |
| Fireball speed | 2 px/frame |
| Weak point | Head only (must jump to hit) |
| Arena | Single screen, flat floor with raised platform edges |
| Weakness | Holy Water (stun-lock on platform), Boomerang |
| Score | 15,000 |

#### Phase 2: Dracula's True Form (Demon)

| Property | Value |
|----------|-------|
| HP | 16 |
| Damage | 4 (contact) |
| Pattern | Large demon form that jumps and lands, fires projectiles |
| Jump height | ~64 pixels |
| Jump distance | ~96 pixels |
| Projectile | Single fireball aimed at Simon |
| Fireball speed | 3 px/frame |
| Hitbox | Much larger than Phase 1 (~32 x 48 pixels) |
| Weakness | Holy Water, Boomerang |
| Score | 50,000 |
| Victory | Defeating Phase 2 completes the game |

---

## 9. Item & Pickup System

### Candle System

Candles line the levels and contain items when struck with the whip or sub-weapons.

| Candle Type | Contents |
|------------|----------|
| Standard candle | Small heart (most common), sub-weapons, score items |
| Large candle/Brazier | Large heart, Morning Star upgrade, II/III shot |

### Item Drops

| Item | Effect | Source |
|------|--------|--------|
| Small Heart | +1 heart | Candles, enemy drops |
| Large Heart | +5 hearts | Large candles, rare drops |
| Morning Star Upgrade | Whip upgrade (1→2→3) | Specific candles |
| Dagger | Sub-weapon: Dagger | Candles |
| Axe | Sub-weapon: Axe | Candles |
| Holy Water | Sub-weapon: Holy Water | Candles |
| Boomerang/Cross | Sub-weapon: Boomerang | Candles |
| Stopwatch | Sub-weapon: Stopwatch | Candles |
| Double Shot (II) | 2 sub-weapons on screen | Candles (specific) |
| Triple Shot (III) | 3 sub-weapons on screen | Candles (rare) |
| Pork Chop | Full HP restore | Hidden in walls (whip walls to reveal) |
| Money Bag (100) | 100 points | Candles |
| Money Bag (400) | 400 points | Candles |
| Money Bag (700) | 700 points | Candles |
| Money Bag (1000) | 1,000 points | Hidden, rare |
| Rosary/Cross | Kills all enemies on screen | Very rare in candles |
| Invisibility Potion | Temporary invincibility (~10 seconds) | Very rare, hidden |
| 1-UP | Extra life | Extremely rare, specific locations |

### Hidden Wall Items

- Certain wall blocks can be destroyed by the whip.
- They contain Pork Chops (full HP), 1-UPs, or Money Bags.
- No visual indicator — player must know or discover the locations.
- Approximately 2-4 hidden wall items per stage.

---

## 10. Scoring System

### Score Sources

| Source | Points |
|--------|--------|
| Zombie | 100 |
| Ghost/Bat | 200 |
| Medusa Head | 200 |
| Fishman | 200 |
| Skeleton | 200 |
| Fleaman | 300 |
| Bone Pillar | 300 |
| Raven | 200 |
| Axe Knight | 500 |
| Armor Knight | 700 |
| Red Skeleton | 0 (cannot die) |
| Boss kills | 3,000-50,000 |
| Money bags | 100/400/700/1,000 |
| Stage clear time bonus | Remaining time x 10 |
| Heart bonus (end of stage) | Each remaining heart x 100 |

### Timer System

| Property | Value |
|----------|-------|
| Starting time | 300 (counts down) |
| Countdown speed | 1 unit per ~0.67 seconds (roughly 5 minutes per stage) |
| Time up | Instant death (lose a life) |
| Stage clear bonus | Remaining time x 10 points |

### Extra Lives

| Score | Effect |
|-------|--------|
| 30,000 points | 1 extra life |
| 100,000 points | 1 extra life |
| No further score-based lives | — |

---

## 11. UI Layout & HUD

### 11.1 In-Game HUD

```
┌──────────────────────────────────────────────────────┐
│ SCORE-  014700   PLAYER   -ENEMY-    TIME  0264      │
│ ████████████████  ♥05     ████████████████            │
│ STAGE 03                  [AXE ICON]                  │
├──────────────────────────────────────────────────────┤
│                                                       │
│                                                       │
│     [Game playfield - Dracula's Castle]               │
│                                                       │
│                                                       │
│                                                       │
└──────────────────────────────────────────────────────┘
```

### HUD Elements

| Element | Position | Description |
|---------|----------|-------------|
| SCORE | Top-left | Current score |
| PLAYER HP bar | Top-center-left | 16-unit horizontal bar |
| Heart count | Below PLAYER bar | Current hearts with heart icon |
| STAGE number | Below heart count | Current stage number |
| ENEMY HP bar | Top-center-right | Boss HP (appears during boss fights) |
| Sub-weapon icon | Below ENEMY bar | Current sub-weapon display |
| Shot multiplier | Below sub-weapon | II or III indicator |
| TIME | Top-right | Countdown timer |

---

## 12. Audio Design

### 12.1 Music (Composer: Kinuyo Yamashita)

| Track | Context | Notable Feature |
|-------|---------|-----------------|
| "Vampire Killer" | Stage 1 | Iconic main theme, upbeat and heroic |
| "Stalker" | Stage 2 | Tense, determined march |
| "Wicked Child" | Stage 3 | Dark and driving |
| "Walking on the Edge" | Stage 4 | Atmospheric, cautious |
| "Heart of Fire" | Stage 5 | Intense, urgent — fan favorite |
| "Out of Time" | Stage 6 | Climactic, foreboding |
| "Poison Mind" | Boss fights | Heavy, aggressive battle music |
| "Nothing to Lose" | Final boss (Dracula) | Dramatic, climactic |
| "Voyage into History" | Stage clear | Short triumphant fanfare |
| "Ending" | Credits/ending | Uplifting, heroic resolution |
| "Game Over" | Game over screen | Somber, brief |
| "Prologue" | Title/intro | Dark, atmospheric setting |

### 12.2 Sound Effects

| Event | Description |
|-------|-------------|
| Whip crack | Sharp "crack/snap" sound |
| Whip hit (enemy) | Thudding impact |
| Whip hit (candle) | Lighter impact + item appear chime |
| Sub-weapon throw | Throwing sound (varies by weapon) |
| Holy Water impact | Sizzling fire sound |
| Boomerang whoosh | Spinning whirr |
| Player hit | Damage sting + grunt |
| Player death | Death jingle |
| Enemy death | Dissolution sound (varies) |
| Item pickup | Rising chime "ding" |
| Heart pickup | Light "bling" |
| Pork chop | Restoration sound |
| Boss damage | Heavy impact |
| Boss death | Extended explosion |
| Stair footstep | Stone step sound |
| Jump | No sound (NES limitation) |
| Knockback | Impact + falling sound |
| Timer warning (low time) | Tempo increases in music |
| Rosary/screen clear | Flash + dissolution sound |
| Door transition | Brief pause, door opening |

---

## 13. Animation System

### 13.1 Simon Belmont Animations

| Animation | Frames | FPS | Description |
|-----------|--------|-----|-------------|
| Idle | 1 | — | Standing with whip coiled |
| Walk | 4 | 10 | Walking cycle, deliberate pace |
| Crouch | 1 | — | Kneeling position |
| Jump (ascend) | 1 | — | Legs tucked |
| Jump (descend) | 1 | — | Legs extended |
| Whip (standing) | 3 | 15 | Arm back → arm forward → whip extend |
| Whip (crouching) | 3 | 15 | Same but lower position |
| Whip (stairs) | 3 | 15 | Same on staircase |
| Climb stairs | 4 | 8 | Stepping up/down animation |
| Hit/knockback | 2 | 10 | Thrown backward |
| Death | 4 | 8 | Explodes into fragments upward |
| Invincibility | Flicker | 30 FPS toggle | Alternates visible/invisible |

### 13.2 Enemy Animations

| Enemy | Frames | Key Animation Details |
|-------|--------|----------------------|
| Zombie | 4 walk | Shuffling gait, arms forward |
| Medusa Head | 2 (wing flap) | Sine wave flight |
| Skeleton | 4 walk + 2 throw | Walking with bone throw |
| Fleaman | 4 bounce | Bouncing erratically |
| Bone Pillar | 2 fire | Skull mouth opens to fire |
| Axe Knight | 4 walk + 2 throw | Armored walk, axe swing |
| Bat | 2 flap | Erratic flight pattern |
| Fishman | 3 leap + 1 stand | Emerges from water |

### 13.3 Visual Effects

| Effect | Frames | Description |
|--------|--------|-------------|
| Enemy death | 4 | Flashing dissolution |
| Candle break | 2 | Candle disappears, item appears |
| Holy Water flame | 4 (loop) | Blue flames on ground |
| Boss explosion | 8 | Large multi-frame explosion |
| Screen clear (Rosary) | Flash | White flash, all enemies dissolve |
| Item sparkle | 4 (loop) | Bouncing item with sparkle |
| Dracula teleport | 4 | Materializes from particles |

---

## 14. Lives & Continue System

### Lives

| Property | Value |
|----------|-------|
| Starting lives | 3 |
| Maximum lives | 9 |
| Extra life from score | 30,000 and 100,000 |
| 1-UP items | 1-2 per full game (hidden) |
| Death penalty | Lose current whip upgrade, revert to Leather Whip |
| Respawn | Start of current block (not stage, but sub-section) |

### Continue System

| Property | Value |
|----------|-------|
| Continues | Unlimited (NES version) |
| On continue | Restart at beginning of current stage (not block) |
| Lives on continue | Reset to 3 |
| Score on continue | Reset to 0 |
| Sub-weapon | Lost |
| Whip level | Reset to Leather Whip (level 1) |

### Game Completion

- Defeating Dracula Phase 2 triggers the ending sequence.
- Castle crumbles (visual sequence).
- Simon stands on a cliff overlooking the dawn.
- Credits roll.
- Game can be replayed on "Second Quest" (harder difficulty).

### Second Quest Changes

- All enemies deal more damage.
- More enemies on screen.
- Some enemy placement changes.
- Faster enemy movement.
- Same level layouts.

---

## Appendix A: Quick Reference — Boss HP and Weaknesses

| Boss | Stage | HP | Weakness | Score |
|------|-------|-----|----------|-------|
| Phantom Bat | 1 | 12 | Holy Water, Boomerang | 3,000 |
| Medusa | 2 | 12 | Boomerang | 5,000 |
| Mummy Pair | 3 | 12 each | Holy Water | 5,000 each |
| Frankenstein+Igor | 4 | 16 | Holy Water | 7,000 |
| Death | 5 | 16 | Holy Water | 10,000 |
| Dracula P1 | 6 | 16 | Holy Water | 15,000 |
| Dracula P2 | 6 | 16 | Holy Water | 50,000 |

## Appendix B: Quick Reference — Sub-Weapon Comparison

| Weapon | Damage | Cost | Range | Best Situation |
|--------|--------|------|-------|---------------|
| Dagger | 1 | 1 | Full screen | Ranged poking |
| Axe | 2 | 1 | Arc overhead | Enemies above |
| Holy Water | 1x8 | 1 | Ground area | Boss stun-lock |
| Boomerang | 2x2 | 1 | Medium + return | Safe ranged |
| Stopwatch | 0 | 5 | Screen-wide | Freeze enemies |

## Appendix C: Block-by-Block Map

| Block | Stage | Setting | Boss |
|-------|-------|---------|------|
| 1 | 1 | Castle exterior | — |
| 2 | 1 | Entrance hall | — |
| 3 | 1 | Main hall | Phantom Bat |
| 4 | 2 | Outdoor walkway | — |
| 5 | 2 | Interior corridors | — |
| 6 | 2 | Upper corridors | Medusa |
| 7 | 3 | Underground cavern | — |
| 8 | 3 | Deep caverns | — |
| 9 | 3 | Cavern exit | Mummy Pair |
| 10 | 4 | Stone passages | — |
| 11 | 4 | Laboratory | — |
| 12 | 4 | Boss passage | Frankenstein |
| 13 | 5 | Castle towers | — |
| 14 | 5 | Upper castle | — |
| 15 | 5 | Tower approach | Death |
| 16 | 6 | Final tower | — |
| 17 | 6 | Inner sanctum | — |
| 18 | 6 | Throne room | Dracula |

---

*This specification is based on Castlevania (1986) by Konami for the Nintendo Entertainment System (NES). Values are sourced from gameplay analysis, ROM data, and community documentation.*
