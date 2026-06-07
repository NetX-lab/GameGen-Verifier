# 32 Rummikub -- Faithful Digital Recreation

## 1. Game Overview

| Field | Value |
|---|---|
| **Title** | Rummikub |
| **Original Designer** | Ephraim Hertzano |
| **Genre** | Board / Tile-Based Set Collection & Manipulation |
| **Player Count** | 2 -- 4 |
| **Core Fantasy** | Form valid groups and runs of numbered tiles on the shared table, strategically rearranging existing melds and emptying your personal rack before any opponent does the same. |
| **Camera / Presentation** | 2D top-down tabletop view with a player rack along the bottom edge, shared table area in the center, draw pool indicator, opponent rack-count panels along the top/sides, and drag-and-drop tile manipulation. |
| **Target Session Length** | 10 -- 30 minutes per round (varies with player count and skill). |
| **Target Skill Curve** | First turns are approachable (simple runs/groups to meet the 30-point threshold); depth emerges through table manipulation, joker timing, rack planning, and denial play. |
| **Rule Variant** | Sabra (the modern standard shipped with all current Rummikub sets). |

---

## 2. Technical Foundation (Digital Version)

### 2.1 Simulation Architecture

| Parameter | Value |
|---|---|
| Logic tick rate | Fixed 60 FPS (`dt = 1/60 s`) |
| Update order | `Input -> Staging -> Validation -> Commit/Draw -> TurnAdvance -> ResultCheck -> UIEventBus` |
| RNG | Single seeded PRNG stream for shuffle, deal, AI decisions, and pool draw order |
| Determinism | Identical seed + identical input stream must produce identical game states |
| Replay format | Initial seed + ordered turn-action records (tile moves, commits, draws) |
| Checksum | Deterministic hash after every committed turn for replay verification |

### 2.2 Performance Budget

| Metric | Budget |
|---|---|
| Render frame | 16.67 ms (60 FPS) |
| Logic tick (avg) | <= 4 ms |
| Logic tick (p99) | <= 8 ms |
| Full-table validation | <= 2 ms even with maximum table complexity |

### 2.3 Core Technical Constraints

- No gameplay rule logic may reside in renderer-only code paths.
- Pause freezes all gameplay timers (turn timer, animation timers, AI planner).
- All balancing numbers must be externalized in configuration (not hardcoded).
- Entity lifecycle: `create -> activate -> stage -> commit -> recycle/despawn`.
- Save operation must be atomic: write to temp file, fsync, rename.

---

## 3. Tile System

### 3.1 Complete Tile Set Composition

| Category | Details | Count |
|---|---|---|
| Number tiles | Values 1 -- 13 in each of 4 colors, with 2 identical copies per color/number combination | 4 colors x 13 values x 2 copies = **104** |
| Joker tiles | Wild tiles (no fixed color or value) | **2** |
| **Total** | | **106 tiles** |

### 3.2 Tile Colors

| Color ID | Display Color | Hex (reference) |
|---|---|---|
| `BLACK` | Black | `#222222` |
| `RED` | Red | `#D62828` |
| `BLUE` | Blue | `#1D3DBF` |
| `ORANGE` | Orange | `#F77F00` |

Color order for display sorting: Black, Red, Blue, Orange (arbitrary but consistent).

### 3.3 Tile Identity

Each of the 104 number tiles is uniquely identified by the triple `(color, value, copy_index)` where:
- `color` is one of {BLACK, RED, BLUE, ORANGE}.
- `value` is an integer in [1, 13].
- `copy_index` is 0 or 1 (distinguishes the two identical copies).

Each of the 2 joker tiles is identified by `(JOKER, copy_index)` where `copy_index` is 0 or 1.

### 3.4 Tile Point Values

| Tile | Point Value (in melds / initial meld) | Penalty Value (left on rack at end) |
|---|---|---|
| Number tile with face value N | N points | N points |
| Joker (when used in a meld) | Value of the tile it represents | N/A (on table) |
| Joker (left on rack at game end) | N/A | **30 points** |

---

## 4. Core Rules -- Valid Meld Types

Every arrangement of tiles on the shared table must consist entirely of valid melds. A valid meld is either a **group** or a **run**. No tile may be left unattached to a valid meld at the end of any turn.

### 4.1 Groups (Sets of Same Number)

| Property | Rule |
|---|---|
| Definition | 3 or 4 tiles of the **same number** but **all different colors** |
| Minimum size | 3 tiles |
| Maximum size | 4 tiles (one per color; no duplicate colors allowed) |
| Joker usage | A joker may substitute for any one missing tile in the group |

**Valid group examples:**

| Tiles | Valid? | Reason |
|---|---|---|
| Red 7, Blue 7, Black 7 | Yes | 3 tiles, same number, all different colors |
| Red 7, Blue 7, Black 7, Orange 7 | Yes | 4 tiles, same number, all 4 colors |
| Red 7, Blue 7, Joker | Yes | Joker represents Black 7 or Orange 7 |
| Red 7, Blue 7 | No | Only 2 tiles (minimum is 3) |
| Red 7, Red 7, Blue 7 | No | Duplicate color (two Red tiles) |
| Red 7, Blue 7, Black 7, Orange 7, Joker | No | 5 tiles exceeds maximum of 4 for a group |

### 4.2 Runs (Consecutive Sequences)

| Property | Rule |
|---|---|
| Definition | 3 or more tiles of the **same color** in **consecutive numerical order** |
| Minimum size | 3 tiles |
| Maximum size | 13 tiles (a complete 1 -- 13 run in one color) |
| Wrap-around | **Not allowed**. The tile 1 may NOT follow 13. A run of 12-13-1 is illegal. |
| Lowest possible run | 1-2-3 |
| Highest possible run | 11-12-13 |
| Joker usage | A joker may substitute for any one missing tile in the run |

**Valid run examples:**

