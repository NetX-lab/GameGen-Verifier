# 21_minecraft - Minecraft (Java Edition, Survival Mode)

## 1. Product Definition
- **Prototype Anchor**: Minecraft Java Edition (Release 1.0 core mechanics, incorporating stable features through modern Survival Mode)
- **Genre Family**: Sandbox / Survival / Open-World Crafting
- **Core Fantasy**: Survive in an infinite, procedurally generated voxel world by mining blocks, crafting tools, building shelter, farming resources, and progressing through three dimensions to defeat the Ender Dragon.
- **Camera / Presentation**: 3D first-person (default) with optional third-person toggle; block-based voxel world at 1-meter cubic resolution.
- **Target Session Length**: Open-ended; typical first-night survival loop is 10-20 minutes, full Ender Dragon progression is 8-40+ hours.
- **Target Skill Curve**: Intuitive punch-a-tree opening; deep mastery through crafting knowledge, redstone engineering, combat skill, and world exploitation.

## 2. Win/Lose Contract
- **Primary Win Condition**: Defeat the Ender Dragon in The End dimension. Credits roll, but the game continues indefinitely.
- **Primary Lose Condition**: Player health reaches 0 (death). Player respawns at spawn point or bed, losing all carried items and experience (items persist as dropped entities for 5 minutes / 6000 ticks).
- **World/Board Definition**: Procedurally generated infinite world (practical limit ~30 million blocks from origin per axis), 3 dimensions: Overworld, Nether, End.
- **Hardcore Variant**: Single life; world is deleted upon death.

## 3. Core Loop (Implementation Sequence)
1. **Gather**: Break blocks (wood, stone, ore) to collect raw materials.
2. **Craft**: Combine materials on crafting grids (2x2 inventory or 3x3 crafting table) to produce tools, weapons, armor, and building blocks.
3. **Build**: Place blocks to construct shelter, farms, and infrastructure.
4. **Survive**: Manage health (20 HP / 10 hearts) and hunger (20 points / 10 drumsticks) through the day/night cycle while avoiding or fighting hostile mobs.
5. **Explore**: Venture into caves, structures, the Nether, and the End to acquire progressively rarer resources.
6. **Progress**: Advance through tool tiers (Wood -> Stone -> Iron -> Diamond -> Netherite), unlock enchanting, brewing, and ultimately reach the Ender Dragon.

## 4. Input Specification
| Action | Default Input | Technical Constraint |
|---|---|---|
| Move Forward / Back / Left / Right | `W / S / A / D` | Continuous movement; speed 4.317 m/s walking |
| Sprint | `Ctrl` (hold) or double-tap `W` | Speed 5.612 m/s; depletes hunger (exhaustion +0.1/m) |
| Jump | `Space` | 1.2522 block height; costs exhaustion +0.05 per jump |
| Sneak / Crouch | `Shift` (hold) | Speed 1.31 m/s; prevents falling off block edges |
| Attack / Mine | `Left Click` | Hold to mine; tap for melee attack; attack cooldown 0.625s (sword) |
| Use / Place / Interact | `Right Click` | Places block, uses item, opens container, interacts with entity |
| Pick Block | `Middle Click` | Selects block type from inventory (creative) or highlights in hotbar |
| Drop Item | `Q` | Drops 1 item; `Ctrl+Q` drops entire stack |
| Open Inventory | `E` | Opens 2x2 craft grid + 36-slot inventory + armor slots |
| Hotbar Select | `1-9` or Scroll Wheel | Selects active hotbar slot |
| Swap Off-Hand | `F` | Moves item to/from off-hand slot |
| Open Chat | `T` | Text entry and command input |
| Pause / Menu | `Esc` | Opens pause menu; pauses game in singleplayer |
| Toggle Perspective | `F5` | Cycles: first-person -> third-person back -> third-person front |
| Debug Screen | `F3` | Shows coordinates, biome, light level, FPS, entity count |

## 5. Top-Level State Machines
### 5.1 Application State Machine
- `Boot`: Load options.txt, resource packs, server list, player profile.
- `TitleScreen`: Singleplayer, Multiplayer, Realms, Options.
- `WorldCreation`: Seed input, game mode, difficulty, world type, bonus chest toggle.
- `WorldLoading`: Terrain generation, spawn point selection, entity initialization.
- `InGame`: Active simulation (substates below).
- `DeathScreen`: "You Died!" with respawn and title screen options.
- `PauseMenu`: (Singleplayer only) Freezes simulation; options, save & quit.

### 5.2 InGame Substate Machine
- `Playing`: Full simulation running, all systems active.
- `Paused`: (Singleplayer) All ticks frozen; menu overlay active.
- `Sleeping`: Player in bed; fast-forward to dawn if all players sleeping; skip to tick 0 (sunrise).
- `RespawnTransition`: Death animation, item drop, respawn delay.
- `DimensionTransition`: Portal animation, chunk loading in target dimension.
- `CreditsRoll`: After Ender Dragon defeat; player returns to Overworld via End Portal.

### 5.3 Player State Machine
- `Idle`: Standing on ground, no movement input.
- `Walking`: Movement at 4.317 m/s base speed.
- `Sprinting`: Movement at 5.612 m/s; requires hunger > 6 (3 drumsticks).
- `Sneaking`: Movement at 1.31 m/s; prevents ledge falls.
- `Jumping`: Ballistic arc; 1.2522 blocks vertical clearance.
- `Swimming`: Water movement at 2.20 m/s; breath meter of 15 seconds (300 ticks).
- `Flying` (Creative only): Free 3D movement at 10.89 m/s.
- `Falling`: Gravity at 32 m/s^2 acceleration; terminal velocity ~78 m/s.
- `Mining`: Hold attack on block; progress bar based on tool speed vs block hardness.
- `Eating`: Hold use with food item; 1.61 seconds (32 ticks) consume time.
- `Hurt`: Knockback + 0.5s (10 tick) invulnerability frames on damage.
- `Dead`: Health <= 0; drop all items and XP; transition to DeathScreen.

## 6. Technical Foundation

### 6.1 World Coordinate System
- **Block coordinates**: Integer (X, Y, Z). Y is vertical (up = positive).
- **World height**: Y = -64 to Y = 320 (384 blocks total in Overworld, post-1.18).
  - Classic (pre-1.18): Y = 0 to Y = 255 (256 blocks).
- **Chunk**: 16 x 16 blocks horizontal, full world height vertical. Basic unit of generation and loading.
- **Region**: 32 x 32 chunks (512 x 512 blocks). Stored as one `.mca` file.
- **Render distance**: Configurable 2-32 chunks.
- **Spawn chunks**: 19 x 19 chunk area around world spawn; always loaded.

### 6.2 Tick System
- **Game tick rate**: 20 ticks per second (TPS). Each tick = 50 ms.
- **Redstone tick**: 2 game ticks = 1 redstone tick (0.1 seconds). 10 redstone ticks per second.
- **Random tick**: Each game tick, 3 random blocks per chunk section (16x16x16) receive a random tick update (used for crop growth, leaf decay, fire spread, etc.).
- **Scheduled tick**: Blocks can schedule future tick updates (e.g., repeaters, water flow).
- **Entity processing**: All entities updated each game tick in deterministic order per chunk.

### 6.3 Light System
- **Light levels**: 0 (total darkness) to 15 (full brightness).
- **Block light**: Emitted by light sources; decreases by 1 per block of distance.
- **Sky light**: Maximum 15 from open sky; decreases underground; affected by time of day.
- **Hostile mob spawning threshold**: Light level <= 0 (post-1.18) or <= 7 (pre-1.18) on the block surface.

| Light Source | Light Level |
|---|---|
| Sunlight (direct) | 15 |
| Torch | 14 |
| Glowstone | 15 |
| Redstone Torch | 7 |
| Lava | 15 |
| Fire | 15 |
| Jack o'Lantern | 15 |
| Sea Lantern | 15 |
| Redstone Lamp (powered) | 15 |
| Brewing Stand | 1 |
| End Portal Frame (active) | 1 |
| Furnace (active) | 13 |

## 7. Block & World System

### 7.1 Block Properties
Every block has the following properties:
- **Hardness**: Determines base mining time. Higher = slower to break.
- **Blast Resistance**: Determines resistance to explosions.
- **Tool Type**: Preferred tool category (pickaxe, axe, shovel, hoe, none).
- **Harvest Level**: Minimum tool tier required to drop the item.
- **Transparency**: Whether light passes through.
- **Solid/Non-solid**: Whether entities collide with it.
- **Flammable**: Whether fire can destroy it.
- **Gravity**: Whether the block falls when unsupported (sand, gravel, concrete powder).

### 7.2 Core Block Hardness Table
| Block | Hardness | Blast Resistance | Preferred Tool | Min. Harvest Tier |
|---|---|---|---|---|
| Dirt | 0.5 | 0.5 | Shovel | None (hand) |
| Grass Block | 0.6 | 0.6 | Shovel | None |
| Sand | 0.5 | 0.5 | Shovel | None |
| Gravel | 0.6 | 0.6 | Shovel | None |
| Clay | 0.6 | 0.6 | Shovel | None |
| Soul Sand | 0.5 | 0.5 | Shovel | None |
| Snow Block | 0.2 | 0.2 | Shovel | None |
| Oak Log | 2.0 | 2.0 | Axe | None |
| Oak Planks | 2.0 | 3.0 | Axe | None |
| Cobblestone | 2.0 | 6.0 | Pickaxe | Wood |
| Stone | 1.5 | 6.0 | Pickaxe | Wood |
| Deepslate | 3.0 | 6.0 | Pickaxe | Wood |
| Sandstone | 0.8 | 0.8 | Pickaxe | Wood |
| Bricks | 2.0 | 6.0 | Pickaxe | Wood |
| Coal Ore | 3.0 | 3.0 | Pickaxe | Wood |
| Iron Ore | 3.0 | 3.0 | Pickaxe | Stone |
| Copper Ore | 3.0 | 3.0 | Pickaxe | Stone |
| Gold Ore | 3.0 | 3.0 | Pickaxe | Iron |
| Lapis Lazuli Ore | 3.0 | 3.0 | Pickaxe | Stone |
| Redstone Ore | 3.0 | 3.0 | Pickaxe | Iron |
| Diamond Ore | 3.0 | 3.0 | Pickaxe | Iron |
| Emerald Ore | 3.0 | 3.0 | Pickaxe | Iron |
| Nether Quartz Ore | 3.0 | 3.0 | Pickaxe | Wood |
| Ancient Debris | 30.0 | 1200.0 | Pickaxe | Diamond |
| Obsidian | 50.0 | 1200.0 | Pickaxe | Diamond |
| Crying Obsidian | 50.0 | 1200.0 | Pickaxe | Diamond |
| Netherrack | 0.4 | 0.4 | Pickaxe | Wood |
| End Stone | 3.0 | 9.0 | Pickaxe | Wood |
| Glowstone | 0.3 | 0.3 | Any | None |
| Glass | 0.3 | 0.3 | None | None |
| Ice | 0.5 | 0.5 | Pickaxe | None |
| Bedrock | Infinity | 3,600,000 | None | Unbreakable |
| Spawner | 5.0 | 5.0 | Pickaxe | None (no drop) |
| Chest | 2.5 | 2.5 | Axe | None |
| Crafting Table | 2.5 | 2.5 | Axe | None |
| Furnace | 3.5 | 3.5 | Pickaxe | Wood |
| Anvil | 5.0 | 1200.0 | Pickaxe | Wood |
| Enchanting Table | 5.0 | 1200.0 | Pickaxe | Wood |
| Iron Block | 5.0 | 6.0 | Pickaxe | Stone |
| Gold Block | 3.0 | 6.0 | Pickaxe | Iron |
| Diamond Block | 5.0 | 6.0 | Pickaxe | Iron |
| TNT | 0.0 | 0.0 | Any | None (instant break) |

