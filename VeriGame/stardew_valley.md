# 18_stardew_valley - Stardew Valley

## 1. Product Definition
- **Prototype Anchor**: Stardew Valley (ConcernedApe, 2016)
- **Genre Family**: Farming Simulation / Life Simulation / RPG
- **Core Fantasy**: Inherit a run-down farm, restore it to glory through crop cultivation, animal husbandry, mining, fishing, and foraging while building relationships with townsfolk and uncovering the valley's mysteries.
- **Camera / Presentation**: 2D top-down, tile-based world, pixel art at 16x16 tile resolution, character sprites 16x32, portrait frames 64x64.
- **Target Session Length**: 15-60 minutes per in-game day; full playthrough spans multiple in-game years (50+ real hours).
- **Target Skill Curve**: Gentle entry with basic farming; depth emerges through optimization of crop schedules, artisan goods, mine progression, and social relationships.

## 2. Win/Lose Contract
- **Primary Win Condition**: There is no hard win condition. The player sets their own goals. Completion milestones include restoring the Community Center (or completing the Joja Warehouse), reaching Perfection (100% completion), and evaluating the farm via Grandpa's Shrine at the start of Year 3.
- **Primary Lose Condition**: No permanent game-over. Passing out at 2:00 AM or reaching 0 HP in mines results in gold loss (10% of gold, max 1,000g) and item loss, but the game continues.
- **World/Board Definition**: Stardew Valley map consisting of: the Farm (multiple layout options), Pelican Town, Cindersap Forest, the Beach, the Mountain/Mines, the Railroad, the Desert (Calico Desert), and Ginger Island (1.5+).
- **Grandpa's Evaluation**: At the start of Year 3, Grandpa's ghost evaluates the farm based on total earnings, skill levels, friendship hearts, Community Center progress, and special achievements. 4 candles lit = best rating = Statue of Perfection reward.

## 3. Core Loop (Implementation Sequence)
1. **Wake at 6:00 AM**: Energy restored (full if slept before midnight, partial if later or if exhausted previous day).
2. **Tend Farm**: Water crops, harvest mature crops, collect animal products, process artisan goods.
3. **Explore**: Mine, fish, forage, or complete quests.
4. **Socialize**: Talk to NPCs, give gifts, trigger heart events.
5. **Return Home**: Sell items via shipping bin; gold credited overnight.
6. **Sleep**: End day, advance calendar. Season changes on Day 29 rollover.

## 4. Input Specification
| Action | Default Input | Technical Constraint |
|---|---|---|
| Move Up/Left/Down/Right | `WASD / Arrow Keys` | 4-directional tile-based movement; diagonal movement not natively supported |
| Use Tool | `Left Click` | Targets tile in facing direction; hold to charge upgraded tools |
| Interact / Harvest | `Right Click / X` | Context-sensitive: talk to NPC, open door, harvest crop, pet animal |
| Open Inventory | `E / Tab` | Pauses time in singleplayer |
| Open Map | `M` | Pauses time in singleplayer |
| Open Journal | `F` | Quest log; pauses time |
| Toolbar Slot Select | `1-9 / 0 / - / =` | 12 slots visible; cycle with mouse wheel |
| Eat/Use Item | `Right Click (on held item)` | Consume food for energy/health restore |
| Run | `Left Shift (hold)` | Slight speed increase; no energy cost |
| Pause | `Esc` | Opens game menu with tabs: Inventory, Skills, Social, Map, Crafting, Collections, Options, Exit |

## 5. Top-Level State Machines

### 5.1 Application State Machine
- `Boot`: Load save data, initialize world seed, set calendar.
- `TitleScreen`: New Game, Load Game, Co-Op, Exit.
- `CharacterCreation`: Choose name, appearance (24 skin tones, 73 hairstyles, shirt color, accessories), farm layout, pet preference (cat/dog), favorite thing.
- `InGame`: Active simulation with day/night cycle.
- `SaveScreen`: End-of-day shipping summary, save to disk.

### 5.2 Day Cycle State Machine
- `Morning`: Player wakes at 6:00 AM, energy restored, mail checked.
- `Daytime`: Free gameplay from 6:00 AM to 6:00 PM; full brightness.
- `Evening`: 6:00 PM to midnight; gradual darkness, some shops close.
- `LateNight`: Midnight to 2:00 AM; exhaustion warning, movement slows at 0 energy.
- `PassOut`: At 2:00 AM or -15 energy; forced end of day with gold penalty.

### 5.3 Player State Machine
- `Idle`: Default standing state.
- `Walk`: Moving between tiles at base speed.
- `ToolUse`: Swinging/charging a tool; animation locks movement.
- `Fish`: Casting, waiting for bite, reeling mini-game.
- `Eat`: Consuming food item; brief animation pause.
- `Interact`: Dialogue, shop, chest, or crafting station interaction.
- `Mount`: Riding horse; 1.5x movement speed.
- `Exhausted`: Energy at 0; movement speed halved, tools sluggish, fishing rod unusable.
- `PassedOut`: Energy at -15 or clock at 2:00 AM; day ends immediately.
- `InMines`: Combat-enabled state; health bar visible.

## 6. Time & Season System

### 6.1 Time Mechanics
| Parameter | Value |
|---|---|
| Day start | 6:00 AM |
| Day end (forced) | 2:00 AM |
| Playable hours per day | 20 in-game hours |
| In-game minutes per real second | ~1.43 (7 real seconds = 10 in-game minutes) |
| Skull Cavern time rate | ~0.9 real seconds per in-game minute (slower) |
| Time increment | 10 in-game minutes per tick |
| Time pause triggers | Cutscenes, dialogue, menus, some animations (singleplayer only) |

### 6.2 Season System
| Season | Duration | Weather Types | Crop Growth | Key Features |
|---|---|---|---|---|
| Spring | 28 days | Sunny, Rain, Storm, Wind | Spring crops grow | Cherry blossoms, green landscape |
| Summer | 28 days | Sunny, Rain, Storm | Summer crops grow | Bright colors, lightning storms |
| Fall | 28 days | Sunny, Rain, Storm, Wind | Fall crops grow | Orange/brown foliage |
| Winter | 28 days | Sunny, Snow | No outdoor crops (Winter Seeds only) | White landscape, frozen lake |

### 6.3 Weather System
| Weather | Effect | Frequency |
|---|---|---|
| Sunny | Normal; crops must be manually watered | Most common |
| Rain | Crops auto-watered; some fish available only in rain; villagers stay indoors | ~18% chance |
| Storm | Same as rain + lightning strikes (can damage crops/trees); Lightning Rods collect Battery Packs | Guaranteed Summer 13, Summer 26 |
| Wind | Aesthetic only; petals/leaves blow across screen | Spring and Fall only |
| Snow | No watering effect (unlike rain); visual only | Winter only |

### 6.4 Fixed Weather Rules
- Year 1 Spring 1, 2, 4, 5: Always sunny.
- Year 1 Spring 3: Always rains.
- Summer 13 and 26: Always stormy (every year).
- Festival days: Always sunny (weather overridden).
- Spring 6 onward: Randomized per day.

## 7. Energy System

### 7.1 Energy Parameters
| Parameter | Value |
|---|---|
| Starting max energy | 270 |
| Energy per Stardrop | +34 |
| Total Stardrops available | 7 |
| Maximum possible energy | 508 (270 + 7 x 34) |
| Exhaustion threshold | 0 energy |
| Pass-out threshold | -15 energy |
| Energy display | Green vertical bar, bottom-right of screen |

### 7.2 Tool Energy Costs
| Action | Base Cost (Level 0 Skill) | Cost at Level 10 Skill |
|---|---|---|
| Hoe (single tile) | 2 | 1 |
| Watering Can (single tile) | 2 | 1 |
| Watering Can (charged, per level) | +2 per charge level | Reduced by 0.1 per skill level |
| Pickaxe (single strike) | 2 | 1 |
| Axe (single strike) | 2 | 1 |
| Fishing Rod (cast) | 8 | ~7 |
| Sword/Combat | 0 | 0 |

### 7.3 Energy Recovery
| Method | Amount |
|---|---|
| Sleep before midnight | Full restore |
| Sleep midnight-2:00 AM | Partial restore (proportional) |
| Sleep while exhausted | 50% of max next morning |
| Spa (hot spring) | +1 per 100ms while standing in water |
| Food items | Varies by recipe (e.g., Salad +113, Complete Breakfast +200) |
| Muscle Remedy | Removes exhaustion debuff |
| Kiss spouse (first daily) | Removes exhaustion debuff |

