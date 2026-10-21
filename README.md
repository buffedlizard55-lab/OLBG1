# OLBG1 — OLBG Reverse-Engineering & Originated Lines Desk

An independent research project that reverse-engineers [OLBG.com](https://www.olbg.com/betting-tips)'s
tipping feeds, collects every upcoming match in scope, and **originates its own betting lines**
(win probability + fair odds, handicap, match total) with a confidence grade — without copying
any bookmaker prices.

**Live site (GitHub Pages):** https://buffedlizard55-lab.github.io/OLBG1/

## Scope
- **Covered (priced):** Tennis, Darts, Snooker, Basketball, Baseball, Ice Hockey, Cricket,
  Rugby Union, Volleyball, Handball, Gaelic Football — 133 matches at the 2026-10-21 snapshot.
- **Verified zero:** Rugby League (off-season — outrights only on OLBG).
- **Out of match scope:** Golf, Greyhound Racing, Motor Racing (outrights/races, no two-sided
  match markets) — documented on the site's Flagged for Review page.
- **Excluded by brief:** football/soccer, boxing, UFC/MMA, American football, hurling,
  horse racing, cycling, specials.

## How it works (reproduce everything)
```bash
python3 scripts/seed_data.py    # data/matches.json  — OLBG fixtures transcribed 2026-10-21
python3 scripts/originate.py    # data/lines.json    — our lines/picks/confidence (see Methodology)
python3 scripts/build_site.py   # docs/              — static site (GitHub Pages)
python3 scripts/validate.py     # hard gate: sources on every row, writeup rules, link check
```
- `data/writeups.json` — hand-written previews for HIGH-confidence picks only (≥30 words each,
  facts traceable to the official source on the row).
- Every match row links its **OLBG event page** and an **official league/governing-body page**.
  Values that could not be confirmed are blank and flagged `UNVERIFIED` — never filled in.
- Coordination between agent sessions: see `COORDINATION.md` (task board, verification log,
  irregularities). The site mirrors irregularities on its **Flagged for Review** page.

## Responsible use
18+. Originated lines are statistical estimates for research/information — not bookmaker odds
and not a guarantee of any outcome. Help: [GamCare](https://www.gamcare.org.uk/) ·
[GambleAware](https://www.gambleaware.org/).
