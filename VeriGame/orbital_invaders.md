# orbital_invaders - Orbital Invaders

## 1. Game Overview

- **Prototype Anchor**: Space Invaders (Taito, 1978 arcade)
- **Genre Family**: Fixed Shooter / Shoot 'em Up
- **Core Fantasy**: Defend Earth as the lone cannon against relentless waves of descending alien invaders. Whittle down the 5x11 formation while managing four eroding bunkers, dodging three distinct alien bullet types, and sniping the mystery UFO for bonus points.
- **Camera / Presentation**: 2D fixed-screen, vertical orientation (portrait). All action takes place on a single non-scrolling playfield.
- **Target Session Length**: Endless -- the game loops through progressively harder waves until all lives are lost.
- **Skill Curve**: Simple two-button controls (move, fire) learned in seconds; mastery emerges from understanding alien speed acceleration, shot-count-based UFO scoring, and bullet pattern exploitation.

---

## 2. Technical Foundation

### 2.1 Display Specifications

| Parameter | Value |
|---|---|
| Native Resolution | 224 wide x 256 tall (portrait orientation) |
| Pixel Format | 1-bit monochrome (on/off per pixel) |
| Refresh Rate | 60 Hz (NTSC-derived vertical sync) |
| Color Method | Colored gel overlays on monochrome CRT |
| Aspect Ratio | ~7:8 (pixels are slightly taller than wide due to CRT stretch on rotated monitor) |

### 2.2 Color Overlay Regions (from top of screen, Y=255 to Y=0)

| Y Range | Overlay Color | Content |
|---|---|---|
| 256-240 | White | Score displays (SCORE<1>, HI-SCORE, SCORE<2>) |
| 240-184 | Red | Top portion of playfield; UFO flight path |
| 184-33  | White | Main playfield (alien formation, bunkers) |
| 32-25   | Green | Bunker row and player cannon area |
| 24-0    | Green | Lives display, credit count, baseline |

Note: Some cabinet variants used green overlays extending higher into the playfield. The canonical Midway upright used the region map above.

### 2.3 Game Loop Architecture

The game runs on an Intel 8080 CPU at 1.9968 MHz with a dual-interrupt display system:

| Interrupt | Trigger | Purpose |
|---|---|---|
| RST 1 (0x0008) | Mid-screen (scanline 96) | Process game objects whose Y upper bit = 0 |
| RST 2 (0x0010) | Vertical blank (scanline 224) | Process game objects whose Y upper bit = 1 |

**Update Order per Frame:**
1. Read input hardware ports
2. Update exactly ONE alien position (cycle through all living aliens sequentially)
3. Process player shot movement (4 px/interrupt)
4. Process alien shots movement (step every 3 frames)
5. Run collision checks (sprite-to-sprite XOR overlap)
6. Update UFO position if active
7. Evaluate game-over conditions
8. Draw changed sprites to video RAM

**Critical Timing:** Only one alien is repositioned per display frame. With 55 aliens alive, it takes 55 frames (~917 ms) to complete one full formation step. With 1 alien alive, each step completes in 1 frame (~16.7 ms), producing the iconic speed acceleration.

---

## 3. Alien Formation and Movement

### 3.1 Grid Layout

The alien formation is a grid of **5 rows x 11 columns = 55 aliens total**.

```
Row 4 (top):    [S] [S] [S] [S] [S] [S] [S] [S] [S] [S] [S]    <- Squid (Small)
Row 3:          [C] [C] [C] [C] [C] [C] [C] [C] [C] [C] [C]    <- Crab (Medium)
Row 2:          [C] [C] [C] [C] [C] [C] [C] [C] [C] [C] [C]    <- Crab (Medium)
Row 1:          [O] [O] [O] [O] [O] [O] [O] [O] [O] [O] [O]    <- Octopus (Large)
Row 0 (bottom): [O] [O] [O] [O] [O] [O] [O] [O] [O] [O] [O]    <- Octopus (Large)
```

Rows are numbered 0 (bottom) to 4 (top). Columns are numbered 0 (left) to 10 (right).

### 3.2 Spacing and Positioning

| Parameter | Value |
|---|---|
| Alien cell size | 16 x 16 pixels (bounding box per alien slot) |
| Horizontal gap between alien centers | 16 pixels |
| Vertical gap between alien centers | 16 pixels |
| Total formation width | 11 x 16 = 176 pixels |
| Total formation height | 5 x 16 = 80 pixels |
| Reference point | Bottom-left alien (Row 0, Col 0) position |

### 3.3 Starting Y Positions (Reference Alien)

The reference alien's initial Y coordinate changes per round, making aliens start progressively lower (closer to the player):

