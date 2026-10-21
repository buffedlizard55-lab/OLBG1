# OLBG.com Reverse-Engineering & Platform Audit (2026-10-21 UTC)

## 1. Canonical URL Grammar & Router Mechanics

`OLBG.com` serves server-rendered HTML with **no public JSON feed**. Every betting-tips URL resolves through four route layers keyed on both `{Sport_Slug}` (case-sensitive) and integer `{sport_id}`:

```text
1. Sport Hub        : https://www.olbg.com/betting-tips/{Sport_Slug}/{sport_id}
2. Competition Hub  : https://www.olbg.com/betting-tips/{Sport_Slug}/{Region}/{Competition_Slug}/{sport_id}
3. Event Market Card: https://www.olbg.com/betting-tips/{Sport_Slug}/{Region}/{Comp}/{Participant_A}_v_{Participant_B}/{sport_id}?event_id={event_id}
4. Tipster Rankings : https://www.olbg.com/best-tipsters/{Sport_Slug}/{sport_id}
```

### Key Router Behaviours Verified Live
1. **Case-sensitive `{Sport_Slug}` enforcement:** `/betting-tips/eSports/23` renders the canonical eSports hub (`<title>eSports Betting Tips - Dota 2, CSGO, LoL Predictions and more - OLBG.com</title>`), whereas `/betting-tips/ESports/23` falls back to a soft error screen while still returning HTTP `200`.
2. **Non-contiguous IDs (`1..28`) + 2 Unlisted Active Hubs (`18`, `26`):** `https://www.olbg.com/sitemap-betting-tips.xml` exposes **22** sport hubs, omitting two live HTTP `200` hubs discovered by probing IDs `1..31`:
   - **`18` = `Specials`** (`/betting-tips/Specials/18` — active hub, excluded by brief)
   - **`26` = `Hurling`** (`/betting-tips/Hurling/26` — cross-linked directly from `/betting-tips/Gaelic_Football/25`, carrying live match `event_id=714` `Ballyhale Shamrocks v Tullaroan` and outright `event_id=675` `All Ireland Hurling Championship 2027`, excluded by brief)
   - Unused / retired IDs in `1..31`: `6, 19, 24, 27, 29, 30, 31`.

---

## 2. All 24 Active OLBG Sports (`17` In Scope · `7` Excluded)