### 7.4 Stardrop Locations
| Source | Requirement |
|---|---|
| Stardew Valley Fair | 2,000 Star Tokens at Fall 16 festival |
| Mines Floor 100 | Reach floor 100 treasure chest |
| Spouse/Roommate | Reach 12.5 hearts with spouse |
| Krobus (Sewers) | Purchase for 20,000g (requires Rusty Key from 60 museum donations) |
| Old Master Cannoli | Give Sweet Gem Berry to statue in Secret Woods |
| Master Angler | Catch every fish species |
| Museum Completion | Donate all 95 items to museum |

## 8. Core Farming Mechanics

### 8.1 Farming Workflow
1. **Till soil**: Use Hoe on dirt tile to create tilled soil.
2. **Apply fertilizer** (optional): Place fertilizer on tilled soil before planting.
3. **Plant seeds**: Use seed item on tilled soil.
4. **Water daily**: Use Watering Can on planted tile each day (unless rain or sprinkler).
5. **Wait for growth**: Each crop has defined growth stages measured in days watered.
6. **Harvest**: Interact with mature crop to collect produce.

### 8.2 Crop Rules
- Crops only grow in their designated season(s). Multi-season crops (Corn, Wheat, Sunflower, Coffee Bean, Ancient Fruit) persist across their valid seasons.
- On Day 1 of a new season, all out-of-season crops wither and die, leaving dead crop debris.
- Unwatered crops do not die but do not advance growth that day.
- Crops cannot be planted on untilled or occupied tiles.
- Some crops use trellises (Green Bean, Hops, Grapes) which block player movement.
- Giant Crops: Cauliflower, Melon, and Pumpkin have a chance to merge into a 3x3 giant crop if a 3x3 area of same-type mature crops exists. Giant crops yield 15-21 items when broken with an axe.

### 8.3 Crop Quality
| Quality | Color | Sell Price Multiplier | Fertilizer That Enables |
|---|---|---|---|
| Normal | None | 1.0x | Default |
| Silver | Silver star | 1.25x | Basic Fertilizer increases chance |
| Gold | Gold star | 1.5x | Quality Fertilizer increases chance |
| Iridium | Purple star | 2.0x | Deluxe Fertilizer only |

### 8.4 Fertilizer Types
| Fertilizer | Effect | Crafting Recipe | Unlock |
|---|---|---|---|
| Basic Fertilizer | Improved chance of silver quality | 2 Sap | Farming 1 |
| Quality Fertilizer | Improved chance of gold quality | 2 Sap + 1 Fish | Farming 9 |
| Deluxe Fertilizer | Guaranteed silver+; chance of gold/iridium | 5 Iridium Bar + 40 Sap | Farming 10 (Qi quest) |
| Speed-Gro | 10% faster growth | 1 Pine Tar + 1 Clam | Farming 3 |
| Deluxe Speed-Gro | 25% faster growth | 1 Oak Resin + 1 Coral | Farming 8 |
| Hyper Speed-Gro | 33% faster growth | 3 Radioactive Ore + 1 Bone Fragment + 1 Solar Essence | Special |
| Basic Retaining Soil | 33% chance soil stays watered overnight | 2 Stone | Farming 4 |
| Quality Retaining Soil | 66% chance soil stays watered overnight | 3 Stone + 1 Clay | Farming 7 |
| Deluxe Retaining Soil | 100% soil stays watered overnight | 5 Stone + 3 Clay + 1 Fiber | Island recipe |

### 8.5 Sprinkler System
| Sprinkler | Tiles Watered | Pattern | Recipe | Unlock |
|---|---|---|---|---|
| Basic Sprinkler | 4 tiles | Cardinal adjacents (+ shape) | 1 Copper Bar + 1 Iron Bar | Farming 2 |
| Quality Sprinkler | 8 tiles | 3x3 area around sprinkler | 1 Iron Bar + 1 Gold Bar + 1 Refined Quartz | Farming 6 |
| Iridium Sprinkler | 24 tiles | 5x5 area around sprinkler | 1 Gold Bar + 1 Iridium Bar + 1 Battery Pack | Farming 9 |

## 9. Crop System

### 9.1 Spring Crops (Season: Spring, Days 1-28)
| Crop | Seed Source | Seed Cost | Growth Days | Regrow Days | Sell Price (Base) | Notes |
|---|---|---|---|---|---|---|
| Parsnip | Pierre | 20g | 4 | -- | 35g | Starter crop; 15 given free on Day 1 |
| Green Bean | Pierre | 60g | 10 | 3 | 40g | Trellis crop; blocks movement |
| Cauliflower | Pierre | 80g | 12 | -- | 175g | Can become Giant Crop (3x3) |
| Potato | Pierre | 50g | 6 | -- | 80g | 25% chance of extra potato per harvest |
| Kale | Pierre | 70g | 6 | -- | 110g | Good profit/day |
| Garlic | Pierre | 40g | 4 | -- | 60g | Year 2+ at Pierre's |
| Rhubarb | Sandy (Desert) | 100g | 13 | -- | 220g | Requires Desert access |
| Strawberry | Egg Festival | 100g | 8 | 4 | 120g | Only sold at Spring 13 Egg Festival |
| Blue Jazz | Pierre | 30g | 7 | -- | 50g | Flower |
| Tulip | Pierre | 20g | 6 | -- | 30g | Flower |
| Coffee Bean | Traveling Cart / Dust Sprites | ~2500g (rare) | 10 | 2 | 15g | Multi-season (Spring+Summer); yields 4 beans |
| Ancient Fruit | Ancient Seed artifact | N/A (craft) | 28 | 7 | 550g | Multi-season (Spring+Summer+Fall); rare seed |

### 9.2 Summer Crops (Season: Summer, Days 1-28)
| Crop | Seed Source | Seed Cost | Growth Days | Regrow Days | Sell Price (Base) | Notes |
|---|---|---|---|---|---|---|
| Melon | Pierre | 80g | 12 | -- | 250g | Can become Giant Crop (3x3) |
| Tomato | Pierre | 50g | 11 | 4 | 60g | Regrows; used in many recipes |
| Blueberry | Pierre | 80g | 13 | 4 | 50g | Yields 3 per harvest; high profit |
| Hot Pepper | Pierre | 40g | 5 | 3 | 40g | Regrows; Shane loves this |
| Wheat | Pierre | 10g | 4 | -- | 25g | Multi-season (Summer+Fall); drops Hay |
| Radish | Pierre | 40g | 6 | -- | 90g | Single harvest |
| Red Cabbage | Pierre | 100g | 9 | -- | 260g | Year 2+ at Pierre's |
| Starfruit | Sandy (Desert) | 400g | 13 | -- | 750g | Most profitable base crop; Starfruit Wine = 2,250g |
| Corn | Pierre | 150g | 14 | 4 | 50g | Multi-season (Summer+Fall) |
| Hops | Pierre | 60g | 11 | 1 (daily) | 25g | Trellis; harvests daily when mature; Pale Ale = 300g |
| Poppy | Pierre | 100g | 7 | -- | 140g | Flower; loved gift for Penny |
| Summer Spangle | Pierre | 50g | 8 | -- | 90g | Flower |
| Sunflower | Pierre | 200g | 8 | -- | 80g | Multi-season (Summer+Fall); drops 0-2 Sunflower Seeds |

### 9.3 Fall Crops (Season: Fall, Days 1-28)
| Crop | Seed Source | Seed Cost | Growth Days | Regrow Days | Sell Price (Base) | Notes |
|---|---|---|---|---|---|---|
| Pumpkin | Pierre | 100g | 13 | -- | 320g | Can become Giant Crop (3x3) |
| Cranberries | Pierre | 240g | 7 | 5 | 75g (x2) | Yields 2 per harvest; very profitable over season |
| Grape | Pierre | 60g | 10 | 3 | 80g | Trellis crop; great for Wine |
| Artichoke | Pierre | 30g | 8 | -- | 160g | Year 2+ at Pierre's |
| Eggplant | Pierre | 20g | 5 | 5 | 60g | Regrows |
| Amaranth | Pierre | 70g | 7 | -- | 150g | |
| Yam | Pierre | 60g | 10 | -- | 160g | |
| Bok Choy | Pierre | 50g | 4 | -- | 80g | Fast grower |
| Beet | Sandy (Desert) | 20g | 6 | -- | 100g | Requires Desert access; used in Sugar via Mill |
| Fairy Rose | Pierre | 200g | 12 | -- | 290g | Flower; produces valuable Fairy Rose Honey (680g) |
| Sunflower | Pierre | 200g | 8 | -- | 80g | Multi-season (Summer+Fall) |
| Corn | Pierre | 150g | 14 | 4 | 50g | Multi-season (Summer+Fall) |
| Sweet Gem Berry | Traveling Cart | 1,000g | 24 | -- | 3,000g | Cannot be turned into Wine/Jelly; give to Old Master Cannoli for Stardrop |

