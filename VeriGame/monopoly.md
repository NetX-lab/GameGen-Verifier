# 22 Monopoly -- Faithful Digital Recreation

## 1. Game Overview

| Field | Value |
|---|---|
| **Title** | Monopoly |
| **Original Publisher** | Parker Brothers (1935); now Hasbro |
| **Genre** | Board / Property Trading / Economic Strategy |
| **Player Count** | 2 -- 8 (best with 3 -- 6) |
| **Core Fantasy** | Roll dice and traverse a square board of 40 spaces, buying streets, railroads, and utilities, collecting rent from opponents, building houses and hotels, and driving every other player into bankruptcy to become the last player standing with a real-estate monopoly. |
| **Camera / Presentation** | Top-down 2D board view; the square board fills the center of the screen, player panels line the edges, a persistent bank/trade overlay is accessible at all times, and property cards pop up on interaction. |
| **Target Session Length** | 60 -- 180 minutes (standard rules); shorter with optional speed die or timed variants. |
| **Target Skill Curve** | Accessible entry (dice rolling, buying properties); depth emerges through trade negotiation, monopoly control, building timing, mortgage leverage, auction strategy, and cash-flow management. |
| **Rule Edition** | Classic US Edition (post-2008 standardization): flat $200 Income Tax, $100 Luxury Tax, 16 Chance / 16 Community Chest cards (2008--2021 deck). Optional Speed Die variant included. |

---

## 2. Technical Foundation (Digital Version)

### 2.1 Simulation Architecture

| Parameter | Value |
|---|---|
| Logic tick rate | Turn-based; no continuous simulation required. UI animations run at 60 FPS. |
| Update order | `DiceRoll -> Movement -> LandingResolution -> PostLandAction (buy/auction/card/tax/jail) -> BuildPhase -> TradePhase -> TurnEnd -> BankruptcyCheck -> NextPlayer` |
| RNG | Single seeded PRNG stream for dice rolls, card-deck shuffles, and AI decisions. |
| Determinism | Identical seed + identical input sequence must produce identical game states. |
| Replay format | Initial seed + ordered action records (dice results, buy/auction/build/trade/mortgage decisions). |
| Checksum | Deterministic hash after every completed turn for replay verification. |

### 2.2 Performance Budget

| Metric | Budget |
|---|---|
| Render frame | 16.67 ms (60 FPS) |
| Logic tick (avg) | <= 2 ms |
| Logic tick (p99) | <= 5 ms |
| Full-state bankruptcy evaluation | <= 5 ms |

### 2.3 Core Technical Constraints

- No gameplay rule logic may reside in renderer-only code paths.
- Pause freezes all gameplay timers and animation timers.
- All monetary values, rents, card texts, and board layout must be externalized in configuration (not hardcoded).
- The Bank is an infinite money source; it can never go bankrupt. If the physical-money supply runs out, the digital Bank simply creates more.
- Save operation must be atomic: write to temp file, fsync, rename.

---

## 3. Board Layout -- All 40 Spaces

The board is a square loop of 40 spaces. Position 0 is GO (the starting space). Players move clockwise. The four sides are commonly called Bottom (spaces 0--10), Left (10--20), Top (20--30), and Right (30--40/0).

| Pos | Space Name | Type | Color Group |
|---|---|---|---|
| 0 | GO | Corner -- Collect $200 | -- |
| 1 | Mediterranean Avenue | Property | Brown |
| 2 | Community Chest | Card Draw | -- |
| 3 | Baltic Avenue | Property | Brown |
| 4 | Income Tax | Tax -- Pay $200 | -- |
| 5 | Reading Railroad | Railroad | -- |
| 6 | Oriental Avenue | Property | Light Blue |
| 7 | Chance | Card Draw | -- |
| 8 | Vermont Avenue | Property | Light Blue |
| 9 | Connecticut Avenue | Property | Light Blue |
| 10 | Jail / Just Visiting | Corner | -- |
| 11 | St. Charles Place | Property | Pink |
| 12 | Electric Company | Utility | -- |
| 13 | States Avenue | Property | Pink |
| 14 | Virginia Avenue | Property | Pink |
| 15 | Pennsylvania Railroad | Railroad | -- |
| 16 | St. James Place | Property | Orange |
| 17 | Community Chest | Card Draw | -- |
| 18 | Tennessee Avenue | Property | Orange |
| 19 | New York Avenue | Property | Orange |
| 20 | Free Parking | Corner -- No action | -- |
| 21 | Kentucky Avenue | Property | Red |
| 22 | Chance | Card Draw | -- |
| 23 | Indiana Avenue | Property | Red |
| 24 | Illinois Avenue | Property | Red |
| 25 | B. & O. Railroad | Railroad | -- |
| 26 | Atlantic Avenue | Property | Yellow |
| 27 | Ventnor Avenue | Property | Yellow |
| 28 | Water Works | Utility | -- |
| 29 | Marvin Gardens | Property | Yellow |
| 30 | Go To Jail | Corner -- Send to Jail | -- |
| 31 | Pacific Avenue | Property | Green |
| 32 | North Carolina Avenue | Property | Green |
| 33 | Community Chest | Card Draw | -- |
| 34 | Pennsylvania Avenue | Property | Green |
| 35 | Short Line | Railroad | -- |
| 36 | Chance | Card Draw | -- |
| 37 | Park Place | Property | Dark Blue |
| 38 | Luxury Tax | Tax -- Pay $100 | -- |
| 39 | Boardwalk | Property | Dark Blue |

### 3.1 Corner Spaces