| Round | Reference Y (hex) | Reference Y (decimal) | Notes |
|---|---|---|---|
| 1 | 0x78 | 120 | Highest start position |
| 2 | 0x60 | 96 | |
| 3 | 0x50 | 80 | |
| 4 | 0x48 | 72 | |
| 5 | 0x48 | 72 | |
| 6 | 0x48 | 72 | |
| 7 | 0x40 | 64 | Maximum difficulty start |
| 8 | 0x40 | 64 | |
| 9 | 0x40 | 64 | |
| 10+ | Cycle repeats from Round 1 values | | Wraps back to 0x78 |

Data sourced from ROM address 0x1DA3.

### 3.4 Movement Pattern

1. **Direction**: Formation begins moving **right**.
2. **Horizontal step**: Each alien moves **2 pixels** per update cycle in the current direction.
3. **Edge detection**: When any alien in the formation reaches the screen boundary, the entire formation:
   - Drops **8 pixels** downward
   - Reverses horizontal direction
4. **Single-alien asymmetry**: When only 1 alien remains, it moves **2 pixels leftward** but **3 pixels rightward** per step, making right-to-left tracking slightly easier than left-to-right.

### 3.5 Speed Acceleration (Frame-Driven)

Since exactly one alien is updated per frame, the time for one complete formation step equals:

```
step_time = (number_of_living_aliens) / 60 seconds
```

| Aliens Remaining | Time Per Full Step | Effective Speed |
|---|---|---|
| 55 | 917 ms | Slowest -- stately march |
| 45 | 750 ms | |
| 35 | 583 ms | |
| 25 | 417 ms | Noticeably faster |
| 15 | 250 ms | Rapid |
| 10 | 167 ms | |
| 5 | 83 ms | Very fast |
| 3 | 50 ms | |
| 2 | 33 ms | |
| 1 | 16.7 ms | Maximum speed -- 60 steps/second |

### 3.6 Sound Tempo Table (Fleet March)

The four-note descending march loop accelerates independently from visual movement. Sound delay is measured in interrupts (1 interrupt = 1/60 second):

| Aliens Remaining (>=) | Sound Delay (interrupts) | Tempo (BPM approx) |
|---|---|---|
| 55 | 52 | ~69 |
| 50 | 46 | ~78 |
| 43 | 39 | ~92 |
| 35 | 34 | ~106 |
| 29 | 28 | ~129 |
| 23 | 24 | ~150 |
| 18 | 21 | ~171 |
| 15 | 19 | ~189 |
| 12 | 16 | ~225 |
| 10 | 14 | ~257 |
| 9 | 13 | ~277 |
| 8 | 12 | ~300 |
| 7 | 11 | ~327 |
| 6 | 9 | ~400 |
| 5 | 7 | ~514 |
| 1 | 5 | ~720 |

Data from ROM address 0x1A21.

### 3.7 Animation

Each alien type has **two animation frames** that alternate with each horizontal step of the formation. The frame toggle occurs per-alien as it is individually updated during the draw cycle.

### 3.8 Alien Hit Freeze

When any alien is hit by the player's shot, the formation movement **pauses for 16 frames** (~267 ms) while the explosion animation plays. During this freeze, the alien's explosion sprite is displayed and then removed.

---

## 4. Alien Types and Scoring

### 4.1 Type Table

| Type Name | Visual | Rows Occupied | Sprite Width | Sprite Height | Points | Animation Frames |
|---|---|---|---|---|---|---|
| Squid (Small Invader) | Narrow body, two tentacles | Row 4 (top row only) | 8 px | 8 px | 30 | 2 (arms open/closed) |
| Crab (Medium Invader) | Wide body, claw-like arms | Rows 2-3 | 11 px | 8 px | 20 | 2 (claws up/down) |
| Octopus (Large Invader) | Broad body, wavy tentacles | Rows 0-1 (bottom) | 12 px | 8 px | 10 | 2 (tentacles spread/compact) |

All alien sprites occupy a 16x8 pixel bounding box for collision and grid purposes. The actual visible pixels vary by type as noted above.

### 4.2 Maximum Points Per Wave

| Type | Count | Points Each | Subtotal |
|---|---|---|---|
| Squid | 11 | 30 | 330 |
| Crab | 22 | 20 | 440 |
| Octopus | 22 | 10 | 220 |
| **Total** | **55** | -- | **990** |

### 4.3 Explosion Sprite

When an alien is destroyed, its sprite is replaced by a shared explosion graphic (approximately 13x8 pixels -- a splayed burst pattern) displayed for 16 frames before being erased.

---

## 5. Player Ship (Laser Cannon) Mechanics

### 5.1 Ship Specifications

| Parameter | Value |
|---|---|
| Sprite width | 16 pixels (2 bytes) |
| Sprite height | 8 pixels |
| Y position | Fixed at Y = 32 (bottom of playfield, above baseline) |
| Movement axis | Horizontal only |
| Movement speed | 1 pixel per input-read cycle |
| X range (left boundary) | 0x30 (48 decimal) |
| X range (right boundary) | 0xD9 (217 decimal) |
| Effective travel range | 169 pixels |
| Starting X | Center of playfield |

