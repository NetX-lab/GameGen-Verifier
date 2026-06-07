# The Legend of Zelda (NES, 1986) — Complete Game Specification

> A comprehensive specification for faithfully recreating the original The Legend of Zelda (Nintendo, 1986 NES/Famicom version). This document covers every system, mechanic, entity, and interaction required for a full clone.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Core Mechanics](#3-core-mechanics)
4. [Player Stats & Equipment](#4-player-stats--equipment)
5. [All Items & Weapons](#5-all-items--weapons)
6. [Overworld Map Structure](#6-overworld-map-structure)
7. [All 9 Dungeons (First Quest)](#7-all-9-dungeons-first-quest)
8. [All Enemy Types](#8-all-enemy-types)
9. [Boss Encounters](#9-boss-encounters)
10. [Economy System](#10-economy-system)
11. [Secrets, Caves & NPCs](#11-secrets-caves--npcs)
12. [Second Quest](#12-second-quest)
13. [UI Layout](#13-ui-layout)
14. [Save System & Game Flow](#14-save-system--game-flow)
15. [Audio Design](#15-audio-design)

---

## 1. Game Overview

| Property | Value |
|----------|-------|
| Title | The Legend of Zelda |
| Platform | Nintendo Entertainment System (NES) / Famicom Disk System |
| Release | February 21, 1986 (JP), August 22, 1987 (NA) |
| Developer | Nintendo R&D4 |
| Director | Shigeru Miyamoto, Takashi Tezuka |
| Composer | Koji Kondo |
| Genre | Action-adventure |
| Perspective | Top-down 2D |
| Input | NES controller (D-pad + A + B + Start + Select) |
| Players | 1 |

### Objective

Princess Zelda has shattered the Triforce of Wisdom into eight fragments and hidden them in eight dungeons across Hyrule. The player controls Link, who must recover all eight Triforce fragments, enter the ninth dungeon (Death Mountain), defeat the evil Ganon, and rescue Princess Zelda.

### Win Condition

Collect all 8 Triforce of Wisdom fragments from Dungeons 1-8, enter Dungeon 9, defeat Ganon with the Silver Arrow, and rescue Zelda.

### Lose Condition

Link's hearts reach zero. Upon death, the player may continue (respawning at the starting screen on the overworld, or at the entrance of the current dungeon) or save and quit.

---

## 2. Technical Foundation

### Display & Rendering

| Property | Value |
|----------|-------|
| Native resolution | 256 x 240 pixels (NTSC) |
| Visible play area | 256 x 176 pixels (bottom 176 px; top 64 px is HUD) |
| Tile size | 16 x 16 pixels |
| Frame rate | 60.098 FPS (NTSC) |
| Sprite limit | 64 sprites on screen, max 8 per scanline |
| Sprite size | 8 x 16 pixels (hardware); Link composed of multiple sprites |
| Color palette | 52 usable colors system-wide |
| On-screen colors | 25 max (4 background palettes of 4 colors + 4 sprite palettes of 3 colors + shared background color) |
| Cartridge type | MMC1 mapper, 128 KB PRG-ROM, 0 KB CHR-ROM (CHR-RAM), battery-backed SRAM |

### Screen Structure

| Region | Pixel rows | Purpose |
|--------|-----------|---------|
| HUD / Status bar | Y 0-55 (56 px) | Minimap, item display, life meter, counters |
| Playfield | Y 56-231 (176 px) | Active game area (11 tile rows, though bottom row is half-visible) |

### Screen Dimensions (Playfield)

| Property | Value |
|----------|-------|
| Width | 256 pixels = 16 tiles |
| Height | 176 pixels = 11 tile rows (bottom row partially rendered) |
| Effective tile grid | 16 columns x 11 rows per screen |

### Coordinate System

- Origin (0, 0) at top-left corner of display.
- Playfield origin at (0, 56) in screen coordinates.
- Overworld and dungeon screens use a column/row address system (column 0-15, row 0-7 for overworld).

### Game Loop

```
1. Read controller input
2. Update game state timers (invincibility frames, stun timers, animation)
3. Process player movement (4 sub-pixel ticks per frame)
4. Process player attacks and item use
5. Update all enemy AI (movement, attack patterns)
6. Update all projectiles (sword beams, arrows, boomerang, enemy projectiles)
7. Check collisions (player vs enemies, player vs projectiles, weapons vs enemies)
8. Apply damage / knockback
9. Check screen transition triggers
10. Update animation frames
11. Render background tiles, then sprites, then HUD
```

### Screen Transitions

| Direction | Speed | Duration |
|-----------|-------|----------|
| Horizontal (left/right) | 4 pixels per frame | ~64 frames (~1.07 seconds) |
| Vertical (up/down) | 8 pixels every 2 frames (4 px/frame avg) | ~44 frames (~0.73 seconds) |
| Cave/stairway entry | Instant (fade to black) | ~30 frames |

During screen transitions, the NES switches nametable mirroring mode (horizontal mirroring switches to vertical during left/right scrolls, and vice versa for vertical scrolls). Enemies despawn from the old screen and spawn fresh on the new screen.

---

## 3. Core Mechanics

### Movement

| Property | Value |
|----------|-------|
| Movement directions | 4 (up, down, left, right) — no diagonal movement |
| Movement speed | 1.5 pixels per frame (subpixel value #$60 per tick, 4 ticks per frame) |
| Movement grid | 8 x 8 pixel half-tile grid |
| Standard tile grid | 16 x 16 pixels |
| Grid alignment | Automatic — if Link is misaligned with the 8px half-tile grid, the game nudges him 1 pixel per movement frame toward the nearest grid vertex |

**Sub-pixel system**: The game stores a sub-pixel position value. Each frame, 4 movement ticks are processed. Per tick, the sub-pixel speed (#$60 = 96/256 of a pixel) is added to/subtracted from the sub-pixel accumulator. When the accumulator overflows (>= 256), Link moves 1 whole pixel. This produces the effective speed of 1.5 pixels per frame (6 ticks out of every 4-frame cycle produce a whole-pixel move).

**Grid alignment correction**: When changing direction, if Link is not aligned to an 8-pixel boundary on the perpendicular axis, the game automatically corrects him 1 pixel per frame toward the nearest boundary. This prevents "snagging" on walls and tile edges and ensures Link lines up with enemies (who use the same grid).

### Collision Detection

- Link's collision hitbox is 8 x 8 pixels centered within his 16 x 16 sprite.
- Walls and obstacles use tile-based collision on the 16 x 16 grid.
- Movement is blocked when Link's leading edge would overlap a solid tile.
- Link cannot walk off the edges of a screen; reaching an edge triggers a screen transition.

### Combat — Sword Attack

| Property | Value |
|----------|-------|
| Attack button | B button |
| Sword reach | 12-16 pixels in facing direction |
| Sword hitbox duration | ~5-6 frames |
| Attack cooldown | Cannot attack again until the animation completes (~12 frames) |
| Movement during attack | Stopped — Link cannot move while attacking |

When Link presses B with a sword equipped, he thrusts the sword in his facing direction. The sword sprite extends from Link's body. Link's movement is halted for the duration of the animation.

### Sword Beam

| Property | Value |
|----------|-------|
| Condition | Link must be at full health (all hearts filled) |
| Projectile speed | ~3 pixels per frame |
| Damage | Same as the equipped sword's base damage |
| Range | Travels to the edge of the screen |
| Limit | Only 1 sword beam on screen at a time |
| Button | B (same as melee attack; beam fires automatically when at full health) |

The beam fires in Link's facing direction. It passes through open space and is destroyed upon hitting an enemy or a wall/obstacle. The beam sprite flashes between colors.

### Knockback

| Property | Value |
|----------|-------|
| Knockback speed | 1 pixel per tick (4 pixels per frame) |
| Knockback duration | 4 ticks (1 frame of knockback movement) |
| Knockback direction | Opposite the direction of the attacking entity/projectile |
| Link knockback | Link is knocked away from the source of damage |
| Enemy knockback | Enemies are knocked in the direction of the sword swing |

### Invincibility Frames

| Entity | Duration |
|--------|----------|
| Link (after taking damage) | ~32 frames (~0.53 seconds) |
| Link (after entering a screen) | ~16 frames |
| Enemies (after being hit) | ~16 frames |

During invincibility frames, the sprite flashes (alternating visible/invisible every 2 frames). The low 2 bits of the invincibility timer also control the sprite palette for the flashing effect.

### B-Button Item Use

The A button is used for the equipped secondary item selected on the subscreen. Items include:

| Item | A-Button Effect |
|------|----------------|
| Boomerang | Throws boomerang in facing direction |
| Bombs | Places bomb at Link's position |
| Bow + Arrow | Fires arrow in facing direction (costs 1 Rupee per shot) |
| Blue Candle | Shoots flame in facing direction (once per screen) |
| Red Candle | Shoots flame in facing direction (unlimited per screen) |
| Recorder | Plays tune; triggers warp tornado or boss effects |
| Food/Bait | Places bait at current location to attract enemies |
| Letter | No combat effect (used to unlock Potion Shop) |
| Magical Rod | Shoots beam in facing direction |
| Magical Rod + Book | Beam creates fire on contact |

**Note**: The B button always swings the sword (if one is equipped). The A button activates the currently selected secondary item.

---

## 4. Player Stats & Equipment

### Health System

| Property | Value |
|----------|-------|
| Health unit | Hearts (each heart = 2 half-hearts internally) |
| Starting hearts | 3 |
| Maximum hearts | 16 |
| Heart Containers obtained | 8 from dungeon bosses + 5 from overworld = 13 gained |
| Damage unit | Half-hearts (1 damage point = 0.5 hearts) |

### Defensive Rings

| Ring | Effect | Acquisition |
|------|--------|-------------|
| No ring | Full damage taken | Default |
| Blue Ring | Damage reduced to 1/2 | Purchase from shop for 250 Rupees |
| Red Ring | Damage reduced to 1/4 | Found in Dungeon 9 |

Rings also change Link's tunic color:
- No ring: Green tunic
- Blue Ring: White/light-blue tunic
- Red Ring: Red tunic

### Shield

| Shield | Effect | Acquisition |
|--------|--------|-------------|
| Small Shield | Blocks enemy projectiles (rocks) from the front; cannot block magic | Starting equipment |
| Magical Shield (Large Shield) | Blocks projectiles AND magic beams from the front; larger hitbox | Purchase from shop (90-160 Rupees) |

**Like Like danger**: If Link is engulfed by a Like Like enemy while carrying the Magical Shield, the Like Like eats the shield. Link reverts to the Small Shield.

### Sword Damage Table

All damage values are in "sword units." 1 sword unit = 1 hit with the Wooden Sword.

| Weapon | Damage (sword units) |
|--------|---------------------|
| Wooden Sword (melee) | 1 |
| Wooden Sword (beam) | 1 |
| White Sword (melee) | 2 |
| White Sword (beam) | 2 |
| Magical Sword (melee) | 4 |
| Magical Sword (beam) | 4 |
| Wooden Arrow | 2 |
| Silver Arrow | 4 |
| Bomb | 4 |
| Boomerang (stun only for most enemies) | 0 (stun) or 1 (kills Keese, Gel, Zol) |
| Magical Boomerang | Same as Boomerang |
| Magical Rod (beam) | 2 |
| Magical Rod + Book (beam + fire) | 2 (beam) + 2 (fire) |
| Blue/Red Candle (fire) | 2 |

---

## 5. All Items & Weapons

### Swords

| Sword | Damage | Location | Requirement |
|-------|--------|----------|-------------|
| Wooden Sword | 1 | Overworld starting cave (screen 7,7 — the cave on the first screen) | None — given by Old Man ("It's dangerous to go alone! Take this.") |
| White Sword | 2 | Overworld cave atop the waterfall (screen 2,2) | 5 or more Heart Containers |
| Magical Sword | 4 | Overworld graveyard cave (screen 4,1) | 12 or more Heart Containers |

### Secondary Items (A-button equippable)

| Item | Effect | Found In | Notes |
|------|--------|----------|-------|
| Boomerang | Stuns most enemies; kills Keese, Gel, Zol; picks up distant items | Dungeon 1: The Eagle | Travels half the screen width then returns |
| Magical Boomerang | Same stun/kill effect, but travels full screen width | Dungeon 2: The Moon | Replaces regular Boomerang |
| Bombs | Explodes after ~2 seconds; damages nearby enemies; reveals bombable walls | Enemy drops / shops (20 Rupees per set of 4) | Starting capacity: 8; upgradeable to 12, then 16 |
| Bow | Required to fire Arrows | Dungeon 1: The Eagle | Useless without purchasing Arrows |
| Arrow | Ranged projectile; costs 1 Rupee per shot | Shop (80 Rupees to acquire ammo capability) | Each shot deducts 1 Rupee |
| Silver Arrow | Enhanced arrow; required to kill Ganon | Dungeon 9: Death Mountain | Replaces regular Arrow |
| Blue Candle | Shoots flame forward; burns bushes to reveal secrets; 1 use per screen | Shop (60 Rupees) | Flame persists ~3 seconds |
| Red Candle | Same as Blue Candle but unlimited uses per screen | Dungeon 7: The Demon | Replaces Blue Candle |
| Recorder (Whistle) | Plays a tune; creates warp tornado; shrinks Digdogger; reveals Dungeon 7 entrance | Dungeon 5: The Lizard | Warp cycles through dungeon entrances 1-8 |
| Food (Bait) | Placed on ground to attract Hungry Goriya and other enemies | Shop (60-100 Rupees) | Required to pass certain blocked rooms |
| Letter | Unlocks the Potion Shop (Old Woman) | Overworld cave (NE region) | Give to Old Woman to activate her shop |
| Magical Rod (Wand) | Fires a beam projectile identical to Wizzrobe attacks | Dungeon 6: The Dragon | Beam does 2 damage |
| Book of Magic | Upgrade to Magical Rod; beams leave fire on contact with enemies or walls | Dungeon 8: The Lion | Stacks with Magical Rod |

### Passive / Automatic Items

| Item | Effect | Found In |
|------|--------|----------|
| Raft | Automatically activates at dock tiles; transports Link across water | Dungeon 3: The Manji |
| Stepladder | Automatically bridges 1-tile gaps (water, lava) when Link walks to the edge | Dungeon 4: The Snake |
| Power Bracelet | Allows Link to push certain boulders in the overworld, revealing staircases | Overworld (under an Armos statue) |
| Magical Key | Opens any locked door without consuming a key; infinite uses | Dungeon 8: The Lion |
| Map | Reveals the dungeon's room layout on the HUD minimap | Found once per dungeon |
| Compass | Shows the location of the Triforce fragment (flashing dot) on the minimap | Found once per dungeon |

### Consumables / Pickups

| Pickup | Effect | Source |
|--------|--------|--------|
| Recovery Heart | Restores 1 heart (2 half-hearts) | Enemy drops, shops (10 Rupees) |
| Fairy | Restores 3 hearts; overworld fairy ponds restore ALL hearts | Random enemy drops, fairy ponds |
| Heart Container | Adds 1 new heart to maximum AND fully heals Link | Dungeon bosses (8), overworld (5) |
| Small Key | Opens one locked door in the current dungeon; consumed on use | Enemy drops, room rewards, shops (80-100 Rupees) |
| Rupee (orange/flashing) | Worth 1 Rupee | Enemy drops, hidden rooms |
| Rupee (blue) | Worth 5 Rupees | Enemy drops |
| Clock | Freezes all enemies on screen for the duration of the current screen | Rare enemy drop |
| Triforce Fragment | Obtained after each dungeon boss (Dungeons 1-8); fully heals Link | Boss rooms |

### Potions

| Potion | Effect | Cost | Requirement |
|--------|--------|------|-------------|
| Blue Potion (Life Potion) | Restores all hearts; single use | 40 Rupees | Must deliver Letter to Old Woman first |
| Red Potion (2nd Potion) | Restores all hearts; two uses (turns into Blue Potion after first use) | 68 Rupees | Must deliver Letter to Old Woman first |

### Bomb Capacity Upgrades

| Upgrade | New Capacity | Cost | Location |
|---------|-------------|------|----------|
| First upgrade | 12 | 100 Rupees | Hidden Old Man cave |
| Second upgrade | 16 | 100 Rupees | Hidden Old Man cave |

---

## 6. Overworld Map Structure

### Grid Layout

| Property | Value |
|----------|-------|
| Grid size | 16 columns x 8 rows = 128 screens |
| Each screen | 16 x 11 tiles (256 x 176 pixels playfield) |
| Total overworld size | 256 x 88 tiles = 4096 x 1408 pixels |
| Column index | 0 (leftmost) to 15 (rightmost) |
| Row index | 0 (topmost) to 7 (bottommost) |
| Starting screen | Column 7, Row 7 (center-south of map) |

### Terrain Types

| Terrain | Tile(s) | Properties |
|---------|---------|------------|
| Grass/Plain | Green tiles | Walkable; most common |
| Forest/Trees | Tree tiles | Blocks movement; some burnable with Candle (reveal caves) |
| Mountain/Rock | Brown/gray rock tiles | Blocks movement; some pushable with Power Bracelet |
| Water/Lake | Blue tiles | Impassable; crossable with Raft (at docks) or Stepladder (1-tile gaps) |
| Sand/Desert | Tan tiles | Walkable; Leevers spawn here |
| Graveyard | Tombstone tiles | Walkable between graves; Ghini spawn; some graves hide caves |
| Bridge | Narrow walkable path over water | Walkable |
| Dock | Special tile at water's edge | Triggers Raft if owned |
| Staircase/Cave entrance | Dark opening in rocks, tree, or ground | Leads to cave interiors or dungeon entrances |

### Overworld Regions

| Region | General Location | Notable Features |
|--------|-----------------|------------------|
| Starting Area | Row 7, columns 5-9 | Starting cave (Wooden Sword), Dungeon 1 nearby |
| Eastern Forest | Rows 5-7, columns 10-15 | Dense trees, Moblins, shops |
| Western Forest/Lost Woods | Rows 4-6, columns 0-3 | Lost Woods puzzle (repeating screens; go N-W-S-W to pass) |
| Lost Hills | Rows 2-3, columns 3-5 | Repeating screens (go N-N-N-N to pass); leads to Dungeon 5 |
| Lake Hylia | Rows 3-5, columns 6-9 | Large lake; dock for Raft |
| Death Mountain | Rows 0-2, columns 0-15 | Mountain maze, boulders, Lynels; Dungeon 9 entrance |
| Graveyard | Rows 1-2, columns 1-4 | Ghini enemies; Magical Sword cave |
| Desert | Rows 3-4, columns 12-14 | Leevers, Zoras at water edges |
| Coastline | Various | Zoras fire projectiles from water tiles |

### Dungeon Entrance Locations (First Quest)

| Dungeon | Name | Overworld Screen (Col, Row) | Access Method |
|---------|------|----------------------------|---------------|
| Level 1 | The Eagle | (7, 3) | Walk into cave entrance (visible) |
| Level 2 | The Moon | (12, 3) | Walk into cave entrance (visible) |
| Level 3 | The Manji | (3, 4) | Walk into cave entrance (visible) |
| Level 4 | The Snake | (3, 2) | Raft from dock on eastern coast to island |
| Level 5 | The Lizard | (5, 1) | Solve Lost Hills puzzle, enter cave |
| Level 6 | The Dragon | (2, 3) | Walk into cave entrance |
| Level 7 | The Demon | (5, 2) | Play Recorder on the correct screen to reveal entrance |
| Level 8 | The Lion | (8, 0) | Burn specific tree with Candle to reveal entrance |
| Level 9 | Death Mountain | (5, 0) | Navigate Death Mountain maze; bomb wall to enter |

### Screen Transition Rules

- Walking off any edge of a screen loads the adjacent screen.
- The overworld wraps: walking off the left edge of column 0 wraps to column 15 (same row), and vice versa. Top/bottom does NOT wrap.
- Enemies reset (despawn and respawn) on every screen transition.
- Link appears on the opposite edge of the new screen (e.g., exiting right places Link at the left edge).
- Items dropped by enemies are lost upon screen transition.

---

## 7. All 9 Dungeons (First Quest)

### Dungeon Common Features

Every dungeon contains:
- **Map**: Reveals room layout on HUD minimap.
- **Compass**: Shows location of Triforce fragment as flashing dot on minimap.
- **Small Keys**: Found in rooms or dropped by enemies; open one locked door each.
- **Locked Doors**: Gray/shuttered doors requiring a key to open; key is consumed.
- **Bombable Walls**: Certain walls (sometimes unmarked) can be bombed to reveal passages.
- **Push Blocks**: One block per room can sometimes be pushed to open a sealed passage or reveal stairs.
- **Old Man Rooms**: Rooms with an Old Man who gives a hint, offers an item, or demands Rupees.
- **Triforce Room**: Final room containing the Triforce fragment (after boss is defeated).

### Dungeon Room Properties

| Property | Value |
|----------|-------|
| Room size | Same as overworld screen: 16 x 11 tiles |
| Door positions | Center of each wall (N, S, E, W) |
| Door types | Open, locked (requires key), shuttered (opens when all enemies killed), bombable (hidden wall) |
| Room grid per dungeon | Up to 8 x 8 rooms (64 rooms max) |

---

### Level 1: The Eagle

| Property | Value |
|----------|-------|
| Shape | Eagle |
| Total rooms | ~6 key rooms |
| Enemies | Stalfos, Keese, Gels, Wallmasters, Goriyas (Red) |
| Key Item | Boomerang |
| Other Item | Bow |
| Boss | Aquamentus |
| Triforce Fragment | #1 |
| Old Man hint | "Eastmost peninsula is the secret." |

**Boomerang**: Found after defeating all enemies in a specific room. The Boomerang stuns most enemies and kills weak ones (Keese, Gels). Travels half the screen width.

**Bow**: Found in a locked room. Required to shoot Arrows (must buy Arrows separately).

---

### Level 2: The Moon

| Property | Value |
|----------|-------|
| Shape | Crescent Moon |
| Enemies | Ropes, Goriyas (Red & Blue), Moldorms, Keese |
| Key Item | Magical Boomerang |
| Boss | Dodongo |
| Triforce Fragment | #2 |
| Old Man hint | "Dodongo dislikes smoke." |

**Magical Boomerang**: Upgrade to regular Boomerang. Travels the full screen width.

**Dodongo strategy**: Feed 2 bombs by placing them in Dodongo's path.

---

### Level 3: The Manji

| Property | Value |
|----------|-------|
| Shape | Manji symbol (swastika-like Buddhist symbol) |
| Enemies | Darknuts (Red), Zols, Keese, Bubbles |
| Key Item | Raft |
| Boss | Manhandla |
| Triforce Fragment | #3 |
| Old Man hint | "Did you get the sword from the old man on top of the waterfall?" |

**Raft**: Allows Link to travel across water from dock tiles. Required to reach Dungeon 4.

**Bubbles**: Invincible bouncing flames. Red Bubbles disable Link's sword use temporarily; Blue Bubbles re-enable it. Touching any Bubble disables sword for several seconds.

---

### Level 4: The Snake

| Property | Value |
|----------|-------|
| Shape | Snake |
| Enemies | Vires, Keese (Red), Like Likes, Zols, Floor Traps |
| Key Item | Stepladder |
| Boss | Gleeok (2 heads) |
| Triforce Fragment | #4 |
| Old Man hint | "Walk into the waterfall." |

**Stepladder**: Automatically bridges 1-tile gaps in water or lava when Link walks to the edge. Essential for reaching certain overworld Heart Containers.

**Floor Traps**: Invincible spike blocks that rush toward Link when he aligns with them horizontally or vertically. They return to their starting position after reaching the opposite wall.

---

### Level 5: The Lizard

| Property | Value |
|----------|-------|
| Shape | Lizard |
| Enemies | Pols Voices, Darknuts (Red & Blue), Gibdos, Keese |
| Key Item | Recorder (Whistle) |
| Boss | Digdogger |
| Triforce Fragment | #5 |
| Old Man hint | "Secret power is said to be in the arrow." |

**Recorder**: Musical item with multiple functions:
1. Creates a warp tornado that transports Link to any previously completed dungeon entrance.
2. Shrinks Digdogger boss, making it vulnerable.
3. When played on the correct overworld screen, reveals the entrance to Dungeon 7.

**Pols Voices**: Large bunny-like enemies with high HP (10 Wooden Sword hits). Vulnerable to Arrows (1 hit kill). In the Famicom version, they could be killed by shouting into the microphone on controller 2.

---

### Level 6: The Dragon

| Property | Value |
|----------|-------|
| Shape | Dragon head |
| Enemies | Wizzrobes (Red & Blue), Like Likes, Vires, Keese (Red), Floor Traps |
| Key Item | Magical Rod (Wand) |
| Boss | Gohma (Red) |
| Triforce Fragment | #6 |
| Old Man hint | "Aim at the eyes of Gohma." |

**Magical Rod**: Fires a beam projectile forward (similar to Wizzrobe attacks). Does 2 damage. Later enhanced by the Book of Magic (Dungeon 8) to create fire on impact.

**Wizzrobes**: Among the most dangerous regular enemies. Red Wizzrobes appear, fire a magic beam, then teleport. Blue Wizzrobes phase through walls and fire continuously.

---

### Level 7: The Demon

| Property | Value |
|----------|-------|
| Shape | Demon face |
| Enemies | Goriyas (Red & Blue), Stalfos, Ropes, Moldorms, Keese, Wallmasters, Bubbles |
| Key Item | Red Candle |
| Boss | Aquamentus (return) |
| Triforce Fragment | #7 |
| Old Man hint | "There's a secret in the tip of the nose." (referring to the demon-shaped dungeon map) |

**Red Candle**: Upgrade to Blue Candle. Shoots flame forward and can be used unlimited times per screen. Burns bushes, damages enemies.

**Dungeon shape hint**: "The tip of the nose" refers to a specific room in the demon-face-shaped map layout where a push block reveals hidden stairs.

---

### Level 8: The Lion

| Property | Value |
|----------|-------|
| Shape | Lion |
| Enemies | Darknuts (Red & Blue), Pols Voices, Gibdos, Keese, Zols, Gels |
| Key Item 1 | Book of Magic |
| Key Item 2 | Magical Key |
| Boss | Gleeok (4 heads) |
| Triforce Fragment | #8 |
| Old Man hint | "Spectacle Rock is an entrance to Death Mountain." |

**Book of Magic**: Upgrades the Magical Rod. Now when the rod's beam hits an enemy or wall, it leaves behind a tile of fire that damages enemies passing through it.

**Magical Key**: Opens any locked door without being consumed. Eliminates the need to find or buy Small Keys for the rest of the game. Essential for navigating Dungeon 9.

---

### Level 9: Death Mountain

| Property | Value |
|----------|-------|
| Shape | Skull |
| Total rooms | 57 (largest dungeon in the game) |
| Enemies | Wizzrobes (Red & Blue), Like Likes, Lanmolas (Red & Blue), Zols, Gels, Keese, Bubbles, Floor Traps, Patra |
| Key Item 1 | Red Ring |
| Key Item 2 | Silver Arrow |
| Boss | Ganon |
| Reward | Rescue Princess Zelda; game completion |
| Old Man hint | "Go to the next room." (multiple rooms of advice) |

**Red Ring**: Reduces all damage to 1/4, the strongest defense in the game. Changes Link's tunic to red.

**Silver Arrow**: Required to deliver the killing blow to Ganon. Without it, Ganon cannot be defeated.

**Patra**: Mini-boss exclusive to Dungeon 9. A large central eye orbited by smaller eyes. The smaller eyes must be destroyed first (they orbit in either a circular 2D pattern or an elliptical 3D-like pattern), then the central eye becomes vulnerable.

**Lanmolas**: Segmented centipede enemies that move erratically. Each segment must be attacked individually. Red Lanmolas are slower; Blue Lanmolas are faster.

---

## 8. All Enemy Types

### Damage System

- Enemy HP is measured in "Wooden Sword hits" (1 unit = damage dealt by one Wooden Sword strike).
- The White Sword does 2x Wooden Sword damage; the Magical Sword does 4x.
- Damage to Link is measured in half-hearts. "2 damage" = 1 full heart lost (without any ring).
- The Blue Ring halves damage to Link; the Red Ring quarters it.

### Overworld Enemies

| Enemy | HP (Wooden / White / Magical Sword hits) | Damage to Link (half-hearts) | Behavior |
|-------|------------------------------------------|------------------------------|----------|
| Octorok (Red) | 1 / 1 / 1 | 1 (contact), 1 (rock) | Walks in cardinal directions, periodically shoots rocks; rocks blockable by shield |
| Octorok (Blue) | 2 / 1 / 1 | 1 (contact), 1 (rock) | Same as Red but faster and more aggressive |
| Moblin (Red) | 2 / 1 / 1 | 1 (contact), 1 (spear) | Patrols in straight lines; throws spears; spears blockable by shield |
| Moblin (Blue) | 3 / 2 / 1 | 2 (contact), 1 (spear) | Stronger, faster variant |
| Tektite (Red) | 1 / 1 / 1 | 1 (contact) | Jumps erratically in hopping arcs; no projectile |
| Tektite (Blue) | 1 / 1 / 1 | 1 (contact) | Same HP but jumps faster and more unpredictably |
| Lynel (Red) | 4 / 2 / 1 | 2 (contact), 2 (sword beam) | Centaur warrior; walks and fires sword beams; beams blockable by Magical Shield |
| Lynel (Blue) | 6 / 3 / 2 | 4 (contact), 2 (sword beam) | Strongest overworld enemy |
| Leever (Red) | 2 / 1 / 1 | 1 (contact) | Burrows underground, emerges to attack, then re-burrows; found in desert |
| Leever (Blue) | 4 / 2 / 1 | 2 (contact) | Faster, tougher variant |
| Peahat | 2 / 1 / 1 | 2 (contact) | Flying propeller creature; invulnerable while spinning/moving; vulnerable only when stopped |
| Zora | 2 / 1 / 1 | 2 (contact), 2 (fireball) | Emerges from water tiles, fires magic fireball at Link, then submerges; fireball not blockable by shield |
| Armos | 3 / 2 / 1 | 2 (contact) | Stone statue; dormant until Link touches it; then chases Link aggressively |
| Ghini | 9 / 5 / 3 | 2 (contact) | Ghost in graveyard; one "real" Ghini per screen plus phantom copies spawned by touching tombstones; only killing the real one removes all phantoms |
| Rock | Invincible | 2 (contact) | Boulders that fall from mountain edges; cannot be destroyed |

### Dungeon Enemies

| Enemy | HP (Wooden / White / Magical Sword hits) | Damage to Link (half-hearts) | Behavior |
|-------|------------------------------------------|------------------------------|----------|
| Gel | 1 / 1 / 1 | 1 (contact) | Tiny slime; moves slowly in random directions; very weak |
| Zol | 1 / 1 / 1 | 2 (contact) | Larger slime; splits into 2 Gels when hit by weak attacks; killed outright by strong weapons |
| Keese (Blue) | 1 / 1 / 1 | 1 (contact) | Bat; flies erratically in sweeping patterns; easy to kill |
| Keese (Red) | 1 / 1 / 1 | 1 (contact) | Faster Keese variant |
| Stalfos | 2 / 1 / 1 | 1 (contact) | Skeleton; walks randomly, occasionally thrusts sword; basic dungeon fodder |
| Rope | 1 / 1 / 1 | 1 (contact) | Snake; moves slowly until it aligns with Link horizontally or vertically, then charges rapidly |
| Goriya (Red) | 3 / 2 / 1 | 1 (contact), 1 (boomerang) | Walks in patterns; throws boomerang that returns; boomerang blockable by shield |
| Goriya (Blue) | 5 / 3 / 2 | 2 (contact), 1 (boomerang) | Stronger, faster boomerang thrower |
| Wallmaster | 2 / 1 / 1 | 2 (contact/grab) | Giant hand that emerges from walls; if it grabs Link, he is sent back to the dungeon entrance |
| Darknut (Red) | 4 / 2 / 1 | 1 (contact) | Armored knight; can only be damaged from the side or behind (front is shielded); moves in straight lines, turns at walls |
| Darknut (Blue) | 8 / 4 / 2 | 2 (contact) | Same behavior as Red but much higher HP |
| Gibdo | 7 / 4 / 2 | 2 (contact) | Mummy; walks slowly; high HP; no projectiles |
| Pols Voice | 10 / 5 / 3 | 2 (contact) | Bouncing rabbit-like creature; very high HP to swords; killed instantly by 1 Arrow |
| Vire | 1 / 1 / 1 | 1 (contact) | Winged demon; flies erratically; splits into 2 Keese when killed |
| Like Like | 9 / 5 / 3 | 1 (contact) | Tube-shaped creature; if it engulfs Link, it eats his Magical Shield; defeat quickly to prevent shield loss |
| Moldorm | 2 / 1 / 1 per segment | 1 (contact) | Segmented worm; moves in winding patterns; each segment has independent HP |
| Bubble (normal) | Invincible | 0 (disables sword temporarily) | Bouncing flame; contact disables Link's sword for several seconds; cannot be killed |
| Bubble (Red) | Invincible | 0 (disables sword permanently) | Red flame; sword disabled until touching a Blue Bubble |
| Bubble (Blue) | Invincible | 0 (re-enables sword) | Blue flame; cures Red Bubble curse |
| Floor Trap (Blade Trap) | Invincible | 2 (contact) | Spike block; rushes toward Link when he aligns with it along a row or column; returns to origin after reaching the opposite wall |
| Wizzrobe (Red) | 4 / 2 / 1 | 2 (beam) | Appears briefly, fires a magic beam, then teleports to new location; beam blockable only by Magical Shield |
| Wizzrobe (Blue) | 10 / 5 / 3 | 2 (beam) | Phases through walls; moves while firing beams continuously; extremely dangerous |
| Lanmola (Red) | 2 / 1 / 1 per segment | 2 (contact) | Centipede; moves in winding paths; each body segment can be attacked |
| Lanmola (Blue) | 2 / 1 / 1 per segment | 4 (contact) | Faster, more damaging centipede |
| Patra (central eye) | 11 / 6 / 3 | 4 (contact) | Mini-boss; central eye orbited by smaller eyes; must destroy all orbiting eyes before the center becomes vulnerable |
| Patra (orbiting eye) | 6 / 3 / 2 | 2 (contact) | Small eyes orbit in circular or elliptical patterns |

### Hungry Goriya (Special)

A unique Goriya blocks certain dungeon passages and will not move until Link uses the Food/Bait item in its presence. It appears in Dungeon 7 and is not an enemy that can be fought.

---

## 9. Boss Encounters

### Boss Damage & HP Summary

All HP values are in Wooden Sword hits. Bosses take proportionally fewer hits with stronger weapons.

| Boss | HP (Wooden Sword Hits) | Damage to Link (half-hearts) | Appears In | Weakness/Strategy |
|------|----------------------|------------------------------|------------|-------------------|
| Aquamentus | 6 | 2 (contact), 2 (fireball x3) | Dungeon 1, Dungeon 7 | Sword to the head; 3 White Sword hits or 2 bombs |
| Dodongo | Special (2 bombs) | 2 (contact) | Dungeon 2 | Feed 2 bombs (place in its path; it swallows them); immune to all other weapons |
| Manhandla | 4 per arm (4 arms) | 2 (contact), 2 (fireball) | Dungeon 3 | Destroy each of 4 mouths; speeds up with each mouth lost; 1 bomb destroys all mouths simultaneously |
| Gleeok (2 heads) | 10 per head | 2 (contact), 2 (fireball) | Dungeon 4 | Attack heads with sword; severed heads float and fire projectiles independently |
| Digdogger | Invulnerable (full size) | 2 (contact) | Dungeon 5 | Play Recorder to shrink; then attack miniature form with sword (4 hits with Wooden Sword) |
| Gohma (Red) | 1 Arrow | 2 (contact), 2 (fireball) | Dungeon 6 | Shoot Arrow at eye when it is open; 1 hit kill for Red; eye opens and closes periodically |
| Aquamentus | 6 | 2 (contact), 2 (fireball x3) | Dungeon 7 (return) | Same as Dungeon 1 |
| Gleeok (4 heads) | 10 per head | 2 (contact), 2 (fireball) | Dungeon 8 | Same strategy as Dungeon 4, but 4 heads to sever; severed heads all remain as hazards |
| Ganon | 8 (sword hits to stun) + 1 Silver Arrow | 4 (contact), 4 (fireball) | Dungeon 9 | Invisible; slash sword randomly to hit; after enough hits Ganon turns brown/visible; shoot Silver Arrow for the kill |

### Detailed Boss Behaviors

#### Aquamentus (Dungeons 1, 7)
- Green dragon occupying the right side of the boss room.
- Moves up and down slowly along the right wall.
- Periodically fires 3 fireballs in a spread pattern (one straight, one angled up, one angled down).
- Fireballs can be blocked by the Magical Shield.
- Vulnerable to: Sword (any), Bombs, Arrows, Magical Rod.
- 6 Wooden Sword hits / 3 White Sword hits / 2 Magical Sword hits / 2 Bombs to kill.

#### Dodongo (Dungeon 2)
- Triceratops-like creature that marches back and forth.
- Moves in the direction it faces; turns periodically.
- Immune to all weapons except Bombs.
- Strategy: Place a bomb in Dodongo's path. Dodongo walks into the bomb and swallows it, taking internal damage.
- 2 swallowed bombs kills it.
- Smoke (from bombs) is the cryptic hint: "Dodongo dislikes smoke."

#### Manhandla (Dungeon 3)
- Large, plant-like creature with 4 snapping mouths (one on each cardinal side).
- Moves around the room in bouncing patterns.
- Each mouth fires fireballs periodically.
- Destroying a mouth removes that attack vector but increases Manhandla's movement speed.
- Each mouth takes 4 Wooden Sword hits.
- A single bomb placed adjacent will destroy all 4 mouths instantly.
- Cannot be stunned by Boomerang.

#### Gleeok (Dungeons 4, 6, 8)
- Multi-headed dragon.
- Dungeon 4: 2 heads. Dungeon 6: 3 heads (mini-boss). Dungeon 8: 4 heads.
- Each head fires individual fireballs (max 1 fireball on screen at a time per head).
- When a head is severed (10 Wooden Sword hits per head), it detaches and floats around the room as a disembodied head, continuing to fire projectiles.
- Severed heads are invincible.
- Only Sword and Magical Rod can damage Gleeok's heads.
- Gleeok dies only when all heads are severed.

#### Digdogger (Dungeon 5)
- Large spiky sea-urchin creature.
- Invulnerable in its large form; bounces around the room.
- Play the Recorder to shrink it.
- In some encounters, it splits into 3 mini-Digdoggers.
- Mini-Digdoggers bounce around and can be attacked with any weapon.
- 4 Wooden Sword hits per mini-Digdogger.

#### Gohma (Dungeon 6; Blue variant in Second Quest)
- Giant crab creature with a single large eye.
- Moves side to side along one axis.
- Fires fireballs periodically.
- The eye opens and closes at intervals.
- Only vulnerable to Arrows shot into its open eye.
- Red Gohma: 1 Arrow kill. Blue Gohma (Second Quest): 3 Arrow kills.

#### Ganon (Dungeon 9)
- The Demon King; final boss.
- **Invisible** for the entire fight.
- Moves in a figure-8 pattern, shifting 4 tiles at a time before turning 90 degrees toward Link.
- Fires fireballs at Link from invisible position.
- Strategy: Swing the sword continuously; when Link's sword hits Ganon's invisible body, Ganon briefly flashes visible and turns red.
- After enough sword strikes (8 with Wooden Sword / 4 with White Sword / 2 with Magical Sword), Ganon becomes fully visible and turns brown.
- While brown, Ganon is stunned/vulnerable. Link must immediately fire the **Silver Arrow** to kill him.
- If Link waits too long, Ganon turns invisible again and the cycle repeats.
- Without the Silver Arrow, Ganon cannot be killed — he is the only enemy in the game that absolutely requires a specific weapon to finish.
- Upon death, Ganon drops the Triforce of Power and opens the way to the final room where Princess Zelda awaits.

---

## 10. Economy System

### Rupee Currency

| Property | Value |
|----------|-------|
| Currency unit | Rupees |
| Maximum capacity | 255 (8-bit unsigned integer limit) |
| Orange/flashing Rupee value | 1 |
| Blue Rupee value | 5 |
| Starting Rupees | 0 |

### Rupee Sources

| Source | Amount |
|--------|--------|
| Orange Rupee drop (enemies) | 1 |
| Blue Rupee drop (enemies) | 5 |
| Hidden cave rewards | 10, 30, or 100 |
| Money Making Game (gambling) | -40, -10, +20, or +50 per selection |
| Defeating certain enemies | Variable (most enemies have a drop table) |

### Enemy Drop Tables

When an enemy is killed, it may drop an item based on a global counter and drop tables:

| Drop Group | Items in Table |
|------------|---------------|
| Group A | Rupee, Heart, Rupee, Fairy, Rupee, Heart, Heart, Rupee, Heart, Rupee (10 entries cycled) |
| Group B | Bomb, Rupee5, Clock, Rupee, Heart, Bomb, Rupee, Rupee5, Bomb, Heart (10 entries cycled) |
| Group C | Rupee5, Bomb, Rupee, Heart, Rupee, Clock, Rupee, Rupee5, Heart, Rupee (10 entries cycled) |
| Group D | Heart, Fairy, Rupee, Heart, Fairy, Heart, Heart, Heart, Rupee, Heart (10 entries cycled) |

A kill counter increments with each enemy killed. The counter's current value indexes into the appropriate drop table for that enemy type. Not every kill drops an item; there is approximately a 40% base drop rate.

### Shop System

There are **four types of Item Shops** run by the Merchant, plus the **Potion Shop** run by the Old Woman.

#### Item Shop Type 1

| Item | Price |
|------|-------|
| Magical Shield | 160 Rupees |
| Small Key | 100 Rupees |
| Blue Candle | 60 Rupees |

#### Item Shop Type 2

| Item | Price |
|------|-------|
| Magical Shield | 130 Rupees |
| Bombs (x4) | 20 Rupees |
| Wooden Arrow | 80 Rupees |

#### Item Shop Type 3

| Item | Price |
|------|-------|
| Magical Shield | 90 Rupees |
| Food (Bait) | 100 Rupees |
| Recovery Heart | 10 Rupees |

#### Item Shop Type 4

| Item | Price |
|------|-------|
| Blue Ring | 250 Rupees |
| Small Key | 80 Rupees |
| Food (Bait) | 60 Rupees |

#### Potion Shop (Old Woman)

| Potion | Price | Requirement |
|--------|-------|-------------|
| Blue Potion (Life Potion) | 40 Rupees | Must deliver Letter to Old Woman |
| Red Potion (2nd Potion) | 68 Rupees | Must deliver Letter to Old Woman |

#### Arrow Economy

- Arrows are purchased once (80 Rupees) to gain the ability to fire them with the Bow.
- Each Arrow fired costs 1 Rupee from Link's wallet.
- If Link has 0 Rupees, Arrows cannot be fired.

### Shop Locations (First Quest)

There are 12 Item Shops scattered across the overworld. Some are hidden behind bombable walls, burnable trees, or movable Armos statues.

| Grid Position | Shop Type | Access Method |
|---------------|-----------|---------------|
| G-7 | Type 1 | Open cave |
| M-1 | Type 1 | Open cave |
| O-6 | Type 1 | Open cave |
| E-5 | Type 2 | Open cave |
| F-3 | Type 2 | Open cave |
| K-5 | Type 2 | Open cave |
| P-7 | Type 2 | Open cave |
| C-2 | Type 3 | Open cave |
| G-3 | Type 3 | Burn tree or bomb wall |
| G-5 | Type 3 | Open cave |
| N-5 | Type 3 | Burn tree |
| E-4 | Type 4 | Move Armos statue |

### Money Making Game (Gambling)

| Property | Value |
|----------|-------|
| Location | Multiple overworld caves (6 locations) |
| Mechanic | 3 Rupees on floor; Link walks over one to collect/lose |
| Prizes | +50, +20, -10, or -40 Rupees |
| Odds | Always 1 positive prize and 2 negative prizes |

The Old Man says "Let's play money making game." Link selects one of three Rupee pickups. The game is random each visit.

---

## 11. Secrets, Caves & NPCs

### Secret Types

| Secret Type | Reveal Method | Contents |
|-------------|--------------|----------|
| Cave under tree | Burn tree with Candle | Various: shop, Old Man, dungeon entrance |
| Cave in rock wall | Bomb the wall | Various: shop, Old Man, Rupees, or passage |
| Cave under Armos | Touch Armos statue | Shop or special item |
| Dock tile | Walk onto with Raft equipped | Transport to distant shore |
| Lost Woods | Navigate N-W-S-W | Progression through maze |
| Lost Hills | Navigate N-N-N-N | Progression through maze |
| Waterfall | Walk into waterfall (screen 2,2) | White Sword cave |

### Old Man Encounters

The Old Man appears throughout the overworld and in every dungeon:

#### Overworld Old Man Types

| Type | Behavior |
|------|----------|
| Sword giver | Gives Wooden Sword, White Sword, or Magical Sword (with heart requirements) |
| Hint giver | Provides a cryptic clue about the game |
| Bomb upgrade | Offers bomb capacity upgrade for 100 Rupees |
| Money Making Game host | Runs the gambling mini-game |
| Door repair charge | "Pay me for the door repair charge." Takes 20 Rupees (in bombed-door caves) |
| Heart Container / Potion choice | "Take any one you want." Offers Heart Container OR a 2nd Potion |

#### Dungeon Old Man Hints (First Quest)

| Dungeon | Hint |
|---------|------|
| Level 1 | "Eastmost peninsula is the secret." |
| Level 2 | "Dodongo dislikes smoke." |
| Level 3 | "Did you get the sword from the old man on top of the waterfall?" |
| Level 4 | "Walk into the waterfall." |
| Level 5 | "Secret power is said to be in the arrow." |
| Level 6 | "Aim at the eyes of Gohma." |
| Level 7 | "There's a secret in the tip of the nose." |
| Level 8 | "Spectacle Rock is an entrance to Death Mountain." |
| Level 9 | "Go to the next room." / "Patra has the map." |

### Bombable Walls (Overworld)

There are numerous bombable wall segments in the overworld, primarily in rocky/mountain areas. They are not visually distinguished from normal walls. Bombing them reveals cave entrances leading to:
- Shops
- Old Man caves (hints, upgrades, Rupees)
- Heart Containers
- Passage shortcuts through mountains

### Bombable Walls (Dungeons)

Many dungeon rooms have bombable walls on one or more sides. Some are hinted at by cracks in the wall texture; others are completely unmarked and require experimentation or knowledge.

### Push Block Puzzles (Dungeons)

- Certain rooms contain a single movable block (visually identical to other floor blocks).
- Pushing the block (by walking into it) in the correct direction triggers a passage to open (a stairway appears or a wall slides open).
- Blocks can only be pushed once and only in one direction.
- If pushed incorrectly, Link must leave and re-enter the room to reset it.
- Typically, the push block is located in the center of the room or adjacent to a wall.

### Fairy Ponds

Several overworld screens contain fairy ponds (small pools). Standing in the pond fully restores Link's hearts. Fairy ponds are often hidden in forest clearings.

---

## 12. Second Quest

### Activation

The Second Quest is unlocked in two ways:
1. **Complete the First Quest**: After rescuing Zelda, the game restarts with the Second Quest automatically.
2. **Name entry**: Entering "ZELDA" as the player name on the file select screen starts the Second Quest immediately.

### Key Differences

| Aspect | First Quest | Second Quest |
|--------|------------|--------------|
| Dungeon locations | Standard positions | Most dungeons relocated to new overworld screens |
| Dungeon layouts | Standard maps | Completely redesigned room arrangements |
| Dungeon shapes | Eagle, Moon, Manji, Snake, Lizard, Dragon, Demon, Lion, Skull | Dungeons 1-5 spell "Z-E-L-D-A" when reordered |
| Enemy difficulty | Normal | Enemies are stronger; more Blue variants appear; enemies from later dungeons appear earlier |
| Item placement | Standard | Many items moved to different dungeons |
| Overworld secrets | Standard locations | Secret caves and bombable walls are relocated |
| Old Man hints | Standard text | Different, often more cryptic hints |
| Boss encounters | Standard | Bosses may differ (e.g., Blue Gohma appears, requiring 3 Arrows) |
| Shop inventory | Standard prices | Some shops have different inventories and prices |

### Second Quest Dungeon Locations

| Dungeon | Location Change |
|---------|----------------|
| Level 1 | Same location as First Quest (only dungeon in the same place) |
| Level 2 | Relocated to where the Blue Ring shop was in the First Quest |
| Level 3 | Relocated to where Level 2 was in the First Quest |
| Level 4 | New location |
| Level 5 | New location |
| Level 6 | New location |
| Level 7 | New location |
| Level 8 | New location |
| Level 9 | New location |

### Second Quest Enemy Changes

- Many overworld enemies are replaced with stronger variants (e.g., Blue Lynels instead of Red).
- Dungeon enemies are generally tougher, with Blue Darknuts and Blue Wizzrobes appearing much earlier.
- Pols Voices become more common in early dungeons.
- The amount of damage enemies deal is generally higher.

---

## 13. UI Layout

### HUD (Heads-Up Display)

The HUD occupies the top 56 pixels of the 256 x 240 screen and is always visible during gameplay.

```
+----------------------------------------------------------------------+
|  MINIMAP AREA        |  ITEM/EQUIP AREA    |  STATS AREA            |
|                      |                     |                        |
|  [Dungeon Map Grid]  |  -LIFE-             |  [B item]  [A item]    |
|  or                  |  ♥♥♥♥♥♥♥♥           |                        |
|  [Overworld dot]     |  ♥♥♥♥♥♥♥♥           |  -USE B    USE A-      |
|                      |                     |                        |
|  x## (Rupees)        |                     |                        |
|  x## (Keys)          |                     |                        |
|  x## (Bombs)         |                     |                        |
+----------------------------------------------------------------------+
```

### HUD Elements (Left Section)

| Element | Position | Description |
|---------|----------|-------------|
| Minimap | Top-left | Shows dungeon room grid (when in dungeon) or overworld position dot (when in overworld) |
| Rupee counter | Below minimap | "x" followed by current Rupee count (0-255) |
| Key counter | Below Rupees | "x" followed by current Small Key count |
| Bomb counter | Below Keys | "x" followed by current Bomb count |

### HUD Elements (Center Section)

| Element | Position | Description |
|---------|----------|-------------|
| "-LIFE-" label | Top-center | Text label |
| Heart meter | Below label | Up to 16 hearts displayed in 2 rows of 8; filled hearts (red), half-hearts (half-filled), empty hearts (outlined) |

### HUD Elements (Right Section)

| Element | Position | Description |
|---------|----------|-------------|
| B-button item icon | Right area | Shows currently equipped secondary item (Boomerang, Bombs, etc.) |
| A-button indicator | Right area | Shows "SWORD" or the sword icon for the A button |
| "USE B BUTTON" | Below B icon | Label indicating the B-button mapping |
| "USE A BUTTON" | Below A icon | Label indicating the A-button mapping |

**Note on button mapping**: In the original game, the B button swings the sword and the A button uses the equipped secondary item. The HUD labels these accordingly.

### Inventory / Subscreen (Start Menu)

Pressing Start opens the subscreen overlay:

```
+----------------------------------------------------------------------+
|                    INVENTORY SUBSCREEN                                |
|                                                                      |
|  ITEM GRID:                              TRIFORCE DISPLAY:           |
|  [Boomerang] [Bombs] [Arrow] [Candle]   [Fragment 1] [Fragment 2]   |
|  [Recorder]  [Food]  [Letter] [Rod]     [Fragment 3] [Fragment 4]   |
|                                          [Fragment 5] [Fragment 6]   |
|  RING: [Blue Ring / Red Ring / None]     [Fragment 7] [Fragment 8]   |
|  MAP: [Yes/No]  COMPASS: [Yes/No]                                   |
|  SELECTION CURSOR: [highlight box]                                   |
|                                                                      |
|  Use D-pad to move cursor over items.                                |
|  Press A/Start to select item for B-button.                          |
+----------------------------------------------------------------------+
```

| Subscreen Element | Description |
|-------------------|-------------|
| Item grid | 2 rows x 4 columns showing all acquired secondary items |
| Selection cursor | D-pad moves a highlight box; selecting an item equips it to the A button |
| Triforce fragments | 8 triangular pieces displayed; filled in with gold as collected |
| Ring indicator | Shows which ring is equipped |
| Map/Compass indicator | Shows if the current dungeon's Map and Compass have been found |

### Dungeon Minimap Details

- The minimap in the HUD shows a grid representation of the current dungeon.
- Rooms Link has visited appear as small squares.
- The current room is indicated by a blinking dot.
- If the Map item is collected, all rooms in the dungeon appear on the minimap.
- If the Compass is collected, the Triforce room location pulses/flashes.
- Without the Map, only visited rooms appear.

---

## 14. Save System & Game Flow

### Title Screen

| Element | Description |
|---------|-------------|
| Title animation | Waterfall scene with game logo and "THE LEGEND OF ZELDA" text |
| Demo mode | After a few seconds, a demo plays showing Link exploring |
| Start button | Pressing Start proceeds to file select |

### File Select Screen

| Property | Value |
|----------|-------|
| Save slots | 3 |
| Name entry | Up to 8 characters per file |
| Display per slot | Name, heart count, death count, quest number (1st or 2nd) |
| "REGISTER" option | Creates a new save file |
| "ELIMINATE" option | Deletes a save file |

### Save Mechanism

| Trigger | How to Save |
|---------|-------------|
| Game Over screen | Select "SAVE" after dying (continues are from starting screen or dungeon entrance) |
| Controller 2 shortcut | While paused (Start), press Up + A on controller 2 to access save screen |
| Battery backup | SRAM in cartridge retains save data when powered off (CR2032 coin cell battery) |

### Death & Continue

| Property | Value |
|----------|-------|
| On death | Screen turns red; "GAME OVER" displayed |
| Options | CONTINUE, SAVE, RETRY |
| Continue spawn (overworld) | Starting screen (column 7, row 7) |
| Continue spawn (dungeon) | Entrance of the current dungeon |
| Hearts on continue | 3 hearts (regardless of max) |
| Items/progress retained | All items, Rupees, keys, and dungeon progress preserved |

### Game Completion

After defeating Ganon and rescuing Zelda:
- A congratulations screen is displayed.
- The player's name and quest number are shown.
- The game automatically begins the Second Quest on the same save file.

---

## 15. Audio Design

### Composer

All music and sound effects were composed by **Koji Kondo**.

### NES Audio Hardware

| Property | Value |
|----------|-------|
| Sound channels | 5 total |
| Pulse channels | 2 (melody and harmony) |
| Triangle channel | 1 (bass line) |
| Noise channel | 1 (percussion and effects) |
| DPCM channel | 1 (sampled audio — not used in this game) |

### Music Tracks

| Track | Context | Duration | Notes |
|-------|---------|----------|-------|
| Title Screen | Title/file select screen | ~40 seconds loop | Gentle, mysterious melody; sets tone for adventure |
| Overworld Theme | All overworld screens | ~60 seconds loop | Iconic adventurous march; the most recognizable Zelda melody; Deep Purple cited as influence |
| Dungeon Theme (Underworld) | All dungeon rooms | ~19 seconds loop | Dark, repetitive, tension-building bass-heavy theme |
| Death Mountain (Dungeon 9 variant) | Dungeon 9 rooms | ~19 seconds loop | Variation of dungeon theme with more urgency |
| Game Over | Link's death | ~5 seconds | Short, descending minor-key phrase |
| Ending / Credits | After defeating Ganon | ~60 seconds | Triumphant arrangement of the main theme |
| Recorder Tune | Playing the Recorder item | ~3 seconds | Short melody (same as the warp whistle tune) |
| Triforce Collected | Obtaining a Triforce fragment | ~5 seconds | Ascending fanfare |
| File Select | File selection screen | Same as title | Continuation of title theme |

### Sound Effects

| Sound Effect | Trigger |
|-------------|---------|
| Sword swing | Pressing attack button (B) |
| Sword beam fire | Firing sword beam at full health |
| Sword beam hit | Sword beam striking an enemy |
| Enemy hit | Weapon connecting with enemy |
| Enemy death | Enemy HP reaches 0; "poof" explosion sound |
| Link hurt | Link takes damage |
| Link death | Link's hearts reach 0 |
| Bomb place | Placing a bomb on the ground |
| Bomb explosion | Bomb detonating |
| Arrow fire | Shooting an arrow |
| Boomerang throw | Throwing the boomerang |
| Boomerang return | Boomerang returning to Link |
| Item collect (small) | Picking up Rupees, hearts, keys |
| Item collect (major) | Obtaining a new item or Heart Container (fanfare) |
| Key unlock | Using a key on a locked door |
| Door open | Sealed door opening (enemies cleared) |
| Secret discovered | Pushing a block, bombing a wall to reveal a passage (iconic ascending chime) |
| Low health warning | Continuous beeping when Link has 1 heart or less remaining |
| Magical Shield block | Projectile deflected by shield |
| Recorder playing | Warp whistle melody |
| Fairy fountain | Gentle looping chime at fairy pond locations |
| Text display | Character-by-character text scroll sound in NPC dialogue |
| Stairs/cave entry | Descending tone when entering a stairway |
| Rupee count ticking | When spending or gaining Rupees, the counter ticks up/down |

### Audio Priority

When multiple sounds trigger simultaneously, the NES hardware prioritizes:
1. Music continues on its assigned channels.
2. Sound effects temporarily override one pulse channel.
3. The low-health beeping alarm overrides the music melody channel, creating the distinctive and annoying beeping that replaces the background music when Link is at critical health.

---

*End of specification. This document covers all major systems, mechanics, entities, and interactions needed to recreate The Legend of Zelda (NES, 1986) faithfully.*