| Corner | Position | Effect |
|---|---|---|
| GO | 0 | Players collect $200 salary each time they pass or land on GO. |
| Jail / Just Visiting | 10 | If sent to Jail, token goes to the "In Jail" section. If passing through normally, the player is "Just Visiting" and nothing happens. |
| Free Parking | 20 | No action. The player's turn ends normally. (Official rules: no money is collected here.) |
| Go To Jail | 30 | Player is sent directly to Jail. They do not pass GO, do not collect $200. |

### 3.2 Tax Spaces

| Space | Position | Amount |
|---|---|---|
| Income Tax | 4 | Pay $200 to the Bank. |
| Luxury Tax | 38 | Pay $100 to the Bank. |

---

## 4. Property System

### 4.1 Street Properties -- Complete Deed Reference

All 22 street properties are listed below with their complete rent schedules. Mortgage value is always half the purchase price. When a player owns all properties in a color group (a "monopoly"), unimproved rent on streets in that group is doubled.

#### Brown (2 properties) -- House/Hotel Cost: $50 each

| Property | Pos | Price | Mortgage | Rent | 1 House | 2 Houses | 3 Houses | 4 Houses | Hotel |
|---|---|---|---|---|---|---|---|---|---|
| Mediterranean Avenue | 1 | $60 | $30 | $2 | $10 | $30 | $90 | $160 | $250 |
| Baltic Avenue | 3 | $60 | $30 | $4 | $20 | $60 | $180 | $320 | $450 |

#### Light Blue (3 properties) -- House/Hotel Cost: $50 each

| Property | Pos | Price | Mortgage | Rent | 1 House | 2 Houses | 3 Houses | 4 Houses | Hotel |
|---|---|---|---|---|---|---|---|---|---|
| Oriental Avenue | 6 | $100 | $50 | $6 | $30 | $90 | $270 | $400 | $550 |
| Vermont Avenue | 8 | $100 | $50 | $6 | $30 | $90 | $270 | $400 | $550 |
| Connecticut Avenue | 9 | $120 | $60 | $8 | $40 | $100 | $300 | $450 | $600 |

#### Pink (3 properties) -- House/Hotel Cost: $100 each

| Property | Pos | Price | Mortgage | Rent | 1 House | 2 Houses | 3 Houses | 4 Houses | Hotel |
|---|---|---|---|---|---|---|---|---|---|
| St. Charles Place | 11 | $140 | $70 | $10 | $50 | $150 | $450 | $625 | $750 |
| States Avenue | 13 | $140 | $70 | $10 | $50 | $150 | $450 | $625 | $750 |
| Virginia Avenue | 14 | $160 | $80 | $12 | $60 | $180 | $500 | $700 | $900 |

#### Orange (3 properties) -- House/Hotel Cost: $100 each

| Property | Pos | Price | Mortgage | Rent | 1 House | 2 Houses | 3 Houses | 4 Houses | Hotel |
|---|---|---|---|---|---|---|---|---|---|
| St. James Place | 16 | $180 | $90 | $14 | $70 | $200 | $550 | $750 | $950 |
| Tennessee Avenue | 18 | $180 | $90 | $14 | $70 | $200 | $550 | $750 | $950 |
| New York Avenue | 19 | $200 | $100 | $16 | $80 | $220 | $600 | $800 | $1000 |

#### Red (3 properties) -- House/Hotel Cost: $150 each

| Property | Pos | Price | Mortgage | Rent | 1 House | 2 Houses | 3 Houses | 4 Houses | Hotel |
|---|---|---|---|---|---|---|---|---|---|
| Kentucky Avenue | 21 | $220 | $110 | $18 | $90 | $250 | $700 | $875 | $1050 |
| Indiana Avenue | 23 | $220 | $110 | $18 | $90 | $250 | $700 | $875 | $1050 |
| Illinois Avenue | 24 | $240 | $120 | $20 | $100 | $300 | $750 | $925 | $1100 |

#### Yellow (3 properties) -- House/Hotel Cost: $150 each

| Property | Pos | Price | Mortgage | Rent | 1 House | 2 Houses | 3 Houses | 4 Houses | Hotel |
|---|---|---|---|---|---|---|---|---|---|
| Atlantic Avenue | 26 | $260 | $130 | $22 | $110 | $330 | $800 | $975 | $1150 |
| Ventnor Avenue | 27 | $260 | $130 | $22 | $110 | $330 | $800 | $975 | $1150 |
| Marvin Gardens | 29 | $280 | $140 | $24 | $120 | $360 | $850 | $1025 | $1200 |

#### Green (3 properties) -- House/Hotel Cost: $200 each

| Property | Pos | Price | Mortgage | Rent | 1 House | 2 Houses | 3 Houses | 4 Houses | Hotel |
|---|---|---|---|---|---|---|---|---|---|
| Pacific Avenue | 31 | $300 | $150 | $26 | $130 | $390 | $900 | $1100 | $1275 |
| North Carolina Avenue | 32 | $300 | $150 | $26 | $130 | $390 | $900 | $1100 | $1275 |
| Pennsylvania Avenue | 34 | $320 | $160 | $28 | $150 | $450 | $1000 | $1200 | $1400 |

#### Dark Blue (2 properties) -- House/Hotel Cost: $200 each

| Property | Pos | Price | Mortgage | Rent | 1 House | 2 Houses | 3 Houses | 4 Houses | Hotel |
|---|---|---|---|---|---|---|---|---|---|
| Park Place | 37 | $350 | $175 | $35 | $175 | $500 | $1100 | $1300 | $1500 |
| Boardwalk | 39 | $400 | $200 | $50 | $200 | $600 | $1400 | $1700 | $2000 |

### 4.2 Building Cost Summary by Color Group

| Color Group | Properties in Group | House Cost | Hotel Cost (+ 4 houses traded in) |
|---|---|---|---|
| Brown | 2 | $50 | $50 |
| Light Blue | 3 | $50 | $50 |
| Pink | 3 | $100 | $100 |
| Orange | 3 | $100 | $100 |
| Red | 3 | $150 | $150 |
| Yellow | 3 | $150 | $150 |
| Green | 3 | $200 | $200 |
| Dark Blue | 2 | $200 | $200 |