### 5.2 Lives System

| Parameter | Value |
|---|---|
| Starting lives | 3 (configurable via DIP switch: 3, 4, 5, or 6) |
| Extra life | Awarded once at 1,500 points (configurable via DIP: 1,000 or 1,500) |
| Maximum extra lives | 1 per game (the bonus is awarded only once) |
| Lives display | Bottom-left of screen as cannon icons + numeric count |

### 5.3 Death Sequence

1. Player cannon is hit by any alien shot or contacted by an alien reaching the cannon row.
2. Cannon sprite is replaced by a **death explosion** animation: two alternating explosion frames displayed for approximately **64 frames** (~1.07 seconds).
3. Lives counter decrements by 1.
4. If lives > 0: cannon respawns at starting X position with a brief delay.
5. If lives = 0: game over.

### 5.4 Player State Machine

```
Idle -> Moving (on directional input)
Moving -> Idle (on input release)
Idle/Moving -> Firing (on fire input, if no shot on screen)
Any -> Hit (on damage received)
Hit -> DeathAnim (play explosion for 64 frames)
DeathAnim -> Respawn (if lives > 0) | GameOver (if lives = 0)
Respawn -> Idle (after brief spawn delay)
```

---

## 6. Bullet System

### 6.1 Player Shot

| Parameter | Value |
|---|---|
| Shots on screen | **1 maximum** -- single shot only |
| Shot speed | 4 pixels per interrupt (240 pixels/second at 60 Hz) |
| Shot sprite | 1 pixel wide, 4 pixels tall |
| Fire origin | Top-center of player cannon sprite |
| Collision | Destroys on first contact with any alien, bunker, UFO, or alien shot |

**Shot Explosion**: When the player's shot hits anything, it is replaced by a small explosion sprite (~8 pixels) displayed for a few frames before despawning, which enables the player to fire again.

### 6.2 Shot Reload Rate

After the player's shot is removed from screen (hit or reached top), there is a **reload delay** before the next shot can be fired. This delay decreases as the player's score increases:

| Player Score (upper 2 digits hex) | Reload Delay (interrupts) | Delay (seconds) |
|---|---|---|
| < 0x02 (below ~200) | 0x30 (48) | 0.80 |
| 0x02 - 0x10 (~200-1000) | 0x10 (16) | 0.27 |
| 0x10 - 0x20 (~1000-2000) | 0x0B (11) | 0.18 |
| 0x20 - 0x30 (~2000-3000) | 0x08 (8) | 0.13 |
| >= 0x30 (3000+) | 0x07 (7) | 0.12 |

Data from ROM address 0x1CB8.

### 6.3 Alien Shot Types

Three alien shot objects operate simultaneously, each with unique behavior and sprite:

#### 6.3.1 Rolling Shot (Targeted)

| Parameter | Value |
|---|---|
| Visual | Spiraling/rotating animation (4 frames) |
| Targeting | Always fires from the column directly above the player's current X position |
| Behavior | Selects the lowest living alien in the column nearest to the player and fires downward |
| Priority | Always active; most dangerous shot type |

#### 6.3.2 Plunger Shot (Column-Sequenced)

| Parameter | Value |
|---|---|
| Visual | Bathroom-plunger shape (narrow shaft, wide cap) cycling 4 frames |
| Targeting | Follows a fixed column sequence table, advancing one entry per shot fired |
| Column Sequence | 1, 7, 1, 1, 1, 4, 11, 1, 6, 3, 1, 1, 11, 9, 2, 8 (16 entries, loops) |
| Special Rule | **Disabled** when only 1 alien remains |

#### 6.3.3 Squiggly Shot (Column-Sequenced)

| Parameter | Value |
|---|---|
| Visual | Zigzag/resistor-like shape cycling 4 frames |
| Targeting | Follows a fixed column sequence table, advancing one entry per shot fired |
| Column Sequence | 11, 1, 6, 3, 1, 1, 11, 9, 2, 8, 2, 11, 4, 7, 10 (15 entries, loops) |
| Special Rule | Shares task slot with the UFO -- squiggly shot cannot fire while UFO is on screen |

#### 6.3.4 Alien Shot Speed Table

| Condition | Delta Y (pixels/step) | Step Frequency | Effective Speed |
|---|---|---|---|
| > 8 aliens remaining | 4 px/step | Every 3 frames | ~80 pixels/second |
| <= 8 aliens remaining | 5 px/step | Every 3 frames | ~100 pixels/second |

#### 6.3.5 Alien Shot Firing Rules

- Maximum **3 alien shots** on screen simultaneously (one of each type).
- Each shot type has its own independent reload timer.
- A shot fires from the **lowest living alien** in the selected column.
- If the selected column has no living aliens, that shot type skips and advances its column pointer.
- Alien shots are destroyed upon hitting the player, a bunker, or the bottom of the screen.

