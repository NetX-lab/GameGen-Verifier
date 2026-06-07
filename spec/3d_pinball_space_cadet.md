# 19_3d_pinball_space_cadet - 3D Pinball: Space Cadet (Faithful Recreation)

## 1. Game Overview

- **Reference**: 3D Pinball for Windows -- Space Cadet, originally developed by Cinematronics and Maxis as part of Full Tilt! Pinball (1995). The Space Cadet table was bundled with Microsoft Plus! 95 and later included in Windows NT 4.0, Windows 2000, Windows Me, and Windows XP.
- **Genre**: Pinball Simulation
- **Core Fantasy**: The player is a space fleet cadet operating a single-table pinball machine themed around a military space program. Complete missions to rise through nine ranks from Cadet to Fleet Admiral, mastering the table's ramps, bumpers, lanes, and special features.
- **Presentation**: 2D pre-rendered graphics viewed from a top-down perspective with slight perspective tilt. The table occupies the left portion of the screen; the right side displays score, ball count, and mission status.
- **Target Session**: 5-30 minutes per game (3 balls default).
- **Skill Curve**: Immediately playable with two-button flipper controls; deep mastery through mission sequencing, multiplier management, and precision shots.

---

## 2. Technical Foundation

| Parameter | Value |
|---|---|
| Original resolution | 640 x 480 pixels (fixed) |
| Full Tilt! resolution | Up to 1024 x 768 pixels (3 resolution options) |
| Frame rate | Variable; Raymond Chen added a frame-rate cap for Windows XP to reduce CPU usage |
| Physics tick rate | Tied to frame rate; physics engine by Mike Sandige, data-driven with scripting system |
| Coordinate system | 2D pixel coordinates; origin at top-left of window |
| Gravity direction | Ball accelerates downward (positive Y) toward drain |
| Programming language | Originally Delphi, translated to C/C++ with x86 assembly segments |
| Graphics engine | Pre-rendered 3D sprites created in TrueSpace; backgrounds and UI in Adobe Photoshop |
| Audio | Composed by Matt Ridgeway; WAV-format sound effects and MIDI music |
| Platform | Windows 95/NT 4.0/2000/Me/XP; decompiled C++ port available (k4zmu2a/SpaceCadetPinball) |
| Ball count (default) | 3 balls per game |
| High score table | Top 5 scores stored locally |
| Default high score | 0 points |

---

## 3. Win / Lose Contract

| Condition | Description |
|---|---|
| **No explicit win** | The game has no final victory screen; the objective is to achieve the highest score and attain the rank of Fleet Admiral |
| **Game Over** | All balls (default 3) have drained without extra balls or replays remaining |
| **Drain** | Ball falls below the flippers into the drain area at the bottom of the table |
| **Tilt** | Holding a nudge key too long causes a TILT; the current ball is forfeit (flippers become inoperable, ball drains) |
| **Replay threshold** | Not a fixed value; replay ball is awarded through the wormhole mechanic (see Section 10.2) |

---

## 4. Controls

### 4.1 Default Keyboard Mapping

| Action | Key | Description |
|---|---|---|
| Left Flipper | `Z` | Activates the left flipper |
| Right Flipper | `/` (forward slash) | Activates the right flipper |
| Plunger | `Space` | Hold to pull back plunger; release to launch ball. Longer hold = stronger launch |
| Nudge Left | `X` | Bumps the table to the left |
| Nudge Right | `.` (period) | Bumps the table to the right |
| Nudge Up | `Up Arrow` | Bumps the table upward |
| Pause | `F3` | Pauses and hides the table |
| New Game | `F2` | Starts a new game |
| Player Controls | `F8` | Opens control customization dialog |

### 4.2 Tilt Mechanic

| Parameter | Value |
|---|---|
| Trigger | Holding any nudge key for too long, or excessive nudging in rapid succession |
| Effect | Table displays "TILT"; flippers become inoperable; ball drains without scoring |
| Penalty | Current ball is lost; no bonus is awarded for that ball |
| Recovery | Next ball (if available) begins normally |

---

## 5. Table Layout

The table is a vertically-oriented playfield viewed from above. Ball flows generally from top (launch) to bottom (drain). The following sections describe every major element and its position on the table.

### 5.1 Table Regions (Top to Bottom)

```
+========================================================+
|  [Satellite Bumper]      [Re-entry Lanes (3)]          |
|         (top-left)        (top-center/right)            |
|                                                         |
|  [Space Warp            [Attack Bumpers (3)]            |
|   Rollover]              (upper-center)                 |
|                                                         |
|  [Left Hazard    [Field Multiplier   [Right Hazard      |
|   Targets (3)]    Drop Targets (3)]   Targets (3)]      |
|                                                         |
|  [Green                              [Red Wormhole]     |
|   Wormhole]     [Fuel Chute          [Hyperspace        |
|                  (left ramp)]         Chute (right)]    |
|                                                         |
|  [Launch Platform]                   [Deployment        |
|  [Engine Bumpers (3)]                 Chute]            |
|  [Engine Lanes (3)]                                     |
|                                                         |
|  [Launch Ramp]  [Yellow Wormhole]    [Booster           |
|                                       Targets]          |
|                                                         |
|  [Mission Target                     [Hyperspace        |
|   Bank (3)]                           Flag]             |
|                                                         |
|  [Medal Targets (3)]                                    |
|                                                         |
|  [Left Rebound]          [Right Rebound]                |
|  [Left Return   [Center  [Right Return                  |
|   Lane]          Post]    Lane]                         |
|  [Left Out Lane] [Drain] [Right Out Lane]               |
|  [Left Kicker]           [Right Kicker]                 |
|        [Left Flipper]  [Right Flipper]                  |
|              [====DRAIN AREA====]                       |
+========================================================+
```

