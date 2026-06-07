# Don't Starve - Complete Game Specification

> A comprehensive specification for recreating Don't Starve (Klei Entertainment, 2013), the single-player wilderness survival sandbox. This spec covers world generation, survival meters, crafting, seasons, creatures, and permadeath structure.

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Don't Starve |
| Developer | Klei Entertainment |
| Initial Release | April 23, 2013 |
| Source Store | Steam, App Store |
| Genre | Survival adventure / crafting sandbox |
| Perspective | 2.5D isometric/top-down |
| Input | Keyboard/mouse or controller; touch possible with contextual actions |
| Session Length | Open-ended; first survival goal is 20+ days |
| Primary Objective | Survive as long as possible by gathering, crafting, exploring, and managing hunger, health, and sanity |
| Lose Condition | Character dies without a resurrection item or world setting |
| Win Condition | Sandbox has no default final win; Adventure Mode or milestones can provide completion |
| Online Requirement | None for original single-player |

## 2. AI-Generation Scope

Minimum viable clone:

- Procedural overworld with biomes, resources, day/dusk/night cycle, hunger, health, sanity, crafting, fire, tools, food spoilage, and hostile creatures.
- One playable character and a 30-day survival milestone.
- Seasons can be simplified to autumn and winter for first version.

High-fidelity target:

- Multiple characters, caves, ruins, magic, summer/spring, giants, Adventure Mode, farming, followers, and world customization.

## 3. Technical Foundation

| System | Requirement |
|--------|-------------|
| Rendering | Stylized 2D sprites in an isometric world |
| World | Procedurally generated tilemap with biome regions and set pieces |
| Time | Day cycle split into Day, Dusk, and Night |
| Save | Auto-save at dawn; permadeath deletes or archives world unless resurrection exists |
| Simulation | Entities update in active area; distant entities can use simplified timers |
| Randomness | World seed controls map, set pieces, creature dens, and resource placement |

Update loop:

```text
1. Advance clock and season timers
2. Process player movement, action queue, inventory, and crafting
3. Update survival meters: hunger drain, sanity modifiers, temperature, wetness
4. Update nearby creatures, combat, resource regrowth, fire, and spoilage
5. Resolve darkness damage if night and no light source
6. Spawn periodic threats such as hound waves
7. Check death, resurrection, day transition, and save
8. Render world, entities, shadows, light radius, UI, and crafting menu
```

## 4. Survival Meters

| Meter | Behavior |
|-------|----------|
| Hunger | Drains over time; at 0, health decreases |
| Health | Damage from combat, hunger, darkness, temperature, poison or hazards |
| Sanity | Changes based on darkness, monsters, food, clothing, actions, and time |
| Temperature | Too cold or hot damages health unless protected |
| Wetness | Optional; increases freezing risk and item slipperiness |

Sanity effects:

- Low sanity causes visual distortion.
- Shadow creatures appear and may attack.
- Some magic actions consume sanity.
- Flowers, cooked food, clothing, and sleep can restore sanity.

## 5. Day And Light

The clock has three phases:

| Phase | Rules |
|-------|-------|
| Day | Safest exploration and gathering time |
| Dusk | Lower visibility, some creatures return home, sanity may drain |
| Night | Complete darkness is lethal unless near fire or light source |

Light sources:

- Campfire: temporary, fueled by logs/grass.
- Fire pit: permanent structure, fueled.
- Torch: portable but burns down.
- Lantern/miner hat: later reusable light with fuel.

Darkness damage should be immediate enough to teach danger but allow a short reaction window.

## 6. World Generation

World generation steps:

1. Choose seed and world settings.
2. Create connected landmass or islands using biome blobs.
3. Place starting area with basic resources.
4. Place biome-specific resources and creature dens.
5. Add roads, wormholes, set pieces, pig villages, graveyards, swamp, rocky areas, and optional cave entrances.
6. Validate that essential resources exist within reasonable travel distance.

Biomes:

