# SESSION REPORT — f1c13c19-olbg1 (Task T57)

**Finished:** 2026-10-22 (harvest clock 07:26:51Z; build 08:20-09:00Z)
**Branch:** `arena/f1c13c19-olbg1` · **Namespace:** `f1c13c19/`, `data/f1c13c19/`, `scripts/sf1c13c19_*.py`, this report.

## Mission
Fresh end-to-end pass: (1) live OLBG harvest of all 17 in-scope hubs, (2) line-by-line
official-source verification, (3) independent multi-market line origination under the
strict `>=70% AND -250..+10000` high-confidence band, (4) namespaced dashboard + flagged
page, (5) validator gate, (6) PR -> main -> merge -> Pages.

## Harvest (2026-10-22, Arena fetch_page, 17 hubs)
~102 cards across 14 sports + 5 outright-only entries + 2 verified-zero hubs
(eSports, Aussie Rules) + empty NHL sub-route. Rugby League outright-only despite
RLWC26 running (upstream defect, now documented 3rd desk in a row). Verbatim archive:
`data/f1c13c19/harvest_notes.md` + `data/f1c13c19/olbg_snapshot.json`.

## Verification (official sources only; Arena fetch_page + indexed official snippets)
- **NHL**: api-web.nhle.com score+schedule for 2026-10-22 — 12 games, FUT, exact UTC
  starts, live team records (W-L-OTL) per team. Ratings = official points share.