### 9.4 Special/Greenhouse Crops
| Crop | Season(s) | Growth | Regrow | Sell Price | Notes |
|---|---|---|---|---|---|
| Ancient Fruit | Spring+Summer+Fall | 28 days | 7 days | 550g | Best greenhouse crop for Wine (1,650g base; 2,310g Artisan) |
| Sweet Gem Berry | Fall | 24 days | -- | 3,000g | Cannot be processed; give to statue for Stardrop |
| Cactus Fruit | N/A (Greenhouse/Desert) | 12 days | 3 days | 75g | Grows in Desert; or Greenhouse |
| Tea Leaves | Spring+Summer+Fall | 20 days (bush) | Daily in last week | 50g | Produces Green Tea (100g) |

## 10. Tool & Upgrade System

### 10.1 Tool Upgrade Table
| Level | Material | Bars Required | Gold Cost | Upgrade Time | Trash Can Cost |
|---|---|---|---|---|---|
| Starter | -- | -- | -- | -- | -- |
| Copper | Copper Bar | 5 | 2,000g | 2 days | 1,000g |
| Steel | Iron Bar | 5 | 5,000g | 2 days | 2,500g |
| Gold | Gold Bar | 5 | 10,000g | 2 days | 5,000g |
| Iridium | Iridium Bar | 5 | 25,000g | 2 days | 12,500g |

### 10.2 Tool Types and Upgrade Effects
| Tool | Base Function | Copper | Steel | Gold | Iridium |
|---|---|---|---|---|---|
| **Hoe** | Till 1 tile | Charge: 3 tiles in line | Charge: 5 tiles in line | Charge: 3x3 area | Charge: 6x3 area (18 tiles) |
| **Watering Can** | Water 1 tile (40 uses) | Charge: 3 tiles; 55 uses | Charge: 5 tiles; 70 uses | Charge: 3x3 area; 85 uses | Charge: 6x3 area; 100 uses |
| **Pickaxe** | Break stones (1-3 hits) | Break copper nodes; small boulders | Break iron nodes; large boulders | Break gold nodes; meteorites | Break iridium nodes; all obstacles in 1 hit |
| **Axe** | Chop trees (10 hits) | 8 hits; large stumps | 6 hits; hardwood stumps | 4 hits; large logs | 2 hits; all wood obstacles |
| **Trash Can** | Delete items | Reclaim 15% sell value | Reclaim 30% sell value | Reclaim 45% sell value | Reclaim 60% sell value |

### 10.3 Other Tools
| Tool | Source | Function |
|---|---|---|
| Scythe | Starting tool | Harvest crops (no energy for forage crops), cut grass/weeds; no energy cost |
| Milk Pail | Marnie (1,000g) | Milk cows and goats |
| Shears | Marnie (1,000g) | Shear sheep for wool |
| Copper Pan | Fish Tank bundle reward | Pan for ores at shimmering water spots |
| Return Scepter | Krobus (2,000,000g) | Warp to farm; unlimited uses |
| Golden Scythe | Quarry Mine | Increased hay drop rate from grass |

## 11. Animal System

### 11.1 Farm Buildings
| Building | Cost | Materials | Capacity | Animals Housed | Features |
|---|---|---|---|---|---|
| Coop | 4,000g | 300 Wood, 100 Stone | 4 | Chickens | Hay feeding trough |
| Big Coop | 10,000g | 400 Wood, 150 Stone | 8 | + Ducks, Void Chickens, Dinosaurs | Incubator added |
| Deluxe Coop | 20,000g | 500 Wood, 200 Stone | 12 | + Rabbits | Auto-feed system |
| Barn | 6,000g | 350 Wood, 150 Stone | 4 | Cows | Hay feeding trough |
| Big Barn | 12,000g | 450 Wood, 200 Stone | 8 | + Goats | Pregnancy enabled |
| Deluxe Barn | 25,000g | 550 Wood, 300 Stone | 12 | + Sheep, Pigs | Auto-feed system |
| Silo | 100g | 100 Stone, 10 Clay, 5 Copper Bar | -- | -- | Stores 240 hay; grass cut on farm auto-stored |
| Mill | 2,500g | 50 Stone, 150 Wood, 4 Cloth | -- | -- | Wheat to Flour; Beet to Sugar; Rice to Rice |
| Well | 1,000g | 75 Stone | -- | -- | Refill Watering Can anywhere on farm |
| Stable | 10,000g | 100 Hardwood, 5 Iron Bar | -- | Horse | Horse provides 1.5x movement speed |
| Slime Hutch | 10,000g | 500 Stone, 10 Refined Quartz, 1 Iridium Bar | 20 slimes | Slimes | Breed slimes; collect slime balls |
| Fish Pond | 5,000g | 200 Stone, 5 Seaweed, 5 Green Algae | 10 fish | Fish | Breed fish; produce roe and special items |

### 11.2 Animals
| Animal | Building Required | Purchase Price | Product | Product Frequency | Base Sell Price | Deluxe Product | Deluxe Price |
|---|---|---|---|---|---|---|---|
| Chicken (White/Brown) | Coop | 800g | Egg / Brown Egg | Daily | 50g | Large Egg | 95g |
| Void Chicken | Big Coop | 5,000g (Krobus) | Void Egg | Daily | 65g | -- | -- |
| Duck | Big Coop | 1,200g | Duck Egg | Every 2 days | 95g | Duck Feather | 250g |
| Rabbit | Deluxe Coop | 8,000g | Wool | Every 4 days | 340g | Rabbit's Foot | 565g |
| Dinosaur | Big Coop (Incubator) | N/A (Dino Egg) | Dinosaur Egg | Every 7 days | 350g | -- | -- |
| Cow | Barn | 1,500g | Milk | Daily | 125g | Large Milk | 190g |
| Goat | Big Barn | 4,000g | Goat Milk | Every 2 days | 225g | Large Goat Milk | 345g |
| Sheep | Deluxe Barn | 8,000g | Wool | Every 3 days (every 2 at high friendship) | 340g | -- | -- |
| Pig | Deluxe Barn | 16,000g | Truffle | Daily (foraging outdoors; not rainy; not winter) | 625g | -- | -- |

### 11.3 Animal Friendship & Happiness
- Max friendship: 1,000 points (5 hearts displayed).
- Petting daily: +15 friendship.
- Not petting: -5 to -10 per day.
- Being outside on sunny day: +8 friendship.
- Locked outside overnight: -20 friendship and mood penalty.
- Fed (hay available): required; unfed animals lose mood and friendship.
- Product quality scales with combined friendship + mood score.
- At 150+ mood: animal can produce silver/gold quality products and large/deluxe variants.
- Happiness (mood): 0-255 range; affects product quality and whether animal produces at all.

### 11.4 Artisan Animal Products
| Input | Machine | Output | Sell Price (Base) | Processing Time |
|---|---|---|---|---|
| Milk / Large Milk | Cheese Press | Cheese | 230g / 345g (gold) | 3.3 hours |
| Goat Milk / Large Goat Milk | Cheese Press | Goat Cheese | 400g / 600g (gold) | 3.3 hours |
| Egg / Large Egg | Mayonnaise Machine | Mayonnaise | 190g / 285g (gold) | 3 hours |
| Duck Egg | Mayonnaise Machine | Duck Mayonnaise | 375g | 3 hours |
| Void Egg | Mayonnaise Machine | Void Mayonnaise | 275g | 3 hours |
| Wool | Loom | Cloth | 470g | 4 hours |
| Truffle | Oil Maker | Truffle Oil | 1,065g | 6 hours |
| Dinosaur Egg | Mayonnaise Machine | Dinosaur Mayonnaise | 800g | 3 hours |

## 12. Mining & Combat System

### 12.1 The Mines Structure
| Floor Range | Theme | Primary Ore | Key Monsters | Notes |
|---|---|---|---|---|
| 1-39 | Earth/Brown caverns | Copper Ore | Green Slime, Rock Crab, Bug, Grub, Cave Fly | Copper ore ramps up floors 20-39 |
| 40-79 | Frost/Ice caverns | Iron Ore | Frost Bat, Dust Sprite, Ghost, Skeleton | Iron ore most common floors 60-79; Dust Sprites drop Coal |
| 80-119 | Lava/Fire caverns | Gold Ore | Shadow Brute, Shadow Shaman, Lava Bat, Lava Crab, Metal Head, Squid Kid | Most dangerous regular mine floors |
| 120 | Bottom | Skull Key | -- | Treasure chest contains Skull Key |

### 12.2 Mine Mechanics
- **Elevator**: Unlocked every 5 floors. Player can return to any unlocked elevator floor.
- **Treasure chests**: Found every 10 floors with useful rewards (boots, weapons, rings).
- **Infested floors**: Randomly replaced with monster-only floors; must kill all to proceed.
- **Ladder**: Appears when all rocks broken or randomly when breaking rocks; chance increases with daily luck.
- **Ore nodes**: Require Pickaxe hits to break. Copper = 2-3 hits (starter pick), Iron = 3-4, Gold = 4-5. Upgraded pickaxe reduces hits.

