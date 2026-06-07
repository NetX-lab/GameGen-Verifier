# Breakout — Complete Game Specification

> A comprehensive specification for faithfully recreating Breakout (Atari, 1976) enhanced with Arkanoid-style mechanics (Taito, 1986). This document covers the classic Breakout foundation -- paddle, ball, brick wall, scoring, and progressive difficulty -- augmented with power-ups, multiple brick types, and expanded level progression drawn from Arkanoid. All values are tuned for a modern 2D implementation at 60 FPS.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Mechanics — Paddle](#3-core-mechanics--paddle)
4. [Core Mechanics — Ball](#4-core-mechanics--ball)
5. [Physics System](#5-physics-system)
6. [Brick Types & Layout](#6-brick-types--layout)
7. [Scoring System](#7-scoring-system)
8. [Level Progression](#8-level-progression)
9. [Power-up System](#9-power-up-system)
10. [Lives & Game Over](#10-lives--game-over)
11. [Game States](#11-game-states)
12. [Audio Design](#12-audio-design)
13. [UI Layout](#13-ui-layout)

---

## 1. Game Overview

- **Genre**: Brick-breaking / block-breaker arcade
- **Perspective**: 2D top-down fixed-screen
- **Input**: Horizontal-axis only (left/right arrow keys, mouse horizontal movement, or analog paddle). One action button (launch ball / fire laser / release caught ball).
- **Objective**: Destroy all destructible bricks on each level by deflecting a ball off a paddle. Clear all levels to win.
- **Lose Condition**: All lives are lost. A life is lost when the ball falls below the paddle (past the bottom edge of the playfield).
- **Win Condition (per level)**: All destructible bricks (colored and silver) are destroyed. Gold/indestructible bricks do not count toward clearance.
- **Win Condition (game)**: Complete all 33 levels.

### Historical Context

The original Breakout (1976) featured 8 rows of bricks, a single ball, a shrinking paddle, and two screens of play. Arkanoid (1986) expanded the formula with power-up capsules, varied brick types, diverse level layouts across 33 stages, and a final boss. This specification merges both: the classic Breakout physics and scoring foundation with Arkanoid's power-up system, brick variety, and level structure.

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Logical resolution | 480 x 640 pixels (portrait orientation) |
| Playfield area | 416 x 576 pixels (centered, 32px border left/right, 32px top, 32px bottom reserved for paddle zone + death zone) |
| Display mode | Windowed or Fullscreen (aspect-ratio locked 3:4) |
| Frame rate target | 60 FPS |
| Physics time step | Fixed 1/60 second (16.667 ms) |
| Coordinate origin | Top-left corner of the playfield is (0, 0) |

### Playfield Layout (top to bottom)

| Region | Y-Range (pixels) | Description |
|--------|-------------------|-------------|
| Ceiling | y = 0 | Top wall. Ball bounces off this surface. |
| Brick zone | y = 32 to y = 288 | Area where brick rows are placed |
| Open play zone | y = 288 to y = 576 | Empty area for ball travel |
| Paddle zone | y = 556 | Vertical center of paddle when at default position |
| Death line | y = 640 | Ball crossing this line = life lost |

### Side Walls

- Left wall at x = 0, right wall at x = 416.
- Ball reflects off both side walls with perfect elastic reflection.
- The playfield is fully enclosed on three sides (left, right, top). The bottom is open.

### Game Loop

```
1. Process input (paddle movement, action button)
2. Update paddle position (clamp to playfield bounds)
3. Update ball position(s) — move by velocity * dt
4. Check ball-wall collisions (left, right, ceiling)
5. Check ball-brick collisions (damage brick, reflect ball, spawn power-up if applicable)
6. Check ball-paddle collision (reflect ball with angle mapping)
7. Check ball-death-line (lose life if ball.y > 640)
8. Update power-up capsules (fall, check paddle catch)
9. Update active power-up effects (timers, laser shots)
10. Check level-clear condition
11. Check game-over condition
12. Render: background -> walls -> bricks -> paddle -> ball(s) -> power-up capsules -> laser shots -> particles -> UI
```

---

## 3. Core Mechanics -- Paddle

### Paddle Properties

| Property | Value |
|----------|-------|
| Default width | 80 pixels |
| Extended width (Extend power-up) | 128 pixels |
| Shrunken width (classic Breakout rule) | 40 pixels |
| Height | 12 pixels |
| Y-position (center) | 556 pixels from top |
| Movement speed | 480 pixels/second (8 pixels/frame at 60 FPS) |
| Color | Bright cyan / light blue (#00E0FF) |

### Paddle Movement

- The paddle moves only along the horizontal axis.
- Clamped so that `paddle.left >= 0` and `paddle.right <= 416` (playfield width).
- Input options:
  - **Keyboard**: Left/Right arrow keys provide constant-speed movement at 480 px/s.
  - **Mouse**: Paddle center tracks mouse X position with no acceleration curve (instant response). Still clamped to playfield bounds.
- The paddle cannot move vertically under any circumstances.

### Paddle States

| State | Description |
|-------|-------------|
| Normal | Default 80px width, standard reflection |
| Extended | 128px width via Extend (E) power-up. Reverts after 30 seconds or next life loss. |
| Laser | 80px width, paddle displays two laser cannons on its top surface. Can fire laser shots with action button. Reverts after collecting a different power-up or losing a life. |
| Catch | 80px width, ball sticks to paddle surface on contact. Player presses action button to release. Reverts after collecting a different power-up or losing a life. |

### Classic Breakout Paddle Shrink (Level 1-2 only)

In the first two levels (which replicate the original Breakout layout), the paddle shrinks to 40 pixels (half-width) after the ball has broken through the top two rows (red rows) and made contact with the ceiling. This is a faithful recreation of the original 1976 mechanic. In levels 3+, this mechanic is replaced by the Arkanoid power-up system.

---

## 4. Core Mechanics -- Ball

### Ball Properties

| Property | Value |
|----------|-------|
| Diameter | 8 pixels |
| Shape | Circle (collision treated as a point at center for simplicity, or full circle for precision) |
| Color | White (#FFFFFF) |
| Initial speed | 240 pixels/second (4 px/frame) |
| Speed after 4 brick hits | 300 pixels/second (5 px/frame) |
| Speed after 12 brick hits | 360 pixels/second (6 px/frame) |
| Speed after orange-row contact | 360 pixels/second (if not already at this speed) |
| Speed after red-row contact | 420 pixels/second (7 px/frame) |
| Maximum speed | 480 pixels/second (8 px/frame) |
| Minimum launch angle | 30 degrees from horizontal (prevents near-horizontal travel) |
| Maximum launch angle | 150 degrees from horizontal |

### Ball Speed Progression

The ball speed increases based on two independent triggers. Once a speed tier is reached, it does not decrease (except via the Slow power-up).

| Trigger | Speed (px/s) | Speed (px/frame) |
|---------|-------------|-------------------|
| Launch / start of life | 240 | 4.0 |
| After 4 total brick hits | 300 | 5.0 |
| After 12 total brick hits | 360 | 6.0 |
| First contact with orange-row brick | 360 | 6.0 |
| First contact with red-row brick | 420 | 7.0 |
| Each subsequent level adds +12 px/s base (cap at 480) | up to 480 | up to 8.0 |

The hit counter and row-contact flags reset at the start of each new level. The Slow (S) power-up temporarily overrides the current speed to 180 px/s for its duration.

### Ball Launch

- At the start of each life, the ball rests on top of the paddle, centered.
- The ball moves with the paddle until the player presses the action button.
- Upon launch, the ball departs at a fixed angle of 60 degrees from horizontal (30 degrees from vertical), moving up and to the right.
- If the Catch power-up is active, the ball also sticks on paddle contact and is re-launched with the action button at the angle of the paddle's normal at the contact point.

### Multi-Ball Behavior

- When the Disruption (D) power-up is collected, the current ball splits into 3 balls.
- The original ball continues on its current trajectory.
- Two additional balls spawn at the same position, traveling at +30 degrees and -30 degrees from the original ball's velocity vector.
- All balls share the same speed. Each ball independently bounces and destroys bricks.
- When multiple balls are in play, losing one ball (it exits the bottom) does not cost a life. A life is lost only when the **last** remaining ball exits the bottom.
- No additional power-up capsules spawn while multiple balls are in play.

---

## 5. Physics System

### Wall Reflection

Walls use perfect elastic reflection (angle of incidence = angle of reflection).

| Surface | Reflection Rule |
|---------|----------------|
| Left wall (x = 0) | `velocity.x = abs(velocity.x)` (reflect horizontal, keep vertical) |
| Right wall (x = 416) | `velocity.x = -abs(velocity.x)` |
| Ceiling (y = 0) | `velocity.y = abs(velocity.y)` (reflect vertical, keep horizontal) |

No energy is lost on wall bounces. The ball speed (magnitude of velocity vector) remains constant through wall reflections.

### Brick Reflection

When the ball collides with a brick:

1. Determine which face of the brick was hit (top, bottom, left, right) based on the ball's approach direction and overlap.
2. Reflect the appropriate velocity component:
   - **Top/bottom hit**: `velocity.y = -velocity.y`
   - **Left/right hit**: `velocity.x = -velocity.x`
3. If the ball hits the exact corner of a brick, both components are reflected: `velocity.x = -velocity.x; velocity.y = -velocity.y`.
4. The ball can destroy only **one** brick per physics step (prevents tunneling through multiple bricks in a single frame). If multiple bricks overlap the ball's path, resolve the closest collision first.

### Paddle Reflection -- Angle Mapping System

The paddle uses a **position-based angle mapping** system rather than simple reflection. This is the core mechanic that gives the player control over the ball's trajectory.

**Formula:**

```
offset = (ball.x - paddle.center_x) / (paddle.width / 2)
    // offset ranges from -1.0 (left edge) to +1.0 (right edge)

reflected_angle = offset * max_deflection_angle
    // max_deflection_angle = 60 degrees

final_angle = 90 + reflected_angle
    // 90 degrees = straight up
    // Result: 30 degrees (hard left) to 150 degrees (hard right)
    // Measured from the positive X-axis (rightward horizontal)
```

| Hit Position | Offset | Reflected Angle | Ball Direction |
|-------------|--------|-----------------|----------------|
| Dead center | 0.0 | 90 degrees (straight up) | Directly upward |
| 1/4 left of center | -0.25 | 105 degrees | Up and slightly left |
| 1/2 left of center | -0.50 | 120 degrees | Up-left at 30 deg from vertical |
| Left edge | -1.0 | 150 degrees | Steep left (60 deg from vertical) |
| 1/4 right of center | +0.25 | 75 degrees | Up and slightly right |
| 1/2 right of center | +0.50 | 60 degrees | Up-right at 30 deg from vertical |
| Right edge | +1.0 | 30 degrees | Steep right (60 deg from vertical) |

**After computing the angle**, the ball's velocity vector is set to:

```
velocity.x = speed * cos(final_angle)
velocity.y = -abs(speed * sin(final_angle))
    // Always ensure the ball moves upward after paddle contact
```

### Angle Clamping

- The ball must never travel at an angle shallower than 30 degrees from horizontal.
- If any collision would result in a near-horizontal trajectory (angle within 5 degrees of 0 or 180 degrees), clamp to 30 degrees (or 150 degrees) to prevent tediously long horizontal bouncing.
- The ball must never travel perfectly vertically (90 degrees exactly) for extended periods. If the ball has bounced vertically for more than 5 consecutive wall hits with no horizontal displacement, apply a small random perturbation of +/- 3 degrees.

### Tunneling Prevention

- At maximum speed (480 px/s = 8 px/frame), the ball moves 8 pixels per frame.
- Since bricks are 8 pixels tall, the ball could skip through a brick in one frame.
- **Solution**: Use swept collision detection. For each frame, cast the ball's path as a line segment from its previous position to its new position, and check for intersections with all collidable surfaces along that segment.
- Alternatively, substep the physics: if ball speed exceeds 4 px/frame, subdivide the movement into 2 substeps per frame.

---

## 6. Brick Types & Layout

### Brick Dimensions

| Property | Value |
|----------|-------|
| Brick width | 32 pixels |
| Brick height | 16 pixels |
| Horizontal gap between bricks | 0 pixels (bricks are flush) |
| Vertical gap between bricks | 0 pixels (bricks are flush) |
| Grid columns | 13 (13 x 32 = 416 = playfield width) |
| Grid rows | 18 maximum (18 x 16 = 288 pixels of brick zone) |
| Bricks per full row | 13 |
| Maximum bricks per level | 234 (13 x 18) |

### Brick Types

#### Colored Bricks (Standard -- 1 Hit to Destroy)

| Color | Hex Code | Points | Hits Required |
|-------|----------|--------|---------------|
| White | #FCFCFC | 50 | 1 |
| Orange | #FC7460 | 60 | 1 |
| Light Blue | #3CBCFC | 70 | 1 |
| Green | #80D010 | 80 | 1 |
| Red | #D82800 | 90 | 1 |
| Blue | #0070EC | 100 | 1 |
| Pink | #FC74B4 | 110 | 1 |
| Yellow | #FC9838 | 120 | 1 |

#### Silver Bricks (Multi-Hit)

| Property | Value |
|----------|-------|
| Color | #BCBCBC (silver/gray) |
| Points | 50 x current level number |
| Hits required | 2 + floor((level - 1) / 8) |
| Hit behavior | Flashes white on hit; no visual crack stages |
| Destructible | Yes |
| Counts toward level clear | Yes |

**Silver brick hit table:**

| Levels | Hits Required |
|--------|---------------|
| 1 -- 8 | 2 |
| 9 -- 16 | 3 |
| 17 -- 24 | 4 |
| 25 -- 32 | 5 |
| 33 | 6 |

#### Gold Bricks (Indestructible)

| Property | Value |
|----------|-------|
| Color | #F0BC3C (gold) |
| Points | 0 (cannot be destroyed) |
| Hits required | Infinite (indestructible) |
| Hit behavior | Ball reflects normally; brick flashes but is not damaged |
| Destructible | No |
| Counts toward level clear | No |
| Exception | The Mega Ball power-up (from Arkanoid II) can destroy gold bricks |

### Classic Breakout Layout (Levels 1 and 2)

Levels 1 and 2 use the original 1976 Breakout brick layout to honor the source material.

| Row (from top) | Color | Points per Brick | Bricks in Row | Row Points |
|----------------|-------|-----------------|----------------|------------|
| Row 1 | Red | 7 | 14 | 98 |
| Row 2 | Red | 7 | 14 | 98 |
| Row 3 | Orange | 5 | 14 | 70 |
| Row 4 | Orange | 5 | 14 | 70 |
| Row 5 | Green | 3 | 14 | 42 |
| Row 6 | Green | 3 | 14 | 42 |
| Row 7 | Yellow | 1 | 14 | 14 |
| Row 8 | Yellow | 1 | 14 | 14 |
| **Total** | | | **112** | **448** |

For the classic layout (levels 1-2), the 13-column grid is not used. Instead, 14 bricks of width 29 pixels each (with 2px padding to fill 416px) are arranged in 8 rows, positioned in the upper portion of the brick zone (rows 3-10 of the 18-row grid), with open space above and below.

### Arkanoid-Style Layouts (Levels 3-33)

Starting from level 3, each level has a unique brick arrangement using the 13-column x 18-row grid. Layouts may include:

- Geometric patterns (diamonds, chevrons, spirals)
- Mixed brick types (colored, silver, gold)
- Open spaces within the grid creating channels for the ball
- Gold bricks forming indestructible barriers that channel ball movement
- Silver bricks as high-value targets requiring multiple hits
- Symmetrical and asymmetrical formations

Each level's layout is stored as a 13 x 18 grid where each cell is either empty (0) or contains a brick type index (1-10).

---

## 7. Scoring System

### Points Per Brick

| Brick Type | Points |
|------------|--------|
| White | 50 |
| Orange | 60 |
| Light Blue | 70 |
| Green | 80 |
| Red | 90 |
| Blue | 100 |
| Pink | 110 |
| Yellow | 120 |
| Silver | 50 x level number |
| Gold | 0 (indestructible) |

### Classic Breakout Scoring (Levels 1-2 only)

| Brick Color | Points |
|-------------|--------|
| Yellow (bottom 2 rows) | 1 |
| Green (rows 5-6) | 3 |
| Orange (rows 3-4) | 5 |
| Red (top 2 rows) | 7 |
| **Total per screen** | **448** |

### Bonus Points

| Action | Points |
|--------|--------|
| Power-up capsule collected | 1,000 |
| Level cleared bonus | 5,000 + (1,000 x level number) |
| Extra life not used at game end | 10,000 each |
| All bricks cleared without losing a life | 50,000 (perfect clear bonus) |

### Score Display

- Score is displayed at the top-right of the screen.
- Displayed as a 7-digit number, zero-padded: `0000000`.
- High score is displayed at the top-center.
- Score updates instantly when a brick is destroyed or a bonus is awarded.
- Score pop-up: A small floating number (+50, +100, etc.) appears at the destroyed brick's position and floats upward for 0.5 seconds before fading.

---

## 8. Level Progression

### Level Structure

| Property | Value |
|----------|-------|
| Total levels | 33 |
| Levels 1-2 | Classic Breakout layout (8 rows x 14 bricks) |
| Levels 3-33 | Arkanoid-style unique layouts (13 x 18 grid) |
| Level clear condition | All colored and silver bricks destroyed |
| Between-level transition | 2-second fade to black, "ROUND X" text, 2-second fade in |

### Difficulty Scaling Per Level

| Level Range | Ball Base Speed (px/s) | Silver Hits | New Brick Types Introduced | Power-up Drop Rate |
|-------------|----------------------|-------------|---------------------------|-------------------|
| 1-2 | 240 | N/A (classic) | Yellow, Green, Orange, Red (classic) | No power-ups |
| 3-5 | 252 | 2 | White, Orange, Light Blue, Green | 25% per colored brick |
| 6-10 | 276 | 2 | + Red, Blue bricks; Silver bricks | 22% per colored brick |
| 11-16 | 300 | 3 | + Pink, Yellow bricks; Gold bricks | 20% per colored brick |
| 17-24 | 336 | 4 | All types in complex patterns | 18% per colored brick |
| 25-32 | 372 | 5 | Dense/challenging layouts | 15% per colored brick |
| 33 (Final) | 408 | 6 | Boss-inspired layout | 12% per colored brick |

### Ball Speed Increase Within a Level

Within each level, the ball speed increases on top of the base speed:

| Trigger | Speed Increase |
|---------|---------------|
| 4 bricks destroyed | +60 px/s |
| 12 bricks destroyed | +60 px/s (cumulative +120) |
| First orange-row brick hit | Set minimum to base + 60 px/s |
| First red-row brick hit | Set minimum to base + 120 px/s |
| Maximum speed cap | 480 px/s |

These in-level speed triggers reset at the start of each level.

### Level Transition

1. Last destructible brick is destroyed.
2. All remaining balls and power-ups are removed from the playfield.
3. Score tallies briefly (level clear bonus appears).
4. 2-second pause with "STAGE CLEAR" text.
5. Screen fades to black.
6. "ROUND [N+1]" displayed for 1.5 seconds.
7. New brick layout fades in.
8. Paddle appears at center with ball attached.
9. Player presses action button to launch.

---

## 9. Power-up System

### General Power-up Rules

| Property | Value |
|----------|-------|
| Capsule width | 16 pixels |
| Capsule height | 8 pixels |
| Fall speed | 60 pixels/second (1 px/frame) |
| Spawn trigger | Destroying certain colored bricks (never silver or gold) |
| Drop probability | Varies by level (see Level Progression table) |
| Max capsules on screen | 1 (no new capsule spawns while one is falling) |
| Collection | Capsule must touch the paddle to be collected |
| Missed capsule | Falls off the bottom of the screen; no penalty |
| Points for collection | 1,000 |
| Capsule during multi-ball | No capsules spawn while more than 1 ball is in play |
| Stacking | Collecting a new power-up **replaces** the current active power-up (except Extra Life, which stacks) |

### Power-up Types

| Letter | Name | Capsule Color | Hex Code | Effect | Duration |
|--------|------|--------------|----------|--------|----------|
| S | Slow | Orange | #FC7460 | Reduces ball speed to 180 px/s | 12 seconds, then returns to current speed tier |
| C | Catch | Green | #80D010 | Ball sticks to paddle on contact; released with action button | Until replaced or life lost |
| E | Extend | Blue | #0070EC | Paddle width increases from 80px to 128px | 30 seconds or until replaced/life lost |
| D | Disruption | Cyan | #3CBCFC | Current ball splits into 3 balls (original + 2 copies at +/-30 degrees) | Until all extra balls are lost |
| L | Laser | Red | #D82800 | Paddle gains two laser cannons; action button fires twin laser bolts | Until replaced or life lost |
| B | Break | Pink | #FC74B4 | Opens an escape portal on the right wall; ball entering it advances to next level | Until ball enters portal or life lost |
| P | Player | Gray | #BCBCBC | Awards one extra life immediately | Instant (no duration) |

### Power-up Details

#### Slow (S) -- Orange

- Immediately sets ball speed to 180 px/s regardless of current speed tier.
- After 12 seconds, the ball returns to whatever speed tier it had before the Slow was collected.
- If the ball hits enough bricks during the slow period to trigger a speed increase, the new speed tier is stored but does not take effect until the slow expires.
- Visual: Ball leaves a short trailing afterimage while slowed.

#### Catch (C) -- Green

- When active, the ball stops on the paddle's surface upon contact instead of reflecting.
- The ball's position is locked relative to the paddle (moves with the paddle horizontally).
- Player presses the action button to release the ball.
- Release angle is determined by the ball's position on the paddle (same angle mapping as normal paddle reflection).
- Only works with a single ball. If multi-ball is active and Catch is collected, only the next ball to contact the paddle will be caught; others continue freely.

#### Extend (E) -- Blue

- Paddle width smoothly animates from 80px to 128px over 0.25 seconds.
- All paddle physics (reflection, clamping) immediately use the new width.
- After 30 seconds, the paddle smoothly shrinks back to 80px over 0.25 seconds.
- If the paddle is against a wall when extended, it is pushed inward so it does not clip outside the playfield.
- Collecting another Extend resets the 30-second timer.

#### Disruption (D) -- Cyan

- The single ball in play becomes 3 balls.
- The two new balls are clones of the original (same speed, size, color).
- New balls launch at +30 degrees and -30 degrees relative to the original's current velocity.
- Each ball independently destroys bricks and reflects off surfaces.
- If a Disruption is collected while already in multi-ball, no additional balls are spawned (capped at 3 balls).
- A life is only lost when the **last** ball exits the bottom.
- No power-up capsules drop while multiple balls are in play.

#### Laser (L) -- Red

- Two small cannon sprites appear on the top-left and top-right of the paddle.
- Pressing the action button fires two laser bolts simultaneously (one from each cannon).
- Laser bolt properties:

| Property | Value |
|----------|-------|
| Bolt width | 4 pixels |
| Bolt height | 12 pixels |
| Bolt speed | 600 pixels/second (10 px/frame) upward |
| Bolt color | Red (#FF0000) |
| Fire rate | Maximum 1 salvo (2 bolts) per 0.5 seconds (2 salvos per second) |
| Damage | 1 hit per bolt (destroys colored bricks instantly, chips 1 hit from silver) |
| Wall interaction | Bolts are destroyed upon hitting any wall or the ceiling |
| Brick interaction | Bolt is destroyed upon hitting any brick; the brick takes 1 hit of damage |
| Gold brick interaction | Bolt is destroyed; gold brick is unaffected |
| Max bolts on screen | 6 (3 salvos) |

#### Break (B) -- Pink

- A glowing portal (24 x 48 pixels) appears on the right wall, vertically centered in the play zone (y = 288).
- The portal flashes/pulses with a pink glow.
- If the ball enters the portal (ball center crosses the portal's hitbox), the level is immediately cleared and the player advances to the next level.
- The portal counts as a wall for reflection purposes if the ball hits the wall outside the portal's hitbox.
- If the player loses a life while Break is active, the portal disappears.

#### Player Extend / Extra Life (P) -- Gray

- Immediately adds 1 life to the player's remaining lives.
- No duration; effect is instant and permanent.
- This is the only power-up that does not replace the current active power-up. The current power-up remains active.
- Maximum lives capped at 9.

---

## 10. Lives & Game Over

### Lives System

| Property | Value |
|----------|-------|
| Starting lives | 3 |
| Maximum lives | 9 |
| Extra life sources | Player (P) power-up; score milestone (every 60,000 points) |
| Life lost trigger | Last (or only) ball exits below the death line (y > 640) |
| Display | Small paddle icons in the bottom-left corner of the screen |

### On Life Lost

1. All active power-up effects are cleared (paddle returns to normal width, laser deactivated, catch deactivated, Break portal closes, Slow ends).
2. All power-up capsules currently falling are removed.
3. Ball speed resets to the current level's base speed (in-level hit counter and row flags reset).
4. A new ball spawns on the paddle, centered.
5. 1.5-second pause before the player can move the paddle.
6. Player presses action button to launch.

### Game Over

1. Triggered when lives reach 0.
2. Ball and paddle freeze for 1 second.
3. "GAME OVER" text appears center-screen in large font.
4. Final score is displayed below.
5. If the score qualifies as a high score, a name-entry screen appears (3 initials, arcade style).
6. After 5 seconds (or after name entry), transition to the title screen.
7. No continues. A new game starts from level 1.

---

## 11. Game States

### State Machine

```
TITLE_SCREEN
    |
    v  (Press Start)
LEVEL_INTRO        <---+
    |                   |
    v  (after 3s)       |
PLAYING ----------------+--- (level cleared) ---> LEVEL_CLEAR
    |                   |                              |
    |  (life lost,      |                              v
    |   lives > 0)      |                         LEVEL_INTRO (next level)
    v                   |
RESPAWN ----------------+
    |
    |  (life lost, lives = 0)
    v
GAME_OVER
    |
    v  (after timeout or input)
HIGH_SCORE_ENTRY (if qualifies)
    |
    v
TITLE_SCREEN
```

### State Details

| State | Duration | Player Input | Description |
|-------|----------|-------------|-------------|
| TITLE_SCREEN | Indefinite | Start button / Enter / click | Shows game title, high score table, "Press Start" blinking text |
| LEVEL_INTRO | 3 seconds | None | Displays "ROUND [N]" centered on screen. Brick layout fades in during final second. |
| PLAYING | Indefinite | Paddle movement, action button | Active gameplay. Ball is live or attached to paddle (pre-launch). |
| RESPAWN | 1.5 seconds | None (input buffered) | After life loss. Paddle recenters, new ball placed. Brief invulnerability flash. |
| LEVEL_CLEAR | 3 seconds | None | "STAGE CLEAR" text, bonus score tally, transition effect |
| GAME_OVER | 5 seconds | None (then any key) | "GAME OVER" text, final score |
| HIGH_SCORE_ENTRY | Indefinite | Letter selection, confirm | 3-character name entry for high score table (top 10) |
| PAUSE | Indefinite | Pause key to resume | Freeze all game state. "PAUSED" overlay. Pressing Escape or P toggles. |

---

## 12. Audio Design

### Sound Effects

| Event | Sound Description | Duration | Priority |
|-------|-------------------|----------|----------|
| Ball hits paddle | Short mid-tone ping (440 Hz) | 50 ms | High |
| Ball hits wall | Short low-tone thud (220 Hz) | 30 ms | Medium |
| Ball hits ceiling | Short high-tone ping (660 Hz) | 40 ms | Medium |
| Colored brick destroyed | Bright pop/crack (varies by color, 500-900 Hz) | 60 ms | High |
| Silver brick hit (not destroyed) | Metallic clang (300 Hz + harmonics) | 80 ms | High |
| Silver brick destroyed | Heavy metallic shatter (200 Hz + white noise) | 120 ms | High |
| Gold brick hit | Dull thud + deflect tone (150 Hz) | 60 ms | Medium |
| Power-up capsule spawns | Soft descending chime | 100 ms | Low |
| Power-up collected | Rising arpeggio (3 notes over 200 ms) | 200 ms | High |
| Power-up expires | Descending two-tone | 150 ms | Medium |
| Laser bolt fired | Short zap/pulse (800 Hz square wave) | 40 ms | Medium |
| Laser bolt hits brick | Snap/crack (1000 Hz) | 50 ms | Medium |
| Ball launched | Soft thwip (300 Hz ascending) | 80 ms | High |
| Life lost | Descending tone (440 Hz to 110 Hz over 500 ms) | 500 ms | Critical |
| Extra life gained | Ascending fanfare (3-note major chord) | 400 ms | Critical |
| Level cleared | Victory jingle (8-note ascending melody) | 1500 ms | Critical |
| Game over | Somber 4-note descending melody | 2000 ms | Critical |
| Break portal active | Pulsing hum (continuous, low volume) | Looping | Low |
| Multi-ball split | Triple-chime spread | 200 ms | High |
| Paddle extend/shrink | Stretching rubber sound | 250 ms | Medium |

### Brick Pitch Mapping

Brick destruction sounds are pitched based on the brick's row position (higher rows = higher pitch), creating a musical effect as the player clears bricks:

| Row Position (from top) | Base Frequency |
|--------------------------|---------------|
| Row 1 (top) | 880 Hz (A5) |
| Row 5 | 740 Hz (F#5) |
| Row 9 | 587 Hz (D5) |
| Row 13 | 440 Hz (A4) |
| Row 18 (bottom) | 330 Hz (E4) |

Frequencies interpolate linearly for intermediate rows.

### Music

| Context | Style | Tempo | Loop |
|---------|-------|-------|------|
| Title screen | Upbeat electronic/chiptune | 130 BPM | Yes, seamless loop |
| Gameplay (levels 1-11) | Moderate-energy electronic | 120 BPM | Yes, per-level variation |
| Gameplay (levels 12-22) | Higher-energy electronic | 135 BPM | Yes |
| Gameplay (levels 23-33) | Intense/urgent electronic | 150 BPM | Yes |
| Level clear | Short victory fanfare | N/A | No (plays once) |
| Game over | Somber/reflective jingle | N/A | No (plays once) |
| High score entry | Light celebratory loop | 100 BPM | Yes |

---

## 13. UI Layout

### Screen Layout (480 x 640 logical pixels)

```
+--------------------------------------------------+  y=0
|  TOP HUD BAR (32px tall)                         |
|  [SCORE: 0000000]  [HI: 0000000]  [ROUND: 01]   |
+--------------------------------------------------+  y=32
|                                                  |
|  PLAYFIELD (416 x 576, centered with 32px        |
|  left/right borders)                             |
|                                                  |
|  +------------------------------------------+    |
|  |  BRICK ZONE (top of playfield)            |    |
|  |  rows of colored/silver/gold bricks       |    |
|  |                                           |    |
|  +------------------------------------------+    |
|  |                                           |    |
|  |  OPEN PLAY ZONE                           |    |
|  |  (ball bouncing area)                     |    |
|  |                                           |    |
|  |         o   <-- ball                      |    |
|  |                                           |    |
|  |       [========]  <-- paddle              |    |
|  +------------------------------------------+    |
|                                                  |
+--------------------------------------------------+  y=608
|  BOTTOM HUD BAR (32px tall)                      |
|  [Lives: PPP]  [Active Power-up: [L]]            |
+--------------------------------------------------+  y=640
```

### HUD Elements

#### Top HUD Bar (y = 0 to y = 32)

| Element | Position | Content | Font Size |
|---------|----------|---------|-----------|
| Current Score | Left-aligned (x = 8) | "SCORE: 0000000" | 14px monospace |
| High Score | Center-aligned | "HI: 0000000" | 14px monospace |
| Round Number | Right-aligned (x = 432) | "ROUND: 01" | 14px monospace |

#### Bottom HUD Bar (y = 608 to y = 640)

| Element | Position | Content | Font Size |
|---------|----------|---------|-----------|
| Lives remaining | Left-aligned (x = 8) | Small paddle icons (12x4 px each), one per remaining life | N/A (icons) |
| Active power-up | Right-aligned (x = 432) | Letter of current power-up in its capsule color, inside a bordered box. Empty if no power-up active. | 16px bold |
| Power-up timer | Right of power-up icon | Countdown bar (for timed power-ups like Slow and Extend) | 4px tall bar |

### Visual Effects

| Effect | Description | Trigger |
|--------|-------------|---------|
| Brick destruction | Brick shatters into 4-6 small rectangular particles matching the brick's color. Particles fly outward with gravity and fade over 0.5 seconds. | Brick health reaches 0 |
| Silver brick hit flash | Brick flashes white for 2 frames (33 ms) | Silver brick hit but not destroyed |
| Gold brick hit flash | Brick flashes bright yellow for 2 frames | Gold brick hit |
| Ball trail | 3-frame motion blur trail behind the ball (decreasing opacity: 60%, 30%, 10%) | Always while ball is moving |
| Power-up capsule glow | Capsule pulses brightness (sinusoidal, period 0.5s) | While capsule is falling |
| Paddle catch glow | Paddle surface shimmers green when Catch is active | Catch power-up active |
| Laser cannon glow | Two red dots pulse on paddle surface | Laser power-up active |
| Break portal | Swirling pink/magenta vortex animation on the right wall | Break power-up active |
| Extend animation | Paddle stretches smoothly from 80px to 128px (or shrinks back) over 0.25s | Extend gained/lost |
| Life lost flash | Screen flashes red for 4 frames (67 ms) | Ball exits the bottom |
| Level clear flash | Screen flashes white for 2 frames, then all remaining elements dissolve | Last brick destroyed |
| Score popup | "+[N]" text in white, floats upward 32px over 0.5s, fades out | Points awarded |

### Color Palette

| Element | Color | Hex |
|---------|-------|-----|
| Background (playfield) | Black | #000000 |
| Side walls | Dark gray | #404040 |
| Ceiling | Dark gray | #404040 |
| Wall highlight | Medium gray | #808080 |
| Paddle (default) | Bright cyan | #00E0FF |
| Paddle (laser mode) | Bright red | #FF4040 |
| Paddle (catch mode) | Bright green | #40FF40 |
| Paddle (extended) | Bright cyan (wider) | #00E0FF |
| Ball | White | #FFFFFF |
| Ball trail | White (fading) | #FFFFFF at 60% alpha |
| HUD text | White | #FFFFFF |
| HUD background | Dark blue | #101030 |
| Score popup text | Yellow | #FFFF00 |
| Game Over text | Red | #FF0000 |
| Stage Clear text | Green | #00FF00 |
| Round number text | White | #FFFFFF |

---

## Appendix A: Classic Breakout Scoring Verification

For levels 1-2 (classic Breakout layout):

```
Row 1 (Red):    14 bricks x 7 points =  98
Row 2 (Red):    14 bricks x 7 points =  98
Row 3 (Orange): 14 bricks x 5 points =  70
Row 4 (Orange): 14 bricks x 5 points =  70
Row 5 (Green):  14 bricks x 3 points =  42
Row 6 (Green):  14 bricks x 3 points =  42
Row 7 (Yellow): 14 bricks x 1 point  =  14
Row 8 (Yellow): 14 bricks x 1 point  =  14
-----------------------------------------
Total per screen:                       448
```

In the original arcade, the player can clear two screens of bricks with 3 lives, for a single-player maximum of **896 points**. In this enhanced version, the two classic levels are followed by 31 Arkanoid-style levels with significantly higher scoring potential.

---

## Appendix B: Ball Angle Reference Diagram

```
                    90deg (straight up)
                         |
              120deg     |     60deg
                  \      |      /
                   \     |     /
            150deg  \    |    /  30deg
                \    \   |   /    /
                 \    \  |  /    /
  180deg --------+----[PADDLE]----+-------- 0deg
  (left)         |               |         (right)
              paddle          paddle
              left edge       right edge

  Ball always moves UPWARD after paddle contact.
  Angle range: 30deg (far right) to 150deg (far left).
  Dead center hit = 90deg (straight up).
```

---

## Appendix C: Power-up Capsule Quick Reference

| Letter | Color | Name | Effect Summary |
|--------|-------|------|---------------|
| S | Orange | Slow | Ball speed -> 180 px/s for 12 seconds |
| C | Green | Catch | Ball sticks to paddle; release with action button |
| E | Blue | Extend | Paddle width 80px -> 128px for 30 seconds |
| D | Cyan | Disruption | Ball splits into 3 |
| L | Red | Laser | Paddle fires twin laser bolts |
| B | Pink | Break | Portal on right wall; enter to skip level |
| P | Gray | Player | +1 extra life (instant, does not replace active power-up) |

---

## Appendix D: Frame-by-Frame Ball Speed Reference

| Speed Tier | Pixels/Second | Pixels/Frame (60 FPS) | Substeps Needed |
|------------|--------------|----------------------|----------------|
| Slow (power-up) | 180 | 3.0 | 1 |
| Launch / base | 240 | 4.0 | 1 |
| After 4 hits | 300 | 5.0 | 1 (or 2 for safety) |
| After 12 hits / orange row | 360 | 6.0 | 2 |
| After red row | 420 | 7.0 | 2 |
| Maximum | 480 | 8.0 | 2 |