### 4.3 Monopoly Rent Bonus

When a player owns all properties in a color group and none of them are mortgaged, the unimproved rent on each street in that group is **doubled**. This doubling applies only to the base rent (no houses/hotel); once any house is built, the deed-card rent schedule applies directly.

---

## 5. Railroads

| Railroad | Position | Price | Mortgage |
|---|---|---|---|
| Reading Railroad | 5 | $200 | $100 |
| Pennsylvania Railroad | 15 | $200 | $100 |
| B. & O. Railroad | 25 | $200 | $100 |
| Short Line | 35 | $200 | $100 |

### 5.1 Railroad Rent Schedule

Rent depends on how many railroads the collecting player owns (all must be unmortgaged to count):

| Railroads Owned | Rent |
|---|---|
| 1 | $25 |
| 2 | $50 |
| 3 | $100 |
| 4 | $200 |

No houses or hotels can be built on railroads.

---

## 6. Utilities

| Utility | Position | Price | Mortgage |
|---|---|---|---|
| Electric Company | 12 | $150 | $75 |
| Water Works | 28 | $150 | $75 |

### 6.1 Utility Rent Calculation

Rent is calculated as a multiplier of the dice roll that brought the opponent to the utility space:

| Utilities Owned | Rent Formula |
|---|---|
| 1 | 4 x (sum of dice roll) |
| 2 | 10 x (sum of dice roll) |

- Both utilities must be unmortgaged for the owner to collect the higher rate.
- No houses or hotels can be built on utilities.
- When a Chance card directs a player to the nearest utility, if owned, the player rolls the dice and pays 10 times the amount rolled (regardless of how many utilities the owner holds).

---

## 7. Card Decks

### 7.1 Chance Cards (16 cards)

The Chance deck is shuffled at game start. When a player lands on a Chance space (positions 7, 22, or 36), they draw the top card, follow its instructions, and return it face-down to the bottom of the deck (except "Get Out of Jail Free," which is kept until used or traded).

| # | Card Text | Effect |
|---|---|---|
| 1 | Advance to Boardwalk. | Move token to Boardwalk (position 39). |
| 2 | Advance to Go. (Collect $200) | Move token to GO; collect $200. |
| 3 | Advance to Illinois Avenue. If you pass Go, collect $200. | Move to Illinois Avenue (position 24); collect $200 if passing GO. |
| 4 | Advance to St. Charles Place. If you pass Go, collect $200. | Move to St. Charles Place (position 11); collect $200 if passing GO. |
| 5 | Advance to the nearest Railroad. If unowned, you may buy it from the Bank. If owned, pay owner twice the rental to which they are otherwise entitled. | Move forward to the nearest railroad; pay double the normal railroad rent if owned. |
| 6 | Advance to the nearest Railroad. If unowned, you may buy it from the Bank. If owned, pay owner twice the rental to which they are otherwise entitled. | (Duplicate of card 5.) |
| 7 | Advance token to nearest Utility. If unowned, you may buy it from the Bank. If owned, throw dice and pay owner a total ten times amount thrown. | Move forward to nearest utility; if owned, roll dice and pay 10x the roll. |
| 8 | Bank pays you dividend of $50. | Collect $50 from the Bank. |
| 9 | Get Out of Jail Free. | Keep this card until used or traded/sold. When used, return to bottom of deck. |
| 10 | Go Back 3 Spaces. | Move token backward 3 spaces; resolve the new space normally. |
| 11 | Go to Jail. Go directly to Jail, do not pass Go, do not collect $200. | Move token to Jail (position 10, "In Jail" side). Do not collect $200. |
| 12 | Make general repairs on all your property. For each house pay $25. For each hotel pay $100. | Pay the Bank: ($25 x number of houses) + ($100 x number of hotels). |
| 13 | Speeding fine $15. | Pay $15 to the Bank. |
| 14 | Take a trip to Reading Railroad. If you pass Go, collect $200. | Move to Reading Railroad (position 5); collect $200 if passing GO. |
| 15 | You have been elected Chairman of the Board. Pay each player $50. | Pay $50 to every other player. |
| 16 | Your building loan matures. Collect $150. | Collect $150 from the Bank. |

### 7.2 Community Chest Cards (16 cards)

The Community Chest deck is shuffled at game start. When a player lands on a Community Chest space (positions 2, 17, or 33), they draw the top card, follow its instructions, and return it face-down to the bottom of the deck (except "Get Out of Jail Free").

| # | Card Text | Effect |
|---|---|---|
| 1 | Advance to Go. (Collect $200) | Move token to GO; collect $200. |
| 2 | Bank error in your favor. Collect $200. | Collect $200 from the Bank. |
| 3 | Doctor's fee. Pay $50. | Pay $50 to the Bank. |
| 4 | From sale of stock you get $50. | Collect $50 from the Bank. |
| 5 | Get Out of Jail Free. | Keep this card until used or traded/sold. When used, return to bottom of deck. |
| 6 | Go to Jail. Go directly to jail, do not pass Go, do not collect $200. | Move token to Jail (position 10, "In Jail" side). Do not collect $200. |
| 7 | Holiday fund matures. Receive $100. | Collect $100 from the Bank. |
| 8 | Income tax refund. Collect $20. | Collect $20 from the Bank. |
| 9 | It is your birthday. Collect $10 from every player. | Every other player pays you $10. |
| 10 | Life insurance matures. Collect $100. | Collect $100 from the Bank. |
| 11 | Pay hospital fees of $100. | Pay $100 to the Bank. |
| 12 | Pay school fees of $50. | Pay $50 to the Bank. |
| 13 | Receive $25 consultancy fee. | Collect $25 from the Bank. |
| 14 | You are assessed for street repair. $40 per house. $115 per hotel. | Pay the Bank: ($40 x number of houses) + ($115 x number of hotels). |
| 15 | You have won second prize in a beauty contest. Collect $10. | Collect $10 from the Bank. |
| 16 | You inherit $100. | Collect $100 from the Bank. |