### 12.3 Skull Cavern
| Parameter | Value |
|---|---|
| Location | Calico Desert (requires Bus repair via Vault bundle or Joja) |
| Entry requirement | Skull Key (floor 120 of Mines) |
| Floor limit | Infinite (no bottom) |
| Primary ore | Iridium Ore (increases with depth; common past floor 50) |
| Unique mechanic | Holes drop player 3-15 floors (10 damage per floor skipped) |
| Unique monsters | Serpent (150 HP, 23 damage), Mummy (260 HP, 30 damage), Iridium Bat (300 HP, 30 damage) |
| Progress reset | Resets to floor 1 each visit (no elevator) |

### 12.4 Monster Bestiary
| Monster | HP | Damage | Location | Drops |
|---|---|---|---|---|
| Green Slime | 24 | 5 | Mines 1-39 | Slime, Sap |
| Bug | 1 | 8 | Mines 1-29 | Bug Meat, Ancient Seed (rare) |
| Rock Crab | 30 | 5 | Mines 1-29 | Stone, Crab (rare) |
| Bat | 24 | 6 | Mines 31-39 | Bat Wing |
| Frost Bat | 30 | 7 | Mines 41-79 | Bat Wing |
| Dust Sprite | 40 | 6 | Mines 41-79 | Coal, Dwarf Scroll, Burglar Ring (500 kills) |
| Ghost | 96 | 10 | Mines 51-79 | Solar Essence |
| Skeleton | 140 | 10 | Mines 71-79 | Bone Fragment |
| Shadow Brute | 160 | 18 | Mines 81-119 | Void Essence, Void Egg (rare) |
| Shadow Shaman | 130 | 12 | Mines 81-119 | Void Essence; heals other shadows |
| Lava Bat | 80 | 15 | Mines 81-119 | Bat Wing, Bomb (rare) |
| Lava Crab | 120 | 15 | Mines 81-119 | Bomb, Crab (rare) |
| Metal Head | 40 | 15 | Mines 81-119 | Copper/Iron/Gold Ore |
| Squid Kid | 1 | 18 | Mines 81-119 | Solar Essence, Squid Ink |
| Serpent | 150 | 23 | Skull Cavern | Spicy Eel, Bomb, Iridium Ore |
| Mummy | 260 | 30 | Skull Cavern | Cloth, Solar Essence; must bomb after knockout |
| Iridium Bat | 300 | 30 | Skull Cavern 50+ | Iridium Ore, Mega Bomb |

### 12.5 Weapon Types
| Type | Attack Style | Special Move | Characteristics |
|---|---|---|---|
| Sword | Horizontal arc swing | Block (right-click): reduces damage taken, reflects damage | Balanced speed and damage |
| Dagger | Rapid stab | Quick stab combo (right-click): fast multi-hit burst | Low damage per hit, high attack speed, high crit chance |
| Club | Overhead slam | Pummel (right-click): rapid hits + knockback slam | Highest single-hit damage, slowest speed |
| Slingshot | Ranged projectile | N/A | Damage based on ammo type; Master Slingshot = 2x damage |

### 12.6 Notable Weapons
| Weapon | Type | Damage | Source |
|---|---|---|---|
| Rusty Sword | Sword | 2-5 | Starting weapon (Mines floor 0) |
| Steel Smallsword | Sword | 4-8 | Mines floor 10 chest |
| Obsidian Edge | Sword | 30-45 | Mines floor 90 chest |
| Lava Katana | Sword | 55-64 | Adventurer's Guild (25,000g) |
| Galaxy Sword | Sword | 60-80 | Prismatic Shard + Desert pillars |
| Galaxy Hammer | Club | 70-90 | Adventurer's Guild (after Galaxy Sword) |

### 12.7 Combat Stats
| Stat | Effect |
|---|---|
| Damage | Base damage dealt per swing |
| Speed | Weapon swing speed modifier |
| Defense | Reduces damage taken by flat amount |
| Weight | Knockback distance on enemies |
| Crit Chance | % chance of critical hit (base ~2% for swords, ~10% for daggers) |
| Crit Power | Multiplier applied to critical hits (base 3x) |

### 12.8 Player Health (Combat)
| Parameter | Value |
|---|---|
| Starting max HP | 100 |
| HP per Combat level | +5 (150 HP at Combat 10) |
| Fighter profession bonus | +15 HP |
| Defender profession bonus | +25 HP |
| Max possible HP | 190 (Combat 10 + Fighter + Defender) |
| HP recovery (food) | Varies per food item |
| Death penalty | Lose items, gold (10% up to 1,000g), wake at Harvey's clinic |

## 13. Fishing System

### 13.1 Fishing Rod Progression
| Rod | Cost | Source | Unlock | Bait | Tackle |
|---|---|---|---|---|---|
| Training Rod | 25g | Willy's Shop | Immediate | No | No |
| Bamboo Pole | Free (Day 2) | Willy (mail) | Day 2 cutscene | No | No |
| Fiberglass Rod | 1,800g | Willy's Shop | Fishing Level 2 | Yes | No |
| Iridium Rod | 7,500g | Willy's Shop | Fishing Level 6 | Yes | Yes |

### 13.2 Fishing Mini-Game Mechanics
1. **Casting**: Hold Use Tool to fill power meter; release to cast. Distance = meter fill percentage. "Max" displayed at 99%+ fill but no gameplay bonus.
2. **Waiting**: Bobber lands in water. Wait for bite (exclamation mark + vibration). Time to bite reduced by 0.25s per Fishing level.
3. **Hooking**: Press Use Tool when bite occurs. Delay = fish escapes.
4. **Reeling Mini-Game**:
   - A vertical bar appears with a small fish icon bouncing up and down.
   - Player controls a green "bobber bar" by clicking/tapping to raise it; gravity pulls it down when released.
   - Goal: Keep fish icon inside the green bar to fill a progress meter on the right.
   - If fish is outside the green bar, progress meter depletes.
   - Progress meter full = fish caught. Progress meter empty = fish escapes.
   - Fish difficulty (1-110 scale) determines fish movement erraticness and speed.
5. **Treasure Chest**: May appear during reeling; move green bar over chest icon to collect bonus items (artifacts, gems, tackle, ore).

### 13.3 Fishing Skill Impact
| Fishing Level | Bobber Bar Size Increase | Bite Time Reduction | New Recipes/Unlocks |
|---|---|---|---|
| 0 | Base (varies by rod) | Base | -- |
| 1 | +1 pixel | -0.25s | -- |
| 2 | +2 pixels | -0.50s | Bait recipe; Fiberglass Rod available |
| 3 | +3 | -0.75s | Crab Pot recipe |
| 4 | +4 | -1.00s | Recycling Machine |
| 5 | +5 | -1.25s | Profession choice (Fisher/Trapper) |
| 6 | +6 | -1.50s | Iridium Rod available; Spinner recipe |
| 7 | +7 | -1.75s | Trap Bobber recipe |
| 8 | +8 | -2.00s | Worm Bin recipe |
| 9 | +9 | -2.25s | Magnet recipe |
| 10 | +10 | -2.50s | Profession choice (Level 10) |

### 13.4 Tackle Types (Iridium Rod only)
| Tackle | Effect | Source |
|---|---|---|
| Spinner | Slightly increases bite rate | Crafting (2 Iron Bar) or Willy (500g) |
| Dressed Spinner | Even higher bite rate increase | Lake Fish bundle reward |
| Trap Bobber | Fish escapes slower when outside green bar | Crafting or Willy (500g) |
| Cork Bobber | Increases green bar size | Crafting (10 Wood, 5 Hardwood, 10 Slime) |
| Lead Bobber | Prevents green bar from bouncing off bottom | Crafting or Willy (200g) |
| Treasure Hunter | Increases treasure chest chance; easier to catch treasure | Crafting (2 Gold Bar) |
| Barbed Hook | Grip effect; bar clings to fish when inside bar | Crafting (1 Copper Bar, 1 Iron Bar, 1 Gold Bar) |
| Curiosity Lure | Increases chance of catching rare fish | Special (Skull Cavern treasure) |

### 13.5 Fish Quality
- Quality determined by casting distance + Fishing level + daily luck.
- Distance zones: close = normal, medium = silver possible, far = gold possible.
- Perfect catch (fish never leaves green bar) = guaranteed quality upgrade.
- Iridium quality fish possible at high levels with perfect catch and max distance.

## 14. NPC & Relationship System

### 14.1 Marriage Candidates (12 total)