#### 6.3.6 Shot-to-Shot Collision

When a player shot and an alien shot collide mid-flight:
- The **player shot is always destroyed**.
- The **plunger and squiggly shots survive** the collision (they pass through).
- The **rolling shot is destroyed** on collision with the player shot.

---

## 7. Shield / Bunker System

### 7.1 Bunker Layout

| Parameter | Value |
|---|---|
| Number of bunkers | 4 |
| Bunker width | 22 pixels |
| Bunker height | 16 pixels |
| Shape | Arch/dome shape with a concave notch on the underside |
| Horizontal spacing | Evenly distributed across the playfield (~45 pixels between centers) |
| Vertical position | Approximately Y = 48, between the alien formation area and the player cannon |
| Data size | 44 bytes per bunker (22 rows x 2 bytes wide) |
| Shield ROM address | 0x1D20 |

### 7.2 Erosion Mechanics

Bunkers are stored directly in video RAM as pixel data (not as sprite objects). Damage is handled via pixel-level XOR operations:

1. **Player shot hits bunker**: The shot is replaced by an **explosion sprite** (~6x8 pixels). This explosion sprite is XOR-drawn over the bunker pixels, erasing any overlapping bunker pixels. The explosion sprite is then removed after a few frames, leaving a hole.

2. **Alien shot hits bunker**: Same mechanism -- an explosion sprite is XOR-drawn at the impact point, eroding a chunk of bunker pixels. The specific erosion pattern depends on the shot type's explosion sprite.

3. **Alien overlap**: When descending aliens physically overlap bunker pixels, the bunker pixels in the overlapping area are **erased entirely** as the aliens pass through. This occurs when the formation reaches the bunker row (approximately Y = 48-64).

4. **Erosion is permanent** within a round. Bunkers are fully restored at the start of each new wave.

### 7.3 Tactical Properties

- Bunkers block **both** player shots and alien shots equally.
- Players can deliberately shoot a narrow channel through a bunker to create a protected firing position.
- Bunker erosion is cumulative -- repeated hits to the same area enlarge the gap.
- No bunker pixel can be "set" by an explosion that was not already set -- erosion only removes, never adds.

---

## 8. UFO / Mystery Ship

### 8.1 Appearance Conditions

| Parameter | Value |
|---|---|
| Minimum aliens for UFO | >= 8 aliens must be alive (UFO shares task slot with squiggly shot) |
| Alien position gate | Reference alien Y coordinate must be > 0x78 (aliens must have moved downward at least once, or wave must have started below that Y) |
| Spawn timer | Approximately 25.6 seconds (resets to 600 game loops after each appearance) |
| Flight path Y | Near top of playfield, in the red overlay zone (~Y = 216-240) |
| Flight speed | 2 pixels per step |

### 8.2 Direction Determination

The UFO enters from **left or right** based on the player's cumulative shot count:

| Shot Count Parity | UFO Entry Direction | Start X | End X |
|---|---|---|---|
| Even number of shots | Right to left | 0xE0 (224) | 0x29 (41) |
| Odd number of shots | Left to right | 0x29 (41) | 0xE0 (224) |

### 8.3 Scoring Table

The UFO's point value is **not random** -- it is determined by the player's shot count at the moment the UFO is hit. The score table (ROM address 0x1D54) contains 16 entries, but due to a code bug at address 0x044E, the pointer wraps after 15 entries instead of 16:

| Shot Count (mod 15) | Score Value |
|---|---|
| 0 | 100 |
| 1 | 50 |
| 2 | 50 |
| 3 | 100 |
| 4 | 150 |
| 5 | 100 |
| 6 | 100 |
| 7 | 50 |
| 8 | **300** |
| 9 | 100 |
| 10 | 100 |
| 11 | 100 |
| 12 | 50 |
| 13 | 150 |
| 14 | 100 |

**300-point exploit**: On each new wave, fire 22 shots into aliens, then hit the UFO with the 23rd shot for 300 points. Every 15th shot thereafter (38th, 53rd, etc.) will also yield 300 points.

### 8.4 UFO Score Display

When the UFO is hit, the score value is displayed at the UFO's last position for approximately 1 second before fading.

---

## 9. Level Progression

### 9.1 Wave Structure

The game has **no final wave** -- it loops indefinitely with increasing difficulty. Each wave begins with a full formation of 55 aliens. After clearing all aliens, a new wave spawns.

### 9.2 Difficulty Escalation

