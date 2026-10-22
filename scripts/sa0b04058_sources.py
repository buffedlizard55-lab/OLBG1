#!/usr/bin/env python3
"""Official source registry, live OLBG 24-sport taxonomy, and reverse-engineering audit
for session a0b04058-olbg1 (TA0B04, 2026-10-22T21:00:00Z UTC).

Every official URL registered here resolves to an exact host in pipeline.config.PUBLISHERS.
OLBG URLs are strictly categorized as upstream discovery/audit endpoints and never verify
sporting facts on their own.
"""
from __future__ import annotations

AS_OF_UTC = "2026-10-22T21:00:00Z"
WINDOW_START_UTC = "2026-10-22T21:00:00Z"
WINDOW_END_UTC = "2026-10-29T21:00:00Z"
SESSION_ID = "a0b04058-olbg1"
SESSION_SLUG = "a0b04058"
TASK_ID = "TA0B04"

# Complete 24-sport OLBG taxonomy probed across sport_id 1..31 on 2026-10-22T20:56Z UTC.
# 17 sports are in scope; 7 are excluded per the project brief.
OLBG_SPORTS = [
    {
        "sport_id": 1, "olbg_slug": "Football", "slug": "football", "name": "Football / Soccer",
        "in_sitemap": True, "in_scope": False, "live_hub_listings_2056z": 20,
        "olbg_url": "https://www.olbg.com/betting-tips/Football/1",
        "official_hub": None,
        "note": "Excluded per brief: soccer / association football.",
    },
    {
        "sport_id": 2, "olbg_slug": "Horse_Racing", "slug": "horse-racing", "name": "Horse Racing",
        "in_sitemap": True, "in_scope": False, "live_hub_listings_2056z": 20,
        "olbg_url": "https://www.olbg.com/betting-tips/Horse_Racing/2",
        "official_hub": None,
        "note": "Excluded per brief: horse racing.",
    },
    {
        "sport_id": 3, "olbg_slug": "Tennis", "slug": "tennis", "name": "Tennis",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 14,
        "olbg_url": "https://www.olbg.com/betting-tips/Tennis/3",
        "official_hub": "https://www.atptour.com/en/scores/current",
        "note": "14 upcoming Fri 23 Oct quarter-finals on live OLBG hub; supplemented with all 16 official QF ties across ATP Almaty, ATP Brussels, ATP Lyon, WTA Ningbo, and WTA Osaka OOP PDFs.",
    },
    {
        "sport_id": 4, "olbg_slug": "Basketball", "slug": "basketball", "name": "Basketball",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 12,
        "olbg_url": "https://www.olbg.com/betting-tips/Basketball/4",
        "official_hub": "https://www.nba.com/standings",
        "note": "Live OLBG hub lists NBA opening-week games, EuroLeague Round 7 Friday slate, and 3 Brazil NBB fixtures; 7 Thursday EuroLeague games already completed/in-play at 21:00Z separated into Elapsed Ledger.",
    },
    {
        "sport_id": 5, "olbg_slug": "Golf", "slug": "golf", "name": "Golf",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 1,
        "olbg_url": "https://www.olbg.com/betting-tips/Golf/5",
        "official_hub": "https://www.pgatour.com/schedule",
        "note": "OLBG hub shows only Stifel Charity Classic outright; supplemented with active PGA Tour Butterfield Bermuda Championship and DP World Tour Genesis Championship (R2–R4 upcoming).",
    },
    {
        "sport_id": 7, "olbg_slug": "Cricket", "slug": "cricket", "name": "Cricket",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 9,
        "olbg_url": "https://www.olbg.com/betting-tips/Cricket/7",
        "official_hub": "https://www.icc-cricket.com/about/cricket/match-officials/match-official-appointments",
        "note": "9 hub items (4 match cards + 5 long-term outrights); supplemented with full NZ v India T20I series, UAE Tri-Series Final & AFG v ZIM T20Is, and SA v AUS 3rd Test.",
    },
    {
        "sport_id": 8, "olbg_slug": "Snooker", "slug": "snooker", "name": "Snooker",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 0,
        "olbg_url": "https://www.olbg.com/betting-tips/Snooker/8",
        "official_hub": "https://www.wst.tv/match-centre/f0b30e58-d987-4505-89c2-8b24805b98d5",
        "note": "OLBG hub dropped to 'No tips found' at 20:56Z after Thursday afternoon ties finished; official WST Match Centre provides Friday 23 Oct Northern Ireland Open Quarter-Finals plus International Championship R2.",
    },
    {
        "sport_id": 9, "olbg_slug": "Rugby_Union", "slug": "rugby-union", "name": "Rugby Union",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 15,
        "olbg_url": "https://www.olbg.com/betting-tips/Rugby_Union/9",
        "official_hub": "https://stats.unitedrugby.com/match-centre/2026-27/4",
        "note": "Full URC Round 4, French Top 14 Journée 7, and French Pro D2 Journée 8 verified against official league match centres.",
    },
    {
        "sport_id": 10, "olbg_slug": "Rugby_League", "slug": "rugby-league", "name": "Rugby League",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 3,
        "olbg_url": "https://www.olbg.com/betting-tips/Rugby_League/10",
        "official_hub": "https://www.intrl.sport/fixtures-results",
        "note": "Zero-tip blind spot on OLBG (only 2027 ante-post markets shown); IRL official match centre confirms 8 RLWC26 Round 2 Men's & Women's fixtures on 23–25 Oct 2026.",
    },
    {
        "sport_id": 11, "olbg_slug": "American_Football", "slug": "american-football", "name": "American Football",
        "in_sitemap": True, "in_scope": False, "live_hub_listings_2056z": 20,
        "olbg_url": "https://www.olbg.com/betting-tips/American_Football/11",
        "official_hub": None,
        "note": "Excluded per brief: American football.",
    },
    {
        "sport_id": 12, "olbg_slug": "Baseball", "slug": "baseball", "name": "Baseball",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 1,
        "olbg_url": "https://www.olbg.com/betting-tips/Baseball/12",
        "official_hub": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29&hydrate=probablePitcher,team,venue",
        "note": "OLBG lists World Series Game 1 (TB Rays @ MIL Brewers); MLB StatsAPI verifies unconditional World Series Games 1–4 plus conditional Game 5 (ifNecessary='Y', flagged).",
    },
    {
        "sport_id": 13, "olbg_slug": "Ice_Hockey", "slug": "ice-hockey", "name": "Ice Hockey",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 16,
        "olbg_url": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
        "official_hub": "https://api-web.nhle.com/v1/schedule/2026-10-22",
        "note": "All 12 Thursday night NHL games (23:00Z–02:00Z, pre-match at 21:00Z) + 2 Friday NHL games verified live via api-web.nhle.com; 4 European minor-league OLBG rows logged unpriced.",
    },
    {
        "sport_id": 14, "olbg_slug": "Motor_Racing", "slug": "motor-racing", "name": "Motor Racing",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 3,
        "olbg_url": "https://www.olbg.com/betting-tips/Motor_Racing/14",
        "official_hub": "https://www.formula1.com/en/racing/2026/united-states",
        "note": "2026 F1 United States Grand Prix at COTA (Qualifying Sat 24 Oct, Race Sun 25 Oct 20:00Z) plus Drivers' Championship and 'Without Antonelli' markets verified on formula1.com.",
    },
    {
        "sport_id": 15, "olbg_slug": "Darts", "slug": "darts", "name": "Darts",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 10,
        "olbg_url": "https://www.olbg.com/betting-tips/Darts/15",
        "official_hub": "https://www.pdc.tv/tournament-hub/10870",
        "note": "8 upcoming Friday 23 Oct Round 1 ties at Westfalenhalle Dortmund verified on pdc.tv; 8 Thursday night ties already underway/elapsed at 21:00Z moved to Elapsed Ledger.",
    },
    {
        "sport_id": 16, "olbg_slug": "Boxing", "slug": "boxing", "name": "Boxing (incl. UFC / MMA)",
        "in_sitemap": True, "in_scope": False, "live_hub_listings_2056z": 12,
        "olbg_url": "https://www.olbg.com/betting-tips/Boxing/16",
        "official_hub": None,
        "note": "Excluded per brief: boxing, UFC, and MMA.",
    },
    {
        "sport_id": 17, "olbg_slug": "Cycling", "slug": "cycling", "name": "Cycling",
        "in_sitemap": True, "in_scope": False, "live_hub_listings_2056z": 1,
        "olbg_url": "https://www.olbg.com/betting-tips/Cycling/17",
        "official_hub": None,
        "note": "Excluded per brief: cycling.",
    },
    {
        "sport_id": 18, "olbg_slug": "Specials", "slug": "specials", "name": "Specials / Entertainment",
        "in_sitemap": False, "in_scope": False, "live_hub_listings_2056z": 0,
        "olbg_url": "https://www.olbg.com/betting-tips/Specials/18",
        "official_hub": None,
        "note": "Active HTTP 200 hub omitted from sitemap-betting-tips.xml; excluded per brief: specials.",
    },
    {
        "sport_id": 20, "olbg_slug": "Handball", "slug": "handball", "name": "Handball",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 16,
        "olbg_url": "https://www.olbg.com/betting-tips/Handball/20",
        "official_hub": "https://ehfcl.eurohandball.com/men/2026-27/standings/",
        "note": "EHF Champions League Men Round 6 ties + Women's international qualifiers verified on eurohandball.com; domestic French/German/Spanish league OLBG rows logged with explicit host-scope flag.",
    },
    {
        "sport_id": 21, "olbg_slug": "Volleyball", "slug": "volleyball", "name": "Volleyball",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 15,
        "olbg_url": "https://www.olbg.com/betting-tips/Volleyball/21",
        "official_hub": "https://www.legavolley.it/calendario/?idCampionato=999",
        "note": "Italian SuperLega Credem Banca Round 2 (25 Oct) and Polish PlusLiga fixtures verified via legavolley.it and plusliga.pl/tauronliga.pl; non-PUBLISHERS domestic rows flagged.",
    },
    {
        "sport_id": 22, "olbg_slug": "Aussie_Rules", "slug": "aussie-rules", "name": "Aussie Rules",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 0,
        "olbg_url": "https://www.olbg.com/betting-tips/Aussie_Rules/22",
        "official_hub": "https://www.afl.com.au/aflw/news/1634321/aflw-r11-preview-contenders-melbourne-western-bulldogs-meet-in-blockbuster-race-for-eighth-heats-up",
        "note": "Zero-tip blind spot on OLBG ('No tips found'); afl.com.au confirms full NAB AFLW Round 11 weekend slate (23–25 Oct 2026).",
    },
    {
        "sport_id": 23, "olbg_slug": "eSports", "slug": "esports", "name": "eSports",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 0,
        "olbg_url": "https://www.olbg.com/betting-tips/eSports/23",
        "official_hub": "https://lolesports.com/en-US/tournament/115660540725177488/overview",
        "note": "Zero-tip blind spot on OLBG ('No tips found') + case-sensitive router bug (/ESports/23 fails); lolesports.com confirms all 8 LoL Worlds 2026 Swiss Round 1 Bo1 matches on Fri 23 Oct.",
    },
    {
        "sport_id": 25, "olbg_slug": "Gaelic_Football", "slug": "gaelic-football", "name": "Gaelic Football",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 6,
        "olbg_url": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
        "official_hub": "https://munster.gaa.ie/fixtures/events-calendar/",
        "note": "Borderline-scope note (GAA Football retained across all repo desks); 5 County SFC Finals on live OLBG plus Kerry SFC Final verified via Munster GAA, Cork GAA & Maigh Cuilinn.",
    },
    {
        "sport_id": 26, "olbg_slug": "Hurling", "slug": "hurling", "name": "Hurling",
        "in_sitemap": False, "in_scope": False, "live_hub_listings_2056z": 2,
        "olbg_url": "https://www.olbg.com/betting-tips/Hurling/26",
        "official_hub": "https://munster.gaa.ie/fixtures/events-calendar/",
        "note": "Active HTTP 200 hub omitted from XML sitemap (carries Ballyhale Shamrocks v Tullaroan event_id=714 & All-Ireland 2027 event_id=675); excluded per brief: hurling.",
    },
    {
        "sport_id": 28, "olbg_slug": "Greyhounds", "slug": "greyhounds", "name": "Greyhounds",
        "in_sitemap": True, "in_scope": True, "live_hub_listings_2056z": 0,
        "olbg_url": "https://www.olbg.com/betting-tips/Greyhounds/28",
        "official_hub": "https://www.gbgb.org.uk/racing/open-races/2025-category-one-schedule/",
        "note": "All 6 daytime UK cards on 22 Oct completed prior to 20:56Z; GBGB official reports verify all 3 weekend Category One Finals (Coral Champion Stakes, Oaks Final, Scurry Gold Cup Final).",
    },
]

