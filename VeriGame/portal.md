# Portal (2D Mechanics Version) — Complete Game Specification

## 1. Game Overview

**Title:** Portal (2D Side-Scrolling Adaptation)
**Genre:** 2D physics-based puzzle platformer
**Platform:** Single-player, keyboard-controlled
**Reference:** Based on Valve's Portal (2007), adapted to 2D side-scrolling perspective
**Objective:** Navigate through test chambers by placing two connected portals on valid surfaces. Objects and the player character pass through one portal and emerge from the other, preserving momentum. Reach the exit of each chamber to progress.

---

## 2. Technical Foundation

### 2.1 Display

| Parameter            | Value                    |
|----------------------|--------------------------|
| Viewport             | 800 x 480 pixels         |
| Tile size            | 32 x 32 pixels           |
| Max level size       | 50 x 30 tiles (1600 x 960) |
| Camera               | Follows player, viewport scrolls |
| Frame rate           | 60 FPS                   |
| Physics tick rate     | 120 Hz (fixed timestep)  |

### 2.2 Coordinate System

- Origin (0, 0) at top-left of the level.
- X increases rightward, Y increases downward.
- Physics uses continuous coordinates (float), not grid-snapped.

### 2.3 Physics Constants

| Constant              | Value                    |
|-----------------------|--------------------------|
| Gravity               | 800 px/s^2 (downward)   |
| Player max walk speed | 200 px/s                 |
| Player jump velocity  | -350 px/s (upward)      |
| Player acceleration   | 1200 px/s^2             |
| Player friction       | 0.85 (ground)           |
| Air friction          | 0.95                    |
| Terminal velocity     | 600 px/s                |
| Portal transfer       | Momentum preserved (speed + direction relative to portal) |

---

## 3. Player Character (Chell)

### 3.1 Properties

| Property           | Value                   |
|--------------------|-------------------------|
| Width              | 20 px                   |
| Height             | 44 px (standing), 28 px (crouching) |
| Color              | White jumpsuit, orange highlights |
| Collision shape    | Axis-aligned bounding box (AABB) |
| Health             | 1 hit (no health bar; fall damage only from extreme heights or hazards) |

### 3.2 Movement

| Action          | Key            | Effect                               |
|-----------------|----------------|--------------------------------------|
| Move Left       | Left Arrow / A | Accelerate left at 1200 px/s^2       |
| Move Right      | Right Arrow / D| Accelerate right at 1200 px/s^2      |
| Jump            | Space / W / Up | Apply upward velocity of -350 px/s   |
| Crouch          | Down / S / Ctrl| Reduce height to 28px, slower movement |
| Shoot Blue Portal  | Left Click  | Fire blue portal projectile          |
| Shoot Orange Portal| Right Click | Fire orange portal projectile        |
| Pick Up Object  | E              | Pick up a nearby physics object      |
| Drop Object     | E (while holding)| Drop the held object              |
| Throw Object    | Left Click (while holding) | Throw object forward   |

### 3.3 Jump Mechanics

- Jump is only allowed when grounded (touching a floor surface).
- No double jump.
- Variable jump height: Release jump key early to reduce jump height (apply 0.5x upward velocity when key released while ascending).
- Coyote time: 80ms after leaving a ledge, the player can still jump.
- Jump buffer: 100ms before landing, if jump key is pressed, jump triggers on landing.

---

## 4. Portal Mechanics

### 4.1 Portal Properties

| Property           | Blue Portal       | Orange Portal     |
|--------------------|-------------------|--------------------|
| Color              | #0088FF           | #FF8800            |
| Glow               | Blue aura (10px)  | Orange aura (10px) |
| Size               | 64 px tall, 8 px wide (on walls) or 8 px tall, 64 px wide (on floors/ceilings) |
| Placement          | Only on portalable surfaces | Only on portalable surfaces |
| Max count          | 1 of each color   | 1 of each color    |

### 4.2 Portal Placement Rules

1. Portals can only be placed on white/light-colored walls, floors, and ceilings marked as "portalable."
2. Dark/metal surfaces are NOT portalable.
3. The portal must fit entirely on the surface (64px of continuous portalable surface required).
4. If a portal is placed on a surface that already has a portal of the same color, the old portal is removed.
5. Portals cannot overlap each other.
6. Portals persist until replaced or the level resets.

### 4.3 Portal Projectile

