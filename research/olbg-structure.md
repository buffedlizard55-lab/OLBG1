# OLBG.com — reverse-engineered structure (fetched live, 2026-10-21)

Source: live fetches of https://www.olbg.com, https://www.olbg.com/betting-tips
and each per-sport page listed below. OLBG describes itself as a tipster
community: each row shows the most-tipped selection, tips for/total, % share,
comments and expert flags. It is **not** a bookmaker; tipster comments are
user opinion, not verified fact.

## URL pattern

- Sport page: `https://www.olbg.com/betting-tips/<Sport>/<sport_id>`
- Event page: `https://www.olbg.com/betting-tips/<Sport>/<Region>/<League>/<Match>/<sport_id>?event_id=<id>`
- Event pages contain: Most Popular Tip, Best Tipster's Tip, then one section
  per market with every selection's tips for/total. Bookmaker prices render as
  `WIN @` with **no price visible** in fetched HTML-to-markdown — therefore no
  bookmaker odds are recorded anywhere in this project (left blank, flagged).

## OLBG sport menu (from https://www.olbg.com/betting-tips)

| ID | OLBG sport | In scope? | Reason |
|---|---|---|---|
| 1 | Football | No | Excluded: soccer / football |
| 2 | Horse Racing | No | Excluded: horse racing |
| 3 | Tennis | Yes | |
| 4 | Basketball | Yes | NBA, WNBA, EuroLeague, EuroCup, BCL, KBL… |
| 5 | Golf | Yes | Outright tournament markets |
| 7 | Cricket | Yes | |
| 8 | Snooker | Yes | |
| 9 | Rugby Union | Yes | |
| 10 | Rugby League | Yes | Only outrights listed on snapshot date |
| 11 | American Football | No | Excluded: American football |
| 12 | Baseball | Yes | MLB, NPB, KBO |
| 13 | Ice Hockey | Yes | NHL + European leagues |
| 14 | Motor Racing | Yes | F1 (+ NASCAR/IndyCar outrights when listed) |
| 15 | Darts | Yes | |
| 16 | Boxing (incl. UFC) | No | Excluded: boxing, UFC, MMA |
| 17 | Cycling | No | Excluded: cycling |
| 20 | Handball | Yes | Moneyline is 3-way (incl. Tie) |
| 21 | Volleyball | Yes | |
| 25 | Gaelic Football | Yes* | Distinct GAA sport; "football" exclusion read as soccer/ID 1 + American football. *Flagged for owner review — remove if "football" was meant to include Gaelic.* |
| 26 | Hurling | No | Excluded: hurling |
| 28 | Greyhounds | Yes | Greyhound racing ≠ horse racing (GBGB-licensed tracks) |

"Specials": no specials sport page was listed in OLBG's tips sport menu at
fetch time, so there was nothing to exclude under that heading (flagged).

IDs 6, 18, 19, 22–24, 27 do not appear in the current sport menu.

## How the list was built

Every event visible on each in-scope sport page (first page, before "Load
More Tips" pagination) on 2026-10-21 was transcribed into
`scripts/build_data.py` → `data/matches.csv` (164 events). OLBG adds/removes
events continuously, so this is a **dated snapshot**, not a live feed.
Events hidden behind "Load More" / later pagination are not included — see
Flagged for Review (F-01).
