# Dwarf Fortress — Complete Game Specification

## 1. Game Overview

Dwarf Fortress is an extremely complex simulation game with two primary modes:
Fortress Mode (build and manage a dwarven settlement) and Adventure Mode (roguelike
RPG). This specification covers both modes with emphasis on Fortress Mode. The game
simulates a detailed fantasy world with geology, fluid dynamics, temperature, combat
with individual body parts, and rich emergent storytelling.

Platform: Single-player, 2D top-down (multi-z-level) tile-based simulation.
Visual style: ASCII/tileset-based. Each tile represents terrain, creatures, items.
Map: Fortress embark site is typically 3x3 to 5x5 world tiles (~150x150 to 250x250 local tiles per z-level).

## 2. Technical Foundation

### 2.1 World Generation
```
World generation creates:
  - Landmasses with tectonic simulation
  - Climate zones (temperature, rainfall)
  - Biomes (100+ types)
  - Rivers, lakes, oceans
  - Mineral layers with realistic geology
  - Civilizations (dwarves, humans, elves, goblins)
  - 250-1000+ years of history
  - Named historical figures, wars, artifacts

Parameters:
  World size: Pocket (17x17) to Large (257x257) region tiles
  History length: 5-1050 years
  Civilization count: varies
  Megabeast count: varies
```

### 2.2 Map Structure (Fortress Mode)
```
struct FortressMap {
    tiles: 3D_array[width][height][z_levels]  // Typically 192x192x~200
    z_levels: ~200 (sky to deep underground)
    surface_level: varies by terrain

    struct Tile {
        material: Material       // granite, iron ore, soil, etc.
        type: TileType           // wall, floor, ramp, stair, open space
        designation: Designation // dig, channel, smooth, carve
        building: Building | null
        items: list[Item]
        creature: Creature | null
        temperature: integer     // In degrees (custom scale)
        liquid: {type: WATER|MAGMA, level: 0-7}
        grass: GrassType | null
        tree: TreePart | null
    }
}
```

### 2.3 Material System
Over 200 materials with properties:
```
struct Material {
    name: string
    type: enum(STONE, METAL, WOOD, CLOTH, LEATHER, BONE, GEM, GLASS, CERAMIC)
    value: integer               // Relative wealth value
    density: integer             // kg/m3
    fracture_strength: integer   // For combat
    yield_strength: integer      // For combat
    melting_point: integer       // Temperature
    boiling_point: integer
    hardness: integer            // Mohs-like scale
    color: Color
}
```

### 2.4 Stone Layers (Geology)
```
Soil layers: 1-8 z-levels deep (clay, loam, sand, silt, peat)
Sedimentary: limestone, sandstone, chalk, shale, mudstone
Igneous (intrusive): granite, gabbro, diorite
Igneous (extrusive): obsidian, basalt, rhyolite
Metamorphic: marble, slate, quartzite, gneiss, schist

Ore veins embedded in stone:
  Iron: magnetite, hematite, limonite (in sedimentary)
  Copper: native copper, malachite, tetrahedrite
  Tin: cassiterite (in granite)
  Gold: native gold (in igneous intrusive)
  Silver: native silver, galena (in multiple)
  Platinum: native platinum (rare, in igneous)
  Adamantine: special deep stone (extremely rare, dangerous)
```

## 3. Fortress Mode

### 3.1 Embark
```
embark_setup:
  - Choose 7 starting dwarves
  - Assign skills to each (total ~70 skill points)
  - Choose supplies (default: food, drink, animals, seeds, tools)
  - Starting points: 1504 (to spend on skills + supplies)
  - Select embark site on world map (biome, resources, neighbors)
```