IN_SCOPE_SPORTS = [s for s in OLBG_SPORTS if s["in_scope"]]
EXCLUDED_SPORTS = [s for s in OLBG_SPORTS if not s["in_scope"]]

# Reverse-engineering findings documented live at 2026-10-22T20:56Z UTC.
REVERSE_ENGINEERING_FINDINGS = [
    {
        "id": "RE-01",
        "title": "Four-Layer Server-Rendered URL Grammar with Zero Public JSON Feed",
        "evidence_url": "https://www.olbg.com/sitemap-betting-tips.xml",
        "official_cross_check_url": "https://api-web.nhle.com/v1/schedule/2026-10-22",
        "summary": "OLBG serves server-rendered HTML across /betting-tips/{Sport}/{id}, /betting-tips/{Sport}/{Region}/{Comp}/{id}, event cards (?event_id=N), and /best-tipsters/{Sport}/{id}, embedding tip counts and percentages directly in HTML without an XHR JSON match feed.",
    },
    {
        "id": "RE-02",
        "title": "Non-Contiguous Numeric IDs (1..28) & Two Active Unlisted Category Hubs (IDs 18 & 26)",
        "evidence_url": "https://www.olbg.com/betting-tips/Hurling/26",
        "official_cross_check_url": "https://munster.gaa.ie/fixtures/events-calendar/",
        "summary": "sitemap-betting-tips.xml lists 22 sports and omits Specials (/betting-tips/Specials/18) and Hurling (/betting-tips/Hurling/26, carrying event_id=714 Ballyhale Shamrocks v Tullaroan). IDs 6, 19, 24, 27, 29–31 are inactive.",
    },
    {
        "id": "RE-03",
        "title": "Unlabelled EDT (UTC-4) vs BST (UTC+1) 5-Hour Clock Split Across Routes",
        "evidence_url": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
        "official_cross_check_url": "https://api-web.nhle.com/v1/schedule/2026-10-22",
        "summary": "At 20:56Z UTC on 22 Oct, /betting-tips/Ice_Hockey/13 rendered BOS Bruins vs NSH Predators (23:00Z official start) as 'Today 19:07' (EDT, UTC-4), while /betting-tips/Basketball/4 rendered CLE @ PHI (23:00Z official start) as 'Tomorrow 00:10' (BST, UTC+1) with no timezone badge on either page.",
    },
    {
        "id": "RE-04",
        "title": "Zero-Tip Suppression Hiding Major Active Championships",
        "evidence_url": "https://www.olbg.com/betting-tips/Rugby_League/10",
        "official_cross_check_url": "https://www.intrl.sport/fixtures-results",
        "summary": "OLBG suppresses any scheduled match with 0 community tips. At 20:56Z UTC on 22 Oct, Snooker (/8), Aussie Rules (/22), eSports (/23), Greyhounds (/28), and match-level Rugby League (/10) showed 0 match rows despite WST Northern Ireland Open QFs, NAB AFLW Round 11, LoL Worlds Swiss Stage, GBGB Cat 1 Finals, and 8 RLWC26 Round 2 tests all running on 23–25 Oct.",
    },
    {
        "id": "RE-05",
        "title": "Case-Sensitive Router Trap on /betting-tips/eSports/23",
        "evidence_url": "https://www.olbg.com/betting-tips/eSports/23",
        "official_cross_check_url": "https://lolesports.com/en-US/tournament/115660540725177488/overview",
        "summary": "Capitalized variants such as /betting-tips/ESports/23 return HTTP 200 with a soft error template instead of redirecting to canonical /betting-tips/eSports/23.",
    },
    {
        "id": "RE-06",
        "title": "Upstream Fixture Date & Club Name Errors on Live Event Cards",
        "evidence_url": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
        "official_cross_check_url": "https://munster.gaa.ie/fixtures/events-calendar/",
        "summary": "Live /betting-tips/Gaelic_Football/25 lists Rathgormack v The Nire (event_id=3536) at '01 Nov 15:30', whereas Munster GAA's official calendar confirms throw-in is Sunday 25 Oct 2026 at 14:30 UTC at Cappoquin Logistics Fraher Field, Dungarvan.",
    },
]

