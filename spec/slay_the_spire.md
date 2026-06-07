# Slay the Spire — Complete Game Specification

## 1. Game Overview

Slay the Spire is a single-player deck-building rogue-like where the player ascends through a procedurally generated spire of three acts, battling enemies with a customizable deck of cards, collecting relics, and making strategic decisions at each node on a branching map. Each run is unique due to randomized card offerings, relics, and map layouts.

- Genre: Deck-building rogue-like
- Resolution: 1920x1080 reference
- Input: Mouse (click cards, click targets, drag cards)
- Run Length: 45-90 minutes
- Replayability: Procedural generation, 4 characters, 20 Ascension levels

## 2. Technical Foundation

### 2.1 Core Game Loop
```
Run Start:
  1. Choose character
  2. Generate Act 1 map
  3. Navigate map node by node:
     For each node:
       - COMBAT: Play cards to defeat enemies
       - EVENT: Make a narrative choice
       - REST: Heal or upgrade a card
       - SHOP: Buy/remove cards and relics
       - TREASURE: Get a relic
       - ELITE: Hard combat with relic reward
       - BOSS: Act boss, then choose boss relic
  4. After Act 3 boss: Victory (or continue to Act 4 with keys)
```

### 2.2 Combat Loop
```
Combat Start:
  - Draw 5 cards from draw pile
  - Player gets 3 energy

Each Turn:
  PLAYER PHASE:
    1. Draw 5 cards (modified by relics/powers)
    2. Gain 3 energy (modified by relics/powers)
    3. Play cards by spending energy
    4. End turn (discard hand to discard pile)
  ENEMY PHASE:
    1. Each enemy executes their intended action
    2. Enemy intents refresh for next turn
  BETWEEN TURNS:
    - Trigger start-of-turn effects
    - Reduce temporary buffs/debuffs by 1
```

## 3. Characters

### 3.1 The Ironclad (Warrior)
- Starting HP: 80
- Starting Relic: Burning Blood (heal 6 HP at end of combat)
- Starting Deck (10 cards):
  - 5x Strike (Attack, 1 energy, 6 damage)
  - 4x Defend (Skill, 1 energy, 5 block)
  - 1x Bash (Attack, 2 energy, 8 damage, apply 2 Vulnerable)
- Playstyle: Strength scaling, exhaust synergy, self-healing

### 3.2 The Silent (Rogue)
- Starting HP: 70
- Starting Relic: Ring of the Snake (draw 2 additional cards on turn 1)
- Starting Deck (12 cards):
  - 5x Strike (Attack, 1 energy, 6 damage)
  - 5x Defend (Skill, 1 energy, 5 block)
  - 1x Survivor (Skill, 1 energy, 8 block, discard 1 card)
  - 1x Neutralize (Attack, 0 energy, 3 damage, apply 1 Weak)
- Playstyle: Poison, shiv generation, discard synergy

### 3.3 The Defect (Robot)
- Starting HP: 75
- Starting Relic: Cracked Core (channel 1 Lightning orb at start of combat)
- Starting Deck (10 cards):
  - 4x Strike (Attack, 1 energy, 6 damage)
  - 4x Defend (Skill, 1 energy, 5 block)
  - 1x Zap (Skill, 1 energy, channel 1 Lightning orb)
  - 1x Dualcast (Skill, 1 energy, evoke top orb twice)
- Playstyle: Orb management, focus scaling, multi-element synergy

### 3.4 The Watcher (Monk)
- Starting HP: 72
- Starting Relic: Pure Water (add Miracle to hand at start of combat)
- Starting Deck (10 cards):
  - 4x Strike (Attack, 1 energy, 6 damage)
  - 4x Defend (Skill, 1 energy, 5 block)
  - 1x Eruption (Attack, 2 energy, 9 damage, enter Wrath stance)
  - 1x Vigilance (Skill, 2 energy, 8 block, enter Calm stance)
- Playstyle: Stance dancing, Wrath/Calm management, scry, retain

## 4. Card System

### 4.1 Card Properties
```
Card {
  name: String
  type: Attack | Skill | Power | Status | Curse
  rarity: Basic | Common | Uncommon | Rare
  energy_cost: 0-5 (or X)
  damage: int (optional)
  block: int (optional)
  effects: List<Effect>
  exhaust: bool  // removed from deck for rest of combat if true
  ethereal: bool // exhausted if in hand at end of turn
  innate: bool   // always drawn on turn 1
  retain: bool   // stays in hand at end of turn
  upgraded: bool
  description: String
}
```

### 4.2 Ironclad Cards (Selected)

