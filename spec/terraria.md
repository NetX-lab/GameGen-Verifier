# Terraria — Complete Game Specification

## 1. Game Overview

Terraria is a 2D sandbox action-adventure game featuring exploration, crafting, building,
and combat across a procedurally generated world. Players mine resources, fight enemies,
build structures, and progress through a series of boss battles that unlock new biomes,
enemies, and items. The game has distinct pre-Hardmode and Hardmode phases.

Platform: Single-player (or multiplayer), 2D side-scrolling tile-based.
World sizes: Small (4200x1200), Medium (6400x1800), Large (8400x2400) tiles.
Tile size: 16x16 pixels.
Physics: Gravity-based platformer with grappling hooks, wings, etc.

## 2. Technical Foundation

### 2.1 World Structure
```
struct World {
    tiles: 2D_array[width][height]  // Each tile: type, wall, liquid, wire
    npcs: list[NPC]
    enemies: list[Enemy]
    projectiles: list[Projectile]
    items_on_ground: list[DroppedItem]
    time_of_day: float              // 0.0-24.0 (4:30 AM start)
    is_day: boolean                 // 4:30 AM - 7:30 PM
    hardmode: boolean               // Activated after Wall of Flesh
    events: ActiveEvents
    weather: WeatherState
    world_evil: enum(CORRUPTION, CRIMSON)
}

struct Tile {
    type: TileType          // 0=air, 1=dirt, 2=stone, etc. (500+ types)
    wall: WallType          // Background wall type
    liquid: enum(NONE, WATER, LAVA, HONEY, SHIMMER)
    liquid_amount: 0-255
    wire: bitmask           // Red, Blue, Green, Yellow wires
    is_active: boolean      // For actuated tiles
    frame_x: integer        // Sprite frame
    frame_y: integer
}
```

### 2.2 World Generation Layers
```
Surface: 0 to ~surface_level (top 15-20%)
Underground: surface to ~cavern_level (15-35%)
Cavern: cavern_level to ~underworld_level (35-85%)
Underworld: bottom 15% (lava, hellstone, Wall of Flesh arena)
Space: above surface (at very top, reduced gravity)
```

### 2.3 Biomes
| Biome          | Location         | Unique Features                        | Key Resources        |
|---------------|------------------|----------------------------------------|----------------------|
| Forest        | Surface center   | Trees, grass, basic enemies            | Wood, gel, herbs      |
| Desert        | Surface          | Sand, antlions, sandstorms             | Sand, fossils         |
| Snow/Ice      | Surface          | Ice, snow, cold enemies                | Ice, boreal wood      |
| Jungle        | Surface/UG       | Dense foliage, hard enemies            | Jungle spores, vines  |
| Corruption    | Surface/UG       | Purple, Eaters, chasms                 | Shadow orbs, demonite |
| Crimson       | Surface/UG       | Red, Crimeras, chasms                  | Crimson hearts, crimtane |
| Ocean         | World edges      | Water, sharks, shells                  | Coral, shark fins     |
| Mushroom       | Underground     | Glowing mushrooms                      | Glowing mushrooms     |
| Dungeon       | Surface (locked) | Locked until Skeletron beaten          | Dungeon bricks, keys  |
| Underworld    | Bottom           | Lava, hellstone, demons                | Hellstone, obsidian   |
| Hallow (HM)   | Surface/UG      | Pastel colors, unicorns (post-WoF)    | Crystal shards, souls |

## 3. Player System

### 3.1 Player Stats
```
struct Player {
    hp: integer              // 100 base, max 500 (via Life Crystals/Fruit)
    max_hp: integer
    mana: integer            // 0 base, max 200 (via Mana Crystals) + 200 from armor
    max_mana: integer
    defense: integer         // Damage reduction = defense * 0.5
    damage_bonus: float      // Percentage bonus per damage type
    speed: float             // Movement speed multiplier
    position: Vec2
    velocity: Vec2
    inventory: Inventory     // 50 slots + equipment
    armor: ArmorSet          // Head, Body, Legs
    accessories: list[Accessory]  // 5-7 slots
    buffs: list[Buff]
    debuffs: list[Debuff]
    coins: integer           // Copper, silver, gold, platinum (base unit: copper)
}
```

### 3.2 Health Progression
```
Starting HP: 100
Life Crystal: +20 HP (found underground, 15 total = 400 HP max pre-HM)
Life Fruit: +5 HP (found in jungle, Hardmode, 20 total = 500 HP max)
Total max: 500 HP
```

