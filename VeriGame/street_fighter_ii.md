# 06_street_fighter_ii - Street Fighter II: The World Warrior (Faithful Arcade Recreation)

## 1. Game Overview

- **Reference**: Street Fighter II: The World Warrior, developed and published by Capcom, released March 1991 on the CPS-1 (Capcom Play System 1) arcade board. This specification targets the original World Warrior revision only (not Champion Edition, Hyper Fighting, or later updates).
- **Genre**: 2D Competitive Fighting
- **Core Fantasy**: Select one of eight martial artists from around the globe and battle through a gauntlet of opponents in one-on-one combat, mastering special moves, spacing, and timing to defeat all challengers and four boss characters to become the World Warrior champion.
- **Presentation**: 2D side-view with hand-drawn pixel art characters on scrolling, parallax-layered stage backgrounds. Fixed horizontal arena with invisible walls. Camera follows fighters horizontally.
- **Players**: 1 Player vs CPU, or 2 Players versus (challenge mode initiated by Player 2 inserting a coin during a match).
- **Target Session**: Single-player arcade run: 20-40 minutes. Versus match: 2-5 minutes.
- **Skill Curve**: Accessible button-mashing for beginners; deep mastery through precise special move execution, spacing, hit-confirm combos, and opponent reads.

---

## 2. Technical Foundation

| Parameter | Value |
|---|---|
| Hardware | Capcom CPS-1 (CP System) arcade board |
| Main CPU | Motorola 68000 @ 10 MHz |
| Sound CPU | Zilog Z80 @ 3.579545 MHz |
| Sound chips | Yamaha YM2151 (FM synthesis) + OKI MSM6295 (ADPCM samples) |
| Screen resolution | 384 x 224 pixels |
| Refresh rate | 59.6294 Hz (approximately 60 fps) |
| Frame duration | ~16.78 ms per frame |
| Color palette | 16 colors per sprite tile (4-bit indexed), 4096 total on-screen colors |
| Sprite tiles | 16 x 16 pixel base tiles, composited into arbitrary character sizes |
| Aspect ratio | 4:3 (displayed on horizontal CRT monitor) |
| Coordinate system | 2D integer pixel coordinates; origin at top-left of screen |
| Playfield width | ~768 pixels of scrollable stage (varies per stage); visible window is 384 pixels |
| Game speed | Fixed 1x speed (no turbo setting in World Warrior) |
| Input device | 8-way joystick + 6 attack buttons per player |

### 2.1 Button Layout

The arcade cabinet uses a standard 6-button Capcom layout per player:

```
  [LP]  [MP]  [HP]
  [LK]  [MK]  [HK]
```

| Button | Abbreviation | Description |
|---|---|---|
| Light Punch | LP | Fastest, least damage, least recovery |
| Medium Punch | MP | Moderate speed and damage |
| Heavy Punch | HP | Slowest, most damage, most recovery |
| Light Kick | LK | Fastest kick, least damage |
| Medium Kick | MK | Moderate speed kick |
| Heavy Kick | HK | Slowest kick, most damage |

### 2.2 Joystick Notation

All joystick directions use numpad notation (player facing right):

| Input | Direction | Numpad |
|---|---|---|
| UB | Up-Back | 7 |
| U | Up | 8 |
| UF | Up-Forward | 9 |
| B | Back | 4 |
| N | Neutral | 5 |
| F | Forward | 6 |
| DB | Down-Back | 1 |
| D | Down | 2 |
| DF | Down-Forward | 3 |

Standard motion shorthand:
- **QCF** = Quarter-Circle Forward: D, DF, F (236)
- **QCB** = Quarter-Circle Back: D, DB, B (214)
- **HCF** = Half-Circle Forward: B, DB, D, DF, F (41236)
- **HCB** = Half-Circle Back: F, DF, D, DB, B (63214)
- **DP** = Dragon Punch motion: F, D, DF (623)
- **360** = Full circle rotation in any direction
- **Charge [X]~[Y]** = Hold direction X for minimum charge time, then press direction Y
- **[B]~F** = Charge Back then press Forward (charge ~60 frames / ~1 second minimum in WW)

---

## 3. Core Fight Mechanics

### 3.1 Movement

| Action | Input | Description |
|---|---|---|
| Walk Forward | Hold F | Character walks toward opponent. Speed varies per character. |
| Walk Backward | Hold B | Character walks away from opponent. Automatically enters standing block if attacked. |
| Crouch | Hold D, DB, or DF | Character ducks. Reduces hittable area. Enables crouching normals. |
| Jump (Neutral) | Tap U | Character jumps straight up. Fixed arc height and duration per character. |
| Jump Forward | Tap UF | Character jumps in an arc toward the opponent. |
| Jump Backward | Tap UB | Character jumps in an arc away from the opponent. |
| Dash | N/A | No dash mechanic exists in World Warrior. |

**Jump properties:**
- Jump startup (pre-jump frames): 4 frames for all characters. Character is grounded and throwable during these frames.
- Once airborne, the character follows a fixed parabolic arc. No air control or air blocking exists.
- Jump trajectories vary per character (height, distance, duration).

### 3.2 Blocking

| Block Type | Input | Description |
|---|---|---|
| Standing Block | Hold B (while grounded) | Blocks mid and high attacks. Does not block low attacks. |
| Crouching Block | Hold DB (while grounded) | Blocks low and mid attacks. Does not block overhead attacks (jumping attacks). |
| Air Block | N/A | Does not exist in World Warrior. |

**Block properties:**
- Blocking is automatic: holding back while an attack connects triggers the block.
- Normal attacks deal zero chip damage when blocked.
- Special moves deal chip damage when blocked (approximately 25% of normal damage, rounded down).
- Chip damage can KO an opponent (reduce health to zero).
- Blocking incurs block stun: the defender is frozen in a blocking animation for a move-specific number of frames.
- There is no guard meter or guard crush in World Warrior.

### 3.3 Throws

| Property | Value |
|---|---|
| Input | F or B + HP (most characters) or F or B + HK (some characters) when adjacent to opponent |
| Range | Approximately 24-32 pixels (varies per character and throw type) |
| Tech/Escape | Not possible. Throws are untechable in World Warrior. |
| Throw invulnerability | Characters in hit stun, block stun, or performing a special move cannot be thrown. |
| Throw priority | If both players attempt a throw on the same frame, Player 1 wins (P1 side advantage). |
| Air throws | Do not exist in World Warrior. |
| Command throws | Zangief (Spinning Piledriver, 360+P), E. Honda (Oicho Throw, HCB+P). These have greater range and damage than normal throws. |

### 3.4 Normal Attacks

Each character has up to 30 normal attacks across three positions:

| Position | Attacks Available |
|---|---|
| Standing (far) | LP, MP, HP, LK, MK, HK |
| Standing (close) | LP, MP, HP, LK, MK, HK (different animations when adjacent to opponent) |
| Crouching | LP, MP, HP, LK, MK, HK |
| Jumping (neutral) | LP, MP, HP, LK, MK, HK |
| Jumping (diagonal) | LP, MP, HP, LK, MK, HK |

**Close vs. Far normals**: When the attacker is within a character-specific proximity threshold (typically ~48 pixels), standing normals use the "close" animation. Outside that range, the "far" animation plays. The game checks distance at the moment the button is pressed.

### 3.5 Attack Priority and Trading