### 7.3 Card Deck Rules

- Each deck is shuffled independently at game start.
- After a card is drawn and resolved, it is placed face-down at the bottom of the deck.
- "Get Out of Jail Free" cards are held by the player and not returned until used or traded.
- If both GOOJF cards are held by players, the deck simply has 15 cards cycling.
- Movement cards that advance the player past GO award the $200 GO salary.
- Movement cards that send the player to Jail do NOT let the player collect $200, even if they "pass" GO en route.

---

## 8. Dice and Movement Rules

### 8.1 Standard Dice

Two six-sided dice (2d6) are rolled at the start of each turn. The player moves their token forward (clockwise) by the sum of both dice.

### 8.2 Doubles

- If both dice show the same number ("doubles"), the player completes their turn for the space they landed on and then rolls again for an additional turn.
- If the player rolls doubles a second consecutive time, they again complete the action and roll once more.
- If the player rolls doubles a **third consecutive time**, they do not move. Instead, they are sent directly to Jail ("speeding"). Their turn ends immediately.

### 8.3 Movement Resolution Order

1. Player rolls dice.
2. Check for third consecutive doubles -> if so, go to Jail; turn ends.
3. Move token forward by the dice sum.
4. If the player passes or lands on GO, collect $200.
5. Resolve the space landed on (see Section 8.4).
6. If doubles were rolled (first or second consecutive), return to step 1.
7. Turn ends; play passes to the next player.

### 8.4 Space Resolution

| Space Type | Resolution |
|---|---|
| Unowned Property | Player may buy at listed price. If declined, property goes to auction (see Section 13). |
| Owned Property (unmortgaged) | Player pays rent to the owner per the deed card or rent schedule. |
| Owned Property (mortgaged) | No rent is due. |
| Own Property | No action required. |
| Chance / Community Chest | Draw the top card and follow its instructions. |
| Income Tax | Pay $200 to the Bank. |
| Luxury Tax | Pay $100 to the Bank. |
| GO | Collect $200 (already collected when passing; landing awards the same $200, not a double payment). |
| Jail / Just Visiting | If arriving via normal movement, the player is "Just Visiting." No penalty. |
| Free Parking | No action. Player's turn continues normally. |
| Go To Jail | Player is sent to Jail immediately (see Section 9). |

### 8.5 Passing GO

- A player collects exactly $200 each time their token lands on or passes over GO while moving in the forward direction.
- Cards that send a player directly to Jail explicitly state "do not pass Go, do not collect $200" -- no salary is collected.
- Cards that advance a player to a specific space (e.g., "Advance to St. Charles Place") do allow collecting $200 if the path of movement crosses GO.
- A player collects only $200 for passing GO, regardless of whether they land on it. There is no bonus for an exact landing.

---

## 9. Jail System

### 9.1 Three Ways to Go to Jail

1. **Landing on "Go To Jail" (position 30):** The player's token is moved directly to Jail. They do not pass GO and do not collect $200.
2. **Drawing a "Go to Jail" card:** From either the Chance or Community Chest deck. Same effect -- go directly to Jail, do not pass GO.
3. **Rolling doubles three times in a row:** On the third consecutive doubles roll, the player does not move. They are sent directly to Jail and their turn ends.

### 9.2 While in Jail

- The player's token is placed in the "In Jail" section of the Jail space.
- The player **cannot move** while in Jail.
- The player **can** still collect rent, buy/sell houses and hotels, trade properties, participate in auctions, and mortgage/unmortgage properties.
- A player may stay in Jail for up to 3 turns.

### 9.3 Three Ways to Get Out of Jail

1. **Pay $50 fine:** At the start of the player's turn (before rolling), they may pay $50 to the Bank. They then roll the dice and move normally. This can be done on any of the three jail turns.
2. **Use a "Get Out of Jail Free" card:** At the start of the player's turn (before rolling), the player presents the card. The card is returned to the bottom of the appropriate deck. The player then rolls and moves normally.
3. **Roll doubles:** The player rolls the dice. If they roll doubles, they are released and move forward the number of spaces shown. They do **not** get an extra turn for these doubles. If they do not roll doubles, their turn ends (on the first and second attempts). On the third attempt, if they fail to roll doubles, they **must** pay the $50 fine and then move forward the number shown on their non-doubles roll.

### 9.4 Jail Strategy Note

Players are not required to try to leave Jail immediately. Staying in Jail can be strategically advantageous later in the game (avoiding landing on developed properties). Early in the game, leaving Jail quickly is generally preferred.

---

## 10. Building System (Houses and Hotels)

### 10.1 Prerequisites for Building

- The player must own **all properties** in a color group (a complete monopoly).
- None of the properties in the color group may be mortgaged.
- Building can only occur on the player's turn (between turns by convention, but most digital implementations allow building at any point during one's own turn, or between any two players' turns).

### 10.2 Even Building Rule

Houses must be built evenly across all properties in a color group:

- A player cannot place a second house on any property until every property in the group has at least one house.
- A player cannot place a third house until every property has at least two, and so on.
- The maximum difference in house count between any two properties in the same color group is **1**.

### 10.3 Hotel Rules