| Biome | Resources | Risks |
|-------|-----------|-------|
| Grassland | Grass, saplings, flowers, rabbits | Low food density after trapping |
| Forest | Trees, mushrooms, spiders | Spider nests, treeguards |
| Savanna | Beefalo, grass, rabbits | Beefalo mating aggression |
| Rockyland | Rocks, gold, flint | Sparse food |
| Swamp | Reeds, tentacles, merms | High danger |
| Deciduous | Birchnut trees, cats, berries | Seasonal threats |

## 7. Inventory And Crafting

Inventory:

- Limited item slots.
- Items can stack up to category-specific limits.
- Tools have durability.
- Food has freshness/spoilage.

Crafting categories:

| Category | Examples |
|----------|----------|
| Tools | Axe, pickaxe, shovel, hammer |
| Light | Campfire, fire pit, torch |
| Survival | Trap, backpack, fishing rod, bug net |
| Food | Crock pot, drying rack, farm plot |
| Science | Science machine, alchemy engine |
| Fight | Spear, log suit, football helmet |
| Magic | Prestihatitator, amulets, staffs |
| Structures | Chests, walls, signs, flooring |

Prototype rule:

- Some recipes require standing near a science or magic station once.
- After prototyping, the recipe may become craftable anywhere if the original rules allow it.

## 8. Food System

Food fields:

```text
name, hunger_delta, health_delta, sanity_delta, spoil_time,
cook_result, crockpot_tags, perish_state
```

Food rules:

- Raw foods can be cooked over fire.
- Crock pot combines four ingredients into recipes based on tags.
- Spoiled food gives poor values and may hurt health/sanity.
- Monster meat is risky but useful in recipes.
- Hunger restoration should not always correlate with health restoration.

## 9. Creatures And Combat

Creature fields:

```text
id, biome, hp, damage, attack_period, speed, aggro_rule,
day_behavior, drops, herd_or_den, sanity_aura
```

Archetypes:

- Passive prey: rabbits, birds, butterflies.
- Neutral herd: beefalo, pigs.
- Den enemies: spiders, hounds.
- Territorial hazards: tentacles, tallbirds.
- Night/shadow enemies: sanity-based threats.
- Giants/bosses: seasonal large enemies with area attacks.

Combat:

- Click or button targets enemy.
- Player attacks at weapon-defined rate.
- Enemy attacks have cooldown and range.
- Armor absorbs percentage or durability-based damage.

## 10. Seasons

Minimum two-season implementation:

| Season | Length | Threats |
|--------|--------|---------|
| Autumn | Mild start, resource gathering | Hound waves |
| Winter | Cold, scarce food, long nights | Freezing, deerclops-style boss |

Full implementation adds:

- Spring rain, wetness, frog rain.
- Summer overheating, wildfires, antlion-style pressure.

Season preparation is the strategic arc: gather food, craft clothing, build base, and prepare fuel.

## 11. Progression And Goals

Sandbox milestones:

- Survive first night.
- Build science machine.
- Build stable food source.
- Survive first hound wave.
- Survive winter.
- Defeat seasonal boss.
- Find portal or Adventure Mode entry.

Adventure Mode can be simplified into generated challenge chapters with special world rules and a final escape objective.

## 12. UI Layout

- Top right: day clock, season, day count.
- Right side: hunger, health, sanity meters.
- Bottom: inventory bar.
- Left: crafting categories and recipe list.
- Context prompt near cursor/target: Chop, Mine, Pick, Attack, Eat, Build.
- Map screen: discovered terrain only.

## 13. Visual And Audio Direction

- Hand-drawn cutout style with strong silhouettes.
- Night should visibly shrink to the light radius.
- Sanity distortion should be noticeable but not unreadable.
- Audio cues: hound warning, night arrival, fire crackle, tool break, creature aggro.

## 14. Validation Checklist

- Player dies in darkness without light.
- Hunger at zero drains health.
- Low sanity spawns shadow threats.
- Essential resources are reachable in generated worlds.
- Food spoils over time and cooked/crockpot recipes behave differently.
- Winter requires warmth preparation to survive.