### 7.3 Block Breaking Time Formula
```
Base Time = Hardness * multiplier
  - If correct tool and tier: multiplier = 1.5
  - If wrong tool or insufficient tier: multiplier = 5.0

Speed = 1.0 (base, no tool)
  - If correct tool: Speed = Tool Speed Multiplier (see Tool table)
  - If Efficiency enchantment: Speed += (Efficiency_Level^2 + 1)
  - If Haste effect: Speed *= (1 + 0.2 * Haste_Level)
  - If Mining Fatigue: Speed *= 0.3^(min(Fatigue_Level, 4))
  - If underwater without Aqua Affinity: Speed *= 0.2
  - If not on ground: Speed *= 0.2

Break Time (seconds) = Base Time / Speed
  - Minimum: 0.05 seconds (1 game tick) for instant-break
  - Damage per tick = Speed / (Hardness * 30)
  - Block breaks when cumulative damage >= 1.0
```

### 7.4 World Generation

#### Overworld Terrain
- **Sea level**: Y = 63.
- **Surface**: Varies by biome; typically Y = 62-100; mountains up to Y = 256.
- **Caves**: Carver caves (Y = -56 to Y = 180), noise caves (cheese, spaghetti, noodle variants).
- **Ore generation**: See Mining section.
- **Structures**: Villages, dungeons, mineshafts, strongholds (3 per world within ring of 1408-2688 blocks from origin), desert temples, jungle temples, woodland mansions, ocean monuments, witch huts, pillager outposts, ruined portals.

#### Chunk Generation Steps
1. **Noise generation**: 3D Perlin noise to determine terrain shape.
2. **Biome assignment**: Based on temperature, humidity, continentalness, erosion, weirdness, depth parameters.
3. **Surface decoration**: Grass, sand, mycelium, snow based on biome.
4. **Carving**: Caves and ravines carved into terrain.
5. **Structure placement**: Structures placed according to structure set rules.
6. **Feature placement**: Trees, flowers, ores, lakes, lava pools.
7. **Light calculation**: Initial sky and block light propagation.
8. **Entity spawning**: Initial passive mob spawning based on biome.

## 8. Crafting System

### 8.1 Crafting Grid Mechanics
- **Inventory grid**: 2x2 (4 slots). Accessible anywhere via inventory screen.
- **Crafting Table grid**: 3x3 (9 slots). Requires placed crafting table block.
- **Recipe types**: Shaped (pattern matters), Shapeless (only ingredients matter).
- **Output slot**: 1 slot; clicking extracts one craft. Shift-click crafts maximum possible.
- **Pattern flexibility**: Shaped recipes can be shifted horizontally/vertically within the grid if space permits.

### 8.2 Essential Crafting Recipes

#### Basic Materials
| Output | Grid Pattern (3x3, `.` = empty) | Ingredients |
|---|---|---|
| Oak Planks (x4) | `...` / `.L.` / `...` (2x2: `L.`/`..`) | 1 Oak Log (L) |
| Sticks (x4) | `.P.` / `.P.` / `...` | 2 Planks (P) |
| Torch (x4) | `.C.` / `.S.` / `...` | 1 Coal (C) + 1 Stick (S) |
| Crafting Table | `PP.` / `PP.` / `...` | 4 Planks (P) in 2x2 |
| Furnace | `CCC` / `C.C` / `CCC` | 8 Cobblestone (C) |
| Chest | `PPP` / `P.P` / `PPP` | 8 Planks (P) |

#### Tools (Pattern: Material on top rows, Sticks as handle)
| Output | Grid Pattern | Ingredients |
|---|---|---|
| Pickaxe | `MMM` / `.S.` / `.S.` | 3 Material (M) + 2 Sticks (S) |
| Axe | `MM.` / `MS.` / `.S.` | 3 Material (M) + 2 Sticks (S) |
| Shovel | `.M.` / `.S.` / `.S.` | 1 Material (M) + 2 Sticks (S) |
| Hoe | `MM.` / `.S.` / `.S.` | 2 Material (M) + 2 Sticks (S) |
| Sword | `.M.` / `.M.` / `.S.` | 2 Material (M) + 1 Stick (S) |

Material (M) can be: Planks (wood), Cobblestone (stone), Iron Ingot, Gold Ingot, or Diamond.

#### Armor (Material = M)
| Output | Grid Pattern |
|---|---|
| Helmet | `MMM` / `M.M` / `...` |
| Chestplate | `M.M` / `MMM` / `MMM` |
| Leggings | `MMM` / `M.M` / `M.M` |
| Boots | `...` / `M.M` / `M.M` |

#### Weapons & Combat
| Output | Grid Pattern | Ingredients |
|---|---|---|
| Bow | `.SM` / `S.M` / `.SM` | 3 Sticks (S) + 3 String (M) |
| Arrow (x4) | `.F.` / `.S.` / `.E.` | 1 Flint (F) + 1 Stick (S) + 1 Feather (E) |
| Shield | `.P.` / `PIP` / `.P.` | 6 Planks (P) + 1 Iron Ingot (I) |

#### Advanced Blocks
| Output | Grid Pattern | Ingredients |
|---|---|---|
| Enchanting Table | `.B.` / `DOD` / `OOO` | 1 Book (B) + 2 Diamonds (D) + 4 Obsidian (O) |
| Anvil | `III` / `.i.` / `iii` | 3 Iron Blocks (I) + 4 Iron Ingots (i) |
| Brewing Stand | `...` / `.B.` / `CCC` | 1 Blaze Rod (B) + 3 Cobblestone (C) |
| Bookshelf | `PPP` / `BBB` / `PPP` | 6 Planks (P) + 3 Books (B) |
| Book | `.P.` / `.P.` / `.L.` (shapeless) | 3 Paper (P) + 1 Leather (L) |
| Paper (x3) | `...` / `RRR` / `...` | 3 Sugar Cane (R) |
| Bed | `...` / `WWW` / `PPP` | 3 Wool (W, same color) + 3 Planks (P) |

#### Smelting (Furnace Recipes)
| Input | Fuel | Output | XP |
|---|---|---|---|
| Iron Ore | Any fuel | Iron Ingot | 0.7 |
| Gold Ore | Any fuel | Gold Ingot | 1.0 |
| Raw Copper | Any fuel | Copper Ingot | 0.7 |
| Sand | Any fuel | Glass | 0.1 |
| Cobblestone | Any fuel | Stone | 0.1 |
| Raw Beef | Any fuel | Steak | 0.35 |
| Raw Porkchop | Any fuel | Cooked Porkchop | 0.35 |
| Raw Chicken | Any fuel | Cooked Chicken | 0.35 |
| Clay Ball | Any fuel | Brick | 0.3 |
| Wood Log | Any fuel | Charcoal | 0.15 |
| Ancient Debris | Any fuel | Netherite Scrap | 2.0 |

#### Fuel Burn Times
| Fuel Item | Burn Time (seconds) | Items Smelted |
|---|---|---|
| Wooden Slab | 7.5 | 0.75 |
| Stick | 5 | 0.5 |
| Wooden Planks | 15 | 1.5 |
| Wood Log | 15 | 1.5 |
| Coal / Charcoal | 80 | 8 |
| Coal Block | 800 | 80 |
| Blaze Rod | 120 | 12 |
| Lava Bucket | 1000 | 100 |
| Dried Kelp Block | 200 | 20 |

## 9. Mining & Resource Gathering

### 9.1 Ore Distribution (Post-1.18 Overworld)
| Ore | Y-Level Range | Peak Y-Level | Vein Size | Attempts/Chunk | Required Tool Tier |
|---|---|---|---|---|---|
| Coal | 0 to 256 | 96 | 1-17 | 20 | Wood+ |
| Copper | -16 to 112 | 48 | 1-10 | 16 | Stone+ |
| Iron | -64 to 320 | 16 (underground), 232 (mountains) | 1-9 | 20 | Stone+ |
| Gold | -64 to 32 | -16 | 1-9 | 4 | Iron+ |
| Gold (Badlands) | 32 to 256 | 32-256 | 1-9 | extra veins | Iron+ |
| Lapis Lazuli | -64 to 64 | 0 | 1-7 | 2 | Stone+ |
| Redstone | -64 to 16 | -59 | 1-8 | 4 | Iron+ |
| Diamond | -64 to 16 | -59 | 1-8 | 1 | Iron+ |
| Emerald | -16 to 320 | 236 | 1 | 1 (mountain biomes only) | Iron+ |