### 5.2 Detailed Element Inventory

#### Flippers

| Element | Position | Description |
|---|---|---|
| Left Flipper | Bottom-left of playfield | Standard pinball flipper; activated by `Z` key |
| Right Flipper | Bottom-right of playfield | Standard pinball flipper; activated by `/` key |

#### Plunger / Deployment Chute

| Element | Position | Description |
|---|---|---|
| Plunger | Bottom-right, behind right flipper | Spring-loaded rod; hold Space to compress, release to launch |
| Deployment Chute | Right side, vertical channel | Ball travels upward from plunger to top of table; contains 6 yellow skill shot lights |

#### Bumpers

| Element | Count | Position | Description |
|---|---|---|---|
| Attack Bumpers | 3 | Upper-center of table, below re-entry lanes | Pop bumpers that upgrade color via re-entry lanes |
| Satellite Bumper | 1 | Top-left of table | Remote attack bumper; upgrades with the attack bumpers |
| Engine Bumpers | 3 | On the launch platform (middle-left) | Pop bumpers accessed via launch ramp; upgrade via engine lanes |

#### Lanes

| Element | Count | Position | Description |
|---|---|---|---|
| Re-entry Lanes | 3 | Top of table, above attack bumpers | Ball rolls through; lighting all 3 upgrades attack bumpers |
| Engine Lanes | 3 | On launch platform | Ball rolls through; lighting all 3 upgrades engine bumpers |
| Return Lanes | 2 | Above each flipper, behind rebounds | Return ball safely to flippers; 2,500 points each |
| Out Lanes | 2 | Outer lanes at bottom beside kickers | Ball passing through drains; 20,000 points awarded |
| Launch Ramp | 1 | Left side, ascending to launch platform | Primary ramp for mission acceptance and accessing engine area |
| Fuel Chute | 1 | Left side, ascending to top of table | Ramp leading to top of table; passes fuel flag |
| Hyperspace Chute | 1 | Right side, ascending to hyperspace kickout | Ramp leading to hyperspace kicker; passes hyperspace flag |

#### Target Banks

| Element | Count | Position | Description |
|---|---|---|---|
| Mission Targets | 3 | Below launch ramp, above left flipper | Spot targets; hitting one selects a mission (1,000 pts each) |
| Field Multiplier Drop Targets | 3 | Upper-center, above left of attack bumpers | Drop targets; clearing all 3 advances field multiplier |
| Left Hazard (Radiation) Targets | 3 | Left of attack bumpers | Spot targets (750 pts each); used in Space Radiation mission |
| Right Hazard (Comet) Targets | 3 | Right of attack bumpers | Spot targets (750 pts each); used in Stray Comet mission |
| Medal Targets | 3 | Below mission targets, above flippers | Drop targets; clearing all 3 with extra ball light on awards extra ball (1,500 pts each) |
| Booster Targets | 3 | Right side, entrance to hyperspace chute | Spot targets (750 pts each); lighting all 3 activates booster |
| Fuel Targets | Varies | Along fuel chute | Spot targets (750 pts each); fill fuel gauge |

#### Special Features

| Element | Position | Description |
|---|---|---|
| Black Hole Kickout | Under the launch ramp | Kicker that captures and ejects ball; 20,000 points |
| Hyperspace Kickout | Upper-right, at end of hyperspace chute | Kicker with escalating rewards based on hyperspace lights |
| Gravity Well | Center of lower playfield light circle | When activated, captures ball and ejects randomly; 50,000 points |
| Wormhole (Yellow) | Center-right of mid-table | One of three wormholes; teleports ball based on destination lights |
| Wormhole (Red) | Upper-right, below re-entry lanes | Second wormhole |
| Wormhole (Green) | Upper-left, near satellite bumper | Third wormhole |
| Space Warp Rollover | Top of table, below satellite bumper | Green oval rollover; 10,000 points |
| Hyperspace Flag | Entrance to hyperspace chute | Spinning flag; points based on booster status |
| Fuel Flag | Top of fuel chute | Spinning flag; points based on booster status |
| Center Post | Between flippers, above drain | Retractable post preventing center drain; activated via hyperspace |
| Left Out Lane Kicker | Left out lane | Kicker that can save ball from draining |
| Right Out Lane Kicker | Right out lane | Kicker that can save ball from draining |
| Rebounds | 4 | Rubber bumpers: 1 above each flipper, 1 below right hazard, 1 right of left hazard |

---

## 6. Ball Physics

### 6.1 Physics Engine Overview

The physics engine was built by Mike Sandige and is almost entirely data-driven with a scripting system for fine-tuning table behavior. All physics values below are derived from the decompiled source code and observed behavior.

### 6.2 Core Physics Parameters

