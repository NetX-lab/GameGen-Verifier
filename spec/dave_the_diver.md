# Dave the Diver - Complete Game Specification

> A comprehensive specification for recreating DAVE THE DIVER (MINTROCKET, 2023), the single-player adventure, diving, fishing, and restaurant-management hybrid. This spec focuses on the dual daily loop: underwater exploration by day and sushi service by night.

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | DAVE THE DIVER |
| Developer | MINTROCKET |
| Initial Release | June 28, 2023 |
| Source Store | Steam |
| Genre | Adventure / simulation / restaurant management |
| Perspective | Side-view 2D diving; 2D management UI for restaurant |
| Input | Keyboard/gamepad; touch-friendly menus possible |
| Session Length | 20-60 minutes per in-game day cluster |
| Primary Objective | Dive to catch fish and gather resources, then serve profitable sushi at night to fund upgrades and story progress |
| Lose Condition | During diving, oxygen reaches 0 and Dave escapes with limited inventory loss; restaurant cannot hard fail in normal play |
| Win Condition | Complete story chapters, unlock areas, and build a successful sushi restaurant |
| Online Requirement | None |

## 2. AI-Generation Scope

Minimum viable clone:

- Day planner with morning/afternoon dives and night restaurant service.
- Side-view Blue Hole with fish AI, oxygen, depth pressure, weight limit, weapons, tools, and resource extraction.
- Restaurant with menu planning, wasabi refill, drink serving, staff, dish upgrades, customer patience, and revenue.
- Story missions that unlock depth zones and equipment tiers.

High-fidelity target:

- Dynamic Blue Hole layouts, boss dives, farm systems, staff training, VIP recipes, photo missions, sea people village, and research app progression.

## 3. Technical Foundation

| System | Requirement |
|--------|-------------|
| Diving Rendering | Side-view 2D with parallax water layers |
| Restaurant Rendering | Side-view restaurant with customer seats and service stations |
| Time | Day divided into Morning, Afternoon, Evening, and Night |
| Save | Auto-save at day transitions and before dives |
| Economy | Ingredients, gold, equipment upgrades, staff wages, recipe levels |
| Randomness | Blue Hole layout and fish spawns vary daily but obey depth zone tables |

Daily loop:

```text
1. Start day on planning screen
2. Choose dive or story event
3. Generate Blue Hole map for current time slot
4. Dive, catch fish, collect resources, manage oxygen and weight
5. Return to boat and convert catch into ingredients
6. Prepare night menu, staff, and upgrades
7. Run sushi service with customer orders and timed tasks
8. Pay revenue, costs, ratings, and story triggers
9. Advance calendar and unlock new missions
```

## 4. Diving Movement

Dave moves freely in 2D water:

| Action | Behavior |
|--------|----------|
| Swim | Directional movement with inertia and turn speed |
| Dash Swim | Short burst consuming stamina or creating recovery delay |
| Aim | Aim harpoon, gun, net, or tool |
| Fire/Use Tool | Attack fish, cut resources, open crates |
| Melee | Short knife attack for close defense or resource cutting |
| Interact | Loot containers, harvest, rescue, enter doors |

Depth:

- Deeper zones contain rarer fish and higher danger.
- Equipment limits maximum safe depth.
- Exceeding depth limit should drain oxygen faster or warn player.

Oxygen:

- Oxygen is both health and dive timer.
- Enemy attacks reduce oxygen.
- Oxygen tanks refill oxygen.
- At 0 oxygen, dive ends and player keeps only one selected item or a reduced catch set.

Weight:

- Fish and resources add weight.
- Above weight threshold, movement slows.
- Severe overweight prevents pickup or heavily slows ascent.

## 5. Fish And Underwater Entities

Fish definition:

```text
name, depth_range, size, speed, behavior, hp, aggression,
catch_method, meat_yield, star_quality_rules, sell_value, recipe_tags
```

Behaviors:

- Passive schooling fish flee when approached.
- Bottom dwellers move slowly near terrain.
- Predators patrol and charge Dave.
- Armored fish require upgraded weapons or weak-point hits.
- Rare fish appear only at certain times or weather.
- Boss creatures have phase attacks and story gating.