**Attacks:**
| Card              | Cost | Base Effect                    | Upgraded Effect              | Rarity   |
|-------------------|------|--------------------------------|------------------------------|----------|
| Strike            | 1    | 6 damage                      | 9 damage                    | Basic    |
| Bash              | 2    | 8 dmg, 2 Vulnerable           | 10 dmg, 3 Vulnerable        | Basic    |
| Anger             | 0    | 6 dmg, add copy to discard    | 8 dmg, add copy to discard  | Common   |
| Body Slam         | 1    | Damage = current Block        | Cost 0                      | Common   |
| Clash             | 0    | 14 damage (only if hand is all attacks)| 18 damage            | Common   |
| Cleave            | 1    | 8 damage to ALL enemies       | 11 damage to ALL            | Common   |
| Headbutt          | 1    | 9 dmg, put card from discard on top| 12 dmg                | Common   |
| Heavy Blade       | 2    | 14 dmg, 3x Strength bonus     | 14 dmg, 5x Strength bonus  | Common   |
| Iron Wave         | 1    | 5 dmg + 5 block               | 7 dmg + 7 block            | Common   |
| Pommel Strike      | 1    | 9 dmg, draw 1                 | 10 dmg, draw 2             | Common   |
| Sword Boomerang   | 1    | Hit random enemy 3x for 3 dmg | 3x for 4 dmg              | Common   |
| Thunderclap       | 1    | 4 dmg + 1 Vulnerable to ALL   | 7 dmg + 1 Vulnerable       | Common   |
| Carnage           | 2    | 20 damage, Ethereal           | 28 damage, Ethereal        | Uncommon |
| Dropkick          | 1    | 5 dmg, if Vulnerable: +1E draw 1| 8 dmg                    | Uncommon |
| Hemokinesis       | 1    | Lose 2 HP, 15 damage          | Lose 2 HP, 20 damage       | Uncommon |
| Pummel            | 1    | Hit 4x for 2 damage, Exhaust  | Hit 5x for 2 damage        | Uncommon |
| Rampage           | 1    | 8 dmg, +5 dmg each play       | 8 dmg, +8 dmg each play   | Uncommon |
| Searing Blow      | 2    | 12 dmg (+4 per additional upgrade)| Infinitely upgradable  | Uncommon |
| Uppercut          | 2    | 13 dmg, 1 Weak, 1 Vulnerable  | 13 dmg, 2 each            | Uncommon |
| Bludgeon          | 3    | 32 damage                     | 42 damage                  | Rare     |
| Feed              | 1    | 10 dmg, if kill: +3 max HP    | 12 dmg, +4 max HP         | Rare     |
| Fiend Fire        | 2    | Exhaust hand, 7 dmg per card  | 10 dmg per card           | Rare     |
| Immolate          | 2    | 21 dmg to ALL, add Burn to discard| 28 dmg to ALL          | Rare     |
| Reaper            | 2    | 4 dmg to ALL, heal per dmg dealt| 5 dmg to ALL             | Rare     |

**Skills:**
| Card              | Cost | Base Effect                    | Upgraded Effect              | Rarity   |
|-------------------|------|--------------------------------|------------------------------|----------|
| Defend            | 1    | 5 block                       | 8 block                     | Basic    |
| Armaments         | 1    | 5 block, upgrade 1 card in hand| 5 block, upgrade ALL in hand| Common   |
| Flex              | 0    | +2 Strength this turn         | +4 Strength this turn       | Common   |
| Havoc             | 1    | Play top card of draw pile     | Cost 0                      | Common   |
| Shrug It Off      | 1    | 8 block, draw 1               | 11 block, draw 1            | Common   |
| True Grit         | 1    | 7 block, Exhaust random card  | 9 block, choose card        | Common   |
| Warcry            | 0    | Draw 2, put 1 card on draw pile| Draw 3                     | Common   |
| Battle Trance     | 0    | Draw 3, can't draw more this turn| Draw 4                   | Uncommon |
| Bloodletting      | 0    | Lose 3 HP, +2 Energy          | Lose 3 HP, +3 Energy       | Uncommon |
| Disarm            | 1    | Enemy loses 2 Strength, Exhaust| Loses 3 Strength           | Uncommon |
| Entrench          | 2    | Double current block           | Cost 1                      | Uncommon |
| Ghost Armor       | 1    | 10 block, Ethereal            | 13 block, Ethereal         | Uncommon |
| Infernal Blade    | 1    | Add random Attack to hand (0 cost)| Cost 0                  | Uncommon |
| Seeing Red        | 1    | +2 Energy                     | Cost 0                      | Uncommon |
| Shockwave         | 2    | 2 Weak + 2 Vulnerable to ALL, Exhaust| 3 each              | Uncommon |
| Impervious        | 2    | 30 block, Exhaust             | 40 block, Exhaust          | Rare     |
| Limit Break       | 1    | Double Strength, Exhaust      | Double Strength (no exhaust)| Rare    |
| Offering          | 0    | Lose 6 HP, +2 Energy, draw 3  | Lose 6 HP, +2E, draw 5    | Rare     |