- A hotel may be placed on a property only after it has **4 houses**.
- When a hotel is built, the 4 houses are returned to the Bank, and the hotel replaces them.
- The cost of a hotel is the same as one house in that color group (the total investment for a hotel is: 4 houses + 1 hotel cost = 5 x house cost).
- Maximum development per property: **1 hotel** (no further building is possible).

### 10.4 Selling Buildings

- Houses and hotels are sold back to the Bank at **half their purchase price**.
- Buildings must be sold evenly (mirroring the even building rule). Hotels must be broken down to 4 houses before any houses can be removed unevenly.
- If there are not enough houses in the Bank supply to break a hotel down to 4 houses, the hotel must be sold outright (at half the hotel cost + half the cost of 4 houses = half total investment).

### 10.5 Building Supply Limits

| Component | Total Supply |
|---|---|
| Houses | 32 |
| Hotels | 12 |

- If the Bank has no houses remaining, players cannot build houses (even if they have the money and a monopoly).
- If multiple players want to buy buildings and the supply is insufficient, the available houses/hotels are **auctioned** to the highest bidder (minimum bid: $1). Each house/hotel is auctioned individually.
- A player may choose not to upgrade to hotels in order to create a **housing shortage**, preventing opponents from building.

---

## 11. Banking and Economy

### 11.1 Starting Money

Each player receives **$1,500** at the start of the game, distributed as follows:

| Denomination | Quantity | Subtotal |
|---|---|---|
| $500 | 2 | $1,000 |
| $100 | 2 | $200 |
| $50 | 1 | $50 |
| $20 | 6 | $120 |
| $10 | 5 | $50 |
| $5 | 5 | $25 |
| $1 | 5 | $5 |
| **Total** | **26 bills** | **$1,500** |

### 11.2 Bank Money Supply

The game includes **$20,580** total in play money (30 of each denomination). However, the Bank can never run out of money in the official rules. If the Bank's cash runs out, the Banker may issue IOUs or supplementary paper to cover obligations.

### 11.3 Bill Denominations

| Denomination | Color (classic) | Count in Box |
|---|---|---|
| $1 | White | 30 |
| $5 | Pink | 30 |
| $10 | Yellow | 30 |
| $20 | Green | 30 |
| $50 | Blue | 30 |
| $100 | Beige | 30 |
| $500 | Orange | 30 |

### 11.4 Bank Responsibilities

The Bank:
- Holds all Title Deed cards, houses, and hotels not yet purchased.
- Pays salaries (GO), card bonuses, and other payouts.
- Collects taxes, fines, building purchases, and interest.
- Sells and auctions properties.
- Sells houses and hotels.
- Manages mortgages and loans (at the mortgage value, repaid at mortgage + 10% interest).
- **Never goes bankrupt.** The Bank has unlimited funds.

---

## 12. Mortgage and Unmortgage Rules

### 12.1 Mortgaging a Property

- Any property can be mortgaged to the Bank to raise cash.
- The mortgage value is printed on the deed card (always half the purchase price).
- **Before mortgaging**, all buildings on the entire color group must be sold back to the Bank (at half price).
- A mortgaged property generates **no rent** if an opponent lands on it.
- The property remains owned by the player and can be traded.
- A mortgaged property's Title Deed card is placed face-down to indicate its status.

### 12.2 Unmortgaging (Lifting a Mortgage)

- To unmortgage, the owner pays the Bank the **mortgage value + 10% interest** (rounded to the nearest dollar if necessary).
- Example: Mediterranean Avenue mortgage = $30. To unmortgage: $30 + $3 = $33.

### 12.3 Mortgaged Property in Trades

When a mortgaged property is transferred to a new owner (via trade or bankruptcy):
- The new owner must immediately pay the Bank **10% of the mortgage value** as interest.
- The new owner may then choose to:
  - **Lift the mortgage immediately:** Pay the mortgage value + 10% interest (but since 10% was already paid at transfer, only the mortgage principal is additionally owed -- effectively paying mortgage + 10% total).
  - **Keep it mortgaged:** Pay only the 10% transfer fee now. Later, to unmortgage, they must pay the full mortgage value + an additional 10% interest (making the total cost: 10% at transfer + mortgage value + 10% at unmortgage).

---

## 13. Trading Rules

### 13.1 What Can Be Traded

Players may trade the following between themselves at any mutually agreed-upon terms:

| Tradeable | Notes |
|---|---|
| Cash | Any amount. |
| Property (Title Deeds) | Streets, railroads, and utilities. |
| Get Out of Jail Free cards | Either the Chance or Community Chest version. |

### 13.2 Trading Restrictions

- **Buildings cannot be traded.** All houses and hotels on any property in a color group must be sold back to the Bank before any property in that group can be traded.
- **Loans between players are not allowed.** No player may give or lend money to another player outside of an obligation (rent, card effect, etc.) or a trade.
- **Gifts are not permitted.** All trades must involve consideration from both parties (in the strictest tournament interpretation).
- Trades may occur during any player's turn.
- Mortgaged properties may be traded (the new owner pays the 10% transfer fee; see Section 12.3).
- Multi-player trades are allowed (involving 3+ players swapping assets simultaneously).

---

## 14. Auction Rules

### 14.1 When Auctions Occur

An auction is triggered whenever:
- A player lands on an unowned property and **declines to purchase** it at the listed price.
- A building shortage requires allocation of limited houses/hotels.

### 14.2 Property Auction Procedure

1. The Banker announces the property for auction.
2. **All players** may bid, including the player who declined to buy.
3. Bidding starts at any amount (minimum $1).
4. Players bid in turn order or openly (depending on house convention; digital version should use sequential bidding or timer-based open bidding).
5. The highest bidder wins and pays their bid amount to the Bank, receiving the Title Deed.
6. There is **no minimum bid requirement** relative to the property's listed price. A property may be auctioned for as little as $1.
7. If no player bids, the property remains unowned (returned to the Bank).