### 3.3 Coin System
```
1 Platinum = 100 Gold
1 Gold = 100 Silver
1 Silver = 100 Copper
// Coins drop from enemies and are primary currency
// Death penalty: drop coins (half in normal, less in softcore)
```

## 4. Crafting System

### 4.1 Crafting Stations
| Station           | Materials to Craft    | Unlocks                          |
|------------------|----------------------|----------------------------------|
| Workbench        | 10 Wood              | Basic items, furniture           |
| Furnace          | 20 Stone, 4 Wood, 3 Torches | Smelting ores to bars    |
| Anvil (Iron)     | 5 Iron Bars          | Metal tools, armor, weapons      |
| Mythril Anvil    | 10 Mythril Bars      | Hardmode metal items             |
| Demon/Crimson Altar| Found in world     | Boss summoning items             |
| Tinkerer's Workshop| 10 Gold (buy)      | Combine accessories              |
| Alchemy Station  | Placed Bottle on table| Potions                         |
| Sawmill          | 10 Wood, 2 Iron, 1 Chain | Advanced wood furniture     |
| Loom             | 12 Wood              | Silk, cloth items                |
| Hellforge        | Found in Underworld  | Hellstone bars                   |
| Adamantite Forge | 30 Adamantite Ore    | Hardmode bars                    |

### 4.2 Key Crafting Recipes (Partial)
| Item               | Materials                    | Station        |
|-------------------|------------------------------|----------------|
| Wooden Sword      | 7 Wood                       | Workbench      |
| Copper Pickaxe    | 12 Copper Bars, 4 Wood       | Anvil          |
| Iron Broadsword   | 8 Iron Bars                  | Anvil          |
| Gold Armor (set)  | 75 Gold Bars                 | Anvil          |
| Night's Edge      | Blade of Grass + Muramasa + Fiery Greatsword + Blood Butcherer | Demon Altar |
| Ironskin Potion   | Bottled Water + Daybloom + Iron Ore | Alchemy Station |
| Campfire          | 10 Wood, 5 Torches           | Hand           |
| Torch             | 1 Wood, 1 Gel                | Hand           |

## 5. Ore and Bar Progression

### 5.1 Pre-Hardmode Ores
| Ore        | Bar Recipe    | Pickaxe Needed | Tier |
|-----------|--------------|----------------|------|
| Copper    | 3 Ore → 1 Bar| Any            | 1    |
| Tin       | 3 Ore → 1 Bar| Any            | 1    |
| Iron      | 3 Ore → 1 Bar| Copper/Tin     | 2    |
| Lead      | 3 Ore → 1 Bar| Copper/Tin     | 2    |
| Silver    | 4 Ore → 1 Bar| Iron/Lead      | 3    |
| Tungsten  | 4 Ore → 1 Bar| Iron/Lead      | 3    |
| Gold      | 4 Ore → 1 Bar| Silver/Tungsten| 4    |
| Platinum  | 4 Ore → 1 Bar| Silver/Tungsten| 4    |
| Demonite  | 3 Ore → 1 Bar| Gold/Platinum  | 5    |
| Crimtane  | 3 Ore → 1 Bar| Gold/Platinum  | 5    |
| Hellstone | 3 Ore+1 Obsidian→1 Bar| Deathbringer/Nightmare | 6 |

### 5.2 Hardmode Ores (spawned by smashing altars)
| Ore          | Bar Recipe    | Pickaxe Needed      | Tier |
|-------------|--------------|---------------------|------|
| Cobalt      | 3 Ore → 1 Bar| Molten Pickaxe      | 7    |
| Palladium   | 3 Ore → 1 Bar| Molten Pickaxe      | 7    |
| Mythril     | 4 Ore → 1 Bar| Cobalt/Palladium    | 8    |
| Orichalcum  | 4 Ore → 1 Bar| Cobalt/Palladium    | 8    |
| Adamantite  | 5 Ore → 1 Bar| Mythril/Orichalcum  | 9    |
| Titanium    | 5 Ore → 1 Bar| Mythril/Orichalcum  | 9    |
| Chlorophyte | 6 Ore → 1 Bar| Pickaxe Axe (HM boss)| 10  |
| Luminite    | 4 Ore → 1 Bar| N/A (drops from Moon Lord) | 11 |

## 6. Boss Progression