### 9.2 Ore Distribution (Pre-1.18 / Classic)
| Ore | Y-Level Range | Best Y-Level | Vein Size | Attempts/Chunk |
|---|---|---|---|---|
| Coal | 0-127 | 5-52 (peak) | 1-17 | 20 |
| Iron | 0-63 | 5-54 (peak) | 1-9 | 20 |
| Gold | 0-31 | 5-29 (peak) | 1-9 | 2 |
| Lapis Lazuli | 0-30 | 13-17 (peak) | 1-7 | 1 |
| Redstone | 0-15 | 5-12 (peak) | 1-8 | 8 |
| Diamond | 0-15 | 5-12 (peak) | 1-8 | 1 |
| Emerald | 4-31 | any (uniform, mountains only) | 1 | 1 |

### 9.3 Nether Ores
| Ore | Y-Level Range | Vein Size | Required Tool |
|---|---|---|---|
| Nether Gold Ore | 10-117 | 1-10 | Wood+ (drops nuggets) |
| Nether Quartz Ore | 10-117 | 1-14 | Wood+ |
| Ancient Debris | 8-119 (peak at 15) | 1-3 | Diamond+ |

### 9.4 Silk Touch vs Fortune
- **Silk Touch**: Ore block drops itself (e.g., Diamond Ore block instead of diamond gem). Cannot combine with Fortune.
- **Fortune III**: Increases average drops. Diamond ore: 1 base, up to 4 with Fortune III (average ~2.2). Coal ore similar scaling. Does not affect iron or gold ore (they drop raw ore 1:1).

## 10. Tool & Equipment System

### 10.1 Tool Tier Table
| Tier | Material | Durability | Mining Speed | Attack Damage (Sword) | Attack Speed (Sword) | Enchantability | Harvest Level |
|---|---|---|---|---|---|---|---|
| Wood | Planks | 59 | 2x | 4 (2 hearts) | 1.6 | 15 | 0 |
| Stone | Cobblestone | 131 | 4x | 5 (2.5 hearts) | 1.6 | 5 | 1 |
| Iron | Iron Ingot | 250 | 6x | 6 (3 hearts) | 1.6 | 14 | 2 |
| Gold | Gold Ingot | 32 | 12x | 4 (2 hearts) | 1.6 | 22 | 0 |
| Diamond | Diamond | 1561 | 8x | 7 (3.5 hearts) | 1.6 | 10 | 3 |
| Netherite | Netherite Ingot | 2031 | 9x | 8 (4 hearts) | 1.6 | 15 | 4 |

### 10.2 Weapon Damage Table
| Weapon | Wood | Stone | Iron | Gold | Diamond | Netherite |
|---|---|---|---|---|---|---|
| Sword Damage | 4 | 5 | 6 | 4 | 7 | 8 |
| Sword Attack Speed | 1.6 | 1.6 | 1.6 | 1.6 | 1.6 | 1.6 |
| Sword DPS | 6.4 | 8.0 | 9.6 | 6.4 | 11.2 | 12.8 |
| Axe Damage | 7 | 9 | 9 | 7 | 9 | 10 |
| Axe Attack Speed | 0.8 | 0.8 | 0.9 | 1.0 | 1.0 | 1.0 |
| Axe DPS | 5.6 | 7.2 | 8.1 | 7.0 | 9.0 | 10.0 |
| Pickaxe Damage | 2 | 3 | 4 | 2 | 5 | 6 |
| Shovel Damage | 2.5 | 3.5 | 4.5 | 2.5 | 5.5 | 6.5 |

### 10.3 Bow & Crossbow
| Weapon | Damage (no charge) | Damage (full charge) | Damage (critical) | Draw Time |
|---|---|---|---|---|
| Bow | 1 | 6 | 7-11 (25% crit chance) | 1.0s full charge |
| Crossbow | -- | 6-11 | -- | 1.25s load time |

### 10.4 Tool Durability by Type
Each use of a tool on its intended block costs 1 durability. Using a tool as a weapon costs 2 durability (swords cost 1 for attacks). Bows lose 1 durability per shot. Armor loses 1 durability per hit taken.

| Tool Type | Wood | Stone | Iron | Gold | Diamond | Netherite |
|---|---|---|---|---|---|---|
| Pickaxe | 59 | 131 | 250 | 32 | 1561 | 2031 |
| Axe | 59 | 131 | 250 | 32 | 1561 | 2031 |
| Shovel | 59 | 131 | 250 | 32 | 1561 | 2031 |
| Hoe | 59 | 131 | 250 | 32 | 1561 | 2031 |
| Sword | 59 | 131 | 250 | 32 | 1561 | 2031 |

### 10.5 Armor Defense Table
| Armor Piece | Leather | Gold | Chainmail | Iron | Diamond | Netherite |
|---|---|---|---|---|---|---|
| Helmet | 1 | 2 | 2 | 2 | 3 | 3 |
| Chestplate | 3 | 5 | 5 | 6 | 8 | 8 |
| Leggings | 2 | 3 | 4 | 5 | 6 | 6 |
| Boots | 1 | 1 | 1 | 2 | 3 | 3 |
| **Full Set Total** | **7** | **11** | **12** | **15** | **20** | **20** |
| Armor Toughness (per piece) | 0 | 0 | 0 | 0 | 2 | 3 |
| Full Set Toughness | 0 | 0 | 0 | 0 | 8 | 12 |
| Knockback Resistance (full set) | 0 | 0 | 0 | 0 | 0 | 4 (10% per piece) |

### 10.6 Armor Durability
Base durability multipliers: Helmet x11, Chestplate x16, Leggings x15, Boots x13.

| Material | Multiplier | Helmet | Chestplate | Leggings | Boots |
|---|---|---|---|---|---|
| Leather | 5 | 55 | 80 | 75 | 65 |
| Gold | 7 | 77 | 112 | 105 | 91 |
| Chainmail | 15 | 165 | 240 | 225 | 195 |
| Iron | 15 | 165 | 240 | 225 | 195 |
| Diamond | 33 | 363 | 528 | 495 | 429 |
| Netherite | 37 | 407 | 592 | 555 | 481 |

### 10.7 Armor Damage Reduction Formula
```
Effective Armor = min(20, max(Armor_Points / 5, Armor_Points - Damage / (2 + Toughness / 4)))
Damage Reduction = Effective_Armor / 25
Final Damage = Damage * (1 - Damage_Reduction)
```
- Each armor point provides 4% damage reduction (at 20 points = 80% max base reduction).
- Armor toughness prevents high-damage attacks from bypassing armor.

## 11. Health & Hunger System

### 11.1 Health
- **Maximum HP**: 20 (10 hearts). Each heart = 2 HP.
- **Natural regeneration**: When hunger >= 18 and saturation > 0: heals 1 HP every 0.5 seconds (rapid healing). When hunger >= 18 and saturation = 0: heals 1 HP every 4 seconds.
- **Starvation damage**: When hunger = 0: takes 1 HP damage every 4 seconds. On Easy, stops at 10 HP. On Normal, stops at 1 HP. On Hard, can kill.
- **Fall damage**: (Distance fallen - 3) * 1 HP. No damage for falls <= 3 blocks.
- **Drowning**: 2 HP per second after breath meter expires (15 seconds underwater).
- **Fire/Lava**: Fire deals 1 HP per second. Lava deals 4 HP per half-second.
- **Void damage**: Below Y = -64, player takes 4 HP per half-second.

### 11.2 Hunger System
- **Hunger bar**: 20 points (10 drumsticks). Visible on HUD.
- **Saturation**: Hidden value, 0 to 20. Cannot exceed current hunger value. Depletes before hunger.
- **Exhaustion**: Hidden accumulator. When exhaustion >= 4, subtract 1 saturation (or 1 hunger if saturation = 0) and reset exhaustion to 0.
- **Sprint requirement**: Hunger must be > 6 to sprint.

### 11.3 Exhaustion Costs
| Action | Exhaustion per Unit |
|---|---|
| Swimming (per meter) | 0.01 |
| Breaking a block | 0.005 |
| Sprinting (per meter) | 0.1 |
| Jumping | 0.05 |
| Sprint-jumping | 0.2 |
| Attacking an entity | 0.1 |
| Taking damage (any) | 0.1 |
| Hunger effect (per tick) | 0.1 |
| Regenerating 1 HP | 6.0 |

### 11.4 Food Values
| Food Item | Hunger Restored | Saturation Restored | Total Nourishment | Special Effects |
|---|---|---|---|---|
| Steak (Cooked Beef) | 8 | 12.8 | 20.8 | None |
| Cooked Porkchop | 8 | 12.8 | 20.8 | None |
| Golden Carrot | 6 | 14.4 | 20.4 | None |
| Cooked Salmon | 6 | 9.6 | 15.6 | None |
| Cooked Chicken | 6 | 7.2 | 13.2 | None |
| Cooked Mutton | 6 | 9.6 | 15.6 | None |
| Bread | 5 | 6.0 | 11.0 | None |
| Cooked Cod | 5 | 6.0 | 11.0 | None |
| Baked Potato | 5 | 6.0 | 11.0 | None |
| Beetroot Soup | 6 | 7.2 | 13.2 | None |
| Mushroom Stew | 6 | 7.2 | 13.2 | None |
| Apple | 4 | 2.4 | 6.4 | None |
| Raw Beef | 3 | 1.8 | 4.8 | None |
| Raw Porkchop | 3 | 1.8 | 4.8 | None |
| Raw Chicken | 2 | 1.2 | 3.2 | 30% chance of Hunger effect (30s) |
| Rotten Flesh | 4 | 0.8 | 4.8 | 80% chance of Hunger effect (30s) |
| Spider Eye | 2 | 3.2 | 5.2 | Poison (4s) |
| Golden Apple | 4 | 9.6 | 13.6 | Absorption I (2 min), Regeneration II (5s) |
| Enchanted Golden Apple | 4 | 9.6 | 13.6 | Absorption IV (2 min), Regeneration II (20s), Resistance (5 min), Fire Resistance (5 min) |
| Melon Slice | 2 | 1.2 | 3.2 | None |
| Carrot | 3 | 3.6 | 6.6 | None |
| Potato | 1 | 0.6 | 1.6 | None |
| Cookie | 2 | 0.4 | 2.4 | None |
| Pumpkin Pie | 8 | 4.8 | 12.8 | None |
| Cake (per slice, 7 total) | 2 | 0.4 | 2.4 | Placed as block; eaten without holding |
| Chorus Fruit | 4 | 2.4 | 6.4 | Teleports player randomly within 8 blocks |
| Dried Kelp | 1 | 0.6 | 1.6 | Fastest eating speed (0.865s) |