**Powers:**
| Card              | Cost | Base Effect                    | Upgraded Effect              | Rarity   |
|-------------------|------|--------------------------------|------------------------------|----------|
| Combust           | 1    | Lose 1 HP/turn, 5 dmg to ALL  | 7 dmg to ALL               | Uncommon |
| Dark Embrace      | 2    | Draw 1 when card exhausted     | Cost 1                      | Uncommon |
| Evolve            | 1    | Draw 1 when Status card drawn  | Draw 2                      | Uncommon |
| Feel No Pain      | 1    | +3 block when card exhausted   | +4 block                    | Uncommon |
| Fire Breathing    | 1    | 6 dmg to ALL when Attack drawn | 10 dmg                      | Uncommon |
| Inflame           | 1    | +2 Strength                    | +3 Strength                 | Uncommon |
| Metallicize       | 1    | +3 block at end of turn        | +4 block                    | Uncommon |
| Rupture           | 1    | +1 Strength when HP lost from card| +2 Strength              | Uncommon |
| Barricade         | 3    | Block no longer expires at turn start| Cost 2                 | Rare     |
| Berserk           | 0    | 2 Vulnerable to self, +1E/turn | 1 Vulnerable to self       | Rare     |
| Brutality         | 0    | Lose 1 HP/turn, draw 1 extra  | Draw 2 extra               | Rare     |
| Corruption        | 3    | Skills cost 0, Exhaust when played| Cost 2                   | Rare     |
| Demon Form        | 3    | +2 Strength at start of turn   | +3 Strength                | Rare     |
| Juggernaut        | 2    | Deal 5 dmg when gain Block     | 7 dmg                      | Rare     |

### 4.3 Silent Cards (Selected)

| Card              | Cost | Effect                         | Rarity   |
|-------------------|------|--------------------------------|----------|
| Neutralize        | 0    | 3 dmg, 1 Weak                 | Basic    |
| Survivor          | 1    | 8 block, discard 1            | Basic    |
| Blade Dance       | 1    | Add 3 Shivs to hand           | Common   |
| Dagger Spray      | 1    | 4 dmg to ALL x2               | Common   |
| Deadly Poison     | 1    | Apply 5 Poison                 | Common   |
| Deflect           | 0    | 4 block                       | Common   |
| Dodge and Roll    | 1    | 4 block, next turn 4 block    | Common   |
| Flying Knee       | 1    | 8 dmg, +1 Energy next turn    | Common   |
| Poisoned Stab     | 1    | 6 dmg, 3 Poison               | Common   |
| Quick Slash       | 1    | 8 dmg, draw 1                 | Common   |
| Slice             | 0    | 6 damage                      | Common   |
| Accuracy          | 1    | Shivs deal +4 damage          | Uncommon |
| Backstab          | 0    | 11 dmg, Innate, Exhaust       | Uncommon |
| Catalyst          | 1    | Double enemy Poison, Exhaust  | Uncommon |
| Dash              | 2    | 10 dmg + 10 block             | Uncommon |
| Footwork          | 1    | +2 Dexterity                  | Uncommon |
| Leg Sweep         | 2    | 2 Weak, 11 block              | Uncommon |
| Noxious Fumes     | 1    | 2 Poison to ALL at turn start | Uncommon |
| Phantasmal Killer | 1    | Next turn: double Attack dmg  | Uncommon |
| Terror            | 1    | 99 Vulnerable, Exhaust        | Uncommon |
| Adrenaline        | 0    | +1E, draw 2, Exhaust          | Rare     |
| After Image       | 1    | 1 block when card played      | Rare     |
| Bullet Time       | 3    | Cards cost 0 this turn, can't draw| Rare |
| Corpse Explosion  | 2    | On death: Poison dmg to ALL   | Rare     |
| Die Die Die       | 1    | 13 dmg to ALL, Exhaust        | Rare     |
| Envenom           | 2    | Attacks apply 1 Poison        | Rare     |
| Malaise           | X    | X Strength loss + X Weak      | Rare     |
| Wraith Form       | 3    | +2 Intangible, 1 Dex loss/turn| Rare     |

### 4.4 Status Cards (Added to deck by enemies/events)
| Card    | Cost | Effect                           |
|---------|------|----------------------------------|
| Burn    | Unplayable | Take 2 damage at end of turn    |
| Dazed   | Unplayable | Ethereal (auto-exhaust)         |
| Slimed  | 1    | Exhaust (waste of energy)        |
| Void    | Unplayable | Ethereal, lose 1 Energy when drawn|
| Wound   | Unplayable | Does nothing, clogs hand         |

