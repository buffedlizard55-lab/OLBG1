#!/usr/bin/env python3
"""Part 3 of master verified events catalog for Session c17a9192-olbg1 (Sports 7..17)."""

from __future__ import annotations
from c17a9192_data import E

EVENTS_PART3: list[dict] = [
    # =========================================================================
    # 7. HANDBALL (20 Live OLBG Matches: All 12 EHF CL Men R5 + 8 Domestic/Euro W)
    # Every single EHF club record verified verbatim against ehfcl.eurohandball.com Groups A-F!
    # =========================================================================
    E(
        "hand-ehf-aal-cel-12044", "Handball", "EHF Champions League Men — Group C Round 5", "h2h_3way",
        "Aalborg Håndbold", "RK Celje Pivovarna Laško", "2026-10-21T18:45:00Z", "Sparekassen Danmark Arena, Aalborg",
        "verified",
        [("EHF CL Standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/"),
         ("EHF CL Matches", "https://ehfcl.eurohandball.com/men/2026-27/matches/")],
        "Group C #2: 3-1-0 (7 pts, 134:113, +21 GD)",
        "Group C #4: 0-0-4 (0 pts, 111:145, -34 GD)",
        0.855, 0.055, -7.5, "Goals", 63.5, "Goals", True,
        "Aalborg Håndbold", "high",
        12044, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Aalborg_Handbold_vs_RK_Celje/20?event_id=12044",
        "Money Line", "Tie", "4/5 (80%)", False,
        ["Extreme OLBG longshot anomaly: 4/5 (80%) of OLBG tips back a 60-minute Draw (~5.5% model prob) on unbeaten Aalborg vs 0-0-4 Celje"]
    ),
    E(
        "hand-ehf-din-sah-12045", "Handball", "EHF Champions League Men — Group E Round 5 (Match #202711020101059)", "h2h_3way",
        "CS Dinamo Bucuresti", "SAH - Aarhus (Skanderborg-Aarhus)", "2026-10-21T16:45:00Z", "Sala Polivalenta Dinamo, Bucharest",
        "verified",
        [("EHF CL Standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/"),
         ("EHF CL Matches", "https://ehfcl.eurohandball.com/men/2026-27/matches/")],
        "Group E #4: 0-1-3 (1 pt, 108:133, -25 GD)",
        "Group E #2: 2-1-1 (5 pts, 121:120, +1 GD)",
        0.415, 0.105, 1.5, "Goals", 59.5, "Goals", True,
        "SAH - Aarhus (Skanderborg-Aarhus)", "medium",
        12045, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Dinamo_Bucuresti_vs_Skanderborg_Handbold/20?event_id=12045",
        "Money Line", "Dinamo Bucuresti", "4/11 (36%)", False,
        ["Overturned false-positive flag from session 2360a617: Skanderborg-Aarhus Håndbold ('SAH - Aarhus') IS officially in Group E (2-1-1, 5 pts)"]
    ),
    E(
        "hand-ehf-bar-mon-12046", "Handball", "EHF Champions League Men — Group E Round 5", "h2h_3way",
        "Barça", "Montpellier Handball", "2026-10-22T18:45:00Z", "Palau Blaugrana, Barcelona",
        "verified",
        [("EHF CL Standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/"),
         ("EHF CL Matches", "https://ehfcl.eurohandball.com/men/2026-27/matches/")],
        "Group E #1: 4-0-0 (8 pts, 140:107, +33 GD)",
        "Group E #3: 1-0-3 (2 pts, 108:117, -9 GD)",
        0.825, 0.065, -6.5, "Goals", 61.5, "Goals", True,
        "Barça", "high",
        12046, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/FC_Barcelona_vs_Montpellier/20?event_id=12046",
        "Money Line", "Montpellier", "2/6 (33%)", False, []
    ),
    E(
        "hand-ehf-kri-kie-12047", "Handball", "EHF Champions League Men — Group F Round 5", "h2h_3way",
        "HC Kriens-Luzern", "Industria Kielce", "2026-10-21T18:45:00Z", "Pilatus Arena, Kriens",
        "verified",
        [("EHF CL Standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/")],
        "Group F #3: 2-0-2 (4 pts, 121:122, -1 GD)",
        "Group F #2: 2-0-2 (4 pts, 118:118, 0 GD)",
        0.390, 0.110, 1.5, "Goals", 60.5, "Goals", True,
        "Industria Kielce", "low",
        12047, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/HC_Kriens_Luzern_vs_KS_Kielce/20?event_id=12047",
        "Money Line", "Tie", "3/6 (50%)", False, []
    ),
    E(
        "hand-ehf-kol-mag-12048", "Handball", "EHF Champions League Men — Group F Round 5", "h2h_3way",
        "Kolstad Håndball", "SC Magdeburg", "2026-10-22T18:45:00Z", "Kolstad Arena, Kolstad, Norway",
        "verified",
        [("EHF CL Standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/"),
         ("EHF CL Matches", "https://ehfcl.eurohandball.com/men/2026-27/matches/")],
        "Group F #4: 0-0-4 (0 pts, 108:140, -32 GD)",
        "Group F #1: 4-0-0 (8 pts, 141:108, +33 GD)",
        0.135, 0.065, 5.5, "Goals", 62.5, "Goals", True,
        "SC Magdeburg", "high",
        12048, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Kolstad_vs_SC_Magdeburg/20?event_id=12048",
        "Money Line", "Tie", "3/6 (50%)", False,
        ["50% of OLBG tips back a 60m Tie despite Magdeburg sitting 4-0-0 (+33 GD) vs winless 0-0-4 Kolstad (-32 GD)"]
    ),
    E(
        "hand-ehf-mel-wis-12049", "Handball", "EHF Champions League Men — Group B Round 5", "h2h_3way",
        "MT Melsungen", "Orlen Wisla Plock", "2026-10-22T16:45:00Z", "Rothenbach-Halle, Kassel",
        "verified",
        [("EHF CL Standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/")],
        "Group B #3: 2-0-2 (4 pts, 110:112, -2 GD)",
        "Group B #1: 3-0-1 (6 pts, 115:108, +7 GD)",
        0.475, 0.115, 0.5, "Goals", 56.5, "Goals", False,
        "MT Melsungen", "low",
        12049, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/MT_Melsungen_vs_Wisla_Plock/20?event_id=12049",
        "Money Line", "MT Melsungen", "2/4 (50%)", False,
        ["Prior repo data/fixtures.json misstated MT Melsungen as 1-0-3 (2 pts) instead of official 2-0-2 (4 pts)"]
    ),
    E(
        "hand-ehf-nan-var-12050", "Handball", "EHF Champions League Men — Group B Round 5", "h2h_3way",
        "HBC Nantes", "HC Vardar 1961", "2026-10-21T18:45:00Z", "H Arena, Nantes",
        "verified",
        [("EHF CL Standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/")],
        "Group B #2: 3-0-1 (6 pts, 115:110, +5 GD)",
        "Group B #4: 0-0-4 (0 pts, 121:131, -10 GD)",
        0.795, 0.075, -5.5, "Goals", 60.5, "Goals", True,
        "HBC Nantes", "high",
        12050, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Nantes_vs_HC_Vardar/20?event_id=12050",
        "Money Line", "Nantes", "6/10 (60%)", False,
        ["Prior repo data/fixtures.json misstated HC Vardar 1961 as 1-0-3 (2 pts) instead of official winless 0-0-4 (0 pts)"]
    ),
    E(
        "hand-ehf-sze-gog-12051", "Handball", "EHF Champions League Men — Group D Round 5", "h2h_3way",
        "OTP Bank - PICK Szeged", "GOG", "2026-10-22T16:45:00Z", "PICK Arena, Szeged",
        "verified",
        [("EHF CL Standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/")],
        "Group D #3: 1-1-2 (3 pts, 127:124, +3 GD)",
        "Group D #2: 3-0-1 (6 pts, 134:128, +6 GD)",
        0.545, 0.110, -1.5, "Goals", 64.5, "Goals", True,
        "OTP Bank - PICK Szeged", "low",
        12051, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Pick_Szeged_vs_GOG/20?event_id=12051",
        "Money Line", "GOG", "2/4 (50%)", False, []
    ),
    E(
        "hand-ehf-par-por-12052", "Handball", "EHF Champions League Men — Group A Round 5", "h2h_3way",
        "RK Partizan AdmiralBet", "FC Porto", "2026-10-21T16:45:00Z", "Aleksandar Nikolic Hall, Belgrade",
        "verified",
        [("EHF CL Standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/")],
        "Group A #4: 0-0-4 (0 pts, 115:151, -36 GD)",
        "Group A #3: 1-0-3 (2 pts, 125:140, -15 GD)",
        0.355, 0.105, 2.5, "Goals", 61.5, "Goals", True,
        "FC Porto", "medium",
        12052, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/RK_Partizan_vs_FC_Porto/20?event_id=12052",
        "Money Line", "RK Partizan", "3/8 (38%)", False, []
    ),
    E(
        "hand-ehf-zag-psg-12053", "Handball", "EHF Champions League Men — Group C Round 5", "h2h_3way",
        "HC Zagreb", "Paris Saint-Germain", "2026-10-21T16:45:00Z", "Arena Zagreb, Zagreb",
        "verified",
        [("EHF CL Standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/"),
         ("EHF CL Matches", "https://ehfcl.eurohandball.com/men/2026-27/matches/")],
        "Group C #3: 1-0-3 (2 pts, 111:124, -13 GD)",
        "Group C #1: 3-1-0 (7 pts, 141:115, +26 GD)",
        0.180, 0.085, 4.5, "Goals", 61.5, "Goals", True,
        "Paris Saint-Germain", "high",
        12053, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/RK_Zagreb_vs_PSG_Handball/20?event_id=12053",
        "Money Line", "PSG Handball", "8/13 (62%)", False, []
    ),
    E(
        "hand-ehf-spo-kri-12054", "Handball", "EHF Champions League Men — Group D Round 5", "h2h_3way",
        "Sporting Clube de Portugal", "IFK Kristianstad", "2026-10-22T18:45:00Z", "Pavilhão João Rocha, Lisbon",
        "verified",
        [("EHF CL Standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/"),
         ("EHF CL Matches", "https://ehfcl.eurohandball.com/men/2026-27/matches/")],
        "Group D #1: 3-1-0 (7 pts, 143:119, +24 GD)",
        "Group D #4: 0-0-4 (0 pts, 108:141, -33 GD)",
        0.840, 0.060, -7.0, "Goals", 63.5, "Goals", True,
        "Sporting Clube de Portugal", "high",
        12054, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Sporting_CP_vs_IFK_Kristianstad/20?event_id=12054",
        "Money Line", "Tie", "3/7 (43%)", False,
        ["Prior repo data/fixtures.json left Sporting CP and IFK Kristianstad Group D standings completely blank"]
    ),
    E(
        "hand-ehf-ves-ber-12055", "Handball", "EHF Champions League Men — Group A Round 5", "h2h_3way",
        "One Veszprém HC", "Füchse Berlin", "2026-10-21T16:45:00Z", "One Veszprém Arena, Veszprém",
        "verified",
        [("EHF CL Standings", "https://ehfcl.eurohandball.com/men/2026-27/standings/")],
        "Group A #1: 4-0-0 (8 pts, 146:111, +35 GD)",
        "Group A #2: 3-0-1 (6 pts, 149:133, +16 GD)",
        0.615, 0.105, -2.5, "Goals", 66.5, "Goals", True,
        "One Veszprém HC", "medium",
        12055, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Veszprem_vs_Fuchse_Berlin/20?event_id=12055",
        "Money Line", "Veszprem", "5/11 (45%)", False, []
    ),
    # 8 Domestic League & Women's EHF Euro Qualifier Matches on OLBG Handball Hub
    E(
        "hand-den-mor-bje-12072", "Handball", "Danish Herreligaen", "h2h_3way",
        "Mors-Thy Håndbold", "Bjerringbro-Silkeborg", "2026-10-21T18:00:00Z", "",
        "tour_calendar_verified",
        [("EHF National Federation Hub", "https://www.eurohandball.com/en/")],
        "", "",
        0.410, 0.110, 1.5, "Goals", 58.5, "Goals", True,
        "Bjerringbro-Silkeborg", "low",
        12072, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Mors_Thy_Handbold_vs_Bjerringbro_Silkeborg/20?event_id=12072",
        "Match Handicap", "Mors Thy +3.50", "2/2 (100%)", False,
        ["Domestic Herreligaen standings not directly fetched; left blank"]
    ),
    E(
        "hand-den-ski-aal-12076", "Handball", "Danish Herreligaen", "h2h_3way",
        "Skive fH", "Aalborg Håndbold", "2026-10-24T13:00:00Z", "",
        "tour_calendar_verified",
        [("EHF Club Profile (Aalborg)", "https://ehfcl.eurohandball.com/men/2026-27/standings/")],
        "", "Reigning Danish champions & EHF CL Group C #2 (3-1-0)",
        0.130, 0.065, 6.5, "Goals", 60.5, "Goals", True,
        "Aalborg Håndbold", "medium",
        12076, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Skive_FH_vs_Aalborg_Handbold/20?event_id=12076",
        "Money Line", "Aalborg Handbold", "2/2 (100%)", False, []
    ),
    E(
        "hand-ehfw-bel-ltu-12108", "Handball", "Women's EHF EURO Qualification", "h2h_3way",
        "Belgium Women", "Lithuania Women", "2026-10-21T15:15:00Z", "",
        "tour_calendar_verified",
        [("EHF EURO Portal", "https://ehfeuro.eurohandball.com/")],
        "", "",
        0.460, 0.105, 0.5, "Goals", 55.5, "Goals", False,
        "Belgium Women", "low",
        12108, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Belgium_W_vs_Lithuania_W/20?event_id=12108",
        "Money Line", "Belgium (W)", "1/2 (50%)", False, []
    ),
    E(
        "hand-ehfw-est-kos-12110", "Handball", "Women's EHF EURO Qualification", "h2h_3way",
        "Estonia Women", "Kosovo Women", "2026-10-23T18:00:00Z", "",
        "tour_calendar_verified",
        [("EHF EURO Portal", "https://ehfeuro.eurohandball.com/")],
        "", "",
        0.395, 0.105, 1.5, "Goals", 53.5, "Goals", False,
        "Kosovo Women", "low",
        12110, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Estonia_W_vs_Kosovo_W/20?event_id=12110",
        "Money Line", "Kosovo (W)", "2/2 (100%)", False, []
    ),
    E(
        "hand-swe-ham-ali-12112", "Handball", "Swedish Handbollsligan", "h2h_3way",
        "Hammarby IF HF", "Alingsås HK", "2026-10-21T17:00:00Z", "Eriksdalshallen, Stockholm",
        "tour_calendar_verified",
        [("EHF National Federation Hub", "https://www.eurohandball.com/en/")],
        "", "",
        0.555, 0.110, -1.5, "Goals", 57.5, "Goals", True,
        "Hammarby IF HF", "low",
        12112, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Hammarby_IF_HF_vs_Alingsas_HK/20?event_id=12112",
        "Money Line", "Hammarby IF HF", "2/3 (67%)", False, []
    ),
    E(
        "hand-swe-mal-lug-12113", "Handball", "Swedish Handbollsligan", "h2h_3way",
        "HK Malmö", "LUGI HF", "2026-10-21T17:00:00Z", "Baltiska Hallen, Malmö",
        "tour_calendar_verified",
        [("EHF National Federation Hub", "https://www.eurohandball.com/en/")],
        "", "",
        0.595, 0.105, -2.5, "Goals", 56.5, "Goals", False,
        "HK Malmö", "low",
        12113, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/HK_Malmo_vs_Lugi_HF/20?event_id=12113",
        "Money Line", "HK Malmo", "1/2 (50%)", False, []
    ),
    E(
        "hand-swe-hal-sav-12114", "Handball", "Swedish Handbollsligan", "h2h_3way",
        "IF Hallby HK", "IK Sävehof", "2026-10-21T17:00:00Z", "Jönköpings Idrottshus, Jönköping",
        "tour_calendar_verified",
        [("EHF National Federation Hub", "https://www.eurohandball.com/en/")],
        "", "",
        0.340, 0.100, 3.0, "Goals", 58.5, "Goals", True,
        "IK Sävehof", "medium",
        12114, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/IF_Hallby_HK_vs_IK_Savehof/20?event_id=12114",
        "Money Line", "IK Savehof", "2/3 (67%)", False, []
    ),
    E(
        "hand-nor-san-run-12115", "Handball", "Norwegian REMA 1000-ligaen", "h2h_3way",
        "Sandefjord Håndball", "Runar Sandefjord", "2026-10-21T16:15:00Z", "Jotunhallen, Sandefjord",
        "tour_calendar_verified",
        [("EHF National Federation Hub", "https://www.eurohandball.com/en/")],
        "", "",
        0.320, 0.095, 3.5, "Goals", 59.5, "Goals", True,
        "Runar Sandefjord", "medium",
        12115, "https://www.olbg.com/betting-tips/Handball/All_Handball/All_Events/Sandefjord_vs_Runar/20?event_id=12115",
        "Money Line", "Runar", "4/5 (80%)", False, []
    ),

    # =========================================================================
    # 8. VOLLEYBALL (19 Live OLBG Matches — incl. +4 Newly Tipped Matches at 06:48Z!)
    # =========================================================================
    E(
        "vol-ger-ber-fre-36983", "Volleyball", "German 1. Volleyball Bundesliga Men", "h2h_2way",
        "BERLIN RECYCLING Volleys", "FT 1844 Freiburg", "2026-10-21T18:00:00Z", "Max-Schmeling-Halle, Berlin",
        "verified",
        [("1. Volleyball Bundesliga Official", "https://www.volleyball-bundesliga.de/")],
        "Reigning 10-time German champions & 18 Oct 2026 Ligacup winners (beat Giesen 3-2 in final)",
        "Mid-table 1. Bundesliga challenger visiting Max-Schmeling-Halle",
        0.875, 0.0, -2.5, "Sets", 3.5, "Sets", False,
        "BERLIN RECYCLING Volleys", "high",
        36983, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Berlin_Volleys_vs_FT_1844_Freiburg/21?event_id=36983",
        "Win Match", "Berlin Volleys", "2/2 (100%)", True,
        ["Newly tipped live OLBG fixture captured at 06:48Z; verified against official 1. Bundesliga opening week"]
    ),
    E(
        "vol-ger-net-gie-36984", "Volleyball", "German 1. Volleyball Bundesliga Men", "h2h_2way",
        "Netzhoppers KW-Bestensee", "Helios GRIZZLYS Giesen", "2026-10-21T17:00:00Z", "Landkost-Arena, Bestensee",
        "verified",
        [("1. Volleyball Bundesliga Official", "https://www.volleyball-bundesliga.de/")],
        "Lower-table 1. Bundesliga host",
        "18 Oct 2026 Ligacup silver medallists (took BR Volleys to 5 sets, 2-3)",
        0.215, 0.0, 1.5, "Sets", 3.5, "Sets", False,
        "Helios GRIZZLYS Giesen", "high",
        36984, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Netzhoppers_KW_vs_Helios_Grizzlys_Giesen/21?event_id=36984",
        "Win Match", "Helios Grizzlys Giesen", "1/1 (100%)", False, []
    ),
    E(
        "vol-ger-mun-fri-36985", "Volleyball", "German 1. Volleyball Bundesliga Men", "h2h_2way",
        "WWK Volleys Herrsching (München)", "VfB Friedrichshafen", "2026-10-21T17:30:00Z", "BMW Park, Munich",
        "verified",
        [("1. Volleyball Bundesliga Official", "https://www.volleyball-bundesliga.de/")],
        "Bavarian host",
        "18 Oct 2026 Ligacup bronze medallists (beat SVG Lüneburg 3-2 for 3rd)",
        0.340, 0.0, 1.5, "Sets", 3.5, "Sets", True,
        "VfB Friedrichshafen", "medium",
        36985, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/WWK_Volleys_Munchen_vs_VfB_Friedrichshafen/21?event_id=36985",
        "Win Match", "VfB Friedrichshafen", "1/1 (100%)", False, []
    ),
    E(
        "vol-ger-kar-lun-36986", "Volleyball", "German 1. Volleyball Bundesliga Men", "h2h_2way",
        "BADEN VOLLEYS SSC Karlsruhe", "SVG Lüneburg", "2026-10-21T18:00:00Z", "Lina-Radke-Halle, Karlsruhe",
        "verified",
        [("1. Volleyball Bundesliga Official", "https://www.volleyball-bundesliga.de/")],
        "Lower-half Bundesliga host",
        "Champions League semifinalists & Ligacup semi-finalists (lost 2-3 to Friedrichshafen on 18 Oct)",
        0.195, 0.0, 1.5, "Sets", 3.5, "Sets", False,
        "SVG Lüneburg", "high",
        36986, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/SSC_Karlsruhe_vs_SVG_Luneburg/21?event_id=36986",
        "Win Match", "SVG Luneburg", "1/1 (100%)", False, []
    ),
    E(
        "vol-ger-sch-erf-36945", "Volleyball", "German 1. Bundesliga Women", "h2h_2way",
        "SSC Palmberg Schwerin", "Schwarz-Weiß Erfurt", "2026-10-21T16:00:00Z", "PALMBERG ARENA, Schwerin",
        "verified",
        [("1. Volleyball Bundesliga Official", "https://www.volleyball-bundesliga.de/")],
        "Reigning German Women's champions", "Lower-tier Women's Bundesliga visitor",
        0.865, 0.0, -2.5, "Sets", 3.5, "Sets", False,
        "SSC Palmberg Schwerin", "medium",
        36945, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Schweriner_W_vs_Erfurt_W/21?event_id=36945",
        "Win Match", "Schweriner W", "3/3 (100%)", False, []
    ),
    # 5 Polish PlusLiga Matches
    E(
        "vol-pol-lub-gda-36961", "Volleyball", "Polish PlusLiga Men", "h2h_2way",
        "BOGDANKA LUK Lublin", "Trefl Gdańsk", "2026-10-21T15:30:00Z", "Hala Globus, Lublin",
        "verified",
        [("PlusLiga Official Portal", "https://www.plusliga.pl/")],
        "Reigning Polish PlusLiga champions", "Mid-table PlusLiga visitor",
        0.795, 0.0, -1.5, "Sets", 3.5, "Sets", False,
        "BOGDANKA LUK Lublin", "medium",
        36961, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/LUK_Lublin_vs_Trefl_Gdansk/21?event_id=36961",
        "Win Match", "LUK Lublin", "3/3 (100%)", False, []
    ),
    E(
        "vol-pol-zaw-zak-36962", "Volleyball", "Polish PlusLiga Men", "h2h_2way",
        "Aluron CMC Warta Zawiercie", "ZAKSA Kędzierzyn-Koźle", "2026-10-21T18:30:00Z", "Hala OSiR II, Zawiercie",
        "verified",
        [("PlusLiga Official Portal", "https://www.plusliga.pl/")],
        "CEV Champions League finalists", "Three-time European champions",
        0.665, 0.0, -1.5, "Sets", 3.5, "Sets", True,
        "Aluron CMC Warta Zawiercie", "medium",
        36962, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Warta_Zawiercie_vs_Kedzierzyn_Kozle/21?event_id=36962",
        "Win Match", "Warta Zawiercie", "1/1 (100%)", False, []
    ),
    E(
        "vol-pol-suw-kat-36963", "Volleyball", "Polish PlusLiga Men", "h2h_2way",
        "Ślepsk Malow Suwałki", "GKS Katowice", "2026-10-23T15:30:00Z", "Suwałki Arena, Suwałki",
        "verified",
        [("PlusLiga Official Portal", "https://www.plusliga.pl/")],
        "PlusLiga host", "PlusLiga visitor",
        0.695, 0.0, -1.5, "Sets", 3.5, "Sets", True,
        "Ślepsk Malow Suwałki", "medium",
        36963, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Slepsk_Suwalki_vs_GKS_Katowice/21?event_id=36963",
        "Win Match", "Slepsk Suwalki", "2/2 (100%)", False, []
    ),
    E(
        "vol-pol-bel-war-36964", "Volleyball", "Polish PlusLiga Men", "h2h_2way",
        "PGE GiEK Skra Bełchatów", "PGE Projekt Warszawa", "2026-10-24T16:00:00Z", "Hala Energia, Bełchatów",
        "verified",
        [("PlusLiga Official Portal", "https://www.plusliga.pl/")],
        "PlusLiga host", "Title contender visitor",
        0.345, 0.0, 1.5, "Sets", 3.5, "Sets", True,
        "PGE Projekt Warszawa", "medium",
        36964, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/PGE_Skra_Belchatow_vs_Projekt_Warszawa/21?event_id=36964",
        "Win Match", "Projekt Warszawa", "2/2 (100%)", False, []
    ),
    E(
        "vol-pol-che-rze-36965", "Volleyball", "Polish PlusLiga Men", "h2h_2way",
        "InPost ChKS Chełm", "Asseco Resovia Rzeszów", "2026-10-25T17:00:00Z", "Hala MOSiR, Chełm",
        "verified",
        [("PlusLiga Official Portal", "https://www.plusliga.pl/")],
        "Promoted host", "CEV Cup champions visitor",
        0.240, 0.0, 1.5, "Sets", 3.5, "Sets", False,
        "Asseco Resovia Rzeszów", "medium",
        36965, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/CHKS_Chelm_vs_Resovia_Rzeszow/21?event_id=36965",
        "Win Match", "Resovia Rzeszow", "2/2 (100%)", False, []
    ),
    # 4 Italian Serie A1 Women + Finnish + Dutch + Polish I/II Liga
    E(
        "vol-ita-ber-mil-36974", "Volleyball", "Italian Serie A1 Tigotà Women", "h2h_2way",
        "Volley Bergamo 1991", "Numia Vero Volley Milano", "2026-10-21T18:30:00Z", "ChorusLife Arena, Bergamo",
        "verified",
        [("Lega Pallavolo Serie A Femminile", "https://www.legavolleyfemminile.it/")],
        "Serie A1 host", "CEV Champions League super-club visitor",
        0.210, 0.0, 1.5, "Sets", 3.5, "Sets", False,
        "Numia Vero Volley Milano", "medium",
        36974, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Bergamo_W_vs_Milano_W/21?event_id=36974",
        "Win Match", "Milano W", "1/1 (100%)", False, []
    ),
    E(
        "vol-ita-nov-mar-36976", "Volleyball", "Italian Serie A1 Tigotà Women", "h2h_2way",
        "Igor Gorgonzola Novara", "Omag-MT San Giovanni in Marignano", "2026-10-21T18:30:00Z", "Pala Igor, Novara",
        "verified",
        [("Lega Pallavolo Serie A Femminile", "https://www.legavolleyfemminile.it/")],
        "Top-4 Serie A1 contender", "Promoted Serie A1 newcomer",
        0.845, 0.0, -2.5, "Sets", 3.5, "Sets", False,
        "Igor Gorgonzola Novara", "medium",
        36976, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Novara_W_vs_Marignano_W/21?event_id=36976",
        "Win Match", "Novara W", "1/1 (100%)", False, []
    ),
    E(
        "vol-ita-val-cun-36977", "Volleyball", "Italian Serie A1 Tigotà Women", "h2h_2way",
        "Megabox Ond. Savio Vallefoglia", "Honda Olivero Cuneo", "2026-10-21T18:30:00Z", "PalaMegabox, Pesaro",
        "verified",
        [("Lega Pallavolo Serie A Femminile", "https://www.legavolleyfemminile.it/")],
        "Playoff quarter-finalist host", "Serie A1 visitor",
        0.655, 0.0, -1.5, "Sets", 3.5, "Sets", True,
        "Megabox Ond. Savio Vallefoglia", "low",
        36977, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Vallefoglia_W_vs_Cuneo_W/21?event_id=36977",
        "Set Score", "Cuneo W 3-0", "1/1 (100%)", False, []
    ),
    E(
        "vol-fin-pui-orp-36981", "Volleyball", "Finnish Mestaruusliiga Women", "h2h_2way",
        "Puijo Wolley", "Oriveden Ponnistus (OrPo)", "2026-10-21T14:00:00Z", "Kuopio",
        "tour_calendar_verified",
        [("CEV National Leagues", "https://www.cev.eu/")],
        "", "",
        0.680, 0.0, -1.5, "Sets", 3.5, "Sets", False,
        "Puijo Wolley", "low",
        36981, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Puijo_W_vs_Orpo_W/21?event_id=36981",
        "Win Match", "Puijo W", "3/3 (100%)", False, []
    ),
    E(
        "vol-ned-sne-utr-36968", "Volleyball", "Dutch Eredivisie Women", "h2h_2way",
        "Friso Sneek", " Booleans / VV Utrecht", "2026-10-21T18:00:00Z", "Sneker Sporthal, Sneek",
        "tour_calendar_verified",
        [("CEV National Leagues", "https://www.cev.eu/")],
        "", "",
        0.640, 0.0, -1.5, "Sets", 3.5, "Sets", True,
        "Friso Sneek", "low",
        36968, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/VC_Sneek_W_vs_VV_Utrecht_W/21?event_id=36968",
        "Win Match", "VC Sneek W", "1/1 (100%)", False, []
    ),
    E(
        "vol-pol1-jel-nys-36979", "Volleyball", "Polish PLS 1. Liga Men", "h2h_2way",
        "IM Rekord Volley Jelcz-Laskowice", "PSG Stal Nysa", "2026-10-21T16:00:00Z", "Jelcz-Laskowice",
        "tour_calendar_verified",
        [("PLS / PlusLiga Portal", "https://www.plusliga.pl/")],
        "", "",
        0.260, 0.0, 1.5, "Sets", 3.5, "Sets", False,
        "PSG Stal Nysa", "low",
        36979, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Jelcz_Laskowice_vs_Stal_Nysa/21?event_id=36979",
        "Win Match", "Stal Nysa", "1/1 (100%)", False, []
    ),
    E(
        "vol-pol1-gwa-bed-36980", "Volleyball", "Polish PLS 1. Liga Men", "h2h_2way",
        "Gwardia Wrocław", "Nowak-Mosty MKS Będzin", "2026-10-21T16:00:00Z", "Wrocław",
        "tour_calendar_verified",
        [("PLS / PlusLiga Portal", "https://www.plusliga.pl/")],
        "", "",
        0.350, 0.0, 1.5, "Sets", 3.5, "Sets", True,
        "Nowak-Mosty MKS Będzin", "low",
        36980, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Gwardia_Wroclaw_vs_MKS_Bedzin/21?event_id=36980",
        "Win Match", "MKS Bedzin", "1/1 (100%)", True, ["Newly tipped live OLBG fixture captured at 06:48Z"]
    ),
    E(
        "vol-pol1-bel-rad-36982", "Volleyball", "Polish PLS 1. Liga / Cup Men", "h2h_2way",
        "SPS Chrobry / Belsk Duży", "Enea Czarni Radom", "2026-10-21T17:00:00Z", "",
        "unverified",
        [("PZPS Polish Volleyball Federation", "https://www.pzps.pl/")],
        "", "",
        0.380, 0.0, 1.5, "Sets", 3.5, "Sets", True,
        "Enea Czarni Radom", "low",
        36982, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/Belsk_Duzy_vs_Czarni_Radom/21?event_id=36982",
        "Win Match", "Czarni Radom", "1/1 (100%)", True,
        ["Newly tipped lower-tier tie on OLBG at 06:48Z; official lower-division match sheet unconfirmed so venue & standings left blank"]
    ),
    E(
        "vol-pol2-szc-sed-36988", "Volleyball", "Polish Lower-Division Women", "h2h_2way",
        "SMS PZPS Szczyrk II W", "Marba Sędziszów Małopolski W", "", "",
        "unverified",
        [("PZPS Polish Volleyball Federation", "https://www.pzps.pl/")],
        "", "",
        0.520, 0.0, -0.5, "Sets", 3.5, "Sets", True,
        "SMS PZPS Szczyrk II W", "low",
        36988, "https://www.olbg.com/betting-tips/Volleyball/All_Volleyball/All_Events/SMS_PZPS_Szczyrk_II_W_vs_Marba_Sedziszow_Malopolski_W/21?event_id=36988",
        "Win Match", "SMS PZPS Szczyrk II W", "1/1 (100%)", True,
        ["Newly tipped lower-division women's fixture on OLBG; flagged unverified with venue/UTC/standings blank"]
    ),

    # =========================================================================
    # 9. CRICKET (14 Live OLBG Events: 9 Matches + 5 Major Tournament Outrights)
    # Note: Every single match has Winner + Handicap + Total originated (closes Audit C!)
    # =========================================================================
    E(
        "cric-afg-ban-188824", "Cricket", "UAE Men's ODI Tri-Nation Series — Match #274658 (50 Overs)", "h2h_2way",
        "Afghanistan", "Bangladesh", "2026-10-21T11:30:00Z", "Sharjah Cricket Stadium, Sharjah",
        "verified",
        [("ICC Match Center #274658", "https://www.icc-cricket.com/matches/274658/afghanistan-vs-bangladesh"),
         ("ICC Team Rankings", "https://www.icc-cricket.com/rankings")],
        "ICC ODI #8 (92 rating; swept Bangladesh 3-0 in UAE ODI series)",
        "ICC ODI #9 (83 rating)",
        0.655, 0.0, -18.5, "Runs/Eq", 489.5, "Runs", False,
        "Afghanistan", "high",
        188824, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Afghanistan_vs_Bangladesh_One_Day_Match/7?event_id=188824",
        "Win Match", "Afghanistan", "7/7 (100%)", False,
        ["Resolved session 2360a617 venue conflict ('Sharjah vs Abu Dhabi'): official icc-cricket.com match #274658 confirms Sharjah Cricket Stadium at 11:30 UTC"]
    ),
    E(
        "cric-nzl-ind-188814", "Cricket", "India Tour of New Zealand — 1st Men's T20I (Match #271646)", "h2h_2way",
        "New Zealand", "India", "2026-10-22T07:00:00Z", "Hagley Oval, Christchurch",
        "verified",
        [("ICC Match Center #271646", "https://www.icc-cricket.com/matches/271646/new-zealand-vs-india"),
         ("NZC Official Fixtures", "https://scoring.nzc.nz/fixtures")],
        "ICC Men's T20I #4 (247 rating)",
        "ICC Men's T20I #1 (268 rating; reigning 2026 T20 World Cup champions)",
        0.345, 0.0, 9.5, "Runs/Eq", 342.5, "Runs", True,
        "India", "high",
        188814, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/New_Zealand_vs_India_1st_T20_Match/7?event_id=188814",
        "Win Match", "India", "5/7 (71%)", False,
        ["Prior repo data/fixtures.json listed start as 06:15Z and India as #2 (267); official icc-cricket.com has 07:00Z and India #1 (268)"]
    ),
    E(
        "cric-ausw-nzw-188826", "Cricket", "Trans-Tasman Women's T20I Series — 3rd T20I", "h2h_2way",
        "Australia Women", "New Zealand Women", "2026-10-22T08:15:00Z", "North Sydney Oval, Sydney",
        "verified",
        [("NZC Official Match Center", "https://scoring.nzc.nz/fixtures"),
         ("ICC Women's T20I Rankings", "https://www.icc-cricket.com/rankings")],
        "ICC Women's T20I #1 (287 rating)",
        "ICC Women's T20I #4 (253 rating)",
        0.775, 0.0, -16.5, "Runs/Eq", 309.5, "Runs", True,
        "Australia Women", "high",
        188826, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Australia_W_vs_New_Zealand_W_3rd_T20_Match/7?event_id=188826",
        "Win Match", "Australia W", "1/2 (50%)", False,
        ["Major venue error caught in prior data/predictions.json [21]: 3rd T20I is at North Sydney Oval, Sydney (scoring.nzc.nz), NOT Manuka Oval, Canberra!"]
    ),
    E(
        "cric-nam-ire-188828", "Cricket", "Ireland Tour / Bilateral Men's 1st ODI (50 Overs)", "h2h_2way",
        "Namibia", "Ireland", "2026-10-22T08:00:00Z", "",
        "tour_calendar_verified",
        [("ICC Men's ODI Rankings", "https://www.icc-cricket.com/rankings")],
        "ICC Men's ODI #17 (31 rating)",
        "ICC Men's ODI #12 (51 rating; Full Member)",
        0.340, 0.0, 22.5, "Runs/Eq", 469.5, "Runs", False,
        "Ireland", "medium",
        188828, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Namibia_vs_Ireland_1st_ODI/7?event_id=188828",
        "Win Match", "Ireland", "3/3 (100%)", False,
        ["Exact ground left blank pending final ICC match card"]
    ),
    E(
        "cric-eng-slk-188829", "Cricket", "England vs Sri Lanka One-Day International (50 Overs)", "h2h_2way",
        "Sri Lanka", "England", "2026-10-22T08:30:00Z", "",
        "tour_calendar_verified",
        [("ICC Men's ODI Rankings", "https://www.icc-cricket.com/rankings")],
        "Subcontinent home ODI conditions advantage",
        "Visiting England ODI squad",
        0.515, 0.0, -3.5, "Runs/Eq", 514.5, "Runs", True,
        "Sri Lanka", "low",
        188829, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/England_vs_Sri_Lanka_One_Day_Match/7?event_id=188829",
        "Win Match", "England", "1/2 (50%)", False, []
    ),
    E(
        "cric-csa-nch-grb-188823", "Cricket", "CSA Provincial T20 Knock-Out (South Africa)", "h2h_2way",
        "Northern Cape Heat", "Garden Route Badgers", "2026-10-21T11:00:00Z", "",
        "unverified",
        [("Cricket South Africa Official", "https://cricket.co.za/")],
        "", "",
        0.475, 0.0, 2.5, "Runs/Eq", 309.5, "Runs", False,
        "Garden Route Badgers", "low",
        188823, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Northern_Cape_Heat_vs_Garden_Route_Badgers_T20/7?event_id=188823",
        "Win Match", "Garden Route Badgers", "5/8 (63%)", False,
        ["CSA Division 2 T20 fixture sheet not directly fetched on cricket.co.za; flagged unverified with stats/venue blank"]
    ),
    E(
        "cric-csa-nwd-lim-188810", "Cricket", "CSA Provincial T20 Challenge (South Africa)", "h2h_2way",
        "North West Dragons", "Limpopo Impalas", "2026-10-21T16:00:00Z", "",
        "unverified",
        [("Cricket South Africa Official", "https://cricket.co.za/")],
        "", "",
        0.660, 0.0, -12.5, "Runs/Eq", 319.5, "Runs", True,
        "North West Dragons", "low",
        188810, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/North_West_Dragons_vs_Limpopo_Impalas_T20/7?event_id=188810",
        "Win Match", "North West Dragons", "5/6 (83%)", False,
        ["CSA domestic T20 standings unconfirmed online; stats & ground left blank"]
    ),
    E(
        "cric-csa-est-tus-188811", "Cricket", "CSA Provincial T20 Knock-Out (South Africa)", "h2h_2way",
        "Eastern Storm", "Tuskers", "2026-10-22T16:00:00Z", "",
        "unverified",
        [("Cricket South Africa Official", "https://cricket.co.za/")],
        "", "",
        0.555, 0.0, -4.5, "Runs/Eq", 312.5, "Runs", False,
        "Eastern Storm", "low",
        188811, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Eastern_Storm_vs_Tuskers_T20/7?event_id=188811",
        "Win Match", "Eastern Storm", "4/4 (100%)", False,
        ["CSA domestic T20 standings unconfirmed online; stats & ground left blank"]
    ),
    E(
        "cric-csa-mpu-sae-188825", "Cricket", "CSA Provincial T20 Knock-Out (South Africa)", "h2h_2way",
        "Mpumalanga Rhinos", "South Africa Emerging", "2026-10-22T11:00:00Z", "",
        "unverified",
        [("Cricket South Africa Official", "https://cricket.co.za/")],
        "", "",
        0.385, 0.0, 9.5, "Runs/Eq", 308.5, "Runs", False,
        "South Africa Emerging", "low",
        188825, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Mpumalanga_Rhinos_vs_South_Africa_Emerging_T20/7?event_id=188825",
        "Win Match", "South Africa Emerging", "1/2 (50%)", False,
        ["CSA domestic T20 standings unconfirmed online; stats & ground left blank"]
    ),
    # 5 Cricket Tournament Outrights on OLBG
    E(
        "cric-out-cwc27-182606", "Cricket", "ICC Men's Cricket World Cup 2027 — Outright", "outright",
        "India (2027 ODI World Cup Outright)", "The Field (13 Nations)", "2027-11-21T09:00:00Z", "South Africa / Zimbabwe / Namibia",
        "verified",
        [("ICC Men's ODI Rankings", "https://www.icc-cricket.com/rankings")],
        "#1 ICC ODI Nation", "Australia, South Africa, New Zealand, England & Field",
        0.285, 0.0, 0.0, "Outright", None, "", False,
        "India (Outright)", "medium",
        182606, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/World_Cup_2027/7?event_id=182606",
        "Outright Winner", "India", "6/12 (50%)", False, []
    ),
    E(
        "cric-out-wbbl26-187184", "Cricket", "Weber WBBL|12 (2026) — Outright Winner", "outright",
        "Sydney Sixers Women (Outright)", "The Field (7 Franchises)", "2026-12-05T08:10:00Z", "Australia",
        "tour_calendar_verified",
        [("Cricket Australia / ICC", "https://www.icc-cricket.com/")],
        "WBBL franchise contender", "7 rival WBBL clubs",
        0.195, 0.0, 0.0, "Outright", None, "", False,
        "Sydney Sixers Women (Outright)", "low",
        187184, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/Big_Bash_Women_2026/7?event_id=187184",
        "Outright Winner", "Sydney Sixers W", "2/3 (67%)", False, []
    ),
    E(
        "cric-out-bbl2627-187503", "Cricket", "KFC Big Bash League 2026-27 — Outright Winner", "outright",
        "Perth Scorchers / Brisbane Heat Co-Favs (Adelaide Strikers OLBG Lead)", "The Field (7 Franchises)", "2026-12-12T08:15:00Z", "Australia",
        "tour_calendar_verified",
        [("ICC / Australian Domestic Calendar", "https://www.icc-cricket.com/")],
        "8-team BBL|16 field", "7 rival BBL clubs",
        0.175, 0.0, 0.0, "Outright", None, "", False,
        "Perth Scorchers / Field Leader", "low",
        187503, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/T20_Big_Bash_2026-27/7?event_id=187503",
        "Outright Winner", "Adelaide Strikers", "1/2 (50%)", False, []
    ),
    E(
        "cric-out-sa20-187504", "Cricket", "Betway SA20 2026-27 — Outright Winner", "outright",
        "Sunrisers Eastern Cape / MI Cape Town (Pretoria Capitals OLBG Lead)", "The Field (5 Franchises)", "2027-01-24T15:30:00Z", "South Africa",
        "tour_calendar_verified",
        [("Cricket South Africa Official", "https://cricket.co.za/")],
        "6-team SA20 franchise field", "5 rival SA20 clubs",
        0.225, 0.0, 0.0, "Outright", None, "", False,
        "Sunrisers Eastern Cape (Outright)", "low",
        187504, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/SA20_2026-27/7?event_id=187504",
        "Outright Winner", "Pretoria Capitals", "1/1 (100%)", False, []
    ),
    E(
        "cric-out-blast27-188350", "Cricket", "Vitality T20 Blast 2027 — Outright Winner", "outright",
        "Surrey / Somerset (Sussex EW OLBG Lead)", "The Field (17 Counties)", "2027-07-18T15:00:00Z", "England & Wales",
        "tour_calendar_verified",
        [("ICC / ECB Calendar Context", "https://www.icc-cricket.com/")],
        "18-county Vitality Blast field", "17 rival counties",
        0.140, 0.0, 0.0, "Outright", None, "", False,
        "Surrey (Outright)", "low",
        188350, "https://www.olbg.com/betting-tips/Cricket/All_Cricket/All_Events/T20_Blast_2027/7?event_id=188350",
        "Outright Winner", "Sussex", "0/0 Win Tips (EW only bug!)", False,
        ["Upstream OLBG bug BUG-OLBG-EW-DIVZERO: displays '0 / 0 Win Tips' (0%) when tipsters place Each-Way-only tips"]
    ),

    # =========================================================================
    # 10. RUGBY UNION (16 Live OLBG Events: 3 Top 14, 4 URC, 8 Pro D2, 1 Six Nations Outright)
    # =========================================================================
    E(
        "ru-top14-tlse-perp-609567", "Rugby Union", "French Top 14 — Round 7 (J7)", "h2h_3way",
        "Stade Toulousain", "USA Perpignan", "2026-10-24T14:35:00Z", "Stade Ernest-Wallon, Toulouse",
        "verified",
        [("LNR Top 14 Official Calendar & Standings", "https://top14.lnr.fr/calendrier-et-resultats")],
        "1st in Top 14 (24 pts after J6; beat Aviron Bayonnais 45-34)",
        "9th in Top 14 (13 pts after J6)",
        0.870, 0.025, -18.5, "Points", 54.5, "Points", True,
        "Stade Toulousain", "high",
        609567, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Toulouse_v_Perpignan/9?event_id=609567",
        "Handicap", "Perpignan +23.50", "1/1 (100%)", False, []
    ),
    E(
        "ru-top14-bay-lyon-609564", "Rugby Union", "French Top 14 — Round 7 (J7)", "h2h_3way",
        "Aviron Bayonnais", "LOU Rugby (Lyon)", "2026-10-24T14:35:00Z", "Stade Jean-Dauger, Bayonne",
        "verified",
        [("LNR Top 14 Official Calendar & Standings", "https://top14.lnr.fr/calendrier-et-resultats")],
        "5th in Top 14 (17 pts; scored 34 away at Toulouse in J6)",
        "8th in Top 14 (14 pts; lost 16-28 home to La Rochelle in J6)",
        0.745, 0.035, -8.5, "Points", 49.5, "Points", True,
        "Aviron Bayonnais", "high",
        609564, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Bayonne_v_Lyon/9?event_id=609564",
        "Handicap", "Lyon +10.50", "1/1 (100%)", False, []
    ),
    E(
        "ru-top14-lar-ubb-609554", "Rugby Union", "French Top 14 — Round 7 (J7)", "h2h_3way",
        "Stade Rochelais", "Union Bordeaux-Bègles", "2026-10-25T20:05:00Z", "Stade Marcel-Deflandre, La Rochelle",
        "verified",
        [("LNR Top 14 Official Calendar & Standings", "https://top14.lnr.fr/calendrier-et-resultats")],
        "4th in Top 14 (18 pts; won 28-16 away at Lyon in J6)",
        "3rd in Top 14 (19 pts)",
        0.605, 0.045, -3.5, "Points", 46.5, "Points", False,
        "Stade Rochelais", "medium",
        609554, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/La_Rochelle_v_Bordeaux/9?event_id=609554",
        "To Win", "La Rochelle", "1/2 (50%)", False, []
    ),
    # 4 URC Round 4 Matches
    E(
        "ru-urc-con-zeb-609577", "Rugby Union", "United Rugby Championship — Round 4", "h2h_3way",
        "Connacht Rugby", "Zebre Parma", "2026-10-23T18:45:00Z", "Dexcom Stadium, Galway",
        "verified",
        [("URC Official Match Centre", "https://www.unitedrugby.com/match-centre")],
        "Irish province hosting in Galway", "Italian URC visitor",
        0.790, 0.030, -11.5, "Points", 48.5, "Points", True,
        "Connacht Rugby", "medium",
        609577, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Connacht_v_Zebre_Parma/9?event_id=609577",
        "To Win", "Connacht", "3/5 (60%)", False, []
    ),
    E(
        "ru-urc-bul-uls-609576", "Rugby Union", "United Rugby Championship — Round 4", "h2h_3way",
        "Vodacom Bulls", "Ulster Rugby", "2026-10-24T11:45:00Z", "Loftus Versfeld, Pretoria",
        "verified",
        [("URC Official Match Centre", "https://www.unitedrugby.com/match-centre")],
        "Highveld altitude fortress at Loftus Versfeld", "Touring Irish province",
        0.785, 0.030, -11.5, "Points", 52.5, "Points", True,
        "Vodacom Bulls", "medium",
        609576, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Bulls_v_Ulster/9?event_id=609576",
        "Handicap", "Ulster +18.50", "2/2 (100%)", False, []
    ),
    E(
        "ru-urc-sto-sca-609580", "Rugby Union", "United Rugby Championship — Round 4", "h2h_3way",
        "DHL Stormers", "Scarlets", "2026-10-24T14:00:00Z", "DHL Stadium, Cape Town",
        "verified",
        [("URC Official Match Centre", "https://www.unitedrugby.com/match-centre")],
        "Former URC champions in Cape Town", "Touring Welsh region",
        0.825, 0.025, -14.5, "Points", 50.5, "Points", True,
        "DHL Stormers", "medium",
        609580, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Stormers_v_Scarlets/9?event_id=609580",
        "To Win", "Stormers", "1/2 (50%)", False, []
    ),
    E(
        "ru-urc-lei-mun-609578", "Rugby Union", "United Rugby Championship — Round 4", "h2h_3way",
        "Leinster Rugby", "Munster Rugby", "2026-10-24T17:00:00Z", "Croke Park / Aviva Stadium, Dublin",
        "verified",
        [("URC Official Match Centre", "https://www.unitedrugby.com/match-centre")],
        "Irish interprovincial hosts", "Reigning derby rivals",
        0.740, 0.035, -8.5, "Points", 45.5, "Points", False,
        "Leinster Rugby", "medium",
        609578, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Leinster_v_Munster/9?event_id=609578",
        "To Win", "Leinster", "1/1 (100%)", False, []
    ),
    # 8 French Pro D2 Round 8 Matches
    E(
        "ru-prod2-mon-oyo-609556", "Rugby Union", "French Pro D2 — Round 8", "h2h_3way",
        "US Montauban", "Oyonnax Rugby", "2026-10-22T19:00:00Z", "Stade Sapiac, Montauban",
        "tour_calendar_verified",
        [("LNR Pro D2 Official Calendar", "https://prod2.lnr.fr/calendrier-et-resultats")],
        "", "",
        0.445, 0.045, 2.0, "Points", 46.5, "Points", False,
        "Oyonnax Rugby", "low",
        609556, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Montauban_v_Oyonnax/9?event_id=609556",
        "To Win", "Oyonnax", "5/7 (71%)", False,
        ["Pro D2 Round 8 schedule verified on prod2.lnr.fr; exact J7 club points left blank"]
    ),
    E(
        "ru-prod2-nar-bri-609557", "Rugby Union", "French Pro D2 — Round 8", "h2h_3way",
        "RC Narbonne", "CA Brive", "2026-10-23T17:00:00Z", "Parc des Sports et de l'Amitié, Narbonne",
        "tour_calendar_verified",
        [("LNR Pro D2 Official Calendar", "https://prod2.lnr.fr/calendrier-et-resultats")],
        "", "",
        0.415, 0.045, 3.5, "Points", 45.5, "Points", False,
        "CA Brive", "low",
        609557, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Narbonne_v_Brive/9?event_id=609557",
        "To Win", "Narbonne", "2/2 (100%)", False, []
    ),
    E(
        "ru-prod2-age-nic-609558", "Rugby Union", "French Pro D2 — Round 8", "h2h_3way",
        "SU Agen", "Stade Niçois (Nice)", "2026-10-23T17:30:00Z", "Stade Armandie, Agen",
        "tour_calendar_verified",
        [("LNR Pro D2 Official Calendar", "https://prod2.lnr.fr/calendrier-et-resultats")],
        "", "",
        0.640, 0.040, -5.5, "Points", 46.5, "Points", True,
        "SU Agen", "low",
        609558, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Agen_v_Nissa/9?event_id=609558",
        "To Win", "Nissa", "3/4 (75%)", False, []
    ),
    E(
        "ru-prod2-val-col-609559", "Rugby Union", "French Pro D2 — Round 8", "h2h_3way",
        "Valence Romans Drôme", "Colomiers Rugby", "2026-10-23T17:30:00Z", "Stade Georges-Pompidou, Valence",
        "tour_calendar_verified",
        [("LNR Pro D2 Official Calendar", "https://prod2.lnr.fr/calendrier-et-resultats")],
        "", "",
        0.480, 0.045, 1.0, "Points", 47.5, "Points", True,
        "Colomiers Rugby", "low",
        609559, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Valence_Romans_v_Colomiers/9?event_id=609559",
        "To Win", "Colomiers", "1/1 (100%)", False, []
    ),
    E(
        "ru-prod2-aur-nev-609560", "Rugby Union", "French Pro D2 — Round 8", "h2h_3way",
        "Stade Aurillacois", "USON Nevers", "2026-10-23T17:30:00Z", "Stade Jean-Alric, Aurillac",
        "tour_calendar_verified",
        [("LNR Pro D2 Official Calendar", "https://prod2.lnr.fr/calendrier-et-resultats")],
        "", "",
        0.545, 0.045, -2.0, "Points", 44.5, "Points", False,
        "Stade Aurillacois", "low",
        609560, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Aurillac_v_Nevers/9?event_id=609560",
        "To Win", "Nevers", "2/4 (50%)", False, []
    ),
    E(
        "ru-prod2-gre-bia-609561", "Rugby Union", "French Pro D2 — Round 8", "h2h_3way",
        "FC Grenoble Rugby", "Biarritz Olympique", "2026-10-23T19:00:00Z", "Stade des Alpes, Grenoble",
        "tour_calendar_verified",
        [("LNR Pro D2 Official Calendar", "https://prod2.lnr.fr/calendrier-et-resultats")],
        "", "",
        0.735, 0.035, -9.5, "Points", 48.5, "Points", True,
        "FC Grenoble Rugby", "medium",
        609561, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Grenoble_v_Biarritz/9?event_id=609561",
        "Handicap", "Biarritz +11.50", "1/1 (100%)", False, []
    ),
    E(
        "ru-prod2-pro-bez-609562", "Rugby Union", "French Pro D2 — Round 8", "h2h_3way",
        "Provence Rugby", "AS Béziers Hérault", "2026-10-23T19:00:00Z", "Stade Maurice-David, Aix-en-Provence",
        "tour_calendar_verified",
        [("LNR Pro D2 Official Calendar", "https://prod2.lnr.fr/calendrier-et-resultats")],
        "", "",
        0.720, 0.035, -8.5, "Points", 47.5, "Points", True,
        "Provence Rugby", "medium",
        609562, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Provence_v_Beziers/9?event_id=609562",
        "Handicap", "Beziers +28.50", "1/1 (100%)", False, []
    ),
    E(
        "ru-prod2-sax-dax-609563", "Rugby Union", "French Pro D2 — Round 8", "h2h_3way",
        "Soyaux-Angoulême XV", "US Dax", "2026-10-23T17:30:00Z", "Stade Chanzy, Angoulême",
        "tour_calendar_verified",
        [("LNR Pro D2 Official Calendar", "https://prod2.lnr.fr/calendrier-et-resultats")],
        "", "",
        0.535, 0.045, -1.5, "Points", 44.5, "Points", False,
        "Soyaux-Angoulême XV", "low",
        609563, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Soyaux_Angouleme_v_Dax/9?event_id=609563",
        "To Win", "Dax", "3/3 (100%)", False, []
    ),
    E(
        "ru-out-sixnations-609013", "Rugby Union", "2027 Men's Six Nations Championship — Outright", "outright",
        "France (2027 Six Nations Outright)", "The Field (Ireland, England, Scotland, Wales, Italy)", "2027-03-14T20:00:00Z", "Europe",
        "verified",
        [("Six Nations Official Portal", "https://www.sixnationsrugby.com/")],
        "Hosts Ireland & England in 2027 rotation", "5 rival Six Nations unions",
        0.415, 0.0, 0.0, "Outright", None, "", False,
        "France (Outright)", "medium",
        609013, "https://www.olbg.com/betting-tips/Rugby_Union/All_Rugby_Union/All_Events/Six_Nations_2027/9?event_id=609013",
        "Win Tournament", "France", "3/9 (33%)", False, []
    ),

    # =========================================================================
    # 11. RUGBY LEAGUE (10 Events: 3 Live OLBG 2027 Outrights + 7 Active RLWC26 R2 Matches)
    # =========================================================================
    E(
        "rl-out-origin-2695857", "Rugby League", "2027 Ampol State of Origin Series — Outright", "outright",
        "New South Wales Blues", "Queensland Maroons", "2027-05-27T10:00:00Z", "Australia",
        "verified",
        [("NRL Official Portal", "https://www.nrl.com/")],
        "Series favourite", "Queensland Maroons",
        0.545, 0.0, 0.0, "Outright", None, "", False,
        "New South Wales Blues", "low",
        2695857, "https://www.olbg.com/betting-tips/Rugby_League/All_Rugby_League/All_Events/State_of_Origin_2027/10?event_id=2695857",
        "Win Tournament", "New South Wales", "9/12 (75%)", False, []
    ),
    E(
        "rl-out-nrl27-2801600", "Rugby League", "2027 NRL Telstra Premiership — Grand Final Winner", "outright",
        "Melbourne Storm / Penrith Panthers", "The Field (15 NRL Clubs)", "2027-10-03T08:30:00Z", "Accor Stadium, Sydney",
        "verified",
        [("NRL Official Portal", "https://www.nrl.com/")],
        "Perennial NRL premiership benchmark", "16-club NRL field",
        0.215, 0.0, 0.0, "Outright", None, "", False,
        "Penrith Panthers / Melbourne Storm", "low",
        2801600, "https://www.olbg.com/betting-tips/Rugby_League/All_Rugby_League/All_Events/NRL_2027/10?event_id=2801600",
        "Grand Final Winner", "Penrith Panthers", "1/1 (100%)", False, []
    ),
    E(
        "rl-out-sl27-2801554", "Rugby League", "2027 Betfred Super League — Grand Final Winner", "outright",
        "Wigan Warriors", "The Field (11 Super League Clubs)", "2027-10-02T17:00:00Z", "Old Trafford, Manchester",
        "verified",
        [("Super League Official Portal", "https://www.superleague.co.uk/")],
        "Dominant Super League benchmark", "Leeds Rhinos, Hull KR, St Helens & Field",
        0.340, 0.0, 0.0, "Outright", None, "", False,
        "Wigan Warriors (Outright)", "medium",
        2801554, "https://www.olbg.com/betting-tips/Rugby_League/All_Rugby_League/All_Events/Super_League_2027/10?event_id=2801554",
        "Grand Final Winner", "Leeds Rhinos", "1/3 (33%)", False, []
    ),
    # 7 Official Active RLWC26 Round 2 Fixtures (OLBG Zero-Tip Match Blind Spot!)
    E(
        "rl-wc26-aus-fij", "Rugby League", "2026 Rugby League World Cup Men — Round 2", "h2h_3way",
        "Australia Kangaroos", "Fiji Bati", "2026-10-25T09:05:00Z", "Suncorp Stadium, Brisbane",
        "verified",
        [("NRL / RLWC26 Official Draw", "https://www.nrl.com/draw/?competition=175&round=2&season=2026")],
        "IRL #1 (beat New Zealand 24-22 in Round 1 opener)",
        "IRL #7",
        0.880, 0.020, -18.5, "Points", 48.5, "Points", True,
        "Australia Kangaroos", "high",
        None, "https://www.olbg.com/betting-tips/Rugby_League/10",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False,
        ["Active RLWC26 Round 2 match verified on nrl.com; OLBG Rugby League hub displays 0 match markets"]
    ),
    E(
        "rl-wc26-nzl-cok", "Rugby League", "2026 Rugby League World Cup Men — Round 2", "h2h_3way",
        "New Zealand Kiwis", "Cook Islands Aitu", "2026-10-25T05:05:00Z", "One New Zealand Stadium, Christchurch",
        "verified",
        [("NRL / RLWC26 Official Draw", "https://www.nrl.com/draw/?competition=175&round=2&season=2026")],
        "IRL #2 (narrow 22-24 loss to Australia in Round 1)",
        "IRL #9",
        0.885, 0.015, -20.5, "Points", 50.5, "Points", True,
        "New Zealand Kiwis", "high",
        None, "https://www.olbg.com/betting-tips/Rugby_League/10",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False,
        ["Active RLWC26 Round 2 match verified on nrl.com; unlisted on OLBG"]
    ),
    E(
        "rl-wc26-eng-fra", "Rugby League", "2026 Rugby League World Cup Men — Round 2", "h2h_3way",
        "England", "France", "2026-10-24T06:35:00Z", "HBF Park, Perth",
        "verified",
        [("NRL / RLWC26 Official Draw", "https://www.nrl.com/draw/?competition=175&round=2&season=2026")],
        "IRL #3",
        "IRL #8 (lost 4-78 to Samoa in Round 1)",
        0.875, 0.020, -22.5, "Points", 52.5, "Points", True,
        "England", "high",
        None, "https://www.olbg.com/betting-tips/Rugby_League/10",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False,
        ["Active RLWC26 Round 2 match verified on nrl.com; unlisted on OLBG"]
    ),
    E(
        "rl-wc26-png-sam", "Rugby League", "2026 Rugby League World Cup Men — Round 2", "h2h_3way",
        "Papua New Guinea Kumuls", "Toa Samoa", "2026-10-24T04:25:00Z", "Santos National Football Stadium, Port Moresby",
        "verified",
        [("NRL / RLWC26 Official Draw", "https://www.nrl.com/draw/?competition=175&round=2&season=2026")],
        "IRL #6 hosting in Port Moresby",
        "IRL #4 (crushed France 78-4 in Round 1)",
        0.340, 0.030, 8.5, "Points", 46.5, "Points", True,
        "Toa Samoa", "medium",
        None, "https://www.olbg.com/betting-tips/Rugby_League/10",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False, []
    ),
    E(
        "rl-wc26-tga-lbn", "Rugby League", "2026 Rugby League World Cup Men — Round 2", "h2h_3way",
        "Tonga XIII", "Lebanon Cedars", "2026-10-23T09:05:00Z", "CommBank Stadium, Sydney",
        "verified",
        [("NRL / RLWC26 Official Draw", "https://www.nrl.com/draw/?competition=175&round=2&season=2026")],
        "IRL #5 NRL-packed forward unit",
        "IRL #11",
        0.855, 0.020, -18.5, "Points", 48.5, "Points", True,
        "Tonga XIII", "medium",
        None, "https://www.olbg.com/betting-tips/Rugby_League/10",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False, []
    ),
    E(
        "rl-wc26w-aus-eng", "Rugby League", "2026 Women's Rugby League World Cup — Round 2", "h2h_3way",
        "Australia Jillaroos", "England Women", "2026-10-24T09:05:00Z", "HBF Park, Perth",
        "verified",
        [("NRL / RLWC26 Women's Draw", "https://www.nrl.com/draw/?competition=176&round=2&season=2026")],
        "IRL Women #1 defending champions",
        "IRL Women #2 (beat Wales Women 70-6 in Round 1)",
        0.835, 0.020, -16.5, "Points", 44.5, "Points", True,
        "Australia Jillaroos", "medium",
        None, "https://www.olbg.com/betting-tips/Rugby_League/10",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False, []
    ),
    E(
        "rl-wc26w-sam-wal", "Rugby League", "2026 Women's Rugby League World Cup — Round 2", "h2h_3way",
        "Fetu Samoa Women", "Wales Women", "2026-10-23T06:45:00Z", "CommBank Stadium, Sydney",
        "verified",
        [("NRL / RLWC26 Women's Draw", "https://www.nrl.com/draw/?competition=176&round=2&season=2026")],
        "IRL Women #5",
        "IRL Women #7 (lost 6-70 to England Women in Round 1)",
        0.790, 0.025, -14.5, "Points", 42.5, "Points", True,
        "Fetu Samoa Women", "medium",
        None, "https://www.olbg.com/betting-tips/Rugby_League/10",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False, []
    ),

    # =========================================================================
    # 12. GOLF (All 10 Live OLBG Tournaments — 100% Priced with Outright + Field Odds! Closes Audit B!)
    # =========================================================================
    E(
        "golf-genesis-101905", "Golf", "Genesis Championship (DP World Tour & KPGA Co-Sanctioned, $4M)", "outright",
        "Si Woo Kim (Tournament Outright)", "The Field (119 Players)", "2026-10-22T00:00:00Z", "Woo Jeong Hills Country Club, Cheonan, Korea",
        "verified",
        [("DP World Tour 2026 Schedule", "https://www.europeantour.com/dpworld-tour/schedule/2026/")],
        "Top Korean PGA TOUR / DPWT headliner", "Full DPWT & KPGA co-sanctioned field",
        0.135, 0.0, 0.0, "Outright", None, "", False,
        "Si Woo Kim (Outright / Each-Way)", "medium",
        101905, "https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Genesis_Championship/5?event_id=101905",
        "Win Tournament", "Si Woo Kim", "5/18 (28%)", False,
        ["Prior repo data/fixtures.json swapped event_id to 101903 (Stifel Charity Classic) instead of 101905"]
    ),
    E(
        "golf-bermuda-101904", "Golf", "Butterfield Bermuda Championship (PGA TOUR FedExCup Fall, $6M)", "outright",
        "Ben James / PGA Fall Headliner", "The Field (119 Players, Def. Champ Adam Schenk)", "2026-10-22T10:30:00Z", "Port Royal Golf Course, Southampton, Bermuda",
        "verified",
        [("PGA TOUR Official Schedule", "https://www.pgatour.com/schedule")],
        "Leading OLBG FedExCup Fall selection", "120-player Port Royal field (def. champ Adam Schenk)",
        0.065, 0.0, 0.0, "Outright", None, "", False,
        "Ben James (Each-Way Outright)", "low",
        101904, "https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Bermuda_Championship/5?event_id=101904",
        "Win Tournament", "Ben James", "3/12 (25%)", False, []
    ),
    E(
        "golf-bmw-ladies-101906", "Golf", "BMW Ladies Championship (LPGA Tour, $2.35M)", "outright",
        "Sei Young Kim (Defending Champion)", "The Field (77 LPGA Players, No Cut)", "2026-10-22T01:00:00Z", "Pine Beach Golf Links, Haenam, Republic of Korea",
        "verified",
        [("LPGA Official Schedule", "https://www.lpga.com/tournaments")],
        "Defending 2025 Pine Beach champion on home soil", "Limited-field 78-player LPGA Asian Swing elite roster",
        0.095, 0.0, 0.0, "Outright", None, "", False,
        "Sei Young Kim (Outright / Top-5)", "medium",
        101906, "https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/BMW_Ladies_Championship/5?event_id=101906",
        "Win Tournament", "Sei Young Kim", "2/8 (25%)", False, []
    ),
    E(
        "golf-stifel-101903", "Golf", "Stifel Charity Classic (PGA TOUR Champions Charles Schwab Cup Playoffs)", "outright",
        "Steven Alker", "The Field (Playoff Qualifiers)", "2026-10-23T15:00:00Z", "Norwood Hills Country Club, St. Louis, MO",
        "verified",
        [("PGA TOUR Champions Schedule", "https://www.pgatour.com/pgatour-champions/schedule")],
        "Perennial Schwab Cup leader", "Champions Tour playoff field",
        0.155, 0.0, 0.0, "Outright", None, "", False,
        "Steven Alker (Outright)", "medium",
        101903, "https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Stifel_Charity_Classic/5?event_id=101903",
        "Win Tournament", "Steven Alker", "2/7 (29%)", False,
        ["Prior repo data/fixtures.json swapped Stifel event_id to 101907 instead of live OLBG 101903"]
    ),
    E(
        "golf-players-sa-101907", "Golf", "Webex Players Series South Australia (PGA Tour of Australasia)", "outright",
        "Josh Armstrong", "The Field", "2026-10-22T20:30:00Z", "Willunga Golf Course, South Australia",
        "tour_calendar_verified",
        [("PGA Tour of Australasia", "https://pga.org.au/")],
        "Leading Australasian tip selection", "Mixed-gender Webex Series field",
        0.085, 0.0, 0.0, "Outright", None, "", False,
        "Josh Armstrong (Each-Way)", "low",
        101907, "https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Players_Series_SA/5?event_id=101907",
        "Win Tournament", "Josh Armstrong", "2/2 (100%)", False, []
    ),
    E(
        "golf-fortinet-101908", "Golf", "Fortinet Players Cup (Japan Golf Tour / JGTO)", "outright",
        "Ryosuke Kinoshita", "The Field", "2026-10-22T22:30:00Z", "Narita Hills Country Club, Chiba, Japan",
        "tour_calendar_verified",
        [("JGTO Official Schedule", "https://www.jgto.org/en/")],
        "JGTO winner", "JGTO field",
        0.075, 0.0, 0.0, "Outright", None, "", False,
        "Ryosuke Kinoshita (Each-Way)", "low",
        101908, "https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Fortinet_Players_Cup/5?event_id=101908",
        "Win Tournament", "Ryosuke Kinoshita", "1/2 (50%)", False, []
    ),
    E(
        "golf-indiaw-101909", "Golf", "Hero Women's Indian Open (Ladies European Tour)", "outright",
        "Avani Prashanth", "The Field", "2026-10-22T02:30:00Z", "DLF Golf and Country Club, Gurugram, India",
        "tour_calendar_verified",
        [("Ladies European Tour Schedule", "https://ladieseuropeantour.com/schedule/")],
        "Leading Indian LET player on home course", "Full LET field",
        0.080, 0.0, 0.0, "Outright", None, "", False,
        "Avani Prashanth (Each-Way)", "low",
        101909, "https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Hero_Womens_Indian_Open/5?event_id=101909",
        "Win Tournament", "Avani Prashanth", "0/0 Win Tips (EW only bug!)", False,
        ["Upstream OLBG bug BUG-OLBG-EW-DIVZERO: displays '0 / 0 Win Tips' (0%) despite active Each-Way tips"]
    ),
    E(
        "golf-hkopen-101910", "Golf", "Link Hong Kong Open (Asian Tour International Series)", "outright",
        "Paul Casey", "The Field", "2026-10-22T00:00:00Z", "Hong Kong Golf Club, Fanling",
        "tour_calendar_verified",
        [("Asian Tour Official Portal", "https://www.asiantour.com/")],
        "International Series contender at Fanling", "Asian Tour / LIV crossover field",
        0.085, 0.0, 0.0, "Outright", None, "", False,
        "Paul Casey (Each-Way)", "low",
        101910, "https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Hong_Kong_Open/5?event_id=101910",
        "Win Tournament", "Paul Casey", "1/3 (33%)", False, []
    ),
    E(
        "golf-sen-ita-101911", "Golf", "Senior Italian Open (Legends Tour)", "outright",
        "Mikael Lundberg", "The Field", "2026-10-22T07:30:00Z", "San Domenico Golf, Puglia, Italy",
        "tour_calendar_verified",
        [("European / Legends Tour Portal", "https://www.europeantour.com/")],
        "Multiple Italian Open winner", "Legends Tour field",
        0.095, 0.0, 0.0, "Outright", None, "", False,
        "Mikael Lundberg (Each-Way)", "low",
        101911, "https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Senior_Italian_Open/5?event_id=101911",
        "Win Tournament", "Mikael Lundberg", "1/2 (50%)", False, []
    ),
    E(
        "golf-stella-sa-101912", "Golf", "Stella Artois Players Championship (Sunshine Tour)", "outright",
        "Daniel van Tonder", "The Field", "2026-10-22T05:00:00Z", "South Africa",
        "tour_calendar_verified",
        [("Sunshine Tour Official Portal", "https://sunshinetour.com/")],
        "Sunshine Tour Order of Merit powerhouse", "Sunshine Tour field",
        0.115, 0.0, 0.0, "Outright", None, "", False,
        "Daniel van Tonder (Outright)", "low",
        101912, "https://www.olbg.com/betting-tips/Golf/All_Golf/All_Events/Stella_Artois_Players_Championship/5?event_id=101912",
        "Win Tournament", "Daniel van Tonder", "1/2 (50%)", False, []
    ),

    # =========================================================================
    # 13. MOTOR RACING (All 3 Live OLBG F1 Markets — Verified on formula1.com!)
    # =========================================================================
    E(
        "f1-drivers-title-828", "Motor Racing", "2026 FIA Formula 1 World Drivers' Championship — Outright", "outright",
        "Kimi Antonelli (Mercedes)", "The Field (Russell 238, Hamilton 229, Verstappen 221)", "2026-12-06T13:00:00Z", "Yas Marina Finale (6 GP Rounds Remaining)",
        "verified",
        [("Formula1.com Official 2026 Drivers' Standings", "https://www.formula1.com/en/results/2026/drivers")],
        "#1 F1 Standings: 340 pts (102-pt lead over #2 Russell 238, +111 over Hamilton 229, +119 over Verstappen 221)",
        "#2 Russell (238), #3 Hamilton (229), #4 Verstappen (221), #5 Leclerc (215), #6 Norris (201)",
        0.925, 0.0, 0.0, "Outright", None, "", False,
        "Kimi Antonelli (World Championship Winner)", "high",
        828, "https://www.olbg.com/betting-tips/Motor_Racing/All_Motor_Racing/All_Events/Formula_1_Drivers_Championship_2026/14?event_id=828",
        "Win Tournament", "Max Verstappen", "9/33 (27%)", False,
        ["Massive stale-tip crowd anomaly on OLBG: 9/33 tipsters still sit on pre-season/early-season Max Verstappen (4th on 221 pts, 119 pts behind Antonelli's 340 pts)"]
    ),
    E(
        "f1-wout-antonelli-912", "Motor Racing", "2026 F1 Drivers' Championship — Without Kimi Antonelli", "outright",
        "George Russell (Mercedes)", "The Field ex-Antonelli (Hamilton 229, Verstappen 221, Leclerc 215)", "2026-12-06T13:00:00Z", "Season Classification ex-Antonelli",
        "verified",
        [("Formula1.com Official 2026 Drivers' Standings", "https://www.formula1.com/en/results/2026/drivers")],
        "#2 F1 Standings: 238 pts (+9 ahead of Hamilton 229, +17 ahead of Verstappen 221)",
        "Hamilton (229), Verstappen (221), Leclerc (215), Norris (201)",
        0.445, 0.0, 0.0, "Outright", None, "", False,
        "George Russell (Without Antonelli)", "medium",
        912, "https://www.olbg.com/betting-tips/Motor_Racing/All_Motor_Racing/All_Events/Formula_1_Drivers_Championship_2026_Without_Kimi_Antonelli/14?event_id=912",
        "Win Tournament", "Max Verstappen", "4/6 (67%)", False, []
    ),
    E(
        "f1-usgp-cota-913", "Motor Racing", "2026 Formula 1 United States Grand Prix — Race Winner", "outright",
        "Kimi Antonelli (Mercedes)", "The Field (Verstappen, Russell, Hamilton, Leclerc, Norris)", "2026-10-25T20:00:00Z", "Circuit of The Americas, Austin, TX",
        "verified",
        [("Formula1.com Official 2026 Standings & Calendar", "https://www.formula1.com/en/results/2026/drivers")],
        "#1 Championship leader on 340 pts",
        "21-car COTA grid",
        0.345, 0.0, 0.0, "Outright", None, "", False,
        "Kimi Antonelli (Race Winner)", "medium",
        913, "https://www.olbg.com/betting-tips/Motor_Racing/All_Motor_Racing/All_Events/USA_Grand_Prix/14?event_id=913",
        "Win Race", "Max Verstappen", "10/31 (32%)", False, []
    ),

    # =========================================================================
    # 14. AUSSIE RULES (All 9 Official NAB AFLW Round 11 Matches — Live 2026 Ladder Re-Priced!)
    # =========================================================================
    E(
        "aflw-r11-nmfc-adel", "Aussie Rules", "2026 NAB AFLW Premiership Season — Round 11 (Match #8979)", "h2h_3way",
        "North Melbourne Tasmanian Kangaroos", "Adelaide Crows", "2026-10-25T02:05:00Z", "North Hobart Oval, Hobart",
        "verified",
        [("NAB AFLW Official R11 Board", "https://www.afl.com.au/aflw"),
         ("NAB AFLW Official 2026 Ladder", "https://www.afl.com.au/aflw/ladder")],
        "1st on 2026 AFLW R10 ladder: 9-1-0 (36 pts, 251.9%)",
        "9th on 2026 AFLW R10 ladder: 5-5-0 (20 pts, 102.4%)",
        0.865, 0.010, -21.5, "Points", 74.5, "Points", True,
        "North Melbourne Tasmanian Kangaroos", "high",
        None, "https://www.olbg.com/betting-tips/Aussie_Rules/22",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False,
        ["Re-priced from live official 2026 AFLW R10 ladder (closes repo open item F-T34-01 / T35); North Hobart Oval venue confirmed"]
    ),
    E(
        "aflw-r11-carl-gws", "Aussie Rules", "2026 NAB AFLW Premiership Season — Round 11 (Match #8975)", "h2h_3way",
        "Carlton", "GWS GIANTS", "2026-10-25T06:05:00Z", "IKON Park, Melbourne",
        "verified",
        [("NAB AFLW Official R11 Board", "https://www.afl.com.au/aflw"),
         ("NAB AFLW Official 2026 Ladder", "https://www.afl.com.au/aflw/ladder")],
        "6th on 2026 AFLW R10 ladder: 7-3-0 (28 pts, 133.0%)",
        "15th on 2026 AFLW R10 ladder: 2-8-0 (8 pts, 68.2%)",
        0.855, 0.010, -19.5, "Points", 71.5, "Points", False,
        "Carlton", "high",
        None, "https://www.olbg.com/betting-tips/Aussie_Rules/22",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False,
        ["Re-priced from live official 2026 AFLW R10 ladder (7-3-0, 28 pts, 133.0% vs 2-8-0, 8 pts, 68.2%)"]
    ),
    E(
        "aflw-r11-haw-ess", "Aussie Rules", "2026 NAB AFLW Premiership Season — Round 11 (Match #8976)", "h2h_3way",
        "Hawthorn", "Essendon", "2026-10-25T04:05:00Z", "Kennedy Community Centre, Dingley",
        "verified",
        [("NAB AFLW Official R11 Board", "https://www.afl.com.au/aflw"),
         ("NAB AFLW Official 2026 Ladder", "https://www.afl.com.au/aflw/ladder")],
        "10th on 2026 AFLW R10 ladder: 5-5-0 (20 pts, 101.5%)",
        "17th on 2026 AFLW R10 ladder: 1-9-0 (4 pts, 55.6%)",
        0.815, 0.010, -16.5, "Points", 68.5, "Points", False,
        "Hawthorn", "high",
        None, "https://www.olbg.com/betting-tips/Aussie_Rules/22",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False,
        ["Re-priced from live official 2026 AFLW R10 ladder; venue corrected to Kennedy Community Centre, Dingley"]
    ),
    E(
        "aflw-r11-geel-fre", "Aussie Rules", "2026 NAB AFLW Premiership Season — Round 11 (Match #8974)", "h2h_3way",
        "Geelong Cats", "Fremantle", "2026-10-24T04:05:00Z", "GMHBA Stadium, Geelong",
        "verified",
        [("NAB AFLW Official R11 Board", "https://www.afl.com.au/aflw"),
         ("NAB AFLW Official 2026 Ladder", "https://www.afl.com.au/aflw/ladder")],
        "2nd on 2026 AFLW R10 ladder: 9-1-0 (36 pts, 167.2%)",
        "8th on 2026 AFLW R10 ladder: 5-5-0 (20 pts, 104.9%)",
        0.785, 0.015, -14.5, "Points", 68.5, "Points", False,
        "Geelong Cats", "medium",
        None, "https://www.olbg.com/betting-tips/Aussie_Rules/22",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False,
        ["Major T35 re-price fix: Geelong sit 2nd on 36 pts (9-1-0, 167.2%), flipping wrong prior underdog price into strong home favourite"]
    ),
    E(
        "aflw-r11-wb-melb", "Aussie Rules", "2026 NAB AFLW Premiership Season — Round 11 (Match #8973)", "h2h_3way",
        "Western Bulldogs", "Melbourne", "2026-10-24T08:15:00Z", "Mission Whitten Oval, Melbourne",
        "verified",
        [("NAB AFLW Official R11 Board", "https://www.afl.com.au/aflw"),
         ("NAB AFLW Official 2026 Ladder", "https://www.afl.com.au/aflw/ladder")],
        "4th on 2026 AFLW R10 ladder: 8-2-0 (32 pts, 140.9%)",
        "3rd on 2026 AFLW R10 ladder: 8-2-0 (32 pts, 177.2%)",
        0.440, 0.015, 3.5, "Points", 72.5, "Points", True,
        "Melbourne", "medium",
        None, "https://www.olbg.com/betting-tips/Aussie_Rules/22",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False,
        ["Major T35 re-price fix: Western Bulldogs sit 4th on 32 pts (8-2-0) facing 3rd Melbourne (32 pts, 177.2%) — tight top-four clash"]
    ),
    E(
        "aflw-r11-gcfc-rich", "Aussie Rules", "2026 NAB AFLW Premiership Season — Round 11 (Match #8972)", "h2h_3way",
        "Gold Coast SUNS", "Richmond", "2026-10-24T06:05:00Z", "People First Stadium, Gold Coast",
        "verified",
        [("NAB AFLW Official R11 Board", "https://www.afl.com.au/aflw"),
         ("NAB AFLW Official 2026 Ladder", "https://www.afl.com.au/aflw/ladder")],
        "5th on 2026 AFLW R10 ladder: 7-3-0 (28 pts, 138.9%)",
        "13th on 2026 AFLW R10 ladder: 4-6-0 (16 pts, 68.9%)",
        0.765, 0.015, -13.5, "Points", 66.5, "Points", False,
        "Gold Coast SUNS", "medium",
        None, "https://www.olbg.com/betting-tips/Aussie_Rules/22",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False,
        ["Major T35 re-price fix: Gold Coast sit 5th on 28 pts (7-3-0, 138.9%), overturning wrong prior 18th-place 1-9 pricing"]
    ),
    E(
        "aflw-r11-port-coll", "Aussie Rules", "2026 NAB AFLW Premiership Season — Round 11 (Match #8970)", "h2h_3way",
        "Port Adelaide", "Collingwood", "2026-10-23T08:15:00Z", "Alberton Oval, Adelaide",
        "verified",
        [("NAB AFLW Official R11 Board", "https://www.afl.com.au/aflw"),
         ("NAB AFLW Official 2026 Ladder", "https://www.afl.com.au/aflw/ladder")],
        "11th on 2026 AFLW R10 ladder: 4-6-0 (16 pts, 78.8%)",
        "16th on 2026 AFLW R10 ladder: 1-9-0 (4 pts, 56.7%)",
        0.745, 0.015, -11.5, "Points", 69.5, "Points", True,
        "Port Adelaide", "medium",
        None, "https://www.olbg.com/betting-tips/Aussie_Rules/22",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False, []
    ),
    E(
        "aflw-r11-syd-wce", "Aussie Rules", "2026 NAB AFLW Premiership Season — Round 11 (Match #8977)", "h2h_3way",
        "Sydney Swans", "West Coast Eagles", "2026-10-25T01:35:00Z", "Henson Park, Sydney",
        "verified",
        [("NAB AFLW Official R11 Board", "https://www.afl.com.au/aflw"),
         ("NAB AFLW Official 2026 Ladder", "https://www.afl.com.au/aflw/ladder")],
        "7th on 2026 AFLW R10 ladder: 7-3-0 (28 pts, 112.9%)",
        "12th on 2026 AFLW R10 ladder: 4-6-0 (16 pts, 75.2%)",
        0.735, 0.015, -10.5, "Points", 71.5, "Points", True,
        "Sydney Swans", "medium",
        None, "https://www.olbg.com/betting-tips/Aussie_Rules/22",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False, []
    ),
    E(
        "aflw-r11-stk-bl", "Aussie Rules", "2026 NAB AFLW Premiership Season — Round 11 (Match #8971)", "h2h_3way",
        "St Kilda", "Brisbane Lions", "2026-10-24T02:05:00Z", "RSEA Park, Melbourne",
        "verified",
        [("NAB AFLW Official R11 Board", "https://www.afl.com.au/aflw"),
         ("NAB AFLW Official 2026 Ladder", "https://www.afl.com.au/aflw/ladder")],
        "18th on 2026 AFLW R10 ladder: 1-9-0 (4 pts, 45.1%)",
        "14th on 2026 AFLW R10 ladder: 3-7-0 (12 pts, 89.7%)",
        0.345, 0.015, 7.5, "Points", 67.5, "Points", False,
        "Brisbane Lions", "low",
        None, "https://www.olbg.com/betting-tips/Aussie_Rules/22",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False,
        ["Re-priced from live official 2026 AFLW R10 ladder: 18th St Kilda (1-9-0, 4 pts) vs 14th Brisbane (3-7-0, 12 pts, 89.7%)"]
    ),

    # =========================================================================
    # 15. eSPORTS (LoL Worlds 2026 Swiss Stage — OLBG Zero-Tip Blind Spot)
    # =========================================================================
    E(
        "esports-lol-tsw-lyon", "eSports", "2026 League of Legends World Championship — Swiss Stage", "h2h_2way",
        "Team Secret Whales", "LYON", "", "Credit Union of Texas Event Center, Allen, TX",
        "verified",
        [("LoL Esports Official Hub", "https://lolesports.com/en-US/")],
        "Pool 2 seed (#1 VCS champion)",
        "Pool 3 Play-In qualifier",
        0.655, 0.0, -1.5, "Maps", 2.5, "Maps", False,
        "Team Secret Whales", "medium",
        None, "https://www.olbg.com/betting-tips/eSports/23",
        "OLBG Blind Spot (0 match tips)", "Unlisted on OLBG", "0/0", False,
        ["OLBG eSports hub displays legacy CS:GO/FIFA copy & 0 active match tips during LoL Worlds 2026 Swiss Stage"]
    ),

    # =========================================================================
    # 16. GAELIC FOOTBALL (All 5 Live OLBG Events: 4 County Finals/Ties + 1 All-Ireland Outright)
    # =========================================================================
    E(
        "gaa-galway-moy-sk-3532", "Gaelic Football", "Galway Senior Football Championship — Final", "h2h_3way",
        "Maigh Cuilinn (Moycullen)", "Salthill-Knocknacarra", "2026-10-24T18:00:00Z", "Pearse Stadium, Salthill",
        "verified",
        [("Galway GAA Official Results & Fixtures", "https://www.galwaygaa.ie/results/")],
        "Recent Galway & Connacht club champions", "Galway city finalists",
        0.605, 0.085, -2.5, "Points", 27.5, "Points", False,
        "Maigh Cuilinn (Moycullen)", "medium",
        3532, "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Moycullen_v_Salthill-Knocknacarra/25?event_id=3532",
        "Handicap", "Moycullen -3.50", "9/17 (53%)", False, []
    ),
    E(
        "gaa-cork-fin-nem-3530", "Gaelic Football", "Cork Premier Senior Football Championship — Final", "h2h_3way",
        "St Finbarr's", "Nemo Rangers", "2026-10-25T16:00:00Z", "SuperValu Páirc Uí Chaoimh, Cork",
        "verified",
        [("Cork GAA Official Fixtures", "https://gaacork.ie/fixtures-results/")],
        "Cork city derby co-finalists", "Record 23-time Cork champions",
        0.465, 0.095, 0.5, "Points", 26.5, "Points", False,
        "Nemo Rangers", "low",
        3530, "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/St_Finbarrs_v_Nemo_Rangers/25?event_id=3530",
        "Handicap", "Nemo Rangers +1.50", "10/12 (83%)", False, []
    ),
    E(
        "gaa-wat-rat-nir-3536", "Gaelic Football", "Waterford Senior Football Championship — Final", "h2h_3way",
        "Rathgormack", "The Nire", "2026-10-25T14:30:00Z", "Fraher Field, Dungarvan",
        "verified",
        [("Munster GAA Official Championship Fixtures", "https://munster.gaa.ie/fixtures/munster-gaa-fixtures/")],
        "Defending Waterford champions", "Perennial Waterford finalists",
        0.585, 0.085, -2.5, "Points", 24.5, "Points", False,
        "Rathgormack", "medium",
        3536, "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Rathgormack_v_The_Nire/25?event_id=3536",
        "Handicap", "Rathgormack -2.50", "1/1 (100%)", False,
        ["Upstream OLBG defect BUG-OLBG-3536-DATE: OLBG lists 01 Nov 10:30, a full week after official Munster GAA fixture (Sun 25 Oct 2026, 14:30 UTC at Fraher Field)"]
    ),
    E(
        "gaa-cork-kan-eir-3531", "Gaelic Football", "Cork Senior A / Club Football (OLBG Listing)", "h2h_3way",
        "Kanturk", "Éire Óg (Cork)", "", "",
        "unverified",
        [("Cork GAA Official Fixtures", "https://gaacork.ie/fixtures-results/")],
        "", "",
        0.545, 0.090, -1.5, "Points", 26.5, "Points", False,
        "Kanturk", "low",
        3531, "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/Kanturk_v_Eire_Og_Cor/25?event_id=3531",
        "To Win", "Kanturk", "3/4 (75%)", False,
        ["Flagged unverified: OLBG lists 'Kanturk v Eire Og Cor' on 01 Nov 09:00, unconfirmed on current Cork GAA Senior PSFC final sheet; UTC & venue left blank"]
    ),
    E(
        "gaa-out-allireland-3327", "Gaelic Football", "2027 All-Ireland Senior Football Championship — Outright", "outright",
        "Kerry (Sam Maguire Outright)", "The Field (Dublin, Galway, Armagh, Donegal & Counties)", "2027-07-25T14:30:00Z", "Croke Park, Dublin",
        "verified",
        [("GAA Official Portal", "https://www.gaa.ie/")],
        "Record All-Ireland champions", "32-county championship field",
        0.315, 0.0, 0.0, "Outright", None, "", False,
        "Kerry (Outright)", "medium",
        3327, "https://www.olbg.com/betting-tips/Gaelic_Football/All_Gaelic_Football/All_Events/All_Ireland_Football_Championship_2027/25?event_id=3327",
        "Outright Winner", "Kerry", "5/7 (71%)", False, []
    ),

    # =========================================================================
    # 17. GREYHOUNDS (All 6 Live OLBG UK Graded Daily Races — Closes Audit B!)
    # Verified GBGB licensed stadium & UTC clock mapping; runner trap cards left blank/unverified
    # because api.gbgb.org.uk/api/results/meeting?date=2026-10-21 returned HTTP 404.
    # =========================================================================
    E(
        "grey-harlow-1032-689384", "Greyhounds", "GBGB UK Graded Greyhound Race — 10:32 BST Harlow", "race",
        "Makeit Sway (OLBG Most-Tipped Runner)", "The Field (5 Graded Runners)", "2026-10-21T09:32:00Z", "Harlow Greyhound Stadium, Essex",
        "unverified",
        [("GBGB Official Regulator Portal", "https://www.gbgb.org.uk/")],
        "OLBG Win selection (trap & sectional form unverified via GBGB API 404)", "",
        0.240, 0.0, 0.0, "Race Win", None, "", False,
        "Makeit Sway (Race Win)", "low",
        689384, "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/10:32_Harlow/28?event_id=689384",
        "Daily Races", "Makeit Sway", "1/1 (100%)", False,
        ["OLBG renders '05:32' (EDT -5h from BST) beside '10:32 Harlow' with zero timezone label; GBGB API returned 404 so trap/form left blank & flagged unverified"]
    ),
    E(
        "grey-harlow-1048-689385", "Greyhounds", "GBGB UK Graded Greyhound Race — 10:48 BST Harlow", "race",
        "Moaning Cashout (OLBG Most-Tipped Runner)", "The Field (5 Graded Runners)", "2026-10-21T09:48:00Z", "Harlow Greyhound Stadium, Essex",
        "unverified",
        [("GBGB Official Regulator Portal", "https://www.gbgb.org.uk/")],
        "OLBG Win selection (trap & sectional form unverified via GBGB API 404)", "",
        0.240, 0.0, 0.0, "Race Win", None, "", False,
        "Moaning Cashout (Race Win)", "low",
        689385, "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/10:48_Harlow/28?event_id=689385",
        "Daily Races", "Moaning Cashout", "1/1 (100%)", False,
        ["Unlabelled -5h EDT display ('05:48' for 10:48 BST = 09:48 UTC); runner form flagged unverified"]
    ),
    E(
        "grey-monmore-1103-689387", "Greyhounds", "GBGB UK Graded Greyhound Race — 11:03 BST Monmore", "race",
        "Relentless I Am (OLBG Most-Tipped Runner)", "The Field (5 Graded Runners)", "2026-10-21T10:03:00Z", "Monmore Green Stadium, Wolverhampton",
        "unverified",
        [("GBGB Official Regulator Portal", "https://www.gbgb.org.uk/")],
        "OLBG Win selection (trap & sectional form unverified via GBGB API 404)", "",
        0.240, 0.0, 0.0, "Race Win", None, "", False,
        "Relentless I Am (Race Win)", "low",
        689387, "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/11:03_Monmore/28?event_id=689387",
        "Daily Races", "Relentless I Am", "1/1 (100%)", False,
        ["Prior repo data/fixtures.json wrote wrong event_id=689386 on Monmore (live OLBG has 689387); runner trap form flagged unverified"]
    ),
    E(
        "grey-harlow-1104-689383", "Greyhounds", "GBGB UK Graded Greyhound Race — 11:04 BST Harlow", "race",
        "Muinteoir Jane (OLBG Most-Tipped Runner)", "The Field (5 Graded Runners)", "2026-10-21T10:04:00Z", "Harlow Greyhound Stadium, Essex",
        "unverified",
        [("GBGB Official Regulator Portal", "https://www.gbgb.org.uk/")],
        "OLBG Win selection (trap & sectional form unverified via GBGB API 404)", "",
        0.240, 0.0, 0.0, "Race Win", None, "", False,
        "Muinteoir Jane (Race Win)", "low",
        689383, "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/11:04_Harlow/28?event_id=689383",
        "Daily Races", "Muinteoir Jane", "1/1 (100%)", False,
        ["Unlabelled -5h EDT display ('06:04' for 11:04 BST = 10:04 UTC); runner form flagged unverified"]
    ),
    E(
        "grey-nott-1109-689386", "Greyhounds", "GBGB UK Graded Greyhound Race — 11:09 BST Nottingham", "race",
        "Bluejig Polly (OLBG Most-Tipped Runner)", "The Field (5 Graded Runners)", "2026-10-21T10:09:00Z", "Nottingham Greyhound Stadium, Colwick Park",
        "unverified",
        [("GBGB Official Regulator Portal", "https://www.gbgb.org.uk/")],
        "OLBG Win selection (trap & sectional form unverified via GBGB API 404)", "",
        0.240, 0.0, 0.0, "Race Win", None, "", False,
        "Bluejig Polly (Race Win)", "low",
        689386, "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/11:09_Nottingham/28?event_id=689386",
        "Daily Races", "Bluejig Polly", "1/1 (100%)", False,
        ["Prior repo data/fixtures.json swapped Nottingham event_id to 689390 (live OLBG has 689386); runner form flagged unverified"]
    ),
    E(
        "grey-kinsley-1114-689390", "Greyhounds", "GBGB UK Graded Greyhound Race — 11:14 BST Kinsley", "race",
        "Swift Perry (OLBG Consensus Runner)", "The Field (5 Graded Runners)", "2026-10-21T10:14:00Z", "Kinsley Greyhound Stadium, Pontefract",
        "unverified",
        [("GBGB Official Regulator Portal", "https://www.gbgb.org.uk/")],
        "2/2 OLBG Win tips (trap & sectional form unverified via GBGB API 404)", "",
        0.265, 0.0, 0.0, "Race Win", None, "", False,
        "Swift Perry (Race Win)", "low",
        689390, "https://www.olbg.com/betting-tips/Greyhounds/All_Greyhounds/All_Events/11:14_Kinsley/28?event_id=689390",
        "Daily Races", "Swift Perry", "2/2 (100%)", False,
        ["Prior repo data/fixtures.json swapped Kinsley event_id to 689388 (live OLBG has 689390); runner form flagged unverified"]
    ),
]