| Parameter | Description |
|---|---|
| Gravity | Constant downward acceleration applied each physics tick; ball accelerates toward drain |
| Friction | Surface friction slows rolling ball; different coefficients for table surface vs. ramp surfaces |
| Elasticity (Rebounds) | Rubber rebounds apply velocity reflection with energy coefficient < 1.0 (some energy lost) |
| Elasticity (Bumpers) | Pop bumpers apply an outward impulse force; bumper hits add energy to the ball |
| Ball mass | Uniform; single ball in play at all times |
| Ball radius | Approximately 8-10 pixels at 640x480 resolution |
| Collision detection | Circle-vs-line and circle-vs-circle; tested each physics tick |
| Maximum velocity | Engine-capped to prevent tunneling through thin walls |

### 6.3 Flipper Physics

| Parameter | Description |
|---|---|
| Flipper rotation | Flippers rotate around a pivot point from rest position (~30 deg below horizontal) to engaged position (~30 deg above horizontal) |
| Flipper angular velocity | High-speed rotation on activation; returns to rest at moderate speed on release |
| Ball interaction | Ball receives velocity based on flipper angular velocity at contact point and ball position along flipper length |
| Tip vs. base | Shots from flipper tip produce faster, more angled trajectories; base shots are slower and more vertical |
| Hold behavior | Holding the flipper key keeps the flipper in the engaged position; ball can rest on a held flipper |
| Dead flipper pass | Ball can roll across a non-engaged flipper to transfer between sides |

### 6.4 Plunger Physics

| Parameter | Description |
|---|---|
| Compression | Plunger compresses linearly while Space is held |
| Maximum compression | Reached after approximately 1-2 seconds of holding |
| Launch force | Proportional to compression distance; determines how high ball travels up deployment chute |
| Skill shot | Partial compression allows ball to reach specific skill shot light positions in the deployment chute |

---

## 7. Scoring System

### 7.1 Bumper Scoring

Attack Bumpers, the Satellite Bumper, and Engine Bumpers have four upgrade levels indicated by color. They advance when their associated lane set is fully lit.

#### Attack Bumpers (3) and Satellite Bumper (1)

| Color Level | Points per Hit | Upgrade Condition |
|---|---|---|
| Blue (default) | 500 | Starting state |
| Green | 1,000 | Light all 3 re-entry lanes once |
| Yellow | 1,500 | Light all 3 re-entry lanes twice |
| Red | 2,000 | Light all 3 re-entry lanes three times |

Bumper color resets to Blue after 60 seconds of inactivity (no re-entry lane completions).

#### Engine Bumpers (3)

| Color Level | Points per Hit | Upgrade Condition |
|---|---|---|
| Blue (default) | 1,500 | Starting state |
| Green | 2,500 | Light all 3 engine lanes once |
| Yellow | 3,500 | Light all 3 engine lanes twice |
| Red | 4,500 | Light all 3 engine lanes three times |

Engine bumper color resets after 60 seconds of inactivity.

### 7.2 Target Scoring

| Target | Points per Hit | Special Effect |
|---|---|---|
| Mission Targets (3 spot targets) | 1,000 | Selects/displays available mission |
| Field Multiplier Drop Targets (each) | 500 | -- |
| Field Multiplier Drop Targets (all 3 cleared) | 1,500 bonus | Advances field multiplier one level |
| Left Hazard / Radiation Targets (each) | 750 | Lights hazard bank lights |
| Right Hazard / Comet Targets (each) | 750 | Lights hazard bank lights |
| Medal Targets (each drop) | 1,500 | Clearing all 3 with extra ball light lit awards extra ball |
| Booster Targets (each) | 750 | Lighting all 3 activates booster mode |
| Fuel Targets (each) | 750 | Fills fuel gauge |

### 7.3 Lane Scoring

| Lane | Points | Notes |
|---|---|---|
| Re-entry Lane (each pass) | Varies by context | Lights one of 3 re-entry lights; all 3 lit upgrades attack bumpers |
| Engine Lane (each pass) | Varies by context | Lights one of 3 engine lights; all 3 lit upgrades engine bumpers |
| Return Lane (each pass) | 2,500 | Ball returns safely to flipper |
| Out Lane (each pass) | 20,000 | Ball typically drains after passing through |
| Launch Ramp (successful pass) | Varies | Initiates mission acceptance; awards points based on mission state |

### 7.4 Special Feature Scoring

| Feature | Points | Additional Effect |
|---|---|---|
| Black Hole Kickout | 20,000 | Ball captured and ejected |
| Hyperspace Kickout (0 lights) | 5,000 | Basic award |
| Hyperspace Kickout (1 light) | 10,000 | Hyperspace Bonus awarded |
| Hyperspace Kickout (2 lights) | 20,000 | Center Post activated |
| Hyperspace Kickout (3 lights) | 50,000 | Extra ball lights turned on in out lanes |
| Hyperspace Kickout (4 lights) | 150,000 | Gravity Well activated |
| Gravity Well capture | 50,000 | Ball ejected in random direction |
| Space Warp Rollover | 10,000 | Green oval at top of table |
| Wormhole (closed, same exit) | 2,000 | Destination light off; ball ejected from same wormhole |
| Wormhole (open, different exit) | 7,500 | Ball teleported to destination wormhole |
| Wormhole (open, same wormhole as destination) | 5,000 | Ball exits same wormhole + Replay Ball awarded |

### 7.5 Flag Scoring

