# FTL Faster Than Light - Complete Game Specification

> A comprehensive specification for recreating FTL: Faster Than Light (Subset Games, 2012), the single-player real-time-with-pause spaceship roguelike. This spec covers ship systems, crew, power, rooms, events, combat, sectors, scrap upgrades, and final boss structure.

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | FTL: Faster Than Light |
| Developer | Subset Games |
| Initial Release | September 14, 2012 |
| Source Store | Steam, App Store |
| Genre | Roguelike strategy / spaceship management |
| Perspective | 2D ship cutaway plus sector map |
| Input | Mouse-heavy with keyboard pause and hotkeys |
| Session Length | 1-2 hours per run |
| Primary Objective | Navigate sectors, upgrade the ship, survive events, and defeat the Rebel Flagship |
| Lose Condition | Player hull reaches 0 or unavoidable story failure |
| Win Condition | Destroy all required phases of the final flagship |
| Online Requirement | None |

## 2. AI-Generation Scope

Minimum viable clone:

- Player ship with rooms, systems, crew, power reactor, weapons, shields, oxygen, engines, medbay, doors, sensors, and piloting.
- Sector map with beacons, text events, stores, enemy ships, rewards, and rebel fleet pursuit.
- Real-time-with-pause combat, scrap upgrades, fires, breaches, boarding, and final boss.

High-fidelity target:

- Multiple ship layouts, alien species, drones, hacking, mind control, clone bay, augments, blue event options, achievements, and advanced content.

## 3. Technical Foundation

| System | Requirement |
|--------|-------------|
| Rendering | 2D ship interior rooms and UI panels |
| Time | Real-time simulation with pause |
| State | Ship systems, crew positions, enemy ship, projectiles, fires, breaches, events |
| Randomness | Seeded run for sector layout, events, stores, and rewards |
| Save | Save on jump and quit; permadeath run structure |
| Input | Pause must be instant and central to play |

Combat loop:

```text
1. Player assigns power, weapons, crew, doors, and targets while paused or live
2. Weapons charge based on system power and crew skill
3. Enemy AI charges and fires weapons, launches drones, boards, or repairs
4. Projectiles travel and hit/miss based on evasion and defense effects
5. Damage applies to shields, hull, systems, rooms, crew, fires, and breaches
6. Crew move, fight, repair, heal, suffocate, or extinguish fires
7. Check surrender, enemy destruction, player destruction, or jump readiness
```

## 4. Ship Layout

Ship is a grid of connected rooms.

Room fields:

```text
id, tiles, system_id, oxygen_level, fire_level, breach,
doors, crew_inside, boarders_inside
```

Core systems:

| System | Function |
|--------|----------|
| Piloting | Required for evasion and jumping |
| Engines | Increases evasion and charges FTL |
| Shields | Blocks laser/beam/projectile layers |
| Weapons | Powers and fires weapons |
| Oxygen | Refills room oxygen |
| Medbay | Heals friendly crew inside |
| Doors | Controls door strength and venting |
| Sensors | Reveals room and enemy information |
| Reactor | Provides power bars |

Optional systems:

- Drone control.
- Teleporter.
- Cloaking.
- Hacking.
- Mind control.
- Clone bay.

## 5. Power Management

Rules:

- Reactor provides finite power bars.
- Systems have maximum upgrade bars.
- Player can allocate/deallocate power at any time.
- Ion damage temporarily locks powered bars.
- Damaged system bars cannot be powered until repaired.

Power tension is core. The UI must make it fast to depower oxygen to power weapons, or depower medbay to power engines, etc.

## 6. Crew System

Crew fields:

```text
name, species, hp, room, task, combat_skill, repair_skill,
pilot_skill, engine_skill, weapon_skill, shield_skill, suffocation_rate
```

Species examples:

| Species | Traits |
|---------|--------|
| Human | No special modifier, skill learning bonus optional |
| Engi | Fast repair, weak combat |
| Mantis | Strong combat, slow repair |
| Rock | High HP, immune to fire, slow movement |
| Zoltan | Provides power to occupied system, low HP |
| Slug | Telepathic sensors, immune to mind control if implemented |
| Lanius | Drains oxygen, no suffocation |