- **MLB**: StatsAPI schedule (2026 WS: TB Rays @ MIL Brewers G1/G2 2026-10-24/25T00:00Z
  at American Family Field; G3 10-27T00:00Z Tropicana) + official 2026 standings
  (MIL 103-59 NL#1, 832/618 runs; TB 98-64 AL#1, 736/650; home/road splits).
- **NBA**: nba.com game pages — CLE@PHI 2026-10-22T23:00Z (Xfinity Mobile Arena, PHI 1-0,
  LeBron's 76ers home debut per official NBA news), DEN@OKC 01:30Z (Paycom Center, 0-0/0-0).
  Only measured records rated; 0-0 rows intentionally blank (rule: never impute).
- **EuroLeague R7**: official standings (PAO 5-1 +90, Fener 5-1, Oly 5-1, Hapoel 5-2,
  Valencia/Zvezda/Dubai 4-2 … Baskonia/Milan/Paris 1-5) + official Game Center article
  (Maccabi's temporary home in Belgrade -> neutral-site pricing flag). Besiktas confirmed
  a genuine EuroLeague club this season (resolves earlier label suspicion).
- **ATP**: official daily schedules + top-seeds pages for Almaty 9410, Brussels 7485,
  Lyon 496 (R16 slates today; Medvedev seed 1 r6, Bublik 3 r22, Khachanov 5 r27;
  Lehecka 2 r16, Michelsen 5 r35, Bergs 6 r39; Cobolli 1 r7, Fritz 2 r12, Vacherot 3 r14,
  Paul 4 r18, Nakashima 5 r19, Musetti 6 r25). Basel/Vienna have no schedule this week
  (official page: "no daily schedule").
- **WTA**: official signed draw PDF `wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf`
  for the BNB Ningbo Open (19-25 Oct, $1.206M): seeds = 1 Rybakina (rank 1, 9696 pts,
  defending champion), 2 Swiatek(9), 3 Kostyuk(10), 4 Jovic(11), 5 Bencic(12), 6 Shnaider(13),
  7 Mertens(14), 8 Cirstea(16); R16 Rybakina-Kudermetova & Eala-Shnaider today.
- **Snooker**: WST official match centre — BetVictor Northern Ireland Open 2026 Round 3
  (Belfast), all 8 OLBG card matches confirmed (Selt-Craigie, Wilson-Pang, Slessor-Walden,
  McGill-Baranowski, Williams-O'Donnell, Gilbert-Cheung, Brown-Donaldson, Jones-Wells).
- **Darts**: PDC official news articles — 2026 Machineseeker European Championship,
  Westfalenhallen Dortmund 22-25 Oct; R1 x8 tonight (order + pairings) & tomorrow;
  official 1-32 tournament seeds (Clayton #1, Nijman #2 … Springer #32). OoM money
  (Littler 3,113,500 etc.) only via corroborated sources (pdc.tv OoM page consent-walled)
  — used only in cross-checked tier, and only for notes.
- **Rugby union**: URC R4 fixtures (official fixture release; Connacht-Zebre Fri,
  Bulls-Ulster / Stormers-Scarlets / Leinster-Munster Sat; Aviva 18:00 local);
  Top 14 J7 (Toulouse-Perpignan, Bayonne-Lyon, La Rochelle-Bordeaux) with LNR official
  post-J6 positions; Pro D2 J8 full round (Oyonnax club site + allrugby: Montauban v
  leaders Oyonnax tonight 21:00 Sapiac; 7 games tomorrow).
- **Handball**: eurohandball.com R5 list (Melsungen-Plock, Szeged-GOG 18:45;
  Barca-Montpellier, Sporting-Kristianstad, Kolstad-Magdeburg 20:45) + official R5
  preview H2H (Magdeburg 37-22, GOG 36-34). Group tables cross-checked.
- **Cricket**: cricinfo/ICC calendar — ENG-SL 3rd ODI Rawalpindi 08:00Z (tri-series,
  Pakistan 2-0 context), NAM-IRE 1st ODI Windhoek 08:15Z, AUSW-NZW 3rd T20I North Sydney
  (cricket.com.au official), AFG-ZIM final Sharjah 23 Oct 13:00Z. CSA T20 domestic two
  games cross-checked (Storm-Tuskers Benoni 16:00Z; Rhinos-Emerging White River 11:00Z).
- **GAA**: Galway GAA official county fixtures — Moycullen v Salthill-Knocknacarra Co.
  Final Sat 24 Oct 19:00 Pearse Stadium (ref Shane Curley); Cork final Nemo-Barrs corroborated.
- **SHL**: Thursday 6-game 19:00 CET slate cross-checked (vaxjolakers.se club + two TV
  schedule hubs + standings hub).
- **Golf/F1/Greyhounds/LoL/RLWC**: root desk verified fixtures reused and re-checked
  (Bermuda Championship today; US GP at COTA Sun 20:00Z; GBGB cards; LoL Worlds play-in;
  RLWC26 24-26 Oct) — all treated as above the OLBG upstream gaps.

## Model & results
- 137 fixtures; 128 priced two-sided; **3 High / 12 Medium (3 above-window) / 113 Low**;
  9 event-only listings (golf, F1, greyhounds).
- Zero-vig band engine on the shared deterministic core: High requires verified fixture +
  both ratings official + p>=70% + vig-free price in [-250,+10000]; handicap ladders walked
  outward for an in-band rung; totals where baselines exist; DNB for draw sports.
- High picks (all with unique human write-ups >=30 words from verified facts only):
  NY Islanders vs LA Kings moneyline (fair -250), Jonny Clayton vs Niko Springer (-250),
  Wessel Nijman vs Martin Schindler (-233).
- Above-window moneylines on the Window Report (Medium): Minnesota Wild @ Calgary (-256),
  Panathinaikos vs Baskonia (-1000), Stade Toulousain vs Perpignan (-476).

## Irregularities logged (see f1c13c19/flagged.html)
Upstream: RLWC26 absent from OLBG RL hub; eSports/Aussie hubs zero mid-season; NHL
sub-route empty on a 12-game night; pervasive OLBG clock/tz defects (darts ~3-4h early,
Almaty ~4h early, greyhounds 1h shift, MLB WS 20:00 vs 20:00 ET); "Baranowski" spelling;
volleyball small-sample underdog card; plusliga.pl redirect defect recurs (F-F7-09).
Desk-side: 34 pending rows blank-and-flagged (never inferred) — volleyball minor leagues,
women's handball, KBL/NBB, Liiga card, tomorrow's NBA cards, Gibson-Krueger venue.
Consent/render blockers: PDC OoM page, WST rankings table, WTA draws/rankings shells —
values taken only where corroborated and capped at Medium accordingly.

## Pipeline
`scripts/sf1c13c19_data.py` (+ `_data2.py`) -> fixtures.json (137) ;
`sf1c13c19_model.py` -> lines.json (128 + 9 listings) ;
`sf1c13c19_predictions.py` -> predictions.json (128 unique texts) ;
`sf1c13c19_site.py` -> f1c13c19/*.html (8 pages) ; `sf1c13c19_validate.py` -> VALIDATION PASSED.