### 6.1 Pre-Hardmode Bosses
| Boss              | HP     | Defense | Summon Method                    | Key Drops                  |
|-------------------|--------|---------|----------------------------------|----------------------------|
| King Slime        | 2000   | 10      | Slime Crown / random spawn      | Ninja armor, Slime Hook    |
| Eye of Cthulhu    | 2800   | 12      | Suspicious Looking Eye at night  | Demonite/Crimtane Ore      |
| Eater of Worlds   | 7500*  | 0-2     | Smash 3 Shadow Orbs / Worm Food | Shadow Scale, Demonite     |
| Brain of Cthulhu  | 1000+  | 14      | Smash 3 Crimson Hearts          | Tissue Sample, Crimtane    |
| Queen Bee         | 3400   | 8       | Break larva in Jungle hive      | Bee weapons, Bee armor     |
| Skeletron         | 4400   | 10      | Talk to Old Man at night        | Bone weapons, Dungeon access|
| Wall of Flesh     | 8000   | 12      | Drop Guide Voodoo Doll in lava  | Pwnhammer, Hardmode start |

### 6.2 Hardmode Bosses
| Boss              | HP      | Defense | Summon Method                   | Key Drops                   |
|-------------------|---------|---------|----------------------------------|-----------------------------|
| The Twins         | 43000*  | 10-36   | Mechanical Eye at night          | Souls of Sight, Hallowed Bars|
| The Destroyer     | 80000   | 0-30    | Mechanical Worm at night         | Souls of Might, Hallowed Bars|
| Skeletron Prime   | 28000   | 24-48   | Mechanical Skull at night        | Souls of Fright, Hallowed Bars|
| Plantera          | 30000   | 14-36   | Break Plantera's Bulb in Jungle | Temple Key, Plantera drops |
| Golem             | 39000   | 26      | Lihzahrd Power Cell on altar    | Sun Stone, Golem drops     |
| Duke Fishron      | 50000   | 50      | Truffle Worm in Ocean           | Fishron Wings, Tsunami     |
| Lunatic Cultist   | 32000   | 42      | Kill Cultists at Dungeon        | Starts Lunar Events        |
| Moon Lord         | 145000* | 50-70   | Defeat 4 Celestial Pillars      | Luminite, Endgame weapons  |

## 7. Enemy System

### 7.1 Common Enemies by Biome
| Enemy          | Biome       | HP   | Damage | Defense | Drops              |
|---------------|-------------|------|--------|---------|---------------------|
| Blue Slime    | Surface     | 25   | 7      | 2       | Gel                 |
| Zombie        | Surface(N)  | 45   | 14     | 6       | Shackle, Zombie Arm |
| Demon Eye     | Surface(N)  | 60   | 18     | 2       | Lens, Black Lens    |
| Skeleton      | Underground | 60   | 20     | 8       | Hook, Bones         |
| Giant Bat     | Underground | 46   | 20     | 4       | Chain, Depth Meter  |
| Hornet        | Jungle      | 50   | 34     | 12      | Stinger, Vine       |
| Demon         | Underworld  | 120  | 32     | 8       | Demon Scythe        |
| Pixie (HM)    | Hallow      | 150  | 55     | 20      | Pixie Dust, Fast Clock|
| Wraith (HM)   | Surface(N)  | 200  | 75     | 18      | Dark Shard          |

### 7.2 Damage Calculation
```
incoming_damage = max(1, enemy.damage - player.defense * 0.5)
// +/- 15% random variance
// Critical hits: 2x damage (player only, some weapons/accessories boost crit)
// Damage types: melee, ranged, magic, summon (each can have separate bonuses)
```

## 8. NPC Housing

### 8.1 Housing Requirements
```
Valid house requires:
  - Enclosed area (walls, ceiling, floor)
  - Minimum size: 10 tiles wide x 6 tiles tall (60 tiles area, inner)
  - Maximum size: 750 tiles (inner area)
  - Background walls (player-placed, not natural)
  - At least 1 light source (torch, candle, etc.)
  - At least 1 flat surface (table, workbench, etc.)
  - At least 1 comfort item (chair, bed, etc.)
  - At least 1 door or platform for entry/exit
  - Not in Corruption/Crimson biome
```

