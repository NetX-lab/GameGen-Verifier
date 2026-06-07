# 11_asteroids - Asteroids (1979 Atari Arcade Faithful Recreation)

## 1. Game Overview

- **Reference**: Asteroids, designed by Lyle Rains and Ed Logg, published by Atari Inc. (November 1979). This specification targets the original upright arcade cabinet (Rev 2/Rev 4 ROM), not Asteroids Deluxe or later home console ports.
- **Genre**: Multi-directional Shooter / Action
- **Core Fantasy**: Pilot a lone triangular spaceship adrift in an asteroid field, rotating and thrusting with Newtonian inertia to destroy drifting rocks and hostile flying saucers while surviving as long as possible for the highest score.
- **Presentation**: 2D top-down monochrome vector graphics on a black background. All objects are drawn as connected line segments on a simulated vector display. The playfield wraps toroidally -- objects leaving one edge reappear at the opposite edge.
- **Target Session**: 2-5 minutes for novice players; 30+ minutes for experts.
- **Skill Curve**: Immediately intuitive (rotate, thrust, shoot), with deep mastery through inertia management, saucer hunting, hyperspace risk assessment, and "lurking" strategies.

---

## 2. Technical Foundation

| Parameter | Value |
|---|---|
| Original hardware CPU | MOS Technology 6502 @ 1.512 MHz |
| Graphics processor | Digital Vector Generator (DVG / QuadraScan) |
| Display type | Monochrome vector CRT (XY deflection) |
| Logical coordinate space | 1024 x 768 units |
| Aspect ratio | 4:3 (horizontal) |
| Simulation tick rate | 60 Hz fixed (`dt = 1/60 s ~ 16.67 ms`) |
| Coordinate origin | (0, 0) at top-left; +X right, +Y down |
| Wrapping | Toroidal: objects wrap seamlessly across all four edges |
| Maximum on-screen objects | 35 total (27 asteroids, 1 saucer, 2 saucer bullets, 1 ship, 4 player bullets) |
| Score storage | 2 BCD bytes with implicit trailing zero; rolls over at 99,990 points |
| RNG | Hardware-seeded pseudo-random via 6502 timing |
| Rendering | All objects drawn as connected line segments (vector strokes); no filled polygons |
| Color | Monochrome white lines on black background |

---

## 3. Win / Lose Contract

| Condition | Description |
|---|---|
| **Win** | No win state; the game is an endurance/score challenge that continues indefinitely until all lives are lost |
| **Lose** | Player loses final ship (collision with asteroid, saucer, or saucer bullet; or fatal hyperspace jump). Game over screen displays; if score qualifies, player enters 3-character initials for the high score table |
| **Score rollover** | Score display rolls over at 99,990 points but gameplay continues internally |

---

## 4. Core Mechanics -- Ship Controls

### 4.1 Control Panel (5 Buttons)

| Button | Action |
|---|---|
| **Rotate Left** | Rotates ship counter-clockwise in discrete angular steps while held |
| **Rotate Right** | Rotates ship clockwise in discrete angular steps while held |
| **Thrust** | Applies forward acceleration in the direction the ship nose is pointing; engine flicker line appears at ship rear |
| **Fire** | Launches a bullet from the ship's nose in the direction the ship is facing |
| **Hyperspace** | Instantly teleports the ship to a random screen location (with risk of destruction) |

### 4.2 Ship Rotation

| Parameter | Value |
|---|---|
| Rotation step | 5 degrees per frame |
| Rotation rate (held) | 5 degrees per frame = 300 degrees/second at 60 Hz |
| Rotation positions | 72 discrete orientations (360 / 5) |
| Rotation behavior | Instantaneous per frame while button is held; no angular momentum or inertia on rotation |

### 4.3 Ship Thrust and Movement

| Parameter | Value |
|---|---|
| Thrust acceleration | Applied as a velocity delta each frame the thrust button is held, in the direction the ship's nose is pointing |
| Maximum ship speed | ~17 ship-lengths per second (approximately 680 coordinate units/second at 60 Hz) |
| Inertia | Full Newtonian: the ship retains its velocity vector when thrust is released; velocity components persist independently |
| Drag / friction | Slight drag applied each frame; ship gradually decelerates to rest when not thrusting (not instant -- takes several seconds) |
| Movement model | Velocity is a 2D vector (vx, vy); thrust adds acceleration along the ship's heading; drag reduces magnitude each frame |
| Speed clamping | Velocity components are clamped to prevent exceeding maximum speed |