## 12. Mob System

### 12.1 Passive Mobs
| Mob | HP | Drops | Breeding Food | Spawn Biome |
|---|---|---|---|---|
| Cow | 10 (5 hearts) | Raw Beef (1-3), Leather (0-2) | Wheat | Most Overworld grassy biomes |
| Pig | 10 | Raw Porkchop (1-3) | Carrots, Potatoes, Beetroot | Most Overworld grassy biomes |
| Sheep | 8 (4 hearts) | Mutton (1-2), Wool (1 if killed, 1-3 if sheared) | Wheat | Most Overworld grassy biomes |
| Chicken | 4 (2 hearts) | Raw Chicken (1), Feather (0-2), lays Egg every 5-10 min | Seeds (any) | Most Overworld grassy biomes |
| Horse | 15-30 (varies) | Leather (0-2) | Golden Apple, Golden Carrot | Plains, Savanna |
| Donkey | 15-30 | Leather (0-2) | Golden Apple, Golden Carrot | Plains, Savanna |
| Rabbit | 3 (1.5 hearts) | Raw Rabbit (0-1), Rabbit Hide (0-1), Rabbit's Foot (rare) | Carrot, Dandelion | Multiple biomes |
| Squid | 10 | Ink Sac (1-3) | N/A (cannot breed) | Ocean, River |
| Bat | 6 (3 hearts) | Nothing | N/A | Caves below Y=63 |
| Villager | 20 | Nothing (trades instead) | Food (automatic, requires beds and workstations) | Villages |
| Mooshroom | 10 | Raw Beef (1-3), Leather (0-2); milkable for Mushroom Stew | Wheat | Mushroom Fields only |
| Turtle | 30 | Seagrass (0-2), Bowl (if killed by lightning) | Seagrass | Beach |
| Parrot | 6 | Feather (1-2) | Seeds (tame only, cannot breed) | Jungle |
| Cat / Ocelot | 10 | String (0-2) | Raw Cod, Raw Salmon (taming/breeding) | Villages / Jungle |
| Strider | 20 | String (2-5) | Warped Fungus | Nether lava oceans |

### 12.2 Neutral Mobs
| Mob | HP | Attack Damage (Normal) | Trigger | Behavior |
|---|---|---|---|---|
| Wolf (wild) | 8 (4 hearts) | 3 (4 in pack) | Hit one wolf, whole pack attacks | Pack aggression; tamed wolves have 20 HP |
| Wolf (tamed) | 20 (10 hearts) | 4 | Attacks player's target | Follows owner; sits on command |
| Bee | 10 | 2 + Poison (10s) | Hit bee or destroy nest | Stings once then dies after 50-60s |
| Spider (daytime) | 16 (8 hearts) | 2-3 | Neutral in light level >= 12 | Hostile at night or in dark |
| Enderman | 40 (20 hearts) | 7 (Normal) | Looked at or hit | Teleports randomly; damaged by water |
| Zombified Piglin | 20 | 8 (Normal) | Hit one, group attacks | Group aggression; 20-40s hostility timer |
| Iron Golem | 100 (50 hearts) | 7.5-21.5 | Player attacks villager/golem | Defends villagers; thrown upward |
| Llama | 15-30 | 1 (spit) | Hit by player | Spits once then stops |
| Polar Bear | 30 | 6 (Normal) | Near cub | Only attacks near cubs |
| Dolphin | 10 | 2.5 | Hit by player | Gives player Dolphin's Grace (swimming speed) when near |
| Piglin | 16 | 5-13 (varies by weapon) | Player not wearing gold armor, or opens/mines gold | Barters with gold ingots |

### 12.3 Hostile Mobs
| Mob | HP | Damage (Easy / Normal / Hard) | Behavior | Drops |
|---|---|---|---|---|
| Zombie | 20 | 2.5 / 3 / 4.5 | Melee; burns in daylight; can break doors (Hard) | Rotten Flesh (0-2) |
| Skeleton | 20 | 2-4 / 3-5 / 4-8 (arrow) | Ranged (bow); burns in daylight; strafes | Bone (0-2), Arrow (0-2), rare Bow |
| Creeper | 20 | 22.5 / 43 / 64.5 (explosion) | Silent approach; 1.5s fuse; explodes destroying blocks | Gunpowder (0-2), Music Disc (if killed by skeleton) |
| Spider | 16 | 2 / 3 / 3 | Melee; climbs walls; hostile at night | String (0-2), Spider Eye (0-1) |
| Cave Spider | 12 | 2 / 2 / 3 (+ Poison) | Smaller; poisons on Normal+; found in mineshafts | String (0-2), Spider Eye (0-1) |
| Witch | 26 | Splash potions (varies) | Throws Poison, Harming, Slowness, Weakness potions; drinks healing | Glowstone Dust, Redstone, Sugar, Spider Eye, Gunpowder, Glass Bottle, Stick |
| Slime | 16/4/1 (big/med/small) | 4/2/0 (Normal) | Splits into smaller on death (big->4 med->4 small) | Slimeball (small only) |
| Phantom | 20 | 2 / 3 / 3 | Swoops from sky; spawns if player hasn't slept 3+ days | Phantom Membrane (0-1) |
| Endermite | 8 | 2 / 3 / 3 | Small; hostile to Endermen | Nothing |
| Silverfish | 8 | 1 / 1.5 / 1.5 | Infests stone blocks; calls nearby silverfish | Nothing |
| Drowned | 20 | 2.5 / 3 / 4.5 (melee), trident throw varies | Underwater zombie; some carry tridents | Rotten Flesh, Copper Ingot, rare Trident |
| Husk | 20 | 2.5 / 3 / 4.5 | Desert zombie; inflicts Hunger effect | Rotten Flesh, Iron Ingot (rare) |
| Stray | 20 | Arrow + Slowness | Cold biome skeleton; arrows inflict Slowness | Bone, Arrow, Arrow of Slowness |
| Guardian | 30 | 6 (Normal, laser) | Underwater; laser attack; in ocean monuments | Prismarine Shard, Prismarine Crystal, Raw Cod |
| Elder Guardian | 80 | 8 (Normal, laser) | Boss-like; inflicts Mining Fatigue III (5 min) | Prismarine, Wet Sponge, Tide Armor Trim |
| Blaze | 20 | 4 / 6 / 9 (melee), fireball 5 | Flies; shoots 3 fireballs; found in Nether Fortresses | Blaze Rod (0-1) |
| Ghast | 10 | 6 (Normal, fireball explosion) | Large flying mob; shoots explosive fireballs; deflectable | Ghast Tear (0-1), Gunpowder (0-2) |
| Magma Cube | 16/4/1 | 6/4/3 (Normal) | Nether slime; fire immune; splits like slimes | Magma Cream |
| Wither Skeleton | 20 | 5 / 8 / 12 | Melee; inflicts Wither II (10s); in Nether Fortresses | Bone, Coal, rare Wither Skeleton Skull |
| Hoglin | 40 | 3-9 (Normal) | Nether pig; attacks on sight; afraid of Warped Fungus | Raw Porkchop, Leather |
| Piglin Brute | 50 | 7.5-19.5 | Always hostile; found in Bastion Remnants | Nothing guaranteed |
| Ravager | 100 | 12 (Normal) | Found in Pillager Raids; breaks crops/leaves | Saddle |
| Evoker | 24 | Summons Vexes and Fangs | Found in Woodland Mansions and Raids | Totem of Undying, Emerald |
| Vindicator | 24 | 7.5 / 13 / 19.5 | Melee axe attack; in Mansions and Raids | Emerald, rare Iron Axe |

### 12.4 Boss Mobs
| Boss | HP | Damage | Mechanics | Drops |
|---|---|---|---|---|
| Ender Dragon | 200 (100 hearts) | Melee: 6/10/15, Breath: 3/s | Flies around 10 obsidian pillars; healed by End Crystals; breath attack on perch; charge attack | 12,000 XP, Dragon Egg (first kill only), End Gateway |
| Wither | 300 (150 hearts) | Skull: 5/8/12, Dash: 15 | Spawned by player (4 Soul Sand + 3 Wither Skeleton Skulls); shoots exploding skulls; Phase 2 (<150 HP): arrow-immune, wither armor, dash attack; regenerates 1 HP/second | Nether Star, 50 XP |

### 12.5 Mob Spawning Rules
- Hostile mobs spawn in darkness (light level 0 post-1.18, 7 or below pre-1.18) on solid opaque blocks.
- Spawn attempts: every game tick, up to 1 mob spawning attempt per eligible chunk.
- Mob cap: 70 hostile mobs per player in loaded chunks (singleplayer).
- Passive mob cap: 10. Ambient (bats): 15. Water creatures: 5.
- Despawn: Hostile mobs despawn instantly if > 128 blocks from any player. Begin random despawn if > 32 blocks. Never despawn if named (Name Tag) or holding picked-up items.
- Undead mobs (zombie, skeleton) burn in direct sunlight unless wearing a helmet or in water.

## 13. Day/Night Cycle

### 13.1 Timing
- **Full cycle**: 20 real-time minutes = 24,000 game ticks.
- **Tick rate**: 20 ticks per second. 1 in-game hour = 1,000 ticks = 50 real seconds.
- **Time scale**: 1 real second = 72 in-game seconds.
- **Days per real hour**: 3 complete day/night cycles.

### 13.2 Cycle Phases
| Phase | In-Game Time | Tick Range | Real-Time Duration | Description |
|---|---|---|---|---|
| Sunrise | 06:00 | 0 - 1,000 | 50s | Light increases from 4 to 15 |
| Day | 06:00 - 18:00 | 1,000 - 12,000 | 10 min | Full brightness; hostile mobs burn |
| Sunset | 18:00 - 19:00 | 12,000 - 13,000 | 50s | Light decreases; mobs begin spawning |
| Night | 19:00 - 05:00 | 13,000 - 23,000 | 7 min | Darkness; hostile mob spawning active |
| Sunrise | 05:00 - 06:00 | 23,000 - 24,000 | 50s | Light returns; undead mobs burn |