#### Bachelors (6)
| Name | Birthday | Location | Occupation | Loved Gifts |
|---|---|---|---|---|
| Alex | Summer 13 | 1 River Road | Aspiring athlete | Complete Breakfast, Salmon Dinner, Prismatic Shard |
| Elliott | Fall 5 | Beach cabin | Writer | Crab Cakes, Duck Feather, Lobster, Pomegranate, Tom Kha Soup |
| Harvey | Winter 14 | Medical clinic | Doctor | Coffee, Pickles, Super Meal, Truffle Oil, Wine |
| Sam | Summer 17 | 1 Willow Lane | Musician / JojaMart worker | Cactus Fruit, Maple Bar, Pizza, Tigerseye |
| Sebastian | Winter 10 | Mountain house (basement) | Programmer | Frozen Tear, Obsidian, Pumpkin Soup, Sashimi, Void Egg |
| Shane | Spring 20 | Marnie's Ranch | JojaMart employee | Beer, Hot Pepper, Pepper Poppers, Pizza |

#### Bachelorettes (6)
| Name | Birthday | Location | Occupation | Loved Gifts |
|---|---|---|---|---|
| Abigail | Fall 13 | Pierre's shop | Adventurer | Amethyst, Blackberry Cobbler, Chocolate Cake, Pufferfish, Pumpkin, Spicy Eel |
| Emily | Spring 27 | 2 Willow Lane | Saloon bartender | Amethyst, Aquamarine, Cloth, Emerald, Jade, Ruby, Topaz, Wool |
| Haley | Spring 14 | 2 Willow Lane | Photographer | Coconut, Fruit Salad, Pink Cake, Sunflower |
| Leah | Winter 23 | Forest cabin | Sculptor/Artist | Goat Cheese, Poppyseed Muffin, Salad, Stir Fry, Truffle, Wine |
| Maru | Summer 10 | Mountain house | Nurse/Inventor | Battery Pack, Cauliflower, Cheese Cauliflower, Diamond, Gold Bar, Iridium Bar, Miner's Treat, Pepper Poppers, Rhubarb Pie, Strawberry |
| Penny | Fall 2 | Trailer (town) | Tutor | Diamond, Emerald, Melon, Poppy, Poppyseed Muffin, Red Plate, Roots Platter, Sandfish, Tom Kha Soup |