### 4.5 Curse Cards
| Card         | Cost | Effect                                |
|--------------|------|---------------------------------------|
| Ascender's Bane| Unplayable | Ethereal, cannot be removed      |
| Clumsy       | Unplayable | Ethereal                          |
| Decay        | Unplayable | Take 2 damage end of turn         |
| Doubt        | Unplayable | 1 Weak at start of turn           |
| Injury       | Unplayable | Just clogs your deck              |
| Normality    | Unplayable | Can't play more than 3 cards/turn |
| Pain         | Unplayable | Lose 1 HP when card played        |
| Parasite     | Unplayable | Lose 3 max HP if removed          |
| Regret       | Unplayable | Lose HP equal to cards in hand    |
| Shame        | Unplayable | 1 Frail at start of turn          |
| Writhe       | Unplayable | Innate (always drawn turn 1)      |

## 5. Status Effects (Buffs/Debuffs)

### 5.1 Common Buffs
| Buff        | Effect                                  | Duration      |
|-------------|----------------------------------------|---------------|
| Strength    | +X damage per Attack card              | Permanent     |
| Dexterity   | +X block per Block card                | Permanent     |
| Artifact    | Negate next X debuffs                  | X uses        |
| Intangible  | Reduce ALL damage to 1                 | X turns       |
| Plated Armor| +X block at end of turn, lose 1 when hit| Until 0     |
| Thorns      | Deal X damage when attacked            | Permanent     |
| Buffer      | Prevent next X HP loss instances        | X uses        |
| Metallicize | Gain X block at end of turn            | Permanent     |
| Ritual      | Gain X Strength at start of turn       | Permanent     |
| Regeneration| Heal X at end of turn                  | X turns       |

### 5.2 Common Debuffs
| Debuff      | Effect                                  | Duration      |
|-------------|----------------------------------------|---------------|
| Vulnerable  | Take 50% more damage from Attacks      | X turns       |
| Weak        | Deal 25% less damage with Attacks      | X turns       |
| Frail       | Block cards give 25% less Block        | X turns       |
| Poison      | Lose X HP at start of turn, reduce by 1| Until 0       |
| Constricted | Lose X HP at end of turn               | Until removed |
| Entangled   | Cannot play Attacks this turn          | 1 turn        |
| Draw Down   | Draw 1 fewer card next turn            | 1 turn        |
| Strength Down| Lose X Strength at end of turn         | 1 turn       |

### 5.3 Damage Formula
```
function calculateDamage(card, source, target):
    baseDamage = card.damage
    damage = baseDamage + source.strength

    if source.isWeak:
        damage = floor(damage * 0.75)

    if target.isVulnerable:
        damage = floor(damage * 1.5)

    // Apply relics
    if source.hasRelic("Pen Nib") and source.penNibCounter == 10:
        damage *= 2
    if source.hasRelic("Wrist Blade") and card.cost == 0:
        damage += 4

    return max(0, damage)

function calculateBlock(card, source):
    baseBlock = card.block
    block = baseBlock + source.dexterity

    if source.isFrail:
        block = floor(block * 0.75)

    return max(0, block)
```

## 6. Enemy System

### 6.1 Enemy Intent System
- Each enemy displays their intent at start of player turn
- Intents are determined by AI patterns (see Section 6.3)
- Intent types: Attack, Defend, Buff, Debuff, Unknown
- Damage numbers shown on Attack intents

### 6.2 Act 1 Enemies

**Normal Encounters:**
| Enemy         | HP     | Attacks                                    |
|---------------|--------|--------------------------------------------|
| Jaw Worm      | 40-44  | Chomp (11 dmg), Bellow (+3 Str, 6 block), Thrash (7 dmg) |
| Cultist       | 48-54  | Incantation (+3 Ritual), Dark Strike (6 dmg)|
| Blue Slaver   | 46-50  | Stab (12 dmg), Rake (7 dmg + 1 Weak)      |
| Red Slaver    | 46-50  | Stab (13 dmg), Scrape (8 dmg + 1 Vulnerable), Entangle |
| Fungi Beast   | 22-28  | Bite (6 dmg), Grow (+3 Str)               |
| Louse (Red)   | 10-15  | Bite (5-7 dmg), Grow (+3 Str)             |
| Louse (Green) | 11-17  | Bite (5-7 dmg), Spit Web (2 Weak)         |
| Acid Slime (M)| 28-32  | Corrosive Spit (7 dmg + Slimed), Lick (Weak), Tackle (10 dmg) |
| Spike Slime(M)| 28-32  | Flame Tackle (8 dmg + Slimed), Lick (Frail)|
| Acid Slime (L)| 65-69  | Same as M but stronger, splits when <50% HP|
| Spike Slime(L)| 64-70  | Same as M but stronger, splits when <50% HP|