### 13.3 Sleeping Mechanics
- Player can sleep in a Bed when it is night (tick >= 12,542) or during a thunderstorm.
- In singleplayer: instantly skips to dawn (tick 0).
- In multiplayer: all players must be in beds simultaneously.
- Sets spawn point to the bed location.
- Resets phantom spawn timer (phantoms spawn after 3+ in-game days without sleeping).

### 13.4 Weather System
- **Clear**: Default state.
- **Rain**: Occurs randomly; lasts 12,000-24,000 ticks (10-20 min). Extinguishes fire on entities. Sky darkens (effective sky light drops by ~3). Snow in cold biomes.
- **Thunderstorm**: Rare subset of rain. Lightning strikes randomly; can set fires, turn pigs into Zombified Piglins, create charged Creepers, turn villagers into witches. Light level drops enough for hostile mobs to spawn during day.

## 14. Biomes

### 14.1 Overworld Biomes
| Category | Biome | Temperature | Key Features |
|---|---|---|---|
| **Temperate** | Plains | 0.8 | Flat grassland; villages; horses; sunflowers |
| | Forest | 0.7 | Oak and birch trees; wolves; flowers |
| | Birch Forest | 0.6 | Birch trees exclusively |
| | Dark Forest | 0.7 | Dense roofed canopy; woodland mansions; mushrooms |
| | Flower Forest | 0.7 | Dense flower variety |
| | Swamp | 0.8 | Shallow water; slimes at night; witch huts; lily pads; mangrove trees |
| | River | 0.5 | Connects biomes; salmon, squid |
| | Meadow | 0.5 | Elevated grassland; bees; flowers; villages |
| **Cold** | Taiga | 0.25 | Spruce trees; foxes; berry bushes; villages |
| | Old Growth Taiga | 0.3 | Giant spruce and pine trees; podzol; mossy cobblestone |
| | Snowy Plains | 0.0 | Snow cover; igloos; polar bears; strays |
| | Snowy Taiga | -0.5 | Snow-covered spruce forest |
| | Frozen River | 0.0 | Ice-covered river |
| | Ice Spikes | 0.0 | Packed ice pillars |
| | Frozen Ocean | 0.0 | Icebergs; polar bears |
| **Hot** | Desert | 2.0 | Sand; cacti; dead bushes; desert temples; villages; no rain |
| | Savanna | 1.2 | Acacia trees; llamas; villages; no rain |
| | Badlands (Mesa) | 2.0 | Terracotta; red sand; gold ore at higher Y-levels; mineshafts at surface |
| **Tropical** | Jungle | 0.95 | Tall trees; vines; cocoa; parrots; ocelots; jungle temples; melons; bamboo |
| | Bamboo Jungle | 0.95 | Dense bamboo; pandas |
| **Mountain** | Windswept Hills | 0.2 | Steep terrain; emerald ore; llamas |
| | Stony Peaks | 1.0 | High altitude stone; calcite |
| | Jagged Peaks | -0.7 | Snow and ice; goats |
| | Frozen Peaks | -0.7 | Packed ice peaks |
| | Grove | -0.2 | Snowy spruce hillside |
| | Cherry Grove | 0.5 | Cherry blossom trees; pig, sheep, bee spawns |
| **Underground** | Dripstone Caves | 0.8 | Pointed dripstone; drip formations |
| | Lush Caves | 0.5 | Moss, azalea, glow berries, axolotl |
| | Deep Dark | 0.8 | Sculk blocks; ancient cities; Warden |
| **Ocean** | Ocean | 0.5 | Sea level water; kelp; cod; drowned |
| | Deep Ocean | 0.5 | Deeper; ocean monuments; guardians |
| | Warm Ocean | 0.5 | Coral reefs; tropical fish; sea pickles |
| | Lukewarm Ocean | 0.5 | Kelp; tropical fish |
| | Cold Ocean | 0.5 | Salmon; gravel seabed |
| **Special** | Mushroom Fields | 0.9 | Mycelium; mooshrooms; no hostile mob spawning |

### 14.2 Biome Influence on Gameplay
- **Temperature**: Determines rain vs. snow, foliage/grass color, water color.
- **Mob spawning**: Certain mobs are biome-specific (e.g., polar bears in snowy, parrots in jungle, mooshrooms in mushroom fields).
- **Structures**: Villages generate in plains, desert, savanna, taiga, and snowy plains. Jungle temples in jungle. Desert temples in desert. Witch huts in swamp.
- **Vegetation**: Tree types, flowers, and ground cover determined by biome.

## 15. Dimensions

### 15.1 Overworld
- **Height**: Y = -64 to Y = 320 (384 blocks).
- **Natural light**: Day/night cycle with sun and moon.
- **Bed**: Functional; sets spawn point.
- **Water/Lava**: Water is abundant on surface; lava pools at low Y-levels.
- **Compass**: Points to world spawn.
- **Map**: Functions normally.
- **Clocks**: Function normally.

### 15.2 The Nether
- **Access**: Build a Nether Portal frame (minimum 4x5 obsidian) and ignite with Flint & Steel.
- **Height**: Y = 0 to Y = 128.
- **Coordinate ratio**: 1 Nether block = 8 Overworld blocks (horizontal).
- **No sky**: Bedrock ceiling at Y = 127; perpetual dim red ambient light.
- **No water**: Water cannot be placed; evaporates instantly. Ice melts.
- **Bed**: Explodes violently when used (cannot set spawn).
- **Compass/Clock**: Spin randomly (non-functional).
- **Hostile environment**: Lava oceans at Y = 31; fire everywhere; ghast fireballs.

#### Nether Biomes
| Biome | Key Blocks | Mobs | Features |
|---|---|---|---|
| Nether Wastes | Netherrack, Soul Sand, Gravel | Zombified Piglin, Ghast, Magma Cube, Enderman, Piglin, Strider | Classic Nether; lava seas; Nether Fortress; Glowstone clusters |
| Crimson Forest | Crimson Nylium, Crimson Stem, Nether Wart Block, Shroomlight | Hoglin, Piglin, Zombified Piglin | Red fungal forest; Weeping Vines |
| Warped Forest | Warped Nylium, Warped Stem, Shroomlight | Enderman, Strider | Blue/teal fungal forest; safest Nether biome |
| Soul Sand Valley | Soul Sand, Soul Soil, Basalt | Skeleton, Ghast, Enderman | Blue fire; fossils; basalt pillars |
| Basalt Deltas | Basalt, Blackstone, Magma Block | Magma Cube, Strider | Volcanic landscape; treacherous terrain |

#### Nether Structures
- **Nether Fortress**: Bridge/corridor structure; spawns Blazes and Wither Skeletons; contains Blaze Spawners and Nether Wart.
- **Bastion Remnant**: Piglin stronghold; contains gold blocks, Pigstep music disc, Netherite gear, Snout Armor Trim.
- **Ruined Portal**: Partially built portal frame; gold items in chest.

### 15.3 The End
- **Access**: Find a Stronghold (located 1,408-2,688 blocks from world origin); activate the End Portal by filling 12 End Portal Frames with Eyes of Ender.
- **Eye of Ender**: Crafted from 1 Ender Pearl + 1 Blaze Powder. When thrown, floats toward the nearest Stronghold; 20% chance to shatter on use.
- **Main island**: Central floating island of End Stone; 10 obsidian pillars in a circle; Exit Portal (inactive) at center.
- **Outer islands**: Accessible after defeating the Ender Dragon via End Gateway portal. Chorus trees, End Cities, End Ships.
- **No day/night cycle**: Perpetual dark purple sky.
- **No weather**: No rain or thunderstorms.
- **Bed**: Explodes (same as Nether).
- **Gravity**: Normal.
- **Ender Dragon arena**: 10 obsidian towers (varying heights 76-103 blocks) arranged in a circle of radius 43 blocks around the exit portal.

#### Ender Dragon Fight Mechanics
1. **End Crystals**: 10 crystals atop the obsidian pillars, 2 protected by iron bar cages. Crystals heal the dragon 1 HP per 0.5 seconds. Must be destroyed (melee, bow, snowball).
2. **Dragon behavior**: Circles the pillars (outside ring if crystals remain, inside if destroyed). Periodically strafes player and shoots Dragon's Breath (lingering Harming cloud).
3. **Perching**: Dragon lands on the exit portal fountain periodically. Breath attack for 3 seconds. Vulnerable to melee during perch. Immune to arrows while perching.
4. **Damage immunities**: Immune to fire, lava, explosions (except beds and End Crystals). Takes damage from melee weapons, arrows (while flying), snowballs (1 damage).
5. **Death**: Drops 12,000 XP (first kill; 500 XP on subsequent kills), activates the Exit Portal, spawns the Dragon Egg on the portal (first kill only), and opens End Gateways.
6. **Respawning**: Place 4 End Crystals on the edges of the Exit Portal (one on each cardinal side). Dragon respawns with full health and all obsidian pillars regenerated.

## 16. Combat Mechanics

### 16.1 Attack Cooldown (Java Edition)
- After an attack, the weapon enters a cooldown. The cooldown duration = 1 / Attack_Speed seconds.
- A strength indicator appears below the crosshair showing cooldown progress.
- Attacking before cooldown is full reduces damage: `Damage * (0.2 + (Cooldown_Progress^2) * 0.8)`.
- Critical hits require: cooldown >= 84.8%, player is falling (not on ground), not sprinting, not in water, not on a ladder, not blind.
- Critical hit multiplier: 1.5x damage.

### 16.2 Melee Combat
- **Sweep attack**: When cooldown is full and standing still, sword attack hits all entities within 1 block of the target for 1 + (Attack_Damage * 0.5) sweep damage. Requires sword.
- **Knockback**: Base knockback from attacks; increased by Knockback enchantment (+3 blocks per level) and sprinting (+3 blocks).
- **Shield blocking**: Right-click with shield to block. Blocks 100% of melee and projectile damage from the front (180-degree arc). Axe attacks have a chance to disable shields for 5 seconds.

### 16.3 Ranged Combat
- **Bow**: Hold right-click to charge (1 second for full charge). Damage scales with charge: 1 (no charge) to 6 (full), with 25% chance for critical (7-11 damage). Arrows arc due to gravity; velocity ~60 m/s at full charge.
- **Crossbow**: Hold right-click to load (1.25s), then click to fire. Damage: 6-11. Can fire Firework Rockets with Multishot or Piercing enchantments.
- **Trident**: Melee 9 damage. Thrown: 8 damage. Returns with Loyalty enchantment. Riptide enchantment launches player in water/rain.
- **Arrow types**: Normal, Tipped (carry potion effects), Spectral (glowing outline).

