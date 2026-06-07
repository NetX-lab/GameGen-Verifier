# card_battle_coliseum - Card Battle Coliseum

## 1. Product Definition
- **Prototype Anchor**: Hearthstone
- **Genre Family**: Board / Card Battle
- **Core Fantasy**: Turn-based deck duel where mana curve, board control, and hand management determine victory.
- **Camera / Presentation**: 2D tabletop board.
- **Target Session Length**: 8-20 minutes per match.
- **Target Skill Curve**: Easy to learn in first 2 minutes, mastery depth through route optimization and system exploitation.

## 2. Win/Lose Contract
- **Primary Win Condition**: Reduce opposing hero to 0 HP.
- **Primary Lose Condition**: Own hero reaches 0 HP.
- **World/Board Definition**: 30-card decks, 7 board slots, 10 hand cap.
- **Tie-Break Rule**: If simultaneous win/lose triggers in same tick, resolve with deterministic priority: `lose -> win -> result`; if game design demands opposite, override in config and document.

## 3. Core Loop (Implementation Sequence)
1. Read current objective and progression stage.
2. Sample and sanitize input; enqueue buffered commands.
3. Update player state machine and ability windows.
4. Execute AI planners and movement/pathing.
5. Resolve collisions and rule events in fixed order.
6. Apply score/resource updates and progression triggers.
7. Emit HUD/audio/VFX events from authoritative state.
8. Evaluate win/lose and transition state if needed.

## 4. Input Specification
| Action | Default Input | Technical Constraint |
|---|---|---|
| Play Card | `Drag card to board/target` | Must satisfy cost and target filters |
| Attack | `Drag attacker to target` | Entity must be attack-ready |
| Inspect | `Right Click` | Shows keywords and source info |
| End Turn | `Space` | Locks further actions this turn |

## 5. Top-Level State Machines
### 5.1 Application State Machine
- `Boot`: load config, input bindings, save profile, seed strategy.
- `MainMenu`: mode selection, options, accessibility settings.
- `Loading`: prewarm assets and initialize deterministic runtime state.
- `Run`: active simulation state (substates below).
- `Result`: immutable summary view; supports replay/export/restart.

### 5.2 Run Substate Machine
- `Prepare`: spawn/reset entities, reset timers, run countdown.
- `Active`: full simulation running.
- `Paused`: gameplay timers frozen; menu interactions allowed.
- `Resolve`: freeze player controls, run reward/failure pipeline.

### 5.3 Player State Machine
- `Idle` -> default controllable state when no high-priority action is active.
- `Move` -> active when movement input is non-zero and movement is permitted.
- `Action` -> primary interaction/attack state with optional cancel windows.
- `Hurt` -> temporary interrupt on damage or hazard contact.
- `Invulnerable` -> optional substate for dodge/spawn grace windows.
- `Dead` -> terminal run state until respawn or run end.

### 5.4 Enemy/Threat State Machine
- `Spawn`: initialize stats, play spawn telegraph if configured.
- `Approach`: path toward target objective or player.
- `Attack`: execute attack script when target in range and cooldown ready.
- `Recover`: short post-action state before next decision cycle.
- `Retreat/Reset`: optional reposition if health threshold or objective logic requires.
- `Death`: drop table resolution and despawn scheduling.

## 6. Entity Specification Table
| Entity ID | Role | Key Stats | Runtime Behavior |
|---|---|---|---|
| `hero` | core unit | hp=30 armor>=0 | active power once per turn |
| `minion` | board unit | atk/hp/keywords | summoning sickness unless charge |
| `spell` | one-shot effect | mana cost | resolved then graveyard |
| `weapon` | hero attack source | atk/durability | 1 attack per turn |

### 6.1 Player Baseline Stats
- `max_hp`: 30
- `move_speed`: 0
- `invulnerability_seconds`: 0
- `collision_size`: 0 (tile or normalized unit)

### 6.2 Shared Entity Component Contract
- `Transform`: position, rotation (if applicable), scale.
- `Kinematics`: velocity, acceleration, friction/drag.
- `Collider`: shape, layer, mask, continuous/discrete mode.
- `Health`: current, max, resistances, immunity flags.
- `State`: FSM state name, timers, transition lock flags.
- `Drops/Rewards`: optional table id, chance, quantity.