### 3.2 Dwarf Properties
```
struct Dwarf {
    name: string
    age: integer
    gender: enum(MALE, FEMALE)

    // Physical attributes (0-5000+, average ~1000)
    strength: integer
    agility: integer
    toughness: integer
    endurance: integer
    recuperation: integer
    disease_resistance: integer

    // Mental attributes
    focus: integer
    willpower: integer
    creativity: integer
    intuition: integer
    patience: integer
    memory: integer
    linguistic_ability: integer
    spatial_sense: integer
    musicality: integer
    analytical_ability: integer
    empathy: integer
    social_awareness: integer

    // Skills (0-20, Legendary at 15+)
    skills: dict[SkillName, SkillLevel]
    // 80+ skills: mining, masonry, carpentry, cooking, brewing,
    //   smithing, armorsmithing, weaponsmithing, engraving, etc.

    // Personality (each trait on a scale)
    personality_traits: dict[Trait, integer]
    // Traits: anxiety, anger, depression, stress, greed, etc.

    // Needs
    happiness: integer          // -1000 to 1000+ (0=neutral)
    stress: integer             // 0-500000+
    hunger: float
    thirst: float
    drowsiness: float

    // Body
    body_parts: list[BodyPart]  // Each can be wounded/missing
    blood_volume: float         // Bleeding tracking

    // Social
    relationships: list[Relationship]
    thoughts: list[Thought]     // Recent positive/negative thoughts
    beliefs: list[Belief]
    goals: list[Goal]
}
```

### 3.3 Skill List (Major Skills)
| Category     | Skills                                                    |
|-------------|-----------------------------------------------------------|
| Mining      | Mining, Engraving                                         |
| Woodwork    | Carpentry, Wood Cutting, Wood Crafting                    |
| Stonework   | Masonry, Stone Crafting, Stone Detailing                  |
| Metalwork   | Smithing, Armorsmithing, Weaponsmithing, Metal Crafting   |
| Craft       | Leatherworking, Bonecarving, Weaving, Clothesmaking       |
| Food/Drink  | Cooking, Brewing, Butchery, Tanning, Fishing              |
| Medical     | Diagnostics, Surgery, Bone Setting, Suturing, Dressing    |
| Military    | Axe, Sword, Mace, Hammer, Spear, Crossbow, Shield, Armor |
| Social      | Negotiator, Consoler, Comedian, Leader                    |
| Other       | Mechanics, Architecture, Animal Training, Siege Engineering|

### 3.4 Designation System
| Designation   | Key | Effect                                    |
|--------------|-----|-------------------------------------------|
| Mine         | d   | Dwarves dig out designated tiles           |
| Channel      | h   | Dig out tile and create ramp below         |
| Up Stair     | u   | Carve upward staircase                     |
| Down Stair   | j   | Carve downward staircase                   |
| Up/Down Stair| i   | Combined staircase                         |
| Ramp         | r   | Create ramp                                |
| Smooth       | s   | Smooth stone walls/floors                  |
| Engrave      | e   | Carve art into smoothed surfaces           |
| Chop Trees   | t   | Mark trees for cutting                     |
| Gather Plants| p   | Gather surface plants                      |
| Dump         | D   | Mark items for dumping                     |

### 3.5 Workshop System
| Workshop           | Materials to Build | Produces                        |
|-------------------|-------------------|----------------------------------|
| Carpenter's       | 1 Log             | Furniture, barrels, bins, beds    |
| Mason's           | 1 Stone            | Stone furniture, blocks           |
| Craftsdwarf's     | 1 Stone            | Crafts, instruments, toys         |
| Metalsmith's Forge| 1 Anvil, 1 Building Material | Metal items, armor, weapons |
| Smelter           | 1 Building Material| Smelt ore to bars                |
| Wood Furnace      | 1 Building Material| Charcoal from wood               |
| Kitchen           | 1 Building Material| Prepared meals                   |
| Still             | 1 Building Material| Brew drinks from plants          |
| Loom              | 1 Building Material| Cloth from thread/yarn           |
| Tanner's          | 1 Building Material| Leather from hides               |
| Butcher's         | 1 Building Material| Butcher animals for meat/bones   |
| Mechanic's        | 1 Building Material| Mechanisms for traps/bridges     |
| Siege Workshop    | 1 Building Material| Catapults, ballistas             |
| Jeweler's         | 1 Building Material| Cut gems, encrust items          |