### 16.4 Damage Types and Modifiers
| Damage Source | Base Damage | Modified By |
|---|---|---|
| Melee (player) | Weapon damage | Critical hit (x1.5), Sharpness (+0.5*level + 0.5), Smite/Bane (extra vs. undead/arthropods) |
| Arrow | 1-11 | Power enchant (+0.5*level + 0.5 per level), critical shot |
| Fall | (blocks - 3) HP | Feather Falling enchant (-12%/level, max 48%), Protection (-4%/level) |
| Explosion (Creeper) | Up to 64.5 (Hard) | Distance from center, Blast Protection (-8%/level), armor |
| Fire | 1/s | Fire Resistance (immune), Fire Protection |
| Lava | 4/0.5s | Fire Resistance (immune), Fire Protection |
| Drowning | 2/s | Respiration (extends breath), Water Breathing (immune) |
| Wither effect | 1/2s | Cannot be blocked by armor |
| Poison | 1/1.25s (Poison I) | Cannot kill; stops at 1 HP |
| Starvation | 1/4s | Only when hunger = 0 |
| Void | 4/0.5s | Nothing prevents it |

### 16.5 Protection Enchantment Stacking
```
Effective Protection Factor (EPF) = sum of all relevant enchantment levels
  - Protection: +1 EPF per level (all damage types)
  - Fire Protection: +2 EPF per level (fire/lava)
  - Blast Protection: +2 EPF per level (explosions)
  - Projectile Protection: +2 EPF per level (arrows/fireballs)
  - Feather Falling: +3 EPF per level (fall damage, boots only)

Cap: EPF capped at 20.
Damage Reduction from EPF = min(20, EPF) * 4% = max 80% from enchantments.
Total Reduction = Armor% + Enchantment% (applied sequentially, not additively).
```

## 17. Farming System

### 17.1 Crop Farming
- **Farmland**: Created by using hoe on dirt/grass. Dries out (reverts to dirt) if no water within 4 blocks (horizontal) or not rained on, or if trampled (jumped on).
- **Hydration**: Water source within 4 blocks (taxicab distance) keeps farmland hydrated (darker texture, faster growth).
- **Light requirement**: Crops need light level >= 8 to grow (torch nearby for night growth).
- **Growth mechanic**: Random tick-based. Each random tick has a chance to advance the crop by one growth stage. Optimal growth: alternate rows of different crops with hydrated farmland.

#### Crop Types
| Crop | Seed Source | Growth Stages | Yield | Growth Condition |
|---|---|---|---|---|
| Wheat | Break tall grass (seeds); harvest mature wheat | 8 stages (0-7) | 1 Wheat + 0-3 Seeds | Farmland, light >= 8 |
| Carrot | Found in villages; drop from zombies | 8 stages | 1-5 Carrots | Farmland, light >= 8 |
| Potato | Found in villages; drop from zombies | 8 stages | 1-5 Potatoes (2% Poisonous Potato) | Farmland, light >= 8 |
| Beetroot | Found in villages; dungeon chests | 4 stages | 1 Beetroot + 0-3 Seeds | Farmland, light >= 8 |
| Melon | Crafted from melon slices; found in jungle/dungeon chests | Stem: 8 stages, then spawns melon block adjacent | 3-7 Melon Slices per block | Farmland for stem; needs air/dirt adjacent |
| Pumpkin | Found in various biomes; dungeon chests | Stem: 8 stages, then spawns pumpkin adjacent | 1 Pumpkin block | Same as melon |
| Sugar Cane | Found near water | Grows up to 3 blocks tall | Break top sections, leave base | Must be on sand/dirt adjacent to water |
| Cactus | Found in desert | Grows up to 3 blocks tall | 1 Cactus block per section | Sand only; no adjacent blocks |
| Nether Wart | Found in Nether Fortresses | 4 stages | 2-4 Nether Wart | Soul Sand only; any dimension, any light |
| Cocoa Beans | Found on jungle trees | 3 stages | 1-3 Cocoa Beans | Must be on jungle log |
| Bamboo | Found in jungle/bamboo jungle | Grows 12-16 blocks tall | 1 Bamboo per section | Any dirt-type block |

#### Growth Time Estimates
- Average time per growth stage (ideal conditions): ~5 minutes.
- Average total growth time (wheat, 7 stages): ~35 minutes in ideal conditions; up to 4+ hours worst case.
- Bone Meal: Instantly advances 2-5 random growth stages per use.

### 17.2 Animal Farming
- **Breeding**: Hold breeding food item near two adults of the same species, right-click both. Hearts appear; they produce one baby.
- **Cooldown**: 5 minutes between breeding for each animal.
- **Baby growth**: 20 minutes to mature from baby to adult.
- **XP**: 1-7 XP per breeding.

| Animal | Breeding Food | Product | Special Notes |
|---|---|---|---|
| Cow | Wheat | Raw Beef, Leather, Milk (bucket) | Right-click with bucket for milk (clears status effects) |
| Pig | Carrot, Potato, Beetroot | Raw Porkchop | Rideable with saddle + carrot on a stick |
| Sheep | Wheat | Mutton, Wool (shearable) | Dyeable; wool regrows after eating grass |
| Chicken | Any Seeds | Raw Chicken, Feather, Egg | Lays egg every 5-10 min; egg has 1/8 chance of spawning chick when thrown |
| Horse | Golden Apple, Golden Carrot | Leather | Tameable; rideable with saddle; armor equippable |
| Rabbit | Carrot, Dandelion | Raw Rabbit, Rabbit Hide, Rabbit's Foot (rare) | 6 color variants |
| Bee | Any Flower (lure only) | Honeycomb (shears on nest), Honey Bottle | Pollinate crops (accelerate growth); nest holds 3 bees |

### 17.3 Tree Farming
- Trees grow from saplings planted on dirt/grass with sufficient light (8+) and vertical space.
- Bone Meal can force growth attempt.
- Leaf decay: leaves not connected to a log within 6 blocks will decay, dropping saplings (~5% chance) and apples (oak only, ~0.5%).

| Tree Type | Sapling | Min Space | Wood Type |
|---|---|---|---|
| Oak | Oak Sapling | 1x1 trunk, 5 blocks vertical | Oak Log |
| Birch | Birch Sapling | 1x1, 7 blocks vertical | Birch Log |
| Spruce | Spruce Sapling | 1x1 or 2x2 (giant), 7-16 blocks | Spruce Log |
| Jungle | Jungle Sapling | 1x1 or 2x2 (giant), 5-32 blocks | Jungle Log |
| Acacia | Acacia Sapling | 1x1, 6 blocks vertical | Acacia Log |
| Dark Oak | Dark Oak Sapling | 2x2 only (4 saplings), 7 blocks | Dark Oak Log |
| Cherry | Cherry Sapling | 1x1, 8 blocks vertical | Cherry Log |

## 18. Enchanting System

### 18.1 Enchanting Table Setup
- **Recipe**: 4 Obsidian + 2 Diamonds + 1 Book.
- **Bookshelves**: Each bookshelf within 1 block air gap of the enchanting table increases max enchantment level by ~2.
- **Maximum**: 15 bookshelves = level 30 enchantments.
- **Layout**: Bookshelves must be placed in a ring at the same level or 1 block above the table, with exactly 1 block of air between.

### 18.2 Enchanting Process
1. Place item (tool, weapon, armor, or book) in the left slot.
2. Place 1-3 Lapis Lazuli in the right slot.
3. Three enchantment options appear with level requirements.
4. Top option: costs 1 level + 1 lapis. Middle: 2 levels + 2 lapis. Bottom: 3 levels + 3 lapis.
5. Player must have at least the displayed level requirement (up to 30) but only pays the tier cost (1, 2, or 3 levels).
6. Enchantments are semi-random, seeded by player XP seed, item type, and bookshelf count.

### 18.3 Enchantment List
| Enchantment | Max Level | Applies To | Effect |
|---|---|---|---|
| **Armor Enchantments** | | | |
| Protection | IV | All armor | -4% damage per level (all sources) |
| Fire Protection | IV | All armor | -8% fire damage per level; reduces burn time |
| Blast Protection | IV | All armor | -8% explosion damage per level; reduces knockback |
| Projectile Protection | IV | All armor | -8% projectile damage per level |
| Feather Falling | IV | Boots | -12% fall damage per level |
| Respiration | III | Helmet | +15s breath per level; reduces drowning damage |
| Aqua Affinity | I | Helmet | Removes underwater mining speed penalty |
| Thorns | III | Chestplate | 15% chance per level to deal 1-4 damage to attacker |
| Depth Strider | III | Boots | Reduces water movement slow by 1/3 per level |
| Frost Walker | II | Boots | Creates frosted ice when walking over water |
| Soul Speed | III | Boots | Increases speed on soul sand/soil; damages boots |
| **Weapon Enchantments** | | | |
| Sharpness | V | Sword, Axe | +0.5*level + 0.5 damage |
| Smite | V | Sword, Axe | +2.5*level damage vs. undead |
| Bane of Arthropods | V | Sword, Axe | +2.5*level damage vs. arthropods + Slowness |
| Knockback | II | Sword | +3 blocks knockback per level |
| Fire Aspect | II | Sword | Sets target on fire (4s per level) |
| Looting | III | Sword | +1 max drop per level; increases rare drop chance |
| Sweeping Edge | III | Sword | Increases sweep attack damage: 50%/67%/75% of hit |
| **Tool Enchantments** | | | |
| Efficiency | V | Pickaxe, Axe, Shovel, Hoe | Mining speed + (level^2 + 1) |
| Silk Touch | I | Pickaxe, Axe, Shovel, Hoe | Block drops itself instead of normal drop |
| Fortune | III | Pickaxe, Axe, Shovel, Hoe | Increases certain block drops (mutually exclusive with Silk Touch) |
| Unbreaking | III | All tools, weapons, armor | Chance to not consume durability: 100/(level+1) % chance of consuming |
| Mending | I | All tools, weapons, armor | XP orbs repair item (2 durability per XP) instead of going to XP bar |
| **Bow Enchantments** | | | |
| Power | V | Bow | +25% * (level + 1) arrow damage |
| Punch | II | Bow | +3 blocks knockback per level |
| Flame | I | Bow | Arrows set target on fire (5s) |
| Infinity | I | Bow | Normal arrows not consumed (still need 1); mutually exclusive with Mending |
| **Crossbow Enchantments** | | | |
| Quick Charge | III | Crossbow | Reduces load time by 0.25s per level |
| Multishot | I | Crossbow | Fires 3 arrows for cost of 1 |
| Piercing | IV | Crossbow | Arrows pass through entities (level = max entities pierced) |
| **Special** | | | |
| Curse of Vanishing | I | Any | Item destroyed on death instead of dropping |
| Curse of Binding | I | Armor | Cannot be removed once equipped (until death) |
| Loyalty | III | Trident | Returns to player after thrown (speed scales with level) |
| Riptide | III | Trident | Launches player when thrown in water/rain (mutually exclusive with Loyalty) |
| Channeling | I | Trident | Summons lightning on hit during thunderstorm |
| Impaling | V | Trident | +2.5 damage per level vs. aquatic mobs |