### 8.2 NPCs
| NPC            | Condition                              | Sells/Does                        |
|---------------|----------------------------------------|-----------------------------------|
| Guide         | Always present (starting NPC)          | Crafting recipes, tips            |
| Merchant      | 50+ Silver in player inventory         | Basic supplies, torches, rope     |
| Nurse         | Eye of Cthulhu defeated                | Heals player for gold             |
| Arms Dealer   | Have a gun in inventory                | Ammo, guns                        |
| Dryad         | Any boss defeated                      | Herbs, purification powder        |
| Demolitionist | Merchant + explosives in inventory     | Bombs, dynamite                   |
| Goblin Tinkerer| Rescue from Underground (after Goblin Army) | Reforging, Tinkerer's Workshop |
| Mechanic      | Rescue from Dungeon                    | Wires, wrenches, mechanisms       |
| Wizard         | Rescue from Caverns (Hardmode)        | Spell Tomes, Crystal Ball         |
| Steampunker   | Any Mechanical Boss defeated           | Clentaminator, Jetpack            |
| Witch Doctor  | Queen Bee defeated                     | Summoner items, Pygmy Staff       |
| Pirate        | Pirate Invasion defeated               | Pirate furniture, Parrot Cracker  |

## 9. Tool Progression

### 9.1 Pickaxes
| Pickaxe          | Pickaxe Power | Damage | Speed | Material/Source          |
|-----------------|---------------|--------|-------|--------------------------|
| Copper Pickaxe  | 35%           | 4      | 15    | 12 Copper Bars           |
| Iron Pickaxe    | 40%           | 5      | 13    | 12 Iron Bars             |
| Silver Pickaxe  | 45%           | 6      | 11    | 12 Silver Bars           |
| Gold Pickaxe    | 55%           | 6      | 10    | 12 Gold Bars             |
| Nightmare Pick  | 65%           | 9      | 15    | 12 Demonite + 6 Shadow Scale |
| Molten Pickaxe  | 100%          | 12     | 18    | 20 Hellstone Bars        |
| Cobalt Drill    | 110%          | 10     | 15    | 15 Cobalt Bars           |
| Mythril Drill   | 150%          | 15     | 12    | 15 Mythril Bars          |
| Adamantite Drill| 180%          | 20     | 8     | 18 Adamantite Bars       |
| Pickaxe Axe     | 200%          | 27     | 7     | 18 Hallowed + Mech Boss  |
| Luminite Pickaxe| 225%          | 80     | 5     | Luminite Bars + Pillar   |

## 10. Weapon Classes

### 10.1 Melee Weapons (Sample)
| Weapon            | Damage | Speed | Knockback | Source               |
|------------------|--------|-------|-----------|----------------------|
| Copper Shortsword| 5      | Fast  | 4.0       | Crafted              |
| Gold Broadsword  | 13     | Fast  | 5.0       | Crafted              |
| Night's Edge     | 42     | Fast  | 4.5       | Crafted (pre-HM best)|
| Excalibur        | 72     | Fast  | 4.5       | Hallowed Bars        |
| Terra Blade      | 115    | Fast  | 6.5       | True Night + True Excal|
| Zenith           | 190    | Insane| 6.5       | Endgame crafting     |

### 10.2 Ranged Weapons (Sample)
| Weapon          | Damage | Speed   | Ammo Type   | Source                |
|----------------|--------|---------|-------------|------------------------|
| Wooden Bow     | 4      | Normal  | Arrows      | Crafted               |
| Minishark      | 6      | Very Fast| Bullets    | Arms Dealer (35 Gold) |
| Megashark      | 25     | Very Fast| Bullets    | Crafted (Hardmode)    |
| Stynger        | 62     | Normal  | Stynger Bolts| Golem drop           |
| S.D.M.G.       | 85     | Very Fast| Bullets   | Moon Lord drop        |

### 10.3 Magic Weapons (Sample)
| Weapon           | Damage | Mana | Speed  | Source                  |
|-----------------|--------|------|--------|--------------------------|
| Wand of Sparking| 8      | 2    | Fast   | Found Underground       |
| Water Bolt      | 17     | 10   | Normal | Dungeon shelves         |
| Crystal Storm   | 25     | 4    | Fast   | Hallowed Bars + Souls   |
| Razorblade Typhoon| 85   | 16   | Fast   | Duke Fishron            |
| Last Prism      | 100    | 12   | Fast   | Moon Lord               |

## 11. Movement and Accessories

### 11.1 Key Accessories
| Accessory         | Effect                               | Source              |
|------------------|--------------------------------------|---------------------|
| Hermes Boots     | Run fast                             | Underground chests  |
| Cloud in a Bottle| Double jump                          | Underground chests  |
| Grappling Hook   | Grapple to surfaces                  | Crafted/found       |
| Rocket Boots     | Short flight                         | Goblin Tinkerer     |
| Spectre Boots    | Run + flight (combined)              | Tinkerer's Workshop |
| Wings (various)  | Extended flight                      | Hardmode crafting   |
| Ankh Shield      | Immunity to many debuffs             | Complex crafting    |
| Terraspark Boots | Run, fly, walk on water/lava, ice    | Complex crafting    |

