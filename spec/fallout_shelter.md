# Fallout Shelter — Complete Game Specification

## 1. Game Overview

Fallout Shelter is a vault management simulation set in the Fallout universe. The player
is the Overseer of a Vault-Tec vault, managing dwellers, building rooms, assigning jobs,
defending against threats, and sending dwellers on wasteland expeditions. The game
combines base-building, resource management, and light RPG elements.

Platform: Single-player, 2D side-view cross-section of underground vault.
Visual style: Stylized 2D with Fallout's retro-futuristic aesthetic.
Simulation tick: Real-time with idle mechanics.

## 2. Technical Foundation

### 2.1 Vault Structure
```
struct Vault {
    rooms: list[list[Room]]     // 2D grid: rows (depth) x columns (width)
    max_width: 24               // Tiles wide (including rock walls)
    max_depth: 25               // Floors deep
    dwellers: list[Dweller]
    resources: Resources
    inventory: Inventory
    quests: list[Quest]
    radio_active: boolean
    happiness_avg: float
}

struct Resources {
    power: float          // 0-max, depletes over time
    food: float           // 0-max, depletes over time
    water: float          // 0-max, depletes over time
    caps: integer         // Currency
    nuka_quantum: integer // Premium currency
    stimpaks: integer     // Healing items
    radaway: integer      // Radiation removal
}
```

### 2.2 Room Grid
- Vault entrance at top center
- Each floor is 1 tile high
- Rooms are 1, 2, or 3 tiles wide (merged rooms)
- Elevators are 1 tile wide, connect floors vertically
- Must have elevator access path from entrance to all rooms

## 3. Room System

### 3.1 Resource Production Rooms

| Room            | Size | Cost (1/2/3 wide) | Resource  | Base Production | SPECIAL  | Unlock    |
|----------------|------|---------------------|-----------|-----------------|----------|-----------|
| Power Generator| 1-3  | 100/200/400        | Power     | 10/20/35 /cycle | S        | Start     |
| Diner          | 1-3  | 100/200/400        | Food      | 8/16/28 /cycle  | A        | Start     |
| Water Treatment| 1-3  | 100/200/400        | Water     | 8/16/28 /cycle  | P        | Start     |
| Nuclear Reactor| 1-3  | 800/1600/3200      | Power     | 25/50/90 /cycle | S        | 60 dwlrs |
| Garden         | 1-3  | 500/1000/2000      | Food      | 18/36/65 /cycle | A        | 50 dwlrs |
| Water Purifier | 1-3  | 500/1000/2000      | Water     | 18/36/65 /cycle | P        | 55 dwlrs |
| Nuka-Cola Plant| 1-3  | 1200/2400/4800     | Food+Water| 15+15 each      | E        | 100 dwlrs|

### 3.2 Training Rooms

| Room                | Size | Cost (1/2/3)        | SPECIAL Stat | Unlock     |
|--------------------|------|----------------------|-------------|------------|
| Weight Room        | 1-3  | 300/600/1200        | Strength    | 24 dwlrs  |
| Athletics Room     | 1-3  | 350/700/1400        | Perception  | 28 dwlrs  |
| Armory             | 1-3  | 400/800/1600        | Endurance   | 32 dwlrs  |
| Classroom          | 1-3  | 500/1000/2000       | Intelligence| 36 dwlrs  |
| Game Room          | 1-3  | 600/1200/2400       | Agility     | 40 dwlrs  |
| Lounge             | 1-3  | 700/1400/2800       | Charisma    | 44 dwlrs  |
| Fitness Room       | 1-3  | 800/1600/3200       | Luck        | 48 dwlrs  |

Training time per stat point:
```
training_hours = base_hours * (current_stat_level)
base_hours = 2.0  (for level 1→2)
// Level 1→2: 2 hours
// Level 5→6: 10 hours
// Level 9→10: 18 hours
// Room size reduces time: 2-wide = 0.9x, 3-wide = 0.8x
```

### 3.3 Utility Rooms

