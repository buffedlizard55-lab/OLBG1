#!/usr/bin/env python3
"""Official-source upcoming fixtures, originated multi-market parameters, and unique
human-written predictions for Sports 9-15 (35 fixtures) — Session 87b30e7f (T87B3).
"""
from __future__ import annotations

from typing import Any
from scripts.s87b30e7f_models import (
    price_field_event,
    price_normal_match,
    price_poisson_match,
    price_race_match,
)


def build_slate_part_b() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    # =========================================================================
    # 9. CRICKET (OLBG ID 7) — 5 Official ICC / BCCI / Cricket Australia Fixtures
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-CR-01",
                "sport": "cricket",
                "sport_name": "Cricket",
                "olbg_sport_id": 7,
                "competition": "Australia Domestic One-Day Cup 2026-27",
                "event": "Western Australia vs New South Wales",
                "away": "New South Wales",
                "home": "Western Australia",
                "venue": "WACA Ground, Perth, WA (50-Over List A)",
                "start_utc": "2026-10-24T06:00:00Z",
                "official_source_name": "Cricket Australia Official One-Day Cup 2026-27 Schedule",
                "official_source_url": "https://www.cricket.com.au/matches/series/CA:4688/one-day-cup-2026-27",
                "secondary_source_url": "https://www.cricket.com.au/",
                "olbg_url": "https://www.olbg.com/betting-tips/Cricket/7",
                "form_summary": "Perennial Marsh/One-Day Cup powerhouse Western Australia host NSW on bouncy Perth WACA deck",
                "stats_summary": "WACA new-ball carry rewards WA domestic seam battery while Test regulars tour South Africa",
                "injury_summary": "Both state sides operating without Australian Test squad members currently in Cape Town for 3rd Test.",
                "unconfirmed_fields": ["playing_xi_at_toss"],
                "markets": price_normal_match(
                    "Western Australia",
                    "New South Wales",
                    mu_margin_a=14.5,
                    sigma_margin=34.0,
                    mu_total=522.0,
                    sigma_total=48.0,
                    spread_a=-12.5,
                    total_line=524.5,
                    deriv_label="1st Innings Score Over/Under 269.5",
                    deriv_outcomes=[("Over 269.5 Runs", 0.488), ("Under 269.5 Runs", 0.512)],
                    overround=0.044,
                    unit_label="Run",
                ),
                "winner_pick": "Western Australia",
                "pick_market": "winner",
                "pick_selection": "Western Australia",
                "confidence": "high",
                "prediction_text": (
                    "Back Western Australia on the match-winner line at the WACA Ground in Saturday's Australian "
                    "One-Day Cup clash against New South Wales. With national Test regulars away in South Africa "
                    "preparing for Cape Town, Western Australia's domestic white-ball depth and familiarity with "
                    "steep Perth bounce consistently overwhelm interstate top orders during the opening ten-over "
                    "powerplay. Final XIs confirm at the toss, yet WA's home List A record makes them clear value."
                ),
            },
            {
                "id": "87b3-CR-02",
                "sport": "cricket",
                "sport_name": "Cricket",
                "olbg_sport_id": 7,
                "competition": "India Tour of New Zealand 2026 — 2nd T20I",
                "event": "New Zealand vs India (2nd T20I)",
                "away": "India",
                "home": "New Zealand",
                "venue": "Hagley Oval, Christchurch (20:00 NZDT / 07:00 UTC)",
                "start_utc": "2026-10-24T07:00:00Z",
                "official_source_name": "BCCI & ICC Official 2nd T20I Schedule & Squad Update",
                "official_source_url": "https://www.icc-cricket.com/news/injury-blow-for-india-ahead-of-second-t20i-with-new-zealand",
                "secondary_source_url": "https://www.bcci.tv/events/336/india-tour-of-new-zealand-2026/match/1924/2nd-t20i",
                "olbg_url": "https://www.olbg.com/betting-tips/Cricket/7",
                "form_summary": "India lead 5-match series 1-0 after chasing 226 in 1st T20I with 5 balls to spare",
                "stats_summary": "1st T20I stars: Sanju Samson 67 (33 balls), Shreyas Iyer 42 (29), Naman Dhir 42* (18); NZ posted 225",
                "injury_summary": "IND: Ishan Kishan ruled out of remaining 4 T20Is (right adductor strain); uncapped wicketkeeper Kumar Kushagra added to squad.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "India",
                    "New Zealand",
                    mu_margin_a=8.8,
                    sigma_margin=24.5,
                    mu_total=372.0,
                    sigma_total=36.0,
                    spread_a=-8.5,
                    total_line=368.5,
                    deriv_label="1st 6 Overs Powerplay Total (Combined)",
                    deriv_outcomes=[("Over 104.5 PP Runs", 0.538), ("Under 104.5 PP Runs", 0.462)],
                    overround=0.042,
                    unit_label="Run",
                ),
                "winner_pick": "India",
                "pick_market": "winner",
                "pick_selection": "India",
                "confidence": "high",
                "prediction_text": (
                    "Back India to win Saturday's second T20I at Hagley Oval in Christchurch (07:00 UTC) and extend "
                    "their series lead to 2-0 over New Zealand. India chased down an imposing 226 with five balls to "
                    "spare in the series opener behind Sanju Samson's blistering 67 off 33 deliveries, Shreyas Iyer's "
                    "42 off 29, and Naman Dhir's unbeaten 42 from 18. Even with Ishan Kishan ruled out by a right "
                    "adductor strain (replaced by Kumar Kushagra), Samson already holds the gloves and top-order rhythm."
                ),
            },
            {
                "id": "87b3-CR-03",
                "sport": "cricket",
                "sport_name": "Cricket",
                "olbg_sport_id": 7,
                "competition": "ICC Women's Championship — 2nd ODI",
                "event": "India Women vs Zimbabwe Women (2nd ODI)",
                "away": "Zimbabwe Women",
                "home": "India Women",
                "venue": "Kotambi Stadium, Vadodara, India",
                "start_utc": "2026-10-25T08:00:00Z",
                "official_source_name": "ICC Official Women's Championship Squad & Injury Update",
                "official_source_url": "https://www.icc-cricket.com/news/india-pacer-to-miss-women-s-championship-series-against-zimbabwe",
                "secondary_source_url": "https://www.bcci.tv/",
                "olbg_url": "https://www.olbg.com/betting-tips/Cricket/7",
                "form_summary": "Massive ICC Women's Championship gulf on home Indian spin-friendly Vadodara surface",
                "stats_summary": "India Women dominant top-order batting & home spin squeeze vs visiting Zimbabwe unit",
                "injury_summary": "IND-W: pacer Renuka Singh ruled out of entire ODI series injured; left-arm seamer Jintimani Kalita called up.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "India Women",
                    "Zimbabwe Women",
                    mu_margin_a=88.0,
                    sigma_margin=46.0,
                    mu_total=418.0,
                    sigma_total=44.0,
                    spread_a=-84.5,
                    total_line=419.5,
                    deriv_label="Zimbabwe Women Runs Over/Under 164.5",
                    deriv_outcomes=[("Over 164.5 Zimbabwe Women runs", 0.445), ("Under 164.5 Zimbabwe Women runs", 0.555)],
                    overround=0.048,
                    unit_label="Run",
                ),
                "winner_pick": "India Women",
                "pick_market": "derivative",
                "pick_selection": "Under 164.5 Zimbabwe Women runs",
                "confidence": "medium",
                "prediction_text": (
                    "Play Under 164.5 Zimbabwe Women runs—with India Women prohibitive match-winner chalk—in Sunday's "
                    "second ICC Women's Championship ODI at Vadodara. Although strike seamer Renuka Singh misses the "
                    "series through injury with Jintimani Kalita drafted into the pace group, Vadodara's dry October "
                    "surface plays straight into India's relentless finger- and wrist-spin stranglehold through the "
                    "middle overs, where visiting associate and lower-seeded batting units routinely stall well "
                    "short of 165."
                ),
            },
            {
                "id": "87b3-CR-04",
                "sport": "cricket",
                "sport_name": "Cricket",
                "olbg_sport_id": 7,
                "competition": "Pakistan ODI Tri-Series 2026 — 1st ODI",
                "event": "Pakistan vs England (Tri-Series Opener)",
                "away": "England",
                "home": "Pakistan",
                "venue": "Gaddafi Stadium, Lahore, Pakistan",
                "start_utc": "2026-10-25T09:00:00Z",
                "official_source_name": "ICC Official Pakistan White-Ball Squad Announcement & CA Series Hub",
                "official_source_url": "https://www.icc-cricket.com/news/pakistan-name-squads-for-home-white-ball-assignments",
                "secondary_source_url": "https://www.cricket.com.au/matches/series/CA:4716/pakistan-odi-tri-series-2026-men",
                "olbg_url": "https://www.olbg.com/betting-tips/Cricket/7",
                "form_summary": "Tri-Series opener (with Sri Lanka) at high-scoring Gaddafi Stadium; Shaheen Shah Afridi leads Pakistan ODI squad",
                "stats_summary": "Lahore flat white-ball pitches regularly yield 300+ first-innings totals under lights",
                "injury_summary": "Shaheen Afridi named Pakistan ODI captain for home Tri-Series; final playing XIs confirmed at Sunday toss.",
                "unconfirmed_fields": ["playing_xi_at_toss"],
                "markets": price_normal_match(
                    "Pakistan",
                    "England",
                    mu_margin_a=4.5,
                    sigma_margin=33.0,
                    mu_total=578.0,
                    sigma_total=52.0,
                    spread_a=-4.5,
                    total_line=572.5,
                    deriv_label="1st Innings Score Over/Under 289.5",
                    deriv_outcomes=[("Over 289.5 Runs", 0.548), ("Under 289.5 Runs", 0.452)],
                    overround=0.044,
                    unit_label="Run",
                ),
                "winner_pick": "Pakistan",
                "pick_market": "winner",
                "pick_selection": "Pakistan",
                "confidence": "medium",
                "prediction_text": (
                    "Side with Pakistan on the match-winner line when Shaheen Shah Afridi leads the hosts out at "
                    "Gaddafi Stadium in Lahore for Sunday's ODI Tri-Series curtain-raiser against England. Pakistan "
                    "selected a settled home 50-over squad accustomed to Lahore's true batting bounce and evening dew, "
                    "where new-ball swing under lights gives Shaheen a decisive second-innings weapon if defending or "
                    "early breakthroughs up top. Medium confidence applies until Sunday's toss confirms England's "
                    "touring seam combination."
                ),
            },
            {
                "id": "87b3-CR-05",
                "sport": "cricket",
                "sport_name": "Cricket",
                "olbg_sport_id": 7,
                "competition": "ICC World Test Championship — 3rd Test (Series Tied 1-1)",
                "event": "South Africa vs Australia (3rd Test)",
                "away": "Australia",
                "home": "South Africa",
                "venue": "Newlands Cricket Ground, Cape Town (Day 1: 08:30 UTC)",
                "start_utc": "2026-10-27T08:30:00Z",
                "official_source_name": "ICC WTC Schedule & Cricket Australia 2nd Test Day 5 Report",
                "official_source_url": "https://www.icc-cricket.com/news/south-africa-unveil-schedule-for-key-wtc-series",
                "secondary_source_url": "https://www.cricket.com.au/news/4597270/day-five-report-australia-south-africa-second-test-gqeberha-port-elizabeth",
                "olbg_url": "https://www.olbg.com/betting-tips/Cricket/7",
                "form_summary": "Series locked 1-1: Australia won 1st Test in Durban by 214 runs; South Africa won 2nd Test in Gqeberha on Oct 22 by an innings & 31 runs",
                "stats_summary": "Zero draws in first two Tests; result-oriented Newlands seam surface in WTC decider",
                "injury_summary": "Both squads travel from Gqeberha with four full recovery days ahead of Tuesday's Cape Town decider.",
                "unconfirmed_fields": ["playing_xi_at_toss"],
                "markets": price_normal_match(
                    "Australia",
                    "South Africa",
                    mu_margin_a=12.0,
                    sigma_margin=82.0,
                    mu_total=1085.0,
                    sigma_total=145.0,
                    spread_a=-15.5,
                    total_line=1099.5,
                    three_way_draw_band=11.5,
                    deriv_label="Draw No Bet (2-Way)",
                    deriv_outcomes=[("Australia DNB", 0.542), ("South Africa DNB", 0.458)],
                    overround=0.045,
                    unit_label="Run",
                ),
                "winner_pick": "Australia",
                "pick_market": "winner",
                "pick_selection": "Australia",
                "confidence": "high",
                "prediction_text": (
                    "Back Australia on the three-way Test result line at plus-money for Tuesday's World Test "
                    "Championship decider at Newlands in Cape Town. Neither side has blinked toward a stalemate: "
                    "Australia crushed South Africa by 214 runs in Durban's opener before the Proteas hit back on "
                    "Thursday in Gqeberha by an innings and 31 runs to level the series 1-1. Newlands' brisk lateral "
                    "seam movement historically produces rapid results inside four days, rewarding Australia's veteran "
                    "pace trio at an attractive price."
                ),
            },
        ]
    )

    # =========================================================================
    # 10. SNOOKER (OLBG ID 8) — 5 Official WST Ranking Matches (wst.tv)
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-SN-01",
                "sport": "snooker",
                "sport_name": "Snooker",
                "olbg_sport_id": 8,
                "competition": "BetVictor Northern Ireland Open 2026 — Semi-Final 1 (Best of 11)",
                "event": "Kyren Wilson vs Sam Craigie",
                "away": "Sam Craigie",
                "home": "Kyren Wilson",
                "venue": "Waterfront Hall, Belfast, Northern Ireland",
                "start_utc": "2026-10-24T12:00:00Z",
                "official_source_name": "World Snooker Tour Official Match Centre (Match 61)",
                "official_source_url": "https://www.wst.tv/match-centre/e6719e69-c712-476e-8081-8e30790868f5",
                "secondary_source_url": "https://www.wst.tv/matches/",
                "olbg_url": "https://www.olbg.com/betting-tips/Snooker/8",
                "form_summary": "Wilson d. Pang Junxu 4-3 & crushed Anthony McGill 6-1 (139, 103 breaks); Craigie d. Xu Si 4-3, Matthew Selt 4-2 & Elliot Slessor 6-2",
                "stats_summary": "Craigie leads tournament main-stage century count with FIVE tons (129, 110, 108, 103, 100) vs 2026 Masters champion Wilson",
                "injury_summary": "Both semi-finalists completed Friday afternoon quarter-finals cleanly.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Kyren Wilson",
                    "Sam Craigie",
                    p_unit_a=0.595,
                    target_units=6,
                    unit_name="Frame",
                    handicap_line=-2.5,
                    total_line=9.5,
                    prop_label="Match Total Centuries (O/U 1.5)",
                    prop_outcomes=[("Over 1.5 Centuries", 0.585), ("Under 1.5 Centuries", 0.415)],
                    overround=0.044,
                ),
                "winner_pick": "Kyren Wilson",
                "pick_market": "handicap",
                "pick_selection": "Sam Craigie +2.5",
                "confidence": "high",
                "prediction_text": (
                    "Play Sam Craigie +2.5 frames—while respecting 2026 Masters champion Kyren Wilson as overall "
                    "match winner—in Saturday afternoon's best-of-11 Northern Ireland Open semi-final at Waterfront "
                    "Hall. Wilson dismantled Anthony McGill 6-1 with breaks of 139 and 103 after surviving a 4-3 "
                    "decider against Pang Junxu, yet Craigie has been the heaviest scorer in Belfast, firing five "
                    "main-stage centuries (129, 110, 108, 103, 100) across wins over Xiao Guodong, Xu Si, Matthew "
                    "Selt, and Elliot Slessor (6-2) to bank at least four frames."
                ),
            },
            {
                "id": "87b3-SN-02",
                "sport": "snooker",
                "sport_name": "Snooker",
                "olbg_sport_id": 8,
                "competition": "International Championship 2026 — Round 2 (Best of 11)",
                "event": "Jimmy White vs Mark Selby",
                "away": "Mark Selby",
                "home": "Jimmy White",
                "venue": "South New City National Fitness Center, Nanjing, China",
                "start_utc": "2026-10-31T01:30:00Z",
                "official_source_name": "World Snooker Tour Official International Championship Match Centre",
                "official_source_url": "https://www.wst.tv/match-centre/4f29872c-75d7-45c2-9a00-accdd8ff44b4",
                "secondary_source_url": "https://www.wst.tv/players/ba7831b4-ab75-4435-946a-c6f02e4e2d4b",
                "olbg_url": "https://www.olbg.com/betting-tips/Snooker/8",
                "form_summary": "Selby won 2026 Championship League & record 4th China Open (8th career ranking title in China); exited Belfast R1 to Heathcote",
                "stats_summary": "10-time Triple Crown winner Selby over two-session-style Best of 11 in Nanjing vs veteran legend Jimmy White",
                "injury_summary": "Full week rest for Selby ahead of Nanjing curtain-raiser.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Mark Selby",
                    "Jimmy White",
                    p_unit_a=0.735,
                    target_units=6,
                    unit_name="Frame",
                    handicap_line=-3.5,
                    total_line=8.5,
                    prop_label="Mark Selby Century Break in Match",
                    prop_outcomes=[("Selby 1+ Century", 0.610), ("Selby 0 Centuries", 0.390)],
                    overround=0.045,
                ),
                "winner_pick": "Mark Selby",
                "pick_market": "handicap",
                "pick_selection": "Mark Selby -3.5",
                "confidence": "medium",
                "prediction_text": (
                    "Side with Mark Selby -3.5 frames—with Selby heavy match-winner chalk—when the International "
                    "Championship opens in Nanjing over best-of-11 frames against veteran whirlwind Jimmy White. "
                    "Ten-time Triple Crown winner Selby has dominated Chinese baize in 2026, lifting a record fourth "
                    "China Open crown (10-6 over Noppon Saengkham) for his eighth ranking trophy in mainland China. "
                    "Over a race to six frames, Selby's granite safety play typically holds White to two frames or fewer."
                ),
            },
            {
                "id": "87b3-SN-03",
                "sport": "snooker",
                "sport_name": "Snooker",
                "olbg_sport_id": 8,
                "competition": "International Championship 2026 — Round 2 (Best of 11)",
                "event": "Shaun Murphy vs Mitchell Mann",
                "away": "Mitchell Mann",
                "home": "Shaun Murphy",
                "venue": "South New City National Fitness Center, Nanjing, China",
                "start_utc": "2026-10-31T01:30:00Z",
                "official_source_name": "World Snooker Tour Official International Championship Match Centre",
                "official_source_url": "https://www.wst.tv/match-centre/4f29872c-75d7-45c2-9a00-accdd8ff44b4",
                "secondary_source_url": "https://play.wst.tv/",
                "olbg_url": "https://www.olbg.com/betting-tips/Snooker/8",
                "form_summary": "Shaun Murphy reached 2026 World Championship Final at Crucible (lost 17-18 decider to Wu Yize) & German Masters Final",
                "stats_summary": "Best-of-11 format insulates elite long-potter Murphy against short-format variance vs lower-ranked Mann",
                "injury_summary": "Confirmed Round 2 fixture on WST Nanjing schedule.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Shaun Murphy",
                    "Mitchell Mann",
                    p_unit_a=0.655,
                    target_units=6,
                    unit_name="Frame",
                    handicap_line=-2.5,
                    total_line=8.5,
                    prop_label="Total Match Frames Over/Under 8.5",
                    prop_outcomes=[("Over 8.5 Frames", 0.518), ("Under 8.5 Frames", 0.482)],
                    overround=0.045,
                ),
                "winner_pick": "Shaun Murphy",
                "pick_market": "handicap",
                "pick_selection": "Shaun Murphy -2.5",
                "confidence": "high",
                "prediction_text": (
                    "Back Shaun Murphy -2.5 frames—and Murphy outright—against Mitchell Mann in Nanjing's opening "
                    "International Championship session. Murphy has enjoyed a resurgent 2026 campaign highlighted by "
                    "reaching both the German Masters Final and a 35-frame Crucible World Championship Final thriller "
                    "(17-18 against Wu Yize). Stepping back up from Belfast's volatile best-of-seven sprints to a "
                    "race-to-six format gives the Magician's long potting ample runway to win 6-3 or wider."
                ),
            },
            {
                "id": "87b3-SN-04",
                "sport": "snooker",
                "sport_name": "Snooker",
                "olbg_sport_id": 8,
                "competition": "International Championship 2026 — Round 2 (Best of 11)",
                "event": "Zhou Yuelong vs Liam Davies",
                "away": "Liam Davies",
                "home": "Zhou Yuelong",
                "venue": "South New City National Fitness Center, Nanjing, China",
                "start_utc": "2026-10-31T01:30:00Z",
                "official_source_name": "World Snooker Tour Official International Championship Match Centre",
                "official_source_url": "https://www.wst.tv/match-centre/4f29872c-75d7-45c2-9a00-accdd8ff44b4",
                "secondary_source_url": "https://www.wst.tv/matches/",
                "olbg_url": "https://www.olbg.com/betting-tips/Snooker/8",
                "form_summary": "World #17 Zhou Yuelong returns to home Chinese ranking tour vs dangerous Welsh youngster Liam Davies (lost 3-4 to Pang Junxu in Belfast R32)",
                "stats_summary": "Davies pushed top-32 Pang Junxu to a deciding 7th frame in Belfast on Oct 21",
                "injury_summary": "Confirmed Round 2 fixture on WST Nanjing schedule.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Zhou Yuelong",
                    "Liam Davies",
                    p_unit_a=0.558,
                    target_units=6,
                    unit_name="Frame",
                    handicap_line=-1.5,
                    total_line=9.5,
                    prop_label="Deciding 11th Frame Played?",
                    prop_outcomes=[("Yes (6-5 Either Way)", 0.232), ("No (<=10 Frames)", 0.768)],
                    overround=0.044,
                ),
                "winner_pick": "Zhou Yuelong",
                "pick_market": "winner",
                "pick_selection": "Zhou Yuelong",
                "confidence": "high",
                "prediction_text": (
                    "Back world No. 17 Zhou Yuelong on the match-winner line in front of home Chinese supporters in "
                    "Nanjing against rising Welshman Liam Davies. Teenage cueist Davies proved his scoring mettle in "
                    "Belfast this week by taking Pang Junxu to a final-frame decider (3-4), keeping Zhou's price "
                    "honest inside our value band. Over 11 frames in familiar domestic conditions, however, Zhou's "
                    "superior tactical Cue-ball control and heavy break-building earn the nod."
                ),
            },
            {
                "id": "87b3-SN-05",
                "sport": "snooker",
                "sport_name": "Snooker",
                "olbg_sport_id": 8,
                "competition": "International Championship 2026 — Round 2 (Best of 11)",
                "event": "Liu Hongyu vs Louis Heathcote",
                "away": "Louis Heathcote",
                "home": "Liu Hongyu",
                "venue": "South New City National Fitness Center, Nanjing, China",
                "start_utc": "2026-10-31T01:30:00Z",
                "official_source_name": "World Snooker Tour Official International Championship Match Centre",
                "official_source_url": "https://www.wst.tv/match-centre/4f29872c-75d7-45c2-9a00-accdd8ff44b4",
                "secondary_source_url": "https://play.wst.tv/",
                "olbg_url": "https://www.olbg.com/betting-tips/Snooker/8",
                "form_summary": "Heathcote stunned Mark Selby in Belfast Round 1 on Oct 18; Liu Hongyu dangerous home break-builder in Nanjing",
                "stats_summary": "Evenly matched mid-ranking best-of-11 clash; high probability of 9+ frames",
                "injury_summary": "Confirmed Round 2 fixture on WST Nanjing schedule.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Liu Hongyu",
                    "Louis Heathcote",
                    p_unit_a=0.538,
                    target_units=6,
                    unit_name="Frame",
                    handicap_line=-1.5,
                    total_line=9.5,
                    prop_label="Both Players Win 4+ Frames?",
                    prop_outcomes=[("Yes (Score >= 6-4)", 0.562), ("No (6-0 to 6-3)", 0.438)],
                    overround=0.045,
                ),
                "winner_pick": "Liu Hongyu",
                "pick_market": "winner",
                "pick_selection": "Liu Hongyu",
                "confidence": "medium",
                "prediction_text": (
                    "Lean Liu Hongyu on the match-winner line at medium confidence against Englishman Louis Heathcote "
                    "in Nanjing's Saturday morning session. Heathcote arrives buoyed by knocking out Mark Selby in the "
                    "opening round of the Northern Ireland Open on October 18, yet long-haul travel to eastern China "
                    "and a longer best-of-11 distance favour 22-year-old former English Open semi-finalist Liu, whose "
                    "fluent scoring among the balls thrives in unhurried Chinese arena conditions."
                ),
            },
        ]
    )

    # =========================================================================
    # 11. DARTS (OLBG ID 15) — 5 PDC European Championship Round 2 Ties (pdc.tv)
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-DT-01",
                "sport": "darts",
                "sport_name": "Darts",
                "olbg_sport_id": 15,
                "competition": "2026 Machineseeker European Championship — Round 2 (Best of 19)",
                "event": "Gian van Veen vs Luke Woodhouse",
                "away": "Luke Woodhouse",
                "home": "Gian van Veen",
                "venue": "Westfalenhalle, Dortmund, Germany",
                "start_utc": "2026-10-24T11:45:00Z",
                "official_source_name": "PDC Official European Championship Schedule & Day 1 Report",
                "official_source_url": "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/",
                "secondary_source_url": "https://www.pdc.tv/",
                "olbg_url": "https://www.olbg.com/betting-tips/Darts/15",
                "form_summary": "Defending champion & #1 seed Van Veen d. Krzysztof Kciuk 6-4 in R1; Woodhouse hit a 9-DARTER & 108.64 average beating Daryl Gurney 6-2!",
                "stats_summary": "Step up from Best of 11 (R1) to Best of 19 legs (race to 10); elite treble-20 scoring battle",
                "injury_summary": "Both players through Thursday evening's opening round cleanly.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Gian van Veen",
                    "Luke Woodhouse",
                    p_unit_a=0.538,
                    target_units=10,
                    unit_name="Leg",
                    handicap_line=-1.5,
                    total_line=16.5,
                    prop_label="Match Total 180s (O/U 10.5)",
                    prop_outcomes=[("Over 10.5 180s", 0.568), ("Under 10.5 180s", 0.432)],
                    overround=0.045,
                ),
                "winner_pick": "Gian van Veen",
                "pick_market": "winner",
                "pick_selection": "Gian van Veen",
                "confidence": "high",
                "prediction_text": (
                    "Back defending European Champion and top seed Gian van Veen to defeat Luke Woodhouse in Saturday "
                    "afternoon's best-of-19 second-round showdown at Dortmund's Westfalenhalle. Woodhouse lit up "
                    "Thursday night with a sensational nine-darter and a 108.64 average in routing Daryl Gurney 6-2, "
                    "keeping Van Veen's price remarkably attractive after the young Dutchman edged Krzysztof Kciuk "
                    "6-4. Across a longer 19-leg distance, Van Veen's sustained Euro Tour scoring power regains command."
                ),
            },
            {
                "id": "87b3-DT-02",
                "sport": "darts",
                "sport_name": "Darts",
                "olbg_sport_id": 15,
                "competition": "2026 Machineseeker European Championship — Round 2 (Best of 19)",
                "event": "Cameron Menzies vs Gerwyn Price",
                "away": "Gerwyn Price",
                "home": "Cameron Menzies",
                "venue": "Westfalenhalle, Dortmund, Germany",
                "start_utc": "2026-10-24T12:30:00Z",
                "official_source_name": "PDC Official European Championship Schedule",
                "official_source_url": "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/",
                "secondary_source_url": "https://www.pdc.tv/",
                "olbg_url": "https://www.olbg.com/betting-tips/Darts/15",
                "form_summary": "Gerwyn Price survived epic 6-5 R1 thriller vs James Wade; Cameron Menzies upset Danny Noppert 6-2",
                "stats_summary": "Best-of-19 format rewards former World Champion Price's stage composure vs streaky Menzies",
                "injury_summary": "Both players rested Friday after winning Thursday's Round 1 ties.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Gerwyn Price",
                    "Cameron Menzies",
                    p_unit_a=0.542,
                    target_units=10,
                    unit_name="Leg",
                    handicap_line=-1.5,
                    total_line=16.5,
                    prop_label="Highest Match Checkout O/U 124.5",
                    prop_outcomes=[("Over 124.5 Checkout", 0.525), ("Under 124.5 Checkout", 0.475)],
                    overround=0.045,
                ),
                "winner_pick": "Gerwyn Price",
                "pick_market": "winner",
                "pick_selection": "Gerwyn Price",
                "confidence": "high",
                "prediction_text": (
                    "Play Gerwyn Price on the match-winner line in Saturday afternoon's race-to-10-legs clash with "
                    "Scotsman Cameron Menzies in Dortmund. Price showed steel under pressure on Thursday night to "
                    "pip veteran James Wade 6-5 in a deciding leg, while Menzies punished an off-colour Danny Noppert "
                    "6-2. Menzies carries explosive 180 bursts, yet double-top streaks often wobble across two TV "
                    "commercial breaks—territory where Price's major-stage pedigree consistently prevails."
                ),
            },
            {
                "id": "87b3-DT-03",
                "sport": "darts",
                "sport_name": "Darts",
                "olbg_sport_id": 15,
                "competition": "2026 Machineseeker European Championship — Round 2 (Best of 19)",
                "event": "Jonny Clayton vs Josh Rock",
                "away": "Josh Rock",
                "home": "Jonny Clayton",
                "venue": "Westfalenhalle, Dortmund, Germany",
                "start_utc": "2026-10-24T17:45:00Z",
                "official_source_name": "PDC Official European Championship Schedule",
                "official_source_url": "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/",
                "secondary_source_url": "https://www.pdc.tv/",
                "olbg_url": "https://www.olbg.com/betting-tips/Darts/15",
                "form_summary": "Josh Rock crushed Chris Dobey 6-1 on Friday night; Jonny Clayton defeated German home hope Niko Springer 6-3",
                "stats_summary": "Rock delivered Friday's most lopsided R1 victory (6-1 vs Dobey); best-of-19 evening showcase",
                "injury_summary": "Both players advanced smoothly through Friday's second Round 1 session.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Josh Rock",
                    "Jonny Clayton",
                    p_unit_a=0.540,
                    target_units=10,
                    unit_name="Leg",
                    handicap_line=-1.5,
                    total_line=16.5,
                    prop_label="Match Total 180s (O/U 11.5)",
                    prop_outcomes=[("Over 11.5 180s", 0.552), ("Under 11.5 180s", 0.448)],
                    overround=0.045,
                ),
                "winner_pick": "Josh Rock",
                "pick_market": "winner",
                "pick_selection": "Josh Rock",
                "confidence": "high",
                "prediction_text": (
                    "Back Northern Ireland star Josh Rock to beat Welshman Jonny Clayton in Saturday evening's "
                    "European Championship second round. Rock produced the most ruthless display of Friday's session "
                    "at Westfalenhalle, dismantling Premier League contender Chris Dobey 6-1 with clinical outer-ring "
                    "finishing. Clayton quieted the German crowd by seeing off Niko Springer 6-3, yet Rock's superior "
                    "first-nine-dart scoring weight creates far too many break-of-throw darts across 19 legs."
                ),
            },
            {
                "id": "87b3-DT-04",
                "sport": "darts",
                "sport_name": "Darts",
                "olbg_sport_id": 15,
                "competition": "2026 Machineseeker European Championship — Round 2 (Best of 19)",
                "event": "Krzysztof Ratajski vs Kevin Doets",
                "away": "Kevin Doets",
                "home": "Krzysztof Ratajski",
                "venue": "Westfalenhalle, Dortmund, Germany",
                "start_utc": "2026-10-24T18:30:00Z",
                "official_source_name": "PDC Official European Championship Schedule",
                "official_source_url": "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/",
                "secondary_source_url": "https://www.pdc.tv/",
                "olbg_url": "https://www.olbg.com/betting-tips/Darts/15",
                "form_summary": "Kevin Doets shocked Michael van Gerwen 6-3 in Friday R1; Krzysztof Ratajski swept aside Dave Chisnall 6-2",
                "stats_summary": "Wide-open quarter after MvG elimination; two methodical rhythm players over 19 legs",
                "injury_summary": "No fitness issues; both posted dominant Friday victories.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Krzysztof Ratajski",
                    "Kevin Doets",
                    p_unit_a=0.522,
                    target_units=10,
                    unit_name="Leg",
                    handicap_line=-1.5,
                    total_line=16.5,
                    prop_label="Both Players Reach 8+ Legs?",
                    prop_outcomes=[("Yes (Score >= 10-8)", 0.445), ("No (10-7 or wider)", 0.555)],
                    overround=0.045,
                ),
                "winner_pick": "Krzysztof Ratajski",
                "pick_market": "total",
                "pick_selection": "Over 16.5",
                "confidence": "medium",
                "prediction_text": (
                    "Side with Over 16.5 total legs—while edging Krzysztof Ratajski as a narrow match-winner lean—when "
                    "the Polish Eagle meets Dutch giant-killer Kevin Doets on Saturday night. Doets blew this section "
                    "of the Dortmund draw wide open on Friday by dumping out four-time champion Michael van Gerwen 6-3, "
                    "shortly after Ratajski clinically dispatched Dave Chisnall 6-2. With two steady mid-90s floor "
                    "technicians holding throw reliably, a 10-7 or closer battle is firmly in play."
                ),
            },
            {
                "id": "87b3-DT-05",
                "sport": "darts",
                "sport_name": "Darts",
                "olbg_sport_id": 15,
                "competition": "2026 Machineseeker European Championship — Round 2 (Best of 19)",
                "event": "Nathan Aspinall vs Luke Littler",
                "away": "Luke Littler",
                "home": "Nathan Aspinall",
                "venue": "Westfalenhalle, Dortmund, Germany",
                "start_utc": "2026-10-24T19:15:00Z",
                "official_source_name": "PDC Official European Championship Schedule",
                "official_source_url": "https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/",
                "secondary_source_url": "https://www.pdc.tv/",
                "olbg_url": "https://www.olbg.com/betting-tips/Darts/15",
                "form_summary": "Littler d. William O'Connor 6-3 on Friday; Aspinall d. Cristo Reyes 6-3; tournament wide open with Humphries (illness) & MvG out",
                "stats_summary": "Blockbuster Saturday night headline clash; Littler prolific 180 hitter over race-to-10 format",
                "injury_summary": "World #1 Luke Humphries withdrew pre-tournament (gastroenteritis); both Littler & Aspinall healthy.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Luke Littler",
                    "Nathan Aspinall",
                    p_unit_a=0.618,
                    target_units=10,
                    unit_name="Leg",
                    handicap_line=-2.5,
                    total_line=16.5,
                    prop_label="Luke Littler 7+ 180s in Match",
                    prop_outcomes=[("Littler 7+ 180s Yes", 0.545), ("Littler <=6 180s", 0.455)],
                    overround=0.044,
                ),
                "winner_pick": "Luke Littler",
                "pick_market": "handicap",
                "pick_selection": "Luke Littler -2.5",
                "confidence": "medium",
                "prediction_text": (
                    "Play Luke Littler -2.5 legs—alongside Littler as Saturday night's headline winner—against "
                    "familiar Premier League sparring partner Nathan Aspinall. With Luke Humphries sidelined before "
                    "Round 1 by gastroenteritis and Michael van Gerwen knocked out Friday, Dortmund's trophy path has "
                    "parted for Littler after his crisp 6-3 victory over William O'Connor. Aspinall beat Cristo Reyes "
                    "6-3, yet Littler's relentless treble-20 barrages routinely open three-leg cushions over best-of-19."
                ),
            },
        ]
    )

    # =========================================================================
    # 12. VOLLEYBALL (OLBG ID 21) — 5 Italian SuperLega Giornata 2 Matches (legavolley.it)
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-VB-01",
                "sport": "volleyball",
                "sport_name": "Volleyball",
                "olbg_sport_id": 21,
                "competition": "Italy Men's SuperLega Credem Banca — Giornata 2",
                "event": "Itas Trentino vs Cisterna Volley",
                "away": "Cisterna Volley",
                "home": "Itas Trentino",
                "venue": "BTS Arena, Trento (17:00 CET / 16:00 UTC)",
                "start_utc": "2026-10-25T16:00:00Z",
                "official_source_name": "Lega Pallavolo Serie A Official Calendar & Standings",
                "official_source_url": "https://www.legavolley.it/calendario/?idCampionato=999",
                "secondary_source_url": "https://www.legavolley.it/classifica/?IdCampionato=999",
                "olbg_url": "https://www.olbg.com/betting-tips/Volleyball/21",
                "form_summary": "Clash of 3-0 Round 1 winners: 3rd Trentino (3 pts, 3-0 sets, 75-61 pts vs Modena) vs 1st Cisterna (3 pts, 3-0 sets, 79-56 pts vs Milano)",
                "stats_summary": "Cisterna posted league-best 1.41 point quotient in R1; Trentino posted 1.23 point quotient behind Riccardo Sbertoli",
                "injury_summary": "Official referees appointed (Goitre Mauro Carlo, Serafin Denis); full squads active.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Itas Trentino",
                    "Cisterna Volley",
                    p_unit_a=0.685,
                    target_units=3,
                    unit_name="Set",
                    handicap_line=-1.5,
                    total_line=3.5,
                    prop_label="Match Total Points (O/U 176.5)",
                    prop_outcomes=[("Over 176.5 Points", 0.535), ("Under 176.5 Points", 0.465)],
                    overround=0.045,
                ),
                "winner_pick": "Itas Trentino",
                "pick_market": "total",
                "pick_selection": "Over 3.5",
                "confidence": "medium",
                "prediction_text": (
                    "Play Over 3.5 sets—while keeping Itas Trentino as home match winners—when Round 1 table-toppers "
                    "Cisterna Volley visit Trento on Sunday afternoon (16:00 UTC after Italy's CET clock change). "
                    "Trentino swept Modena 3-0 (75-61 points, 1.23 quotient) on opening weekend, yet Cisterna looked "
                    "even sharper in dismantling Allianz Milano 3-0 (79-56 points, league-best 1.41 quotient), giving "
                    "the visitors more than enough side-out firepower to steal at least a set."
                ),
            },
            {
                "id": "87b3-VB-02",
                "sport": "volleyball",
                "sport_name": "Volleyball",
                "olbg_sport_id": 21,
                "competition": "Italy Men's SuperLega Credem Banca — Giornata 2",
                "event": "Sir Susa Scai Perugia vs Tinet Prata di Pordenone",
                "away": "Tinet Prata di Pordenone",
                "home": "Sir Susa Scai Perugia",
                "venue": "Pala Barton Energy, Perugia (18:00 CET / 17:00 UTC)",
                "start_utc": "2026-10-25T17:00:00Z",
                "official_source_name": "Lega Pallavolo Serie A Official Calendar & Match Preview",
                "official_source_url": "https://www.legavolley.it/calendario/?idCampionato=999",
                "secondary_source_url": "https://www.legavolley.it/2026/il-palazzetto-di-perugia-e-pronto-a-riaccendere-i-riflettori/",
                "olbg_url": "https://www.olbg.com/betting-tips/Volleyball/21",
                "form_summary": "Perugia (6th, 2 pts, won 3-2 at Cuneo 114-95 pts; reigning Scudetto & CEV Champions League winners) vs newly promoted Prata (5th, 3 pts, beat Monza 3-1 94-91 pts)",
                "stats_summary": "Perugia feature Simone Giannelli, Massimo Colaci (30.77% perfect reception) & Giovanni Sanguinetti (74.27% middle attack)",
                "injury_summary": "Official referees appointed (Piana Rossella, Scotti Paolo); home trophy banner celebration night in Perugia.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Sir Susa Scai Perugia",
                    "Tinet Prata di Pordenone",
                    p_unit_a=0.775,
                    target_units=3,
                    unit_name="Set",
                    handicap_line=-2.5,
                    total_line=3.5,
                    prop_label="Sir Susa Scai Perugia 3-0 Exact Sweep",
                    prop_outcomes=[("Perugia 3-0 Yes", 0.465), ("Prata Wins 1+ Set", 0.535)],
                    overround=0.046,
                ),
                "winner_pick": "Sir Susa Scai Perugia",
                "pick_market": "total",
                "pick_selection": "Under 3.5",
                "confidence": "medium",
                "prediction_text": (
                    "Side with Under 3.5 total sets (a straight-sets sweep, with reigning Italian and European "
                    "champions Sir Susa Scai Perugia heavy match-winner chalk) in Sunday's Pala Barton Energy home "
                    "opener against newly promoted Tinet Prata di Pordenone. Prata earned full credit for shocking "
                    "Monza 3-1 (94-91) on debut while Perugia needed five sets at Cuneo (114-95), yet Angelo "
                    "Lorenzetti's Block Devils—led by Simone Giannelli, Massimo Colaci (30.77% perfect reception), and "
                    "Giovanni Sanguinetti—rarely drop sets in Umbria."
                ),
            },
            {
                "id": "87b3-VB-03",
                "sport": "volleyball",
                "sport_name": "Volleyball",
                "olbg_sport_id": 21,
                "competition": "Italy Men's SuperLega Credem Banca — Giornata 2 (Via Emilia Derby)",
                "event": "Gas Sales Bluenergy Piacenza vs Valsa Group Modena",
                "away": "Valsa Group Modena",
                "home": "Gas Sales Bluenergy Piacenza",
                "venue": "PalaBancaSport, Piacenza (18:00 CET / 17:00 UTC)",
                "start_utc": "2026-10-25T17:00:00Z",
                "official_source_name": "Lega Pallavolo Serie A Official Calendar & Standings",
                "official_source_url": "https://www.legavolley.it/calendario/?idCampionato=999",
                "secondary_source_url": "https://www.legavolley.it/classifica/?IdCampionato=999",
                "olbg_url": "https://www.olbg.com/betting-tips/Volleyball/21",
                "form_summary": "Piacenza 2nd (1-0, 3 pts, swept Padova 3-0, 75-56 pts, 1.34 quotient); Modena 10th (0-1, 0 pts, lost 0-3 to Trentino, 61-75 pts)",
                "stats_summary": "Setter Paolo Porro steers Piacenza offense; fierce Via Emilia rivalry after finishing 1 pt apart (44 vs 43) last regular season",
                "injury_summary": "Referees Vagni Ilaria & Giardini Massimiliano assigned; live on Rai Sport.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Gas Sales Bluenergy Piacenza",
                    "Valsa Group Modena",
                    p_unit_a=0.585,
                    target_units=3,
                    unit_name="Set",
                    handicap_line=-1.5,
                    total_line=3.5,
                    prop_label="Match Total Points (O/U 181.5)",
                    prop_outcomes=[("Over 181.5 Points", 0.558), ("Under 181.5 Points", 0.442)],
                    overround=0.044,
                ),
                "winner_pick": "Gas Sales Bluenergy Piacenza",
                "pick_market": "winner",
                "pick_selection": "Gas Sales Bluenergy Piacenza",
                "confidence": "high",
                "prediction_text": (
                    "Back Gas Sales Bluenergy Piacenza on the match-winner line in Sunday's Via Emilia derby against "
                    "Valsa Group Modena at PalaBancaSport (17:00 UTC). Piacenza opened 2026-27 in ruthless rhythm "
                    "behind Italian international setter Paolo Porro, sweeping Padova 3-0 while conceding just 56 "
                    "points (1.34 quotient). Modena were blanked 0-3 (61-75) by Trentino in Round 1, and although "
                    "these rivals finished separated by one point last season, Piacenza's serve-receive sharpness "
                    "gives the hosts clear authority."
                ),
            },
            {
                "id": "87b3-VB-04",
                "sport": "volleyball",
                "sport_name": "Volleyball",
                "olbg_sport_id": 21,
                "competition": "Italy Men's SuperLega Credem Banca — Giornata 2",
                "event": "Cucine Lube Civitanova vs Pallavolo Padova",
                "away": "Pallavolo Padova",
                "home": "Cucine Lube Civitanova",
                "venue": "Eurosuole Forum, Civitanova Marche (18:00 CET / 17:00 UTC)",
                "start_utc": "2026-10-25T17:00:00Z",
                "official_source_name": "Lega Pallavolo Serie A Official Calendar & Standings",
                "official_source_url": "https://www.legavolley.it/calendario/?idCampionato=999",
                "secondary_source_url": "https://www.legavolley.it/classifica/?IdCampionato=999",
                "olbg_url": "https://www.olbg.com/betting-tips/Volleyball/21",
                "form_summary": "Civitanova 4th (1-0, 3 pts, swept title contenders Verona 3-0, 78-65 pts); Padova 11th (0-1, 0 pts, lost 0-3 at Piacenza, 56-75 pts)",
                "stats_summary": "2026 Scudetto finalists Lube (setter Mattia Boninfante) posted 1.20 point quotient in statement opener vs Verona",
                "injury_summary": "Referees Simbari Armando & Giglio Anthony assigned for Eurosuole Forum clash.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Cucine Lube Civitanova",
                    "Pallavolo Padova",
                    p_unit_a=0.735,
                    target_units=3,
                    unit_name="Set",
                    handicap_line=-1.5,
                    total_line=3.5,
                    prop_label="Cucine Lube Civitanova -2.5 Sets (3-0 Sweep)",
                    prop_outcomes=[("Civitanova -2.5 Sets", 0.398), ("Padova +2.5 Sets", 0.602)],
                    overround=0.045,
                ),
                "winner_pick": "Cucine Lube Civitanova",
                "pick_market": "handicap",
                "pick_selection": "Cucine Lube Civitanova -1.5",
                "confidence": "medium",
                "prediction_text": (
                    "Take Cucine Lube Civitanova -1.5 sets—with Lube clear match-winner chalk—at Eurosuole Forum on "
                    "Sunday against 11th-placed Pallavolo Padova. Giampaolo Medei's 2026 Scudetto finalists made the "
                    "loudest statement of Round 1 by sweeping last year's regular-season runners-up Rana Verona 3-0 "
                    "(78-65 points) behind young Italy setter Mattia Boninfante. Padova managed only 56 total points "
                    "in an 0-3 loss at Piacenza and lack the terminal pin hitting to push Lube to a tiebreak."
                ),
            },
            {
                "id": "87b3-VB-05",
                "sport": "volleyball",
                "sport_name": "Volleyball",
                "olbg_sport_id": 21,
                "competition": "Italy Men's SuperLega Credem Banca — Giornata 2",
                "event": "Vero Volley Monza vs Rana Verona",
                "away": "Rana Verona",
                "home": "Vero Volley Monza",
                "venue": "OpiquadArena, Monza (18:00 CET / 17:00 UTC)",
                "start_utc": "2026-10-25T17:00:00Z",
                "official_source_name": "Lega Pallavolo Serie A Official Calendar & Standings",
                "official_source_url": "https://www.legavolley.it/calendario/?idCampionato=999",
                "secondary_source_url": "https://www.legavolley.it/classifica/?IdCampionato=999",
                "olbg_url": "https://www.olbg.com/betting-tips/Volleyball/21",
                "form_summary": "Verona 9th (0-1, lost 0-3 at Civitanova 65-78; finished 2nd on 48 pts in 2025-26); Monza 8th (0-1, stunned 1-3 by newly promoted Prata 91-94)",
                "stats_summary": "Verona outpaced Monza by 23 points (48 vs 25) across 2025-26 regular season",
                "injury_summary": "Referees Brunelli Michele & Luciani Ubaldo assigned; live DAZN/VBTV.",
                "unconfirmed_fields": [],
                "markets": price_race_match(
                    "Rana Verona",
                    "Vero Volley Monza",
                    p_unit_a=0.578,
                    target_units=3,
                    unit_name="Set",
                    handicap_line=-1.5,
                    total_line=3.5,
                    prop_label="Match Goes to 5th Set?",
                    prop_outcomes=[("Yes (5 Sets)", 0.275), ("No (3 or 4 Sets)", 0.725)],
                    overround=0.044,
                ),
                "winner_pick": "Rana Verona",
                "pick_market": "winner",
                "pick_selection": "Rana Verona",
                "confidence": "high",
                "prediction_text": (
                    "Back Rana Verona on the road match-winner line at OpiquadArena against Vero Volley Monza on "
                    "Sunday evening (17:00 UTC). Both sides seek their first points of 2026-27, yet context separates "
                    "their opening setbacks: Verona ran into red-hot Civitanova away (65-78) after finishing second "
                    "overall on 48 points last campaign, whereas Monza (25 points last year) dropped a 1-3 upset to "
                    "newly promoted Prata (91-94). Verona's physical serving ceiling makes them strong road favourites."
                ),
            },
        ]
    )

    # =========================================================================
    # 13. HANDBALL (OLBG ID 20) — 5 LNH StarLigue & DAIKIN HBL Fixtures
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-HB-01",
                "sport": "handball",
                "sport_name": "Handball",
                "olbg_sport_id": 20,
                "competition": "France Liqui Moly StarLigue — Journée 8",
                "event": "HBC Nantes vs Chambéry Savoie Mont Blanc",
                "away": "Chambéry Savoie Mont Blanc",
                "home": "HBC Nantes",
                "venue": "H Arena, Nantes (19:00 CEST / 17:00 UTC)",
                "start_utc": "2026-10-24T17:00:00Z",
                "official_source_name": "LNH Official StarLigue Calendar & Standings",
                "official_source_url": "https://www.lnh.fr/daikin-starligue/calendrier",
                "secondary_source_url": "https://www.lnh.fr/daikin-starligue/classement",
                "olbg_url": "https://www.olbg.com/betting-tips/Handball/20",
                "form_summary": "Nantes 2nd (6-0-1, 12 pts, +41 GD, 4-game winning streak); Chambéry 12th (2-2-3, 6 pts, -7 GD)",
                "stats_summary": "Nantes average 34.86 GF / 29.00 GA (244:203 in 7 GP); Chambéry 32.00 GF / 33.00 GA (224:231)",
                "injury_summary": "Official J8 Saturday evening showcase on LNH calendar (CEST UTC+2 before Sunday clock fallback).",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "HBC Nantes",
                    "Chambéry Savoie Mont Blanc",
                    mu_margin_a=5.8,
                    sigma_margin=4.9,
                    mu_total=64.2,
                    sigma_total=5.4,
                    spread_a=-5.5,
                    total_line=63.5,
                    three_way_draw_band=0.5,
                    unit_label="Goal",
                ),
                "winner_pick": "HBC Nantes",
                "pick_market": "handicap",
                "pick_selection": "HBC Nantes -5.5",
                "confidence": "high",
                "prediction_text": (
                    "Play HBC Nantes -5.5 goals—with Nantes clear home winners—in Saturday's Liqui Moly StarLigue "
                    "Journée 8 clash at H Arena (17:00 UTC). Second-placed Nantes (6-0-1, 12 points) enter on a four-"
                    "game winning tear while averaging 34.9 goals scored against just 29.0 conceded (244:203, +41 "
                    "differential). Twelfth-placed Chambéry (2-2-3, 6 points, 224:231) leak 33.0 goals per game, "
                    "leaving them vulnerable to Nantes' relentless second-wave fast breaks."
                ),
            },
            {
                "id": "87b3-HB-02",
                "sport": "handball",
                "sport_name": "Handball",
                "olbg_sport_id": 20,
                "competition": "Germany DAIKIN Handball-Bundesliga — 10. Spieltag",
                "event": "HBW Balingen-Weilstetten vs MT Melsungen",
                "away": "MT Melsungen",
                "home": "HBW Balingen-Weilstetten",
                "venue": "Sparkassen-Arena, Balingen (20:00 CEST / 18:00 UTC)",
                "start_utc": "2026-10-24T18:00:00Z",
                "official_source_name": "HBW Balingen-Weilstetten Official Bundesliga Spielplan",
                "official_source_url": "https://www.h-bw.de/team-bundesliga/spielplan/",
                "secondary_source_url": "https://www.rhein-neckar-loewen.de/spiele/spielplan/alle-spiele",
                "olbg_url": "https://www.olbg.com/betting-tips/Handball/20",
                "form_summary": "Melsungen 5th (5-1-3, 11:7 pts, 283:254, +29 GD); promoted Balingen 14th (2-1-4, 5:9 pts, 208:200, lost home nailbiters 28:29 vs Stuttgart & Bergischer)",
                "stats_summary": "Melsungen boast HBL's stingiest defense (28.22 GA/GP); Balingen average 29.71 GF / 28.57 GA",
                "injury_summary": "Official Saturday 20:00 CEST throw-off confirmed on HBW Balingen club fixture schedule.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "MT Melsungen",
                    "HBW Balingen-Weilstetten",
                    mu_margin_a=2.5,
                    sigma_margin=4.7,
                    mu_total=57.2,
                    sigma_total=5.1,
                    spread_a=-2.5,
                    total_line=58.5,
                    three_way_draw_band=0.5,
                    unit_label="Goal",
                ),
                "winner_pick": "MT Melsungen",
                "pick_market": "winner",
                "pick_selection": "MT Melsungen",
                "confidence": "high",
                "prediction_text": (
                    "Back fifth-placed MT Melsungen on the three-way match-winner line at promoted HBW Balingen-"
                    "Weilstetten on Saturday night (18:00 UTC). Melsungen (5-1-3, 11:7 points) own the stingiest "
                    "6-0 defensive wall in Germany's Bundesliga, surrendering just 28.2 goals per game (283:254, "
                    "+29 differential). Fourteenth-placed Balingen (2-1-4, 5:9 points) have twice agonizingly "
                    "dropped 28:29 home heartbreakers to Stuttgart and Bergischer HC, and Melsungen's late-game "
                    "experience closes tight contests cleanly."
                ),
            },
            {
                "id": "87b3-HB-03",
                "sport": "handball",
                "sport_name": "Handball",
                "olbg_sport_id": 20,
                "competition": "Germany DAIKIN Handball-Bundesliga — 10. Spieltag",
                "event": "Rhein-Neckar Löwen vs SC Magdeburg",
                "away": "SC Magdeburg",
                "home": "Rhein-Neckar Löwen",
                "venue": "SAP Arena, Mannheim (15:00 CET / 14:00 UTC)",
                "start_utc": "2026-10-25T14:00:00Z",
                "official_source_name": "Rhein-Neckar Löwen Official Bundesliga Spielplan",
                "official_source_url": "https://www.rhein-neckar-loewen.de/spiele/spielplan/alle-spiele",
                "secondary_source_url": "https://www.rhein-neckar-loewen.de/heimspiele-in-2026-vorverkauf-gestartet-968737",
                "olbg_url": "https://www.olbg.com/betting-tips/Handball/20",
                "form_summary": "Magdeburg 3rd (8-0-1, 16:2 pts, 301:266, +35 GD); Rhein-Neckar Löwen 12th (3-1-5, 7:11 pts, 266:273, lost 36:37 thriller at THW Kiel on Oct 15)",
                "stats_summary": "Magdeburg score 33.44 GF/GP; Löwen just pushed 2nd-placed Kiel to a 73-goal shootout (36:37)",
                "injury_summary": "Sunday 15:00 CET throw-off (14:00 UTC following Central European clock fallback).",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "SC Magdeburg",
                    "Rhein-Neckar Löwen",
                    mu_margin_a=3.6,
                    sigma_margin=4.8,
                    mu_total=62.4,
                    sigma_total=5.3,
                    spread_a=-3.5,
                    total_line=60.5,
                    three_way_draw_band=0.5,
                    unit_label="Goal",
                ),
                "winner_pick": "SC Magdeburg",
                "pick_market": "total",
                "pick_selection": "Over 60.5",
                "confidence": "high",
                "prediction_text": (
                    "Play Over 60.5 total goals—with third-placed SC Magdeburg (8-0-1, 16:2 points) favoured to win "
                    "at SAP Arena—in Sunday's Bundesliga marquee clash against Rhein-Neckar Löwen (14:00 UTC). "
                    "Magdeburg pour in 33.4 goals per outing (301:266 across nine games), while Mannheim's 12th-placed "
                    "hosts (3-1-5, 266:273) showed explosive attacking pace in a 37:36 road shootout loss at THW Kiel "
                    "on October 15, setting up sixty minutes of rapid centre-throw transitions."
                ),
            },
            {
                "id": "87b3-HB-04",
                "sport": "handball",
                "sport_name": "Handball",
                "olbg_sport_id": 20,
                "competition": "France Liqui Moly StarLigue — Journée 8",
                "event": "Saint-Raphaël Var Handball vs Paris Saint-Germain Handball",
                "away": "Paris Saint-Germain Handball",
                "home": "Saint-Raphaël Var Handball",
                "venue": "Palais des Sports J.-F. Krakowski, Saint-Raphaël (16:00 CET / 15:00 UTC)",
                "start_utc": "2026-10-25T15:00:00Z",
                "official_source_name": "LNH Official StarLigue Calendar & Standings",
                "official_source_url": "https://www.lnh.fr/daikin-starligue/calendrier",
                "secondary_source_url": "https://www.lnh.fr/daikin-starligue/classement",
                "olbg_url": "https://www.olbg.com/betting-tips/Handball/20",
                "form_summary": "PSG 1st (perfect 7-0-0, 14 pts, 249:199, +50 GD); Saint-Raphaël 14th (2-0-5, 4 pts, 207:223, -16 GD, L3 skid)",
                "stats_summary": "PSG average league-leading 35.57 GF / 28.43 GA (+7.14 margin); Saint-Raphaël score 29.57 GF/GP",
                "injury_summary": "Sunday 16:00 CET throw-off (15:00 UTC after French winter time change).",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Paris Saint-Germain Handball",
                    "Saint-Raphaël Var Handball",
                    mu_margin_a=6.6,
                    sigma_margin=5.0,
                    mu_total=63.8,
                    sigma_total=5.4,
                    spread_a=-6.5,
                    total_line=63.5,
                    three_way_draw_band=0.5,
                    unit_label="Goal",
                ),
                "winner_pick": "Paris Saint-Germain Handball",
                "pick_market": "handicap",
                "pick_selection": "Paris Saint-Germain Handball -6.5",
                "confidence": "medium",
                "prediction_text": (
                    "Side with Paris Saint-Germain Handball -6.5 goals—with unbeaten PSG heavy match-winner chalk—at "
                    "14th-placed Saint-Raphaël on Sunday afternoon (15:00 UTC). PSG sit 7-0-0 atop France's StarLigue "
                    "on 14 points with a +50 goal differential (249:199, winning by 7.1 goals per match), whereas "
                    "Saint-Raphaël (2-0-5, 4 points, 207:223) have dropped three straight fixtures and struggle to "
                    "score thirty against elite six-on-six defenses."
                ),
            },
            {
                "id": "87b3-HB-05",
                "sport": "handball",
                "sport_name": "Handball",
                "olbg_sport_id": 20,
                "competition": "France Liqui Moly StarLigue — Journée 8",
                "event": "Montpellier Handball vs USM Saran Loiret Handball",
                "away": "USM Saran Loiret Handball",
                "home": "Montpellier Handball",
                "venue": "FDI Stadium, Montpellier (17:00 CET / 16:00 UTC)",
                "start_utc": "2026-10-25T16:00:00Z",
                "official_source_name": "LNH Official StarLigue Calendar & Standings",
                "official_source_url": "https://www.lnh.fr/daikin-starligue/calendrier",
                "secondary_source_url": "https://www.lnh.fr/daikin-starligue/classement",
                "olbg_url": "https://www.olbg.com/betting-tips/Handball/20",
                "form_summary": "Montpellier 3rd (5-0-2, 10 pts, 232:197, +35 GD); Saran 10th (3-0-4, 6 pts, 211:227, -16 GD)",
                "stats_summary": "Montpellier concede league-best 28.14 GA/GP (197 in 7 matches) while scoring 33.14 GF/GP",
                "injury_summary": "Official Sunday 17:00 CET StarLigue closing match of Journée 8.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Montpellier Handball",
                    "USM Saran Loiret Handball",
                    mu_margin_a=6.9,
                    sigma_margin=4.9,
                    mu_total=61.2,
                    sigma_total=5.2,
                    spread_a=-6.5,
                    total_line=61.5,
                    three_way_draw_band=0.5,
                    unit_label="Goal",
                ),
                "winner_pick": "Montpellier Handball",
                "pick_market": "total",
                "pick_selection": "Under 61.5",
                "confidence": "medium",
                "prediction_text": (
                    "Take Under 61.5 total goals—alongside third-placed Montpellier Handball as clear home winners—in "
                    "Sunday's Journée 8 finale against 10th-placed USM Saran at FDI Stadium (16:00 UTC). Montpellier "
                    "(5-0-2, 10 points) boast the stingiest defensive record in France at 28.1 goals allowed per "
                    "match (232:197), while Saran average a modest 30.1 goals scored (211:227) and will face immense "
                    "half-court resistance trying to crack 27."
                ),
            },
        ]
    )

    # =========================================================================
    # 14. GAELIC SPORTS (OLBG ID 25) — 5 Official GAA County Senior Football Finals
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-GS-01",
                "sport": "gaelic-sports",
                "sport_name": "Gaelic Sports",
                "olbg_sport_id": 25,
                "competition": "Louth Senior Football Championship Final Replay",
                "event": "Newtown Blues vs St Mochta's",
                "away": "St Mochta's",
                "home": "Newtown Blues",
                "venue": "Integral GAA Grounds, Drogheda (15:30 IST / 14:30 UTC)",
                "start_utc": "2026-10-24T14:30:00Z",
                "official_source_name": "GAA Official Weekend Senior Club Championship Finals Preview",
                "official_source_url": "https://www.gaa.ie/article/preview-weekend-s-senior-club-championship-finals-x9182",
                "secondary_source_url": "https://www.gaa.ie/",
                "olbg_url": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
                "form_summary": "Saturday replay after dramatic drawn Louth SFC Final; 23-time Louth champions Newtown Blues vs first-time senior finalists St Mochta's",
                "stats_summary": "Drogheda venue suits Blues' big-day championship know-how; Byrne brothers lead St Mochta's attack",
                "injury_summary": "Both sides came through drawn final without reported suspensions; Saturday IST (UTC+1) throw-in.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Newtown Blues",
                    "St Mochta's",
                    mu_margin_a=1.8,
                    sigma_margin=5.6,
                    mu_total=29.2,
                    sigma_total=5.4,
                    spread_a=-1.5,
                    total_line=29.5,
                    three_way_draw_band=0.5,
                    unit_label="Point",
                ),
                "winner_pick": "Newtown Blues",
                "pick_market": "winner",
                "pick_selection": "Newtown Blues",
                "confidence": "high",
                "prediction_text": (
                    "Back 23-time Louth kings Newtown Blues on the 60-minute match-winner line in Saturday afternoon's "
                    "Senior Football Championship Final replay against St Mochta's in Drogheda (14:30 UTC). First-time "
                    "finalists St Mochta's—spearheaded by the Byrne brothers—had their golden chance in the drawn "
                    "opener before Blues' late surge forced a second day out. Playing in their home town of Drogheda, "
                    "Newtown Blues' bench craft and county-final muscle memory typically tell in replays."
                ),
            },
            {
                "id": "87b3-GS-02",
                "sport": "gaelic-sports",
                "sport_name": "Gaelic Sports",
                "olbg_sport_id": 25,
                "competition": "Kerry Senior Football Championship Final",
                "event": "Dr Crokes vs Kenmare Shamrocks",
                "away": "Kenmare Shamrocks",
                "home": "Dr Crokes",
                "venue": "Austin Stack Park, Tralee (14:00 GMT / 14:00 UTC)",
                "start_utc": "2026-10-25T14:00:00Z",
                "official_source_name": "Munster GAA Official Fixtures Calendar & GAA Club Preview",
                "official_source_url": "https://munster.gaa.ie/fixtures/events-calendar/",
                "secondary_source_url": "https://www.gaa.ie/article/preview-weekend-s-senior-club-championship-finals-x9182",
                "olbg_url": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
                "form_summary": "Killarney powerhouse Dr Crokes face Sean O'Shea-inspired Kenmare Shamrocks for the Bishop Moynihan Cup",
                "stats_summary": "Dr Crokes carry deeper six-forward scoring spread vs Kenmare's reliance on Kerry star Sean O'Shea",
                "injury_summary": "Sunday 14:00 GMT throw-in (14:00 UTC after Ireland's overnight switch from IST to GMT).",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Dr Crokes",
                    "Kenmare Shamrocks",
                    mu_margin_a=2.9,
                    sigma_margin=5.8,
                    mu_total=31.4,
                    sigma_total=5.6,
                    spread_a=-2.5,
                    total_line=31.5,
                    three_way_draw_band=0.5,
                    unit_label="Point",
                ),
                "winner_pick": "Dr Crokes",
                "pick_market": "winner",
                "pick_selection": "Dr Crokes",
                "confidence": "high",
                "prediction_text": (
                    "Play Dr Crokes to lift the Kerry Senior Football Championship in 60 minutes against Kenmare "
                    "Shamrocks on Sunday at Austin Stack Park in Tralee (14:00 UTC). Kenmare possess arguably the "
                    "premier two-point dead-ball shooter in club football in Kerry talisman Sean O'Shea, yet Killarney "
                    "giants Dr Crokes bring superior balance across all six attacking positions and battle-tested "
                    "knockout composure that wears divisional and club challengers down in the closing quarter."
                ),
            },
            {
                "id": "87b3-GS-03",
                "sport": "gaelic-sports",
                "sport_name": "Gaelic Sports",
                "olbg_sport_id": 25,
                "competition": "Waterford Senior Football Championship Final",
                "event": "Rathgormack vs The Nire",
                "away": "The Nire",
                "home": "Rathgormack",
                "venue": "Cappoquin Logistics Fraher Field, Dungarvan (14:30 GMT / 14:30 UTC)",
                "start_utc": "2026-10-25T14:30:00Z",
                "official_source_name": "Munster GAA Official Fixtures Calendar & GAA Club Preview",
                "official_source_url": "https://munster.gaa.ie/fixtures/events-calendar/",
                "secondary_source_url": "https://www.gaa.ie/article/preview-weekend-s-senior-club-championship-finals-x9182",
                "olbg_url": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
                "form_summary": "Modern Waterford football classic: defending champions Rathgormack vs traditional standard-bearers The Nire",
                "stats_summary": "Low-scoring autumn Fraher Field deciders historically settled by 1-4 points",
                "injury_summary": "Official Munster GAA fixture confirmed for Sunday 2:30 PM GMT in Dungarvan.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Rathgormack",
                    "The Nire",
                    mu_margin_a=2.6,
                    sigma_margin=5.4,
                    mu_total=25.8,
                    sigma_total=5.0,
                    spread_a=-2.5,
                    total_line=26.5,
                    three_way_draw_band=0.5,
                    unit_label="Point",
                ),
                "winner_pick": "Rathgormack",
                "pick_market": "winner",
                "pick_selection": "Rathgormack",
                "confidence": "medium",
                "prediction_text": (
                    "Side with defending champions Rathgormack on the 60-minute match-winner line against perennial "
                    "foes The Nire in Sunday's Waterford Senior Football Final at Fraher Field (14:30 UTC). These two "
                    "parishes have monopolised Déise senior football for over a decade in Cagey, low-scoring Dungarvan "
                    "tussles, and Rathgormack's athletic middle-third running power and stingy tackling unit hold a "
                    "two-to-three-point edge over sixty minutes."
                ),
            },
            {
                "id": "87b3-GS-04",
                "sport": "gaelic-sports",
                "sport_name": "Gaelic Sports",
                "olbg_sport_id": 25,
                "competition": "Cork Premier Senior Football Championship Final",
                "event": "St Finbarr's vs Nemo Rangers",
                "away": "Nemo Rangers",
                "home": "St Finbarr's",
                "venue": "SuperValu Páirc Uí Chaoimh, Cork (16:00 GMT / 16:00 UTC)",
                "start_utc": "2026-10-25T16:00:00Z",
                "official_source_name": "Munster GAA Official Fixtures Calendar & GAA Club Preview",
                "official_source_url": "https://munster.gaa.ie/fixtures/events-calendar/",
                "secondary_source_url": "https://www.gaa.ie/article/preview-weekend-s-senior-club-championship-finals-x9182",
                "olbg_url": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
                "form_summary": "Box-office Cork city Southside derby: 2025 Munster finalists St Finbarr's (Steven Sherlock) vs 23-time Cork champions Nemo Rangers",
                "stats_summary": "Wide Páirc Uí Chaoimh pitch rewards St Finbarr's kick-passing & two-point shooting range",
                "injury_summary": "Confirmed Sunday 4:00 PM GMT throw-in at SuperValu Páirc Uí Chaoimh.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "St Finbarr's",
                    "Nemo Rangers",
                    mu_margin_a=2.1,
                    sigma_margin=5.7,
                    mu_total=28.6,
                    sigma_total=5.3,
                    spread_a=-1.5,
                    total_line=28.5,
                    three_way_draw_band=0.5,
                    unit_label="Point",
                ),
                "winner_pick": "St Finbarr's",
                "pick_market": "winner",
                "pick_selection": "St Finbarr's",
                "confidence": "high",
                "prediction_text": (
                    "Back St Finbarr's to edge arch-rivals Nemo Rangers in normal-time 1X2 betting for Sunday's "
                    "Cork Premier Senior Football Final at SuperValu Páirc Uí Chaoimh (16:00 UTC). Nemo's 23-title "
                    "pedigree always commands respect on Leeside, yet the Togher Blues bring prime age-profile "
                    "cohesion from last winter's Munster Club Championship final run and elite scoring efficiency "
                    "through marksman Steven Sherlock on Páirc Uí Chaoimh's expansive turf."
                ),
            },
            {
                "id": "87b3-GS-05",
                "sport": "gaelic-sports",
                "sport_name": "Gaelic Sports",
                "olbg_sport_id": 25,
                "competition": "Galway Senior Football Championship Final (Rescheduled)",
                "event": "Maigh Cuilinn vs Salthill-Knocknacarra",
                "away": "Salthill-Knocknacarra",
                "home": "Maigh Cuilinn",
                "venue": "Pearse Stadium, Salthill, Galway (16:00 GMT / 16:00 UTC)",
                "start_utc": "2026-10-25T16:00:00Z",
                "official_source_name": "Galway GAA Official Weather Fixture Change Notice",
                "official_source_url": "https://www.galwaygaa.ie/changes-weekend-football-fixture-schedule/",
                "secondary_source_url": "https://www.gaa.ie/article/preview-weekend-s-senior-club-championship-finals-x9182",
                "olbg_url": "https://www.olbg.com/betting-tips/Gaelic_Football/25",
                "form_summary": "Officially moved from Sat 24 Oct 18:15 IST to Sun 25 Oct 16:00 GMT due to weather warning; 2022 & 2025 champions Maigh Cuilinn vs Rob Finnerty's Salthill-Knocknacarra",
                "stats_summary": "Pearse Stadium coastal breeze & Salthill local familiarity keep margins razor-thin",
                "injury_summary": "Extra 22 hours recovery from Galway CCC weather postponement benefits both panels.",
                "unconfirmed_fields": [],
                "markets": price_normal_match(
                    "Maigh Cuilinn",
                    "Salthill-Knocknacarra",
                    mu_margin_a=1.6,
                    sigma_margin=5.5,
                    mu_total=26.4,
                    sigma_total=5.1,
                    spread_a=-1.5,
                    total_line=26.5,
                    three_way_draw_band=0.5,
                    unit_label="Point",
                ),
                "winner_pick": "Maigh Cuilinn",
                "pick_market": "winner",
                "pick_selection": "Maigh Cuilinn",
                "confidence": "medium",
                "prediction_text": (
                    "Lean defending Galway champions Maigh Cuilinn on the 60-minute match-winner line after Galway "
                    "GAA shifted this Frank Fox Cup decider from Saturday evening's storm warning to Sunday at "
                    "16:00 UTC at Pearse Stadium. Salthill-Knocknacarra enjoy home-parish familiarity on the promenade "
                    "and prolific forward Rob Finnerty, yet Maigh Cuilinn's seasoned inter-county spine—winners in "
                    "both 2022 and 2025—handles heavy coastal Pearse Stadium conditions better than anyone in Connacht."
                ),
            },
        ]
    )

    # =========================================================================
    # 15. GREYHOUNDS (OLBG ID 28) — 5 Official Saturday Dunstall Park Open Races
    # =========================================================================
    rows.extend(
        [
            {
                "id": "87b3-GH-01",
                "sport": "greyhounds",
                "sport_name": "Greyhounds",
                "olbg_sport_id": 28,
                "competition": "Dunstall Park Open Card — Race 8 (OR3 Bitches, 480m Flat)",
                "event": "20:38 Dunstall Park — Premier Greyhound Racing Bitches (480m)",
                "away": "T1 Kilwest Diva / T2 Countess Penny",
                "home": "T3 Jazzy Belle",
                "venue": "Dunstall Park Greyhound Stadium, Wolverhampton (£1,000 Purse)",
                "start_utc": "2026-10-24T19:38:00Z",
                "official_source_name": "Dunstall Park Official GBGB Racecard PDF (Meeting 216, Race 8)",
                "official_source_url": "https://www.dunstallpark-greyhounds.co.uk/DunstallParkGreyhounds/downloads/24-10-2026-evening-racecard.pdf",
                "secondary_source_url": "https://www.gbgb.org.uk/oaks-quality-shines-as-seal-tips-track-record-bid-at-dunstall-park/",
                "olbg_url": "https://www.olbg.com/betting-tips/Greyhounds/28",
                "form_summary": "6-trap OR3 bitches consolation featuring Oaks heat winner T3 Jazzy Belle (28.53s, Kevin Hutton) & Oaks SF qualifiers T1 Kilwest Diva & T2 Countess Penny",
                "stats_summary": "Traps: 1 Kilwest Diva, 2 Countess Penny, 3 Jazzy Belle, 4 Headford Lily (M), 5 Aero Dash (M), 6 Ballyhoe Natalee (M)",
                "injury_summary": "Official 6-runner GBGB automated trap draw confirmed on Meeting 216 final card.",
                "unconfirmed_fields": [],
                "markets": price_field_event(
                    winner_label="Race 8 Winner (6 Traps)",
                    field_weights=[
                        ("Trap 3 Jazzy Belle", 0.275),
                        ("Trap 1 Kilwest Diva", 0.225),
                        ("Trap 2 Countess Penny", 0.195),
                        ("Trap 4 Headford Lily", 0.125),
                        ("Trap 5 Aero Dash", 0.095),
                        ("Trap 6 Ballyhoe Natalee", 0.085),
                    ],
                    h2h_label="Trap Matchup: Trap 3 Jazzy Belle vs Trap 1 Kilwest Diva",
                    h2h_pair=[("Trap 3 Jazzy Belle", 0.550), ("Trap 1 Kilwest Diva", 0.450)],
                    total_label="Winning Time vs 28.20 Seconds (480m)",
                    total_pair=[("Faster than 28.20s (<28.20)", 0.480), ("28.20s or Slower", 0.520)],
                    total_line=28.20,
                    deriv_label="Inside Traps (1-3) vs Outside Traps (4-6)",
                    deriv_pair=[("Inside Traps 1-3 Win", 0.695), ("Outside Traps 4-6 Win", 0.305)],
                ),
                "winner_pick": "Trap 3 Jazzy Belle",
                "pick_market": "winner",
                "pick_selection": "Trap 3 Jazzy Belle",
                "confidence": "medium",
                "prediction_text": (
                    "Side with Trap 3 Jazzy Belle to land Race 8 (20:38 BST / 19:38 UTC), the Premier Greyhound Racing "
                    "Bitches 480m open supporting Dunstall Park's Gala card. Trained at Towcester by Kevin Hutton, "
                    "Jazzy Belle clocked an all-the-way 28.53s victory in Round 1 of the Oaks here earlier this month "
                    "and drops out of Classic company alongside Oaks semi-finalists Kilwest Diva (Trap 1) and Countess "
                    "Penny (Trap 2), holding early-pace command inside three middle seeds."
                ),
            },
            {
                "id": "87b3-GH-02",
                "sport": "greyhounds",
                "sport_name": "Greyhounds",
                "olbg_sport_id": 28,
                "competition": "Dunstall Park Open Card — Race 9 (OR3 Standard Div 1, 480m Flat)",
                "event": "20:58 Dunstall Park — PGR Standard Div 1 (480m)",
                "away": "T1 Newin Spot / T2 Droopys Vicar",
                "home": "T6 Holding Blaze",
                "venue": "Dunstall Park Greyhound Stadium, Wolverhampton (£1,000 Purse)",
                "start_utc": "2026-10-24T19:58:00Z",
                "official_source_name": "Dunstall Park Official GBGB Racecard PDF (Meeting 216, Race 9)",
                "official_source_url": "https://www.dunstallpark-greyhounds.co.uk/DunstallParkGreyhounds/downloads/24-10-2026-evening-racecard.pdf",
                "secondary_source_url": "https://www.gbgb.org.uk/",
                "olbg_url": "https://www.olbg.com/betting-tips/Greyhounds/28",
                "form_summary": "Lone wide seed T6 Holding Blaze (Richie Taberner) drops from Cat 1 Steel City Cup campaign vs Graham Holland's Irish raider T1 Newin Spot",
                "stats_summary": "Traps: 1 Newin Spot, 2 Droopys Vicar, 3 Tomahawk, 4 Dunbolg Formula, 5 Skyfall Khan (M), 6 Holding Blaze (W - lone wide!)",
                "injury_summary": "Official 6-runner GBGB automated trap draw confirmed on Meeting 216 final card.",
                "unconfirmed_fields": [],
                "markets": price_field_event(
                    winner_label="Race 9 Winner (6 Traps)",
                    field_weights=[
                        ("Trap 6 Holding Blaze", 0.305),
                        ("Trap 1 Newin Spot", 0.255),
                        ("Trap 2 Droopys Vicar", 0.175),
                        ("Trap 5 Skyfall Khan", 0.105),
                        ("Trap 3 Tomahawk", 0.085),
                        ("Trap 4 Dunbolg Formula", 0.075),
                    ],
                    h2h_label="Trap Matchup: Trap 6 Holding Blaze vs Trap 1 Newin Spot",
                    h2h_pair=[("Trap 6 Holding Blaze", 0.545), ("Trap 1 Newin Spot", 0.455)],
                    total_label="Winning Time vs 28.05 Seconds (480m)",
                    total_pair=[("Faster than 28.05s (<28.05)", 0.505), ("28.05s or Slower", 0.495)],
                    total_line=28.05,
                    deriv_label="Trap 6 Holding Blaze Top-2 Finish",
                    deriv_pair=[("Holding Blaze Top-2 Yes", 0.548), ("Outside Top-2", 0.452)],
                ),
                "winner_pick": "Trap 6 Holding Blaze",
                "pick_market": "winner",
                "pick_selection": "Trap 6 Holding Blaze",
                "confidence": "high",
                "prediction_text": (
                    "Back Trap 6 Holding Blaze to win Race 9 (20:58 BST / 19:58 UTC), Dunstall Park's Standard "
                    "Division 1 open over 480 metres. Richie Taberner's Monmore runner brings genuine Category One "
                    "class from Sheffield's Steel City Cup semi-finals and lands a dream racing-room makeup as the "
                    "solitary wide seed outside middle runner Skyfall Khan (Trap 5), keeping clear of inside crowding "
                    "between Graham Holland's Irish challenger Newin Spot (Trap 1) and Droopys Vicar (Trap 2)."
                ),
            },
            {
                "id": "87b3-GH-03",
                "sport": "greyhounds",
                "sport_name": "Greyhounds",
                "olbg_sport_id": 28,
                "competition": "GBGB Category One Final — ARC Scurry Gold Cup Final (270m Sprint)",
                "event": "21:18 Dunstall Park — ARC Scurry Gold Cup Final (OR1, £12,500)",
                "away": "T5 Magical Jason / T4 Roanna Mamba",
                "home": "T2 Shadow Storm",
                "venue": "Dunstall Park Greyhound Stadium, Wolverhampton (270m Flat)",
                "start_utc": "2026-10-24T20:18:00Z",
                "official_source_name": "GBGB Scurry Gold Cup Final Preview & Dunstall Park Racecard (Race 10)",
                "official_source_url": "https://www.gbgb.org.uk/shadow-storm-chases-scurry-gold-cup-history-at-dunstall-park/",
                "secondary_source_url": "https://www.dunstallpark-greyhounds.co.uk/DunstallParkGreyhounds/downloads/24-10-2026-evening-racecard.pdf",
                "olbg_url": "https://www.olbg.com/betting-tips/Greyhounds/28",
                "form_summary": "T2 Shadow Storm (reigning GBGB Sprinter of the Year & defending 2025 Scurry champ, fastest SF 15.66s -5); T4 Roanna Mamba (SF2 15.73s -5); T5 Magical Jason (fastest Heat 15.50s); T1 Avarua Lake (SF1 15.86s -5)",
                "stats_summary": "Traps: 1 Avarua Lake, 2 Shadow Storm, 3 Newinn Souly, 4 Roanna Mamba, 5 Magical Jason, 6 Ballinakill Liam",
                "injury_summary": "All six Category One Scurry Gold Cup finalists confirmed on official Race 10 card.",
                "unconfirmed_fields": [],
                "markets": price_field_event(
                    winner_label="ARC Scurry Gold Cup Final Winner",
                    field_weights=[
                        ("Trap 2 Shadow Storm", 0.355),
                        ("Trap 5 Magical Jason", 0.215),
                        ("Trap 4 Roanna Mamba", 0.165),
                        ("Trap 1 Avarua Lake", 0.115),
                        ("Trap 6 Ballinakill Liam", 0.085),
                        ("Trap 3 Newinn Souly", 0.065),
                    ],
                    h2h_label="Final Matchup: Trap 2 Shadow Storm vs Trap 5 Magical Jason",
                    h2h_pair=[("Trap 2 Shadow Storm", 0.622), ("Trap 5 Magical Jason", 0.378)],
                    total_label="Winning Clock vs 15.58 Seconds (270m)",
                    total_pair=[("Faster than 15.58s (<15.58)", 0.515), ("15.58s or Slower", 0.485)],
                    total_line=15.58,
                    deriv_label="Richard Rees Kennel (T1 or T2) Wins Trophy?",
                    deriv_pair=[("Yes (T1 or T2 Wins)", 0.470), ("No (Traps 3-6 Win)", 0.530)],
                ),
                "winner_pick": "Trap 2 Shadow Storm",
                "pick_market": "winner",
                "pick_selection": "Trap 2 Shadow Storm",
                "confidence": "high",
                "prediction_text": (
                    "Back defending champion Trap 2 Shadow Storm to make Category One history in Saturday night's "
                    "£12,500 Arena Racing Company Scurry Gold Cup Final over 270 metres at Dunstall Park (20:18 UTC). "
                    "Richard Rees' reigning GBGB Sprinter of the Year posted the fastest semi-final victory in "
                    "15.66s (-5) after surging past Newinn Souly between the turns, and breaks directly alongside "
                    "kennelmate Avarua Lake (Trap 1, 15.86s) inside 15.50s heat blazer Magical Jason (Trap 5) and "
                    "Roanna Mamba (Trap 4)."
                ),
            },
            {
                "id": "87b3-GH-04",
                "sport": "greyhounds",
                "sport_name": "Greyhounds",
                "olbg_sport_id": 28,
                "competition": "GBGB Category One Final — Premier Greyhound Racing Oaks Final (480m)",
                "event": "21:38 Dunstall Park — PGR Oaks Final (OR1, £20,000)",
                "away": "T3 Strike It Skye / T5 Slingshot Poppy",
                "home": "T1 Fahrenheit Jess",
                "venue": "Dunstall Park Greyhound Stadium, Wolverhampton (480m Flat)",
                "start_utc": "2026-10-24T20:38:00Z",
                "official_source_name": "GBGB Oaks Final Preview & Dunstall Park Racecard (Race 11)",
                "official_source_url": "https://www.gbgb.org.uk/signet-nayla-chases-oaks-glory-as-hutton-targets-dunstall-park-double/",
                "secondary_source_url": "https://www.dunstallpark-greyhounds.co.uk/DunstallParkGreyhounds/downloads/24-10-2026-evening-racecard.pdf",
                "olbg_url": "https://www.olbg.com/betting-tips/Greyhounds/28",
                "form_summary": "T1 Fahrenheit Jess (Graham Holland, fastest SF 27.87s -10); T5 Slingshot Poppy (unbeaten 3/3 in Oaks, SF 27.90s -10); T3 Strike It Skye (27.90s R2); T6 Signet Nayla (SF1 28.35s -10)",
                "stats_summary": "Traps: 1 Fahrenheit Jess, 2 Holding Hollie, 3 Strike It Skye, 4 Ballydoyle Tina, 5 Slingshot Poppy, 6 Signet Nayla (M)",
                "injury_summary": "All six Category One Oaks finalists confirmed on official Race 11 card.",
                "unconfirmed_fields": [],
                "markets": price_field_event(
                    winner_label="PGR Oaks Final Winner (£20,000)",
                    field_weights=[
                        ("Trap 1 Fahrenheit Jess", 0.340),
                        ("Trap 3 Strike It Skye", 0.215),
                        ("Trap 5 Slingshot Poppy", 0.165),
                        ("Trap 6 Signet Nayla", 0.130),
                        ("Trap 4 Ballydoyle Tina", 0.085),
                        ("Trap 2 Holding Hollie", 0.065),
                    ],
                    h2h_label="Final Matchup: Trap 1 Fahrenheit Jess vs Trap 3 Strike It Skye",
                    h2h_pair=[("Trap 1 Fahrenheit Jess", 0.612), ("Trap 3 Strike It Skye", 0.388)],
                    total_label="Winning Clock vs 27.85 Seconds (480m)",
                    total_pair=[("Faster than 27.85s (<27.85)", 0.525), ("27.85s or Slower", 0.475)],
                    total_line=27.85,
                    deriv_label="Graham Holland Kennel (T1 or T4) Wins Oaks?",
                    deriv_pair=[("Yes (Irish Raider Wins)", 0.425), ("No (UK Kennel Wins)", 0.575)],
                ),
                "winner_pick": "Trap 1 Fahrenheit Jess",
                "pick_market": "winner",
                "pick_selection": "Trap 1 Fahrenheit Jess",
                "confidence": "high",
                "prediction_text": (
                    "Play Graham Holland's Irish raider Trap 1 Fahrenheit Jess to capture Saturday night's £20,000 "
                    "Premier Greyhound Racing Oaks Final over 480 metres at Dunstall Park (20:38 UTC). Lightly raced "
                    "Fahrenheit Jess clocked the fastest semi-final time of the round in 27.87s (-10) from the front "
                    "and draws the coveted red jacket on the rails, whereas unbeaten Scottish star Slingshot Poppy "
                    "(27.90s) faces a tricky Trap 5 berth between Ballydoyle Tina and Signet Nayla (28.35s), with "
                    "Strike It Skye chasing from Trap 3."
                ),
            },
            {
                "id": "87b3-GH-05",
                "sport": "greyhounds",
                "sport_name": "Greyhounds",
                "olbg_sport_id": 28,
                "competition": "Dunstall Park Open Card — Race 12 (OR3 Stayers Div 1, 660m Flat)",
                "event": "21:54 Dunstall Park — PGR Stayers Div 1 (660m)",
                "away": "T4 Newinn Jolie / T2 Quill Quids",
                "home": "T5 Resonate",
                "venue": "Dunstall Park Greyhound Stadium, Wolverhampton (5-Runner Card, T6 Vacant)",
                "start_utc": "2026-10-24T20:54:00Z",
                "official_source_name": "Dunstall Park Official GBGB Racecard PDF (Meeting 216, Race 12)",
                "official_source_url": "https://www.dunstallpark-greyhounds.co.uk/DunstallParkGreyhounds/downloads/24-10-2026-evening-racecard.pdf",
                "secondary_source_url": "https://www.gbgb.org.uk/",
                "olbg_url": "https://www.olbg.com/betting-tips/Greyhounds/28",
                "form_summary": "5-runner six-bend 660m open (Trap 6 VACANT); Kevin Hutton's T5 Resonate steps back up to optimal staying trip after reaching Oaks Semi-Finals over 480m!",
                "stats_summary": "Traps: 1 Carrick Scholsey (transposed GBGB-approved), 2 Quill Quids, 3 Beatties Lena (M), 4 Newinn Jolie (M), 5 Resonate (W), 6 VACANT",
                "injury_summary": "Trap 6 officially VACANT on GBGB Meeting 216 card (logged on Flagged for Review; 5 runners priced).",
                "unconfirmed_fields": ["trap_6_vacant"],
                "markets": price_field_event(
                    winner_label="Race 12 Winner (5 Runners, T6 Vacant)",
                    field_weights=[
                        ("Trap 5 Resonate", 0.345),
                        ("Trap 4 Newinn Jolie", 0.245),
                        ("Trap 2 Quill Quids", 0.175),
                        ("Trap 3 Beatties Lena", 0.125),
                        ("Trap 1 Carrick Scholsey", 0.110),
                    ],
                    h2h_label="Stayers Matchup: Trap 5 Resonate vs Trap 4 Newinn Jolie",
                    h2h_pair=[("Trap 5 Resonate", 0.585), ("Trap 4 Newinn Jolie", 0.415)],
                    total_label="Winning Clock vs 39.85 Seconds (660m)",
                    total_pair=[("Faster than 39.85s (<39.85)", 0.510), ("39.85s or Slower", 0.490)],
                    total_line=39.85,
                    deriv_label="Wide/Middle (T4-T5) vs Inside (T1-T3)",
                    deriv_pair=[("Traps 4 or 5 Win", 0.590), ("Traps 1-3 Win", 0.410)],
                ),
                "winner_pick": "Trap 5 Resonate",
                "pick_market": "winner",
                "pick_selection": "Trap 5 Resonate",
                "confidence": "medium",
                "prediction_text": (
                    "Side with Trap 5 Resonate to capture Race 12 (21:54 BST / 20:54 UTC) over six bends (660 metres) "
                    "at Dunstall Park. Trainer Kevin Hutton noted during the Oaks campaign that four bends was shorter "
                    "than Resonate's natural trip even as she impressively qualified all the way to the Oaks semi-"
                    "finals, and stepping back up to 660m with Trap 6 vacant outside her gives the wide seed acres of "
                    "room against Maxine Locke's Newinn Jolie (Trap 4)."
                ),
            },
        ]
    )

    return rows