| Wave | Alien Start Y | Reload Rate Category | Difficulty Notes |
|---|---|---|---|
| 1 | 0x78 (120) | Slow (score-dependent) | Tutorial-level spacing; aliens far from player |
| 2 | 0x60 (96) | Score-dependent | Aliens start noticeably lower |
| 3 | 0x50 (80) | Score-dependent | Moderate threat |
| 4-6 | 0x48 (72) | Fast (score > 3000 by now) | Aliens start close to bunkers |
| 7-9 | 0x40 (64) | Maximum rate | Aliens start AT bunker level; bunkers erased almost immediately |
| 10 | 0x78 (120) | Maximum rate | Position resets to wave 1 height, but fire rate remains fast |
| 11+ | Cycle repeats | Maximum rate | Pattern repeats from wave 2 positions |

### 9.3 Difficulty Factors Summary

| Factor | How It Increases |
|---|---|
| Alien starting Y | Lower each wave (rounds 1-9), then cycles |
| Alien movement speed | Inherent -- fewer aliens = faster movement (always applies) |
| Alien shot speed | Increases from 4 to 5 px/step when <= 8 aliens remain |
| Player reload delay | Decreases with score (player benefit -- but also signals score-based difficulty) |
| Alien fire reload | Decreases with player score (aliens fire more frequently as score rises) |
| UFO availability | Constrained by alien count (>= 8) and position gate |

### 9.4 Invasion (Instant Game Over)