| Tiles | Valid? | Reason |
|---|---|---|
| Blue 3, Blue 4, Blue 5 | Yes | 3 consecutive, same color |
| Red 10, Red 11, Red 12, Red 13 | Yes | 4 consecutive, same color |
| Orange 1, Orange 2, Orange 3, Orange 4, Orange 5 | Yes | 5 consecutive, same color |
| Blue 3, Joker, Blue 5 | Yes | Joker represents Blue 4 |
| Blue 12, Blue 13, Blue 1 | No | Wrap-around is illegal |
| Blue 3, Red 4, Blue 5 | No | Mixed colors |
| Blue 3, Blue 5 | No | Only 2 tiles (and gap) |

---

## 5. Player Setup & Game Start

### 5.1 Initial Deal

| Step | Detail |
|---|---|
| 1. Tile pool | All 106 tiles are placed face-down and shuffled thoroughly (the "pool" or "boneyard"). |
| 2. Draw starting tiles | Each player draws **14 tiles** from the pool and places them on their personal rack (hidden from other players). |
| 3. Determine first player | Each player draws 1 additional tile from the pool. The player who draws the **highest number** goes first. Joker counts as highest. Ties are broken by redrawing. Drawn tiles are returned to the pool and reshuffled. |
| 4. Turn order | Play proceeds **clockwise** from the starting player. |

### 5.2 Pool Size After Deal

| Player Count | Tiles Dealt | Tiles Remaining in Pool |
|---|---|---|
| 2 players | 2 x 14 = 28 | 106 - 28 = **78** |
| 3 players | 3 x 14 = 42 | 106 - 42 = **64** |
| 4 players | 4 x 14 = 56 | 106 - 56 = **50** |

---

## 6. Initial Meld Requirement

### 6.1 The 30-Point Threshold

Before a player may manipulate any tiles already on the table, they must first make an **initial meld**: one or more valid groups and/or runs played from their rack in a single turn, whose tile face values sum to **at least 30 points**.

| Rule | Detail |
|---|---|
| Minimum point total | **30** |
| Source of tiles | **Only from the player's own rack** (no table tiles may be used) |
| Joker value for initial meld | Counts as the face value of the tile it represents |
| Number of melds | May be split across multiple groups/runs in the same turn |
| Failure | If a player cannot or chooses not to meet the threshold, they draw 1 tile and end their turn |

### 6.2 Initial Meld Examples

| Played Tiles | Total Points | Valid Initial Meld? |
|---|---|---|
| Red 10 + Blue 10 + Black 10 (group) | 30 | Yes (exactly 30) |
| Blue 7 + Blue 8 + Blue 9 + Blue 10 (run) | 34 | Yes (exceeds 30) |
| Red 3 + Blue 3 + Black 3 (group) + Orange 7 + Orange 8 + Orange 9 (run) | 9 + 24 = 33 | Yes (combined total exceeds 30) |
| Red 5 + Blue 5 + Black 5 (group) | 15 | No (below 30) |
| Red 9 + Blue 9 + Joker (group, joker = Black 9 or Orange 9) | 27 | No (27 < 30) |
| Red 10 + Joker + Red 12 (run, joker = Red 11) | 10 + 11 + 12 = 33 | Yes (joker valued as 11) |

### 6.3 Post-Initial-Meld Unlock

Once a player has successfully completed their initial meld (met the 30-point threshold), they gain full table manipulation privileges on all subsequent turns. They may now:
- Add tiles from their rack to any existing meld on the table.
- Rearrange, split, and recombine any tiles on the table.
- Reclaim jokers from table melds (subject to joker rules).

---

## 7. Table Manipulation Rules

Table manipulation is the defining strategic mechanic of Rummikub. After completing the initial meld, a player may rearrange any and all tiles on the shared table during their turn, provided that **every meld on the table is valid at the end of the turn**.

### 7.1 Fundamental Constraint

> At the conclusion of a player's turn, **every tile on the table must belong to a valid group or run**. No loose, orphaned, or partially-formed melds are permitted. If this constraint cannot be satisfied, the turn is invalid.

### 7.2 Manipulation Techniques

#### 7.2.1 Adding a Tile to an Existing Meld

A player places a tile from their rack onto an existing meld.

| Before | Action | After |
|---|---|---|
| Table: Blue 4, Blue 5, Blue 6 | Add Blue 7 from rack | Blue 4, Blue 5, Blue 6, Blue 7 |
| Table: Red 8, Blue 8, Black 8 | Add Orange 8 from rack | Red 8, Blue 8, Black 8, Orange 8 |

#### 7.2.2 Splitting a Run

A long run is divided into two valid runs, sometimes by inserting a tile from the player's rack.

| Before | Action | After |
|---|---|---|
| Table: Blue 3, Blue 4, Blue 5, Blue 6, Blue 7, Blue 8 | Split at 5/6 boundary | Run A: Blue 3, Blue 4, Blue 5 AND Run B: Blue 6, Blue 7, Blue 8 |
| Table: Blue 6, Blue 7, Blue 8, Blue 9, Blue 10 | Insert own Blue 8 (second copy) to split | Run A: Blue 6, Blue 7, Blue 8 AND Run B: Blue 8, Blue 9, Blue 10 |

#### 7.2.3 Removing a Tile from a Four-Tile Group

A tile is taken from a group of 4 (leaving a still-valid group of 3) and used elsewhere.

| Before | Action | After |
|---|---|---|
| Table: Red 5, Blue 5, Black 5, Orange 5 | Remove Orange 5 | Table group: Red 5, Blue 5, Black 5 (still valid) AND Orange 5 used in a new meld |

#### 7.2.4 Combining Tiles from Multiple Melds

Tiles from different existing melds and the player's rack are recombined to form new valid melds.

| Before | Action | After |
|---|---|---|
| Table group: Red 5, Blue 5, Black 5 AND Table run: Red 3, Red 4, Red 5, Red 6 | Take Red 5 from the run; add Orange 5 from rack to the group; extend run with rack tiles | Group: Red 5, Blue 5, Black 5, Orange 5 AND Run: Red 3, Red 4 (needs extension) -- only valid if all pieces form legal melds |

#### 7.2.5 Replacing a Tile in a Group to Use Elsewhere

