# Session 8f6d7364 — T66 fresh 22 Oct 2026 21:00Z live desk + final integration

**Session:** `8f6d7364-olbg1` · **Task:** T66 (§60) · **Branch:** `arena/8f6d7364-olbg1`
**Window:** 2026-10-22T21:00Z → 2026-10-29T21:00Z · **Desk:** `/8f6d7364/` (26 pages)

## What was done

1. **Claim** T66/§60 written to COORDINATION.md and pushed before work (commit `7ffa6f1`).
2. **Discovery harvest** — all 17 in-scope OLBG hubs fetched 20:50–20:57Z via the Arena page-fetch
   tool (chunk 0 of each server-rendered page). 117 OLBG events recorded in
   `data/8f6d7364/harvest.json` (event ids, displayed time text, most-tipped selection, tip
   counts, hub links). OLBG treated as discovery only.
3. **Official verification, line by line** — 46 sources with observation windows in
   `sources.json`. Result: **134 fixture rows**: 72 OLBG-discovered + officially verified,
   29 official-only (OLBG visible capture missed them), 33 discovery rows that could **not**
   be confirmed officially — published with blank official fields and flags (never inferred).
4. **Own lines** — model `8f6d7364-v1.0` (zero margin) priced **69 fixtures / 136 selections**
   (winner + MLB totals/run-line + URC totals/handicap + StarLigue totals/handicap):
   2 High / 49 Medium / 18 Low. 65 rows investigated and recorded as *not priced* with the
   missing official input named (markets page + unpriced ledger).
5. **High gate** (brief's literal rule: model p ≥ 0.70 AND fair American in −250…+10000 AND
   fixture officially verified) yields **2 High selections**:
   - `nhl-min-cgy` — MIN Wild winner, p = 0.702273, fair **−236**;
   - `rugby-league-rl-women-3` — Australia W winner, p = 0.714286, fair **−250.0** (boundary).
   The conjunction excludes every favourite shorter than −250: **17 ≥70% out-of-window winners
   are disclosed** on the High-confidence page, plus 2 near-band (0.685–0.700) watch items.
   The only official market quotes held (NHL API embedded odds, de-vigged) show **no game ≥70%**
   (max ≈0.66 New Jersey); model-vs-market table published on Analysis.
6. **Predictions** — 2 hand-written predictions (125 and 119 words), one per High pick, each
   clause mapped to an official fact with source + observation window; 6-gram uniqueness and
   word counts enforced by the validator.
7. **Dashboard** — 26 pages under `8f6d7364/`: landing KPIs, all-matches table, markets
   (incl. investigation matrix), high-confidence gate + ledgers, predictions, analysis/findings,
   flagged (21), sources (46), methodology, and 17 sport subpages (esports and greyhounds
   published as coverage-gap pages).

## Key sources (all fetched this session unless marked)

- NHL schedule + standings: `api-web.nhle.com` (20:53–21:04Z, standingsDateTimeUtc 20:57:30Z)
  — 12 games, official embedded odds, all 32 club records/L10/streaks.
- MLB World Series schedule `statsapi.mlb.com` (21:02Z); season records re-used from the
  canonical same-day capture (07:17:40–07:30:30Z) with that window disclosed.
- EuroLeague Round 7 game-center (21:05–21:08Z): Friday CEST tip times + records + form.
- WTA Osaka/Ningbo order-of-play + main-draw PDFs `wtafiles.wtatennis.com` (21:11–21:40Z).
- ATP Almaty/Brussels/Lyon daily schedules + `atptour.com/en/scores/current` results (21:16–21:39Z).
- PDC European Championship schedule — official pdc.tv page content confirmed via the
  canonical same-day capture (07:17Z) + this session's indexed reads; **direct fetch blocked
  by consent wall** (flag F-8F6D-03, attempts logged).
- URC Round 4 fixtures + full table (21:08–21:33Z); LNR Top 14 J7 + Pro D2 J8 (21:32–21:35Z);
  IRL fixtures + world rankings (21:09–21:35Z); LNH StarLigue J08 + classement (21:39–21:56Z);
  Munster GAA calendar (21:10/21:44Z); AFLW match centre (21:41Z); WST NI Open (21:09–21:12Z);
  F1 US GP page (21:01Z); PGA TOUR Champions hub (21:40Z); GBGB, LoL Esports, plusliga, ICC,
  nba.com, premrugby.com, cricket.co.za, hbl.de (results recorded, several failed/JS-walled).

## Irregularities found (full detail on /8f6d7364/flagged.html)

- **F-8F6D-01 (high)** — OLBG time text uses inconsistent zones across sports (NHL/MLB/tennis/
  darts track US Eastern with a start pad; EuroLeague equals BST; rugby equals venue-local).
- **F-8F6D-02 (high)** — OLBG lists Rathgormack v The Nire on 01 Nov; the official Munster GAA
  calendar has the Waterford final on Sun 25 Oct 14:30. Official published, OLBG kept as
  discovery with the conflict flagged.
- **F-8F6D-03 (medium)** — pdc.tv direct fetch returns only a consent wall (8 attempts).
- **F-8F6D-04 (medium)** — nba.com matchup cards JS-blocked: 23-Oct NBA rows keep discovery
  participants with official fields blank (the official calendar confirms 12 games that day).
- **F-8F6D-05/18 (medium)** — official pages unreachable/JS/paginated for cricket (ICC/NZC/CSA),
  Galway GAA, Premiership, Brazil NBB, Danish/German/Spanish handball, non-Polish volleyball:
  33 rows blank + flagged.
- **F-8F6D-06 (medium)** — hbl.de now serves unrelated steel-company content (redirect observed).
- **F-8F6D-07/08/09/10/17 (medium/low)** — timezone not stated on WST/IRL pages, F1 page's
  MY TIME/TRACK TIME ambiguity, Stifel Classic official date absent from fetched content,
  WTA OP tz-by-venue conversions disclosed.
- **F-8F6D-12 (low)** — OLBG's visible hub capture excludes XHR pagination; 29 official fixtures
  were published as official-only with the discovery gap noted.
- **F-8F6D-16 (low)** — ≥70% out-of-window conjunction documented as a systematic disclosure
  (17 winner selections listed, never labelled High).

## Gates (all green before PR)

- `python3 scripts/s8f6d7364_validate.py` → **VALIDATION PASSED (0 errors)** (21 flags,
  134 fixtures, 69 priced, 2 High, 2 predictions, 26 pages, links/anchors/price arithmetic).
- `python3 scripts/validate.py` → **PASSED** — 791 published pages link-checked, 0 errors,
  3 pre-existing warnings in `f7fa77fc/flagged.html` (not this session's files).
- `python3 -m unittest discover -s tests/pipeline` → **OK**; preserved suite → **OK**.
- `python3 -m pipeline.build --out _site` → 83 canonical pages with `_site/8f6d7364/` staged;
  `python3 -m pipeline.validate --site _site` → **0 errors**.

## Scope

Only `data/8f6d7364/**`, `scripts/s8f6d7364_*.py`, `8f6d7364/**`,
`reports/SESSION_8F6D7364.md` and append-only COORDINATION.md were touched. No root page,
`pipeline/**`, workflow, `data/current/**` or other session's desk was modified (§0.4).
PR/merge/Pages receipts are appended to COORDINATION.md §60 post-merge.