| Room              | Size | Cost          | Function                         | Unlock      |
|------------------|------|---------------|----------------------------------|-------------|
| Vault Door       | 1    | Free          | Entry point, defense             | Start       |
| Living Quarters  | 1-3  | 100/200/400   | +8/16/28 dweller capacity        | Start       |
| Medbay           | 1-3  | 400/800/1600  | Produces Stimpaks                | 14 dwlrs   |
| Science Lab      | 1-3  | 400/800/1600  | Produces RadAway                 | 16 dwlrs   |
| Storage Room     | 1-3  | 300/600/1200  | +10/20/35 inventory slots        | 12 dwlrs   |
| Radio Station    | 1-3  | 600/1200/2400 | Attracts new dwellers, +happiness| 20 dwlrs   |
| Overseer's Office| 1    | 1000          | Quest management                 | 18 dwlrs   |
| Barbershop       | 1    | 500           | Cosmetic changes                 | 22 dwlrs   |
| Weapon Workshop  | 1-3  | 800/1600/3200 | Craft weapons                    | 22 dwlrs   |
| Outfit Workshop  | 1-3  | 600/1200/2400 | Craft outfits                    | 32 dwlrs   |
| Theme Workshop   | 1-3  | 800/1600/3200 | Craft decorations                | 42 dwlrs   |

### 3.4 Room Merging
Adjacent rooms of the same type merge automatically:
- 2 rooms merge = double-wide (higher capacity, efficiency)
- 3 rooms merge = triple-wide (highest capacity, efficiency)
- Merged rooms function as one unit

### 3.5 Room Upgrades
Each room can be upgraded 3 times:
| Level | Cost Multiplier | Production Bonus |
|-------|----------------|-----------------|
| 1     | 1x base        | Base production  |
| 2     | 2x base        | +50% production  |
| 3     | 3x base        | +100% production |

### 3.6 Rush Mechanic
Player can "rush" any production room:
```
success_chance = 60% - (rush_count_today * 10%) + (assigned_dwellers_avg_luck * 2%)
if success:
    instantly complete current production cycle
    bonus caps = room.production_value * 0.5
    dweller_happiness += 10
if failure:
    incident occurs (fire or radroach)
    dweller_happiness -= 10
    no production
```

## 4. Dweller System

### 4.1 SPECIAL Stats
```
struct Dweller {
    name: string
    level: 1-50
    hp: float                    // max_hp = 105 + (endurance * 2.5 * level)
    max_hp: float
    experience: integer
    happiness: 0-100
    radiation: 0-100             // Reduces effective max HP
    S: 1-10  // Strength         // Power production, melee damage
    P: 1-10  // Perception       // Water production, exploration finds
    E: 1-10  // Endurance        // HP per level, rad resistance
    C: 1-10  // Charisma         // Radio recruitment, breeding speed
    I: 1-10  // Intelligence     // Stimpak/RadAway production, crafting
    A: 1-10  // Agility          // Food production, combat speed
    L: 1-10  // Luck             // Rush success, loot quality
    weapon: Weapon | null
    outfit: Outfit | null
    pet: Pet | null
    assigned_room: Room | null
    is_pregnant: boolean
    pregnancy_timer: float       // Hours remaining
    is_child: boolean
    child_growth_timer: float    // Hours until adult
    exploring: boolean
    quest_active: boolean
}
```

### 4.2 Experience and Leveling
```
xp_per_level = 100 * current_level
// Level 1→2: 100 XP
// Level 49→50: 4900 XP

xp_sources:
  - working in rooms: 1 XP per production cycle
  - rushing successfully: 10 XP
  - combat: 5 XP per enemy killed
  - exploration: varies (10-100 per event)
  - completing quests: 50-500 XP

// HP gain per level:
hp_gain = 2.5 + (endurance * 0.5)
// E=1: +3 HP/level, E=10: +7.5 HP/level
// This makes early Endurance training critical
```