### 4.4 Ship Visual

| Element | Description |
|---|---|
| Shape | Narrow isosceles triangle (arrow/chevron), open at the rear |
| Size | Approximately 28 x 18 coordinate units (the reference "ship length" for relative measurements) |
| Thrust indicator | When thrusting, a flickering short line extends from the rear of the ship (engine exhaust) |
| Vertices | 5 points forming the outline: nose tip, two forward wing points, two rear indent points |

---

## 5. Physics System

### 5.1 Newtonian Motion

All moving objects (ship, asteroids, saucers, bullets) follow simple Newtonian physics:

```
position.x += velocity.x * dt
position.y += velocity.y * dt
```

- **Ship**: velocity modified by thrust acceleration and drag
- **Asteroids**: constant velocity (no acceleration or drag)
- **Saucers**: constant velocity with periodic direction changes
- **Bullets**: constant velocity (no drag); inherit ship velocity at moment of firing plus bullet speed in ship's facing direction

### 5.2 Screen Wrapping

| Rule | Description |
|---|---|
| Horizontal wrap | When `position.x > 1023`, set `position.x = 0`; when `position.x < 0`, set `position.x = 1023` |
| Vertical wrap | When `position.y > 767`, set `position.y = 0`; when `position.y < 0`, set `position.y = 767` |
| Applies to | Ship, all asteroids, all saucers, all bullets (player and saucer) |
| Visual continuity | Objects partially off one edge appear simultaneously on the opposite edge; no "pop" -- the object is drawn at both positions during transition |
| Bullet wrapping | Player bullets and saucer bullets wrap around screen edges, enabling cross-screen shots |

### 5.3 Collision Detection

| Method | Description |
|---|---|
| Primary check | Bounding circle overlap test for fast rejection |
| Precise check | Point-in-polygon (crossing number / ray casting algorithm) for ship-asteroid and bullet-asteroid collisions |
| Ship collision | Any vertex of the ship polygon inside an asteroid polygon, or any asteroid vertex inside the ship polygon, triggers destruction |
| Bullet collision | Bullet point tested against asteroid polygon |
| Saucer collision | Bounding box or bounding circle overlap; saucer treated as a rectangular hitbox |
| Wrap-aware | Collision checks account for screen wrapping (objects near edges are tested against both positions) |

---

## 6. Asteroid System

### 6.1 Asteroid Sizes

| Size | Diameter (coord units) | Relative to Ship Length | Points |
|---|---|---|---|
| Large | ~68 units (~2.4 ship lengths) | 2.4x | 20 |
| Medium | ~34 units (~1.2 ship lengths) | 1.2x | 50 |
| Small | ~17 units (~0.6 ship lengths) | 0.6x | 100 |

### 6.2 Asteroid Visual Shapes

| Parameter | Value |
|---|---|
| Shape type | Irregular convex polygons drawn as connected line segments |
| Shape variants | 4 distinct shape templates per size category (randomly selected at spawn) |
| Vertices per asteroid | 8-12 vertices, irregularly placed around a rough circle |
| Rotation | Asteroids rotate visually at a slow constant rate (cosmetic only; hitbox rotates with the shape) |
| Color | Monochrome white outlines, same brightness as all other objects |

### 6.3 Asteroid Splitting Behavior

| Event | Result |
|---|---|
| Large asteroid destroyed | Splits into **2 medium** asteroids |
| Medium asteroid destroyed | Splits into **2 small** asteroids |
| Small asteroid destroyed | Destroyed completely (no fragments) |
| Fragment velocity | Fragments inherit a component of the parent asteroid's momentum and gain random velocity offsets; smaller fragments tend to move faster |
| Fragment direction | Semi-random; fragments generally scatter in different directions from the parent, with some momentum conservation |

### 6.4 Object Limit Rule