Crew tasks:

- Manning system for bonuses.
- Repairing damage.
- Fighting boarders.
- Extinguishing fire.
- Moving between rooms.
- Healing in medbay.

## 7. Weapons And Damage

Weapon definition:

```text
name, type, power_required, charge_time, shots,
damage, shield_pierce, breach_chance, fire_chance, stun_chance,
targeting_rule, projectile_speed
```

Weapon types:

- Laser: individual shots, blocked by shields.
- Missile: consumes missile ammo, bypasses shields, can miss.
- Beam: line damage after shields are down or pierced.
- Bomb: teleports to room, bypasses shields, no hull damage unless specified.
- Ion: disables shield/system power temporarily.
- Flak: area projectiles with spread.

Damage applies to:

- Hull.
- System bars.
- Crew in room.
- Fires.
- Breaches.
- Stun effects.

## 8. Combat Systems

Shields:

- Each shield layer blocks one normal projectile or reduces beam damage.
- Ion can temporarily remove layers.
- Shield system damage reduces maximum layers.

Evasion:

- Requires piloting manned/auto and engines powered.
- Incoming projectiles roll hit/miss.
- Beams do not miss once fired if path intersects.

Oxygen and venting:

- Rooms have oxygen percentage.
- Breaches and open doors to space drain oxygen.
- Crew take suffocation damage in low oxygen.
- Venting is a tactical tool against boarders and fires.

Fires:

- Damage systems and crew over time.
- Spread to adjacent rooms.
- Extinguished by crew or vacuum.

## 9. Sector Map And Events

Sector:

```text
id, type, beacon_graph, store_nodes, quest_nodes,
exit_node, rebel_fleet_position, environmental_hazards
```

Beacon events:

- Enemy combat.
- Distress call.
- Store.
- Empty salvage.
- Moral choice.
- Crew recruitment.
- Hazard: asteroid field, nebula, pulsar, solar flare.

Rebel fleet:

- Advances after each jump.
- Catches beacons behind player.
- Fighting fleet ships is dangerous and low reward.
- Exit beacon moves player to next sector if reached.

## 10. Economy And Upgrades

Scrap is main currency.

Spend scrap on:

- System upgrades.
- Reactor bars.
- Repairs.
- Fuel, missiles, drone parts.
- Weapons, drones, crew.
- Augments.

Upgrade costs should rise by level. Stores are random but categorized.

## 11. Events And Choices

Event definition:

```text
id, text, choices, requirements, outcomes, rewards, followup_event
```

Choice outcomes:

- Fight enemy.
- Gain/lose scrap.
- Gain/lose crew.
- Take hull damage.
- Spend missiles/fuel.
- Blue option from crew/system/augment creates better result.

Avoid long text walls. Choices should reveal risk tone but not exact math unless debug mode.

## 12. Final Boss

Final flagship:

- Multi-phase fight.
- Repairs between phases may be limited.
- Phase 1: strong weapons and cloaking/hacking style pressure.
- Phase 2: drone surge and boarding risk.
- Phase 3: super shield, mind control/boarders, power surge.

Victory requires destroying final phase before player base is lost.

## 13. UI Layout

- Top: hull, shields, fuel, missiles, drone parts, scrap.
- Bottom: system power bars and weapon controls.
- Center left/right: player and enemy ships.
- Crew list with health and room assignment.
- Sector map screen for jumps.
- Event modal with text choices.

## 14. Visual And Audio Direction

- Rooms must show oxygen, fire, breach, system damage, and crew clearly.
- Weapon charge bars need exact readability.
- Pause/unpause sound should be subtle but clear.
- Combat audio: lasers, missiles, shield hit, hull breach, fire, crew damage, FTL jump.

## 15. Validation Checklist

- Pause freezes combat and allows orders.
- Deallocating reactor power immediately disables systems.
- Damaged systems cannot use damaged bars.
- Fires spread and can be vented.
- Crew suffocate in low oxygen.
- Sector exit and rebel fleet pursuit create route pressure.
- Final boss has multiple phases and can end in victory.