## 7. Rule System (Numeric and Deterministic)
- Mana crystal increases by 1 each turn up to 10.
- Hand limit 10; overdraw burns card.
- Fatigue starts when drawing from empty deck; damage escalates 1,2,3...
- Combat simultaneous between attacker and defender unless spell effect says otherwise.
- Taunt restricts legal attack targets to taunt units.
- RNG effects must use seeded stream for deterministic replay mode.

### 7.1 Collision Matrix
| Channel A | Channel B | Resolution |
|---|---|---|
| `player` | `enemy` | damage exchange or knockback according to category rules |
| `player_projectile` | `enemy` | apply projectile damage, status, and hit-stop |
| `enemy_projectile` | `player` | apply damage and i-frame validation |
| `player` | `pickup` | collect resource and emit pickup event |
| `dynamic` | `world_static` | resolve penetration and velocity response |
| `tile_swap_or_piece` | `board_rules` | validate legal move then resolve chain/update |

### 7.2 Resource Model
- `mana`
- `hand`
- `deck`
- `board`
- `hp`
- `armor`

### 7.3 Scoring Formula
- **Primary Formula**: `ladder_mmr_delta derived externally; match stats include damage, board control turns, and resource efficiency`
- **Mandatory Property**: Score updates occur in logic step only; never in render callbacks.
- **Ranking Model**: 3-star thresholds loaded from config and shown pre-level.

## 8. Progression and Difficulty Table
| Stage | Trigger | Gameplay Change |
|---|---|---|
| Turns 1-3 | tempo setup | curve out low-cost minions |
| Turns 4-7 | board contest | removal and value trades |
| Turns 8+ | finishers | high-cost win conditions |

### 8.1 Difficulty Scaling Parameters
- Scale vectors should be externalized: enemy HP multipliers, speed multipliers, spawn cadence, objective pressure.
- Scaling must be monotonic per stage unless explicitly tagged as relief stage.
- Any stage transition should be event-driven and replay-visible.

## 9. UI/HUD Specification
- Mana crystals and turn indicator
- Hero HP/armor and deck count
- Card hover popups and keyword glossary

### 9.1 Mandatory Screens
- Main Menu
- In-Run HUD
- Pause Menu
- Settings (input/audio/accessibility)
- Result Screen with stat breakdown and restart controls

### 9.2 HUD Update Constraints
- Critical values (HP, timer, objective) update every logic tick.
- Non-critical decorations can update at render rate.
- No UI element may source data from stale cached duplicates.

## 10. Audio and Feedback Matrix
- Distinct play/attack/death cues
- Turn start/end chimes
- Lethal threat tension layer

### 10.1 Event Bus Audio Contract
- `OnSpawn(entity_type)`
- `OnHit(attacker, defender, damage_type)`
- `OnPickup(item_type, amount)`
- `OnObjectiveProgress(step_id)`
- `OnDanger(level)`
- `OnWin` / `OnLose`

## 11. Data Contracts
### 11.1 Config Schema Example
```json
{
  "game": {
    "version": "1.0.0",
    "seed": 123456,
    "difficulty": "normal",
    "mode": "card_battle"
  },
  "timing": {
    "logic_fps": 60,
    "max_catchup_steps": 5,
    "pause_stops_timers": true
  },
  "player": {
    "hp": 30,
    "max_hp": 30,
    "speed": 0,
    "invuln_seconds": 0,
    "hitbox_tiles": 0
  },
  "scoring": {
    "formula": "data-driven",
    "rank_thresholds": [
      10000,
      25000,
      50000
    ]
  }
}
```

### 11.2 Runtime Snapshot Schema Example
```json
{
  "time": {
    "tick": 0,
    "elapsed_seconds": 0.0,
    "paused": false
  },
  "run": {
    "state": "Active",
    "stage": "Stage 1",
    "seed": 123456
  },
  "player": {
    "position": {
      "x": 0.0,
      "y": 0.0
    },
    "velocity": {
      "x": 0.0,
      "y": 0.0
    },
    "hp": 30,
    "status_flags": []
  },
  "resources": {
    "mana": 0,
    "hand": 0,
    "deck": 0,
    "board": 0,
    "hp": 0,
    "armor": 0
  },
  "entities": [
    {
      "id": "e_001",
      "type": "enemy",
      "state": "Approach",
      "hp": 100,
      "alive": true
    }
  ],
  "events": [
    {
      "tick": 120,
      "type": "spawn",
      "payload": {
        "entity": "enemy_basic"
      }
    }
  ]
}
```