# Official governing-body sources read directly in session a0b04058-olbg1 (all hosts in PUBLISHERS).
OFFICIAL_SOURCES = [
    {
        "id": "SRC-NHL-SCHED", "sport": "ice-hockey", "publisher": "NHL",
        "title": "NHL Official Web API Schedule (2026-10-22 through 2026-10-28)",
        "url": "https://api-web.nhle.com/v1/schedule/2026-10-22",
        "checked_utc": "2026-10-22T20:57:00Z", "role": "Pre-match UTC starts, venues, game IDs",
    },
    {
        "id": "SRC-NHL-STAND", "sport": "ice-hockey", "publisher": "NHL",
        "title": "NHL Official Standings Table (as of 2026-10-22T20:57:30Z)",
        "url": "https://api-web.nhle.com/v1/standings/now",
        "checked_utc": "2026-10-22T20:57:30Z", "role": "All 32 clubs W-L-OTL, GF/GA, Home/Road & L10 splits, streaks",
    },
    {
        "id": "SRC-NHL-LEADERS", "sport": "ice-hockey", "publisher": "NHL",
        "title": "NHL Official 2026-27 Skater Leaders (Goals & Points Top 25)",
        "url": "https://api-web.nhle.com/v1/skater-stats-leaders/current?categories=points,goals&limit=25",
        "checked_utc": "2026-10-22T21:01:00Z", "role": "Verified 2026-27 player goals & points totals",
    },
    {
        "id": "SRC-NHL-SCORES", "sport": "ice-hockey", "publisher": "NHL",
        "title": "NHL Official Game Scores & Scorers (2026-10-21)",
        "url": "https://api-web.nhle.com/v1/score/2026-10-21",
        "checked_utc": "2026-10-22T21:01:00Z", "role": "Recent NHL match results & goal scorers",
    },
    {
        "id": "SRC-NBA-STAND", "sport": "basketball", "publisher": "NBA",
        "title": "NBA Official 2026-27 Regular Season Standings",
        "url": "https://www.nba.com/standings",
        "checked_utc": "2026-10-22T20:57:30Z", "role": "Opening-week W-L, Home/Road & streak records across all 30 clubs",
    },
    {
        "id": "SRC-NBA-PHI", "sport": "basketball", "publisher": "NBA",
        "title": "NBA Official Game Summary & Team Schedule: Cavaliers @ 76ers (0022600006)",
        "url": "https://www.nba.com/game/cle-vs-phi-0022600006",
        "checked_utc": "2026-10-22T20:59:00Z", "role": "Tip-off time, venue, Opening Night 106-100 PHI @ NYK recap & roster context",
    },
    {
        "id": "SRC-NBA-OKC", "sport": "basketball", "publisher": "NBA",
        "title": "NBA Official Game Summary & Team Schedule: Nuggets @ Thunder (0022600007)",
        "url": "https://www.nba.com/game/den-vs-okc-0022600007",
        "checked_utc": "2026-10-22T20:59:00Z", "role": "Tip-off time, Paycom Center venue, OKC 116-104 SAS opener & SGA 32 pts",
    },
    {
        "id": "SRC-NBA-SCHED", "sport": "basketball", "publisher": "NBA",
        "title": "NBA Official 2026-27 American Express Tip-Off Week Schedule & Recaps",
        "url": "https://www.nba.com/news/2026-27-nba-regular-season-schedule",
        "checked_utc": "2026-10-22T20:59:00Z", "role": "Verified Friday Oct 23 Prime doubleheader (NYK @ BOS, HOU @ SAS Moody Center)",
    },
    {
        "id": "SRC-EL-STAND", "sport": "basketball", "publisher": "Euroleague Basketball",
        "title": "EuroLeague 2026-27 Official Regular Season Standings (Live Round 7 Update)",
        "url": "https://www.euroleaguebasketball.net/en/euroleague/standings/",
        "checked_utc": "2026-10-22T20:58:00Z", "role": "All 20 EuroLeague clubs GP, W-L, PTS+/PTS-, Home/Away splits",
    },
    {
        "id": "SRC-EL-R7", "sport": "basketball", "publisher": "Euroleague Basketball",
        "title": "EuroLeague 2026-27 Round 7 Game Center & Injury Report",
        "url": "https://www.euroleaguebasketball.net/en/euroleague/news/injury-report-round-7-fantasy/",
        "checked_utc": "2026-10-22T20:59:00Z", "role": "Friday Oct 23 tip times, player availability, Round 6 results",
    },
    {
        "id": "SRC-ATP-ALMATY", "sport": "tennis", "publisher": "ATP draw service",
        "title": "ATP 250 Almaty Open Official Friday 23 Oct Order of Play PDF",
        "url": "https://www.protennislive.com/posting/2026/9410/op.pdf",
        "checked_utc": "2026-10-22T21:00:00Z", "role": "Verified Friday Oct 23 Center Court & Court 1 singles quarter-finals",
    },
    {
        "id": "SRC-ATP-BRUSSELS", "sport": "tennis", "publisher": "ATP draw service",
        "title": "ATP 250 BNP Paribas Fortis European Open Brussels Official Friday 23 Oct OOP PDF",
        "url": "https://www.protennislive.com/posting/2026/7485/op.pdf",
        "checked_utc": "2026-10-22T21:01:00Z", "role": "Verified Friday Oct 23 Brussels singles quarter-finals",
    },
    {
        "id": "SRC-ATP-LYON", "sport": "tennis", "publisher": "ATP draw service",
        "title": "ATP Open Auvergne-Rhône-Alpes Lyon Official Friday 23 Oct OOP PDF",
        "url": "https://www.protennislive.com/posting/2026/496/op.pdf",
        "checked_utc": "2026-10-22T21:01:00Z", "role": "Verified Friday Oct 23 Court Central singles quarter-finals",
    },
    {
        "id": "SRC-WTA-NINGBO", "sport": "tennis", "publisher": "WTA",
        "title": "WTA 500 BNB Ningbo Open Official Friday 23 Oct Order of Play PDF",
        "url": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",
        "checked_utc": "2026-10-22T21:00:00Z", "role": "Verified Friday Oct 23 Ningbo Center Court quarter-finals",
    },
    {
        "id": "SRC-WTA-OSAKA", "sport": "tennis", "publisher": "WTA",
        "title": "WTA 250 Kinoshita Group Japan Open Osaka Official Friday 23 Oct OOP PDF",
        "url": "https://wtafiles.wtatennis.com/pdf/draws/2026/405/OP.pdf",
        "checked_utc": "2026-10-22T21:01:00Z", "role": "Verified Friday Oct 23 Osaka Center Court quarter-finals",
    },
    {
        "id": "SRC-MLB-WS", "sport": "baseball", "publisher": "MLB",
        "title": "MLB StatsAPI 2026 World Series Schedule & Probable Pitchers (TB @ MIL)",
        "url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-22&endDate=2026-10-29&hydrate=probablePitcher,team,venue",
        "checked_utc": "2026-10-22T20:58:00Z", "role": "Games 1–4 unconditional schedule, probable starters, conditional Game 5 flag",
    },
    {
        "id": "SRC-MLB-STAND", "sport": "baseball", "publisher": "MLB",
        "title": "MLB StatsAPI 2026 Final Regular Season Standings & ALCS/NLCS Decisions",
        "url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026&standingsTypes=regularSeason",
        "checked_utc": "2026-10-22T21:02:00Z", "role": "Brewers (103-59, 832 RS / 618 RA) & Rays (98-64, 736 RS / 650 RA) + postseason logs",
    },
    {
        "id": "SRC-PDC-EC", "sport": "darts", "publisher": "Professional Darts Corporation",
        "title": "PDC 2026 Machineseeker European Championship Official Tournament Hub & Schedule",
        "url": "https://www.pdc.tv/tournament-hub/10870",
        "checked_utc": "2026-10-22T20:59:00Z", "role": "All 16 Round 1 ties, exact Friday Oct 23 CEST/UTC slots, European Tour seedings",
    },
    {
        "id": "SRC-PDC-PREVIEW", "sport": "darts", "publisher": "Professional Darts Corporation",
        "title": "PDC 2026 European Championship Preview & ET15 Maastricht Results",
        "url": "https://www.pdc.tv/news/2026/october/21/2026-machineseeker-european-championship-preview/",
        "checked_utc": "2026-10-22T20:59:00Z", "role": "Player ET titles, Maastricht results, Huybrechts replacement for Humphries",
    },
    {
        "id": "SRC-WST-MC", "sport": "snooker", "publisher": "World Snooker Tour",
        "title": "WST BetVictor Northern Ireland Open 2026 Live Match Centre & Quarter-Final Draw",
        "url": "https://www.wst.tv/match-centre/f0b30e58-d987-4505-89c2-8b24805b98d5",
        "checked_utc": "2026-10-22T20:58:00Z", "role": "Live R3 status, Friday Oct 23 Belfast Quarter-Finals & Oct 30 International Championship",
    },
    {
        "id": "SRC-WST-RANK", "sport": "snooker", "publisher": "World Snooker Tour",
        "title": "WST Johnstone's Paint World Rankings, One-Year List & Season Centuries",
        "url": "https://www.wst.tv/rankings/",
        "checked_utc": "2026-10-22T20:58:30Z", "role": "Official rankings, prize money & century break totals",
    },
    {
        "id": "SRC-URC-R4", "sport": "rugby-union", "publisher": "URC",
        "title": "United Rugby Championship 2026-27 Round 4 Match Centre & League Table",
        "url": "https://stats.unitedrugby.com/match-centre/2026-27/4",
        "checked_utc": "2026-10-22T20:59:00Z", "role": "Round 4 fixtures, venues, Round 3 scores, 16-club table & bonus points",
    },
    {
        "id": "SRC-TOP14-J7", "sport": "rugby-union", "publisher": "Ligue Nationale de Rugby",
        "title": "LNR TOP 14 2026-27 Journée 7 & PRO D2 Journée 8 Official Calendars",
        "url": "https://top14.lnr.fr/calendrier-et-resultats",
        "checked_utc": "2026-10-22T20:59:00Z", "role": "Official kick-offs, league rankings & match sheets for Top 14 J7 & Pro D2 J8",
    },
    {
        "id": "SRC-IRL-RLWC", "sport": "rugby-league", "publisher": "International Rugby League",
        "title": "IRL Rugby League World Cup 2026 Round 2 Fixtures, Round 1 Reports & World Rankings",
        "url": "https://www.intrl.sport/fixtures-results",
        "checked_utc": "2026-10-22T20:59:00Z", "role": "RLWC26 Men's & Women's Round 2 fixtures, Round 1 try scorers, IRL World Rankings",
    },
    {
        "id": "SRC-NZC-IND", "sport": "cricket", "publisher": "New Zealand Cricket",
        "title": "NZC Official Match Centre: BLACKCAPS vs India 2026-27 T20I Series",
        "url": "https://scoring.nzc.nz/fixtures",
        "checked_utc": "2026-10-22T21:02:00Z", "role": "2nd & 3rd T20I UTC times, venues, squads & 1st T20I Christchurch result",
    },
    {
        "id": "SRC-ICC-APPT", "sport": "cricket", "publisher": "ICC",
        "title": "ICC Official Match Schedule, Squads & Match Officials (UAE Tri-Series, NZ-IND, SA-AUS)",
        "url": "https://www.icc-cricket.com/about/cricket/match-officials/match-official-appointments",
        "checked_utc": "2026-10-22T21:02:00Z", "role": "AFG-ZIM Sharjah ODI Final & T20I series, SA-AUS 3rd Test Newlands, official squads",
    },
    {
        "id": "SRC-VOLLEY-IT", "sport": "volleyball", "publisher": "Lega Pallavolo Serie A",
        "title": "SuperLega Credem Banca 2026-27 Official Calendar & Giornata 1 Results",
        "url": "https://www.legavolley.it/calendario/?idCampionato=999",
        "checked_utc": "2026-10-22T21:01:00Z", "role": "Giornata 2 Sunday Oct 25 matches, venues & Giornata 1 exact set scores",
    },
    {
        "id": "SRC-VOLLEY-PL", "sport": "volleyball", "publisher": "Polish professional volleyball league",
        "title": "PlusLiga 2026-27 Official Fixtures, Rosters & Results",
        "url": "https://www.plusliga.pl/teams/id/62.html",
        "checked_utc": "2026-10-22T21:01:00Z", "role": "Polish PlusLiga Oct 23–25 fixtures, club rosters & recent set scores",
    },
    {
        "id": "SRC-EHF-CL", "sport": "handball", "publisher": "EHF",
        "title": "EHF Champions League Men 2026-27 Group Standings, Round 5 Review & Playing Times",
        "url": "https://ehfcl.eurohandball.com/men/2026-27/standings/",
        "checked_utc": "2026-10-22T21:00:00Z", "role": "Group standings, Round 5 scores (Oct 21) & Round 6 schedule (Oct 28–29)",
    },
    {
        "id": "SRC-AFLW-R11", "sport": "aussie-rules", "publisher": "Australian Football League",
        "title": "NAB AFLW 2026 Round 11 Official Preview, Team Line-Ups & Ladder",
        "url": "https://www.afl.com.au/aflw/news/1634321/aflw-r11-preview-contenders-melbourne-western-bulldogs-meet-in-blockbuster-race-for-eighth-heats-up",
        "checked_utc": "2026-10-22T21:00:00Z", "role": "Round 11 fixtures, venues, confirmed ins/outs & 10-round ladder stats",
    },
    {
        "id": "SRC-LOL-WORLDS", "sport": "esports", "publisher": "Riot Games / LoL Esports",
        "title": "LoL Esports Worlds 2026 Swiss Stage Overview, Rosters & Global Power Rankings",
        "url": "https://lolesports.com/en-US/tournament/115660540725177488/overview",
        "checked_utc": "2026-10-22T21:01:00Z", "role": "All 8 Swiss Round 1 Bo1 matches (Oct 23, Allen TX), team rosters & GPR scores",
    },
    {
        "id": "SRC-GAA-MUNSTER", "sport": "gaelic-football", "publisher": "Munster GAA",
        "title": "Munster GAA Official Events Calendar & Cork / Galway County Finals",
        "url": "https://munster.gaa.ie/fixtures/events-calendar/",
        "checked_utc": "2026-10-22T21:00:00Z", "role": "Cork PSFC, Cork SAFC, Waterford SFC, Kerry SFC & Galway SFC Final dates/venues",
    },
    {
        "id": "SRC-GAA-CORK", "sport": "gaelic-football", "publisher": "Cork GAA",
        "title": "Cork GAA Official Fixtures & Semi-Final Results Hub",
        "url": "https://gaacork.ie/fixtures/",
        "checked_utc": "2026-10-22T21:00:30Z", "role": "St Finbarr's v Nemo Rangers (Oct 25) & Kanturk v Éire Óg (Nov 1), semi-final scores & referees",
    },
    {
        "id": "SRC-GAA-GALWAY", "sport": "gaelic-football", "publisher": "Maigh Cuilinn GAA",
        "title": "CLG Maigh Cuilinn Official Galway SFC Final Notice",
        "url": "https://www.maighcuilinn.com/",
        "checked_utc": "2026-10-22T21:00:30Z", "role": "Moycullen v Salthill-Knocknacarra Galway SFC Final (Sat 24 Oct, Pearse Stadium)",
    },
    {
        "id": "SRC-PGA-BERMUDA", "sport": "golf", "publisher": "PGA TOUR",
        "title": "PGA TOUR Butterfield Bermuda Championship Leaderboard & Stifel Charity Classic Overview",
        "url": "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/overview",
        "checked_utc": "2026-10-22T21:00:00Z", "role": "Port Royal GC field, R1 scores (63 co-leaders) & Stifel Charity Classic Schwab Playoffs",
    },
    {
        "id": "SRC-DPWT-GENESIS", "sport": "golf", "publisher": "European Tour",
        "title": "DP World Tour 2026 Genesis Championship Official Hub & Round 1 Report",
        "url": "https://www.europeantour.com/dpworld-tour/genesis-championship-2026/",
        "checked_utc": "2026-10-22T21:02:00Z", "role": "Woo Jeong Hills CC Cheonan R1 scores (Casey Jarvis -6, Sanghun Shin -5) & field rankings",
    },
    {
        "id": "SRC-F1-USGP", "sport": "motor-racing", "publisher": "Formula 1",
        "title": "Formula 1 2026 United States Grand Prix Official Hub & Drivers' Standings",
        "url": "https://www.formula1.com/en/racing/2026/united-states",
        "checked_utc": "2026-10-22T21:00:00Z", "role": "COTA session times, 56-lap distance, 2026 Drivers' Standings (Antonelli 340, Russell 238, Verstappen 221)",
    },
    {
        "id": "SRC-GBGB-CAT1", "sport": "greyhounds", "publisher": "Greyhound Board of Great Britain",
        "title": "GBGB 2026 Category One Schedule & Oaks / Scurry Gold Cup / Champion Stakes Final Reports",
        "url": "https://www.gbgb.org.uk/signet-nayla-chases-oaks-glory-as-hutton-targets-dunstall-park-double/",
        "checked_utc": "2026-10-22T21:00:00Z", "role": "Official qualifiers, heat/semi-final clockings & trainers for all 3 weekend GBGB Cat 1 Finals",
    },
]

SOURCE_BY_ID = {s["id"]: s for s in OFFICIAL_SOURCES}
