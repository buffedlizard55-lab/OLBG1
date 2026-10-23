# Session `496eaf02` — OLBG15 Evening Desk (2026-10-23 ~20:30 UTC)

**Live desk:** [`../496eaf02/index.html`](../496eaf02/index.html)
**Data:** [`../data/496eaf02/`](../data/496eaf02/) (fixtures.json · matches.csv · markets.csv · predictions.json · flagged.json · sources.json · summary.json)

## Scope

The exact 15 sports named in the brief: Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts,
Baseball, Gaelic Sports, Greyhounds, Tennis, Motor Racing, Handball, Ice Hockey, Basketball,
Rugby League. Soccer/football, American football, boxing/UFC/MMA, hurling, horse racing,
cycling and specials are excluded. Gaelic Sports is the inherited OLBG category covering Gaelic
Football (id 25); Hurling (id 26) stays excluded.

## What was done

1. **OLBG discovery** — all 15 in-scope hubs harvested 2023-10-23 ~19:30Z via the search/render
   layer. OLBG tip shares are votes, not probabilities; OLBG renders Eastern Daylight Time to
   this session. OLBG is discovery only.
2. **Official-source verification** — every fixture row was checked this session against a
   governing body, league, tour or team source (60 sources, all listed on
   [`../496eaf02/sources.html`](../496eaf02/sources.html)). Missing values stay blank and are
   flagged, never inferred.
3. **Originated lines** — 200 markets / 460 outcomes across 67 priced fixtures, zero-vig fair
   prices (1/p, no margin, no clipping). Confidence policy: High-A = ≥70% and fair US price in
   −250…+10000; High-B = 62–70% in band; Medium = 50–62% or price-capped chalk; Low below.
4. **High-confidence picks** — 51 selections, each with a unique hand-written ≥30-word prediction
   (no "model"/"verified" wording, no repeated phrases).
5. **Flagged items** — 28 items on the Flagged-for-Review page (start-time rendering, conditional
   MLB games, unverified values, media-only fixtures).

## Counts (as captured 2026-10-23 20:30 UTC)

| Metric | Value |
|---|---|
| Fixtures captured (15 sports) | 81 |
| Upcoming fixtures | 70 |
| Priced fixtures | 67 |
| Originated markets / outcomes | 200 / 460 |
| High-confidence picks | 51 |
| Unique predictions | 51 |
| Flagged items | 28 |
| Official sources read | 60 |

Per-sport High picks: Tennis 5 · Volleyball 5 · Rugby Union 5 · Rugby League 5 · Cricket 5 ·
Darts 4 · Baseball 4 · Ice Hockey 6 · Basketball 10 · Handball 1 · Motor Racing 1 ·
Golf 0 · Snooker 0 · Gaelic Sports 0 · Greyhounds 0.

Golf, Snooker, Gaelic Sports and Greyhounds have no High picks this capture: their official
inputs (OWGR outright shares, snooker match form, county-final form, greyhound form) do not
support a selection inside the −250…+10000 window with ≥62% probability. The desk publishes
their fixtures and lines without inventing a pick.

## Key verified facts used

- **MLB World Series** — Rays (AL, 98-64) vs Brewers (NL, 103-59); Games 1–4 scheduled, Game 5
  conditional (`ifNecessary=Y` → all markets withheld). Probable pitchers: Martinez/Misiorowski
  (G1), Rasmussen/Henderson (G2). [statsapi.mlb.com](https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-18&endDate=2026-11-02&hydrate=team,probablePitcher,linescore)
- **NHL** — Friday: Canadiens @ Blackhawks (Suzuki out 2–4 weeks, upper-body; [NHL.com](https://www.nhl.com/news/montreal-canadiens-nick-suzuki-injury-status-update-october-22-2026)); Saturday slate from [api-web.nhle.com](https://api-web.nhle.com/v1/schedule/2026-10-23).
- **NBA** — standings + game notes: Celtics lost opener 113-121 at Detroit despite Paul George's
  38-point debut; Pacers 1-0 with Haliburton back from a torn Achilles; Clippers have five out.
- **EuroLeague** — Round 7 Saturday: Efes v Fenerbahce, Virtus v Panathinaikos, Bayern v
  Olympiacos, Partizan v Paris, with the official Round 7 injury report.
- **Rugby League World Cup** — Round 2 fixtures and Round 1 results on nrl.com (Australia 24-22
  NZ; Samoa 78-4 France; PNG 42-18 Lebanon; England 12-30 Tonga; Fiji 40-12 Cook Islands; women:
  Australia 40-0 Samoa, England 70-6 Wales).
- **Cricket** — NZ v India 2nd T20I (Hagley Oval); Pakistan ODI Tri-Series Game 4 (Pakistan 2-0,
  England 0-2); One-Day Cup Tasmania v Victoria, WA v NSW; NZ A v India A Test Day 1.
- **Tennis** — Almaty SFs (Medvedev v Bublik, Basilashvili v Tsitsipas); WTA Ningbo Open SFs
  (Rybakina v Shnaider, Fernandez v Kostyuk); WTA Osaka SF (Li v Boulter).
- **Motor Racing** — F1 US GP: FP1 fastest Leclerc; race Sunday 21:00Z; qualifying Saturday
  22:00Z; Drivers' standings Antonelli 340, Russell 238.
- **Golf** — Butterfield Bermuda Championship (Conners/Power tied -12 after R2); BMW Ladies
  Championship (Ryu 2-stroke lead); DP World Tour Genesis Championship (Jarvis/Rozner tied).
- **GAA** — Shinty-Hurling Internationals (Ireland v Scotland, Cork); Kilkenny SHC final
  (Ballyhale v Tullaroan); Cork SFC final (St Finbarr's v Nemo); Galway SFC final (Maigh Cuilinn
  v Salthill-Knocknacarra, moved to Sunday by Storm Boelo); Limerick SHC final (Kilmallock v
  Na Piarsaigh — media-verified, official page 404).
- **Greyhounds** — Romford Champion Stakes Final (Grouchos Gregor unbeaten over 575m); Dunstall
  Park Scurry Gold Cup.

## Irregularities flagged for review

1. OLBG renders Eastern Daylight Time (UTC−4) with no timezone label; independent UTC
   cross-checks were required for every row (e.g. MLB Game 1 "Today 20:00" = 2026-10-24T00:00Z;
   ATP Brussels "Not Before 18:30" Brussels = 16:30Z).
2. OLBG suppresses fixtures with zero open community tips — the entire Rugby League World Cup
   Round 2 (men's and women's) is invisible on OLBG and was found on nrl.com.
3. MLB World Series Game 5 carries the official `ifNecessary=Y` flag; all its markets are
   withheld per policy.
4. The Galway SFC final was moved from Saturday to Sunday 4pm by Galway GAA (Storm Boelo).
5. Darts PDC Order of Merit figures were cross-checked on multiple outlets; the official
   pdc.tv/rankings page renders behind a consent wall this session.
6. Limerick SHC final fixture verified on media only (Limerick Leader / The 42); the official
   Limerick GAA fixtures page returned HTTP 404.

## Build, tests and publication

- `python3 scripts/se496eaf02_build.py` writes all data files and 25 HTML pages.
- `python3 -m unittest tests.pipeline.test_desk_496eaf02` — 21 checks, all green.
- Full pipeline suite (`tests/pipeline`) and the preserved upstream suite pass.
- `python3 -m pipeline.validate --site .` and `python3 scripts/validate.py` — see
  COORDINATION.md receipts.
