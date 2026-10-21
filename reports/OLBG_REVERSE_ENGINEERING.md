# Reverse Engineering `OLBG.com` — Technical Architecture, Routing & Anomalies

**Snapshot Date (UTC):** `2026-10-21`  
**Primary Target:** [`https://www.olbg.com/betting-tips`](https://www.olbg.com/betting-tips)  
**Sitemap Index Inspected:** [`https://www.olbg.com/sitemap.xml`](https://www.olbg.com/sitemap.xml) & [`https://www.olbg.com/sitemap-betting-tips.xml`](https://www.olbg.com/sitemap-betting-tips.xml)

---

## 1. Platform Architecture & URL Routing Schema

`OLBG.com` runs a hybrid server-rendered PHP / OctoberCMS application backed by relational `sport_id` and `event_id` integer keys, paired with client-side JavaScript hydration for live bookmaker odds and dynamic pagination.

### 1.1 Canonical Route Patterns

| Route Layer | URL Pattern | Example | Backend Behavior |
| :--- | :--- | :--- | :--- |
| **Global Hot Tips Feed** | `/betting-tips` | [`/betting-tips`](https://www.olbg.com/betting-tips) | Top 20 most-tipped selections across all sports ordered by `win_tips DESC`. |
| **Sport Hub Feed** | `/betting-tips/{Sport_Slug}/{sport_id}` | [`/betting-tips/Basketball/4`](https://www.olbg.com/betting-tips/Basketball/4) | Queries open events for integer `sport_id` (`4`), rendering up to **20 match cards** (9 above mid-page promo banner + 11 below) plus open ante-post markets. |
| **Competition Sub-Hub** | `/betting-tips/{Sport}/{Region}/{Comp}/{sport_id}` | [`/betting-tips/Basketball/NBA/4`](https://www.olbg.com/betting-tips/Basketball/NBA/4) | Filters `sport_id` by competition hierarchy — **exposing lower-tip-count matches cut off at row #20 on the main sport feed**. |
| **Individual Event Page** | `/betting-tips/{Sport}/{Region}/{Comp}/{Event_Slug}/{sport_id}?event_id={event_id}` | [`...?event_id=534889`](https://www.olbg.com/betting-tips/Basketball/NBA/NBA/MIL_Bucks_@_WAS_Wizards/4?event_id=534889) | Primary lookup key is `?event_id={int}`. Renders `Most Popular Tip`, `Best Tipster's Tip`, full market accordions (`Money Line`, `Pointspread`, `Game Totals`, etc.), tip counts, percentages, and tipster comments. |
| **Profitable Tipster Hub** | `/best-tipsters/{Sport_Slug}/{sport_id}` | [`/best-tipsters/Tennis/3`](https://www.olbg.com/best-tipsters/Tennis/3) | Lists positive-annual-profit tipsters who currently hold open tips in `sport_id`. |
| **Individual Tipster Open Tips** | `/best-tipsters/{Sport_Slug}/{sport_id}/{member_id}` | [`/best-tipsters/Tennis/3/620242`](https://www.olbg.com/best-tipsters/Tennis/3/620242) | Displays every open selection, market handicap (`WIN @ / -0.50 hcap`), and written rationale by member ID. |

### 1.2 Discovery via Integer `sport_id` Probing (`1..31`)

Probing synthetic slugs `/betting-tips/Probe/{id}` across `1..31` revealed that OLBG's router ignores arbitrary `{Sport_Slug}` text when executing its event query and only renders a custom CMS article when `{Sport_Slug}/{sport_id}` matches an OctoberCMS entry (falling back to double-spaced `<title>{Slug}  Tips - OLBG.com</title>` on unmapped slugs). This allowed complete verification of all 31 numeric slots:

- **Excluded Sports (6 IDs covering all 10 excluded terms):**
  - `1` = `Football` (*soccer / association football*)
  - `2` = `Horse_Racing` (*horse racing*)
  - `11` = `American_Football` (*american football*)
  - `16` = `Boxing` (*combines Boxing, UFC, and MMA on a single unified feed*)
  - `17` = `Cycling` (*cycling*)
  - `18` = `Specials` (*entertainment, TV, awards, politics*)
  - `26` = `Hurling` (*hurling*)
  *(7 excluded sport IDs total: `1, 2, 11, 16, 17, 18, 26` — mapping cleanly onto all 10 excluded labels in the specification.)*
- **Covered Sports (17 IDs):**
  - **Active Match/Event Feeds (15 sports, 172 total events — 141 head-to-head matches + 31 tournament/race/ante-post events):** `3` Tennis (20), `4` Basketball (29 across main + subroutes), `5` Golf (10), `7` Cricket (14: 9 matches + 5 outrights), `8` Snooker (6), `9` Rugby Union (16: 15 matches + 1 outright), `10` Rugby League (3 outrights), `12` Baseball (1), `13` Ice Hockey (7), `14` Motor Racing (3), `15` Darts (18: 16 matches + 2 outrights), `20` Handball (19), `21` Volleyball (15), `25` Gaelic Football (5: 4 matches + 1 outright — included + flagged for scope review), `28` Greyhounds (6 races).
  - **Seasonal / Zero-Open-Tip Covered Feeds (2 sports, 0 open events):** `22` Aussie Rules (0 — AFL off-season) and `23` eSports (0 open tips on snapshot).
- **Unassigned / Legacy Empty IDs:** `6, 19, 24, 27, 29, 30, 31`.

---

## 2. Five Production Quirks & Irregularities Uncovered on `OLBG.com`

1. **Silent GeoIP Timezone Shifting Without Timezone Labels (`EDT` vs `BST`):**
   - Server-rendered event timestamps on `OLBG.com` localize dynamically by requester IP geolocation **without printing a timezone suffix**.
   - Proof: `2:25 Newmarket` (`event_id=1134655`) renders `Today 09:25` from a US-East (`America/New_York`, `UTC-4`) egress IP (`14:25 BST - 5h = 09:25 EDT`), while `MIL Bucks @ WAS Wizards` (`event_id=534889`, official tipoff `2026-10-21T23:10:00Z` / `7:10 PM EDT`) renders `Today 19:10` on US-East egress and `Tomorrow 00:10` (`BST`, `UTC+1`) on UK egress.
   - **Impact & Mitigation:** Every row in our dataset normalizes timestamps explicitly to **ISO-8601 UTC** verified against official league schedules while also recording OLBG's raw display string.
2. **20-Row Top-Level Feed Truncation Hiding Valid Open Matches:**
   - Top-level sport pages (`/betting-tips/Basketball/4`) cap initial server-rendered match cards at **20 rows** ordered by `win_tips DESC`. Querying competition sub-routes (`/Basketball/NBA/4`, `/Basketball/European/Euroleague/4`, `/Basketball/European/Euro_Cup/4`, `/Basketball/European/Basketball_Champions_League/4`) uncovered **9 additional live basketball matches** (`UTA Jazz @ MEM Grizzlies`, `SAC Kings @ LA Clippers`, `CLE Cavaliers @ PHI 76ers`, `Anadolu Efes vs Besiktas`, `Maccabi Tel Aviv vs Real Madrid`, `Zalgiris vs Asvel Lyon Villeurbanne`, `Napoli vs Tofas`, `Maxima Roma vs Venezia`, `Reggio Emilia vs Juventus`).
3. **Division-by-Zero / Blank Counter Bug on Each-Way-Only Outright Events (`0 / 0 Win Tips`):**
   - On `Hero Womens Indian Open` ([`event_id=101909`](https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Hero_Womens_Indian_Open/5?event_id=101909)) and `T20 Blast 2027` ([`event_id=188350`](https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/T20_Blast_2027/7?event_id=188350)), tipsters placed **Each-Way (`EW @`)** selections with zero straight-win selections. OLBG promotes the golfer/team to the sport feed card with **blank tip counts**, and renders `0 / 0 Win Tips (0%)` directly above the active `EW @` tip on the event page.
4. **Client-Side Odds Hydration Suppression (`WIN @ [blank]`):**
   - Static HTML intentionally omits live bookmaker decimal prices (`WIN @ ` empty text node; `/api/` blocked in `robots.txt`), preventing stale odds indexing by search crawlers and requiring independent mathematical line origination across all markets.
5. **Duplicate Event Cards on Main Feed Across Markets (`event_id=3530`):**
   - On `/betting-tips`, `St Finbarrs v Nemo Rangers` (`event_id=3530`) appears **twice** in consecutive rows once for `Draw` (`10/20 Win Tips`) and once for `Nemo Rangers +1.50` (`10/12 Win Tips`), showing that the global feed ranks `(event_id, market_selection)` pairs rather than deduplicating by `event_id`.