| Parameter | Value |
|---|---|
| Maximum asteroids on screen | 27 |
| Behavior when at limit | If 27 asteroids already exist: destroying a large asteroid produces only **1** medium (not 2); destroying a medium produces only **1** small (not 2) |
| Purpose | Hardware constraint to maintain performance and object rendering budget |

### 6.5 Asteroid Speed

| Parameter | Value |
|---|---|
| Speed range (all sizes) | 4.0 - 6.5 ship-lengths per second (~112 - 182 coord units/second) |
| Small asteroid speed bonus | Small asteroids can travel up to 63% faster than large asteroids |
| Speed assignment | Random within range at spawn; fragments receive random speed within range |
| Acceleration | None; asteroids travel at constant velocity |
| Direction | Random angle at wave start; fragments get semi-random directions |

### 6.6 Asteroid Spawn (Wave Start)

| Parameter | Value |
|---|---|
| Spawn location | Edges of the screen (never near the center where the ship spawns) |
| Direction | Random, directed generally inward toward the playfield |
| Speed | Random within the speed range for large asteroids |
| Safe zone | Asteroids spawn with a minimum distance from the player ship's spawn point at center screen |

---

## 7. UFO / Saucer System

### 7.1 Saucer Types

| Property | Large Saucer | Small Saucer |
|---|---|---|
| Internal name | "Sluggo" | "Mr. Bill" |
| Size (relative to ship) | 1.5 ship lengths (~42 coord units) | 0.75 ship lengths (~21 coord units) |
| Points | 200 | 1,000 |
| Shape | Classic flying saucer silhouette (dome on top, flat bottom, wider middle) | Same shape, half the size |
| AI behavior | Fires in **random** directions | **Aims at the player** ship |
| Appearance | Enters from left or right screen edge, travels horizontally with vertical deviations | Same entry pattern |
| Speed | 4.0 - 6.5 ship-lengths per second (varies by score) | Same range, tends toward faster end |

### 7.2 Saucer Spawn Timing

| Parameter | Value |
|---|---|
| Initial saucer timer | ~146 frames (~2.4 seconds) after wave start |
| Timer decrement | After each saucer appearance, the timer for the next saucer decreases by ~6 frames |
| Minimum saucer interval | 32 frames (~0.53 seconds) |
| Spawn trigger | Timer also triggers when few asteroids remain (to prevent indefinite stalling / "lurking") |
| Maximum saucers on screen | 1 at a time |

### 7.3 Saucer Type Selection by Score

| Score Range | Saucer Type |
|---|---|
| 0 - 10,000 | Large saucer only |
| 10,000 - 40,000 | Mix of large and small saucers (probability shifts toward small as score increases) |
| 40,000+ | Small saucer only |

### 7.4 Saucer AI and Shooting

| Parameter | Large Saucer | Small Saucer |
|---|---|---|
| Firing interval | Every ~10 frames (~0.17 seconds) | Every ~10 frames (~0.17 seconds) |
| Aim method | Random angle | Aimed at the player ship within a "window" of a few degrees on each side of the direct line to the player |
| Aim accuracy by score | No change (always random) | Accuracy increases as score rises; aim window narrows significantly above 35,000 points |
| Maximum saucer bullets on screen | 2 | 2 |
| Bullet speed | Same as player bullet speed (~17 ship-lengths/second) | Same as player bullet speed |
| Bullet wrapping | Yes -- saucer bullets wrap around screen edges | Yes -- in Rev 4, small saucer fires across screen borders deliberately |
| Movement pattern | Horizontal traversal with random vertical direction changes at intervals | Same pattern, slightly more erratic |
| Screen traversal | Enters from one side, exits the other; if not destroyed, despawns upon exit | Same |

### 7.5 Saucer Behavior by ROM Revision

| Revision | Small Saucer Behavior |
|---|---|
| Rev 1 | Shoots late after spawning; only fires toward the player within screen bounds; enables "lurking" exploit at screen edges |
| Rev 2 | Shoots sooner after spawning; same directional limitations as Rev 1 |
| Rev 4 (most common) | Fires both inside the screen and across screen borders; much more lethal; "lurking" exploit largely eliminated |

---

## 8. Bullet System

### 8.1 Player Bullets