### 11.3 Save/Load Requirements
- Save format versioned with migration path.
- Save operation must be atomic (write temp -> fsync -> rename).
- Load validation rejects malformed data and falls back safely.

## 12. Technical Requirements
- Simulation tick: fixed `dt = 1/60` for deterministic gameplay decisions.
- Update order: `Input -> AI -> Movement -> Collision -> Damage/Rules -> Spawning -> UI/EventBus`.
- All random decisions must consume a seeded RNG stream (single source of truth).
- Entity lifecycle contract: `spawn -> activate -> disable -> recycle/despawn`.
- No gameplay rule is allowed in renderer-only code path.
- Pause freezes gameplay timers, cooldown timers, and AI planners.
- 2x simulation speed must preserve deterministic outcomes (same seed, same inputs).
- Support at least 10-second input replay logs for bug reproduction.

### 12.1 Performance Budget
- Target render frame budget: 16.67ms at 60 FPS.
- Logic update budget: <= 4ms average, <= 8ms p99.
- Audio thread must not block gameplay thread.
- Stress scenario must be documented and reproducible.

### 12.2 Determinism and Replay
- Replay record format: initial seed + input events (tick, action, value).
- Deterministic checksum each 300 ticks for debug verification.
- Mismatch handling: dump state diff and event trace.

## 13. Telemetry (For Evaluation and Balancing)
- Run duration
- Win/Lose reason code
- Damage taken/dealt timelines
- Objective completion timeline
- Input error rate (invalid/late inputs)
- Stage transition times
- Frame-time histogram and spike markers

## 14. Accessibility and UX Safety
- Remappable controls for keyboard/gamepad.
- Independent sliders: master, music, SFX, UI.
- Colorblind-safe critical indicators (shape + color).
- Optional reduced camera shake and flash intensity controls.
- Subtitle/text-scale options where narrative text exists.

## 15. QA Acceptance Matrix
1. Win condition triggers exactly once and transitions to result state within 1 logic tick.
2. Lose condition triggers exactly once and prevents additional score gain.
3. Pause/resume does not desync timers, cooldowns, or AI state.
4. Restart creates clean state (no stale entities, no stale timers).
5. Seeded run replay with same input stream produces identical key events.
6. Running at 2x speed preserves logical outcomes compared to 1x speed.
7. No entity can leave world bounds without explicit wrap or despawn rule.
8. UI values are updated from authoritative game state, not local duplicates.
9. Audio event spam protection prevents duplicate trigger bursts in the same frame.
10. Saving/loading runtime snapshot restores score, timers, and entity states correctly.
11. Edge case: rapid pause/unpause spam does not duplicate frame updates.
12. Edge case: objective completion and lethal damage in same frame resolve by documented priority.
13. Performance: maintain target frame budget in stress scenario (entity cap / max effects).
14. Input: remapped keys persist across restart and are loaded on boot.
15. Audio: muting SFX or BGM independently does not affect gameplay timers.
16. Localization safety: long strings do not overlap HUD anchors.

## 16. Engineering Milestones
- Milestone 1 - Core Loop: boot, menu, run state, pause, restart, deterministic tick loop.
- Milestone 2 - Input + Movement: all control bindings, buffering, state transitions, collision with world.
- Milestone 3 - Rule Engine: scoring/resources/win-lose logic and deterministic event ordering.
- Milestone 4 - Content: entities, progression schedule, balancing data in external config.
- Milestone 5 - UX: HUD, feedback, audio event routing, settings.
- Milestone 6 - QA: replay validation, edge-case tests, performance pass.

## 17. Non-Negotiable Implementation Constraints
- Do not hardcode balancing numbers inside gameplay methods.
- All win/lose transitions must be centralized in one rule module.
- Every harmful interaction must call a unified damage API.
- Every collectible interaction must call a unified pickup API.
- Every major transition must emit an analytics/debug event.
- Any behavior that depends on randomness must consume seeded RNG only.