| Flag State | Points per Half-Spin |
|---|---|
| No Booster lit | 500 |
| Booster lit | 2,500 |

Both the Hyperspace Flag (at hyperspace chute entrance) and the Fuel Flag (at fuel chute top) use this scoring.

### 7.6 Skill Shot (Deployment Chute)

The deployment chute contains 6 yellow arch lights. A partial plunger launch that lands the ball on a specific light awards bonus points:

| Light Position | Points |
|---|---|
| 1st (lowest) | 15,000 |
| 2nd | 30,000 |
| 3rd (highest value) | 75,000 |
| 4th | 30,000 |
| 5th | 15,000 |
| 6th (highest, full launch) | 7,500 |

The 3rd light from the bottom is the optimal skill shot target, awarding the maximum 75,000 points.

### 7.7 Bonus System

| Parameter | Description |
|---|---|
| Bonus accumulation | Points are added to the bonus counter as scoring events occur during ball play |
| Maximum bonus | 75,000 points (all bonus lights lit) |
| Minimum bonus | 7,500 points |
| Bonus award | Awarded when ball drains normally (not on tilt, not on replay) |
| Bonus reset | Bonus counter resets when ball drains and bonus is collected |
| Replay exception | On replay ball, no bonus is awarded and the table does not reset |

---

## 8. Field Multiplier System

### 8.1 Multiplier Levels

The field multiplier affects all points scored on the table. It is advanced by clearing all 3 field multiplier drop targets.

| Level | Multiplier | How to Reach |
|---|---|---|
| 1 (default) | 1x | Starting state |
| 2 | 2x | Clear drop targets once |
| 3 | 3x | Clear drop targets twice |
| 4 | 5x | Clear drop targets three times |
| 5 | 10x | Clear drop targets four times |

### 8.2 Multiplier Decay

| Parameter | Value |
|---|---|
| Decay timer | 60 seconds |
| Behavior | The topmost lit field multiplier light resets after 60 seconds of no new drop target completions |
| Full decay | If no targets are hit, multiplier decays one level every 60 seconds until it returns to 1x |

### 8.3 Extended Multipliers (Cheat / Hidden)

When all 4 standard multiplier lights are lit (10x), further advancement is possible through hidden commands or repeated target completion:

| Level | Multiplier | Notes |
|---|---|---|
| 6 | 20x | Fifth full drop target clear (or cheat code) |
| 7 | 50x | Sixth full clear |
| 8 | 100x | Seventh full clear; multiplier no longer decays on timer |

---

## 9. Rank Progression System

### 9.1 Rank Hierarchy

There are 9 ranks. The player begins at Cadet (Rank 1). Rank is displayed by 9 yellow lights in a circle at the bottom-center of the table.

| Rank Number | Rank Name | Yellow Lights Lit |
|---|---|---|
| 1 | Cadet | 1 |
| 2 | Ensign | 2 |
| 3 | Lieutenant | 3 |
| 4 | Captain | 4 |
| 5 | LT Commander | 5 |
| 6 | Commander | 6 |
| 7 | Commodore | 7 |
| 8 | Admiral | 8 |
| 9 | Fleet Admiral | 9 |

### 9.2 Progress Lights

| Parameter | Value |
|---|---|
| Progress light count | 18 blue lights arranged in a circle at bottom-center |
| Advancement | When all 18 progress lights are lit, the player advances one rank |
| Progress per mission | Varies by mission (6 to 18 progress lights per mission completion) |
| Reset on promotion | All 18 progress lights reset to unlit upon rank advancement |

### 9.3 Promotion Rules

- Completing missions fills progress lights. Different missions award different numbers of lights.
- A player does not need to complete all available missions; any combination that fills all 18 lights triggers promotion.
- The same mission can be repeated multiple times within a rank.
- At higher ranks, certain missions (e.g., Cosmic Plague, Secret Mission) can shortcut promotion by awarding large numbers of progress lights.
- The Time Warp mission can promote OR demote the player depending on the chosen warp direction.

---

## 10. Mission System

### 10.1 Mission Activation

| Step | Description |
|---|---|
| 1. Select mission | Hit one of the 3 Mission Target Bank spot targets (awards 1,000 points). The info display shows the available mission name. |
| 2. Accept mission | Send the ball up the Launch Ramp. Display shows "MISSION ACCEPTED." |
| 3. Complete objectives | Blinking blue arrows on the table indicate where the ball must go. Complete all required steps. |
| 4. Collect reward | Points and progress lights are awarded upon final objective completion. |
| 5. Abort/fail | Mission can be abandoned by selecting a new mission target. Active missions persist across ball drains within the same game. |

### 10.2 Mission Acceptance Points

| Event | Points |
|---|---|
| Accepting any mission | 30,000 |

### 10.3 Cadet Missions (Rank 1)

Available at rank: **Cadet**

#### Mission: Re-entry Training

| Parameter | Value |
|---|---|
| Objective | Send the ball through any of the 3 re-entry lanes, 3 times total |
| Reward | 500,000 points + 6 progress lights |
| Difficulty | Easy |

#### Mission: Launch Training

| Parameter | Value |
|---|---|
| Objective | Send the ball past the red light on the launch ramp, 3 times |
| Reward | 500,000 points + 6 progress lights |
| Difficulty | Easy |

#### Mission: Target Practice