**Elite Encounters:**
| Enemy         | HP     | Attacks                                    |
|---------------|--------|--------------------------------------------|
| Gremlin Nob   | 82-86  | Rush (14 dmg), Skull Bash (6 dmg + 2 Vulnerable), Rage (+2 Str when player plays Skill) |
| Lagavulin     | 108-112| Attack (18 dmg), Siphon Soul (-1 Str, -1 Dex), Sleeping (starts asleep, wakes on hit or turn 3) |
| 3 Sentries    | 38-42 each | Bolt (9 dmg), Dazed (add Dazed to discard), alternate attack/debuff |

**Act 1 Bosses:**
| Boss           | HP      | Mechanics                                  |
|----------------|---------|-------------------------------------------|
| The Guardian   | 240     | Twin Slam (32 dmg), Shield (Sharp Hide: deal 3 dmg when attacked), cycles between Attack and Defend modes |
| Hexaghost      | 250     | Activate (divides into 6 flames), Inferno (6x dmg based on first turn damage), Sear (6 dmg + Burn) |
| Slime Boss     | 140     | Slam (35 dmg), Preparing (charges), splits into 2 large slimes at 50% HP |

### 6.3 Enemy AI Patterns
```
// Example: Jaw Worm AI
jawWormAI = {
  turn 1: 75% Chomp, 25% Bellow
  subsequent:
    after Chomp: 45% Bellow, 30% Thrash, 25% Chomp
    after Bellow: 30% Chomp, 30% Thrash, 40% Chomp
    after Thrash: 55% Chomp, 45% Bellow
    never same move 3 times in row
}

// Example: Cultist AI
cultistAI = {
  turn 1: Incantation (always)
  turn 2+: Dark Strike (always, damage increases from Ritual)
}
```

### 6.4 Act 2 Enemies (Samples)
| Enemy          | HP      | Key Mechanic                              |
|----------------|---------|-------------------------------------------|
| Chosen         | 95      | Hex (debuff), Poke (5x2 dmg)             |
| Byrd           | 25-31   | Flying (50% less damage until grounded)   |
| Shelled Parasite| 68-72  | Suck (10 dmg + heal), Double Strike       |
| Snecko         | 114-120 | Tail Whip (8 dmg + 2 Vulnerable), Perplexing Glare (confuse) |
| Book of Stabbing| 160    | Multi-stab (6 dmg, +1 stab per turn)     |
| Automaton      | 188     | Boost (3 Str + 3 block), Hyper Beam (45 dmg, debuff self) |

### 6.5 Act 3 Enemies (Samples)
| Enemy          | HP      | Key Mechanic                              |
|----------------|---------|-------------------------------------------|
| Reptomancer    | 180     | Summons 2 Daggers (25 HP, hit hard)       |
| Giant Head     | 500     | Slow (reduce damage dealt), Count (grows stronger) |
| Nemesis        | 185     | Scythe (45 dmg), Debilitate (3 Burn), becomes intangible |
| Awakened One   | 300+300 | Phase 1: hits, Phase 2: stronger, +2 Str when player plays Power |
| Time Eater     | 456     | Stops player after 12 cards played per turn|
| Donu & Deca    | 250+250 | One buffs, one attacks, must kill both    |

## 7. Relics

### 7.1 Starter Relics
| Relic          | Character | Effect                                   |
|----------------|-----------|------------------------------------------|
| Burning Blood  | Ironclad  | Heal 6 HP at end of combat              |
| Ring of Snake  | Silent    | Draw 2 extra cards on turn 1            |
| Cracked Core   | Defect    | Channel 1 Lightning at combat start     |
| Pure Water     | Watcher   | Add Miracle to hand at combat start     |

### 7.2 Common Relics
| Relic              | Effect                                       |
|--------------------|----------------------------------------------|
| Anchor             | Start combat with 10 Block                   |
| Bag of Marbles     | Apply 1 Vulnerable to ALL at combat start    |
| Blood Vial         | Heal 2 HP at start of each combat            |
| Bronze Scales      | 3 Thorns                                     |
| Centennial Puzzle  | First time you lose HP: draw 3 cards         |
| Lantern            | +1 Energy on first turn                      |
| Oddly Smooth Stone | +1 Dexterity                                 |
| Orichalcum         | End turn without Block: gain 6 Block         |
| Pen Nib            | Every 10th Attack: double damage             |
| Red Skull           | +3 Strength while HP <= 50%                  |
| Snecko Skull       | +1 Poison when applying Poison               |
| Vajra              | +1 Strength                                  |