### 4.3 Happiness
```
happiness starts at 50 for new dwellers
happiness modifiers:
  +10: working in matching SPECIAL room
  +10: successful rush
  +20: leveling up
  +10: completing quest
  +10-40: radio station broadcast (based on Charisma)
  -10: failed rush
  -20: dweller death
  -5: low food/water per tick
  -10: incident in their room
  -30: revived from death
  +20: mating (briefly)

// Happiness affects vault average
vault_happiness = average(dweller.happiness for dweller in all_dwellers)
```

### 4.4 Reproduction
```
// Two dwellers in Living Quarters with space available
// Both must be adults, not related (parent-child, siblings)
mating_time = 4 hours / (avg_charisma / 5)
// High charisma = faster

pregnancy_duration = 3 hours (real time)
child_growth_duration = 3 hours (real time)

// Child inherits:
child.SPECIAL = average(parent1.SPECIAL, parent2.SPECIAL) + random(-1, +1) per stat
child.SPECIAL = clamp(child.SPECIAL, 1, 10)
```

## 5. Resource Management

### 5.1 Resource Consumption
```
// Per dweller per tick (1 tick = ~1 minute real time):
power_consumption = 0.5 per room (not per dweller)
food_consumption = 0.1 per dweller per tick
water_consumption = 0.1 per dweller per tick

// Low resource effects:
if power < 25%: rooms start shutting down (furthest from power first)
if food < 25%: dwellers lose HP slowly, happiness decreases
if water < 25%: dwellers gain radiation slowly, happiness decreases
```

### 5.2 Production Cycles
```
cycle_time = base_time / (1 + assigned_dwellers_relevant_stat_avg * 0.1)
// base_time varies by room type (typically 60-180 seconds)
// More and better skilled dwellers = faster cycles

production_amount = base_production * (1 + upgrade_level * 0.5) * merge_bonus
merge_bonus: 1-wide=1.0, 2-wide=1.15, 3-wide=1.30
```

### 5.3 Resource Caps
```
resource_max = sum(room.storage_capacity for room in rooms_of_type)
// Each production room stores its own resource:
storage_per_room = base_storage * (1 + upgrade_level * 0.5)
// base_storage: Power=30, Food=25, Water=25
```

## 6. Combat System

### 6.1 Incidents
| Incident     | Trigger                    | Threat                            |
|-------------|---------------------------|-----------------------------------|
| Radroach    | Failed rush, random       | Weak enemies, attack dwellers     |
| Fire        | Failed rush, random       | Damages room, hurts dwellers      |
| Mole Rat    | Random, rooms touching dirt| Medium enemies, spread between rooms|
| Raider      | Random (5+ dwellers)      | Attack vault door, steal resources|
| Deathclaw   | Random (60+ dwellers)     | Very strong, fast, move room to room|
| Radscorpion | Random (50+ dwellers)     | Poison, spread between rooms      |

### 6.2 Combat Mechanics
```
// Dwellers auto-attack enemies in their room
damage_per_hit = weapon.damage * (1 + relevant_stat * 0.1)
attack_speed = 1 + agility * 0.1  // Hits per second

// Weapon damage ranges:
weapon_damage = {
    "Rusty BB Gun": 0-1,
    "10mm Pistol": 2-3,
    "Hunting Rifle": 3-5,
    "Laser Pistol": 4-6,
    "Plasma Rifle": 7-9,
    "Fat Man": 15-18,
    "Dragon's Maw": 19-22,
    "Vengeance": 22-25
}

// Enemy HP:
radroach_hp = 5 * vault_avg_level
raider_hp = 10 * vault_avg_level (2-4 raiders per attack)
deathclaw_hp = 50 * vault_avg_level (2-3 deathclaws per attack)
mole_rat_hp = 8 * vault_avg_level
```

### 6.3 Healing
```
stimpak: heals 50% of max HP instantly
radaway: removes 50% of radiation
// Player must manually use these on dwellers during combat
// Auto-use can be enabled for exploration/quests
```

## 7. Exploration