### 18.4 Anvil Mechanics
- Combines two items of the same type, merging enchantments.
- Applies enchanted books to items.
- Renames items.
- Cost increases with each use (prior work penalty). Max cost: 39 levels (anything above says "Too Expensive!").
- Anvil has a chance to degrade each use (3 stages: normal -> chipped -> damaged -> destroyed, 12% chance per use).

### 18.5 Enchantability
Higher enchantability = better chance of high-level and multiple enchantments.

| Material | Enchantability |
|---|---|
| Wood / Netherite | 15 |
| Leather | 15 |
| Stone | 5 |
| Iron | 14 (tools), 9 (armor) |
| Gold | 22 (tools), 25 (armor) |
| Diamond | 10 (tools), 10 (armor) |
| Chain | 12 |

## 19. Brewing & Potions

### 19.1 Brewing Stand
- **Recipe**: 1 Blaze Rod + 3 Cobblestone.
- **Fuel**: Blaze Powder (1 powder = 20 brewing operations).
- **Slots**: 3 bottle slots (bottom), 1 ingredient slot (top), 1 fuel slot.
- **Brew time**: 20 seconds per operation.

### 19.2 Brewing Process
```
1. Fill Glass Bottles with Water (right-click water source) -> Water Bottle
2. Place Water Bottles in Brewing Stand (up to 3)
3. Add Nether Wart -> Awkward Potion (base for most potions)
4. Add effect ingredient -> Effect Potion
5. Optional modifiers:
   - Redstone Dust: Extends duration (usually 3:00 -> 8:00)
   - Glowstone Dust: Increases potency (Level I -> Level II, shorter duration)
   - Gunpowder: Converts to Splash Potion (throwable)
   - Dragon's Breath: Converts Splash to Lingering Potion (area cloud)
   - Fermented Spider Eye: Corrupts effect (e.g., Healing -> Harming)
```

