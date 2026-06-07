# Brotato - Complete Game Specification

> A comprehensive specification for recreating Brotato (Blobfish, 2023), the top-down arena roguelite shooter. The game is built around short waves, automatic weapons, stat-heavy builds, and shop drafting.

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | Brotato |
| Developer | Blobfish |
| Initial Release | June 23, 2023 |
| Source Store | Steam, App Store |
| Genre | Action roguelite / arena shooter |
| Perspective | Top-down 2D single-screen arena |
| Input | Movement plus optional aim mode; menus use mouse/touch |
| Session Length | 15-30 minutes for a full 20-wave run |
| Primary Objective | Survive 20 waves while building a character through weapons, items, and stats |
| Lose Condition | Player HP reaches 0 during a wave |
| Win Condition | Clear wave 20, optionally defeating the final elite or boss |
| Online Requirement | None |

## 2. AI-Generation Scope

Minimum viable clone:

- Single-screen arena, 20 waves, auto-targeting weapons, materials, XP, level-up stat choices, and shop rerolls.
- At least 10 characters, 30 items, 15 weapons, 12 enemy types, and elite/boss waves.
- Clear stat panel and item tooltips.

High-fidelity target:

- Danger levels, character unlocks, item tags, weapon sets, harvesting economy, engineering summons, elemental/status builds, and endless mode.

## 3. Technical Foundation

| System | Requirement |
|--------|-------------|
| Rendering | 2D sprites with simple hit circles |
| Camera | Fixed single arena, no scrolling required |
| Timing | Each wave has a countdown timer, usually 20-90 seconds depending on wave |
| Entity Pooling | Required for bullets, enemies, materials, and damage numbers |
| Save | Persistent unlocks and settings; run can save between shop phases |

Wave loop:

```text
1. Start wave and reset wave timer
2. Spawn enemies from perimeter using wave budget
3. Update player movement and optional aim direction
4. Update all weapons based on cooldown and targeting rules
5. Resolve hits, knockback, status effects, and deaths
6. Drop materials and XP from enemies
7. End wave when timer reaches 0 and player is alive
8. Vacuum remaining materials to player
9. Resolve level-ups, then enter shop
10. Player buys, combines, locks, sells, rerolls, then starts next wave
```

## 4. Player Stats

| Stat | Effect |
|------|--------|
| Max HP | Maximum health |
| HP Regeneration | Passive healing over time |
| Life Steal | Chance to heal on weapon hit |
| Damage | Global damage percent |
| Melee Damage | Added to melee weapon scaling |
| Ranged Damage | Added to ranged weapon scaling |
| Elemental Damage | Added to elemental and burn weapons |
| Engineering | Improves turrets, mines, and structures |
| Attack Speed | Reduces weapon cooldowns |
| Crit Chance | Chance for critical hit |
| Range | Increases weapon range and projectile reach |
| Armor | Reduces incoming damage |
| Dodge | Chance to ignore incoming hit |
| Speed | Movement speed |
| Luck | Improves drops, crates, and shop rarity |
| Harvesting | Grants materials and grows between waves |

Stats can be negative. Negative stats must still produce predictable behavior, such as slower movement or reduced range.

## 5. Weapons

The player can hold up to 6 weapons. Weapons have tiers I-IV and may combine:

- Two identical weapons of the same tier combine into one weapon of the next tier.
- Higher tiers improve damage, cooldown, projectile count, crit, or secondary effects.

Weapon fields:

```text
name, tier, class_tags, damage_formula, cooldown, range, crit_chance,
crit_multiplier, knockback, targeting_rule, projectile_speed, special_effect
```

Weapon classes:

