# Session 87b30e7f (`T87B3`) — 15-Sport OLBG Verification, Multi-Market Line Origination & Audit Report

- **Generated UTC:** `2026-10-23T22:00:00Z` (Active fixture cutoff: strictly `>= 2026-10-24T00:00:00Z`)
- **Branch:** `arena/87b30e7f-olbg1` · **Dashboard:** `/OLBG1/87b30e7f/` · **Data Namespace:** `data/87b30e7f/`
- **Scope:** Strictly the 15 specified OLBG sports (`Golf, Volleyball, Rugby Union, Cricket, Snooker, Darts, Baseball, Gaelic Sports, Greyhounds, Tennis, Motor Racing, Handball, Ice Hockey, Basketball, Rugby League`).

## 1. Executive Delivery Summary

| Metric | Value | Verification Gate |
| --- | ---: | --- |
| Covered OLBG Sports | **15** | Excluded 9 hubs (`1, 2, 11, 16, 17, 18, 22, 23, 26`) with zero leakage |
| Verified Upcoming Fixtures | **75** (`5 × 15`) | 100% start `>= 2026-10-24T00:00:00Z`; 100% HTTPS governing-body sourced |
| Originated Betting Markets | **300** (`4 × 75`) | `673` outcomes; zero-vig probabilities sum to `1.000000` |
| Unique Written Predictions | **75** (`5 × 15`) | 60–86 words each; `0` duplicate 6-grams; `0` banned words |
| Confidence Breakdown | **44 High / 29 Medium / 2 Low** | 100% of High picks sit inside `[-250, +10000]` AND `<= 70.0%` zero-vig |
| Blank / Flagged Items | **8** | Left strictly blank (`""`) and documented on `87b30e7f/flagged.html` |
| Adjudicated Repo Findings | **10** | SHA-256 + line-range citations in `data/87b30e7f/repo_audit.json` |

## 2. High-Severity Repository Audit Discoveries

1. **EuroLeague Round 7 Hallucinated Saturday Slate (`data/496eaf02/fixtures.json`)**: `BK07`–`BK10` listed Saturday Oct 24 EuroLeague fixtures after all Round 7 games concluded Thu–Fri Oct 22–23 (`euroleaguebasketball.net`).
2. **WTA Ningbo & Osaka Draw Misreads (`data/496eaf02/fixtures.json`)**: Listed `Fernandez vs Kostyuk` (`[3]` Kostyuk retired in R16; `Bouzkova` advanced) and `Ann Li vs Katie Boulter` (opposite halves; official `wtafiles.wtatennis.com` `OP.pdf` confirms `Li vs Krueger` and `Boulter vs Siniakova`).
3. **Galway SFC Final Weather Postponement Missed (`data/8a900c04/desk.json`)**: `GS04` retained Saturday `17:15Z` from a club blog despite official `galwaygaa.ie` postponement to Sunday `2026-10-25T16:00:00Z`.
4. **Timezone & DST Fallback Errors (`496eaf02` & `8a900c04`)**: Adjudicated `NZ vs India 2nd T20I` to `2026-10-24T07:00:00Z` (`20:00 NZDT` on `bcci.tv`), `F1 US GP` to `21:00Z` Sat / `20:00Z` Sun (`CDT UTC-5` on `formula1.com`), and Sunday Oct 25 European/Irish `CEST->CET` & `IST->GMT` fallback across Handball, SuperLega Volleyball, and GAA County Finals.
5. **GAA Hurling (`ID 26`) & Women's TauronLiga Wrapper Cleanup**: Replaced Hurling rows (`GS01`, `GS02`) with pure County Senior Football Finals (`ID 25`) and men's PlusLiga redirect URLs with official Italian SuperLega (`legavolley.it`) fixtures.
