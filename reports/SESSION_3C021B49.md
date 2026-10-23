# Session 3c021b49 — independent live 15-sport desk

**Captured:** 2026-10-23 22:30 UTC  
**Scope:** the user's exact 15 sports only: Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Baseball, Gaelic Sports, Greyhounds, Tennis, Motor Racing, Handball, Ice Hockey, Basketball and Rugby League.

## Method

- OLBG was used for route discovery only; no OLBG community-tip percentage is treated as a probability or sporting fact.
- Every published fixture row links to at least one official governing body, league, tour, promoter or team page.
- Unsupported fields remain blank and are listed on **Flagged for Review**.
- Prices are the desk's own zero-vig fair prices, not copied bookmaker quotes.
- High confidence requires the originated probability to exceed 70% and the fair American price to remain inside −250 to +10000.
- Predictions are unique hand-written passages of at least 30 words and omit the internal terms `model` and `verified`.

## Verification performed this session

Official pages and APIs fetched on 23 October 2026 include ATP Tour Almaty, NHL schedule and standings, MLB Stats API World Series schedule, NBA schedule, URC match centre, NRL World Cup draw, ICC match centre, PGA TOUR and LPGA leaderboards, World Snooker Tour matches, PDC tournament hub, Formula 1 schedule and standings, EHF/club and league pages, GBGB schedule, TAURON Liga, Lega Pallavolo and GAA fixture pages.

The NHL API was checked again at approximately 21:27 UTC: Montreal–Chicago remains scheduled for 2026-10-24T00:00Z and Tampa Bay–Colorado for 01:00Z; Saturday's twelve-game slate and Boston's 8-2-1 record were confirmed. The MLB API confirms Game 1 at 00:00Z with Nick Martinez against Jacob Misiorowski and `ifNecessary=N`; conditional Game 5 remains withheld. ATP's official page confirms the Almaty order of play, including Basilashvili–Tsitsipas and Medvedev–Bublik. The OLBG Golf, Snooker, Gaelic Football, Greyhounds, Handball and Motor Racing hubs were read directly and currently render “No tips found”, which is a platform-availability irregularity rather than proof that no event exists.

## Outputs

- Machine-readable data: `data/3c021b49/`
- Site: `3c021b49/` (overview, High picks, Predictions, Matches, Markets, 15 sport pages, Sources, Methodology, Reverse engineering, Repository audit, Flagged for Review)
- Reproducible build: `python3 scripts/s3c021b49_build.py`
- Gate: `python3 -m unittest tests.pipeline.test_desk_3c021b49`

## Known limits and irregularities

- Coverage is partial worldwide coverage, not a claim to enumerate every match in every league.
- No bookmaker market prices are copied; there is no independently captured live price feed in this desk.
- Some official pages do not publish a timezone or exact start. Those cells are blank and flagged.
- The OLBG hub clock and tip-render layer are inconsistent in places; official UTC feeds control publication.
- Where official evidence cannot support the brief's threshold, fewer than five High picks are shown for that sport rather than inventing a quota.
