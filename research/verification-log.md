# Verification log — line by line (snapshot 2026-10-21)

## What was checked, and against what

| Item | Source of record | Result |
|---|---|---|
| OLBG sport menu, sport IDs, URL patterns | https://www.olbg.com/betting-tips (live fetch) | 21 sports listed; 15 in scope after exclusions (see `olbg-structure.md`) |
| Every match row: fixture, date/time label, leading market/selection, tips k/n, %, experts, event_id | OLBG per-sport pages (live fetches, IDs 3,4,5,7,8,9,10,12,13,14,15,20,21,25,28) | Transcribed into `scripts/build_data.py`; each row in `data/matches.csv` carries its OLBG event + sport URL. Spot-rechecked event pages agreed with sport-page counts (e.g. 902039: 6/7 both places; 534889: 9/11; 32324: 7/8; 188824: 7/7; 9933: 8/11; 12053: 8/13) |
| Market structures (handicap/totals lines, splits) | OLBG event pages 902039, 534889, 32324, 188824, 9933, 12053 + sport-page guides | Recorded in `markets.md`; lines quoted are OLBG-listed, not invented |
| Bookmaker odds | Same pages | **Not visible** (`WIN @` blank) → field left empty on all 164 rows (F-03). No odds were inferred from third parties. |
| Originated prices & confidence | Computed by `build_data.py` from tip counts only | Recomputed on every build; High rows re-derived by hand below |
| High-pick fixtures/form | Official sites (below) | See per-pick table |
| Site build & internal links | `build_board.py` (renamed at integration — name clashed with session ce5920e3 builder) + automated link check | 20 HTML pages generated; 0 broken internal links; 0 rows missing OLBG source URL; `bookmaker_odds` blank on 164/164 rows |

## High-confidence picks — hand re-derivation + official checks

| Pick | k/n → p=(k+1)/(n+2) → fair price | Official fixture check |
|---|---|---|
| Fernandez (Tennis) | 6/7 → 7/9 = 77.8% → **1.29** (opp 4.50) | WTA Ningbo player list includes both players; ESPN: Fernandez (WTA 30) beat (7) Mertens 2-6 6-3 7-5 R1; Sasnovich (WTA 122, Q) beat Kasatkina 6-4 6-2. Fixture 21 Oct 2026 confirmed. |
| WAS Wizards (NBA) | 9/11 → 10/13 = 76.9% → **1.30** (opp 4.33) | NBA.com game 0022600086: Wed 21 Oct 2026 7:00 PM ET, Capital One Arena; WAS won last 3 H2H; Giannis traded; Davis+Young WAS; **Dybantsa OUT** (corrects OLBG tipster claim, F-05). |
| Afghanistan (Cricket) | 7/7 → 8/9 = 88.9% → **1.12** (opp 9.01) | ICC: tri-series final league game 21 Oct 2026, final 23 Oct. Vs Zimbabwe: AFG won by 158 runs (19 Oct), BAN lost by 99, bowled out 172 (17 Oct). Venue disputed → omitted (F-06). |
| Zonneveld (Darts) | 6/7 → 7/9 = 77.8% → **1.29** (opp 4.50) | PDC: R1 Thu 22 Oct 2026, Westfalenhalle Dortmund; seeds 4 v 29; Zonneveld won Dutch Darts Championship 18 Oct (maiden Euro Tour title). |
| van Duijvenbode (Darts) | 7/8 → 8/10 = 80.0% → **1.25** (opp 5.00) | PDC fixture confirmed as above; seeds **against** pick (Woodhouse 9 v DVD 24); OLBG best-tipster text contradicts its own tip (F-04) — disclosed in write-up. |

## Claims deliberately NOT used (unverified)

- OLBG tipster comments as facts (form, H2H, player news) — two were wrong/contradictory (F-04, F-05); others were simply not adopted without official corroboration (e.g. cricket innings figures Atal 102 / Rashid 4-17 quoted by a tipster; snooker "beat O'Sullivan last round" narrative).
- Third-party betting odds seen in search snippets (e.g. ESPN/DraftKings WSH −4.5) — noted only as corroboration that OLBG's listed handicap matches the wider market; not recorded as data.
- Start-time timezones, cricket venue, Gaelic market names — blank/flagged rather than guessed.

## Rebuild & re-verify

```bash
python3 scripts/build_data.py   # data/matches.csv + matches.json (164 rows)
python3 scripts/build_board.py   # docs/*.html (20 pages)
```

## Addendum (integration with session ce5920e3)

- **F-13 — Two in-scope sports missed by this board.** Session `ce5920e3` enumerated OLBG's
  taxonomy from the XML sitemap and found **Aussie Rules (ID 22)** and **eSports (ID 23)**,
  which do not appear in the HTML sport menu this board used. The 164-event snapshot therefore
  covers 15 of 17 in-scope sports. No rows were back-filled without a fetch. Follow-up: harvest
  `https://www.olbg.com/betting-tips/Aussie_Rules/22` and the eSports equivalent (confirm exact
  URL slug from `data/olbg_taxonomy.json`) into `scripts/build_data.py`.
- Builder renamed `scripts/build_site.py` → `scripts/build_board.py` (filename collision with
  the other session's site builder; both programs retained). Board publishes under `/docs/`
  alongside the root dashboard via legacy Pages. See `COORDINATION.md` §6.
