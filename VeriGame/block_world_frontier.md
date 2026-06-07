# block_world_frontier - Block World Frontier

## 1. Product Definition
- **Prototype Anchor**: Minecraft
- **Genre Family**: Adventure / Sandbox
- **Core Fantasy**: Open-ended voxel survival and building with crafting, exploration, and automation.
- **Camera / Presentation**: First-person 3D (optional third person).
- **Target Session Length**: Open-ended; no strict run duration.
- **Target Skill Curve**: Easy to learn in first 2 minutes, mastery depth through route optimization and system exploitation.

## 2. Win/Lose Contract
- **Primary Win Condition**: Optional milestone: defeat world boss or complete custom objective.
- **Primary Lose Condition**: In survival mode, death drops inventory and respawns player.
- **World/Board Definition**: Infinite chunked world, chunk size 16x16x256.
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
| Move/Look | `WASD + Mouse` | FPS movement and camera |
| Mine/Attack | `LMB` | block break progress over time |
| Place/Use | `RMB` | place block on valid face |
| Inventory | `E` | crafting and item management |
| Hotbar | `1-9` | quick item selection |

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
| `block` | world atom | hardness/light/emission | voxel updates with neighbor events |
| `mob` | ecosystem actor | passive/neutral/hostile | spawn by biome/light rules |
| `craft_station` | production | input/output slots | recipe graph |
| `liquid_cell` | fluid simulation | flow level 0..8 | cellular spread model |

### 6.1 Player Baseline Stats
- `max_hp`: 20
- `move_speed`: 4.3
- `invulnerability_seconds`: 0.0
- `collision_size`: 0.6 (tile or normalized unit)

### 6.2 Shared Entity Component Contract
- `Transform`: position, rotation (if applicable), scale.
- `Kinematics`: velocity, acceleration, friction/drag.
- `Collider`: shape, layer, mask, continuous/discrete mode.
- `Health`: current, max, resistances, immunity flags.
- `State`: FSM state name, timers, transition lock flags.
- `Drops/Rewards`: optional table id, chance, quantity.

## 7. Rule System (Numeric and Deterministic)
- Server tick 20Hz; render independent target 60 FPS.
- Block break time = hardness / tool_efficiency * status_modifiers.
- Mob spawning requires low light and valid floor in loaded chunks.
- Crafting validates exact recipe pattern for shaped recipes.
- Chunk streaming radius configurable; unload saves modified voxel data.
- Death creates item-drop entities with despawn timer.

### 7.1 Collision Matrix
| Channel A | Channel B | Resolution |
|---|---|---|
| `player` | `enemy` | damage exchange or knockback according to category rules |
| `player_projectile` | `enemy` | apply projectile damage, status, and hit-stop |
| `enemy_projectile` | `player` | apply damage and i-frame validation |
| `player` | `pickup` | collect resource and emit pickup event |
| `dynamic` | `world_static` | resolve penetration and velocity response |

### 7.2 Resource Model
- `health`
- `hunger`
- `xp`
- `inventory`
- `durability`

### 7.3 Scoring Formula
- **Primary Formula**: `optional progression score = exploration + crafting + combat milestones`
- **Mandatory Property**: Score updates occur in logic step only; never in render callbacks.
- **Ranking Model**: 3-star thresholds loaded from config and shown pre-level.

## 8. Progression and Difficulty Table
| Stage | Trigger | Gameplay Change |
|---|---|---|
| Tier 1 | wood/stone | basic shelter and tools |
| Tier 2 | metal | durable tools and utility blocks |
| Tier 3 | enchant/advanced | dimension travel and automation |

### 8.1 Difficulty Scaling Parameters
- Scale vectors should be externalized: enemy HP multipliers, speed multipliers, spawn cadence, objective pressure.
- Scaling must be monotonic per stage unless explicitly tagged as relief stage.
- Any stage transition should be event-driven and replay-visible.

## 9. UI/HUD Specification
- Bottom hotbar and vital bars
- Inventory and crafting grids
- Debug overlay for chunk/perf metrics

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
- Material-specific break/place sounds
- Biome ambiance layers
- Night danger layer for hostile proximity

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
    "mode": "sandbox"
  },
  "timing": {
    "logic_fps": 60,
    "max_catchup_steps": 5,
    "pause_stops_timers": true
  },
  "player": {
    "hp": 20,
    "max_hp": 20,
    "speed": 4.3,
    "invuln_seconds": 0.0,
    "hitbox_tiles": 0.6
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
    "hp": 20,
    "status_flags": []
  },
  "resources": {
    "health": 0,
    "hunger": 0,
    "xp": 0,
    "inventory": 0,
    "durability": 0
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

