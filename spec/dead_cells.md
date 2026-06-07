# Dead Cells - Complete Game Specification

> A comprehensive specification for recreating Dead Cells (Motion Twin, 2018), the single-player roguelite action platformer. This spec focuses on responsive combat, procedural level assembly, weapon synergies, permanent unlocks, and boss-based run structure.

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Dead Cells |
| Developer | Motion Twin |
| Initial Release | August 6, 2018 |
| Source Store | Steam, App Store |
| Genre | Roguelite action platformer / metroidvania-inspired |
| Perspective | Side-view 2D |
| Input | Keyboard/gamepad; touch controls for mobile |
| Session Length | 30-60 minutes per full run |
| Primary Objective | Fight through interconnected biomes, collect gear, defeat bosses, and escape |
| Lose Condition | Player HP reaches 0; run restarts with permanent unlock progress retained |
| Win Condition | Defeat the final boss for the current difficulty tier |
| Online Requirement | None |

## 2. AI-Generation Scope

Minimum viable clone:

- Responsive 2D controller with jump, double jump, roll, melee, ranged, skill, heal, and interact.
- Procedurally assembled rooms connected into a biome path.
- Gear rarity, affixes, scroll stat scaling, enemies, elites, timed doors, and two bosses.
- Cells as permanent unlock currency between biomes.

High-fidelity target:

- Multiple routes, biome keys, boss cells difficulty ladder, mutations, cursed chests, legendary gear, malaise-style pressure, and blueprint unlocks.

## 3. Technical Foundation

| System | Requirement |
|--------|-------------|
| Rendering | 2D sprites or skeletal animation with tilemap collision |
| Camera | Smooth side-scrolling camera with look-ahead |
| Physics | Kinematic character controller; deterministic hitboxes |
| Level Generation | Select authored room chunks and stitch with doors, elevators, and teleporters |
| Save | Persistent meta-progression; run state checkpoint at biome transitions only |
| Frame Feel | Low input latency; combat should buffer inputs and support cancel windows |

Frame update:

```text
1. Read movement, jump, roll, attack, skill, heal, and interact inputs
2. Update player controller, gravity, ledge/platform rules
3. Update enemies and telegraphed attacks
4. Advance weapons, cooldowns, traps, projectiles, and status effects
5. Resolve hitbox/hurtbox collisions
6. Apply damage, stun, knockback, breach, and death
7. Collect gold, cells, scrolls, food, and blueprints
8. Check room locks, doors, biome exit, and boss defeat
9. Render world, entities, VFX, UI, and minimap
```

## 4. Player Controller

Core moves:

| Action | Requirement |
|--------|-------------|
| Run | Immediate acceleration with responsive direction changes |
| Jump | Variable height based on button hold |
| Double Jump | One extra jump in air by default |
| Drop-Through | Down+jump passes through one-way platforms |
| Roll | Short invulnerability, passes through enemies, cooldown after use |
| Ground Slam | Down attack in air; damages enemies below and breaks weak floors |
| Wall Interaction | Wall climb or wall jump can be unlocked by rune-style abilities |
| Heal Flask | Limited charges; long animation that can be interrupted by damage |

Roll tuning:

- Invulnerability starts almost immediately.
- Roll cannot be spammed continuously; enforce recovery.
- Roll can cancel some movement recovery but not every attack.

## 5. Combat Model

Player equipment slots:

- Main weapon slot 1.
- Main weapon slot 2.
- Skill slot 1.
- Skill slot 2.
- Amulet passive.

Weapon definition:

```text
name, category, scaling_color, base_damage, combo_steps, windup,
active_frames, recovery, crit_condition, breach_damage, affixes, ammo_or_cooldown
```

Damage colors:

| Color | Build Identity |
|-------|----------------|
| Brutality | Fast melee, bleeding, aggressive close combat |
| Tactics | Ranged weapons, turrets, traps, high damage low HP |
| Survival | Heavy weapons, shields, health, freeze, control |

Critical hits are conditional, not random. Examples: hit after parry, hit rooted enemy, hit from behind, final combo strike, or long-range shot.

## 6. Enemy System