| Before | Action | After |
|---|---|---|
| Table group: Red 9, Blue 9, Black 9 AND player has Orange 9 and needs Red 9 for a run | Add Orange 9 to group, take Red 9 out | Group: Orange 9, Blue 9, Black 9 AND Red 9 placed in a new run (e.g., Red 7, Red 8, Red 9) |

### 7.3 Manipulation Constraints

| Constraint | Detail |
|---|---|
| End-of-turn validity | Every tile on the table must be in a valid meld when the turn is committed |
| No stockpiling | A player may NOT remove tiles from the table and add them to their rack. All tiles that start a turn on the table must end the turn on the table. |
| Initial meld required first | A player who has not yet completed their initial meld may NOT manipulate table tiles |
| Must play from rack | On any turn where manipulation occurs, the player must place **at least one tile from their rack** onto the table (except when only rearranging without adding -- some rule variants differ here; in the strict Sabra version, a player is allowed to rearrange without adding from rack, but the common digital implementation requires adding at least one tile or drawing) |

---

## 8. Joker Rules

### 8.1 Joker as Wildcard

| Rule | Detail |
|---|---|
| Representation | A joker may represent **any tile** (any color, any number 1 -- 13) needed to complete a valid meld |
| In a group | The joker takes the place of a specific missing color of that number |
| In a run | The joker takes the place of a specific missing number of that color |
| Limit per meld | A meld may contain at most **1 joker** (standard Sabra rules) |
| Initial meld | A joker **may** be used in the initial meld; its point value equals the face value of the tile it represents |

### 8.2 Joker Reclamation

A joker on the table can be retrieved by a player and reused, subject to strict conditions:

| Condition | Rule |
|---|---|
| Replacement tile | The player must replace the joker with the **exact tile it represents** (correct color and number). The replacement tile may come from the player's rack or from the table (via manipulation). |
| Immediate use | The retrieved joker **must be played on the table in a new meld during the same turn**. It may NOT be placed on the player's rack. |
| Rack tile required | The player must use **at least one tile from their rack** during the turn in which a joker is reclaimed (in addition to or as part of the new meld containing the joker). |
| Initial meld prerequisite | A player may NOT reclaim a joker before completing their initial meld. |

### 8.3 Joker Scoring

| Situation | Joker Value |
|---|---|
| Used in initial meld | Face value of the tile it represents (for meeting the 30-point threshold) |
| On the table at game end | 0 (already played; no penalty) |
| Left on a player's rack at game end | **30 penalty points** |

---

## 9. Turn Structure

### 9.1 Turn Flow

```
TURN START
    |
    v
[Has player completed initial meld?]
    |                    |
    NO                  YES
    |                    |
    v                    v
[Attempt initial    [May manipulate table
 meld from rack      AND play from rack]
 (>= 30 points)]        |
    |                    |
    v                    v
[Can play?]         [Stage moves: add tiles,
    |       |        rearrange melds, reclaim
   YES     NO        jokers, etc.]
    |       |            |
    v       v            v
[Place   [Draw 1   [All table melds valid?]
 melds]   tile,        |           |
    |     end turn]   YES          NO
    v        |         |            |
[Commit]     |    [Commit turn]  [Timer expired?]
    |        |         |            |        |
    v        v         v           YES      NO
[END TURN]  [END]  [END TURN]      |        |
                                   v        v
                              [Revert all  [Continue
                               changes,     editing]
                               return
                               rack tiles,
                               draw 3 tiles
                               as penalty,
                               END TURN]
```

### 9.2 Turn Actions Summary

| Action | Condition | Effect |
|---|---|---|
| Play tiles from rack | Always available | Places rack tiles into new or existing melds on the table |
| Manipulate table melds | Only after initial meld completed | Rearrange, split, combine existing table tiles |
| Reclaim joker | Only after initial meld; must replace with exact tile; must play joker immediately | Swaps joker back to hand for immediate reuse |
| Draw tile | When player cannot or chooses not to play | Draws exactly **1 tile** from the pool; turn ends immediately |
| Commit turn | When all table melds are valid | Locks in all changes; advances to next player |

### 9.3 Turn Timer

| Parameter | Value |
|---|---|
| Default time limit | **60 seconds** (1 minute) per turn |
| Extended/casual mode | **120 seconds** (2 minutes) per turn |
| Timer starts | When the player's turn begins |
| Timer visible | Countdown display in the HUD |
| Timer expiration consequence | All staged changes are **reverted** (table restored to start-of-turn state), any tiles played from rack are **returned to rack**, and the player must draw **3 tiles** from the pool as a penalty |

---

## 10. Drawing & the Pool

### 10.1 Voluntary Draw

| Rule | Detail |
|---|---|
| When | A player who cannot play or chooses not to play on their turn |
| Quantity | Exactly **1 tile** drawn from the pool |
| Turn end | Drawing immediately ends the player's turn |
| May not play after draw | Once a player draws, they may not play any tiles that turn (the draw is the final action) |

### 10.2 Penalty Draw (Invalid Turn / Timer Expiration)

| Rule | Detail |
|---|---|
| Trigger | Player's staged changes result in an invalid table state when the timer expires, or the player cannot resolve the table to a valid configuration |
| Revert | All table tiles are returned to their positions at the start of the turn |
| Rack tiles returned | Any tiles the player moved from rack to table are returned to the rack |
| Penalty | Player draws **3 tiles** from the pool |
| Turn end | Turn ends immediately after the penalty draw |

### 10.3 Pool Exhaustion

| Rule | Detail |
|---|---|
| Condition | The pool has 0 tiles remaining |
| Drawing | No tiles can be drawn; if a player cannot play, they simply pass |
| Game continuation | Play continues as long as at least one player can make a legal play |
| Stalemate | If the pool is empty AND no player can (or chooses to) make a legal play, the round ends |
| Stalemate winner | The player with the **lowest total face-value sum** of tiles remaining on their rack wins the round |
| Stalemate scoring | Each losing player scores negative the total face value of their own remaining tiles; the winner scores plus the sum of differences (see Scoring System) |

---

## 11. Scoring System