| Parameter | Value |
|---|---|
| Objective | Hit attack bumpers 8 times total |
| Reward | 500,000 points + 6 progress lights |
| Difficulty | Easy |

#### Mission: Science

| Parameter | Value |
|---|---|
| Objective | Hit 9 drop targets (any combination of field multiplier and medal drop targets) |
| Reward | 750,000 points + 9 progress lights |
| Difficulty | Medium |

### 10.4 Ensign / Lieutenant Missions (Ranks 2-3)

Available at ranks: **Ensign**, **Lieutenant**

#### Mission: Bug Hunt

| Parameter | Value |
|---|---|
| Objective | Hit 15 targets of any type |
| Reward | 750,000 points + 7 progress lights |
| Difficulty | Easy |

#### Mission: Rescue

| Parameter | Value |
|---|---|
| Objective | Step 1: Upgrade the flags by lighting all 3 booster targets. Step 2: Enter the hyperspace kickout while flags are upgraded |
| Reward | 750,000 points + 7 progress lights |
| Difficulty | Medium |
| Note | If flags degrade before entering the hyperspace kickout, they must be re-upgraded |

#### Mission: Alien Menace

| Parameter | Value |
|---|---|
| Objective | Step 1: Upgrade the attack bumpers by lighting all 3 re-entry lanes. Step 2: Hit attack bumpers 12 times |
| Reward | 750,000 points + 7 progress lights |
| Difficulty | Medium |

#### Mission: Secret

| Parameter | Value |
|---|---|
| Objective | Enter the Yellow wormhole, then the Red wormhole, then the Green wormhole (in that specific order) |
| Reward | 1,500,000 points + 10 progress lights |
| Difficulty | Hard |
| Note | Completing 2 Secret Missions achieves immediate rank promotion |

### 10.5 Captain / LT Commander Missions (Ranks 4-5)

Available at ranks: **Captain**, **LT Commander**

#### Mission: Stray Comet

| Parameter | Value |
|---|---|
| Objective | Step 1: Light up all 3 Right Hazard (Comet) targets. Step 2: Enter the hyperspace kickout |
| Reward | 1,000,000 points + 8 progress lights |
| Difficulty | Medium |
| Note | No time constraint on Step 2 after completing Step 1 |

#### Mission: Space Radiation

| Parameter | Value |
|---|---|
| Objective | Step 1: Light up all 3 Left Hazard (Radiation) targets. Step 2: Enter any wormhole |
| Reward | 1,000,000 points + 8 progress lights |
| Difficulty | Medium |

#### Mission: Black Hole Threat

| Parameter | Value |
|---|---|
| Objective | Step 1: Upgrade launch (engine) bumpers to maximum (Red) by completing engine lanes multiple times. Step 2: Enter the black hole kickout |
| Reward | 1,000,000 points + 8 progress lights |
| Difficulty | Hard |

#### Mission: Cosmic Plague

| Parameter | Value |
|---|---|
| Objective | Step 1: Hit the flags until the flag hit counter decrements from 75 to 0. Step 2: Hit the Space Warp Rollover |
| Reward | 1,750,000 points + 11 progress lights |
| Difficulty | Easy (despite many hits required, flags are reliably targetable) |
| Note | Completing a Cosmic Plague + one other mission (even another Cosmic Plague) achieves promotion |

### 10.6 Commander / Commodore Missions (Ranks 6-7)

Available at ranks: **Commander**, **Commodore**

#### Mission: Satellite Retrieval

| Parameter | Value |
|---|---|
| Objective | Hit the Satellite Bumper 3 times |
| Reward | 1,250,000 points + 9 progress lights |
| Difficulty | Hard (Satellite Bumper is in the top-left, difficult to target) |
| Strategy | Use the Fuel Chute and Green Wormhole to direct ball toward the Satellite Bumper |

#### Mission: Recon Mission

| Parameter | Value |
|---|---|
| Objective | Pass through any lanes 15 times total |
| Reward | 1,250,000 points + 9 progress lights |
| Difficulty | Medium |
| Strategy | Sending ball up the Launch Ramp guarantees at least 2 lane passes per ramp shot |

#### Mission: Doomsday Machine

| Parameter | Value |
|---|---|
| Objective | Send the ball through the out lanes 3 times |
| Reward | 1,250,000 points + 9 progress lights |
| Difficulty | Very Hard (out lanes typically drain the ball) |
| Note | On entry to an out lane, its gate closes. Reopen by lighting all 3 hazard target banks or having a replay ball active |

#### Mission: Time Warp

| Parameter | Value |
|---|---|
| Objective | Step 1: Hit rebound bumpers 25 times. Step 2: Choose time warp direction |
| Reward (Forward) | Advance to Admiral rank (rank 8) by sending ball up the Launch Ramp |
| Reward (Backward) | Demote by 1 rank by sending ball into the Hyperspace Chute |
| Points | 1,250,000 |
| Progress Lights | 9 |
| Difficulty | Medium |
| Note | Forward warp skips ranks; backward warp demotes (Commander to LT Commander, or Commodore to Commander) |

### 10.7 Admiral / Fleet Admiral Missions (Ranks 8-9)

Available at ranks: **Admiral**, **Fleet Admiral**

#### Mission: Secret (Repeated)

Same as Ensign/Lieutenant Secret mission (Yellow, Red, Green wormhole sequence). Awards 1,500,000 points + 10 progress lights.

