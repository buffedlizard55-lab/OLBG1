# Session 37003e61 — 15-sport OLBG desk, 24 October 2026

**Captured:** 2026-10-24 17:40 UTC
**Branch:** `arena/37003e61-olbg1` (base `0f6a849`, claim `7acd478`)
**Scope:** exactly the fifteen requested sports — Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Baseball, Gaelic Sports, Greyhounds, Tennis, Motor Racing, Handball, Ice Hockey, Basketball, Rugby League.

## What was tried first

All fifteen OLBG hub routes were fetched before any line was originated. Prices are client-rendered on
OLBG, so every documented market is text-only: no quote, no overround, no implied probability. The hubs
were therefore used for **discovery** (which events exist and when) and nothing else. Community tip
votes were never converted into probabilities.

Fourteen sports returned a live card. Golf returned `No tips found.` — recorded verbatim in
`GOLF_NOTE` and on the site, rather than backfilled from memory.

## Official verification

Every priced row was rebuilt from a governing-body, league, tour or promoter page fetched in this session:

| Sport | Official source | What it supplied |
| --- | --- | --- |
| Ice Hockey | `api-web.nhle.com` schedule + standings | 12-game slate, UTC starts, records, home/road splits, goals for/against |
| Basketball | `nba.com/standings` | all 30 records including home/road and conference splits |
| Baseball | `statsapi.mlb.com` | World Series Game 2, probable pitchers, series score |
| Tennis | `atptour.com` Almaty and Vienna | order of play, seeds, final pairing |
| Rugby Union | `top14.lnr.fr`, `premrugby.com` | Journée 7 fixtures, six results, league positions, Round 4 form strings |
| Rugby League | `nrl.com` RLWC draw | Round 2 fixtures, scores, venues, group positions |
| Snooker | `wst.tv/matches` | quarter-final results, Match 62 semi-final, Match 63 final |
| Volleyball | `legavolley.it` calendar | SuperLega matchday 2-5 fixtures, venues, referees |
| Motor Racing | `formula1.com` United States GP | session times and FP2 classification |
| Cricket | `cricket.co.za` | South African board for 24 October |
| Gaelic Sports | `gaa.ie/fixtures-results` | 24 October inter-county listing |
| Greyhounds | `gbgb.org.uk/racing` | results search and race reports |

Routes that would not render were recorded as failures rather than worked around: PDC's tournament hub
(cookie-consent shell), both EHF match routes (404), both HBL schedule routes (reCAPTCHA), the WST
tournament page (404), and five other 404s listed in the access log.

## Decisions that shaped the desk

1. **No line without an input.** A row is priced only when its rating inputs were read from an official
   page. Fourteen fixtures qualify; thirty-six do not, and each of the thirty-six carries the specific
   reason on the site.
2. **The brief's two gates intersect in a 1.4-point window.** A fair price of −250 is 71.43%, so a
   selection must sit between 70.0% and 71.43% to satisfy both "greater than 70%" and "inside −250 to
   +10000". Lines are therefore originated at the 70.1–71.3% quantile, and every High price prints
   between −235 and −248. This is disclosed as finding F-3700-01 rather than presented as a coincidence.
3. **Handicaps carry the High tier in most sports.** The money line for a strong favourite is usually
   shorter than −250, so the High selection is the handicap at the price the window allows. The
   money-line call is still published, with its own tier and the reason it is not High.
4. **Unresolved clocks stay blank.** The two Rugby League World Cup rows carry no UTC start because
   NRL.com prints 1:05am and 5:05am without a timezone. Filling those cells would be guesswork.
5. **Golf is published with zero fixtures.** The alternative — inventing an event to fill a quota — is
   the failure mode the brief exists to prevent.

## Outputs

- Site: `37003e61/` — overview, picks, write-ups, all matches, markets, 15 sport pages, sources,
  methodology, OLBG map, repository audit, flagged register, 404.
- Data: `data/37003e61/` — `fixtures.json`, `markets.json`, `picks.json`, `predictions.json`,
  `sources.json`, `flagged.json`, `summary.json`, `matches.csv`.
- Build: `python3 scripts/s37003e61_build.py`
- Checks: `python3 scripts/s37003e61_validate.py` and
  `python3 -m unittest tests.pipeline.test_desk_37003e61`

## Numbers

50 fixtures · 15 sports · 31 originated markets · 65 priced outcomes · 14 priced fixtures ·
10 High selections · 10 unique write-ups (57–64 words each) · 25 sources (21 read, 4 failed) ·
48 flags.

High selections: Basketball 5/5, Rugby Union 2, Rugby League 2, Ice Hockey 1. Nine sports fall short;
each reason is stated per sport on the overview and in finding F-3700-02.

## Repository findings (line by line, this session)

- `COORDINATION.md` — 103 task rows contain 15 duplicated task IDs; ownership is ambiguous where it
  matters most.
- `data/current/snapshot.json` — stamped 2026-10-22T12:29:50Z, reports 108 listings and **0 High picks**,
  while later desks publish dozens. The root front door therefore contradicts the desks behind it.
- `data/3c021b49/fixtures.json` — still carries two ATP Almaty semi-finals for 24 October
  (Basilashvili–Tsitsipas, Medvedev–Bublik). The official ATP order of play shows the final as
  Medvedev–Basilashvili, so at least one pairing was already stale within a day. This desk stamps every
  row with a read time for exactly that reason.
- `data/3c021b49/predictions.json` — 51 entries, minimum 39 words, neither internal term present.
  Recorded as a positive control.
- Root HTML — no conflict markers, no tracked `.pyc`, zero broken local links across the five main pages.

## Limits

- This is a snapshot at 17:40 UTC, not a live feed. Start times move.
- Prices are the desk's own zero-vig estimates. No bookmaker quote was copied and no availability or
  edge is claimed.
- Coverage is partial worldwide coverage; it is not a claim to enumerate every match in every league.
- Nine sports did not reach the five-High target because the platform or the official route did not
  supply an event card, a draw, a table or a rule set. Nothing was padded to close the gap.