### 11.1 Standard Round Scoring

When a player empties their rack and calls "Rummikub!":

| Player | Score Formula |
|---|---|
| **Winner** (empty rack) | `+ SUM of all losing players' remaining tile values` |
| **Each loser** | `- SUM of their own remaining tile values` |

The plus scores and minus scores for each round always sum to zero.

### 11.2 Tile Values for Scoring

| Tile | Penalty Value |
|---|---|
| Number tile (face value N) | **N points** (e.g., a 13 tile = 13 points) |
| Joker (left on rack) | **30 points** |

### 11.3 Scoring Example (4-Player Round)

| Player | Remaining Tiles | Tile Sum | Round Score |
|---|---|---|---|
| Player A (winner) | None | 0 | **+75** |
| Player B | Red 5, Blue 8, Orange 2 | 15 | **-15** |
| Player C | Black 13, Joker | 13 + 30 = 43 | **-43** |
| Player D | Red 7, Blue 10 | 17 | **-17** |
| **Total** | | 75 | **0** (balanced) |

### 11.4 Stalemate Scoring (Pool Exhausted, No Plays Possible)

When the round ends due to pool exhaustion with no available plays:

1. Each player totals the face values of tiles on their rack.
2. The player with the **lowest total** wins the round.
3. Each losing player's score = `-(own_total - winner_total)`.
4. The winner's score = `+SUM of all losing players' (own_total - winner_total)`.

| Player | Remaining Total | Difference from Winner | Round Score |
|---|---|---|---|
| Player A (winner, lowest) | 8 | 0 | **+52** |
| Player B | 22 | 14 | **-14** |
| Player C | 35 | 27 | **-27** |
| Player D | 19 | 11 | **-11** |
| **Total** | | 52 | **0** (balanced) |

### 11.5 Multi-Round / Match Scoring

| Rule | Detail |
|---|---|
| Running total | Scores accumulate across multiple rounds |
| Match end | Players agree on a number of rounds, a target score, or play until mutual agreement |
| Overall winner | Player with the **highest cumulative score** at match end |

---

## 12. Player Count & Setup Variations

| Parameter | 2 Players | 3 Players | 4 Players |
|---|---|---|---|
| Starting tiles per player | 14 | 14 | 14 |
| Initial pool size | 78 | 64 | 50 |
| Turn order | Clockwise | Clockwise | Clockwise |
| Initial meld threshold | 30 | 30 | 30 |
| Joker penalty | 30 | 30 | 30 |
| All other rules | Identical | Identical | Identical |

---

## 13. Win Conditions

### 13.1 Primary Win Condition

A player wins the round by **placing all tiles from their rack onto the table in valid melds**, leaving their rack completely empty. The player calls "Rummikub!" to declare victory.

### 13.2 Stalemate Win Condition

If the pool is exhausted and no player can make a legal play, the player with the **lowest remaining rack value** wins the round.

### 13.3 Match Win Condition

The player with the highest cumulative score after the agreed number of rounds wins the match.

---

## 14. Time Limit System

### 14.1 Configuration

| Setting | Default | Casual | Tournament |
|---|---|---|---|
| Turn time limit | 60 s | 120 s | 60 s |
| Warning threshold | 15 s remaining | 30 s remaining | 15 s remaining |
| Visual warning | Timer turns red, pulsing animation | Timer turns yellow, then red | Timer turns red |
| Audio warning | Ticking sound at warning threshold | Gentle chime at warning | Ticking sound |
| Expiration behavior | Revert + 3-tile penalty draw | Revert + 3-tile penalty draw | Revert + 3-tile penalty draw |

### 14.2 Timer Behavior

| State | Timer Active? |
|---|---|
| Player's turn (active editing) | Yes |
| Pause menu open | No (frozen) |
| AI opponent thinking | Yes (AI has same time limit) |
| Animation/commit resolution | No (paused during resolution) |
| Between turns | No |

---

## 15. Validation System

### 15.1 End-of-Turn Validation

At turn commit, the system must verify:

| Check | Rule | Failure Action |
|---|---|---|
| All tiles in valid melds | Every tile on the table belongs to a group (3-4 same number, different colors) or a run (3+ consecutive, same color) | Block commit; highlight invalid melds |
| No orphaned tiles | No tile exists outside of a meld | Block commit; highlight orphans |
| No duplicate colors in group | A group contains at most one tile of each color | Block commit; highlight duplicates |
| Run consecutiveness | Run tiles are sequential with no gaps (joker fills gaps) | Block commit; highlight breaks |
| No wrap-around | Runs do not wrap from 13 to 1 | Block commit; highlight illegal wrap |
| Group size limits | Groups have exactly 3 or 4 tiles | Block commit; highlight undersized/oversized groups |
| Run minimum size | Runs have at least 3 tiles | Block commit; highlight undersized runs |
| Joker legality | Each meld contains at most 1 joker; joker's assigned identity is consistent | Block commit; highlight joker conflict |
| Initial meld threshold | If this is the player's first meld, the total face value of played tiles >= 30 | Block commit; display point shortfall |
| Tile conservation | No tiles have been moved from the table to a player's rack (all table tiles from turn start remain on the table) | Block commit; flag illegal tile removal |

### 15.2 Real-Time Feedback During Editing

| Feedback Type | Trigger | Visual |
|---|---|---|
| Valid meld indicator | A staged meld satisfies all rules | Green border / checkmark |
| Invalid meld warning | A staged meld violates a rule | Red border / X marker with tooltip explaining the violation |
| Point counter (initial meld) | Player has not yet completed initial meld | Running total of staged tile values vs. 30-point threshold |
| Orphan highlight | A tile is not part of any meld | Yellow pulsing outline |
| Joker identity display | Joker is placed in a meld | Ghost text showing the tile the joker represents |

### 15.3 Snapshot & Revert System

| Feature | Detail |
|---|---|
| Turn-start snapshot | The complete table state is captured at the beginning of each turn |
| Undo staged move | Player can undo individual moves within the current turn (stack-based undo) |
| Full revert | "Reset Turn" button restores the table and rack to the turn-start snapshot |
| Auto-revert on timer expiry | System automatically reverts to snapshot and applies 3-tile penalty |

---

## 16. State Machines

### 16.1 Application State Machine

```
Boot -> MainMenu -> MatchSetup -> Loading -> Run -> Result -> MainMenu
                                                 \-> Pause -> Run (resume)