#### Mission: Cosmic Plague (Repeated)

Same as Captain/LT Commander Cosmic Plague (flag counter 75 to 0, then Space Warp Rollover). Awards 1,750,000 points + 11 progress lights.

#### Mission: Time Warp (Repeated)

Same as Commander/Commodore Time Warp (25 bumper hits, choose direction). Backward warp demotes rank.

#### Mission: Maelstrom

| Parameter | Value |
|---|---|
| Objective | Complete all 8 steps in sequence: |
| Step 1 | Hit any drop target 3 times |
| Step 2 | Hit any spot target 3 times |
| Step 3 | Pass the ball through any lane 5 times |
| Step 4 | Send ball up the fuel chute |
| Step 5 | Send ball up the launch ramp |
| Step 6 | Hit one of the flags |
| Step 7 | Enter a wormhole |
| Step 8 | Enter the hyperspace kickout |
| Reward | 5,000,000 points + 18 progress lights (instant promotion) |
| Difficulty | Very Hard (8 sequential objectives that must be completed in order) |
| Note | All table lights are turned on upon completion |

### 10.8 Complete Mission Availability by Rank

| Rank | Mission 1 | Mission 2 | Mission 3 | Mission 4 |
|---|---|---|---|---|
| Cadet | Re-entry Training | Launch Training | Target Practice | Science |
| Ensign | Bug Hunt | Rescue | Alien Menace | Secret |
| Lieutenant | Bug Hunt | Rescue | Alien Menace | Secret |
| Captain | Stray Comet | Space Radiation | Black Hole Threat | Cosmic Plague |
| LT Commander | Stray Comet | Space Radiation | Black Hole Threat | Cosmic Plague |
| Commander | Satellite Retrieval | Recon Mission | Doomsday Machine | Time Warp |
| Commodore | Satellite Retrieval | Recon Mission | Doomsday Machine | Time Warp |
| Admiral | Secret | Cosmic Plague | Time Warp | Maelstrom |
| Fleet Admiral | Secret | Cosmic Plague | Time Warp | Maelstrom |

---

## 11. Extra Ball and Replay System

### 11.1 Extra Ball

| Parameter | Description |
|---|---|
| Default ball count | 3 balls per game |
| Extra ball trigger | Light the extra ball lights in the out lanes (via 3 hyperspace kickout entries), then drop all 3 medal targets |
| Extra ball limit | Unlimited; each full set of medal target drops with the light on awards another extra ball |
| Extra ball behavior | After current ball drains, table fully resets and a new ball is placed at the plunger. Ball counter does not advance. Display shows "SHOOT AGAIN" |

### 11.2 Replay Ball

| Parameter | Description |
|---|---|
| Replay trigger | Enter a wormhole that is the same as its currently set destination (i.e., ball enters and exits the same wormhole when that wormhole is its own destination) |
| Replay behavior | After the ball drains, the same ball is placed at the plunger. Table does NOT reset (all targets, lights, mission progress remain as they were). No bonus is awarded. Ball counter does not advance. |
| Replay light | The "Replay" wormhole light indicator is lit when a replay is available |
| Early drain replay | If a ball drains within the first 15 seconds of launch, a replay ball is automatically awarded |

### 11.3 Ball Save Mechanisms

| Mechanism | Description |
|---|---|
| Out Lane Kickers | Kickers in each out lane can activate to kick the ball back into play (activated by lighting hazard targets) |
| Center Post | Retractable post between flippers; prevents center drain. Activated by entering hyperspace kickout with 2 lights lit |
| Center Post duration | Active for a limited time; eventually retracts |

---

## 12. Hyperspace System

The hyperspace system is a multi-level progression tied to the hyperspace kickout. Each entry lights the next hyperspace light (4 lights total around the kickout).

### 12.1 Hyperspace Light Progression

| Lights Lit | Points Awarded | Special Effect |
|---|---|---|
| 0 (no lights) | 5,000 | None |
| 1 | 10,000 | Hyperspace Bonus |
| 2 | 20,000 | Center Post activated |
| 3 | 50,000 | Extra ball lights turned on in out lanes |
| 4 | 150,000 | Gravity Well activated |

### 12.2 Hyperspace Decay

| Parameter | Value |
|---|---|
| Decay timer | 60 seconds |
| Behavior | Hyperspace lights reset after 60 seconds of no hyperspace entries |

---

## 13. Wormhole System

### 13.1 Wormhole Locations

| Wormhole | Color | Position |
|---|---|---|
| Yellow | Yellow | Center-right of mid-table |
| Red | Red | Upper-right, below re-entry lanes |
| Green | Green | Upper-left, near satellite bumper |

### 13.2 Wormhole Destination Lights

Wormhole destination lights are activated by hitting the Space Warp target near the hyperspace chute entrance. Each hit cycles the destination.

### 13.3 Wormhole Behavior

| Destination Light State | Behavior | Points |
|---|---|---|
| Off | Ball ejected from the same wormhole it entered | 2,000 |
| Lit (different wormhole) | Ball teleported to the lit destination wormhole | 7,500 |
| Lit (same wormhole as entry) | Ball exits same wormhole; Replay Ball awarded | 5,000 + Replay |

---

## 14. Booster System

### 14.1 Booster Activation