### 7.1 Wasteland Exploration
Send dwellers into the wasteland to find items and caps.
```
exploration_event_interval = 60 seconds (real time)
each event:
    type = random([COMBAT, LOOT, NOTHING, SPECIAL], weights=[0.3, 0.4, 0.2, 0.1])

    if COMBAT:
        enemy = random_wasteland_enemy()
        damage_taken = enemy.damage - dweller.armor_rating
        dweller.hp -= damage_taken
        if dweller.hp <= 0: dweller dies (can be revived with caps)
        xp_gained = enemy.level * 10

    if LOOT:
        item = generate_loot(dweller.luck)
        caps_found = random(1, 100) * (1 + dweller.luck * 0.1)

    if SPECIAL:
        // Rare event: unique dialog, choice, special loot
```

### 7.2 Exploration Loot Quality
```
loot_tier = random weighted by luck:
    common (60% - luck*3%)
    rare (25% + luck*1.5%)
    legendary (15% + luck*1.5%)
```

### 7.3 Return Time
```
return_time = exploration_time / 2  // Takes half as long to return
// Dweller auto-uses stimpaks and radaway during exploration
// Must carry supplies: give stimpaks and radaway before sending out
```

## 8. Quest System

### 8.1 Quest Types
| Quest Type      | Duration   | Enemies | Rooms | Rewards                    |
|----------------|-----------|---------|-------|----------------------------|
| Daily          | 15-30 min | Easy    | 3-5   | Caps, items, lunchboxes    |
| Weekly         | 1-3 hours | Medium  | 5-10  | Rare items, lunchboxes     |
| Story          | Varies    | Hard    | 5-15  | Legendary items, unlocks   |

### 8.2 Quest Mechanics
- Send 1-3 dwellers on a quest
- Navigate through rooms, fighting enemies
- Find loot in containers
- Boss fights at end
- Dwellers can die (revivable with caps)

### 8.3 Quest Locations
```
struct QuestLocation {
    name: string
    rooms: list[QuestRoom]
    enemies: list[Enemy]
    loot_table: list[LootEntry]
    boss: Enemy | null
    difficulty: 1-5
}
```

## 9. Lunchbox / Premium System

### 9.1 Lunchboxes
Premium reward crates containing 4 cards:
```
Card rarity distribution per lunchbox:
  - 1 guaranteed rare or higher
  - 3 common-rare

Card contents:
  - Resources (caps, food, water, power)
  - Items (weapons, outfits)
  - Dwellers (rare/legendary with high SPECIAL)
  - Nuka-Cola Quantum

Lunchbox sources:
  - Completing objectives
  - Real-money purchase (IAP)
  - Rare quest rewards
```

### 9.2 Objectives
Rolling objectives that reward lunchboxes:
| Objective Example              | Reward      |
|-------------------------------|-------------|
| "Collect 500 food"            | 1 Lunchbox  |
| "Level up 5 dwellers"        | 1 Lunchbox  |
| "Equip 10 dwellers"          | 1 Lunchbox  |
| "Send 3 dwellers exploring"  | 1 Lunchbox  |
| "Complete 2 quests"          | 1 Lunchbox  |
| "Have 30 dwellers"           | 1 Lunchbox  |

3 active objectives at a time. Can skip one per day for free.

## 10. Crafting System

### 10.1 Weapon Crafting
```
Weapon Workshop + junk items = new weapon
crafting_time = weapon_tier * 30 minutes
crafting_requires:
  - Recipe (unlocked via quests or exploration)
  - Junk items (specific combinations)
  - Caps (100-5000 depending on tier)

Intelligence affects crafting speed: time *= (1 - I * 0.05)
```

### 10.2 Outfit Crafting
Similar to weapon crafting but in Outfit Workshop.
Outfits boost SPECIAL stats when worn.