```

| State | Description |
|---|---|
| `Boot` | Load configuration, audio engine, AI profiles, input bindings |
| `MainMenu` | Mode selection (local, vs AI, online), settings, credits |
| `MatchSetup` | Player count (2-4), human/AI assignment, AI difficulty, time limit, round count |
| `Loading` | Shuffle tiles (seeded), deal 14 to each player, initialize pool, determine first player |
| `Run` | Active match (see Run Substate Machine) |
| `Result` | Round/match scores, rack reveal, replay option, rematch, return to menu |
| `Pause` | Timers frozen, resume/quit/settings options |

### 16.2 Run Substate Machine

| State | Description |
|---|---|
| `Deal` | Animate tile dealing to racks; transition to `TurnStart` |
| `TurnStart` | Set current player; start turn timer; enable input |
| `Editing` | Player is staging moves (placing tiles, rearranging) |
| `Validating` | System checks all table melds on commit attempt |
| `Committing` | Valid turn: lock changes, animate placement, update scores |
| `Drawing` | Player chose to draw or must draw: animate pool draw, add to rack |
| `PenaltyRevert` | Timer expired with invalid state: animate revert, draw 3 penalty tiles |
| `TurnEnd` | Check for round end conditions, advance to next player |
| `RoundEnd` | A player emptied rack or stalemate: calculate scores, display results |

### 16.3 Player Turn State Machine

| State | Description |
|---|---|
| `Waiting` | Not the current player; rack visible but not interactive |
| `Active` | Current player; full interaction enabled within rules |
| `Committed` | Move validated and locked; awaiting resolution |
| `Drew` | Drew tile(s); turn ending |
| `Finished` | Emptied rack; round ending |

### 16.4 Tile State Machine

| State | Description |
|---|---|
| `InPool` | Tile is face-down in the draw pool |
| `OnRack` | Tile is on a player's rack (private) |
| `Staged` | Tile moved during current turn but not yet committed |
| `OnTable` | Tile is part of a committed meld on the table |
| `JokerBound` | Joker tile assigned to represent a specific color/number in a meld |

---

## 17. Entity Specification

### 17.1 Entity Table

| Entity ID | Role | Key Properties | Behavior |
|---|---|---|---|
| `number_tile` | Standard tile | `color`, `value`, `copy_index`, `state` | Participates in groups and runs |
| `joker_tile` | Wildcard tile | `copy_index`, `state`, `bound_color`, `bound_value` | Substitutes for any tile in a valid meld |
| `player_rack` | Private tile container | `player_id`, `tiles[]`, `tile_count` | Holds player's private tiles; hidden from opponents |
| `table_meld` | Committed meld | `meld_id`, `type` (group/run), `tiles[]` | Must be valid at end of every turn |
| `draw_pool` | Tile source | `tiles[]`, `remaining_count` | Provides tiles on draw actions; shuffled at game start |
| `player` | Game participant | `id`, `name`, `is_human`, `has_initial_meld`, `score` | Takes turns, makes decisions |
| `ai_player` | AI opponent | Inherits `player` + `difficulty`, `strategy_profile` | Automated decision-making |

### 17.2 Player Baseline Configuration

| Parameter | Value |
|---|---|
| `starting_rack_size` | 14 |
| `initial_meld_threshold` | 30 |
| `joker_penalty_value` | 30 |
| `max_players` | 4 |
| `min_players` | 2 |
| `draw_on_pass` | 1 tile |
| `penalty_draw` | 3 tiles |

---

## 18. AI Opponent Design

### 18.1 Difficulty Levels

| Level | Description | Behavior |
|---|---|---|
| Easy | Beginner-friendly | Plays obvious melds; rarely manipulates table; does not track opponent tiles |
| Medium | Competent player | Performs basic table manipulation; tracks approximate opponent rack sizes; manages jokers adequately |
| Hard | Expert player | Aggressive table manipulation; optimal initial meld timing; tracks drawn/played tiles; strategic joker hoarding and denial; minimizes rack value as endgame approaches |

### 18.2 AI Decision Framework

| Priority | Action | Condition |
|---|---|---|
| 1 | Empty rack (win) | All tiles can be legally placed |
| 2 | Play tiles to minimize rack value | Reduce penalty exposure; prefer high-value tiles |
| 3 | Perform table manipulation to enable plays | Only after initial meld completed |
| 4 | Reclaim joker if strategically valuable | Replacement tile available; joker enables significant plays |
| 5 | Meet initial meld threshold | If not yet done and >= 30 points available from rack |
| 6 | Draw from pool | No beneficial plays identified |

---

## 19. UI Layout (Digital Version)

### 19.1 Main Gameplay Screen Layout

```
+------------------------------------------------------------------+
|  [Opponent 3 Rack: 8 tiles]          [Turn Timer: 0:45]          |
+------------------------------------------------------------------+
|  [Opp 2]  |                                            | [Opp 4] |
|  Rack: 12 |          SHARED TABLE AREA                 | Rack: 6 |
|  tiles    |                                            | tiles   |
|           |    [Meld 1: R5 B5 K5]                      |         |
|           |    [Meld 2: B3 B4 B5 B6]                   |         |
|           |    [Meld 3: R10 R11 R12 R13]               |         |
|           |    [Meld 4: O7 B7 K7 JKR]                  |         |
|           |                                            |         |
|           |                                            |         |
+-----------+--------------------------------------------+---------+
|  [Draw    |  YOUR RACK (14 tiles)                      | [Commit]|
|   Pile:   |  [R3][R7][R9][B1][B4][B5][B11][K2][K8]    | [Undo]  |
|   42]     |  [K13][O4][O6][O10][JKR]                   | [Reset] |
+-----------+--------------------------------------------+---------+
|  [Score: +23]  [Initial Meld: DONE]  [Round: 2/5]     | [Menu]  |
+------------------------------------------------------------------+
```

### 19.2 Screen Inventory

| Screen | Purpose |
|---|---|
| Main Menu | Game mode selection, settings, credits, quit |
| Match Setup | Player count, human/AI, AI difficulty, time limit, round count |
| Gameplay | Main play area (layout above) |
| Pause Menu | Resume, settings, quit to menu |
| Round Result | Winner announcement, rack reveal for all players, scoring breakdown |
| Match Result | Cumulative scores across all rounds, overall winner, rematch option |
| Settings | Audio, visual, accessibility, controls, timer configuration |
| Tutorial | Interactive walkthrough of basic plays, initial meld, manipulation, joker rules |

### 19.3 HUD Elements

| Element | Location | Update Frequency |
|---|---|---|
| Turn timer | Top center | Every frame (countdown) |
| Current player indicator | Top center (below timer) | On turn change |
| Pool count | Bottom left | On draw |
| Player rack | Bottom center | On every rack change |
| Opponent rack counts | Top/sides | On every opponent rack change |
| Player score | Bottom bar | On round end |
| Initial meld status | Bottom bar | Once (when threshold met) |
| Meld validity indicators | On each table meld | Real-time during editing |
| Point counter (pre-initial meld) | Near staged tiles | Real-time during editing |
| Undo / Reset / Commit buttons | Bottom right | Context-dependent availability |

### 19.4 Interaction Design

| Action | Input | Visual Feedback |
|---|---|---|
| Select tile from rack | Click/tap tile | Tile lifts slightly, highlighted border |
| Place tile on table | Drag to target position or click target slot | Tile snaps to nearest valid position in meld |
| Move table tile | Drag from one meld to another | Source meld adjusts; destination meld previews |
| Create new meld | Drag tile to empty table area | New meld container appears |
| Commit turn | Click "Commit" button or press Enter | Validation runs; success = green flash + lock; failure = red flash + error tooltips |
| Undo last move | Click "Undo" button or press Ctrl+Z | Last staged move is reversed |
| Reset entire turn | Click "Reset" button or press Backspace | Table and rack restored to turn-start snapshot |
| Draw tile | Click pool or press D | Tile animates from pool to rack; turn ends |
| Sort rack | Click sort button or press S | Tiles rearrange by color then value, or by value then color (toggle) |

---

## 20. Audio Design

### 20.1 Music

| Context | Track Type | Characteristics |
|---|---|---|
| Main menu | Warm, inviting | Acoustic, light percussion, moderate tempo |
| Gameplay (early) | Calm, focused | Ambient, minimal, unobtrusive |
| Gameplay (late / low rack counts) | Tense, building | Subtle tempo increase, added layers |
| Round victory | Celebratory | Short fanfare, bright instrumentation |
| Round loss | Subdued | Brief minor-key resolution |
| Match victory | Grand celebration | Extended fanfare with flourish |

### 20.2 Sound Effects

| Event | Sound | Priority |
|---|---|---|
| Tile pick up (from rack) | Soft click / lift | Normal |
| Tile place (on table) | Satisfying clack / snap | Normal |
| Tile slide (rearranging on table) | Smooth slide / scrape | Low |
| Meld commit (valid turn) | Confirmation chime / ding | High |
| Invalid meld attempt | Error buzz / dull thud | High |
| Draw tile from pool | Card-draw whoosh | Normal |
| Penalty draw (3 tiles) | Three rapid draws + warning tone | High |
| Timer warning (15s remaining) | Soft ticking begins | High |
| Timer expiration | Buzzer / time-out bell | Critical |
| Joker placed | Special sparkle / wild-card jingle | Normal |
| Joker reclaimed | Reverse sparkle + pick-up sound | Normal |
| "Rummikub!" (round win) | Victory fanfare + tile cascade | Critical |
| Opponent plays | Muffled tile sounds (directional, from opponent position) | Low |
| Turn change | Subtle transition whoosh | Low |
| Rack sort | Quick shuffle / riffle | Low |

### 20.3 Audio Event Bus Contract

| Event | Payload |
|---|---|
| `OnTilePickUp(tile_id, source)` | Tile identity and whether from rack, table, or pool |
| `OnTilePlace(tile_id, target_meld_id)` | Tile identity and destination meld |
| `OnTileSlide(tile_id, from_meld, to_meld)` | Tile identity and movement path |
| `OnMeldCommit(player_id, meld_count)` | Committing player and number of melds affected |
| `OnValidationFail(error_type, meld_id)` | Type of validation failure and affected meld |
| `OnDraw(player_id, count)` | Drawing player and number of tiles drawn (1 or 3) |
| `OnTimerWarning(seconds_remaining)` | Remaining seconds when warning threshold crossed |
| `OnTimerExpired(player_id)` | Player whose timer expired |
| `OnJokerPlayed(tile_id, bound_color, bound_value)` | Joker identity and its assigned representation |
| `OnJokerReclaimed(tile_id, player_id)` | Joker identity and reclaiming player |
| `OnRoundWin(player_id)` | Winning player |
| `OnRoundEnd(reason)` | "rack_empty" or "stalemate" |
| `OnTurnChange(from_player, to_player)` | Turn transition |

### 20.4 Audio Configuration

| Setting | Default | Range |
|---|---|---|
| Master volume | 80% | 0 -- 100% |
| Music volume | 60% | 0 -- 100% |
| SFX volume | 80% | 0 -- 100% |
| UI sounds | 70% | 0 -- 100% |

---

## 21. Strategy Considerations

### 21.1 Key Strategic Principles

| Strategy | Description |
|---|---|
| **Initial meld timing** | Completing the initial meld early grants table manipulation access but reveals information to opponents. Waiting risks accumulating a large rack if another player goes out early. |
| **High-value-first play** | Prioritize playing high-value tiles (10, 11, 12, 13) to minimize penalty exposure if an opponent wins. |
| **Joker management** | Jokers are powerful for completing melds but carry a 30-point penalty if held at round end. Play them strategically but do not hold too long. |
| **Table manipulation** | After the initial meld, use table rearrangement aggressively to play tiles from your rack without relying solely on direct melds. |
| **Tile tracking** | Track which tiles have been played and which remain in opponents' hands or the pool to make informed decisions. |
| **Defensive play** | Avoid placing tiles that enable opponents' obvious plays. If an opponent is close to winning (low rack count), consider not adding useful tiles to the table. |
| **Rack balance** | Maintain diverse colors and number ranges on your rack to maximize future play options. |
| **Fourth-tile reserve** | If you have a fourth tile for a group (e.g., you have all 4 colors of a number), consider playing only 3 and holding the fourth for a future turn when you need a guaranteed play. |
| **Forced draws** | Sometimes choosing to draw voluntarily can be strategic if the pool is still large and you are waiting for specific tiles to enable large manipulation plays. |
| **Endgame minimization** | As the pool depletes, focus on emptying your rack as fast as possible rather than optimal play, since the round may end abruptly via stalemate. |

---

## 22. Data Contracts

### 22.1 Configuration Schema

```json
{
  "game": {
    "version": "1.0.0",
    "seed": 948271,
    "rule_variant": "sabra",
    "mode": "match"
  },
  "match": {
    "round_count": 5,
    "player_count": 4,
    "players": [
      { "id": "p1", "name": "Player 1", "type": "human" },
      { "id": "p2", "name": "CPU Easy", "type": "ai", "difficulty": "easy" },
      { "id": "p3", "name": "CPU Medium", "type": "ai", "difficulty": "medium" },
      { "id": "p4", "name": "CPU Hard", "type": "ai", "difficulty": "hard" }
    ]
  },
  "rules": {
    "starting_rack_size": 14,
    "initial_meld_threshold": 30,
    "joker_penalty_value": 30,
    "penalty_draw_count": 3,
    "normal_draw_count": 1,
    "wrap_around_runs": false,
    "max_jokers_per_meld": 1
  },
  "timing": {
    "turn_time_limit_seconds": 60,
    "timer_warning_seconds": 15,
    "logic_fps": 60,
    "pause_stops_timers": true
  },
  "scoring": {
    "formula": "winner_gets_sum_of_losers",
    "joker_penalty": 30,
    "stalemate_rule": "lowest_rack_wins"
  }
}
```

### 22.2 Runtime Snapshot Schema

```json
{
  "time": {
    "tick": 4820,
    "elapsed_seconds": 80.33,
    "paused": false
  },
  "round": {
    "number": 2,
    "state": "Editing",
    "seed": 948271,
    "current_player_id": "p1",
    "turn_number": 14,
    "turn_timer_remaining_seconds": 38.5
  },
  "pool": {
    "remaining_count": 29,
    "tiles": ["...ordered_tile_ids..."]
  },
  "players": [
    {
      "id": "p1",
      "rack_tile_ids": ["red_7_0", "blue_3_1", "black_11_0", "joker_0"],
      "rack_count": 4,
      "has_initial_meld": true,
      "cumulative_score": 23,
      "round_score": 0
    },
    {
      "id": "p2",
      "rack_count": 11,
      "has_initial_meld": false,
      "cumulative_score": -8,
      "round_score": 0
    }
  ],
  "table_melds": [
    {
      "id": "meld_001",
      "type": "group",
      "tiles": [
        { "id": "red_5_0", "color": "RED", "value": 5 },
        { "id": "blue_5_0", "color": "BLUE", "value": 5 },
        { "id": "black_5_1", "color": "BLACK", "value": 5 }
      ]
    },
    {
      "id": "meld_002",
      "type": "run",
      "tiles": [
        { "id": "orange_9_0", "color": "ORANGE", "value": 9 },
        { "id": "orange_10_1", "color": "ORANGE", "value": 10 },
        { "id": "orange_11_0", "color": "ORANGE", "value": 11 },
        { "id": "orange_12_0", "color": "ORANGE", "value": 12 }
      ]
    },
    {
      "id": "meld_003",
      "type": "group",
      "tiles": [
        { "id": "red_8_0", "color": "RED", "value": 8 },
        { "id": "blue_8_1", "color": "BLUE", "value": 8 },
        { "id": "joker_1", "color": "JOKER", "value": null, "bound_color": "BLACK", "bound_value": 8 }
      ]
    }
  ],
  "staged_changes": {
    "moves": [
      { "tile_id": "red_7_0", "from": "rack_p1", "to": "meld_002" }
    ],
    "snapshot_id": "snap_turn_14"
  },
  "events": [
    { "tick": 4800, "type": "turn_start", "payload": { "player_id": "p1" } },
    { "tick": 4812, "type": "tile_staged", "payload": { "tile_id": "red_7_0", "target": "meld_002" } }
  ]
}
```

### 22.3 Save/Load Requirements

| Requirement | Detail |
|---|---|
| Format | JSON with schema version field for migration |
| Atomicity | Write to temp file, fsync, rename to final path |
| Validation on load | Reject duplicate tile IDs, invalid meld states, illegal joker bindings, rack/pool count mismatches |
| Compatibility | Save files must be forward-compatible within the same major version |

---

## 23. Input Specification

| Action | Keyboard | Mouse/Touch | Gamepad |
|---|---|---|---|
| Select tile | Arrow keys + Space | Click/Tap tile | D-pad + A |
| Place tile | Arrow keys to target + Enter | Drag to position | D-pad to target + A |
| Commit turn | Enter | Click "Commit" button | Start |
| Undo last move | Ctrl+Z | Click "Undo" button | B |
| Reset turn | Backspace | Click "Reset" button | Select + B |
| Draw tile | D | Click pool | Y |
| Sort rack | S | Click sort button | X |
| Pause | Escape | Click menu button | Start (hold) |
| Cycle focus (melds) | Tab | N/A | LB/RB |

---

## 24. Accessibility

| Feature | Implementation |
|---|---|
| Colorblind mode | Tiles display both color and a unique shape/pattern per color (circle, triangle, square, diamond) so melds can be identified without color alone |
| High-contrast mode | Increased border thickness, bolder number fonts, higher-contrast backgrounds |
| Large text mode | Scalable UI with text size options (100%, 125%, 150%) |
| Screen reader support | All tiles, melds, and game state announce via screen reader labels |
| Keyboard-only play | Full game playable without mouse; clear focus indicators |
| Reduced motion | Disable tile slide animations; instant placement |
| Audio cues for game events | Distinct sounds for valid/invalid plays, draws, turn changes (not relying on visuals alone) |
| Remappable controls | All keyboard/gamepad bindings configurable |

---

## 25. Telemetry (Evaluation & Balancing)

| Metric | Purpose |
|---|---|
| Turns per round | Assess game length |
| Average rack size by turn number | Track pace of play |
| Draw frequency per player | Identify passive play patterns |
| Table manipulation frequency | Measure engagement with core mechanic |
| Joker play rate and reclamation rate | Balance joker power |
| Invalid move attempts per turn | Assess UI clarity |
| Initial meld turn number | Balance 30-point threshold |
| Win condition type (rack empty vs. stalemate) | Ensure stalemates are rare |
| Timer expiration frequency | Calibrate time limits |
| AI decision time | Ensure AI stays within time budget |
| Score distribution per round | Balance scoring system |

---

## 26. QA Acceptance Matrix

| # | Test Case | Pass Criteria |
|---|---|---|
| 1 | Group validation | Groups of 3-4 same-number, all-different-color tiles are accepted; all others are rejected |
| 2 | Run validation | Runs of 3+ consecutive same-color tiles are accepted; wrap-around (13-1) is rejected |
| 3 | Initial meld threshold | Player cannot manipulate table tiles until they have played melds totaling >= 30 points from their rack |
| 4 | Initial meld point calculation | Joker in initial meld counts as the value of the tile it represents |
| 5 | Draw on pass | Player who cannot or chooses not to play draws exactly 1 tile and turn ends |
| 6 | Penalty draw | Timer expiration with invalid table state reverts all changes and draws 3 tiles |
| 7 | Tile conservation | No tile can be moved from the table to a player's rack during a turn |
| 8 | Joker substitution | Joker can represent any tile; meld containing joker passes validation |
| 9 | Joker reclamation | Joker can be reclaimed only by replacing with the exact tile it represents; reclaimed joker must be played on the same turn in a new meld |
| 10 | Joker reclamation prerequisites | Player must have completed initial meld before reclaiming a joker |
| 11 | Joker penalty scoring | Joker left on rack at round end counts as 30 points |
| 12 | Round win detection | Player emptying rack triggers round end exactly once |
| 13 | Stalemate detection | Pool empty + no player can play triggers stalemate; lowest rack value wins |
| 14 | Score balance | Sum of all players' round scores equals zero |
| 15 | Undo system | Undo reverses the most recent staged move; multiple undos unwind the full stack |
| 16 | Reset turn | Reset restores table and rack to exact turn-start snapshot |
| 17 | Turn timer | Timer counts down correctly; expiration triggers penalty |
| 18 | Pause/resume | Pause freezes timer and blocks interaction; resume restores exactly |
| 19 | Save/load integrity | Saving and loading mid-game produces identical game state |
| 20 | Deterministic replay | Same seed + same inputs produces identical game outcomes |
| 21 | AI legality | AI never commits an invalid table state |
| 22 | AI time compliance | AI completes turns within the configured time limit |
| 23 | Pool exhaustion | Game handles empty pool correctly (no draws, pass-only, stalemate check) |
| 24 | Rack sort | Sort correctly orders tiles by color-then-value or value-then-color |
| 25 | Multi-round scoring | Cumulative scores persist and display correctly across rounds |

---

## 27. Engineering Milestones

| Milestone | Deliverables |
|---|---|
| **M1 -- Core Tile Model** | Tile data structures, rack container, pool shuffle/deal, basic meld validation (groups and runs) |
| **M2 -- Turn Flow** | Turn state machine, draw action, commit action, turn timer, penalty revert system |
| **M3 -- Table Manipulation** | Drag-and-drop tile movement on table, splitting/combining melds, real-time validation feedback, undo/reset |
| **M4 -- Joker System** | Joker placement, binding, validation, reclamation rules, initial meld joker point counting |
| **M5 -- Scoring & Win Conditions** | Round scoring (winner/loser), stalemate handling, multi-round cumulative scoring, match end |
| **M6 -- AI Opponents** | Easy/Medium/Hard AI decision engines, tile tracking, table manipulation AI |
| **M7 -- UI & Audio** | Full HUD implementation, all screens, sound effects, music, animations |
| **M8 -- Polish & QA** | Accessibility features, replay system, save/load, full QA acceptance matrix, performance optimization |

---

## 28. Non-Negotiable Implementation Constraints

1. **Single authoritative validator**: All meld legality checks must pass through one centralized validation module. No duplicate or shadow validation logic.
2. **No gameplay in renderer**: All game rules execute in the logic layer. The renderer only reads committed state.
3. **Deterministic RNG**: Every random decision (shuffle, deal, AI) consumes from a single seeded PRNG stream.
4. **Externalized configuration**: All numeric values (thresholds, penalties, timer durations, tile counts) are loaded from config, never hardcoded in game logic.
5. **Tile integrity**: The system must enforce that exactly 106 tiles exist at all times (distributed across pool, racks, and table). No tile duplication or loss.
6. **Joker consistency**: A joker's bound identity must be consistent with the meld it occupies at all times. Validation must reject inconsistent bindings.
7. **Score zero-sum**: The sum of all players' scores in any round must equal zero. The scoring module must enforce this invariant.
8. **Evaluation hooks**: The runtime must expose structured game state (racks, table melds, scores, pool) via API -- not only through DOM/UI rendering.
9. **Atomic state transitions**: Turn commits and reverts must be atomic operations. No partial commits or intermediate invalid states are observable.
10. **Replay fidelity**: Replay must reproduce identical deal order, move sequences, AI decisions, and final scores for any given seed.