### 3.6 Room System
```
Rooms are designated zones:
  - Bedroom (bed required): assigned to dwarf, affects happiness
  - Dining Room (table+chair): communal or assigned
  - Office (chair+table): for nobles/administrators
  - Tomb (coffin): burial site
  - Hospital (bed+table+container): medical treatment
  - Barracks (armor stand/weapon rack): military training
  - Jail (chain/cage): for criminals

Room quality = sum(item_quality * item_value) in room
  quality levels: MEAGER, MODEST, DECENT, FINE, GREAT, GRAND, ROYAL
```

## 4. Resource Management

### 4.1 Food System
```
Each dwarf eats ~2 meals per season (game time)
Food sources:
  - Farming (underground: plump helmets, pig tails, sweet pods, cave wheat)
  - Farming (surface: wheat, barley, various vegetables)
  - Hunting (butchered animal meat)
  - Fishing (river/lake fish)
  - Trade caravans
  - Gathered plants (surface foraging)

Prepared meals (in kitchen):
  - Easy meal: 2 ingredients, value varies
  - Fine meal: 3 ingredients, higher value
  - Lavish meal: 4 ingredients, highest value
  - Ingredient variety increases meal value

food_storage: in barrels or pots (prevents rot)
rot_time: ~1 season if not stored properly
```

### 4.2 Drink System
```
Each dwarf drinks ~4 drinks per season
Dwarves prefer alcohol (unhappy drinking water)
Brewing: 1 plant → ~5 units of alcohol (at Still)

Drink types:
  - Dwarven Wine (from plump helmets)
  - Dwarven Ale (from sweet pods)
  - Dwarven Beer (from wheat/barley)
  - Dwarven Rum (from sweet pods)
  - Various fruit wines

storage: in barrels
```

### 4.3 Trade System
```
Caravans arrive seasonally:
  - Dwarven caravan (Autumn): most goods, request fulfillment
  - Human caravan (Summer): diverse goods
  - Elven caravan (Spring): wooden goods, animals, cloth (no wood items for trade!)

Trade value = item.material_value * item.quality_modifier * item.type_value
Quality modifiers: Well-crafted x2, Superior x3, Exceptional x5, Masterwork x12, Artifact x120

Export strategies:
  - Crafts (stone/bone crafts are high value/effort ratio)
  - Prepared meals (lavish meals with valuable ingredients)
  - Metal items (steel weapons/armor)
  - Gems (cut gems)
```

## 5. Military System

### 5.1 Squad Organization
```
Squads: groups of up to 10 dwarves
  - Assign equipment (uniform)
  - Assign schedule (training/patrol/guard)
  - Assign barracks for training

Equipment types:
  - Weapons: swords, axes, maces, hammers, spears, crossbows
  - Armor: helm, mail shirt, breastplate, gauntlets, greaves, boots, shield
  - Material hierarchy: copper < bronze < iron < steel < adamantine

Training:
  - Dwarves spar in barracks
  - Skill improves with practice
  - Individual combat drills
  - Danger rooms (training with traps, controversial)
```

### 5.2 Combat System
```
Combat is per-body-part:
  attack targets specific body part
  attack types: slash, stab, bash, bite, scratch

  hit_chance = attacker_skill - defender_skill + modifiers

  damage_calculation:
    contact_area = weapon.edge_area (for sharp) or weapon.surface_area (for blunt)
    force = attacker.strength * weapon.weight * velocity
    stress = force / contact_area

    if stress > material.yield_strength: tissue deforms
    if stress > material.fracture_strength: tissue breaks/severs

  wound_effects:
    - Bleeding (blood loss tracking)
    - Pain (can cause unconsciousness)
    - Severed limbs (permanent)
    - Broken bones (requires setting)
    - Organ damage (can be fatal)
    - Bruising (minor)

  armor:
    reduces effective stress based on material properties
    can be penetrated by sufficient force
    coverage: partial body coverage map
```