### 14.3 Building Shortage Auction

When multiple players want to buy houses/hotels and the Bank supply is insufficient:
1. The available buildings are auctioned one at a time.
2. Bidding follows the same open-bid procedure.
3. The winning bidder pays their bid to the Bank and receives the building.

---

## 15. Bankruptcy and Elimination

### 15.1 When Bankruptcy Occurs

A player is **bankrupt** when they owe more money than they can raise through:
- Selling buildings back to the Bank (at half price).
- Mortgaging properties.
- Trading assets with other players.

### 15.2 Bankruptcy to Another Player

If a player goes bankrupt due to rent, card effects, or any debt owed to another player:
1. The bankrupt player turns over **all assets** to the creditor: cash, Title Deeds, and Get Out of Jail Free cards.
2. Any mortgaged properties are transferred to the creditor.
3. The creditor must immediately pay the Bank **10% of the mortgage value** on each transferred mortgaged property.
4. The creditor may then choose to unmortgage immediately (paying the mortgage principal) or keep the property mortgaged (and pay the mortgage + 10% interest later).
5. The bankrupt player is eliminated from the game.

### 15.3 Bankruptcy to the Bank

If a player goes bankrupt due to taxes, fines, or other Bank obligations:
1. All buildings are returned to the Bank.
2. All properties are **auctioned off immediately** to the remaining players (one at a time).
3. Mortgages on auctioned properties are lifted (the properties are auctioned unmortgaged).
4. All cash is returned to the Bank.
5. Get Out of Jail Free cards are returned to the bottom of their respective decks.
6. The bankrupt player is eliminated from the game.

### 15.4 Elimination

- An eliminated player's token is removed from the board.
- They take no further turns and have no further role in the game.

---

## 16. Win Condition

The last player remaining after all other players have been eliminated by bankruptcy **wins the game**.

### 16.1 Optional Timed Game Variant

If players agree before starting to play a timed game:
- A fixed time limit is set (e.g., 60, 90, or 120 minutes).
- When time expires, the current turn is completed.
- Each player calculates their total net worth:
  - Cash on hand.
  - Properties owned at their printed (purchase) price.
  - Mortgaged properties at half their printed price (the mortgage value).
  - Houses at purchase price.
  - Hotels at purchase price (hotel cost + 4 house costs).
- The player with the highest net worth wins.

---

## 17. Speed Die Variant (Optional)

The Speed Die is a third die with special faces, included in many modern Monopoly editions since 2007.

### 17.1 Speed Die Faces

| Face | Count | Symbol |
|---|---|---|
| 1 pip | 1 | Numeral |
| 2 pips | 1 | Numeral |
| 3 pips | 1 | Numeral |
| Mr. Monopoly | 2 | Top hat icon |
| Bus | 1 | Bus icon |

### 17.2 Speed Die Rules

The Speed Die is rolled simultaneously with the two standard dice. After all players have completed one full circuit of the board, the Speed Die takes effect:

