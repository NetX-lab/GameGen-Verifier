# Ticket to Ride (USA) -- Complete Game Specification

> A comprehensive specification for faithfully recreating the original Ticket to Ride board game (Days of Wonder, 2004), designed by Alan R. Moon. This document covers the USA map edition -- the base game -- including every route, destination ticket, card, rule, and scoring mechanic required for a digital implementation.

---

## Table of Contents

1. [Game Overview](#1-game-overview)
2. [Technical Foundation](#2-technical-foundation)
3. [Board Map -- Cities](#3-board-map--cities)
4. [Board Map -- Routes](#4-board-map--routes)
5. [Train Car Card System](#5-train-car-card-system)
6. [Destination Ticket System](#6-destination-ticket-system)
7. [Game Setup](#7-game-setup)
8. [Turn Actions](#8-turn-actions)
9. [Route Claiming Rules](#9-route-claiming-rules)
10. [Card Display and Drawing Rules](#10-card-display-and-drawing-rules)
11. [Scoring System](#11-scoring-system)
12. [Longest Continuous Path Bonus](#12-longest-continuous-path-bonus)
13. [Game End and Final Scoring](#13-game-end-and-final-scoring)
14. [Player Counts and Double Routes](#14-player-counts-and-double-routes)
15. [UI Layout](#15-ui-layout)
16. [Audio Design](#16-audio-design)
17. [AI Opponents](#17-ai-opponents)
18. [QA Acceptance Matrix](#18-qa-acceptance-matrix)

---

## 1. Game Overview

- **Title**: Ticket to Ride
- **Designer**: Alan R. Moon
- **Publisher**: Days of Wonder (2004)
- **Genre**: Board Game / Strategy / Route-Building / Set Collection
- **Players**: 2--5
- **Recommended Age**: 8+
- **Session Length**: 30--60 minutes
- **Core Fantasy**: Compete with rival railroad barons to claim railway routes across North America, connecting distant cities to fulfill secret destination tickets while racing to build the longest continuous rail network.
- **Primary Mechanics**: Set collection (train car cards), route claiming (place trains on board), hidden objectives (destination tickets), hand management.
- **Win Condition**: The player with the most points at the end of the game wins. Points come from claimed routes, completed destination tickets, and the longest continuous path bonus. Incomplete destination tickets subtract points.
- **Historical Note**: Ticket to Ride won the 2004 Spiel des Jahres (German Game of the Year), the most prestigious award in board gaming. It has sold over 10 million copies worldwide and spawned numerous expansions and map variants.

---

## 2. Technical Foundation

### 2.1 Digital Recreation Target

| Property | Value |
|----------|-------|
| Minimum Resolution | 1280 x 720 (16:9) |
| Recommended Resolution | 1920 x 1080 |
| Frame Rate | 60 FPS |
| Input Methods | Mouse + keyboard; touch (tablet); gamepad |
| Platform Targets | Desktop (Windows/macOS/Linux), Mobile (iOS/Android), Web |
| Network | Local play (hot-seat), Online multiplayer (client-server or P2P) |
| Determinism | All game logic must be deterministic given the same RNG seed and input sequence |

### 2.2 Game State Architecture

The game state consists of:

| Component | Type | Description |
|-----------|------|-------------|
| `board` | Graph | 36 city nodes with 100 route edges (counting each double route separately) |
| `trainCardDeck` | Stack | Draw pile of train car cards |
| `trainCardDiscard` | Stack | Discard pile; reshuffled when draw pile exhausted |
| `faceUpCards` | Array[5] | Five visible train car cards available for drawing |
| `destinationDeck` | Stack | Draw pile of destination ticket cards |
| `players[]` | Array | Per-player state (see below) |
| `currentPlayer` | Index | Whose turn it is |
| `turnPhase` | Enum | `CHOOSE_ACTION`, `DRAWING_SECOND_CARD`, `CHOOSING_TICKETS` |
| `gamePhase` | Enum | `SETUP`, `PLAYING`, `FINAL_ROUND`, `GAME_OVER` |
| `lastRoundTrigger` | Index | Player who triggered final round (null until triggered) |
| `longestPathHolder` | Index[] | Player(s) currently holding longest path bonus |

**Per-Player State:**

| Field | Type | Description |
|-------|------|-------------|
| `hand` | Map<Color, Count> | Train car cards in hand |
| `trainsRemaining` | Integer | Starts at 45; decremented when routes are claimed |
| `claimedRoutes` | List<Route> | Routes this player has claimed |
| `destinationTickets` | List<Ticket> | Secret destination ticket cards held |
| `score` | Integer | Running point total (updated on route claim) |
| `playerColor` | Enum | Blue, Red, Green, Yellow, or Black |

### 2.3 Random Number Generation

| Event | Method |
|-------|--------|
| Shuffling train card deck | Fisher-Yates shuffle with seeded PRNG |
| Shuffling destination deck | Fisher-Yates shuffle with seeded PRNG |
| Initial deal | Draw from top of shuffled deck |
| Reshuffle discard | Fisher-Yates shuffle of discard pile |

### 2.4 Game Loop (Per Turn)

```
1. Display current player indicator
2. Player selects one of three actions:
   a. Draw Train Car Cards
   b. Claim a Route
   c. Draw Destination Tickets
3. Execute chosen action (with sub-steps as needed)
4. Check game-end trigger: if currentPlayer.trainsRemaining <= 2
      AND lastRoundTrigger == null:
      set lastRoundTrigger = currentPlayer
5. Advance to next player (clockwise)
6. If lastRoundTrigger != null AND all players have had one final turn:
      transition to GAME_OVER; execute final scoring
```

---

## 3. Board Map -- Cities

The board depicts a stylized map of North America with **36 cities** connected by railway routes. The cities span from Vancouver and Seattle in the northwest to Miami in the southeast.

### 3.1 Complete City List

| # | City | Region | Country |
|---|------|--------|---------|
| 1 | Atlanta | Southeast | USA |
| 2 | Boston | Northeast | USA |
| 3 | Calgary | Northwest | Canada |
| 4 | Charleston | Southeast | USA |
| 5 | Chicago | Midwest | USA |
| 6 | Dallas | South Central | USA |
| 7 | Denver | Mountain West | USA |
| 8 | Duluth | Midwest | USA |
| 9 | El Paso | Southwest | USA |
| 10 | Helena | Mountain West | USA |
| 11 | Houston | South Central | USA |
| 12 | Kansas City | Midwest | USA |
| 13 | Las Vegas | Southwest | USA |
| 14 | Little Rock | South Central | USA |
| 15 | Los Angeles | West | USA |
| 16 | Miami | Southeast | USA |
| 17 | Montreal | Northeast | Canada |
| 18 | Nashville | Southeast | USA |
| 19 | New Orleans | South | USA |
| 20 | New York | Northeast | USA |
| 21 | Oklahoma City | South Central | USA |
| 22 | Omaha | Midwest | USA |
| 23 | Phoenix | Southwest | USA |
| 24 | Pittsburgh | Northeast | USA |
| 25 | Portland | Northwest | USA |
| 26 | Raleigh | Southeast | USA |
| 27 | Saint Louis | Midwest | USA |
| 28 | Salt Lake City | Mountain West | USA |
| 29 | San Francisco | West | USA |
| 30 | Santa Fe | Southwest | USA |
| 31 | Sault St. Marie | Midwest | USA/Canada |
| 32 | Seattle | Northwest | USA |
| 33 | Toronto | Northeast | Canada |
| 34 | Vancouver | Northwest | Canada |
| 35 | Washington | Northeast | USA |
| 36 | Winnipeg | North Central | Canada |

### 3.2 Approximate City Coordinates (Normalized 0.0--1.0)

For rendering the board map, use the following normalized positions (origin at bottom-left, X increases rightward, Y increases upward):

| City | X | Y |
|------|---|---|
| Atlanta | 0.781 | 0.367 |
| Boston | 0.945 | 0.794 |
| Calgary | 0.235 | 0.871 |
| Charleston | 0.872 | 0.356 |
| Chicago | 0.684 | 0.596 |
| Dallas | 0.555 | 0.221 |
| Denver | 0.390 | 0.451 |
| Duluth | 0.564 | 0.686 |
| El Paso | 0.378 | 0.185 |
| Helena | 0.333 | 0.677 |
| Houston | 0.595 | 0.163 |
| Kansas City | 0.555 | 0.477 |
| Las Vegas | 0.208 | 0.335 |
| Little Rock | 0.623 | 0.344 |
| Los Angeles | 0.145 | 0.250 |
| Miami | 0.904 | 0.125 |
| Montreal | 0.875 | 0.878 |
| Nashville | 0.731 | 0.419 |
| New Orleans | 0.686 | 0.180 |
| New York | 0.894 | 0.684 |
| Oklahoma City | 0.535 | 0.350 |
| Omaha | 0.535 | 0.551 |
| Phoenix | 0.262 | 0.240 |
| Pittsburgh | 0.812 | 0.618 |
| Portland | 0.082 | 0.691 |
| Raleigh | 0.845 | 0.452 |
| Saint Louis | 0.638 | 0.475 |
| Salt Lake City | 0.263 | 0.497 |
| San Francisco | 0.068 | 0.402 |
| Santa Fe | 0.383 | 0.318 |
| Sault St. Marie | 0.688 | 0.783 |
| Seattle | 0.104 | 0.767 |
| Toronto | 0.795 | 0.752 |
| Vancouver | 0.108 | 0.846 |
| Washington | 0.902 | 0.551 |
| Winnipeg | 0.453 | 0.855 |

---

## 4. Board Map -- Routes

There are **78 unique city-pair connections** on the board, but several of these are **double routes** (two parallel routes between the same pair of cities), yielding a total of **100 individual route segments** when each parallel route is counted separately.

### 4.1 Route Color Legend

Routes are colored to indicate which train car cards are required to claim them:

| Code | Color | Hex Code | Card Required |
|------|-------|----------|---------------|
| Gray | Gray | `#8E8E8E` | Any single color (player's choice) |
| Red | Red | `#D32F2F` | Red cards |
| Orange | Orange | `#F57C00` | Orange cards |
| Yellow | Yellow | `#FBC02D` | Yellow cards |
| Green | Green | `#388E3C` | Green cards |
| Blue | Blue | `#1976D2` | Blue cards |
| Pink | Pink | `#E91E90` | Pink cards |
| White | White | `#F5F5F5` | White cards |
| Black | Black | `#212121` | Black cards |

Note: The physical game uses "pink" (sometimes called "purple") as one of the 8 card/route colors. Throughout this document, "Pink" refers to this color.

### 4.2 Complete Route Table

Each row represents one claimable route segment. Double routes appear as two rows for the same city pair with different colors. The "Double" column marks routes that have a parallel counterpart.

| # | City A | City B | Length | Color | Points | Double? |
|---|--------|--------|--------|-------|--------|---------|
| 1 | Vancouver | Calgary | 3 | Gray | 4 | No |
| 2 | Vancouver | Seattle | 1 | Gray | 1 | Yes |
| 3 | Vancouver | Seattle | 1 | Gray | 1 | Yes |
| 4 | Seattle | Calgary | 4 | Gray | 7 | No |
| 5 | Seattle | Helena | 6 | Yellow | 15 | No |
| 6 | Seattle | Portland | 1 | Gray | 1 | Yes |
| 7 | Seattle | Portland | 1 | Gray | 1 | Yes |
| 8 | Portland | Salt Lake City | 6 | Blue | 15 | No |
| 9 | Portland | San Francisco | 5 | Green | 10 | Yes |
| 10 | Portland | San Francisco | 5 | Pink | 10 | Yes |
| 11 | San Francisco | Salt Lake City | 5 | Orange | 10 | Yes |
| 12 | San Francisco | Salt Lake City | 5 | White | 10 | Yes |
| 13 | San Francisco | Los Angeles | 3 | Yellow | 4 | Yes |
| 14 | San Francisco | Los Angeles | 3 | Pink | 4 | Yes |
| 15 | Los Angeles | Las Vegas | 2 | Gray | 2 | No |
| 16 | Los Angeles | Phoenix | 3 | Gray | 4 | No |
| 17 | Los Angeles | El Paso | 6 | Black | 15 | No |
| 18 | Calgary | Winnipeg | 6 | White | 15 | No |
| 19 | Calgary | Helena | 4 | Gray | 7 | No |
| 20 | Helena | Winnipeg | 4 | Blue | 7 | No |
| 21 | Helena | Salt Lake City | 3 | Pink | 4 | No |
| 22 | Helena | Denver | 4 | Green | 7 | No |
| 23 | Helena | Duluth | 6 | Orange | 15 | No |
| 24 | Helena | Omaha | 5 | Red | 10 | No |
| 25 | Salt Lake City | Denver | 3 | Red | 4 | Yes |
| 26 | Salt Lake City | Denver | 3 | Yellow | 4 | Yes |
| 27 | Las Vegas | Salt Lake City | 3 | Orange | 4 | No |
| 28 | Phoenix | Denver | 5 | White | 10 | No |
| 29 | Phoenix | Santa Fe | 3 | Gray | 4 | No |
| 30 | Phoenix | El Paso | 3 | Gray | 4 | No |
| 31 | El Paso | Houston | 6 | Green | 15 | No |
| 32 | El Paso | Dallas | 4 | Red | 7 | No |
| 33 | El Paso | Oklahoma City | 5 | Yellow | 10 | No |
| 34 | El Paso | Santa Fe | 2 | Gray | 2 | No |
| 35 | Santa Fe | Oklahoma City | 3 | Blue | 4 | No |
| 36 | Santa Fe | Denver | 2 | Gray | 2 | No |
| 37 | Denver | Oklahoma City | 4 | Red | 7 | No |
| 38 | Denver | Kansas City | 4 | Black | 7 | Yes |
| 39 | Denver | Kansas City | 4 | Orange | 7 | Yes |
| 40 | Denver | Omaha | 4 | Pink | 7 | No |
| 41 | Winnipeg | Sault St. Marie | 6 | Gray | 15 | No |
| 42 | Winnipeg | Duluth | 4 | Black | 7 | No |
| 43 | Duluth | Sault St. Marie | 3 | Gray | 4 | No |
| 44 | Duluth | Toronto | 6 | Pink | 15 | No |
| 45 | Duluth | Chicago | 3 | Red | 4 | No |
| 46 | Duluth | Omaha | 2 | Gray | 2 | Yes |
| 47 | Duluth | Omaha | 2 | Gray | 2 | Yes |
| 48 | Omaha | Chicago | 4 | Blue | 7 | No |
| 49 | Omaha | Kansas City | 1 | Gray | 1 | Yes |
| 50 | Omaha | Kansas City | 1 | Gray | 1 | Yes |
| 51 | Kansas City | Saint Louis | 2 | Blue | 2 | Yes |
| 52 | Kansas City | Saint Louis | 2 | Pink | 2 | Yes |
| 53 | Kansas City | Oklahoma City | 2 | Gray | 2 | Yes |
| 54 | Kansas City | Oklahoma City | 2 | Gray | 2 | Yes |
| 55 | Oklahoma City | Little Rock | 2 | Gray | 2 | No |
| 56 | Oklahoma City | Dallas | 2 | Gray | 2 | Yes |
| 57 | Oklahoma City | Dallas | 2 | Gray | 2 | Yes |
| 58 | Dallas | Little Rock | 2 | Gray | 2 | No |
| 59 | Dallas | Houston | 1 | Gray | 1 | Yes |
| 60 | Dallas | Houston | 1 | Gray | 1 | Yes |
| 61 | Houston | New Orleans | 2 | Gray | 2 | No |
| 62 | New Orleans | Miami | 6 | Red | 15 | No |
| 63 | New Orleans | Atlanta | 4 | Orange | 7 | Yes |
| 64 | New Orleans | Atlanta | 4 | Yellow | 7 | Yes |
| 65 | New Orleans | Little Rock | 3 | Green | 4 | No |
| 66 | Little Rock | Nashville | 3 | White | 4 | No |
| 67 | Little Rock | Saint Louis | 2 | Gray | 2 | No |
| 68 | Saint Louis | Nashville | 2 | Gray | 2 | No |
| 69 | Saint Louis | Pittsburgh | 5 | Green | 10 | No |
| 70 | Saint Louis | Chicago | 2 | Green | 2 | Yes |
| 71 | Saint Louis | Chicago | 2 | White | 2 | Yes |
| 72 | Chicago | Pittsburgh | 3 | Black | 4 | Yes |
| 73 | Chicago | Pittsburgh | 3 | Orange | 4 | Yes |
| 74 | Chicago | Toronto | 4 | White | 7 | No |
| 75 | Sault St. Marie | Montreal | 5 | Black | 10 | No |
| 76 | Sault St. Marie | Toronto | 2 | Gray | 2 | No |
| 77 | Toronto | Montreal | 3 | Gray | 4 | No |
| 78 | Toronto | Pittsburgh | 2 | Gray | 2 | No |
| 79 | Pittsburgh | New York | 2 | White | 2 | Yes |
| 80 | Pittsburgh | New York | 2 | Green | 2 | Yes |
| 81 | Pittsburgh | Washington | 2 | Gray | 2 | No |
| 82 | Pittsburgh | Raleigh | 2 | Gray | 2 | No |
| 83 | Nashville | Raleigh | 3 | Black | 4 | No |
| 84 | Nashville | Atlanta | 1 | Gray | 1 | No |
| 85 | Nashville | Pittsburgh | 4 | Yellow | 7 | No |
| 86 | Atlanta | Miami | 5 | Blue | 10 | No |
| 87 | Atlanta | Charleston | 2 | Gray | 2 | No |
| 88 | Atlanta | Raleigh | 2 | Gray | 2 | Yes |
| 89 | Atlanta | Raleigh | 2 | Gray | 2 | Yes |
| 90 | Charleston | Miami | 4 | Pink | 7 | No |
| 91 | Raleigh | Charleston | 2 | Gray | 2 | No |
| 92 | Raleigh | Washington | 2 | Gray | 2 | Yes |
| 93 | Raleigh | Washington | 2 | Gray | 2 | Yes |
| 94 | Washington | New York | 2 | Orange | 2 | Yes |
| 95 | Washington | New York | 2 | Black | 2 | Yes |
| 96 | New York | Boston | 2 | Yellow | 2 | Yes |
| 97 | New York | Boston | 2 | Red | 2 | Yes |
| 98 | New York | Montreal | 3 | Blue | 4 | No |
| 99 | Boston | Montreal | 2 | Gray | 2 | Yes |
| 100 | Boston | Montreal | 2 | Gray | 2 | Yes |

### 4.3 Route Length Distribution

| Length | Count (single segments) | Points per Route |
|--------|------------------------|-----------------|
| 1 | 9 | 1 |
| 2 | 38 | 2 |
| 3 | 21 | 4 |
| 4 | 16 | 7 |
| 5 | 8 | 10 |
| 6 | 8 | 15 |
| **Total** | **100** | |

### 4.4 Double Route Pairs

The following city pairs have two parallel routes. In 2--3 player games, only one of the two routes may be claimed (see Section 14).

| City A | City B | Route 1 Color | Route 2 Color | Length |
|--------|--------|---------------|---------------|--------|
| Vancouver | Seattle | Gray | Gray | 1 |
| Seattle | Portland | Gray | Gray | 1 |
| Portland | San Francisco | Green | Pink | 5 |
| San Francisco | Salt Lake City | Orange | White | 5 |
| San Francisco | Los Angeles | Yellow | Pink | 3 |
| Salt Lake City | Denver | Red | Yellow | 3 |
| Duluth | Omaha | Gray | Gray | 2 |
| Omaha | Kansas City | Gray | Gray | 1 |
| Kansas City | Saint Louis | Blue | Pink | 2 |
| Kansas City | Oklahoma City | Gray | Gray | 2 |
| Oklahoma City | Dallas | Gray | Gray | 2 |
| Dallas | Houston | Gray | Gray | 1 |
| Denver | Kansas City | Black | Orange | 4 |
| New Orleans | Atlanta | Orange | Yellow | 4 |
| Saint Louis | Chicago | Green | White | 2 |
| Chicago | Pittsburgh | Black | Orange | 3 |
| Atlanta | Raleigh | Gray | Gray | 2 |
| Raleigh | Washington | Gray | Gray | 2 |
| Pittsburgh | New York | White | Green | 2 |
| Washington | New York | Orange | Black | 2 |
| New York | Boston | Yellow | Red | 2 |
| Boston | Montreal | Gray | Gray | 2 |

Total: **22 double-route pairs** = 44 segments, plus **56 single-route segments** = 100 total segments.

---

## 5. Train Car Card System

### 5.1 Card Distribution

The train car deck contains **110 cards** total:

| Card Type | Color | Hex Code | Count |
|-----------|-------|----------|-------|
| Box Car | Pink | `#E91E90` | 12 |
| Passenger Car | White | `#F5F5F5` | 12 |
| Tanker | Blue | `#1976D2` | 12 |
| Reefer | Yellow | `#FBC02D` | 12 |
| Freight | Orange | `#F57C00` | 12 |
| Hopper | Black | `#212121` | 12 |
| Coal Car | Red | `#D32F2F` | 12 |
| Caboose | Green | `#388E3C` | 12 |
| Locomotive (Wild) | Rainbow | multicolor | 14 |
| **Total** | | | **110** |

### 5.2 Card Properties

- **Colored cards** (8 types x 12 = 96 cards): Each card depicts a specific type of train car in one of the 8 colors. When claiming a route, the player must play cards matching the route's color.
- **Locomotive cards** (14 cards): These are wild cards. A locomotive can substitute for any color when claiming a route. They are depicted as a multicolored/rainbow steam locomotive.
- **Card backs**: All train car cards share an identical back design so that cards drawn from the draw pile are hidden information.

### 5.3 Card Illustration Mapping

Each of the 8 colors corresponds to a specific type of train car depicted on the card:

| Color | Train Car Type | Visual Description |
|-------|---------------|-------------------|
| Pink | Box Car | Enclosed rectangular freight car |
| White | Passenger Car | Windowed passenger coach |
| Blue | Tanker | Cylindrical tank car |
| Yellow | Reefer | Refrigerated boxcar |
| Orange | Freight | Open-top gondola car |
| Black | Hopper | Covered hopper car |
| Red | Coal Car | Open coal hopper |
| Green | Caboose | End-of-train crew car |
| Wild | Locomotive | Colorful steam engine |

---

## 6. Destination Ticket System

### 6.1 Overview

The destination ticket deck contains **30 cards**. Each card names two cities on the board and a point value. If a player has a continuous path of their claimed routes connecting the two cities at the end of the game, they earn the indicated points. If not connected, they lose that many points.

### 6.2 Complete Destination Ticket List

| # | City A | City B | Points |
|---|--------|--------|--------|
| 1 | Denver | El Paso | 4 |
| 2 | Kansas City | Houston | 5 |
| 3 | New York | Atlanta | 6 |
| 4 | Calgary | Salt Lake City | 7 |
| 5 | Chicago | New Orleans | 7 |
| 6 | Duluth | Houston | 8 |
| 7 | Helena | Los Angeles | 8 |
| 8 | Sault St. Marie | Nashville | 8 |
| 9 | Chicago | Santa Fe | 9 |
| 10 | Montreal | Atlanta | 9 |
| 11 | Sault St. Marie | Oklahoma City | 9 |
| 12 | Seattle | Los Angeles | 9 |
| 13 | Duluth | El Paso | 10 |
| 14 | Toronto | Miami | 10 |
| 15 | Dallas | New York | 11 |
| 16 | Denver | Pittsburgh | 11 |
| 17 | Portland | Phoenix | 11 |
| 18 | Winnipeg | Little Rock | 11 |
| 19 | Boston | Miami | 12 |
| 20 | Winnipeg | Houston | 12 |
| 21 | Calgary | Phoenix | 13 |
| 22 | Montreal | New Orleans | 13 |
| 23 | Vancouver | Santa Fe | 13 |
| 24 | Los Angeles | Chicago | 16 |
| 25 | Portland | Nashville | 17 |
| 26 | San Francisco | Atlanta | 17 |
| 27 | Los Angeles | Miami | 20 |
| 28 | Vancouver | Montreal | 20 |
| 29 | Los Angeles | New York | 21 |
| 30 | Seattle | New York | 22 |

### 6.3 Point Value Distribution

| Point Value | Count |
|-------------|-------|
| 4 | 1 |
| 5 | 1 |
| 6 | 1 |
| 7 | 2 |
| 8 | 3 |
| 9 | 4 |
| 10 | 2 |
| 11 | 4 |
| 12 | 2 |
| 13 | 3 |
| 16 | 1 |
| 17 | 2 |
| 20 | 2 |
| 21 | 1 |
| 22 | 1 |
| **Total** | **30** |

### 6.4 Destination Ticket Rules

- Destination tickets are kept **secret** from other players until the end of the game.
- A player may never voluntarily discard a destination ticket once they have chosen to keep it.
- A ticket is "completed" if the two named cities are connected by a continuous chain of routes **all claimed by that player**. Routes claimed by other players do not count.
- Connection does not need to be a direct route; any chain of that player's routes between the two cities counts.
- At game end: completed tickets **add** their point value to the player's score; incomplete tickets **subtract** their point value.

---

## 7. Game Setup

### 7.1 Component Preparation

1. **Unfold the board** and place it in the center of the table (or display it on screen).
2. **Shuffle the 110 train car cards** thoroughly and place the deck face-down near the board.
3. **Turn 5 cards face-up** from the top of the train car deck, placing them in a row beside the deck. This forms the **face-up display**.
4. **Shuffle the 30 destination ticket cards** and place the deck face-down near the board.
5. **Place the Longest Path bonus card** face-up near the board (it will be awarded at game end).

### 7.2 Player Setup (Per Player)

| Step | Action | Details |
|------|--------|---------|
| 1 | Choose a color | Blue, Red, Green, Yellow, or Black |
| 2 | Take 45 train pieces | All 45 plastic trains of the chosen color |
| 3 | Place scoring marker | On the "0" space of the scoring track around the board edge |
| 4 | Deal 4 train car cards | Drawn from the top of the shuffled train car deck; these go into the player's hand (hidden) |
| 5 | Deal 3 destination tickets | Drawn from the top of the destination ticket deck |
| 6 | Choose destination tickets | Player must keep **at least 2** of the 3 dealt destination tickets, but **may keep all 3**. Returned tickets go to the **bottom** of the destination ticket deck |

### 7.3 Starting Player

The player who is the most experienced traveler goes first (thematic rule). In a digital implementation, the starting player may be selected randomly or by the youngest player, at the host's discretion. Play proceeds **clockwise**.

---

## 8. Turn Actions

On their turn, a player must perform **exactly one** of the following three actions. A player cannot pass or skip their turn.

### 8.1 Action 1: Draw Train Car Cards

The player draws **2 train car cards**. Each card may be drawn from either:
- The **face-up display** (one of the 5 visible cards), OR
- The **top of the draw pile** (blind draw)

**Important restrictions:**
- If the player draws a **face-up Locomotive** (wild) card, that counts as **both draws** -- they may not draw a second card.
- If the player draws a non-Locomotive face-up card as their first draw, they may draw their second card from the face-up display or the draw pile. However, they **may not** take a face-up Locomotive as their second card.
- A player **may** draw a Locomotive from the top of the draw pile as either their first or second draw without restriction (only face-up Locomotives trigger the single-draw limit).
- Whenever a face-up card is taken, it is **immediately replaced** with the top card of the draw pile before the player draws their second card.

See Section 10 for complete card display and drawing rules, including the 3-locomotive cascade rule.

### 8.2 Action 2: Claim a Route

The player claims one route on the board by:
1. Selecting an **unclaimed** route.
2. Playing a set of train car cards from their hand that matches the route's requirements (see Section 9).
3. Placing one of their plastic trains on **each space** of the route.
4. Discarding the played cards to the discard pile.
5. **Immediately scoring** the route's point value and advancing their scoring marker.

**Restrictions:**
- A player may claim **at most one route per turn**.
- A player does **not** need to connect to any of their previously claimed routes. Routes may be claimed anywhere on the board.
- A player may never claim a route if they do not have enough trains remaining to fill all spaces.

### 8.3 Action 3: Draw Destination Tickets

The player draws **3 destination ticket cards** from the top of the destination ticket deck and must:
- Keep **at least 1** of the 3 drawn cards.
- They **may keep 2 or all 3** if they wish.
- Any cards they choose not to keep are placed at the **bottom** of the destination ticket deck.

**Note:** If fewer than 3 destination tickets remain in the deck, the player draws as many as are available and must keep at least 1 (or all of them if only 1 remains).

---

## 9. Route Claiming Rules

### 9.1 Colored Routes

To claim a colored route, the player must play a number of train car cards **equal to the route length**, all of the **same color matching the route's color**. Locomotive (wild) cards may substitute for any needed colored card.

**Example:** To claim a 4-length Red route, a player could play:
- 4 Red cards
- 3 Red cards + 1 Locomotive
- 2 Red cards + 2 Locomotives
- 1 Red card + 3 Locomotives
- 4 Locomotives

### 9.2 Gray Routes

Gray routes have no specific color requirement. To claim a gray route, the player must play cards of **any single color** (all the same) equal to the route length. Locomotives may substitute for any cards in the set. The player **cannot mix** different colored cards (excluding Locomotives) for a single gray route.

**Example:** To claim a 3-length Gray route, a player could play:
- 3 Blue cards
- 2 Green cards + 1 Locomotive
- 1 Yellow card + 2 Locomotives
- 3 Locomotives
- **NOT:** 1 Blue + 1 Green + 1 Red (mixed colors are not allowed)

### 9.3 Locomotive (Wild) Usage

- Locomotive cards may be used as part of any set when claiming any route.
- There is **no limit** to how many Locomotives can be used in a single claim.
- A route may be claimed using **only** Locomotive cards if the player has enough.

### 9.4 Route Ownership

- Once claimed, a route belongs to that player for the rest of the game. No other player may claim that same route.
- The claiming player's plastic train pieces remain on the route as a visible marker of ownership.
- For **double routes**, see Section 14.

### 9.5 Train Piece Placement

When claiming a route of length N:
- The player places exactly N train pieces from their supply onto the N spaces of that route on the board.
- The player's `trainsRemaining` is decreased by N.
- If a player does not have enough trains remaining (i.e., `trainsRemaining < N`), they **cannot** claim that route.

---

## 10. Card Display and Drawing Rules

### 10.1 Face-Up Display

Five train car cards are always displayed face-up beside the draw pile (except when the deck is empty). Players can see these cards and choose to draw from them.

### 10.2 Card Replacement

Whenever a card is taken from the face-up display, it is **immediately** replaced by the top card of the draw pile, before the player takes their second draw (if applicable).

### 10.3 Three-Locomotive Cascade Rule

If, at any time (after a replacement or during setup), **3 or more** of the 5 face-up cards are Locomotive cards, **all 5 face-up cards are immediately discarded** and 5 new cards are drawn from the top of the draw pile to replace them.

- This check occurs every time a new card is placed face-up.
- If the new set of 5 cards also has 3 or more Locomotives, they are discarded and replaced again. This repeats until fewer than 3 Locomotives are among the face-up 5, or until the draw pile is exhausted.

### 10.4 Drawing from the Draw Pile

- Cards drawn from the draw pile go directly into the player's hand, unseen by other players.
- There is no hand size limit.

### 10.5 Deck Exhaustion

- When the draw pile runs out, the discard pile is **shuffled** to form a new draw pile.
- If both the draw pile and discard pile are empty (all cards are in players' hands or face-up), players **cannot** draw train car cards. They must choose one of the other two actions on their turn.
- If the draw pile is empty but face-up cards remain, a player may still draw from the face-up display (cards are not replaced until the discard pile is reshuffled into a new draw pile or new cards become available).

### 10.6 Drawing Restrictions Summary

| First Draw | Second Draw Allowed? | Notes |
|-----------|---------------------|-------|
| Face-up colored card | Yes (face-up colored or blind draw) | Normal two-card draw |
| Face-up Locomotive | **No** -- turn ends | Locomotive from display = only 1 card drawn |
| Blind draw (any card) | Yes (face-up colored or blind draw) | Even if blind draw reveals a Locomotive in hand |
| Face-up colored card (1st) | Face-up Locomotive (2nd)? **No** | Cannot take face-up Locomotive as 2nd card |
| Blind draw (1st) | Face-up Locomotive (2nd)? **No** | Cannot take face-up Locomotive as 2nd card |

---

## 11. Scoring System

### 11.1 Route Scoring Table

Points are awarded **immediately** when a route is claimed and the scoring marker is advanced on the track.

| Route Length | Points |
|-------------|--------|
| 1 | 1 |
| 2 | 2 |
| 3 | 4 |
| 4 | 7 |
| 5 | 10 |
| 6 | 15 |

These values are fixed and non-negotiable. The point values follow approximately a quadratic progression, heavily rewarding longer routes.

### 11.2 Route Scoring by Length (Total Available Points)

| Length | Segments | Points Each | Total Points Available |
|--------|----------|-------------|----------------------|
| 1 | 9 | 1 | 9 |
| 2 | 38 | 2 | 76 |
| 3 | 21 | 4 | 84 |
| 4 | 16 | 7 | 112 |
| 5 | 8 | 10 | 80 |
| 6 | 8 | 15 | 120 |
| **Total** | **100** | | **481** |

### 11.3 Destination Ticket Scoring

Evaluated at game end only:
- **Completed** ticket: **+N** points (where N is the ticket's point value)
- **Incomplete** ticket: **-N** points (deducted from total score)

### 11.4 Longest Continuous Path Bonus

- **+10 points** to the player(s) with the longest continuous path of claimed routes.
- In case of a tie, **all tied players** receive the 10-point bonus.
- See Section 12 for detailed calculation rules.

### 11.5 Scoring Track

The board has a scoring track running along its border, numbered from 0 to 100. If a player exceeds 100 points, they continue around the track (their score is 100 + current position on the track). The scoring marker is advanced immediately whenever points are earned from claiming routes.

---

## 12. Longest Continuous Path Bonus

### 12.1 Definition

The "longest continuous path" is the longest chain of connected routes that a single player has claimed on the board. It is measured in **total number of train cars** (sum of route lengths), not in number of routes or number of cities.

### 12.2 Calculation Rules

- The path must be **continuous** -- each route in the path must connect to the next route at a shared city.
- The path **may include loops** and **may pass through the same city multiple times**.
- Each **individual train piece** (route segment) may only be counted **once** in the path. A claimed route is either fully included or fully excluded.
- The path does **not** need to start or end at any particular city.
- The path does **not** need to correspond to any destination ticket.

### 12.3 Algorithm

Computing the longest continuous path is equivalent to finding the longest trail in a multigraph (where edges = claimed routes, vertices = cities). This is an NP-hard problem in general but tractable for the small graph sizes in Ticket to Ride (at most 45 edges per player). A DFS/backtracking approach is recommended:

```
function longestPath(player):
    claimedRoutes = player.claimedRoutes
    best = 0
    for each route R in claimedRoutes:
        for each endpoint city C of R:
            visited = {R}
            pathLength = R.length
            best = max(best, dfs(C, visited, pathLength, claimedRoutes))
            // also try starting from the other endpoint
            otherCity = R.otherEndpoint(C)
            visited2 = {R}
            best = max(best, dfs(otherCity, visited2, R.length, claimedRoutes))
    return best

function dfs(currentCity, visitedRoutes, currentLength, allRoutes):
    best = currentLength
    for each route R in allRoutes where R not in visitedRoutes:
        if R connects to currentCity:
            nextCity = R.otherEndpoint(currentCity)
            visitedRoutes.add(R)
            best = max(best, dfs(nextCity, visitedRoutes, currentLength + R.length, allRoutes))
            visitedRoutes.remove(R)
    return best
```

### 12.4 Tie-Breaking

If two or more players tie for the longest continuous path, **all tied players** receive the 10-point bonus. There is no tie-breaking; the bonus is simply shared.

---

## 13. Game End and Final Scoring

### 13.1 Game End Trigger

The game enters its final round when, at the **end of any player's turn**, that player has **2 or fewer train pieces remaining** in their supply.

- The triggering player is noted.
- **Every player** (including the triggering player) then gets **one more turn**. Once the player immediately before the triggering player (in clockwise order) completes their final turn, the game ends.
- In other words: the triggering player's turn is their last turn, and all other players get exactly one more turn after the trigger.

### 13.2 Final Scoring Procedure

After the last turn is completed, scoring proceeds as follows:

| Step | Action | Details |
|------|--------|---------|
| 1 | Route points | Already tracked on scoring marker throughout the game |
| 2 | Reveal destination tickets | All players simultaneously reveal their destination ticket cards |
| 3 | Score completed tickets | For each completed ticket, **add** the ticket's point value to the player's score |
| 4 | Penalize incomplete tickets | For each incomplete ticket, **subtract** the ticket's point value from the player's score |
| 5 | Determine longest path | Calculate each player's longest continuous path (see Section 12) |
| 6 | Award longest path bonus | The player(s) with the longest path receive **+10 points** |
| 7 | Determine winner | The player with the **highest total score** wins |

### 13.3 Tie-Breaking (Final Score)

If two or more players tie for the highest score, the tied player who **completed the most destination tickets** wins. If still tied, the tied player with the **longest continuous path** wins. If still tied, the players share the victory.

### 13.4 Score Calculation Summary

```
Final Score = (Sum of all claimed route points)
            + (Sum of completed destination ticket values)
            - (Sum of incomplete destination ticket values)
            + (10 if holding Longest Path bonus)
```

A player's final score **can be negative** if destination ticket penalties outweigh their route points and completed tickets.

---

## 14. Player Counts and Double Routes

### 14.1 Player Count Support

| Players | Supported | Special Rules |
|---------|-----------|---------------|
| 2 | Yes | Double route restriction applies |
| 3 | Yes | Double route restriction applies |
| 4 | Yes | Full rules (no restrictions) |
| 5 | Yes | Full rules (no restrictions) |

### 14.2 Double Route Restriction (2--3 Players)

In games with **2 or 3 players**, when there are double routes (two parallel routes between the same pair of cities), **only one of the two routes may be claimed**. Once any player claims one route of the double pair, the other route is **permanently blocked** and may not be claimed by any player for the rest of the game.

### 14.3 Double Route Rules (4--5 Players)

In games with **4 or 5 players**, both routes of a double pair may be claimed, but **not by the same player**. A single player may never claim both routes between the same pair of cities.

### 14.4 Impact on Strategy

| Player Count | Double Routes Available | Effect |
|-------------|----------------------|--------|
| 2 | Only 1 of each pair | More blocking potential; route scarcity increased |
| 3 | Only 1 of each pair | Similar to 2-player; slightly less blocking |
| 4 | Both available | Reduced blocking; more route options |
| 5 | Both available | Most competitive for single routes; double routes provide relief |

---

## 15. UI Layout

### 15.1 Main Game Screen Layout

```
+-----------------------------------------------------------------------+
|  [Score Track / Leaderboard]                               [Menu] [?] |
+-----------------------------------------------------------------------+
|                                                                       |
|                                                                       |
|                         BOARD MAP                                     |
|                    (scrollable/zoomable)                               |
|                                                                       |
|                     Cities + Routes                                   |
|                     Player train pieces                               |
|                                                                       |
|                                                                       |
+-----------------------------------------------------------------------+
|  [Face-Up Cards: 1] [2] [3] [4] [5]    [Draw Pile]  [Dest. Tickets]  |
+-----------------------------------------------------------------------+
|  [Player Hand: card counts by color]    [Trains: 45] [Tickets: icons] |
+-----------------------------------------------------------------------+
```

### 15.2 Board Map Area

- The central area displays the stylized map of North America with all 36 cities and 100 route segments.
- Cities are represented as labeled dots or markers.
- Routes are displayed as colored paths between cities, with small rectangular spaces (one per train car length) along each route.
- Claimed routes show the claiming player's colored train pieces filling the spaces.
- Unclaimed routes show empty spaces in the route's color.
- Double routes are drawn as two parallel paths between the same cities, visually offset from each other.
- The map should support **zoom** (mouse scroll / pinch) and **pan** (click-drag / touch-drag) for detailed viewing.

### 15.3 City Rendering

| Element | Visual |
|---------|--------|
| City marker | Circular dot (10--14px radius) with city name label |
| City name | Text label adjacent to marker; font size scales with zoom |
| Hover state | City name enlarges; connected routes highlight |
| Active state | When selecting a route, valid cities pulse or glow |

### 15.4 Route Rendering

| Element | Visual |
|---------|--------|
| Route spaces | Rounded rectangles along the path, one per length unit |
| Route color | Filled with the route's color; Gray routes use a neutral gray |
| Unclaimed route | Semi-transparent colored spaces with dashed/outlined borders |
| Claimed route | Solid player-colored train piece in each space |
| Hover state | Route highlights when hovered, showing length and color tooltip |
| Blocked route (2--3 players) | Crossed out or dimmed after parallel route is claimed |

### 15.5 Face-Up Card Display

- Five cards displayed in a horizontal row below the board.
- Each card shows the train car illustration and its color.
- Locomotive cards are visually distinct with a rainbow/multicolor design.
- A face-down draw pile is shown to the right of the face-up display, with a card count indicator.
- The destination ticket draw pile is shown separately with its own card count indicator.
- Clicking a face-up card or the draw pile initiates the "Draw Train Car Cards" action.

### 15.6 Player Hand Display

- The current player's hand is shown at the bottom of the screen.
- Cards are grouped by color with a count indicator (e.g., "Red: 3", "Blue: 1", "Locomotive: 2").
- Cards may optionally be displayed as fanned-out hand or as compact color-coded tabs.
- Other players' hand sizes (total count) are visible, but not their specific cards.

### 15.7 Score and Player Info

- A leaderboard or score track displayed at the top or side of the screen.
- Each player's entry shows: player name, color, current score, trains remaining.
- The current player's turn is highlighted.
- During final scoring, an animated breakdown shows route points, ticket bonuses/penalties, and longest path bonus.

### 15.8 Destination Ticket View

- Players can view their own destination tickets at any time by clicking a "Tickets" button.
- Each ticket shows: City A, City B, point value, and a completion status indicator (connected / not yet connected / impossible to complete).
- A mini-map overlay can highlight the path between the two ticket cities.

### 15.9 Turn Action UI Flow

**Draw Train Car Cards:**
1. Player clicks a face-up card or the draw pile.
2. Card animates to player's hand.
3. If face-up card taken, replacement card flips from draw pile.
4. If first card was not a face-up Locomotive, prompt for second draw.
5. If first card was a face-up Locomotive, turn ends.

**Claim a Route:**
1. Player clicks on a route on the board (or selects from a list).
2. UI highlights the route and shows required cards.
3. For Gray routes, player selects which color to use.
4. If multiple valid card combinations exist, player selects which cards to play.
5. Cards are discarded; train pieces animate onto the route spaces.
6. Score updates with point animation (+N flies to score display).

**Draw Destination Tickets:**
1. Player clicks the destination ticket draw pile.
2. Three cards are revealed to the player (private view).
3. Player selects which cards to keep (minimum 1, maximum 3).
4. Unkept cards are returned to the bottom of the deck.
5. Confirmation dialog before finalizing selection.

### 15.10 Game End / Final Scoring Screen

- Animated sequence showing each player's final scoring breakdown:
  1. Route points (already scored)
  2. Each destination ticket revealed one at a time, with connection path highlighted on the map (green for completed, red for incomplete)
  3. Longest path calculated and highlighted on the map
  4. Final totals tallied
- Winner announcement with celebration animation.
- Option to view game statistics (routes claimed, cards drawn, etc.).

---

## 16. Audio Design

### 16.1 Music

| Context | Track Description | Tempo | Loop? |
|---------|-------------------|-------|-------|
| Main menu | Ambient train station atmosphere with soft orchestral undertone | Slow | Yes |
| In-game (relaxed) | Light acoustic guitar / piano with subtle train rhythm | Moderate (80--100 BPM) | Yes |
| In-game (tense / late game) | Builds tempo with added percussion as trains run low | Moderate-Fast (100--120 BPM) | Yes |
| Final scoring | Dramatic orchestral reveal with building crescendo | Variable | No |
| Victory | Triumphant brass fanfare with train whistle | Fast | No |

### 16.2 Sound Effects

| Event | Sound Description | Duration |
|-------|-------------------|----------|
| Draw card (blind) | Soft card flip / paper rustle | 0.3s |
| Draw card (face-up) | Card slide with slight snap | 0.3s |
| Draw Locomotive | Enhanced card draw with metallic chime | 0.5s |
| Claim route (short, 1--2) | Quick train whistle + click-clack | 0.8s |
| Claim route (medium, 3--4) | Medium train whistle + rhythmic click-clack | 1.2s |
| Claim route (long, 5--6) | Long train whistle + extended rumble | 1.8s |
| Place train piece | Wooden piece placement "clunk" | 0.2s |
| Score increment | Ascending chime / bell per point step | 0.1s per step |
| Destination ticket draw | Paper shuffle / fan | 0.4s |
| Ticket completed (revealed) | Celebratory ding + cash register ring | 0.6s |
| Ticket failed (revealed) | Descending trombone / sad horn | 0.8s |
| Longest path awarded | Extended train whistle + applause | 2.0s |
| 3-Locomotive cascade | Dramatic card sweep + shuffle whoosh | 1.0s |
| Last round warning | Train bell alarm + announcement chime | 1.5s |
| Turn notification | Soft bell / ding | 0.3s |
| Button hover | Subtle click | 0.1s |
| Invalid action | Error buzz / denied tone | 0.3s |

### 16.3 Ambient Background

| Layer | Description |
|-------|-------------|
| Steam engine idle | Soft rhythmic chugging, barely audible | 
| Station ambiance | Distant crowd murmur, occasional announcement | 
| Train on track | Rhythmic click-clack synced with turn timer (if used) |

---

## 17. AI Opponents

### 17.1 Difficulty Levels

| Level | Name | Description |
|-------|------|-------------|
| 1 | Easy | Random valid moves; prioritizes drawing cards; poor destination ticket management |
| 2 | Medium | Balances card drawing and route claiming; attempts to complete destination tickets; basic blocking awareness |
| 3 | Hard | Optimized route planning; considers opponent positions; strategic Locomotive usage; attempts to maximize destination ticket completion while blocking opponents |

### 17.2 AI Decision Framework

Each AI turn, evaluate the following priority order:

1. **Can I claim a critical route?** (one that completes or enables a destination ticket)
2. **Should I draw destination tickets?** (only if current tickets are near completion and confidence is high)
3. **What cards should I draw?** (prioritize colors needed for planned routes)

### 17.3 AI Route Planning

- At the start of the game and whenever destination tickets are drawn, the AI should compute shortest paths between ticket cities using Dijkstra's algorithm on the board graph, weighted by route length.
- The AI maintains a "plan" of routes to claim and collects cards accordingly.
- When an opponent claims a planned route, the AI recalculates its plan.

---

## 18. QA Acceptance Matrix

### 18.1 Core Mechanics Validation

| Test Case | Expected Result | Priority |
|-----------|----------------|----------|
| Claim a colored route with exact color cards | Route claimed; cards discarded; score updated; trains decremented | Critical |
| Claim a colored route using Locomotives as wild | Route claimed with mixed color + Locomotive set | Critical |
| Claim a gray route with single color + Locomotives | Route claimed; only one color type used (plus wilds) | Critical |
| Attempt to claim gray route with mixed non-Locomotive colors | Action rejected with error message | Critical |
| Attempt to claim route with insufficient cards | Action rejected | Critical |
| Attempt to claim route with insufficient trains | Action rejected | Critical |
| Attempt to claim already-claimed route | Action rejected | Critical |
| Draw 2 cards from draw pile | 2 cards added to hand | Critical |
| Draw 1 face-up + 1 draw pile | 1 specific + 1 random card added; face-up replaced | Critical |
| Draw face-up Locomotive as first card | Only 1 card drawn; turn ends | Critical |
| Attempt to draw face-up Locomotive as second card | Action rejected; must draw from pile or different face-up | Critical |
| Draw Locomotive from draw pile as either card | Normal 2-card draw continues | Critical |
| 3 Locomotives in face-up display | All 5 discarded and replaced | Critical |
| Cascade: replacement cards also have 3+ Locomotives | Repeat discard-and-replace until < 3 Locomotives or deck empty | Critical |
| Draw pile exhausted | Discard pile shuffled into new draw pile | Critical |
| Both piles exhausted | Draw cards action unavailable | Critical |
| Draw 3 destination tickets, keep 1 | 1 added to hand; 2 returned to bottom of deck | Critical |
| Draw 3 destination tickets, keep 2 or 3 | Correct number added; remainder returned | Critical |
| Fewer than 3 destination tickets remain | Draw as many as available; keep at least 1 | High |
| Game end trigger: player at 2 trains remaining | Final round begins | Critical |
| Game end trigger: player at 0 trains remaining | Final round begins (same rule) | Critical |
| All players get exactly 1 more turn after trigger | Turn order correct; game ends after last turn | Critical |

### 18.2 Scoring Validation

| Test Case | Expected Result | Priority |
|-----------|----------------|----------|
| Claim length-1 route | +1 point | Critical |
| Claim length-2 route | +2 points | Critical |
| Claim length-3 route | +4 points | Critical |
| Claim length-4 route | +7 points | Critical |
| Claim length-5 route | +10 points | Critical |
| Claim length-6 route | +15 points | Critical |
| Complete destination ticket (cities connected) | +N points at game end | Critical |
| Fail destination ticket (cities not connected) | -N points at game end | Critical |
| Score goes below 0 from ticket penalties | Negative score allowed | High |
| Longest path: single player has longest | +10 points to that player | Critical |
| Longest path: tie between 2+ players | All tied players receive +10 points each | Critical |
| Longest path: path may loop through same city | Correctly counted | High |
| Longest path: each train piece counted only once | Correctly enforced | Critical |

### 18.3 Double Route Validation

| Test Case | Expected Result | Priority |
|-----------|----------------|----------|
| 2-player game: claim one of a double route | Other route becomes blocked | Critical |
| 3-player game: claim one of a double route | Other route becomes blocked | Critical |
| 4-player game: claim one of a double route | Other route remains available to other players | Critical |
| 5-player game: same player tries to claim both routes | Action rejected | Critical |
| 4-player game: two different players claim both routes | Both claims succeed | Critical |

### 18.4 Edge Cases

| Test Case | Expected Result | Priority |
|-----------|----------------|----------|
| Player has no valid actions (extremely rare) | Player must still take a turn; draw from available sources if possible | High |
| All destination tickets drawn during setup | Deck is empty; draw destination tickets action unavailable until cards returned | Medium |
| Score exceeds 100 on track | Marker wraps; display shows correct total | High |
| Simultaneous game-end trigger check (digital) | Only the first player to trigger is recorded | Medium |
| Destination ticket connection through long chain | Pathfinding correctly identifies connected cities | Critical |
| Player keeps all 3 initial destination tickets | Valid; no cards returned to deck | High |
| Final scoring tie-break: most completed tickets | Correct player wins | High |
| Final scoring tie-break: longest path (secondary) | Correct player wins | High |
| Final scoring: complete tie | Shared victory announced | Medium |