### 5.3 Siege Defense
```
Defense structures:
  - Walls (any material, blocks movement)
  - Fortifications (allow shooting through, block movement)
  - Drawbridges (can be raised to seal entry, crushes creatures)
  - Cage traps (captures creatures)
  - Stone-fall traps (drops heavy stone)
  - Weapon traps (uses installed weapons)
  - Flooding (channel water/magma into passages)
  - Atom smasher (raising drawbridge on creatures/items)
```

## 6. Happiness and Stress

### 6.1 Happy Thoughts
| Source              | Happiness Bonus |
|--------------------|-----------------|
| Fine bedroom       | +modest         |
| Great dining room  | +moderate       |
| Good meal          | +small          |
| Alcohol            | +small          |
| Masterwork item    | +moderate       |
| Completed artifact | +large          |
| Talking to friend  | +small          |
| Seeing nature      | +small          |
| Beautiful room     | +moderate       |

### 6.2 Unhappy Thoughts
| Source                  | Stress Increase |
|------------------------|-----------------|
| Death of friend/family | +very large     |
| Saw dead body          | +large          |
| Rained on              | +small          |
| No alcohol             | +moderate       |
| Poor bedroom           | +moderate       |
| Attacked               | +large          |
| Vermin in food         | +small          |
| Cave adaptation (sun)  | +moderate       |
| Mandates not met       | +moderate       |

### 6.3 Mental Breaks
```
if stress > threshold:
    break_type = based on personality:
      - Tantrum (violent, attacks others/items)
      - Depression (lies in bed, refuses to work)
      - Berserk (extremely violent, must be subdued)
      - Oblivious wandering (wanders aimlessly)
      - Stark raving mad (permanent insanity)
      - Catatonic (unresponsive)
      - Melancholy (suicidal)

// Cascade: one dwarf's tantrum can stress others → tantrum spiral
```

## 7. Noble System

### 7.1 Noble Positions
| Noble          | Requirement           | Demands                          |
|---------------|----------------------|----------------------------------|
| Expedition Leader| Start of game      | Office                           |
| Mayor         | 50+ dwarves          | Office, bedroom, dining room     |
| Manager       | Appointed            | Office                           |
| Bookkeeper    | Appointed            | Office                           |
| Sheriff/Captain| Appointed           | Office, jail                     |
| Baron         | Royal appointment    | Grand quarters, throne room      |
| Count         | Further progression  | Even grander quarters            |
| Duke          | Further progression  | Royal quarters                   |
| King          | Capital of civilization| Legendary quarters              |

### 7.2 Noble Mandates
Nobles periodically mandate:
- Production of specific items (must be fulfilled)
- Ban of specific exports (must be obeyed)
- Failure → dwarf gets punished in jail

## 8. Adventure Mode (Basics)

### 8.1 Character Creation
```
Choose:
  - Race (dwarf, human, elf)
  - Starting location (fortress, town, wilderness)
  - Attributes and skills (point-buy system)
  - Background/civilization

Attributes: same as Fortress Mode dwarves
Skills: same skill list, chosen at creation
```

### 8.2 Adventure Gameplay
```
Turn-based movement and combat on the same world map
  - Travel between sites (fast travel on world map)
  - Enter sites (towns, dungeons, lairs, fortresses)
  - Talk to NPCs (ask about quests, rumors, directions)
  - Fight monsters and bandits
  - Loot treasure
  - Gain reputation and followers

Combat: same body-part system as Fortress Mode
  - Choose attack: slash/stab/bash
  - Choose target body part
  - Consider weapon reach vs enemy size
  - Grappling system for close combat
  - Dodge/block/parry skills

Quest system:
  - Generated quests based on world history
  - "Slay the beast [name] at [location]"
  - "Retrieve the artifact [name] from [location]"
  - NPCs provide directions and rumors
```

## 9. Fluid Dynamics