### 19.3 Potion Recipes
| Potion | Ingredient | Effect | Duration (Base / Extended) |
|---|---|---|---|
| Awkward Potion | Nether Wart + Water Bottle | None (base) | -- |
| Potion of Swiftness | Awkward + Sugar | Speed I (+20% move speed) | 3:00 / 8:00 |
| Potion of Swiftness II | Swiftness + Glowstone | Speed II (+40% move speed) | 1:30 / -- |
| Potion of Slowness | Swiftness + Fermented Spider Eye | Slowness I (-15% move speed) | 1:30 / 4:00 |
| Potion of Strength | Awkward + Blaze Powder | Strength I (+3 attack damage) | 3:00 / 8:00 |
| Potion of Strength II | Strength + Glowstone | Strength II (+6 attack damage) | 1:30 / -- |
| Potion of Healing | Awkward + Glistering Melon Slice | Instant Health (heals 4 HP) | Instant |
| Potion of Healing II | Healing + Glowstone | Instant Health II (heals 8 HP) | Instant |
| Potion of Harming | Healing + Fermented Spider Eye | Instant Damage (deals 6 HP) | Instant |
| Potion of Harming II | Harming + Glowstone | Instant Damage II (deals 12 HP) | Instant |
| Potion of Regeneration | Awkward + Ghast Tear | Regen I (heal 1 HP/2.5s) | 0:45 / 1:30 |
| Potion of Regeneration II | Regen + Glowstone | Regen II (heal 1 HP/1.2s) | 0:22 / -- |
| Potion of Poison | Awkward + Spider Eye | Poison I (1 HP/1.25s, can't kill) | 0:45 / 1:30 |
| Potion of Poison II | Poison + Glowstone | Poison II (1 HP/0.4s) | 0:21 / -- |
| Potion of Night Vision | Awkward + Golden Carrot | Night Vision (full brightness) | 3:00 / 8:00 |
| Potion of Invisibility | Night Vision + Fermented Spider Eye | Invisibility (mobs less aggressive) | 3:00 / 8:00 |
| Potion of Fire Resistance | Awkward + Magma Cream | Fire Resistance (immune to fire/lava) | 3:00 / 8:00 |
| Potion of Water Breathing | Awkward + Pufferfish | Water Breathing (no drowning) | 3:00 / 8:00 |
| Potion of Leaping | Awkward + Rabbit's Foot | Jump Boost I (+0.5 blocks) | 3:00 / 8:00 |
| Potion of Leaping II | Leaping + Glowstone | Jump Boost II (+1.25 blocks) | 1:30 / -- |
| Potion of Slow Falling | Awkward + Phantom Membrane | Slow Falling (reduced fall speed, no fall damage) | 1:30 / 4:00 |
| Potion of Weakness | Water Bottle + Fermented Spider Eye | Weakness (-4 attack damage) | 1:30 / 4:00 |
| Potion of Turtle Master | Awkward + Turtle Shell | Slowness IV + Resistance III | 0:20 / 0:40 |

### 19.4 Splash & Lingering Potions
- **Splash Potion**: Add Gunpowder to any potion. Throwable; affects all entities within ~4 block radius. Duration reduced to 75% of base.
- **Lingering Potion**: Add Dragon's Breath to Splash Potion. Creates a cloud on impact lasting 30 seconds; duration reduced to 25% of base. Cloud shrinks over time. Used to craft Tipped Arrows (8 arrows + 1 lingering potion = 8 tipped arrows).

## 20. Redstone System

### 20.1 Core Concepts
- **Redstone dust**: Placed on blocks; transmits signal up to 15 blocks. Signal strength decreases by 1 per block of distance.
- **Signal strength**: Integer 1-15. 0 = no signal (OFF).
- **Power sources**: Generate redstone signals when activated.
- **Transmission**: Redstone dust, repeaters, comparators carry signals.
- **Mechanisms**: React to redstone signals (doors, pistons, lamps, etc.).

### 20.2 Redstone Components
| Component | Type | Behavior |
|---|---|---|
| Redstone Dust | Transmission | Carries signal; -1 strength per block; can go up/down 1 block |
| Redstone Torch | Source | Emits signal strength 15; turns OFF when block it's on is powered |
| Redstone Repeater | Transmission | Refreshes signal to 15; adds 1-4 tick delay (configurable); one-way; lockable |
| Redstone Comparator | Transmission | Compares or subtracts two signals; reads container fill level |
| Lever | Source | Toggle ON/OFF; signal strength 15 |
| Button (Stone) | Source | Pulse: 10 ticks (1 second); signal 15 |
| Button (Wood) | Source | Pulse: 15 ticks (1.5 seconds); signal 15; activated by arrows |
| Pressure Plate | Source | Activated by entity standing on it; signal strength varies |
| Tripwire Hook | Source | Activated when string is broken or walked through |
| Daylight Detector | Source | Signal proportional to sunlight (0-15) |
| Observer | Source | Emits 1-tick pulse when adjacent block state changes |
| Target Block | Source | Signal strength proportional to accuracy of projectile hit (1-15) |
| Redstone Block | Source | Constant signal 15 in all directions; movable by pistons |
| Piston | Mechanism | Pushes up to 12 blocks; normal or sticky (pulls 1 block back) |
| Dispenser | Mechanism | Fires/places items from internal 9-slot inventory |
| Dropper | Mechanism | Drops items from internal inventory |
| Hopper | Mechanism/Transmission | Transfers items between containers; 2.5 items/second; disabled by redstone |
| Redstone Lamp | Mechanism | Emits light level 15 when powered |
| Note Block | Mechanism | Plays a note; pitch determined by number of clicks; instrument by block below |
| TNT | Mechanism | Ignited by redstone; 4-second fuse; explosion power 4 |
| Door/Trapdoor | Mechanism | Opens/closes with signal |
| Piston (Sticky) | Mechanism | Pushes and pulls 1 block; can push up to 12 in a row |

### 20.3 Redstone Tick Timing
- 1 game tick = 0.05 seconds. 1 redstone tick = 2 game ticks = 0.1 seconds.
- Repeater delay: 1, 2, 3, or 4 redstone ticks (0.1-0.4 seconds).
- Comparator delay: 1 redstone tick.
- Piston extension: 0 ticks (instant in some cases) to 1.5 redstone ticks.

## 21. Inventory & UI Layout

### 21.1 Inventory Structure
| Slot Category | Count | Description |
|---|---|---|
| Hotbar | 9 | Bottom row; always visible on HUD; slots 0-8 |
| Main Inventory | 27 | 3 rows of 9 slots; visible when inventory opened |
| Armor: Helmet | 1 | Head slot; accepts helmets and some carved items |
| Armor: Chestplate | 1 | Chest slot; accepts chestplates and elytra |
| Armor: Leggings | 1 | Legs slot; accepts leggings |
| Armor: Boots | 1 | Feet slot; accepts boots |
| Off-Hand | 1 | Shield, torch, map, or any item |
| Crafting Grid | 4 | 2x2 grid in inventory screen |
| Crafting Output | 1 | Result slot |
| **Total Slots** | **46** | Including crafting grid and output |

### 21.2 Stack Sizes
- Most blocks and items: **64 per slot**.
- Some items: **16 per slot** (ender pearls, eggs, snowballs, signs, banners, honey bottles).
- Unstackable: **1 per slot** (tools, weapons, armor, potions, stews, buckets, boats, minecarts, beds, enchanted books, totems).

### 21.3 HUD Elements (In-Game)
```
+--------------------------------------------------+
|  [Hearts: 10 red hearts]   [Armor: shield icons] |
|                                                    |
|              [Crosshair +]                         |
|                                                    |
|  [Hunger: 10 drumsticks]   [XP Bar: green bar]   |
|  [Hotbar: 9 item slots with selected highlight]   |
|  [Held item name text]                             |
+--------------------------------------------------+
```

- **Health bar**: 10 hearts (left side, above hotbar). Flash when taking damage. Absorption hearts are yellow.
- **Hunger bar**: 10 drumsticks (right side, above hotbar). Animate (shake) when hunger effect is active or hunger is low.
- **Armor bar**: Appears above hearts when wearing armor. Up to 10 armor icons (each = 2 armor points).
- **Experience bar**: Green bar above hotbar. Level number displayed in center.
- **Hotbar**: 9 slots with white border highlight on selected slot.
- **Air bubbles**: Appear above hunger when underwater (10 bubbles = 15 seconds of air).
- **Boss bar**: Appears at top center when in range of boss mob (Ender Dragon, Wither, Elder Guardian).
- **Crosshair**: Center screen; attack cooldown indicator below it.
- **Held item name**: Appears briefly above hotbar when switching items.

### 21.4 Container UIs
| Container | Slots | Special Features |
|---|---|---|
| Crafting Table | 9 input + 1 output | 3x3 grid |
| Furnace | 3 (input, fuel, output) | Progress arrow, flame indicator |
| Chest | 27 | Single chest |
| Large Chest | 54 | Two chests side by side |
| Ender Chest | 27 | Shared across all ender chests per player |
| Shulker Box | 27 | Portable; retains contents when broken |
| Enchanting Table | 2 (item + lapis) + 3 options | Bookshelf count affects options |
| Anvil | 2 input + 1 output | Level cost displayed |
| Brewing Stand | 5 (3 bottles + ingredient + fuel) | Bubble and arrow progress indicators |
| Hopper | 5 | Auto-transfers items |
| Dispenser | 9 | Fires contents when powered |
| Villager Trading | Varies by profession | 2 input + 1 output per trade; supply/demand pricing |
| Beacon | 1 (payment) + effect selection | Requires pyramid of iron/gold/diamond/emerald/netherite blocks |
| Smithing Table | 3 (template + equipment + material) | Netherite upgrade; armor trims |

## 22. Experience System
- **XP Orbs**: Dropped by mobs (1-5 typically), mining certain ores (0.1-2.0), smelting, breeding, trading, fishing.
- **Level formula**: XP required increases with level.
  - Levels 0-16: `2*level + 7` XP per level.
  - Levels 17-31: `5*level - 38` XP per level.
  - Levels 32+: `9*level - 158` XP per level.
- Total XP for level 30: 1,395 XP points.
- **Death penalty**: Drop all XP; can recover up to 7 levels worth (capped at 100 points per orb) from death location.
- **Uses**: Enchanting (consumes levels), anvil repairs/combinations (consumes levels), Mending enchantment (consumes orbs to repair gear).

## 23. Audio Design

### 23.1 Music System
- **Overworld**: Ambient music tracks by C418 (Volume Alpha, Volume Beta). Plays intermittently with 10-20 minute gaps of silence between tracks.
- **Nether**: Distinct ominous ambient tracks per biome (Chrysopoeia, Rubedo, etc.).
- **End**: Eerie ambient music; boss music during dragon fight.
- **Creative**: Additional relaxed tracks.
- **Music discs**: 16+ collectible discs playable in Jukebox blocks. Found in dungeon chests or when Creeper is killed by Skeleton arrow.

### 23.2 Sound Effects Categories
| Category | Examples |
|---|---|
| Block breaking/placing | Unique sound per material (wood, stone, dirt, glass, sand, wool, metal) |
| Footsteps | Per-surface material sounds; splashing in water |
| Combat | Sword swing, bow draw/release, arrow impact, shield block, critical hit |
| Mob sounds | Idle, hurt, death, ambient sounds per mob type; Creeper hiss (1.5s warning) |
| Environment | Rain, thunder, lava bubbling, water flowing, fire crackling, wind in caves |
| UI | Inventory open/close, item pickup, XP orb collection, level-up chime |
| Eating | Chewing sounds (1.61 seconds); burp on completion |
| Explosion | TNT, Creeper, fireball impact, bed/respawn anchor in wrong dimension |
| Redstone | Piston extend/retract, door open/close, pressure plate click, note block tones |
| Portal | Nether portal ambient hum; End portal activation |
| Minecart | Rolling on rails; speed-dependent pitch |

### 23.3 Ambient Sound Design
- **Cave sounds**: Random ambient sounds play when player is in a dark area or near a cave. Eerie tones and noises at random intervals.
- **Underwater**: Muffled audio; unique ambient sounds.
- **Nether**: Continuous ambient background per biome; ghast wails audible at distance.
- **End**: Minimal ambient; dragon wing flaps and roars during boss fight.

### 23.4 3D Audio
- Stereo panning based on sound source direction relative to player facing.
- Volume attenuation: sounds attenuate over 16-block radius (most effects).
- Mob sounds can be heard through walls at reduced volume.

## 24. Difficulty Levels
| Setting | Hunger Starvation | Mob Damage Multiplier | Mob Spawning | Special |
|---|---|---|---|---|
| Peaceful | No hunger depletion | No hostile mobs | Hostile mobs despawn instantly | Health regenerates rapidly |
| Easy | Starvation stops at 10 HP | 0.5x + 1 | Normal spawning | Zombies cannot break doors |
| Normal | Starvation stops at 1 HP | 1x (base) | Normal spawning | Default; zombies rarely break doors |
| Hard | Starvation can kill | 1.5x | Increased spawning; mobs can spawn with armor/enchantments | Zombies can break wooden doors; spiders can spawn with status effects |

## 25. Technical Requirements
- **Simulation tick**: Fixed 20 TPS (50 ms per tick) for all game logic.
- **Update order per tick**: Input -> Player movement -> Entity AI -> Entity movement -> Block ticks -> Scheduled ticks -> Redstone -> Weather -> Time -> Chunk loading/unloading.
- **Random number generation**: Seeded world generation (64-bit seed); entity AI uses separate RNG streams.
- **Chunk loading**: Lazy chunks (only block updates), entity-ticking chunks (full simulation), border chunks.
- **Save format**: NBT (Named Binary Tag) for entities and block entities; Anvil format for chunk storage in region files (.mca).
- **Entity limit**: No hard cap; performance-based practical limits (~200-300 entities in view).
- **Block entity limit**: Tiles with extra data (chests, signs, spawners, beacons) stored as block entities.
- **Render distance**: Client-configurable 2-32 chunks; server can enforce maximum.
- **View distance**: Server-configurable; determines entity simulation range.

### 25.1 Performance Budget
- Target: 60 FPS render, 20 TPS simulation.
- Chunk generation: Async, does not block game thread.
- Light updates: Propagated incrementally to avoid frame spikes.
- Entity processing: Batched per chunk; LOD for distant entities.
- Redstone: Updates propagated breadth-first to avoid stack overflow on large circuits.

### 25.2 World Save & Load
- **Auto-save**: Every 6000 ticks (5 minutes) in singleplayer.
- **Save data**: Player position/inventory/health, chunk data (blocks + entities + block entities), world time, weather, difficulty.
- **Level.dat**: World metadata (seed, spawn point, game rules, time, weather).
- **Player data**: Individual .dat files per player (UUID-named).
- **Region files**: 32x32 chunk regions stored in `/region/r.X.Z.mca`.

## 26. Telemetry (For Evaluation and Balancing)
- Time survived
- Blocks mined / placed (by type)
- Mobs killed (by type)
- Deaths (by cause)
- Items crafted (by type)
- Distance traveled (by transport type: walk, sprint, swim, boat, minecart, elytra, horse)
- Dimensions visited
- Achievements / Advancements completed
- Tool tier progression timeline
- XP earned / spent
- Trades completed with villagers
- Bosses defeated

## 27. Accessibility and UX Safety
- Remappable controls for keyboard and mouse.
- Controller support with customizable bindings.
- Independent audio sliders: Master, Music, Jukebox/Note Blocks, Weather, Blocks, Hostile Creatures, Friendly Creatures, Players, Ambient/Environment.
- GUI scale: Auto, Small, Normal, Large (1-4x).
- Chat text size and opacity configurable.
- Subtitles: Directional sound indicators with text labels.
- Colorblind mode: Not built-in, but resource packs can modify textures.
- Brightness / Gamma: Adjustable from "Moody" (realistic) to "Bright" (no dark areas).
- Reduced motion: FOV effects toggle.
- Auto-jump: Toggleable (automatically jumps when approaching 1-block step).
- Narrator: Reads chat messages and UI text aloud (toggleable).
- Text-to-speech for menu navigation.

## 28. QA Acceptance Matrix
1. All tool tiers can mine their appropriate block types within expected break times.
2. Crafting recipes produce correct output with correct ingredient consumption.
3. Hunger and health regeneration follow documented formulas precisely.
4. Mob spawning respects light level thresholds, biome restrictions, and mob caps.
5. Day/night cycle completes in exactly 20 real-time minutes (24,000 ticks).
6. Nether portal correctly links coordinates at 1:8 ratio.
7. Ender Dragon fight sequence: all 10 crystals healable, destroyable; dragon perches; death triggers XP, portal, egg.
8. Enchanting table respects bookshelf count and level requirements.
9. Brewing stand produces correct potion from documented ingredient + base combinations.
10. Armor damage reduction matches formula within 0.01 HP tolerance.
11. Redstone signal propagation: strength decreases by 1 per block; repeaters refresh to 15.
12. Crop growth occurs only with sufficient light and proper farmland conditions.
13. Fall damage = (distance - 3) HP, verified to 0 for falls <= 3 blocks.
14. All food items restore documented hunger and saturation values.
15. World generation produces documented structures in correct biomes.
16. Item stacking respects per-item stack size limits.
17. Death drops all inventory items and XP; items persist 5 minutes at death location.
18. Dimension transitions preserve player state (health, hunger, inventory).
19. Save/load cycle preserves complete world state without data loss.
20. Peaceful difficulty: no hostile mobs spawn; existing hostiles despawn; health regenerates.
