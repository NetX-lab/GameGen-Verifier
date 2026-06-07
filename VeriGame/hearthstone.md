# Hearthstone -- Complete Game Specification

> A comprehensive specification for faithfully recreating Hearthstone (Blizzard Entertainment, 2014), focusing on the Classic/Core set mechanics and the fundamental rules engine. This document covers every system, mechanic, card type, class, and interaction required for a faithful implementation.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Turn Structure](#3-core-turn-structure)
4. [Mana System](#4-mana-system)
5. [Card Types](#5-card-types)
6. [Card Attributes & Rarity](#6-card-attributes--rarity)
7. [All 10 Classes & Hero Powers](#7-all-10-classes--hero-powers)
8. [Combat System](#8-combat-system)
9. [Board & Hand Mechanics](#9-board--hand-mechanics)
10. [Deck Building Rules](#10-deck-building-rules)
11. [Mulligan System](#11-mulligan-system)
12. [Keyword Glossary](#12-keyword-glossary)
13. [Secrets](#13-secrets)
14. [Discover Mechanic](#14-discover-mechanic)
15. [Fatigue System](#15-fatigue-system)
16. [Game Modes](#16-game-modes)
17. [UI Layout](#17-ui-layout)
18. [Audio & Visual Design](#18-audio--visual-design)

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Hearthstone (formerly Hearthstone: Heroes of Warcraft) |
| Developer | Blizzard Entertainment |
| Genre | Digital collectible card game (CCG) |
| Release | March 11, 2014 |
| Platform | PC, Mac, iOS, Android |
| Players | 1v1 (online multiplayer, or vs AI practice) |
| Setting | Warcraft universe |
| Objective | Reduce the opponent's hero health from 30 to 0 |
| Lose condition | Your hero's health reaches 0 (or below) |
| Core loop | Draw a card, gain a mana crystal, play cards, attack with minions/weapons, end turn |

### Design Pillars

- **Accessibility**: Simple core rules; complexity emerges from card interactions.
- **Speed**: Matches average 8-12 minutes; turn timer enforces pace.
- **Collection**: Players build a card collection over time through packs, crafting, and rewards.
- **Class identity**: Each of the 10 classes has a unique hero power and exclusive card pool.
- **Randomness**: Controlled RNG through mechanics like Discover, random targeting, and random summoning adds variance while maintaining strategic depth.

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Aspect ratio | 16:9 (primary), scales to 4:3 on mobile |
| Reference resolution | 1920 x 1080 (desktop) |
| Frame rate target | 30 FPS (mobile), 60 FPS (desktop) |
| Engine | Unity (migrated from custom engine in 2021) |
| Networking | Client-server; authoritative server validates all actions |
| Animation system | Spine 2D skeletal animation for card art; particle systems for spells |

### Game State Model

The server is the single source of truth. The client sends player intents (play card, attack, end turn) and the server validates, resolves, and returns the resulting game state. Key server-tracked state:

```
Game State:
  - current_turn: int (1-based, increments each player's turn)
  - active_player: Player
  - game_phase: MULLIGAN | PLAYING | GAME_OVER

Per Player:
  - hero: { class, health (max 30), armor (uncapped), attack (temporary), weapon }
  - hero_power: { id, cost, used_this_turn: bool }
  - deck: ordered list of Card (max 60 at runtime)
  - hand: list of Card (max 10)
  - board: ordered list of Minion (max 7)
  - secrets: list of Secret (max 5)
  - mana_crystals: int (0-10)
  - current_mana: int (0-10, can exceed 10 with temporary mana)
  - overload_pending: int
  - overload_locked: int
  - fatigue_counter: int (starts at 0)
  - combo_active: bool (true if at least 1 card played this turn)
```

### Game Loop (Per Turn)

```
1. Start of Turn Phase
   a. Increment mana crystals (max 10)
   b. Refill all non-overloaded mana crystals
   c. Lock pending overload crystals
   d. Clear pending overload
   e. Trigger "start of turn" effects
   f. Draw 1 card from deck (may trigger fatigue)
   g. Reset hero attack to 0 (unless weapon equipped)
   h. Unfreeze characters that were frozen and did not attack last turn
   i. Reset hero power usage

2. Action Phase (player may perform in any order, any number of times):
   - Play a card from hand (if sufficient mana)
   - Attack with a minion (if able)
   - Attack with hero (if has attack, e.g., weapon)
   - Use hero power (once per turn, if not already used)

3. End of Turn Phase
   a. Player clicks "End Turn" or timer expires
   b. Trigger "end of turn" effects
   c. Remove temporary hero attack
   d. Clear combo flag
   e. Pass active_player to opponent
```

---

## 3. Core Turn Structure

### Going First vs Going Second

| Attribute | Player 1 (goes first) | Player 2 (goes second) |
|-----------|-----------------------|------------------------|
| Opening hand size | 3 cards | 4 cards |
| The Coin | No | Yes (added to hand after mulligan) |
| First-turn mana | 1 crystal | 1 crystal |
| Card drawn turn 1 | Yes (draws to 4) | Yes (draws to 5, or 6 with Coin) |

**The Coin** is a 0-mana spell that reads: "Gain 1 Mana Crystal this turn only." It counts as a spell for combo, spell-trigger, and spell-count purposes. It is uncollectible and does not start in the deck.

### Turn Timer

| Condition | Time Allowed |
|-----------|-------------|
| Normal turn | 75 seconds |
| Rope appears | ~20 seconds remaining |
| After full idle turn (0 actions taken) | ~7 seconds (short fuse); any action restores full 75 seconds |
| First two turns of the game | Slightly shorter timer |
| Reconnection grace | 60 seconds before auto-concede |

When time expires, the turn ends automatically. Any action currently animating completes, but no new actions can be initiated.

---

## 4. Mana System

### Mana Crystal Growth

| Turn Number | Mana Crystals Available |
|-------------|------------------------|
| 1 | 1 |
| 2 | 2 |
| 3 | 3 |
| 4 | 4 |
| 5 | 5 |
| 6 | 6 |
| 7 | 7 |
| 8 | 8 |
| 9 | 9 |
| 10+ | 10 (cap) |

- Players gain exactly **1 permanent Mana Crystal** at the start of each of their turns, up to a maximum of **10**.
- All non-overloaded crystals **refill** at the start of each turn.
- Playing a card **spends** mana equal to the card's mana cost. Spent mana does not refill until the next turn.

### Mana Types

| Type | Description |
|------|-------------|
| Permanent crystals | Gained each turn (up to 10). Some cards grant or destroy permanent crystals (e.g., Wild Growth, Darnassus Aspirant). |
| Current (available) mana | The amount that can currently be spent. |
| Temporary mana | Granted by The Coin, Innervate, etc. Can exceed the 10-crystal cap. Expires at end of turn if unspent. |
| Overloaded crystals | Locked at the start of the following turn. Cannot be refilled or used that turn. |

### Overload (Shaman Mechanic)

- Cards with **Overload: (X)** lock X mana crystals on your **next** turn.
- When the Overload card is played, X crystals become "pending overload" (shown as padlocks under crystals).
- At the start of the next turn, pending overload converts to "locked overload" -- those crystals do not refill.
- After that turn, the locked crystals are freed and refill normally on the subsequent turn.
- Overload only triggers when the card is **played from hand** (not when summoned by other effects).
- There is no upper limit on overload. A player can accumulate more overload than they have crystals; excess overload effectively wastes no additional mana but is tracked for synergy cards like Snowfury Giant.

### Mana Display

- Displayed at bottom-right of the player's board as filled blue crystals (available) and empty gray crystals (spent).
- Format: **"X / Y"** where X = current mana, Y = total mana crystals.
- Overloaded crystals display a padlock icon.

---

## 5. Card Types

### 5.1 Minion Cards

Minions are persistent characters summoned to the battlefield.

| Attribute | Description |
|-----------|-------------|
| Mana cost | Top-left corner; 0-10+ mana |
| Attack | Bottom-left corner; damage dealt when attacking |
| Health | Bottom-right corner; when reduced to 0, the minion dies |
| Card text | Center; describes abilities, keywords, or triggered effects |
| Tribe | Optional tag (Beast, Dragon, Murloc, Mech, Demon, Elemental, Pirate, Totem, Undead, etc.) |

**Minion behavior:**
- Summoned to the player's side of the board.
- Subject to **summoning sickness**: cannot attack the turn they are played, unless they have **Charge** or **Rush**.
- Can attack once per turn (twice with **Windfury**, four times with **Mega-Windfury**).
- When they attack, both the attacker and defender deal their respective attack values as damage simultaneously.
- A minion's current health can be reduced by damage but cannot exceed its maximum health through normal healing (it can exceed max via buff effects).
- When health reaches 0 or less, the minion dies (removed from board; triggers Deathrattles).

### 5.2 Spell Cards

Spells are one-time effects played from hand.

| Attribute | Description |
|-----------|-------------|
| Mana cost | Top-left corner |
| Card text | Describes the effect |
| Spell school | Optional tag: Arcane, Fire, Frost, Holy, Nature, Shadow, or Fel |
| Target requirement | Some spells require a target; others affect the board, hero(es), or happen automatically |

- Spells resolve immediately upon being played.
- After resolution, the spell card is removed from the game (goes to the "graveyard" -- not accessible in normal play).
- Spells can trigger Secrets, Counterspell can negate them, and spell-related synergies apply.

### 5.3 Weapon Cards

Weapons equip to the hero, granting attack power.

| Attribute | Description |
|-----------|-------------|
| Mana cost | Top-left corner |
| Attack | Bottom-left; the damage the hero deals when attacking with this weapon |
| Durability | Bottom-right; number of attacks before the weapon is destroyed |
| Card text | Optional additional effects |

**Weapon rules:**
- A hero can equip only **one weapon** at a time. Equipping a new weapon **destroys** the old one (no refund).
- While equipped, the weapon's Attack value is added to the hero's Attack during the player's turn only.
- Each hero attack reduces Durability by 1. When Durability reaches 0, the weapon is destroyed.
- Hero attack granted by a weapon persists through the opponent's turn for purposes of triggered effects (e.g., if attacked by a minion with Poisonous), but the hero cannot normally initiate attacks on the opponent's turn.
- Weapons can be buffed (increased attack or durability) or debuffed. The Ooze family of minions can destroy a weapon outright via Battlecry.

### 5.4 Hero Cards

Hero cards replace the player's current hero.

| Attribute | Description |
|-----------|-------------|
| Mana cost | Top-left corner |
| Armor | Amount of Armor gained upon playing the card |
| Card text | Describes Battlecry or other effects |
| New Hero Power | Replaces the current Hero Power with an upgraded or unique one |

**Hero card rules:**
- Playing a hero card does **not** change current or maximum Health; only Armor is added.
- The hero portrait, hero power, and emotes change to match the new hero.
- Hero cards are always **Legendary** rarity.
- The new hero power can be used once per turn for its stated cost (usually 2 mana).

### 5.5 Location Cards

Locations are persistent board entities introduced in Murder at Castle Nathria.

| Attribute | Description |
|-----------|-------------|
| Mana cost | Top-left corner |
| Durability | Number of times the ability can be used before the location is destroyed |
| Card text | Describes the activated ability |

**Location rules:**
- Placed on the board; occupy a board slot (count toward the 7-minion limit).
- Cannot be targeted by spells, attacks, or hero powers.
- Ability is activated by clicking (free, no mana cost after initial play).
- After each use, the location enters a **1-turn cooldown** and loses 1 Durability.
- Can be used immediately on the turn played.
- When Durability reaches 0, the location is destroyed and removed.

---

## 6. Card Attributes & Rarity

### Rarity Tiers

| Rarity | Gem Color | Deck Limit | Crafting Cost (Dust) | Disenchant Value (Dust) |
|--------|-----------|------------|----------------------|-------------------------|
| Free / Basic | No gem (gemless) | 2 copies | Cannot be crafted/disenchanted | N/A |
| Common | White | 2 copies | 40 | 5 |
| Rare | Blue | 2 copies | 100 | 20 |
| Epic | Purple | 2 copies | 400 | 100 |
| Legendary | Orange | 1 copy | 1,600 | 400 |

### Golden Cards

- Cosmetic upgrade with animated card art.
- Functionally identical to non-golden versions.
- Higher crafting and disenchant values.

| Rarity | Golden Craft Cost | Golden Disenchant |
|--------|-------------------|-------------------|
| Common | 400 | 50 |
| Rare | 800 | 100 |
| Epic | 1,600 | 400 |
| Legendary | 3,200 | 1,600 |

### Card Sets

| Set Type | Description |
|----------|-------------|
| Core Set | Free, rotates annually; provides baseline cards for all classes |
| Expansion Sets | Released ~3 times per year (~135 cards each); enter Standard for ~2 years |
| Wild Sets | Rotated expansion sets; usable only in Wild format |
| Classic Set | Legacy set (now replaced by Core); all original cards |

---

## 7. All 10 Classes & Hero Powers

All basic hero powers cost **2 mana** unless otherwise noted and can be used **once per turn**.

### 7.1 Mage

| Property | Value |
|----------|-------|
| Default Hero | Jaina Proudmoore |
| Hero Power | **Fireblast** |
| HP Cost | 2 mana |
| HP Effect | Deal 1 damage to any target (hero or minion, friendly or enemy) |
| HP Targeting | Requires a target; not restricted by Taunt |
| Class Identity | Spells, direct damage, Freeze effects, Secrets (3 mana), board clears, spell synergy |
| Signature Keywords | Freeze, Spell Damage, Secrets |
| Strengths | Powerful removal spells (Fireball, Flamestrike, Blizzard), card generation, combo potential |
| Weaknesses | Limited healing, weak early-game minions, reliant on spell combos |

### 7.2 Warrior

| Property | Value |
|----------|-------|
| Default Hero | Garrosh Hellscream |
| Hero Power | **Armor Up!** |
| HP Cost | 2 mana |
| HP Effect | Gain 2 Armor |
| HP Targeting | No target needed; self-only |
| Class Identity | Armor, weapons, damage-based removal, enrage, rush minions |
| Signature Keywords | Armor, Weapons, Rush, Enrage |
| Strengths | Massive armor stacking, efficient weapons, strong removal (Execute, Shield Slam) |
| Weaknesses | Limited card draw (compared to Warlock), slow without combo pieces |

**Armor Mechanics:**
- Armor has **no maximum**. A warrior can stack hundreds of armor.
- Damage is always absorbed by Armor first, then Health.
- Armor does not count as Health for effects that reference Health (e.g., Alexstrasza sets Health to 15, does not consider armor).

### 7.3 Priest

| Property | Value |
|----------|-------|
| Default Hero | Anduin Wrynn |
| Hero Power | **Lesser Heal** |
| HP Cost | 2 mana |
| HP Effect | Restore 2 Health to any target (hero or minion, friendly or enemy) |
| HP Targeting | Requires a target; not restricted by Taunt |
| Class Identity | Healing, Health buffs, removal via Shadow spells, stealing/copying opponent resources |
| Signature Keywords | Heal, Shadow, Silence, Deathrattle (Shadow Priest) |
| Strengths | Sustain, board control via removal (Shadow Word: Pain/Death), value generation |
| Weaknesses | Limited burst damage, struggles to close out games quickly |

### 7.4 Hunter

| Property | Value |
|----------|-------|
| Default Hero | Rexxar |
| Hero Power | **Steady Shot** |
| HP Cost | 2 mana |
| HP Effect | Deal 2 damage to the enemy hero |
| HP Targeting | No target needed; always hits the enemy hero |
| Class Identity | Aggression, Beasts, face damage, Secrets (2 mana), traps, Deathrattle |
| Signature Keywords | Beasts, Deathrattle, Secrets |
| Strengths | Consistent hero damage, efficient early-game minions, strong beast synergies |
| Weaknesses | Limited board clears, poor healing, limited card draw, losing the board often means losing the game |

### 7.5 Paladin

| Property | Value |
|----------|-------|
| Default Hero | Uther Lightbringer |
| Hero Power | **Reinforce** |
| HP Cost | 2 mana |
| HP Effect | Summon a 1/1 Silver Hand Recruit |
| HP Targeting | No target needed; summons to the board |
| Class Identity | Buffs, Divine Shield, healing, Silver Hand Recruit synergy, Secrets (1 mana), Librams |
| Signature Keywords | Divine Shield, Buffs, Secrets, Librams |
| Strengths | Strong buffs (Blessing of Kings), board flooding, divine shield synergy, healing |
| Weaknesses | Weak individual hero power value, vulnerable to board clears, limited card draw |

**Silver Hand Recruit:** 1/1 minion token with no abilities. Subject to the 7-minion board limit.

### 7.6 Rogue

| Property | Value |
|----------|-------|
| Default Hero | Valeera Sanguinar |
| Hero Power | **Dagger Mastery** |
| HP Cost | 2 mana |
| HP Effect | Equip a 1/2 Wicked Knife |
| HP Targeting | No target needed; equips weapon (destroys existing weapon) |
| Class Identity | Combo cards, tempo plays, card draw, weapons, bounce effects, Stealth, Secrets (2 mana) |
| Signature Keywords | Combo, Stealth, Deathrattle, Secrets |
| Strengths | Efficient removal (Backstab, Eviscerate), burst combos, strong card draw (Sprint, Gadgetzan Auctioneer) |
| Weaknesses | No healing, limited board clears, fragile board presence, hero takes damage from weapon attacks |

**Combo Mechanic:** Cards with Combo gain an additional or enhanced effect if another card has already been played from hand this turn. The Coin counts as playing a card for Combo purposes.

### 7.7 Shaman

| Property | Value |
|----------|-------|
| Default Hero | Thrall |
| Hero Power | **Totemic Call** |
| HP Cost | 2 mana |
| HP Effect | Summon a random basic Totem |
| HP Targeting | No target needed; summons to the board |
| Class Identity | Overload, totems, elementals, Windfury, board-wide effects, Evolve |
| Signature Keywords | Overload, Windfury, Freeze, Evolve |
| Strengths | Undercosted powerful cards (via Overload), versatile toolbox, wide board threats |
| Weaknesses | Overload restricts next-turn tempo, RNG-dependent hero power, inconsistent card quality |

**The Four Basic Totems:**

| Totem | Stats | Ability | Element |
|-------|-------|---------|---------|
| Healing Totem | 0/2 | At the end of your turn, restore 1 Health to all friendly minions | Water |
| Searing Totem | 1/1 | None | Fire |
| Stoneclaw Totem | 0/2 | Taunt | Earth |
| Wrath of Air Totem | 0/2 | Spell Damage +1 | Air |

- Totemic Call summons one of the four totems at random.
- Subject to the 7-minion board limit.
- Totems have the **Totem** tribe tag.

### 7.8 Warlock

| Property | Value |
|----------|-------|
| Default Hero | Gul'dan |
| Hero Power | **Life Tap** |
| HP Cost | 2 mana |
| HP Effect | Draw a card and deal 2 damage to your hero |
| HP Targeting | No target needed; self-only |
| Class Identity | Self-damage for card advantage, Demons, board clears, discard effects, sacrifice |
| Signature Keywords | Demons, Self-damage, Discard, Destroy friendly minions |
| Strengths | Unmatched card draw via hero power, powerful board clears (Hellfire, Twisting Nether, Defile), demon synergy |
| Weaknesses | Self-damage is a real cost, weaker individual card quality (balanced by card advantage) |

### 7.9 Druid

| Property | Value |
|----------|-------|
| Default Hero | Malfurion Stormrage |
| Hero Power | **Shapeshift** |
| HP Cost | 2 mana |
| HP Effect | Gain +1 Attack this turn and +1 Armor |
| HP Targeting | No target needed; self-only |
| Class Identity | Mana ramp, Choose One versatility, large minions, Treant tokens, armor |
| Signature Keywords | Choose One, Mana ramp, Treants |
| Strengths | Mana acceleration (Wild Growth, Innervate), versatile cards (Choose One), large late-game threats |
| Weaknesses | Poor single-target hard removal, limited board clears, must invest turns ramping |

**Choose One Mechanic:** Druid cards with "Choose One" present two options when played; the player selects one. Some cards combine both effects under certain conditions (e.g., Ossirian Tear, Fandral Staghelm).

### 7.10 Demon Hunter

| Property | Value |
|----------|-------|
| Default Hero | Illidan Stormrage |
| Hero Power | **Demon Claws** |
| HP Cost | **1 mana** (unique -- the only basic hero power costing 1) |
| HP Effect | Gain +1 Attack this turn |
| HP Targeting | No target needed; self-only |
| Class Identity | Aggressive attacks, Demons, Outcast, card draw, big demons, Lifesteal |
| Signature Keywords | Outcast, Lifesteal, Demons, Attack buffs |
| Strengths | Cheap hero power for consistent face/trade damage, efficient card draw, strong burst combos |
| Weaknesses | Self-damage from attacking minions, limited healing without Lifesteal, narrow card pool |

**Outcast Mechanic:** A card with Outcast triggers an enhanced effect only if it is played from the leftmost or rightmost position in your hand.

---

## 8. Combat System

### 8.1 Attack Action

An **attack** occurs when a friendly character (minion or hero with Attack > 0) is directed at an enemy character (minion or enemy hero).

**Attack Resolution Steps:**

```
1. DECLARATION: Player selects attacker and target.
2. VALIDATION:
   a. Attacker has Attack > 0
   b. Attacker has not exhausted its attacks this turn
   c. Attacker is not Frozen
   d. Attacker does not have summoning sickness (unless Charge/Rush)
   e. If any enemy minion has Taunt, target must be a Taunt minion
   f. If attacker has Rush and this is its first turn, target must be a minion
   g. Target is not Stealthed (unless using area-of-effect)
   h. Target is not Immune
3. PREPARATION PHASE:
   a. Trigger "whenever a character attacks" effects (e.g., Truesilver Champion heals hero)
   b. Trigger "whenever this minion attacks" effects
   c. Trigger Secrets that activate on attack declaration
4. DAMAGE PHASE (simultaneous):
   a. Attacker deals damage equal to its Attack to the defender
   b. Defender deals damage equal to its Attack to the attacker
   c. Both damage events are created in order (attack, counterattack) and resolved
5. POST-COMBAT:
   a. If attacker is a hero with a weapon: weapon loses 1 Durability
   b. Check for deaths (any character at 0 or less Health)
   c. Process Deathrattles and on-death triggers
   d. Mark attacker as having used an attack this turn
   e. Attacker with Windfury has 2 attacks per turn; Mega-Windfury has 4
```

### 8.2 Damage Types

| Type | Description |
|------|-------------|
| Combat damage | Dealt mutually during an attack action (simultaneous) |
| Spell damage | Dealt by spell cards; can be modified by Spell Damage keyword |
| Hero power damage | Dealt by hero powers (Fireblast, Steady Shot); not modified by Spell Damage unless explicitly stated |
| Triggered damage | Dealt by Deathrattle, Battlecry, Inspire, and other triggered effects |
| Fatigue damage | Dealt to the hero when drawing from an empty deck |

### 8.3 Damage Resolution Rules

- Damage is always dealt in a specific, deterministic order based on play order and trigger order.
- **Deaths are not processed mid-sequence.** A minion at 0 health is "pending dead" until the current phase completes, then all deaths are processed simultaneously.
- **Overkill damage** is not carried over. A 10-attack minion attacking a 1-health minion still only destroys that minion; excess damage is wasted (it does not "splash" to other targets).
- Damage from any source can kill a hero. If a hero's Health + Armor reaches 0 or below, that hero is destroyed and the game ends.

### 8.4 Healing

| Rule | Detail |
|------|--------|
| Cannot exceed maximum Health | A hero's Health cannot be healed above 30 (its starting maximum). Minions cannot be healed above their current maximum Health. |
| Armor is separate | Healing does not restore Armor; Armor is gained by specific effects. |
| Auchenai effect | Priest's Auchenai Soulpriest converts all healing to damage for that player. |

### 8.5 Taunt

- If one or more enemy minions have **Taunt**, the attacking player **must** target a Taunt minion.
- Taunt does **not** prevent:
  - Spells from targeting non-Taunt targets
  - Hero powers (e.g., Fireblast, Steady Shot) from ignoring Taunt
  - Random effects from hitting non-Taunt characters
- Taunt is negated by **Stealth** (a minion with both Taunt and Stealth does not force attacks until Stealth is broken).

### 8.6 Stealth

- A Stealthed minion **cannot be targeted** by enemy attacks, spells, hero powers, or Battlecries.
- Stealth is **removed** when the minion deals damage (attacking, or dealing damage through effects like Knife Juggler).
- Friendly spells **can** target a friendly Stealthed minion.
- Area-of-effect (AoE) damage still hits Stealthed minions.
- A minion can have both Stealth and Taunt; in this case, the Taunt has no effect until Stealth is removed.

### 8.7 Face vs. Trade

- **Going face**: Attacking the enemy hero directly. Ignores minions (unless Taunt is present).
- **Trading**: Attacking an enemy minion to remove it. Both characters take damage.
- This is a **strategic decision**, not a mechanical rule. The game allows either as long as Taunt rules are respected.

---

## 9. Board & Hand Mechanics

### 9.1 Board Limits

| Limit | Value | Consequence of Exceeding |
|-------|-------|--------------------------|
| Minions per player | 7 | Cannot summon/play additional minions; effects that would summon are wasted |
| Secrets per player | 5 | Cannot play additional secrets |
| Weapons per player | 1 | Equipping a new weapon destroys the current one |
| Quests per player | 1 | Only 1 quest/sidequest/questline active at a time (occupies secret zone) |
| Hand size | 10 | Drawing beyond 10 burns (destroys) the drawn card; it is revealed to both players briefly |
| Deck size (in-game) | 60 | Cannot shuffle more than 60 cards into a deck during a match |

### 9.2 Board Positioning

- Minions are arranged in a horizontal row. New minions can be placed **between** existing minions or at either end.
- Position matters for:
  - **Adjacent effects**: e.g., Dire Wolf Alpha (+1 Attack to adjacent minions), Flametongue Totem (+2 Attack to adjacent minions)
  - **Random effects**: Some effects target "a random enemy minion" -- all minions have equal probability.
  - **AoE patterns**: Some effects deal damage based on position (e.g., Betrayal causes a minion to deal its Attack damage to the minions next to it).
- The **leftmost** and **rightmost** positions are relevant for the Outcast keyword (Demon Hunter).

### 9.3 Hand Mechanics

- Cards in hand are visible only to their owner.
- The **number** of cards in the opponent's hand is visible (shown as card backs).
- When hand is full (10 cards) and a draw occurs:
  - The drawn card is destroyed ("burned/milled").
  - The burned card is briefly revealed to **both players**.
  - This applies to all card draw effects, including start-of-turn draw.

### 9.4 Summoning Order

- When multiple minions are summoned simultaneously (e.g., by a spell that summons several), they are placed left to right.
- The order in which minions were played/summoned determines their **play order**, which affects trigger resolution order.

---

## 10. Deck Building Rules

### Constructed Format Rules

| Rule | Value |
|------|-------|
| Deck size | Exactly **30 cards** |
| Maximum copies per card | **2** (for Common, Rare, Epic) |
| Maximum copies per Legendary | **1** |
| Class restriction | A deck belongs to one class; it may only include cards from that class and Neutral cards |
| Multi-class cards | Some expansions introduced dual-class cards usable by either class |
| Format legality | Cards must be legal in the chosen format (Standard or Wild) |

### Special Deck-Building Constraints

| Card / Effect | Rule |
|---------------|------|
| Prince Renathal | Increases deck size to 40 and starting Health to 35 |
| Highlander cards (Reno Jackson, Zephrys, etc.) | Reward for having no duplicate cards in your deck |
| C'Thun, the Shattered | Auto-shuffles 4 pieces into the deck at the start of the game |
| Quest cards | Start in the opening hand (not drawn from deck) |

### Format Types

| Format | Card Pool |
|--------|-----------|
| Standard | Core Set + expansions from the current and previous Hearthstone year (~2 years of sets) |
| Wild | All cards ever released, including Hall of Fame and rotated sets |
| Classic | Only cards from the original Classic set, in their original state |
| Twist | Rotating special format with curated card pools and unique rules |

---

## 11. Mulligan System

### Mulligan Procedure

```
Step 1: Random player order is determined (coin flip for who goes first).
Step 2: Each player is shown their opening hand:
        - Player going first: 3 random cards from their deck.
        - Player going second: 4 random cards from their deck.
Step 3: Both players have 65 seconds to select cards to replace.
        - First 5 seconds: cards are not yet selectable (animation).
        - Remaining 60 seconds: click cards to mark for replacement (green outline).
        - Any number of cards (0 to all) can be marked.
Step 4: Both players click "Confirm" (or timer expires).
Step 5: Marked cards are shuffled back into the deck.
Step 6: Replacement cards are drawn (guaranteed different from mulliganed cards).
Step 7: Player going second receives The Coin added to their hand.
Step 8: Game begins -- Player 1's first turn starts.
```

### Mulligan Rules

| Rule | Detail |
|------|--------|
| Replacement guarantee | You will not re-draw a card you mulliganed away |
| Independent decisions | Both players mulligan simultaneously and independently |
| No communication | Neither player sees the opponent's mulligan choices |
| Quest cards | Quest and Questline cards always start in the opening hand and cannot be mulliganed |
| The Coin timing | The Coin is added after the mulligan; it is not part of the mulligan selection |

---

## 12. Keyword Glossary

### Primary Keywords (Core Mechanics)

| Keyword | Type | Exact Rules |
|---------|------|-------------|
| **Taunt** | Persistent | Enemy attacks **must** target this minion while it is alive. Does not block spells, hero powers, or random effects. Negated by Stealth. |
| **Charge** | Persistent | This minion can attack immediately when summoned (ignores summoning sickness). Can attack both minions and the enemy hero on its first turn. |
| **Rush** | Persistent | This minion can attack enemy **minions** immediately when summoned. Cannot attack the enemy hero on its first turn. Normal attacking rules apply on subsequent turns. |
| **Divine Shield** | Persistent (one-use) | The first instance of damage dealt to this minion is reduced to 0. The shield is then removed. Does not prevent destroy effects (e.g., Assassinate). Refreshable by certain cards. |
| **Windfury** | Persistent | This minion can attack **twice** per turn instead of once. |
| **Mega-Windfury** | Persistent | This minion can attack **four times** per turn. |
| **Stealth** | Persistent (conditional) | Cannot be targeted by enemy attacks, spells, hero powers, or Battlecries. Removed when the minion deals any damage. Friendly effects can still target it. AoE still hits it. |
| **Poisonous** | Persistent | Any minion damaged by this minion is **destroyed**, regardless of remaining Health. Does not affect heroes. |
| **Lifesteal** | Persistent | Whenever this card deals damage, restore that much Health to your hero. Applies to all damage sources from the card (attack, spell, effect). |
| **Reborn** | Persistent (one-use) | The first time this minion dies, it is resummoned with **1 Health** and without Reborn. Retains enchantments. |
| **Elusive** | Persistent | Cannot be targeted by spells or Hero Powers (from either player). Can still be affected by AoE, Battlecries that do not target, and attacks. Not an official keyword on cards; described in full text as "Can't be targeted by spells or Hero Powers." |
| **Immune** | Persistent (usually temporary) | Cannot take damage from any source. Cannot be targeted by the enemy. Characters that are Immune can still attack. |
| **Freeze** | Debuff | A Frozen character misses its next possible attack opportunity. A Frozen minion on its owner's turn will skip that attack, then unfreeze at the end of the turn. If frozen during the opponent's turn, it remains frozen through the owner's next turn. |
| **Silence** | Instant | Removes all card text, enchantments (buffs and debuffs), and keyword abilities from the target minion. Restores the minion's Health to its current maximum (if that was buffed, the buff is removed). The minion retains its base stats if health was buffed above base, it drops to whatever its new maximum would be. |
| **Spell Damage +X** | Persistent (aura) | While this minion is on the board, your spells deal **+X** additional damage. Stacks with other Spell Damage sources. Only affects damage-dealing spells, not healing or non-damage effects. |

### Triggered Keywords

| Keyword | Trigger Timing | Exact Rules |
|---------|---------------|-------------|
| **Battlecry** | When played from hand | Triggers once when the card is played from the hand. Does **not** trigger when summoned by other effects (e.g., Resurrect, Recruit). If the Battlecry requires a target and no valid target exists, the card can still be played but the Battlecry has no effect. |
| **Deathrattle** | When the minion dies | Triggers when the minion is destroyed (Health reaches 0 or a destroy effect). Multiple Deathrattles on one minion all trigger. Resolved in the order they were applied. Silencing a minion removes its Deathrattle. |
| **Inspire** | When you use your Hero Power | Triggers each time the controlling player uses their Hero Power while the Inspire minion is on the board. |
| **Combo** | When played from hand (conditional) | The Combo effect activates only if another card was played earlier in the same turn. The Coin counts as a card for Combo purposes. |
| **Outcast** | When played from hand (positional) | The Outcast effect activates only if the card is played from the **leftmost or rightmost** position in your hand. Exclusive to Demon Hunter. |
| **Spellburst** | After you cast a spell (one-time) | Triggers once after the controlling player casts a spell while the Spellburst minion is on the board. The keyword is then consumed. |
| **Frenzy** | When this minion survives damage (one-time) | Triggers once after the minion takes damage and survives. The keyword is then consumed. |
| **Honorable Kill** | When this deals exact lethal damage | Triggers when this card deals exactly enough damage to kill a minion (reduces it to exactly 0 Health). |
| **Infuse** | While in hand, friendly minions die (conditional) | The card upgrades (Infuses) after a specified number of friendly minions die while it is in your hand. |
| **Overheal** | When healed past max Health | Triggers when a minion is healed while already at full Health. The excess healing triggers the Overheal effect. |

### Action Keywords

| Keyword | Type | Exact Rules |
|---------|------|-------------|
| **Discover** | Selection | Choose one of 3 randomly offered cards. Usually adds the chosen card to your hand. Pool is typically your class cards + Neutral cards. See Section 14 for full rules. |
| **Adapt** | Selection | Choose one of 3 random Adaptations from a pool of 10 buffs. Applied to the specified minion. (Un'Goro expansion.) |
| **Choose One** | Selection | Druid-exclusive. Pick one of two (or sometimes more) effects when playing the card. Some effects combine both options under specific conditions. |
| **Recruit** | Summon | Summon a minion from your deck (meeting specified conditions). It does not trigger Battlecry. |
| **Tradeable** | Hand utility | Pay 1 mana to shuffle this card into your deck and draw a new card. Cannot be used if you have 0 mana. |
| **Forge** | Hand upgrade | Pay 2 mana while the card is in your hand to upgrade it to a more powerful version. |
| **Echo** | Replay | After playing this card, a temporary copy is added to your hand. Can be replayed as long as you have mana. Copies vanish at end of turn. Echo copies cannot cost less than 1 mana. |
| **Magnetic** | Merge | When played to the **left** of a friendly Mech minion, this card merges with that Mech (stats and effects combine). If played in any other position, it functions as a standalone minion. (Boomsday expansion.) |
| **Corrupt** | Hand upgrade | While this card is in your hand, if you play a card with a higher mana cost, this card transforms into a more powerful Corrupted version. |
| **Colossal +X** | Summon | When this minion is played, it also summons X additional appendage minions. The appendages often have synergistic effects with the main body. |
| **Titan** | Multi-ability | This minion enters the board with 3 unique abilities. Each turn, one ability can be activated. After all 3 are used, the minion can attack normally. |
| **Dredge** | Deck manipulation | Look at the bottom 3 cards of your deck. Choose one to place on top of your deck. |

### Minion Aura Effects

| Effect | Description |
|--------|-------------|
| **Aura buff** (e.g., +1/+1 to adjacent minions) | Ongoing effect while the source minion is alive. Removed when the source dies or is silenced. |
| **Ongoing effect** (e.g., "Your spells cost (1) less") | Continuous effect that modifies game rules while the minion is on the board. |
| **End of turn** (e.g., "At the end of your turn, deal 1 damage to all other minions") | Triggers once at the end of the controlling player's turn. |
| **Start of turn** (e.g., "At the start of your turn, draw a card") | Triggers once at the start of the controlling player's turn. |

---

## 13. Secrets

### Overview

Secrets are spell cards with a hidden, delayed effect that triggers when a specific condition is met **on the opponent's turn**.

### Secret Rules

| Rule | Detail |
|------|--------|
| Hidden from opponent | The opponent sees a "?" icon on your hero portrait but not which Secret it is |
| Trigger timing | Only on the **opponent's turn** (you cannot trigger your own Secrets) |
| One per type | You cannot have two copies of the same Secret active simultaneously |
| Maximum active | 5 Secrets per player at a time |
| Order of resolution | Secrets trigger in the order they were played |
| Post-Battlecry | Secrets triggered by a minion being played activate **after** the minion's Battlecry resolves |
| Cannot be targeted | Active Secrets cannot be destroyed by targeting (some specific cards like Kezan Mystic or Flare can interact with them) |

### Secret Costs by Class

| Class | Secret Mana Cost | Glow Color |
|-------|-------------------|------------|
| Paladin | 1 mana | Yellow |
| Hunter | 2 mana | Green |
| Rogue | 2 mana | Dark Purple |
| Mage | 3 mana | Pink/Magenta |

All Secrets within a class cost the same amount to prevent deduction by mana cost.

### Example Classic Secrets

**Mage (3 mana):**

| Secret | Trigger | Effect |
|--------|---------|--------|
| Counterspell | Opponent casts a spell | Counter (negate) it |
| Mirror Entity | Opponent plays a minion | Summon a copy of it |
| Ice Block | Your hero takes fatal damage | Become Immune until end of turn; prevent death |
| Ice Barrier | Your hero is attacked | Gain 8 Armor |
| Vaporize | A minion attacks your hero | Destroy it |
| Spellbender | Opponent casts a targeted spell on a minion | Redirect it to a 1/3 minion summoned for you |

**Hunter (2 mana):**

| Secret | Trigger | Effect |
|--------|---------|--------|
| Explosive Trap | Your hero is attacked | Deal 2 damage to all enemies |
| Freezing Trap | An enemy minion attacks | Return it to the opponent's hand; it costs (2) more |
| Misdirection | An enemy character attacks your hero | Redirect the attack to a random other character |
| Snipe | Opponent plays a minion | Deal 4 damage to it |
| Snake Trap | One of your minions is attacked | Summon three 1/1 Snakes |

**Paladin (1 mana):**

| Secret | Trigger | Effect |
|--------|---------|--------|
| Noble Sacrifice | An enemy character attacks | Summon a 2/1 Defender to take the attack instead |
| Redemption | One of your minions dies | Return it to life with 1 Health |
| Repentance | Opponent plays a minion | Set its Health to 1 |
| Avenge | One of your minions dies | Give a random friendly minion +3/+2 |
| Eye for an Eye | Your hero takes damage | Deal the same amount to the enemy hero |

---

## 14. Discover Mechanic

### Core Rules

| Rule | Detail |
|------|--------|
| Options presented | 3 cards |
| Pool | Class cards + Neutral cards (unless otherwise specified) |
| Selection | Player chooses 1 of the 3; the other 2 are discarded |
| Default destination | Added to the player's hand |
| Duplicates | The same card can appear multiple times in the 3 options |
| Not from deck | Discovered cards are generated (not drawn from your deck) |
| Collectible only | Only collectible cards appear (not tokens) unless specified |

### Special Discover Variants

| Variant | Description |
|---------|-------------|
| "Discover a spell" | Only spells appear in the 3 options |
| "Discover a Deathrattle minion" | Only minions with Deathrattle appear |
| "Discover a card from your opponent's class" | Shows cards from the opponent's class + Neutral |
| Immediate summon (e.g., Free From Amber) | The chosen card is summoned directly, not added to hand |
| Immediate cast (e.g., Tortollan Primalist) | The chosen spell is cast immediately with random targets |

### Discover Pool Weighting

- Originally (League of Explorers), class cards were weighted 4x more likely than Neutral cards.
- This weighting was reduced over time. Current behavior: equal weighting for all eligible cards, though expansions may introduce specific pool filters.

---

## 15. Fatigue System

### Overview

When a player's deck is empty and they attempt to draw a card (either the automatic start-of-turn draw or any card draw effect), they instead take **Fatigue damage**.

### Fatigue Damage Progression

| Draw Attempt | Damage Taken | Cumulative Total |
|--------------|-------------|------------------|
| 1st | 1 | 1 |
| 2nd | 2 | 3 |
| 3rd | 3 | 6 |
| 4th | 4 | 10 |
| 5th | 5 | 15 |
| 6th | 6 | 21 |
| 7th | 7 | 28 |
| 8th | 8 | 36 |
| Nth | N | N(N+1)/2 |

### Fatigue Rules

| Rule | Detail |
|------|--------|
| Counter persistence | The fatigue counter **never resets**, even if cards are shuffled back into the deck. |
| Shuffle protection | If cards are shuffled into the deck, the next draw succeeds (no fatigue), but the counter remains at its current value for the next failed draw. |
| Multiple draws | If an effect draws multiple cards and the deck empties mid-effect, each subsequent draw triggers increasing fatigue. Example: Drawing 3 cards with 1 card left = 1 card drawn + 1 fatigue + 2 fatigue. |
| No card gained | Fatigue does not add a card to the hand. The draw simply fails and deals damage. |
| Damage to hero | Fatigue damage bypasses Armor (it is dealt to Armor first per normal damage rules, but it is damage to the hero). |
| Lethal fatigue | Fatigue damage can kill a hero, ending the game. |
| Both players | If both players reach 0 Health simultaneously (e.g., from simultaneous effects), the game is a **draw** (tie). |

---

## 16. Game Modes

### 16.1 Ranked (Standard / Wild)

| Property | Detail |
|----------|--------|
| Format | Standard or Wild (separate ladders) |
| Season length | 1 calendar month |
| Leagues | Bronze, Silver, Gold, Platinum, Diamond (each has ranks 10 through 1) |
| Legend rank | Above Diamond 1; numbered by MMR position (e.g., Legend #1 is the top player) |
| Stars per win | 1 star; bonus stars for win streaks (up to x11 at season start based on prior finish) |
| Stars to rank up | 3 stars per rank within a league |
| Rank floors | Ranks 10 and 5 within each league are floors (cannot drop below them once reached) |
| Season reset | All players are reset; distance depends on prior season finish |
| Rewards | Card packs and a card back for each season |

**Star Bonus System:**

| Previous Season Finish | Star Bonus |
|------------------------|------------|
| Bronze 5 - Bronze 1 | x2 |
| Silver 10 - Silver 1 | x3 |
| Gold 10 - Gold 1 | x4 |
| Platinum 10 - Platinum 1 | x5 |
| Diamond 10 - Diamond 5 | x6 |
| Diamond 4 - Diamond 1 | x7-x9 |
| Legend | x10-x11 |

### 16.2 Casual

| Property | Detail |
|----------|--------|
| Format | Standard or Wild |
| Matchmaking | MMR-based (hidden), separate from Ranked MMR |
| Progression | No rank displayed; counts toward daily quests and XP |
| Stakes | No rank gain/loss |

### 16.3 Arena

| Property | Detail |
|----------|--------|
| Entry fee | 150 Gold or real money equivalent |
| Draft process | Choose 1 of 3 cards, 30 times, building a 30-card deck |
| Class selection | Choose 1 of 3 randomly offered classes |
| Card limits | No rarity or copy limits (can have 3+ copies of a card, multiple Legendaries) |
| Collection independent | All cards in the arena pool are available regardless of player's collection |
| Win target | 12 wins (maximum) |
| Loss limit | 3 losses (run ends) |
| Rewards | Scale with wins; at 7+ wins, gold reward exceeds entry fee |
| No time limit | Run can be completed across multiple sessions |

**Arena Reward Tiers:**

| Wins | Approximate Rewards |
|------|---------------------|
| 0-2 | 1 card pack + small dust/gold |
| 3-4 | 1 card pack + 25-60 gold |
| 5-6 | 1 card pack + 50-100 gold |
| 7-8 | 1 card pack + 150-200 gold (breaks even or profit) |
| 9-10 | 1 card pack + 200-300 gold + extra rewards |
| 11 | 1 card pack + 300-400 gold + extra rewards |
| 12 | 1 card pack + 400-500 gold + extra rewards (golden card, packs) |

### 16.4 Tavern Brawl

| Property | Detail |
|----------|--------|
| Frequency | Weekly (new brawl each Wednesday) |
| Rules | Unique rules each week (pre-built decks, special mechanics, deck-building challenges) |
| Reward | 1 Classic/Standard card pack for first win each week |
| Cost | Free |

### 16.5 Solo Adventures

| Property | Detail |
|----------|--------|
| Format | PvE (player vs AI bosses) |
| Structure | Linear campaign with escalating difficulty |
| Rewards | Card packs, unique cards, hero portraits |
| Examples | Curse of Naxxramas, League of Explorers, Knights of the Frozen Throne (free Prologue) |

### 16.6 Battlegrounds (Auto-Battler Mode)

| Property | Detail |
|----------|--------|
| Players | 8-player free-for-all |
| Format | Auto-battler; recruit minions in a tavern phase, combat is automated |
| Health | Each player starts at 30-40 Health (varies by hero) |
| Elimination | Last player standing wins; top 4 = positive result |
| Separate from constructed | Uses its own card pool, hero pool, and progression |

---

## 17. UI Layout

### 17.1 Main Game Board

```
+===========================================================================+
|                           OPPONENT'S HERO                                  |
|  [Hero Portrait] [HP: ##] [Armor: ##] [Hero Power] [Weapon] [Mana: X/Y]  |
|  [Secret Icons: ? ? ? ? ?]                                                 |
|---------------------------------------------------------------------------+
|                        OPPONENT'S HAND (card backs)                        |
|  [Card][Card][Card][Card][Card][Card][Card][Card][Card][Card]             |
|---------------------------------------------------------------------------+
|                        OPPONENT'S BOARD (minions)                          |
|  [Minion1] [Minion2] [Minion3] [Minion4] [Minion5] [Minion6] [Minion7]  |
|===========================================================================|
|                     *** GAME BOARD CENTER ***                              |
|              [Turn counter]  [History sidebar]                             |
|===========================================================================|
|                        YOUR BOARD (minions)                                |
|  [Minion1] [Minion2] [Minion3] [Minion4] [Minion5] [Minion6] [Minion7]  |
|---------------------------------------------------------------------------+
|                           YOUR HAND (face-up)                              |
|  [Card][Card][Card][Card][Card][Card][Card][Card][Card][Card]             |
|---------------------------------------------------------------------------+
|                            YOUR HERO                                       |
|  [Hero Portrait] [HP: ##] [Armor: ##] [Hero Power] [Weapon] [Mana: X/Y]  |
|  [Secret Icons]                                                            |
|                                                      [END TURN BUTTON]    |
+===========================================================================+
```

### 17.2 Card Display (In-Hand)

```
+-------------------+
| [Mana Cost]       |      -- Top-left crystal icon
|                   |
|   [Card Art]      |      -- Central illustration
|                   |
| [Name Banner]     |      -- Card name; rarity gem centered below
|                   |
| [Card Text]       |      -- Description / keywords
|                   |
| [ATK]       [HP]  |      -- Bottom corners (minions/weapons only)
+-------------------+        ATK = Attack, HP = Health or Durability
```

### 17.3 Hero Zone Detail

| Element | Position | Description |
|---------|----------|-------------|
| Hero portrait | Center | Circular portrait; shows current hero (can change with Hero cards) |
| Health counter | Below portrait | Green number; turns red when damaged below 15 |
| Armor counter | Over health | Gray shield icon with armor value; overlays health |
| Hero Power | Right of portrait | Clickable button; grays out after use |
| Weapon | Left of portrait | Displays weapon art with Attack/Durability overlay |
| Secret icon(s) | Above portrait | Up to 5 "?" icons with class-colored glow |
| Mana crystals | Bottom-right | Row of crystals: blue (available), gray (spent), padlocked (overloaded) |

### 17.4 Additional UI Elements

| Element | Description |
|---------|-------------|
| End Turn button | Large green button at right side of board; glows when it is your turn; text changes to "ENEMY TURN" when waiting |
| Turn history | Right sidebar showing a scrollable log of recent plays (cards played, attacks, effects) |
| Rope / Fuse | Burning fuse across the center of the board when ~20 seconds remain in the turn |
| Emote menu | Right-click hero portrait to show emotes: Greetings, Well Played, Thanks, Wow, Oops, Threaten |
| Squelch | Right-click enemy hero to squelch (mute) their emotes |
| Concede button | In the options menu (gear icon, top-right) |
| Deck counter | Shows remaining cards in each player's deck (number on the deck) |
| Card hover | Hovering over a card in hand shows an enlarged version; hovering over a board minion shows its stats and enchantments |

---

## 18. Audio & Visual Design

### 18.1 Audio Design

| Category | Description |
|----------|-------------|
| Menu music | Warm tavern theme with lute, accordion, and ambient crowd chatter |
| In-game music | Class-specific or board-specific ambient music; low intensity to avoid distraction |
| Card play SFX | Each card has unique voice lines when played (Battlecry quote), attack, and death |
| Hero power SFX | Class-specific sound effect (e.g., Fireblast has a fire crackle, Armor Up! has a metallic clang) |
| Attack SFX | Impact sounds that vary by attack value (light tap for 1 ATK, heavy slam for 8+ ATK) |
| Spell SFX | Unique per spell; fire spells crackle, frost spells shatter, holy spells chime |
| Rope SFX | Sizzling fuse sound that intensifies as time runs out |
| Lethal alert | Dramatic sting when a player is about to die |
| Legendary play | Unique entrance animation with dramatic sound sting and golden border flash |
| Board interactions | Clickable interactive elements on the game board (vary by board theme) |
| Emote voice lines | Each hero has 6 voiced emotes (Greetings, Well Played, Thanks, Wow, Oops, Threaten) |
| Coin flip | Distinct coin-flip sound at game start to determine who goes first |

### 18.2 Visual Design

| Element | Description |
|---------|-------------|
| Art style | Hand-painted Warcraft fantasy art; colorful, exaggerated proportions; approachable and warm |
| Card art | Each card has a unique illustration by a professional artist |
| Golden cards | Animated card art with particle effects (flames, sparkles, flowing water) |
| Game boards | Themed interactive boards (Stormwind, Orgrimmar, Pandaria, etc.) with clickable elements |
| Minion tokens | On-board minions displayed as circular portraits with attack (yellow shield, bottom-left) and health (red drop, bottom-right) |
| Damage numbers | Red floating numbers appear when damage is dealt; green numbers for healing |
| Divine Shield | Golden bubble surrounds the minion; shatters visually when broken |
| Taunt | Minion border shows a large shield-shaped outline |
| Stealth | Minion appears translucent/shadowy |
| Frozen | Blue ice crystal overlay on the frozen character |
| Poisonous | Green dripping venom effect on the minion border |
| Deathrattle | Skull icon on the card and minion token |
| Buffed stats | Green numbers indicate stats above base values |
| Damaged stats | Red numbers indicate health below maximum |
| Legendary border | Dragon-head border on Legendary minion tokens |
| Mana crystal animation | Crystals crack and shatter when spent; re-form (refill) at turn start |
| Pack opening | Dramatic pack-opening animation with rarity-based visual effects (Legendary: orange beam of light) |
| Hero death | Exploding hero portrait with dramatic shatter effect |

### 18.3 Board Themes

| Board | Theme | Interactive Elements |
|-------|-------|---------------------|
| Stormwind | Alliance city; stone architecture | Catapult, flags, shield |
| Orgrimmar | Horde fortress; spikes and bones | Drums, bone pile, campfire |
| Pandaria | Mists of Pandaria; eastern temple | Gong, garden, lanterns |
| Stranglethorn | Jungle board; tribal theme | Volcano, vines, tribal mask |
| Naxxramas | Undead citadel; dark stone | Slime pool, spider eggs, bones |
| GvG | Mechanical/steampunk | Levers, gears, robots |

Each board has multiple clickable zones that produce small animations and sounds when clicked repeatedly (purely cosmetic).

### 18.4 Animation Timing

| Animation | Approximate Duration |
|-----------|---------------------|
| Card draw | 0.5 seconds |
| Card play (minion) | 0.8 seconds |
| Card play (spell) | 0.5-2.0 seconds (varies by spell complexity) |
| Minion attack | 0.6 seconds |
| Hero attack | 0.6 seconds |
| Minion death | 0.4 seconds |
| Battlecry effect | 0.3-1.5 seconds |
| Deathrattle effect | 0.3-1.5 seconds |
| Legendary entrance | 2.0-3.0 seconds (with camera zoom and fanfare) |
| Secret trigger | 1.0 seconds (reveal animation + effect) |
| Discover selection | Player-controlled (choices displayed until selection or timeout) |
| End of turn transition | 0.3 seconds |
| Fatigue damage | 0.5 seconds (deck sparks, damage number appears) |

---

## Appendix A: Complete Turn Flow Example

```
=== PLAYER A's TURN (Turn 5, 5 Mana Crystals) ===

START OF TURN:
  - Mana crystals: 4 -> 5 (gain 1 crystal)
  - Pending overload: 2 (from Lightning Storm last turn)
  - Locked overload: 0 -> 2 (pending becomes locked)
  - Available mana: 5 - 2 = 3 mana available
  - Draw 1 card (now has 5 cards in hand)
  - Start-of-turn triggers resolve (e.g., Nat Pagle may draw a card)

ACTION PHASE (player may do these in any order):
  1. Play "Feral Spirit" (3 mana, Overload: 2)
     - Summon two 2/3 Spirit Wolf tokens with Taunt
     - Remaining mana: 0
     - Pending overload: 0 -> 2 (will lock next turn)
  2. Attack with existing Huffer (4/2 Beast) -> Enemy Hero
     - Enemy hero takes 4 damage
     - Huffer has now attacked this turn
  3. Hero Power not used (0 mana remaining)

END OF TURN:
  - End-of-turn triggers resolve
  - Hero temporary attack removed
  - Pass to Player B

=== PLAYER B's TURN ===
  ...
```

## Appendix B: Interaction Priority & Resolution Order

When multiple effects trigger simultaneously, the following priority applies:

```
1. Death processing (check for any pending deaths)
2. Deathrattles (in play order -- the minion played first triggers first)
3. On-death triggers (e.g., "Whenever a friendly minion dies")
4. Secrets (in the order they were played)
5. Aura updates (recalculate all ongoing effects)
6. Death processing again (if new deaths occurred from step 2-4)
```

**Key Resolution Principles:**
- Effects resolve **one at a time**, in order.
- **Play order** determines trigger order when multiple effects could trigger simultaneously.
- The **active player's** effects always trigger before the **non-active player's** effects.
- Deaths are checked in a "death phase" after each outermost phase resolves, not during mid-resolution.
- If both heroes reach 0 Health simultaneously, the game is a **draw**.

---

*This specification covers the core mechanics of Hearthstone necessary for a faithful recreation. Individual card implementations, expansion-specific mechanics, and balance tuning would require additional card-by-card documentation beyond this core rules engine.*