### 10.3 Junk Items
25+ junk types found in wasteland/quests:
| Junk Type        | Rarity  | Used For              |
|-----------------|---------|------------------------|
| Duct Tape       | Common  | Many recipes           |
| Screw           | Common  | Weapons, misc          |
| Adhesive        | Common  | Outfits                |
| Globe           | Uncommon| High-tier weapons      |
| Camera          | Uncommon| Outfits                |
| Gold Watch      | Rare    | Legendary items        |
| Military Tape   | Rare    | Legendary weapons      |
| Tri-tool        | Rare    | Legendary items        |

## 11. Pets

### 11.1 Pet Types
| Pet Type | Effect Examples                               |
|---------|-----------------------------------------------|
| Cat     | +damage, +exploration speed                   |
| Dog     | +wasteland caps, +wasteland items             |
| Parrot  | +quest rewards, +child SPECIAL               |

### 11.2 Pet Rarity
| Rarity    | Bonus Range | Source              |
|-----------|------------|---------------------|
| Common    | +5-10%     | Pet carriers        |
| Rare      | +10-20%    | Pet carriers        |
| Legendary | +20-50%    | Pet carriers (rare) |

## 12. UI Layout

### 12.1 Main Vault View
```
+------------------------------------------------------------------+
| [Menu] Caps: 15,240 | Dwellers: 45/50 | [Objectives] [Quests]    |
+------------------------------------------------------------------+
|                                                                    |
|  Ground Level:        ████ VAULT DOOR ████                        |
|                       ║                    ║                       |
|  Depth 1:  [Power Gen ][Power Gen ][Power Gen ] ║ [Living Qrtrs ] |
|            [  S:7 S:5 ][  S:8 S:6 ][  S:9    ] ║ [👤👤👤👤👤 ] |
|                                                  ║                 |
|  Depth 2:  [Diner     ][Diner     ] ║ [Medbay   ][Medbay   ]     |
|            [ A:6 A:7  ][ A:5 A:8  ] ║ [ I:7 I:8 ][ I:6     ]     |
|                                      ║                             |
|  Depth 3:  [Water Trt ][Water Trt ][Water Trt ] ║ [Storage  ]     |
|            [ P:8 P:6  ][ P:7 P:5  ][ P:9      ] ║ [📦📦📦  ]     |
|                                                  ║                 |
|  Depth 4:  [Weight Rm ]             ║ [Classroom]                  |
|            [ 🏋️ S+1   ]             ║ [ 📚 I+1  ]                 |
|                                      ║                             |
|  Depth 5:  [  ROCK  ][  ROCK  ][  ROCK  ][  ROCK  ][  ROCK  ]    |
|                                                                    |
+------------------------------------------------------------------+
| [Build] [Dwellers] [Storage] [Survival Guide]                     |
+------------------------------------------------------------------+
```

### 12.2 Dweller List
```
+------------------------------------------+
|  DWELLERS (45/50)                        |
+------------------------------------------+
| Name          | Lvl | HP  | Job    | 😊 |
|---------------|-----|-----|--------|-----|
| John Smith    | 15  | 230 | Power  | 85% |
| Jane Doe      | 22  | 380 | Diner  | 92% |
| Bob Builder   | 8   | 120 | Train  | 75% |
| Alice Wonder  | 30  | 520 | Explore| 60% |
| ...           |     |     |        |     |
+------------------------------------------+
```

### 12.3 Dweller Detail
```
+--------------------------------------+
|  JOHN SMITH  Level 15                |
|  [character portrait]                |
+--------------------------------------+
|  HP: ████████████░░  230/280        |
|  RAD: ██░░░░░░░░░░   15%           |
|  XP: ███████░░░░░░   700/1500      |
|  Happiness: 😊 85%                  |
+--------------------------------------+
|  S.P.E.C.I.A.L:                     |
|  S: 7  P: 4  E: 6  C: 3            |
|  I: 5  A: 8  L: 5                   |
+--------------------------------------+
|  Weapon: Hunting Rifle (3-5 dmg)    |
|  Outfit: Wasteland Gear (+2E +1P)   |
|  Pet: Dogmeat (+15% wasteland caps) |
+--------------------------------------+
|  [Equip] [Assign] [Explore] [Quest] |
+--------------------------------------+
```