| Parameter | Description |
|---|---|
| Activation | Light all 3 booster targets (right side of table) |
| Effect | Flags award increased points (500 -> 2,500 per half-spin); flag functionality is "upgraded" |
| Duration | Until booster lights time out or are used for mission completion |
| Decay | Booster lights reset after 60 seconds |

---

## 15. UI Layout

### 15.1 Screen Composition

| Region | Position | Content |
|---|---|---|
| Playfield | Left ~60% of screen | The pinball table with all interactive elements |
| Info Panel | Right ~40% of screen | Score display, mission text, ball counter, rank indicators |

### 15.2 Info Panel Elements

| Element | Position | Description |
|---|---|---|
| Score Display | Top of info panel | Current score in large LED-style digits |
| Mission Display | Middle of info panel | Scrolling text showing current mission name, status, and objectives |
| Ball Counter | Info panel | Shows current ball number (Ball 1, Ball 2, Ball 3, etc.) |
| Rank Lights (9 yellow) | Bottom-center of table | Circle of 9 yellow lights; lit lights indicate current rank |
| Progress Lights (18 blue) | Bottom-center of table | Circle of 18 blue lights; lit lights show mission progress within current rank |
| Player Display | Info panel | Shows current player number (for multiplayer) |

### 15.3 Table Indicators

| Indicator | Description |
|---|---|
| Attack Bumper color | Blue/Green/Yellow/Red glow indicates current bumper level |
| Engine Bumper color | Blue/Green/Yellow/Red glow indicates current bumper level |
| Re-entry lane lights | 3 individual lights above attack bumpers; all lit = bumper upgrade |
| Engine lane lights | 3 individual lights on launch platform; all lit = engine bumper upgrade |
| Hyperspace lights | 4 lights around hyperspace kickout showing progression level |
| Field multiplier lights | 4 lights near drop targets showing current multiplier level |
| Booster lights | 3 lights near booster targets |
| Hazard lights (left) | 3 lights below left hazard targets (blue, red, purple progression) |
| Hazard lights (right) | 3 lights below right hazard targets (blue, red, purple progression) |
| Extra ball lights | Lights in out lanes indicating extra ball is available |
| Wormhole destination lights | Color indicators on each wormhole showing current destination |
| Mission arrows | Blinking blue arrows on table pointing to current mission objective |
| Fuel gauge | Lights along fuel chute showing fuel fill level |
| Deployment chute lights | 6 yellow arch lights in plunger chute for skill shot |

---

## 16. Audio Design

### 16.1 Music

| Element | Description |
|---|---|
| Composer | Matt Ridgeway |
| Background music | Ambient electronic/space-themed soundtrack; MIDI-based in Windows version |
| Full Tilt! version | Higher quality audio with CD-quality music |
| Music behavior | Loops continuously during gameplay; changes intensity during missions |

### 16.2 Sound Effects

| Event | Sound Description |
|---|---|
| Flipper activation | Mechanical click/thwack |
| Ball hit bumper (pop) | Electronic pop/boing with pitch varying by bumper color level |
| Ball hit drop target | Metallic clank |
| Ball hit spot target | Lighter metallic tap |
| Ball enters ramp | Whooshing/ascending tone |
| Ball enters wormhole | Sci-fi warping/teleport sound |
| Ball enters hyperspace | Deeper sci-fi chute sound |
| Ball enters black hole | Ominous swirling sound |
| Gravity well capture | Spiraling electronic capture sound |
| Plunger launch | Spring release mechanical sound |
| Skill shot hit | Triumphant ascending chime |
| Mission accepted | Voice callout / electronic confirmation tone |
| Mission completed | Fanfare/celebration jingle |
| Rank promotion | Extended fanfare with rank announcement |
| Extra ball awarded | "SHOOT AGAIN" voice or distinctive jingle |
| Replay ball | Distinctive electronic replay tone |
| Ball drain | Descending tone / disappointment sound |
| Tilt warning | Warning buzzer |
| Tilt | Harsh buzzer; all sounds stop briefly |
| Medal target drop | Metallic drop sound |
| Multiplier advance | Ascending electronic tone |
| Flag spin | Mechanical spinning/clicking |
| Out lane kicker save | Spring kick sound |
| Center post activation | Mechanical rise sound |
| Game over | Extended descending melody |

### 16.3 Voice Callouts

The game features synthesized voice or text-to-speech style callouts for mission events:

| Event | Callout |
|---|---|
| Mission selected | Mission name displayed on scrolling text display |
| Mission accepted | "MISSION ACCEPTED" |
| Mission objective | Description scrolls across the info display |
| Mission completed | "MISSION COMPLETED" + points display |
| Rank promotion | New rank name displayed prominently |

---

## 17. Menus and Game Options

### 17.1 Menu Bar

| Menu | Options |
|---|---|
| Game | New Game (F2), Launch Ball, Pause/Resume (F3), High Scores, Exit |
| Options | Full Screen, Player Controls (F8), Music, Sound Effects |
| Help | Help Topics, About |

### 17.2 Multiplayer

| Parameter | Value |
|---|---|
| Max players | 4 (hot-seat on same keyboard) |
| Turn order | Sequential; each player completes a ball before the next player takes their turn |
| Scoring | Independent scores for each player |

### 17.3 Cheat Codes (from original game)