### 9.1 Water
```
Water levels: 0-7 per tile
Water flows downhill (obeys gravity through z-levels)
Water pressure: builds up behind walls
Water source: rivers, underground caverns, rain
Water can freeze (in cold biomes)
Water puts out fire
Dwarves can drown (swim skill matters)
Water wheels: generate power from flowing water
```

### 9.2 Magma
```
Magma levels: 0-7 per tile
Magma found deep underground (magma sea, magma pipes)
Magma forges: free fuel for smelting/forging
Magma destroys most items
Obsidian: formed when water meets magma
Magma-proof materials: iron, steel, adamantine, raw stone
```

## 10. UI Layout (Classic ASCII)

```
+------------------------------------------------------------------+
|                     Dwarf Fortress                                 |
+------------------------------------------------------------------+
| #######+#########    | Announcements:                             |
| #.......#........    | A recruit has become a Legendary Miner!    |
| #.T..C..#..h.h..    | Spring has arrived!                        |
| #.......+..h.h..    | A caravan from the Mountainhomes has arrived|
| #.......#........    |                                            |
| #####+####+####      | Units: 87 Dwarves                          |
| .....X........       | Food: 2450                                 |
| .....d........       | Drink: 1820                                |
| ......≈≈≈.....      | Wealth: 245,000☼                           |
| .......≈≈......      |                                            |
| ................     | Current z-level: -5                        |
| ~~~~≈≈≈≈~~~~..      | Season: Mid-Spring, Year 128               |
+------------------------------------------------------------------+
| [d]esignate [b]uild [q]uery [k]look [z]status [m]ilitary [n]oble|
+------------------------------------------------------------------+
Legend:
  # = Wall (stone)        . = Floor
  + = Door                T = Table
  C = Chair               h = Bed (horizontal)
  X = Up/Down Staircase   d = Dwarf
  ≈ = Water               ~ = Murky Pool
```

## 11. Key Simulation Systems

### 11.1 Temperature
```
Every tile has a temperature
Heat sources: magma, fire, forges
Cold: above-ground in winter, ice biomes
Effects: water freezes/thaws, creatures get too hot/cold
Fire: flammable materials ignite at high temps
Temperature propagates through adjacent tiles
```

### 11.2 Plant Growth
```
Surface plants: grow in spring/summer/fall, die in winter
Underground plants: grow year-round (plump helmets, etc.)
Trees: grow over multiple years, can be cut
Farm plots: designate area, assign crop, dwarves plant/harvest
Seasons affect what can be planted
```

### 11.3 Pathfinding
```
A* pathfinding across 3D space
Dwarves path through stairs, ramps
Locked doors block pathing
Burrows restrict dwarf movement
Traffic designations affect path cost:
  High traffic: preferred
  Normal: default
  Low traffic: avoided
  Restricted: only if no alternative
```

## 12. Constants

```
EMBARK_DWARVES = 7
STARTING_EMBARK_POINTS = 1504
MAX_Z_LEVELS = ~200
SEASONS_PER_YEAR = 4
TICKS_PER_SEASON = ~33600
TICKS_PER_DAY = 1200
SKILL_LEVELS = {0: Dabbling, 3: Competent, 5: Proficient, 8: Talented, 11: Expert, 14: Master, 15+: Legendary}
WATER_MAX_LEVEL = 7
MAGMA_MAX_LEVEL = 7
MAX_SQUAD_SIZE = 10
FOOD_PER_DWARF_PER_SEASON = 2 meals
DRINK_PER_DWARF_PER_SEASON = 4 drinks
BREWING_RATIO = 1 plant : 5 drinks
```

## 13. Implementation Priority

1. Tile-based multi-z-level map
2. Dwarf movement and simple pathfinding
3. Mining designation and execution
4. Basic resource tracking (food, drink)
5. Workshop construction and basic crafting
6. Farming system
7. Brewing
8. Room designation (bedrooms, dining)
9. Dwarf happiness/stress system
10. Trade caravans
11. Military squads and basic combat
12. Fluid dynamics (water, basic)
13. Noble system
14. Siege events
15. Adventure mode basics
16. Detailed combat system
