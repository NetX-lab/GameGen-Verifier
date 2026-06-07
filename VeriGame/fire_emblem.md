# Fire Emblem: The Blazing Blade -- Complete Game Specification

> A comprehensive specification for faithfully recreating Fire Emblem: The Blazing Blade (Fire Emblem 7, Intelligent Systems / Nintendo, 2003 GBA). This document covers every system, formula, class, weapon, terrain tile, and interaction required for a full clone of the definitive classic GBA tactical RPG.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Tactical Mechanics](#3-core-tactical-mechanics)
4. [Combat Formulas](#4-combat-formulas)
5. [Weapon Triangle & Trinity of Magic](#5-weapon-triangle--trinity-of-magic)
6. [Weapon Types & Complete Weapon Tables](#6-weapon-types--complete-weapon-tables)
7. [Weapon Ranks & Weapon Experience](#7-weapon-ranks--weapon-experience)
8. [All Unit Classes & Promotions](#8-all-unit-classes--promotions)
9. [Stats System & Growth Rates](#9-stats-system--growth-rates)
10. [Experience System](#10-experience-system)
11. [Support System & Affinities](#11-support-system--affinities)
12. [Terrain System](#12-terrain-system)
13. [Rescue & Drop Mechanics](#13-rescue--drop-mechanics)
14. [Fog of War](#14-fog-of-war)
15. [Chapter Structure & Campaign Flow](#15-chapter-structure--campaign-flow)
16. [Economy: Gold, Shops & Arena](#16-economy-gold-shops--arena)
17. [Permadeath & Game Over](#17-permadeath--game-over)
18. [Tactician System](#18-tactician-system)
19. [UI Layout](#19-ui-layout)
20. [Audio Design](#20-audio-design)

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Full title | Fire Emblem: The Blazing Blade (known as "Fire Emblem" in the West) |
| Developer | Intelligent Systems |
| Publisher | Nintendo |
| Platform | Game Boy Advance |
| Release | JP: April 25, 2003 / NA: November 3, 2003 / EU: July 16, 2004 |
| Genre | Turn-based tactical role-playing game (SRPG) |
| Perspective | Top-down 2D grid map; side-view battle animations |
| Input | D-pad + A/B/L/R/Start/Select (standard GBA controls) |
| Players | 1 (story); 2-4 (link cable multiplayer) |
| Save slots | 3 |

### Objective

Command a roster of unique characters across grid-based tactical maps. Move units, attack enemies, seize objectives, and protect allies. Defeat the enemy forces and fulfill the chapter's win condition (Seize throne, Defeat boss, Survive X turns, or Rout all enemies).

### Lose Conditions

- **Lord death**: If Eliwood, Hector, or Lyn (the three Lord characters) is killed in combat, the game ends immediately (Game Over).
- **All other units**: When any non-Lord unit reaches 0 HP, they die permanently (permadeath) and are removed from the roster for the remainder of the playthrough.

### Campaign Structure

The game consists of three sequential tales:

| Tale | Protagonist | Chapters | Difficulty |
|------|-------------|----------|------------|
| Lyn's Tale (Tutorial) | Lyndis | Prologue + Ch. 1-10 (+ 1 gaiden) | Easy / tutorial |
| Eliwood's Story | Eliwood | Ch. 11-30 (+ 7 gaiden chapters) | Normal and Hard |
| Hector's Story (unlocked) | Hector | Ch. 11-32 (+ 8 gaiden chapters) | Normal and Hard |
| Final Chapter | All three lords | Ch. 31E / 33H: Light | Boss gauntlet |

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Native resolution | 240 x 160 pixels |
| Color depth | 15-bit (32,768 colors) |
| Tile size (map) | 16 x 16 pixels per grid cell |
| Visible map area | 15 x 10 tiles on screen at once |
| Sprite layers | 4 background layers + OAM (128 hardware sprites) |
| Frame rate | 60 FPS (hardware V-blank driven) |

### Coordinate System

- Origin (0, 0) at top-left of the map grid.
- Maps range from approximately 15 x 10 tiles (small indoor) to 35 x 30+ tiles (large outdoor).
- The camera scrolls to follow the cursor; units are always addressed by integer grid coordinates (column, row).

### Game Loop (Per Turn)

```
PHASE: PLAYER TURN
  1. Begin-of-turn effects:
     a. Terrain healing (Fort: +20% max HP; Gate/Throne: +10% max HP)
     b. Status condition tick-down (Sleep, Silence, Berserk: duration -= 1)
     c. Support points accumulate for adjacent pairs
  2. Player selects and moves units (any order):
     a. Select unit -> display movement range (blue tiles)
     b. Choose destination tile -> display action menu
     c. Execute action: Attack, Item, Staff, Trade, Rescue, Drop, Talk, Visit, Shop, Seize, Wait
     d. Unit grays out after acting (except mounted units with remaining Canto movement)
  3. Player ends turn (or all units have acted)

PHASE: ENEMY TURN
  1. AI evaluates all enemy units
  2. Each enemy unit acts in order (move + attack/heal)
  3. AI priorities: attack vulnerable targets > heal allies > advance toward objectives

PHASE: NPC/OTHER TURN (green units)
  1. Allied NPC units act under AI control
  2. Behavior: typically move toward player units or defend positions

PHASE: END OF TURN
  1. Increment turn counter
  2. Check chapter victory/defeat conditions
  3. Return to Player Turn
```

---

## 3. Core Tactical Mechanics

### Movement

- Each unit has a **Movement (Mov)** stat defining maximum tiles traversable per turn.
- Movement is consumed by terrain costs (see Section 12).
- Units cannot pass through enemy-occupied tiles.
- Allied units can pass through each other's tiles but cannot end on an occupied tile.
- **Mounted units** (Cavalier, Paladin, Nomad, Troubadour, Wyvern Rider, Pegasus Knight, etc.) possess the **Canto** ability: after performing an action (Attack, Item use), they may use any remaining movement points to continue moving.

### Actions

| Action | Description |
|--------|-------------|
| Attack | Engage an enemy unit within weapon range. Initiates combat. |
| Staff | Use an equipped staff (healing, warp, status infliction). |
| Item | Use a consumable item (Vulnerary, Elixir, Antitoxin, etc.) or equip a different weapon. |
| Trade | Swap items with an adjacent allied unit (does not end turn unless unit also Waits). |
| Rescue | Pick up an adjacent ally whose Con <= your Aid. Rescued unit is carried. |
| Drop | Place a rescued unit on an adjacent empty tile. |
| Give/Take | Transfer a rescued unit to/from an adjacent ally. |
| Visit | Enter a village tile to receive items, gold, or recruit characters. |
| Shop/Armory | Purchase weapons or items from a shop tile. |
| Talk | Initiate a special conversation with a specific adjacent unit (recruitment, story). |
| Seize | (Lord only) Capture a throne/gate tile to complete the chapter. |
| Wait | End the unit's turn at their current position. |
| Dance/Play | (Dancer/Bard only) Refresh an adjacent allied unit, allowing them to act again this turn. |
| Steal | (Thief/Assassin only) Steal a non-equipped item from an adjacent enemy if your Spd >= their Spd and the item's weight <= your Con. |
| Pick (Lockpick) | (Thief only) Open a locked door or chest without a key. |

### Item Management

- Each unit carries up to **5 items** in their inventory.
- The first item slot is the **equipped weapon** (the unit will use this in combat).
- Items have limited **durability** (Uses). When uses reach 0, the item breaks and is removed.
- **Convoy/Supply**: Merlinus (Transporter) holds overflow items. From Chapter 13x onward, items can be sent to/retrieved from the convoy during Battle Preparations or by visiting Merlinus on the map (if he is deployed).

---

## 4. Combat Formulas

### Attack Power (Atk)

```
Physical: Atk = Str + [Mt + T_atk] * E + Atk_support
Magical:  Atk = Mag + [Mt + T_atk] * E + Atk_support

Where:
  Mt      = Weapon Might
  T_atk   = Weapon Triangle attack bonus (+1 advantage, -1 disadvantage, 0 neutral)
  E        = Effectiveness multiplier:
             1 (normal), 2 (effective, English version), 3 (effective, Japanese version)
  Atk_support = cumulative attack bonus from support partners within 3 tiles
```

**Special cases:**
- Light Brand and Runesword at range 2: Atk = Str/2 + Mt (halved Strength).
- Nosferatu: Damage dealt is recovered as HP by the attacker.
- Luna: Ignores enemy Def/Res entirely (Might = 0, but negates defense).
- Eclipse: Reduces enemy HP to half current HP (no kill).

### Damage (Dmg)

```
Dmg = Atk_attacker - Def_target    (physical weapons)
Dmg = Atk_attacker - Res_target    (magical weapons / staves that deal damage)

Minimum damage = 0 (attacks can deal 0 damage)

Critical Hit Damage = Dmg * 3
```

### Attack Speed (AS)

```
AS = Spd - max(0, Wt - Con)

Where:
  Spd = unit's Speed stat
  Wt  = equipped weapon's Weight
  Con = unit's Constitution
```

If `Wt <= Con`, the weapon imposes no speed penalty.

### Doubling Threshold

```
If AS_attacker >= AS_defender + 4:
    Attacker strikes TWICE (double attack)

Brave weapons: Each "strike" becomes TWO hits.
    Normal attack: 2 hits; Double attack with Brave weapon: 4 hits.
```

### Hit Rate

```
Hit = Hit_weapon + (Skl * 2) + (Lck / 2) + T_hit + Hit_support + Hit_Srank + Hit_tactician

Where:
  Hit_weapon  = weapon's base Hit value
  Skl         = unit's Skill stat
  Lck         = unit's Luck stat (integer division, rounded down)
  T_hit       = Weapon Triangle hit bonus (+15 advantage, -15 disadvantage, 0 neutral)
  Hit_support = cumulative hit bonus from support partners within 3 tiles
  Hit_Srank   = +5 if unit has S rank in equipped weapon type
  Hit_tactician = +1 per tactician star if unit shares tactician's affinity
```

### Avoid (Avo)

```
Avo = (AS * 2) + Lck + Avo_support + Avo_terrain + Avo_tactician

Where:
  AS           = Attack Speed (as calculated above)
  Lck          = unit's Luck stat
  Avo_support  = cumulative avoid bonus from support partners within 3 tiles
  Avo_terrain  = terrain avoid bonus (see Section 12)
  Avo_tactician = +1 per tactician star (all units)
```

### Displayed Hit Rate

```
Displayed_Hit = Hit_attacker - Avo_target
Clamped to range [0, 100]
```

**True Hit (2-RN system):** FE7 uses a **two random number** system. Two random numbers (0-99) are generated and averaged. This makes displayed hit rates above 50% more reliable than shown, and rates below 50% less reliable. Effective true hit probabilities:

| Displayed | True % (approx) |
|-----------|-----------------|
| 10% | ~2% |
| 25% | ~11% |
| 50% | ~50% |
| 75% | ~89% |
| 90% | ~98% |
| 99% | ~100% |

### Critical Rate

```
Crit = Crit_weapon + (Skl / 2) + Crit_support + Crit_class + Crit_Srank

Where:
  Crit_weapon  = weapon's base Critical value
  Skl          = unit's Skill stat (integer division)
  Crit_support = cumulative crit bonus from support partners
  Crit_class   = +15 for Swordmaster and Berserker classes; 0 for all others
  Crit_Srank   = +5 if unit has S rank in equipped weapon type
```

### Critical Avoid (Crit Avo)

```
CritAvo = Lck + CritAvo_support + CritAvo_tactician

Where:
  Lck              = unit's Luck stat
  CritAvo_support  = cumulative crit-avoid bonus from support partners
  CritAvo_tactician = +1 per tactician star (all units)
```

### Displayed Critical

```
Displayed_Crit = max(0, Crit_attacker - CritAvo_target)
```

### Actual Critical Probability

Critical is rolled independently from hit. A critical can only occur if the attack hits.

```
Actual_Crit% = (True_Hit% / 100) * Displayed_Crit
```

Critical uses a **single RN** (not the 2-RN system used for hit).

### Combat Sequence

```
1. Attacker strikes (check hit -> if hit, deal damage; check crit)
2. If defender is alive and can counter (has weapon with correct range):
   Defender strikes back (check hit -> damage; check crit)
3. If attacker has double attack (AS >= defender AS + 4) and defender still alive:
   Attacker strikes again
4. If defender has double attack and attacker still alive:
   Defender strikes again

Brave weapons: Each "strike" above becomes TWO consecutive hits.

Special: Assassin's Lethality (Silencer) skill:
  - 50% chance of instant kill on each hit by an Assassin
  - Actually: Crit% chance to activate; if it activates, target is instantly killed
  - Activation rate = Skl/2 (same as crit formula component)
```

---

## 5. Weapon Triangle & Trinity of Magic

### Physical Weapon Triangle

```
Swords > Axes > Lances > Swords

  Sword beats Axe:   Sword user gains +1 Atk, +15 Hit; Axe user gets -1 Atk, -15 Hit
  Axe beats Lance:   Axe user gains +1 Atk, +15 Hit; Lance user gets -1 Atk, -15 Hit
  Lance beats Sword:  Lance user gains +1 Atk, +15 Hit; Sword user gets -1 Atk, -15 Hit
```

### Trinity of Magic

```
Anima > Light > Dark > Anima

  Anima beats Light:  Anima user gains +1 Atk, +15 Hit; Light user gets -1 Atk, -15 Hit
  Light beats Dark:   Light user gains +1 Atk, +15 Hit; Dark user gets -1 Atk, -15 Hit
  Dark beats Anima:   Dark user gains +1 Atk, +15 Hit; Anima user gets -1 Atk, -15 Hit
```

### Neutral Matchups

Bows, Staves, and all cross-category matchups (physical vs magic) are **neutral** -- no triangle bonus or penalty applies.

---

## 6. Weapon Types & Complete Weapon Tables

### Swords

*Light, accurate, and moderate in power. Favored by Myrmidons, Mercenaries, and Lords.*

| Weapon | Rank | Mt | Hit | Crit | Wt | Range | Uses | Cost | Special |
|--------|------|----|-----|------|----|-------|------|------|---------|
| Iron Sword | E | 5 | 90 | 0 | 5 | 1 | 46 | 460 | -- |
| Slim Sword | E | 3 | 100 | 5 | 2 | 1 | 30 | 480 | -- |
| Steel Sword | D | 8 | 75 | 0 | 10 | 1 | 30 | 600 | -- |
| Silver Sword | A | 13 | 80 | 0 | 8 | 1 | 20 | 1500 | -- |
| Iron Blade | D | 9 | 65 | 0 | 12 | 1 | 35 | 980 | -- |
| Steel Blade | C | 11 | 60 | 0 | 14 | 1 | 25 | 1250 | -- |
| Silver Blade | A | 14 | 60 | 0 | 13 | 1 | 15 | 1800 | -- |
| Brave Sword | B | 9 | 75 | 0 | 12 | 1 | 30 | 3000 | Strikes twice per attack |
| Killing Edge | C | 9 | 75 | 30 | 7 | 1 | 20 | 1300 | High crit |
| Lancereaver | C | 9 | 75 | 5 | 11 | 1 | 15 | 1800 | Reverses weapon triangle vs lances |
| Armorslayer | D | 8 | 80 | 0 | 11 | 1 | 18 | 1260 | Effective vs armored |
| Wyrmslayer | C | 7 | 75 | 0 | 8 | 1 | 20 | 3360 | Effective vs wyverns/dragons |
| Light Brand | C | 9 | 70 | 0 | 9 | 1-2 | 25 | -- | Range 2: targets Res; Str halved |
| Wind Sword | C | 9 | 70 | 0 | 9 | 1-2 | 25 | -- | Range 2: targets Res; effective vs fliers |
| Rapier | Prf | 7 | 95 | 10 | 5 | 1 | 40 | -- | Eliwood/Lyn only; effective vs cavalry and armored |
| Mani Katti | Prf | 8 | 80 | 20 | 3 | 1 | 45 | -- | Lyn only; effective vs cavalry and armored |
| Durandal | Prf | 17 | 90 | 0 | 16 | 1 | 20 | -- | Eliwood only; +5 Str when equipped; legendary |
| Sol Katti | Prf | 12 | 95 | 25 | 14 | 1 | 30 | -- | Lyn only; legendary |
| Regal Blade | S | 20 | 85 | 0 | 9 | 1 | 25 | -- | -- |
| Runesword | -- | 12 | 65 | 0 | 11 | 1-2 | 15 | -- | Drains HP; cannot crit; enemy only typically |

### Lances

*Balanced power and accuracy. Favored by Cavaliers, Knights, Pegasus Knights.*

| Weapon | Rank | Mt | Hit | Crit | Wt | Range | Uses | Cost | Special |
|--------|------|----|-----|------|----|-------|------|------|---------|
| Iron Lance | E | 7 | 80 | 0 | 8 | 1 | 45 | 360 | -- |
| Slim Lance | E | 4 | 85 | 5 | 4 | 1 | 30 | 450 | -- |
| Steel Lance | D | 10 | 70 | 0 | 13 | 1 | 30 | 480 | -- |
| Silver Lance | A | 14 | 75 | 0 | 10 | 1 | 20 | 1200 | -- |
| Brave Lance | B | 10 | 70 | 0 | 14 | 1 | 30 | 3000 | Strikes twice per attack |
| Killer Lance | C | 10 | 70 | 30 | 9 | 1 | 20 | 1200 | High crit |
| Javelin | E | 6 | 65 | 0 | 11 | 1-2 | 20 | 400 | Indirect capable |
| Short Spear | C | 9 | 60 | 0 | 12 | 1-2 | 18 | 900 | Indirect capable |
| Spear | A | 14 | 70 | 0 | 10 | 1-2 | 15 | 3000 | Indirect + brave-tier stats |
| Axereaver | C | 10 | 70 | 5 | 11 | 1 | 15 | 1950 | Reverses weapon triangle vs axes |
| Horseslayer | D | 7 | 70 | 0 | 9 | 1 | 16 | 1040 | Effective vs cavalry |
| Heavy Spear | D | 9 | 70 | 0 | 14 | 1 | 16 | 1200 | Effective vs armored |
| Rex Hasta | S | 21 | 80 | 0 | 11 | 1 | 25 | -- | -- |

### Axes

*Heavy and powerful but inaccurate. Favored by Fighters, Pirates, and Warriors.*

| Weapon | Rank | Mt | Hit | Crit | Wt | Range | Uses | Cost | Special |
|--------|------|----|-----|------|----|-------|------|------|---------|
| Iron Axe | E | 8 | 75 | 0 | 10 | 1 | 45 | 270 | -- |
| Steel Axe | E | 11 | 65 | 0 | 15 | 1 | 30 | 360 | -- |
| Silver Axe | A | 15 | 70 | 0 | 12 | 1 | 20 | 1000 | -- |
| Brave Axe | B | 10 | 65 | 0 | 16 | 1 | 30 | 3000 | Strikes twice per attack |
| Killer Axe | C | 11 | 65 | 30 | 11 | 1 | 20 | 1000 | High crit |
| Hand Axe | E | 7 | 60 | 0 | 12 | 1-2 | 20 | 300 | Indirect capable |
| Tomahawk | A | 13 | 65 | 0 | 14 | 1-2 | 15 | 3000 | Indirect capable |
| Swordreaver | C | 11 | 65 | 5 | 13 | 1 | 15 | 2100 | Reverses weapon triangle vs swords |
| Halberd | D | 10 | 60 | 0 | 12 | 1 | 18 | 810 | Effective vs cavalry |
| Hammer | D | 10 | 55 | 0 | 15 | 1 | 20 | 800 | Effective vs armored |
| Devil Axe | E | 18 | 55 | 0 | 18 | 1 | 20 | 900 | (31 - Lck)% chance of damaging self |
| Wolf Beil | Prf | 10 | 75 | 5 | 10 | 1 | 30 | -- | Hector only; effective vs cavalry and armored |
| Armads | Prf | 18 | 85 | 0 | 18 | 1 | 25 | -- | Hector only; +5 Def when equipped; legendary |
| Basilikos | S | 22 | 75 | 0 | 13 | 1 | 25 | -- | -- |

### Bows

*Ranged-only weapons. Effective against all flying units (x2 damage). Cannot counter at melee range.*

| Weapon | Rank | Mt | Hit | Crit | Wt | Range | Uses | Cost | Special |
|--------|------|----|-----|------|----|-------|------|------|---------|
| Iron Bow | E | 6 | 85 | 0 | 5 | 2 | 45 | 540 | -- |
| Steel Bow | D | 9 | 70 | 0 | 9 | 2 | 30 | 720 | -- |
| Silver Bow | A | 13 | 75 | 0 | 6 | 2 | 20 | 1600 | -- |
| Brave Bow | B | 10 | 70 | 0 | 12 | 2 | 30 | 3000 | Strikes twice per attack |
| Killer Bow | C | 9 | 75 | 30 | 7 | 2 | 20 | 1400 | High crit |
| Short Bow | D | 5 | 85 | 10 | 3 | 2 | 22 | 1760 | -- |
| Longbow | A | 5 | 65 | 0 | 10 | 2-3 | 20 | -- | Extended range |
| Ballista | -- | 8 | 60 | 0 | -- | 3-10 | 5 | -- | Map-placed siege; immobile |
| Iron Ballista | -- | 13 | 55 | 0 | -- | 3-10 | 5 | -- | Siege engine |
| Killer Ballista | -- | 10 | 50 | 40 | -- | 3-10 | 5 | -- | Siege engine; high crit |
| Rienfleche | S | 20 | 80 | 0 | 7 | 2 | 25 | -- | -- |

### Anima Magic (Tomes)

*Balanced offensive magic. Beats Light in the Trinity of Magic.*

| Weapon | Rank | Mt | Hit | Crit | Wt | Range | Uses | Cost | Special |
|--------|------|----|-----|------|----|-------|------|------|---------|
| Fire | E | 5 | 90 | 0 | 4 | 1-2 | 40 | 560 | -- |
| Thunder | D | 8 | 80 | 5 | 6 | 1-2 | 35 | 700 | -- |
| Elfire | C | 10 | 85 | 0 | 10 | 1-2 | 30 | 1200 | -- |
| Fimbulvetr | A | 13 | 80 | 0 | 12 | 1-2 | 20 | 6000 | -- |
| Bolting | B | 12 | 60 | 0 | 20 | 3-10 | 5 | 2500 | Siege tome |
| Forblaze | Prf | 14 | 85 | 5 | 11 | 1-2 | 20 | -- | Athos Prf; legendary |
| Excalibur | S | 18 | 90 | 10 | 13 | 1-2 | 25 | -- | Effective vs fliers |

### Light Magic

*Accurate with high crit; weaker might. Beats Dark.*

| Weapon | Rank | Mt | Hit | Crit | Wt | Range | Uses | Cost | Special |
|--------|------|----|-----|------|----|-------|------|------|---------|
| Lightning | E | 4 | 95 | 5 | 6 | 1-2 | 35 | 630 | -- |
| Shine | D | 6 | 90 | 8 | 8 | 1-2 | 30 | 900 | -- |
| Divine | C | 8 | 85 | 10 | 12 | 1-2 | 25 | 2500 | -- |
| Purge | B | 10 | 75 | 5 | 20 | 3-10 | 5 | 3000 | Siege light |
| Aura | A | 12 | 85 | 15 | 15 | 1-2 | 20 | 8000 | -- |
| Aureola | S | 15 | 90 | 5 | 14 | 1-2 | 20 | -- | Effective vs monsters; legendary |
| Luce | Prf | 16 | 95 | 25 | 16 | 1-2 | 25 | -- | Athos Prf; legendary |

### Dark Magic

*Heavy and powerful. Unique effects. Beats Anima.*

| Weapon | Rank | Mt | Hit | Crit | Wt | Range | Uses | Cost | Special |
|--------|------|----|-----|------|----|-------|------|------|---------|
| Flux | D | 7 | 80 | 0 | 8 | 1-2 | 45 | 900 | -- |
| Nosferatu | C | 10 | 70 | 0 | 14 | 1-2 | 20 | 3200 | Drains HP equal to damage dealt |
| Luna | C | 0 | 95 | 20 | 12 | 1-2 | 35 | 4200 | Ignores target's Def/Res entirely |
| Eclipse | B | -- | 30 | 0 | 12 | 3-10 | 5 | -- | Halves target's current HP (siege) |
| Fenrir | A | 15 | 70 | 0 | 18 | 1-2 | 20 | 6000 | -- |
| Gespenst | S | 23 | 80 | 0 | 20 | 1-2 | 25 | -- | Heaviest and most powerful dark tome |
| Ereshkigal | Prf | 20 | 95 | 0 | 12 | 1-2 | -- | -- | Nergal only; infinite uses |

### Staves

*Support/utility weapons for Clerics, Bishops, Sages, Valkyries, Troubadours.*

| Staff | Rank | Range | Uses | Effect |
|-------|------|-------|------|--------|
| Heal | E | 1 | 30 | Restores Mag + 10 HP to adjacent ally |
| Mend | D | 1 | 20 | Restores Mag + 20 HP to adjacent ally |
| Recover | C | 1 | 15 | Restores target ally to full HP |
| Physic | B | 1 to Mag/2 | 15 | Restores Mag + 10 HP at range (no adjacency needed) |
| Fortify | A | All allies in Mag/2 range | 8 | Restores Mag + 10 HP to all allies in range |
| Restore | C | 1 | 10 | Removes all status conditions (Sleep, Silence, Berserk, Poison) |
| Barrier | C | 1 | 15 | Grants +7 Res for 1 turn (decays each subsequent turn) |
| Torch (staff) | D | Mag/2 area | 10 | Illuminates a targeted area in Fog of War (+4 tiles vision) |
| Unlock | D | 1 to Mag/2 | 10 | Opens a locked door or chest at range |
| Warp | A | 1 (target); anywhere in Mag/2 range (destination) | 5 | Teleports adjacent ally to any tile within range |
| Rescue (staff) | B | Mag/2 | 3 | Warps a distant ally to a tile adjacent to the caster |
| Hammerne | C | 1 | 3 | Fully repairs one weapon/staff/tome to max durability |
| Silence | B | 1 to Mag/2 | 3 | Inflicts Silence (cannot use magic) for ~3 turns |
| Sleep | B | 1 to Mag/2 | 3 | Inflicts Sleep (cannot act) for ~3 turns |
| Berserk | B | 1 to Mag/2 | 3 | Inflicts Berserk (attacks nearest unit, friend or foe) for ~3 turns |

### Consumable Items

| Item | Uses | Effect |
|------|------|--------|
| Vulnerary | 3 | Restores 10 HP |
| Elixir | 3 | Restores HP to full |
| Pure Water | 3 | +7 Res for 1 turn (decays by 1 per turn) |
| Antitoxin | 3 | Cures Poison status |
| Torch (item) | 5 | Increases unit's Fog of War vision by 4 tiles for the turn |
| Chest Key | 1 | Opens one chest |
| Door Key | 1 | Opens one door |
| Lockpick | 15 | Opens doors and chests (Thief only) |
| Mine | 1 | Places a hidden trap tile; deals 10 damage when stepped on |
| Light Rune | 1 | Places an invisible obstacle tile; blocks movement |
| Member Card | -- | Grants access to Secret Shops (unlimited uses; item slot occupied) |
| Silver Card | -- | Halves shop prices while in inventory |

### Promotion Items

| Item | Promotes | Classes |
|------|----------|---------|
| Hero Crest | Promotes at Lv 10+ | Mercenary, Myrmidon, Fighter |
| Knight Crest | Promotes at Lv 10+ | Cavalier, Knight |
| Orion's Bolt | Promotes at Lv 10+ | Archer, Nomad |
| Elysian Whip | Promotes at Lv 10+ | Pegasus Knight, Wyvern Rider |
| Guiding Ring | Promotes at Lv 10+ | Mage, Cleric, Monk, Troubadour, Shaman |
| Ocean Seal | Promotes at Lv 10+ | Pirate |
| Fell Contract | Promotes at Lv 10+ | Thief (to Assassin) |
| Heaven Seal | Promotes at Lv 10+ | Lord (Eliwood, Hector, Lyn) |
| Earth Seal | Promotes at Lv 10+ | Any unpromoted class (universal) |

### Stat-Boosting Items

| Item | Effect |
|------|--------|
| Angelic Robe | +7 HP |
| Energy Ring | +2 Str/Mag |
| Secret Book | +2 Skl |
| Speedwing | +2 Spd |
| Goddess Icon | +2 Lck |
| Dragonshield | +2 Def |
| Talisman | +2 Res |
| Body Ring | +2 Con |
| Boots | +2 Mov |
| Afa's Drops | +5% to all growth rates (one character; permanent) |

---

## 7. Weapon Ranks & Weapon Experience

### Weapon Rank Thresholds

| Rank | Cumulative WEXP Required |
|------|--------------------------|
| -- (none) | 0 |
| E | 1 |
| D | 31 |
| C | 71 |
| B | 121 |
| A | 181 |
| S | 251 |

- **Unpromoted units** are capped at 181 WEXP (cannot reach S rank until after promotion).
- **Each unit may hold only one S rank** across all weapon types (except Athos/Archsage and Nergal/Dark Druid).
- **S rank bonus:** +5 Hit, +5 Crit when using a weapon of the S-ranked type.

### Weapon Experience Gain

| Action | WEXP Gained |
|--------|-------------|
| Strike with weapon (per hit) | Weapon's WEXP value (typically 1-2) |
| Kill bonus | WEXP for killing blow is doubled |
| Use a staff | Staff's WEXP value (typically 2-8) |

**Common WEXP values by weapon:**

| Weapon | WEXP per use |
|--------|-------------|
| Iron weapons | 1 |
| Steel weapons | 2 |
| Silver weapons | 2 |
| Brave weapons | 1 |
| Killer weapons | 1 |
| Legendary (Prf) weapons | 2 |
| Heal staff | 2 |
| Mend staff | 2 |
| Physic staff | 4 |
| Recover staff | 4 |
| Warp/Rescue staff | 8 |
| Hammerne | 8 |
| Devil Axe | 8 |

---

## 8. All Unit Classes & Promotions

### Unpromoted Classes

| Class | Type | Weapons | Mov | Promotes To | Item Required |
|-------|------|---------|-----|-------------|---------------|
| Lord (Eliwood) | Infantry | Swords (D) | 5 | Knight Lord | Heaven Seal |
| Lord (Lyn) | Infantry | Swords (D) | 5 | Blade Lord | Heaven Seal |
| Lord (Hector) | Infantry | Axes (D) | 5 | Great Lord | Heaven Seal |
| Cavalier | Mounted (horse) | Swords (E), Lances (E) | 7 | Paladin | Knight Crest |
| Knight | Armored | Lances (D) | 4 | General | Knight Crest |
| Myrmidon | Infantry | Swords (D) | 5 | Swordmaster | Hero Crest |
| Mercenary | Infantry | Swords (D) | 5 | Hero | Hero Crest |
| Fighter | Infantry | Axes (D) | 5 | Warrior | Hero Crest |
| Archer | Infantry | Bows (D) | 5 | Sniper | Orion's Bolt |
| Nomad | Mounted (horse) | Bows (D) | 7 | Nomadic Trooper | Orion's Bolt |
| Mage | Infantry | Anima (D) | 5 | Sage | Guiding Ring |
| Monk | Infantry | Light (D) | 5 | Bishop | Guiding Ring |
| Shaman | Infantry | Dark (D) | 5 | Druid | Guiding Ring |
| Cleric | Infantry | Staves (D) | 5 | Bishop | Guiding Ring |
| Troubadour | Mounted (horse) | Staves (D) | 7 | Valkyrie | Guiding Ring |
| Pegasus Knight | Flying (pegasus) | Lances (D) | 7 | Falcon Knight | Elysian Whip |
| Wyvern Rider | Flying (wyvern) | Lances (D) | 7 | Wyvern Lord | Elysian Whip |
| Thief | Infantry | Swords (E) | 6 | Assassin | Fell Contract |
| Pirate | Infantry (water-walk) | Axes (D) | 5 | Berserker | Ocean Seal |
| Dancer | Infantry | -- | 5 | -- (no promotion) | -- |
| Bard | Infantry | -- | 5 | -- (no promotion) | -- |
| Transporter | Mounted (horse) | -- | 6 | -- (no promotion) | -- |

### Promoted Classes

| Class | Type | Weapons | Mov | Promotes From |
|-------|------|---------|-----|---------------|
| Knight Lord | Mounted (horse) | Swords, Lances | 7 | Lord (Eliwood) |
| Blade Lord | Infantry | Swords, Bows | 6 | Lord (Lyn) |
| Great Lord | Armored/Infantry | Axes, Swords | 5 | Lord (Hector) |
| Paladin | Mounted (horse) | Swords, Lances, +Axes (opt.) | 8 | Cavalier |
| General | Armored | Lances, +Axes | 5 | Knight |
| Swordmaster | Infantry | Swords | 6 | Myrmidon |
| Hero | Infantry | Swords, Axes | 6 | Mercenary |
| Warrior | Infantry | Axes, Bows | 6 | Fighter |
| Sniper | Infantry | Bows | 6 | Archer |
| Nomadic Trooper | Mounted (horse) | Bows, Swords | 8 | Nomad |
| Sage | Infantry | Anima, Staves | 6 | Mage |
| Bishop | Infantry | Light, Staves | 6 | Cleric, Monk |
| Druid | Infantry | Dark, Staves | 6 | Shaman |
| Valkyrie | Mounted (horse) | Light, Staves | 8 | Troubadour |
| Falcon Knight | Flying (pegasus) | Lances, Swords | 8 | Pegasus Knight |
| Wyvern Lord | Flying (wyvern) | Lances, Swords | 8 | Wyvern Rider |
| Assassin | Infantry | Swords | 6 | Thief |
| Berserker | Infantry (water-walk) | Axes | 6 | Pirate |

### Special / NPC / Boss Classes

| Class | Weapons | Notes |
|-------|---------|-------|
| Archsage | Anima, Light, Dark, Staves | Athos (NPC ally); joins for final chapters |
| Dark Druid | Dark, Anima, Staves | Nergal (final boss) |
| Magic Seal | -- | Kishuna (boss); nullifies all magic in radius |
| Fire Dragon | Fire breath | Final boss of the game |
| Bramimond | Dark | Story NPC |
| Soldier | Lances | Enemy-only generic infantry |
| Brigand | Axes | Enemy-only bandit |
| Corsair | Axes | Enemy-only pirate variant |

### Promotion Stat Bonuses

When a unit promotes (must be Level 10-20 of unpromoted class), they gain fixed stat bonuses and reset to Level 1 of the promoted class. Remaining levels: up to Level 20 promoted = effective maximum of Level 40 total.

| Promoted Class | HP | Str | Skl | Spd | Def | Res | Con | Mov |
|----------------|----|-----|-----|-----|-----|-----|-----|-----|
| Knight Lord (Eliwood) | +4 | +2 | +0 | +1 | +1 | +3 | +2 | +2 |
| Blade Lord (Lyn) | +3 | +2 | +2 | +0 | +3 | +5 | +1 | +1 |
| Great Lord (Hector) | +3 | +0 | +2 | +3 | +1 | +5 | +2 | +0 |
| Paladin (M) | +2 | +1 | +1 | +1 | +2 | +1 | +2 | +1 |
| Paladin (F) | +2 | +1 | +1 | +1 | +2 | +2 | +1 | +1 |
| General (M) | +4 | +2 | +2 | +3 | +2 | +3 | +2 | +1 |
| General (F) | +3 | +2 | +3 | +2 | +2 | +3 | +2 | +1 |
| Hero (M) | +4 | +0 | +2 | +2 | +2 | +2 | +1 | +1 |
| Hero (F) | +3 | +1 | +2 | +1 | +2 | +3 | +1 | +1 |
| Swordmaster (M) | +5 | +2 | +0 | +0 | +2 | +1 | +1 | +1 |
| Swordmaster (F) | +4 | +2 | +1 | +0 | +2 | +2 | +1 | +1 |
| Assassin | +3 | +1 | +0 | +0 | +2 | +2 | +0 | +0 |
| Warrior | +3 | +1 | +2 | +0 | +3 | +3 | +2 | +1 |
| Berserker | +4 | +1 | +1 | +1 | +2 | +2 | +3 | +1 |
| Sniper (M) | +3 | +1 | +2 | +2 | +2 | +3 | +1 | +1 |
| Sniper (F) | +4 | +3 | +1 | +1 | +2 | +2 | +1 | +1 |
| Nomadic Trooper (M) | +3 | +2 | +1 | +1 | +3 | +3 | +1 | +1 |
| Sage (M) | +3 | +1 | +1 | +0 | +3 | +3 | +1 | +1 |
| Sage (F) | +4 | +1 | +0 | +0 | +3 | +3 | +1 | +1 |
| Bishop (M) | +3 | +2 | +1 | +1 | +2 | +2 | +1 | +1 |
| Bishop (F) | +3 | +1 | +2 | +0 | +3 | +2 | +1 | +1 |
| Druid (M) | +4 | +0 | +0 | +3 | +2 | +2 | +1 | +1 |
| Falcon Knight | +5 | +2 | +0 | +0 | +2 | +2 | +1 | +1 |
| Wyvern Lord (M) | +4 | +0 | +2 | +2 | +0 | +2 | +1 | +1 |
| Valkyrie | +3 | +2 | +1 | +0 | +2 | +3 | +1 | +1 |

### Class-Specific Abilities

| Ability | Classes | Effect |
|---------|---------|--------|
| Canto | All mounted classes (Cavalier, Paladin, Knight Lord, Nomad, Nomadic Trooper, Troubadour, Valkyrie, Pegasus Knight, Falcon Knight, Wyvern Rider, Wyvern Lord) | After performing an action, may use remaining movement to reposition |
| Critical +15 | Swordmaster, Berserker | Permanent +15 critical rate |
| Lethality (Silencer) | Assassin | Chance to instantly kill target on each hit |
| Steal | Thief, Assassin | Can steal non-equipped items from enemies |
| Lockpick | Thief, Assassin | Can open doors and chests without keys |
| Dance | Dancer (Ninian) | Refreshes one adjacent ally to act again |
| Play | Bard (Nils) | Refreshes one adjacent ally to act again |
| Water Walk | Pirate, Berserker | Can traverse water/sea tiles |
| Fly | Pegasus Knight, Falcon Knight, Wyvern Rider, Wyvern Lord | Ignores terrain movement costs; crosses any tile |

---

## 9. Stats System & Growth Rates

### The Nine Stats

| Stat | Abbr | Description |
|------|------|-------------|
| Hit Points | HP | Unit's health. At 0 HP, the unit dies. |
| Strength | Str | Physical attack power. Added to weapon Might for physical damage. |
| Magic | Mag | Magical attack power. (In FE7, Str and Mag share the same stat slot per class: physical classes use Str, magic classes use Mag.) |
| Skill | Skl | Affects hit rate (x2) and critical rate (/2). |
| Speed | Spd | Affects Attack Speed and Avoid. Determines doubling. |
| Luck | Lck | Affects hit rate (+Lck/2), avoid (+Lck), and critical avoid (+Lck). |
| Defense | Def | Reduces incoming physical damage. |
| Resistance | Res | Reduces incoming magical damage. |
| Constitution | Con | Body size. Offsets weapon weight penalty (Wt - Con). Affects Rescue/Aid. |
| Movement | Mov | Maximum tiles a unit can traverse per turn. |

### Stat Caps by Class Tier

| Tier | HP | Str/Mag | Skl | Spd | Lck | Def | Res | Con | Mov |
|------|----|---------|-----|-----|-----|-----|-----|-----|-----|
| Unpromoted | 60 | 20 | 20 | 20 | 30 | 20 | 20 | 20 | 15 |
| Promoted (varies) | 60 | 22-30 | 24-30 | 22-30 | 30 | 20-30 | 20-30 | 20-25 | 15 |

### Selected Promoted Class Stat Caps

| Class | HP | Str | Skl | Spd | Lck | Def | Res | Con |
|-------|----|-----|-----|-----|-----|-----|-----|-----|
| Blade Lord | 60 | 24 | 29 | 30 | 30 | 22 | 22 | 25 |
| Knight Lord | 60 | 27 | 26 | 24 | 30 | 23 | 25 | 25 |
| Great Lord | 60 | 30 | 24 | 24 | 30 | 29 | 20 | 25 |
| Paladin (M) | 60 | 25 | 26 | 24 | 30 | 25 | 25 | 25 |
| Paladin (F) | 60 | 23 | 27 | 25 | 30 | 24 | 26 | 25 |
| General (M) | 60 | 29 | 27 | 24 | 30 | 30 | 25 | 20 |
| Swordmaster (M) | 60 | 24 | 29 | 30 | 30 | 22 | 23 | 25 |
| Swordmaster (F) | 60 | 22 | 29 | 30 | 30 | 22 | 25 | 25 |
| Hero (M) | 60 | 25 | 30 | 26 | 30 | 25 | 22 | 20 |
| Assassin | 60 | 20 | 30 | 30 | 30 | 20 | 20 | 20 |
| Warrior | 60 | 30 | 28 | 26 | 30 | 26 | 22 | 20 |
| Berserker | 60 | 30 | 29 | 28 | 30 | 23 | 21 | 20 |
| Sniper (M) | 60 | 25 | 30 | 28 | 30 | 25 | 23 | 20 |
| Sage (M) | 60 | 28 | 30 | 26 | 30 | 21 | 25 | 20 |
| Sage (F) | 60 | 30 | 28 | 26 | 30 | 21 | 25 | 20 |
| Bishop (M) | 60 | 25 | 26 | 24 | 30 | 22 | 30 | 25 |
| Bishop (F) | 60 | 25 | 25 | 26 | 30 | 21 | 30 | 20 |
| Druid (M) | 60 | 29 | 26 | 26 | 30 | 21 | 28 | 20 |
| Falcon Knight | 60 | 23 | 25 | 28 | 30 | 23 | 26 | 20 |
| Wyvern Lord (M) | 60 | 27 | 25 | 23 | 30 | 28 | 22 | 25 |
| Valkyrie | 60 | 25 | 24 | 25 | 30 | 24 | 28 | 20 |
| Nomadic Trooper (M) | 60 | 25 | 28 | 30 | 30 | 24 | 23 | 20 |

### Growth Rate Mechanics

When a unit levels up, each stat has an independent chance to increase by +1 based on that unit's **growth rate** for that stat.

```
For each stat S:
  Generate random number R in [0, 99]
  If R < GrowthRate_S:
    S += 1
```

- Growth rates are **per character**, not per class. They range from 0% to 90%+.
- FE7 implements **blank level-up protection**: if a level-up produces zero stat gains, the game re-rolls once to attempt to get at least one stat increase. (Only one re-roll.)

### Example Character Growth Rates

| Character | HP | Str | Skl | Spd | Lck | Def | Res |
|-----------|----|-----|-----|-----|-----|-----|-----|
| Eliwood | 80% | 45% | 50% | 40% | 45% | 30% | 35% |
| Hector | 90% | 60% | 45% | 35% | 30% | 50% | 25% |
| Lyn | 70% | 40% | 60% | 60% | 55% | 20% | 30% |
| Marcus | 65% | 30% | 50% | 25% | 30% | 15% | 35% |
| Nino | 55% | 50% | 55% | 60% | 45% | 15% | 50% |
| Oswin | 90% | 40% | 30% | 30% | 35% | 55% | 30% |
| Florina | 60% | 40% | 50% | 55% | 50% | 15% | 35% |
| Kent | 85% | 40% | 50% | 45% | 20% | 25% | 25% |
| Sain | 80% | 60% | 35% | 40% | 35% | 20% | 20% |
| Serra | 50% | 50% | 30% | 40% | 60% | 8% | 55% |

---

## 10. Experience System

### Experience Points (EXP)

- A unit needs **100 EXP** to level up. Excess EXP carries over.
- Maximum level: **20** (unpromoted) or **20** (promoted), for an effective cap of 40 total levels.
- At Level 20/20, units can still fight but gain 0 EXP.

### EXP Formula (Combat)

**Damage EXP (awarded per attack that connects):**

```
EXP_dmg = (31 + L_e + X_e - L_p - X_p) / Q_p

Where:
  L_e = Enemy level
  L_p = Player unit level
  X_e = 20 if enemy is promoted; 0 if unpromoted
  X_p = 20 if player unit is promoted; 0 if unpromoted
  Q_p = Class power of player unit (see table below)

Minimum EXP_dmg = 1
```

**Kill EXP (bonus for defeating the enemy):**

```
EXP_kill = EXP_dmg + ((L_e * Q_e + Y_e) - (L_p * Q_p + Y_p)) / D + 20 + B_e + T_e

Where:
  Q_e = Enemy class power
  Y_e = Promotion class bonus for enemy (see table)
  Q_p = Player class power
  Y_p = Promotion class bonus for player
  D   = Difficulty divisor (see table)
  B_e = Boss bonus (40 if map boss, 0 otherwise)
  T_e = Thief bonus (20 if enemy is a Thief, 0 otherwise)
```

### Class Power (Q) Values

| Q Value | Classes |
|---------|---------|
| 2 | Soldier, Troubadour, Cleric, Bard, Dancer, Thief |
| 3 | All other standard classes |
| 5 | Fire Dragon |

### Promotion Class Bonus (Y) Values

| Y Value | Classes |
|---------|---------|
| 0 | All unpromoted classes |
| 40 | Assassin, Bishop, Valkyrie |
| 60 | All other promoted classes |

### Difficulty Divisor (D)

| Condition | D |
|-----------|---|
| Hard Mode | 1 |
| Enemy class power > Player class power | 1 |
| Enemy class power <= Player class power (Normal) | 2 |

### Special EXP Cases

| Action | EXP |
|--------|-----|
| Miss / 0 damage hit | 1 |
| Staff use (healing) | ~(31 + L_e(recipient counts as L=target_level)) / Q; typically 10-20 |
| Dance / Play (refreshing) | 10 |
| Steal (successful) | 10 |
| Assassin Lethality kill | EXP_kill * ~1.8 |
| Arena victory | Standard kill formula |

---

## 11. Support System & Affinities

### Building Supports

- To build support points, two compatible units must **end their turn adjacent** (within 1 tile) to each other.
- Each compatible pair has a **base support value** (starting points when both join the army) and a **per-turn gain rate**.
- Typical per-turn gain: 1 to 4 points depending on the character pair.
- Only **one support conversation** may be triggered per chapter.
- Each character may have at most **5 total support conversations** (regardless of partner count).
- A character can have support levels with multiple partners, but the 5-conversation limit and the "one per chapter" rule constrain progression.

### Support Level Thresholds

| Support Level | Cumulative Points Required | Bonus Multiplier |
|---------------|---------------------------|------------------|
| C | 80 | x1 (base bonuses) |
| B | 160 | x2 |
| A | 240 | x3 |

### Support Bonus Activation

Support bonuses are active **when the two supported units are within 3 tiles of each other** on the map. Bonuses apply during both Player Phase and Enemy Phase combat.

### The Seven Affinities

Each character has one fixed affinity. When two characters support each other, both gain bonuses based on **both characters' affinities** combined.

**Bonus per affinity per support level:**

| Affinity | Atk | Hit | Avo | Crit | Crit Avo | Def |
|----------|-----|-----|-----|------|----------|-----|
| Fire | +0.5 | +2.5 | +2.5 | +2.5 | -- | -- |
| Thunder | -- | -- | +2.5 | +2.5 | +2.5 | +0.5 |
| Wind | +0.5 | +2.5 | -- | +2.5 | +2.5 | -- |
| Ice | -- | +2.5 | +2.5 | -- | +2.5 | +0.5 |
| Dark | -- | +2.5 | +2.5 | +2.5 | +2.5 | -- |
| Light | +0.5 | +2.5 | -- | +2.5 | -- | +0.5 |
| Anima | +0.5 | -- | +2.5 | -- | +2.5 | +0.5 |

**Calculation:**
```
Total bonus from partner = (Partner's affinity bonuses) * Support_Level_Multiplier

Where Support_Level_Multiplier:
  C = 1, B = 2, A = 3

Both partners' affinities contribute to YOUR bonuses.
Decimal totals are rounded down before application.
```

**Example:** A unit with Fire affinity (C support) paired with a unit with Ice affinity (C support):
- From partner's Ice affinity: +0 Atk, +2.5 Hit, +2.5 Avo, +0 Crit, +2.5 CritAvo, +0.5 Def (x1 for C)
- Rounded: +0 Atk, +2 Hit, +2 Avo, +0 Crit, +2 CritAvo, +0 Def

### Affinity Assignments (Selected Characters)

| Character | Affinity |
|-----------|----------|
| Eliwood | Anima |
| Hector | Thunder |
| Lyn | Wind |
| Marcus | Ice |
| Oswin | Thunder |
| Serra | Thunder |
| Matthew | Wind |
| Florina | Light |
| Kent | Anima |
| Sain | Wind |
| Nino | Fire |
| Jaffar | Ice |
| Athos | Fire |

---

## 12. Terrain System

### Terrain Defense & Avoid Bonuses

| Terrain | Avoid Bonus | Def Bonus | HP Recovery | Special |
|---------|-------------|-----------|-------------|---------|
| Plain | 0 | 0 | -- | -- |
| Road | 0 | 0 | -- | -- |
| Floor | 0 | 0 | -- | -- |
| Stairs | 0 | 0 | -- | -- |
| Deck | 0 | 0 | -- | -- |
| Bridge | 0 | 0 | -- | -- |
| Sand / Desert | +5 | 0 | -- | -- |
| House / Armory / Vendor / Village / Ruins / Arena | +10 | 0 | -- | -- |
| Sea / Lake | +10 | 0 | -- | Impassable for most; Pirates/Berserkers can cross |
| Forest | +20 | +1 | -- | -- |
| Pillar | +20 | +1 | -- | -- |
| Mountain | +30 | +1 | -- | -- |
| Peak | +40 | +2 | -- | Accessible only to fliers, bandits, pirates |
| Fort | +20 | +2 | +20% max HP/turn | -- |
| Gate | +20 | +3 | +10% max HP/turn | -- |
| Throne | +20 | +3 | +10% max HP/turn | Clears status conditions; +5 Res while occupied |

**Important:** Flying units receive NO terrain avoid or defense bonuses (except healing from Fort/Gate/Throne).

### Terrain Movement Costs

Movement costs vary by class movement group. "--" means impassable.

| Terrain | Foot | Armored | Cavalry | Nomad | Mage | Flier | Pirate/Berserker | Brigand |
|---------|------|---------|---------|-------|------|-------|------------------|---------|
| Plain | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Road | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Floor | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Bridge | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Forest | 2 | 2 | 3 | 3 | 2 | 1 | 2 | 2 |
| Pillar | 2 | 2 | 3 | 3 | 3 | 1 | 2 | 2 |
| Fort | 2 | 2 | 2 | 2 | 2 | 1 | 2 | 2 |
| Gate | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Throne | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Sand | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Desert | 2 | -- | -- | 3 | 2 | 1 | 2 | 3 |
| Mountain | 4 | -- | -- | -- | -- | 1 | 4 | 3 |
| Peak | -- | -- | -- | -- | -- | 1 | -- | 4 |
| River | 5 | -- | -- | -- | -- | 1 | 2 | 5 |
| Sea | -- | -- | -- | -- | -- | 1 | 2 (walk on water) | -- |
| Lake | -- | -- | -- | -- | -- | 1 | 2 (walk on water) | -- |
| House/Village | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |
| Armory/Vendor/Arena | 1 | 1 | 1 | 1 | 1 | 1 | 1 | 1 |

---

## 13. Rescue & Drop Mechanics

### Constitution and Aid

```
Aid (infantry/foot units) = Con - 1
Aid (mounted male)        = 25 - Con
Aid (mounted female)      = 20 - Con
```

A unit can **Rescue** an adjacent ally if:
```
Rescuer's Aid >= Rescued unit's Con
```

### Rescue Penalties

While carrying a rescued unit, the rescuer suffers:
- **Skill halved** (Skl = Skl / 2, rounded down)
- **Speed halved** (Spd = Spd / 2, rounded down)

These penalties affect all combat calculations (hit rate, avoid, doubling, crit) while carrying.

### Drop

- A unit carrying another unit can **Drop** them onto any adjacent, empty, traversable tile.
- Dropping ends the rescuer's turn (except mounted units can Drop then Canto if movement remains).
- The dropped unit cannot act until the next Player Phase.

### Give and Take

- **Give**: A unit carrying someone can transfer the carried unit to an adjacent ally (if that ally can carry them based on Aid/Con). Uses rescuer's action.
- **Take**: A unit can take a carried unit from an adjacent ally. Uses the taker's action.

### Tactical Applications

- Rescue fragile units out of danger.
- "Rescue chain": Unit A rescues unit B, Unit C takes B from A, Unit C drops B forward -- effectively extending B's movement range.
- Rescue to prevent enemy from targeting a vulnerable ally on Enemy Phase.

---

## 14. Fog of War

### Overview

Certain chapters feature **Fog of War**, which limits the player's visibility to a radius around each unit. Enemy units, terrain features (like villages), and items are hidden until a player unit can "see" them.

### Vision Ranges

| Unit Type | Base Vision (tiles) |
|-----------|-------------------|
| Standard unit | 3 |
| Thief / Assassin | 8 (approximately; highest non-modified vision) |

### Extending Vision

| Method | Effect |
|--------|--------|
| Torch (item) | Increases using unit's vision by +4 tiles for 1 turn |
| Torch (staff) | Illuminates a target tile area with +4 tiles radius; lasts until next turn |
| Ally adjacency | Tiles visible to any ally are shared with all allies |

### Enemy AI in Fog

- Enemy units move and act normally; they always know where player units are (fog does not restrict AI).
- Enemies hiding in fog can ambush the player by attacking from unseen positions.
- Fog chapters thus reward careful advancement, use of Thieves for scouting, and strategic Torch placement.

### Fog of War Chapters

Fog appears in select chapters, including:
- Chapter 13x: The Peddler Merlinus
- Chapter 18x: Imprisoner of Magic
- Chapter 24: Unfulfilled Heart
- Chapter 26: Battle Before Dawn
- And several Hector-exclusive chapters

---

## 15. Chapter Structure & Campaign Flow

### Lyn's Tale (Tutorial -- 12 chapters)

| Chapter | Name | Objective |
|---------|------|-----------|
| Prologue | A Girl from the Plains | Defeat boss |
| 1 | Footsteps of Fate | Defeat boss |
| 2 | Sword of Spirits | Defeat boss |
| 3 | Band of Mercenaries | Defeat boss |
| 4 | In Occupation's Shadow | Defeat boss |
| 5 | Beyond the Borders | Defeat boss |
| 6 | Blood of Pride | Survive / Defeat boss |
| 7 | Siblings Abroad | Defeat boss |
| 7x | The Black Shadow | (Gaiden) Defeat boss |
| 8 | Vortex of Strategy | Defeat boss |
| 9 | A Grim Reunion | Defeat boss |
| 10 | The Distant Plains | Defeat boss (Lundgren) |

### Eliwood's Story (21 chapters + 7 gaiden)

| Chapter | Name |
|---------|------|
| 11 | Taking Leave |
| 12 | Birds of a Feather |
| 13 | In Search of Truth |
| 13x | The Peddler Merlinus (gaiden -- Fog of War) |
| 14 | False Friends |
| 15 | Noble Lady of Caelin |
| 16 | Whereabouts Unknown |
| 16x | The Port of Badon (gaiden) |
| 17 | Pirate Ship |
| 18 | The Dread Isle |
| 18x | Imprisoner of Magic (gaiden -- Fog of War) |
| 19 | Dragon's Gate |
| 19x | A Glimpse in Time (gaiden) |
| 19xx | Kishuna's Shadow (gaiden -- Hector only) |
| 20 | New Resolve |
| 21 | Kinship's Bond |
| 22 | Living Legend |
| 22x | Genesis (gaiden) |
| 23 | Four-Fanged Offense (route split: Lloyd or Linus) |
| 24 | Unfulfilled Heart |
| 25 | Pale Flower of Darkness |
| 26 | Battle Before Dawn (Fog of War) |
| 26x | Night of Farewells (gaiden) |
| 27 | Cog of Destiny |
| 28 | Valorous Roland |
| 29 | Sands of Time |
| 29x | Battle Preparations (gaiden -- shop/supply chapter) |
| 30 | Victory or Death |
| Final | Light (two-part final chapter; the Dragon) |

### Hector's Story (23 chapters + 8 gaiden)

Hector's Story shares most chapters with Eliwood's Story but includes 6 exclusive chapters:

| Hector-Exclusive Chapter | Name |
|--------------------------|------|
| 11 (H) | Another Journey (replaces "Taking Leave") |
| 19x (H) | A Glimpse in Time |
| 19xx (H) | Kisshuna's Shadow |
| 25 (H) | Crazed Beast |
| 28 (H) | The Berserker |
| 32x (H) | The Value of Life (final gaiden; complete Ch. 32 in <= 20 turns) |

Hector's Story ends at Chapter 33H (equivalent to Final Chapter) and numbers two chapters higher than Eliwood's route.

### Gaiden (Side Chapter) Unlock Conditions

Gaiden chapters are accessed by fulfilling specific conditions in the preceding chapter:

| Gaiden | Condition |
|--------|-----------|
| 7x | Keep all NPCs alive in Chapter 7 |
| 13x | Visit specific village in Chapter 13 |
| 16x | Recruit Farina; total funds above threshold |
| 18x | Complete Chapter 18 by turn threshold |
| 19x | Defeat Kishuna in Chapter 19 |
| 22x | Complete specific conditions; total levels/funds met |
| 26x | Recruit Nino and Jaffar in Chapter 26; both survive |
| 29x | Proceed to battle preparations |
| 32x (H only) | Complete Chapter 32 in 20 turns or fewer |

### Chapter Types

| Type | Description |
|------|-------------|
| Seize | Lord must capture the throne/gate after boss is defeated |
| Defeat Boss | Kill the chapter boss to win |
| Rout | Defeat every enemy unit on the map |
| Survive | Hold out for a set number of turns |
| Defend | Protect a specific tile/NPC for set turns |

---

## 16. Economy: Gold, Shops & Arena

### Gold

- Currency is measured in **Gold (G)**.
- Gold is shared across the entire army (single pool).
- Sources: treasure chests, village visits, chapter completion rewards, arena winnings, enemy drops.
- Maximum gold: **900,000 G** (display capped at 999,999 in some interfaces).

### Shops

There are three types of shops, accessible by moving a unit onto the shop tile:

| Shop Type | Sells | Tile Appearance |
|-----------|-------|-----------------|
| Armory | Physical weapons (swords, lances, axes, bows) | Shield icon |
| Vendor | Items, magic tomes, staves | Potion icon |
| Secret Shop | Rare items, promotion items, stat boosters, legendary weapons | Hidden tile; requires Member Card in inventory |

- Shop inventories vary per chapter.
- The **Silver Card** halves all purchase prices while in the buyer's inventory.
- Shops are also accessible from the **Battle Preparations** screen before a chapter (limited to previously visited shop inventories).

### Arena

The Arena is a special tile found in select chapters where units can gamble gold for experience and profit.

**How it works:**
1. Move a unit onto the Arena tile and select "Arena."
2. The game generates a random opponent matched roughly to the unit's level and strength.
3. A gold wager is displayed (varies by opponent strength; typically 500-5000 G).
4. The player can choose to **Fight** or **Cancel** (forfeit half the wager).
5. Combat proceeds in a standard sequence; the player cannot control the unit's actions.
6. **Win**: The unit gains the wager amount in gold AND full combat EXP for the kill.
7. **Lose**: The unit **dies** (permadeath applies!), and the wager is lost.
8. The player may **choose to quit mid-battle** after each round of combat, losing the wager but keeping the unit alive.

**Arena Chapters (Eliwood route):**
Chapters that contain arenas include Ch. 16x (Port of Badon), Ch. 22 (Living Legend), Ch. 29x (Battle Preparations), and others.

**Strategic note:** Arena abuse (fighting repeatedly for gold and EXP) costs turns, which negatively affects the **Tactics ranking**.

### Rankings

The game tracks 5 ranking categories:

| Rank | Criteria |
|------|----------|
| Tactics | Fewer total turns = better rank |
| Survival | Fewer unit deaths = better rank |
| Funds | More total gold (earned + items' sell value) = better rank |
| EXP | More total EXP gained = better rank |
| Combat | Higher ratio of hits landed vs received |

A cumulative rank (S/A/B/C/D) is computed and displayed at the end. Achieving an overall S rank is extremely difficult and requires careful optimization of all five categories.

---

## 17. Permadeath & Game Over

### Permadeath

- When any non-Lord unit is reduced to 0 HP, they are **permanently dead**. They deliver a short death quote, and are removed from the roster for the rest of the playthrough.
- There is no revival mechanic (unlike later entries in the series).
- Dead units cannot be accessed, spoken to, or re-recruited.
- Dead units' items are lost unless traded away before death.

### Game Over Conditions

| Condition | Result |
|-----------|--------|
| Eliwood reaches 0 HP | Immediate Game Over |
| Hector reaches 0 HP | Immediate Game Over |
| Lyn reaches 0 HP (during Lyn's Tale) | Immediate Game Over |
| Lyn reaches 0 HP (during Eliwood/Hector's Story) | Permadeath (not Game Over) |
| Nils/Ninian reaches 0 HP (certain defend chapters) | Immediate Game Over |
| Protected NPC is killed (when objective is "defend NPC") | Immediate Game Over |

On Game Over, the player is returned to the title screen and must reload from the last save (chapter start or mid-chapter suspend save).

### Suspend Save

- The player may create a **suspend save** at the start of any turn during a chapter (one slot; overwritten each time).
- Suspend saves are deleted upon loading (one-use).
- The full save occurs only at the end of a completed chapter.

---

## 18. Tactician System

### Overview

At the start of the game, the player creates a **Tactician** avatar (named Mark by default). The Tactician is not a combat unit but provides passive bonuses to the entire army.

### Tactician Affinity

The Tactician's **affinity** is determined by birth month:

| Birth Month | Affinity |
|-------------|----------|
| January | Fire |
| February | Thunder |
| March | Wind |
| April | Ice |
| May | Dark |
| June | Light |
| July | Anima |
| August | Fire |
| September | Thunder |
| October | Wind |
| November | Ice |
| December | Dark |

### Tactician Stars

As the player progresses through the game and performs well, the Tactician earns **stars** (up to 10). Stars accumulate based on performance metrics (turns used, units surviving, etc.). Every 12 points of performance earns 1 star.

### Tactician Bonuses

| Bonus | Recipient | Per Star |
|-------|-----------|----------|
| Critical Avoid | All player units | +1 |
| Hit Rate | Units sharing Tactician's affinity only | +1 |
| Avoid | Units sharing Tactician's affinity only | +1 |

At maximum 10 stars: all units get +10 Crit Avoid; units matching the Tactician's affinity also get +10 Hit and +10 Avoid.

---

## 19. UI Layout

### Main Map Screen (240 x 160)

```
+--------------------------------------------------+
|  [Terrain Info]           [Turn Count] [Phase]    |
|                                                   |
|                                                   |
|              MAP GRID (scrollable)                 |
|         (15 x 10 visible tiles at 16x16)          |
|                                                   |
|                                                   |
|                                                   |
|  [Selected Unit Info: Name, HP bar, Class]        |
+--------------------------------------------------+
```

### Unit Info Panel (when cursor hovers over unit)

- **Top-left corner**: Terrain name, Def bonus, Avo bonus, movement cost.
- **Bottom panel**: Unit name, class, level, HP (current/max), equipped weapon icon.

### Action Menu (after moving a unit)

A vertical list appears adjacent to the unit:
```
  Attack
  Staff
  Item
  Trade
  Rescue
  Drop
  Visit
  Seize
  Wait
```
Only valid actions for the current context are shown.

### Combat Forecast (before confirming Attack)

```
+-----------------------------+
|  ATTACKER    vs    DEFENDER |
|  Name              Name    |
|  HP: 28/30        HP: 20/22|
|  Mt: 14           Mt: 10  |
|  Hit: 87%          Hit: 62%|
|  Crt: 4%           Crt: 0%|
|  [x2 if doubling]          |
+-----------------------------+
```

### Battle Animation Screen

When combat occurs, the screen transitions to a **side-view animated battle**:
- Left side: attacking unit sprite (detailed, animated)
- Right side: defending unit sprite
- HP bars displayed at bottom
- Damage numbers shown on impact
- Critical hits trigger a special animation (screen flash, unique pose)
- Player can toggle animations ON/OFF or set to MAP mode (combat resolved on the grid with minimal animation)

### Status Screen (pressing R on a unit)

Multi-page detailed view:
- **Page 1**: Portrait, Name, Class, Level, EXP, HP, Str, Skl, Spd, Lck, Def, Res, Con, Mov, Aid, Affinity, Rescue status
- **Page 2**: Equipment (5 item slots with stats), weapon ranks (all types with letter grade)
- **Page 3**: Support list (partners and levels)

### Battle Preparations Screen (before chapters 12+)

```
+--------------------------------------------------+
|  Pick Units      Items       Save       Options   |
|                                                   |
|  [Unit roster -- swap who deploys on map]         |
|  [Item management -- send to/from convoy]         |
|  [Shop -- buy from previously visited shops]      |
|  [Support -- view support conversations]          |
|  [Save game]                                      |
|  [Fight -- begin chapter]                         |
+--------------------------------------------------+
```

---

## 20. Audio Design

### Music System

The GBA uses the **M4A/Sappy** sound engine, producing sampled audio via the ARM7 CPU software mixer. All music is sequenced (MIDI-like), not streamed.

### Music Tracks (Selected)

| Context | Track Name / Description |
|---------|--------------------------|
| Title screen | "Fire Emblem Theme" -- iconic orchestral main theme |
| Lyn's Tale map theme | "A Journey's Start" -- gentle, adventurous |
| Eliwood's map theme | "Companions" -- warm, determined |
| Hector's map theme | "Loyalty" -- bold, heavy |
| Player Phase | "Strike" -- upbeat, tactical |
| Enemy Phase | "Adversity" -- tense, ominous |
| Battle (normal) | "Attack!" -- fast-paced combat music |
| Battle (boss) | "Unshakable Faith" -- intense boss fight theme |
| Critical hit | Brief unique jingle overlaid on battle music |
| Recruitment | "Join Us" -- short hopeful fanfare |
| Chapter victory | "Victory" -- triumphant fanfare |
| Death / permadeath | "Grief" -- somber requiem |
| Final chapter | "Everything into the Dark" -- epic, dire |
| Final boss (Dragon) | "Dragon of Darkness" -- choir + heavy percussion |
| Ending / credits | "Bittersweet Victory" -- reflective, hopeful |
| Shops | "Bargains Aplenty" -- cheerful market tune |
| Preparations | "Preparing to Advance" -- calm strategic theme |
| Support conversation | "Bonds of Trust" -- warm character theme |

### Sound Effects

| Event | Sound |
|-------|-------|
| Cursor move | Soft click |
| Menu select (A button) | Confirm chime |
| Menu cancel (B button) | Cancel click |
| Unit select | Short "ping" |
| Movement | Footstep / hoofbeat loop (varies by class: armored = heavy clank; mounted = gallop) |
| Sword hit | Sharp metallic slash |
| Lance hit | Heavy thrust/pierce |
| Axe hit | Deep chunky impact |
| Bow hit | Arrow whizz + thud |
| Magic (fire) | Crackling flames |
| Magic (thunder) | Electric zap / boom |
| Magic (light) | Bright hum / radiance |
| Magic (dark) | Deep whoosh / void pulse |
| Critical hit | Dramatic slash + screen flash sfx |
| Miss | Swoosh of air |
| Level up | Ascending chime |
| Level up (stat gain) | Individual stat "ping" per stat increased |
| Level up (no gain) | Dull thud (empty level) |
| Unit death | Fading collapse sound + somber tone |
| Healing | Gentle sparkle/restore sound |
| Treasure chest open | Satisfying click + sparkle |
| Turn change (Player -> Enemy) | Whoosh transition |
| Promotion | Dramatic fanfare with ascending scale |

### Voice Clips

Fire Emblem: The Blazing Blade includes minimal voice acting:
- Battle cries during critical hits (short exclamation; 1-2 syllables)
- Hit grunts on receiving damage
- Death gasps
- All voice clips are short GBA-quality samples (~8-bit, heavily compressed)

---

## Appendix A: Key Numeric Constants

| Constant | Value |
|----------|-------|
| Max level (unpromoted) | 20 |
| Max level (promoted) | 20 |
| EXP to level up | 100 |
| Items per unit | 5 |
| Deployment slots (typical) | 8-14 depending on chapter |
| Max support conversations per character | 5 |
| Support activation range | 3 tiles |
| Weapon triangle Atk bonus | +/- 1 |
| Weapon triangle Hit bonus | +/- 15 |
| Doubling speed threshold | 4 AS advantage |
| Critical damage multiplier | x3 |
| Effectiveness multiplier (English) | x2 |
| Effectiveness multiplier (Japanese) | x3 |
| Rescue Skill/Speed penalty | Halved |
| Fort HP recovery | 20% max HP per turn |
| Gate/Throne HP recovery | 10% max HP per turn |
| Throne Res bonus | +5 |
| Swordmaster/Berserker crit bonus | +15 |
| S-rank weapon Hit/Crit bonus | +5 / +5 |
| Max gold | 900,000 |
| Fog of War base vision | 3 tiles |
| Thief Fog vision | ~8 tiles |
| Torch vision bonus | +4 tiles |

## Appendix B: Two Random Number (2-RN) Hit System

Fire Emblem: The Blazing Blade uses a **True Hit** system that differs from displayed percentages. Two random numbers from 0-99 are generated and averaged. The attack hits if this average is less than the displayed hit rate.

```
RN1 = random(0, 99)
RN2 = random(0, 99)
Average = (RN1 + RN2) / 2

If Average < Displayed_Hit_Rate:
    Attack HITS
Else:
    Attack MISSES
```

This produces a bell curve distribution, making high displayed hit rates more reliable and low displayed hit rates less likely to connect than a single-RN system would suggest. Critical hits, by contrast, use a **single RN**.

## Appendix C: Random Number Generator (RNG)

The GBA Fire Emblem games use a **linear congruential generator** with a pre-computed table of 2^16 (65,536) random numbers. The RNG index advances with each consumption (hit checks, level-up rolls, AI decisions, etc.). This deterministic RNG means that identical inputs always produce identical outputs -- the foundation of RNG manipulation strategies.

```
Next_RN_Index = (Current_RN_Index + 1) mod 65536
Random_Value = RN_Table[Next_RN_Index] mod 100   (for percentage rolls)
```
