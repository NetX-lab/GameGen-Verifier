# Diablo I — Complete Game Specification

> A comprehensive specification for faithfully recreating the original Diablo (Blizzard North, 1996/1997 PC version). This document covers every system, mechanic, entity, and interaction required for a full recreation. Data sourced from Jarulf's Guide to Diablo and Hellfire, community wikis, and original game data.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Stats & Attributes System](#3-stats--attributes-system)
4. [Character Classes](#4-character-classes)
5. [Leveling & Experience](#5-leveling--experience)
6. [Core Combat Mechanics](#6-core-combat-mechanics)
7. [Magic System — All Spells](#7-magic-system--all-spells)
8. [Dungeon Generation](#8-dungeon-generation)
9. [Monster Types & Stats](#9-monster-types--stats)
10. [Boss Encounters](#10-boss-encounters)
11. [Quest System](#11-quest-system)
12. [Item System](#12-item-system)
13. [Item Affixes — Prefixes & Suffixes](#13-item-affixes--prefixes--suffixes)
14. [Unique Items](#14-unique-items)
15. [Economy & Gold](#15-economy--gold)
16. [Town of Tristram & NPCs](#16-town-of-tristram--npcs)
17. [Shrine System](#17-shrine-system)
18. [Multiplayer](#18-multiplayer)
19. [UI Layout & Screen Flow](#19-ui-layout--screen-flow)
20. [Audio Design](#20-audio-design)

---

## 1. Game Overview

- **Title**: Diablo
- **Developer**: Blizzard North (Condor Games)
- **Publisher**: Blizzard Entertainment
- **Release**: December 31, 1996 (NA), 1997 (EU)
- **Platform**: Windows 95 (original); later Mac OS Classic
- **Genre**: Action RPG (hack-and-slash dungeon crawler)
- **Perspective**: 2.5D isometric (3/4 top-down)
- **Input**: Mouse-driven (left-click move/attack, right-click spell) with keyboard shortcuts
- **Players**: 1 (singleplayer) or 1-4 (multiplayer via Battle.net, LAN, modem, serial)
- **Objective**: Descend through 16 dungeon levels beneath the Cathedral of Tristram, defeat the Lord of Terror Diablo on level 16
- **Win Condition**: Kill Diablo. The hero then plunges Diablo's soulstone into their own forehead, containing the demon
- **Lose Condition**: Character death. In singleplayer, player reloads last save. In multiplayer, corpse drops equipped items on the ground

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Native resolution | 640 x 480 pixels |
| Color depth | 8-bit (256 colors) |
| Display mode | Fullscreen (exclusive) |
| Frame rate target | ~20 FPS (game logic ticks) |
| Rendering | Software-rendered 2D sprite engine |
| Tile size | 64 x 32 pixels (isometric diamond) |
| Dungeon grid | 40 x 40 tiles per level |

### System Requirements (Original)

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | Pentium 60 MHz | Pentium 90 MHz |
| RAM | 8 MB | 16 MB |
| HDD | 30 MB (minimum install) | 450 MB (full install) |
| Video | SVGA (640x480, 256 colors) | SVGA |
| OS | Windows 95 | Windows 95 |
| Audio | DirectSound-compatible | DirectSound-compatible |
| Multiplayer | 14.4k modem, IPX LAN, or Internet | 28.8k+ modem |

### Coordinate System

- Isometric projection: world coordinates map to screen via diamond-shaped tile grid
- Origin at top of the diamond map; X increases to lower-right, Y increases to lower-left
- Each tile subdivides into 4 "dungeon pieces" for rendering detail (32 x 16 each)
- Viewport shows approximately 17 x 17 tiles centered on the player

### Game Loop

```
1. Process input (mouse position, click state, keyboard)
2. Update player movement (pathfinding on tile grid)
3. Update monster AI (target selection, movement, attack)
4. Process combat (to-hit rolls, damage calculation, resistances)
5. Update spell effects (projectiles, AoE timers, duration)
6. Update item timers (durability checks, trap triggers)
7. Check death conditions (player, monsters)
8. Award experience for kills
9. Process environmental interactions (shrines, doors, levers, chests)
10. Render (floor tiles -> walls -> objects -> entities -> projectiles -> UI overlay)
```

### Save System

- **Singleplayer**: Save and load at any time; one save slot per character
- **Multiplayer**: Character saved client-side (no server-side validation); susceptible to editing
- Character files store: stats, inventory, equipped items, spell levels, quest progress, dungeon seed

---

## 3. Stats & Attributes System

### Four Primary Attributes

| Attribute | Abbreviation | Effect |
|-----------|-------------|--------|
| Strength | Str | Increases melee/ranged damage; determines weapon/armor equip requirements |
| Magic | Mag | Determines maximum mana; affects spell damage; determines spellbook read requirements |
| Dexterity | Dex | Increases to-hit chance, armor class, blocking chance; Rogue damage component |
| Vitality | Vit | Increases maximum life |

### Derived Stats

| Derived Stat | Formula |
|-------------|---------|
| Maximum Life | Base_Life + (Vit * Life_Per_Vit) + (clvl * Life_Per_Level) |
| Maximum Mana | Base_Mana + (Mag * Mana_Per_Mag) + (clvl * Mana_Per_Level) |
| Armor Class | Dex / 5 + AC_from_equipment |
| To-Hit (melee) | 50 + Dex/2 + ToHit_items + clvl + class_bonus |
| To-Hit (ranged) | 50 + Dex + ToHit_items + clvl + class_bonus - distance^2/2 |
| To-Hit (magic) | 50 + Mag - 2 * mlvl + class_bonus |
| Blocking | Dex + 2 * (clvl - mlvl) + bonus (bonus bugged to 0 after first game) |
| Character Damage (War) | Str * clvl / 100 |
| Character Damage (Rog) | (Str + Dex) * clvl / 200 |
| Character Damage (Sorc) | Str * clvl / 100 |

### Life & Mana Per Attribute Point

| Class | Life per Vitality | Mana per Magic |
|-------|------------------|----------------|
| Warrior | 2 | 1 |
| Rogue | 2 | 1.5 |
| Sorcerer | 1 | 2 |

---

## 4. Character Classes

### Starting Attributes

| Attribute | Warrior | Rogue | Sorcerer |
|-----------|---------|-------|----------|
| Strength | 30 | 20 | 15 |
| Magic | 10 | 15 | 35 |
| Dexterity | 20 | 30 | 15 |
| Vitality | 25 | 20 | 20 |
| **Starting Life** | **70** | **45** | **30** |
| **Starting Mana** | **10** | **22** | **70** |

### Maximum Attributes (Level 50, no items)

| Attribute | Warrior | Rogue | Sorcerer |
|-----------|---------|-------|----------|
| Strength | 250 | 55 | 45 |
| Magic | 50 | 70 | 250 |
| Dexterity | 60 | 250 | 85 |
| Vitality | 100 | 80 | 80 |
| **Max Life** | **316** | **201** | **138** |
| **Max Mana** | **98** | **173** | **596** |

### Per-Level Gains

| Gain | Warrior | Rogue | Sorcerer |
|------|---------|-------|----------|
| Stat points | 5 | 5 | 5 |
| Life | +2 | +2 | +1 |
| Mana | +1 | +2 | +2 |

### Class-Specific Skills

| Class | Skill | Description |
|-------|-------|-------------|
| Warrior | **Repair** | Restore item durability at cost of -1 max durability. Higher clvl reduces durability penalty. |
| Rogue | **Disarm Trap** | Detect and disarm trapped objects. Success chance scales with Dexterity. |
| Sorcerer | **Recharge Staff** | Restore charges to equipped staff at cost of reduced max charges. Higher clvl reduces charge loss. |

### Class Combat Bonuses

| Property | Warrior | Rogue | Sorcerer |
|----------|---------|-------|----------|
| Melee to-hit bonus | +20 | 0 | 0 |
| Ranged to-hit bonus | 0 | +20 | 0 |
| Magic to-hit bonus | 0 | 0 | +20 |
| Critical hit chance | clvl % | 0 | 0 |
| Critical hit multiplier | 2x damage | N/A | N/A |
| Block bonus | 30 | 20 | 10 |
| Attack speed (base frames) | Fastest melee | Fastest bow | Fastest cast |

---

## 5. Leveling & Experience

### General Rules

- **Maximum character level**: 50
- **Stat points per level**: 5 (freely distributed among Str/Mag/Dex/Vit)
- **No skill points**: Spells are learned from spellbooks found as loot
- Each level also grants automatic Life and Mana bonuses (class-dependent, see above)

### Experience Formula

```
XP gained = Monster_Base_XP * [1.0 + 0.1 * (mlvl - clvl)]
```

- If `clvl >= mlvl + 10`: zero experience gained
- **Multiplayer cap**: min(200 * clvl, XP_to_next_level / 20)
- **Singleplayer**: no cap on XP per kill
- Player must be alive when monster dies and must not have left the level since damaging it

### Experience Table (Selected Levels)

| Level | Total XP Required | XP to Next Level |
|-------|------------------|-----------------|
| 1 | 0 | 2,000 |
| 2 | 2,000 | 2,620 |
| 3 | 4,620 | 3,420 |
| 4 | 8,040 | 4,450 |
| 5 | 12,490 | 5,810 |
| 10 | 58,640 | 16,540 |
| 15 | 188,185 | 46,430 |
| 20 | 534,625 | 130,830 |
| 25 | 1,440,946 | 369,578 |
| 30 | 3,821,993 | 1,048,019 |
| 35 | 10,076,983 | 2,975,667 |
| 40 | 26,595,847 | 8,455,545 |
| 45 | 70,330,529 | 24,068,267 |
| 50 | 1,310,707,109 | (max level) |

### Monster Experience Values

- Each monster type has a base XP value
- Higher dungeon levels have higher base XP monsters
- Cathedral monsters: ~50-200 base XP
- Catacombs monsters: ~200-600 base XP
- Caves monsters: ~600-2,000 base XP
- Hell monsters: ~2,000-8,000 base XP

---

## 6. Core Combat Mechanics

### Melee Attack Sequence

```
1. Player clicks on target monster (or monster attacks player)
2. Calculate to-hit chance:
   Hit% = 50 + Dex/2 + ToHit_items + clvl + class_bonus - target_AC
3. Clamp: always 5% minimum miss chance, always 5% minimum hit chance
4. Roll: random(1-100) <= Hit% means hit
5. If Warrior: check critical hit (clvl% chance for 2x damage)
6. Calculate damage:
   Total_Damage = Character_Damage + Weapon_Damage + Bonus_Damage
   Character_Damage(Warrior) = Str * clvl / 100
   Character_Damage(Rogue) = (Str + Dex) * clvl / 200
   Character_Damage(Sorc) = Str * clvl / 100
   Weapon_Damage = random(min_weapon_dmg, max_weapon_dmg)
7. Apply +% damage modifiers from items
8. Subtract monster resistance if applicable
9. Apply damage to target HP
```

### Ranged Attack Sequence

```
1. Same as melee but:
   Hit% = 50 + Dex + ToHit_items + clvl + class_bonus - target_AC - distance^2/2
2. Arrow/bolt travels to target; can miss if target moves
3. Damage = Character_Damage + Bow_Damage + Bonus_Damage
```

### Monster Attacking Player

```
1. Monster to-hit:
   Hit% = 30 + ToHit_monster + 2*(mlvl - clvl) - player_AC
2. Clamp: 15% minimum hit, 95% maximum hit
3. If hit: check player blocking
   Block% = Dex + 2*(clvl - mlvl) + bonus
   (bonus bugged to 0 except in first game session)
4. If blocked: reduce damage by shield AC, play block animation
5. If not blocked: full damage applied
   Damage = random(monster_min_dmg, monster_max_dmg) - damage_reduction_from_items
```

### Damage Types

| Type | Source | Resistance |
|------|--------|-----------|
| Physical | Melee weapons, arrows, monster melee | Armor Class reduces hit chance; -damage items reduce damage taken |
| Fire | Fire spells, fire arrows, monster fire attacks | Fire Resistance (%) |
| Lightning | Lightning spells, lightning monsters | Lightning Resistance (%) |
| Magic | Magic-type spells, Apocalypse | Magic Resistance (%) |

### Resistance Mechanics

- Resistances range from 0% to 75% maximum for players
- Each point of resistance reduces incoming elemental damage by that percentage
- Monsters can have Resistance (50% damage reduction) or Immunity (0 damage taken) per type
- Three resistance types: Fire, Lightning, Magic

### Hit Recovery (Stun)

- When a character or monster takes damage exceeding 1/4 of their max life in a single hit, they enter a "hit recovery" animation
- During hit recovery, the entity cannot act (stunlocked if repeatedly hit)
- Hit recovery speed can be improved via item suffixes (Balance/Stability/Harmony)

---

## 7. Magic System — All Spells

### Spell Learning

- Spells are learned by reading **Spellbooks** found as loot or purchased
- Each book read increases that spell by 1 level (maximum level 15)
- Magic requirement to read: increases 20% per spell level; caps at 255 Magic for levels approaching 15
- Spells can also be cast from **Scrolls** (single use, no mana cost, lower magic requirement) or **Staves** (limited charges, no mana cost)
- All three classes can learn all spells, but Magic stat caps limit non-Sorcerer progression

### Spellbook Pages

Spells are organized on 4 pages in the spellbook UI:

#### Page 1 — Basic Spells

| Spell | Type | Initial Mana | Mana Decrease/lvl | Min Mana | Magic Req (Book) | Magic Req (Staff) | Effect |
|-------|------|-------------|-------------------|----------|-----------------|-------------------|--------|
| Firebolt | Fire | 6 | 1 | 3 | 15 | 15 | Single fire projectile; Dmg = random(1-10) + slvl + Mag/8 |
| Charged Bolt | Lightning | 6 | 0 | 6 | 25 | 25 | Fires 1+ bolts in spread; bolts = slvl/2 + 3; each bolt deals 1-6 + Mag/4 |
| Holy Bolt | Magic | 7 | 1 | 3 | 20 | 20 | Projectile that only damages Undead and heals allies; Dmg = random(1-6) + slvl |
| Healing | N/A | 8+2*clvl-3*slvl | special | 1 | 17 | 17 | Restores HP = (random(1-10) + clvl + 1) * min(slvl+3, 10) / 8 |
| Heal Other | N/A | 8+2*clvl-3*slvl | special | 1 | 17 | 17 | Same as Healing but targets another player |
| Inferno | Fire | 11 | 1 | 3 | 20 | 20 | Short-range flame stream; Dmg = (random(1-6) + slvl + Mag/8) per tick |
| Fire Wall | Fire | 28 | 2 | 16 | 27 | 27 | Creates wall of fire; Dmg = (random(1-10) + slvl + Mag/2 + 4) per tick |
| Telekinesis | N/A | 15 | 2 | 8 | 33 | 33 | Interact with objects at range; can trigger traps/shrines/doors remotely |

#### Page 2 — Intermediate Spells

| Spell | Type | Initial Mana | Mana Decrease/lvl | Min Mana | Magic Req (Book) | Magic Req (Staff) | Effect |
|-------|------|-------------|-------------------|----------|-----------------|-------------------|--------|
| Lightning | Lightning | 10 | 1 | 3 | 20 | 20 | Beam of lightning; Dmg = (random(1-10) + slvl + Mag/2) per frame hit |
| Town Portal | N/A | 35 | 3 | 18 | 20 | 20 | Opens portal to Tristram; persists until re-entered or new portal cast |
| Flash | Lightning | 30 | 2 | 16 | 33 | 33 | AoE damage around caster; Dmg = random(Mag/2, Mag/2 + Mag*2) |
| Stone Curse | Magic | 60 | 3 | 40 | 51 | 51 | Petrifies target monster for 12s; fails against unique monsters in Hell |
| Phasing | N/A | 12 | 2 | 4 | 25 | 25 | Random teleport within current screen |
| Mana Shield | N/A | 33 | 0 | 33 | 25 | 25 | Damage taken drains mana instead of HP; 1 dmg = 1 mana drained |
| Elemental | Fire | 35 | 2 | 20 | 35 | 35 | Fireball that seeks nearest target; Dmg = (random(2-10) + slvl*2 + Mag/2) * (9/8)^slvl |
| Fireball | Fire | 16 | 1 | 8 | 48 | 48 | Exploding fire projectile; Dmg = (random(1-10) + slvl + clvl + Mag/8) * (9/8)^slvl |

#### Page 3 — Advanced Spells

| Spell | Type | Initial Mana | Mana Decrease/lvl | Min Mana | Magic Req (Book) | Magic Req (Staff) | Effect |
|-------|------|-------------|-------------------|----------|-----------------|-------------------|--------|
| Flame Wave | Fire | 35 | 3 | 20 | 54 | 54 | Wave of fire crossing screen; Dmg = random(1-10) + slvl*2 + Mag/8 |
| Chain Lightning | Lightning | 30 | 1 | 18 | 54 | 54 | Lightning arcing between targets; hits slvl/2 + 6 times per bolt |
| Guardian | Fire | 50 | 2 | 30 | 61 | 61 | Summons fire-breathing dragon head(s); dragon shoots Firebolts at enemies |
| Golem | N/A | 100 | 6 | 60 | 51 | 51 | Summons stone golem; HP = 2*Mag + 10*slvl; one golem at a time |
| Teleport | N/A | 35 | 3 | 15 | 81 | 81 | Instant teleport to cursor location within line of sight |
| Bone Spirit | Magic | 24 | 0 | 24 | 34 | 34 | Homing spirit that deals 1/3 of target's current HP as damage |

#### Page 4 — Expert Spells (Scroll/Staff Only for some)

| Spell | Type | Initial Mana | Mana Decrease/lvl | Min Mana | Magic Req | Effect |
|-------|------|-------------|-------------------|----------|-----------|--------|
| Apocalypse | Fire | 150 | 0 | 150 | N/A (scroll/staff only) | Damages all monsters on screen; Dmg = random(clvl, clvl*6) |
| Nova | Lightning | 60 | 3 | 35 | N/A (scroll/staff only) | Ring of lightning in all directions from caster |
| Resurrect | N/A | 0 | 0 | 0 | N/A (scroll only) | Revives a dead player in multiplayer |
| Identify | N/A | 0 | 0 | 0 | N/A (scroll only) | Reveals properties of an unidentified magic/unique item |
| Infravision | N/A | 0 | 0 | 0 | N/A (scroll only) | Reveals all monsters on current level |

### Spell Type Interactions

| Monster Type | Holy Bolt | Other Magic |
|-------------|-----------|-------------|
| Undead | Full damage | Normal |
| Demon | No damage | Normal |
| Animal | No damage | Normal |

---

## 8. Dungeon Generation

### Overview

All dungeon levels are generated procedurally on a **40 x 40 tile grid**. Generation uses a two-phase process: **predungeon** (abstract walkability layout) followed by **dungeon** (actual tile/wall placement). Each dungeon has preset "set pieces" for stairs, quest areas, and special rooms.

### Dungeon Tilesets

| Tileset | Levels | Visual Theme | Music Track |
|---------|--------|-------------|-------------|
| Cathedral | 1-4 | Gray stone, pillars, arches, wooden doors | "Cathedral" |
| Catacombs | 5-8 | Dark brick, blue-lit, iron gates, corridors | "Catacombs" |
| Caves | 9-12 | Natural rock, lava rivers, open caverns | "Caves" |
| Hell | 13-16 | Red/black stone, pentagrams, fire, flesh walls | "Hell" |

### Cathedral Generation (Levels 1-4)

```
1. Place up to 3 central 10x10 rooms along a primary axis, connected by wide corridors
2. Recursive "budding" (L5roomGen):
   a. Attach 2-, 4-, or 6-tile rooms to existing room edges
   b. Alternate between X and Y axes with 25% axis-switching chance
   c. Creates open-plan spaces without internal walls initially
3. Apply marching squares for wall placement
   - Opposing walls attach to solid tiles for thinner separators
4. Insert 4 free-standing columns in central rooms
5. Add arch colonnades
6. Randomly insert dividing walls: 25% arches, 25% barred arches, 50% solid with doors
7. Place set pieces (stairs, quest rooms)
8. Validate full traversability
```

### Catacombs Generation (Levels 5-8)

```
1. Recursive subdivision of 40x40 area via CreateRoom:
   a. Generate rooms sized 4-9 tiles per side at random positions
   b. Subdivide remaining area into 4 rectangles, shrinking by 2 tiles
   c. Record hallway connections between adjacent rooms
2. Create ASCII map ('.'-floor, '#'-wall, 'D'-door)
3. Draw connecting hallways between room pairs (random width 1-3 tiles)
4. Fill void sections with 5x5 to 12x14 rectangles until 700+ floor tiles
5. Use custom 3x3 pattern matching for tile selection (not standard marching squares)
6. Insert set pieces and validate traversability
```

### Caves Generation (Levels 9-12)

```
1. Begin with single 2x2 room near center
2. DRLG_L3CreateBlock: recursively add 3-4 tile blocks to edges
   - 25% continuation chance per block
   - Edge tiles have 50% floor probability (rough organic boundaries)
3. Four erosion cleanup passes:
   a. Replace diagonal solid pairs with floor randomly
   b. Remove isolated solid tiles surrounded by 8 floor tiles
   c. Roughen long straight walls (50% replacement)
   d. Re-clean diagonals
4. Lava generation: floodfill wall sections < 40 tiles surrounded by floor -> lava pools
5. Add 1-4 lava rivers (7-100 tiles) with bridge tiles for traversability
6. Require 600+ floor tiles or restart
7. Place set pieces and validate
```

### Hell Generation (Levels 13-16)

```
1. Generate 5-6 tile rooms via cathedral-style recursive budding
2. Restrict generation to 20x20 area
3. Add vertical and horizontal corridors to 20x20 edges
4. Mirror predungeon vertically and horizontally to fill full 40x40 grid
5. Apply standard marching squares with cathedral-style wall addition
6. Place set pieces (Lazarus' lair on 15, Diablo's room on 16)
7. Validate full traversability
```

### Common Elements Across All Levels

- **Set pieces**: Pre-authored chunks (stairs up/down, quest rooms) inserted once per level
- **Minisets**: Small 3x3 tile patterns for detail variation (torch sconces, cracks, etc.)
- **Theme rooms**: Detected via floodfill; contain preset objects (shrines, libraries, monster pits, treasure rooms)
- **Tile substitutions**: Common tiles swap visual variants to prevent monotony
- **Fixup routines**: Pattern matching corrects generation faults
- **Lockout detection**: Flood-fill validates that all floor tiles are reachable

---

## 9. Monster Types & Stats

### Monster Categories

All monsters belong to one of three categories affecting spell interactions:
- **Undead**: Vulnerable to Holy Bolt; immune to life steal; immune to Stone Curse on some variants
- **Demon**: Not affected by Holy Bolt
- **Animal**: Not affected by Holy Bolt

### Cathedral Monsters (Levels 1-4)

| Monster | Type | Dungeon Levels | HP (Normal) | AC | Damage | Resistances | Special |
|---------|------|---------------|-------------|-----|--------|-------------|---------|
| Zombie | Undead | 1-2 | 2-3 | 5 | 2-5 | Immune Magic | Slow movement |
| Ghoul | Undead | 2-3 | 3-5 | 10 | 3-10 | Immune Magic | Slow movement |
| Rotting Carcass | Undead | 2-4 | 7-12 | 15 | 5-15 | Immune Magic, Resist Fire | Slow movement |
| Black Death | Undead | 3-5 | 12-20 | 25 | 6-22 | Immune Magic, Resist Fire | **Permanently reduces max HP by 1 on hit** |
| Skeleton | Undead | 1-2 | 1-2 | 2-4 | 1-4 | Immune Magic | Melee |
| Corpse Axe | Undead | 2-3 | 2-3 | 4-7 | 3-5 | Immune Magic | Melee |
| Burning Dead | Undead | 2-4 | 4-6 | 8-12 | 3-7 | Immune Magic/Fire | Melee |
| Horror | Undead | 3-5 | 6-10 | 12-20 | 4-9 | Immune Magic, Resist Fire | Melee |
| Skeleton Archer | Undead | 2-3 | 1-2 | 2-4 | 1-2 | Immune Magic | Ranged |
| Corpse Bow | Undead | 2-4 | 4-8 | 8-16 | 1-4 | Immune Magic | Ranged |
| Burning Dead Archer | Undead | 3-5 | 5-12 | 10-24 | 1-6 | Immune Magic/Fire | Ranged |
| Horror Archer | Undead | 4-6 | 7-22 | 15-45 | 2-9 | Immune Magic, Resist Fire | Ranged |
| Skeleton Captain | Undead | 1-3 | 1-3 | 3-6 | 2-7 | Immune Magic | Heals nearby skeletons |
| Fallen One (Spear) | Animal | 1-3 | 1-2 | 1-4 | 1-3 | None | Flees when allies die |
| Carver (Spear) | Animal | 2-3 | 2-4 | 4-8 | 2-5 | None | Flees when allies die |
| Devil Kin (Spear) | Animal | 2-4 | 6-12 | 12-24 | 3-7 | Resist Fire | Flees when allies die |
| Dark One (Spear) | Animal | 3-5 | 10-18 | 20-36 | 4-8 | Resist Lightning | Flees when allies die |
| Fallen One (Sword) | Animal | 1-3 | 1-2 | 2-5 | 1-4 | None | Flees when allies die |
| Carver (Sword) | Animal | 2-3 | 2-4 | 5-9 | 2-7 | None | Flees when allies die |
| Scavenger | Animal | 1-3 | 1-3 | 3-6 | 1-5 | Resist Fire | Charges at low HP |
| Plague Eater | Animal | 2-4 | 6-12 | 12-24 | 1-8 | Resist Lightning | Charges at low HP |
| Shadow Beast | Animal | 3-5 | 12-18 | 24-36 | 3-12 | Resist Fire | Charges at low HP |
| Bone Gasher | Animal | 4-6 | 14-20 | 28-40 | 5-15 | Resist Lightning | Charges at low HP |
| Hidden | Demon | 2-5 | 4-12 | 8-24 | 3-6 | None | Invisible until near player |
| Stalker | Demon | 5-7 | 15-22 | 30-45 | 8-16 | None | Invisible until near player |
| Fiend | Animal | 2-3 | 1-3 | 3-6 | 1-6 | None | Flying; ranged attack |
| Blink | Animal | 3-5 | 6-14 | 12-28 | 1-8 | None | Flying; teleports |

### Catacombs Monsters (Levels 5-8)

| Monster | Type | Dungeon Levels | HP (Normal) | AC | Damage | Resistances | Special |
|---------|------|---------------|-------------|-----|--------|-------------|---------|
| Unseen | Demon | 6-8 | 17-25 | 35-50 | 12-20 | Resist Magic | Invisible |
| Illusion Weaver | Demon | 8-10 | 20-30 | 40-60 | 16-24 | Resist Magic/Fire | Invisible |
| Flesh Clan | Demon | 4-6 | 15-22 | 30-45 | 4-10 | None | Goat-man melee |
| Stone Clan | Demon | 5-7 | 20-27 | 40-55 | 6-12 | Resist Magic | Goat-man melee |
| Fire Clan | Demon | 6-8 | 25-32 | 50-65 | 8-16 | Resist Fire | Goat-man melee |
| Night Clan | Demon | 7-9 | 27-35 | 55-70 | 10-20 | Resist Magic | Goat-man melee |
| Flesh Clan Archer | Demon | 4-6 | 10-17 | 20-35 | 1-7 | None | Goat-man ranged |
| Stone Clan Archer | Demon | 5-7 | 15-20 | 30-40 | 2-9 | Resist Magic | Goat-man ranged |
| Fire Clan Archer | Demon | 6-8 | 20-25 | 40-50 | 3-11 | Resist Fire | Goat-man ranged |
| Night Clan Archer | Demon | 7-9 | 25-32 | 50-65 | 4-13 | Resist Magic | Goat-man ranged |
| Overlord | Demon | 5-7 | 30-40 | 60-80 | 6-12 | Resist Fire | Large demon; heavy hitter |
| Mud Man | Demon | 7-9 | 50-62 | 100-125 | 8-16 | Immune Lightning | Large demon |
| Toad Demon | Demon | 8-10 | 67-80 | 135-160 | 8-16 | Immune Magic, Resist Fire | Large demon |
| Flayed One | Demon | 10-12 | 80-100 | 160-200 | 10-20 | Resist Magic, Immune Fire | Large demon |
| Gloom | Animal | 4-6 | 14-18 | 28-36 | 4-12 | Resist Magic | Flying |
| Familiar | Animal | 6-8 | 10-17 | 20-35 | 4-16 | Resist Magic, Immune Lightning | Flying |
| Winged Demon | Demon | 5-7 | 22-30 | 45-60 | 10-16 | Immune Magic/Fire | Gargoyle; stone form |
| Gargoyle | Demon | 7-9 | 30-45 | 60-90 | 10-16 | Immune Magic, Resist Fire | Stone form until approached |
| Acid Beast | Animal | 6-8 | 20-33 | 40-66 | 4-12 | Immune Magic | Spits acid pools on death |
| Poison Spitter | Animal | 8-10 | 30-42 | 60-85 | 4-16 | Immune Magic | Spits acid pools on death |

### Caves Monsters (Levels 9-12)

| Monster | Type | Dungeon Levels | HP (Normal) | AC | Damage | Resistances | Special |
|---------|------|---------------|-------------|-----|--------|-------------|---------|
| Horned Demon | Animal | 7-9 | 20-40 | 40-80 | 2-16 | Resist Fire | Charge attack |
| Mud Runner | Animal | 8-10 | 25-45 | 50-90 | 6-18 | Resist Fire | Charge attack |
| Frost Charger | Animal | 9-11 | 30-50 | 60-100 | 8-20 | Immune Fire | Charge attack |
| Obsidian Lord | Animal | 10-12 | 35-55 | 70-110 | 10-22 | Immune Fire | Charge attack |
| Pit Beast | Animal | 10-12 | 40-55 | 80-110 | 8-18 | Resist Magic, Immune Fire | Acid spit |
| Lava Maw | Animal | 12-14 | 50-75 | 100-150 | 10-20 | Resist Magic, Immune Fire | Acid spit |
| Blood Claw | Demon | 9-11 | 37-62 | 75-125 | 14-22 | Immune Magic/Fire | Gargoyle |
| Death Wing | Demon | 10-12 | 45-75 | 90-150 | 16-28 | Immune Magic, Resist Fire | Gargoyle |
| Magma Demon | Demon | 8-9 | 25-35 | 50-70 | 2-10 | Immune Magic/Fire | Ranged magma attack |
| Blood Stone | Demon | 8-10 | 28-37 | 55-75 | 2-12 | Immune Magic/Fire | Ranged magma attack |
| Hell Stone | Demon | 9-11 | 30-40 | 60-80 | 2-20 | Immune Magic/Fire | Ranged magma attack |
| Lava Lord | Demon | 9-11 | 35-42 | 70-85 | 4-24 | Immune Magic/Fire | Ranged magma attack |
| Red Storm | Demon | 9-11 | 27-55 | 55-110 | 8-18 | Immune Fire | Lightning attack |
| Storm Rider | Demon | 10-12 | 30-60 | 60-120 | 8-18 | Resist Magic, Immune Lightning | Lightning attack |
| Storm Lord | Demon | 11-13 | 37-67 | 75-135 | 12-24 | Resist Magic, Immune Lightning | Lightning attack |
| Maelstrom | Demon | 12-14 | 45-75 | 90-150 | 12-28 | Resist Magic, Immune Lightning | Lightning attack |

### Hell Monsters (Levels 13-16)

| Monster | Type | Dungeon Levels | HP (Normal) | AC | Damage | Resistances | Special |
|---------|------|---------------|-------------|-----|--------|-------------|---------|
| Slayer | Demon | 10-12 | 60-70 | 120-140 | 12-20 | Resist Magic, Immune Fire | Balrog; melee |
| Guardian (monster) | Demon | 11-13 | 70-80 | 140-160 | 14-22 | Resist Magic, Immune Fire | Balrog |
| Vortex Lord | Demon | 12-14 | 80-90 | 160-180 | 18-24 | Resist Magic, Immune Fire/Lightning | Balrog |
| Balrog | Demon | 13-15 | 90-100 | 180-200 | 22-30 | Resist Magic, Immune Fire/Lightning | Balrog |
| Cave Viper | Demon | 11-13 | 50-75 | 100-150 | 8-20 | Immune Magic | Ranged; charges |
| Fire Drake | Demon | 12-14 | 60-85 | 120-170 | 12-24 | Immune Magic/Fire | Ranged |
| Gold Viper | Demon | 13-14 | 70-80 | 140-180 | 15-26 | Immune Magic, Resist Fire | Ranged |
| Azure Drake | Demon | 15 | 80-100 | 160-200 | 18-30 | Immune Magic/Lightning, Resist Fire | Ranged |
| Succubus | Demon | 12-14 | 60-75 | 120-150 | 1-20 | Resist Magic | Ranged fire; teleports |
| Snow Witch | Demon | 13-15 | 67-87 | 135-175 | 1-24 | Resist Lightning | Ranged; teleports |
| Hell Spawn | Demon | 14-15 | 75-100 | 150-200 | 1-30 | Resist Magic, Immune Lightning | Ranged; teleports |
| Soul Burner | Demon | 15 | 70-112 | 140-225 | 1-35 | Resist Magic, Immune Fire/Lightning | Ranged; teleports |
| Black Knight | Demon | 12-14 | 75 | 150 | 15-20 | Resist Magic/Fire | Heavy melee |
| Doom Guard | Demon | 13-15 | 82 | 165 | 18-25 | Resist Magic/Fire | Heavy melee |
| Steel Lord | Demon | 14-15 | 90 | 180 | 20-30 | Resist Magic, Immune Fire | Heavy melee |
| Blood Knight | Demon | 13-14 | 100 | 200 | 25-35 | Immune Magic, Resist Fire | Heavy melee |
| Counselor | Demon | 13-14 | 35 | 70 | 8-20 | Resist Magic/Fire/Lightning | Casts spells |
| Magistrate | Demon | 14-15 | 42 | 85 | 10-24 | Resist Magic, Immune Fire | Casts spells |
| Cabalist | Demon | 15 | 60 | 120 | 14-30 | Resist Magic/Fire, Immune Lightning | Casts spells |
| Advocate | Demon | 16 | 72 | 145 | 15-25 | Immune Magic, Resist Fire/Lightning | Casts spells |

### Unique Monsters

Each dungeon level may spawn 1-4 unique (named) monsters with:
- Random name based on monster type
- Boosted HP (3x normal)
- 1-3 special abilities chosen from: {Lightning, Fire, Magic resistance/immunity, Fast, Stone Curse immune, teleport, etc.}
- Always drop a magic or unique item on death
- Surrounded by a pack of 6-10 minions of the same type

---

## 10. Boss Encounters

### The Butcher

| Property | Normal | Nightmare | Hell |
|----------|--------|-----------|------|
| Dungeon Level | 2 | 2 | 2 |
| Hit Points | 110 | 330 | 660 |
| Armor Class | 25 | 55 | 85 |
| Damage | 6-16 | 16-36 | 30-70 |
| To-Hit | 60 | 90 | 120 |
| Type | Demon | Demon | Demon |
| Resistances | None | None | None |

- **Location**: Unique room on dungeon level 2 with dismembered corpses
- **Opening line**: "Ah, fresh meat!"
- **AI**: Charges directly at player; very fast melee attack speed
- **Weakness**: Cannot open doors; can be trapped behind doorways for ranged attacks
- **Drop**: The Butcher's Cleaver (unique cleaver)

### Skeleton King (King Leoric)

| Property | Normal | Nightmare | Hell |
|----------|--------|-----------|------|
| Dungeon Level | 3 (mini-dungeon) | 3 | 3 |
| Hit Points | 120 | 360 | 720 |
| Armor Class | 30 | 60 | 90 |
| Damage | 6-16 | 16-36 | 30-70 |
| To-Hit | 65 | 95 | 125 |
| Type | Undead | Undead | Undead |
| Resistances | Immune Magic | Immune Magic | Immune Magic |

- **Location**: King Leoric's Tomb, accessed from dungeon level 3
- **AI**: Raises skeleton minions during combat; targets nearest player
- **Special (Multiplayer)**: 100% life steal (heals full damage dealt); can exceed max HP
- **Drop**: The Undead Crown (unique helm)

### Archbishop Lazarus

| Property | Normal | Nightmare | Hell |
|----------|--------|-----------|------|
| Dungeon Level | 15 (mini-dungeon) | 15 | 15 |
| Hit Points | 600 | 1,200 | 1,800 |
| Armor Class | 90 | 120 | 150 |
| Damage | 30-50 | 50-80 | 80-120 |
| Type | Demon | Demon | Demon |
| Resistances | Immune Magic, Immune Fire | All immunities | All immunities |

- **Location**: Lazarus' Lair, a star-shaped mini-level accessible from level 15 via the Staff of Lazarus
- **AI**: Casts powerful spells (Blood Star, Flash); teleports frequently
- **Guards**: Red Vex and Black Jade (unique succubi)
- **Drop**: Quest completion triggers access to level 16

### Diablo (The Dark Lord)

| Property | Normal | Nightmare | Hell |
|----------|--------|-----------|------|
| Dungeon Level | 16 | 16 | 16 |
| Hit Points | 1,666 | 3,332 | 4,998 |
| Armor Class | 145 | 200 | 240 |
| Damage | 30-50 | 60-90 | 90-120 |
| To-Hit | 175 | 200 | 250 |
| Type | Demon | Demon | Demon |
| Resistances | Immune Magic, Immune Fire, Resist Lightning | All immunities | All immunities |

- **Location**: Center of level 16 behind bone levers
- **Opening**: Two bone levers must be pulled to open the path to Diablo's chamber
- **AI**: Melee attacks + casts Apocalypse (unavoidable magic damage to all players on level)
- **Special Attacks**:
  - Apocalypse: Hits all players regardless of position; deals physical damage; cannot be blocked or resisted
  - Melee: Extremely fast with high damage
  - Charges at players
- **Death**: Defeating Diablo triggers the ending cinematic
- **Drop**: No item drop (game ends)

---

## 11. Quest System

### Quest Structure

- Most quests are **optional** and randomized per game
- Only **Archbishop Lazarus** and **Diablo** are mandatory for game completion
- Quests are assigned to groups; each new game randomly selects from each group
- Multiplayer only has 4 quests: Butcher, King Leoric, Lazarus, Diablo

### Quest Groups & Selection

| Group | Selection | Quests |
|-------|-----------|--------|
| Always | All present | Chamber of Bone, Archbishop Lazarus, Diablo |
| Group 1 | 1 of 2 | King Leoric's Curse, Poisoned Water Supply |
| Group 2 | 2 of 3 | The Butcher, Gharbad the Weak, Ogden's Sign |
| Group 3 | 2 of 3 | The Magic Rock, Arkaine's Valor, Halls of the Blind |
| Group 4 | 2 of 3 | Zhar the Mad, The Black Mushroom, Anvil of Fury |
| Group 5 | 1 of 2 | Warlord of Blood, Lachdanan |

### Complete Quest List

| Quest | Quest Giver | Level | Objective | Reward |
|-------|------------|-------|-----------|--------|
| **The Butcher** | Wounded Townsman | 2 | Kill The Butcher in his gore-filled room | The Butcher's Cleaver (unique cleaver) |
| **King Leoric's Curse** | Ogden | 3 | Find Leoric's Tomb, defeat Skeleton King | The Undead Crown (unique helm) |
| **Poisoned Water Supply** | Pepin | 2 (mini-dungeon) | Clear infected water source area | Ring of Truth (unique ring) |
| **Ogden's Sign** | Ogden | 4 | Retrieve tavern sign from Dark Ones | Harlequin Crest (unique helm) |
| **Gharbad the Weak** | Gharbad (in dungeon) | 4 | Interact with Gharbad 3 times; he attacks on 3rd | Random magic items |
| **The Magic Rock** | Griswold | 5 | Retrieve heavenly stone from dungeon | Empyrean Band (unique ring) |
| **Arkaine's Valor** | Book of Blood | 5 | Place 3 blood stones on stands | Arkaine's Valor (unique armor) |
| **Halls of the Blind** | Book of the Blind | 7 | Clear the Halls of the Blind | Optic Amulet (unique amulet) |
| **Chamber of Bone** | Mythical Book | 6 | Kill all monsters, activate levers in chamber | Guardian spell +1 level |
| **Zhar the Mad** | Zhar (in dungeon) | 8 | Speak twice / take his book; he attacks | 2 spellbooks + magic item |
| **The Black Mushroom** | Adria (multi-step) | 9 | Collect Fungal Tome -> Mushroom -> Demon's Brain | Spectral Elixir (+3 all attributes) |
| **Anvil of Fury** | Griswold | 10 | Retrieve the Anvil of Fury from lava-surrounded isle | Griswold's Edge (unique sword) |
| **Warlord of Blood** | Steel Tome | 13 | Defeat the Warlord of Blood in his armory | 4 magic weapons, 2 magic armor, 1 magic item |
| **Lachdanan** | Lachdanan (in dungeon) | 14 | Retrieve Golden Elixir from level 15 | Veil of Steel (unique helm) |
| **Archbishop Lazarus** | Cain | 15 (mini-dungeon) | Enter Lazarus' lair via Staff of Lazarus, defeat him | Opens path to level 16 |
| **Diablo** | Cain | 16 | Pull bone levers, defeat Diablo | Game completion cinematic |

---

## 12. Item System

### Item Categories

| Category | Types |
|----------|-------|
| Weapons | Swords, Axes, Maces, Clubs, Staves, Bows |
| Armor | Light Armor, Medium Armor, Heavy Armor, Helms, Shields |
| Jewelry | Rings, Amulets |
| Consumables | Potions, Scrolls, Spellbooks, Elixirs |
| Gold | Currency (takes inventory space: 5,000 per slot) |

### Item Quality Tiers

| Quality | Color | Properties |
|---------|-------|-----------|
| Normal | White | Base stats only; no magical properties |
| Magic | Blue | 1 prefix and/or 1 suffix (max 2 affixes total) |
| Unique | Gold | Predefined special properties (up to 6); fixed name and stats |

- **No rare items** in Diablo I
- **No set items** in Diablo I
- Unidentified magic/unique items appear as blue/gold but properties hidden until identified

### Weapon Base Types

| Weapon | Damage | Speed | Str Req | Dex Req | Hands |
|--------|--------|-------|---------|---------|-------|
| Short Sword | 2-6 | Normal | 18 | 0 | 1 |
| Falchion | 4-8 | Normal | 30 | 0 | 1 |
| Scimitar | 3-7 | Fast | 23 | 23 | 1 |
| Claymore | 1-12 | Normal | 35 | 0 | 1 |
| Broad Sword | 4-12 | Normal | 40 | 0 | 1 |
| Sabre | 1-8 | Fast | 17 | 0 | 1 |
| Long Sword | 2-10 | Normal | 30 | 30 | 1 |
| Bastard Sword | 6-15 | Normal | 50 | 0 | 1 |
| Two-Handed Sword | 8-16 | Normal | 65 | 0 | 2 |
| Great Sword | 10-20 | Normal | 75 | 0 | 2 |
| Small Axe | 2-10 | Normal | 0 | 0 | 1 |
| Axe | 4-12 | Normal | 22 | 0 | 1 |
| Large Axe | 6-16 | Normal | 30 | 0 | 2 |
| Broad Axe | 8-20 | Normal | 50 | 0 | 2 |
| Battle Axe | 10-25 | Normal | 65 | 0 | 2 |
| Great Axe | 12-30 | Normal | 80 | 0 | 2 |
| Mace | 1-8 | Normal | 16 | 0 | 1 |
| Morning Star | 1-10 | Normal | 26 | 0 | 1 |
| War Hammer | 5-9 | Normal | 40 | 0 | 1 |
| Flail | 2-12 | Normal | 30 | 0 | 1 |
| Maul | 6-20 | Normal | 55 | 0 | 2 |
| Short Bow | 1-4 | Normal | 0 | 0 | 2 |
| Hunter's Bow | 2-5 | Normal | 0 | 20 | 2 |
| Long Bow | 1-6 | Normal | 0 | 25 | 2 |
| Composite Bow | 3-6 | Normal | 25 | 40 | 2 |
| Short Battle Bow | 3-7 | Normal | 30 | 50 | 2 |
| Long Battle Bow | 1-10 | Normal | 30 | 60 | 2 |
| Short War Bow | 4-8 | Normal | 35 | 70 | 2 |
| Long War Bow | 1-14 | Normal | 45 | 80 | 2 |
| Short Staff | 2-4 | Normal | 0 | 0 | 1 |
| Long Staff | 4-8 | Normal | 0 | 0 | 1 |
| Composite Staff | 5-10 | Normal | 0 | 0 | 1 |
| Quarter Staff | 6-12 | Normal | 0 | 0 | 1 |
| War Staff | 8-16 | Normal | 0 | 0 | 1 |

### Armor Base Types

| Armor | AC | Str Req | Durability |
|-------|-----|---------|-----------|
| Cape | 1-5 | 0 | 12 |
| Rags | 2-6 | 0 | 6 |
| Cloak | 3-7 | 0 | 18 |
| Robe | 4-7 | 0 | 24 |
| Quilted Armor | 7-10 | 0 | 30 |
| Leather Armor | 10-13 | 0 | 35 |
| Hard Leather Armor | 11-14 | 0 | 40 |
| Studded Leather Armor | 15-17 | 20 | 45 |
| Ring Mail | 17-20 | 25 | 50 |
| Chain Mail | 18-22 | 30 | 55 |
| Scale Mail | 23-28 | 35 | 60 |
| Breast Plate | 20-24 | 40 | 80 |
| Splint Mail | 30-35 | 65 | 65 |
| Plate Mail | 42-50 | 60 | 75 |
| Field Plate | 40-45 | 65 | 80 |
| Gothic Plate | 50-60 | 80 | 100 |
| Full Plate Mail | 60-75 | 90 | 90 |

### Shield Base Types

| Shield | AC | Str Req | Durability | Block% bonus |
|--------|-----|---------|-----------|-------------|
| Buckler | 1-5 | 0 | 16 | 0 |
| Small Shield | 3-8 | 25 | 24 | 0 |
| Large Shield | 5-10 | 40 | 32 | 0 |
| Kite Shield | 8-15 | 50 | 40 | 0 |
| Tower Shield | 12-20 | 60 | 50 | 0 |
| Gothic Shield | 14-18 | 80 | 60 | 0 |

### Helm Base Types

| Helm | AC | Str Req | Durability |
|------|-----|---------|-----------|
| Cap | 1-3 | 0 | 15 |
| Skull Cap | 2-4 | 0 | 20 |
| Helm | 4-6 | 25 | 30 |
| Full Helm | 6-8 | 35 | 35 |
| Crown | 8-12 | 0 | 40 |
| Great Helm | 10-15 | 50 | 60 |

### Inventory Grid

- **Grid size**: 10 columns x 4 rows (40 slots)
- **Item sizes**: Items occupy 1x1, 1x2, 1x3, 2x2, or 2x3 grid spaces depending on type
- **Belt**: 8 quick-access slots (numbered 1-8) for single-slot items (potions, scrolls)
- **Equipment slots**: Head, Body, Left Hand, Right Hand, Left Ring, Right Ring, Amulet

### Potion Types

| Potion | Effect | Buy Price | Size |
|--------|--------|-----------|------|
| Potion of Healing | Restores partial HP (variable by class) | 50 | 1x1 |
| Potion of Full Healing | Restores all HP | 150 | 1x1 |
| Potion of Mana | Restores partial Mana (variable by class) | 50 | 1x1 |
| Potion of Full Mana | Restores all Mana | 150 | 1x1 |
| Potion of Rejuvenation | Restores partial HP and Mana | 120 | 1x1 |
| Potion of Full Rejuvenation | Restores all HP and Mana | 600 | 1x1 |
| Elixir of Strength | +1 Strength (permanent) | 5,000 | 1x1 |
| Elixir of Magic | +1 Magic (permanent) | 5,000 | 1x1 |
| Elixir of Dexterity | +1 Dexterity (permanent) | 5,000 | 1x1 |
| Elixir of Vitality | +1 Vitality (permanent) | 5,000 | 1x1 |

### Scroll Types

| Scroll | Effect | Buy Price |
|--------|--------|-----------|
| Scroll of Town Portal | Opens portal to town | 200 |
| Scroll of Identify | Identifies one magic/unique item | 100 |
| Scroll of Infravision | Reveals all monsters on level | 600 |
| Scroll of Healing | Casts Healing spell | 50 |
| Scroll of Resurrect | Revives dead player (multiplayer) | 250 |
| Scroll of Teleport | Casts Teleport spell | 3,000 |
| Scroll of Apocalypse | Casts Apocalypse on all visible monsters | 20,000 |
| Scroll of Nova | Casts Nova spell | 10,000 |
| Scroll of Flame Wave | Casts Flame Wave | 2,500 |
| Scroll of Fireball | Casts Fireball | 1,000 |
| Scroll of Lightning | Casts Lightning | 750 |
| Scroll of Stone Curse | Casts Stone Curse | 3,500 |
| Scroll of Chain Lightning | Casts Chain Lightning | 3,000 |
| Scroll of Phasing | Casts Phasing | 500 |
| Scroll of Mana Shield | Casts Mana Shield | 1,200 |
| Scroll of Golem | Casts Golem | 4,500 |
| Scroll of Charged Bolt | Casts Charged Bolt | 100 |

### Durability

- All weapons and armor have a **current durability** and **maximum durability**
- Each hit received (armor) or dealt (weapon) has a chance to reduce current durability by 1
- When durability reaches 0, the item **breaks** and provides no stats until repaired
- Indestructible items never lose durability
- Griswold repairs items for gold (restores to max durability)
- Warrior's Repair skill restores durability but permanently reduces max durability by at least 1

---

## 13. Item Affixes — Prefixes & Suffixes

### Prefix Tables

#### Armor Class Prefixes (Armor & Shields)

| Prefix | AC Bonus % | QLvl |
|--------|-----------|------|
| Vulnerable | -100 to -51% | 3 |
| Rusted | -50 to -25% | 1 |
| Fine | +20-30% | 1 |
| Strong | +31-40% | 3 |
| Grand | +41-55% | 6 |
| Valiant | +56-70% | 10 |
| Glorious | +71-90% | 14 |
| Blessed | +91-110% | 19 |
| Saintly | +111-130% | 24 |
| Awesome | +131-150% | 28 |
| Holy | +151-170% | 35 |
| Godly | +171-200% | 60 |

#### To-Hit & Damage Prefixes (Weapons)

| Prefix | To-Hit % | Damage % | QLvl |
|--------|---------|---------|------|
| Clumsy | -10 to -6 | -75 to -50 | 5 |
| Dull | -5 to -1 | -45 to -25 | 1 |
| Sharp | +1-5 | +20-35 | 1 |
| Fine | +6-10 | +36-50 | 6 |
| Warrior's | +11-15 | +51-65 | 10 |
| Soldier's | +16-20 | +66-80 | 15 |
| Lord's | +21-30 | +81-95 | 19 |
| Knight's | +31-40 | +96-110 | 23 |
| Master's | +41-50 | +111-125 | 28 |
| Champion's | +51-75 | +126-150 | 40 |
| King's | +76-100 | +151-175 | 28 |

#### To-Hit Only Prefixes (Weapons, Bows, Jewelry)

| Prefix | To-Hit % | QLvl |
|--------|---------|------|
| Tin | -10 to -6 | 3 |
| Brass | -5 to -1 | 1 |
| Bronze | +1-5 | 1 |
| Iron | +6-10 | 4 |
| Steel | +11-15 | 6 |
| Silver | +16-20 | 9 |
| Gold | +21-30 | 12 |
| Platinum | +31-40 | 16 |
| Mithril | +41-60 | 20 |
| Meteoric | +61-80 | 23 |
| Weird | +81-100 | 35 |
| Strange | +101-150 | 60 |

#### Damage Only Prefixes (Weapons, Bows)

| Prefix | Damage % | QLvl |
|--------|---------|------|
| Savage | +111-125 | 23 |
| Ruthless | +126-150 | 35 |
| Merciless | +151-175 | 60 |

#### Resistance Prefixes (All Item Types)

| Prefix | Element | Range | QLvl |
|--------|---------|-------|------|
| White | Magic | 10-20% | 4 |
| Pearl | Magic | 21-30% | 10 |
| Ivory | Magic | 31-40% | 16 |
| Crystal | Magic | 41-50% | 20 |
| Diamond | Magic | 51-60% | 26 |
| Red | Fire | 10-20% | 4 |
| Crimson | Fire | 21-30% | 10 |
| Garnet | Fire | 41-50% | 20 |
| Ruby | Fire | 51-60% | 26 |
| Blue | Lightning | 10-20% | 4 |
| Azure | Lightning | 21-30% | 10 |
| Lapis | Lightning | 31-40% | 16 |
| Cobalt | Lightning | 41-50% | 20 |
| Sapphire | Lightning | 51-60% | 26 |
| Topaz | All | 10-15% | 8 |
| Amber | All | 16-20% | 12 |
| Jade | All | 21-30% | 18 |
| Obsidian | All | 31-40% | 24 |
| Emerald | All | 41-50% | 31 |

#### Mana Prefixes (Staves, Jewelry)

| Prefix | Mana | QLvl |
|--------|------|------|
| Hyena's | -25 to -11 | 4 |
| Frog's | -10 to -1 | 1 |
| Spider's | +10-15 | 1 |
| Raven's | +15-20 | 5 |
| Snake's | +21-30 | 9 |
| Serpent's | +30-40 | 15 |
| Drake's | +41-50 | 21 |
| Dragon's | +51-60 | 27 |

#### Spell & Special Prefixes (Staves)

| Prefix | Effect | QLvl |
|--------|--------|------|
| Angel's | +1 Spell Levels | 15 |
| Arch-Angel's | +2 Spell Levels | 25 |
| Plentiful | x2 Staff Charges | 4 |
| Bountiful | x3 Staff Charges | 9 |

#### Elemental Damage Prefixes (Weapons)

| Prefix | Damage | QLvl |
|--------|--------|------|
| Flaming | +1-10 Fire | 7 |
| Lightning | +2-20 Lightning | 18 |

### Suffix Tables

#### Attribute Suffixes

| Suffix | Attribute | Range | QLvl |
|--------|-----------|-------|------|
| of Frailty | Strength | -10 to -6 | 3 |
| of Weakness | Strength | -5 to -1 | 1 |
| of Strength | Strength | +1-5 | 1 |
| of Might | Strength | +6-10 | 5 |
| of Power | Strength | +11-15 | 11 |
| of Giants | Strength | +16-20 | 17 |
| of Titans | Strength | +21-30 | 23 |
| of the Fool | Magic | -10 to -6 | 3 |
| of Dyslexia | Magic | -5 to -1 | 1 |
| of Magic | Magic | +1-5 | 1 |
| of the Mind | Magic | +6-10 | 5 |
| of Brilliance | Magic | +11-15 | 11 |
| of Sorcery | Magic | +16-20 | 17 |
| of Wizardry | Magic | +21-30 | 23 |
| of Paralysis | Dexterity | -10 to -6 | 3 |
| of Atrophy | Dexterity | -5 to -1 | 1 |
| of Dexterity | Dexterity | +1-5 | 1 |
| of Skill | Dexterity | +6-10 | 5 |
| of Accuracy | Dexterity | +11-15 | 11 |
| of Precision | Dexterity | +16-20 | 17 |
| of Perfection | Dexterity | +21-30 | 23 |
| of Illness | Vitality | -10 to -6 | 3 |
| of Disease | Vitality | -5 to -1 | 1 |
| of Vitality | Vitality | +1-5 | 1 |
| of Zest | Vitality | +6-10 | 5 |
| of Vim | Vitality | +11-15 | 11 |
| of Vigor | Vitality | +16-20 | 17 |
| of Life | Vitality | +21-30 | 23 |

#### All Attributes Suffixes

| Suffix | All Attributes | QLvl |
|--------|---------------|------|
| of Trouble | -10 to -6 | 12 |
| of the Pit | -5 to -1 | 5 |
| of the Sky | +1-3 | 5 |
| of the Moon | +4-7 | 11 |
| of the Stars | +8-11 | 17 |
| of the Heavens | +12-15 | 25 |
| of the Zodiac | +16-20 | 30 |

#### Life Suffixes (Armor, Shields, Jewelry)

| Suffix | Life | QLvl |
|--------|------|------|
| of the Vulture | -25 to -11 | 4 |
| of the Jackal | -10 to -1 | 1 |
| of the Fox | +10-15 | 1 |
| of the Jaguar | +16-20 | 5 |
| of the Eagle | +21-30 | 9 |
| of the Wolf | +30-40 | 15 |
| of the Tiger | +41-50 | 21 |
| of the Lion | +51-60 | 27 |
| of the Mammoth | +61-80 | 35 |
| of the Whale | +81-100 | 60 |

#### Attack Speed Suffixes (Weapons)

| Suffix | Speed | QLvl |
|--------|-------|------|
| of Readiness | Quick | 1 |
| of Swiftness | Fast | 10 |
| of Speed | Faster | 19 |
| of Haste | Fastest | 27 |

#### Hit Recovery Suffixes (Armor, Jewelry)

| Suffix | Speed | QLvl |
|--------|-------|------|
| of Balance | Fast | 1 |
| of Stability | Faster | 10 |
| of Harmony | Fastest | 20 |

#### Damage Reduction Suffixes (Armor, Shields)

| Suffix | Reduction | QLvl |
|--------|-----------|------|
| of Pain | +4 to +2 (penalty) | 4 |
| of Tears | -1 | 2 |
| of Health | -1 | 2 |
| of Protection | -2 | 6 |
| of Absorption | -3 | 12 |
| of Deflection | -4 | 20 |
| of Osmosis | -5 to -6 | 50 |

#### Life/Mana Steal Suffixes (Weapons)

| Suffix | Steal % | Type | QLvl |
|--------|---------|------|------|
| of the Leech | 3% Life Steal | Weapons | 8 |
| of Blood | 5% Life Steal | Weapons | 19 |
| of the Bat | 3% Mana Steal | Weapons | 8 |
| of Vampires | 5% Mana Steal | Weapons | 19 |

#### Durability Suffixes

| Suffix | Effect | QLvl |
|--------|--------|------|
| of Fragility | -1 durability | 3 |
| of Brittleness | -75 to -26 | 1 |
| of Sturdiness | +26 to +75 | 1 |
| of Craftsmanship | +51 to +100 | 6 |
| of Structure | +101 to +200 | 12 |
| of the Ages | Indestructible | 25 |

#### Special Suffixes

| Suffix | Effect | QLvl |
|--------|--------|------|
| of the Bear | Knockback | 5 |
| of Blocking | Fast Block | 5 |
| of Thieves | Absorb half trap damage | 11 |
| of Thorns | Attacker takes 1-3 damage | 1 |
| of Corruption | Drains all mana | 5 |

#### Light Radius Suffixes

| Suffix | Radius Change | QLvl |
|--------|--------------|------|
| of the Dark | -40% | 6 |
| of the Night | -20% | 3 |
| of Light | +20% | 4 |
| of Radiance | +40% | 8 |

#### Elemental Arrow Suffixes (Bows)

| Suffix | Damage | QLvl |
|--------|--------|------|
| of Flame | +1-3 Fire | 1 |
| of Fire | +1-6 Fire | 11 |
| of Burning | +1-16 Fire | 35 |
| of Shock | +1-6 Lightning | 13 |
| of Lightning | +1-10 Lightning | 21 |
| of Thunder | +1-20 Lightning | 60 |

#### Armor Penetration Suffixes (Weapons)

| Suffix | Effect | QLvl |
|--------|--------|------|
| of Piercing | -2 to -6 target AC | 1 |
| of Puncturing | -4 to -12 target AC | 9 |
| of Bashing | -8 to -24 target AC | 17 |

---

## 14. Unique Items

### Unique Weapons

| Item | Base Type | Damage | Key Properties |
|------|-----------|--------|---------------|
| The Butcher's Cleaver | Cleaver | 4-24 | Unusual item damage |
| Shadowhawk | Broad Sword | 4-12 | 5% life steal, +15% to-hit, +5% all resist |
| The Executioner's Blade | Long Sword | 4-8 | +150% damage, -10 HP, -10% light radius |
| The Grizzly | Two-Handed Sword | 8-16 | +20 Str, +200% damage, knockback |
| The Grandfather | Great Sword | 10-20 | +5 all attributes, +20% to-hit, +70% damage |
| Gnarled Root | Short Staff | 1-6 | +300% damage, +5 Magic, +10 Dex, +30% to-hit |
| Dreamflange | Mace | 1-8 | +30 Magic, +50 Mana, 50% magic resist, +1 spell levels |
| Cranium Basher | Maul | 6-20 | +20 damage, +15 Str, -150 Mana, Indestructible |
| Schaefer's Hammer | War Hammer | 5-9 | -100% damage, +1-50 lightning hit, +50 HP |
| Baranar's Star | Morning Star | 1-10 | +12% to-hit, +80% damage, quick attack, +4 Vit, -4 Dex |
| Doombringer | Bastard Sword | 6-15 | +25% to-hit, +250% damage, -5 all attributes, -25 HP |
| Lightsabre | Sabre | 1-8 | +20% light radius, +1-10 lightning hit, 50% lightning resist |
| Black Razor | Dagger | 1-4 | +150% damage, +2 Vit |
| The Falcon's Talon | Scimitar | 3-7 | Fastest attack, +20% to-hit, -33% damage, +10 Dex |
| Eaglehorn | Long War Bow | 1-10 | +20 Dex, +50% to-hit, +100% damage, Indestructible |
| Windforce | Long Battle Bow | 1-14 | +200% damage, knockback |
| Fleshstinger | Long Bow | 1-6 | +15 Dex, +40% to-hit, +80% damage |
| The Needler | Short Bow | 1-3 | +50% to-hit, fast attack |
| Flamedart | Hunter's Bow | 2-5 | +1-6 fire arrows, +1-6 fire hit, +40% fire resist |
| Bow of the Dead | Short Bow | 3-6 | +10% to-hit, +4 Dex, -3 Vit, -20% light radius |
| Hellslayer | Battle Axe | 10-25 | +8 Str/Vit, +100% damage, +25 HP |
| Celestial Axe | Battle Axe | 10-25 | No Str requirement, +15% to-hit, +15 HP, -15 Str |
| Wicked Axe | Large Axe | 6-16 | +30% to-hit, +10 Dex, Indestructible |
| Stonecleaver | Broad Axe | 8-20 | +30 HP, +20% to-hit, +50% damage, 40% lightning resist |
| Aguinara's Hatchet | Small Axe | 2-10 | +1 spell levels, 75% magic resist, +10 Magic |
| Messerschmidt's Reaver | Great Axe | 12-30 | +200% damage, +15 damage, +5 all attributes |
| Ice Shank | Long Sword | 2-10 | +40% fire resist, +5 Str |
| Inferno | Long Staff | 2-10 | +2-12 fire hit, +20 Mana, 75% fire resist |
| Rod of Onan | War Staff | 8-16 | 50 Golem charges, +100% damage, +5 all attributes |
| Mindcry | Composite Staff | 6-12 | +15 Magic, 69 Guardian charges, +15% all resist |
| Thundercall | Composite Staff | 5-10 | +35% to-hit, +1-10 lightning hit, 76 charges, +30% lightning resist |
| Storm Spire | War Staff | 8-16 | +50% lightning resist, +2-8 lightning hit, +10 Str |
| Wizardspike | Dagger | 1-4 | +15 Magic, +35 Mana, +25% to-hit |
| Celestial Star | Flail | 2-12 | No requirement, +20% light radius, +10 damage, -8 AC |

### Unique Armor

| Item | Base Type | AC | Key Properties |
|------|-----------|-----|---------------|
| Demonspike Coat | Full Plate Mail | 100 | -6 damage from enemies, +10 Str, Indestructible |
| Naj's Light Plate | Plate Mail | 44-47 | +5 Magic, +20 Mana, +20% all resist, no requirement |
| The Gladiator's Bane | Studded Leather | 25 | -2 damage from enemies, high durability, -3 all attributes |
| Leather of Aut | Leather Armor | 15 | +5 Str, -5 Magic, Indestructible, no requirement |
| Torn Flesh of Souls | Rags | 8 | +10 Vit, -1 damage from enemies, Indestructible |
| Scavenger's Carapace | Breast Plate | -6 to -9 | -15 damage from enemies, +40% lightning resist |
| Sparking Mail | Chain Mail | 30-32 | +1-10 lightning hit damage |
| Arkaine's Valor | Splint Mail | 25 | +10 Vit, fastest hit recovery, -3 damage from enemies |
| Gotterdamerung | Gothic Plate | 60 | +20 all attributes, -4 damage from enemies, all resist = 0 |

### Unique Helms

| Item | Base Type | AC | Key Properties |
|------|-----------|-----|---------------|
| The Undead Crown | Crown | 8 | Life steal on each hit |
| Harlequin Crest | Cap | 4 | +2 all attributes, +7 HP, +7 Mana, -1 damage |
| Thinking Cap | Skull Cap | 4 | +30 Mana, +2 spell levels, +20% all resist |
| Overlord's Helm | Helm | 12 | +20 Str, +15 Dex, +5 Vit, -20 Magic |
| Royal Circlet | Crown | 40 | +10 all attributes, +40 Mana, +10% light radius |
| Veil of Steel | Great Helm | 18 | +15 Str, +15 Vit, -30 Mana, +50% all resist, -20% light radius |
| Fool's Crest | Helm | varies | -4 all attributes, +100 HP, attacker takes 1-3 damage |

### Unique Shields

| Item | Base Type | AC | Key Properties |
|------|-----------|-----|---------------|
| Split Skull Shield | Buckler | 10 | +10 HP, +2 Str, -10% light radius |
| Dragon's Breach | Kite Shield | 20 | +25% fire resist, +5 Str, Indestructible |
| Blackoak Shield | Small Shield | 18 | +10 Dex, -10 Vit, -10% light radius |
| Holy Defender | Large Shield | 15 | -2 damage from enemies, 20% fire resist, fast block |
| Stormshield | Tower Shield | 40 | +10 Str, Indestructible, fast block |
| The Protector | Large Shield | 40 | +5 Vit, -5 damage from enemies, 86 Healing charges |

### Unique Jewelry

| Item | Type | Key Properties |
|------|------|---------------|
| Ring of Truth | Ring | +10 HP, +10% all resist, -1 damage from enemies |
| Empyrean Band | Ring | +2 all attributes, +20% light radius, +1 spell levels, fast hit recovery |
| Ring of Engagement | Ring | -1 to -2 damage from enemies, attacker takes 1-3, +5 AC |
| Constricting Ring | Ring | 75% all resist max, constantly drains HP |
| Optic Amulet | Amulet | +20% light radius, +5 Magic, +20% magic resist |
| The Bleeder | Amulet | +20% magic resist, +30 Mana, -10 HP |
| Naj's Puzzler | Amulet | +20 Magic, +10 Dex, 57 Teleport charges, +20% all resist |
| The Rainbow Cloak | Amulet | +1 all attributes, +5 HP, +10% all resist |

---

## 15. Economy & Gold

### Gold Properties

| Property | Value |
|----------|-------|
| Max gold per inventory slot | 5,000 |
| Gold takes inventory space | Yes (1x1 per pile, up to 5,000) |
| Max gold on ground pile | 5,000 |
| Sell price ratio | 1/4 of buy price |
| Gold dropped on death (multiplayer) | All held gold drops on corpse |

### NPC Pricing

| NPC | Service | Cost |
|-----|---------|------|
| Griswold | Repair items | Varies by item value and damage |
| Griswold | Buy weapons/armor | Market price |
| Griswold | Sell weapons/armor | 1/4 of buy price |
| Pepin | Heal to full HP | Free |
| Pepin | Buy scrolls/potions | Listed price |
| Cain | Identify item | 100 gold |
| Adria | Buy scrolls/books/staves/elixirs | Listed price |
| Adria | Recharge staff | Varies (free if < 1% charges missing) |
| Wirt | View premium item | 50 gold (non-refundable) |
| Wirt | Buy premium item | Premium price (higher qlvl items than Griswold) |

### Item Level (QLvl) and Shops

- Griswold sells items up to qlvl 30 in Normal; items refresh each visit to dungeon
- Adria sells staves, scrolls, books up to qlvl 30
- Wirt sells one premium item per visit; qlvl up to 60 (can sell highest-tier affixes)
- Item affixes can only appear if the item's qlvl meets or exceeds the affix's qlvl
- Dungeon drops have qlvl based on dungeon level: generally dlvl * 2 for magic items

### Inventory Management

- Gold occupies regular inventory space (5,000 max per slot)
- Players often must make trips to town to sell items and free space
- No shared stash; each character has their own inventory
- Items on the ground disappear if player travels too far or changes levels (except in town)

---

## 16. Town of Tristram & NPCs

### Town Layout

The town of Tristram serves as the hub between dungeon runs. It is a fixed, non-randomized map featuring:
- **Central square**: Ogden's Tavern, the well, Griswold's smithy
- **Cathedral entrance**: North side of town; entrance to dungeon level 1
- **Pepin's house**: South-west area
- **Adria's shack**: Far north-east, on an island across a bridge
- **Wirt**: Far south-west corner
- **Cain**: Near the well in the center
- **Farnham**: Near the tavern, usually sitting on the ground
- **Gillian**: Near the tavern entrance
- **Cow**: Beside a fence near Gillian (clicking it triggers "moo" sound; no gameplay effect in base game)

### NPC Details

#### Griswold the Blacksmith
- **Location**: Center of town, at his forge
- **Services**:
  - Sells normal and magic weapons and armor (inventory refreshes each dungeon visit)
  - Buys all weapons, armor, and jewelry
  - Repairs damaged items (for gold)
- **Quest role**: Gives Magic Rock and Anvil of Fury quests; crafts Griswold's Edge as reward

#### Pepin the Healer
- **Location**: South-west area
- **Services**:
  - Heals player to full HP (free, unlimited)
  - Sells healing potions, full healing potions, scrolls of healing, scrolls of resurrect
  - Buys elixirs and staves
- **Quest role**: Gives Poisoned Water Supply quest; involved in Black Mushroom quest chain

#### Adria the Witch
- **Location**: North-east island
- **Services**:
  - Sells scrolls, spellbooks, staves (with charges), elixirs
  - Buys staves and scrolls
  - Recharges staves (for gold)
- **Quest role**: Gives Black Mushroom quest; involved in several quest dialogues

#### Wirt the Peg-Legged Boy
- **Location**: Far south-west
- **Services**:
  - Pay 50 gold to see his single premium item
  - Premium items have higher qlvl than Griswold's stock (up to qlvl 60)
  - Inventory of 1 item; refreshes each dungeon visit
- **Special**: Only vendor that can sell the highest-tier affix items; overpriced

#### Deckard Cain the Elder
- **Location**: Near the well, center of town
- **Services**:
  - Identifies magic and unique items for 100 gold each
  - Provides quest dialogue and lore
- **Quest role**: Gives Archbishop Lazarus and Diablo quests; provides extensive lore

#### Ogden the Tavern Owner
- **Location**: Inside the tavern
- **Services**:
  - Quest dialogue only; does not buy or sell
- **Quest role**: Gives Ogden's Sign and King Leoric's Curse quests

#### Farnham the Drunk
- **Location**: Near the tavern, sitting on the ground
- **Services**:
  - Quest dialogue and lore only; does not buy or sell
- **Personality**: Traumatized former warrior; unreliable narrator

#### Gillian the Barmaid
- **Location**: Near the tavern
- **Services**:
  - Quest dialogue only; does not buy or sell
- **Personality**: Grandmother is ill; polite and concerned

#### Wounded Townsman (Kael Rills)
- **Appears**: Only when The Butcher quest is active
- **Role**: Staggers into town; triggers The Butcher quest with dying words

---

## 17. Shrine System

### Shrine Mechanics

- Shrines are one-use interactive objects found in dungeon levels
- Each shrine has a specific effect (some beneficial, some harmful)
- Shrine effects are immediate and most are permanent
- Goat Shrines and Cauldrons trigger a random shrine effect
- Blood Fountains and Purifying Springs are reusable

### All Shrine Types

| Shrine | Effect | Message |
|--------|--------|---------|
| **Abandoned** | +2 Dexterity | "The hands of men may be guided by fate" |
| **Creepy** | +2 Strength | "Strength is bolstered by heavenly faith" |
| **Cryptic** | Casts Nova + refills Mana | "Arcane power brings destruction" |
| **Divine** | Restores HP/Mana, fills potions | "Drink and be refreshed" |
| **Eerie** | +2 Magic | "Knowledge and wisdom at the cost of self" |
| **Eldritch** | Converts all potions to Rejuvenation type | "Crimson and Azure become as the sun" |
| **Enchanted** | -1 level to one random spell, +1 to all others | "Magic is not always what it seems" |
| **Fascinating** | +2 Firebolt levels, -10% max mana | "Intensity comes at the cost of wisdom" |
| **Glimmering** | Identifies all items in inventory | "Mysteries are revealed in the light of reason" |
| **Gloomy** | All armor +2 AC, all weapons -1 max damage | "Those who defend seldom attack" |
| **Hidden** | -10 durability to one random item, +10 durability to all others | "New strength is forged through destruction" |
| **Holy** | Casts Phasing (random teleport on level) | "Wherever you go, there you are" |
| **Magical** | Casts Mana Shield | "While the spirit is vigilant the body thrives" |
| **Mysterious** | +5 to one random attribute, -1 to all others | "Some are weakened as one grows strong" |
| **Ornate** | +2 Holy Bolt levels, -10% max mana | "Salvation comes at the cost of wisdom" |
| **Quiet** | +2 Vitality | "The essence of life flows from within" |
| **Religious** | Repairs all items to full durability | "Time cannot diminish the power of steel" |
| **Sacred** | +2 Charged Bolt levels, -10% max mana | "Energy comes at the cost of wisdom" |
| **Secluded** | Reveals full automap for current level | "The way is made clear when viewed from above" |
| **Spiritual** | Fills empty inventory slots with gold | "Riches abound when least expected" |
| **Spooky** | Restores other players' HP/Mana (MP); nothing useful in SP | "Where avarice fails, patience gains reward" |
| **Stone** | Recharges all staves in inventory | "The powers of mana refocused renews" |
| **Tainted** | +1 to one random stat for other players; -1 for activator (MP only) | "Those who are last may yet be first" |
| **Thaumaturgic** | Refills all chests on level (singleplayer only) | "What once was opened now is closed" |
| **Weird** | +1 to maximum weapon damage | "The sword of justice is swift and sharp" |

### Reusable Water Features

| Feature | Effect | Uses |
|---------|--------|------|
| Blood Fountain | +1 HP per use | Unlimited |
| Purifying Spring | +1 Mana per use | Unlimited |
| Fountain of Tears | +1 to one random attribute, -1 to another | Unlimited |
| Murky Pool | Casts Infravision | Unlimited |
| Goat Shrine | Random shrine effect | One use |
| Cauldron | Random shrine effect | One use |

---

## 18. Multiplayer

### Connection Methods

| Method | Players | Protocol | Notes |
|--------|---------|----------|-------|
| Battle.net | 1-4 | TCP/IP (Internet) | Free service; peer-to-peer game hosting |
| Local Area Network | 1-4 | IPX | Lowest latency |
| Modem | 2 | Serial/modem | Direct dial connection |
| Serial Cable | 2 | RS-232 | Direct physical connection |

### Battle.net Features

- **Account system**: Free username/password registration
- **Chat channels**: Public lobbies for finding games
- **Game listing**: Browse and join available games
- **No server-side saves**: Character data stored on client machine (prone to hacking/duping)
- **Peer-to-peer**: Once in game, players connect directly; Battle.net only for matchmaking

### Multiplayer Differences from Singleplayer

| Feature | Singleplayer | Multiplayer |
|---------|-------------|-------------|
| Save system | Save anywhere, load saves | Character saved on exit; no save-scumming |
| Death penalty | Reload last save | Drop all equipped items + gold at death location |
| Quests available | All 16 quests (randomized groups) | 4 quests only: Butcher, King Leoric, Lazarus, Diablo |
| Dungeon reset | Fixed per save | Regenerates each game session |
| Difficulty levels | Normal only | Normal, Nightmare, Hell (sequential) |
| Experience cap | None | 200*clvl or next_level_xp/20 |
| Friendly fire | N/A | PvP enabled (toggle-able) |
| Shrine effects | Standard | Some shrines affect other players (Spooky, Tainted) |

### Difficulty Levels (Multiplayer)

| Difficulty | Monster HP | Monster Damage | Monster AC | Monster To-Hit | Unlocked After |
|------------|-----------|---------------|-----------|---------------|---------------|
| Normal | 1x | 1x | 1x | 1x | Start |
| Nightmare | 3x | 3x | ~1.5x | ~1.5x | Beating Normal |
| Hell | 4.5-5x | 4.5x | ~2x | ~2x | Beating Nightmare |

### PvP (Player vs Player)

- **Activation**: Any player can toggle PvP mode on/off
- **Combat**: Same formulas as PvE but against player stats
- **Death**: Victim drops equipped items and gold
- **Etiquette**: No formal dueling system; often chaotic in public games
- **Town safety**: PvP attacks do not work in Tristram

---

## 19. UI Layout & Screen Flow

### Main Game HUD

```
+----------------------------------------------------------------+
|                                                                |
|                                                                |
|                     GAME VIEWPORT                              |
|                   (Isometric dungeon)                          |
|                   640 x 352 pixels                             |
|                                                                |
|                                                                |
+----------------------------------------------------------------+
|  [Health    ] [CHAR] [QUEST] [MAP] [MENU] [INV] [SPELL] [Mana]|
|  [  Orb     ] [    BELT SLOTS 1-8 (potions)    ] [  Orb  ]    |
|  [  (Red)   ]                                    [ (Blue) ]    |
+----------------------------------------------------------------+
```

**Bottom Panel (128 pixels high)**:
- **Left**: Red health orb (fills/drains proportionally to current/max HP)
- **Right**: Blue mana orb (fills/drains proportionally to current/max Mana)
- **Center-top row**: Button icons for Character Screen (C), Quest Log (Q), Automap (Tab), Menu (Esc), Inventory (I), Spellbook (B)
- **Center-bottom row**: 8 belt slots for quick-use items (hotkeys 1-8)

### Screen Modes

| Screen | Hotkey | Position | Description |
|--------|--------|----------|-------------|
| Character Screen | C | Left half of viewport | Shows all stats, attributes, resistances, damage |
| Inventory | I | Right half of viewport | Grid-based inventory + equipment slots |
| Spellbook | B | Left half of viewport | 4-page spell list with current levels |
| Automap | Tab | Overlay on viewport | Semi-transparent dungeon map explored areas |
| Quest Log | Q | Left half of viewport | Lists active and completed quests |
| Game Menu | Esc | Center overlay | Save/Load/Options/Quit |

### Character Sheet Display

```
+---------------------------+
| CHARACTER NAME             |
| CLASS      Level XX        |
| Experience: XXXXXXX        |
| Next Level: XXXXXXX        |
+---------------------------+
| Strength:  XX  Base XX     |
| Magic:     XX  Base XX     |
| Dexterity: XX  Base XX     |
| Vitality:  XX  Base XX     |
+---------------------------+
| Life:   XXX / XXX          |
| Mana:   XXX / XXX          |
+---------------------------+
| Armor Class: XX            |
| To Hit:      XX%           |
| Damage:      XX-XX         |
+---------------------------+
| Resist Magic:    XX%       |
| Resist Fire:     XX%       |
| Resist Lightning: XX%      |
+---------------------------+
```

### Inventory Screen Layout

```
+------------------------------------------+
|  [Head]                                   |
|  [Ring L] [Body Armor] [Ring R]           |
|  [Left Hand]       [Right Hand]           |
|  [Amulet]                                 |
+------------------------------------------+
|  10 x 4 Grid Inventory                    |
|  +--+--+--+--+--+--+--+--+--+--+         |
|  |  |  |  |  |  |  |  |  |  |  |         |
|  +--+--+--+--+--+--+--+--+--+--+         |
|  |  |  |  |  |  |  |  |  |  |  |         |
|  +--+--+--+--+--+--+--+--+--+--+         |
|  |  |  |  |  |  |  |  |  |  |  |         |
|  +--+--+--+--+--+--+--+--+--+--+         |
|  |  |  |  |  |  |  |  |  |  |  |         |
|  +--+--+--+--+--+--+--+--+--+--+         |
|                              [GOLD: XXXX] |
+------------------------------------------+
```

### Mouse Interaction

| Action | Left Click | Right Click |
|--------|-----------|-------------|
| Ground | Move to location | Cast selected spell at location |
| Monster | Melee/ranged attack | Cast selected spell at monster |
| NPC | Talk/interact | Cast selected spell |
| Item (ground) | Pick up | N/A |
| Item (inventory) | Pick up / place | N/A |
| Potion (belt) | Use potion | N/A |
| Door | Open/close | Cast selected spell |
| Shrine | Activate | Cast selected spell |
| Chest/Barrel | Open/break | Cast selected spell |

### Spell Selection

- **Right-click spell**: Selected via spellbook or hotkey (S + function key F1-F8 to assign)
- **Quick-cast**: Hotkeys F5-F8 for spell quick slots
- **Current spell indicator**: Displayed at bottom-right of screen near mana orb

---

## 20. Audio Design

### Music

Composed by **Matt Uelmen** — recognized with the inaugural IGDA Excellence in Audio award (2001).

| Track | Location | Style | Duration |
|-------|----------|-------|----------|
| **Tristram** | Town of Tristram | Acoustic 12-string guitar with flute; melancholic, haunting | ~8:00 |
| **Cathedral** | Dungeon Levels 1-4 | Dark ambient; sparse percussion, distant echoes | ~5:30 |
| **Catacombs** | Dungeon Levels 5-8 | Industrial ambient; processed electric guitar, eerie drones | ~6:00 |
| **Caves** | Dungeon Levels 9-12 | Oppressive atmosphere; rumbling bass, metallic textures | ~5:00 |
| **Hell** | Dungeon Levels 13-16 | Intense dark ambient; ominous choir samples, distorted tones | ~6:00 |

#### Tristram Theme Details

- Opens with solo 12-string acoustic guitar
- Flute enters as secondary melody
- Gradually acquires deeper, foreboding timbre from cello/string elements
- Features dissonant chord progressions and unexpected fade-outs
- Considered one of the most iconic video game music pieces; reused in Diablo II and III

### Sound Effects

| Category | Examples |
|----------|---------|
| Player attacks | Sword swing, axe chop, bow release, arrow impact, spell cast |
| Monster sounds | Growls, screams, death cries (unique per monster family) |
| Environmental | Door creak, chest open, barrel break, torch crackle, water drip |
| UI | Button click, inventory equip/unequip, gold pickup, potion drink |
| Combat feedback | Hit impact (flesh), miss (whoosh), critical hit (louder impact), block (shield clang) |
| Spell effects | Fireball explosion, lightning crackle, healing chime, town portal hum |
| The Butcher | "Ah, fresh meat!" (iconic voice line on door open) |
| Skeleton King | Bone rattle, sword clash |
| Diablo | Deep growl, Apocalypse rumble |
| NPC greetings | Each NPC has voiced greeting lines when approached |

### Audio Technical Details

| Property | Value |
|----------|-------|
| Music format | Redbook CD audio (tracks on game disc) or WAV |
| Sound effects format | WAV (22050 Hz, 8/16-bit) |
| Channels | Stereo music; mono sound effects with positional panning |
| Sound attenuation | Sound volume decreases with distance from source |
| Simultaneous sounds | Up to 16 concurrent sound effect channels |
| Volume controls | Separate Music and Sound Effect volume sliders in options |
| Voice | Selected NPC dialogue fully voiced; player character has attack grunts |

---

## Appendix A: Difficulty Multipliers (Multiplayer)

| Stat | Normal | Nightmare | Hell |
|------|--------|-----------|------|
| Monster HP | x1 | x3 | x4.5 |
| Monster Damage | x1 | x3 | x4.5 |
| Monster AC | x1 | x1.4 | x2 |
| Monster To-Hit | x1 | x1.4 | x2 |
| Player Resistance Cap | 75% | 75% | 75% |
| Item Drops | Normal | Better qlvl | Best qlvl |
| XP Multiplier | x1 | x1 | x1 |

## Appendix B: Dungeon Level Composition

| Dungeon Level | Tileset | Min Monster Types | Boss/Quest Content |
|---------------|---------|------------------|-------------------|
| 1 | Cathedral | 3-4 | Entry level; possible Butcher quest trigger |
| 2 | Cathedral | 4-5 | The Butcher (quest); Poisoned Water entrance |
| 3 | Cathedral | 4-5 | Skeleton King (King Leoric's Tomb entrance) |
| 4 | Cathedral | 4-5 | Gharbad the Weak; Ogden's Sign |
| 5 | Catacombs | 4-5 | Magic Rock; Arkaine's Valor |
| 6 | Catacombs | 4-5 | Chamber of Bone (always present) |
| 7 | Catacombs | 4-5 | Halls of the Blind |
| 8 | Catacombs | 4-5 | Zhar the Mad |
| 9 | Caves | 4-5 | Black Mushroom |
| 10 | Caves | 4-5 | Anvil of Fury |
| 11 | Caves | 4-5 | Standard |
| 12 | Caves | 4-5 | Standard |
| 13 | Hell | 4-5 | Warlord of Blood |
| 14 | Hell | 4-5 | Lachdanan |
| 15 | Hell | 4-5 | Archbishop Lazarus (lair entrance) |
| 16 | Hell | 3-4 | **Diablo** (final boss) |

## Appendix C: Complete Game Flow

```
1. Title Screen -> New Game / Load Game / Multiplayer
2. Character Creation: Choose class (Warrior/Rogue/Sorcerer), enter name
3. Start in Town of Tristram
4. Talk to NPCs for quests and lore
5. Enter Cathedral (dungeon level 1)
6. Clear dungeon levels, find stairs down
7. Return to town via Town Portal scroll/spell for healing, selling, buying
8. Complete optional quests for unique item rewards
9. Progress through Cathedral (1-4) -> Catacombs (5-8) -> Caves (9-12) -> Hell (13-16)
10. Level 15: Obtain Staff of Lazarus, enter Lazarus' Lair, defeat Archbishop Lazarus
11. Level 16: Pull bone levers, enter Diablo's chamber, defeat Diablo
12. Ending cinematic: Hero plunges soulstone into forehead
13. (Multiplayer): Continue to Nightmare/Hell difficulties
```