### 14.2 Friendship Mechanics
| Parameter | Value |
|---|---|
| Points per heart | 250 |
| Max hearts (non-datable) | 10 (2,500 points) |
| Max hearts (datable, pre-bouquet) | 8 (2,000 points; capped) |
| Max hearts (datable, post-bouquet) | 10 |
| Max hearts (married spouse) | 14 (3,500 points) |
| Gift limit | 2 per NPC per week + 1 birthday gift |
| Talking daily | +20 friendship |
| Loved gift | +80 friendship |
| Liked gift | +45 friendship |
| Neutral gift | +20 friendship |
| Disliked gift | -20 friendship |
| Hated gift | -40 friendship |
| Birthday multiplier | 8x (loved birthday gift = +640 points) |
| Bouquet cost | 200g (Pierre's; unlocks romance path at 8 hearts) |
| Mermaid's Pendant cost | 5,000g (Old Mariner, beach, rainy day, after house upgrade) |

### 14.3 Universal Gift Preferences
| Category | Items |
|---|---|
| Universal Loves | Golden Pumpkin, Pearl, Prismatic Shard, Rabbit's Foot, Magic Rock Candy |
| Universal Likes | Most Artisan Goods, Gems (except specified), Cooked Meals, Fruit, Vegetables |
| Universal Dislikes | Most Foraged Minerals, Bait, Strange Bun, specified per NPC |
| Universal Hates | Most Trash items, Sap, Sea Cucumber (varies per NPC) |

### 14.4 Marriage System
1. Reach 8 hearts with candidate.
2. Give Bouquet (200g from Pierre) to begin dating.
3. Reach 10 hearts; trigger all heart events.
4. Upgrade farmhouse (first upgrade from Robin: 10,000g + 450 Wood).
5. Purchase Mermaid's Pendant from Old Mariner (5,000g; appears on beach during rain).
6. Wedding ceremony 3 days after proposal.
7. Spouse moves into farmhouse; has unique room addition.
8. Spouse helps on farm (waters crops, feeds animals, repairs fences randomly).
9. Can have children (2 max: first after 7+ days married with nursery upgrade).
10. Friendship decays if spouse is not talked to daily (-20/day) or kissed.

### 14.5 Heart Events
- Each marriage candidate has unique cutscene events at 2, 4, 6, 8, 10, and 14 hearts.
- Some events have dialogue choices that affect friendship gain/loss.
- Group 10-heart event triggers jealousy mechanic if dating multiple candidates.
- Non-marriage NPCs also have heart events at various thresholds.

## 15. Community Center

### 15.1 Room Overview
| Room | Number of Bundles | Reward | Unlocks |
|---|---|---|---|
| Crafts Room | 6 | Bridge Repair | Quarry access |
| Pantry | 6 | Greenhouse | Year-round indoor farming |
| Fish Tank | 6 | Glittering Boulder Removed | Panning for ores; Copper Pan |
| Boiler Room | 3 | Minecart Repair | Fast travel between Mine, Town, Bus Stop, Quarry |
| Bulletin Board | 5 | Friendship Bonus | +2 hearts with all non-datable villagers |
| Vault | 4 | Bus Repair | Access to Calico Desert |

### 15.2 Crafts Room Bundles
| Bundle | Items Required | Reward |
|---|---|---|
| Spring Foraging | Wild Horseradish, Daffodil, Leek, Dandelion | 30 Spring Seeds |
| Summer Foraging | Grape, Spice Berry, Sweet Pea | 30 Summer Seeds |
| Fall Foraging | Common Mushroom, Wild Plum, Hazelnut, Blackberry | 30 Fall Seeds |
| Winter Foraging | Winter Root, Crystal Fruit, Snow Yam, Crocus | 30 Winter Seeds |
| Construction | Wood (99x2), Stone (99), Hardwood (10) | Charcoal Kiln |
| Exotic Foraging | Coconut, Cactus Fruit, Cave Carrot, Red Mushroom, Purple Mushroom, Maple Syrup, Oak Resin, Pine Tar (5 of 9) | 5 Autumn's Bounty |

### 15.3 Pantry Bundles
| Bundle | Items Required | Reward |
|---|---|---|
| Spring Crops | Parsnip, Green Bean, Cauliflower, Potato | 20 Speed-Gro |
| Summer Crops | Tomato, Hot Pepper, Blueberry, Melon | Quality Sprinkler |
| Fall Crops | Corn, Eggplant, Pumpkin, Yam | Bee House |
| Quality Crops | 5 Gold Parsnip, 5 Gold Melon, 5 Gold Pumpkin, 5 Gold Corn | Preserves Jar |
| Animal | Large Milk, Large Brown Egg, Large White Egg, Large Goat Milk, Wool, Duck Egg | Cheese Press |
| Artisan | Truffle Oil, Cloth, Goat Cheese, Cheese, Honey, Jelly, Apple, Apricot, Orange, Peach, Pomegranate, Cherry (6 of 12) | Keg |

### 15.4 Fish Tank Bundles
| Bundle | Items Required | Reward |
|---|---|---|
| River Fish | Sunfish, Catfish, Shad, Tiger Trout | 30 Bait |
| Lake Fish | Largemouth Bass, Carp, Bullhead, Sturgeon | Dressed Spinner |
| Ocean Fish | Sardine, Tuna, Red Snapper, Tilapia | 5 Warp Totem: Beach |
| Night Fishing | Walleye, Bream, Eel | Small Glow Ring |
| Crab Pot | Lobster, Crayfish, Crab, Cockle, Mussel, Shrimp, Snail, Clam, Oyster, Periwinkle (5 of 10) | 3 Crab Pots |
| Specialty Fish | Pufferfish, Ghostfish, Sandfish, Woodskip | 5 Dish O' The Sea |

### 15.5 Boiler Room Bundles
| Bundle | Items Required | Reward |
|---|---|---|
| Blacksmith's | Copper Bar, Iron Bar, Gold Bar | Furnace |
| Geologist's | Quartz, Earth Crystal, Frozen Tear, Fire Quartz | 5 Omni Geodes |
| Adventurer's | 99 Slime, 10 Bat Wings, 1 Solar Essence, 1 Void Essence | Small Magnet Ring |

### 15.6 Bulletin Board Bundles
| Bundle | Items Required | Reward |
|---|---|---|
| Chef's | Maple Syrup, Fiddlehead Fern, Truffle, Poppy, Maki Roll, Fried Egg | 3 Pink Cake |
| Dye | Red Mushroom, Sea Urchin, Sunflower, Duck Feather, Aquamarine, Red Cabbage | Seed Maker |
| Field Research | Purple Mushroom, Nautilus Shell, Chub, Frozen Geode | Recycling Machine |
| Fodder | Wheat (10), Hay (10), Apple (3) | Heater |
| Enchanter's | Oak Resin, Wine, Rabbit's Foot, Pomegranate | 5 Gold Bars |

### 15.7 Vault Bundles
| Bundle | Gold Required | Reward |
|---|---|---|
| Bundle 1 | 2,500g | 3 Chocolate Cake |
| Bundle 2 | 5,000g | 30 Quality Fertilizer |
| Bundle 3 | 10,000g | Lightning Rod |
| Bundle 4 | 25,000g | Crystalarium |
| **Total** | **42,500g** | |

### 15.8 Joja Community Development (Alternative Path)
- Purchase Joja Membership for 5,000g to abandon Community Center.
- Purchase improvements directly with gold: Bus (40,000g), Minecarts (15,000g), Bridge (25,000g), Greenhouse (35,000g), Panning (20,000g).
- Total Joja cost: 140,000g.

## 16. Skills & Professions System

### 16.1 Skill Overview
| Skill | XP Source | Key Benefits Per Level |
|---|---|---|
| Farming | Harvesting crops, animal care | Crafting recipes (sprinklers, fertilizer); crop quality chance |
| Mining | Breaking rocks, ore nodes | Crafting recipes (bombs, stairs); +1 pickaxe proficiency per level |
| Foraging | Picking forage items, chopping trees | Crafting recipes (tapper, seeds); forage quality improvement |
| Fishing | Catching fish, crab pot harvest | Larger bobber bar; faster bite time; tackle recipes |
| Combat | Killing monsters | +5 HP per level; combat ring recipes |

### 16.2 XP Requirements by Level
| Level | Total XP | XP from Previous Level |
|---|---|---|
| 1 | 100 | 100 |
| 2 | 380 | 280 |
| 3 | 770 | 390 |
| 4 | 1,300 | 530 |
| 5 | 2,150 | 850 |
| 6 | 3,300 | 1,150 |
| 7 | 4,800 | 1,500 |
| 8 | 6,900 | 2,100 |
| 9 | 10,000 | 3,100 |
| 10 | 15,000 | 5,000 |

### 16.3 All Professions

#### Farming Professions
| Level | Choice A | Choice B |
|---|---|---|
| 5 | **Rancher**: Animal products worth 20% more | **Tiller**: Crops worth 10% more |
| 10 (Rancher) | **Coopmaster**: Coop animals befriend faster; incubation halved | **Shepherd**: Barn animals befriend faster; sheep produce wool faster |
| 10 (Tiller) | **Artisan**: Artisan goods worth 40% more | **Agriculturist**: Crops grow 10% faster |

#### Mining Professions
| Level | Choice A | Choice B |
|---|---|---|
| 5 | **Miner**: +1 ore per vein | **Geologist**: Gems may spawn in pairs |
| 10 (Miner) | **Blacksmith**: Metal bars worth 50% more | **Prospector**: Coal find doubled |
| 10 (Geologist) | **Excavator**: Geode find doubled | **Gemologist**: Gems worth 30% more |

#### Foraging Professions
| Level | Choice A | Choice B |
|---|---|---|
| 5 | **Forester**: Wood worth 50% more | **Gatherer**: Chance for double harvest of foraged items |
| 10 (Forester) | **Lumberjack**: Normal trees may drop hardwood | **Tapper**: Syrup worth 25% more |
| 10 (Gatherer) | **Botanist**: Foraged items always iridium quality | **Tracker**: Forageable locations revealed (arrow indicators) |

#### Fishing Professions
| Level | Choice A | Choice B |
|---|---|---|
| 5 | **Fisher**: Fish worth 25% more | **Trapper**: Crab pot recipe cost reduced |
| 10 (Fisher) | **Angler**: Fish worth 50% more | **Pirate**: Treasure chest chance doubled (~30%) |
| 10 (Trapper) | **Mariner**: Crab pots never catch trash | **Luremaster**: Crab pots don't require bait |

#### Combat Professions
| Level | Choice A | Choice B |
|---|---|---|
| 5 | **Fighter**: +10% damage, +15 HP | **Scout**: +50% crit chance |
| 10 (Fighter) | **Brute**: +15% more damage (25% total) | **Defender**: +25 HP |
| 10 (Scout) | **Acrobat**: Special move cooldown halved | **Desperado**: Critical hits deal more damage |

## 17. Foraging System

### 17.1 Seasonal Forage Items
| Season | Item | Sell Price (Base) | Location |
|---|---|---|---|
| Spring | Wild Horseradish | 50g | Mountain, Bus Stop, backwoods |
| Spring | Daffodil | 30g | Bus Stop, town paths, forest |
| Spring | Leek | 60g | Forest, mountain paths |
| Spring | Dandelion | 40g | Bus Stop, Railroad, forest |
| Spring | Spring Onion | 8g | Cindersap Forest (south) |
| Spring | Morel | 150g | Secret Woods, Farm (forest type) |
| Summer | Grape | 80g | Mountain, backwoods |
| Summer | Spice Berry | 80g | Bus Stop, forest, Railroad |
| Summer | Sweet Pea | 50g | Bus Stop, Railroad, forest |
| Summer | Fiddlehead Fern | 90g | Secret Woods (summer only) |
| Summer | Red Mushroom | 75g | Mines, Secret Woods |
| Fall | Common Mushroom | 40g | Forest, mountain, Secret Woods |
| Fall | Wild Plum | 80g | Bus Stop, mountain, forest |
| Fall | Hazelnut | 90g | Bus Stop, backwoods, mountain |
| Fall | Blackberry | 20g | Bus Stop, Railroad, mountain (especially Days 8-11) |
| Fall | Chanterelle | 160g | Secret Woods |
| Winter | Winter Root | 70g | Hoeing worm tiles in winter |
| Winter | Crystal Fruit | 150g | Mines, foraged in winter |
| Winter | Snow Yam | 100g | Hoeing worm tiles in winter |
| Winter | Crocus | 60g | Bus Stop, forest, mountain |
| Winter | Holly | 80g | Bus Stop, mountain, Railroad |
| Winter | Nautilus Shell | 120g | Beach (winter) |

### 17.2 Tree Tapping
| Tree | Tapper Product | Value | Production Time |
|---|---|---|---|
| Maple Tree | Maple Syrup | 200g | 9 days |
| Oak Tree | Oak Resin | 150g | 7 days |
| Pine Tree | Pine Tar | 100g | 5 days |

## 18. Economy

### 18.1 Selling Methods
| Method | Details |
|---|---|
| Shipping Bin | Place items; gold received next morning after overnight tally screen |
| Pierre's Store | Sell directly for same price as shipping bin; immediate payment |
| Adventurer's Guild | Sell monster loot and weapons |
| Willy's Fish Shop | Sell fish directly |

### 18.2 Key Artisan Goods Pricing
| Item | Input | Machine | Processing Time | Base Sell Price | With Artisan (+40%) |
|---|---|---|---|---|---|
| Wine | Any Fruit | Keg | 7 days | 3x fruit base price | 4.2x fruit base price |
| Juice | Any Vegetable | Keg | 4 days | 2.25x vegetable base price | 3.15x vegetable base price |
| Jelly | Any Fruit | Preserves Jar | 2-3 days | 50 + 2x fruit base price | (50 + 2x) * 1.4 |
| Pickles | Any Vegetable | Preserves Jar | 2-3 days | 50 + 2x vegetable base price | (50 + 2x) * 1.4 |
| Pale Ale | Hops | Keg | 1-2 days | 300g | 420g |
| Beer | Wheat | Keg | 1 day | 200g | 280g |
| Cheese | Milk | Cheese Press | 3.3 hours | 230g | 322g |
| Goat Cheese | Goat Milk | Cheese Press | 3.3 hours | 400g | 560g |
| Truffle Oil | Truffle | Oil Maker | 6 hours | 1,065g | 1,491g |
| Cloth | Wool | Loom | 4 hours | 470g | 658g |
| Honey | N/A | Bee House | 4 days | 100g (wild); up to 680g (Fairy Rose) | Scaled by flower proximity |
| Mayonnaise | Egg | Mayonnaise Machine | 3 hours | 190g | 266g |
| Starfruit Wine | Starfruit | Keg | 7 days | 2,250g | 3,150g |
| Ancient Fruit Wine | Ancient Fruit | Keg | 7 days | 1,650g | 2,310g |

### 18.3 Cask Aging (Cellar Required - Final House Upgrade)
| Quality | Days to Age | Sell Multiplier |
|---|---|---|
| Silver | 14 days | 1.25x |
| Gold | 28 days | 1.5x |
| Iridium | 56 days | 2.0x |

Only Wine, Cheese, Goat Cheese, Beer, Pale Ale, and Mead can be aged in casks.
- Iridium Starfruit Wine: 2,250g x 2.0 = 4,500g (base); with Artisan: 3,150g x 2.0 = 6,300g (most valuable standard item in game).

### 18.4 Store Comparison
| Item | Pierre's Price | JojaMart Price |
|---|---|---|
| Parsnip Seeds | 20g | 25g |
| Potato Seeds | 50g | 62g |
| Cauliflower Seeds | 80g | 100g |
| Sugar | 100g | 125g |
| Wheat Flour | 100g | 125g |
| Rice | 200g | 250g |
| Grass Starter | 100g | 125g |

JojaMart prices are typically 25% higher than Pierre's. Open 9 AM - 11 PM daily (Pierre closed Wednesdays).

## 19. Festival Events

### 19.1 Festival Calendar
| Festival | Date | Time | Location | Key Activity |
|---|---|---|---|---|
| Egg Festival | Spring 13 | 9 AM - 2 PM | Town Square | Egg Hunt (win prize: Straw Hat); buy Strawberry Seeds |
| Flower Dance | Spring 24 | 9 AM - 2 PM | Cindersap Forest | Dance with partner (requires 4 hearts); unique items |
| Luau | Summer 11 | 9 AM - 2 PM | Beach | Potluck soup (quality of contributed item affects Governor's response) |
| Dance of Moonlight Jellies | Summer 28 | 10 PM - 12 AM | Beach | Watch jellyfish; purely narrative/social |
| Stardew Valley Fair | Fall 16 | 9 AM - 3 PM | Town Square | Grange Display (judged for tokens); Star Token games; buy Stardrop (2,000 tokens) |
| Spirit's Eve | Fall 27 | 10 PM - 11:50 PM | Town Square | Haunted maze; win Golden Pumpkin (2,500g) |
| Festival of Ice | Winter 8 | 9 AM - 2 PM | Forest | Ice fishing competition (catch most fish to win) |
| Night Market | Winter 15-17 | 5 PM - 2 AM | Beach | Traveling merchant; submarine fishing; mermaid show; rare items |
| Feast of the Winter Star | Winter 25 | 9 AM - 2 PM | Town Square | Secret gift exchange (receive gift from random NPC) |

## 20. Cooking & Crafting

### 20.1 Cooking Overview
- 81 total cooked recipes in the base game.
- Unlocked via: Queen of Sauce TV show (Sundays, reruns Wednesdays), NPC friendship gifts (mail), Stardrop Saloon purchase, skill level ups.
- Cooking requires a kitchen (first house upgrade) or Cookout Kit (crafted).
- Fried Egg known by default from game start.
- Cooked food restores Energy and Health; some provide temporary buffs (speed, luck, defense, attack, fishing, farming, etc.).

### 20.2 Notable Cooking Recipes
| Recipe | Ingredients | Energy | Health | Buff | Source |
|---|---|---|---|---|---|
| Fried Egg | 1 Egg | +50 | +22 | -- | Default |
| Salad | 1 Leek, 1 Dandelion, 1 Vinegar | +113 | +50 | -- | Emily 3-heart |
| Complete Breakfast | 1 Fried Egg, 1 Hashbrowns, 1 Pancakes, 1 Milk | +200 | +90 | +2 Farming | Queen of Sauce |
| Pepper Poppers | 1 Hot Pepper, 1 Cheese | +130 | +58 | +2 Speed, +1 Farming | Shane 3-heart |
| Pumpkin Soup | 1 Pumpkin, 1 Milk | +200 | +90 | +2 Luck, +2 Defense | Robin 7-heart |
| Spicy Eel | 1 Eel, 1 Hot Pepper | +115 | +51 | +1 Luck, +1 Speed | George 7-heart |
| Lucky Lunch | 1 Sea Cucumber, 1 Tortilla, 1 Blue Jazz | +100 | +45 | +3 Luck | Queen of Sauce |
| Crab Cakes | 1 Crab, 1 Wheat Flour, 1 Egg, 1 Oil | +225 | +101 | +1 Speed, +1 Defense | Queen of Sauce |
| Triple Shot Espresso | 3 Coffee | +12 | +5 | +1 Speed (2x duration of Coffee) | Purchase from Stardrop Saloon |

### 20.3 Key Crafting Recipes
| Item | Materials | Unlock | Function |
|---|---|---|---|
| Furnace | 20 Copper Ore + 25 Stone | Clint cutscene (collect copper) | Smelt ores into bars |
| Keg | 30 Wood + 1 Copper Bar + 1 Iron Bar + 1 Oak Resin | Farming 8 | Wine, Juice, Pale Ale, Beer, Coffee |
| Preserves Jar | 50 Wood + 40 Stone + 8 Coal | Farming 4 | Jelly, Pickles, Aged Roe, Caviar |
| Cheese Press | 45 Wood + 45 Stone + 10 Hardwood + 1 Copper Bar | Farming 6 | Milk to Cheese |
| Mayonnaise Machine | 15 Wood + 15 Stone + 1 Earth Crystal + 1 Copper Bar | Farming 2 | Eggs to Mayonnaise |
| Oil Maker | 50 Slime + 20 Hardwood + 1 Gold Bar | Farming 8 | Truffle Oil, Sunflower Oil |
| Bee House | 40 Wood + 8 Coal + 1 Iron Bar + 1 Maple Syrup | Farming 3 | Produces Honey (quality depends on nearby flower) |
| Seed Maker | 25 Wood + 10 Coal + 1 Gold Bar | Farming 9 | Convert harvested crop into 1-3 seeds |
| Crystalarium | 99 Stone + 5 Gold Bar + 2 Iridium Bar + 1 Battery Pack | Mining 9 | Replicate placed gem/mineral infinitely |
| Lightning Rod | 1 Iron Bar + 1 Refined Quartz + 5 Bat Wing | Foraging 6 | Collects Battery Pack during storms |
| Tapper | 40 Wood + 2 Copper Bar | Foraging 3 | Maple Syrup, Oak Resin, Pine Tar from trees |
| Bomb | 4 Iron Ore + 1 Coal | Mining 6 | Explodes; breaks rocks in radius |
| Mega Bomb | 4 Gold Ore + 1 Solar Essence + 1 Void Essence | Mining 8 | Larger explosion radius |
| Warp Totem: Farm | 1 Hardwood + 1 Honey + 20 Fiber | Foraging 8 | Instant teleport to farm |
| Staircase | 99 Stone | Mining 2 | Creates ladder down 1 floor in mines |

### 20.4 Smelting
| Input | Output | Time | Fuel |
|---|---|---|---|
| 5 Copper Ore | 1 Copper Bar | 30 min | 1 Coal |
| 5 Iron Ore | 1 Iron Bar | 2 hours | 1 Coal |
| 5 Gold Ore | 1 Gold Bar | 5 hours | 1 Coal |
| 5 Iridium Ore | 1 Iridium Bar | 8 hours | 1 Coal |
| 1 Quartz + 1 Coal | 1 Refined Quartz | 1.5 hours | -- |
| 5 Radioactive Ore | 1 Radioactive Bar | 10 hours | 1 Coal |

## 21. UI/HUD Specification

### 21.1 Main HUD Elements
| Element | Position | Description |
|---|---|---|
| Toolbar | Bottom center | 12 item slots (expandable to 24, then 36 via Backpack upgrades: 2,000g and 10,000g) |
| Clock | Top-right | Shows current time (HH:MM format), current day name, date, and season |
| Gold Counter | Top-right (below clock) | Current gold amount |
| Energy Bar | Bottom-right | Green vertical bar; shows current/max energy numerically on hover |
| Health Bar | Bottom-right (next to energy) | Red vertical bar; only visible in combat areas or when damaged |
| Active Buffs | Top-left or below clock | Icons showing active food/drink buff effects with remaining duration |
| Day/Season Display | Top-right | "Day X of [Season], Year Y" |

### 21.2 Inventory Screen (Tab Menu)
| Tab | Content |
|---|---|
| Inventory | Backpack contents, equipped hat/ring/boots/weapon slots, character appearance, trash can |
| Skills | 5 skill bars with current level, XP bar, unlocked professions |
| Social | List of all NPCs with heart meters, birthday reminders, gifting history |
| Map | Full valley map; shows NPC locations (with friendship level 2+) |
| Crafting | All known crafting recipes; greyed if materials insufficient |
| Collections | Museum artifacts, minerals, fish, cooking, shipping, achievements |
| Options | Volume sliders (Music, Sound, Ambience), zoom, UI scale, controls, accessibility |
| Exit | Save and exit to title |

### 21.3 Shipping Summary Screen
- Displayed when sleeping; shows all items placed in shipping bin that day.
- Lists each item with quantity and gold earned.
- Total daily earnings displayed.
- New items shipped marked with a star.
- Tracking toward shipping collection completion.

### 21.4 Key UI Interactions
| Context | UI Behavior |
|---|---|
| Shop | Grid of items with prices; hover for description; click to buy; right-click for bulk |
| Chest | Side-by-side inventory view; drag and drop between chest and backpack |
| Crafting station | Recipe list with material requirements; grayed if insufficient |
| Museum | Place artifacts/minerals on display pedestals |
| Calendar | Wall calendar in Pierre's shop shows birthdays, festivals, and season info |
| TV | Watch weather forecast, fortune teller (daily luck), cooking show, fishing tips |

## 22. Audio Design

### 22.1 Music System
| Context | Style | Notes |
|---|---|---|
| Spring (Farm) | Light acoustic guitar, piano, pastoral folk | Multiple tracks rotate: "Spring (The Valley Comes Alive)", "Spring (It's a Big World Outside)" |
| Summer (Farm) | Upbeat, jazzy, bright instrumentation | "Summer (Nature's Crescendo)", "Summer (Tropicala)" |
| Fall (Farm) | Mellow, melancholy, wind instruments, synth | "Fall (The Smell of Mushroom)", "Fall (Ghost Synth)" |
| Winter (Farm) | Quiet, contemplative, piano, minimal | "Winter (Nocturne of Ice)", "Winter (The Wind Can Be Still)" |
| Town | Warm community theme, accordion, strings | Changes by season |
| Mines (Upper) | Dark ambient, echoing percussion | Floors 1-39 |
| Mines (Frost) | Crystalline, eerie tones | Floors 40-79 |
| Mines (Lava) | Intense, driving rhythm, distorted | Floors 80-119 |
| Skull Cavern | Ominous, high tension, fast tempo | Danger-emphasizing |
| Festival | Unique per festival; upbeat, celebratory | Egg Festival jingle, Moonlight Jellies ambient |
| Rain | Ambient rain loop overlaid on muted seasonal track | Reduces music volume; emphasizes rain SFX |

### 22.2 Sound Effects
| Event | Sound Description |
|---|---|
| Tool use (Hoe) | Dirt scraping, thud |
| Tool use (Watering Can) | Water splash, pouring |
| Tool use (Pickaxe) | Stone cracking, metallic ring |
| Tool use (Axe) | Wood chopping, crack |
| Crop harvest | Soft pop/pluck |
| Animal pet | Happy chirp/moo/baa |
| Fish bite | Splash, exclamation ding |
| Fish caught | Victory jingle, splash |
| Monster hit | Impact thud, creature cry |
| Player damaged | Pain grunt, screen flash |
| Footsteps | Varies by surface: grass (soft), wood (hollow), stone (hard), sand (shuffle) |
| Door open/close | Wooden creak |
| Menu open | Paper rustle / click |
| Purchase | Cash register ding |
| Level up | Fanfare jingle + stat display |
| Season change | Unique transition melody |
| Clock chime | Subtle bell at midnight |
| Cooking | Sizzle, pot bubbling |

### 22.3 Audio Configuration
- Independent volume sliders: Music, Sound Effects, Ambient/Footsteps.
- Music transitions: Crossfade between location/time-of-day tracks over ~2 seconds.
- Rain and storm effects layer over music with dynamic volume ducking.
- Indoor/outdoor audio filtering: indoor areas muffle outdoor ambience.
- Music plays sparsely by design -- periods of silence between tracks to emphasize ambient sounds (birds, water, wind, insects).

## 23. Technical Foundation

### 23.1 Core Parameters
| Parameter | Value |
|---|---|
| Engine | MonoGame / XNA (C#) |
| Native resolution | 256x224 base (scaled to display resolution) |
| Tile size | 16x16 pixels |
| Character sprite | 16x32 pixels (world); 64x64 (portrait) |
| Target framerate | 60 FPS |
| Simulation tick | 10 in-game minutes per ~7 real seconds |
| Map format | Tiled-based with xnb data files |
| Save format | XML-based save files; one per slot |
| Random seed | Daily luck value determined per day; affects drop rates, treasure, gift preferences |
| Multiplayer | Up to 4 players (co-op); shared farm, independent inventories |

### 23.2 Update Order
1. Process input queue.
2. Advance game clock (if not paused).
3. Update player state machine and movement.
4. Update NPC schedules and pathfinding.
5. Update animal AI (grazing, returning to barn).
6. Process crop growth (daily at 6:00 AM on wake).
7. Process weather effects (watering, lightning strikes).
8. Resolve collisions (player-NPC, player-monster, tool-tile).
9. Apply damage/health/energy changes.
10. Update UI/HUD from authoritative game state.
11. Emit audio events.
12. Render frame.

### 23.3 Daily Calculations (Processed at Day Start / Sleep)
| System | Calculation |
|---|---|
| Crop growth | Each watered crop advances 1 growth stage; check maturity |
| Animal products | Determine daily product based on friendship + mood + random |
| Foraging respawn | Random forage items placed on map tiles |
| NPC schedules | Load daily pathing schedule based on season, day, weather, hearts |
| Daily luck | Random value (-0.1 to +0.1) determining bonus chances all day |
| Friendship decay | -2 per day for non-dated NPCs not talked to; -20 for ignored spouse |
| Energy restore | Based on sleep time and exhaustion status |
| Shipping payment | Sum of all items in shipping bin; gold added to wallet |

### 23.4 Save System
- Autosave at end of each day (after shipping summary).
- Save file contains: complete farm state, all NPC hearts, inventory, skills, calendar date, quest progress, Community Center progress, museum donations, achievements, mail flags, event flags.
- Save is atomic: write to temp file, verify, rename.
- Multiple save slots supported.

## 24. Data Contracts

### 24.1 Config Schema Example
```json
{
  "game": {
    "version": "1.5.6",
    "farm_type": "standard",
    "difficulty": "normal",
    "multiplayer": false,
    "cabin_limit": 3
  },
  "player": {
    "name": "Farmer",
    "farm_name": "Sunrise Farm",
    "favorite_thing": "Stardew",
    "pet": "cat",
    "max_energy": 270,
    "max_hp": 100,
    "gold": 500
  },
  "calendar": {
    "season": "spring",
    "day": 1,
    "year": 1,
    "time": "0600",
    "weather": "sunny"
  },
  "skills": {
    "farming": 0,
    "mining": 0,
    "foraging": 0,
    "fishing": 0,
    "combat": 0
  }
}
```

### 24.2 Runtime State Snapshot Example
```json
{
  "time": {
    "season": "summer",
    "day": 15,
    "year": 1,
    "clock": "1430",
    "weather": "rain",
    "daily_luck": 0.07
  },
  "player": {
    "position": { "x": 64, "y": 12 },
    "facing": "down",
    "energy": 180,
    "max_energy": 270,
    "hp": 100,
    "max_hp": 100,
    "gold": 15420,
    "held_item": "iridium_watering_can",
    "active_buffs": [
      { "type": "speed", "value": 1, "remaining_seconds": 420 }
    ]
  },
  "farm": {
    "crops": [
      {
        "tile": { "x": 5, "y": 8 },
        "type": "melon",
        "growth_stage": 3,
        "watered_today": true,
        "fertilizer": "quality_fertilizer",
        "days_since_plant": 6
      }
    ],
    "animals": [
      {
        "id": "cow_01",
        "type": "cow",
        "name": "Bessie",
        "friendship": 780,
        "mood": 200,
        "produced_today": false
      }
    ]
  },
  "relationships": [
    { "npc": "abigail", "hearts": 6, "points": 1540, "gifts_this_week": 1, "dating": false }
  ],
  "community_center": {
    "crafts_room": { "spring_foraging": true, "summer_foraging": false },
    "pantry": { "spring_crops": true, "summer_crops": false }
  },
  "skills": {
    "farming": { "level": 4, "xp": 1450 },
    "mining": { "level": 3, "xp": 820 },
    "foraging": { "level": 2, "xp": 400 },
    "fishing": { "level": 5, "xp": 2200, "profession": "fisher" },
    "combat": { "level": 2, "xp": 390 }
  }
}
```

## 25. Accessibility and UX
- Remappable controls for keyboard and gamepad.
- Independent volume sliders: Music, Sound Effects, Ambient.
- Zoom levels: 75% to 200% in 25% increments.
- UI scale adjustable independently of zoom.
- Auto-run toggle available.
- Tool hit location indicator (shows which tile will be affected).
- Inventory toolbar can be locked to top or bottom of screen.
- Colorblind considerations: crop quality indicated by both star shape and color; health/energy bars have distinct shapes.
- Text speed options for dialogue.
- Controller support with radial menus for tool/item selection.

## 26. Telemetry (For Evaluation and Balancing)
- Total gold earned per season.
- Crops planted/harvested per season with profit margins.
- Skill XP gain rates and level-up timestamps.
- NPC friendship progression timeline.
- Community Center bundle completion order and timestamps.
- Mining depth reached per session.
- Fish caught by type and quality distribution.
- Energy consumption patterns per day.
- Time-of-day activity distribution.
- Tool upgrade progression timeline.
- Artisan goods production volume and revenue.
- Festival participation and outcomes.