## 13. Outfits

### 13.1 Outfit Examples
| Outfit               | SPECIAL Bonus    | Source        |
|---------------------|------------------|---------------|
| Vault Suit          | None             | Starting      |
| Wasteland Gear      | +2E, +1P        | Exploration   |
| Lab Coat            | +3I             | Crafting      |
| Power Armor         | +2S, +2E        | Legendary     |
| Formal Wear         | +3C             | Lunchbox      |
| Lucky Pajamas       | +3L             | Lunchbox      |
| Commander Outfit    | +3A, +2P        | Quest         |
| Professor's Outfit  | +5I             | Legendary     |

## 14. Vault Layout Strategy

### 14.1 Optimal Layout Considerations
- Power rooms near top (power failure cascades from bottom)
- Training rooms deeper (less raid exposure)
- 3-wide merged rooms for efficiency
- Elevators create chokepoints for defense
- Living quarters away from production (breeding distracts)

### 14.2 Defense Layout
```
Top floors = armed dwellers in production rooms
Vault door = 2 strongest dwellers
Each room with dwellers can fight invaders
Invaders path: door → room by room → down elevators
```

## 15. Sound Design

| Event                    | Sound                        |
|--------------------------|------------------------------|
| Room built               | Construction hammering       |
| Resource collected       | Satisfying click + sparkle   |
| Rush success             | Cash register + cheering     |
| Rush failure             | Alarm + screeching           |
| Raider attack            | Siren + gunfire              |
| Deathclaw attack         | Roar + heavy footsteps       |
| Dweller leveled up       | Fanfare + sparkle            |
| Lunchbox opening         | Dramatic card reveals        |
| Dweller death            | Sad trombone                 |
| Baby born                | Baby cry + cheer             |

## 16. Constants and Tuning

```
MAX_DWELLERS = 200
MAX_VAULT_WIDTH = 24
MAX_VAULT_DEPTH = 25
STARTING_DWELLERS = 12
STARTING_CAPS = 500
PRODUCTION_TICK = 60 seconds (base)
FOOD_CONSUMPTION_PER_DWELLER = 0.1 per tick
WATER_CONSUMPTION_PER_DWELLER = 0.1 per tick
PREGNANCY_DURATION = 3 hours
CHILD_GROWTH_DURATION = 3 hours
STIMPAK_HEAL_PERCENT = 0.5
RADAWAY_REMOVE_PERCENT = 0.5
RUSH_BASE_SUCCESS = 0.6
RUSH_DECAY_PER_ATTEMPT = 0.1
RUSH_LUCK_BONUS = 0.02 per luck point
REVIVE_COST = dweller.level * 100 caps
EXPLORE_EVENT_INTERVAL = 60 seconds
RAIDER_ATTACK_INTERVAL = 600-1200 seconds (random)
DEATHCLAW_THRESHOLD = 60 dwellers
MAX_SPECIAL_STAT = 10
MAX_DWELLER_LEVEL = 50
HP_PER_LEVEL_BASE = 2.5
HP_PER_ENDURANCE = 0.5
MERGED_ROOM_BONUS = {1: 1.0, 2: 1.15, 3: 1.30}
UPGRADE_PRODUCTION_BONUS = {1: 1.0, 2: 1.5, 3: 2.0}
TRAINING_BASE_HOURS = 2.0
```

## 17. Implementation Priority for AI Recreation

1. Vault grid rendering with room placement
2. Basic resource production (power, food, water)
3. Dweller creation and assignment
4. Resource consumption and depletion effects
5. Room merging and upgrades
6. SPECIAL stats and their effects
7. Rush mechanic
8. Combat system (radroaches, raiders)
9. Training rooms
10. Exploration system
11. Crafting system
12. Quest system
13. Reproduction system
14. Lunchbox/reward system
15. Pets
16. Advanced enemies (deathclaws, radscorpions)