### 7.3 Uncommon Relics
| Relic              | Effect                                       |
|--------------------|----------------------------------------------|
| Blue Candle        | Can play Curses (they Exhaust, lose 1 HP)    |
| Bottled Flame      | Choose an Attack: it's Innate                |
| Bottled Lightning  | Choose a Skill: it's Innate                  |
| Bottled Tornado    | Choose a Power: it's Innate                  |
| Darkstone Periapt  | +6 max HP when obtain a Curse                |
| Eternal Feather    | Heal 3 HP per 5 cards in deck at rest site   |
| Frozen Egg         | Attacks obtained are Upgraded                 |
| Kunai              | Play 3 Attacks in a turn: +1 Dexterity       |
| Letter Opener      | Play 3 Skills in a turn: 5 damage to ALL     |
| Meat on the Bone   | End combat <= 50% HP: heal 12                |
| Mercury Hourglass  | 3 damage to ALL at start of each turn        |
| Mummified Hand     | Play a Power: random card costs 0 this turn  |
| Ornamental Fan     | Play 3 Attacks: gain 4 Block                 |
| Shuriken           | Play 3 Attacks in a turn: +1 Strength        |
| Sundial            | Every 3 shuffles: +2 Energy                  |
| White Beast Statue | Potions drop from all combats                |

### 7.4 Rare Relics
| Relic              | Effect                                       |
|--------------------|----------------------------------------------|
| Bird-Faced Urn     | Heal 2 HP when playing a Power card          |
| Calipers           | Block decays by 15 instead of ALL            |
| Dead Branch        | When Exhaust a card: add random card to hand |
| Du-Vu Doll         | +1 Strength per Curse in deck                |
| Fossilized Helix   | 1 Buffer at combat start                     |
| Gambling Chip      | Discard any cards, redraw that many (turn 1)  |
| Ginger             | Cannot be Weakened                           |
| Ice Cream           | Energy carries over between turns             |
| Incense Burner     | Every 6 turns: 1 Intangible                  |
| Lizard Tail        | Die? Revive with 50% HP (once)               |
| Magic Flower       | Healing increased by 50%                     |
| Mango              | +14 max HP                                   |
| Old Coin           | +300 gold                                    |
| Pear               | +10 max HP                                   |
| Stone Calendar     | Every 7 turns: 52 damage to ALL              |
| Tungsten Rod       | All HP loss reduced by 1                     |
| Turnip             | Cannot be Frailed                            |

### 7.5 Boss Relics
| Relic              | Effect                                       |
|--------------------|----------------------------------------------|
| Astrolabe          | Upgrade 3 random cards                        |
| Black Star         | Elites drop 2 relics                         |
| Busted Crown       | +1 Energy, 2 fewer card choices              |
| Coffee Dripper     | +1 Energy, cannot rest at rest sites         |
| Cursed Key         | +1 Energy, gain Curse when opening chests    |
| Ectoplasm          | +1 Energy, cannot gain gold                  |
| Empty Cage         | Remove 2 cards from deck                     |
| Fusion Hammer      | +1 Energy, cannot upgrade at rest sites      |
| Holy Water         | +1 Energy, 3 Miracles instead of 1 (Watcher)|
| Mark of Pain       | +1 Energy, 2 Wounds added to deck            |
| Philosopher's Stone| +1 Energy, ALL enemies gain 1 Strength       |
| Runic Dome         | +1 Energy, cannot see enemy intents          |
| Runic Pyramid      | Retain hand at end of turn (no discard)      |
| Sacred Bark        | Potions are twice as effective               |
| Slavers Collar     | +1 Energy, 25% more Elite HP                 |
| Snecko Eye         | +1 Energy, randomize card costs (0-3)        |
| Sozu               | +1 Energy, cannot obtain potions             |
| Tiny House         | +1 potion slot, 50 gold, card, relic, upgrade, +5 HP |
| Velvet Choker      | +1 Energy, max 6 cards per turn              |

## 8. Map Generation

### 8.1 Map Structure
```
Act Map: 15 rows, 7 columns
Each row has 1-4 nodes
Nodes connected by paths (can branch and merge)

Row distribution (from bottom to top):
  Row 1 (bottom): 1 node (starting combat)
  Rows 2-5: Normal encounters, events, shops (1-3 nodes)
  Row 6: Treasure chest (always)
  Rows 7-8: Normal encounters, events (1-3 nodes)
  Row 9: Elite or hard encounter
  Rows 10-13: Mix of encounters, events, shops, rest (1-3 nodes)
  Row 14: Rest site (usually)
  Row 15 (top): Boss
```

### 8.2 Node Types and Distribution
| Node Type | Symbol | Act 1 Freq | Act 2 Freq | Act 3 Freq |
|-----------|--------|-----------|-----------|-----------|
| Monster   | [M]    | ~35%      | ~30%      | ~25%      |
| Elite     | [E]    | ~8%       | ~10%      | ~12%      |
| Rest Site | [R]    | ~12%      | ~12%      | ~15%      |
| Shop      | [S]    | ~5%       | ~8%       | ~8%       |
| Event     | [?]    | ~22%      | ~22%      | ~22%      |
| Treasure  | [T]    | ~3%       | ~3%       | ~3%       |
| Boss      | [B]    | 1 (fixed) | 1 (fixed) | 1 (fixed) |