| Class | Examples | Build Role |
|-------|----------|------------|
| Blade | Knife, Sword | Fast melee crit |
| Blunt | Stick, Rock | Cheap scaling and knockback |
| Gun | Pistol, SMG, Shotgun | Ranged damage and fire rate |
| Heavy | Rocket Launcher, Minigun | Area damage or late-game scaling |
| Elemental | Wand, Flamethrower | Burn and elemental stat |
| Engineering | Wrench, Screwdriver | Turrets and mines |
| Medical | Medical Gun, Scissors | Sustain |

## 6. Combat Rules

- Contact with enemies damages the player after a short invulnerability window.
- Most weapons auto-target the nearest enemy inside range.
- Melee weapons create an arc or thrust hitbox.
- Ranged weapons fire projectiles that collide with the first enemy unless piercing is specified.
- Burn applies damage over time and can spread through items.
- Knockback pushes enemies away from the player or impact center.
- Enemy projectiles are optional for early implementation but should appear on later waves.

## 7. Enemy Waves

Enemy definitions:

```text
id, hp, speed, damage, material_drop, xp_value, behavior, wave_range,
spawn_weight, elite_flag
```

Enemy behaviors:

- Chaser: moves directly at player.
- Charger: pauses, then rushes in a straight line.
- Shooter: keeps distance and fires projectiles.
- Buffer: increases nearby enemy stats.
- Exploder: detonates on death or proximity.
- Loot carrier: drops a crate when killed.
- Elite: large enemy with telegraphed attacks and unique patterns.

Wave pacing:

- Waves 1-5: basic chasers, teach movement.
- Waves 6-10: add chargers and shooters.
- Waves 11-15: higher density, tank enemies, elites.
- Waves 16-19: mixed swarms and projectile pressure.
- Wave 20: final boss or elite pair plus dense adds.

## 8. Shop And Economy

After each wave, the shop displays four offers:

- Weapons and items appear by rarity.
- Player may buy, reroll, lock, combine, or sell.
- Reroll cost increases during the shop visit and resets next shop.
- Locking keeps selected offers for the next shop.
- Crates collected during waves open before or during shop.

Materials are both currency and XP source. Materials left on the ground at wave end are automatically collected. Some items modify material pickup, harvesting, or shop prices.

## 9. Character System

Each character changes build incentives.

Character definition:

```text
name, starting_weapon_options, stat_modifiers, unique_rule,
unlock_condition, recommended_tags
```

Examples:

- Well-Rounded: small positive all-around stats.
- Brawler: strong unarmed/melee, weak ranged.
- Ranger: strong ranged, weak melee.
- Engineer: structures scale with Engineering, weak normal damage.
- Pacifist: gains rewards for leaving enemies alive, low damage.
- One-Armed: one weapon slot, very high attack speed.

## 10. Items

Items are passive modifiers. Each item should specify:

```text
name, rarity, cost, stat_changes, conditional_effect, tags
```

Item categories:

- Flat stat boosters.
- Tradeoff items with positive and negative stats.
- Economy items.
- On-hit effects.
- On-kill effects.
- Summons and structures.
- Build-defining items that transform core rules.

The UI must show all stat deltas before purchase.

## 11. UI Layout

- During wave: timer top center, HP bar near player or top left, wave number, material count, XP bar.
- Between waves: level-up cards first, then shop.
- Shop: four offer cards, character stats panel, inventory list, lock toggles, reroll button, start wave button.
- Tooltips: exact stat math and weapon scaling.

## 12. Visual And Audio Direction

- High-contrast arena floor so enemies and materials remain readable.
- Damage numbers should be small and fade quickly.
- Materials should magnetize cleanly at wave end.
- Shop sound effects are important: buy, combine, reroll, lock, error.
- Weapon firing sounds should vary enough that builds feel distinct.

## 13. Validation Checklist

- A 20-wave run can be completed without manual aiming.
- Combining two same-tier weapons produces the next tier.
- Negative stats affect gameplay without breaking math.
- Shop lock preserves selected offers across one reroll or wave.
- Harvesting grants materials between waves.
- Wave 20 victory unlocks the character or difficulty reward.