| Parameter | Value |
|---|---|
| Maximum on screen | 4 simultaneously |
| Bullet speed (ship at rest) | ~17 ship-lengths per second (~476 coord units/second) -- same as ship maximum speed |
| Velocity composition | Bullet velocity = ship's current velocity + bullet speed in ship's facing direction |
| Bullet lifetime | ~18 frames (~0.3 seconds); slightly shorter than the time needed to cross the full screen |
| Wrapping | Yes; bullets wrap around all screen edges |
| Size | Single bright point (1-2 coordinate units) |
| Fire rate | As fast as the player can press the fire button, limited only by the 4-bullet cap |
| Stationary bullet trick | If the ship is moving and fires in the opposite direction, the bullet's net velocity can be near zero, creating a "mine" effect |

### 8.2 Saucer Bullets

| Parameter | Value |
|---|---|
| Maximum on screen | 2 simultaneously |
| Speed | Same as player bullet speed |
| Lifetime | Same as player bullet lifetime (~18 frames) |
| Wrapping | Yes |
| Collision | Can destroy the player ship; cannot destroy asteroids |

---

## 9. Scoring System

### 9.1 Point Values

| Target | Points |
|---|---|
| Large asteroid | 20 |
| Medium asteroid | 50 |
| Small asteroid | 100 |
| Large saucer (UFO) | 200 |
| Small saucer (UFO) | 1,000 |

Note: The small saucer point value in the ROM disassembly reads as 990 due to BCD encoding, but the canonical documented value is 1,000 points.

### 9.2 Extra Life

| Parameter | Value |
|---|---|
| Extra life threshold | Every 10,000 points (default DIP switch setting) |
| Behavior | Cumulative; player earns a bonus ship at 10,000, 20,000, 30,000, etc. |
| Audio cue | Distinctive ascending tone plays when extra life is awarded |

### 9.3 Score Display

| Parameter | Value |
|---|---|
| Display format | 5-digit score with trailing zero (00000-99990), displayed at top-left |
| Rollover | Score display rolls over at 99,990 back to 00000; internal counter continues |
| Player indicator | Current player number shown; remaining ships shown as small ship icons |

---

## 10. Level Progression

### 10.1 Wave Structure

| Wave | Starting Large Asteroids |
|---|---|
| 1 | 4 |
| 2 | 6 |
| 3 | 8 |
| 4 | 10 |
| 5+ | 11 (maximum; all subsequent waves start with 11) |

### 10.2 Wave Completion

| Parameter | Value |
|---|---|
| Completion condition | All asteroids and the current saucer (if any) are destroyed |
| New wave delay | Brief pause (~48 frames / ~0.8 seconds) after clearing all objects before new asteroids spawn |
| New wave spawn | New large asteroids appear at screen edges, outside the center safe zone |
| Difficulty scaling | Number of starting asteroids increases per wave (see table above); saucer frequency and accuracy scale with score (see Section 7) |

### 10.3 Difficulty Curve

| Score Milestone | Effect |
|---|---|
| 0 - 10,000 | Only large saucers appear; asteroids at base difficulty |
| 10,000+ | Small saucers begin appearing alongside large saucers |
| 35,000+ | Small saucer aim window narrows significantly (near-perfect accuracy) |
| 40,000+ | Only small saucers appear (no more large saucers) |
| Saucer timer | Decreases progressively, making saucers appear more frequently as the game progresses |

---

## 11. Hyperspace Mechanic

### 11.1 Activation

| Parameter | Value |
|---|---|
| Trigger | Press the Hyperspace button |
| Immediate effect | Ship instantly vanishes from current position |
| Reappearance | Ship materializes at a random screen location after a brief delay |
| Reappearance orientation | Random facing direction |
| Reappearance velocity | Ship retains its pre-jump velocity |

### 11.2 Risk of Destruction

| Parameter | Value |
|---|---|
| Failure probability | Approximately 1 in 4 to 1 in 5 chance (~20-25%) of the ship exploding upon rematerialization |
| Mechanism (from ROM) | A random number from 0-31 is generated; if the value is 24-31 (the top 25%), the jump is fatal |
| Asteroid-dependent modifier | If the random value (after processing) is less than the number of asteroids currently on screen, the jump succeeds; with 19+ asteroids on screen, hyperspace never randomly fails |
| Additional risk | Even on a "successful" random roll, the ship may materialize on top of an asteroid or saucer bullet, resulting in immediate death from collision |
| Strategy implication | Hyperspace is a desperate last resort, not a routine tactical maneuver |

