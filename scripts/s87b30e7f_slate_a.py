#!/usr/bin/env python3
"""Official-source upcoming fixtures, originated multi-market parameters, and unique
human-written predictions for Sports 1-8 (40 fixtures) — Session 87b30e7f (T87B3).
"""
from __future__ import annotations

from typing import Any
from scripts.s87b30e7f_models import (
    price_field_event,
    price_normal_match,
    price_poisson_match,
    price_race_match,
)


def build_slate_part_a() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    # =========================================================================
    # 1. BASKETBALL (OLBG ID 4) — 5 upcoming NBA Regular Season games (>= 00:00Z)
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-BK-01",
                "sport": "basketball",
                "sport_name": "Basketball",
                "olbg_sport_id": 4,
                "competition": "NBA Regular Season",
                "event": "Detroit Pistons @ Miami Heat",
                "away": "Detroit Pistons",
                "home": "Miami Heat",
                "venue": "Kaseya Center, Miami, FL",
                "start_utc": "2026-10-24T00:00:00Z",
                "official_source_name": "NBA Official Referee Injury Report (2026-10-23 3:45 PM ET)",
                "official_source_url": "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-23_03_45PM.pdf",
                "secondary_source_url": "https://www.nba.com/news/starting-5-october-23-2026",
                "olbg_url": "https://www.olbg.com/betting-tips/Basketball/4",
                "form_summary": "Early-season Eastern Conference opener in Miami; both active NBA rotations cleared",
                "stats_summary": "Miami half-court defense holds home pace near 97.5 possessions; Detroit active rotation intact",
                "injury_summary": "MIA: Vladislav Goldin Available (ankle), Dru Smith Available (calf). DET: Taurean Prince Available; two-ways Harkless/Jones/Onyenso Out.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Miami Heat",
                    "Detroit Pistons",
                    mu_margin_a=4.1,
                    sigma_margin=11.8,
                    mu_total=217.2,
                    sigma_total=15.4,
                    spread_a=-4.5,
                    total_line=219.5,
                    unit_label="Point",
                ),
                "winner_pick": "Miami Heat",
                "pick_market": "winner",
                "pick_selection": "Miami Heat",
                "confidence": "high",
                "prediction_text": (
                    "Back Miami Heat on the moneyline in Friday night's home opener at Kaseya Center against the "
                    "Detroit Pistons. Miami's afternoon injury filing upgraded both Dru Smith (right calf) and "
                    "Vladislav Goldin (right ankle) to available, giving Erik Spoelstra a complete active rotation, "
                    "while Detroit only sits two-way assignees Elijah Harkless, Isaac Jones, and Ugonna Onyenso "
                    "alongside an available Taurean Prince. Miami's half-court ball pressure and late-clock execution "
                    "historically drag early-season Eastern visitors below 107 points per 100 possessions, creating "
                    "a four-point home edge."
                ),
            },
            {
                "id": "87b3-BK-02",
                "sport": "basketball",
                "sport_name": "Basketball",
                "olbg_sport_id": 4,
                "competition": "NBA Regular Season (I-35 Series)",
                "event": "Houston Rockets @ San Antonio Spurs",
                "away": "Houston Rockets",
                "home": "San Antonio Spurs",
                "venue": "Moody Center, Austin, TX",
                "start_utc": "2026-10-24T01:30:00Z",
                "official_source_name": "San Antonio Spurs Official NBA Game Notes & NBA Injury Report",
                "official_source_url": "https://www.nba.com/gamenotes/spurs.pdf",
                "secondary_source_url": "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-23_03_45PM.pdf",
                "olbg_url": "https://www.olbg.com/betting-tips/Basketball/4",
                "form_summary": "HOU 1-0; SAS 0-1 (lost 104-116 vs OKC on Oct 20 after closing preseason 126-97 over SAC)",
                "stats_summary": "Neutral-home Austin Moody Center clash; Wembanyama & Castle face Durant-led Rockets",
                "injury_summary": "SAS: Tobias Harris Out (left calf), Jayden Quaintance Out (knee), De'Aaron Fox Questionable (wrist), Keldon Johnson Questionable (mouth). HOU: Steven Adams Questionable (calf), Reed Sheppard Questionable (knee).",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Houston Rockets",
                    "San Antonio Spurs",
                    mu_margin_a=3.6,
                    sigma_margin=11.9,
                    mu_total=223.8,
                    sigma_total=15.8,
                    spread_a=-3.5,
                    total_line=224.5,
                    unit_label="Point",
                ),
                "winner_pick": "Houston Rockets",
                "pick_market": "winner",
                "pick_selection": "Houston Rockets",
                "confidence": "high",
                "prediction_text": (
                    "Take Houston Rockets on the moneyline at Moody Center in Austin, where San Antonio surrenders "
                    "part of its Frost Bank Center comfort after dropping Tuesday's opener 116-104 to Oklahoma City. "
                    "Mitch Johnson's Spurs already have Tobias Harris (left calf strain) and rookie Jayden Quaintance "
                    "(knee) ruled out, with De'Aaron Fox (right wrist sprain) and Keldon Johnson (mouth laceration) "
                    "both questionable. Even with Steven Adams and Reed Sheppard questionable for 1-0 Houston, Kevin "
                    "Durant's shot-making against Victor Wembanyama's drop coverage tilts this Texas tilt toward the visitors."
                ),
            },
            {
                "id": "87b3-BK-03",
                "sport": "basketball",
                "sport_name": "Basketball",
                "olbg_sport_id": 4,
                "competition": "NBA Regular Season",
                "event": "New Orleans Pelicans @ Utah Jazz",
                "away": "New Orleans Pelicans",
                "home": "Utah Jazz",
                "venue": "Delta Center, Salt Lake City, UT",
                "start_utc": "2026-10-24T01:30:00Z",
                "official_source_name": "NBA Official Referee Injury Report (2026-10-23 3:45 PM ET)",
                "official_source_url": "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-23_03_45PM.pdf",
                "secondary_source_url": "https://www.nba.com/news/starting-5-october-23-2026",
                "olbg_url": "https://www.olbg.com/betting-tips/Basketball/4",
                "form_summary": "Western Conference early-season clash at altitude in Salt Lake City",
                "stats_summary": "Utah loses primary interior rebounder Nurkic; Pelicans enter with clean NBA roster",
                "injury_summary": "UTA: Jusuf Nurkic Out (right 2nd plantar plate tear), Tony Bradley Available (quad), two-ways Alexander/Ingram Out. NOP: Only two-ways Dia/Pierre Jr./Reese Out.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "New Orleans Pelicans",
                    "Utah Jazz",
                    mu_margin_a=2.7,
                    sigma_margin=12.1,
                    mu_total=229.4,
                    sigma_total=16.0,
                    spread_a=-2.5,
                    total_line=228.5,
                    unit_label="Point",
                ),
                "winner_pick": "New Orleans Pelicans",
                "pick_market": "winner",
                "pick_selection": "New Orleans Pelicans",
                "confidence": "medium",
                "prediction_text": (
                    "Play New Orleans Pelicans on the moneyline at Delta Center despite Salt Lake City's altitude "
                    "boost. Utah's frontcourt suffers a major interior blow with starting center Jusuf Nurkic sidelined "
                    "by a right second plantar plate tear, forcing Tony Bradley—cleared after a left quadriceps "
                    "strain—into heavier paint duty. New Orleans brings a clean main-roster availability sheet with "
                    "only G League two-way players Malik Dia, Jaron Pierre Jr., and Julian Reese inactive, giving "
                    "the Pelicans' athletic wings steady rim pressure across four quarters."
                ),
            },
            {
                "id": "87b3-BK-04",
                "sport": "basketball",
                "sport_name": "Basketball",
                "olbg_sport_id": 4,
                "competition": "NBA Regular Season",
                "event": "Memphis Grizzlies @ Golden State Warriors",
                "away": "Memphis Grizzlies",
                "home": "Golden State Warriors",
                "venue": "Chase Center, San Francisco, CA",
                "start_utc": "2026-10-24T02:00:00Z",
                "official_source_name": "NBA Official Referee Injury Report (2026-10-23 3:45 PM ET)",
                "official_source_url": "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-23_03_45PM.pdf",
                "secondary_source_url": "https://www.nba.com/news/starting-5-october-23-2026",
                "olbg_url": "https://www.olbg.com/betting-tips/Basketball/4",
                "form_summary": "Western Conference Pacific-Southwest rivalry at Chase Center",
                "stats_summary": "Warriors short four frontcourt/wing pieces; Grizzlies push top-5 transition tempo",
                "injury_summary": "GSW: Jimmy Butler III Out (ACL), Moses Moody Out (patellar tendon), Kristaps Porzingis Out (not with team), Charles Bassey Out (patellar), Brandin Podziemski Probable (back). MEM: Cedric Coward Doubtful (wrist), Isaiah Stewart Questionable (ankle).",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Golden State Warriors",
                    "Memphis Grizzlies",
                    mu_margin_a=2.2,
                    sigma_margin=12.2,
                    mu_total=231.6,
                    sigma_total=16.2,
                    spread_a=-2.5,
                    total_line=229.5,
                    unit_label="Point",
                ),
                "winner_pick": "Golden State Warriors",
                "pick_market": "total",
                "pick_selection": "Over 229.5",
                "confidence": "medium",
                "prediction_text": (
                    "Side with Over 229.5 total points—while leaning Golden State on a narrow home moneyline—when "
                    "the Warriors welcome Memphis to Chase Center. Golden State's defense and size are stretched thin "
                    "with Jimmy Butler III (right ACL repair), Moses Moody (patellar tendon), Charles Bassey, and "
                    "Kristaps Porzingis all inactive, leaving Stephen Curry and probable guard Brandin Podziemski to "
                    "lean heavily on small-ball perimeter volume. With Isaiah Stewart questionable on a sore ankle for "
                    "fast-breaking Memphis, small-lineup spacing points toward a track meet past 230."
                ),
            },
            {
                "id": "87b3-BK-05",
                "sport": "basketball",
                "sport_name": "Basketball",
                "olbg_sport_id": 4,
                "competition": "NBA Regular Season",
                "event": "LA Clippers @ Los Angeles Lakers",
                "away": "LA Clippers",
                "home": "Los Angeles Lakers",
                "venue": "Crypto.com Arena, Los Angeles, CA",
                "start_utc": "2026-10-24T02:00:00Z",
                "official_source_name": "NBA Official Referee Injury Report (2026-10-23 3:45 PM ET)",
                "official_source_url": "https://ak-static.cms.nba.com/referee/injury/Injury-Report_2026-10-23_03_45PM.pdf",
                "secondary_source_url": "https://www.nba.com/news/starting-5-october-23-2026",
                "olbg_url": "https://www.olbg.com/betting-tips/Basketball/4",
                "form_summary": "Hallway rivalry in downtown Los Angeles; Clippers missing five rotation scorers/bigs",
                "stats_summary": "Lakers rim protection reinforced by Walker Kessler; Clippers wing depth decimated",
                "injury_summary": "LAC: Bradley Beal Out (right knee), Brandon Ingram Out (right heel surgery), Max Strus Out (plantar fascia tear), Jordan Miller Out (rotator cuff), Yanic Konan Niederhauser Out (Lisfranc). LAL: Walker Kessler Available (finger splint), Jake LaRavia Questionable (ankle), Cameron Carr & Adou Thiero Out.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Los Angeles Lakers",
                    "LA Clippers",
                    mu_margin_a=5.4,
                    sigma_margin=11.6,
                    mu_total=222.4,
                    sigma_total=15.5,
                    spread_a=-4.5,
                    total_line=223.5,
                    unit_label="Point",
                ),
                "winner_pick": "Los Angeles Lakers",
                "pick_market": "winner",
                "pick_selection": "Los Angeles Lakers",
                "confidence": "high",
                "prediction_text": (
                    "Side with Los Angeles Lakers outright for Friday's Crypto.com Arena showdown against the "
                    "shorthanded LA Clippers. League injury filings rule out five Clippers contributors—Bradley Beal "
                    "(right knee management), Brandon Ingram (heel surgery), Max Strus (plantar fascia tear), Jordan "
                    "Miller (rotator cuff), and Yanic Konan Niederhauser (Lisfranc)—stripping Tyronn Lue of secondary "
                    "shot creation and wing shooting. By contrast, seven-footer Walker Kessler is cleared to play in a "
                    "left finger splint for the Lakers, anchoring paint control across 48 minutes."
                ),
            },
        ]
    )

    # =========================================================================
    # 2. BASEBALL (OLBG ID 12) — 2026 MLB World Series Games 1-5 (Rays vs Brewers)
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-BB-01",
                "sport": "baseball",
                "sport_name": "Baseball",
                "olbg_sport_id": 12,
                "competition": "2026 MLB World Series — Game 1",
                "event": "Tampa Bay Rays @ Milwaukee Brewers (Game 1)",
                "away": "Tampa Bay Rays",
                "home": "Milwaukee Brewers",
                "venue": "American Family Field, Milwaukee, WI",
                "start_utc": "2026-10-24T00:00:00Z",
                "official_source_name": "MLB StatsAPI Official Schedule & Standings (gamePk 849805)",
                "official_source_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-31&hydrate=probablePitcher,team,venue",
                "secondary_source_url": "https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason",
                "olbg_url": "https://www.olbg.com/betting-tips/Baseball/12",
                "form_summary": "MIL 103-59 (.636, MLB #1, 55-26 home, W5 streak, 8-2 L10); TB 98-64 (.605, AL #1, 46-35 road, 8-2 L10)",
                "stats_summary": "MIL 832 RS / 618 RA (+214 diff, 68-35 night); TB 736 RS / 650 RA (+86 diff). Starters: Nick Martinez vs Jacob Misiorowski.",
                "injury_summary": "Official Game 1 starters confirmed on MLB StatsAPI: RHP Nick Martinez (#28, TB) vs RHP Jacob Misiorowski (#32, MIL).",
                "unconfirmed_fields": [],
                "markets": price_poisson_match(
                    "Tampa Bay Rays",
                    "Milwaukee Brewers",
                    lam_away=3.68,
                    lam_home=4.34,
                    three_way=False,
                    spread_home=-1.5,
                    total_line=7.5,
                    unit_name="Run",
                    deriv_label="First 5 Innings Winner (2-Way)",
                    deriv_outcomes=[("Tampa Bay Rays F5", 0.435), ("Milwaukee Brewers F5", 0.565)],
                    overround=0.040,
                ),
                "winner_pick": "Milwaukee Brewers",
                "pick_market": "winner",
                "pick_selection": "Milwaukee Brewers",
                "confidence": "high",
                "prediction_text": (
                    "Back Milwaukee Brewers on the Game 1 moneyline at American Family Field as baseball's top "
                    "103-59 regular-season club (+214 run differential, 832 runs scored, 618 allowed) opens the Fall "
                    "Classic against 98-64 Tampa Bay (+86 differential). Milwaukee went a dominant 55-26 at home and "
                    "68-35 under the lights while riding a five-game winning streak. Flamethrower Jacob Misiorowski "
                    "takes the ball opposite Rays right-hander Nick Martinez, and Milwaukee's deep bullpen plus a "
                    "67-45 mark against right-handed pitching earn a clear home edge."
                ),
            },
            {
                "id": "87b3-BB-02",
                "sport": "baseball",
                "sport_name": "Baseball",
                "olbg_sport_id": 12,
                "competition": "2026 MLB World Series — Game 2",
                "event": "Tampa Bay Rays @ Milwaukee Brewers (Game 2)",
                "away": "Tampa Bay Rays",
                "home": "Milwaukee Brewers",
                "venue": "American Family Field, Milwaukee, WI",
                "start_utc": "2026-10-25T00:00:00Z",
                "official_source_name": "MLB StatsAPI Official Schedule & Standings (gamePk 849802)",
                "official_source_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-31&hydrate=probablePitcher,team,venue",
                "secondary_source_url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103&season=2026&standingsTypes=regularSeason",
                "olbg_url": "https://www.olbg.com/betting-tips/Baseball/12",
                "form_summary": "TB 98-64 (31-20 in 1-run games, .608); MIL 103-59 (55-26 home, 32-16 vs AL)",
                "stats_summary": "Confirmed Game 2 starters: RHP Drew Rasmussen (#57, TB) vs RHP Logan Henderson (#50, MIL)",
                "injury_summary": "Both Game 2 probable starters posted on MLB StatsAPI; bullpens get off-day Sunday before travel to St. Petersburg.",
                "unconfirmed_fields": [],
                "markets": price_poisson_match(
                    "Tampa Bay Rays",
                    "Milwaukee Brewers",
                    lam_away=3.55,
                    lam_home=3.82,
                    three_way=False,
                    spread_home=-1.5,
                    total_line=7.5,
                    unit_name="Run",
                    deriv_label="First 5 Innings Total Runs",
                    deriv_outcomes=[("Over 3.5 F5 Runs", 0.518), ("Under 3.5 F5 Runs", 0.482)],
                    overround=0.040,
                ),
                "winner_pick": "Milwaukee Brewers",
                "pick_market": "total",
                "pick_selection": "Under 7.5",
                "confidence": "high",
                "prediction_text": (
                    "Play Under 7.5 total runs in World Series Game 2, with a slight moneyline lean to Milwaukee at "
                    "home. Saturday night pairs Tampa Bay command righty Drew Rasmussen against Brewers rookie standout "
                    "Logan Henderson, and both bullpens can deploy every high-leverage arm knowing Sunday is a scheduled "
                    "travel off-day. Milwaukee surrendered just 3.81 runs per game across 162 contests (618 allowed), "
                    "while Tampa Bay yielded 4.01 (650 allowed) and went 31-20 in tight one-run battles, pointing to "
                    "crisp October run prevention."
                ),
            },
            {
                "id": "87b3-BB-03",
                "sport": "baseball",
                "sport_name": "Baseball",
                "olbg_sport_id": 12,
                "competition": "2026 MLB World Series — Game 3",
                "event": "Milwaukee Brewers @ Tampa Bay Rays (Game 3)",
                "away": "Milwaukee Brewers",
                "home": "Tampa Bay Rays",
                "venue": "Tropicana Field, St. Petersburg, FL",
                "start_utc": "2026-10-27T00:00:00Z",
                "official_source_name": "MLB StatsAPI Official Schedule & Standings (gamePk 849804)",
                "official_source_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-31&hydrate=probablePitcher,team,venue",
                "secondary_source_url": "https://statsapi.mlb.com/api/v1/standings?leagueId=103&season=2026&standingsTypes=regularSeason",
                "olbg_url": "https://www.olbg.com/betting-tips/Baseball/12",
                "form_summary": "TB 52-29 (.642) at Tropicana Field & 56-31 (.644) on turf; MIL 48-33 (.593) road",
                "stats_summary": "TB 66-39 (.629) in night games & 55-35 vs winning clubs; MIL 4-2 on turf in 2026",
                "injury_summary": "Game 3 probable pitchers not yet posted on MLB StatsAPI (flagged blank rather than inferred).",
                "unconfirmed_fields": ["probable_pitchers"],
                "markets": price_poisson_match(
                    "Milwaukee Brewers",
                    "Tampa Bay Rays",
                    lam_away=3.88,
                    lam_home=4.06,
                    three_way=False,
                    spread_home=-1.5,
                    total_line=7.5,
                    unit_name="Run",
                    deriv_label="Extra Innings Required?",
                    deriv_outcomes=[("Yes Extra Innings", 0.112), ("No (9 Innings)", 0.888)],
                    overround=0.042,
                ),
                "winner_pick": "Tampa Bay Rays",
                "pick_market": "winner",
                "pick_selection": "Tampa Bay Rays",
                "confidence": "medium",
                "prediction_text": (
                    "Side with Tampa Bay Rays on the Game 3 moneyline when the Fall Classic shifts indoors to "
                    "Tropicana Field on Monday night. Probable starters remain unannounced on MLB's schedule feed—so "
                    "confidence stays medium—but Tampa Bay's surface and venue splits are unmistakable: the Rays went "
                    "52-29 (.642) at home, 56-31 (.644) on artificial turf, and 55-35 (.611) against winning clubs "
                    "this season. Even against a 48-33 Milwaukee road club, Tampa Bay's dome defense and match-up "
                    "platoons tilt Game 3 toward the American League champions."
                ),
            },
            {
                "id": "87b3-BB-04",
                "sport": "baseball",
                "sport_name": "Baseball",
                "olbg_sport_id": 12,
                "competition": "2026 MLB World Series — Game 4",
                "event": "Milwaukee Brewers @ Tampa Bay Rays (Game 4)",
                "away": "Milwaukee Brewers",
                "home": "Tampa Bay Rays",
                "venue": "Tropicana Field, St. Petersburg, FL",
                "start_utc": "2026-10-28T00:00:00Z",
                "official_source_name": "MLB StatsAPI Official Schedule & Standings (gamePk 849803)",
                "official_source_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-31&hydrate=probablePitcher,team,venue",
                "secondary_source_url": "https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason",
                "olbg_url": "https://www.olbg.com/betting-tips/Baseball/12",
                "form_summary": "Guaranteed World Series Game 4 (ifNecessary=N); MIL 32-16 (.667) interleague vs AL",
                "stats_summary": "MIL +214 run diff (5.14 RS/G) vs TB +86 run diff (4.54 RS/G); mid-series bullpen depth test",
                "injury_summary": "Game 4 probable pitchers unannounced on MLB StatsAPI (left blank and logged on Flagged for Review).",
                "unconfirmed_fields": ["probable_pitchers"],
                "markets": price_poisson_match(
                    "Milwaukee Brewers",
                    "Tampa Bay Rays",
                    lam_away=4.18,
                    lam_home=4.04,
                    three_way=False,
                    spread_home=1.5,
                    total_line=8.5,
                    unit_name="Run",
                    deriv_label="Run Scored in 1st Inning",
                    deriv_outcomes=[("YRFI (1+ Run)", 0.472), ("NRFI (0 Runs)", 0.528)],
                    overround=0.042,
                ),
                "winner_pick": "Milwaukee Brewers",
                "pick_market": "winner",
                "pick_selection": "Milwaukee Brewers",
                "confidence": "medium",
                "prediction_text": (
                    "Lean Milwaukee Brewers on the Game 4 moneyline in Tuesday's back-to-back middle contest at "
                    "Tropicana Field. With fourth-starter / bulk-reliever assignments still unposted by MLB, medium "
                    "sizing is warranted, yet Milwaukee's offensive depth shines brightest deeper in rotations: the "
                    "Brewers averaged 5.14 runs per game (832 total), crushed left-handers at 36-14 (.720), and posted "
                    "a 32-16 (.667) interleague mark against American League clubs. When Rays relievers work on "
                    "consecutive nights without rest, Milwaukee's lineup patience gains clear leverage."
                ),
            },
            {
                "id": "87b3-BB-05",
                "sport": "baseball",
                "sport_name": "Baseball",
                "olbg_sport_id": 12,
                "competition": "2026 MLB World Series — Game 5 (If Necessary)",
                "event": "Milwaukee Brewers @ Tampa Bay Rays (Game 5*)",
                "away": "Milwaukee Brewers",
                "home": "Tampa Bay Rays",
                "venue": "Tropicana Field, St. Petersburg, FL",
                "start_utc": "2026-10-29T00:00:00Z",
                "official_source_name": "MLB StatsAPI Official Schedule & Standings (gamePk 849799)",
                "official_source_url": "https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-31&hydrate=probablePitcher,team,venue",
                "secondary_source_url": "https://statsapi.mlb.com/api/v1/standings?leagueId=104&season=2026&standingsTypes=regularSeason",
                "olbg_url": "https://www.olbg.com/betting-tips/Baseball/12",
                "form_summary": "Conditional Game 5 (ifNecessary=Y); top-of-rotation turn on normal four days' rest",
                "stats_summary": "MIL 11-5 (.688) extra-inning & 27-20 one-run record; TB 31-20 one-run & 52-29 home",
                "injury_summary": "Conditional fixture (ifNecessary=Y) and unannounced Game 5 starters disclosed on Flagged for Review.",
                "unconfirmed_fields": ["probable_pitchers", "conditional_if_necessary"],
                "markets": price_poisson_match(
                    "Milwaukee Brewers",
                    "Tampa Bay Rays",
                    lam_away=3.92,
                    lam_home=3.96,
                    three_way=False,
                    spread_home=-1.5,
                    total_line=7.5,
                    unit_name="Run",
                    deriv_label="Tampa Bay Rays +1.5 Alt Run Line",
                    deriv_outcomes=[("Tampa Bay Rays +1.5", 0.654), ("Milwaukee Brewers -1.5", 0.346)],
                    overround=0.044,
                ),
                "winner_pick": "Tampa Bay Rays",
                "pick_market": "winner",
                "pick_selection": "Tampa Bay Rays",
                "confidence": "low",
                "prediction_text": (
                    "Hold sizing to low confidence on Tampa Bay Rays moneyline for conditional World Series Game 5 "
                    "on Wednesday night at Tropicana Field, which MLB's schedule carries as an if-necessary contest "
                    "with starters still unconfirmed. Should the series reach a fifth game on normal rest, Tampa Bay's "
                    "52-29 home record, 31-20 resilience in one-run finishes, and familiarity with Tropicana Field's "
                    "catwalks offset Milwaukee's 103-win pedigree just enough to make the hosts a narrow pick-em "
                    "choice before the series returns to Wisconsin."
                ),
            },
        ]
    )

    # =========================================================================
    # 3. ICE HOCKEY (OLBG ID 13) — 5 upcoming NHL Regular Season games
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-IH-01",
                "sport": "ice-hockey",
                "sport_name": "Ice Hockey",
                "olbg_sport_id": 13,
                "competition": "NHL Regular Season",
                "event": "Montréal Canadiens @ Chicago Blackhawks",
                "away": "Montréal Canadiens",
                "home": "Chicago Blackhawks",
                "venue": "United Center, Chicago, IL",
                "start_utc": "2026-10-24T00:00:00Z",
                "official_source_name": "NHL Official API Schedule & Standings (gameId 2026020166)",
                "official_source_url": "https://api-web.nhle.com/v1/schedule/2026-10-23",
                "secondary_source_url": "https://api-web.nhle.com/v1/standings/2026-10-23",
                "olbg_url": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
                "form_summary": "MTL 4-3-2 (10 pts, .556, OT1); CHI 3-6-0 (6 pts, .333, 3-2-0 at United Center)",
                "stats_summary": "MTL 30 GF / 34 GA (3.33 GF/GP, only 1 RW in 9 GP); CHI 21 GF / 36 GA (15 GF / 17 GA in 5 home GP)",
                "injury_summary": "Official NHL pre-game morning skate goaltender confirmation pending puck drop; roster records live.",
                "unconfirmed_fields": [],
                "markets": price_poisson_match(
                    "Montréal Canadiens",
                    "Chicago Blackhawks",
                    lam_away=3.14,
                    lam_home=2.92,
                    three_way=False,
                    spread_home=1.5,
                    total_line=6.5,
                    unit_name="Goal",
                    deriv_label="Regulation 1X2 (60 Min)",
                    deriv_outcomes=[("Chicago Reg", 0.365), ("Draw (OT)", 0.228), ("Montréal Reg", 0.407)],
                    overround=0.042,
                ),
                "winner_pick": "Montréal Canadiens",
                "pick_market": "winner",
                "pick_selection": "Montréal Canadiens",
                "confidence": "medium",
                "prediction_text": (
                    "Take Montréal Canadiens on the full-game moneyline (including overtime and shootout) at United "
                    "Center against the 3-6-0 Chicago Blackhawks. Montréal enters at 4-3-2 (10 points) averaging "
                    "3.33 goals per game (30 GF, 34 GA) with a perfect 2-0 shootout mark, whereas Chicago sits 31st "
                    "overall at 2.33 goals per game (21 GF, 36 GA). Although Chicago has been far competitive on home "
                    "ice (3-2-0, 15 GF, 17 GA) and Montréal owns just one regulation win, Canadiens skill prevails "
                    "once overtime is included."
                ),
            },
            {
                "id": "87b3-IH-02",
                "sport": "ice-hockey",
                "sport_name": "Ice Hockey",
                "olbg_sport_id": 13,
                "competition": "NHL Regular Season",
                "event": "Tampa Bay Lightning @ Colorado Avalanche",
                "away": "Tampa Bay Lightning",
                "home": "Colorado Avalanche",
                "venue": "Ball Arena, Denver, CO",
                "start_utc": "2026-10-24T01:00:00Z",
                "official_source_name": "NHL Official API Schedule & Standings (gameId 2026020167)",
                "official_source_url": "https://api-web.nhle.com/v1/schedule/2026-10-23",
                "secondary_source_url": "https://api-web.nhle.com/v1/standings/2026-10-23",
                "olbg_url": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
                "form_summary": "TBL 7-2-0 (14 pts, .778, W3 streak, 2-2-0 road); COL 5-4-1 (11 pts, 3-1-1 home, L2)",
                "stats_summary": "COL averages NHL-elite 4.10 GF/GP (41 GF / 31 GA, 24 GF in 5 home GP); TBL 3.44 GF/GP (31 GF / 23 GA)",
                "injury_summary": "Official NHL schedule & standings verified; both clubs enter fully rested.",
                "unconfirmed_fields": [],
                "markets": price_poisson_match(
                    "Tampa Bay Lightning",
                    "Colorado Avalanche",
                    lam_away=3.26,
                    lam_home=3.54,
                    three_way=False,
                    spread_home=-1.5,
                    total_line=6.5,
                    unit_name="Goal",
                    deriv_label="1st Period Total Goals",
                    deriv_outcomes=[("Over 1.5 1P Goals", 0.562), ("Under 1.5 1P Goals", 0.438)],
                    overround=0.042,
                ),
                "winner_pick": "Colorado Avalanche",
                "pick_market": "total",
                "pick_selection": "Over 6.5",
                "confidence": "high",
                "prediction_text": (
                    "Play Over 6.5 total goals—with Colorado Avalanche edged ahead as the moneyline winner—in Friday's "
                    "heavyweight showdown at Ball Arena. Colorado leads Central Division offenses at 4.10 goals per "
                    "game (41 GF, 31 GA through 10 games) and has poured in 24 goals across five Denver home dates "
                    "(3-1-1). Visiting Tampa Bay arrives red-hot at 7-2-0 on a three-game winning streak averaging "
                    "3.44 goals per night, yet has conceded 14 times across four road trips (2-2-0), setting up "
                    "relentless power-play trading past six goals."
                ),
            },
            {
                "id": "87b3-IH-03",
                "sport": "ice-hockey",
                "sport_name": "Ice Hockey",
                "olbg_sport_id": 13,
                "competition": "NHL Regular Season",
                "event": "Anaheim Ducks @ Philadelphia Flyers",
                "away": "Anaheim Ducks",
                "home": "Philadelphia Flyers",
                "venue": "Xfinity Mobile Arena, Philadelphia, PA",
                "start_utc": "2026-10-24T17:00:00Z",
                "official_source_name": "NHL Official API Schedule & Standings (gameId 2026020168)",
                "official_source_url": "https://api-web.nhle.com/v1/schedule/2026-10-24",
                "secondary_source_url": "https://api-web.nhle.com/v1/standings/2026-10-23",
                "olbg_url": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
                "form_summary": "PHI 3-6-3 (9 pts, riding W3 winning streak); ANA 4-6-0 (8 pts, riding L5 losing skid, 3-3-0 road)",
                "stats_summary": "PHI 20 GF / 37 GA (1.67 GF/GP, low-event structure); ANA 27 GF / 33 GA (18 GF / 18 GA on road)",
                "injury_summary": "Saturday 1:00 PM ET matinee in Philadelphia; both clubs off Friday night.",
                "unconfirmed_fields": [],
                "markets": price_poisson_match(
                    "Anaheim Ducks",
                    "Philadelphia Flyers",
                    lam_away=2.66,
                    lam_home=2.84,
                    three_way=False,
                    spread_home=-1.5,
                    total_line=5.5,
                    unit_name="Goal",
                    deriv_label="Regulation 1X2 (60 Min)",
                    deriv_outcomes=[("Philadelphia Reg", 0.402), ("Draw (OT)", 0.238), ("Anaheim Reg", 0.360)],
                    overround=0.042,
                ),
                "winner_pick": "Philadelphia Flyers",
                "pick_market": "winner",
                "pick_selection": "Philadelphia Flyers",
                "confidence": "medium",
                "prediction_text": (
                    "Back Philadelphia Flyers on the Saturday matinee moneyline at Xfinity Mobile Arena against a "
                    "skidding Anaheim Ducks squad. Despite scoring just 20 goals through 12 outings (3-6-3, 9 points), "
                    "Philadelphia has tightened its neutral-zone structure to string together three consecutive wins, "
                    "collecting points in four of six home dates (2-2-2). Anaheim (4-6-0, 27 GF, 33 GA) arrives on a "
                    "five-game losing streak and faces an awkward 10:00 AM Pacific body-clock puck drop, giving rested "
                    "Philadelphia a timely edge."
                ),
            },
            {
                "id": "87b3-IH-04",
                "sport": "ice-hockey",
                "sport_name": "Ice Hockey",
                "olbg_sport_id": 13,
                "competition": "NHL Regular Season",
                "event": "Los Angeles Kings @ New Jersey Devils",
                "away": "Los Angeles Kings",
                "home": "New Jersey Devils",
                "venue": "Prudential Center, Newark, NJ",
                "start_utc": "2026-10-24T19:30:00Z",
                "official_source_name": "NHL Official API Schedule & Standings (gameId 2026020169)",
                "official_source_url": "https://api-web.nhle.com/v1/schedule/2026-10-24",
                "secondary_source_url": "https://api-web.nhle.com/v1/standings/2026-10-23",
                "olbg_url": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
                "form_summary": "NJD 6-4-0 (12 pts, 5-2-0 home, W2 streak); LAK 2-4-2 (6 pts, 2-1-2 road, W2 streak)",
                "stats_summary": "NJD 26 GF / 17 GA (+9 diff) in 7 home games at Prudential Center; LAK 20 GF / 29 GA (2.50 GF/GP)",
                "injury_summary": "Saturday afternoon Prudential Center showcase; New Jersey #3 in NHL home points.",
                "unconfirmed_fields": [],
                "markets": price_poisson_match(
                    "Los Angeles Kings",
                    "New Jersey Devils",
                    lam_away=2.62,
                    lam_home=3.38,
                    three_way=False,
                    spread_home=-1.5,
                    total_line=6.5,
                    unit_name="Goal",
                    deriv_label="New Jersey Regulation Win (60 Min)",
                    deriv_outcomes=[("New Jersey in 60 Min", 0.504), ("LAK or Overtime", 0.496)],
                    overround=0.042,
                ),
                "winner_pick": "New Jersey Devils",
                "pick_market": "winner",
                "pick_selection": "New Jersey Devils",
                "confidence": "high",
                "prediction_text": (
                    "Back New Jersey Devils on the moneyline Saturday afternoon at Prudential Center against the "
                    "visiting Los Angeles Kings. New Jersey (6-4-0, 12 points) has turned Newark into a fortress early "
                    "in 2026-27, going 5-2-0 at home while outscoring visitors 26-17 (+9 differential) and riding a "
                    "two-game winning streak. Los Angeles (2-4-2, 6 points) has stabilized with consecutive road wins "
                    "(2-1-2 away), yet generates only 2.50 goals per game (20 GF, 29 GA) and owns just one regulation "
                    "victory all season."
                ),
            },
            {
                "id": "87b3-IH-05",
                "sport": "ice-hockey",
                "sport_name": "Ice Hockey",
                "olbg_sport_id": 13,
                "competition": "NHL Regular Season",
                "event": "New York Rangers @ Ottawa Senators",
                "away": "New York Rangers",
                "home": "Ottawa Senators",
                "venue": "Canadian Tire Centre, Ottawa, ON",
                "start_utc": "2026-10-24T23:00:00Z",
                "official_source_name": "NHL Official API Schedule & Standings (gameId 2026020171)",
                "official_source_url": "https://api-web.nhle.com/v1/schedule/2026-10-24",
                "secondary_source_url": "https://api-web.nhle.com/v1/standings/2026-10-23",
                "olbg_url": "https://www.olbg.com/betting-tips/Ice_Hockey/13",
                "form_summary": "OTT 7-4-0 (14 pts, 4-2-0 home, 2-0 SO); NYR 7-4-1 (15 pts, 6-0-0 home BUT 1-4-1 road!)",
                "stats_summary": "Extreme road split: NYR scored just 8 goals in 6 road games (8 GF / 19 GA, -11 diff) vs OTT 4-2-0 at home",
                "injury_summary": "Hockey Night in Canada Eastern showcase; both clubs off Friday.",
                "unconfirmed_fields": [],
                "markets": price_poisson_match(
                    "New York Rangers",
                    "Ottawa Senators",
                    lam_away=2.76,
                    lam_home=2.98,
                    three_way=False,
                    spread_home=-1.5,
                    total_line=5.5,
                    unit_name="Goal",
                    deriv_label="1st Period Total Goals",
                    deriv_outcomes=[("Over 1.5 1P Goals", 0.492), ("Under 1.5 1P Goals", 0.508)],
                    overround=0.042,
                ),
                "winner_pick": "Ottawa Senators",
                "pick_market": "winner",
                "pick_selection": "Ottawa Senators",
                "confidence": "high",
                "prediction_text": (
                    "Play Ottawa Senators as a live home moneyline selection on Hockey Night in Canada against the "
                    "New York Rangers. Headline points flatter 7-4-1 New York (15 points), because the Rangers' entire "
                    "+8 differential was built going 6-0-0 at Madison Square Garden (29 GF, 10 GA) while collapsing to "
                    "1-4-1 on the road with a league-low eight road goals scored against 19 allowed. Ottawa sits "
                    "7-4-0 (14 points), holds a 4-2-0 mark at Canadian Tire Centre, and went 2-0 in shootouts."
                ),
            },
        ]
    )

    # =========================================================================
    # 4. TENNIS (OLBG ID 3) — 5 WTA 500 & ATP 250 Saturday Semi-Finals
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-TN-01",
                "sport": "tennis",
                "sport_name": "Tennis",
                "olbg_sport_id": 3,
                "competition": "WTA 500 Ningbo Open — Semi-Final 1",
                "event": "Leylah Fernandez vs Marie Bouzkova",
                "away": "Leylah Fernandez",
                "home": "Marie Bouzkova",
                "venue": "Ningbo (鄞州) Tennis Center, Ningbo, China (Hard, Plexipave)",
                "start_utc": "2026-10-24T07:00:00Z",
                "official_source_name": "WTA Official Main Draw & Saturday Order of Play PDF (Ningbo 2092)",
                "official_source_url": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",
                "secondary_source_url": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf",
                "olbg_url": "https://www.olbg.com/betting-tips/Tennis/3",
                "form_summary": "Fernandez (#25) d. [4] Alexandrova 7-5, 6-7(3), 6-3; Bouzkova (#41) d. [Q] Starodubtseva 6-4, 6-1",
                "stats_summary": "Bottom half opened after [2] Swiatek WD (left thigh) & [3] Kostyuk RET (right wrist in R16)",
                "injury_summary": "Both semi-finalists healthy; Fernandez played marathon 3-set QF vs Bouzkova's 81-minute straight-set rout.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Leylah Fernandez",
                    "Marie Bouzkova",
                    p_unit_a=0.558,
                    target_units=2,
                    unit_name="Set",
                    handicap_line=-1.5,
                    total_line=2.5,
                    prop_label="Total Match Games (O/U 21.5)",
                    prop_outcomes=[("Over 21.5 Games", 0.548), ("Under 21.5 Games", 0.452)],
                    overround=0.044,
                ),
                "winner_pick": "Leylah Fernandez",
                "pick_market": "winner",
                "pick_selection": "Leylah Fernandez",
                "confidence": "high",
                "prediction_text": (
                    "Back world No. 25 Leylah Fernandez to defeat No. 41 Marie Bouzkova in Saturday's opening Ningbo "
                    "Open semi-final on Plexipave hard court. While third seed Marta Kostyuk retired with a right "
                    "wrist injury earlier in this bottom half and Iga Swiatek withdrew pre-event, Fernandez earned her "
                    "spot the hard way by outlasting fourth seed Ekaterina Alexandrova 7-5, 6-7(3), 6-3 after sweeping "
                    "Zeynep Sonmez 6-2, 6-2. Bouzkova eased past qualifier Yulia Starodubtseva 6-4, 6-1, yet "
                    "Fernandez's lefty forehand angles consistently break down passive counterpunching."
                ),
            },
            {
                "id": "87b3-TN-02",
                "sport": "tennis",
                "sport_name": "Tennis",
                "olbg_sport_id": 3,
                "competition": "WTA 500 Ningbo Open — Semi-Final 2",
                "event": "Elena Rybakina vs Diana Shnaider",
                "away": "Diana Shnaider",
                "home": "Elena Rybakina",
                "venue": "Ningbo Tennis Center, Ningbo, China (Hard, Plexipave)",
                "start_utc": "2026-10-24T09:30:00Z",
                "official_source_name": "WTA Official Main Draw & Saturday Order of Play PDF (Ningbo 2092)",
                "official_source_url": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/OP.pdf",
                "secondary_source_url": "https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf",
                "olbg_url": "https://www.olbg.com/betting-tips/Tennis/3",
                "form_summary": "[1] Rybakina (World #1) d. Yastremska 6-4, 6-7(6), 6-3 & d. [Q] Tomljanovic 6-2, 6-0; [6] Shnaider (#13) d. Muchova 2-6, 6-1, 6-2 & d. Zhu 2-6, 6-3, 6-1",
                "stats_summary": "Shnaider dropped opening set 2-6 in consecutive rounds; Rybakina won 12 of last 14 games in QF",
                "injury_summary": "No medical timeouts reported in QFs; both top-15 seeds fit.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Elena Rybakina",
                    "Diana Shnaider",
                    p_unit_a=0.655,
                    target_units=2,
                    unit_name="Set",
                    handicap_line=-1.5,
                    total_line=2.5,
                    prop_label="Total Match Games (O/U 20.5)",
                    prop_outcomes=[("Over 20.5 Games", 0.524), ("Under 20.5 Games", 0.476)],
                    overround=0.044,
                ),
                "winner_pick": "Elena Rybakina",
                "pick_market": "handicap",
                "pick_selection": "Elena Rybakina -1.5",
                "confidence": "medium",
                "prediction_text": (
                    "Play Elena Rybakina -1.5 sets—alongside Rybakina as the clear match winner—against sixth seed "
                    "Diana Shnaider in Ningbo's evening semi-final. World No. 1 Rybakina shook off a tight opener "
                    "against Dayana Yastremska by demolishing Ajla Tomljanovic 6-2, 6-0 in Friday's quarter-finals, "
                    "winning the last nine games straight behind dominant first-serve holds. World No. 13 Shnaider "
                    "dropped her opening set 2-6 to both Karolina Muchova and wild card Zhu Lin, a slow-starting habit "
                    "she cannot survive against Rybakina's flat pace."
                ),
            },
            {
                "id": "87b3-TN-03",
                "sport": "tennis",
                "sport_name": "Tennis",
                "olbg_sport_id": 3,
                "competition": "ATP 250 Grand Prix Auvergne-Rhone-Alpes (Lyon) — Semi-Final 1",
                "event": "Tommy Paul vs Taylor Fritz",
                "away": "Tommy Paul",
                "home": "Taylor Fritz",
                "venue": "LDLC Arena, Lyon-Décines, France (Indoor Hard)",
                "start_utc": "2026-10-24T12:00:00Z",
                "official_source_name": "ATP Official Lyon Order of Play PDF (Event 496)",
                "official_source_url": "https://www.protennislive.com/posting/2026/496/op.pdf",
                "secondary_source_url": "https://www.atptour.com/en/scores/current/lyon/496/daily-schedule",
                "olbg_url": "https://www.olbg.com/betting-tips/Tennis/3",
                "form_summary": "[2] Fritz d. Altmaier 7-6(5), 6-2; [4] Paul d. Moutet 6-4, 3-6, 6-3",
                "stats_summary": "All-American indoor hard semi-final; Fritz unbroken in second set vs Altmaier",
                "injury_summary": "Both Americans completed Friday afternoon QFs cleanly with full evening recovery.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Taylor Fritz",
                    "Tommy Paul",
                    p_unit_a=0.588,
                    target_units=2,
                    unit_name="Set",
                    handicap_line=-1.5,
                    total_line=2.5,
                    prop_label="Tiebreak in Match?",
                    prop_outcomes=[("Yes Tiebreak Played", 0.575), ("No Tiebreak", 0.425)],
                    overround=0.042,
                ),
                "winner_pick": "Taylor Fritz",
                "pick_market": "winner",
                "pick_selection": "Taylor Fritz",
                "confidence": "high",
                "prediction_text": (
                    "Back second seed Taylor Fritz on the moneyline over fellow American fourth seed Tommy Paul on "
                    "Lyon's brisk indoor hard court. Fritz dismissed Daniel Altmaier 7-6(5), 6-2 on Friday afternoon "
                    "without dropping serve after the opening tiebreak, whereas Paul needed three physical sets "
                    "(6-4, 3-6, 6-3) to subdue crowd favourite Corentin Moutet. Indoors where wind cannot blunt first "
                    "deliveries, Fritz's heavier serve-plus-forehand combination wins far more free points than Paul's "
                    "all-court baseline defense."
                ),
            },
            {
                "id": "87b3-TN-04",
                "sport": "tennis",
                "sport_name": "Tennis",
                "olbg_sport_id": 3,
                "competition": "ATP 250 Almaty Open — Semi-Final 2",
                "event": "Daniil Medvedev vs Alexander Bublik",
                "away": "Alexander Bublik",
                "home": "Daniil Medvedev",
                "venue": "Almaty Arena, Almaty, Kazakhstan (Indoor Hard, Altitude)",
                "start_utc": "2026-10-24T13:00:00Z",
                "official_source_name": "ATP Tour Official Almaty Daily Schedule (Event 9410)",
                "official_source_url": "https://www.atptour.com/en/scores/current/almaty/9410/daily-schedule",
                "secondary_source_url": "https://www.atptour.com/en/scores/current",
                "olbg_url": "https://www.olbg.com/betting-tips/Tennis/3",
                "form_summary": "[1] Medvedev d. Marozsan 6-2, 6-1; [3] Bublik d. Shevchenko 6-2, 6-3",
                "stats_summary": "Medvedev dominates career ATP H2H vs Bublik (6-0 / 7-0 tour-level) via deep fence-hugging return",
                "injury_summary": "Both top-3 seeds breezed through Friday QFs in under 70 minutes.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Daniil Medvedev",
                    "Alexander Bublik",
                    p_unit_a=0.635,
                    target_units=2,
                    unit_name="Set",
                    handicap_line=-1.5,
                    total_line=2.5,
                    prop_label="Total Match Games (O/U 22.5)",
                    prop_outcomes=[("Over 22.5 Games", 0.512), ("Under 22.5 Games", 0.488)],
                    overround=0.042,
                ),
                "winner_pick": "Daniil Medvedev",
                "pick_market": "handicap",
                "pick_selection": "Daniil Medvedev -1.5",
                "confidence": "high",
                "prediction_text": (
                    "Play Daniil Medvedev -1.5 sets—and Medvedev to win outright—against Kazakh third seed Alexander "
                    "Bublik in Saturday's Almaty Open semi-final. Top-seeded Medvedev looked razor-sharp in dismantling "
                    "Fabian Marozsan 6-2, 6-1 on Friday, neutralizing pace from deep behind the baseline. Although "
                    "Bublik cruised past countryman Alexander Shevchenko 6-2, 6-3 in front of home supporters at "
                    "altitude, Medvedev has owned this stylistic matchup throughout their tour careers by absorbing "
                    "big first serves and coaxing double faults and drop-shot errors."
                ),
            },
            {
                "id": "87b3-TN-05",
                "sport": "tennis",
                "sport_name": "Tennis",
                "olbg_sport_id": 3,
                "competition": "ATP 250 European Open (Brussels) — Semi-Final 2",
                "event": "Arthur Fils vs Jan-Lennard Struff",
                "away": "Jan-Lennard Struff",
                "home": "Arthur Fils",
                "venue": "ING Arena, Brussels, Belgium (Indoor Hard)",
                "start_utc": "2026-10-24T16:30:00Z",
                "official_source_name": "ATP Tour Official Brussels Daily Schedule (Event 7485)",
                "official_source_url": "https://www.atptour.com/en/scores/current/brussels/7485/daily-schedule",
                "secondary_source_url": "https://www.atptour.com/en/scores/current",
                "olbg_url": "https://www.olbg.com/betting-tips/Tennis/3",
                "form_summary": "[1] Fils d. Halys 6-7(4), 7-6(2), 7-5; Struff d. Bergs 6-3, 7-6(5)",
                "stats_summary": "Fils played 36 games across two tiebreaks vs Halys; Struff serving >80% first-serve points won indoors",
                "injury_summary": "No injury flags; Fils faced grueling three-hour QF vs Halys on Friday evening.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Arthur Fils",
                    "Jan-Lennard Struff",
                    p_unit_a=0.576,
                    target_units=2,
                    unit_name="Set",
                    handicap_line=-1.5,
                    total_line=2.5,
                    prop_label="Total Match Games (O/U 22.5)",
                    prop_outcomes=[("Over 22.5 Games", 0.592), ("Under 22.5 Games", 0.408)],
                    overround=0.042,
                ),
                "winner_pick": "Arthur Fils",
                "pick_market": "winner",
                "pick_selection": "Arthur Fils",
                "confidence": "high",
                "prediction_text": (
                    "Back top seed Arthur Fils on the moneyline over veteran German serve-and-volleyer Jan-Lennard "
                    "Struff in Saturday evening's Brussels semi-final at ING Arena. Fils showed tremendous poise to "
                    "edge big-serving Frenchman Quentin Halys 6-7(4), 7-6(2), 7-5 in Friday's quarter-finals, tuning "
                    "his return timing against 135-mph deliveries. Struff silenced Belgian hope Zizou Bergs 6-3, "
                    "7-6(5), yet whenever rallies extend past four shots on indoor hard court, Fils' heavy topspin "
                    "passing shots dictate terms."
                ),
            },
        ]
    )

    # =========================================================================
    # 5. GOLF (OLBG ID 5) — 5 Official Tour Events / Matchups (Oct 24-25, 2026)
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-GF-01",
                "sport": "golf",
                "sport_name": "Golf",
                "olbg_sport_id": 5,
                "competition": "LPGA Tour — BMW Ladies Championship (Round 3 -> Outright)",
                "event": "BMW Ladies Championship 72-Hole Outright",
                "away": "Lauren Coughlin / Field",
                "home": "Haeran Ryu",
                "venue": "Pine Beach Golf Links, Haenam-gun, South Korea (Par 72, 6,784 yds)",
                "start_utc": "2026-10-24T01:00:00Z",
                "official_source_name": "LPGA Official Leaderboard & Round 2 Report",
                "official_source_url": "https://www.lpga.com/tournaments/bmw-lpga-championship/leaderboard",
                "secondary_source_url": "https://www.lpga.com/news/2026/field-breakdown-2026-bmw-ladies-championship",
                "olbg_url": "https://www.olbg.com/betting-tips/Golf/5",
                "form_summary": "World #3 Haeran Ryu leads by 2 strokes after bogey-free 67 in R1 & birdie finish on 18 in R2; won 2 majors in 2026 (Evian & KPMG Women's PGA)",
                "stats_summary": "T2 Lauren Coughlin & Minsun7 Kim (-2 back); Julia Lopez Ramirez & Chizzy Iwai (two R2 eagles, 66) chasing",
                "injury_summary": "No LPGA withdrawals among top-15 contenders entering Saturday's moving day.",
                "unconfirmed_fields": [],
                "markets": price_field_event(
                    winner_label="Tournament Winner (36-Hole In-Running)",
                    field_weights=[
                        ("Haeran Ryu", 0.345),
                        ("Lauren Coughlin", 0.145),
                        ("Minsun7 Kim", 0.105),
                        ("Chizzy Iwai", 0.095),
                        ("Hye-Jin Choi", 0.090),
                        ("Field (Others)", 0.220),
                    ],
                    h2h_label="Round 3 Final Group 2-Ball",
                    h2h_pair=[("Haeran Ryu", 0.578), ("Lauren Coughlin", 0.422)],
                    total_label="Winning 72-Hole Score vs -19.5",
                    total_pair=[("Better than -19.5 (-20 or lower)", 0.535), ("-19 or worse", 0.465)],
                    total_line=-19.5,
                    deriv_label="Korean Winner vs Rest of World",
                    deriv_pair=[("Korean Player Wins", 0.615), ("Rest of World Wins", 0.385)],
                ),
                "winner_pick": "Haeran Ryu",
                "pick_market": "winner",
                "pick_selection": "Haeran Ryu",
                "confidence": "high",
                "prediction_text": (
                    "Back world No. 3 Haeran Ryu to convert her two-stroke 36-hole lead into the BMW Ladies "
                    "Championship trophy at Pine Beach Golf Links. Playing on home soil in Jeollanam-do after capturing "
                    "two major titles this season—the Amundi Evian Championship and KPMG Women's PGA—Ryu opened with a "
                    "bogey-free 67 and rolled in a closing birdie on 18 Friday to stay two clear of Lauren Coughlin "
                    "and Minsun7 Kim. Even with Chizzy Iwai firing two Friday eagles for 66, Ryu's ball-striking sets "
                    "the benchmark."
                ),
            },
            {
                "id": "87b3-GF-02",
                "sport": "golf",
                "sport_name": "Golf",
                "olbg_sport_id": 5,
                "competition": "DP World Tour — Genesis Championship (Round 3 -> Outright)",
                "event": "Genesis Championship 72-Hole Outright",
                "away": "Casey Jarvis / Ryan Fox",
                "home": "Antoine Rozner",
                "venue": "Woo Jeong Hills Country Club, Cheonan, South Korea",
                "start_utc": "2026-10-24T02:50:00Z",
                "official_source_name": "DP World Tour Official Genesis Championship Leaderboard",
                "official_source_url": "https://www.europeantour.com/dpworld-tour/genesis-championship-2026/leaderboard",
                "secondary_source_url": "https://www.europeantour.com/dpworld-tour/",
                "olbg_url": "https://www.olbg.com/betting-tips/Golf/5",
                "form_summary": "T1 Antoine Rozner (68-64=132, -10) & Casey Jarvis (66-66=132, -10) lead by 3 strokes over T3 (-7)",
                "stats_summary": "T3 Martin Couvra, Filippo Celli, Ryan Fox, Yonggu Shin at -7 (135); T7 Si Woo Kim at -6 (136)",
                "injury_summary": "Final Round 3 three-ball (Rozner, Jarvis, Couvra) tees off 11:50 local (02:50 UTC).",
                "unconfirmed_fields": [],
                "markets": price_field_event(
                    winner_label="Tournament Winner (36-Hole In-Running)",
                    field_weights=[
                        ("Antoine Rozner", 0.275),
                        ("Casey Jarvis", 0.240),
                        ("Ryan Fox", 0.115),
                        ("Si Woo Kim", 0.105),
                        ("Martin Couvra", 0.085),
                        ("Field (Others)", 0.180),
                    ],
                    h2h_label="36-Hole Co-Leaders 72-Hole Matchup",
                    h2h_pair=[("Antoine Rozner", 0.538), ("Casey Jarvis", 0.462)],
                    total_label="Winning 72-Hole Score vs -16.5",
                    total_pair=[("Better than -16.5 (-17 or lower)", 0.542), ("-16 or worse", 0.458)],
                    total_line=-16.5,
                    deriv_label="Playoff Needed After 72 Holes?",
                    deriv_pair=[("Yes Sudden-Death Playoff", 0.185), ("No (Regulation Winner)", 0.815)],
                ),
                "winner_pick": "Antoine Rozner",
                "pick_market": "winner",
                "pick_selection": "Antoine Rozner",
                "confidence": "high",
                "prediction_text": (
                    "Back three-time DP World Tour winner Antoine Rozner outright at the Genesis Championship entering "
                    "Saturday's third round at Woo Jeong Hills. Rozner vaulted to 10-under 132 (68-64) with Friday's "
                    "low-of-the-leaders seven-under 64, sharing a commanding three-stroke cushion alongside South "
                    "African Casey Jarvis (66-66) ahead of Ryan Fox, Martin Couvra, Filippo Celli, and Yonggu Shin at "
                    "-7, plus Si Woo Kim at -6. Rozner's proven weekend closing pedigree gives him clear value above +220."
                ),
            },
            {
                "id": "87b3-GF-03",
                "sport": "golf",
                "sport_name": "Golf",
                "olbg_sport_id": 5,
                "competition": "PGA Tour — Butterfield Bermuda Championship (Outright)",
                "event": "Butterfield Bermuda Championship 72-Hole Outright",
                "away": "Chandler Blanchet / Kensei Hirata",
                "home": "Corey Conners",
                "venue": "Port Royal Golf Course, Southampton, Bermuda (Par 71, $6M Purse)",
                "start_utc": "2026-10-24T11:30:00Z",
                "official_source_name": "PGA Tour Official Butterfield Bermuda Leaderboard (R2026528)",
                "official_source_url": "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/leaderboard",
                "secondary_source_url": "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/tee-times",
                "olbg_url": "https://www.olbg.com/betting-tips/Golf/5",
                "form_summary": "T1 Hirata (65-64=129) & Blanchet (62-67=129) at -13; T3 Conners (63-67=130), Power (67-63), Cole, Silverman, Walker at -12",
                "stats_summary": "Cut fell at -5 (69 players); Denny McCarthy (68-63=131) & David Skinns sit two back at -11",
                "injury_summary": "Round 2 completed cleanly Friday; full 69-player weekend field confirmed.",
                "unconfirmed_fields": [],
                "markets": price_field_event(
                    winner_label="Tournament Winner (36-Hole In-Running)",
                    field_weights=[
                        ("Corey Conners", 0.195),
                        ("Seamus Power", 0.140),
                        ("Chandler Blanchet", 0.135),
                        ("Eric Cole", 0.120),
                        ("Kensei Hirata", 0.110),
                        ("Denny McCarthy / Field", 0.300),
                    ],
                    h2h_label="72-Hole Matchup: Corey Conners vs Seamus Power",
                    h2h_pair=[("Corey Conners", 0.562), ("Seamus Power", 0.438)],
                    total_label="Winning 72-Hole Score vs -21.5",
                    total_pair=[("Better than -21.5 (-22 or lower)", 0.520), ("-21 or worse", 0.480)],
                    total_line=-21.5,
                    deriv_label="Corey Conners Top-3 Finish (Incl. Ties)",
                    deriv_pair=[("Conners Top-3 Yes", 0.465), ("Conners Outside Top-3", 0.535)],
                ),
                "winner_pick": "Corey Conners",
                "pick_market": "winner",
                "pick_selection": "Corey Conners",
                "confidence": "high",
                "prediction_text": (
                    "Play Corey Conners outright at Port Royal Golf Course trailing 36-hole co-leaders Kensei Hirata "
                    "and Chandler Blanchet (-13, 129) by a single stroke after rounds of 63-67 (-12, 130). While "
                    "Blanchet sits No. 114 and Hirata No. 176 in the FedExCup Fall standings chasing maiden PGA Tour "
                    "silverware, two-time Tour winner Conners brings elite wind-flighted iron control into coastal "
                    "Southampton gusts alongside past Bermuda champion Seamus Power (-12), Eric Cole (-12), and Denny "
                    "McCarthy (-11)."
                ),
            },
            {
                "id": "87b3-GF-04",
                "sport": "golf",
                "sport_name": "Golf",
                "olbg_sport_id": 5,
                "competition": "PGA Tour — Butterfield Bermuda Championship (Round 3 Co-Leader 2-Ball)",
                "event": "Chandler Blanchet vs Kensei Hirata (Round 3 Matchup)",
                "away": "Kensei Hirata",
                "home": "Chandler Blanchet",
                "venue": "Port Royal Golf Course, Southampton, Bermuda (Par 71)",
                "start_utc": "2026-10-24T16:30:00Z",
                "official_source_name": "PGA Tour Official Butterfield Bermuda Leaderboard & Recap",
                "official_source_url": "https://www.pgatour.com/article/news/daily-wrapup/2026/10/22/round-1-recap-butterfield-bermuda-championship-port-royal-leaderboard",
                "secondary_source_url": "https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/leaderboard",
                "olbg_url": "https://www.olbg.com/betting-tips/Golf/5",
                "form_summary": "Blanchet 62-67=129 (-13, two eagles in R1, previous island peak at Puerto Rico Open); Hirata 65-64=129 (-13)",
                "stats_summary": "Head-to-head 18-hole Round 3 tie-no-bet co-leader pairing at Port Royal",
                "injury_summary": "Both co-leaders finished 36 holes bogey-minimal Friday afternoon.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Chandler Blanchet",
                    "Kensei Hirata",
                    mu_margin_a=0.42,
                    sigma_margin=3.15,
                    mu_total=136.4,
                    sigma_total=3.8,
                    spread_a=-0.5,
                    total_line=136.5,
                    deriv_label="Either Player Shoots 66 or Lower in R3",
                    deriv_outcomes=[("Yes (<=66 Carded)", 0.555), ("No (Both >=67)", 0.445)],
                    overround=0.045,
                    unit_label="Stroke",
                ),
                "winner_pick": "Chandler Blanchet",
                "pick_market": "winner",
                "pick_selection": "Chandler Blanchet",
                "confidence": "medium",
                "prediction_text": (
                    "Side with Chandler Blanchet over Kensei Hirata in Saturday's Round 3 co-leader matchup (tie no "
                    "bet) at Port Royal. Blanchet torched the par-5s with two eagles—including a 52-foot bomb on "
                    "No. 17—during Thursday's career-low 62 before backing it up with a composed four-under 67 to "
                    "reach 13-under 129, matching his strong island comfort from earlier this year in Puerto Rico. "
                    "Hirata's 65-64 start has relied heavily on short-game saves that face stiffer weekend pin locations."
                ),
            },
            {
                "id": "87b3-GF-05",
                "sport": "golf",
                "sport_name": "Golf",
                "olbg_sport_id": 5,
                "competition": "PGA Tour Champions — Stifel Charity Classic (Schwab Cup Playoffs #1)",
                "event": "Stifel Charity Classic 54-Hole Outright",
                "away": "Stephen Ames / Stewart Cink",
                "home": "Vijay Singh",
                "venue": "Norwood Hills Country Club, St. Louis, MO ($2.3M Purse)",
                "start_utc": "2026-10-24T15:30:00Z",
                "official_source_name": "PGA Tour Champions Official Stifel Charity Classic Leaderboard",
                "official_source_url": "https://www.pgatour.com/pgatour-champions/tournaments/2026/stifel-charity-classic/S2026625/overview",
                "secondary_source_url": "https://www.pgatour.com/pgatour-champions/leaderboard",
                "olbg_url": "https://www.olbg.com/betting-tips/Golf/5",
                "form_summary": "Vijay Singh won last Sunday's SAS Championship (69-69-69=207, -9) & opened -1 thru 3; Stephen Ames -2 early",
                "stats_summary": "54-hole Charles Schwab Cup Playoffs opener (top 72 to top 54 cutline); defending champ Thomas Bjorn (-12 in 2025)",
                "injury_summary": "Round 1 in progress Friday afternoon; full playoff field active.",
                "unconfirmed_fields": [],
                "markets": price_field_event(
                    winner_label="Tournament Winner (54-Hole Outright)",
                    field_weights=[
                        ("Stewart Cink", 0.165),
                        ("Stephen Ames", 0.150),
                        ("Vijay Singh", 0.145),
                        ("Steven Alker", 0.125),
                        ("Bernhard Langer", 0.095),
                        ("Field (Others)", 0.320),
                    ],
                    h2h_label="Tournament Matchup: Vijay Singh vs Bernhard Langer",
                    h2h_pair=[("Vijay Singh", 0.558), ("Bernhard Langer", 0.442)],
                    total_label="Winning 54-Hole Score vs -12.5",
                    total_pair=[("Better than -12.5 (-13 or lower)", 0.515), ("-12 or worse", 0.485)],
                    total_line=-12.5,
                    deriv_label="Vijay Singh Top-5 Finish",
                    deriv_pair=[("Singh Top-5 Yes", 0.420), ("Singh Outside Top-5", 0.580)],
                ),
                "winner_pick": "Stewart Cink",
                "pick_market": "handicap",
                "pick_selection": "Vijay Singh",
                "confidence": "low",
                "prediction_text": (
                    "Keep stakes modest (low confidence) backing Vijay Singh in his 54-hole tournament matchup over "
                    "Bernhard Langer—while pricing Stewart Cink as narrow outright favourite—at the Stifel Charity "
                    "Classic in St. Louis. Hall of Famer Singh arrives at Norwood Hills riding last Sunday's SAS "
                    "Championship triumph in North Carolina, where three straight 69s (-9) made him the seventh-oldest "
                    "Champions winner, and he immediately birdied inside his opening three holes Friday alongside "
                    "early pacesetter Stephen Ames."
                ),
            },
        ]
    )

    # =========================================================================
    # 6. MOTOR RACING (OLBG ID 14) — F1 COTA, MotoGP Phillip Island, NASCAR Talladega
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-MR-01",
                "sport": "motor-racing",
                "sport_name": "Motor Racing",
                "olbg_sport_id": 14,
                "competition": "MotoGP Australian Grand Prix — Tissot Sprint",
                "event": "2026 Australian Motorcycle Grand Prix — Saturday Sprint",
                "away": "Jorge Martin / Marc Marquez",
                "home": "Marco Bezzecchi",
                "venue": "Phillip Island Grand Prix Circuit, Victoria, Australia (4.448 km)",
                "start_utc": "2026-10-24T04:00:00Z",
                "official_source_name": "MotoGP Official GP18 Australia Coverage & Calendar",
                "official_source_url": "https://www.motogp.com/en/calendar?view=grid",
                "secondary_source_url": "https://www.motogp.com/",
                "olbg_url": "https://www.olbg.com/betting-tips/Motor_Racing/14",
                "form_summary": "Marco Bezzecchi topped Friday Practice P1 at Phillip Island as four Aprilias locked Q2 places alongside championship leader Jorge Martin (1st) & Marc Marquez",
                "stats_summary": "Bezzecchi sits 3rd in WDC behind teammate Martin with no Aprilia team orders in effect",
                "injury_summary": "Joan Mir (#36 Honda) officially ruled out of Australian GP with no replacement rider.",
                "unconfirmed_fields": [],
                "markets": price_field_event(
                    winner_label="Tissot Sprint Winner",
                    field_weights=[
                        ("Marco Bezzecchi", 0.305),
                        ("Jorge Martin", 0.255),
                        ("Marc Marquez", 0.215),
                        ("Pedro Acosta", 0.085),
                        ("Francesco Bagnaia", 0.065),
                        ("Field (Others)", 0.075),
                    ],
                    h2h_label="Sprint Matchup: Marco Bezzecchi vs Jorge Martin",
                    h2h_pair=[("Marco Bezzecchi", 0.545), ("Jorge Martin", 0.455)],
                    total_label="Winning Sprint Margin vs 0.65 Seconds",
                    total_pair=[("Over 0.65s Margin", 0.470), ("Under 0.65s Margin", 0.530)],
                    total_line=0.65,
                    deriv_label="Aprilia Bike Wins Sprint?",
                    deriv_pair=[("Yes (Aprilia Winner)", 0.595), ("No (Ducati/KTM/Other)", 0.405)],
                ),
                "winner_pick": "Marco Bezzecchi",
                "pick_market": "winner",
                "pick_selection": "Marco Bezzecchi",
                "confidence": "high",
                "prediction_text": (
                    "Back Marco Bezzecchi to win Saturday's Tissot Sprint at Phillip Island after setting the "
                    "benchmark P1 lap in a wildlife-interrupted Friday Practice where four Aprilias surged directly "
                    "into Q2. Aprilia team manager Paolo Bonora confirmed on Friday that no team orders apply between "
                    "championship leader Jorge Martin and third-placed Bezzecchi, while Honda's Joan Mir (#36) sits "
                    "out injured without replacement. Flowing high-corner-speed sweepers suit Aprilia's front-end "
                    "stability even against Marc Marquez."
                ),
            },
            {
                "id": "87b3-MR-02",
                "sport": "motor-racing",
                "sport_name": "Motor Racing",
                "olbg_sport_id": 14,
                "competition": "Formula 1 MSC Cruises United States Grand Prix — Qualifying",
                "event": "2026 F1 United States Grand Prix — Pole Position",
                "away": "Max Verstappen / Lando Norris",
                "home": "Charles Leclerc",
                "venue": "Circuit of The Americas, Austin, TX (5.513 km, 20 Corners)",
                "start_utc": "2026-10-24T21:00:00Z",
                "official_source_name": "Formula 1 Official Race Hub & FP1 Results (Race 1297)",
                "official_source_url": "https://www.formula1.com/en/racing/2026/united-states",
                "secondary_source_url": "https://www.formula1.com/en/results/2026/drivers",
                "olbg_url": "https://www.olbg.com/betting-tips/Motor_Racing/14",
                "form_summary": "FP1 top 5: 1. Leclerc 1:36.052, 2. Verstappen +0.084s, 3. Norris +0.245s, 4. Russell +0.326s, 5. Antonelli +0.481s",
                "stats_summary": "Conventional weekend (no Sprint); Pirelli C2/C3/C4 tyres; resurfaced Turns 9-11; WDC: Antonelli 340, Russell 238, Hamilton 229, Verstappen 221, Leclerc 215",
                "injury_summary": "All 22 full-time F1 drivers completed FP1 cleanly in Austin.",
                "unconfirmed_fields": [],
                "markets": price_field_event(
                    winner_label="Qualifying Pole Winner",
                    field_weights=[
                        ("Max Verstappen", 0.285),
                        ("Charles Leclerc", 0.275),
                        ("Lando Norris", 0.175),
                        ("George Russell", 0.115),
                        ("Kimi Antonelli", 0.085),
                        ("Lewis Hamilton / Field", 0.065),
                    ],
                    h2h_label="Qualifying H2H: Charles Leclerc vs Lando Norris",
                    h2h_pair=[("Charles Leclerc", 0.585), ("Lando Norris", 0.415)],
                    total_label="Pole Winning Margin vs 0.100 Seconds",
                    total_pair=[("Over 0.100s", 0.485), ("Under 0.100s", 0.515)],
                    total_line=0.100,
                    deriv_label="Ferrari Front-Row Start (Top 2)?",
                    deriv_pair=[("Yes Ferrari Top-2", 0.560), ("No Ferrari Top-2", 0.440)],
                ),
                "winner_pick": "Max Verstappen",
                "pick_market": "handicap",
                "pick_selection": "Charles Leclerc",
                "confidence": "high",
                "prediction_text": (
                    "Play Charles Leclerc in his Saturday qualifying head-to-head over Lando Norris—while pricing Max "
                    "Verstappen a whisker ahead for overall pole—at Circuit of The Americas (21:00 UTC). Leclerc "
                    "topped Friday's opening practice in 1:36.052 on the resurfaced Sector 2 asphalt, edging "
                    "Verstappen by 0.084s and clearing Norris (+0.245s), George Russell (+0.326s), and championship "
                    "leader Kimi Antonelli (+0.481s). Ferrari's single-lap traction out of Turns 11 and 16 on C4 softs "
                    "has looked dialled in from the first run."
                ),
            },
            {
                "id": "87b3-MR-03",
                "sport": "motor-racing",
                "sport_name": "Motor Racing",
                "olbg_sport_id": 14,
                "competition": "MotoGP Australian Grand Prix — Grand Prix Race",
                "event": "2026 Australian Motorcycle Grand Prix — Full Race",
                "away": "Jorge Martin / Marco Bezzecchi",
                "home": "Marc Marquez",
                "venue": "Phillip Island Grand Prix Circuit, Victoria, Australia (27 Laps)",
                "start_utc": "2026-10-25T03:00:00Z",
                "official_source_name": "MotoGP Official GP18 Australia Schedule & Standings",
                "official_source_url": "https://www.motogp.com/",
                "secondary_source_url": "https://www.motogp.com/en/calendar?view=grid",
                "olbg_url": "https://www.olbg.com/betting-tips/Motor_Racing/14",
                "form_summary": "GP18 of 22; Aprilia duo Martin & Bezzecchi lead Friday speed charts while Marc Marquez stalks on long-run tyre wear",
                "stats_summary": "Phillip Island notorious rear-tyre degradation over full 27-lap left-hand bias distance",
                "injury_summary": "Joan Mir (#36) sidelined; 21-bike grid expected for Sunday GP.",
                "unconfirmed_fields": [],
                "markets": price_field_event(
                    winner_label="Grand Prix Winner",
                    field_weights=[
                        ("Marc Marquez", 0.275),
                        ("Marco Bezzecchi", 0.265),
                        ("Jorge Martin", 0.235),
                        ("Pedro Acosta", 0.090),
                        ("Alex Marquez", 0.070),
                        ("Field (Others)", 0.065),
                    ],
                    h2h_label="Race H2H: Marc Marquez vs Jorge Martin",
                    h2h_pair=[("Marc Marquez", 0.535), ("Jorge Martin", 0.465)],
                    total_label="Classified Finishers vs 17.5 Riders",
                    total_pair=[("Over 17.5 Finishers", 0.510), ("Under 17.5 Finishers", 0.490)],
                    total_line=17.5,
                    deriv_label="Marc Marquez Podium Finish (Top 3)",
                    deriv_pair=[("Marquez Top-3 Yes", 0.640), ("Marquez Outside Top-3", 0.360)],
                ),
                "winner_pick": "Marc Marquez",
                "pick_market": "winner",
                "pick_selection": "Marc Marquez",
                "confidence": "medium",
                "prediction_text": (
                    "Side with Marc Marquez outright in Sunday's full-distance Australian Grand Prix at Phillip Island "
                    "(03:00 UTC). While Marco Bezzecchi and championship leader Jorge Martin put four Aprilias into Q2 "
                    "during Friday's time attack, Phillip Island's relentless anti-clockwise sweepers punish asymmetric "
                    "rear Michelin rubber across the closing eight laps more than any circuit on the 22-round "
                    "calendar. Marquez's unmatched throttle preservation on worn rubber at Lukey Heights and Stoner "
                    "Corner makes him prime Sunday value."
                ),
            },
            {
                "id": "87b3-MR-04",
                "sport": "motor-racing",
                "sport_name": "Motor Racing",
                "olbg_sport_id": 14,
                "competition": "NASCAR Cup Series — YellaWood 500 (The Chase Race #8)",
                "event": "2026 NASCAR Cup Series YellaWood 500 at Talladega",
                "away": "Tyler Reddick / Chase Briscoe",
                "home": "Ryan Blaney",
                "venue": "Talladega Superspeedway, Talladega, AL (2.66-Mile Tri-Oval, 188 Laps)",
                "start_utc": "2026-10-25T18:00:00Z",
                "official_source_name": "NASCAR Official Talladega Weekend Schedule & Chase Standings",
                "official_source_url": "https://www.nascar.com/weekend-schedule/weekend-schedule-for-2026-talladega-superspeedway-chase-race/",
                "secondary_source_url": "https://www.nascar.com/news-media/2026/10/23/2026-fantasy-fastlane-talladega-chase/",
                "olbg_url": "https://www.olbg.com/betting-tips/Motor_Racing/14",
                "form_summary": "Chase standings (3 left): 1. Larson 2370, 2. Bell -5, 3. Briscoe -24, 4. Hamlin -31, 5. Blaney -40 (finishes of 5th, 5th, 3rd, 2nd in last 4!), 7. Reddick -56 (Phoenix winner)",
                "stats_summary": "Blaney owns 6 career drafting-track Cup wins (3 at Talladega) & top-2 in 19% (11/57) of drafting starts; new 3.5-inch rear spoiler",
                "injury_summary": "Full Cup Charter field entered; Saturday two-round qualifying at 17:00 UTC.",
                "unconfirmed_fields": [],
                "markets": price_field_event(
                    winner_label="YellaWood 500 Race Winner",
                    field_weights=[
                        ("Ryan Blaney", 0.115),
                        ("Tyler Reddick", 0.095),
                        ("Brad Keselowski", 0.085),
                        ("Joey Logano", 0.080),
                        ("Chase Briscoe", 0.075),
                        ("Field (35 Others)", 0.550),
                    ],
                    h2h_label="Driver Matchup: Tyler Reddick vs Chase Briscoe",
                    h2h_pair=[("Tyler Reddick", 0.552), ("Chase Briscoe", 0.448)],
                    total_label="Total Race Cautions vs 6.5",
                    total_pair=[("Over 6.5 Cautions", 0.545), ("Under 6.5 Cautions", 0.455)],
                    total_line=6.5,
                    deriv_label="Ryan Blaney Top-5 Finish",
                    deriv_pair=[("Blaney Top-5 Yes", 0.345), ("Blaney Outside Top-5", 0.655)],
                ),
                "winner_pick": "Ryan Blaney",
                "pick_market": "handicap",
                "pick_selection": "Tyler Reddick",
                "confidence": "medium",
                "prediction_text": (
                    "Play Tyler Reddick over defending fall winner Chase Briscoe in Sunday's YellaWood 500 head-to-head "
                    "at Talladega Superspeedway, while pricing three-time Talladega winner Ryan Blaney (finishes of "
                    "5th, 5th, 3rd, and 2nd in his last four Chase starts, sitting -40 behind Kyle Larson) as top "
                    "outright choice. Reddick just conquered Phoenix and leads the entire Cup garage with 233 "
                    "superspeedway points in 2026 after topping 2025 with 199, whereas last fall's victory was "
                    "Briscoe's lone top-10 across his past six Talladega trips."
                ),
            },
            {
                "id": "87b3-MR-05",
                "sport": "motor-racing",
                "sport_name": "Motor Racing",
                "olbg_sport_id": 14,
                "competition": "Formula 1 MSC Cruises United States Grand Prix — Race",
                "event": "2026 F1 United States Grand Prix — 56-Lap Race",
                "away": "Charles Leclerc / Kimi Antonelli",
                "home": "Max Verstappen",
                "venue": "Circuit of The Americas, Austin, TX (308.432 km, 56 Laps)",
                "start_utc": "2026-10-25T20:00:00Z",
                "official_source_name": "Formula 1 Official Race Hub & Drivers Championship Standings",
                "official_source_url": "https://www.formula1.com/en/racing/2026/united-states",
                "secondary_source_url": "https://www.formula1.com/en/results/2026/drivers",
                "olbg_url": "https://www.olbg.com/betting-tips/Motor_Racing/14",
                "form_summary": "Verstappen (4th, 221 pts) won consecutive Grands Prix in Malaysia & Singapore + 4 of last 5 COTA GPs; P2 (+0.084s) in FP1",
                "stats_summary": "WDC top 6: Antonelli 340, Russell 238, Hamilton 229, Verstappen 221, Leclerc 215, Norris 201",
                "injury_summary": "No grid penalties posted entering Friday evening session.",
                "unconfirmed_fields": [],
                "markets": price_field_event(
                    winner_label="Grand Prix Race Winner",
                    field_weights=[
                        ("Max Verstappen", 0.335),
                        ("Charles Leclerc", 0.245),
                        ("Kimi Antonelli", 0.140),
                        ("Lando Norris", 0.125),
                        ("George Russell", 0.095),
                        ("Lewis Hamilton / Field", 0.060),
                    ],
                    h2h_label="Race H2H: Max Verstappen vs Charles Leclerc",
                    h2h_pair=[("Max Verstappen", 0.578), ("Charles Leclerc", 0.422)],
                    total_label="Safety Car Deployed During Race?",
                    total_pair=[("Yes Safety Car", 0.565), ("No Safety Car", 0.435)],
                    total_line=0.5,
                    deriv_label="Kimi Antonelli Podium Finish (Top 3)",
                    deriv_pair=[("Antonelli Top-3 Yes", 0.485), ("Antonelli Outside Top-3", 0.515)],
                ),
                "winner_pick": "Max Verstappen",
                "pick_market": "winner",
                "pick_selection": "Max Verstappen",
                "confidence": "high",
                "prediction_text": (
                    "Back Max Verstappen outright to win Sunday's 56-lap United States Grand Prix at Circuit of The "
                    "Americas (20:00 UTC). Fresh off back-to-back victories in Malaysia and Singapore, Red Bull's "
                    "four-time champion has captured four of the last five Austin Grands Prix and slotted within "
                    "0.084s of Charles Leclerc's FP1 benchmark (1:36.052) on Friday afternoon. With Mercedes runaway "
                    "leader Kimi Antonelli (340 points) protecting championship margin over George Russell (238) and "
                    "Lewis Hamilton (229), Verstappen can attack COTA's two-stop medium-hard strategy aggressively."
                ),
            },
        ]
    )

    # =========================================================================
    # 7. RUGBY LEAGUE (OLBG ID 10) — 5 RLWC 2026 Round 2 Matches (nrl.com)
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-RL-01",
                "sport": "rugby-league",
                "sport_name": "Rugby League",
                "olbg_sport_id": 10,
                "competition": "2026 Women's Rugby League World Cup — Round 2",
                "event": "Fiji Bulikula vs Papua New Guinea Orchids",
                "away": "Fiji Bulikula",
                "home": "Papua New Guinea Orchids",
                "venue": "Santos National Football Stadium, Port Moresby",
                "start_utc": "2026-10-24T02:15:00Z",
                "official_source_name": "NRL Official Women's RLWC Round 2 Team Lists",
                "official_source_url": "https://www.nrl.com/news/2026/10/20/world-cup-team-lists-womens-round-2/",
                "secondary_source_url": "https://www.nrl.com/",
                "olbg_url": "https://www.olbg.com/betting-tips/Rugby_League/10",
                "form_summary": "PNG Orchids return to packed Port Moresby home turf after opening loss to Jillaroos; Fiji led by NRLW back-rower Talei Holmes",
                "stats_summary": "Elsie Albert captains PNG middle forward pack alongside Belinda Gwasamun & Essay Banu",
                "injury_summary": "Official Round 2 17-player squads confirmed on nrl.com; Elsie Albert starts at prop (#10).",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Papua New Guinea Orchids",
                    "Fiji Bulikula",
                    mu_margin_a=4.2,
                    sigma_margin=13.5,
                    mu_total=38.5,
                    sigma_total=11.2,
                    spread_a=-4.5,
                    total_line=38.5,
                    unit_label="Point",
                ),
                "winner_pick": "Papua New Guinea Orchids",
                "pick_market": "winner",
                "pick_selection": "Papua New Guinea Orchids",
                "confidence": "medium",
                "prediction_text": (
                    "Side with Papua New Guinea Orchids on the moneyline in Saturday's Women's World Cup Round 2 "
                    "double-header opener at Santos National Football Stadium in Port Moresby. Stepping down in class "
                    "after facing the defending champion Jillaroos in Round 1, captain Elsie Albert anchors a physical "
                    "Orchids middle alongside Belinda Gwasamun in stifling home humidity. Fiji Bulikula carry genuine "
                    "strike out wide through Cassie Staples and Talei Holmes, yet Port Moresby's crowd and forward "
                    "yardage tilt a competitive Pacific contest toward PNG."
                ),
            },
            {
                "id": "87b3-RL-02",
                "sport": "rugby-league",
                "sport_name": "Rugby League",
                "olbg_sport_id": 10,
                "competition": "2026 Men's Rugby League World Cup — Round 2",
                "event": "Papua New Guinea Kumuls vs Samoa",
                "away": "Samoa",
                "home": "Papua New Guinea Kumuls",
                "venue": "Santos National Football Stadium, Port Moresby",
                "start_utc": "2026-10-24T04:25:00Z",
                "official_source_name": "NRL Official Men's RLWC Round 2 Team Lists",
                "official_source_url": "https://www.nrl.com/news/2026/10/20/world-cup-team-lists-mens-round-2/",
                "secondary_source_url": "https://www.nrl.com/",
                "olbg_url": "https://www.olbg.com/betting-tips/Rugby_League/10",
                "form_summary": "Samoa stacked with NRL premiership spine & pack (Luai, Crichton, To'o, Haas); PNG host in Port Moresby led by Lachlan Lam & Nene Macdonald",
                "stats_summary": "Samoa forward power (Payne Haas, Junior Paulo, Jeremiah Nanai) vs PNG tropical home cauldron",
                "injury_summary": "Samoa: Deine Mariner ruled out (hamstring), Melbourne speedster Sua Fa'alogo called onto wing; Simi Sasagi #14. PNG: Morea Morea #1, Rhyse Martin #11, Jack de Belin #13.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Samoa",
                    "Papua New Guinea Kumuls",
                    mu_margin_a=11.5,
                    sigma_margin=13.8,
                    mu_total=44.5,
                    sigma_total=11.8,
                    spread_a=-10.5,
                    total_line=44.5,
                    unit_label="Point",
                ),
                "winner_pick": "Samoa",
                "pick_market": "handicap",
                "pick_selection": "Samoa -10.5",
                "confidence": "high",
                "prediction_text": (
                    "Play Samoa -10.5 points—and Samoa to win—when they visit Port Moresby to face the Papua New "
                    "Guinea Kumuls on Saturday afternoon. Although winger Deine Mariner is sidelined by a hamstring "
                    "strain, coach Ben Gardiner slots electrifying Storm flyer Sua Fa'alogo straight opposite Brian "
                    "To'o outside Stephen Crichton and Jarome Luai, behind a monster pack led by Payne Haas, Junior "
                    "Paulo, and Jeremiah Nanai. Lachlan Lam and Rhyse Martin keep PNG competitive early, but Samoa's "
                    "bench depth pulls clear late."
                ),
            },
            {
                "id": "87b3-RL-03",
                "sport": "rugby-league",
                "sport_name": "Rugby League",
                "olbg_sport_id": 10,
                "competition": "2026 Men's Rugby League World Cup — Round 2",
                "event": "England vs France",
                "away": "France",
                "home": "England",
                "venue": "HBF Park, Perth, WA",
                "start_utc": "2026-10-24T06:35:00Z",
                "official_source_name": "NRL Official Men's RLWC Round 2 Team Lists",
                "official_source_url": "https://www.nrl.com/news/2026/10/20/world-cup-team-lists-mens-round-2/",
                "secondary_source_url": "https://www.nrl.com/",
                "olbg_url": "https://www.olbg.com/betting-tips/Rugby_League/10",
                "form_summary": "England opened World Cup with statement Round 1 victory over Tonga; France rebuild around Arthur Mourgue & Theo Fages",
                "stats_summary": "England won last five Test meetings vs France by 26+ points; fast dry surface in Perth",
                "injury_summary": "England: loose forward Morgan Knowles ruled out injured (Mikolaj Oledzki #15 onto bench; Matty Ashton replaces Joe Burgess on wing; AJ Brimson #1, George Williams #6, Mikey Lewis #7).",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "England",
                    "France",
                    mu_margin_a=30.5,
                    sigma_margin=14.2,
                    mu_total=52.5,
                    sigma_total=12.4,
                    spread_a=-29.5,
                    total_line=51.5,
                    unit_label="Point",
                ),
                "winner_pick": "England",
                "pick_market": "handicap",
                "pick_selection": "England -29.5",
                "confidence": "medium",
                "prediction_text": (
                    "Take England -29.5 on the handicap—with England heavy match-winner chalk—against European rivals "
                    "France at HBF Park in Perth. Coming off an impressive Round 1 victory over Tonga, Shaun Wane "
                    "loses loose forward Morgan Knowles to injury, bringing Mikolaj Oledzki onto the interchange and "
                    "recalling finisher Matty Ashton on the wing outside Herbie Farnworth, AJ Brimson, George "
                    "Williams, and Mikey Lewis. Against a Super League-based French side led by Arthur Mourgue and "
                    "Theo Fages, England's ruck speed routinely piles on five-plus second-half tries."
                ),
            },
            {
                "id": "87b3-RL-04",
                "sport": "rugby-league",
                "sport_name": "Rugby League",
                "olbg_sport_id": 10,
                "competition": "2026 Men's Rugby League World Cup — Round 2",
                "event": "New Zealand Kiwis vs Cook Islands Aitu",
                "away": "Cook Islands Aitu",
                "home": "New Zealand Kiwis",
                "venue": "One New Zealand Stadium, Christchurch, New Zealand",
                "start_utc": "2026-10-25T05:05:00Z",
                "official_source_name": "NRL Official Men's RLWC Round 2 Team Lists",
                "official_source_url": "https://www.nrl.com/news/2026/10/20/world-cup-team-lists-mens-round-2/",
                "secondary_source_url": "https://www.nrl.com/",
                "olbg_url": "https://www.olbg.com/betting-tips/Rugby_League/10",
                "form_summary": "NZ Kiwis return home to Christchurch after Round 1 loss to Australia; Cook Islands boosted by Valentine Holmes debut",
                "stats_summary": "NZ pack (Fisher-Harris, Tapine, Leota) massive yardage edge, but Cook Islands add NRL star Holmes at #1",
                "injury_summary": "NZ: Kalyn Ponga ruled out of tournament (broken arm vs Australia) -> Keano Kini #1, Phoenix Crossland #14. Cook Islands: Valentine Holmes debuts at fullback, KL Iro #4, Esan Marsters #6,Brendan Piakura #11.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "New Zealand Kiwis",
                    "Cook Islands Aitu",
                    mu_margin_a=27.5,
                    sigma_margin=14.4,
                    mu_total=53.5,
                    sigma_total=12.6,
                    spread_a=-28.5,
                    total_line=52.5,
                    unit_label="Point",
                ),
                "winner_pick": "New Zealand Kiwis",
                "pick_market": "handicap",
                "pick_selection": "Cook Islands Aitu +28.5",
                "confidence": "medium",
                "prediction_text": (
                    "Play Cook Islands Aitu +28.5 points—while keeping New Zealand as clear match winners—on Sunday in "
                    "Christchurch. The Kiwis suffered a tournament-ending broken arm to star fullback Kalyn Ponga in "
                    "their opener against Australia, handing livewire Keano Kini the No. 1 jersey alongside Dylan "
                    "Brown and Jahrome Hughes. Meanwhile, Cook Islands receive a massive boost with prolific goal-kicker "
                    "and finisher Valentine Holmes making his Aitu debut at fullback beside KL Iro, Esan Marsters, "
                    "and Brendan Piakura, giving the underdogs real scoring punch inside four converted tries."
                ),
            },
            {
                "id": "87b3-RL-05",
                "sport": "rugby-league",
                "sport_name": "Rugby League",
                "olbg_sport_id": 10,
                "competition": "2026 Men's Rugby League World Cup — Round 2",
                "event": "Australia Kangaroos vs Fiji Bati",
                "away": "Fiji Bati",
                "home": "Australia Kangaroos",
                "venue": "Suncorp Stadium, Brisbane, QLD",
                "start_utc": "2026-10-25T09:05:00Z",
                "official_source_name": "NRL Official Men's RLWC Round 2 Team Lists",
                "official_source_url": "https://www.nrl.com/news/2026/10/20/world-cup-team-lists-mens-round-2/",
                "secondary_source_url": "https://www.nrl.com/",
                "olbg_url": "https://www.olbg.com/betting-tips/Rugby_League/10",
                "form_summary": "Australia beat NZ in Round 1 opener; heavy squad rotation (7 changes) for Brisbane clash vs Fiji",
                "stats_summary": "Australia completely new halves pairing (Cody Walker #6, Tom Dearden #7); Fiji field Bula, Turuva, Sivo & Kikau",
                "injury_summary": "AUS: Mitchell Moses ruled out injured; Nathan Cleary, Cameron Munster, Harry Grant, Latrell Mitchell, Patrick Carrigan & Haas rested; James Tedesco returns at #1, Connor Watson #9, David Fifita #12.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Australia Kangaroos",
                    "Fiji Bati",
                    mu_margin_a=24.8,
                    sigma_margin=14.0,
                    mu_total=51.5,
                    sigma_total=12.2,
                    spread_a=-26.5,
                    total_line=50.5,
                    unit_label="Point",
                ),
                "winner_pick": "Australia Kangaroos",
                "pick_market": "handicap",
                "pick_selection": "Fiji Bati +26.5",
                "confidence": "high",
                "prediction_text": (
                    "Back Fiji Bati +26.5 on the Suncorp Stadium handicap—while Australia still take the victory—after "
                    "Kevin Walters made seven sweeping changes to the Kangaroos' Round 1 lineup. With Mitchell Moses "
                    "injured and Nathan Cleary, Cameron Munster, Harry Grant, Latrell Mitchell, and Patrick Carrigan "
                    "all rested, Australia pair debutant combination Cody Walker and Tom Dearden in the halves around "
                    "returning skipper James Tedesco. Fiji field genuine NRL firepower in Jahream Bula, Sunia Turuva, "
                    "Maika Sivo, Kurt Donoghoe, Tui Kamikamica, and Viliame Kikau to stay within 26."
                ),
            },
        ]
    )

    # =========================================================================
    # 8. RUGBY UNION (OLBG ID 9) — 5 URC Round 4 Saturday Fixtures (unitedrugby.com)
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-RU-01",
                "sport": "rugby-union",
                "sport_name": "Rugby Union",
                "olbg_sport_id": 9,
                "competition": "United Rugby Championship — Round 4",
                "event": "Vodacom Bulls vs Ulster Rugby",
                "away": "Ulster Rugby",
                "home": "Vodacom Bulls",
                "venue": "Loftus Versfeld, Pretoria (Altitude 1,350m)",
                "start_utc": "2026-10-24T11:45:00Z",
                "official_source_name": "URC Official Round 4 Team Announcements & Match-Centre Table",
                "official_source_url": "https://www.unitedrugby.com/latest/news/round-4-team-announcements/",
                "secondary_source_url": "https://stats.unitedrugby.com/match-centre/table/",
                "olbg_url": "https://www.olbg.com/betting-tips/Rugby_Union/9",
                "form_summary": "Bulls 4th (2-0-1, 11 pts, +72 PD); Ulster 8th (2-0-1, 8 pts, +20 PD)",
                "stats_summary": "Bulls own URC's best scoring differential (+72 thru 3 rounds); Loftus Versfeld highveld heat & altitude",
                "injury_summary": "Official XVs named: Handre Pollard captains Bulls at #10 with Willie le Roux #15, Kurt-Lee Arendse #11, Canan Moodie #13, Wilco Louw #3; Iain Henderson captains Ulster with Jacob Stockdale & Nathan Doak.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Vodacom Bulls",
                    "Ulster Rugby",
                    mu_margin_a=12.4,
                    sigma_margin=13.2,
                    mu_total=55.5,
                    sigma_total=12.5,
                    spread_a=-10.5,
                    total_line=54.5,
                    three_way_draw_band=0.5,
                    unit_label="Point",
                ),
                "winner_pick": "Vodacom Bulls",
                "pick_market": "handicap",
                "pick_selection": "Vodacom Bulls -10.5",
                "confidence": "high",
                "prediction_text": (
                    "Play Vodacom Bulls -10.5 points—and Bulls to win—at Loftus Versfeld against eighth-placed Ulster "
                    "(2-0-1, 8 points, +20 differential). Pretoria's highveld hosts enter Round 4 sitting fourth on "
                    "11 points with a league-best +72 points differential, and coach Jake White hands captaincy to "
                    "Springbok fly-half Handre Pollard inside an electric back three of Willie le Roux, Kurt-Lee "
                    "Arendse, and Canan Moodie behind tighthead anchor Wilco Louw. Even with Iain Henderson returning "
                    "to lead Ulster, Pretoria's final-quarter altitude attrition stretches visiting packs past double digits."
                ),
            },
            {
                "id": "87b3-RU-02",
                "sport": "rugby-union",
                "sport_name": "Rugby Union",
                "olbg_sport_id": 9,
                "competition": "United Rugby Championship — Round 4",
                "event": "DHL Stormers vs Scarlets",
                "away": "Scarlets",
                "home": "DHL Stormers",
                "venue": "DHL Stadium, Cape Town",
                "start_utc": "2026-10-24T14:00:00Z",
                "official_source_name": "URC Official Round 4 Team Announcements & Match-Centre Table",
                "official_source_url": "https://www.unitedrugby.com/latest/news/round-4-team-announcements/",
                "secondary_source_url": "https://stats.unitedrugby.com/match-centre/table/",
                "olbg_url": "https://www.olbg.com/betting-tips/Rugby_Union/9",
                "form_summary": "Stormers 5th (2-0-1, 11 pts, +25 PD); Scarlets 9th (1-0-2, 7 pts, -8 PD)",
                "stats_summary": "Stormers unleash Springbok playmakers Feinberg-Mngomezulu (#10) & Damian Willemse (#12) with Evan Roos (#8)",
                "injury_summary": "Official XVs named: Stormers captained by Salmaan Moerat (#5) with Warrick Gelant (#15); Scarlets captained by Josh Macleod (#7) with Blair Murray (#15) & Sam Costelow (#10).",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "DHL Stormers",
                    "Scarlets",
                    mu_margin_a=15.8,
                    sigma_margin=13.4,
                    mu_total=52.5,
                    sigma_total=12.2,
                    spread_a=-14.5,
                    total_line=52.5,
                    three_way_draw_band=0.5,
                    unit_label="Point",
                ),
                "winner_pick": "DHL Stormers",
                "pick_market": "handicap",
                "pick_selection": "DHL Stormers -14.5",
                "confidence": "medium",
                "prediction_text": (
                    "Side with DHL Stormers -14.5 on the handicap—alongside Stormers as clear home winners—when ninth-"
                    "placed Scarlets (1-0-2, 7 points, -8 differential) visit Cape Town. Fifth-placed Stormers (2-0-1, "
                    "11 points, +25 differential) roll out a dynamic Springbok spine featuring Sacha Feinberg-"
                    "Mngomezulu at fly-half, Damian Willemse at inside centre, Warrick Gelant at fullback, and ball-"
                    "carrying No. 8 Evan Roos behind skipper Salmaan Moerat. Josh Macleod and Sam Costelow keep "
                    "Scarlets competitive at the breakdown, yet Cape Town counter-attacking pace breaks this open."
                ),
            },
            {
                "id": "87b3-RU-03",
                "sport": "rugby-union",
                "sport_name": "Rugby Union",
                "olbg_sport_id": 9,
                "competition": "United Rugby Championship — Round 4",
                "event": "Benetton Rugby vs Glasgow Warriors",
                "away": "Glasgow Warriors",
                "home": "Benetton Rugby",
                "venue": "Stadio Comunale di Monigo, Treviso",
                "start_utc": "2026-10-24T14:00:00Z",
                "official_source_name": "URC Official Round 4 Team Announcements & Match-Centre Table",
                "official_source_url": "https://www.unitedrugby.com/latest/news/round-4-team-announcements/",
                "secondary_source_url": "https://stats.unitedrugby.com/match-centre/table/",
                "olbg_url": "https://www.olbg.com/betting-tips/Rugby_Union/9",
                "form_summary": "Glasgow 2nd (unbeaten 3-0-0, 13 pts, +32 PD); Benetton 13th (1-0-2, 5 pts, -26 PD)",
                "stats_summary": "Glasgow boast Scotland midfield Sione Tuipulotu & Huw Jones plus Kyle Steyn, Matt Fagerson & Jack Dempsey",
                "injury_summary": "Official XVs named: Michele Lamaro captains Benetton with Ignacio Mendy, Malakai Fekitoa & Jacob Umaga; Kyle Steyn captains full-strength Glasgow.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Glasgow Warriors",
                    "Benetton Rugby",
                    mu_margin_a=5.6,
                    sigma_margin=12.6,
                    mu_total=47.5,
                    sigma_total=11.8,
                    spread_a=-4.5,
                    total_line=47.5,
                    three_way_draw_band=0.5,
                    unit_label="Point",
                ),
                "winner_pick": "Glasgow Warriors",
                "pick_market": "winner",
                "pick_selection": "Glasgow Warriors",
                "confidence": "high",
                "prediction_text": (
                    "Back unbeaten Glasgow Warriors (3-0-0, 13 points, +32 differential) to win outright in Treviso "
                    "against 13th-placed Benetton (1-0-2, 5 points, -26 differential). Franco Smith names an "
                    "international-calibre visiting lineup led by skipper Kyle Steyn alongside Scottish midfield "
                    "axis Sione Tuipulotu and Huw Jones, plus abrasive back-rowers Matt Fagerson, Rory Darge, and "
                    "Jack Dempsey. Stadio Monigo is never straightforward against Michele Lamaro, Malakai Fekitoa, "
                    "and Jacob Umaga, yet Glasgow's multi-phase tempo has outclassed every opponent so far."
                ),
            },
            {
                "id": "87b3-RU-04",
                "sport": "rugby-union",
                "sport_name": "Rugby Union",
                "olbg_sport_id": 9,
                "competition": "United Rugby Championship — Round 4 (Irish Interpro)",
                "event": "Leinster Rugby vs Munster Rugby",
                "away": "Munster Rugby",
                "home": "Leinster Rugby",
                "venue": "Aviva Stadium, Dublin",
                "start_utc": "2026-10-24T17:00:00Z",
                "official_source_name": "URC Official Round 4 Team Announcements & Match-Centre Table",
                "official_source_url": "https://www.unitedrugby.com/latest/news/round-4-team-announcements/",
                "secondary_source_url": "https://stats.unitedrugby.com/match-centre/table/",
                "olbg_url": "https://www.olbg.com/betting-tips/Rugby_Union/9",
                "form_summary": "Munster 6th (2-0-1, 9 pts, +3 PD); Leinster 7th (2-0-1, 8 pts, -9 PD after early SA/opening rotation)",
                "stats_summary": "Leinster recall Test heavyweights Doris, van der Flier, Conan, Sheehan, Furlong, Gibson-Park & Ringrose at Aviva",
                "injury_summary": "Official XVs named: Caelan Doris captains Leinster with Sam Prendergast at #10 & RG Snyman on bench; Tadhg Beirne captains Munster with Craig Casey (#9) & Jack Crowley (#10).",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Leinster Rugby",
                    "Munster Rugby",
                    mu_margin_a=8.8,
                    sigma_margin=12.4,
                    mu_total=45.5,
                    sigma_total=11.4,
                    spread_a=-8.5,
                    total_line=45.5,
                    three_way_draw_band=0.5,
                    unit_label="Point",
                ),
                "winner_pick": "Leinster Rugby",
                "pick_market": "total",
                "pick_selection": "Under 45.5",
                "confidence": "high",
                "prediction_text": (
                    "Play Under 45.5 total points—while picking Leinster to win the Aviva Stadium derby—when sixth-"
                    "placed Munster (2-0-1, 9 points) visit seventh-placed Leinster (2-0-1, 8 points). Leo Cullen "
                    "reloads his Ireland Test pack with Dan Sheehan, Tadhg Furlong, James Ryan, Josh van der Flier, "
                    "Jack Conan, and skipper Caelan Doris, plus RG Snyman off the bench, opposite Tadhg Beirne, "
                    "Craig Casey, and Jack Crowley. Autumn Dublin interpros featuring full Test packs consistently "
                    "turn into ferocious territorial arm-wrestles under 45 points."
                ),
            },
            {
                "id": "87b3-RU-05",
                "sport": "rugby-union",
                "sport_name": "Rugby Union",
                "olbg_sport_id": 9,
                "competition": "United Rugby Championship — Round 4 (Welsh Derby)",
                "event": "Ospreys vs Dragons RFC",
                "away": "Dragons RFC",
                "home": "Ospreys",
                "venue": "Brewery Field, Bridgend",
                "start_utc": "2026-10-24T18:00:00Z",
                "official_source_name": "URC Official Round 4 Team Announcements & Match-Centre Table",
                "official_source_url": "https://www.unitedrugby.com/latest/news/round-4-team-announcements/",
                "secondary_source_url": "https://stats.unitedrugby.com/match-centre/table/",
                "olbg_url": "https://www.olbg.com/betting-tips/Rugby_Union/9",
                "form_summary": "Dragons 7th/9 pts (2-0-1, -17 PD); Ospreys 11th (1-0-2, 6 pts, +2 PD)",
                "stats_summary": "Ospreys hold superior +2 points differential despite 1-2 start; Jac Morgan & Dewi Lake anchor home pack",
                "injury_summary": "Official XVs named: Dewi Lake captains Ospreys alongside Jac Morgan (#7), Ross Moriarty (#6), Gareth Thomas (#1) & Dan Edwards (#10); Angus O'Brien captains Dragons with Aaron Wainwright (#8) & Rio Dyer (#11).",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Ospreys",
                    "Dragons RFC",
                    mu_margin_a=6.8,
                    sigma_margin=12.5,
                    mu_total=44.5,
                    sigma_total=11.5,
                    spread_a=-5.5,
                    total_line=44.5,
                    three_way_draw_band=0.5,
                    unit_label="Point",
                ),
                "winner_pick": "Ospreys",
                "pick_market": "handicap",
                "pick_selection": "Ospreys -5.5",
                "confidence": "high",
                "prediction_text": (
                    "Back Ospreys -5.5 points—and Ospreys to win outright—at Brewery Field in Saturday night's Welsh "
                    "derby against Dragons RFC. Although Dragons sit three points higher in the early URC table (2-0-1, "
                    "9 points, -17 differential) than 11th-placed Ospreys (1-0-2, 6 points), Ospreys carry a positive "
                    "+2 differential and field a ferocious Test breakdown unit led by Wales co-captains Dewi Lake and "
                    "Jac Morgan alongside Ross Moriarty and Gareth Thomas. Against Aaron Wainwright's visitors, home "
                    "maul dominance carries Bridgend past a converted try."
                ),
            },
        ]
    )

    return rows
