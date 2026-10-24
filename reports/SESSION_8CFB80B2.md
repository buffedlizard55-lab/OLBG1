# Session 8cfb80b2 — fresh desk, 24 October 2026

Task `T8CFB`. Branch `arena/8cfb80b2-olbg1`. Capture window **2026-10-24T17:05Z–17:30Z**.
Namespaced outputs only: `8cfb80b2/**`, `data/8cfb80b2/**`, `scripts/s8cfb80b2_*.py`,
`tests/pipeline/test_desk_8cfb80b2.py`, this report, and the appended coordination log.
One shared file was touched: `index.html` (a single "start here" bar, no layout or data change).

## What was asked

A clean, obvious dashboard for the fifteen in-scope OLBG sports: our own lines for every match, a winner pick
tiered low/medium/high, every market family examined, unique written predictions of at least 30 words for high
confidence picks with real form, history, statistics and availability, five of each per sport per day, priced
inside the −250…+10000 band with a better than 70% chance for High.

## What was produced

| Item | Count |
|---|---|
| Pages built | 24 (`8cfb80b2/index.html` plus 15 sport pages and 8 desk pages) |
| Captured match rows | 50 |
| Rows with a confirmed official start | 22 |
| Price books issued | 6 |
| Written predictions (≥30 words, unique, no banned words) | 6 (56–71 words) |
| Official sources read | 9 of 25 recorded sources |
| Flagged items | 10 |

Picks: Boston Bruins −215, Charles Leclerc podium −190, Golden State Warriors −160, Kyren Wilson final −170
(all Medium); Milwaukee Brewers −130 and Charles Leclerc race win +275 (Low).

## Live sources actually read

* **MLB statsapi** — World Series Game 2, first pitch `2026-10-25T00:00Z`, probable pitchers Rasmussen/Henderson,
  `ifNecessary=N`; Brewers 103-59 (.636), 55-26 home, 8-2 last ten; Rays 98-64 (.605), 43-38 away, 5-5 last ten.
* **NHL api-web** — official UTC starts for the 24 October slate (Sharks at Bruins and Rangers at Senators both
  23:00Z); standings read: Bruins 8-2-1, 17 points, .773 points percentage, 42 goals for, 22 against, 4-1-0 home.
* **NBA official injury report (12:15 PM ET PDF)** — all eight 24 October games with ET tip-off, plus Suns,
  Cavaliers, Nets, 76ers and Nuggets availability.
* **formula1.com** — United States Grand Prix weekend schedule (race 25 October, 16:00 track time), 56 laps of
  5.513 km, FP2 classification (Leclerc 1:35.291, Antonelli +0.042, Verstappen +0.189, Hamilton +0.615,
  Russell +0.744) and the FP1 report.
* **wst.tv** — Northern Ireland Open semi-final Williams v Jones scheduled 14:00 on 24 October, Wilson's 6-5 win
  over Craigie, final listed 08:00 on 25 October.
* **OLBG** — discovery for all fifteen sports, recorded as `discovery` role and never used to confirm a fact.

## The outcome that matters

**No pick reached High.** On our own numbers nothing cleared 70%, so the ladder stops at Medium and two picks are
explicitly Low. The brief's High rule (p > 0.70 and fair price within −250…+10000) is enforced in code by
`scripts/s8cfb80b2_validate.py` and by `tests/pipeline/test_desk_8cfb80b2.py`; a tier cannot be inflated without
failing the gate. Five of the fifteen sports produced no selection because no official fixture or form source could
be read in-session.

## Findings

| Id | Finding |
|---|---|
| F-8C-01 | No High-confidence selection issued; no tier inflated to hit the quota. |
| F-8C-02 | Nine sports produced no price; the blocking source is named for each. |
| F-8C-03 | OLBG hub times are US Eastern (UTC−4), pinned by matching all eight NBA fixtures to the NBA injury report. Hub times are labelled *derived*, never confirmed. |
| F-8C-04 | Greyhound race times are displaced five hours between the printed race name and the rendered start. |
| F-8C-05 | The golf hub returned "No tips found" at capture; no golf market existed to select from. |
| F-8C-06 | The rugby league hub listed outrights only; no fixture market was open. |
| F-8C-07 | San Jose's record was not on the readable portion of the NHL standings page, so the Bruins price is opponent-blind and capped at Medium. |
| F-8C-08 | Four NBA games were still "not yet submitted" on the injury report; no availability claim is made for them. |
| F-8C-09 | The snooker final's second player was undecided, so frame handicap and total frames could not be priced. |
| F-8C-10 | Several OLBG secondary routes return marketing copy or 404 bodies; only hub listings were used as discovery. |

## Dead ends worth recording

`stats.nba.com` scoreboard → request failed. `cdn.nba.com` scoreboard → HTTP 500. `pdc.tv/tournament/...` and
`pdc.tv/news` → cookie-consent wall. `unitedrugby.com/fixtures` → 404. `wtatennis.com/tournament/405/japan-open`
→ redirected to the 2025 event page with no 2026 match detail. Sandbox egress blocks direct TLS to `olbg.com`
and government/tour domains, so every live read went through the retrieval tool.

## Gates run

* `python3 scripts/s8cfb80b2_build.py` — 24 pages, deterministic from the data module.
* `python3 scripts/s8cfb80b2_validate.py` — 1,080 checks, 0 failures (provenance, tier arithmetic, prose length
  and uniqueness, banned words, every relative link and fragment, JSON freshness).
* `python3 -m unittest tests.pipeline.test_desk_8cfb80b2` — 11 tests, OK.
* `python3 -m pipeline.validate --site .` — 0 errors, including the edited root `index.html`.
* `python3 scripts/validate.py` — 1,455 pages swept, 0 errors, 3 pre-existing warnings from desk `f7fa77fc`.

## Not done, and why

Five picks per sport per day (75) was not achievable on readable evidence. Twenty-two of the fifty captured rows
still lack an official start, and nine sports lack any official form source reaching this environment. Those gaps
are published on the Coverage and Flagged pages rather than papered over, which is the only way the rest of the
record stays usable.