---

## 12. Lives and Ship Spawn System

### 12.1 Starting Lives

| Parameter | Value (Default) |
|---|---|
| Starting ships | 3 (DIP switch configurable: 3 or 4) |
| Ship display | Remaining ships shown as small ship icons at top-left of screen, below the score |
| Maximum displayable lives | Limited by screen width of the life indicator area |

### 12.2 Ship Spawn / Respawn

| Parameter | Value |
|---|---|
| Initial spawn position | Center of screen (512, 384 in coordinate space) |
| Respawn position | Center of screen |
| Respawn delay | ~48 frames (~0.8 seconds) after ship destruction |
| Spawn safety check | Ship does not respawn if asteroids or saucers are too close to the center; the game waits until the center area is clear |
| Respawn orientation | Facing upward (0 degrees / 12 o'clock) |
| Respawn velocity | Stationary (0, 0) |
| Invincibility | Brief invincibility period upon respawn (~1-2 seconds); ship may flash/blink during this window |

### 12.3 Ship Destruction

| Parameter | Value |
|---|---|
| Death animation | Ship breaks into several line segments that fly outward (explosion effect), lasting ~160 frames (~2.67 seconds) |
| Death causes | Collision with any asteroid, collision with saucer, hit by saucer bullet, fatal hyperspace jump |
| On death | Decrement remaining lives; if lives > 0, respawn after delay; if lives == 0, game over |

---

## 13. DIP Switch Configuration

| Switch | Options | Default |
|---|---|---|
| Language | English, German, French, Spanish | English |
| Ships per game | 3 or 4 | 3 |
| Coin play | Various coinage settings (1 coin/1 play, 1 coin/2 plays, 2 coins/1 play, free play) | 1 coin / 1 play |
| Center coin multiplier | x1, x2 | x1 |
| Right coin multiplier | x1, x4, x5, x6 | x1 |
| Bonus ship | Every 10,000 points | 10,000 |

---

## 14. Game States

### 14.1 State Machine

```
Power-On -> Self-Test -> Attract Mode -> Coin Insert -> Game Active -> Game Over -> High Score Entry -> Attract Mode
                                              ^                             |
                                              +-----------------------------+
                                                    (coin insert)
```

| State | Description |
|---|---|
| **Self-Test** | Hardware diagnostic on power-up; vector display calibration |
| **Attract Mode** | Demo gameplay with asteroids drifting; "INSERT COIN" text flashes; high score table displayed; game logo shown |
| **Coin Insert** | Credit counter incremented; "PUSH START" appears; 1-player or 2-player select |
| **Game Active** | Main gameplay loop; substates: Playing, Ship Destroyed, Respawning, Wave Transition |
| **Game Over** | "GAME OVER" text displayed over playfield |
| **High Score Entry** | If score qualifies for top 10: player enters 3-character initials using rotate buttons to cycle letters and fire/hyperspace to confirm |

### 14.2 Two-Player Mode

| Parameter | Value |
|---|---|
| Mode | Alternating turns (not simultaneous) |
| Turn switch | Players alternate on each life lost |
| Separate state | Each player has independent score, lives, and wave progress |
| Display | Current player indicator shown; scores for both players displayed |

### 14.3 Game Active Substates

| Substate | Description |
|---|---|
| **Playing** | Ship on screen; all game objects active; player has full control |
| **Ship Destroyed** | Death animation playing; ~160 frames; no player control |
| **Respawning** | Waiting for center of screen to be clear; ship materializes with brief invincibility |
| **Wave Transition** | All asteroids cleared; brief pause (~48 frames); new wave of asteroids spawns at edges |
| **Hyperspace Jump** | Ship invisible for several frames; random position calculated; reappearance check performed |

---

## 15. Audio Design

### 15.1 Background "Heartbeat" (Thump-Thump)

| Parameter | Value |
|---|---|
| Sound | Alternating two-tone low-frequency "thump" -- a deep bass pulse alternating between two slightly different pitches (often compared to the Jaws theme) |
| Tempo at wave start | Slow (~1 beat per second) |
| Tempo progression | Increases as asteroids are destroyed within a wave; faster = fewer asteroids remaining |
| Maximum tempo | Rapid pulsing when only 1-2 asteroids remain |
| Reset | Tempo resets to slow at the start of each new wave |
| Purpose | Creates tension and communicates game state aurally; serves as the game's "music" |

### 15.2 Sound Effects

| Event | Sound Description |
|---|---|
| **Ship thrust** | Continuous white-noise rumble / hiss while thrust button is held |
| **Fire (player)** | Short sharp "pew" -- high-pitched blip |
| **Ship explosion** | Low-frequency cascading crunch / boom, longer duration than asteroid explosions |
| **Large asteroid explosion** | Deep, bassy crumble |
| **Medium asteroid explosion** | Mid-frequency crumble, shorter than large |
| **Small asteroid explosion** | High-pitched short pop / crack |
| **Large saucer** | Low-pitched warbling tone (oscillating frequency); plays continuously while saucer is on screen |
| **Small saucer** | Higher-pitched, faster warbling tone; distinctly more urgent than large saucer sound |
| **Saucer explosion** | Similar to asteroid explosion |
| **Extra life earned** | Distinctive ascending chime / tone sequence |
| **Hyperspace (departure)** | Quick descending "zip" or whoosh |
| **Hyperspace (arrival)** | Quick ascending "zip" or pop |

### 15.3 Audio Hardware

| Parameter | Value |
|---|---|
| Sound generation | Discrete analog circuits (no dedicated sound chip) |
| Channels | Multiple simultaneous analog sound generators |
| Output | Mono speaker in cabinet |
| Volume | Thump volume is constant; only tempo changes. Other sounds mix on top of the heartbeat |

---

## 16. UI Layout

### 16.1 Screen Composition

```
+-----------------------------------------------------------+
|  00000          1UP        00000                          |
|  [ship][ship]                             2UP             |
|                                                           |
|                                                           |
|            *                                              |
|         *     *        [asteroid]                         |
|        *       *                                          |
|         *     *              [asteroid]                   |
|            *                                              |
|                                                           |
|                    /\                                     |
|                   /  \          [asteroid]                |
|                  / == \                                    |
|                   \  /                                    |
|                                                           |
|      [asteroid]                                           |
|                                  [asteroid]               |
|                                                           |
|                                                           |
|                                                           |
+-----------------------------------------------------------+
```

### 16.2 HUD Elements

| Element | Position | Description |
|---|---|---|
| Player 1 Score | Top-left corner | 5-digit score, always visible |
| Player 2 Score | Top-right area | 5-digit score (shown in 2-player mode) |
| Current Player Indicator | Top-center ("1UP" / "2UP") | Indicates whose turn is active |
| Remaining Lives | Below Player 1 score (left side) | Small ship icons; one icon per remaining life (excluding the currently active ship) |
| High Score | Top-center (attract mode) | Displayed during attract mode |
| "INSERT COIN" | Center-bottom (attract mode) | Flashing text during attract mode |
| Copyright | Bottom of screen (attract mode) | "@ 1979 ATARI INC" |

### 16.3 Visual Characteristics

| Property | Description |
|---|---|
| Line brightness | All vector lines rendered at uniform brightness (monochrome white) |
| Line weight | Thin single-pixel-equivalent vector strokes |
| Background | Pure black (no beam deflection = no light) |
| Flicker | Slight natural vector display flicker from refresh timing; more objects = more visible flicker due to DVG draw time |
| Glow | Vector CRT phosphor produces a natural slight glow/bloom around bright lines |

---

## 17. Object Definitions (Vector Shapes)

### 17.1 Player Ship

```
     /\
    /  \
   /    \
  / /--\ \
   /    \
```

- Narrow isosceles triangle, open notch at rear
- 5 connected line segments forming the outline
- Thrust flame: flickering short line at rear center when thrusting

### 17.2 Asteroids (Example Shapes)

- Irregular roughly-circular polygons
- 4 shape variants per size (randomly assigned)
- Large: ~8-12 vertices; Medium: same shapes scaled 50%; Small: same shapes scaled 25%
- Vertices are offset from a circle at varying radii to create the jagged appearance

### 17.3 Saucers

```
  ____
 /    \
/======\
 \----/
```

- Classic flying saucer profile: dome on top, horizontal line across middle, wider body, tapered bottom
- Large saucer: ~42 coordinate units wide
- Small saucer: ~21 coordinate units wide

### 17.4 Bullets

- Single bright dot (point)
- No trailing effect in the original

### 17.5 Explosions

- Ship explosion: the ship's line segments separate and fly outward in random directions, fading over ~160 frames
- Asteroid explosion: fragments of the asteroid outline scatter briefly, then disappear
- Saucer explosion: similar scatter effect to asteroids

---

## 18. Data Contracts

### 18.1 Config Schema

```json
{
  "game": {
    "version": "1.0.0",
    "starting_lives": 3,
    "extra_life_every": 10000,
    "max_players": 2,
    "language": "english"
  },
  "display": {
    "resolution_x": 1024,
    "resolution_y": 768,
    "target_fps": 60,
    "render_mode": "vector",
    "monochrome": true,
    "phosphor_glow": true
  },
  "physics": {
    "ship_rotation_step_degrees": 5,
    "ship_max_speed": 17.0,
    "ship_thrust_acceleration": 0.15,
    "ship_drag_coefficient": 0.005,
    "bullet_speed": 17.0,
    "bullet_lifetime_frames": 18,
    "max_player_bullets": 4,
    "max_saucer_bullets": 2,
    "max_asteroids": 27
  },
  "asteroids": {
    "large_radius": 34,
    "medium_radius": 17,
    "small_radius": 8,
    "min_speed": 4.0,
    "max_speed": 6.5,
    "small_speed_bonus_factor": 1.63,
    "shape_variants_per_size": 4
  },
  "saucers": {
    "initial_timer_frames": 146,
    "timer_decrement": 6,
    "minimum_timer_frames": 32,
    "fire_interval_frames": 10,
    "large_saucer_size": 42,
    "small_saucer_size": 21,
    "small_saucer_score_threshold": 10000,
    "small_saucer_only_threshold": 40000,
    "high_accuracy_threshold": 35000
  },
  "hyperspace": {
    "failure_range_start": 24,
    "failure_range_end": 31,
    "random_range": 32
  },
  "scoring": {
    "large_asteroid": 20,
    "medium_asteroid": 50,
    "small_asteroid": 100,
    "large_saucer": 200,
    "small_saucer": 1000,
    "score_rollover": 99990
  }
}
```

### 18.2 Runtime State Snapshot

```json
{
  "time": {
    "tick": 0,
    "elapsed_seconds": 0.0
  },
  "game": {
    "state": "playing",
    "wave": 1,
    "current_player": 1,
    "saucer_timer_frames": 146,
    "wave_timer_frames": 0,
    "thump_tempo_frames": 60
  },
  "player": {
    "score": 0,
    "lives_remaining": 3,
    "next_extra_life_at": 10000,
    "ship": {
      "active": true,
      "position": { "x": 512, "y": 384 },
      "velocity": { "x": 0.0, "y": 0.0 },
      "heading_degrees": 0,
      "thrusting": false,
      "invincible": false,
      "invincibility_timer_frames": 0
    }
  },
  "bullets": [
    {
      "active": false,
      "position": { "x": 0, "y": 0 },
      "velocity": { "x": 0.0, "y": 0.0 },
      "lifetime_remaining_frames": 0
    }
  ],
  "asteroids": [
    {
      "active": true,
      "size": "large",
      "shape_variant": 0,
      "position": { "x": 100, "y": 200 },
      "velocity": { "x": 1.5, "y": -0.8 },
      "rotation_angle": 0.0,
      "rotation_speed": 0.5
    }
  ],
  "saucer": {
    "active": false,
    "type": "none",
    "position": { "x": 0, "y": 0 },
    "velocity": { "x": 0.0, "y": 0.0 },
    "direction_change_timer": 0,
    "fire_timer": 0
  },
  "saucer_bullets": [
    {
      "active": false,
      "position": { "x": 0, "y": 0 },
      "velocity": { "x": 0.0, "y": 0.0 },
      "lifetime_remaining_frames": 0
    }
  ]
}
```

---

## 19. Technical Requirements

| Requirement | Specification |
|---|---|
| Simulation tick | Fixed `dt = 1/60 s`; all gameplay logic runs at 60 Hz |
| Update order | `Input -> Ship Physics -> Bullet Update -> Asteroid Update -> Saucer AI -> Collision Detection -> Scoring -> Spawn Logic -> Audio -> Render` |
| Determinism | Same initial RNG seed + same input sequence = identical game state at every tick |
| Pause behavior | Not present in original arcade (coin-op games do not pause); implementation may add pause with all timers frozen |
| Wrapping calculation | All position updates must apply modular wrapping before collision checks |
| Collision pass | Run collision checks every frame after position updates; check all bullet-asteroid, bullet-saucer, ship-asteroid, ship-saucer, and ship-saucer-bullet pairs |
| Object pooling | Pre-allocate arrays: 27 asteroid slots, 4 player bullet slots, 2 saucer bullet slots, 1 saucer slot, 1 ship slot |
| Score overflow | Handle BCD rollover at 99,990; continue tracking internally for extra life calculations |
| Entity lifecycle | `spawn -> active -> destroyed (animation) -> inactive (returned to pool)` |

### 19.1 Performance Budget

| Metric | Target |
|---|---|
| Render frame | 16.67 ms (60 FPS) |
| Logic tick | <= 2 ms average |
| Input latency | <= 1 frame (16.67 ms) from button press to visual response |
| Audio latency | <= 2 frames (33 ms) from event to sound |
| Maximum draw list | 35 objects with full vertex sets in a single frame |

---

## 20. QA Acceptance Criteria

1. Ship rotates in exactly 72 discrete steps of 5 degrees each; holding rotate for one full second produces 300 degrees of rotation.
2. Ship thrust applies acceleration in the nose direction; releasing thrust causes the ship to coast and gradually decelerate (not stop instantly).
3. Ship velocity is clamped and cannot exceed the maximum speed regardless of thrust duration.
4. All objects (ship, asteroids, bullets, saucers) wrap seamlessly across all four screen edges with no visual discontinuity.
5. Player can fire a maximum of 4 bullets simultaneously; the 5th press is ignored until a bullet expires or hits a target.
6. Bullets travel at the correct speed (equal to ship max speed when fired from rest) and expire after ~18 frames.
7. Bullet velocity correctly composes with ship velocity (firing backward while moving forward produces slow or stationary bullets).
8. Large asteroids split into exactly 2 medium asteroids; medium into exactly 2 small; small are destroyed. Exception: when 27 asteroids are on screen, splits produce only 1 fragment.
9. Scoring values are exact: large=20, medium=50, small=100, large saucer=200, small saucer=1000.
10. Extra life is awarded at every 10,000-point increment with the correct audio cue.
11. Wave 1 starts with 4 large asteroids; wave 2 with 6; wave 3 with 8; wave 4 with 10; wave 5+ with 11.
12. Large saucers fire randomly; small saucers aim at the player with increasing accuracy above 35,000 points.
13. Only large saucers appear below 10,000 points; only small saucers appear above 40,000 points; mixed in between.
14. Hyperspace teleports the ship to a random location with approximately a 25% chance of fatal explosion.
15. Ship respawns at center screen only when the center area is clear of asteroids and saucers.
16. Ship death animation shows ship fragments flying outward for ~160 frames before respawn sequence begins.
17. The heartbeat thump sound alternates between two pitches, starting slow at wave start and accelerating as asteroids are destroyed.
18. Saucer warbling sound plays continuously while a saucer is on screen; pitch differs between large and small saucer.
19. Score display is 5 digits and rolls over at 99,990.
20. High score entry allows 3-character initials using rotate buttons to cycle letters and fire to confirm.
21. Collision detection correctly handles objects near screen edges that are partially wrapped to the opposite side.
22. Two-player alternating mode maintains independent scores, lives, and wave progress for each player.
23. Saucer spawn timer decreases after each saucer appearance, preventing indefinite stalling by not shooting asteroids.
24. New wave asteroids spawn only at screen edges, never overlapping the center safe zone.
25. All vector-drawn objects render as connected line segments with uniform brightness on a black background.