| Speed Die Result | Effect |
|---|---|
| **Number (1, 2, or 3)** | Add the Speed Die value to the total of the two standard dice. Move that combined total. |
| **Mr. Monopoly** | Move according to the two standard dice only (Mr. Monopoly = 0 for movement). After resolving the space landed on, advance to the **next unowned property** and buy it or auction it. If all properties are owned, advance to the next property on which you owe rent. |
| **Bus** | Move the value of **either** one standard die, the **other** standard die, or the **sum** of both (player's choice). |

### 17.3 Triples

If all three dice show the same number (triple), the player may move to **any space on the board** of their choosing.

### 17.4 Doubles with Speed Die

Doubles are still determined by the two standard white dice only. The Speed Die does not count toward doubles.

---

## 18. Complete Game Component List

| Component | Quantity |
|---|---|
| Game board | 1 |
| Standard six-sided dice | 2 |
| Speed Die (optional) | 1 |
| Player tokens | 8 (classic tokens: Scottie dog, top hat, car, iron/cat, thimble/T-Rex, boot, wheelbarrow/penguin, battleship/rubber duck -- varies by edition) |
| Title Deed cards | 28 (22 streets + 4 railroads + 2 utilities) |
| Chance cards | 16 |
| Community Chest cards | 16 |
| Houses (green) | 32 |
| Hotels (red) | 12 |
| Money bills | 210 (30 of each of 7 denominations) |
| Banker's tray | 1 |

---

## 19. UI Layout (Digital Version)

### 19.1 Main Game Screen

```
+---------------------------------------------------------------+
|                        TOP SIDE (20-30)                       |
|  [Free Parking] [KY] [CH] [IN] [IL] [B&O] [AT] [VE] [WW]   |
|  [MG] [Go To Jail]                                           |
+-------+-----------------------------------------------+-------+
|  LEFT |                                               | RIGHT |
| SIDE  |           CENTER AREA                         | SIDE  |
| (10-20|                                               |(30-40)|
|       |   - Active Player Info Panel                  |       |
| [Jail]|   - Dice Display (animated)                   |[GtJ]  |
| [StC] |   - Property Card Popup                       |[Pac]  |
| [EC]  |   - Trade Interface (overlay)                 |[NC]   |
| [Sta] |   - Auction Interface (overlay)               |[CC]   |
| [VA]  |   - Card Draw Animation                       |[PA]   |
| [PRR] |   - Player Token Positions                    |[SL]   |
| [StJ] |                                               |[CH]   |
| [CC]  |   PLAYER PANELS (around center):              |[PP]   |
| [TN]  |   - Name, Token, Cash                         |[LT]   |
| [NY]  |   - Property Thumbnails                       |[BW]   |
| [FP]  |   - GOOJF card indicator                      |       |
+-------+-----------------------------------------------+-------+
|                       BOTTOM SIDE (0-10)                      |
|  [GO] [Med] [CC] [Bal] [IT] [RR] [Ori] [CH] [VT] [CT]       |
|  [Jail/JV]                                                    |
+---------------------------------------------------------------+
|  [Roll Dice] [Build] [Mortgage] [Trade] [End Turn]            |
+---------------------------------------------------------------+
```

### 19.2 UI Elements

| Element | Description |
|---|---|
| **Board** | Central square board with all 40 spaces rendered with correct colors, names, and icons. Player tokens are visible on the board at their current positions. |
| **Player Panel** | Displays each player's: name/avatar, token icon, current cash, owned properties (color-coded thumbnails), number of houses/hotels, GOOJF card count, and jail status. |
| **Dice Display** | Animated 3D or 2D dice roll with result clearly shown. Speed Die shown alongside if enabled. |
| **Property Card Popup** | On hover/click of any property space: shows the full Title Deed with all rent levels, purchase price, mortgage value, house/hotel cost, current owner, and development status. |
| **Action Bar** | Contextual buttons: Roll Dice, Buy Property, Auction, Build Houses/Hotels, Sell Buildings, Mortgage, Unmortgage, Trade, Use GOOJF Card, Pay Jail Fine, End Turn. Buttons are enabled/disabled based on game state. |
| **Trade Interface** | Overlay/modal with two player panels for asset exchange: cash slider, property selection checkboxes, GOOJF card toggle, confirm/cancel. |
| **Auction Interface** | Overlay showing the property being auctioned, current high bid, high bidder, and bid input for each player with a timer. |
| **Card Display** | Animated card draw showing card face with text and icon. Dismiss on click/timer. |
| **Chat/Log** | Scrollable game log showing all actions, transactions, and events in chronological order. |
| **Bank Display** | Shows remaining houses (out of 32) and hotels (out of 12) in the Bank supply. |
| **Jail Indicator** | Visual indicator on the board and player panel when a player is "In Jail" vs. "Just Visiting." |

### 19.3 Color Palette

| Element | Hex Color |
|---|---|
| Board background | `#C8E6C0` (light green) |
| Brown group | `#8B4513` |
| Light Blue group | `#AAD8E6` |
| Pink group | `#D93A96` |
| Orange group | `#F7922E` |
| Red group | `#ED1B24` |
| Yellow group | `#FEF200` |
| Green group | `#1FB25A` |
| Dark Blue group | `#0036AB` |
| Railroad space | `#000000` (black text on white) |
| Utility space | `#FFFFFF` (white with icon) |
| GO space | `#FF0000` (red arrow) |
| Free Parking | `#FF6347` (red/orange) |
| Jail | `#F08000` (orange) |
| Chance | `#FF6600` (orange with "?") |
| Community Chest | `#0099FF` (blue with chest icon) |
| Tax spaces | `#808080` (gray) |

---

## 20. Audio Design

### 20.1 Music

| Track | Context | Style |
|---|---|---|
| Main Menu Theme | Title screen, lobby | Jazzy, upbeat big-band instrumental; evokes 1930s Atlantic City. |
| In-Game Background | During normal gameplay | Light, looping ragtime/swing; low volume, non-intrusive. |
| Tension Theme | When a player is near bankruptcy or during auctions | Slightly faster tempo, minor-key variation of the main theme. |
| Victory Fanfare | When a player wins | Triumphant brass and strings crescendo. |
| Elimination Sting | When a player goes bankrupt | Brief descending trombone "wah-wah." |

### 20.2 Sound Effects

| Event | Sound |
|---|---|
| Dice roll | Rattling dice on wood surface, two distinct impacts. |
| Token movement | Light tap-tap-tap for each space traversed (scaled to movement speed). |
| Land on property | Soft "thud" arrival sound. |
| Purchase property | Cash register "ka-ching." |
| Pay rent | Coin clinking / cash shuffling sound. |
| Build house | Hammer tap / construction sound. |
| Build hotel | Larger construction sound with a celebratory chime. |
| Sell building | Demolition / deconstruction sound. |
| Draw Chance card | Bright, curious ascending chime (mystery). |
| Draw Community Chest card | Warm, pleasant ascending chime. |
| Go to Jail | Jail cell door slamming shut. |
| Get Out of Jail | Key turning in lock, door creaking open. |
| Pass GO / Collect $200 | Cheerful cash register with coin shower. |
| Mortgage property | Paper stamping / bureaucratic thud. |
| Unmortgage property | Paper tearing / stamp removal. |
| Auction start | Gavel bang. |
| Auction bid | Quick ascending "bid" chirp. |
| Auction won | Gavel bang (final) + brief applause. |
| Trade proposed | Notification chime. |
| Trade accepted | Handshake sound / pleasant confirmation. |
| Trade declined | Brief negative buzz. |
| Bankruptcy | Dramatic descending tone, cash register emptying. |
| Victory | Extended fanfare with crowd cheering. |
| Doubles rolled | Bonus chime layered on dice sound. |
| Third doubles (speeding) | Police siren snippet. |
| Tax payment | Sad trombone / reluctant coin sound. |
| Timer warning (auction) | Ticking clock, accelerating. |
| Button click (UI) | Soft click / pop. |
| Turn start notification | Gentle bell / chime. |

### 20.3 Audio Settings

| Setting | Default | Range |
|---|---|---|
| Master Volume | 80% | 0 -- 100% |
| Music Volume | 60% | 0 -- 100% |
| SFX Volume | 80% | 0 -- 100% |
| UI Sounds | On | On / Off |
| Dice Roll Sound | On | On / Off |

---

## 21. Miscellaneous Official Rules and Edge Cases

### 21.1 Rent Collection

- **Rent must be demanded.** If a player lands on an owned property and the owner does not ask for rent before the next player rolls the dice, the rent is forfeited. (In digital implementation, rent is typically collected automatically.)
- Rent cannot be collected on mortgaged properties.
- Rent cannot be collected while the owner is in Jail (common misconception -- **this is FALSE in official rules**; owners in Jail may still collect rent).

### 21.2 Property Ownership

- Once a property is bought or auctioned, it remains owned for the rest of the game (unless the owner goes bankrupt, in which case it is transferred or re-auctioned).
- A player may not refuse to pay rent if they have the assets to cover it.
- A player cannot choose to go bankrupt voluntarily if they can pay their debts.

### 21.3 Money Obligations

- If a player cannot pay a debt, they must sell buildings and mortgage properties to raise cash.
- Buildings are sold at half price; mortgages provide the mortgage value.
- If still unable to pay after liquidating all possible assets, the player declares bankruptcy.

### 21.4 Immunity Deals

- The official rules do not address immunity deals (agreeing not to charge rent in exchange for trade concessions). Tournament rules typically disallow such arrangements. Digital implementations should either disallow them or flag them as optional house rules.

### 21.5 Landing on GO

- Landing on GO collects exactly $200, the same as passing over it. There is no double payment for an exact landing (this is a common house rule, not an official rule).

### 21.6 Multiple Properties from One Turn

- If a card moves a player to a property, that property is subject to normal landing rules (buy, auction, or pay rent).
- A player could potentially interact with multiple spaces in one turn (e.g., rolling doubles, landing on a Chance card that moves them, then rolling again).

### 21.7 Free Parking

- **Official rules:** Absolutely nothing happens. No money is collected.
- The common "house rule" of placing tax/fine money on Free Parking for collection is **not** in the official rulebook and significantly lengthens the game.

---

## 22. Quick Reference: Property Group Summary

| Color | Count | Price Range | House Cost | Max Rent (Hotel) | Total to Monopolize | Total to Fully Develop |
|---|---|---|---|---|---|---|
| Brown | 2 | $60 -- $60 | $50 | $450 | $120 | $120 + $500 = $620 |
| Light Blue | 3 | $100 -- $120 | $50 | $600 | $320 | $320 + $750 = $1,070 |
| Pink | 3 | $140 -- $160 | $100 | $900 | $440 | $440 + $1,500 = $1,940 |
| Orange | 3 | $180 -- $200 | $100 | $1,000 | $560 | $560 + $1,500 = $2,060 |
| Red | 3 | $220 -- $240 | $150 | $1,100 | $680 | $680 + $2,250 = $2,930 |
| Yellow | 3 | $260 -- $280 | $150 | $1,200 | $800 | $800 + $2,250 = $3,050 |
| Green | 3 | $300 -- $320 | $200 | $1,400 | $920 | $920 + $3,000 = $3,920 |
| Dark Blue | 2 | $350 -- $400 | $200 | $2,000 | $750 | $750 + $2,000 = $2,750 |
| Railroads | 4 | $200 each | -- | $200 (all 4) | $800 | N/A |
| Utilities | 2 | $150 each | -- | 10x dice | $300 | N/A |

---

## 23. Player Setup and Turn Order

### 23.1 Setup

1. Place the board on a flat surface.
2. Each player selects a token and places it on GO.
3. Shuffle the Chance deck and place it face-down on the board.
4. Shuffle the Community Chest deck and place it face-down on the board.
5. Place all houses and hotels near the board (the Bank supply).
6. Select one player as the Banker. (The Banker may also play; they must keep personal funds separate from Bank funds.)
7. The Banker distributes $1,500 to each player.
8. Place all Title Deed cards near the board (or in the Banker's tray).

### 23.2 Determining First Player

Each player rolls both dice. The player with the highest total goes first. In case of a tie, the tied players re-roll. Play proceeds clockwise.

### 23.3 Turn Structure

1. **(Optional) Pre-roll actions:** Build houses/hotels, trade, mortgage/unmortgage, pay jail fine, use GOOJF card.
2. **Roll dice** and move.
3. **Resolve space** (buy, auction, pay rent, draw card, pay tax, go to jail, etc.).
4. **(Optional) Post-landing actions:** Build, trade, mortgage/unmortgage.
5. **Check for doubles:** If doubles, repeat from step 2 (unless third consecutive doubles).
6. **End turn.** Play passes clockwise.

---

## 24. Digital Implementation Notes

### 24.1 AI Opponents

| Difficulty | Behavior |
|---|---|
| Easy | Buys properties randomly (~50% chance), never trades aggressively, builds only when cash > 2x building cost, overbids in auctions. |
| Medium | Buys all properties it can afford, makes reasonable trades, builds strategically on high-traffic groups (orange, red), bids intelligently in auctions. |
| Hard | Employs advanced strategy: prioritizes orange/red monopolies, creates housing shortages, trades to complete monopolies, calculates expected rent income vs. building cost, exploits auction rules, manages cash reserves carefully. |

### 24.2 Network Multiplayer Considerations

| Feature | Specification |
|---|---|
| Max players per game | 8 |
| Turn timer | Configurable (30s, 60s, 90s, 120s, unlimited). Default: 60s. |
| Trade timer | Configurable. Default: 120s for negotiation. |
| Auction timer | Configurable. Default: 15s per bid round. |
| Disconnect handling | Player's turn is auto-skipped; if disconnected for > 2 consecutive turns, player is eliminated and properties are auctioned. |
| Spectator mode | Allowed; spectators see all public information but not other players' cash (optional fog-of-war). |

### 24.3 Save/Load

- Full game state is serializable: board state, player states (cash, properties, buildings, jail status, position, GOOJF cards), deck states (card order), turn order, doubles count, and current turn phase.
- Supports save at any point during a turn.
- Autosave after each completed turn.