### 8.3 Example Map
```
                    [BOSS]
                   /      \
               [R]          [?]
              / |              \
          [M] [E]          [M]
           |    \         /   \
         [?]    [M]    [S]   [?]
          |      |      |     |
        [M]    [?]    [M]   [M]
           \    |    /
            [M][R][M]
             | | |
            [T][T][T]
           /   |   \
        [M]  [?]  [M]
         |    |     |
       [M]  [M]  [?]
          \   |   /
           [START]
```

## 9. Shop System

### 9.1 Shop Contents
```
Shop {
  cards: 5 cards (2 Attack, 2 Skill, 1 Power or Colorless)
  relics: 3 relics (1 per rarity tier)
  potions: 3 potions
  card_removal: 1 slot (cost: 50 gold first, +25 each subsequent)
}
```

### 9.2 Pricing
| Item        | Base Price Range |
|-------------|-----------------|
| Common card | 45-55 gold      |
| Uncommon card| 68-82 gold     |
| Rare card   | 135-165 gold    |
| Common relic| 143-157 gold    |
| Uncommon relic| 238-262 gold  |
| Rare relic  | 285-315 gold    |
| Potion      | 48-52 gold      |
| Card removal| 50 (+25 each)   |

### 9.3 Membership Card Relic
- Halves all shop prices (50% discount)

## 10. Event System

### 10.1 Event Structure
```
Event {
  name: String
  description: String
  choices: List<{
    text: String
    outcome: Outcome  // deterministic or random
    requirements: Optional<Condition>
  }>
}
```

### 10.2 Sample Events

**The Cleric (Act 1):**
- Choice 1: Heal 25% max HP (free)
- Choice 2: Cleanse (remove a Curse if you have one)
- Choice 3: Leave

**Big Fish (Act 1):**
- Choice 1: Eat (heal to full, gain a Curse)
- Choice 2: Banana (heal 1/3 max HP)
- Choice 3: Donut (+5 max HP)

**The Library (Act 1-2):**
- Choice 1: Read (choose 1 of 20 cards to add to deck)
- Choice 2: Sleep (heal 33% max HP)

**Vampires (Act 2):**
- Choice 1: Accept (remove all Strikes, gain 5 Bites, lose Burning Blood)
- Choice 2: Refuse (fight 3 enemies)

**Mind Bloom (Act 3):**
- Choice 1: I am War (fight boss from Act 1, get rare relic)
- Choice 2: I am Awake (upgrade all cards, gain Normality Curse)
- Choice 3: I am Rich (+999 gold, gain 2 Curses)

## 11. Potion System

### 11.1 Potion Slots
- Default: 2 potion slots
- Can be increased by relics (+1 from White Beast Statue, etc.)

### 11.2 Potions List
| Potion              | Rarity   | Effect                                  |
|---------------------|----------|-----------------------------------------|
| Block Potion        | Common   | Gain 12 Block                           |
| Attack Potion       | Common   | Deal 5x3 damage to random enemies       |
| Dexterity Potion    | Common   | +2 Dexterity this combat                |
| Energy Potion       | Common   | +2 Energy this turn                     |
| Strength Potion     | Common   | +2 Strength this combat                 |
| Fire Potion         | Common   | Deal 20 damage to target                |
| Explosive Potion    | Common   | Deal 10 damage to ALL                   |
| Fear Potion         | Common   | Apply 3 Vulnerable                      |
| Weak Potion         | Common   | Apply 3 Weak                            |
| Swift Potion        | Common   | Draw 3 cards                            |
| Poison Potion       | Common   | Apply 6 Poison                          |
| Ancient Potion      | Uncommon | Gain 1 Artifact                         |
| Distilled Chaos     | Uncommon | Play top 3 cards of draw pile           |
| Elixir              | Uncommon | Exhaust any cards from hand             |
| Essence of Steel    | Uncommon | Gain 4 Plated Armor                     |
| Gamblers Brew       | Uncommon | Discard hand, draw that many            |
| Liquid Bronze       | Uncommon | Gain 3 Thorns this combat               |
| Regen Potion        | Uncommon | Gain 5 Regeneration                     |
| Smoke Bomb          | Uncommon | Escape non-boss combat (no rewards)     |
| Cultist Potion      | Rare     | Gain 1 Ritual                           |
| Duplication Potion  | Rare     | This turn, next card played plays twice |
| Entropic Brew       | Rare     | Fill all potion slots with random potions|
| Fairy in a Bottle   | Rare     | Auto-use on death: heal 30% HP          |
| Fruit Juice         | Rare     | +5 max HP                               |

## 12. Rest Sites