| ID | Canonical Slug | Sport Name | XML Sitemap | Scope | Live OLBG Events (`2026-10-21`) | Governing-Body Verification |
|---:|---|---|---|---|---:|---|
| 1 | `Football` | Football | Yes | **Excluded** | 20+ | Excluded (`football` / `soccer`) |
| 2 | `Horse_Racing` | Horse Racing | Yes | **Excluded** | 20+ | Excluded (`horse racing`) |
| 3 | `Tennis` | Tennis | Yes | **In Scope** | 20 | Verified on `atptour.com` & `wtatennis.com` (Almaty, Lyon, Brussels, Ningbo, Osaka) |
| 4 | `Basketball` | Basketball | Yes | **In Scope** | 29 (20 hub + 9 sub-route) | Verified on `nba.com` & `euroleaguebasketball.net` (NBA, EuroLeague R7, EuroCup R4) |
| 5 | `Golf` | Golf | Yes | **In Scope** | 10 outrights | Verified on `pgatour.com` & `europeantour.com` (Bermuda, Genesis, Stifel Charity Classic) |
| 7 | `Cricket` | Cricket | Yes | **In Scope** | 9 matches + 5 outrights | Verified on `icc-cricket.com`, `scoring.nzc.nz` & `cricket.com.au` |
| 8 | `Snooker` | Snooker | Yes | **In Scope** | 6 matches | Verified on `wst.tv` (BetVictor Northern Ireland Open, Waterfront Hall, Belfast) |
| 9 | `Rugby_Union` | Rugby Union | Yes | **In Scope** | 15 matches + 1 outright | Verified on `unitedrugby.com` (URC R4) & `top14.lnr.fr` (Top 14 J7) |
| 10 | `Rugby_League` | Rugby League | Yes | **In Scope** | 3 ante-post outrights (0 matches) | **OLBG Blind Spot #1:** Verified **7 RLWC26 Round 2 ties** live on `nrl.com` (23–25 Oct) |
| 11 | `American_Football` | American Football | Yes | **Excluded** | 20+ | Excluded (`american football`) |
| 12 | `Baseball` | Baseball | Yes | **In Scope** | 1 match (`event_id=160789`) | Verified Games 1–4 of 2026 World Series (`TB @ MIL` / `MIL @ TB`) on `statsapi.mlb.com` |
| 13 | `Ice_Hockey` | Ice Hockey | Yes | **In Scope** | 7 matches (`event_id=199896..901`) | Verified NHL schedule & full standings on `api-web.nhle.com` |
| 14 | `Motor_Racing` | Motor Racing | Yes | **In Scope** | 1 GP + 2 outrights | Verified F1 Round 18 US GP at Circuit of The Americas (`2026-10-25T20:00:00Z`) on `formula1.com` |
| 15 | `Darts` | Darts | Yes | **In Scope** | 16 matches + 2 outrights | Verified all **16** European Championship R1 ties + seeds `1..32` on `pdc.tv` |
| 16 | `Boxing` | Boxing (incl. UFC/MMA) | Yes | **Excluded** | 12 | Excluded (`boxing` / `ufc` / `mma`) |
| 17 | `Cycling` | Cycling | Yes | **Excluded** | 1 | Excluded (`cycling`) |
| 18 | `Specials` | Specials | **No** | **Excluded** | 0 | Excluded (`specials`) |
| 20 | `Handball` | Handball | Yes | **In Scope** | 20 matches (`event_id=12044..55`) | Verified all **12** EHF Champions League Men Round 5 ties + standings on `eurohandball.com` |
| 21 | `Volleyball` | Volleyball | Yes | **In Scope** | 15 matches (`event_id=36945..86`) | Verified SuperLega Credem Banca R2 (`legavolley.it`) & Polish PlusLiga (`plusliga.pl`) |
| 22 | `Aussie_Rules` | Aussie Rules | Yes | **In Scope** | 0 (`No tips found`) | **OLBG Blind Spot #2:** Verified all **9** 2026 NAB AFLW Round 11 fixtures on `afl.com.au/aflw` |
| 23 | `eSports` | eSports | Yes | **In Scope** | 0 (`No tips found`) | **OLBG Blind Spot #3:** Verified LoL Worlds 2026 Swiss Round 1 (`TSW vs LYON`) on `lolesports.com` |
| 25 | `Gaelic_Football` | Gaelic Football | Yes | **In Scope*** | 4 matches + 1 outright | Verified 4 County SFC Finals on `munster.gaa.ie`, `gaacork.ie` & `galwaygaa.ie` (*borderline flagged*) |
| 26 | `Hurling` | Hurling | **No** | **Excluded** | 1 match + 1 outright | Excluded (`hurling`) |
| 28 | `Greyhounds` | Greyhounds | Yes | **In Scope** | 6 racecards (`event_id=689383..90`) | Verified UK racecards & GBGB Category 1 Open Calendar on `gbgb.org.uk` |

---

## 3. Five Platform Anomalies Proven Reproducibly on Live `OLBG.com`

1. **Unlabelled `EDT (UTC-4)` vs `BST (UTC+1)` 5-Hour Clock Split:**
   - On `/betting-tips/Basketball/4`, `event_id=534889` (`MIL Bucks @ WAS Wizards`) renders **`Today 19:10`** (`America/New_York`, `UTC-4`), whereas `/betting-tips/Basketball/NBA/4` renders the exact same `event_id=534889` as **`Tomorrow 00:10`** (`Europe/London`, `UTC+1`) — with **no timezone label on either page**.
   - Definitive proof on `/betting-tips/Greyhounds/28`: race **`11:14 Kinsley`** (`event_id=689388`, 11:14 BST = `10:14 UTC`) renders start time **`Today 06:14`** (`10:14 UTC − 4h = 06:14 EDT`).
2. **Upstream Fixture Date Error (`event_id=3536`, Waterford SFC Final):**
   - `/betting-tips/Gaelic_Football/25` displays `Rathgormack v The Nire` at **`01 Nov 10:30`**, whereas official Munster GAA (`https://munster.gaa.ie/fixtures/munster-gaa-fixtures/`) confirms the Waterford County Senior Football Championship Final kicks off **Sunday 25 October 2026 at `14:30 UTC`** at Fraher Field, Dungarvan.
3. **Outdated Club Name (`event_id=12045`, EHF Champions League Group E):**
   - `/betting-tips/Handball/20` lists **`Dinamo Bucuresti vs Skanderborg Handbold`**, whereas the European Handball Federation (`eurohandball.com`) registers the Danish club as **`SAH Aarhus`**.
4. **Each-Way Outright `0/0` Consensus Bug:**
   - Outright markets with Each-Way-only tips and zero straight Win tips render `0/0 Win Tips (0%)` on hub cards.
5. **Zero-Tip Suppression Hiding Major Active Championships:**
   - Because OLBG hides matches until at least one tipster posts a pick, three major international/national championships active during `21–25 Oct 2026` — **2026 Rugby League World Cup Round 2**, **2026 NAB AFLW Round 11**, and **LoL Worlds 2026 Swiss Stage** — are completely invisible on `OLBG.com`.
