# Hades -- Complete Game Specification

> A comprehensive specification for faithfully recreating Hades (Supergiant Games, 2020), the roguelike action dungeon crawler. This document covers every system, mechanic, weapon, boon, enemy, and progression system required for a full recreation.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Combat Mechanics](#3-core-combat-mechanics)
4. [All Weapons -- Infernal Arms](#4-all-weapons----infernal-arms)
5. [Boon System -- All Olympians](#5-boon-system----all-olympians)
6. [Duo Boons](#6-duo-boons)
7. [Legendary Boons](#7-legendary-boons)
8. [Room Generation & Biomes](#8-room-generation--biomes)
9. [Enemy Types per Biome](#9-enemy-types-per-biome)
10. [Boss Encounters](#10-boss-encounters)
11. [Meta-Progression Systems](#11-meta-progression-systems)
12. [Mirror of Night](#12-mirror-of-night)
13. [Keepsakes & Companions](#13-keepsakes--companions)
14. [Heat System -- Pact of Punishment](#14-heat-system----pact-of-punishment)
15. [Economy & Currencies](#15-economy--currencies)
16. [Narrative System](#16-narrative-system)
17. [Audio Design](#17-audio-design)
18. [UI Layout](#18-ui-layout)

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Hades |
| Developer | Supergiant Games |
| Release | September 17, 2020 (1.0); Early Access from December 6, 2018 |
| Genre | Roguelike action dungeon crawler |
| Perspective | Isometric 2D (hand-painted art with 3D-lit effects) |
| Input | Keyboard + Mouse or Gamepad (recommended) |
| Platforms | PC (Windows/Mac/Linux), Nintendo Switch, PS4/PS5, Xbox One/Series |
| Engine | Supergiant proprietary engine |
| Protagonist | Zagreus, son of Hades |
| Objective | Escape the Underworld by fighting through four biomes, defeating bosses, and reaching the surface |
| Core Loop | Attempt escape -> die -> return to House of Hades -> spend resources -> attempt again |
| Run Length | ~20-45 minutes per successful escape attempt (~40 chambers) |
| Story Completion | Approximately 10 successful escapes to reach credits; epilogue requires further runs |
| Total Voice Lines | 21,020 lines spanning 305,433 words |

### Win/Lose Conditions

- **Win (run)**: Defeat the final boss (Hades) and reach the surface.
- **Lose (run)**: Zagreus's HP reaches 0 with no Death Defiance charges remaining. Returns to the House of Hades.
- **Permanent death**: Does not exist. All runs contribute to meta-progression and narrative advancement.

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Native resolution | 1920 x 1080 (16:9) |
| Supported resolutions | 1280x720 through 3840x2160 |
| Display mode | Windowed, Borderless Windowed, Fullscreen |
| Frame rate target | 60 FPS (vsync-locked by default) |
| Art style | Hand-painted 2D sprites with dynamic lighting |
| Animation style | Skeletal animation system (Spine-like) |

### Coordinate System

- Isometric projection with camera angle approximately 45 degrees.
- Rooms are self-contained arenas with fixed layouts and procedurally selected encounters.
- No scrolling camera; each room fits within a single screen view.
- Player character and enemies operate on a 2D plane with isometric rendering.

### Game Loop (Per Frame)

```
1. Process input (movement, attack, special, cast, dash, call, interact)
2. Update player state (position, animation, i-frames, cooldowns)
3. Update all enemy AI (behavior trees, attack patterns, pathfinding)
4. Update all projectiles and area effects
5. Process collision detection (hitboxes vs hurtboxes)
6. Apply damage calculations (base * multipliers * status effects)
7. Update status effect timers (Doom, Hangover, Weak, Chill, Exposed, Jolted, Marked)
8. Check death conditions (player and enemies)
9. Check room clear conditions
10. Update particle systems and VFX
11. Render (floor -> walls -> shadows -> entities -> projectiles -> VFX -> UI)
```

### Randomization

| System | Seed Behavior |
|--------|---------------|
| Room layout | Procedurally selected from preset pool per biome |
| Room rewards | Visible on door icon before entry; weighted random |
| Enemy composition | Random within biome-appropriate pool per room |
| Boon offerings | Weighted random based on god keepsake, existing boons, rarity modifiers |
| Shop inventory | Random subset from available pool |
| Hammer (Daedalus) offers | Random 3 from weapon-specific pool; mutually exclusive sets enforced |

---

## 3. Core Combat Mechanics

### Zagreus Base Stats

| Stat | Value |
|------|-------|
| Base HP | 50 (before Mirror of Night Thick Skin upgrades) |
| Base dash charges | 1 (before Greater Reflex upgrade) |
| Base cast ammo (Bloodstones) | 1 (before Infernal Soul upgrades) |
| Base move speed | ~450 units/sec |
| Base dodge chance | 0% |
| God Gauge (Call meter) | 0% start; fills from dealing/taking damage |

### Movement & Dash

| Property | Value |
|----------|-------|
| Dash distance | Fixed (~120 units) |
| Dash duration | ~0.2 seconds |
| Dash cooldown | ~0.3 seconds between dashes |
| I-frames during dash | Active for the first ~0.15 seconds of dash |
| I-frame cancellation | Using attack, special, or cast during dash cancels remaining i-frames |
| Dash charges | 1 base; +1 from Greater Reflex (Mirror); additional from Hermes boons |
| Dash-Strike | Attack input during dash; deals weapon-specific dash-strike damage |

### Attack Types

Every weapon has five core actions:

| Action | Input | Notes |
|--------|-------|-------|
| Attack | Primary button | Multi-hit combo; damage varies per hit in chain |
| Special | Secondary button | Unique per weapon; often AoE or ranged |
| Cast | Cast button | Fires a Bloodstone projectile; base 50 damage |
| Dash | Dash button | Evasive movement with i-frames |
| Call (Aid) | Call button | God-specific power; requires God Gauge |

### Cast / Bloodstone System

| Property | Value |
|----------|-------|
| Base cast damage | 50 |
| Starting Bloodstones | 1 (upgradeable to 3 via Infernal Soul Mirror talent) |
| Lodge duration | Bloodstones lodge in enemies for ~15 seconds before dropping |
| Retrieval methods | Enemy death, timer expiry, Aspect of Poseidon special, Stygian Soul regen |
| Stygian Soul (alt Mirror talent) | Cast does not lodge; instead regenerates over time (base 3 sec per stone) |
| Boiling Blood bonus | +10% Attack/Special damage per rank vs enemies with lodged Bloodstones (max +50%) |

### God Gauge & Calls

| Property | Value |
|----------|-------|
| Gauge fill rate | Gains from dealing and receiving damage |
| Regular Call activation | Uses minimum 25% of gauge for a short burst effect |
| Greater Call activation | Hold Call button; uses 100% of gauge for an amplified effect lasting ~2-5 seconds |
| Greater Call i-frames | Most Greater Calls grant temporary invulnerability |

### Damage Calculation

```
Final Damage = Base Damage
             * (1 + sum of additive % bonuses)
             * (product of multiplicative % bonuses)
             * (backstab bonus if applicable)
             * (critical multiplier if applicable: 3x default)
             * (1 - enemy armor reduction)
```

### Status Effects (Curses)

| Status | Source God | Effect |
|--------|-----------|--------|
| Weak | Aphrodite | Target deals 30% less damage (base) |
| Doom | Ares | After a delay (~1.1 sec), target takes burst damage (base 50) |
| Hangover (Poison) | Dionysus | Stacking damage over time; up to 5 stacks; each tick deals damage (base 4/tick) |
| Chill | Demeter | Slows target by 4% per stack; max 10 stacks = 40% slow; at 10 stacks, shatter for bonus damage |
| Jolted | Zeus | Next time target attacks, they take lightning damage (base 60) and Jolt is consumed |
| Exposed | Artemis (via Marked) | Target takes +50% damage from Attack/Special from behind |
| Deflect | Athena | Reflects projectiles back at enemies for 80% of original damage |
| Knockback | Poseidon | Pushes enemies away; bonus damage when they hit walls |
| Marked | Artemis | Grants bonus critical chance against target |
| Rupture | Poseidon (tier 2) | Enemies take damage when they move |

### Death Defiance

| Variant | Source | Charges | Heal Amount | Notes |
|---------|--------|---------|-------------|-------|
| Death Defiance | Mirror of Night (default) | Up to 3 per run | 50% max HP per trigger | Consumed permanently for the run |
| Stubborn Defiance | Mirror of Night (alternate) | 1 per chamber | 30% max HP per trigger | Regenerates each new chamber |
| Skelly's Lucky Tooth | Keepsake | 1 per run | 50/75/100 HP by rank | Stacks with Death Defiance |
| Athena's Aid (Greater Call) | Boon | N/A | Prevents damage | Brief invulnerability window |

---

## 4. All Weapons -- Infernal Arms

There are six Infernal Arms, each with four Aspects (upgrade paths). Weapons are unlocked with Chthonic Keys. Aspects are upgraded with Titan Blood (1-5 levels per aspect).

### Weapon Unlock Costs

| Weapon | Unlock Cost | Order |
|--------|-------------|-------|
| Stygian Blade (Stygius) | Free (starter) | 1st |
| Eternal Spear (Varatha) | 4 Chthonic Keys | Any |
| Shield of Chaos (Aegis) | 3 Chthonic Keys | Any |
| Heart-Seeking Bow (Coronacht) | 1 Chthonic Key | Any |
| Twin Fists of Malphon (Malphon) | 8 Chthonic Keys | Any |
| Adamant Rail (Exagryph) | 8 Chthonic Keys | Last (requires all others unlocked) |

### 4.1 Stygian Blade (Stygius)

**Description**: A balanced melee sword with a 3-hit attack combo and a wide AoE special (Nova).

#### Base Moveset

| Move | Base Damage | Notes |
|------|-------------|-------|
| Attack (Hit 1) | 20 | Fast horizontal slash |
| Attack (Hit 2) | 25 | Second swing in combo |
| Attack (Hit 3) | 30 | Overhead chop (combo finisher) |
| Dash-Strike | 30 | Lunge attack during dash |
| Special (Nova) | 50 | AoE burst around Zagreus; brief wind-up |
| Cast | 50 | Standard Bloodstone throw |

#### Aspects

| Aspect | Hidden? | Bonus | Scaling (Lv1-5) | Titan Blood Cost |
|--------|---------|-------|------------------|------------------|
| Zagreus | No | +% Attack Speed & Move Speed | +3/6/9/12/15% | 1/1/1/1/1 |
| Nemesis | No | +% Critical Chance on Special for 3 sec | +15/19/22/26/30% | 1/2/3/4/5 |
| Poseidon | No | Special dislodges Cast; +% Cast damage bonus | +10/20/30/40/50% | 2/2/3/4/5 |
| Arthur | Yes | Unique Hallowed moveset; +HP; Special creates damage-reducing aura | Aura: 20/25/30/35/40% reduction; +50 HP | 3/3/3/3/3 |

**Aspect of Arthur Unique Moveset**:

| Move | Base Damage | Notes |
|------|-------------|-------|
| Heavy Slash (Hit 1) | 60 | Slow overhead |
| Heavy Slash (Hit 2) | 80 | Second heavy swing |
| Heavy Slash (Hit 3) | 200 | Massive finisher |
| Dash-Strike | 50 | Slower lunge |
| Hallowed Ground (Special) | 70 | Creates an aura zone reducing damage taken |

**Daedalus Hammer Upgrades (Stygian Blade)**:

| Upgrade | Effect |
|---------|--------|
| Breaching Slash | Attack deals +300% damage to Armor |
| Cruel Thrust | Thrust (Hit 3) deals +200% damage; has extended range |
| Cursed Slash | Attack restores 2 HP per hit; -60% max HP |
| Double Edge | Special hits twice but with 20% reduced damage per hit |
| Flurry Slash | Hold Attack for rapid slashes; each deals 25 base damage |
| Hoarding Slash | Attack deals bonus damage equal to 5% of current Obols |
| Piercing Wave | Attack fires a ranged projectile wave |
| Shadow Slash | Attack deals +200% damage when striking from behind |
| Super Nova | Special hits a wider area and deals +20% damage |
| World Splitter | Charge Attack for a massive overhead dealing 90 base damage (single hit replaces combo) |

---

### 4.2 Eternal Spear (Varatha)

**Description**: A long-range polearm with rapid stabs, a throwable special, and a chargeable spin attack.

#### Base Moveset

| Move | Base Damage | Notes |
|------|-------------|-------|
| Attack (Stab) | 25 | Long-range thrust; can combo into repeated stabs |
| Dash-Strike | 30 | Dash-forward thrust |
| Special (Throw) | 70 | Throws spear forward; returns to Zagreus; hits on both paths |
| Spin Attack (Charged) | 200 (uncharged: 25 per tick) | Hold Attack to charge; release for 360-degree sweep |
| Cast | 50 | Standard Bloodstone throw |

#### Aspects

| Aspect | Hidden? | Bonus | Scaling (Lv1-5) | Titan Blood Cost |
|--------|---------|-------|------------------|------------------|
| Zagreus | No | +% Special Damage, Range & Speed | +10/13/16/19/25% | 1/1/1/1/1 |
| Achilles | No | After Special throw, +% Attack & Cast for next 4 hits (Raging Rush) | +50/75/100/125/150% | 1/2/3/4/5 |
| Hades | No | Spin Attack hits apply Punishing debuff; +% bonus on next hit | +30/60/90/120/150% | 2/2/3/4/5 |
| Guan Yu | Yes | Unique Serpent Slash spin; healing on Special; -% max HP & healing | HP penalty: -70/-65/-60/-55/-50% | 3/3/3/3/3 |

**Guan Yu Unique Moveset**:

| Move | Base Damage | Notes |
|------|-------------|-------|
| Attack (Combo) | 40/60/100 | Three-hit combo with glaive |
| Dash-Strike | 30 | Quick lunge |
| Serpent Slash (Special) | 20/30/50 per tick | Charged whirling projectile that travels forward |
| Frost Fair Blade (Spin) | Channeled area damage | Replaces normal spin |

**Daedalus Hammer Upgrades (Eternal Spear)**:

| Upgrade | Effect |
|---------|--------|
| Breaching Skewer | Special deals +400% damage to Armor |
| Chain Skewer | Special bounces to up to 7 foes, dealing 30% reduced damage per bounce |
| Charged Skewer | Hold Special to charge; release for a power throw dealing up to +200% damage |
| Exploding Launcher | Special explodes on impact for 50 area damage |
| Extending Jab | Attack has extended range and +40% damage |
| Flurry Jab | Hold Attack for rapid jabs at 70% base damage per hit |
| Massive Spin | Spin Attack deals +125% damage and hits a wider area |
| Quick Spin | Spin Attack charges and recovers faster |
| Serrated Point | Attack and Dash-Strike hit 3 times rapidly |
| Vicious Skewer | Special deals +50% damage on outgoing flight; +50% on return |
| Winged Serpent | Spin Attack projectile travels 80% farther (Guan Yu only) |

---

### 4.3 Shield of Chaos (Aegis)

**Description**: A versatile shield that can bash, block, bull rush, and throw. Blocks damage from the front when holding Attack.

#### Base Moveset

| Move | Base Damage | Notes |
|------|-------------|-------|
| Attack (Bash) | 20 | Single forward swing; knocks enemies back |
| Dash-Strike | 25 | Forward bash during dash |
| Bull Rush (Charged Attack) | 50 (max charge) | Hold Attack to block; release to charge forward |
| Special (Shield Throw) | 15 per hit | Bounces between up to 4 enemies before returning |
| Block | 0 (damage negation) | Hold Attack to block all frontal damage |
| Cast | 50 | Standard Bloodstone throw |

#### Aspects

| Aspect | Hidden? | Bonus | Scaling (Lv1-5) | Titan Blood Cost |
|--------|---------|-------|------------------|------------------|
| Zagreus | No | +Attack & Dash-Strike base damage | +3/6/9/12/15 flat damage | 1/1/1/1/1 |
| Chaos | No | After Bull Rush, Special throws additional shields | +1/2/3/4/5 bonus shields | 1/2/3/4/5 |
| Zeus | No | Special becomes Blitz Disc (passes through; lingers at endpoint dealing DPS) | 8/13/19/24/30 damage per 0.3 sec | 2/2/3/4/5 |
| Beowulf | Yes | Dragon Rush replaces Bull Rush; loads Cast into Special; +% damage but take +10% damage | Dragon Rush: +50/+20%/+40%/+60%/+80%/+100% scaling | 3/3/3/3/3 |

**Daedalus Hammer Upgrades (Shield of Chaos)**:

| Upgrade | Effect |
|---------|--------|
| Breaching Rush | Bull Rush deals +400% damage to Armor |
| Charged Shot | Bull Rush fires a ranged projectile dealing 80 damage |
| Charged Flight | Hold Special to charge shield throw; +80% damage at max charge |
| Dashing Wallop | Dash-Strike deals +50% damage in a wider area |
| Dread Flight | Shield bounces to +4 additional enemies |
| Empowering Flight | After Special hits, +80% damage for 3 seconds |
| Explosive Return | Returning Shield deals 50 damage in an area |
| Ferocious Guard | After blocking, +20% damage for 10 seconds |
| Minotaur Rush | Bull Rush deals +500% damage to bosses; wider area |
| Pulverizing Blow | Attack hits twice; second hit deals 30% damage |
| Sudden Rush | Bull Rush charges and recovers much faster |
| Unyielding Defense | Bull Rush gains a power-shot (perfect timing) for +400% damage |

---

### 4.4 Heart-Seeking Bow (Coronacht)

**Description**: A long-range bow with chargeable attacks, a power shot mechanic, and a volley special.

#### Base Moveset

| Move | Base Damage | Notes |
|------|-------------|-------|
| Attack (Uncharged) | 10 | Quick snap shot; minimal damage |
| Attack (Fully Charged) | 70 | Hold and release at full draw |
| Power Shot (perfect release) | 80 | Release at exact moment of full charge flash |
| Dash-Strike | 40 | Quick mid-draw shot during dash |
| Special (Volley) | 10 per arrow (9 arrows) | Fan of arrows in a cone; 90 total at point blank |
| Cast | 50 | Standard Bloodstone throw |

#### Aspects

| Aspect | Hidden? | Bonus | Scaling (Lv1-5) | Titan Blood Cost |
|--------|---------|-------|------------------|------------------|
| Zagreus | No | +% Critical Chance on Attack | +3/6/9/12/15% | 1/1/1/1/1 |
| Chiron | No | Special auto-targets last Attack-hit foe; +max arrows | 4/5/6/7/8 seeking arrows | 1/2/3/4/5 |
| Hera | No | Cast is loaded into next Attack shot; combined damage | Cast Drop Time: 10/8/6.7/6.2/5 sec | 2/2/3/4/5 |
| Rama | Yes | Unique Triple Shot attack; Shared Suffering spreads damage to nearby foes | +30/38/45/53/60% shared damage | 3/3/3/3/3 |

**Aspect of Rama Unique Moveset**:

| Move | Base Damage | Notes |
|------|-------------|-------|
| Triple Shot (Attack) | 45 per arrow (3 arrows) | Fires 3 arrows in a spread |
| Power Shot | 3 x 55 | Triple power shot |
| Dash-Strike | 25 per arrow | Quick triple shot |
| Celestial Sharanga (Special) | 10 per arrow | Applies Shared Suffering debuff |

**Daedalus Hammer Upgrades (Heart-Seeking Bow)**:

| Upgrade | Effect |
|---------|--------|
| Chain Shot | Attack bounces to nearby foe for +15% damage per bounce |
| Charged Volley | Hold Special to charge; +300% damage at max charge |
| Explosive Shot | Attack deals +100% damage in an area; no longer pierces |
| Flurry Shot | Hold Attack for rapid fire; each arrow deals 40% base damage |
| Perfect Shot | Power Shot deals +150% bonus damage |
| Point-Blank Shot | Attack deals +150% damage at close range |
| Piercing Volley | Special pierces through enemies |
| Relentless Volley | Special fires +4 additional arrows |
| Sniper Shot | Attack deals +200% damage at extreme range |
| Triple Shot | Attack fires 3 arrows in a spread; -30% damage per arrow |
| Twin Shot | Attack fires 2 arrows side by side; -15% damage per arrow |

---

### 4.5 Twin Fists of Malphon (Malphon)

**Description**: Extremely fast close-range gauntlets with a 5-hit combo and an uppercut special.

#### Base Moveset

| Move | Base Damage | Notes |
|------|-------------|-------|
| Attack (Hit 1-4) | 15 each | Rapid left-right punches |
| Attack (Hit 5) | 25 | Combo finisher |
| Dash-Strike | 20 | Lunging punch |
| Special (Rising Cutter/Uppercut) | 30 x 2 hits | Hits twice (60 total); knocks enemies up |
| Dash-Upper (Dash + Special) | 40 | Single heavy uppercut during dash |
| Cast | 50 | Standard Bloodstone throw |

#### Aspects

| Aspect | Hidden? | Bonus | Scaling (Lv1-5) | Titan Blood Cost |
|--------|---------|-------|------------------|------------------|
| Zagreus | No | +% Dodge Chance & Move Speed | +5/7/9/12/15% dodge | 1/1/1/1/1 |
| Talos | No | Special becomes Magnetic Cutter (pulls enemies in); +% Attack/Cast damage after pull | +10/20/30/40/50% bonus | 1/2/3/4/5 |
| Demeter | No | After 12 strikes, Special creates Grasping Vortex (lingering AoE); +bonus hits | +1/2/3/4/5 bonus Special hits | 2/2/3/4/5 |
| Gilgamesh | Yes | Unique Claws of Enkidu moveset; Maim debuff (enemies take +25% damage, deal +50% damage; burst on expiry) | Maim Damage: 100/175/250/325/400 | 3/3/3/3/3 |

**Aspect of Gilgamesh Unique Moveset**:

| Move | Base Damage | Notes |
|------|-------------|-------|
| Swipe (Attack) | 60 (per combo hit varies) | Claw slash combo |
| Rising Cutter (Special) | 30 x 2 | Uppercut with Maim application |
| Dash-Strike | 20 | Quick claw lunge |
| Dash-Upper | 40 | Heavy Maim-applying uppercut |
| Maim effect | 100-400 (by aspect level) | Burst damage on expiry after 4 seconds |

**Daedalus Hammer Upgrades (Twin Fists)**:

| Upgrade | Effect |
|---------|--------|
| Breaching Cross | Special deals +400% damage to Armor |
| Colossus Knuckle | Hold Attack for a slow charged punch dealing 80 base damage |
| Concentrated Knuckle | Attack combo deals +5 damage per successive hit |
| Draining Cutter | Special restores 2% max HP per hit |
| Flying Cutter | Hold Special to fly forward, hitting repeatedly |
| Heavy Knuckle | Attack deals +40% damage; dash-strike removed |
| Long Knuckle | Attack range increased by +40% |
| Kinetic Launcher | Special deals +60% damage; flings enemies away |
| Rolling Knuckle | Dash-Strike hits twice; second hit deals +30% damage |
| Rush Kick | Special is replaced by a forward rush-kick dealing 40 damage |

---

### 4.6 Adamant Rail (Exagryph)

**Description**: A ranged automatic weapon (gun) with a reloading magazine and a lobbed grenade special. The only weapon with an ammunition and reload system.

#### Base Moveset

| Move | Base Damage | Notes |
|------|-------------|-------|
| Attack (per shot) | 10 | Rapid fire; fires continuously while held |
| Magazine size | 12 rounds | Must reload when empty (manual or auto) |
| Reload time | ~1 second | Manual reload or auto-reload on empty |
| Dash-Strike | 10 (single shot) | Fires one shot while dashing |
| Special (Bombard) | 60 | Lobs a grenade at cursor position; area damage after brief delay |
| Cast | 50 | Standard Bloodstone throw |

#### Aspects

| Aspect | Hidden? | Bonus | Scaling (Lv1-5) | Titan Blood Cost |
|--------|---------|-------|------------------|------------------|
| Zagreus | No | +Magazine Capacity | +4/5/7/9/12 extra rounds | 1/1/1/1/1 |
| Eris | No | After absorbing own Special blast, +% damage for 4 sec | +15/30/45/60/75% damage | 1/2/3/4/5 |
| Hestia | No | After manual reload, next shot is Empowered | Empowered Shot: 50/75/100/125/150 bonus damage | 2/2/3/4/5 |
| Lucifer | Yes | Unique Igneus Eden moveset; fires beam; Special launches Hellfire orbs | Hellfire Blast: 50/63/75/88/100 damage | 3/3/3/3/3 |

**Aspect of Lucifer Unique Moveset**:

| Move | Base Damage | Notes |
|------|-------------|-------|
| Beam (Attack) | 10 per tick (continuous) | Laser beam; no magazine/reload |
| Hellfire Orbs (Special) | 50-100 (by level) | 3 slow-moving orbs that absorb damage and detonate |
| Dash-Strike | 10 | Quick beam pulse |
| Detonation (triggered) | Absorbed damage + base | Orbs explode dealing accumulated damage |

**Daedalus Hammer Upgrades (Adamant Rail)**:

| Upgrade | Effect |
|---------|--------|
| Delta Chamber | Attack fires a spread of 3 shots; +1 ammo consumed per shot |
| Cluster Bomb | Special fires 5 smaller grenades for +40% total area |
| Explosive Fire | Attack hits deal damage in an area; +50% base; -6 magazine capacity |
| Flurry Fire | Attack fires +50% faster but -25% damage per shot |
| Hazard Bomb | Special deals +300% damage; also damages Zagreus in the blast |
| Inescapable Blast | Special becomes homing; slower but tracks enemies |
| Piercing Fire | Attack pierces enemies, hitting those behind |
| Ricochet Fire | Attack bounces off walls and enemies once |
| Rocket Bomb | Special becomes a rocket, dealing 80 damage on impact; no blast delay |
| Spread Fire | Attack becomes a short-range shotgun; 3 pellets for +40% total at close range |
| Targeting System | Attack and Special automatically target nearest foe; +10% critical chance |
| Triple Bomb | Special can be used 3 times before entering cooldown |

---

## 5. Boon System -- All Olympians

Boons are temporary power-ups granted by Olympian gods during a run. Each god has a thematic focus and unique status effect. Boons come in four rarity tiers affecting their numeric values.

### Rarity Tiers

| Rarity | Color | Damage/Effect Multiplier |
|--------|-------|--------------------------|
| Common | Blue | 1.0x (base value) |
| Rare | Green | ~1.25-1.3x |
| Epic | Purple | ~1.5-1.8x |
| Heroic | Red | ~2.0-2.5x |

### Boon Slots

Each god can offer boons for these slots (one boon per slot maximum; new boons in same slot replace old):

| Slot | Description |
|------|-------------|
| Attack | Modifies primary Attack action |
| Special | Modifies Special action |
| Cast | Modifies Cast (Bloodstone) |
| Dash | Modifies Dash action |
| Call (Aid) | Grants a Call ability (requires God Gauge) |
| Passive (Tier 2+) | Enhances or synergizes with existing boons |

### 5.1 Zeus -- God of Thunder

**Theme**: Chain lightning, lightning bolts, Jolted status.

| Boon | Slot | Effect (Common) |
|------|------|-----------------|
| Lightning Strike | Attack | Attack emits chain-lightning dealing 10 bonus lightning damage |
| Thunder Flourish | Special | Special causes a lightning bolt to strike nearby foes for 30 damage |
| Electric Shot | Cast | Cast fires chain-lightning dealing 60 damage |
| Thunder Dash | Dash | Dash creates a lightning bolt dealing 10 damage to nearby foes |
| Zeus' Aid | Call | Repeatedly strike nearby foes with lightning for 50 damage per bolt |
| Heaven's Vengeance | Revenge | When hit, lightning strikes nearby foes for 80 damage |
| Lightning Reflexes | Passive | After dashing, lightning strikes nearby foes for 20 damage |
| Storm Lightning | Passive | Chain-lightning bounces +2 additional times |
| High Voltage | Passive | Lightning bolt area increased by +60% |
| Double Strike | Passive | Lightning bolts have a 25% chance to strike twice |
| Static Discharge | Passive | Jolt effect deals 60 damage when triggered |
| Clouded Judgement | Passive | God Gauge charges +10% faster |
| Billowing Strength | Passive | After using Call, deal +20% damage for 15 seconds |
| **Splitting Bolt** | **Legendary** | **All lightning effects create a secondary bolt dealing 40 damage** |

---

### 5.2 Athena -- Goddess of Wisdom

**Theme**: Deflect, damage reduction, invulnerability.

| Boon | Slot | Effect (Common) |
|------|------|-----------------|
| Divine Strike | Attack | Attack deflects and deals +40% damage |
| Divine Flourish | Special | Special deflects and deals +60% damage |
| Phalanx Shot | Cast | Cast deflects and deals +10% damage |
| Divine Dash | Dash | Dash deflects attacks in a wider area |
| Athena's Aid | Call | Become invulnerable for 1.5 seconds (Greater Call: 6 seconds) |
| Bronze Skin | Passive | Resist +5% damage from all sources |
| Holy Shield | Passive | After deflecting, briefly gain +15% damage |
| Sure Footing | Passive | Resist +25% damage from traps |
| Brilliant Riposte | Passive | Deflected projectiles deal +80% damage |
| Blinding Flash | Passive | Deflect renders enemies Exposed (+50% backstab damage) |
| Proud Bearing | Passive | God Gauge starts at 20% full at start of each encounter |
| **Divine Protection** | **Legendary** | **Barrier absorbs one hit every 20 seconds** |

---

### 5.3 Ares -- God of War

**Theme**: Doom status, Blade Rifts (lingering AoE), damage over time.

| Boon | Slot | Effect (Common) |
|------|------|-----------------|
| Curse of Agony | Attack | Attack inflicts Doom for 50 damage after 1.1 seconds |
| Curse of Pain | Special | Special inflicts Doom for 60 damage |
| Slicing Shot | Cast | Cast creates a Blade Rift dealing 20 damage per 0.1 sec |
| Blade Dash | Dash | Dash creates a Blade Rift lasting 0.7 seconds |
| Ares' Aid | Call | Create a large Blade Rift on Zagreus dealing 30 damage per 0.1 sec (Greater: larger, longer) |
| Urge to Kill | Passive | +20% Attack Speed and Move Speed for 2 seconds after slaying a foe |
| Blood Frenzy | Passive | After slaying a foe, gain +0.2% damage permanently per kill (this run) |
| Battle Rage | Passive | After slaying a foe, next Attack/Special deals +100% damage |
| Black Metal | Passive | Blade Rift hits deal +20% damage to Armor |
| Engulfing Vortex | Passive | Blade Rifts are +20% larger and pull enemies in |
| Dire Misfortune | Passive | Doom deals +10% damage per application on same target |
| Impending Doom | Passive | Doom delay +0.5 sec; Doom deals +60% damage |
| **Vicious Cycle** | **Legendary** | **Blade Rift damage increases by +1 per consecutive hit** |

---

### 5.4 Aphrodite -- Goddess of Love

**Theme**: Weak status (enemies deal less damage), high base damage bonuses, survivability.

| Boon | Slot | Effect (Common) |
|------|------|-----------------|
| Heartbreak Strike | Attack | Attack deals +50% damage and inflicts Weak |
| Heartbreak Flourish | Special | Special deals +80% damage and inflicts Weak |
| Crush Shot | Cast | Cast deals +50% damage and inflicts Weak |
| Passion Dash | Dash | Dash deals 20 damage to enemies you pass through; inflicts Weak |
| Aphrodite's Aid | Call | Fire a projectile that Charms foes for 5 seconds (Greater: wider, longer) |
| Dying Lament | Revenge | When hit, deal 40 damage to nearby foes |
| Life Affirmation | Passive | Max HP bonuses from Centaur Hearts are +30% more effective |
| Different League | Passive | Resist +10% damage from all sources |
| Empty Inside | Passive | Weak effects last +5 seconds |
| Sweet Surrender | Passive | Weak foes take +10% more damage |
| Broken Resolve | Passive | Weak effect reduces enemy damage by an additional +10% (total -40%) |
| Blown Kiss | Passive | Cast fires faster and deals +20% damage |
| **Unhealthy Fixation** | **Legendary** | **Weak foes have a 15% chance to be Charmed for 4 seconds** |

---

### 5.5 Artemis -- Goddess of the Hunt

**Theme**: Critical hits, bonus damage, tracking projectiles.

| Boon | Slot | Effect (Common) |
|------|------|-----------------|
| Deadly Strike | Attack | Attack deals +20% damage; +15% Critical Chance |
| Deadly Flourish | Special | Special deals +40% damage; +20% Critical Chance |
| True Shot | Cast | Cast fires a homing arrow for 70 damage |
| Hunter Dash | Dash | After dashing, next Attack deals +50% damage |
| Artemis' Aid | Call | Fire a volley of 10 seeking arrows dealing 100 damage each |
| Pressure Points | Passive | All attacks gain +2% Critical Chance |
| Exit Wounds | Passive | Foes take 100 damage when Bloodstones are dislodged from them |
| Clean Kill | Passive | Critical hits deal +15% more damage |
| Hide Breaker | Passive | Critical hits deal +100% damage to Armor |
| Hunter's Mark | Passive | After Critical hit, foe is Marked (next hit is guaranteed Critical) |
| Support Fire | Passive | After Attack or Special, fire an additional arrow for 10 damage |
| Hunter Instinct | Passive | God Gauge gains +3% per Critical hit |
| **Fully Loaded** | **Legendary** | **Gain +2 extra Bloodstones for Cast** |

---

### 5.6 Dionysus -- God of Wine

**Theme**: Hangover (stacking poison DoT), Festive Fog, healing/survivability.

| Boon | Slot | Effect (Common) |
|------|------|-----------------|
| Drunken Strike | Attack | Attack inflicts Hangover (4 damage per 0.5 sec; max 5 stacks) |
| Drunken Flourish | Special | Special inflicts Hangover |
| Trippy Shot | Cast | Cast lobs Festive Fog that lingers and deals 100 burst + Hangover |
| Drunken Dash | Dash | Dash inflicts Hangover to nearby foes |
| Dionysus' Aid | Call | Create a large Festive Fog at your location (Greater: enormous area) |
| Premium Vintage | Passive | Gain +20 max HP when you pick up Nectar in a run |
| Strong Drink | Passive | Gain +30% max HP from Fountains; heal to full |
| Positive Outlook | Passive | Take -10% damage when under 40% HP |
| After Party | Passive | After each encounter, heal up to 50% of any damage taken |
| Bad Influence | Passive | Deal +50% damage while 3+ foes are Hangover-afflicted |
| Peer Pressure | Passive | Hangover-afflicted foes spread Hangover to nearby foes |
| Numbing Sensation | Passive | Hangover-afflicted foes are +15% slower |
| High Tolerance | Passive | Hangover stacks +1 additional time (max 6) |
| **Black Out** | **Legendary** | **Hangover-afflicted foes in Festive Fog take 100% more combo damage** |

---

### 5.7 Poseidon -- God of the Sea

**Theme**: Knockback, wall-slam bonus damage, room reward enhancement.

| Boon | Slot | Effect (Common) |
|------|------|-----------------|
| Tempest Strike | Attack | Attack deals +30% damage and knocks foes away |
| Tempest Flourish | Special | Special deals +50% damage and knocks foes away |
| Flood Shot | Cast | Cast knocks foes away and deals +30% damage |
| Tidal Dash | Dash | Dash deals 35 damage to nearby foes and knocks them away |
| Poseidon's Aid | Call | Create a pulling vortex dealing 250 damage per second (Greater: larger) |
| Hydraulic Might | Passive | Attack and Special deal +30% damage at start of encounter (first 10 sec) |
| Ocean's Bounty | Passive | Gems, Darkness, and Obol room rewards are +50% greater |
| Sunken Treasure | Passive | Gain a random assortment of gems, darkness, obol, and max HP |
| Typhoon's Fury | Passive | Knockback effects deal +40 damage to foes slammed into walls |
| Breaking Wave | Passive | Knockback effects create a secondary splash dealing 100 damage |
| Razor Shoals | Passive | Enemies knocked back take Rupture (damage while moving) |
| Boiling Point | Passive | God Gauge charges +20% faster after taking damage |
| Rip Current | Passive | Call pulls foes closer before activating |
| **Second Wave** | **Legendary** | **Knockback effects shove foes a second time** |
| **Huge Catch** | **Legendary** | **Fishing spawn chance increased by 20%** |

---

### 5.8 Demeter -- Goddess of Seasons

**Theme**: Chill status (stacking slow), Decay burst, crystal beams.

| Boon | Slot | Effect (Common) |
|------|------|-----------------|
| Frost Strike | Attack | Attack deals +40% damage and inflicts Chill |
| Frost Flourish | Special | Special deals +60% damage and inflicts Chill |
| Crystal Beam | Cast | Cast creates a beam that fires continuously for 8 damage per hit; applies Chill |
| Mistral Dash | Dash | Dash inflicts Chill on nearby foes |
| Demeter's Aid | Call | Create a winter vortex around Zagreus that deals 10 damage per hit and Chill (Greater: larger, longer) |
| Snow Burst | Passive | When Cast drops from foes, deal 40 damage in an area |
| Ravenous Will | Passive | After not using Attack/Special/Cast for 2 sec, gain +10% damage and speed |
| Nourished Soul | Passive | Any healing effects are +30% more effective |
| Rare Crop | Passive | Random boons gain +1 rarity level |
| Glacial Glare | Passive | Cast effects last +40% longer; Crystal Beam is wider |
| Arctic Blast | Passive | Chill-affected foes take 80 damage when fully Chilled (10 stacks) |
| Killing Freeze | Passive | Chill-affected foes are +10% slower; fully Chilled foes are +30% slower |
| **Winter Harvest** | **Legendary** | **Chill-afflicted foes at 10% HP shatter for 50 area damage** |

---

### 5.9 Hermes -- God of Swiftness

**Theme**: Speed, evasion, utility. Hermes does not offer Attack/Special/Cast boons. His boons enhance existing capabilities.

| Boon | Slot | Effect (Common) |
|------|------|-----------------|
| Quick Reload | Passive | Bloodstones dislodge +50% faster |
| Greater Haste | Passive | +20% Move Speed |
| Hyper Sprint | Passive | After dashing, gain +100% Move Speed for 0.5 seconds |
| Greatest Reflex | Passive | Gain +1 Dash charge |
| Second Wind | Passive | After using all Dash charges, gain +30% Move Speed for 3 seconds |
| Swift Strike | Passive | Attack is +10% faster |
| Swift Flourish | Passive | Special is +10% faster |
| Flurry Cast | Passive | +50% Cast speed (reduced delay between casts) |
| Quick Favor | Passive | God Gauge fills +50% faster |
| Auto Reload | Passive | Bloodstones regenerate +1 per 3 seconds (Stygian Soul equivalent) |
| Rush Delivery | Passive | Deal +10% damage while Move Speed is boosted |
| Side Hustle | Passive | Gain +10 Obols per chamber |
| **Greater Recall** | **Legendary** | **Cast Bloodstones automatically return to you** |
| **Bad News** | **Legendary** | **First Cast against each foe deals +50% damage** |

### 5.10 Chaos -- Primordial Entity

**Theme**: High-risk/high-reward. Chaos boons impose a curse (penalty) for a set number of encounters, then grant a permanent blessing. Accessed through Chaos Gates (cracks in the floor that cost HP to enter).

| Curse (Penalty) | Duration | Effect |
|-----------------|----------|--------|
| Addled | 3-4 encounters | -70% Cast damage |
| Atrophied | 3-4 encounters | -40% Attack damage |
| Caustic | 3-4 encounters | Take +50% damage from traps |
| Engulfed | 3-4 encounters | Take 25 damage per second in magma |
| Flayed | 3-4 encounters | -50% max HP |
| Halting | 3-4 encounters | -30% Dash distance |
| Maimed | 3-4 encounters | -40% Special damage |
| Pained | 3-4 encounters | Take 20 damage per room |
| Slippery | 3-4 encounters | -30% Dodge chance |
| Slothful | 3-4 encounters | -40% Attack speed |

| Blessing (Reward) | Effect |
|-------------------|--------|
| Affluence | +50% Obol from rooms |
| Ambush | +40% backstab damage |
| Assault | +20% Attack damage |
| Eclipse | +30% to get Gemstone/Darkness rewards |
| Favor | +10% to get Boon/Hammer rewards |
| Flourish | +30% Special damage |
| Grasp | +2% rarity chance for boons |
| Lunge | +50% Dash-Strike damage |
| Shot | +30% Cast damage |
| Soul | +1 Bloodstone |
| Strike | +25% Attack damage |
| **Defiance** | **Legendary: +1 Death Defiance** |

---

## 6. Duo Boons

Duo Boons combine the powers of two Olympians. There are 28 total Duo Boons. They require at least one qualifying boon from each of the two gods involved. Neither Hermes nor Chaos offers Duo Boons.

| # | Duo Boon | Gods | Effect |
|---|----------|------|--------|
| 1 | Curse of Longing | Aphrodite + Ares | Doom effects continuously damage Weak foes |
| 2 | Heart Rend | Aphrodite + Artemis | Critical hits deal +150% bonus damage to Weak foes |
| 3 | Parting Shot | Aphrodite + Athena | Cast gains backstab bonus (+35% damage from behind) |
| 4 | Low Tolerance | Aphrodite + Dionysus | Hangover stacks deal +3 additional damage to Weak foes |
| 5 | Cold Embrace | Aphrodite + Demeter | Crystal Beam fires at Zagreus with +30% bonus damage |
| 6 | Sweet Nectar | Aphrodite + Poseidon | Poms of Power are +1 level more effective |
| 7 | Smoldering Air | Aphrodite + Zeus | God Gauge auto-charges, but max is capped at 25% |
| 8 | Merciful End | Ares + Athena | Deflect triggers immediate Doom detonation |
| 9 | Hunting Blades | Ares + Artemis | Blade Rift seeks nearest foe and moves faster |
| 10 | Curse of Nausea | Ares + Dionysus | Hangover damage ticks 3x faster |
| 11 | Freezing Vortex | Ares + Demeter | Blade Rift inflicts Chill; smaller but lingering |
| 12 | Curse of Drowning | Ares + Poseidon | Attack creates a damaging pulse around Zagreus |
| 13 | Vengeful Mood | Ares + Zeus | Revenge effects trigger periodically without taking damage |
| 14 | Deadly Reversal | Artemis + Athena | After deflecting, gain +20% Critical Chance for 2 seconds |
| 15 | Splitting Headache | Artemis + Dionysus | Hangover-afflicted foes take +1.5% Critical Chance per Hangover stack |
| 16 | Crystal Clarity | Artemis + Demeter | Crystal Beam tracks foes and deals +10% damage |
| 17 | Mirage Shot | Artemis + Poseidon | Cast fires a second projectile dealing 30% damage |
| 18 | Lightning Rod | Artemis + Zeus | Lodged Bloodstones periodically strike foes with lightning for 70 damage |
| 19 | Calculated Risk | Athena + Dionysus | Foes' ranged projectiles move slower |
| 20 | Stubborn Roots | Athena + Demeter | When at 0 Death Defiance, slowly regenerate HP (1 HP per 0.8 sec) |
| 21 | Unshakable Mettle | Athena + Poseidon | Cannot be stunned; resist boss slam damage |
| 22 | Lightning Phalanx | Athena + Zeus | Phalanx Shot bounces between enemies like chain lightning |
| 23 | Ice Wine | Demeter + Dionysus | Festive Fog becomes freezing (Chill + Hangover) |
| 24 | Blizzard Shot | Demeter + Poseidon | Cast moves slowly, piercing foes and firing shards |
| 25 | Cold Fusion | Demeter + Zeus | Jolt effects do not expire when foes attack |
| 26 | Exclusive Access | Dionysus + Poseidon | All boons found have improved rarity |
| 27 | Scintillating Feast | Dionysus + Zeus | Festive Fog deals periodic lightning damage |
| 28 | Sea Storm | Poseidon + Zeus | Knockback effects also strike foes with lightning |

---

## 7. Legendary Boons

Each god (except Chaos, who has one) offers one Legendary Boon (Poseidon and Hermes each offer two). Legendary Boons require specific prerequisite boons from that god and are classified as Tier 3.

| # | Legendary Boon | God | Effect | Key Prerequisites |
|---|---------------|-----|--------|-------------------|
| 1 | Splitting Bolt | Zeus | All lightning creates secondary bolt for 40 damage | Storm Lightning + (Double Strike or High Voltage) |
| 2 | Divine Protection | Athena | Barrier absorbs 1 hit; 20-sec recharge | 2 Athena strike/defense boons |
| 3 | Vicious Cycle | Ares | Blade Rift damage +1 per consecutive hit | Ares Blade Rift boon + (Black Metal or Engulfing Vortex) |
| 4 | Unhealthy Fixation | Aphrodite | Weak foes have 15% Charm chance for 4 sec | Aphrodite strike/dash boon + (Empty Inside or Sweet Surrender) |
| 5 | Fully Loaded | Artemis | Gain +2 extra Bloodstones | 2 qualifying Artemis boons |
| 6 | Black Out | Dionysus | Hangover foes in Festive Fog take 100% more combo damage | Trippy Shot + (Peer Pressure or High Tolerance) |
| 7 | Second Wave | Poseidon | Knockback shoves foes a second time | Poseidon knockback boon + (Typhoon's Fury or Breaking Wave) |
| 8 | Huge Catch | Poseidon | +20% Fishing Point spawn chance | Ocean's Bounty + Sunken Treasure |
| 9 | Winter Harvest | Demeter | Chill foes at 10% HP shatter for 50 AoE damage | Demeter strike/dash boon + (Killing Freeze or Arctic Blast) |
| 10 | Greater Recall | Hermes | Bloodstones auto-return to Zagreus | Quick Reload or Flurry Cast |
| 11 | Bad News | Hermes | First Cast against each foe deals +50% damage | Any 2 Hermes boons |
| 12 | Defiance | Chaos | Gain +1 Death Defiance for this run | Any Chaos blessing |

---

## 8. Room Generation & Biomes

### Biome Structure

A complete run passes through 4 biomes in fixed order. Each biome ends with a boss encounter.

| Biome | Name | Chambers (Excl. Boss) | Boss Chamber | Total |
|-------|------|-----------------------|--------------|-------|
| 1 | Tartarus | 13-14 | 1 (Fury) | 14-15 |
| 2 | Asphodel | 9-10 | 1 (Hydra) | 10-11 |
| 3 | Elysium | 10-11 | 1 (Theseus & Asterius) | 11-12 |
| 4 | Temple of Styx | 5 tunnels (variable rooms each) | 1 (Hades) | Variable (~8-15) |
| **Total** | | | | **~40-53 chambers** |

### Room Reward Types

Room rewards are indicated by symbols on the exit door before entering.

| Symbol | Reward | Laurel Color | Description |
|--------|--------|--------------|-------------|
| Skull (Darkness) | Darkness | Blue | Persistent currency for Mirror upgrades |
| Gemstone | Gemstones | Blue | Persistent currency for House Contractor |
| Key | Chthonic Key | Blue | Persistent currency for weapon/mirror unlocks |
| Nectar bottle | Nectar | Blue | Gift currency for NPC relationships |
| Coin bag | Obols (Gold) | Gold | Run-only currency for shops |
| God symbol | Boon | Gold | Olympian god boon selection |
| Anvil (Hammer) | Daedalus Hammer | Gold | Weapon upgrade (max 2 per run) |
| Heart | Centaur Heart | Gold | +25 max HP for this run |
| Arrow up | Pom of Power | Gold | +1 level to a random existing boon |
| Shop icon | Charon's Shop | N/A | Purchase boons, items, upgrades with Obols |
| Trident (miniboss) | Miniboss | Skull marker | Harder encounter; enhanced reward |
| Dual gods | Trial of the Gods | Skull marker | Choose between 2 gods; spurned god attacks |
| Skull door | Erebus Gate | Skull marker | Perfect challenge room (no damage allowed) |
| Chaos rift | Chaos Gate | N/A | Crack in floor; costs 16 HP to enter |

### Special Room Types

| Room Type | Description |
|-----------|-------------|
| Fountain Chamber | Heal for ~40% HP; offers Keepsake swap between biomes |
| Charon's Shop | Buy items/boons with Obols; stock varies |
| Well of Charon | Purple well with temporary buffs purchasable with Obols |
| Pool of Purging | Sell boons for Obols (value = boon rarity) |
| Infernal Trove | Timed enemy wave; rewards scale with completion speed |
| Sisyphus Encounter | Friendly NPC; choose Darkness, HP heal, or Obols |
| Eurydice Encounter | Friendly NPC; choose 1 of 3 food buffs (upgrade boon rarity) |
| Patroclus Encounter | Friendly NPC; choose Kiss of Styx (DD refill), HyperSprint, or PatroclusKeepsake buff |
| Thanatos Encounter | Compete to kill more enemies; win = Centaur Heart |
| Survival Room | Enemies spawn in waves; survive all waves to clear |
| Fishing Point | Sparkle on specific platforms; can fish if you have rod |

### Temple of Styx Structure

The Temple of Styx is unique: it has a central hub with 5 tunnel entrances. Each tunnel contains 3-5 small rooms. One tunnel (random) contains the Satyr Sack needed to feed Cerberus and access the final boss. The other tunnels contain rewards.

---

## 9. Enemy Types per Biome

### 9.1 Tartarus Enemies

| Enemy | HP (Base) | Behavior | Elite? |
|-------|-----------|----------|--------|
| Wretched Thug | 120 | Slow melee; overhead slam | Can be Elite |
| Wretched Lout | 100 | Ranged stone throw | Can be Elite |
| Wretched Witch | 150 | Teleporting caster; fires homing orbs | Can be Elite |
| Wretched Pest | 60 | Small; fast dash attacks | No |
| Wretched Sneak | 80 | Invisible until close; backstab attack | No |
| Numbskull | 50 | Basic melee charger | Can be Elite |
| Skullomat | 30 | Stationary turret; fires projectiles | No |
| Brimstone | 80 | Stationary; fires a sweeping beam | No |
| Bloodless | 100 | Ranged; throws bones | Can be Elite |
| Inferno-Bomber | 90 | Lobs explosive projectiles | No |
| Doomstone | 200 | Large floating stone; area slam | Can be Elite |
| Wringer | 150 | Grapples and squeezes Zagreus | Can be Elite |

**Minibosses**: Doomstone (armored variant with enhanced attacks), Wretched Sneak (armored).

---

### 9.2 Asphodel Enemies

| Enemy | HP (Base) | Behavior | Elite? |
|-------|-----------|----------|--------|
| Bloodless | 130 | Ranged bone thrower (upgraded from Tartarus) | Can be Elite |
| Bone-Raker | 150 | Skeleton with sweeping melee attacks | Can be Elite |
| Inferno-Bomber | 120 | Explosive lobber (upgraded) | Can be Elite |
| Wave Maker | 160 | Creates damaging wave patterns on magma | Can be Elite |
| Burn-Flinger | 140 | Throws burning projectiles | Can be Elite |
| Slam-Dancer | 180 | Charges and performs AoE slam | Can be Elite |
| Skull-Crusher | 250 | Large skeleton; powerful ground pound | Miniboss |
| Gorgon | 100 | Fires petrifying beam; floats | Can be Elite |
| Megagorgon | 500 | Large Gorgon; wider beam; summons small Gorgons | Miniboss |
| Spreader | 400 | Splits into smaller enemies when killed | Miniboss |
| Voidstone | 200 | Stationary shield generator; makes nearby enemies invulnerable | No |
| Dracon | 200 | Serpentine enemy; lunges from magma | Can be Elite |

**Environmental Hazard**: Magma (lava) covers most floor area; standing in it deals ~10 damage per tick.

---

### 9.3 Elysium Enemies

| Enemy | HP (Base) | Behavior | Elite? |
|-------|-----------|----------|--------|
| Brightsword | 200 | Armored swordsman; quick slash combos | Can be Elite |
| Longspear | 200 | Armored spearman; long-range thrusts | Can be Elite |
| Strongbow | 180 | Armored archer; fires tracking arrows | Can be Elite |
| Greatshield | 250 | Armored shieldbearer; blocks frontal attacks; charges | Can be Elite |
| Exalted (any above) | +Armor | All Elysium warriors have pink armor that must be broken first | Always Armored |
| Soul Catcher | 150 | Butterfly-like; revives fallen Exalted warriors | Priority target |
| Flame Wheel | 100 | Rolling fire wheel; charges in lines | No |
| Splitter | 100 (x3) | Splits into smaller units when killed; 3 stages | No |
| Nemean Chariot | 300 | Charges across arena; armored front | Can be Elite |

**Key Mechanic**: Exalted warriors have Armor (pink health bar above regular HP). Armor must be depleted before HP damage is dealt. Soul Catchers resurrect fallen Exalted if not killed quickly.

**Miniboss**: Asterius (solo encounter before boss, ~3000 HP mini-boss version).

---

### 9.4 Temple of Styx Enemies

| Enemy | HP (Base) | Behavior | Elite? |
|-------|-----------|----------|--------|
| Crawler | 60 | Tiny fast-moving vermin; swarm attacks | No |
| Gigantic Vermin | 200 | Large rat; charges and bites | Can be Elite |
| Bother | 80 | Flying pest; swoops to attack | No |
| Satyr | 250 | Primary enemy; fires rapid projectile bursts; applies poison | Can be Elite |
| Satyr Cultist | 300 | Enhanced Satyr; stronger poison; faster attacks | Can be Elite |
| Snakestone | 200 | Stone snake; lunges and coils | Can be Elite |
| Tiny Vermin | 30 | Swarm enemy; appears in groups of 5-8 | No |

**Environmental Note**: Satyr poison is one of the most dangerous status effects; it deals continuous damage and can stack.

---

## 10. Boss Encounters

### 10.1 The Fury Sisters (Tartarus Boss -- Chamber 14/15)

One of three Furies is randomly selected each run (after all three are unlocked narratively).

#### Megaera (Default Fury)

| Phase | HP Threshold | Behavior |
|-------|-------------|----------|
| Phase 1 | 100%-75% | Dash attacks, whip lash (line AoE), basic melee |
| Phase 2 | 75%-50% | Adds: Fire AoE circles, Shadow Blast projectiles, summons Wretched Thugs/Witches |
| Phase 3 | 50%-25% | Doubles summons; becomes temporarily invulnerable during summon; faster attacks |
| Phase 4 | 25%-0% | Maximum aggression; all abilities faster; continuous summons |

**Total HP**: ~3,860 (scales with Heat)

#### Alecto (Alternate Fury)

| Property | Details |
|----------|---------|
| Unique mechanic | Rage meter builds; when full, enters enraged state with faster/stronger attacks |
| Attacks | Blade combos, diving charge, ground slam AoE, thrown blades |
| Summons | Numbskulls and Wretched Louts |

#### Tisiphone (Alternate Fury)

| Property | Details |
|----------|---------|
| Unique mechanic | Arena periodically shrinks (green fog closes in) |
| Attacks | Whip strike, green circle AoE, teleport-slam |
| Summons | Minimal; focuses on solo damage |
| Vocabulary | Only says "Murderer" (narrative element) |

---

### 10.2 Lernaean Bone Hydra (Asphodel Boss -- Chamber ~24)

| Phase | HP Threshold | Behavior |
|-------|-------------|----------|
| Phase 1 | 100%-67% | Lunges at player, slams ground, fires projectile spreads |
| Phase 2 | 67%-33% | Submerges; summons 3 smaller Hydra heads at arena edges; each head has unique attack pattern |
| Phase 3 | 33%-0% | Summons both head waves simultaneously; main head attacks faster; magma hazards increase |

**Total HP**: ~5,500 (main head); ~800 each (sub-heads)

**Sub-Head Types**:

| Type | Behavior |
|------|----------|
| Slam Head | Slams ground creating shockwave |
| Fire Head | Breathes a sweeping fire beam |
| Projectile Head | Fires tracking projectiles |

**Arena Hazard**: Magma pools at arena edges deal periodic damage.

---

### 10.3 Theseus & Asterius (Elysium Boss -- Chamber ~35)

This is a dual boss fight. Both must be defeated.

#### Asterius (The Minotaur)

| Property | Value |
|----------|-------|
| HP | ~6,800 |
| Attacks | Double-axe swing, arena-length charge, jumping slam |
| Charge stun | If Asterius hits a wall/pillar during charge, he is stunned for ~3 seconds |
| Priority | Recommended to defeat first |
| Enrage | Below 25% HP: faster attacks, shorter cooldowns |

#### Theseus

| Property | Value |
|----------|-------|
| HP | ~7,200 |
| Shield | Blocks all frontal attacks; must be hit from behind or sides |
| Attacks | Spear throw (pink reticle warning), shield bash at close range |
| Phase 2 (50% HP) | Calls upon an Olympian God for aid; god rains AoE attacks across arena |
| God Aid selection | Calls a god who has NOT given Zagreus any boons this run (never Hermes) |
| Chariot | Rides chariot around arena edges in Phase 2 |

**Arena**: Circular coliseum with 4 pillars (breakable; provide cover from Theseus's spear).

---

### 10.4 Hades (Final Boss -- After Temple of Styx)

The fight takes place on the surface, in a snowy field before the house.

#### Phase 1

| Property | Value |
|----------|-------|
| HP | ~5,700 |
| Weapon | Bident (two-pronged spear) |
| Attacks | Wide sweeping strikes, spear thrust combo, spinning AoE, skull-cast projectiles |
| Skull Cast | Fires 2-4 seeking skulls that deal heavy damage |
| Laser Beam | Channels a red beam across the arena |
| Summon | Periodically summons Wretched shades |

#### Phase 2 (After depleting Phase 1 HP)

| Property | Value |
|----------|-------|
| HP | ~7,200 (second health bar) |
| New Attacks | Boiling Blood (green AoE pools), faster skull volleys, dash-spin combo |
| Green Vases | Arena has vases that heal Hades if not destroyed |
| Invulnerability | Brief invulnerability during transition |
| Increased Speed | All attacks ~30% faster |
| Desperation | Below 25%: maximum aggression, near-constant skull barrage |

**Total Combined HP**: ~12,900

**Special Mechanic**: Hades is immune to Call effects during certain attack animations.

**Death Defiance Interaction**: If Zagreus has Death Defiance, Hades will acknowledge it in dialogue. If Zagreus dies, the run ends (return to House); there is no checkpoint.

---

### Extreme Measures Boss Variants (Pact of Punishment)

| EM Level | Boss | Changes |
|----------|------|---------|
| EM1 | Megaera | Sisters fight alongside Megaera (2v1 or 3v1) |
| EM2 | Bone Hydra | Starts with sub-heads already active; lava geysers |
| EM3 | Theseus & Asterius | Chariot arena; Theseus rides chariot from start; arena is smaller |
| EM4 | Hades | Fight takes place in Zagreus's bedroom; Hades has new attacks, Cerberus assists Hades, Persephone's garden hazards |

---

## 11. Meta-Progression Systems

### House of Hades (Hub)

Between runs, Zagreus returns to the House of Hades where he can:

| Activity | Location |
|----------|----------|
| Talk to NPCs | Throughout the House |
| Upgrade at Mirror of Night | Zagreus's bedroom |
| Equip Keepsakes | Keepsake cabinet (bedroom or pre-run) |
| Choose weapon | Courtyard weapon rack |
| Pet Cerberus | Lounge area |
| Access House Contractor | West wing |
| Talk to Wretched Broker | West wing |
| Access training dummy (Skelly) | Courtyard |
| Check Fated List of Prophecies | Lounge area |

### House Contractor Upgrades

Purchased with Gemstones and Diamonds. Unlock cosmetic and functional upgrades:

| Category | Examples | Currency |
|----------|----------|----------|
| Cosmetic (House) | Rugs, curtains, decorations | Gemstones |
| Functional | Fountain chambers, Well of Charon stock, music player | Gemstones/Diamonds |
| Lounge renovations | Instrument for Orpheus, decorations | Gemstones |
| Garden | Persephone's garden (post-story) | Diamonds |

### Wretched Broker

Trades currencies at fixed rates:

| Trade Direction | Rate |
|----------------|------|
| Gemstones -> Chthonic Keys | 500 Gems -> 1 Key |
| Chthonic Keys -> Nectar | 15 Keys -> 1 Nectar |
| Nectar -> Diamonds | 10 Nectar -> 1 Diamond |
| Diamonds -> Ambrosia | 1 Diamond -> 1 Ambrosia |
| Ambrosia -> Titan Blood | 1 Ambrosia -> 1 Titan Blood |

*Note: Trades are unidirectional; you cannot reverse the conversion chain.*

### Fated List of Minor Prophecies

A checklist of challenges/goals that grant rewards upon completion:

| Category | Examples | Rewards |
|----------|----------|---------|
| Weapon prophecies | Complete a run with each weapon | Gemstones, Darkness |
| God prophecies | Obtain all boons from a god | Nectar |
| Duo Boon prophecies | Obtain specific duo boons | Ambrosia |
| Relationship prophecies | Max affinity with NPCs | Diamonds |
| Run challenges | Escape at X heat, etc. | Titan Blood |

---

## 12. Mirror of Night

Located in Zagreus's bedroom. Spend Darkness to unlock permanent upgrades. Each of the 12 slots has two variants (Red = default, Green = alternate). Only one variant per slot can be active at a time. Alternate talents are unlocked after a conversation with Nyx (requires accumulating 300+ Darkness).

**Key Unlock Cost**: 5 keys for slots 3-4; 10 keys for slots 5-6; 20 keys for slots 7-8; 30 keys for slots 9-10; total 65 Chthonic Keys for all.

### All 12 Talent Pairs

| # | Default (Red) | Ranks | Total Darkness | Effect | Alternate (Green) | Ranks | Total Darkness | Effect |
|---|--------------|-------|----------------|--------|-------------------|-------|----------------|--------|
| 1 | Shadow Presence | 5 | 100 | +10% damage per rank when striking from behind (max +50%) | Fiery Presence | 5 | 100 | +15% damage per rank vs undamaged foes (max +75%) |
| 2 | Chthonic Vitality | 3 | 70 | Restore +1 HP per rank on entering each chamber (max +3) | Dark Regeneration | 2 | 90 | Recover 30% of Darkness collected as HP per rank (max 60%) |
| 3 | Death Defiance | 3 | 1,530 | +1 resurrection per rank at 50% HP (max 3 per run) | Stubborn Defiance | 1 | 600 | Resurrect once per chamber at 30% HP |
| 4 | Greater Reflex | 1 | 50 | +1 Dash charge | Ruthless Reflex | 1 | 75 | +50% damage and dodge for 2 sec after a close-call dash |
| 5 | Boiling Blood | 5 | 250 | +10% Attack/Special damage per rank vs foes with lodged Cast (max +50%) | Abyssal Blood | 5 | 300 | Foes with lodged Cast have -6% speed and damage per rank (max -30%) |
| 6 | Infernal Soul | 2 | 100 | +1 Bloodstone per rank (total: 3 with both ranks) | Stygian Soul | 3 | 100 | Cast regenerates; -1 sec per rank from base retrieval time (min 3 sec) |
| 7 | Deep Pockets | 10 | 525 | Start each run with +10 Obols per rank (max +100) | Golden Touch | 3 | 270 | Gain interest: +5% of current Obols per rank when clearing a region (max +15%) |
| 8 | Thick Skin | 10 | 625 | +5 max HP per rank (max +50) | High Confidence | 5 | 750 | +5% damage per rank while above 80% HP (max +25%) |
| 9 | Privileged Status | 2 | 550 | +20% damage per rank vs foes with 2+ status curses (max +40%) | Family Favorite | 2 | 200 | +2.5% damage per rank for each different Olympian blessing (max +5% per god) |
| 10 | Olympian Favor | 40 | 2,000 | +1% chance per rank for boons to be Rare or better (max +40%) | Dark Foresight | 10 | 1,500 | +2% chance per rank for gold laurel (run-relevant) rewards (max +20%) |
| 11 | Gods' Pride | 20 | 2,000 | +1% chance per rank for boons to be Epic (max +20%) | Gods' Legacy | 10 | 2,500 | +1% chance per rank for Legendary/Duo boons to appear (max +10%) |
| 12 | Fated Authority | 8 | 11,000 | Reroll chamber rewards; +1 use per rank (max 8 per run) | Fated Persuasion | 4 | 10,000 | Reroll boon and Well of Charon options; +1 use per rank (max 4 per run) |

**Total Darkness to max all default talents**: ~18,800
**Total Darkness to max all alternate talents**: ~16,485
**Grand total to max everything**: ~35,365

---

## 13. Keepsakes & Companions

### 13.1 Keepsakes

Keepsakes are passive items equipped before a run (or swapped at Fountain chambers between biomes). Each is obtained by giving Nectar to an NPC for the first time. Keepsakes have 3 ranks, upgraded by clearing encounters while equipped (Rank 2 at 25 encounters; Rank 3 at 75 total encounters).

#### NPC Keepsakes

| Keepsake | Given By | Effect (Rank 1 / 2 / 3) |
|----------|----------|--------------------------|
| Old Spiked Collar | Cerberus | +25 / +38 / +50 max HP |
| Myrmidon Bracer | Achilles | -20% / -25% / -30% frontal damage taken |
| Black Shawl | Nyx | +10% / +15% / +20% damage to undamaged foes and from behind |
| Pierced Butterfly | Thanatos | +1% / +1.5% / +2% damage per encounter cleared without taking damage |
| Bone Hourglass | Charon | Well of Charon items last +4 / +6 / +8 extra encounters |
| Chthonic Coin Purse | Hypnos | Gain 100 / 125 / 150 Obols at start of run |
| Skull Earring | Megaera | +20% / +30% / +40% damage while under 35% HP |
| Distant Memory | Orpheus | +10% / +20% / +30% damage to distant foes (500+ units) |
| Harpy Feather Duster | Dusa | 3% / 5% / 6% chance urns contain healing items |
| Lucky Tooth | Skelly | Resurrect once with 50 / 75 / 100 HP (once per run) |
| Shattered Shackle | Sisyphus | +50% / +75% / +100% damage to Attack/Special without boon |
| Evergreen Acorn | Eurydice | Block first 3 / 4 / 5 hits per boss encounter |
| Broken Spearpoint | Patroclus | 1.0 / 1.25 / 1.5 sec invulnerability after taking damage (7 sec cooldown) |
| Pom Blossom | Persephone | Random boon gains +1 level every 6 / 5 / 4 encounters |
| Sigil of the Dead | Hades | God Gauge starts 10% / 20% / 30% full each encounter (obtained on 2nd Nectar gift, post-story) |

#### Olympian Keepsakes

Each Olympian's keepsake guarantees that god's boon appears in the next eligible chamber, with increased rarity chance.

| Keepsake | God | Effect (Rank 1 / 2 / 3) |
|----------|-----|--------------------------|
| Thunder Signet | Zeus | Next boon is Zeus; 10% / 15% / 20% chance to be Rare+ |
| Owl Pendant | Athena | Next boon is Athena; 10% / 15% / 20% Rare+ |
| Blood-Filled Vial | Ares | Next boon is Ares; 10% / 15% / 20% Rare+ |
| Eternal Rose | Aphrodite | Next boon is Aphrodite; 10% / 15% / 20% Rare+ |
| Adamant Arrowhead | Artemis | Next boon is Artemis; 10% / 15% / 20% Rare+ |
| Overflowing Cup | Dionysus | Next boon is Dionysus; 10% / 15% / 20% Rare+ |
| Conch Shell | Poseidon | Next boon is Poseidon; 10% / 15% / 20% Rare+ |
| Frostbitten Horn | Demeter | Next boon is Demeter; 10% / 15% / 20% Rare+ |
| Lambent Plume | Hermes | +1.0% / +1.1% / +1.2% Dodge Chance and Move Speed per quick clear |
| Cosmic Egg | Chaos | Chaos blessings 20% / 30% / 40% Rare+; no HP cost to enter Chaos Gates |

---

### 13.2 Companions (Legendary Keepsakes)

Companions are powerful summon items obtained after completing an NPC's favor questline and then giving them Ambrosia. Each can be used once per encounter (up to 5 times per run base; upgradeable with additional Ambrosia). Companions cannot be used against the associated character's boss fight.

| Companion | Given By | Summon Effect | Restriction |
|-----------|----------|---------------|-------------|
| Battie | Megaera | Megaera appears; deals 2,500 AoE damage in a line | Cannot use vs Fury Sisters |
| Mort | Thanatos | Thanatos deals 3,500 damage in a large radial area after brief charge | Cannot use vs Hades |
| Rib | Skelly | Skelly appears as a decoy with 250 HP; draws enemy aggro | No restriction |
| Fidi | Dusa | Dusa fires seeking shots dealing 70 damage each; freezes targets for 15 seconds | Cannot use vs Hades |
| Antos | Achilles | Achilles and Patroclus attack together; deal 1,500 damage to 2 targets in sequence | Cannot use vs Hades |
| Shady | Sisyphus | Sisyphus and Bouldy drop from sky; deal 1,000 damage in large area | Cannot use vs Hades |

**Companion Upgrade**: Each additional Ambrosia given (up to 5 total) increases uses per run by +1 (max 5 uses per run per companion).

---

## 14. Heat System -- Pact of Punishment

After the first successful escape with a weapon, the Pact of Punishment unlocks. It allows players to add difficulty modifiers (Heat) to runs. Heat is tracked per weapon.

**Bounty System**: Each new Heat threshold per weapon yields first-clear bounty rewards (Titan Blood, Diamonds, Ambrosia).

**Maximum Heat**: 63 (64 in Hell Mode, which adds +1 from Personal Liability).

### All 15 Conditions

| # | Condition | Max Ranks | Heat per Rank | Max Heat | Effect per Rank |
|---|-----------|-----------|---------------|----------|-----------------|
| 1 | Hard Labor | 5 | 1 | 5 | Enemies deal +20% damage per rank (max +100%) |
| 2 | Lasting Consequences | 4 | 1 | 4 | Healing reduced by 25% per rank (max -100%; no healing) |
| 3 | Convenience Fee | 2 | 1/1 | 2 | Shop prices +40% per rank (max +80%) |
| 4 | Jury Summons | 3 | 1 | 3 | +20% more enemies per rank (max +60%) |
| 5 | Extreme Measures | 4 | 1/2/2/3 | 8 | Bosses gain new attacks and mechanics per rank |
| 6 | Calisthenics Program | 2 | 1 | 2 | Enemies gain +15% max HP per rank (max +30%) |
| 7 | Benefits Package | 2 | 2/3 | 5 | Armored enemies gain +1 perk per rank (e.g., regeneration, retaliation) |
| 8 | Middle Management | 1 | 2 | 2 | Minibosses gain an Elite companion |
| 9 | Underworld Customs | 1 | 2 | 2 | Must sacrifice 1 boon when leaving each biome |
| 10 | Forced Overtime | 2 | 3 | 6 | Enemies move/attack +20% faster per rank (max +40%) |
| 11 | Heightened Security | 1 | 1 | 1 | Traps and magma deal +400% damage |
| 12 | Routine Inspection | 4 | 2 | 8 | Deactivate 3 Mirror talents per rank (max 12 disabled) |
| 13 | Damage Control | 2 | 1 | 2 | Enemies gain 1 Shielded HP per rank (absorbs first hit) |
| 14 | Approval Process | 2 | 2/3 | 5 | Boon choices reduced by -1 per rank (min 1 choice) |
| 15 | Tight Deadline | 2 | 2/3 | 5 | Biome timer reduced by 2:00 per rank (must clear each biome within time limit; base: 9 min) |

**Heat 16 (Hell Mode only)**: Personal Liability -- All damage dealt to Zagreus is +100% (effectively doubles all incoming damage).

### Erebus Gates

Accessible at certain Heat thresholds:

| Gate Location | Heat Required |
|--------------|---------------|
| Tartarus | 5 Heat |
| Asphodel | 10 Heat |
| Elysium | 15 Heat |

Erebus challenge rooms require clearing all enemies without taking any damage. Reward is enhanced (double) room reward.

---

## 15. Economy & Currencies

### Persistent Currencies (Kept Between Runs)

| Currency | Icon | Primary Uses | Sources |
|----------|------|-------------|---------|
| Darkness | Purple crystal | Mirror of Night upgrades | Room rewards, bosses, fishing |
| Gemstones | Green gems | House Contractor cosmetics/upgrades | Room rewards, fishing |
| Chthonic Keys | Silver keys | Weapon unlocks, Mirror slot unlocks | Room rewards, fishing |
| Nectar | Golden bottle | Gift to NPCs (earn Keepsakes); trade | Room rewards, fishing, bosses |
| Ambrosia | Red/gold bottle | Gift to NPCs (earn Companions, max affinity); upgrade Companions | Boss bounties (first clear at new Heat), fishing |
| Diamonds | Blue diamond | House Contractor premium upgrades | Boss bounties, fishing |
| Titan Blood | Red drop | Weapon Aspect upgrades (1-5 per aspect) | Boss bounties (first clear per Heat per weapon), fishing |

### Run-Only Currency

| Currency | Icon | Uses | Sources |
|----------|------|------|---------|
| Charon's Obol (Gold) | Coin | Purchase items at Charon's Shop and Well of Charon | Room rewards, enemies, urns, Deep Pockets |

### Obol Economy (Per Run)

| Item Category | Base Price (Obols) |
|---------------|-------------------|
| Boon (Common) | 150 |
| Boon (Rare) | 200 |
| Boon (Epic) | 250 |
| Pom of Power | 100 |
| Centaur Heart | 125 |
| Daedalus Hammer | 275 |
| Well of Charon buffs | 30-80 |
| Charon's Loyalty Card | Reduces future prices by 20% |

### Well of Charon Items

| Item | Cost | Effect |
|------|------|--------|
| Light of Ixion | 50 | Next 4 encounters, foes drop +3 Obols |
| Cyclops Jerky | 40 | +40 max HP for 3 encounters |
| Braid of Atlas | 40 | +40% damage for 3 encounters |
| Prometheus Stone | 60 | +1 Bloodstone for 3 encounters |
| Kiss of Styx | 100 | Replenish 1 Death Defiance charge |
| Nail of Talos | 80 | +4% dodge chance for 10 encounters |
| Yarn of Ariadne | 80 | Next boon is Legendary/Duo rarity |
| HydraLite | 30 | Restore 30% HP |
| Centaur Soul | 60 | +25 max HP (permanent for run) |
| Night Spindle | 30 | +1 use of Fated Authority/Persuasion |

---

## 16. Narrative System

### Story Structure

Hades tells its story entirely through runs. There is no separate "story mode" or cutscenes outside gameplay. Dialogue advances between and during runs.

| Narrative Element | Implementation |
|-------------------|----------------|
| Main plot | Zagreus discovers his true mother (Persephone) and attempts to reach the surface to find her |
| Dialogue triggers | NPC dialogue advances based on run count, events, relationships, and narrative flags |
| Relationship system | Nectar gifts (Keepsake unlock) -> Ambrosia gifts (Companion unlock) -> Favor completion |
| Affinity gauge | Hearts displayed per NPC; 6-10 hearts depending on character |
| Locked hearts | After ~6 Nectar gifts, hearts lock; must complete character's Favor (questline) to unlock |
| Story credits | Roll after approximately 10 successful escapes |
| Epilogue | Requires maxing key relationships and additional escapes after credits |
| Total dialogue | 305,433 words across 21,020 voiced lines |

### NPC Relationship Progression

| Stage | Action | Result |
|-------|--------|--------|
| 1. First Nectar | Give Nectar to NPC | Receive Keepsake; heart fills |
| 2. Additional Nectar (up to 5-6) | Give more Nectar | Hearts fill; new dialogue |
| 3. Locked Heart | Cannot give more Nectar | Must complete Favor (quest) |
| 4. Favor Complete | Complete NPC's personal storyline | Hearts unlock; can give Ambrosia |
| 5. Ambrosia Gift | Give Ambrosia | Receive Companion (if applicable); affinity increases |
| 6. Max Affinity | All hearts filled | Character storyline complete |

### Key NPCs and Locations

| NPC | Location | Role |
|-----|----------|------|
| Zagreus | Protagonist | Player character; ~8,500 voice lines |
| Hades | House of Hades throne | Father/antagonist; comments on each death |
| Nyx | House of Hades | Adoptive mother; unlocks Mirror alternates |
| Megaera | House of Hades (lounge) | Romance option; Fury boss |
| Thanatos | House of Hades (randomly) | Romance option; combat ally |
| Dusa | House of Hades (lounge) | Romance option (mild); floating Gorgon maid |
| Achilles | House of Hades (west hall) | Mentor; weapon training lore |
| Orpheus | House of Hades (lounge) | Court musician; sings after favor |
| Hypnos | House of Hades (entrance) | Comments on cause of death |
| Cerberus | House of Hades (lounge) | Pet-able three-headed dog |
| Skelly | Courtyard | Training dummy; sarcastic |
| Sisyphus | Tartarus mid-run NPC | Gives resources |
| Eurydice | Asphodel mid-run NPC | Gives food buffs |
| Patroclus | Elysium mid-run NPC | Gives combat buffs |
| Charon | Shop rooms | Shopkeeper (can be fought as secret miniboss) |
| Persephone | Surface (post-escape) | Zagreus's mother; central to plot |

### Charon Secret Fight

If Zagreus tries to steal from Charon's shop (grab the sack behind him), Charon attacks. Defeating Charon (boss-tier fight, ~14,000 HP) grants a 20% discount on all shops for the rest of the run plus the stolen item.

---

## 17. Audio Design

### Music

| Property | Details |
|----------|---------|
| Composer | Darren Korb (Audio Director at Supergiant Games) |
| Vocalist | Ashley Barrett (frequent collaborator) |
| Style | Mediterranean/Eastern-influenced rock with metal, electronic, and folk elements |
| Recording | Some orchestral tracks recorded at Abbey Road Studios |
| Adaptive music | Music layers add/remove based on combat state |
| Track count | ~50 unique tracks |

### Key Tracks

| Track | Context |
|-------|---------|
| "Good Riddance" | End credits; acoustic ballad by Ashley Barrett and Darren Korb |
| "In the Blood" | Surface escape scenes |
| "On the Coast" | Asphodel theme (orchestral) |
| "The Unseen Ones" | Tartarus combat |
| "Lament of Orpheus" | Orpheus singing in the lounge |
| "The Exalted" | Elysium combat |
| "The King and the Bull" | Theseus & Asterius boss fight |
| "God of the Dead" | Final boss (Hades) fight |
| "No Escape" | Phase 2 of Hades fight |
| "Out of Tartarus" | House of Hades ambient |
| "Mouth of Styx" | Temple of Styx theme |

### Voice Acting

| Actor | Role(s) |
|-------|---------|
| Darren Korb | Zagreus, Skelly, additional voices |
| Logan Cunningham | Hades, Poseidon, Achilles, Charon, Asterius, narrator |
| Supergiant Voice Cast | 23+ voiced characters total |

**Voice Line Breakdown**:
- Zagreus: ~8,500 lines (most of any character)
- Hades: ~2,000+ lines
- Other major NPCs: 200-800 lines each
- Olympian gods: 150-400 lines each

### Sound Effects

| Category | Description |
|----------|-------------|
| Weapon impacts | Unique per weapon type; different for hitting enemies vs armor vs walls |
| Dash | Quick whoosh with magical undertone |
| Boon selection | Chime specific to god (e.g., thunder crack for Zeus, sea wave for Poseidon) |
| Enemy death | Varied per enemy type; shades dissolve |
| Door transition | Heavy stone grinding |
| Currency pickup | Distinct jingle per currency type |
| Status effects | Each curse has a unique audio indicator when applied |
| Boss transitions | Musical stingers on phase changes |
| Death/respawn | Blood pool dissolution; river of Styx surfacing sound |

---

## 18. UI Layout

### HUD (In Combat)

```
+------------------------------------------------------------------+
|  [Boon Icons (active boons, top-left, small)]                    |
|                                                                    |
|                                                                    |
|                        GAME ARENA                                  |
|                                                                    |
|                                                                    |
|                                                                    |
|  [DD Icons]  [HP Bar]  [Cast Ammo]         [Enemy HP] (when hit)  |
|  [God Gauge (below HP)]                                            |
|              [Gold Counter]                [Weapon Icon]            |
+------------------------------------------------------------------+
```

| HUD Element | Position | Description |
|-------------|----------|-------------|
| HP Bar | Bottom-left | Red bar; current/max HP; white for bonus HP |
| Death Defiance icons | Left of HP bar | Skull icons (filled = available, empty = used) |
| Cast Ammo | Right of HP bar | Bloodstone icons (filled = available, hollow = lodged in enemy) |
| God Gauge | Below HP bar | Circular meter; fills yellow; flashes when Call is ready |
| Gold Counter | Bottom-center | Current Obol count with coin icon |
| Active Boons | Top-left corner | Small god-colored icons showing equipped boons |
| Enemy HP | Above enemies | Red bar appears when enemy is damaged; armor shown in pink above red |
| Boss HP | Top-center | Large bar with boss name; shows phases |
| Room Reward | Pre-entry door | Icon above door showing next room's reward |
| Darkness/Gem counter | Pop-up | Appears when collecting persistent currencies |
| Weapon Icon | Bottom-right | Shows equipped weapon aspect |

### Boon Selection Screen

When Zagreus receives a boon offering:

```
+------------------------------------------------------------------+
|                      [God Portrait + Name]                        |
|                      [God Flavor Text]                            |
|                                                                    |
|  +----------------+  +----------------+  +----------------+       |
|  | [Boon Icon]    |  | [Boon Icon]    |  | [Boon Icon]    |       |
|  | Boon Name      |  | Boon Name      |  | Boon Name      |       |
|  | [Rarity Color] |  | [Rarity Color] |  | [Rarity Color] |       |
|  | Effect Text    |  | Effect Text    |  | Effect Text    |       |
|  | Numeric Value  |  | Numeric Value  |  | Numeric Value  |       |
|  +----------------+  +----------------+  +----------------+       |
|                                                                    |
|  [Reroll Button (if Fated Persuasion available)]                  |
|  [Slot indicator: "Replaces: X" if applicable]                    |
+------------------------------------------------------------------+
```

| Element | Description |
|---------|-------------|
| Choices | Usually 3 boons; reduced by Approval Process (Pact) |
| Rarity border | Blue=Common, Green=Rare, Purple=Epic, Red=Heroic, Orange=Legendary/Duo |
| Slot indicator | Shows which existing boon would be replaced |
| Reroll | Costs 1 Fated Persuasion charge; refreshes all 3 options |
| God voice line | God speaks a unique line when offering boons |

### Pause Menu

| Option | Function |
|--------|----------|
| Resume | Return to gameplay |
| Boon Info | View all currently held boons with descriptions |
| Give Up | Abandon run and return to House (counts as death) |
| Settings | Audio, video, controls, accessibility |
| Codex | In-game encyclopedia of enemies, characters, gods, items |

### Codex

The Codex is a comprehensive in-game encyclopedia that unlocks entries as the player encounters new elements:

| Category | Contents |
|----------|----------|
| Olympians | God lore, boon lists |
| Chthonic Gods | Underworld deity information |
| Foes | Enemy descriptions, biome locations |
| Arms | Weapon descriptions, aspect lore |
| Keepsakes | Item descriptions |
| Characters | NPC biographies, relationship info |

### Death Screen

Upon death, a brief animation plays (Zagreus sinking into blood), followed by respawning in the Pool of Styx in the House of Hades. Hypnos greets Zagreus with a comment about how he died. Hades comments from his desk. No explicit "Game Over" screen -- the transition is seamless back into the hub.

### Run Summary (Post-Escape)

After defeating Hades and reaching the surface, a brief narrative scene plays. Zagreus eventually returns to the House (due to story reasons: he cannot survive on the surface permanently). No formal stats screen; progression is tracked via the Fated List and relationship gauges.

---

## Appendix A: Daedalus Hammer Distribution Rules

- Maximum 2 Daedalus Hammers per run.
- First Hammer is guaranteed to appear before the end of Asphodel.
- Second Hammer is guaranteed to appear in Elysium or Temple of Styx.
- Hammers always offer 3 upgrade choices (weapon-specific).
- Some upgrades are mutually exclusive (e.g., Flurry Slash and World Splitter for the Blade).
- Aspect of Arthur/Guan Yu/Gilgamesh/Lucifer/Beowulf/Rama have unique exclusive hammer options.

## Appendix B: Fishing System

Fishing Points appear as a sparkling spot on specific room platforms after clearing all enemies. Requires the Rod of Fishing (purchased from House Contractor for 1 Diamond).

| Fish Tier | Reward |
|-----------|--------|
| Common | Small currency reward (Darkness, Gems) |
| Rare | Medium reward (Nectar, Chthonic Keys) |
| Legendary | Large reward (Diamonds, Ambrosia, Titan Blood) |

Fish rarity depends on biome and timing of the catch (visual cue: press interact when bobber dips).

## Appendix C: Complete Run Flow

```
1. House of Hades (Hub)
   - Equip Keepsake
   - Select Weapon (random bonus: +20% Darkness/Gemstones for "dark thirst" weapon)
   - Interact with NPCs for dialogue advancement
   
2. Tartarus (Chambers 1-14)
   - 13-14 combat/reward chambers
   - Optional: Chaos Gates, Erebus Gates, Infernal Troves
   - Mid-run NPC: Sisyphus (random encounter)
   - Miniboss: Doomstone or elite variants
   - BOSS: Fury Sister (Megaera/Alecto/Tisiphone)
   - Fountain Chamber (heal + keepsake swap)

3. Asphodel (Chambers 15-24)
   - 9-10 combat/reward chambers
   - Magma hazard throughout
   - Mid-run NPC: Eurydice (random encounter)
   - Miniboss: Megagorgon, Skull-Crusher, or Spreader
   - BOSS: Lernaean Bone Hydra
   - Fountain Chamber

4. Elysium (Chambers 25-35)
   - 10-11 combat/reward chambers
   - Armored enemies throughout
   - Mid-run NPC: Patroclus (random encounter)
   - Miniboss: Asterius (solo, weaker than boss version)
   - Thanatos encounter (random; compete for kills)
   - BOSS: Theseus & Asterius
   - Fountain Chamber

5. Temple of Styx (Chambers 36+)
   - Central hub with 5 tunnel entrances
   - Each tunnel: 3-5 small rooms
   - One tunnel contains Satyr Sack (for Cerberus)
   - Must find Satyr Sack to proceed
   - Shop available in hub
   - BOSS: Hades (2-phase fight on the surface)

6. Surface
   - Narrative scene with Persephone
   - Zagreus eventually returns to House
   - Run complete; rewards tallied
```

## Appendix D: Accessibility Options

| Option | Description |
|--------|-------------|
| God Mode | Toggle; start at 20% damage resistance, +2% per death (caps at 80%) |
| Colorblind options | Adjustable UI colors |
| Subtitles | Always on for voiced dialogue |
| Controller remapping | Full rebinding support |
| Screen shake | Adjustable intensity |
| Aim assist | Adjustable for cast targeting |