### 12.1 Options
- **Rest**: Heal 30% of max HP (modified by relics like Dream Catcher)
- **Upgrade**: Upgrade 1 card in your deck (improved stats)
- **Smith** (with specific relics): Additional options
- **Dig** (with Shovel relic): Find a random relic
- **Lift** (with Girya relic): +1 Strength (max 3 times)
- **Recall** (with Peace Pipe relic): Remove a card

## 13. Ascension System

20 difficulty levels that stack:

| Ascension | Modifier                                        |
|-----------|-------------------------------------------------|
| 1         | Elites are harder                               |
| 2         | Normal enemies are harder                       |
| 3         | Lose 1 max HP per Elite combat                  |
| 4         | Normal enemies are harder (again)               |
| 5         | Heal 25% at rest instead of 30%                |
| 6         | Start with Ascender's Bane curse (Unremovable)  |
| 7         | Bosses are harder                               |
| 8         | Normal enemies are harder (again)               |
| 9         | Lose max HP per Boss combat                     |
| 10        | Start with less gold (99 instead of 99)         |
| 11        | Start with less max HP (-5)                     |
| 12        | Elites are harder (again)                       |
| 13        | Bosses are harder (again)                       |
| 14        | Start with less max HP (-5 more)                |
| 15        | Heal 20% at rest instead of 25%                |
| 16        | Fewer potions from combat                       |
| 17        | Normal enemies are harder (again)               |
| 18        | Elites are harder (again)                       |
| 19        | Bosses are harder (again)                       |
| 20        | Start with 1 Curse, double boss at Act 3        |

## 14. User Interface

### 14.1 Combat Screen
```
+------------------------------------------------------------------+
| [Map] [Deck] [Discard] [Exhaust]  [Potion1] [Potion2]           |
+------------------------------------------------------------------+
|                                                                    |
|     [Enemy 1]         [Enemy 2]         [Enemy 3]                |
|     HP: 32/48         HP: 15/30         HP: 44/44               |
|     Intent: ATK 12    Intent: BUFF      Intent: ATK 8x2         |
|                                                                    |
|                                                                    |
|                     [Player]                                       |
|                     HP: 65/80                                     |
|                     Block: 12                                      |
|                     Buffs: [Str+2] [Metallicize]                  |
|                                                                    |
+------------------------------------------------------------------+
| Energy: [2/3]                                                      |
|                                                                    |
|  [Card1]  [Card2]  [Card3]  [Card4]  [Card5]                     |
|  Strike   Defend   Bash     Shrug    Inflame                     |
|  1E-6dmg  1E-5blk  2E-8dmg  1E-8blk  1E-Power                   |
|                                                                    |
| [End Turn]                              Draw: 12  Discard: 3      |
+------------------------------------------------------------------+
```

### 14.2 Map Screen
```
+------------------------------------------------------------------+
| Act 1: Exordium                    HP: 65/80   Gold: 120         |
+------------------------------------------------------------------+
|                                                                    |
|                    [BOSS]                                          |
|                   / |   \                                          |
|                [R] [?]  [M]                                       |
|                |    |  / |                                        |
|              [E]  [M]  [S]                                        |
|               |  / |    |                                         |
|             [M] [?] [M]                                           |
|              |   |   |                                             |
|            [YOU] [T] [M]                                          |
|                                                                    |
+------------------------------------------------------------------+
```

## 15. Card Reward Screen

After combat, choose 1 of 3 cards (or skip):
```
+------------------------------------------------------------------+
| VICTORY!  Gold: +25                                                |
|                                                                    |
|   [Card A]        [Card B]        [Card C]                       |
|   Cleave           Flame Barrier    Spot Weakness                |
|   1E - 8 dmg ALL   2E - 12 blk+   1E - If enemy attacks         |
|   Common            Uncommon        gain 3 Str, Uncommon         |
|                                                                    |
|   [SKIP]                                                          |
+------------------------------------------------------------------+
```

Rarity distribution for card rewards:
| Rarity   | Chance (Normal) | Chance (Modified by relics) |
|----------|----------------|-----------------------------|
| Common   | 60%            | Varies                      |
| Uncommon | 37%            | Varies                      |
| Rare     | 3%             | Increases with bad luck     |

## 16. Gold and Economy

### 16.1 Gold Sources
- Normal combat: 10-20 gold
- Elite combat: 25-35 gold
- Boss combat: 75-100 gold
- Events: Variable
- Gold Idol event: +300 gold (with curse)

### 16.2 Gold Sinks
- Shop cards: 45-165 gold
- Shop relics: 143-315 gold
- Card removal: 50 gold (+25 each time)
- Event costs: Variable

## 17. Save System

- Auto-save after every node on the map
- Save includes: deck, relics, potions, HP, gold, map state
- One save slot per character
- Quitting mid-combat saves combat state