Enemy definition:

```text
id, biome_tags, hp, damage, detection_range, attack_patterns,
telegraph_duration, cooldown, movement_type, elite_modifiers, drops
```

Enemy archetypes:

- Zombie: basic leap or slash.
- Archer: ranged line projectile.
- Shieldbearer: blocks front attacks, vulnerable from behind.
- Runner: fast melee chase.
- Grenadier: lobs explosive projectile.
- Kamikaze: flying approach and explosion.
- Inquisitor: fires through walls.
- Golem: pulls player and slams.
- Elite: empowered enemy with aura, minions, shields, and higher rewards.

All dangerous attacks require clear telegraphs. Fairness depends on letting the player see and react.

## 7. Procedural Biomes

A biome is a sequence of authored chunks.

Room chunk fields:

```text
id, size, entrances, exits, difficulty, enemy_slots, treasure_slots,
secret_slots, traversal_requirements, theme
```

Generation process:

1. Choose route graph for the current biome.
2. Place start room and exit room.
3. Fill path with combat rooms, traversal rooms, shops, treasure rooms, lore rooms, and challenge rooms.
4. Add teleporters at intervals to reduce backtracking.
5. Place locked doors, timed doors, and optional cursed chest rooms.
6. Validate that exits are reachable with current permanent abilities.

## 8. Scrolls, Gear, And Scaling

Scrolls increase one or two damage colors and max HP.

- Brutality, Tactics, and Survival affect matching gear damage.
- Dual-color gear uses the higher matching stat.
- Off-color gear still works but scales poorly.

Gear rarity:

| Rarity | Behavior |
|--------|----------|
| Normal | Basic item with few affixes |
| Plus | Higher level and more affixes |
| Plus Plus | Stronger version in later biomes |
| S | Best standard tier with more affixes |
| Legendary | Special scaling and unique affix behavior |

Affixes can add burning oil synergy, poison, bleeding, extra damage to statused enemies, ammo return, pierce, or cooldown reduction.

## 9. Meta-Progression

Cells drop from enemies and are spent at the Collector between biomes.

Unlock categories:

- New weapons.
- New skills.
- Mutations.
- Health flask upgrades.
- Starting gold retention.
- Random starting weapon quality.
- Specialist shops and recycling.

Blueprints unlock items for future runs but should not immediately add them to the item pool until cells are spent.

## 10. Mutations

After each boss or transition, the player can choose mutations:

- Damage after kill.
- Cooldown reduction on melee kill.
- Ammo recovery.
- More healing efficiency.
- Parry bonus.
- Extra life equivalent with strict limits.

Mutations can be reset for gold between biomes.

## 11. Boss Encounters

Boss design rules:

- Arena is locked until boss death.
- Boss has phases based on HP thresholds.
- Attacks must be telegraphed through animation, sound, or ground markers.
- Boss cannot be permanently stun-locked.
- Victory drops cells, gold, and a transition reward.

Example bosses:

- Concierge: leaps, fire waves, aura, stomp.
- Time Keeper: sword combos, shuriken, hook pull, phase speed-up.
- Hand-style final boss: lance charges, bombs, banners, summons, ground slam.

## 12. UI Layout

- Top left: HP bar, flask charges, status effects.
- Bottom left/right: equipped weapons and skills with cooldown/ammo.
- Top right: minimap, gold, cells.
- Popups: item comparison, scroll selection, mutation selection.
- Pause menu: current build, biome route, settings, quit.

## 13. Visual And Audio Direction

- Combat hit sparks must show impact direction and damage type.
- Elite enemies need obvious outline or aura.
- Secret walls can shimmer subtly after player passes nearby.
- Music should shift by biome and intensify for bosses.
- Important sounds: parry, crit, roll, flask, cell pickup, cursed chest.

## 14. Validation Checklist

- Roll avoids a telegraphed attack only during invulnerability frames.
- Weapon crit conditions produce different damage than normal hits.
- Generated biomes always have reachable exit rooms.
- Cells are lost on death unless banked at the Collector.
- Blueprints require cell investment before entering the item pool.
- Boss attacks remain dodgeable without hidden knowledge.