Catch quality:

- Harpoon or lethal damage gives lower quality.
- Net, tranquilizer, or gentle capture gives higher star quality.
- Higher quality yields better ingredients and dish value.

## 6. Blue Hole Generation

The Blue Hole is semi-procedural.

Map generation fields:

```text
day_seed, depth_zones, terrain_chunks, cave_entrances, currents,
resource_nodes, fish_spawn_tables, event_rooms, extraction_points
```

Depth zones:

| Zone | Depth | Content |
|------|-------|---------|
| Shallows | 0-50m | Small fish, tutorial resources, low danger |
| Mid Waters | 50-130m | Medium fish, predators, crates |
| Deep Waters | 130-250m | Valuable fish, hazards, oxygen pressure |
| Special Zone | Story-gated | Bosses, rare resources, puzzles |

## 7. Equipment

Upgrade categories:

| Equipment | Function |
|-----------|----------|
| Diving Suit | Increases depth limit |
| Air Tank | Increases oxygen capacity |
| Cargo Box | Increases weight limit |
| Harpoon Gun | Basic capture weapon |
| Rifle/Shotgun | Strong combat weapon with ammo |
| Net Gun | Captures small fish alive |
| Tranquilizer | Enables high-quality capture |
| Scooter | Improves movement temporarily |
| Salvage Tools | Unlock heavy resources |

Weapons should have ammo, range, damage, reload, and upgrade levels.

## 8. Restaurant Service

Restaurant phase is a timed service minigame.

Preparation:

1. Choose menu dishes from available ingredients.
2. Assign staff to cooking and serving roles.
3. Upgrade recipes by spending ingredients.
4. Check expected customer volume and VIP requests.

Service tasks:

- Customers enter and order dishes.
- Kitchen prepares dishes automatically or by staff speed.
- Dave or servers deliver dishes to customers.
- Refill wasabi before it runs out.
- Pour drinks with timing precision.
- Clean tables if implemented.

Customer patience:

- Each customer has a patience meter.
- Late service reduces rating and tip.
- Failed service wastes dish opportunity.

## 9. Recipes And Economy

Dish definition:

```text
name, ingredient_requirements, base_price, taste_score,
servings_per_prep, upgrade_level, unlock_condition
```

Revenue:

- Customer payment = dish price + tip based on service quality.
- Better fish quality can increase dish price or recipe upgrade value.
- Unsold menu items may waste ingredients depending on difficulty.

Expenses:

- Staff wages.
- Equipment upgrades.
- Research and app unlocks.

## 10. Staff System

Staff fields:

```text
name, role, serving, cooking, appeal, procurement, level, skills, wage
```

Staff can be:

- Hired from applicants.
- Trained to increase stats.
- Assigned to kitchen, floor, dispatch, or branch.
- Given skills such as drink serving, cleaning, wasabi refill, or ingredient prep.

## 11. Story And Mission Structure

Mission types:

- Catch a specific fish.
- Collect a specific resource.
- Photograph an underwater target.
- Defeat or avoid a boss.
- Serve a VIP dish by a deadline.
- Upgrade equipment to access a new zone.

Story missions should introduce new mechanics gradually and unlock new systems rather than only giving money.

## 12. UI Layout

Diving HUD:

- Oxygen bar.
- Depth meter.
- Weight gauge.
- Weapon/ammo indicator.
- Mini objective list.
- Inventory quick view.

Restaurant HUD:

- Night timer.
- Customer patience bubbles.
- Current orders.
- Wasabi meter.
- Revenue counter.
- Staff status icons.

## 13. Visual And Audio Direction

- Water layers should become darker and more saturated with depth.
- Fish silhouettes must be identifiable by size and movement.
- Restaurant should feel busy but readable; orders need clear icons.
- Audio contrast: muffled underwater ambience by day, lively restaurant music by night.

## 14. Validation Checklist

- Oxygen loss can end a dive without ending the whole game.
- Weight changes swim speed and pickup decisions.
- Fish quality changes based on capture method.
- Night menu only uses ingredients actually owned.
- Customers lose patience and pay based on service quality.
- Equipment upgrades unlock deeper zones and stronger catch options.
