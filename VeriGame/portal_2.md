# Portal 2 - Complete Game Specification

> A comprehensive specification for recreating the single-player puzzle core of Portal 2 (Valve, 2011). This document focuses on first-person portal mechanics, physics puzzles, test chamber structure, puzzle devices, and readable spatial problem solving.

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Portal 2 |
| Developer | Valve |
| Initial Release | April 18, 2011 |
| Source Store | Steam |
| Genre | First-person puzzle platformer |
| Perspective | First-person 3D |
| Input | Keyboard/mouse or controller |
| Session Length | 6-10 hours in the original; compact clone may target 1-3 hours |
| Primary Objective | Solve test chambers by placing linked portals and manipulating physics devices |
| Lose Condition | Player dies from hazards, crushing, toxic goo, or falling into void; respawn at chamber checkpoint |
| Win Condition | Reach chamber elevator or final story escape endpoint |
| Online Requirement | None for single-player campaign |

## 2. AI-Generation Scope

Minimum viable clone:

- First-person movement with jump, crouch optional, interact, and two-portal gun.
- 12-20 test chambers using portals, cubes, buttons, doors, emancipation grids, lasers, light bridges, funnels, and gel surfaces.
- Checkpoint respawn and chamber select.

High-fidelity target:

- Story intercom, dynamic set pieces, aerial faith plates, excursion funnels, hard light bridges, thermal discouragement beams, gels, turrets, and final multi-stage escape.

## 3. Technical Foundation

| System | Requirement |
|--------|-------------|
| Rendering | 3D first-person rooms with clean readable materials |
| Physics | Rigid bodies for cubes, momentum conservation through portals |
| Portal Surface | Only marked white/portalable surfaces accept portals |
| Save | Chamber progress and checkpoints |
| Camera | First-person with no third-person view |
| Accessibility | Reticle, colorblind-safe portal colors, subtitle support |

Core update loop:

```text
1. Process player movement, look, jump, fire blue portal, fire orange portal, use object
2. Update physics bodies, buttons, doors, platforms, funnels, lasers, gels, and turrets
3. Resolve portal placement raycasts and portal validity
4. Teleport player or objects crossing portal plane with transformed position, rotation, and velocity
5. Update puzzle logic graph and door states
6. Check hazards, checkpoints, chamber exit, and death volumes
7. Render recursive portal views or simplified portal masks
```

## 4. Portal Mechanics

Portal placement:

- Player fires blue or orange portal.
- Raycast must hit portalable surface.
- Surface must have enough flat area for portal bounds.
- New portal replaces previous portal of same color.
- If both portals exist, they form a bidirectional link.

Teleport rules:

- Crossing portal plane transfers entity to paired portal.
- Preserve speed magnitude and transform velocity into destination portal orientation.
- Player view rotates smoothly to destination orientation.
- Prevent immediate re-entry loops with a short portal cooldown or side test.

Momentum rule:

- Falling into one portal launches player out of the other with corresponding speed.
- This is central to fling puzzles.

## 5. Player And Object Interaction

Player actions:

| Action | Behavior |
|--------|----------|
| Move | Standard first-person walking |
| Jump | Short jump for ledges and cube climbing |
| Fire Portal A | Place blue portal |
| Fire Portal B | Place orange portal |
| Use | Pick up, drop, or press object |
| Hold Cube | Cube floats in front of player with collision constraints |

Carry rules:

- Player can carry one cube or sphere.
- Carried objects cannot pass through emancipation grids.
- Dropping object preserves modest forward velocity.

## 6. Puzzle Devices

| Device | Behavior |
|--------|----------|
| Weighted Button | Activated while cube/player is on top |
| Pedestal Button | Timed activation after press |
| Door | Opens when logic condition is true |
| Cube Dropper | Spawns a cube when triggered; may destroy previous cube |
| Emancipation Grid | Clears portals and destroys carried/loose cubes crossing it |
| Thermal Beam | Straight laser; can be redirected through portals or cubes |
| Laser Receiver | Activates when beam hits it |
| Hard Light Bridge | Solid bridge projected from emitter; can pass through portals |
| Excursion Funnel | Tractor beam moves player/objects; direction can reverse |
| Aerial Faith Plate | Launches player/object along fixed arc |
| Turret | Detects player in cone and fires until tipped or blocked |
| Toxic Goo | Death volume |

## 7. Gel System

Gels modify surfaces:

| Gel | Effect |
|-----|--------|
| Repulsion Gel | Player bounces high after contact |
| Propulsion Gel | Player accelerates while running on surface |
| Conversion Gel | Makes non-portalable surface portalable |
| Cleansing Water | Removes gel from surfaces or objects |

Gel can be transported through portals. Use decals or surface state maps to remember painted areas.

## 8. Chamber Design Rules

Chamber fields:

```text
id, title, entry_elevator, exit_elevator, surfaces, devices,
logic_graph, checkpoints, hazards, intended_solution_steps
```

Design principles:

- Introduce one new device at a time.
- Make portalable surfaces visually distinct.
- Exit door should be visible early when possible.
- Avoid requiring extremely precise physics unless taught.
- Include observation windows and signage-style cues.

## 9. Puzzle Logic Graph

Represent device dependencies as logic nodes:

```text
button_a AND laser_receiver_b -> exit_door_open
pedestal_button_c -> cube_dropper_spawn for 5 seconds
funnel_reverse_button -> funnel_direction = reverse
```

Logic should be debuggable in editor. Each chamber should expose:

- Required conditions.
- Optional reset triggers.
- Timed state duration.
- Door/device animation state.

## 10. Hazards And Respawn

Hazards:

- Turret bullets.
- Goo.
- Crushing panels.
- Falling out of chamber.
- Laser overexposure if using damage variant.

Respawn:

- Return to last checkpoint at chamber start or midpoint.
- Reset movable objects to puzzle-defined state.
- Preserve solved state only if checkpoint says so.
- Clear portals unless chamber specifically keeps them.

## 11. UI Layout

- Center reticle shows portal placement validity.
- Two portal indicators show whether blue/orange portals are active.
- Minimal HUD; no health bar needed if damage is binary or fast regen.
- Subtitles and intercom text appear at bottom.
- Pause menu includes restart chamber and options.

## 12. Visual And Audio Direction

- Portalable panels should be bright and flat; non-portalable walls darker or metallic.
- Blue and orange portal colors must be unambiguous.
- Portal ambience, gun fire, valid/invalid placement sounds, button clicks, cube dropper sounds, and emancipation fizzles are essential.
- Test chambers should be clean and readable rather than cluttered.

## 13. Validation Checklist

- A falling player preserves momentum through a portal.
- Cubes can activate buttons through portals.
- Emancipation grid clears portals and carried cubes.
- Laser can pass through portals and activate receivers.
- Chamber reset restores all puzzle objects.
- Every chamber has a documented intended solution and can be completed without glitches.

