# Dance Dance Revolution — Complete Game Specification

> A comprehensive specification for faithfully recreating Dance Dance Revolution (based on the DDR A / A20 / A3 arcade series by Konami, with historical reference to DDR Extreme and SuperNOVA 2 for foundational mechanics). This document covers every system, mechanic, timing value, and interaction required for a full recreation.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Gameplay Mechanics](#3-core-gameplay-mechanics)
4. [Note Types](#4-note-types)
5. [Timing System](#5-timing-system)
6. [Scoring System](#6-scoring-system)
7. [Combo & Grade System](#7-combo--grade-system)
8. [Life Gauge System](#8-life-gauge-system)
9. [Difficulty & Chart System](#9-difficulty--chart-system)
10. [Speed & Scroll Modifiers](#10-speed--scroll-modifiers)
11. [Game Options & Modifiers](#11-game-options--modifiers)
12. [Song Selection & UI Flow](#12-song-selection--ui-flow)
13. [Stage Progression](#13-stage-progression)
14. [Groove Radar](#14-groove-radar)
15. [Audio System](#15-audio-system)
16. [Visual Feedback System](#16-visual-feedback-system)
17. [Step Chart Format](#17-step-chart-format)

---

## 1. Game Overview

- **Genre**: Rhythm / Music
- **Perspective**: 2D vertical scrolling note highway (arrows scroll from bottom to top)
- **Input**: 4-panel dance pad (Left, Down, Up, Right directional arrows), pressed by foot
- **Play Modes**: Single (1 player, 4 panels), Double (1 player, 8 panels across two pads), Versus (2 players, 4 panels each)
- **Objective**: Step on the correct arrow panel(s) in time with scrolling arrows as they align with the stationary Step Zone receptors at the top of the screen, matching the rhythm of the music.
- **Win Condition**: Complete the song without the Dance Gauge (life bar) being fully depleted.
- **Lose Condition**: The Dance Gauge reaches zero at any point during the song; gameplay ends immediately with a stage failure (grade E).
- **Core Loop**: Select song and difficulty, set options/modifiers, play through the chart by stepping on arrows, receive judgment per note, accumulate score and maintain life gauge, receive final grade.

---

## 2. Technical Foundation

### Display & Resolution

| Property | Value |
|----------|-------|
| Native resolution (modern cabinets) | 1920 x 1080 (Full HD) |
| Legacy resolution (CRT cabinets) | 640 x 480 |
| Screen orientation | Landscape (horizontal) |
| Monitor size (modern) | 42-inch LCD (Generation 3 cabinets) |
| Monitor size (earlier LCD) | 37-inch LCD (Generation 2 cabinets) |
| Frame rate | 60 FPS (game logic and rendering locked to 60 Hz) |
| Timing base (classic) | Frame-based at 60 FPS (1 frame = 16.667 ms) |
| Timing base (DDR A onward) | Millisecond-based (engine rewrite for precision) |

### Input System

| Property | Value |
|----------|-------|
| Panel count per player | 4 directional (Left, Down, Up, Right) |
| Double mode panels | 8 (full left pad + full right pad for one player) |
| Panel activation | Pressure-sensitive switches beneath each arrow panel |
| Input polling | Hardware-dependent; arcade boards poll at 1000 Hz (1 ms resolution); USB adapters may poll at 125 Hz (8 ms resolution) |
| Panel dimensions | Each arrow panel approximately 11 inches x 11 inches (28 cm x 28 cm) |
| Center panel | Non-directional metal plate between arrows; used for resting or avoiding Shock Arrows |
| Simultaneous inputs | All 4 panels can be pressed simultaneously; each panel registers independently |

### Playfield Layout

| Element | Position |
|---------|----------|
| Arrow highway | Vertical column(s) occupying roughly the center 40% of the screen per player |
| Step Zone (receptors) | Fixed row of 4 translucent arrow outlines near the top of the screen (~85% from bottom) |
| Judgment display | Centered on the playfield, just below the Step Zone |
| Combo counter | Directly below the judgment text |
| Dance Gauge (life bar) | Horizontal bar at the top of the screen |
| Score display | Upper area of the screen |
| BPM display | Shown on the song select screen; not typically visible during gameplay |
| Background | Music video, animated background, or 3D dancer character behind the arrow highway |

### Game Loop (per frame at 60 FPS)

```
1. Poll input from dance pad panels (detect press/release state changes)
2. Advance song position by frame time (track current beat/measure)
3. For each active note approaching the Step Zone:
   a. Check if any panel input matches the note's direction
   b. If matched: calculate timing offset (ms difference from perfect alignment)
   c. Assign judgment based on timing offset (Marvelous/Perfect/Great/Good/Miss)
   d. Update score, combo counter, life gauge, and EX score
   e. Trigger visual/audio feedback for the judgment
4. For each active Freeze Arrow:
   a. Check if the corresponding panel is still held down
   b. If released early: assign NG judgment; apply life gauge penalty
   c. If held through the tail end: assign OK judgment; award points
5. For each Shock Arrow row reaching the Step Zone:
   a. If any directional panel is pressed: assign NG; apply penalty and visual disruption
   b. If no directional panel is pressed: assign OK; award points
6. Check for notes that have passed beyond the timing window without input: assign Miss
7. Update Dance Gauge; check for gauge depletion (stage failure)
8. Render: background layer -> arrow highway -> notes -> Step Zone -> judgments -> combo -> UI overlay
```

---

## 3. Core Gameplay Mechanics

### Arrow Scrolling

- Arrows appear at the bottom of the screen and scroll upward toward the Step Zone at a constant speed determined by the song's BPM multiplied by the player's chosen speed modifier.
- The scroll speed formula is: **Effective Speed = Song BPM x Speed Modifier**
- Arrows that align perfectly with the Step Zone at the exact moment the corresponding beat occurs represent the ideal timing for input.
- Arrows scroll at a constant pixel-per-beat rate within a given BPM section; BPM changes cause the scroll speed to change accordingly.

### Step Zone (Receptors)

- Four stationary arrow outlines (Left, Down, Up, Right) arranged horizontally near the top of the screen.
- Receptors flash white on each quarter-note beat pulse in sync with the song's BPM.
- When a note is hit, the corresponding receptor flashes brightly (color depends on judgment quality).
- The Step Zone serves as the visual target for when to press the panel.

### Basic Step Input

- The player must press the correct panel when the scrolling arrow overlaps the corresponding Step Zone receptor.
- Pressing a panel when no note is near does **not** incur a penalty (no "empty step" punishment in standard DDR).
- Pressing the wrong direction when a note is present does **not** consume that note; the note continues toward Miss if no correct input arrives.

### Combo System

- A **combo** is the consecutive count of notes hit with a judgment of Good or better (Great or better in versions before DDR 2013).
- The combo counter begins at 0 and increments by 1 for each successfully judged note.
- A **Miss** judgment resets the combo counter to 0.
- A **Good** judgment in DDR 2013+ maintains the combo (does not break it), but in earlier versions Good breaks combo.
- Freeze Arrow OK/NG judgments do **not** affect the combo counter (NG does not break combo).
- Shock Arrow OK/NG judgments: NG breaks combo; OK does not increment combo.
- **Jump notes** (two simultaneous arrows) increment the combo by 1 per arrow hit, so a fully hit jump adds 2 to the combo.
- The combo counter display appears after the 4th consecutive successful note (combos 1-3 are not shown).

### Combo Counter Colors

| Combo State | Color |
|-------------|-------|
| All Marvelous (no Perfects, Greats, or Goods) | White with frost/glow effect |
| All Marvelous and/or Perfect (no Greats or Goods) | Yellow/Gold |
| Includes Great judgments | Green |

---

## 4. Note Types

### Tap Arrow (Regular Note)

| Property | Value |
|----------|-------|
| Appearance | Colored arrow pointing in one of 4 directions (Left, Down, Up, Right) |
| Input | Single press of the matching panel |
| Judgment | Based on timing offset from the ideal beat position |
| Color scheme (NOTE mode) | Red = 4th notes, Blue = 8th notes, Yellow = 16th notes, Green = all others |
| Scoring | Awards points based on judgment tier |

### Freeze Arrow (Hold Note)

| Property | Value |
|----------|-------|
| Appearance | Arrow head (same as tap) with a long green vertical tail extending downward |
| Input | Press the matching panel at the arrow head, then **hold** the panel down through the entire tail length |
| Head judgment | Standard timing judgment (Marvelous/Perfect/Great/Good/Miss) at the press moment |
| Hold judgment | OK if held to completion; NG if released early |
| Minimum length | Can be as short as a 64th note or as long as the entire song |
| Visual feedback | The tail glows/pulses while successfully held; goes dark on release |
| Release timing | Player does **not** need to release the panel at the tail end; holding past the end is acceptable |
| Combo interaction | The head press affects combo normally; OK/NG on the hold portion does **not** affect combo |
| Scoring | Head awards tap points based on judgment; OK awards additional hold points; NG awards 0 hold points |
| Life gauge | OK recovers life; NG drains life (same amount as a Miss) |

### Jump (Double Note)

| Property | Value |
|----------|-------|
| Appearance | Two arrows appearing on the same beat (e.g., Left + Right simultaneously) |
| Input | Press both panels simultaneously (within the timing window) |
| Judgment | Each arrow in the jump is judged independently |
| Combo | Each arrow adds 1 to the combo independently (a jump can add 0, 1, or 2 to combo) |
| Possible combinations | Left+Down, Left+Up, Left+Right, Down+Up, Down+Right, Up+Right |
| Scoring | Each arrow scores independently |

### Shock Arrow

| Property | Value |
|----------|-------|
| Appearance | Full row of all 4 arrows connected by blue lightning/electricity; metallic color |
| Introduced in | DanceDanceRevolution X (2008) |
| Input | **Avoid** pressing any directional panel when the shock row reaches the Step Zone |
| OK judgment | Awarded when no directional panel is pressed as the shock row passes |
| NG judgment | Awarded when any directional panel is pressed; triggers electric sound effect |
| Visual penalty | On NG: all other arrows briefly disappear from the highway for several frames |
| Combo | NG breaks combo; OK does not change combo |
| Scoring | OK awards points (equivalent to Marvelous); NG awards 0 points |
| Life gauge | OK recovers life; NG drains life |
| Evasion technique | Players jump (both feet off all panels), stand on the center metal plate, or move feet to non-directional areas |
| Color | Always blue/metallic regardless of arrow color option setting |

---

## 5. Timing System

### Judgment Windows

Judgments are assigned based on the absolute timing offset between the player's input and the note's ideal beat position. DDR's timing system was historically frame-based (multiples of 16.667 ms at 60 FPS). Beginning with DDR A (2016), the engine was rewritten to use millisecond-based timing for improved precision.

#### Classic Frame-Based Timing (DDR Extreme through DDR X3)

| Judgment | Window (symmetric +/-) | Frames at 60 FPS | Description |
|----------|----------------------|-------------------|-------------|
| Marvelous | +/- 16.667 ms | +/- 1 frame | Virtually perfect timing |
| Perfect | +/- 33.333 ms | +/- 2 frames | Near-perfect timing |
| Great | +/- 91.667 ms | +/- 5.5 frames | Good timing |
| Good | +/- 141.667 ms | +/- 8.5 frames | Acceptable timing |
| Boo/Almost | +/- 225.000 ms | +/- 13.5 frames | Poor timing (still registered) |
| Miss | Beyond +/- 225 ms | Beyond 13.5 frames | Note passes without valid input |

#### DDR Extreme Asymmetric Windows (Measured Values)

| Judgment | Early (ms) | Late (ms) |
|----------|-----------|----------|
| Marvelous | -13.333 | +13.333 |
| Perfect | -26.667 | +26.667 |
| Great | -86.667 | +73.333 |
| Good | -126.667 | +113.333 |
| Boo | -153.333 | +180.000 |

#### DDR A / A20 / A3 Timing (Millisecond-Based)

| Judgment | Estimated Window (+/-) | Notes |
|----------|----------------------|-------|
| Marvelous | +/- 16.667 ms | Believed to be maintained from classic values |
| Perfect | +/- 33.333 ms | Believed to be maintained from classic values |
| Great | ~+/- 92 ms | Approximate; may differ slightly from frame-based era |
| Good | ~+/- 142 ms | Approximate |
| Miss | Beyond Good window | No input within any valid window |

### Judgment Hierarchy

```
MARVELOUS  (best)   -- White flash, "MARVELOUS!!" text
PERFECT             -- Yellow flash, "PERFECT!" text
GREAT               -- Green flash, "GREAT" text
GOOD                -- Blue/purple text, "GOOD" text (maintains combo in modern DDR)
BOO / ALMOST        -- Faint text (used in pre-SuperNOVA2 versions; removed in modern versions)
MISS                -- Red X or "MISS" text; combo broken; life gauge drained
```

### Timing Notes

- **Early vs. Late**: The game distinguishes between early and late hits internally. Some versions display "FAST" or "SLOW" indicators on the judgment text to help players calibrate.
- **Marvelous availability**: In DDR Extreme, Marvelous was only available in Nonstop/Challenge (Oni) modes. From DDR SuperNOVA 2 onward, Marvelous is available in all modes.
- **Input timing**: The judgment is calculated at the moment the panel transitions from unpressed to pressed (the rising edge of the input signal).

---

## 6. Scoring System

DDR has used multiple scoring systems across its history. This specification covers both the modern 1,000,000-point system and the legacy Dance Point / EX Score systems.

### Modern Score System (SuperNOVA 2 / DDR A onward)

The maximum possible score for any song is **1,000,000 points**. All scoreable elements (tap notes, freeze arrows, shock arrows) are weighted equally.

#### Step Score Calculation

Let **N** = total number of scoreable elements (tap notes + freeze arrows + shock arrows).

**Base step value (SC)** = floor(1,000,000 / N), rounded down to the nearest 10.

| Judgment | Points Awarded |
|----------|---------------|
| Marvelous | SC |
| Perfect | SC - 10 |
| Great | floor(SC / 2) - 10 |
| Good | 0 (in some versions: floor(SC / 2) - 10 penalty structure; effectively minimal) |
| OK (Freeze/Shock) | SC |
| Miss | 0 |
| NG (Freeze/Shock) | 0 |

#### Score Display

- The internal score is calculated as a floating-point value.
- The displayed score is rounded down to the nearest **10 points**.
- Maximum displayed score: **1,000,000** (only achievable with all Marvelous + all OK).

#### DDR A Simplified Scoring (Alternative Formula)

Each scoreable element has a maximum of **5 points** internally:

| Judgment | Internal Points |
|----------|----------------|
| Marvelous | 5 |
| Perfect | 5 |
| Great | 3 |
| Good | 1 |
| OK | 5 |
| Miss / NG | 0 |

**Money Score** = (Earned Points / Maximum Possible Points) x 1,000,000, rounded down to the nearest 10.

Where Maximum Possible Points = 5 x N.

A penalty of 10 is subtracted from every non-Marvelous judgment score (excluding Misses and NGs).

### EX Score System

The EX Score is a secondary scoring metric introduced in DDR Extreme for Challenge/Oni mode. It became universally tracked from DDR SuperNOVA 2 onward.

| Judgment | EX Points |
|----------|-----------|
| Marvelous | 3 |
| Perfect | 2 |
| Great | 1 |
| Good | 0 |
| OK (Freeze/Shock) | 3 |
| Miss | 0 |
| NG | 0 |

**Maximum EX Score** = 3 x N (where N is total scoreable elements including freeze/shock).

The EX Score is displayed alongside the standard score on the results screen.

### Legacy Dance Point System (DDR Extreme and Earlier)

Used for grade calculation in classic versions:

| Judgment | Dance Points |
|----------|-------------|
| Marvelous | 3 |
| Perfect | 2 |
| Great | 1 |
| Good | 0 |
| Boo | -4 |
| Miss | -8 |
| OK (Freeze) | 6 |
| NG (Freeze) | 0 |

**Maximum Dance Points** = (3 x number of tap notes) + (6 x number of freeze arrows).

Grades were assigned based on the percentage of earned Dance Points to the maximum possible.

---

## 7. Combo & Grade System

### Full Combo Types

| Full Combo Type | Abbreviation | Requirement | Color Indicator |
|----------------|-------------|-------------|-----------------|
| Marvelous Full Combo | MFC | Every note is Marvelous; every hold/shock is OK | White/Platinum |
| Perfect Full Combo | PFC | Every note is Marvelous or Perfect; every hold/shock is OK | Gold/Yellow |
| Great Full Combo | GFC | Every note is Great or better; every hold/shock is OK | Green |
| Full Combo | FC | No Miss judgments at all (Good is acceptable in DDR 2013+) | Blue |
| Good Full Combo | (none) | Legacy: no Boo or Miss (Good allowed; Boo breaks combo in old versions) | -- |

### Grade Thresholds (Modern: DDR A / A20 / A3)

Grades are based on the final Money Score out of 1,000,000. The player must also clear the song (not fail) to receive grades D+ through AAA. A failed song always receives grade E.

| Grade | Score Range |
|-------|------------|
| AAA | 990,000 - 1,000,000 |
| AA+ | 950,000 - 989,990 |
| AA | 900,000 - 949,990 |
| AA- | 890,000 - 899,990 |
| A+ | 850,000 - 889,990 |
| A | 800,000 - 849,990 |
| A- | 790,000 - 799,990 |
| B+ | 750,000 - 789,990 |
| B | 700,000 - 749,990 |
| B- | 690,000 - 699,990 |
| C+ | 650,000 - 689,990 |
| C | 600,000 - 649,990 |
| C- | 590,000 - 599,990 |
| D+ | 550,000 - 589,990 |
| D | 0 - 549,990 (cleared) |
| E | Any score (failed / gauge depleted) |

### Legacy Grade Thresholds (DDR Extreme / Classic System)

Based on percentage of maximum Dance Points earned:

| Grade | Dance Point Percentage |
|-------|----------------------|
| AAA | 100% |
| AA | 93% - 99% |
| A | 80% - 92% |
| B | 65% - 79% |
| C | 45% - 64% |
| D | 1% - 44% (cleared) |
| E | Failed (gauge depleted) |

### Clear Types (Result Screen Icons)

| Clear Type | Icon / Indicator | Condition |
|-----------|-----------------|-----------|
| MFC | White/Platinum star | Marvelous Full Combo achieved |
| PFC | Gold star | Perfect Full Combo achieved |
| GFC | Green star | Great Full Combo achieved |
| FC | Blue circle / Full Combo marker | Full Combo (no Misses) |
| Clear | Green "CLEAR" icon | Song completed without failing; not a full combo |
| Assist Clear | Purple "CLEAR" icon | Song completed with assist options enabled (Cut, Freeze Off, Jump Off) |
| Failed | Red "FAILED" / E grade | Dance Gauge depleted during song |
| Flare Clear | Colored "FLARE" frame (DDR A3+) | Cleared with Flare Gauge active |

---

## 8. Life Gauge System

### Normal Dance Gauge (Default)

| Property | Value |
|----------|-------|
| Starting value | 50% (half-full) |
| Maximum value | 100% (full) |
| Minimum value | 0% (empty = fail) |
| Danger threshold | 20% or below (visual warning state: gauge flashes red) |
| Fail condition | Gauge reaches 0% at any point during the song |

#### Life Change Per Judgment

These values represent the percentage change to the Dance Gauge per judgment received. Values are based on StepMania's DDR-emulation defaults, which closely mirror actual arcade behavior.

| Judgment | Gauge Change |
|----------|-------------|
| Marvelous | +0.8% |
| Perfect | +0.8% |
| Great | +0.4% |
| Good | +0.0% (no change) |
| Miss | -8.0% |
| OK (Freeze held) | +0.8% |
| NG (Freeze released) | -8.0% |
| Hit Mine / Shock NG | -16.0% |
| Missed Hold (did not start) | 0.0% |

#### Gauge Behavior

- The gauge recovers slowly with good play and drains sharply on mistakes.
- A single Miss drains 10 times more than a Marvelous recovers. This means sustaining a full gauge requires consistent accuracy.
- The gauge cannot exceed 100% or go below 0%.
- When the gauge is in the "Danger" zone (below 20%), the gauge bar flashes red and a warning sound/visual may play.
- If the gauge reaches 0%, the song immediately ends with a failure screen and the grade E is assigned.

### LIFE4 Gauge (Hard Clear)

| Property | Value |
|----------|-------|
| Lives | 4 |
| Life loss | 1 life lost per Miss or NG judgment |
| Life recovery | None (lives cannot be regained) |
| Fail condition | All 4 lives lost (0 remaining) |
| Display | 4 heart/life icons; one disappears per Miss |
| Available in | Premium Play modes |

### RISKY Gauge

| Property | Value |
|----------|-------|
| Lives | 1 |
| Life loss | Instant fail on any Miss judgment |
| Life recovery | None |
| Fail condition | A single Miss ends the song immediately |
| Display | Single life icon |
| Purpose | Ultimate challenge mode; demands perfect (no Miss) play |

### Flare Gauge (DDR A3+)

| Property | Value |
|----------|-------|
| Starting value | 100% (full) |
| Recovery | None (gauge never recovers) |
| Drain | Decreases on Good, Miss, and NG judgments |
| Fail condition | Gauge reaches 0% |
| Levels | Multiple Flare Gauge levels (I through X) with increasing drain rates |
| Purpose | Competitive gauge for FLARE SKILL ranking system |
| Clear reward | Flare Points awarded based on gauge level survived |

### Extra Stage Gauge (Classic Versions)

| Property | Value |
|----------|-------|
| Starting value | 100% (full) |
| Recovery | None (gauge never increases) |
| Drain | Any non-Marvelous/Perfect judgment drains the gauge |
| Fail condition | Gauge reaches 0% |
| Context | Used during Extra Stage in DDR Extreme through DDR X3 |
| Forced options | Typically forced 1.5x speed, Reverse, Dark, or other challenge modifiers |

### Course Mode Gauge

| Variant | Description |
|---------|-------------|
| Normal Course Gauge | Standard Dance Gauge that persists across all songs in the course |
| Battery (4 Lives) | 4-life meter; one life lost per Miss; persists across all course songs |
| Battery (1 Life) | Single life; any Miss fails the entire course |

---

## 9. Difficulty & Chart System

### Difficulty Tiers

Each song has up to 5 difficulty tiers, each containing a unique step chart (pattern of arrows):

| Difficulty | Abbreviation | Target Audience | Typical Level Range | Color Code |
|-----------|-------------|-----------------|--------------------|-----------| 
| Beginner | BEG | Complete newcomers | 1 - 4 | Light blue |
| Basic | BSC | Casual players | 1 - 8 | Orange/Yellow |
| Difficult | DIF | Intermediate players | 4 - 13 | Red |
| Expert | EXP | Advanced players | 7 - 18 | Green |
| Challenge | CHA | Expert players | 8 - 19 | Purple |

### Difficulty Level Scale

| Property | Value |
|----------|-------|
| Minimum level | 1 |
| Maximum level | 19 (20 in some rare instances) |
| Scale type | Integer values only; no decimal levels |
| Historical scale | 1-10 "Foot Rating" (DDR 1st through SuperNOVA 2); expanded to 1-20 in DDR X |

### Chart Properties

Each chart (difficulty of a song) defines:

| Property | Description |
|----------|-------------|
| Note count | Total number of tap arrows (including each arrow in a jump counted separately) |
| Freeze count | Total number of freeze arrows |
| Shock count | Total number of shock arrow rows |
| BPM | Song tempo (may have multiple BPM values for speed changes) |
| Stops | Moments where scroll pauses but music continues |
| Step designer | The person who created the chart (credited in metadata) |

### Chart Patterns and Terminology

| Pattern | Description |
|---------|-------------|
| Stream | Continuous flow of notes at consistent intervals (typically 8th or 16th notes) |
| Crossover | Pattern requiring one foot to cross over the other (e.g., Left then Right with same foot) |
| Gallop | Alternating between faster and slower note spacing within a stream |
| Jack | Repeated notes in the same direction (e.g., Down-Down-Down) |
| Candle | A stream where one foot holds a freeze arrow while the other foot taps additional notes |
| Drills | Very fast repeated single-direction taps |
| Jump stream | Alternating between jumps and single taps at stream speed |
| Freeze-tap | Holding a freeze arrow while tapping other arrows with the free foot |

---

## 10. Speed & Scroll Modifiers

### Speed Modifier System

The speed modifier multiplies the song's current BPM to determine the visual scroll speed of arrows. Higher speed values result in more widely spaced arrows that scroll faster, while lower values produce denser, slower-scrolling arrows.

**Formula**: Visual Scroll Speed = Song BPM x Speed Modifier

#### Available Speed Modifiers (DDR A20 / Premium Play)

Fine increments from x0.25 to x4.0 in steps of 0.25, then from x4.5 to x8.0 in steps of 0.5:

```
x0.25, x0.50, x0.75, x1.00, x1.25, x1.50, x1.75, x2.00,
x2.25, x2.50, x2.75, x3.00, x3.25, x3.50, x3.75, x4.00,
x4.50, x5.00, x5.50, x6.00, x6.50, x7.00, x7.50, x8.00
```

#### Available Speed Modifiers (Standard Play / Non-Premium)

```
x1.0, x1.5, x2.0, x2.5, x3.0, x3.5, x4.0, x4.5,
x5.0, x5.5, x6.0, x6.5, x7.0, x7.5, x8.0
```

#### Speed Selection

- Speed is selected from the Options menu on the song select screen before each stage.
- Speed can also be adjusted **during gameplay** before the first note of the chart by pressing the Left or Right cabinet buttons to decrease or increase speed, respectively.
- **Recommended effective speed range**: 250 - 600 BPM effective. Most competitive players use an effective scroll speed between 400 and 600.

#### Speed Interaction with BPM Changes

- Songs with variable BPM (speed changes) will have their scroll speed change proportionally.
- Example: A song that shifts from 150 BPM to 300 BPM at x2.0 speed will shift from 300 effective to 600 effective.
- Players choose speed modifiers to optimize readability at the song's dominant BPM.

### Scroll Speed Modifiers (Non-Multiplier)

| Modifier | Effect |
|----------|--------|
| Boost | Arrows accelerate as they approach the Step Zone (start slow, finish fast) |
| Brake | Arrows decelerate as they approach the Step Zone (start fast, finish slow) |
| Wave | Arrows oscillate in speed as they scroll, creating a wave-like motion |

---

## 11. Game Options & Modifiers

All modifiers are set from the Options screen accessible during song selection. Options are per-player and persist across stages within a credit unless changed.

### Turn Modifiers

Turn modifiers remap the arrow directions in the chart:

| Modifier | Effect |
|----------|--------|
| Off | No changes to arrow directions (default) |
| Mirror | Left <-> Right and Up <-> Down are swapped (full mirror) |
| Left | All arrows rotated 90 degrees counter-clockwise (Left->Down, Down->Right, Right->Up, Up->Left) |
| Right | All arrows rotated 90 degrees clockwise (Left->Up, Up->Right, Right->Down, Down->Left) |
| Shuffle | Arrows are randomly remapped; the mapping is consistent within a song but different each play |
| Random | Each individual arrow is randomly reassigned to a direction (can produce patterns impossible in the original chart) |

### Appearance Modifiers

| Modifier | Effect |
|----------|--------|
| Visible | Arrows are fully visible at all times (default) |
| Hidden | Arrows fade out and become invisible approximately halfway up the screen |
| Sudden | Arrows are invisible from the bottom, then fade in approximately halfway up the screen |
| Hidden+ | Adjustable version of Hidden; the player can set the exact cutoff point where arrows disappear. A coverage bar is shown and can be adjusted with cabinet buttons. |
| Sudden+ | Adjustable version of Sudden; the player can set the exact point where arrows become visible. A coverage bar is shown and can be adjusted. |
| Hidden+ & Sudden+ | Both active simultaneously; only a narrow window of the highway is visible |
| Stealth | Arrows are completely invisible at all times (purely for showmanship or extreme challenge) |

**Note**: In DDR A and later, the classic Hidden/Sudden options are replaced by Hidden+ and Sudden+ with adjustable coverage.

### Scroll Direction

| Modifier | Effect |
|----------|--------|
| Normal | Arrows scroll upward from bottom to top (default) |
| Reverse | Arrows scroll downward from top to bottom; Step Zone moves to the bottom of the screen |

### Screen Filter (Dark)

| Setting | Effect |
|---------|--------|
| Off | No filter (default); background video/animation fully visible |
| Dark (various levels) | A dark overlay is placed behind the arrow highway, dimming the background to improve note visibility. Available at multiple opacity levels (e.g., 25%, 50%, 75%, 100% black). |

### Arrow Color / Note Skin Options

| Option | Description |
|--------|-------------|
| NOTE | Arrows are colored by beat quantization: Red = 4th notes, Blue = 8th notes, Yellow = 16th notes, Green = other subdivisions |
| VIVID | Same color cycle as Flat (Yellow, Maroon, Blue, Cyan) but each note per beat starts at a different phase |
| FLAT | Consistent color cycling regardless of note quantization (Yellow, Maroon, Blue, Cyan rotation) |
| RAINBOW | Orange = 4th notes, Blue = 8th notes, Purple/Pink = other subdivisions |

### Assist Options

Enabling any assist option marks the clear as an **Assist Clear** (purple clear lamp) instead of a normal clear.

| Option | Effect |
|--------|--------|
| Auto Velocity | Automatically adjusts scroll speed based on BPM changes to maintain constant visual speed |
| Freeze Arrows Off | All freeze arrows are converted to regular tap arrows |
| Jump Off | All jumps (double notes) are simplified to single notes |
| Cut (ON1) | Removes notes at certain subdivisions to simplify the chart |
| Cut (ON2) | Removes more notes than ON1 for further simplification |

### Gauge Options

| Option | Description |
|--------|-------------|
| Normal | Standard Dance Gauge (default) |
| LIFE4 | 4-life battery gauge |
| RISKY | 1-life instant-fail gauge |
| Flare I - X | Flare Gauge at specified level (DDR A3+) |

### Guideline Options

| Option | Effect |
|--------|--------|
| Off | No guidelines on the arrow highway (default) |
| On | Horizontal guidelines appear at beat intervals on the highway to help identify note timing/spacing |
| Center | A guideline appears at the center of the highway |
| Border | Guidelines appear at the borders of the highway |

---

## 12. Song Selection & UI Flow

### Overall Game Flow

```
1. Title Screen / Attract Mode
2. Credit Insert (Coin drop or e-Amusement card tap)
3. Mode Select (Single / Double / Versus)
4. Song Select (1st Stage)
   a. Browse song wheel
   b. Select difficulty
   c. Set options/modifiers
   d. Confirm selection (timer countdown)
5. Gameplay (1st Stage)
6. Results Screen (1st Stage)
7. Song Select (2nd Stage)
8. Gameplay (2nd Stage)
9. Results Screen (2nd Stage)
10. Song Select (Final Stage)
11. Gameplay (Final Stage)
12. Results Screen (Final Stage)
13. [Conditional] Extra Stage
14. [Conditional] Encore Extra Stage / One More Extra Stage
15. Total Results / Final Score Screen
16. Name Entry (if high score)
17. Game Over / Return to Attract Mode
```

### Song Select Screen Layout

| Element | Position/Description |
|---------|---------------------|
| Song Wheel | Right side of screen; vertical list of song titles in rectangular banners, scrollable up/down |
| Selected Song Banner | Large banner/jacket art displayed prominently on the left side |
| BPM Display | Shown near the song banner; displays the song's BPM (or BPM range for variable-BPM songs) |
| Difficulty Selector | Horizontal row of 5 difficulty blocks (Beginner, Basic, Difficult, Expert, Challenge) below or beside the banner; selected difficulty is highlighted |
| Level Number | Large numeric display showing the selected chart's difficulty level (1-19) |
| Groove Radar | Pentagon-shaped radar chart showing 5 attributes of the selected chart |
| High Score | Best score and grade for the selected song/difficulty displayed for the current player |
| Timer | Countdown timer (typically 60-99 seconds) for song selection; auto-selects if time expires |
| Sort Options | Songs can be sorted by: Title (A-Z), BPM, Difficulty Level, Category/Folder, Version |
| Folder System | Songs organized into folders by version, genre, difficulty range, or other criteria |

### Song Selection Controls

| Input | Action |
|-------|--------|
| Up panel | Scroll song list up / navigate menu up |
| Down panel | Scroll song list down / navigate menu down |
| Left panel | Change difficulty level down (e.g., Expert -> Difficult) |
| Right panel | Change difficulty level up (e.g., Difficult -> Expert) |
| Start button (2x) | Confirm song selection / enter options menu on first press, confirm on second |
| Start button (hold) | Open options menu for modifier settings |

### Options Menu (During Song Select)

Accessed by pressing and holding the Start button or double-tapping Start. A semi-transparent overlay appears with scrollable option categories:

- Speed (x0.25 - x8.0)
- Boost / Brake / Wave
- Appearance (Visible / Hidden+ / Sudden+ / Stealth)
- Turn (Off / Mirror / Left / Right / Shuffle)
- Scroll (Normal / Reverse)
- Arrow Skin (NOTE / VIVID / FLAT / RAINBOW)
- Screen Filter (Off / Dark levels)
- Guideline (Off / On)
- Gauge Type (Normal / LIFE4 / RISKY / Flare)
- Assist Options (Freeze Off / Jump Off / Auto Velocity)

---

## 13. Stage Progression

### Standard Play (3-Stage System)

| Stage | Name | Description |
|-------|------|-------------|
| 1st Stage | 1st Stage | First song; player selects freely from available songs |
| 2nd Stage | 2nd Stage | Second song; player selects freely |
| Final Stage | Final Stage | Third and typically last song; player selects freely |

After the Final Stage, the game proceeds to the total results screen unless Extra Stage conditions are met.

### Stage Count

- Standard (coin) play: 3 stages
- Premium Play (e-Amusement card): Typically 3 stages; may be extended to 4 or more depending on operator settings
- Event modes: Operator-configurable stage count (1-5+)

### Extra Stage System

The Extra Stage is a bonus stage available after the Final Stage under specific conditions. Its requirements have varied across DDR versions.

#### Extra Stage Access (DDR X3 / A / A20 — Result Star System)

| Property | Value |
|----------|-------|
| System | Result Stars accumulated across all stages |
| Stars needed | 9 stars total to unlock Extra Stage |
| Stars per song | Maximum 3 stars per song per player |
| Star awards | AAA grade = 3 stars; AA- or higher = 2 stars; A+ or lower = 1 star |
| Bonus star | +1 star for Full Combo or playing on LIFE4/RISKY gauge (up to max of 3) |
| Both players | Stars from both players are combined (in Versus mode) |
| Carryover | If Extra Stage not reached, star progress carries to the next credit |

#### Extra Stage Conditions (Classic: DDR Extreme)

| Condition | Requirement |
|-----------|------------|
| Final Stage grade | AA or higher on Expert (Heavy) difficulty |
| Forced song | Specific song predetermined by the game version (e.g., MAX 300 in DDRMAX) |
| Forced options | Typically: 1.5x speed, Reverse, Dark, and non-recovering life gauge |

### Encore Extra Stage / One More Extra Stage

| Property | Value |
|----------|-------|
| Condition | Achieve AA or higher on the Extra Stage song on Expert difficulty |
| Forced song | A specific predetermined boss song |
| Forced gauge | Non-recovering gauge (starts full, only drains) |
| Reward | Exclusive song unlock, special ending screen, or achievement |
| Availability | Present in DDRMAX through DDR X3 vs 2ndMIX; format varies in later versions |

---

## 14. Groove Radar

The Groove Radar is a pentagon-shaped chart displayed on the song select screen that provides a visual representation of a chart's characteristics across 5 axes. It was introduced in DDRMAX (6thMIX).

### Groove Radar Parameters

| Parameter | Position | Measures | Calculation Basis |
|-----------|----------|----------|-------------------|
| Stream | Top | Overall note density relative to song length | Total number of notes divided by song length |
| Voltage | Upper-right | Peak note density (busiest section) | Maximum notes in any 4 consecutive beats, relative to average BPM |
| Air | Lower-right | Number of jumps (and Shock Arrows in DDR X+) | Jump count relative to song length |
| Freeze | Lower-left | Total length of freeze arrows | Sum of freeze arrow durations (in beats) relative to total beats in the song |
| Chaos | Upper-left | Off-beat note density and complexity | Count of notes not on 4th-note beats; increased by BPM changes and stops |

### Groove Radar Scale

| Property | Value |
|----------|-------|
| Minimum value | 0 |
| Maximum value | 200 (values can technically exceed 100 and overflow the pentagon visually) |
| Display | Values 0-100 fit within the pentagon outline; values above 100 extend beyond the outline |
| Visual | Each axis extends from center (0) to the pentagon vertex (100); a filled polygon connects the 5 values |

---

## 15. Audio System

### Music Playback

| Property | Value |
|----------|-------|
| Format | Pre-rendered audio tracks (MP3, OGG, or proprietary format depending on platform) |
| Sample rate | 44,100 Hz (CD quality) |
| Channels | Stereo (2-channel) |
| Sync method | Music playback is the master clock; note positions are defined relative to beat timestamps |
| Offset calibration | Global audio offset setting (in ms) to compensate for hardware latency |

### Sound Effects

| Event | Sound |
|-------|-------|
| Tap note hit | Percussive "clap" or "tap" sound (optional; can be toggled) |
| Freeze arrow hold | Continuous tone or hum while held |
| Shock arrow NG | Electric zap / shock sound effect |
| Combo milestone (50, 100, etc.) | Ascending chime or flourish |
| Danger (low gauge) | Heartbeat or alarm sound loop |
| Stage failed | Dramatic failure sound / record scratch |
| Stage cleared | Triumphant fanfare |
| Song select scroll | Click/tick sound per song scrolled |
| Timer warning | Beeping sound when selection timer is low |

### Keysound System

- DDR does **not** use a keysound system (unlike IIDX/beatmania).
- The music plays as a pre-mixed track regardless of player input.
- Player accuracy does not affect the music output.
- Some versions may dim or alter background music audio on stage failure.

---

## 16. Visual Feedback System

### Judgment Display

| Judgment | Text Display | Color | Animation |
|----------|-------------|-------|-----------|
| Marvelous | "MARVELOUS!!" | White / Rainbow shimmer | Large, bright flash with particle burst |
| Perfect | "PERFECT!" | Yellow / Gold | Bright flash, slightly smaller than Marvelous |
| Great | "GREAT" | Green | Moderate flash |
| Good | "GOOD" | Blue / Light purple | Subdued flash |
| Miss | "MISS" or red X | Red | No positive flash; note falls through with failure animation |

- Judgment text appears at the center of the playfield, briefly displayed then fading.
- Each new judgment replaces the previous judgment text.
- An optional "FAST" or "SLOW" sub-indicator may appear above or below the judgment text showing timing direction.

### Receptor (Step Zone) Feedback

| Event | Visual |
|-------|--------|
| Beat pulse | All 4 receptors flash white on each quarter-note beat |
| Note hit (Marvelous) | Receptor flashes bright white with expanding glow ring |
| Note hit (Perfect) | Receptor flashes yellow |
| Note hit (Great) | Receptor flashes green |
| Note hit (Good) | Receptor flashes dim blue |
| Note hit (Miss) | No flash; receptor remains static |
| Freeze hold active | Receptor glows continuously in green while panel is held |

### Combo Display

| Property | Description |
|----------|-------------|
| Position | Below the judgment text, centered on playfield |
| Visibility | Appears at combo 4 and above |
| Format | Numeric value with "COMBO" label beneath |
| Color | Matches combo state: White (all Marvelous), Yellow (Marvelous/Perfect), Green (includes Great) |
| Animation | Number scales up briefly on each increment |

### Dance Gauge Visual

| State | Appearance |
|-------|-----------|
| Normal (above 80%) | Green bar, smoothly filling/draining |
| Caution (20% - 80%) | Yellow/orange bar with slight pulsing |
| Danger (below 20%) | Red flashing bar; screen edges may flash red; heartbeat sound |
| Empty (0%) | Bar empty; FAILED text appears; screen darkens |
| Full (100%) | Green bar fully filled; may glow or shimmer |

### Background Visuals

| Element | Description |
|---------|-------------|
| Music video | Some songs have associated background videos that play behind the arrow highway |
| Background animation | Procedurally generated or pre-rendered visual effects synchronized to the music |
| 3D dancer | An animated 3D character model that performs dance moves in sync with the player's steps (featured in many DDR versions) |
| Stage effects | Lighting effects, color washes, and particle effects that intensify with combo and performance |

### Results Screen

| Element | Description |
|---------|-------------|
| Grade | Large letter grade displayed prominently (AAA through E) |
| Score | Final numeric score out of 1,000,000 |
| EX Score | Secondary score displayed below the main score |
| Max Combo | Longest consecutive combo achieved |
| Judgment breakdown | Count of each judgment type: Marvelous, Perfect, Great, Good, Miss, OK, NG |
| Full Combo indicator | MFC/PFC/GFC/FC badge if applicable |
| Clear type | Clear / Assist Clear / Failed lamp |
| Flare Points | Points earned toward Flare Skill ranking (DDR A3+) |
| New Record | Highlighted if the score exceeds the player's previous best for this song/difficulty |

---

## 17. Step Chart Format

### SM File Format (StepMania Standard)

Step charts are commonly stored in the .SM file format (StepMania format), which has become the de facto standard for DDR chart data in simulators and community tools.

#### File Structure

```
#TITLE:Song Title;
#SUBTITLE:;
#ARTIST:Artist Name;
#TITLETRANSLIT:;
#SUBTITLETRANSLIT:;
#ARTISTTRANSLIT:;
#GENRE:;
#CREDIT:Chart Author;
#BANNER:banner.png;
#BACKGROUND:bg.png;
#CDTITLE:cdtitle.png;
#MUSIC:song.ogg;
#OFFSET:0.000;
#SAMPLESTART:45.000;
#SAMPLELENGTH:15.000;
#SELECTABLE:YES;
#BPMS:0.000=150.000;
#STOPS:;
#NOTES:
     dance-single:
     Chart Author:
     Expert:
     15:
     0.800,0.900,0.200,0.100,0.600:
<note data>
;
```

#### Note Data Encoding

Each row in the note data represents one time position. Each character represents one column (panel):

| Column Position | Panel (dance-single) |
|----------------|---------------------|
| 1st character | Left |
| 2nd character | Down |
| 3rd character | Up |
| 4th character | Right |

| Character | Meaning |
|-----------|---------|
| 0 | No note |
| 1 | Tap note |
| 2 | Freeze arrow head (start of hold) |
| 3 | Freeze arrow tail (end of hold) |
| 4 | Roll head (start of roll; not in classic DDR) |
| M | Mine / Shock arrow |

#### Measure Division

- Each measure is separated by a comma.
- The number of rows per measure determines the beat subdivision:
  - 4 rows = quarter notes (4th notes)
  - 8 rows = 8th notes
  - 12 rows = 12th notes (triplets)
  - 16 rows = 16th notes
  - 24 rows = 24th notes
  - 32 rows = 32nd notes
  - 48 rows = 48th notes
  - 64 rows = 64th notes
  - 192 rows = 192nd notes (maximum practical subdivision)

#### Example: One Measure of 8th Notes

```
1000    <- Left arrow on beat 1
0000    <- rest on beat 1.5
0010    <- Up arrow on beat 2
0000    <- rest on beat 2.5
0001    <- Right arrow on beat 3
0000    <- rest on beat 3.5
0100    <- Down arrow on beat 4
0000    <- rest on beat 4.5
```

#### Example: Jump Notes

```
1001    <- Left + Right simultaneously (a jump)
0000
0110    <- Down + Up simultaneously (a jump)
0000
```

#### Example: Freeze Arrow

```
2000    <- Freeze head on Left
0000
0000
3000    <- Freeze tail on Left (hold from beat 1 to beat 4)
```

### BPM and Timing Data

```
#BPMS:0.000=140.000,48.000=170.000,96.000=140.000;
```

This defines BPM changes at specific beat positions: starts at 140 BPM, changes to 170 BPM at beat 48, returns to 140 BPM at beat 96.

### Stops

```
#STOPS:24.000=0.500,48.000=1.000;
```

This defines scroll stops: a 0.5-second pause at beat 24 and a 1.0-second pause at beat 48. During stops, the arrows freeze in place but the music continues.