If **any** alien reaches the bottom row of the playfield (the player's row at Y = 32), the game ends **immediately** regardless of remaining lives. This is the "invasion" loss condition.

---

## 10. Scoring System

### 10.1 Point Values

| Target | Points |
|---|---|
| Octopus (Large, rows 0-1) | 10 |
| Crab (Medium, rows 2-3) | 20 |
| Squid (Small, row 4) | 30 |
| UFO / Mystery Ship | 50, 100, 150, or 300 (shot-count dependent; see Section 8.3) |

### 10.2 Maximum Score Per Wave

- Aliens only: 990 points (see Section 4.2)
- With optimal UFO farming: 990 + multiple 300-point UFO hits (theoretically 1-2 UFOs per wave depending on timing)

### 10.3 Score Display

| Element | Position | Format |
|---|---|---|
| SCORE<1> | Top-left | 4 digits, leading zeros |
| HI-SCORE | Top-center | 4 digits, persists across games |
| SCORE<2> | Top-right | 4 digits (2-player mode only) |

### 10.4 Score Rollover

The score is stored in **2 bytes (BCD format)**, giving a maximum displayable score of **9,999**. Upon exceeding this value the display rolls over to 0000. Skilled players can exceed this in extended play sessions.

### 10.5 Extra Life

One bonus life is awarded at **1,500 points** (or 1,000 points depending on DIP switch setting). This bonus is awarded **only once per game**.

---

## 11. Game States

### 11.1 Application State Machine

```
PowerOn -> Attract
Attract -> CoinInsert
CoinInsert -> PlayerStart (on Start button)
PlayerStart -> WaveInit
WaveInit -> Playing
Playing -> AlienHitFreeze (on alien destroyed, 16 frames, returns to Playing)
Playing -> PlayerDeath (on player hit)
PlayerDeath -> DeathAnimation (64 frames)
DeathAnimation -> WaveInit (respawn, if lives > 0)
DeathAnimation -> GameOver (if lives = 0)
Playing -> WaveClear (all 55 aliens destroyed)
WaveClear -> WaveInit (next wave, with new starting Y from table)
Playing -> Invasion (alien reaches player row)
Invasion -> GameOver
GameOver -> Attract (after score display / high score entry)
```

### 11.2 Attract Mode

- Alternates between two demonstration animations:
  - Alien sprites rearranging to spell "PLAY" and "SPACE INVADERS"
  - Score table display showing each alien type and its point value
- "INSERT COIN" text blinks at bottom of screen
- No gameplay demo is shown (the original arcade did not include an AI demo)

### 11.3 Two-Player Mode

- Two players alternate turns (not simultaneous).
- Each player has independent: lives, score, wave state, bunker damage, alien positions.
- Player 2's state is swapped in/out of active memory on turn change.
- Turn changes occur on player death.

---

## 12. Collision System

### 12.1 Collision Detection Method

All collision detection uses **pixel-perfect XOR bit checking** against video RAM. When drawing a sprite, the game XORs the sprite data with existing video RAM contents. If any bits overlap (both the sprite and existing pixels are "on"), a collision is registered.

### 12.2 Collision Matrix

| Object A | Object B | Result |
|---|---|---|
| Player shot | Alien | Alien destroyed; shot destroyed; score awarded; 16-frame freeze |
| Player shot | UFO | UFO destroyed; shot destroyed; score displayed at UFO position |
| Player shot | Bunker | Shot destroyed; bunker pixels eroded at impact point |
| Player shot | Alien shot (rolling) | Both destroyed |
| Player shot | Alien shot (plunger) | Player shot destroyed; plunger survives |
| Player shot | Alien shot (squiggly) | Player shot destroyed; squiggly survives |
| Player shot | Top of screen | Shot destroyed (explosion animation at top) |
| Alien shot | Player | Player destroyed; shot destroyed; life lost |
| Alien shot | Bunker | Shot destroyed; bunker pixels eroded at impact point |
| Alien shot | Bottom of screen | Shot destroyed |
| Alien body | Bunker | Bunker pixels erased where alien overlaps |
| Alien body | Player row (Y=32) | Instant game over (invasion) |

### 12.3 Priority Resolution

When multiple collisions occur in the same frame, they are processed in the fixed update order:
1. Player shot collisions (checked during player shot movement)
2. Alien shot collisions (checked during each alien shot movement)
3. Alien-bunker overlap (checked during alien repositioning)
4. Invasion check (checked after alien descent)

---

## 13. Audio Design

### 13.1 Sound Hardware

The original arcade uses a combination of:
- **SN76477** Complex Sound Generation chip (for UFO sound)
- Discrete analog circuits (7 total sound circuits)

### 13.2 Sound Effects Table

| Event | Sound Description | Behavior |
|---|---|---|
| Fleet march | Four descending tones: D4, C4, Bb3, A3 (approximate) | Loops continuously; tempo accelerates per sound table (Section 3.6) |
| Player fire | Short high-pitched rising "pew" | Plays on each shot fired |
| Alien explosion | Brief white-noise burst | Plays on each alien destroyed |
| Player death | Descending warble/buzz, ~1 second | Plays during 64-frame death animation |
| UFO flying | Continuous oscillating low-frequency hum (VCO + SLF from SN76477) | Loops while UFO is on screen |
| UFO destroyed | Short ascending tone | Plays when UFO is hit |
| Alien shot fire | Soft click/thud | Plays when each alien shot spawns |
| Extra life | Brief ascending jingle | Plays once when bonus life is awarded |

### 13.3 Fleet March Tempo

The fleet march is the game's only continuous "music." It consists of four notes played in sequence, with the delay between notes controlled by the sound timing table (Section 3.6). At 55 aliens the interval is ~867 ms per note; at 1 alien the interval is ~83 ms per note, creating the iconic accelerating heartbeat effect.

---

## 14. UI Layout

### 14.1 Screen Regions (224 x 256 pixels, portrait)

```
Y=256 +-----------------------------------------+
      |  SCORE<1>    HI-SCORE    SCORE<2>      |  <- Score row (white)
Y=240 +-----------------------------------------+
      |  [UFO flight path - red zone]           |  <- UFO zone
Y=216 +-----------------------------------------+
      |                                         |
      |    Alien Formation (5x11 grid)          |  <- Main playfield (white)
      |    descends from here                   |
      |                                         |
      |                                         |
      |                                         |
Y=64  |  [===]  [===]  [===]  [===]             |  <- 4 Bunkers (green zone)
Y=48  |                                         |
      |         [ Player Cannon ]               |  <- Player (green zone)
Y=32  +-----------------------------------------+
      |  3 [c][c]              CREDIT 00        |  <- Lives + credits (green)
Y=0   +-----------------------------------------+
```

### 14.2 HUD Elements

| Element | Position | Content |
|---|---|---|
| SCORE<1> label | Top-left | "SCORE<1>" text header |
| Player 1 score | Below SCORE<1> | 4-digit numeric, updates on every kill |
| HI-SCORE label | Top-center | "HI-SCORE" text header |
| High score value | Below HI-SCORE | 4-digit numeric, persists across games |
| SCORE<2> label | Top-right | "SCORE<2>" text header (2P mode) |
| Lives count | Bottom-left | Numeric digit |
| Lives icons | Bottom-left (after digit) | Miniature cannon sprites x (lives - 1) |
| Credit count | Bottom-right | "CREDIT XX" |
| Green baseline | Y = 25 | Solid green horizontal line separating play area from HUD |

---

## 15. Win/Lose Contract

### 15.1 Win Condition (Wave Clear)

All 55 aliens in the current wave are destroyed. This triggers the next wave with new alien positions and restored bunkers.

### 15.2 Lose Conditions

| Condition | Trigger | Result |
|---|---|---|
| Lives depleted | Player hit with 0 remaining lives | Game Over |
| Invasion | Any alien reaches the player row (Y = 32) | Immediate Game Over (regardless of lives) |

### 15.3 Score Persistence

The high score is maintained in RAM and displayed during attract mode. On the original arcade, this resets on power cycle (no persistent storage).

---

## 16. DIP Switch Configuration

The original arcade includes hardware DIP switches for operator-configurable settings:

| Setting | Options | Default |
|---|---|---|
| Number of lives | 3, 4, 5, 6 | 3 |
| Extra life threshold | 1,000 or 1,500 points | 1,500 |
| Coin slots | 1 coin/1 credit or 2 coins/1 credit | 1 coin/1 credit |

---

## 17. Technical Implementation Notes

### 17.1 Sprite Drawing

All sprites are drawn via **XOR blitting** to video RAM. This means:
- Drawing a sprite toggles pixels on/off
- Drawing the same sprite at the same position again **erases** it
- The move-erase-redraw cycle: erase old position (XOR), then draw new position (XOR)
- Collision is detected by checking if any "on" bits overlap during the draw XOR

### 17.2 Alien Update Cycle

The game maintains a pointer that cycles through all 55 alien slots (including dead ones). Each frame:
1. Advance pointer to next alien slot
2. If alien is alive: erase at old position, draw at new position (shifted by current direction delta)
3. If alien is dead: skip (but still count the frame)
4. When pointer wraps past slot 54, one complete formation step is done

This means dead alien slots still consume frames, but since the game skips their drawing, the visual effect is that surviving aliens appear to move at the same rate until the pointer wraps faster (fewer total slots to process = fewer frames per complete cycle).

**Correction**: Actually, dead alien slots are skipped entirely in the update cycle. The pointer advances to the next *living* alien. Therefore, fewer living aliens = fewer frames to complete one full step = faster movement. This is the core mechanic producing the acceleration.

### 17.3 Determinism

The game is fully deterministic given the same inputs:
- No true random number generation is used
- UFO scoring is based on shot count
- Alien shot columns follow fixed sequences (plunger: 16-entry table, squiggly: 15-entry table)
- Rolling shot targets player position (deterministic given input)
- All timing is frame-locked to the 60 Hz interrupt

### 17.4 Known Bugs (Faithfully Preserved)

| Bug | Description |
|---|---|
| UFO score table wrap | Pointer wraps after 15 entries instead of 16 due to off-by-one at ROM 0x044E |
| Column calculation error | Shot hitting Row 3, Column 11 (out of bounds) maps to index 44, which equals Row 4, Column 0 -- can falsely destroy the wrong alien |
| Last alien direction bias | Asymmetric 2px left / 3px right movement is intentional difficulty tuning, not technically a bug |

---

## 18. Data Contracts

### 18.1 Config Schema

```json
{
  "game": {
    "version": "1.0.0",
    "title": "Orbital Invaders",
    "mode": "fixed_shooter"
  },
  "display": {
    "native_width": 224,
    "native_height": 256,
    "orientation": "portrait",
    "refresh_rate_hz": 60
  },
  "timing": {
    "logic_fps": 60,
    "aliens_per_frame": 1,
    "alien_hit_freeze_frames": 16,
    "player_death_frames": 64,
    "ufo_spawn_timer_loops": 600
  },
  "player": {
    "start_lives": 3,
    "extra_life_score": 1500,
    "max_extra_lives": 1,
    "move_speed_px_per_frame": 1,
    "x_min": 48,
    "x_max": 217,
    "y_position": 32,
    "shot_speed_px_per_interrupt": 4
  },
  "aliens": {
    "rows": 5,
    "columns": 11,
    "cell_size_px": 16,
    "horizontal_step_px": 2,
    "descent_step_px": 8,
    "last_alien_left_step_px": 2,
    "last_alien_right_step_px": 3
  },
  "alien_shots": {
    "max_simultaneous": 3,
    "normal_speed_px_per_step": 4,
    "fast_speed_px_per_step": 5,
    "fast_speed_threshold_aliens": 8,
    "step_frequency_frames": 3,
    "plunger_column_table": [1,7,1,1,1,4,11,1,6,3,1,1,11,9,2,8],
    "squiggly_column_table": [11,1,6,3,1,1,11,9,2,8,2,11,4,7,10]
  },
  "ufo": {
    "speed_px_per_step": 2,
    "min_aliens_for_spawn": 8,
    "score_table": [100,50,50,100,150,100,100,50,300,100,100,100,50,150,100]
  },
  "bunkers": {
    "count": 4,
    "width_px": 22,
    "height_px": 16,
    "y_position": 48
  },
  "scoring": {
    "squid_points": 30,
    "crab_points": 20,
    "octopus_points": 10,
    "max_points_per_wave": 990
  },
  "reload_table": {
    "thresholds": [
      {"min_score_hex": "0x0000", "delay_interrupts": 48},
      {"min_score_hex": "0x0200", "delay_interrupts": 16},
      {"min_score_hex": "0x1000", "delay_interrupts": 11},
      {"min_score_hex": "0x2000", "delay_interrupts": 8},
      {"min_score_hex": "0x3000", "delay_interrupts": 7}
    ]
  },
  "wave_start_y_table": ["0x78","0x60","0x50","0x48","0x48","0x48","0x40","0x40","0x40"]
}
```

### 18.2 Runtime Snapshot Schema

```json
{
  "time": {
    "tick": 0,
    "elapsed_seconds": 0.0,
    "current_wave": 1
  },
  "player": {
    "x": 112,
    "y": 32,
    "lives": 3,
    "score": 0,
    "shot_count": 0,
    "state": "Idle",
    "shot_active": false,
    "shot_x": 0,
    "shot_y": 0,
    "reload_timer": 0
  },
  "aliens": {
    "alive_count": 55,
    "alive_grid": [[true,true,true,true,true,true,true,true,true,true,true],
                   [true,true,true,true,true,true,true,true,true,true,true],
                   [true,true,true,true,true,true,true,true,true,true,true],
                   [true,true,true,true,true,true,true,true,true,true,true],
                   [true,true,true,true,true,true,true,true,true,true,true]],
    "reference_x": 26,
    "reference_y": 120,
    "direction": "right",
    "update_pointer": 0
  },
  "alien_shots": {
    "rolling": {"active": false, "x": 0, "y": 0},
    "plunger": {"active": false, "x": 0, "y": 0, "column_index": 0},
    "squiggly": {"active": false, "x": 0, "y": 0, "column_index": 0}
  },
  "ufo": {
    "active": false,
    "x": 0,
    "direction": "left",
    "spawn_timer": 600
  },
  "bunkers": [
    {"pixel_data": "base64_encoded_44_bytes"},
    {"pixel_data": "base64_encoded_44_bytes"},
    {"pixel_data": "base64_encoded_44_bytes"},
    {"pixel_data": "base64_encoded_44_bytes"}
  ],
  "high_score": 0
}
```

---

## 19. QA Acceptance Matrix

1. Formation of 55 aliens (5x11) spawns correctly at the designated Y position for the current wave.
2. Aliens march right, descend 8 px at screen edge, reverse direction, and repeat.
3. Destroying an alien awards correct points (10/20/30) based on row type.
4. Alien speed increases proportionally as aliens are destroyed; final alien moves at 60 steps/second.
5. Last alien exhibits asymmetric movement (2 px left, 3 px right).
6. Player can move horizontally within bounds (X: 48-217) and fire one shot at a time.
7. Player shot travels at 4 px/interrupt and is destroyed on contact with any collidable object.
8. Three alien shot types fire simultaneously with correct behaviors (rolling=targeted, plunger=sequenced, squiggly=sequenced).
9. Alien shot speed increases from 4 to 5 px/step when <= 8 aliens remain.
10. Plunger shot is disabled when 1 alien remains; squiggly shot does not fire when UFO is active.
11. Four bunkers erode pixel-by-pixel on shot impact (both player and alien shots).
12. Aliens erase bunker pixels when overlapping during descent.
13. UFO appears only when >= 8 aliens alive; direction based on shot-count parity; score follows 15-entry table.
14. Hitting UFO on 23rd shot (and every 15th shot thereafter) awards 300 points.
15. Extra life awarded once at 1,500 points.
16. Game over triggers on lives = 0 OR alien invasion (reaching Y = 32).
17. Alien hit causes 16-frame formation freeze with explosion animation.
18. Player death plays 64-frame explosion animation before respawn or game over.
19. Bunkers fully restore at the start of each new wave.
20. Wave start Y positions follow the 9-entry table and cycle after wave 9.
21. Sound tempo for fleet march accelerates per the 16-entry timing table.
22. Score display updates immediately on kill; high score persists across games (within session).
23. Two-player mode alternates turns correctly with independent state per player.
24. Shot-to-shot collision: rolling shot destroyed by player shot; plunger and squiggly survive collision.
25. Score rolls over at 9,999 to 0,000 (BCD 2-byte limitation).

---

## 20. Engineering Milestones

- **Milestone 1 -- Core Loop**: Boot sequence, attract mode, coin insert, game start, 60 Hz fixed tick loop, pause (if applicable).
- **Milestone 2 -- Player**: Cannon movement, single-shot firing, shot collision with screen top, reload timer.
- **Milestone 3 -- Alien Formation**: 5x11 grid spawn, sequential per-frame alien updates, edge detection, descent, direction reversal, speed acceleration.
- **Milestone 4 -- Combat**: Alien destruction with scoring, explosion freeze, three alien shot types with correct targeting/sequencing, shot-to-shot collision.
- **Milestone 5 -- Bunkers**: Four bunkers with pixel-level erosion from all damage sources (player shots, alien shots, alien overlap).
- **Milestone 6 -- UFO**: Spawn timer, direction logic, shot-count-based scoring table, score display.
- **Milestone 7 -- Progression**: Wave transitions, start Y table, reload rate scaling, difficulty curve.
- **Milestone 8 -- Polish**: Lives system, extra life, death animation, game over, two-player mode, attract mode, sound integration, score persistence.
- **Milestone 9 -- QA**: Full acceptance matrix validation, edge case testing (last alien, simultaneous events, score rollover, invasion trigger).