| Code | Effect |
|---|---|
| `hidden test` | Activates hidden test mode; click and drag ball with mouse; press `H` for instant 1,000,000,000 points |
| `1max` | Instant max launch on next plunger use |
| `gmax` | Activates gravity well |
| `rmax` | Increases rank |
| `bmax` | Instant extra ball |

---

## 18. Timing and State Reset Rules

### 18.1 Timer-Based Resets (60-second Decay)

The following table elements reset/decay after 60 seconds of inactivity in their associated mechanic:

| Element | Decay Behavior |
|---|---|
| Attack Bumper color | Drops one level (e.g., Red -> Yellow -> Green -> Blue) |
| Engine Bumper color | Drops one level |
| Field Multiplier | Topmost lit light resets (drops one multiplier level) |
| Hyperspace lights | Reset toward 0 |
| Booster lights | Reset |

### 18.2 Ball Drain Reset

When a ball drains (and it is not a replay ball):

| Element | Behavior |
|---|---|
| Drop targets | All reset to upright position |
| Spot targets | All reset |
| Bumper colors | Reset to Blue |
| Field multiplier | Reset to 1x |
| Hyperspace lights | Reset to 0 |
| Booster | Reset to off |
| Hazard lights | Reset |
| Center Post | Retracts |
| Mission state | Persists across balls; active mission remains active |
| Progress lights | Persist; do not reset between balls |
| Rank | Persists; does not reset between balls |
| Bonus | Awarded then reset |

### 18.3 Replay Ball State

When a replay ball is triggered:

| Element | Behavior |
|---|---|
| All table elements | Remain exactly as they were; NO reset occurs |
| Bonus | Not awarded |
| Ball counter | Does not advance |

---

## 19. Gravity Well Details

| Parameter | Value |
|---|---|
| Activation | Enter the hyperspace kickout with all 4 hyperspace lights lit (or via cheat code) |
| Location | Center of the circular light arrangement in the lower portion of the table |
| Behavior | When active, the gravity well attracts any ball passing near it, pulling it into a spiraling orbit |
| Capture | Ball spirals into the well center |
| Ejection | Ball is launched out in a random direction |
| Points | 50,000 per capture/ejection |
| Duration | Active until the ball drains or a set time elapses |

---

## 20. Complete Scoring Reference Table

| Event | Base Points |
|---|---|
| Attack Bumper (Blue) | 500 |
| Attack Bumper (Green) | 1,000 |
| Attack Bumper (Yellow) | 1,500 |
| Attack Bumper (Red) | 2,000 |
| Satellite Bumper (Blue) | 1,500 |
| Satellite Bumper (Green) | 2,500 |
| Satellite Bumper (Yellow) | 3,500 |
| Satellite Bumper (Red) | 4,500 |
| Engine Bumper (Blue) | 1,500 |
| Engine Bumper (Green) | 2,500 |
| Engine Bumper (Yellow) | 3,500 |
| Engine Bumper (Red) | 4,500 |
| Mission Target (each) | 1,000 |
| Field Multiplier Drop Target (each) | 500 |
| Field Multiplier Drop Target (all 3 cleared bonus) | 1,500 |
| Medal Target (each drop) | 1,500 |
| Left Hazard Target (each) | 750 |
| Right Hazard Target (each) | 750 |
| Booster Target (each) | 750 |
| Fuel Target (each) | 750 |
| Return Lane (each pass) | 2,500 |
| Out Lane (each pass) | 20,000 |
| Space Warp Rollover | 10,000 |
| Black Hole Kickout | 20,000 |
| Hyperspace Kickout (0 lights) | 5,000 |
| Hyperspace Kickout (1 light) | 10,000 |
| Hyperspace Kickout (2 lights) | 20,000 |
| Hyperspace Kickout (3 lights) | 50,000 |
| Hyperspace Kickout (4 lights) | 150,000 |
| Gravity Well capture | 50,000 |
| Wormhole (closed) | 2,000 |
| Wormhole (open, different exit) | 7,500 |
| Wormhole (open, same exit = replay) | 5,000 |
| Flag (no booster, per half-spin) | 500 |
| Flag (booster lit, per half-spin) | 2,500 |
| Skill Shot Light 1 | 15,000 |
| Skill Shot Light 2 | 30,000 |
| Skill Shot Light 3 | 75,000 |
| Skill Shot Light 4 | 30,000 |
| Skill Shot Light 5 | 15,000 |
| Skill Shot Light 6 | 7,500 |
| Mission acceptance | 30,000 |
| Mission: Re-entry Training | 500,000 |
| Mission: Launch Training | 500,000 |
| Mission: Target Practice | 500,000 |
| Mission: Science | 750,000 |
| Mission: Bug Hunt | 750,000 |
| Mission: Rescue | 750,000 |
| Mission: Alien Menace | 750,000 |
| Mission: Secret | 1,500,000 |
| Mission: Stray Comet | 1,000,000 |
| Mission: Space Radiation | 1,000,000 |
| Mission: Black Hole Threat | 1,000,000 |
| Mission: Cosmic Plague | 1,750,000 |
| Mission: Satellite Retrieval | 1,250,000 |
| Mission: Recon Mission | 1,250,000 |
| Mission: Doomsday Machine | 1,250,000 |
| Mission: Time Warp | 1,250,000 |
| Mission: Maelstrom | 5,000,000 |

Note: All base points are subject to the current field multiplier (1x through 10x or higher).