### 11.2 Movement Physics
```
walk_speed = 15 mph (base)
run_speed = 30 mph (with boots)
max_fall_speed = 51 mph
jump_height = 6 tiles (base)
double_jump = +6 tiles
wings_flight_time = 1.5-3 seconds depending on wing type
gravity = 0.4 tiles/tick^2
terminal_velocity = 10 tiles/tick
```

## 12. Events

### 12.1 Invasion Events
| Event            | Trigger                    | Enemy Types              | Reward              |
|-----------------|---------------------------|--------------------------|---------------------|
| Goblin Army     | Random (after Shadow Orb)  | Goblin Warrior, Sorcerer | Goblin Tinkerer NPC |
| Pirate Invasion | Random (Hardmode)          | Pirates, Flying Dutchman | Pirate NPC, Cutlass |
| Martian Madness | Martian Probe escape (HM)  | Martians, Saucers       | Cosmic Car Key      |
| Frost Legion    | Snow Globe (Hardmode)      | Snowmen, Frost archers  | Snow Block items    |
| Pumpkin Moon    | Pumpkin Moon Medallion     | Pumpking, Mourning Wood | Spooky armor        |
| Frost Moon      | Naughty Present            | Santa-NK1, Everscream   | Elf armor, weapons  |
| Lunar Events    | Defeat Lunatic Cultist     | 4 Celestial Pillars     | Lunar Fragments     |

## 13. World Events and Weather

| Event/Weather    | Effect                              | Duration          |
|-----------------|-------------------------------------|-------------------|
| Blood Moon      | Harder enemies, zombie doors        | One night          |
| Solar Eclipse   | Hardmode surface enemies at day     | One day            |
| Rain            | Special fish, some enemies          | Random duration    |
| Slime Rain      | Slimes fall from sky, King Slime    | Random             |
| Sandstorm       | Desert enemies, reduced visibility  | Random             |
| Meteor          | After smashing Shadow Orb           | Permanent (mineable)|

## 14. UI Layout

```
+------------------------------------------------------------------+
| HP: ♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥♥ 400/400                              |
| MP: ★★★★★★★★★★ 200/200                                          |
| Buffs: [🗡+10%] [🛡+8] [⚡speed] [💨featherfall]                |
+------------------------------------------------------------------+
|                                                                    |
|                                                                    |
|              2D SIDE-SCROLLING WORLD VIEW                          |
|                                                                    |
|           [sky / surface / underground]                             |
|           [player character in center]                             |
|           [enemies, tiles, items visible]                          |
|                                                                    |
|                                                                    |
+------------------------------------------------------------------+
| Hotbar: [1:Pickaxe][2:Sword][3:Bow][4:Torch][5:Potion][...][10]  |
+------------------------------------------------------------------+
| Minimap (top-right corner): [small map view]                       |
+------------------------------------------------------------------+
```

## 15. Constants

```
MAX_HP = 500
MAX_MANA = 400
INVENTORY_SLOTS = 50
HOTBAR_SLOTS = 10
ACCESSORY_SLOTS = 5 (7 in expert)
ARMOR_SLOTS = 3 (head, body, legs)
STACK_SIZE = 9999 (most items), 1 (weapons/tools/accessories)
COIN_CONVERSION = 100
DAY_LENGTH = 24 minutes real time (15 day, 9 night)
TILE_SIZE = 16
GRAVITY = 0.4
MAX_FALL = 10
WORLD_SMALL = (4200, 1200)
WORLD_MEDIUM = (6400, 1800)
WORLD_LARGE = (8400, 2400)
NPC_HAPPINESS_RANGE = 25-150 (affects prices)
DEFENSE_MULTIPLIER = 0.5
CRIT_MULTIPLIER = 2.0
```

## 16. Implementation Priority

1. Tile-based world rendering with scrolling
2. Player movement and physics (gravity, jumping)
3. Tile mining and placement
4. Basic crafting (workbench, furnace)
5. Inventory system
6. Day/night cycle
7. Basic enemies (slimes, zombies)
8. Ore progression and smelting
9. Tool/weapon crafting and combat
10. Underground exploration and world generation
11. NPC housing and spawning
12. Boss fights (Eye of Cthulhu first)
13. Biome generation
14. Hardmode transition
15. Advanced crafting and progression
16. Events and invasions