- Speed: 1500 px/s (instant feel).
- Collision: Stops at the first portalable or non-portalable surface.
- If it hits a portalable surface: Place portal.
- If it hits a non-portalable surface: Fizzle (small spark particle effect, 200ms).
- Projectile is a small glowing orb (8px diameter) with a trail.

### 4.4 Portal Traversal

When an object touches one portal:
1. The object begins entering the portal.
2. The object emerges from the linked portal.
3. **Momentum conservation:** Speed is preserved. Direction is remapped based on portal orientations.

Direction remapping rules:
```
Portal A orientation -> Portal B orientation -> Velocity transform

Wall-left  -> Wall-right:  (vx, vy) -> (-vx, vy)     [mirror horizontal]
Wall-left  -> Floor:       (vx, vy) -> (vy, -vx)      [rotate 90 CCW]
Wall-left  -> Ceiling:     (vx, vy) -> (-vy, vx)      [rotate 90 CW]
Wall-right -> Wall-left:   (vx, vy) -> (-vx, vy)      [mirror horizontal]
Floor      -> Wall-left:   (vx, vy) -> (-vy, vx)      [rotate 90 CW]
Floor      -> Wall-right:  (vx, vy) -> (vy, -vx)      [rotate 90 CCW]
Floor      -> Ceiling:     (vx, vy) -> (vx, -vy)      [mirror vertical]
Ceiling    -> Floor:       (vx, vy) -> (vx, -vy)      [mirror vertical]
Same orientation:          (vx, vy) -> (vx, vy)        [no change, exit same dir]
```

General rule: The exit velocity is the entry velocity rotated by the angle difference between portal normals, pointing outward from the exit portal.

### 4.5 Flinging (Key Mechanic)

"Speedy thing goes in, speedy thing comes out."

If the player falls through a floor portal with high downward velocity, they emerge from a wall portal with equivalent horizontal velocity (or from a ceiling portal with upward velocity). This is the core "flinging" mechanic.

Example fling setup:
```
                    +---+
                    | E |  (exit platform)
                    +---+

   +------+
   | P    |         +-O-+  (orange portal on wall)
   | L    |         |   |
   | A    |         |   |
   | T    |         |   |
   +-B----+---------+---+
     (blue portal on floor)

Player walks off the high platform, falls through blue portal,
exits orange portal horizontally with the same speed, reaches exit.
```

### 4.6 Infinite Loop Prevention

If both portals face each other directly (e.g., both on the floor and ceiling of the same column), objects could theoretically loop infinitely. Handle by:
- Objects pass through a portal at most once per physics tick.
- After exiting a portal, the object is briefly "immune" to re-entering the same portal for 2 physics ticks (16.67ms).

---

## 5. Physics Objects

### 5.1 Weighted Companion Cube