- Attacks do not have a universal priority value. Outcomes are determined by hitbox vs. hurtbox overlap.
- If both characters' attacking hitboxes overlap the other's hurtbox on the same frame, a "trade" occurs: both take damage and enter hit stun simultaneously.
- Projectiles have their own hitbox. Two projectiles meeting cancel each other out (both disappear) if they are the same strength; a stronger projectile will persist with reduced hits if applicable. In WW, single-hit projectiles always mutually cancel.
- Special moves extend hurtboxes along with hitboxes (e.g., Ryu's Hadouken leaves his hands vulnerable during startup).

### 3.6 Knockdowns

| Knockdown Type | Description |
|---|---|
| Soft knockdown | Opponent falls, wakes up quickly. Caused by most sweeps (crouching HK). |
| Hard knockdown | Opponent is launched into the air, hits the ground, must recover. Caused by throws, most special moves, jumping HK on grounded opponents. |
| Recovery | No quick-rise or tech roll exists in World Warrior. Wakeup timing is fixed per knockdown type. |

### 3.7 Reversal System

- **Reversals do NOT exist in World Warrior.** Unlike later SF2 revisions, there is no 1-frame reversal window on wakeup.
- On wakeup, the character must go through their full standing recovery before any action can be performed.
- This makes meaty attacks (attacks timed to hit on the first wakeup frame) and safe jumps extremely powerful.
- The only defensive option on wakeup is blocking.

### 3.8 Negative Edge

- All special moves can be executed using **Negative Edge**: the button release counts as a second button input.
- Example: Hold HP, perform QCF motion, release HP = Hadouken fires on the button release.
- This applies to all special move inputs in the game.

---

## 4. Input System

### 4.1 Input Buffer

| Parameter | Value |
|---|---|
| Input buffer window | ~8 frames for special move inputs |
| Charge time minimum | ~60 frames (~1 second) for charge moves |
| Charge partitioning | Does not exist in World Warrior |
| Pianoing | Rapidly alternating button presses for rapid-fire moves (e.g., Chun-Li Lightning Legs) |

### 4.2 Input Priority

When multiple valid inputs are detected on the same frame:
1. **Special moves** take priority over normal attacks.
2. **Throws** take priority over normal attacks when in range (F/B + HP near opponent = throw, not standing HP).
3. **Heavy attacks** take priority over medium, medium over light (when simultaneous buttons are pressed).
4. If a special move motion is detected alongside a normal attack input, the special move is performed.

### 4.3 CPS-1 Chains (Unique to World Warrior)

- Characters with rapid-fire light attacks (LP or LK that can be chained into themselves) can cancel a light attack into a different normal attack of the same strength class. This is known as a **CPS-1 chain**.
- Example: Crouching LK can be canceled into Standing LP.
- Chainable light normals can also be jump-canceled on hit or block.

### 4.4 Special Move Input Windows

| Motion | Input Tolerance |
|---|---|
| QCF / QCB | Must complete D -> DF -> F (or reverse) within ~15 frames. Shortcut via D -> F accepted. |
| DP (F, D, DF) | Must complete F -> D -> DF within ~15 frames. Common shortcut: DF -> D -> DF accepted. |
| HCF / HCB | Must complete B -> DB -> D -> DF -> F within ~20 frames. |
| 360 | Any full rotation through all 4 cardinal directions within ~20 frames. Can start from any direction. Does not need to be precise; 270 degrees is sufficient. |
| Charge | Direction must be held for minimum charge frames. Diagonal counts (DB counts as both B and D charge). |

### 4.5 Random Special Moves (World Warrior Bug)

- There is a 1-in-256 chance per frame that a random button press will execute a special move regardless of joystick input.
- There is a 1-in-256 chance per frame that an incoming attack will be automatically blocked.

---

## 5. Health and Damage System

### 5.1 Health (Vitality)

| Parameter | Value |
|---|---|
| Maximum health | 144 points (corresponds to 144 pixels on the health bar) |
| Starting health | 144 (full) at the start of each round |
| Health equality | All characters have equal maximum health in World Warrior |
| Health display | Horizontal bar at top of screen. Yellow = remaining health. Red = lost health. |
| KO threshold | 0 health points. Character is knocked out when health reaches 0. |

### 5.2 Damage Calculation

Each attack has a base damage value. The final damage dealt follows this formula:

```
Final Damage = Base Damage + Random Modifier
```

- **Random Modifier**: A small random value (positive or negative) is added per hit. This creates slight variance in damage between identical hits. Range is typically +/- 1-3 points.
- **Chip Damage** (blocked special moves): Approximately 25% of the move's base damage (rounded down).
- **Weak Point Damage**: In World Warrior, certain hurtbox states cause double damage. Ryu has a known weak point during his dizzy lean-forward animation where he takes 2x damage.
- **Counter hits**: Do not exist as a formal system in World Warrior. However, hitting an opponent out of a move's startup or recovery may interact with weak point hurtboxes.
- **Aerial hit damage reduction**: Moves hitting airborne opponents deal slightly less damage and stun than the same move hitting a grounded opponent (approximately 85-90% of grounded damage).

### 5.3 Normal Attack Damage Reference (Ryu/Ken)

| Move | Base Damage |
|---|---|
| Standing LP (far) | 4 |
| Standing MP (far) | 12 |
| Standing HP (far) | 16 |
| Standing LK (far) | 6 |
| Standing MK (far) | 12 |
| Standing HK (far) | 16 |
| Crouching LP | 4 |
| Crouching MP | 10 |
| Crouching HP | 16 |
| Crouching LK | 4 |
| Crouching MK | 10 |
| Crouching HK (sweep) | 16 |
| Jumping HP | 18 |
| Jumping HK | 18 |

### 5.4 Special Move Damage Reference (Ryu)

| Move | Base Damage |
|---|---|
| Hadouken (LP) | 12 |
| Hadouken (MP) | 14 |
| Hadouken (HP) | 16 |
| Shoryuken (LP) | 16 |
| Shoryuken (MP) | 18 |
| Shoryuken (HP) | 20 |
| Tatsumaki Senpukyaku (LK) | 14 |
| Tatsumaki Senpukyaku (MK) | 16 |
| Tatsumaki Senpukyaku (HK) | 18 |
| Throw (HP) | 20 |

---

## 6. Dizzy / Stun System

### 6.1 Stun Accumulation

| Parameter | Value |
|---|---|
| Stun threshold | 32 stun points |
| Stun recovery | Stun points decay over time when not being hit. Each move adds to a stun timeout counter that determines how long before decay begins. |
| Stun from normals | LP: 1-2, MP: 3-4, HP: 5-7, LK: 1-2, MK: 3-4, HK: 5-7 (varies per character) |
| Stun from specials | Varies widely. Example: Blanka Rolling Attack = 16 stun (grounded), 14 stun (airborne). |
| Stun timeout per hit | Each hit adds a timeout value to the stun decay counter. Higher values keep stun damage "alive" longer. |
| Aerial reduction | Moves hitting airborne opponents add less stun and less stun timeout. Example: Blanka Rolling Attack adds 120 timeout grounded, 80 timeout airborne. |

### 6.2 Dizzy State

When stun reaches the 32-point threshold:
1. The character enters a **dizzy state** and cannot act for a random duration.
2. **Visual indicator**: Stars or birds (ducks) circle above the dizzied character's head.
   - **Stars**: Easier to escape (shorter dizzy duration, approximately 60-90 frames).
   - **Birds/Ducks**: Harder to escape (longer dizzy duration, approximately 90-150 frames).
   - The type is randomly selected upon becoming dizzied.
3. **Mashing to escape**: Rapidly pressing buttons and moving the joystick reduces dizzy duration.
4. **Re-dizzy**: After a character is dizzied, only the first hit while dizzied does NOT contribute to the stun counter. The second hit onward does contribute, making immediate re-dizzy possible with powerful combos.
5. **Stun reset**: After recovering from dizzy (or being hit during dizzy), the stun counter resets to 0.

---

## 7. Combo System

### 7.1 Hit Stun

- When a grounded attack connects, the opponent enters **hit stun** for a move-specific number of frames.
- During hit stun, the opponent cannot block, attack, or move.
- If a second attack connects before hit stun ends, it forms a **combo**.
- Hit stun duration for the second hit onward in a combo is reduced by 1 frame (combo hit stun reduction).

### 7.2 Cancels

| Cancel Type | Description |
|---|---|
| Normal -> Special Cancel | Certain normal attacks can be canceled into special moves on hit or block. The special move begins during the normal's animation, skipping remaining recovery frames. |
| CPS-1 Chain | Light rapid-fire normals can chain into other normals (WW exclusive mechanic). |
| Jump Cancel | Chainable light normals can be canceled into a jump (WW exclusive). |

**Cancelable normals** (general rules; varies per character):
- Standing/crouching close LP and LK are generally cancelable.
- Standing/crouching close MP and MK are often cancelable.
- Standing/crouching close HP and HK are sometimes cancelable.
- Far normals are generally NOT cancelable.
- Crouching normals: varies per character. Crouching MK is often cancelable (e.g., Ryu cr.MK -> Hadouken is the classic combo).

### 7.3 Common Combo Types

| Combo | Example |
|---|---|
| Jump-in combo | Jumping HK -> Close standing HP -> Hadouken (Ryu, 3 hits) |
| Ground combo | Close MP xx Special Move (2 hits) |
| Tick throw | Crouching LK (blocked) -> Walk forward -> Throw |
| Dizzy combo | After dizzying opponent: jumping HP -> close HP xx Shoryuken |
| CPS-1 chain combo | Crouching LK -> Standing LP (chained via CPS-1 chain) |

### 7.4 Damage Scaling

- World Warrior has **no damage scaling** for combos. Each hit in a combo deals its full damage value regardless of combo length.
- This makes combos extremely rewarding and high-damage in World Warrior compared to later revisions.

---

## 8. Round and Match Structure

### 8.1 Round Rules

| Parameter | Default Value | DIP Switch Range |
|---|---|---|
| Rounds to win | 2 | 1, 2, 3, or 4 |
| Maximum rounds per match | Up to 10 (if draws occur) | N/A |
| Round timer (display) | 99 | 30, 60, or 99 (or Infinite) |
| Round timer speed | Each displayed "second" is approximately 1 real second | Adjusted by game speed |
| Round start | "Round X... FIGHT!" announcement and text overlay | N/A |
| Round end | KO, Time Over, Double KO, or Draw Game | N/A |

### 8.2 Round Flow

1. **Pre-round**: Characters walk on-screen. "Round X" text displays. "FIGHT!" appears.
2. **Active round**: Timer counts down. Players fight. Round ends when:
   - One character's health reaches 0 (KO).
   - Both characters' health reaches 0 simultaneously (Double KO - neither wins the round).
   - Timer reaches 0 (Time Over - character with more remaining health wins).
   - Timer reaches 0 with equal health (Draw Game - neither wins the round).
3. **Post-round**: Winner performs a victory pose. "You Win" or "You Lose" text.
4. **Match end**: If a player has won the required number of rounds, the match is over.
5. **Draw handling**: If 10 rounds pass with no winner (due to Double KOs and Draw Games), both players lose. In single-player mode, this results in a continue screen.

### 8.3 Time Over

- When the timer reaches 0, the round immediately ends.
- The character with more remaining health wins the round.
- The "TIME" text flashes on screen.
- If both characters have exactly equal health remaining, it is a Draw Game.

### 8.4 Continue System

| Parameter | Value |
|---|---|
| Continue timer | 10-second countdown |
| Continue cost | 1 credit (coin) |
| Continue behavior | Player may choose the same or different character. Restarts the current match (not the entire run). |
| Game Over | If the countdown expires without a continue, the game returns to the title/attract screen. |

---

## 9. Character Profiles and Complete Move Lists

### 9.1 Ryu

| Attribute | Value |
|---|---|
| Full Name | Ryu |
| Nationality | Japanese |
| Fighting Style | Ansatsuken (Shotokan-style Karate) |
| Height | 5'10" (175 cm) |
| Weight | 150 lbs (68 kg) |
| Blood Type | O |
| Birthday | July 21, 1964 |
| Stage | Suzaku Castle, Japan |
| Win Quote | "You must defeat Sheng Long to stand a chance." |

**Special Moves:**

| Move Name | Input | Description |
|---|---|---|
| Hadouken | QCF + P | Fires a blue fireball horizontally. Speed varies by punch button: LP = slow, MP = medium, HP = fast. Recovery is fixed regardless of button strength. |
| Shoryuken | DP + P (F, D, DF + P) | Rising uppercut. LP = shortest rise, least damage. HP = highest rise, most damage. **Does not knock down grounded opponents in WW** (unique WW trait). Upper body invincibility on startup frames. |
| Tatsumaki Senpukyaku | QCB + K | Spinning hurricane kick traveling forward. LK = short distance, HK = far distance. Passes through projectiles. Knocks down on hit. |

**Normal Move Highlights:**

| Move | Properties |
|---|---|
| Close st.HP | Cancelable into specials. Strong combo starter. |
| Close st.MP | Cancelable. Good for hit confirms. |
| Cr.MK | Cancelable into Hadouken. The classic Ryu ground poke combo. |
| Cr.HK | Sweep. Knocks down. Not cancelable. Good range. |
| Far st.HK | Long-range roundhouse. Good poke. |
| j.HK | Diagonal jump roundhouse. Primary jump-in combo starter. |
| j.HP | Diagonal jump fierce. Strong jump-in. |

**Throw:** F or B + HP (close range). Ryu grabs and tosses the opponent over his shoulder.

**Key Properties:**
- Ryu has a weak point during his dizzy animation (leaning forward frame) where he takes 2x damage.
- Ryu's Shoryuken does NOT knock down grounded opponents in WW, making it weaker than Ken's for anti-air.
- Hadouken recovery is identical for all strengths.

---

### 9.2 Ken

| Attribute | Value |
|---|---|
| Full Name | Ken Masters |
| Nationality | American |
| Fighting Style | Ansatsuken (Shotokan-style Karate) |
| Height | 5'11" (176 cm) |
| Weight | 169 lbs (76 kg) |
| Blood Type | B |
| Birthday | February 14, 1965 |
| Stage | Harbor, USA (San Francisco Bay) |
| Win Quote | "Attack me if you dare, I will crush you." |

**Special Moves:**

| Move Name | Input | Description |
|---|---|---|
| Hadouken | QCF + P | Identical animation and properties to Ryu's Hadouken. Blue fireball. |
| Shoryuken | DP + P (F, D, DF + P) | Rising uppercut. **Knocks down grounded opponents** (unlike Ryu in WW). Stronger than Ryu's version. |
| Tatsumaki Senpukyaku | QCB + K | Spinning hurricane kick. Identical function to Ryu's. |

**Throw:** F or B + HP (close range). Ken uses a knee bash throw.

**Key Differences from Ryu:**
- Ken's Shoryuken knocks down grounded opponents and deals more effective damage, making Ken strictly stronger than Ryu in WW.
- Visual differences: Ken wears a red gi; Ryu wears a white gi.
- Same normal move properties and frame data as Ryu in WW.
- Ken is generally considered the stronger character in WW due to the Shoryuken knockdown difference.

---

### 9.3 Chun-Li

| Attribute | Value |
|---|---|
| Full Name | Chun-Li (Spring Beauty) |
| Nationality | Chinese |
| Fighting Style | Chinese martial arts (Tai Chi Quan-based) |
| Height | 5'8" (169 cm) |
| Weight | Secret |
| Blood Type | A |
| Birthday | March 1, 1968 |
| Stage | Bustling street market, China |
| Win Quote | "I'm the strongest woman in the world." |

**Special Moves:**

| Move Name | Input | Description |
|---|---|---|
| Hyakuretsukyaku (Lightning Legs) | Rapidly press K (any kick button ~5 times within ~20 frames) | Chun-Li performs a rapid flurry of kicks. Hits multiple times. Button used affects range slightly. |
| Spinning Bird Kick | Charge [D]~U + K | Chun-Li flips upside-down and spins with legs extended, traveling forward. LK = short distance, HK = long distance. |
| **No fireball in WW** | N/A | Chun-Li does NOT have the Kikoken in World Warrior. It was added in Hyper Fighting. |

**Unique Normal:**

| Move | Properties |
|---|---|
| Yousoukyaku (Head Stomp) | DF + MK (in the air, near opponent's head). Chun-Li bounces off the opponent's head. Can cross up. |
| Cr.HK | Sweep with excellent range. |

**Throw:** F or B + HP (close range). Chun-Li tosses the opponent.

**Key Properties:**
- Only female character in World Warrior.
- Lacks a projectile, making her disadvantaged in fireball wars.
- Lightning Legs provides strong close-range pressure.
- Small hurtbox while crouching.

---

### 9.4 Guile

| Attribute | Value |
|---|---|
| Full Name | Guile |
| Nationality | American |
| Fighting Style | US Special Forces martial arts |
| Height | 6'1" (182 cm) |
| Weight | 191 lbs (86 kg) |
| Blood Type | O |
| Birthday | December 23, 1960 |
| Stage | US Air Force Base, USA |
| Win Quote | "Go home and be a family man." |

**Special Moves:**

| Move Name | Input | Description |
|---|---|---|
| Sonic Boom | Charge [B]~F + P | Guile throws a crescent-shaped projectile. LP = slow, MP = medium, HP = fast. Excellent recovery, allowing Guile to walk behind it. |
| Flash Kick (Somersault Kick) | Charge [D]~U + K | Guile performs a rising backflip kick. Powerful anti-air. LK = lowest arc, HK = highest arc with most damage. |

**Normal Move Highlights:**

| Move | Properties |
|---|---|
| Cr.HP (Crouching Fierce) | Excellent anti-air normal. |
| Far st.HK | Strong long-range poke (the "roundhouse"). |
| Cr.MK | Cancelable. Good poke. |
| j.HP | Strong jump-in attack. |
| Back + MK (Sobat Kick) | Guile's unique forward-advancing kick. Useful for spacing. |

**Throws:**
- F or B + HP: Standard throw.
- F or B + HK: Guile's suplex throw (different throw animation and direction).

**Key Properties:**
- Pure charge character. Must hold back or down to charge before executing specials.
- Sonic Boom has one of the best recoveries of any projectile in the game, enabling strong zoning.
- Flash Kick is one of the best anti-air specials.
- World Warrior Guile has several known glitches: Magic Throw (throw at distance), Handcuffs (opponent stuck to Guile), and stored charge exploits. These are bugs, not intended mechanics.
- Widely considered the strongest character in World Warrior.

---

### 9.5 Blanka

| Attribute | Value |
|---|---|
| Full Name | Jimmy (Blanka) |
| Nationality | Brazilian |
| Fighting Style | Self-taught feral fighting / Savage Jungle Combat |
| Height | 6'5" (192 cm) |
| Weight | 218 lbs (98 kg) |
| Blood Type | B |
| Birthday | February 12, 1966 |
| Stage | Amazon River Basin, Brazil |
| Win Quote | "Seeing you in action is a joke." |

**Special Moves:**

| Move Name | Input | Description |
|---|---|---|
| Rolling Attack (Horizontal) | Charge [B]~F + P | Blanka curls into a ball and rolls forward. LP = slow/short, HP = fast/far. Knocks down on hit. |
| Vertical Rolling Attack | Charge [D]~U + K | Blanka curls into a ball and launches upward diagonally. Anti-air. LK = lowest arc, HK = highest. |
| Electric Thunder | Rapidly press P (any punch button ~5 times within ~20 frames) | Blanka surrounds himself with electricity. Hits opponents who touch him. Multiple hits. Beats throws. |

**Normal Move Highlights:**

| Move | Properties |
|---|---|
| Cr.HP (Slide) | Low-profile sliding attack. Good range. |
| Far st.HP | Slow but long-range swipe. |
| j.HP | Strong jump-in. |
| Cr.MK | Good low poke. |

**Throw:** F or B + HP (close range). Blanka bites the opponent.

**Key Properties:**
- Charge character with both horizontal and vertical mobility specials.
- Electric Thunder provides anti-throw and anti-meaty defense.
- Rolling Attack has a large hurtbox during travel, making it risky against prepared opponents.
- Strong cross-up with diagonal jump MK.

---

### 9.6 Zangief

| Attribute | Value |
|---|---|
| Full Name | Zangief |
| Nationality | Soviet Union (Russian) |
| Fighting Style | Wrestling / Sambo |
| Height | 7'0" (214 cm) |
| Weight | 256 lbs (116 kg) |
| Blood Type | A |
| Birthday | June 1, 1956 |
| Stage | Iron Foundry, USSR |
| Win Quote | "I am the Red Cyclone." |

**Special Moves:**

| Move Name | Input | Description |
|---|---|---|
| Spinning Piledriver (SPD) | 360 + P | Zangief grabs the opponent and performs a devastating piledriver. LP = least damage (~30), HP = most damage (~38). The most damaging regular move in the game. Range is greater than normal throws. |
| Double Lariat (Spinning Clothesline) | All 3 Punch buttons simultaneously (LP+MP+HP) | Zangief spins with arms outstretched. Upper body invincible to projectiles. Slow movement during spin. Hits multiple times. |
| Quick Lariat | All 3 Kick buttons simultaneously (LK+MK+HK) | Shorter version of the Double Lariat with less recovery. |

**Normal Move Highlights:**

| Move | Properties |
|---|---|
| Far st.HP | Strong poke, decent range. |
| Cr.HK (Sweep) | Long-range sweep. |
| Cr.LP | Fast jab, good for tick into SPD. |
| j.HP (Splash) | Crossup jump-in. |
| j.HK (Body Press) | Large hitbox jump-in. |

**Throws:**
- F or B + HP: Normal throw.
- F or B + HK: Different throw animation (German Suplex-style).
- SPD (360 + P): Command throw with huge damage.

**Key Properties:**
- Grappler archetype. Entire gameplan revolves around landing the SPD.
- No projectile. Must approach opponents through their projectile zoning.
- Double Lariat passes through projectiles (upper body projectile invulnerability).
- Largest character sprite in the game, making him easier to hit.
- Difficult to execute the 360 motion without accidentally jumping. Commonly performed during a jump's pre-jump frames (buffered from a crouching state) or from other action states.
- Weakest character in WW tier lists due to lack of tools to approach projectile characters.

---

### 9.7 Dhalsim

| Attribute | Value |
|---|---|
| Full Name | Dhalsim |
| Nationality | Indian |
| Fighting Style | Yoga |
| Height | 5'10" (176 cm) (stretches much taller) |
| Weight | 107 lbs (48 kg) |
| Blood Type | O |
| Birthday | November 22, 1952 |
| Stage | Temple courtyard, India (elephants in background) |
| Win Quote | "I will meditate and then destroy you." |

**Special Moves:**

| Move Name | Input | Description |
|---|---|---|
| Yoga Fire | QCF + P | Dhalsim spits a small, slow-moving fireball. LP = slowest, HP = fastest. |
| Yoga Flame | HCB + P | Dhalsim breathes a large burst of flame at close range. Short range, high damage. Knocks down. |
| **No Yoga Teleport in WW** | N/A | The Yoga Teleport was added in Hyper Fighting. It does NOT exist in World Warrior. |

**Unique Normals (Stretching Limbs):**

| Move | Properties |
|---|---|
| Far st.LP | Extended arm jab. Medium range. |
| Far st.MP | Long stretching arm punch. Very long range. |
| Far st.HP | Maximum stretch punch. Longest normal in the game. Slow but enormous reach. |
| Far st.LK | Extended leg kick. |
| Far st.MK | Long stretching leg kick. |
| Far st.HK | Maximum stretch kick. Extremely long range. |
| Cr.HP | Stretching uppercut. Anti-air. |
| Cr.HK (Slide) | Low-profile sliding kick. |

**Drill Kicks (Air specials):**

| Move | Input | Description |
|---|---|---|
| Yoga Mummy (Head Drill) | D + HP (while jumping diagonally) | Dhalsim dives downward head-first at a steep angle. |
| Yoga Spear (Foot Drill) | D + HK (while jumping diagonally) | Dhalsim dives downward feet-first at an angle. |

**Throw:** F or B + HP (close range), also B or F + MP at slightly further range for a "Yoga Noogie" (unique throw).

**Key Properties:**
- Longest normal attack range in the game due to stretching limbs.
- Stretching normals extend Dhalsim's hurtbox along with his hitbox, making him vulnerable to attacks hitting his outstretched limbs.
- Slow walk speed and jump arc.
- Yoga Fire is a slow projectile, good for space control rather than zoning wars.
- Yoga Flame is very strong but short-range; used as anti-air and combo ender at close range.
- Strong from full screen; vulnerable up close.

---

### 9.8 E. Honda

| Attribute | Value |
|---|---|
| Full Name | Edmond Honda |
| Nationality | Japanese |
| Fighting Style | Sumo Wrestling |
| Height | 6'2" (185 cm) |
| Weight | 304 lbs (137 kg) |
| Blood Type | A |
| Birthday | November 3, 1960 |
| Stage | Sentou (Public Bathhouse), Japan |
| Win Quote | "Can't you do better than that?" |

**Special Moves:**

| Move Name | Input | Description |
|---|---|---|
| Hundred Hand Slap (Hyaku Retsu Harite) | Rapidly press P (~5 times within ~20 frames) | Honda unleashes a rapid barrage of palm slaps. Multiple hits. Good chip damage. |
| Sumo Headbutt (Super Zutsuki) | Charge [B]~F + P | Honda launches himself forward head-first. LP = slow/short, HP = fast/far. Knocks down. Travels through projectiles partially. |
| Oicho Throw | HCB + P | Command throw. Honda grabs the opponent and slams them. Greater range and damage than normal throws. Cannot be teched. |

**Normal Move Highlights:**

| Move | Properties |
|---|---|
| Far st.HP | Strong slap. Good range. |
| Cr.MP | Quick mid poke. |
| Cr.HK (Sweep) | Long-range sweep. |
| j.HP | Strong jump-in. |
| j.HK | Downward kick, good jump-in. |

**Throw:** F or B + HP (close range). Honda performs a sumo throw.

**Key Properties:**
- Charge character for the Headbutt, mashing character for Hundred Hand Slap.
- Headbutt is his primary approach tool against zoners.
- Oicho Throw provides powerful close-range damage.
- Hundred Hand Slap provides good chip damage pressure.
- Large body makes him susceptible to crossups and combos.

---

### 9.9 Balrog (Boss 1)

| Attribute | Value |
|---|---|
| Full Name | Balrog (M. Bison in Japan) |
| Nationality | American |
| Fighting Style | Heavyweight Boxing |
| Height | 6'5" (198 cm) |
| Weight | 252 lbs (114 kg) |
| Blood Type | A |
| Birthday | September 4, 1968 |
| Stage | Las Vegas Casino, USA |
| Win Quote | "My fists have your blood on them." |

**Special Moves (CPU-only in WW; NOT playable):**

| Move Name | Input (CPU) | Description |
|---|---|---|
| Dash Straight | Charge [B]~F + P | Balrog dashes forward with a straight punch. Fast, long range. LP = shorter, HP = longer dash. |
| Dash Uppercut | Charge [B]~F + K | Balrog dashes forward with a rising uppercut. Launches opponent. Anti-air properties. |
| Turn Punch (TAP) | Hold all 3 punch or kick buttons, release | Balrog winds up and throws a powerful overhand punch. Damage increases with charge time. |

**Key Properties:**
- NOT playable in World Warrior (CPU-controlled boss only; becomes playable in Champion Edition).
- Boxing-only fighting style: cannot kick. All attacks are punch-based.
- Fast forward movement and powerful dash punches.
- First of the four boss characters encountered in single-player mode.
- High damage output with relatively simple but aggressive AI patterns.

---

### 9.10 Vega (Boss 2)

| Attribute | Value |
|---|---|
| Full Name | Vega (Balrog in Japan) |
| Nationality | Spanish |
| Fighting Style | Spanish Ninjutsu (Ninjutsu + Bullfighting) |
| Height | 6'0" (186 cm) |
| Weight | 208 lbs (94 kg) |
| Blood Type | O |
| Birthday | January 27, 1967 |
| Stage | Chain-link cage arena, Spain (unique enclosed stage with wall) |
| Win Quote | "Handsome fighters never lose battles." |

**Special Moves (CPU-only in WW):**

| Move Name | Input (CPU) | Description |
|---|---|---|
| Rolling Crystal Flash | Charge [B]~F + P | Vega rolls forward slashing with his claw. LP = short, HP = long range. |
| Flying Barcelona Attack | Charge [D]~U + K, then P when near opponent | Vega leaps to the wall/cage, bounces off it, then dive-attacks. Can change direction. |
| Izuna Drop | Charge [D]~U + K, then close to opponent press P near their head | Same wall-dive approach, but Vega grabs and slams the opponent (throw). |
| Backslash | PPP (3 punches simultaneously) | Vega performs a quick backflip dodge. Invulnerable during animation. |

**Key Properties:**
- NOT playable in World Warrior (CPU-controlled boss only).
- Unique stage: fights in an enclosed cage with walls. Vega can bounce off the cage walls for his Barcelona Attack.
- Vega's claw can be knocked off if he takes enough damage, reducing his attack range and damage.
- Wears a mask to protect his face; the mask can also be knocked off (cosmetic only).
- Fastest walk speed of any character in the game.
- Wall-dive attacks create unpredictable attack angles.

---

### 9.11 Sagat (Boss 3)

| Attribute | Value |
|---|---|
| Full Name | Sagat |
| Nationality | Thai |
| Fighting Style | Muay Thai |
| Height | 7'5" (226 cm) |
| Weight | 330 lbs (150 kg) |
| Blood Type | B |
| Birthday | July 2, 1955 |
| Stage | Reclining Buddha Temple, Thailand |
| Win Quote | "You are not a warrior. You are a beginner." |

**Special Moves (CPU-only in WW):**

| Move Name | Input (CPU) | Description |
|---|---|---|
| Tiger Shot (High) | QCF + P | Sagat throws a high fireball. LP = slow, HP = fast. |
| Tiger Shot (Low) | QCF + K | Sagat throws a low fireball (must be blocked crouching). LP = slow, HP = fast. |
| Tiger Uppercut | DP + P (F, D, DF + P) | Devastating rising uppercut. One of the highest-damage special moves in the game. HP version can hit multiple times. |
| Tiger Knee (Tiger Crush) | QCF, UF + K (D, DF, F, UF + K) | Sagat leaps forward with a flying knee strike. |

**Key Properties:**
- NOT playable in World Warrior (CPU-controlled boss only).
- Tallest character in the game at 7'5".
- Has both high and low Tiger Shots, creating difficult projectile patterns to navigate.
- Tiger Uppercut is extremely damaging and has strong anti-air properties.
- Visible scar across his chest from his previous battle with Ryu (lore detail).
- Third boss encountered; extremely challenging due to projectile and anti-air dominance.

---

### 9.12 M. Bison (Final Boss)

| Attribute | Value |
|---|---|
| Full Name | M. Bison (Vega in Japan) |
| Nationality | Unknown (Shadaloo Dictator) |
| Fighting Style | Psycho Power |
| Height | 5'11" (182 cm) |
| Weight | 247 lbs (112 kg) |
| Blood Type | A |
| Birthday | April 17, 1953 |
| Stage | Shadaloo Temple, Thailand (with breakable stone statues) |
| Win Quote | "Get lost, you can't compare with my powers." |

**Special Moves (CPU-only in WW):**

| Move Name | Input (CPU) | Description |
|---|---|---|
| Psycho Crusher | Charge [B]~F + P | Bison propels himself forward in a corkscrew motion wreathed in Psycho Power energy. Full-screen range. Multi-hit. His signature move. |
| Double Knee Press (Scissor Kick) | Charge [B]~F + K | Bison flies forward with both legs extended in a scissor motion. Knocks down. Good range. |
| Head Press (Head Stomp) | Charge [D]~U + K | Bison leaps high and stomps on the opponent's head. Can follow up with a Somersault Skull Diver (press P after the stomp for a diving punch). |
| Devil Reverse | Charge [D]~U + P, then P in the air | Bison leaps high, then reverses direction mid-air and descends with a Psycho Power-infused punch. |

**Key Properties:**
- NOT playable in World Warrior (CPU-controlled final boss only).
- Final boss of the game. Must be defeated to complete single-player mode.
- Psycho Crusher covers enormous horizontal distance and hits multiple times.
- Has no fireball, but extremely strong offensive pressure with Scissor Kick and Psycho Crusher.
- Head Press and Devil Reverse create aerial mixups that are difficult to anti-air.
- Breaking the stone statues on his stage causes background monks to stand up and shout.
- AI is the most aggressive and reading-heavy of all CPU opponents.

---

## 10. Frame Data Reference

Frame data is presented for key moves. All values are in frames at 59.63 Hz (~16.78 ms per frame).

### 10.1 Ryu/Ken Key Frame Data

| Move | Startup | Active | Recovery | On Hit | On Block |
|---|---|---|---|---|---|
| Standing LP (close) | 3 | 3 | 5 | +5 | +3 |
| Standing MP (close) | 4 | 4 | 8 | +3 | +1 |
| Standing HP (close) | 5 | 4 | 16 | -2 | -7 |
| Crouching LK | 3 | 3 | 7 | +4 | +2 |
| Crouching MK | 4 | 4 | 12 | +1 | -2 |
| Crouching HK (sweep) | 6 | 4 | 20 | Knockdown | -10 |
| Crouching HP | 4 | 4 | 18 | +0 | -5 |
| Jumping HP | 5 | 7 | Until landing | Variable | Variable |
| Hadouken (any) | 12 | -- | 42 | Knockdown | -6 |
| Shoryuken (LP) | 3 | 8 | 28 | Juggle | -17 |
| Shoryuken (HP) | 3 | 12 | 34 | Juggle | -22 |
| Tatsumaki (LK) | 9 | Varies | 14 | Knockdown | -8 |

### 10.2 Guile Key Frame Data

| Move | Startup | Active | Recovery | On Hit | On Block |
|---|---|---|---|---|---|
| Standing LP (close) | 3 | 3 | 5 | +5 | +3 |
| Crouching MP | 4 | 4 | 10 | +2 | -1 |
| Crouching HP | 5 | 5 | 16 | +1 | -4 |
| Far st.HK | 8 | 4 | 18 | -1 | -5 |
| Sonic Boom (LP) | 12 | -- | 34 | +2 | -2 |
| Sonic Boom (HP) | 12 | -- | 34 | +6 | +2 |
| Flash Kick (LK) | 4 | 8 | 30 | Knockdown | -18 |
| Flash Kick (HK) | 4 | 12 | 34 | Knockdown | -22 |

### 10.3 Zangief Key Frame Data

| Move | Startup | Active | Recovery | On Hit | On Block |
|---|---|---|---|---|---|
| Standing LP (close) | 3 | 4 | 5 | +5 | +3 |
| Crouching LK | 3 | 4 | 7 | +4 | +2 |
| Crouching HK (sweep) | 7 | 5 | 22 | Knockdown | -12 |
| SPD (LP) | 1 | 2 | -- | Throw | -- |
| SPD (HP) | 1 | 2 | -- | Throw | -- |
| Double Lariat | 6 | (multi-hit) | 22 | Variable | Variable |

---

## 11. Stage Descriptions

Each character has a home stage where fights take place when facing that character. In versus mode, the stage is the defending character's (Player 2 or CPU opponent's) home stage.

### 11.1 Ryu's Stage -- Suzaku Castle, Japan

- **Setting**: A traditional Japanese castle courtyard at dusk.
- **Background**: Tiled rooftop with a Japanese castle visible in the distance. Orange sky with clouds.
- **Ground**: Stone/tile floor.
- **Spectators**: Onlookers in traditional garb stand along the edges.
- **Ambient details**: Wind blows across the scene. Banners flutter.
- **Music**: "Ryu's Theme" -- upbeat martial arts-inspired melody.

### 11.2 Ken's Stage -- Harbor/Port, USA

- **Setting**: A busy waterfront/port area near San Francisco Bay.
- **Background**: Large cargo ship docked at pier. Crates stacked along the dock. Bay water visible.
- **Ground**: Concrete dock surface.
- **Spectators**: Dockworkers and bystanders cheer in the background.
- **Ambient details**: Water reflections, ship horn sounds.
- **Music**: "Ken's Theme" -- energetic rock-influenced composition.

### 11.3 Chun-Li's Stage -- Street Market, China

- **Setting**: A bustling Chinese street market.
- **Background**: Colorful banners, shop signs with Chinese characters, storefronts. Crowd of people walking and shopping.
- **Ground**: Stone street pavement.
- **Spectators**: Market vendors and customers react to the fight. A man in the background with a chicken (notorious background detail).
- **Ambient details**: Busy market atmosphere.
- **Music**: "Chun-Li's Theme" -- fast-paced Chinese-influenced melody with strong rhythm.

### 11.4 Guile's Stage -- Air Force Base, USA

- **Setting**: A US military air force base tarmac.
- **Background**: F-16 fighter jet parked on the runway. Chain-link fence. Military crates. Storage hangars.
- **Ground**: Asphalt tarmac.
- **Spectators**: Military personnel in uniform stand watching. One man crouches near the fence.
- **Ambient details**: Jet exhaust heat shimmer. American flags.
- **Music**: "Guile's Theme" -- iconic military march with soaring melody (widely known meme: "Guile's Theme goes with everything").

### 11.5 Blanka's Stage -- Amazon River, Brazil

- **Setting**: A jungle clearing on the banks of the Amazon River.
- **Background**: Dense tropical foliage, wooden shack/hut, a small boat on the river. Overgrown vegetation.
- **Ground**: Dirt/mud ground.
- **Spectators**: Villagers and animals (including a capybara-like creature) in the background.
- **Ambient details**: Water ripples on the river. Lush greenery.
- **Music**: "Blanka's Theme" -- tribal/jungle rhythm with wild energy.

### 11.6 Zangief's Stage -- Iron Foundry, USSR

- **Setting**: An industrial factory/iron foundry in the Soviet Union.
- **Background**: Massive industrial machinery, glowing furnaces, pipes, and smokestacks. Workers in the background.
- **Ground**: Metal factory floor.
- **Spectators**: Factory workers in overalls watch and cheer.
- **Ambient details**: Sparks fly from machinery. Red-hot metal visible. Smoke and steam.
- **Music**: "Zangief's Theme" -- heavy, Russian-influenced composition with powerful rhythm.

### 11.7 Dhalsim's Stage -- Temple, India

- **Setting**: A courtyard outside an Indian temple.
- **Background**: Ornate temple architecture, stone carvings, elephants standing in the background.
- **Ground**: Dusty stone floor.
- **Spectators**: Indian devotees and onlookers. Elephants sway gently.
- **Ambient details**: Incense smoke, spiritual atmosphere.
- **Music**: "Dhalsim's Theme" -- mysterious, meditative melody with Indian musical influences.

### 11.8 E. Honda's Stage -- Sentou (Bathhouse), Japan

- **Setting**: A traditional Japanese public bathhouse.
- **Background**: Ornate tiled walls with Mount Fuji mural. Steaming water. Wooden buckets and stools.
- **Ground**: Wet tiled floor.
- **Spectators**: Bathhouse patrons sit in the background watching.
- **Ambient details**: Steam rises from the bath. Splashing water effects.
- **Music**: "E. Honda's Theme" -- Japanese traditional-style music with sumo drumming energy.

### 11.9 Balrog's Stage -- Las Vegas Casino, USA

- **Setting**: Inside a Las Vegas boxing ring/casino.
- **Background**: Neon lights, casino signage, boxing ring ropes. Slot machines visible. Crowd cheering.
- **Ground**: Boxing ring canvas floor.
- **Spectators**: Enthusiastic Vegas crowd. One spectator is known for crying after KOs (betting on the loser).
- **Ambient details**: Neon glow, camera flashes from the crowd.
- **Music**: "Balrog's Theme" -- aggressive, boxing-match energy with heavy brass.

### 11.10 Vega's Stage -- Cage Arena, Spain

- **Setting**: An outdoor bullfighting-inspired arena enclosed with a chain-link cage/fence.
- **Background**: Chain-link fence surrounding the arena. Night sky. Spanish architecture visible beyond the cage. Crowd pressing against the fence.
- **Ground**: Stone/dirt arena floor.
- **Special mechanic**: Vega can jump to the cage wall and launch off it for his Flying Barcelona Attack. This is the only stage with a wall-jump surface.
- **Spectators**: Rowdy crowd pressed against the fence, cheering.
- **Music**: "Vega's Theme" -- dramatic Spanish flamenco-influenced composition.

### 11.11 Sagat's Stage -- Reclining Buddha, Thailand

- **Setting**: A temple with a massive Reclining Buddha statue.
- **Background**: Enormous golden Reclining Buddha statue fills the background. Ornate temple pillars and decorations.
- **Ground**: Temple stone floor.
- **Spectators**: Thai monks and spectators in the background.
- **Ambient details**: Candlelight, spiritual atmosphere.
- **Music**: "Sagat's Theme" -- composed by Isao Abe. Intense Muay Thai combat energy.

### 11.12 M. Bison's Stage -- Shadaloo Temple, Thailand

- **Setting**: M. Bison's Shadaloo headquarters temple.
- **Background**: Large stone bell and statues. Monks meditating in the background. Torches and candles.
- **Ground**: Stone temple floor.
- **Destructible elements**: Stone statues flanking the arena can be destroyed by stray attacks. When destroyed, the meditating monks stand up and begin shouting angrily.
- **Spectators**: Meditating monks (who become agitated if statues are broken).
- **Music**: "M. Bison's Theme" -- ominous, militaristic, and powerful. Dark and foreboding.

---

## 12. Bonus Stages

Three bonus stages appear between sets of opponents in single-player mode. They are timed events awarding bonus points.

### 12.1 Bonus Stage 1: Car Destruction

| Parameter | Value |
|---|---|
| Appears after | Defeating the 3rd opponent |
| Time limit | 40 seconds |
| Objective | Completely destroy a parked car using attacks |
| Car sections | Hood, roof, trunk, doors (left and right), windshield, taillights, wheels |
| Scoring | 100 points per hit, plus section completion bonuses |
| Perfect bonus | 30,000 points for destroying all sections + 100 points per second remaining |
| Strategy | Use heavy attacks and special moves. Must attack from both sides to reach all sections. |
| Failure | If time expires before the car is destroyed, no perfect bonus. Still awarded points for damage done. |

### 12.2 Bonus Stage 2: Barrel Breaking

| Parameter | Value |
|---|---|
| Appears after | Defeating the 6th opponent |
| Time limit | Display shows "20" but this is a barrel count, not seconds |
| Objective | Smash all 20 barrels as they drop from a conveyor belt above |
| Barrel behavior | Barrels drop one at a time from an overhead conveyor belt, landing on either side of the player |
| Scoring | 1,000 points per barrel destroyed |
| Perfect bonus | 30,000 points for destroying all 20 barrels (total maximum: 50,000 points) |
| Strategy | Position yourself to intercept barrels quickly. Use fast normals. |
| Barrel damage | If a barrel lands on the player, it knocks them down briefly. |

### 12.3 Bonus Stage 3: Oil Drum Destruction

| Parameter | Value |
|---|---|
| Appears after | Defeating the 7th opponent (before the boss gauntlet) |
| Time limit | 40 seconds |
| Objective | Destroy a stack of flaming oil drums |
| Drum arrangement | Drums are stacked in a pyramid formation. Some are on fire. |
| Barrel rolling | Barrels roll toward the player from above and can knock them down |
| Scoring | Points awarded per drum destroyed |
| Perfect bonus | 30,000 points for complete destruction + time bonus |
| Hazard | Flaming drums and rolling barrels damage the player on contact |

---

## 13. Single-Player Mode

### 13.1 Opponent Order

The single-player mode has three phases:

**Phase 1: World Warriors (7 fights)**
- The player fights the other 7 playable characters (excluding their own character, since mirror matches are not allowed in World Warrior).
- Fight order is variable. The first 3-4 opponents are generally weaker, with difficulty scaling upward.
- Each fight is a best-of-3 rounds match (default 2 rounds to win).
- Bonus Stage 1 (Car) appears after the 3rd win.
- Bonus Stage 2 (Barrels) appears after the 6th win.
- Bonus Stage 3 (Oil Drums) appears after the 7th win.

**Phase 2: Boss Gauntlet (4 fights)**
- The player fights the four non-playable boss characters in fixed order:
  1. Balrog (Las Vegas)
  2. Vega (Spain)
  3. Sagat (Thailand)
  4. M. Bison (Thailand -- Shadaloo Temple)
- Each boss fight is best-of-3 rounds.

**Phase 3: Ending**
- After defeating M. Bison, the player sees their selected character's unique ending sequence (text and still artwork/animation).
- The game displays the player's final score and then returns to the title screen / attract mode.

### 13.2 CPU AI Behavior

The CPU AI operates through three primary modes:

| AI Mode | Description |
|---|---|
| Waiting/Idle | AI selects random walking patterns (forward/backward). Waits for the player to commit to an action. |
| Attacking | AI selects attack scripts from a pool of 8 difficulty levels. Higher levels use more aggressive and optimal sequences. |
| Reacting/Countering | AI reads player input on the frame it is entered (before the move's first animation frame displays) and selects a counter-script. |

**AI Difficulty Scaling:**
- 8 difficulty levels configurable via DIP switch: Easiest, Very Easy, Easy, Normal (default), Difficult, Hard, Very Hard, Hardest.
- Within a single-player run, AI difficulty increases progressively with each opponent.
- The AI script level also scales with round timer -- later in a round, the AI uses higher-level scripts.

**AI Cheating Mechanics:**
- The CPU can read player inputs before the move's first animation frame (1-frame input reading advantage).
- The CPU can execute charge moves with zero charge time (instant charge specials).
- The CPU has perfect execution (zero input failure chance).
- At lower difficulty levels, the AI deliberately lets attacks through unblocked.

**AI Exploitable Weaknesses:**
- The AI has poor understanding of Dhalsim's range at lower difficulties.
- Repeating certain safe patterns (e.g., Dhalsim Yoga Fire + standing MK) can exploit predictable AI responses.
- The AI is generally weak against cross-ups at lower difficulty levels.

### 13.3 Scoring System

| Event | Points Awarded |
|---|---|
| Normal attack hit | 100 points per hit |
| Special move hit | 200-300 points per hit |
| Throw | 300 points |
| Round win | Time bonus: 100 points per second remaining on timer |
| Perfect round (no damage taken) | 30,000 point bonus |
| Bonus stage completion | Variable (see Bonus Stages section) |
| KO finish (opponent KO'd by special move) | 500 bonus points |
| Match win | Match completion bonus |

### 13.4 Character Endings

Each of the 8 playable characters has a unique ending sequence after defeating M. Bison:

| Character | Ending Summary |
|---|---|
| Ryu | Refuses fame; continues his training journey alone seeking stronger opponents. |
| Ken | Returns home to his girlfriend Eliza; continues competing but finds meaning in personal life. |
| Chun-Li | Avenges her father's death at the hands of Shadaloo; returns to her normal life. |
| Guile | Confronts Bison to avenge his friend Charlie; considers killing Bison but is stopped by his family. |
| Blanka | Reunites with his mother who recognizes him by his ankle bracelet. Emotional reunion. |
| Zangief | Returns to the USSR as a hero; celebrated by the people. |
| Dhalsim | Returns to his Indian village; uses his winnings to help his community. |
| E. Honda | Returns to Japan; sumo wrestling gains international recognition due to his victory. |

---

## 14. Audio Design

### 14.1 Music

The soundtrack was primarily composed by **Yoko Shimomura** (credited as "Pii" in the game), with additional contributions from **Isao Abe** (Sagat's Theme and various jingles). The music was requested by head designer Akira Nishitani to have clear, catchy melodies reflecting each fighter's national origin and personality.

**Hardware:** Yamaha YM2151 (4-operator FM synthesis, 8 channels) + OKI MSM6295 (ADPCM sample playback, 4 channels).

| Track | Usage | Tempo/Style |
|---|---|---|
| Ryu's Theme | Ryu's stage | Moderate, martial arts energy, iconic main melody |
| Ken's Theme | Ken's stage | Fast, rock-influenced, guitar-like FM synth leads |
| Chun-Li's Theme | Chun-Li's stage | Fast, Chinese-influenced melody with driving rhythm |
| Guile's Theme | Guile's stage | Military march feel, soaring melody, most iconic track |
| Blanka's Theme | Blanka's stage | Wild tribal rhythm, jungle percussion |
| Zangief's Theme | Zangief's stage | Heavy Russian-influenced, powerful and imposing |
| Dhalsim's Theme | Dhalsim's stage | Mysterious, meditative, Indian instrumentation |
| E. Honda's Theme | E. Honda's stage | Japanese traditional feel, sumo energy, taiko-like drums |
| Balrog's Theme | Balrog's stage | Aggressive, boxing match intensity, heavy brass |
| Vega's Theme | Vega's stage | Dramatic Spanish flamenco, elegant yet menacing |
| Sagat's Theme | Sagat's stage (composed by Isao Abe) | Intense Muay Thai combat, driving percussion |
| M. Bison's Theme | M. Bison's stage | Dark, ominous, militaristic, foreboding power |
| Character Select | Character selection screen | Tense, anticipatory |
| VS Screen | Pre-fight matchup display | Brief dramatic sting |
| Continue Screen | Continue countdown | Urgent, pressuring |
| Ending Theme | Character endings | Triumphant, heroic |
| Game Over | Game over screen | Somber, defeated |
| Bonus Stage | All bonus stages | Energetic, encouraging |

### 14.2 Sound Effects

| Sound | Trigger |
|---|---|
| Punch impact (light) | LP connects |
| Punch impact (medium) | MP connects |
| Punch impact (heavy) | HP connects. Louder, deeper impact. |
| Kick impact (light) | LK connects |
| Kick impact (medium) | MK connects |
| Kick impact (heavy) | HK connects. Louder thud. |
| Block sound | Attack is blocked. Distinct from hit sound (more of a thud/slap). |
| Whiff sound | No sound on whiffed normals (air slash sound on some moves). |
| Hadouken fire | Ryu/Ken/Sagat fireball released |
| Sonic Boom fire | Guile releases Sonic Boom |
| Shoryuken rising | Rising whoosh sound during Shoryuken |
| Throw impact | Slam/thud on throw connection |
| KO impact | Exaggerated heavy impact on the finishing blow |
| Dizzy birds/stars | Twittering/jingling sound while dizzied |
| Timer warning | Rapid beeping when timer drops below 10 |
| Round call | "Round One... FIGHT!" (synthesized voice) |
| KO call | "K.O." (synthesized voice) |
| Perfect call | "PERFECT!" (synthesized voice when winning without taking damage) |
| You Win / You Lose | Post-round announcements |
| Character select sound | Click/confirm when selecting a character |

### 14.3 Character Voice Samples

Each character has distinctive voice samples for special moves and reactions:

| Character | Voice Lines |
|---|---|
| Ryu | "Hadouken!", "Shoryuken!", "Tatsumaki Senpukyaku!" + hit grunts, KO cry |
| Ken | "Hadouken!", "Shoryuken!", "Tatsumaki Senpukyaku!" + hit grunts (slightly different pitch from Ryu) |
| Chun-Li | "Yatta!" (victory), kiai shouts during attacks, KO cry |
| Guile | "Sonic Boom!", "Somersault!" + grunts |
| Blanka | Roars and growls during attacks, electric sizzle during Electric Thunder |
| Zangief | "Hyaah!" during Lariat, slam sounds during SPD, grunts |
| Dhalsim | "Yoga Fire!", "Yoga Flame!" + meditative kiai shouts |
| E. Honda | "Dosukoi!" during Hundred Hand Slap, headbutt impact shout |

---

## 15. UI Layout

### 15.1 HUD Elements (During Gameplay)

The in-game HUD is positioned along the top edge of the screen, leaving the majority of the 384x224 display clear for the fight.

```
+------------------------------------------------------------------+
| [P1 SCORE]                                        [P2 SCORE]     |
| [P1 Name] [P1 Health Bar]====[TIMER]====[P2 Health Bar] [P2 Name]|
| [P1 V V]  [P1 Stun Meter]            [P2 Stun Meter]   [V V P2] |
+------------------------------------------------------------------+
|                                                                    |
|                     (Fight Area ~384x180)                          |
|                                                                    |
|        [P1 Character]              [P2 Character]                  |
|                                                                    |
|  ==============================Ground Line====================     |
+------------------------------------------------------------------+
```

| HUD Element | Position | Description |
|---|---|---|
| Player 1 Health Bar | Top-left, extending right | Yellow bar (144 pixels max). Depletes left-to-right as damage is taken. Turns red for lost health. |
| Player 2 Health Bar | Top-right, extending left | Mirror of P1 health bar. Depletes right-to-left. |
| Round Timer | Top-center, between health bars | 2-digit number counting down. Displays "99" at round start (default). |
| Player 1 Name | Below P1 health bar, left side | Character name in text. |
| Player 2 Name | Below P2 health bar, right side | Character name in text. |
| Round Win Markers | Below health bars, near names | "V" symbols (victory markers). One V per round won. Shows how many rounds each player has won. |
| Player 1 Score | Top-left corner above health bar | Running point total. |
| Player 2 Score | Top-right corner above health bar | Running point total. |
| Stun Meter | Small bar below health bars | Invisible in WW original (stun meter display was added in Super SF2). In WW, stun is a hidden value. |

**Correction**: The stun meter is NOT visually displayed in World Warrior. It is an internal hidden value. The stun meter became visible in later versions (Super Street Fighter II onward).

### 15.2 Character Select Screen

```
+------------------------------------------------------------------+
|                    SELECT YOUR FIGHTER                             |
|                                                                    |
|   [RYU]    [E.HONDA]  [BLANKA]  [GUILE]                          |
|   [KEN]    [CHUN-LI]  [ZANGIEF] [DHALSIM]                        |
|                                                                    |
|   [P1 Cursor]                   [P2 Cursor]                       |
|                                                                    |
|   [Character Portrait]    [Character Portrait]                     |
|   [P1 selected char]     [P2 selected char]                       |
+------------------------------------------------------------------+
```

- 8 character portraits arranged in a 4x2 grid.
- Player 1 cursor (hand icon) selects with joystick and confirms with any button.
- Player 2 cursor appears if a second player joins.
- **Mirror match restriction**: Both players cannot select the same character in World Warrior. If P2 tries to pick P1's character, the selection is denied.
- Selected character's large portrait and name appear below the grid.

### 15.3 VS Screen

After character selection, a VS screen displays:
- Player 1's character portrait on the left.
- "VS" text in the center.
- Player 2's (or CPU's) character portrait on the right.
- Country flags for each character.
- Brief dramatic music sting.

### 15.4 Round Start Overlay

- "ROUND X" text appears center-screen (X = 1, 2, 3...).
- Followed by "FIGHT!" text.
- Characters are briefly immobilized during this display (~60 frames).

### 15.5 Round End Overlays

| Condition | Display |
|---|---|
| KO | "K.O." text flashes on screen. Loser falls. |
| Time Over | "TIME" text flashes. Winner determined by remaining health. |
| Double KO | "DOUBLE K.O." text. Both characters fall. |
| Draw Game | "DRAW GAME" text. Neither player wins the round. |
| Perfect | "PERFECT" text if the winner took zero damage. |

### 15.6 Continue Screen

- 10-second countdown with large numbers.
- The player's defeated character is shown in a beaten/defeated pose.
- "CONTINUE?" prompt.
- If a credit is inserted and start is pressed, the player continues.
- If time expires, "GAME OVER" is displayed and the game returns to the attract mode.

### 15.7 Attract Mode / Title Screen

- "STREET FIGHTER II: The World Warrior" logo.
- Cycles through: title screen -> demo fight (CPU vs CPU) -> high score table -> character intro screens.
- "INSERT COIN" text flashes.
- Press START to begin (with credits available).

---

## 16. DIP Switch Configuration (Arcade Operator Settings)

| DIP Switch | Options | Default |
|---|---|---|
| Difficulty | Easiest, Very Easy, Easy, Normal, Difficult, Hard, Very Hard, Hardest | Normal |
| Round Timer | 30, 60, 99, Infinite | 99 |
| Rounds to Win | 1, 2, 3, 4 | 2 |
| Coin Slots | 1 Coin/1 Credit through 4 Coins/1 Credit (various configurations) | 1 Coin/1 Credit |
| Free Play | On / Off | Off |
| Demo Sound | On / Off | On |
| Flip Screen | On / Off | Off |
| Continue | On / Off | On |

---

## 17. Known Bugs and Glitches (World Warrior Specific)

These are documented bugs present in the original World Warrior arcade ROM that should be faithfully reproduced for an accurate recreation.

| Bug | Description |
|---|---|
| Guile Magic Throw | Guile can throw opponents from outside normal throw range by holding Forward slightly longer with near-simultaneous button presses. |
| Guile Handcuffs | Guile's MP throw followed immediately by Flash Kick causes the opponent to become "stuck" to Guile. The opponent becomes invincible while Guile loses access to special moves. A Magic Throw can break the effect. |
| Random Special Move | 1-in-256 chance per frame that a random button press executes a special move without the correct joystick motion. |
| Random Auto-Block | 1-in-256 chance per frame that an incoming attack is automatically blocked regardless of player input. |
| CPS-1 Chains | Light rapid-fire normals can be canceled into other normals in different positions (standing/crouching). This is technically unintended but is a core WW mechanic. |
| Jump Cancel from Chains | Chainable light normals can be jump-canceled, allowing unusual combo routes. |
| Ryu Weak Point | Ryu takes double damage when hit during the farthest forward-leaning frame of his dizzy animation. |
| Charge Storage via Throw | Specific throw timing with Guile can store a charge, allowing Flash Kick from any kick button without the charge motion. |
| Knock Down Cancel | When knockdown and non-knockdown moves hit simultaneously, the knockdown is canceled. |

---

## 18. Tier List (Competitive Community Consensus, World Warrior)

For reference in balancing and AI difficulty:

| Tier | Characters |
|---|---|
| S (Top) | Guile |
| A (High) | Dhalsim, Ken |
| B (Mid-High) | Ryu, Chun-Li, E. Honda |
| C (Mid) | Blanka |
| D (Low) | Zangief |

**Note**: Boss characters are not ranked as they are CPU-only and not subject to competitive play in World Warrior.

---

## 19. Technical Notes for Implementation

### 19.1 Collision System

- **Hitboxes**: Rectangular regions attached to character sprites that deal damage when overlapping an opponent's hurtbox.
- **Hurtboxes**: Rectangular regions attached to character sprites that receive damage when overlapped by an opponent's hitbox.
- **Push boxes**: Rectangular region preventing characters from overlapping. Characters cannot walk through each other.
- **Throw boxes**: Separate rectangular region for throw range detection.
- Each animation frame has independently defined hitboxes, hurtboxes, and push boxes.
- Projectiles have their own hitboxes that travel independently of the character.

### 19.2 Camera System

- Camera tracks the midpoint between both characters horizontally.
- Camera does not move vertically (fixed Y position).
- Invisible walls at stage boundaries prevent characters from leaving the arena.
- When characters reach the edge of the stage, the trailing character is pushed by the camera boundary.

### 19.3 Game Loop

```
Each frame (~16.78ms):
1. Read inputs from both players
2. Process input buffers and detect special move commands
3. Update character states (idle, walking, attacking, hit stun, block stun, airborne, etc.)
4. Execute active move logic (advance animation frames, activate/deactivate hitboxes)
5. Check hitbox/hurtbox collisions
6. Apply damage, stun, and hit stun/block stun on collision
7. Update health bars, timer, score
8. Check round-end conditions (KO, Time Over, Double KO)
9. Update camera position
10. Render background layers (parallax scrolling)
11. Render character sprites
12. Render HUD overlay
13. Output audio (music + sound effects)
```

### 19.4 State Machine (Per Character)

| State | Description |
|---|---|
| Idle | Standing neutral. Can perform any action. |
| Walking Forward | Moving toward opponent. Can cancel into any action. |
| Walking Backward | Moving away from opponent. Automatically blocks if hit. Can cancel into any action. |
| Crouching | Ducking. Can perform crouching normals, block low. |
| Pre-Jump | 4 frames of grounded startup before becoming airborne. Throwable. |
| Airborne (Rising) | Ascending phase of jump. Can perform aerial normals. |
| Airborne (Falling) | Descending phase of jump. Can perform aerial normals. |
| Standing Normal | Performing a standing attack. May be cancelable. |
| Crouching Normal | Performing a crouching attack. May be cancelable. |
| Jumping Normal | Performing an aerial attack. |
| Special Move | Performing a special move. Cannot be interrupted. |
| Hit Stun (Standing) | Taking a hit while standing. Cannot act until stun ends. |
| Hit Stun (Crouching) | Taking a hit while crouching. Cannot act until stun ends. |
| Block Stun (Standing) | Blocking a hit while standing. Cannot act until stun ends. |
| Block Stun (Crouching) | Blocking a hit while crouching. Cannot act until stun ends. |
| Airborne Hit | Hit while airborne. Character enters tumble animation. |
| Knockdown | On the ground after being knocked down. Invulnerable until wakeup begins. |
| Wakeup | Rising from knockdown. Vulnerable but cannot act until fully recovered. |
| Dizzy | Stunned with stars/birds overhead. Cannot act until mashing escape or timer expires. |
| Thrown | In the process of being thrown by the opponent. |
| KO | Health reached 0. Fall animation plays. Round ends. |
| Victory Pose | Post-round win animation. |
| Intro Walk | Pre-round walk-on animation. |

---

## 20. Summary of World Warrior-Specific Traits

The following features are unique to the original World Warrior and differ from later Street Fighter II revisions:

| Feature | World Warrior Behavior |
|---|---|
| Mirror matches | NOT allowed. Both players must pick different characters. |
| Playable bosses | NOT available. Balrog, Vega, Sagat, and M. Bison are CPU-only. |
| Reversals on wakeup | Do NOT exist. Cannot perform special moves on the first wakeup frame. |
| Chun-Li Kikoken | Does NOT exist. Added in Hyper Fighting. |
| Dhalsim Yoga Teleport | Does NOT exist. Added in Hyper Fighting. |
| Ryu Shoryuken knockdown | Does NOT knock down grounded opponents (Ken's does). |
| CPS-1 chains | Present. Light normals chain into other normals across positions. |
| Combo damage scaling | None. All hits deal full damage. |
| Game speed | Fixed. No turbo/speed options. |
| Throw teching | NOT possible. All throws are guaranteed if in range. |
| Air blocking | Does NOT exist. |
| Super meter / Super combos | Do NOT exist. Added in Super Street Fighter II Turbo. |
| Random special move bug | 1/256 chance present. |
| Random auto-block bug | 1/256 chance present. |
| Guile glitches | Magic Throw, Handcuffs, and Charge Storage bugs all present. |
