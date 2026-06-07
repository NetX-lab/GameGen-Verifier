# Temple Run 2 -- Complete Game Specification

> A comprehensive specification for faithfully recreating Temple Run 2 (Imangi Studios, 2013 mobile endless runner). This document covers every system, mechanic, obstacle, power-up, scoring rule, environment, and interaction required for a full clone.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Running Mechanics](#3-core-running-mechanics)
4. [Control System](#4-control-system)
5. [Path & Lane System](#5-path--lane-system)
6. [Obstacle Types](#6-obstacle-types)
7. [Special Traversal Sections](#7-special-traversal-sections)
8. [Power-Up System](#8-power-up-system)
9. [Coin & Gem Economy](#9-coin--gem-economy)
10. [Character System](#10-character-system)
11. [Objective / Mission System](#11-objective--mission-system)
12. [Difficulty Scaling](#12-difficulty-scaling)
13. [Environment Zones & Maps](#13-environment-zones--maps)
14. [Resurrection / Save Me Mechanic](#14-resurrection--save-me-mechanic)
15. [Upgrade System (Abilities)](#15-upgrade-system-abilities)
16. [Scoring System](#16-scoring-system)
17. [UI Layout & HUD](#17-ui-layout--hud)
18. [Audio Design](#18-audio-design)

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| **Title** | Temple Run 2 |
| **Developer / Publisher** | Imangi Studios |
| **Original Release** | January 17, 2013 (iOS); January 24, 2013 (Android) |
| **Genre** | Endless Runner / Action |
| **Perspective** | Third-person, over-the-shoulder chase camera |
| **Input** | Touch (swipe gestures) + accelerometer tilt (mobile) |
| **Primary Objective** | Run as far as possible through procedurally assembled temple ruins, avoiding obstacles and collecting coins while being pursued by a giant Demon Monkey |
| **Core Fantasy** | You are an explorer who has stolen a cursed idol from a temple and must flee an enormous, enraged Demon Monkey through crumbling ancient pathways, cliffs, forests, mines, and waterways |
| **Target Session Length** | 1--5 minutes per run (skilled players: 10+ minutes) |
| **Target Audience** | Casual to mid-core players; all ages |
| **Monetization** | Free-to-play with optional gem purchases (IAP) |

---

## 2. Technical Foundation

### Resolution & Display

| Property | Value |
|----------|-------|
| Orientation | Portrait (vertical) |
| Aspect ratio | 9:16 (standard mobile portrait) |
| Frame rate target | 60 FPS (30 FPS minimum on older devices) |
| Rendering | 3D environment with real-time lighting and shadows |
| Camera | Third-person chase cam, positioned behind and above the runner |
| Original platforms | iOS, Android |
| Current platforms | iOS, Android, Windows Phone, Kindle Fire |

### Coordinate System

- The runner moves along a continuous **forward axis** (Z-axis) at all times.
- The path is 3 lanes wide across the **lateral axis** (X-axis): Left, Center, Right.
- The **vertical axis** (Y-axis) handles jump height and slide ducking.
- Gravity is constant at standard Earth-like acceleration; jumps follow a parabolic arc.
- The camera follows the runner with a slight lag and smooth interpolation on turns.

### Core Game Loop

```
1. Character auto-runs forward continuously at current speed
2. Poll for player input (swipe gestures and accelerometer tilt)
3. Process input:
   a. Swipe Left/Right at turn -> execute 90-degree turn
   b. Swipe Left/Right on straight -> lane change
   c. Swipe Up -> jump
   d. Swipe Down -> slide/duck
   e. Tilt device -> fine lateral movement within lane
   f. Double-tap -> activate power meter ability (if meter is full)
4. Advance runner position along path
5. Check for obstacle collisions:
   a. If collision + Shield active -> consume Shield, continue
   b. If collision + no Shield -> stumble (minor) or death (major)
6. Check for coin/gem/power-up pickups within collection radius
7. Update power meter based on coins collected
8. If power meter full and activated -> trigger current equipped power-up
9. Increment distance counter and score
10. Apply difficulty scaling (speed increase based on distance)
11. Check for death conditions:
    a. Fall off edge / into gap / into water
    b. Fail to turn at 90-degree junction
    c. Stumble twice in quick succession (Demon Monkey catches runner)
12. If dead -> show Save Me prompt
13. If saved -> resurrect at death point, continue from step 1
14. If not saved -> end run, calculate final score, show results
15. Return to step 1
```

---

## 3. Core Running Mechanics

### Auto-Run

- The character runs forward **automatically** at all times. The player never controls forward/backward movement.
- Running speed begins at a base rate and **increases continuously** with distance traveled.
- The runner never stops unless the player dies or activates certain power-ups (Boost pauses normal collision for its duration).

### Stumble System

| Event | Consequence |
|-------|-------------|
| Hit a minor obstacle (e.g., small tree root, low barrier edge) | Character **stumbles** and slows momentarily; the Demon Monkey closes distance |
| Stumble once | Demon Monkey becomes visible behind the runner, growling and swiping |
| Stumble twice in quick succession (before recovery) | Demon Monkey **catches and kills** the runner; run ends |
| Recover without stumbling for ~10 seconds | Demon Monkey falls back out of view; stumble state resets |
| Miss a turn entirely | **Instant death** -- runner runs off the edge |
| Fall into a gap / chasm / water | **Instant death** -- no stumble, immediate run end |

### Demon Monkey Behavior

- A single, large Demon Monkey pursues the runner throughout the entire run.
- The monkey is normally invisible (behind the camera) but becomes visible when the runner stumbles.
- After a stumble, the monkey appears in the background, gradually closing the gap over approximately 10 seconds.
- If the runner does not stumble again within this 10-second window, the monkey retreats and becomes invisible once more.
- A second stumble while the monkey is close triggers a death animation where the monkey grabs the runner.
- The Boost power-up propels the runner forward at high speed, pushing the monkey far behind and resetting any close-chase state.

---

## 4. Control System

### Swipe Gestures

| Gesture | Context | Action |
|---------|---------|--------|
| **Swipe Left** | Approaching a left-turn junction | Execute 90-degree left turn |
| **Swipe Right** | Approaching a right-turn junction | Execute 90-degree right turn |
| **Swipe Left** | On a straight path segment | Change one lane to the left |
| **Swipe Right** | On a straight path segment | Change one lane to the right |
| **Swipe Up** | Any ground segment | Jump (used to clear obstacles, gaps, and low walls) |
| **Swipe Down** | Any ground segment | Slide/duck (used to pass under low obstacles, branches, fire) |
| **Double-Tap** | Any time (power meter full) | Activate the filled power meter ability |

### Swipe Detection Parameters

| Parameter | Value |
|-----------|-------|
| Minimum swipe distance | ~30 pixels (device-dependent) |
| Swipe direction tolerance | 45-degree cone from primary axis |
| Swipe response time | Immediate (within 1 frame, ~16ms at 60 FPS) |
| Input buffer window | Swipes can be **queued** slightly before the action point (e.g., swiping up before reaching a gap will execute the jump at the correct moment) |
| Mid-air input | Player can swipe left/right **during a jump** to lane-change or turn while airborne |

### Tilt Controls (Accelerometer)

| Parameter | Description |
|-----------|-------------|
| Axis | Device roll (lateral tilt left/right) |
| Function | Fine lateral positioning within the 3-lane path |
| Sensitivity | Configurable in settings (Low / Medium / High) |
| Range | Full path width (left edge to right edge) |
| Use cases | Collecting coins positioned between lanes; fine-tuning position to avoid narrow obstacles |
| Disabled during | Mine cart sections and zip-line (tilt controls turning instead of lane movement) |

### Turn Mechanics

- **90-degree turns** occur at fixed junction points along the procedurally generated path.
- Turns are always either left or right (never both at once as a choice between paths).
- The player must swipe in the turn direction **before** reaching the turn point.
- There is a generous input window: the swipe can be executed approximately 0.5--1.0 seconds before the turn.
- Failing to swipe at a turn results in **instant death** -- the runner runs off the edge of the path.
- Turns can be executed **mid-jump**, allowing the player to jump at the last moment and swipe to turn while airborne.

---

## 5. Path & Lane System

### Lane Configuration

| Property | Value |
|----------|-------|
| Number of lanes | 3 (Left, Center, Right) |
| Lane width | Approximately 1 character-width each |
| Total path width | 3 character-widths across |
| Default position | Center lane |
| Lane-change speed | Near-instantaneous (~150ms animation) |
| Lane-change method | Swipe left/right on straight segments; tilt for fine positioning |

### Path Segment Types

| Segment Type | Description | Controls Available |
|-------------|-------------|-------------------|
| **Straight Path** | Standard 3-lane running surface (stone, wood, or terrain) | All controls: swipe, tilt, jump, slide |
| **Turn Junction** | 90-degree corner, left or right | Must swipe to turn; can also jump/slide |
| **Bridge / Narrow Path** | Reduced-width path over a chasm or gap | Tilt carefully to stay centered; jump over gaps |
| **Mine Cart Track** | Enclosed mine tunnel on rails | Tilt to steer on rails; duck under low bars; **cannot jump** |
| **Water Slide / Rift** | Water channel the runner slides through | Tilt to steer; duck under logs and wheels; **cannot jump** |
| **Zip-Line** | Rope/cable the runner grabs and slides along | Tilt to collect coins; **no obstacles**; brief respite section |
| **Log Bridge** | Narrow elevated log bridge | Limited lateral movement; jump over gaps |

### Procedural Path Generation

- The path is generated procedurally by chaining together pre-built segments.
- Segments are selected from a pool appropriate to the current environment zone.
- Difficulty influences segment selection: harder segments (more obstacles, tighter turns) become more frequent at greater distances.
- Transitions between environment zones occur at specific distance thresholds or at zone-boundary trigger segments.

---

## 6. Obstacle Types

### Ground Obstacles (Swipe Up to Jump Over)

| Obstacle | Description | Avoidance |
|----------|-------------|-----------|
| **Tree Roots (Small)** | Low roots crossing the path at ankle height | Jump (swipe up) or lane-change to avoid |
| **Tree Roots (Large)** | Thick raised roots blocking one or two lanes | Jump over or lane-change to clear lane |
| **Fallen Log** | A horizontal log lying across the path | Jump over |
| **Broken Bridge Gap** | A gap/hole in the bridge surface | Jump across; falling in = instant death |
| **Chasm / Cliff Edge** | Large gap between path segments | Jump across; must time correctly |
| **River / Water Hazard** | Flowing water crossing the path (in forest sections) | Jump over; falling in = instant death (swept away) |

### Overhead Obstacles (Swipe Down to Slide Under)

| Obstacle | Description | Avoidance |
|----------|-------------|-----------|
| **Low Branch** | Tree branch extending across the path at head height | Slide under (swipe down) |
| **Fire Trap (Horizontal)** | Horizontal jet of flame at head/chest height | Slide under |
| **Low Wooden Bar** | Wooden crossbeam in mine sections | Slide/duck under |
| **Low Stone Archway** | Decorative arch with low clearance | Slide under |
| **Spinning Blade (Horizontal)** | Rotating saw/blade at torso height | Slide under or jump over depending on height |

### Lane-Blocking Obstacles (Swipe Left/Right to Lane-Change)

| Obstacle | Description | Avoidance |
|----------|-------------|-----------|
| **Stone Pillar** | Vertical pillar blocking a single lane | Lane-change left or right |
| **Broken Wall Segment** | Collapsed wall debris blocking 1--2 lanes | Lane-change to open lane |
| **Fire Column** | Vertical column of flame in one lane | Lane-change to avoid |
| **Rotating Blade (Vertical)** | Spinning circular blade in one lane, moving laterally | Time lane-change or jump to avoid |

### Combination Obstacles (Multiple Inputs Required)

| Obstacle Combo | Description | Avoidance |
|----------------|-------------|-----------|
| **Root + Low Branch** | Root on ground with branch overhead in sequence | Jump over root, then immediately slide under branch |
| **Gap + Fire** | Gap in path with fire jet on the landing side | Jump the gap, slide immediately upon landing |
| **Two-Lane Block + Root** | Two lanes blocked by pillars, remaining lane has a root | Lane-change to open lane, then jump the root |
| **Narrow Gap + Overhead** | Gap to jump combined with low obstacle after landing | Jump, then slide in rapid succession |

### Environment-Specific Obstacles

| Zone | Unique Obstacles |
|------|-----------------|
| **Sky Summit** | Rope swings, water slides, mine cart tracks, forest rivers, zip-lines |
| **Blazing Sands** | Spike panels in floor, swinging hammers, rotating saw blades crossing path, narrow canyon ledges, trap walls |
| **Frozen Shadows** | Ice blocks, frozen barriers, rock barriers on skull-slide, icy chasms, falling rocks from mountainside |

---

## 7. Special Traversal Sections

### Mine Cart Section

| Property | Value |
|----------|-------|
| Entry | Automatic -- runner hops into a mine cart at a transition point |
| Controls | **Tilt** device to steer left/right on forking rail tracks |
| Jump | **Disabled** -- cannot jump while in the mine cart |
| Slide/Duck | **Enabled** -- swipe down to duck under low wooden crossbars |
| Obstacles | Low wooden bars (duck), gaps in rails (tilt to correct track), tight turns |
| Duration | Approximately 10--20 seconds per mine segment |
| Exit | Cart reaches end of track; runner hops out and resumes normal running |
| Coins | Lines of coins along the rails, collectible by tilting |

### Water Slide / Water Rift Section

| Property | Value |
|----------|-------|
| Entry | Runner slides into a water channel and begins surfing/sliding |
| Controls | **Tilt** device to steer left/right within the water channel |
| Jump | **Disabled** -- cannot jump in water |
| Slide/Duck | **Enabled** -- swipe down to duck under low logs, wheels, and overhanging obstacles |
| Obstacles | Floating logs (duck), water wheels (duck), narrow channel splits |
| Speed | Slightly faster than normal running speed |
| Duration | Approximately 10--15 seconds |
| Exit | Water channel ends; runner emerges and resumes running |

### Zip-Line Section

| Property | Value |
|----------|-------|
| Entry | Runner grabs onto a rope/cable at a transition ledge |
| Controls | **Tilt** device to swing left/right for coin collection |
| Jump | **Disabled** |
| Slide/Duck | **Disabled** |
| Obstacles | **None** -- zip-line sections are obstacle-free, serving as a brief respite |
| Coins | Coins arranged in arcs and patterns along the zip-line path |
| Duration | Approximately 5--10 seconds |
| Exit | Runner releases at the end and lands on the next path segment |

### Rope Swing Section (Sky Summit)

| Property | Value |
|----------|-------|
| Entry | Runner reaches a gap between floating islands |
| Mechanic | Automated -- runner grabs rope and swings across |
| Player Input | Tilt to adjust landing position; time not critical |
| Duration | ~3--5 seconds |

---

## 8. Power-Up System

### Power Meter Mechanic

| Property | Value |
|----------|-------|
| Location | Top-right corner of HUD (vertical bar) |
| Fill method | Collecting coins fills the meter incrementally |
| Visual indicator | Bar fills from bottom to top; **glows green** when full |
| Activation | **Double-tap** anywhere on screen when meter is green/full |
| Effect | Triggers the currently active power-up |
| Post-activation | Meter empties and begins refilling with subsequent coin collection |
| Upgrade | "Power Meter" ability increases the fill rate |

### Collectible Power-Ups (Picked Up During Run)

These appear as floating icons on the path and activate **immediately** upon collection (no meter required).

| Power-Up | Icon | Effect | Base Duration |
|----------|------|--------|---------------|
| **Shield** | Blue shield icon | Protects from **one** obstacle hit. After absorbing one collision, the shield breaks. Does **not** protect from falling off edges, missing turns, or falling into chasms/water. | Single-use (one hit) OR timed duration if upgraded |
| **Boost** | Red rocket/arrow icon | Propels the runner forward at extreme speed with **temporary invulnerability**. All obstacles are bypassed. Coins along the path are auto-collected. Pushes Demon Monkey far behind. | ~5 seconds base (upgradeable via Boost Distance) |
| **Coin Magnet** | Yellow magnet icon | Automatically attracts and collects all coins within a wide radius regardless of lane position. No need to tilt or lane-change for coins. | ~5 seconds base (upgradeable via Coin Magnet ability) |
| **Score Bonus** | Green star/plus icon | Instantly adds a flat bonus of **500 base points** to the current score. This bonus is then multiplied by the player's current Score Multiplier. | Instant (no duration) |

### Power Meter Activated Abilities

When the power meter is filled and the player double-taps, one of the following activates depending on the player's equipped/unlocked ability:

| Ability | Unlock Condition | Effect |
|---------|-----------------|--------|
| **Shield** | Default (Level 1) | Activates a timed shield that absorbs multiple hits for its duration |
| **Boost** | Default (available early) | Triggers a speed boost with invulnerability |
| **Coin Magnet** | Default (available early) | Activates coin magnet for its duration |
| **Coin Bonus** | Unlocked at Level 5 | Instantly awards 50 coins (100 when powered up) |
| **Gem Bonus** | Unlocked at Level 13 | Awards bonus gems upon activation |
| **Bolt** | Unlocked via progression | Combines increased speed, invulnerability, and coin magnet simultaneously |

---

## 9. Coin & Gem Economy

### Coin Types

| Coin Type | Color | Value | Appearance Distance |
|-----------|-------|-------|-------------------|
| **Standard Coin** | Yellow/Gold | 1 coin | 0 m (available from start) |
| **Double Coin** | Red | 2 coins | ~1,000 m (requires Coin Value upgrade Level 1+) |
| **Triple Coin** | Blue | 3 coins | ~2,500 m (requires Coin Value upgrade Level 2+) |

### Coin Arrangement Patterns

| Pattern | Composition | Total Value |
|---------|------------|-------------|
| Standard Yellow Line | 25 yellow coins in a row | 25 coins |
| Yellow-Red Mix Line | 3 yellow + 2 red, repeated 5 times | 35 coins |
| Yellow-Red-Blue Mix Line | 2 blue + 2 red + 1 yellow, repeated 5 times | 55 coins |
| Arc Pattern (zip-line) | Curved arc of 10--15 coins | 10--45 coins (varies by type) |
| Grid Pattern (wide sections) | Coins spread across 3 lanes | Varies |

### Coin Uses

| Use | Cost Range |
|-----|-----------|
| Ability upgrades | 250 -- 50,000 coins per level |
| Character unlocks | 5,000 -- 25,000 coins |
| Head Start purchase | 2,500 coins (base); 2,000 coins (fully upgraded) |
| Mega Head Start purchase | 10,000 coins (base); 7,500 coins (fully upgraded) |

### Gems (Premium Currency)

| Property | Value |
|----------|-------|
| Appearance | Green diamond-shaped crystals |
| Path spawn | Rare; appear in power-up spawn locations along the path |
| Spawn rate | Very low (~1--3 per average run); increased by Pickup Spawn upgrade |
| Collection | Must jump to collect (always placed at jump height) |
| Earn methods | Collect during runs, level-up rewards, objective completion rewards, IAP |

### Gem Uses

| Use | Cost |
|-----|------|
| Save Me (1st use per run) | 1 gem |
| Save Me (2nd use per run) | 2 gems |
| Save Me (3rd use per run) | 4 gems |
| Save Me (4th use per run) | 8 gems |
| Save Me (nth use per run) | 2^(n-1) gems (doubling pattern) |
| Premium character unlocks | ~25--60 gems per character |
| Power-up enhancement | Varies |

---

## 10. Character System

### Default Character

| Character | Description | Cost | Special Ability |
|-----------|-------------|------|-----------------|
| **Guy Dangerous** | Default explorer; male adventurer with brown hat and jacket | Free (starting character) | Shield power-up |

### Unlockable Characters (Coins)

| Character | Description | Unlock Cost | Associated Power-Up |
|-----------|-------------|-------------|-------------------|
| **Scarlett Fox** | Female escape artist with red outfit | Free (originally 5,000 coins; made free in April 2022 update) | Boost |
| **Barry Bones** | Skeletal/undead character | 15,000 coins | Coin Bonus |
| **Karma Lee** | Female martial artist in traditional garb | 25,000 coins | Score Bonus |
| **Montana Smith** | Male adventurer with cowboy hat | 25,000 coins | Boost |
| **Francisco Montoya** | Spanish conquistador-themed character | 25,000 coins | Shield |
| **Zack Wonder** | Athletic male character | 25,000 coins | Coin Magnet |
| **Maria Selva** | Female explorer with jungle attire | 25,000 coins | Shield |
| **Rahi Raaja** | Male character with South Asian-inspired attire | 25,000 coins | Score Bonus |
| **Nidhi Nirmal** | Female character with South Asian-inspired attire | 25,000 coins | Coin Magnet |

### Token-Based Characters

| Character | Description | Unlock Cost |
|-----------|-------------|-------------|
| **Cleopatra** | Egyptian queen themed | 5 character tokens |
| **Imhotep** | Egyptian priest themed | 10 character tokens |

### Premium / Gem Characters

| Character | Description | Unlock Cost |
|-----------|-------------|-------------|
| **Anubis** | Egyptian god themed | Gems |
| **Sigur Frostbeard** | Viking/Norse themed (Frozen Shadows) | Gems |
| **Freya Coldheart** | Norse warrior female (Frozen Shadows) | Gems |
| **Santa Claus** | Holiday seasonal character | Gems (limited-time) |
| **Mrs. Claus** | Holiday seasonal character | Gems (limited-time) |

### Real-Money Premium Characters

| Character | Description | Unlock Method |
|-----------|-------------|---------------|
| **Usain Bolt** | Olympic sprinter; multiple outfit variants | Real money (IAP only) |
| **Bruce Lee** | Martial artist; jumpsuit and nunchucks | Real money (IAP only) |

### Character Mechanics

- All characters have **identical gameplay stats** -- no character runs faster or jumps higher than another.
- Each character is associated with a default power-up type, but this is cosmetic/thematic -- all power-ups are available to all characters.
- Characters have alternate outfits/costumes purchasable with coins or gems.
- Character selection is made in the main menu before starting a run.

---

## 11. Objective / Mission System

### System Overview

| Property | Value |
|----------|-------|
| Active objectives | **3 at a time** displayed in the objectives panel |
| Completion tracking | Some complete in a single run; others track across multiple runs (lifetime) |
| Reward per objective | Score Multiplier +1 AND/OR coins/gems |
| Level-up trigger | Completing a set number of objectives advances the player's level |
| Level-up rewards | Coins, gems, and occasionally unlocked abilities/power-ups |

### Objective Categories

| Category | Example Objectives |
|----------|-------------------|
| **Distance (Single Run)** | "Run 500m", "Run 1,000m", "Run 5,000m", "Run 10,000m" |
| **Distance (Lifetime)** | "100,000 lifetime meters", "1,000,000 lifetime meters", "10,000,000 lifetime meters" |
| **Coins (Single Run)** | "Collect 100 coins", "Collect 250 coins", "Collect 500 coins", "Collect 1,000 coins", "Collect 2,500 coins", "Collect 5,000 coins" |
| **Coins (Lifetime)** | "100,000 lifetime coins", "500,000 lifetime coins", "1,000,000 lifetime coins" |
| **Score (Single Run)** | "Score 25,000 points", "Score 50,000 points", "Score 100,000 points", "Score 250,000 points", "Score 500,000 points", "Score 1,000,000 points", "Score 2,500,000 points", "Score 5,000,000 points", "Score 10,000,000 points" |
| **No-Coin Runs** | "Run 250m collecting no coins", "Run 500m collecting no coins", "Run 1,000m collecting no coins" |
| **No-Trip Runs** | "Run 2,500m without tripping", "Run 5,000m without tripping" |
| **Gem Collection** | "Find a gem", "Collect 2 gems in one run", "Collect 5 gems in one run" |
| **Save Me Usage** | "Use a Save Me", "Use Save Me twice in one run", "Use Save Me 9 times (lifetime)" |
| **Head Start Usage** | "Use a Head Start", "Use 5 Head Starts" |
| **Power-Up Collection** | "Collect 20 bonus items", "Unlock a 2nd powerup" |
| **Score Without Power-Ups** | "Score 1,000,000 without powerups" |

### Complete Original Objectives List (44 Base Objectives)

| # | Name | Requirement |
|---|------|-------------|
| 1 | Novice Runner | Run 500 meters |
| 2 | Pocket Change | Collect 100 coins |
| 3 | Adventurer | Score 25,000 points |
| 4 | Sprinter | Run 1,000 meters |
| 5 | Piggy Bank | Collect 250 coins |
| 6 | Treasure Hunter | Score 50,000 points |
| 7 | Stingy | Run 250m collecting no coins |
| 8 | High Roller | Score 100,000 points |
| 9 | Miser Run | Run 500m collecting no coins |
| 10 | Gem Collector | Find a gem |
| 11 | Lump Sum | Collect 500 coins |
| 12 | Cheat Death | Use a Save Me |
| 13 | Power Collector | Unlock a 2nd powerup |
| 14 | Athlete | Run 2,500 meters |
| 15 | Payday | Collect 750 coins |
| 16 | Allergic to Gold | Run 1,000m collecting no coins |
| 17 | 1/4 Million Club | Score 250,000 points |
| 18 | Lucky Strike | Collect 2 gems in one run |
| 19 | Couch to 5k | Collect 5,000 coins |
| 20 | 5k Runner | Run 5,000 meters |
| 21 | Steady Feet | Run 2,500m without tripping |
| 22 | 1/2 Million Club | Score 500,000 points |
| 23 | Head Start | Use a Head Start |
| 24 | Double Resurrection | Use Save Me twice in one run |
| 25 | Bonus Items | Collect 20 bonus items |
| 26 | Money Bags | Collect 1,000 coins |
| 27 | NoTripRunner | Run 5,000m without tripping |
| 28 | 9 Lives | Use Save Me 9 times (lifetime) |
| 29 | Marathoner | 100,000 lifetime meters |
| 30 | 10k Runner | Run 10,000 meters |
| 31 | Money Bin | Collect 2,500 coins |
| 32 | Million Club | Score 1,000,000 points |
| 33 | Minor Miner | 100,000 lifetime coins |
| 34 | Fort Knox | Collect 5,000 coins |
| 35 | 2.5 Million Club | Score 2,500,000 points |
| 36 | The Spartan | Score 1,000,000 without powerups |
| 37 | 5 Million Club | Score 5,000,000 points |
| 38 | Jackpot | Collect 5 gems in one run |
| 39 | Speedy Start | Use 5 Head Starts |
| 40 | 10 Million Club | Score 10,000,000 points |
| 41 | Circumnavigator | 1,000,000 lifetime meters |
| 42 | Gold Miner | 500,000 lifetime coins |
| 43 | Midas Touch | 1,000,000 lifetime coins |
| 44 | Infinirunner | 10,000,000 lifetime meters |

### Level-Up Rewards

| Level | Notable Reward |
|-------|---------------|
| Level 2+ | Score Multiplier +1 per completed objective |
| Level 5 | Unlocks **Coin Bonus** power-up (awards 50 coins, 100 when powered) |
| Level 13 | Unlocks **Gem Bonus** ability |
| Various | Coins (amounts vary: 250, 500, 1000, 2500) |
| Various | Gems (amounts vary: 1, 2, 5) |
| Various | Free power-up activations |

---

## 12. Difficulty Scaling

### Speed Progression

| Property | Behavior |
|----------|----------|
| Base running speed | Moderate pace at the start of each run |
| Speed increase | Continuous, gradual acceleration based on distance traveled |
| Speed curve | Logarithmic -- fast initial increase, then diminishing increments |
| Practical max speed | Reached at approximately 5,000--10,000 meters; speed plateaus to remain playable |
| Stumble slowdown | Hitting a minor obstacle slows the runner temporarily, then speed resumes |
| Boost override | During Boost, speed is set to maximum regardless of current distance |

### Obstacle Density Scaling

| Distance Range | Obstacle Frequency | Obstacle Complexity |
|----------------|-------------------|-------------------|
| 0 -- 500 m | Low; simple single obstacles | Single-type obstacles with generous spacing |
| 500 -- 1,500 m | Moderate; obstacles appear more frequently | Introduction of combination obstacles |
| 1,500 -- 3,000 m | High; tight sequences of obstacles | Multi-input combos (jump + slide, lane-change + jump) |
| 3,000 -- 5,000 m | Very high; minimal safe gaps between obstacles | Rapid-fire sequences requiring instant reaction |
| 5,000+ m | Maximum density; near-continuous obstacle flow | All obstacle types in rapid combination; minimal margin for error |

### Coin Progression

| Distance Threshold | Coin Types Available |
|-------------------|---------------------|
| 0 m | Yellow coins only (1x value) |
| ~1,000 m (with Coin Value Level 1) | Yellow + Red coins (2x value) |
| ~2,500 m (with Coin Value Level 2) | Yellow + Red + Blue coins (3x value) |

### Path Complexity Scaling

| Distance Range | Path Characteristics |
|----------------|---------------------|
| 0 -- 1,000 m | Long straight segments; turns are well-telegraphed; wide paths |
| 1,000 -- 3,000 m | Shorter segments between turns; introduction of special sections (mine cart, water) |
| 3,000 -- 5,000 m | Frequent turns; multiple special sections; narrow bridges |
| 5,000+ m | Very short segments; rapid turn sequences; maximum environmental variety |

---

## 13. Environment Zones & Maps

### Sky Summit (Default / Original Map)

| Property | Value |
|----------|-------|
| Release | January 2013 (launch map) |
| Theme | Floating islands in the sky; ancient Asian-style temple ruins |
| Visual palette | Lush greens, golden temple stone, blue sky, white clouds |
| Unique features | Rope swings between islands, water slides, mine cart tunnels, zip-lines, forest paths |

#### Sky Summit Sub-Zones

| Zone | Description | Unique Mechanics |
|------|-------------|-----------------|
| **Temple Path** | Starting area; stone temple corridors and platforms | Standard 3-lane running with pillars, fire traps, roots |
| **Forest / Woods** | Wooded area with natural terrain; railings on both sides | Rivers to jump over, tree roots, low branches, natural gaps |
| **Mine Cart Tunnel** | Dark mine interior with rail tracks | Mine cart riding; tilt to steer; duck under bars; no jumping |
| **Water Rift / Aqueduct** | Water channel / slide section | Water surfing; tilt to steer; duck under logs/wheels; no jumping |
| **Zip-Line** | Cable connecting elevated platforms over chasms | Tilt to collect coins; no obstacles; brief rest |
| **Log Bridge** | Narrow elevated wooden bridge | Limited lateral movement; jump gaps in the bridge |

### Blazing Sands

| Property | Value |
|----------|-------|
| Release | June 2016 |
| Theme | Desert canyon; ancient Egyptian-style ruins; Hall of Kings |
| Visual palette | Sandy yellows, warm oranges, red rock, golden artifacts |
| Unique features | Spike floor panels, swinging hammers, rotating saw blades, narrow canyon ledges, trap walls |

#### Blazing Sands Sub-Zones

| Zone | Description | Unique Mechanics |
|------|-------------|-----------------|
| **Canyon Path** | Main running path through desert canyons | Standard obstacles plus sand-themed hazards |
| **Hall of Kings** | Interior temple hall with Egyptian decorations | Spike panels in the floor (activated/deactivated by buttons); trap walls |
| **Canyon Cliffs** | Narrow ledges along canyon walls | Very narrow path; precision tilting required; long drops |

### Frozen Shadows

| Property | Value |
|----------|-------|
| Release | December 2015 |
| Theme | Icy tundra; frozen caves; snowy mountain passes |
| Visual palette | Icy blues, stark whites, dark cave interiors, snow-covered stone |
| Unique features | Ice blocks, frozen barriers, demon skull slide, falling rocks, icy chasms |

#### Frozen Shadows Sub-Zones

| Zone | Description | Unique Mechanics |
|------|-------------|-----------------|
| **Frozen Path** | Snow-covered main running path | Ice blocks, frozen barriers, slippery visuals |
| **Ice Cave** | Dark cave interior with ice formations | Narrow passages, ice shards, icicle obstacles |
| **Demon Skull Slide** | Frozen river section; character rides in a large demon monkey skull like a snowboard | Tilt to steer; avoid rock barriers and ice blocks; faster than normal speed; cannot jump |
| **Mountain Ravine** | Narrow ledges along icy ravine edges | Falling rocks from mountainside; precision movement required |

### Zone Transition Mechanics

| Property | Value |
|----------|-------|
| Transition trigger | Distance-based thresholds or fixed segment boundaries |
| Transition visual | Camera sweep / brief cinematic showing environment change |
| Starting zone | Varies by season (e.g., Sky Summit default; Frozen Shadows in winter; Blazing Sands in summer) |
| Zone rotation | Zones cycle as the player progresses through the run |
| Player choice | Some updates allow players to select a starting map from the menu |

---

## 14. Resurrection / Save Me Mechanic

### Save Me System

| Property | Value |
|----------|-------|
| Trigger | Activated after death; prompt appears immediately on the death screen |
| Effect | Resurrects the runner at the exact point of death; run continues |
| Currency | Gems (green diamonds) |
| Cost escalation | Doubles with each successive use within the same run |
| Free option | First Save Me can be obtained by watching a video ad (if internet-connected) |
| Upgrade | "Save Me" ability reduces gem cost at each level |
| Minimum cost | 1 gem (even with maximum upgrade) |
| Time limit | Player has approximately 5 seconds to decide; countdown timer shown |

### Save Me Cost Table (Per Run, Base Cost)

| Use # | Gem Cost (Base) | Gem Cost (Fully Upgraded Save Me Ability) |
|-------|-----------------|-------------------------------------------|
| 1st | 1 gem | 1 gem (minimum) |
| 2nd | 2 gems | 1 gem |
| 3rd | 4 gems | 2 gems |
| 4th | 8 gems | 4 gems |
| 5th | 16 gems | 8 gems |
| nth | 2^(n-1) gems | Reduced by upgrade level |

### Save Me Mechanics

- Cost resets at the start of each new run (always begins at 1 gem base).
- After resurrection, the Demon Monkey is temporarily pushed back (similar to Boost effect).
- The runner resumes at the same speed they were traveling at before death.
- All coins, score, and distance accumulated before death are preserved.
- The power meter retains its current fill level.

---

## 15. Upgrade System (Abilities)

### Ability Upgrade Table

Each ability has **5 upgrade levels**. The cost in coins for each level is listed below.

| Ability | Effect | Lv 1 | Lv 2 | Lv 3 | Lv 4 | Lv 5 | Total Cost |
|---------|--------|-------|-------|-------|-------|-------|------------|
| **Coin Value** | Causes higher-value coins (red, blue) to appear at shorter distances | 250 | 1,000 | 2,500 | 5,000 | 10,000 | 18,750 |
| **Shield Duration** | Extends the duration of the Shield power-up | 250 | 1,000 | 2,500 | 5,000 | 10,000 | 18,750 |
| **Coin Magnet** | Extends the duration of the Coin Magnet power-up | 1,000 | 2,500 | 5,000 | 10,000 | 25,000 | 43,500 |
| **Boost Distance** | Extends the distance/duration of the Boost power-up by ~50m per level | 1,000 | 2,500 | 5,000 | 10,000 | 25,000 | 43,500 |
| **Pickup Spawn** | Increases the frequency of power-up and gem spawns during runs | 2,500 | 5,000 | 10,000 | 25,000 | 50,000 | 92,500 |
| **Power Meter** | Increases the speed at which the power meter fills from coin collection | 2,500 | 5,000 | 10,000 | 25,000 | 50,000 | 92,500 |
| **Save Me** | Reduces the gem cost of Save Me resurrections | 5,000 | 10,000 | 15,000 | 25,000 | 50,000 | 105,000 |
| **Head Start** | Reduces the coin cost of purchasing Head Starts before a run | 5,000 | 10,000 | 15,000 | 25,000 | 50,000 | 105,000 |
| **Score Multiplier** | Increases the passive score multiplier added per meter run | 5,000 | 10,000 | 15,000 | 25,000 | 50,000 | 105,000 |

**Total cost to fully upgrade all abilities: 624,500 coins**

### Ability Detail Notes

- **Coin Value**: At Level 0, all coins are yellow (1x). Level 1 introduces red coins (2x) past ~1,500m. Level 2 introduces blue coins (3x) past ~3,000m. Higher levels reduce the distance threshold for higher-value coins.
- **Shield Duration**: Base shield is single-use (one hit). Upgrading adds timed duration so the shield lasts several seconds and can absorb multiple hits.
- **Coin Magnet**: Base duration ~5 seconds. Each level adds approximately 25% more duration.
- **Boost Distance**: Base distance ~250m. Each level adds ~50m to the boost travel distance.
- **Pickup Spawn**: Affects both power-up and gem spawn rates. Higher levels noticeably increase gem frequency.
- **Power Meter**: Base fill rate requires collecting many coins. Each level makes the meter fill faster, allowing more frequent power-up activations.
- **Save Me**: Each level reduces the gem cost multiplier. Does not reduce below 1 gem minimum.
- **Head Start**: Base Head Start costs 2,500 coins (1,000m boost). Fully upgraded: 2,000 coins. Mega Head Start base: 10,000 coins (2,500m boost). Fully upgraded: 7,500 coins.
- **Score Multiplier**: Adds a flat bonus to the per-meter score multiplier. Stacks with multiplier earned from completing objectives.

---

## 16. Scoring System

### Score Calculation Formula

```
Final Score = (Distance Points + Coin Points + Bonus Points) x Score Multiplier

Where:
  Distance Points = Total meters run x 1
  Coin Points     = Total coins collected x 5
  Bonus Points    = (Floor(Total Coins / 100)) x 600  [bonus for every 100 coins]
                  + (Score Bonus power-up activations x 500)
  Score Multiplier = Base Multiplier (starts at 1) 
                   + Objectives Completed (each adds +1)
                   + Score Multiplier Ability Upgrade Bonus
```

### Score Multiplier Progression

| Source | Multiplier Increase |
|--------|-------------------|
| Starting value | 1x |
| Each completed objective | +1x |
| Score Multiplier ability (per level) | +1x per level (up to +5x at Level 5) |
| Typical mid-game multiplier | 15x -- 25x |
| Theoretical maximum | 50x+ (after completing all objectives + max upgrades) |

### Point Values per Component

| Component | Base Points | With 10x Multiplier | With 20x Multiplier |
|-----------|-------------|--------------------|--------------------|
| 1 meter run | 1 | 10 | 20 |
| 1 yellow coin (value: 1) | 5 | 50 | 100 |
| 1 red coin (value: 2) | 10 | 100 | 200 |
| 1 blue coin (value: 3) | 15 | 150 | 300 |
| Every 100th coin bonus | 600 | 6,000 | 12,000 |
| Score Bonus power-up | 500 | 5,000 | 10,000 |

### Head Start Scoring

| Head Start Type | Distance Boost | Coin Cost (Base) | Coin Cost (Fully Upgraded) |
|----------------|----------------|------------------|--------------------------|
| **Head Start** | 1,000 m | 2,500 coins | 2,000 coins |
| **Mega Head Start** | 2,500 m | 10,000 coins | 7,500 coins |

- Head Start distance counts toward the score.
- All coins collected during the Head Start boost are counted normally.
- Head Start essentially "skips" the easy early section and begins the run at a higher speed with more obstacles.

---

## 17. UI Layout & HUD

### In-Run HUD

```
+-------------------------------------------------------+
|  [Score: 12,450]              [Coin: 87]  [Power Bar]  |
|  [Distance: 1,234m]          [Gem: 3]     [||||||||--] |
|                                                         |
|                                                         |
|                    [3D GAME VIEW]                        |
|                                                         |
|              Runner in center of screen                  |
|              Path extending ahead                        |
|              Demon Monkey behind (if active)             |
|                                                         |
|  [Pause Button - Top Left]                              |
+-------------------------------------------------------+
```

| HUD Element | Position | Description |
|-------------|----------|-------------|
| **Score Counter** | Top-left | Current score; updates in real-time as points accumulate |
| **Distance Counter** | Top-left (below score) | Current distance in meters; counts up continuously |
| **Coin Counter** | Top-right | Current coins collected this run; numeric display with coin icon |
| **Gem Counter** | Top-right (near coins) | Current gems held (total, not just this run); diamond icon |
| **Power Meter Bar** | Top-right (vertical bar) | Fills as coins are collected; glows green when full and ready to activate |
| **Pause Button** | Top-left corner | Tapping pauses the game and shows pause menu |
| **Objective Tracker** | Shown briefly at run start | Displays current 3 active objectives |

### Main Menu Screen

| Element | Position | Description |
|---------|----------|-------------|
| **Play Button** | Center | Large "Run" or "Play" button to start a run |
| **Character Display** | Center (behind Play) | 3D model of selected character on temple background |
| **Coin Balance** | Top bar | Total coins owned |
| **Gem Balance** | Top bar | Total gems owned |
| **Objectives Button** | Left side | Opens objectives panel showing 3 current missions |
| **Store / Upgrades Button** | Right side | Opens the upgrade shop for abilities |
| **Characters Button** | Bottom | Opens character selection / unlock screen |
| **Settings Button** | Top corner | Audio, controls sensitivity, notifications |
| **Leaderboards Button** | Bottom | Opens Game Center / Google Play Games leaderboard |
| **Head Start Option** | Below Play | Option to purchase Head Start / Mega Head Start before run |

### Death / Game Over Screen

| Element | Description |
|---------|-------------|
| **Save Me Prompt** | Large animated button showing gem icon and cost; countdown timer (~5 seconds) |
| **Watch Ad Button** | Alternative to gems for first resurrection (if ad available) |
| **Score Summary** | Final score, distance, coins collected |
| **Objectives Progress** | Shows completion status of any objectives advanced during the run |
| **High Score Notification** | Displayed if the run set a new personal best |
| **Share Button** | Share score to social media |
| **Play Again Button** | Immediately start a new run |
| **Main Menu Button** | Return to main menu |

### Pause Menu

| Element | Description |
|---------|-------------|
| **Resume Button** | Continue the run |
| **Quit Button** | End the run (score is forfeited) |
| **Music Toggle** | On/Off for background music |
| **SFX Toggle** | On/Off for sound effects |

---

## 18. Audio Design

### Music

| Track | Context | Style |
|-------|---------|-------|
| **Main Menu Theme** | Main menu / character select | Mysterious, ambient orchestral with exotic percussion; evokes ancient temple atmosphere |
| **Running Theme (Sky Summit)** | During gameplay in Sky Summit zones | Up-tempo percussive track with tribal drums, string accents, and building intensity; tempo increases subtly with speed |
| **Running Theme (Blazing Sands)** | During gameplay in desert zones | Middle-Eastern influenced melody with oud/sitar-like instruments, rhythmic drums, and tension-building motifs |
| **Running Theme (Frozen Shadows)** | During gameplay in ice zones | Atmospheric, cold-sounding synths mixed with Nordic/folk-inspired strings and heavy drum beats |
| **Boost/Power-Up Jingle** | During active Boost | Brief triumphant fanfare that plays over the running theme |
| **Death Sting** | On player death | Short dramatic sting with low brass/percussion hit |

### Sound Effects

| Sound | Trigger | Description |
|-------|---------|-------------|
| **Footsteps** | Continuous during run | Rhythmic footstep sounds matching run speed; varies by surface (stone, wood, dirt, ice, water) |
| **Coin Pickup** | Collecting a coin | Bright metallic "ting" sound; pitch varies slightly per coin for variety |
| **Gem Pickup** | Collecting a gem | Sparkly, high-pitched crystalline chime (more prominent than coin sound) |
| **Power-Up Pickup** | Collecting a path power-up | Whoosh/activation sound specific to each power-up type |
| **Power Meter Full** | Meter reaches maximum | Ascending chime indicating readiness; accompanied by green glow |
| **Power Meter Activate** | Double-tap to activate | Explosive activation sound with brief crescendo |
| **Shield Activate** | Shield power-up begins | Energy hum / forcefield sound |
| **Shield Break** | Shield absorbs a hit | Shattering glass/energy burst sound |
| **Boost Activate** | Boost begins | Whooshing rocket/jet sound that sustains for duration |
| **Coin Magnet Activate** | Magnet begins | Magnetic hum; coins produce rapid "ting-ting-ting" as they fly toward runner |
| **Jump** | Swipe up / jump | Brief wind/swoosh sound |
| **Slide** | Swipe down / slide | Sliding/scraping sound |
| **Lane Change** | Swipe left/right on straight | Quick lateral swoosh |
| **Turn** | 90-degree turn execution | Sharp directional whoosh with brief footstep scuff |
| **Stumble** | Hit minor obstacle | Tripping/impact thud; character grunt |
| **Demon Monkey Growl** | Monkey closes in after stumble | Deep, menacing growl/roar that intensifies the closer the monkey gets |
| **Demon Monkey Attack** | Monkey catches runner (double stumble) | Loud roar combined with impact sound |
| **Death (Fall)** | Falling off edge / into gap | Descending pitch wind sound / scream |
| **Death (Water)** | Falling into water/river | Splash sound |
| **Death (Fire)** | Running into fire obstacle | Sizzle/flame burst |
| **Mine Cart Enter** | Transitioning to mine cart | Metallic clank of cart engaging rails |
| **Mine Cart Ride** | During mine cart section | Rhythmic clacking of wheels on rail tracks |
| **Water Slide Enter** | Entering water section | Splash/water flowing |
| **Water Slide Ride** | During water section | Continuous rushing water sound |
| **Zip-Line Grab** | Grabbing the zip-line | Metallic clang/grab sound |
| **Zip-Line Ride** | Sliding on zip-line | High-pitched metallic zipping/sliding sound |
| **Save Me Prompt** | Death screen appears | Alert/notification chime with urgency |
| **Resurrection** | Save Me activated | Triumphant revival sound; magical shimmer |
| **UI Button Press** | Any menu button tap | Soft click/tap sound |
| **Objective Complete** | An objective is fulfilled | Achievement fanfare; short celebratory jingle |
| **Level Up** | Player reaches new level | Extended celebratory fanfare with ascending notes |

### Audio Settings

| Setting | Options | Default |
|---------|---------|---------|
| Music Volume | On / Off | On |
| Sound Effects Volume | On / Off | On |
| Note | Volume is binary (on/off) in the original game, not a slider | -- |

---

## Appendix A: Key Constants Summary

| Constant | Value |
|----------|-------|
| Number of lanes | 3 |
| Turn angle | 90 degrees |
| Save Me base cost | 1 gem |
| Save Me cost doubling | 2^(n-1) per use in a run |
| Coin point value | 5 base points per coin |
| Distance point value | 1 base point per meter |
| 100-coin bonus | 600 base points |
| Score Bonus power-up value | 500 base points |
| Starting Score Multiplier | 1x |
| Multiplier per objective | +1x |
| Head Start distance | 1,000 m |
| Mega Head Start distance | 2,500 m |
| Head Start base cost | 2,500 coins |
| Mega Head Start base cost | 10,000 coins |
| Total ability upgrade cost | 624,500 coins |
| Ability upgrade levels | 5 per ability |
| Number of abilities | 9 |
| Active objectives at a time | 3 |
| Original objective count | 44 |
| Yellow coin value | 1 |
| Red coin value | 2 |
| Blue coin value | 3 |
| Red coin appearance | ~1,000--1,500 m (with Coin Value upgrade) |
| Blue coin appearance | ~2,500--3,000 m (with Coin Value upgrade) |
| Demon Monkey recovery window | ~10 seconds after stumble |
| Characters (original roster) | ~8 coin-purchasable + default |