| Property           | Value                    |
|--------------------|--------------------------|
| Size               | 28 x 28 pixels           |
| Mass               | 2.0 (relative to player = 1.0) |
| Color              | Gray (#888888) with pink heart (#FF69B4) |
| Bounciness         | 0.3                      |
| Friction           | 0.8                      |
| Portal-able        | Yes (can pass through portals) |
| Holdable           | Yes (player can pick up and carry) |

### 5.2 Weighted Storage Cube

- Same as Companion Cube but without the heart decoration.
- Appearance: Gray cube with Aperture Science logo.

### 5.3 Physics Object Interactions

- Objects can be placed on floor buttons to activate them.
- Objects can be thrown through portals.
- Objects are affected by gravity.
- Objects can block laser beams.
- Objects collide with other objects and the player.
- Held objects move with the player and can be thrown at 400 px/s.

---

## 6. Environmental Hazards

### 6.1 Hazard Types

| Hazard              | Effect                          | Visual                    |
|---------------------|---------------------------------|---------------------------|
| Acid/Goo            | Instant death on contact        | Green bubbling liquid     |
| Turret              | Shoots bullets in a cone        | White tripod with red eye |
| Laser beam          | Continuous damage (instant death)| Red beam across the level |
| Crusher             | Moving wall that squishes player | Large piston              |
| Fizzler (Emancipation Grid) | Destroys portals and objects | Blue translucent grid |
| Moving platform     | Carries player (not a hazard)   | Metal platform on track   |

### 6.2 Turret Behavior

| Property           | Value                    |
|--------------------|--------------------------|
| Detection range    | 300 pixels               |
| Detection angle    | 45 degrees (cone)        |
| Fire rate          | 3 shots/second           |
| Bullet speed       | 500 px/s                 |
| Bullet damage      | Instant death             |
| Can be tipped over | Yes (by objects or portals)|
| Tipped state       | Deactivated, harmless    |

```python
class Turret:
    def update(self, player_pos):
        if self.tipped:
            return
        direction = player_pos - self.position
        if direction.magnitude() < 300:
            angle = direction.angle()
            if abs(angle - self.facing) < 22.5:  # within 45-degree cone
                if has_line_of_sight(self.position, player_pos):
                    self.shoot()
```

### 6.3 Laser Beam

- Continuous red beam from an emitter to the wall/object it hits.
- Can be redirected using Redirection Cubes (special cube with prism).
- Can be interrupted by placing objects in the beam path.
- Laser + Receiver: Directing a laser into a receiver activates a mechanism (door, platform).

---

## 7. Level Elements

### 7.1 Interactive Elements

| Element              | Interaction              | Effect                         |
|----------------------|--------------------------|--------------------------------|
| Floor Button         | Object placed on it      | Activates linked mechanism     |
| Floor Button (player)| Player stands on it      | Activates while standing       |
| Door                 | Linked to button/laser   | Opens when activated           |
| Moving Platform      | Linked to button         | Moves along track when active  |
| Light Bridge         | Linked to button         | Hard light surface appears     |
| Funnel (Excursion)   | Always active or linked  | Beam that carries objects/player |
| Gel Dispenser (Blue) | Always active            | Drops repulsion gel            |
| Gel Dispenser (Orange)| Always active           | Drops propulsion gel           |

### 7.2 Gel Types (Simplified)

| Gel Type       | Color    | Effect                                    |
|----------------|----------|-------------------------------------------|
| Repulsion Gel  | #4488FF  | Surfaces coated bounce objects (bounciness = 1.0) |
| Propulsion Gel | #FF8800  | Surfaces coated increase speed (2x acceleration) |
| Conversion Gel | #FFFFFF  | Surfaces coated become portalable         |

### 7.3 Surface Types

| Surface            | Portalable? | Visual              |
|--------------------|-------------|----------------------|
| White panel        | Yes         | Clean white (#F0F0F0)|
| Dark panel         | No          | Dark gray (#404040)  |
| Metal panel        | No          | Metallic (#707080)   |
| Glass              | No          | Transparent blue tint|
| Goo surface        | No          | Green bubbling       |
| Gel-coated (conv.) | Yes         | White splatter       |

---

## 8. Camera System

### 8.1 Camera Following

- Camera centers on the player character.
- Smooth following with lerp factor of 0.1 (10% of distance per frame).
- Camera is clamped to level boundaries (no seeing outside the level).
- Look-ahead: Camera offsets slightly in the direction the player is moving (30px ahead).

### 8.2 Portal Camera

When close to a portal, the camera may show a "view through" the portal:
- Render a small window within the portal showing the destination area.
- This is a miniature viewport (64px wide) rendered inside the portal frame.
- Updates in real-time.

---

## 9. Level Structure

### 9.1 Test Chamber List

| Chamber | Name                 | Key Mechanic              | Difficulty |
|---------|----------------------|---------------------------|------------|
| 00      | Orientation          | Basic movement, no portals| Tutorial   |
| 01      | Portal Introduction  | Pre-placed portals only   | Easy       |
| 02      | Blue Portal          | Player gets blue portal   | Easy       |
| 03      | Both Portals         | Player gets both portals  | Easy       |
| 04      | Momentum             | Basic flinging            | Easy       |
| 05      | Double Fling         | Two-fling chain           | Medium     |
| 06      | Cube and Button      | Cube + button + portal    | Medium     |
| 07      | Turret Introduction  | Avoid/tip turrets         | Medium     |
| 08      | Laser Redirection    | Redirect lasers to receivers | Medium  |
| 09      | Acid Crossing        | Portal over acid pits     | Medium     |
| 10      | Multiple Buttons     | Multiple cubes + buttons  | Medium     |
| 11      | Fizzler Challenge    | Navigate around fizzlers  | Hard       |
| 12      | Gel Mechanics        | Repulsion + Propulsion gel| Hard       |
| 13      | Complex Fling        | Multi-step momentum puzzle| Hard       |
| 14      | Turret Gauntlet      | Multiple turrets, timing  | Hard       |
| 15      | Laser Maze           | Complex laser routing     | Hard       |
| 16      | The Pit              | Deep vertical chamber     | Hard       |
| 17      | Conversion           | Conversion gel + portals  | Expert     |
| 18      | Everything           | All mechanics combined    | Expert     |
| 19      | Escape               | Final chamber, narrative  | Expert     |

### 9.2 Level Data Format

```json
{
  "chamber_id": 5,
  "name": "Double Fling",
  "width": 40,
  "height": 25,
  "spawn": {"x": 64, "y": 700},
  "exit": {"x": 1200, "y": 100},
  "tiles": [
    {"type": "white_panel", "x": 0, "y": 24, "w": 10, "h": 1},
    {"type": "dark_panel", "x": 10, "y": 24, "w": 5, "h": 1},
    ...
  ],
  "objects": [
    {"type": "cube", "x": 300, "y": 700},
    {"type": "button", "x": 500, "y": 780, "linked_to": "door_1"},
    {"type": "door", "id": "door_1", "x": 800, "y": 500, "w": 1, "h": 3}
  ],
  "hazards": [
    {"type": "acid", "x": 400, "y": 790, "w": 10, "h": 1},
    {"type": "turret", "x": 900, "y": 400, "facing": "left"}
  ]
}
```

---

## 10. Animations

| Animation               | Duration | Description                         |
|-------------------------|----------|-------------------------------------|
| Player walk cycle       | 400 ms   | 6-frame loop                        |
| Player jump             | 300 ms   | Ascend + apex + descend             |
| Player crouch           | 100 ms   | Shrink to crouch height             |
| Player death            | 500 ms   | Ragdoll + fade out                  |
| Portal open             | 300 ms   | Expanding oval                      |
| Portal idle             | Loop     | Swirling particle effect            |
| Portal close            | 200 ms   | Shrinking oval                      |
| Portal traversal        | 100 ms   | Player stretches into portal        |
| Cube pickup             | 150 ms   | Cube levitates to held position     |
| Cube throw              | N/A      | Follows physics                     |
| Turret activate         | 200 ms   | Eye lights up red                   |
| Turret fire             | 50 ms    | Muzzle flash                        |
| Turret tip over         | 500 ms   | Falls to side with physics          |
| Door open               | 400 ms   | Slides up                           |
| Door close              | 400 ms   | Slides down                         |
| Button press            | 100 ms   | Depresses 4px                       |
| Fizzler                 | Loop     | Vertical blue particles             |
| Laser beam              | Loop     | Pulsing red line with particles     |
| Gel splatter            | 300 ms   | Splash + spread on surface          |
| Level complete          | 1500 ms  | Checkmark + particle burst          |

---

## 11. Audio Design

### 11.1 Sound Effects

| Event                    | Description                          | Duration |
|--------------------------|--------------------------------------|----------|
| Footstep (concrete)      | Hard tap                             | 80 ms    |
| Footstep (metal)         | Metallic clang                       | 80 ms    |
| Jump                     | Whoosh up                            | 200 ms   |
| Land                     | Impact thud                          | 100 ms   |
| Portal shoot             | Energy whoosh                        | 300 ms   |
| Portal open              | Dimensional tear                     | 400 ms   |
| Portal enter/exit        | Warp woosh                           | 200 ms   |
| Portal fizzle (bad shot) | Electric fizzle                      | 200 ms   |
| Cube pickup              | Magnetic hum                         | 200 ms   |
| Cube drop                | Thud                                 | 100 ms   |
| Cube throw               | Whoosh                               | 150 ms   |
| Button activate          | Click + hum                          | 200 ms   |
| Button deactivate        | Lower click + silence                | 200 ms   |
| Door open                | Mechanical sliding                   | 400 ms   |
| Door close               | Mechanical sliding (reverse)         | 400 ms   |
| Turret spot player       | "Target acquired" (voice, optional)  | 500 ms   |
| Turret fire              | Rapid gunshot                        | 100 ms   |
| Turret tipped            | "I don't blame you" (voice, opt.)    | 1000 ms  |
| Fizzler pass through     | Electric buzz                        | 300 ms   |
| Laser beam (continuous)  | Low hum                              | Loop     |
| Acid bubbling            | Bubbling/sizzling                    | Loop     |
| Gel splat                | Wet splat                            | 200 ms   |
| Gel bounce               | Boing                                | 150 ms   |
| Player death             | Impact + system error                | 500 ms   |
| Level complete           | Success jingle                       | 1000 ms  |

### 11.2 Music

- Ambient, industrial electronic soundtrack.
- Layers add as puzzle complexity increases.
- Style: Clean, sterile, scientific atmosphere (like the original Portal).
- GLaDOS voice lines (optional): Brief comments between chambers.

---

## 12. UI Layout

```
+------------------------------------------------------+
|  Chamber 05: Double Fling           [Portals: 2/2]   |
|                                                      |
|  +-------------------------------------------------+ |
|  |                                                 | |
|  |         GAME VIEWPORT                           | |
|  |                                                 | |
|  |    [Player character with portal gun]           | |
|  |                                                 | |
|  |    [Blue portal on floor]                       | |
|  |    [Orange portal on wall]                      | |
|  |                                                 | |
|  +-------------------------------------------------+ |
|                                                      |
|  [B] Blue Portal    [O] Orange Portal    [R] Reset   |
+------------------------------------------------------+
```

### 12.1 Crosshair

- Simple crosshair at the mouse position.
- Inner circle: 4px, white outline.
- Color hint: Left half blue, right half orange (indicating which portal fires with which button).

### 12.2 Portal Indicator

- Top-right: Two small portal icons showing portal status.
- Filled circle = portal placed. Empty circle = not placed.
- Blue and orange colored.

---

## 13. State Machine

```
[MAIN_MENU]
    --> [CHAMBER_SELECT] or [CONTINUE]
        --> [LEVEL_LOADING]
            --> [GAMEPLAY]

[GAMEPLAY]
    --> [PLAYING]
        --> [PLAYER_DEATH]
            --> Respawn at checkpoint or level start (after 1 second)
            --> [PLAYING]
        --> [LEVEL_COMPLETE]
            --> [TRANSITION]
                --> [NEXT_LEVEL_LOADING]
    --> [PAUSED]
        --> [PLAYING] (resume)
        --> [CHAMBER_SELECT]
        --> [MAIN_MENU]
```

---

## 14. Edge Cases

1. **Portal on moving platform:** If a portal is on a surface that moves, the portal moves with it. Objects entering the portal emerge from the other portal with velocity adjusted for the platform's movement.
2. **Player standing on portal:** If a floor portal opens under the player, the player falls through it next physics tick.
3. **Cube stuck in wall:** If a cube exits a portal into a position where it overlaps a wall, push the cube to the nearest valid position.
4. **Portal closed while player is traversing:** Player is ejected from the last valid portal position.
5. **Fizzler removes portals:** Both portals disappear. Any object passing through fizzler is destroyed.
6. **Laser through portal:** Lasers CAN pass through portals. The laser enters one portal and exits the other with appropriate direction change.
7. **Gel through portal:** Gel can be directed through portals to coat surfaces on the other side.

---

## 15. Performance Requirements

| Metric               | Target           |
|-----------------------|------------------|
| Input latency         | < 16ms           |
| Physics tick          | < 8ms (120Hz)    |
| Render frame          | < 16.67ms (60Hz) |
| Portal rendering      | < 4ms            |
| Memory usage          | < 50 MB          |
| Level load time       | < 1 second       |

---

## 16. Testing Checklist

1. Player moves, jumps, and crouches correctly.
2. Portal projectile travels in correct direction at correct speed.
3. Portals can only be placed on portalable surfaces.
4. Portal placement rejects surfaces too small for the portal.
5. Objects pass through portals with correct momentum transformation.
6. Flinging works: Vertical momentum converts to horizontal through portals.
7. Double fling works: Chained portal traversals.
8. Cubes can be picked up, carried, thrown, and placed on buttons.
9. Buttons activate linked mechanisms correctly.
10. Doors open and close based on button state.
11. Turrets detect and fire at the player.
12. Turrets can be tipped over by cubes/portal tricks.
13. Lasers are blocked by cubes.
14. Lasers pass through portals with correct direction.
15. Fizzlers destroy portals and cubes.
16. Acid/goo kills the player on contact.
17. Gel mechanics work (bounce, speed, conversion).
18. Camera follows player smoothly.
19. Level transitions work correctly.
20. All 20 chambers are completable.
