# Hollow Knight — Complete Game Specification

> A comprehensive specification for faithfully recreating Hollow Knight (Team Cherry, 2017). This document covers every system, mechanic, entity, and interaction required for a full clone.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Mechanics](#3-core-mechanics)
4. [Player Character — The Knight](#4-player-character--the-knight)
5. [Nail Combat System](#5-nail-combat-system)
6. [Soul & Spell System](#6-soul--spell-system)
7. [Charm System](#7-charm-system)
8. [All Areas & Map](#8-all-areas--map)
9. [All Enemies — Complete Stats](#9-all-enemies--complete-stats)
10. [All Bosses](#10-all-bosses)
11. [NPCs & Shops](#11-npcs--shops)
12. [Items & Upgrades](#12-items--upgrades)
13. [UI Layout & Screens](#13-ui-layout--screens)
14. [Audio Design](#14-audio-design)
15. [Save & Progression](#15-save--progression)

---

## 1. Game Overview

- **Genre**: Action-adventure / Metroidvania
- **Perspective**: 2D side-scrolling
- **Input**: D-pad/analog (movement), Jump, Attack (Nail), Spell/Cast, Dash, Focus/Heal, Quick Map, Inventory/Charms
- **Objective**: Explore the fallen kingdom of Hallownest, uncover its history, and confront the source of the Infection.
- **Lose Condition**: HP (Masks) reaches zero. Shade spawns at death location. Respawn at last bench.
- **Win Condition**: Multiple endings depending on items collected and actions taken. Minimum: Defeat Hollow Knight in Black Egg Temple.
- **Estimated playtime**: 25-40 hours for main story, 60+ for completions.

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Native resolution | 1920 x 1080 pixels |
| Internal render | Variable (Unity engine, resolution-independent) |
| Frame rate | 60 FPS target |
| Engine | Unity 2D |
| Physics | Custom 2D physics (not Unity physics) |
| Tile size | Varies (mostly 64x64 for environment collision tiles) |

### Coordinate System

- Unity world coordinates (floating point).
- Player position tracked in world space.
- Camera follows player with lerp smoothing.
- Each area is a separate Unity scene loaded via transitions.

### Game Loop

```
1. Process input (with input buffering)
2. Update player state machine
3. Update enemy AI for all active enemies
4. Update projectiles and spells
5. Update environmental hazards (acid, spikes)
6. Check collisions
7. Update camera (follow player, room boundaries)
8. Update particle systems
9. Update UI/HUD
10. Render (parallax backgrounds -> tilemap -> entities -> player -> effects -> HUD)
```

---

## 3. Core Mechanics

### Movement

| Parameter | Value |
|-----------|-------|
| Walk speed | 8.3 units/sec |
| Sprint speed (not available by default) | N/A |
| Jump velocity | 12.65 units/sec upward |
| Short hop (release early) | Velocity set to min(current, 2.0) when button released while ascending |
| Gravity | 40 units/sec² |
| Max fall speed | 20 units/sec |
| Wall slide speed | 4.0 units/sec (when touching wall while falling, with Mantis Claw) |
| Coyote time | 5 frames |
| Jump buffer | 4 frames |
| Turn speed | Instant (1 frame) |
| Acceleration | Instant (full speed in 1 frame on ground) |
| Air control | Full horizontal control in air (same speed as ground) |

### Dash (Mothwing Cloak)

| Parameter | Value |
|-----------|-------|
| Dash speed | 20.0 units/sec |
| Dash duration | 0.35 seconds (21 frames) |
| Dash cooldown | 0.6 seconds (36 frames) |
| Direction | Horizontal only (left/right, direction Kight is facing) |
| Invincibility | Frames 2-16 of dash (with Shade Cloak upgrade) |
| Shade Cloak | Upgraded dash through enemies/shadows. Cooldown: 1.5 seconds. |

### Wall Jump / Cling (Mantis Claw)

| Parameter | Value |
|-----------|-------|
| Wall slide speed | 4.0 units/sec downward |
| Wall jump horizontal velocity | 6.0 units/sec away from wall |
| Wall jump vertical velocity | 12.0 units/sec upward |
| Wall cling | Hold toward wall to cling (0 vertical speed) |
| Re-grab delay | 8 frames before can grab same wall again |

### Double Jump (Monarch Wings)

| Parameter | Value |
|-----------|-------|
| Double jump velocity | 12.0 units/sec upward |
| Available | Once per airborne period, resets on landing |
| Can combine | With wall jump and dash |

### Swimming (Isma's Tear)

- Without Isma's Tear: Acid = instant death (same as spikes).
- With Isma's Tear: Can swim through acid. Speed: 5.0 units/sec.

### Crystal Heart (Super Dash)

| Parameter | Value |
|-----------|-------|
| Charge time | 0.75 seconds (hold while on wall) |
| Dash speed | 25.0 units/sec horizontal |
| Duration | Infinite until hitting a wall or canceling |
| Cancel | Press jump to cancel and launch upward slightly |
| Direction | Horizontal, in direction Knight faces when activated |

### Dream Nail

| Parameter | Value |
|-----------|-------|
| Swing range | Short (melee range, ~2 units) |
| Swing time | 1.2 seconds (slow compared to regular nail) |
| Effect | Reads enemy thoughts (dialog text appears). Generates 33 Soul. |
| Combat use | Does 0 damage. Only for Soul generation and specific dream targets. |
| Dream Gate | Place a warp point; teleport to it from anywhere. Costs 1 Essence. |

---

## 4. Player Character — The Knight

### Masks (Health)

| Stat | Value |
|------|-------|
| Starting masks | 5 |
| Maximum masks | 9 (with 4 Mask Shards) |
| Mask Shards needed | 4 per additional mask |
| Total Mask Shards in game | 16 (= 4 extra masks) |
| Damage per enemy hit | Usually 1 mask (some deal 2) |
| Invincibility after hit | 1.2 seconds (72 frames) |
| Knockback distance | ~3 units in direction away from source |
| Knockback duration | 0.2 seconds |

### Shade

- On death, a Shade spawns at the death location.
- Shade holds all Geo (currency) the player had.
- Player respawns at last rested bench with 0 Geo and reduced max Soul (vessel cracked).
- To recover: Find and defeat the Shade.
- Shade HP: Scales with player's nail damage (approximately 15-20 HP).
- Shade attacks: Lunges at player, shoots Soul projectiles.
- If player dies again before recovering Shade: Previous Shade (and its Geo) is lost permanently.
- Shade can be summoned at Confessor Jiji for 1 Rancid Egg (returns Geo without combat).

### Hitbox

| State | Size | Notes |
|-------|------|-------|
| Standing | 0.65 x 1.4 units | Slightly smaller than sprite |
| Jumping | 0.65 x 1.2 units | Slightly compressed |
| Dashing | 0.65 x 1.0 units | Low profile |
| Wall clinging | 0.65 x 1.4 units | Same as standing |

---

## 5. Nail Combat System

### Nail Attacks

| Direction | Hitbox Size | Hitbox Position | Notes |
|-----------|------------|-----------------|-------|
| Side slash | 2.5 x 0.7 units | Forward from Knight | Default slash |
| Up slash | 0.7 x 2.5 units | Above Knight | Hold up + attack |
| Down slash | 0.7 x 2.5 units | Below Knight | Hold down + attack (in air) |

### Nail Stats by Upgrade

| Nail | Damage | Cost (Geo) | Pale Ore Required |
|------|--------|------------|-------------------|
| Old Nail | 5 | — | — |
| Sharpened Nail | 9 | 250 | 0 |
| Channeled Nail | 13 | 800 | 1 |
| Coiled Nail | 17 | 2000 | 2 |
| Pure Nail | 21 | 4000 | 3 |

### Attack Timing

| Parameter | Value |
|-----------|-------|
| Slash duration | 0.35 seconds |
| Recovery (before next slash) | 0.41 seconds |
| Total attack cycle | 0.76 seconds (~1.3 attacks/sec) |
| Movement during slash | Possible (no lock) |
| Recoil on enemy hit | Knight pushed back 2 units from enemy (horizontal) or bounced up 8 units (downslash on enemy/bounce surface) |

### Nail Arts (Nailmaster abilities)

| Nail Art | Source | Charge Time | Damage | Effect |
|----------|--------|-------------|--------|--------|
| Cyclone Slash | Nailmaster Mato | 1.2 sec | 3 hits of nail damage | Spin attack, hits multiple times |
| Dash Slash | Nailmaster Oro | 1.2 sec | 2.5x nail damage | Long-range dash forward slash |
| Great Slash | Nailmaster Sheo | 1.2 sec | 2.5x nail damage | Powerful overhead slash, wide hitbox |

Charging: Hold attack button. Visual indicator (flash) at full charge. Release to perform Art.

---

## 6. Soul & Spell System

### Soul

| Parameter | Value |
|-----------|-------|
| Max Soul | 99 |
| Soul per nail hit | 11 |
| Soul per Dream Nail hit | 33 |
| Focus (heal) cost | 33 Soul |
| Spell cost | 33 Soul |
| Soul Vessels | Extra storage. Each holds 33 Soul. 3 available (total max: 99 + 99 = 198 with all) |
| Soul Vessel Shards | 3 fragments = 1 Soul Vessel. 9 total fragments in game = 3 vessels. |

### Healing (Focus)

| Parameter | Value |
|-----------|-------|
| Focus time | 0.89 seconds (hold spell button) |
| HP restored | 1 mask |
| Soul cost | 33 |
| Movement | Cannot move during Focus (rooted) |
| Cancel | Release button or take damage |
| Quick Focus (charm) | 0.59 seconds |
| Deep Focus (charm) | Heals 2 masks per Focus, costs 33 Soul, takes 1.3 seconds |

### Spells

| Spell | Cost | Damage | Behavior | Upgrade |
|-------|------|--------|----------|---------|
| Vengeful Spirit | 33 Soul | 15 | Horizontal fireball, passes through enemies | Shade Soul (30 damage, larger hitbox) |
| Desolate Dive | 33 Soul | 15 ground + 20 shockwave | Slam downward, invincible during, AOE on landing | Descending Dark (30 + 40 damage, larger AOE) |
| Howling Wraiths | 33 Soul | 20 (multi-hit) | Upward blast of spirits | Abyss Shriek (40 damage, much larger area) |

### Spell Upgrades

Found in specific locations (Elegance Key areas, Abyss):
- **Shade Soul**: Replace Vengeful Spirit. Found in Soul Sanctum (Elegant Key + boss fight).
- **Descending Dark**: Replace Desolate Dive. Found in Crystal Peak.
- **Abyss Shriek**: Replace Howling Wraiths. Found in The Abyss.

---

## 7. Charm System

### Charm Basics

- Charms are passive abilities equipped at benches.
- Each charm costs a number of **Notch** slots.
- Starting Notches: 3.
- Maximum Notches: 11 (with all Notch upgrades found/purchased).
- **Overcharming**: Equipping charms exceeding total Notches is possible but doubles all damage taken.

### All Charms

| # | Charm Name | Notch Cost | Effect |
|---|-----------|-----------|--------|
| 1 | Wayward Compass | 1 | Shows Knight's position on the map |
| 2 | Gathering Swarm | 1 | Geo attracted to Knight automatically |
| 3 | Stalwart Shell | 2 | Invincibility time after hit increased to 1.7 sec |
| 4 | Soul Catcher | 2 | +3 Soul per nail hit (14 total) |
| 5 | Shaman Stone | 3 | Spell damage +33%, spell size increased |
| 6 | Soul Eater | 4 | +8 Soul per nail hit (19 total) |
| 7 | Dashmaster | 2 | Dash cooldown halved (0.3 sec). Can dash downward. |
| 8 | Sprintmaster | 1 | Walk speed +20% (10.0 units/sec) |
| 9 | Grubsong | 1 | Gain 15 Soul when taking damage |
| 10 | Grubberfly's Elegy | 3 | At full health, nail swings fire projectiles (half nail damage) |
| 11 | Fragile Heart | 2 | +2 masks. Breaks on death (repairable for Geo). |
| 12 | Fragile Greed | 2 | Enemies drop +50% more Geo. Breaks on death. |
| 13 | Fragile Strength | 3 | Nail damage +50%. Breaks on death. |
| 14 | Spell Twister | 2 | Spells cost 24 Soul instead of 33 |
| 15 | Steady Body | 1 | No recoil knockback when hitting enemies |
| 16 | Heavy Blow | 2 | Enemies knocked back further on hit |
| 17 | Quick Slash | 3 | Attack speed +50% (0.51 sec cycle vs 0.76) |
| 18 | Longnail | 2 | Nail reach +15% |
| 19 | Mark of Pride | 3 | Nail reach +25% |
| 20 | Fury of the Fallen | 2 | At 1 mask: nail damage +75%, red visual effect |
| 21 | Thorns of Agony | 1 | When hit, thorns burst outward dealing 2x nail damage |
| 22 | Baldur Shell | 2 | While Focusing, protective shell blocks up to 4 hits |
| 23 | Flukenest | 3 | Vengeful Spirit replaced by swarm of flukes (many small projectiles) |
| 24 | Defender's Crest | 1 | Dung cloud surrounds Knight, dealing 1 damage/sec to nearby enemies |
| 25 | Glowing Womb | 2 | Spawns hatchlings every 4 seconds (cost 6 Soul each). Hatchlings home on enemies. |
| 26 | Quick Focus | 3 | Focus time reduced to 0.59 seconds |
| 27 | Deep Focus | 4 | Focus heals 2 masks, but takes 65% longer |
| 28 | Lifeblood Heart | 2 | +2 temporary blue masks at bench rest |
| 29 | Lifeblood Core | 3 | +4 temporary blue masks at bench rest |
| 30 | Joni's Blessing | 4 | All masks become blue (temporary). Cannot heal. Max masks +40% (rounded). |
| 31 | Hiveblood | 4 | Regenerate 1 mask every 10 seconds. Only heals most recent damage. |
| 32 | Dream Wielder | 1 | Dream Nail charges faster, generates +66% Soul |
| 33 | Dreamshield | 3 | Orbiting shield that blocks projectiles and deals damage |
| 34 | Weaversong | 2 | Spawns 3 mini-spiders that attack enemies (3 damage each) |
| 35 | Shape of Unn | 2 | Can move slowly (slug form) while Focusing |
| 36 | Unbreakable Heart | 2 | +2 masks. Cannot break. (Upgraded from Fragile Heart) |
| 37 | Unbreakable Greed | 2 | +50% Geo drops. Cannot break. |
| 38 | Unbreakable Strength | 3 | +50% nail damage. Cannot break. |
| 39 | Carefree Melody | 3 | Random chance (escalating) to negate damage. |
| 40 | Kingsoul / Void Heart | 5/0 | Kingsoul: Generates 4 Soul every 2 sec. Void Heart: 0 notch, enables true ending. |

### Charm Combos (Synergies)

| Combo | Charms | Effect |
|-------|--------|--------|
| Spore Shroom + Defender's Crest | 17 + 24 | Healing cloud also deals poison damage |
| Grubsong + Weaversong | 9 + 34 | Weaverlings generate Soul on hit |
| Flukenest + Defender's Crest | 23 + 24 | Flukes become exploding dung flukes |
| Flukenest + Shaman Stone | 23 + 5 | Larger, more damaging flukes |
| Longnail + Mark of Pride | 18 + 19 | Stacks: +40% total nail reach |

---

## 8. All Areas & Map

### Area Overview

| # | Area | Benches | Enemies (types) | Boss(es) | Key Items |
|---|------|---------|------------------|----------|-----------|
| 1 | King's Pass | 0 | 3 | None | Tutorial area |
| 2 | Dirtmouth | 1 | 0 | None | Hub town, shops |
| 3 | Forgotten Crossroads | 3 | 12 | False Knight, Gruz Mother | Vengeful Spirit, City Crest |
| 4 | Greenpath | 2 | 10 | Hornet (1st fight), Massive Moss Charger | Mothwing Cloak (Dash) |
| 5 | Fungal Wastes | 2 | 11 | Mantis Lords | Mantis Claw (Wall Jump) |
| 6 | City of Tears | 3 | 14 | Soul Master, Watcher Knights | Desolate Dive, Shopkeeper |
| 7 | Resting Grounds | 1 | 5 | None (Spirit Glade) | Dream Nail, Seer |
| 8 | Crystal Peak | 2 | 8 | Crystal Guardian (x2) | Crystal Heart (Super Dash), Descending Dark |
| 9 | Royal Waterways | 1 | 8 | Dung Defender, Flukemarm | Isma's Tear |
| 10 | Howling Cliffs | 1 | 4 | Grimm (DLC) | Grimm Troupe content |
| 11 | Deepnest | 2 | 15 | Nosk | Tram Pass |
| 12 | Ancient Basin | 1 | 6 | Broken Vessel | Monarch Wings (Double Jump) |
| 13 | Kingdom's Edge | 1 | 8 | Hornet (2nd fight), Markoth | King's Brand |
| 14 | Queen's Gardens | 1 | 7 | Traitor Lord | Half of Kingsoul |
| 15 | Fog Canyon | 1 | 4 | Uumuu | Teacher's Archive |
| 16 | The Abyss | 0 | 3 | None | Shade Cloak, Abyss Shriek, Void Heart |
| 17 | White Palace | 1 | 0 (platforming) | Path of Pain (optional) | Other half of Kingsoul |
| 18 | Infected Crossroads | 0 | 8 (infected variants) | Broken Vessel (rematch) | — |
| 19 | Black Egg Temple | 0 | 0 | Hollow Knight / Radiance | Endings |
| 20 | Godhome (DLC) | 1 | All (boss rush) | All bosses + Absolute Radiance | — |

### Map Connectivity (Simplified)

```
              Howling Cliffs
                    |
               Dirtmouth
                    |
          Forgotten Crossroads ---- Crystal Peak
         /     |        \               |
   Greenpath   |     Fog Canyon    Ancient Basin
        |      |         |              |
  Fungal Wastes|    Queen's Gardens  Kingdom's Edge
        |      |         |              |
    Deepnest   |    City of Tears ------+
               |    /          \
        Resting Grounds  Royal Waterways
                              |
                          The Abyss
```

### Map System

- Map starts mostly blank.
- **Cornifer** (cartographer NPC) sells area maps for Geo (found in each area).
- Exploring rooms fills in map details.
- Map only updates at benches (newly explored rooms shown after resting).
- **Wayward Compass** charm: Shows Knight's position on map (otherwise, position is not shown).

### Map Prices (Cornifer)

| Area | Map Price (Geo) |
|------|----------------|
| Forgotten Crossroads | 30 |
| Greenpath | 60 |
| Fungal Wastes | 75 |
| City of Tears | 90 |
| Crystal Peak | 112 |
| Royal Waterways | 75 |
| Deepnest | 38 |
| Ancient Basin | 112 |
| Kingdom's Edge | 112 |
| Queen's Gardens | 150 |
| Howling Cliffs | 75 |
| Fog Canyon | 150 |
| Resting Grounds | 75 |

---

## 9. All Enemies — Complete Stats (Selection)

### Forgotten Crossroads

| Enemy | HP | Damage | Geo Drop | Behavior |
|-------|----|--------|----------|----------|
| Crawlid | 4 | 1 | 2 | Walks back and forth on ground |
| Tiktik | 3 | 1 | 2 | Walks along walls and ceilings |
| Gruzzer | 5 | 1 | 3 | Flies in sine wave pattern, charges when near |
| Husk Guard | 15 | 1 | 20 | Stands guard, lunges with weapon when player approaches |
| Leaping Husk | 8 | 1 | 8 | Leaps toward player in arcs |
| Vengefly | 4 | 1 | 3 | Flying, swoops at player |
| Husk Bully | 20 | 1 | 12 | Charges at player, can be knocked back |
| Elder Baldur | 15 | 1 | 0 | Rolls into ball, blocks passage. Break shell. |
| Aspid (Primal) | 15 | 2 | 20 | Flies, shoots 3-way projectile spread |
| Volatile Gruzzer | 8 | 2 | 0 | Explodes on death, deals AOE damage |

### Greenpath

| Enemy | HP | Damage | Geo Drop | Behavior |
|-------|----|--------|----------|----------|
| Mossy Vagabond | 15 | 1 | 8 | Walks, throws moss projectile |
| Moss Knight | 30 | 2 | 25 | Sword-wielding, 3-hit combo |
| Squit | 5 | 1 | 4 | Small flying insect, dives at player |
| Obble | 6 | 1 | 3 | Bounces along ground |
| Fool Eater | 20 | 1 | 15 | Stationary plant, snaps when player near |
| Massive Moss Charger | 60 | 2 | 50 | Mini-boss: charges across arena, only vulnerable during charge |

### City of Tears

| Enemy | HP | Damage | Geo Drop | Behavior |
|-------|----|--------|----------|----------|
| Husk Sentry | 20 | 1 | 15 | Guard with lance, attacks when near |
| Heavy Sentry | 25 | 1 | 20 | Armored guard, slow but strong |
| Winged Sentry | 15 | 1 | 12 | Flying guard, sword swipes |
| Soul Twister | 20 | 2 | 30 | Teleports, fires homing Soul orb |
| Soul Warrior | 60 | 2 | 50 | Mini-boss: fast sword attacks + Soul projectiles |
| Great Husk Sentry | 35 | 2 | 30 | Large guard, shield bash + lance combo |

### Deepnest

| Enemy | HP | Damage | Geo Drop | Behavior |
|-------|----|--------|----------|----------|
| Dirtcarver | 10 | 1 | 5 | Burrows underground, surfaces near player |
| Deepling | 12 | 1 | 8 | Spider-like, drops from ceiling |
| Carver Hatcher | 20 | 1 | 8 | Produces baby spiders (3 HP each) every 5 seconds |
| Stalking Devout | 25 | 2 | 20 | Aggressive mantis, charges and slashes |
| Nosk | 200 | 2 | — | Boss: Shape-shifter, ceiling charge + ground slam patterns |
| Corpse Creeper | 15 | 1 | 10 | Reanimated corpse, walks toward player |

---

## 10. All Bosses

### Boss Stats & Patterns

#### False Knight (Forgotten Crossroads)
- **HP**: 355 (armor phases)
- **Arena**: Flat room, 20 units wide
- **Phase 1** (HP > 200): Leap attack (jumps to player position, slams mace). Shockwave on landing (travels 5 units).
  - Jump height: 8 units. Hang time: 0.8 sec.
  - Mace slam: 2 damage.
  - Shockwave: 1 damage, speed 8 units/sec.
- **Stagger** (every ~100 damage): Falls over, armor opens revealing Maggot inside. Hit Maggot for bonus damage.
  - Stagger duration: 3 seconds.
  - Maggot has no separate HP; damage counts toward total.
- **Phase 2** (HP < 200): Adds ground pound (jump + slam creating 2 shockwaves in both directions). Rocks fall from ceiling (3 rocks, 1 damage each).
- **Death**: Maggot exposed, floor collapses.

#### Hornet Protector (Greenpath)
- **HP**: 225
- **Arena**: Medium room, platforms at varying heights
- **Attacks**:
  - Lunge: Dashes toward player at 15 units/sec. Damage: 1. Range: 8 units.
  - Needle Throw: Throws needle in arc. Returns to Hornet. Damage: 1. Speed: 12 units/sec.
  - Aerial Dive: Jumps up, then dives at player position. Damage: 1.
  - Silk Barrage: Throws 5 silk threads in spread pattern. Damage: 1 each.
- **Stagger**: At 100 and 50 HP remaining, pauses briefly (2 seconds, surrounded by silk — touching silk = 1 damage).
- **Speed increases**: Below 100 HP, attack frequency +30%.

#### Mantis Lords (Fungal Wastes)
- **HP**: 210 each (1 + 2 simultaneously)
- **Arena**: Rectangular room with 3 platforms (top, middle, bottom).
- **Phase 1** (1 Mantis Lord): Attacks one at a time.
  - Dash Slash: Charges across arena at 16 units/sec. Damage: 1.
  - Dive Attack: From wall, dives at 45° angle. Damage: 1.
  - Boomerang: Throws disc projectile. Damage: 1. Curves back.
  - Pattern: Attack -> retreat to wall -> 1 sec pause -> attack.
- **Phase 2** (2 Mantis Lords): Both attack simultaneously with coordinated patterns.
  - One dashes while other dives.
  - Increased frequency (0.5 sec between attacks).
  - Combined HP bar.

#### Soul Master (City of Tears)
- **HP**: 385
- **Phase 1** (HP > 175):
  - Teleports to random position, fires 4 Soul orbs in compass directions. Orb damage: 1. Speed: 6 units/sec.
  - Homing Dive: Teleports above player, dives down. Damage: 2. Shockwave: 1.
  - Orbit: Creates ring of Soul orbs that rotate and close inward.
  - Teleport frequency: every 2 seconds.
- **Fake Death**: At 175 HP, appears to die. Floor collapses to lower arena.
- **Phase 2** (HP < 175): Faster, erratic.
  - Teleports every 1 second.
  - Orbs fire in 6 directions.
  - Spins across arena (dash attack, 3 laps). Speed: 18 units/sec. Damage: 2.

#### Dung Defender (Royal Waterways)
- **HP**: 365
- **Arena**: Flat with dung pits on sides
- **Attacks**:
  - Burrow: Dives underground, surfaces under player. Damage: 1.
  - Dung Toss: Throws dung ball in arc. Explodes on landing (AOE). Damage: 1.
  - Rolling Charge: Curls into ball, rolls across arena. Speed: 12 units/sec. Damage: 1.
  - Laugh: Occasionally pauses to laugh ("Doma, doma!"). Free hits.
- **Phase 2** (HP < 150): Throws 3 dung balls simultaneously. Burrow+surface faster.

#### Hollow Knight (Black Egg Temple — Final Boss)
- **HP**: 1000
- **Phase 1** (HP > 700):
  - Triple Slash: 3 sequential nail swings. Damage: 1 each.
  - Lunge: Dashes forward with nail extended. Damage: 2.
  - Parry: Blocks player attack, counters with slam.
- **Phase 2** (HP 700-400):
  - Adds Pillars: Summons Soul pillars from ground (4 pillars, 1 damage each).
  - Infection Blast: Horizontal beam of infection. Damage: 2. Sweeps up.
  - Belly stab: Stabs self (story-related), leaving opening for attacks.
- **Phase 3** (HP < 400):
  - Frequently stabs self (more openings but erratic).
  - Infection Orbs: Sprays orange orbs in all directions. Damage: 1.
  - Reduced attack variety; primarily flails.
- **Endings**:
  - Without Void Heart: Hollow Knight dies, player takes its place (Ending 1).
  - With Void Heart: Hornet pins Hollow Knight, player Dream Nails it to enter Radiance fight.

#### The Radiance (Dream Boss — True Final Boss)
- **HP**: 1700
- **Arena**: Floating platforms in dream space
- **Phase 1**:
  - Sword Rain: Swords fall from top of screen in wave pattern. Damage: 2. 12 swords, speed 15 units/sec.
  - Beam Sweep: Horizontal beam sweeps across platform level. Damage: 2. Duration: 1.5 sec.
  - Orb Barrage: 6 orbs fired in spread. Damage: 1. Speed: 8 units/sec.
  - Spike Wall: Wall of spikes closes from one side. Must dash through gap. Damage: 2.
- **Phase 2** (HP < 1100):
  - Platforms become smaller and more spread.
  - All attacks more frequent and combined.
  - Adds: Floor spikes (temporary, 3 second duration).
- **Phase 3** (HP < 500):
  - Platforms disappear and reappear.
  - Adds: Beam from all 4 directions sequentially.
  - Beam speed increased.
- **Phase 4** (HP < 200):
  - Ascending section. Platforms rise upward.
  - Must climb toward Radiance while avoiding attacks.
  - Final hit: Single nail strike in cinematic moment.

---

## 11. NPCs & Shops

### Dirtmouth NPCs

| NPC | Service | Details |
|-----|---------|---------|
| Elderbug | Dialog | Story hints, reacts to game progress |
| Sly (Shopkeeper) | Shop | Items, charms, keys. Must be rescued from Forgotten Crossroads first. |
| Iselda | Map shop | Sells map-related items (pins, quill, markers) |
| Bretta | Dialog | Rescued from Fungal Wastes, optional admirer |
| Grimm (DLC) | Grimm Troupe quest | Flame collection questline |

### Sly's Shop

| Item | Price (Geo) | Effect |
|------|------------|--------|
| Gathering Swarm (charm) | 300 | Auto-collect Geo |
| Stalwart Shell (charm) | 200 | Longer invincibility |
| Lumafly Lantern | 1800 | Illuminates dark areas |
| Simple Key | 950 | Opens certain locked doors |
| Elegant Key | 800 | Opens Soul Sanctum door |
| Mask Shard 1 | 150 | 1/4 extra mask |
| Mask Shard 2 | 500 | 1/4 extra mask |
| Mask Shard 3 | 800 | 1/4 extra mask |
| Mask Shard 4 | 1500 | 1/4 extra mask |
| Vessel Fragment 1 | 550 | 1/3 extra Soul Vessel |
| Vessel Fragment 2 | 900 | 1/3 extra Soul Vessel |

### Iselda's Shop

| Item | Price | Effect |
|------|-------|--------|
| Quill | 120 | Required to update map while exploring |
| Bench Pin | 100 | Mark bench locations on map |
| Stag Pin | 100 | Mark Stag Station locations |
| Vendor Pin | 100 | Mark shop locations |
| Cocoon Pin | 100 | Mark Lifeblood Cocoons |
| Hot Spring Pin | 100 | Mark Hot Springs |
| Warrior Pin | 100 | Mark Warrior Graves |

### Leg Eater (Fungal Wastes)

| Item | Price | Effect |
|------|-------|--------|
| Fragile Heart | 350 | +2 masks, breaks on death |
| Fragile Greed | 250 | +50% Geo drops, breaks on death |
| Fragile Strength | 600 | +50% nail damage, breaks on death |
| Repair any | 200-350 | Fixes broken fragile charm |

### The Nailsmith (City of Tears)

Upgrades the nail (see Nail Stats table above). Requires Geo + Pale Ore for higher tiers.

---

## 12. Items & Upgrades

### Movement Abilities (in order of typical acquisition)

| Ability | Location | Effect |
|---------|----------|--------|
| Mothwing Cloak | Greenpath (after Hornet 1) | Dash (horizontal) |
| Mantis Claw | Fungal Wastes (Mantis Village) | Wall jump/cling |
| Crystal Heart | Crystal Peak | Super Dash (long horizontal charge) |
| Monarch Wings | Ancient Basin (after Broken Vessel) | Double jump |
| Isma's Tear | Royal Waterways | Swim through acid |
| Shade Cloak | The Abyss | Shadow Dash (invincible dash through enemies) |
| Dream Nail | Resting Grounds | Read minds, enter dreams |

### Pale Ore Locations (6 total, 3 needed for nail upgrades)

1. Forgotten Crossroads — Grub reward
2. Crystal Peak — hidden room
3. Deepnest — Nosk reward
4. Kingdom's Edge — Colosseum Trial 2 reward
5. Ancient Basin — secret room
6. Resting Grounds — Seer reward (300 Essence)

### Stag Stations (Fast Travel)

11 stations throughout Hallownest. Unlock by finding and paying a small Geo fee (50-200).
Access by sitting at station bench and selecting destination.

---

## 13. UI Layout & Screens

### In-Game HUD

```
+------------------------------------------------------------------+
|  [Mask1][Mask2][Mask3][Mask4][Mask5]     [SoulOrb]               |
|                                          [VesselOrbs]            |
|                                                                   |
|                                                                   |
|                    (GAMEPLAY AREA)                                |
|                                                                   |
|                                                                   |
|                                                                   |
|  [Geo counter: 1234]                                             |
+------------------------------------------------------------------+
```

- **Masks**: Top-left. White = full, cracked = empty, blue = lifeblood (temporary).
- **Soul Orb**: Top-right. Large circle that fills with white (Soul). Empties as spells/focus used. Divided into 3 segments of 33.
- **Vessel Orbs**: Below Soul Orb. Smaller circles (additional Soul storage).
- **Geo counter**: Bottom-left. Shows current Geo. Hidden when 0.
- **All HUD elements**: Animate in/out. Fade after 3 seconds of inactivity.

### Inventory / Charm Screen

```
+--------------------------------------------------+
|  CHARMS                                           |
|  Notches: [■][■][■][■][□][□][□][□][□][□][□]     |
|  (filled = used, empty = available)               |
|                                                    |
|  [Charm Grid - 5 columns x 8 rows]               |
|  [Selected charm name and description]            |
|                                                    |
|  EQUIPPED: [C1] [C2] [C3] [C4]                   |
|                                                    |
|  KEY ITEMS: [list of collected key items]         |
+--------------------------------------------------+
```

### Map Screen

```
+--------------------------------------------------+
|  [Area Name]                                       |
|                                                    |
|  [Full area map with rooms as rectangles]         |
|  [Player position: white icon (with Wayward      |
|   Compass)]                                       |
|  [Pins placed by player: colored icons]           |
|  [Unexplored rooms: dark/hidden]                  |
|                                                    |
|  [Legend: bench, stag, shop icons]                |
+--------------------------------------------------+
```

---

## 14. Audio Design

### Music

| Area | Track | Style | BPM |
|------|-------|-------|-----|
| Dirtmouth | "Dirtmouth" | Melancholic piano + strings | 80 |
| Forgotten Crossroads | "Crossroads" | Eerie, sparse | 90 |
| Greenpath | "Greenpath" | Lush, natural, peaceful | 100 |
| City of Tears | "City of Tears" | Piano + rain, somber | 85 |
| Fungal Wastes | "Fungal Wastes" | Quirky, bouncy | 95 |
| Crystal Peak | "Crystal Peak" | Crystalline, ringing | 110 |
| Deepnest | "Deepnest" | Sparse, terrifying, ambient | 60 |
| Resting Grounds | "Resting Grounds" | Peaceful, ethereal | 75 |
| Queen's Gardens | "Queen's Gardens" | Grand, floral | 90 |
| Kingdom's Edge | "Kingdom's Edge" | Wind, desolate | 70 |
| The Abyss | "The Abyss" | Dark ambient, void | 50 |
| White Palace | "White Palace" | Grand, imposing | 100 |
| Radiance Battle | "Radiance" | Epic orchestral | 140 |
| Hollow Knight Battle | "Sealed Vessel" | Emotional, intense | 130 |
| Mantis Lords | "Mantis Lords" | Aggressive, rhythmic | 150 |
| Dung Defender | "Dung Defender" | Heroic, jolly | 120 |
| Hornet Battle | "Hornet" | Fast, string-driven | 140 |
| Grimm (DLC) | "Nightmare King" | Waltz, dramatic | 160 |

### Sound Effects

| Sound | Trigger | Description |
|-------|---------|-------------|
| Nail swing | Attack button | Sharp metal whoosh |
| Nail hit (enemy) | Nail connects with enemy | Metallic clang + squish |
| Nail hit (wall) | Swing hits wall | Clank, spark particles |
| Focus heal | Holding spell button | Humming building sound, chime on heal complete |
| Spell cast | Spell fires | Ethereal burst |
| Damage taken | Player hit | Impact thud + slight ring |
| Geo collect | Walking over Geo | Light metallic clink (pitch varies with value) |
| Bench sit | Sitting at bench | Settling sound + sigh |
| Door/gate open | Gate unlocks | Stone grinding |
| Map open | Press map button | Paper unfold |
| Charm equip | Charm slotted | Magical click |
| Boss death | Boss HP reaches 0 | Extended death cry + explosion |
| Dream Nail | Dream Nail swing | Ethereal resonance |
| Dash | Dash ability | Fabric whoosh |
| Wall slide | Sliding on wall | Scraping |
| Double jump | Second jump | Wing flutter |
| Crystal Heart charge | Charging super dash | Building crystal resonance |
| Crystal Heart launch | Super dash fires | Explosive launch |

---

## 15. Save & Progression

### Save System

- Game saves at **benches** (sit to rest, equip charms, and save).
- **Auto-save** on bench rest, area transition, and certain events.
- **Single save slot** per profile (3 profiles available).
- **Saved data**: Player position, all items/charms collected, map exploration state, Geo count, all flags (bosses defeated, NPCs rescued, etc.), completion percentage.

### Completion Percentage

- Base game: 112% maximum.
- Each item/boss/area contributes:
  - Charms: 1% each (40 total)
  - Bosses: 1% each (main bosses)
  - Mask Shards (full masks): 1% per mask
  - Abilities: 2% each
  - Dreamers (3): 1% each
  - DLC content adds additional percentage

### Endings

| Ending | Requirements | Trigger |
|--------|-------------|---------|
| The Hollow Knight | None | Defeat Hollow Knight without Void Heart |
| Sealed Siblings | Have Void Heart, don't Dream Nail | Hornet pins HK, but Knight replaces HK |
| Dream No More | Have Void Heart, Dream Nail Hollow Knight | Enter Radiance fight, defeat Radiance |
| Embrace the Void (DLC) | Complete Godmaster pantheons | Defeat Absolute Radiance in Godhome |
| Delicate Flower | Deliver Delicate Flower to grave | Side quest ending |

---

## Appendix: Timing Constants

| Constant | Value |
|----------|-------|
| Frame rate | 60 FPS |
| Invincibility after damage | 1.2 sec (72 frames) |
| Knockback duration | 0.2 sec (12 frames) |
| Dash duration | 0.35 sec (21 frames) |
| Dash cooldown | 0.6 sec (36 frames) |
| Shade Cloak cooldown | 1.5 sec (90 frames) |
| Focus (heal) time | 0.89 sec (53 frames) |
| Quick Focus time | 0.59 sec (35 frames) |
| Attack cycle (nail) | 0.76 sec (46 frames) |
| Quick Slash cycle | 0.51 sec (31 frames) |
| Nail Art charge | 1.2 sec (72 frames) |
| Wall re-grab delay | 8 frames |
| Jump buffer | 4 frames |
| Coyote time | 5 frames |
| Hiveblood regen | 10 sec |
| Glowing Womb spawn | 4 sec |
| Soul per nail hit | 11 |
| Soul per Dream Nail | 33 |
| Spell/Focus cost | 33 |
