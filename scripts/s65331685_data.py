#!/usr/bin/env python3
"""T65331685 desk: encode official-source reads, originate zero-vig multi-market
lines (Beta(2,2) shrinkage + log5 / Poisson / gaussian ladders), and emit the
data/65331685/ JSON artifacts.

Run: python3 scripts/s65331685_data.py
"""
from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "65331685")
SESSION = "T65331685"
NOW = "2026-10-23T20:40:00Z"

CONSTANTS = {
    "shrinkage_prior": "Beta(2,2)",
    "link": "log5",
    "home_edge": "none applied",
    "nhl_loss_convention": "OTL counts as a defeat for win-percentage inputs",
    "rugby_draw_convention": "draw counts 0.5 win and 0.5 loss in raw rates",
    "baseball_totals": "paired regular-season run rates; independent Poisson scores conditioned on no tie",
    "nba_margin_sd_points": 11.5,
    "nhl_margin_sd_goals": 1.9,
    "rugby_margin_sd_points": 14.0,
    "handball_margin_sd_goals": 4.0,
    "mlb_run_sd": 4.3,
    "tennis_link": "rank-Elo proxy: Elo(rank)=1500+40*log10(500/rank), logistic 400",
    "greyhound_link": "semi-final clock logistic, k=1.5 per second",
    "rlwc_link": "elite-spine representation index (documented 17-4 scale)",
    "cricket_link": "Beta(2,2)-shrunk series win rate, log5",
    "volleyball_link": "Beta(2,2)-shrunk set-share win rate, log5",
    "snooker_link": "Beta(2,2)-shrunk frame share this tournament, log5",
    "high_band": "p>0.70 AND -250 <= fair american <= +10000 (unrounded decides; 1e-6 float tolerance on band edges)",
    "read_channel": "Arena fetch/search layer; each read logged with URL and UTC time",
}

# ---------------------------------------------------------------- harvest ----
READS = [
    # (url, read_utc, what it gave)
    ("https://api-web.nhle.com/v1/schedule/2026-10-23", "2026-10-23T19:36:00Z",
     "NHL game week: MTL@CHI 2026-10-24T00:00Z (id 2026020166, United Center, FUT/OK), TBL@COL 01:00Z (2026020167, Ball Arena); Sat slate incl. ANA@PHI 17:00Z, LAK@NJD 19:30Z, TOR@EDM 23:00Z, VGK@CBJ 23:00Z, CAR@STL 23:00Z (chunks 0 and 2)"),
    ("https://api-web.nhle.com/v1/standings/2026-10-23", "2026-10-23T19:36:00Z",
     "NHL standings 2026-10-23T19:29:30Z (chunks 0-6): all 32 team W-L-OTL records incl. EDM 8-1-1, BOS 8-2-1, TBL 7-2-0, CAR 8-2-2, VGK 8-4-0, TOR 6-4-2, COL 5-4-1, MTL 4-3-2, CHI 3-6-0, ANA 4-6-0, PHI 3-6-3, CBJ 3-5-0, LAK 2-4-2, SJS 6-4-1, NJD 6-4-0"),
    ("https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-29&hydrate=team,probablePitcher,linescore", "2026-10-23T19:38:00Z",
     "World Series schedule: G1 TB@MIL 2026-10-24T00:00Z (gamePk 849805, ifNecessary=N, Martinez v Misiorowski), G2 2026-10-25T00:00Z (849802, Rasmussen v Henderson), G3 MIL@TB 2026-10-27T00:00Z (849804)"),
    ("https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026", "2026-10-23T19:40:00Z",
     "MLB 2026 standings: Rays 98-64 (RS 736 RA 650, home 55-26 away 43-38); chunk 1-2: Brewers 103-59 (RS 832 RA 618, W5, lastTen 8-2, xWinLoss 103-59)"),
    ("https://statsapi.mlb.com/api/v1.1/game/849805/feed/live", "2026-10-23T20:05:00Z",
     "WS G1 feed (Preview/Scheduled, 20:05Z): series 0-0; TB starter Nick Martinez, MIL starter Jacob Misiorowski confirmed"),
    ("https://www.nba.com/games?date=2026-10-23", "2026-10-23T19:38:00Z",
     "NBA Friday slate (12 games) with records and season-leader lines: NYK 0-1 @ BOS 0-1 7:00PM ET; MIN 1-0 @ ORL 0-1; DAL 0-1 @ IND 1-0; MEM 1-0 @ GSW 0-1 (Ty Jerome 45/7/6, Stephen Curry 23/2/1); plus CHI@MIL, TOR@WAS, ATL@CHA, DET@MIA, HOU@SAS, NOP@UTA, LAC@LAL, POR@SAC"),
    ("https://www.euroleaguebasketball.net/en/euroleague/news/game-center-round-7-el2627/", "2026-10-23T19:45:00Z",
     "EuroLeague Round 7 game center: Zalgiris 105-85 ASVEL (Valanciunas 15/8, Edwards 16); Oly-Fener and Paris-Valencia in progress at read time; Thu: Efes 89-80 Besiktas, Bayern 91-107 Dubai, Maccabi 99-113 Real Madrid, Panathinaikos 85-79 Baskonia, Milan 81-89 Barcelona, Partizan 85-82 Zvezda (OT); Paris 1-5 v Valencia 5-1 with Hifi 20.2 ppg top scorer, Shorts return"),
    ("https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf", "2026-10-23T20:15:00Z",
     "WTA Ningbo 500 official draw (released 23 Oct 10:00 PM): SF Rybakina (rank 1) v Shnaider (rank 13); Rybakina path bye, d. Kudermetova 6-1 3-6 6-1, d. Kawa 6-1 3-6 6-1? draw lines: d. Kawa 6-1 3-6 6-1 wait scores 61 36 61; Shnaider d. Kalinina 6-3 4-6 6-1, d. Eala 6-3 6-1? lines 63 46 61 and 75 64, d. Putintseva 7-5 7-6(4); Swiatek withdrawn (left thigh), Kostyuk right wrist injury"),
    ("https://wtafiles.wtatennis.com/pdf/draws/2026/405/MDS.pdf", "2026-10-23T20:16:00Z",
     "WTA Osaka 250 official draw: SF Boulter (seed 8, rank 54) v Siniakova; Boulter d. Sakatsume 6-3 6-1, d. Golubic 3-6 6-3 6-3; Siniakova d. Shibahara 6-1 6-2, d. Linette 6-4 6-1, d. Stearns (2) 6-4 0-6 4-0 ret (Stearns foot); withdrawals: Birrell calf, Kartal knee; Day low back"),
    ("https://www.atptour.com/en/scores/current", "2026-10-23T19:50:00Z",
     "ATP live: Brussels QF Fils (1) d. Michelsen (5) 6-4 7-6(12); Struff v Bergs (6) live 4-3; Lyon QF Cobolli (1) d. Nakashima (5) 4-6 6-4 6-4, Fritz (2) d. Altmaier 7-6(5) 6-2; Basel QF Medvedev d. Atmane 6-4 6-4, Bublik d. Khachanov"),
    ("https://www.unitedrugby.com/latest/news/round-4-team-announcements/", "2026-10-23T19:45:00Z",
     "URC Round 4 team lists (full): Fri Cardiff-Sharks, Connacht-Zebre, Edinburgh-Lions (all 18:45Z); Sat Bulls-Ulster 11:45Z, Stormers-Scarlets 14:00Z, Benetton-Glasgow 14:00Z, Leinster-Munster 17:00Z (Aviva), Ospreys-Dragons 18:00Z; Leinster XV: Keenan, T O'Brien, Osborne, Henshaw, J O'Brien, Carbery, Gibson-Park; Porter, Kelleher, Furlong, McCarthy, Ryan, Baird, van der Flier, Sheehan (capt); Munster XV: B O'Connor, S McCarthy, S O'Brien, Nankivell, Daly, O'Shea, Casey; Wycherley, van der Merwe, Brookes, F Wycherley, Beirne (capt), O'Donoghue, Kendellen, Coombes; Bulls: Pollard, Coetzee (capt); Stormers: Feinberg-Mngomezulu, de Villiers (capt), Roos; Glasgow: Steyn (capt), Tuipulotu, Fagerson, Darge; Ospreys at new St Helen's venue; Scarlets 'impressive start' per Davies"),
    ("https://stats.unitedrugby.com/match-centre/table/", "2026-10-23T20:35:00Z",
     "Official URC match-centre table (search read): Glasgow 13 pts (2-1-0, 95-72); Dragons 9 (1-1-1, 88-83); Ospreys 6 (1-0-2, 81-107); Benetton 3-5 pts (0-1-2, 64-68); Bulls 11 (2-0-1, 126-54); Stormers/Munster/Leinster rows partial; cross-checked BBC Sport table (Ulster 0-2-1 88-93 8pts; Scarlets 1-0-2 68-85 7pts; Leinster 75-58 8pts; Munster 72-74 9pts; Stormers 81-54 11pts)"),
    ("https://www.nrl.com/news/2026/10/20/world-cup-team-lists-mens-round-2/", "2026-10-23T19:45:00Z",
     "RLWC2026 men's R2 team lists: Tonga 36-0 Lebanon (FT); PNG v Samoa Sat 04:25Z (Samoa: Tabuai-Fidow, To'o, Tago, Crichton, Harris-Tavita, Luai, Molo, Leniu bench; Mariner hamstring out, Fa'alogo in after 4 tries v France; PNG: Biondi-Odo, Rhyse Martin, de Belin); England v France Sat 06:35Z HBF Park Perth (England: Brimson, Young, Farnworth, Williams, Smith, Radley, Thompson, Welsby 18; Knowles injured; France: Lacans, Fages, Garcia); NZ v Cook Islands Sun 05:05Z (Kini, Hughes, Nikorima, Mulitalo v Holmes, Iro)"),
    ("https://www.nrl.com/news/2026/10/20/world-cup-team-lists-womens-round-2/", "2026-10-23T20:15:00Z",
     "RLWC women's R2: Samoa 76-0 Wales (FT); Fiji v PNG Sat; Jillaroos v England Sat (Strange ACL out for tournament, Murray in); team lists for Samoa-Wales and Fiji-PNG read"),
    ("https://www.wst.tv/matches/", "2026-10-23T19:55:00Z",
     "BetVictor Northern Ireland Open draw/results: QFs Fri: Wilson 6-1 McGill, Craigie 6-2 Slessor (both completed); Jones 2-2 Donaldson and Gilbert 3-1 Williams live at read time; R3: Wilson 4-3 Pang, Craigie 4-2 Selt, Slessor 4-1 Jones, Gilbert 4-2 Cheung, Williams 4-0 O'Donnell, Jones 4-2 Wells, Donaldson 4-2 Brown; SFs scheduled Sat (Wilson v Craigie per OLBG render 12:00Z)"),
    ("https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/leaderboard", "2026-10-23T19:55:00Z",
     "Butterfield Bermuda Championship R2 in progress, Port Royal, cut line -5: Hirata -13 (65-64), Blanchet -13 (62-67), Power -12 (66-64), Conners -12 (63-67), Cole -12 (65-65), Skinns -11 (68-63), McCarthy -11; published odds column exists (bookmaker-branded) - left blank per repo policy"),
    ("https://www.icc-cricket.com/fixtures-results", "2026-10-23T19:55:00Z",
     "ICC fixtures: NZ v IND T20I (match 271647) Sat (07:00Z per OLBG render); Denmark v Kuwait and Qatar v Kenya List A 06:45Z; Namibia v Ireland ODI 07:30Z; Uganda v Mozambique 08:30Z; Gambia v Zambia and Lesotho v Nigeria 12:50Z; Mexico v Argentina T20s 14:00Z and 19:00Z; UAE v Netherlands CWC League 2 05:30Z (tool-clock rendered EDT, converted)"),
    ("https://www.icc-cricket.com/news/injury-blow-for-india-ahead-of-second-t20i-with-new-zealand", "2026-10-23T20:15:00Z",
     "India lead 1-0 after chasing 226 in Christchurch (highest T20I chase in India's history; Samson 67, Iyer 42, Dhir 42*); Ishan Kishan OUT 2nd T20I (low-grade right adductor strain), Kumar Kushagra added; 2nd T20I Saturday at Hagley Oval; India squad listed (Iyer c, Abhishek, Samson, Sooryavanshi, Tilak, Axar, Dube, NKR, Dhir, Prince Yadav, Mayank Yadav, Arshdeep, Bhuvneshwar, Varun, Kuldeep)"),
    ("https://www.cricinfo.com/series/pakistan-odi-tri-series-2026-27-1550706/pakistan-vs-england-4th-match-1550716/live-cricket-score", "2026-10-23T20:38:00Z",
     "PAK ODI Tri-Series 2026/27 (PAK/ENG/SL, 18-31 Oct): PAK v ENG 4th match Sun 25 Oct 13:00 PKT (08:00Z) Gaddafi Stadium Lahore, D/N; PAK beat SL by 37 runs (Oct 18), PAK 302/9 beat ENG 215 by 87 runs (Oct 20 Rawalpindi); captains Shaheen Afridi v Harry Brook"),
    ("https://www.formula1.com/en/latest/article/need-to-know-the-most-important-facts-stats-and-trivia-ahead-of-the-2026-united-states-grand-prix.3yCUtnzlXLwOvhVtmsdVRK", "2026-10-23T19:55:00Z",
     "F1 US GP (Round 18, COTA 5.513km): FP1/FP2 Fri Oct 23, FP3+Qualifying Sat Oct 24, race Sun Oct 25; Antonelli leads standings and can clinch title if he wins with Russell 9th-or-lower and Hamilton 5th-or-lower; Verstappen won Malaysia+Singapore and 4 of last 5 US GPs; Hamilton most wins (6) here; lap record Leclerc 1m36.169 (2019); C2/C3/C4 tyres, likely one-stop"),
    ("https://www.gbgb.org.uk/category-one-glory-beckons-in-coral-100-champion-stakes-final/", "2026-10-23T20:15:00Z",
     "Coral 100 Champion Stakes Final Romford Fri night over 575m, £20,000 to winner; Newinn Jolly withdrawn (urine infection); semis: Grouchos Gregor 35.36 (-20) fastest, beat Fortanach Col (Wilton 1-2); Aayamza Legend 35.75 beat Don Cici; Bubbly Holly 35.95 beat Newinn Jolly"),
    ("https://munster.gaa.ie/fixtures/events-calendar/", "2026-10-23T20:15:00Z",
     "Munster GAA events: Hurling Shinty International Ireland v Scotland Sat 24 Oct 18:00 local (17:00Z) SuperValu Pairc Ui Chaoimh; Camogie Shinty Intl 16:00 local; Kerry SFC final Dr Crokes v Kenmare Shamrocks Sun 25 Oct 14:00 (post-clock-change WET = 14:00Z) Fitzgerald Stadium; Waterford SFC final Rathgormack v The Nire Sun 14:30"),
    ("https://www.lnh.fr/daikin-starligue/calendrier", "2026-10-23T20:10:00Z",
     "LNH Daikin StarLigue J08: Aix-Toulouse, Chartres-Nimes, Limoges-Dunkerque, Selestat-Caen, Tremblay-Cesson live/elapsed Fri; upcoming Nantes-Chambery Sat 24 Oct 19:00 CEST (17:00Z); Saint-Raphael-Paris Sun 25 Oct 16:00 (14:00Z); Montpellier-Saran Sun 17:00 (15:00Z)"),
    ("https://www.lnh.fr/daikin-starligue/classement", "2026-10-23T20:30:00Z",
     "LNH standings after 7: Paris 14 pts (7-0-0, 239-190), Nantes 12 (6-1-0, 244-203), Montpellier 10 (4-1-2, 234-205), Nimes 10, Limoges 8, Chambre 6 (2-3-2, 224-231), Saran 6 (3-0-4, 202-216), Saint-Raphael 4 (2-0-5, 207-225)"),
    ("https://www.legavolley.it/calendario/?idCampionato=999", "2026-10-23T20:10:00Z",
     "SuperLega clubs confirmed on official league site (Itas Trentino, Cisterna Volley, Sir Susa Scai Perugia, Tinet Prata di Pordenone); fixture rows themselves rendered elsewhere (start times carried from OLBG and flagged)"),
    ("https://www.plusliga.pl/table.html", "2026-10-23T20:10:00Z",
     "Polish league live-centre (redirects to tauronliga.pl): recent PlusLiga results read - Skra 3-1 Trefl Gdansk (17 Oct), ZAKSA 0-3 LUK Lublin (18 Oct), Norwid-Resovia 3-2 (17 Oct)"),
    ("https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/", "2026-10-23T20:35:00Z",
     "PDC (search-layer reads of pdc.tv articles): Machineseeker European Championship Westfalenhalle Dortmund 22-25 Oct, £750,000; Thu R1: Woodhouse 6-3 van Duijvenbode (nine-dart per pdc.tv headline), Bunting 6-5 Noppert, Menzies 6-3 Zonneveld, Price 6-2 Cross, Heta 6-5 Wade, Huybrechts 6-1 Searle, van Veen 6-4 Gilding (record European Tour average that weekend), Smith d. Sedlacek; Fri R1: Littler v O'Connor (19:15Z), Clayton v Springer, Doets v van Gerwen, Nijman v Schindler, Joyce v Wattimena, Ratajski v Chisnall, Aspinall v Reyes, Rock v Dobey; Sat afternoon R2: Smith/Heta v Wade/Heta winner bracket, van Veen v Woodhouse, Menzies/Price winner bracket, Bunting v Huybrechts; Humphries (world #2) absent from final R1 list (replaced by Huybrechts v Searle)"),
    ("https://www.olbg.com/betting-tips", "2026-10-23T19:35:00Z",
     "OLBG hub discovery: tip feed renders 'No tips found.' in the fetch channel tonight (platform irregularity); sport menu + editorial retained; event pages via ?event_id= render full tip blocks (see NYK-BOS read)"),
    ("https://www.olbg.com/betting-tips/Basketball/NBA/NBA/NY_Knicks_@_BOS_Celtics/4?event_id=534842", "2026-10-23T19:48:00Z",
     "OLBG event page NYK-BOS: ML BOS 5/6 (83%) v NYK 1/6; pointspread BOS -2.50 4/4; totals U221.5 3/4 v O221.5 1/4; tipster profit rows; tips flagged Expired pre-start when odds gone; OLBG hub times render America/New_York unlabeled (converted, flagged)"),
]

# --------------------------------------------------------------- helpers -----
def shrunk(wins, games):
    return (wins + 2.0) / (games + 4.0)


def log5(a, b):
    return (a * (1 - b)) / (a * (1 - b) + b * (1 - a))


def fair_american(p):
    if p <= 0:
        return None
    if p >= 1:
        return None
    if p > 0.5:
        return -100.0 * p / (1.0 - p)
    return 100.0 * (1.0 - p) / p


def fair_decimal(p):
    return 1.0 / p if p > 0 else None


def tier_for(p, market=""):
    am = fair_american(p)
    if p > 0.70 and am is not None and (-250.0 - 1e-6) <= am <= (10000.0 + 1e-6):
        return "High"
    if p > 0.7143:
        if market.startswith("match winner") or market in ("race winner", "matchup winner", "title winner", "to win the series"):
            return "Chalk (disclosed)"
        return "Out-of-band (disclosed)"
    return "Medium" if 0.55 <= p <= 0.70 else "Low"


def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def gaussian_ladder(expected_margin, sd):
    """Return rungs [(handicap, p_cover)] for both sides and totals ladders."""
    rungs = []
    for hc in (-8.5, -6.5, -4.5, -2.5, -1.5, 1.5, 2.5, 4.5, 6.5, 8.5):
        p = phi((expected_margin - hc) / sd) if expected_margin is not None else None
        rungs.append((hc, p))
    return rungs


def poisson_pmf(k, lam):
    return math.exp(-lam) * lam ** k / math.factorial(k)


def poisson_total_over(total, lam_a, lam_b):
    """P(A+B > total) for half-integer totals, scores conditioned on no tie is
    approximated by using independent Poisson and ignoring the tie mass shift."""
    lam = lam_a + lam_b
    k = int(math.floor(total + 1))
    s = 0.0
    for i in range(k, 60):
        s += poisson_pmf(i, lam)
    return s


def poisson_win(lam_a, lam_b):
    pa = 0.0
    for i in range(0, 40):
        for j in range(0, 40):
            if i > j:
                pa += poisson_pmf(i, lam_a) * poisson_pmf(j, lam_b)
    pab = 0.0
    for i in range(0, 40):
        pab += poisson_pmf(i, lam_a) * poisson_pmf(i, lam_b)
    return pa / (1.0 - pab)


def handicap_markets(fid, sport, match, an, hn, m_a, sd, rungs, model, note, label="handicap"):
    """Zero-vig rungs: (favourite -r) is paired with (underdog +r)."""
    for r in rungs:
        p_an = phi((m_a - r) / sd)
        S.append(sel(fid, sport, match, f"{label} {r:.1f}", f"{an} -{r:.1f}", p_an, model, note))
        S.append(sel(fid, sport, match, f"{label} {r:.1f}", f"{hn} +{r:.1f}", 1.0 - p_an, model, note))
        p_hn = phi((-m_a - r) / sd)
        S.append(sel(fid, sport, match, f"{label} {r:.1f} (other side)", f"{hn} -{r:.1f}", p_hn, model, note))
        S.append(sel(fid, sport, match, f"{label} {r:.1f} (other side)", f"{an} +{r:.1f}", 1.0 - p_hn, model, note))


def total_markets(fid, sport, match, line, p_over, model, note):
    S.append(sel(fid, sport, match, f"total {line}", "over", p_over, model, note))
    S.append(sel(fid, sport, match, f"total {line}", "under", 1.0 - p_over, model, note))


def sel(fixture_id, sport, match, market, selection, prob, model, note, counter=None):
    am = fair_american(prob)
    return {
        "fixture_id": fixture_id,
        "sport": sport,
        "match": match,
        "market": market,
        "selection": selection,
        "prob": round(prob, 4),
        "fair_decimal": round(fair_decimal(prob), 3),
        "fair_american": round(am, 1),
        "tier": tier_for(prob, market),
        "model": model,
        "note": note,
    }


# ------------------------------------------------------------- fixtures ------
F = []


def fx(fid, sport, slug, comp, start, home, away, venue, olbg, official, note, label, state="upcoming"):
    F.append({
        "id": fid, "sport": sport, "sport_slug": slug, "competition": comp,
        "start_utc": start, "home": home, "away": away, "venue": venue,
        "state": state,
        "olbg": olbg, "official": official, "note": note, "label": label,
    })


NHLS = "https://api-web.nhle.com/v1/schedule/2026-10-23"
NHLST = "https://api-web.nhle.com/v1/standings/2026-10-23"
URCT = "https://www.unitedrugby.com/latest/news/round-4-team-announcements/"

fx("65331685-H-01", "Ice Hockey", "ice-hockey", "NHL", "2026-10-24T00:00:00Z", "Chicago Blackhawks", "Montreal Canadiens",
   "United Center", {"listed": True, "url": "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/13", "rendered_time": "today 20:07 (America/New_York, unlabeled on hub)"},
   {"competition": "NHL", "home": "Blackhawks 3-6-0 (6 pts)", "away": "Canadiens 4-3-2 (10 pts)",
    "start_utc": "2026-10-24T00:00:00Z", "venue": "United Center", "game_state": "FUT", "game_id": "2026020166",
    "record_home": "3-6-0", "record_away": "4-3-2", "sources": [NHLS, NHLST], "read_utc": "2026-10-23T19:36:00Z"},
   "MTL 4-0-1 road split NOT applied (no-splits pricing policy).", "CHI-65331685-H-01")

fx("65331685-H-02", "Ice Hockey", "ice-hockey", "NHL", "2026-10-24T01:00:00Z", "Colorado Avalanche", "Tampa Bay Lightning",
   "Ball Arena", {"listed": True, "url": "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/13", "rendered_time": "today 21:00"},
   {"competition": "NHL", "home": "Avalanche 5-4-1 (11 pts)", "away": "Lightning 7-2-0 (14 pts)",
    "start_utc": "2026-10-24T01:00:00Z", "venue": "Ball Arena", "game_state": "FUT", "game_id": "2026020167",
    "record_home": "5-4-1", "record_away": "7-2-0", "sources": [NHLS, NHLST], "read_utc": "2026-10-23T19:36:00Z"},
   "TBL W3 streak; COL L2 streak (standings read).", "")

fx("65331685-H-03", "Ice Hockey", "ice-hockey", "NHL", "2026-10-24T17:00:00Z", "Philadelphia Flyers", "Anaheim Ducks",
   "Xfinity Mobile Arena", {"listed": True, "url": "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/13", "rendered_time": "tomorrow 13:00"},
   {"competition": "NHL", "home": "Flyers 3-6-3 (9 pts)", "away": "Ducks 4-6-0 (8 pts)",
    "start_utc": "2026-10-24T17:00:00Z", "venue": "Xfinity Mobile Arena", "game_state": "FUT", "game_id": "2026020168",
    "record_home": "3-6-3", "record_away": "4-6-0", "sources": [NHLS, NHLST], "read_utc": "2026-10-23T19:36:00Z"},
   "ANA on a five-game slide (L5); PHI W3.", "")

fx("65331685-H-04", "Ice Hockey", "ice-hockey", "NHL", "2026-10-24T19:30:00Z", "New Jersey Devils", "Los Angeles Kings",
   "Prudential Center", {"listed": False},
   {"competition": "NHL", "home": "Devils 6-4-0 (12 pts)", "away": "Kings 2-4-2 (6 pts)",
    "start_utc": "2026-10-24T19:30:00Z", "venue": "Prudential Center", "game_state": "FUT", "game_id": "2026020169",
    "record_home": "6-4-0", "record_away": "2-4-2", "sources": [NHLS, NHLST], "read_utc": "2026-10-23T19:36:00Z"},
   "Not on the OLBG discovery list; official slate only.", "")

fx("65331685-H-05", "Ice Hockey", "ice-hockey", "NHL", "2026-10-24T23:00:00Z", "Edmonton Oilers", "Toronto Maple Leafs",
   "Rogers Place", {"listed": True, "url": "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/13", "rendered_time": "tomorrow 19:00"},
   {"competition": "NHL", "home": "Oilers 8-1-1 (17 pts)", "away": "Maple Leafs 6-4-2 (14 pts)",
    "start_utc": "2026-10-24T23:00:00Z", "venue": "Rogers Place", "game_state": "FUT", "game_id": "2026020176",
    "record_home": "8-1-1", "record_away": "6-4-2", "sources": [NHLS, NHLST], "read_utc": "2026-10-23T19:36:00Z"},
   "EDM W3, TOR W3; league-best .850 point percentage.", "")

fx("65331685-H-06", "Ice Hockey", "ice-hockey", "NHL", "2026-10-24T23:00:00Z", "Columbus Blue Jackets", "Vegas Golden Knights",
   "Nationwide Arena", {"listed": False},
   {"competition": "NHL", "home": "Blue Jackets 3-5-0 (6 pts)", "away": "Golden Knights 8-4-0 (16 pts)",
    "start_utc": "2026-10-24T23:00:00Z", "venue": "Nationwide Arena", "game_state": "FUT", "game_id": "2026020174",
    "record_home": "3-5-0", "record_away": "8-4-0", "sources": [NHLS, NHLST], "read_utc": "2026-10-23T19:36:00Z"},
   "", "")

fx("65331685-H-07", "Ice Hockey", "ice-hockey", "NHL", "2026-10-24T23:00:00Z", "St. Louis Blues", "Carolina Hurricanes",
   "Enterprise Center", {"listed": False},
   {"competition": "NHL", "home": "Blues 5-4-1 (11 pts)", "away": "Hurricanes 8-2-2 (18 pts)",
    "start_utc": "2026-10-24T23:00:00Z", "venue": "Enterprise Center", "game_state": "FUT", "game_id": "2026020175",
    "record_home": "5-4-1", "record_away": "8-2-2", "sources": [NHLS, NHLST], "read_utc": "2026-10-23T19:36:00Z"},
   "CAR top of the overall table.", "")

fx("65331685-H-08", "Ice Hockey", "ice-hockey", "NHL", "2026-10-24T23:00:00Z", "San Jose Sharks", "Boston Bruins",
   "SAP Center", {"listed": True, "url": "https://www.olbg.com/betting-tips/Ice_Hockey/NHL/13", "rendered_time": "tomorrow 19:00"},
   {"competition": "NHL", "home": "Sharks 6-4-1 (13 pts)", "away": "Bruins 8-2-1 (17 pts)",
    "start_utc": "2026-10-24T23:00:00Z", "venue": "SAP Center", "game_state": "FUT", "game_id": None,
    "record_home": "6-4-1", "record_away": "8-2-1", "sources": [NHLST], "read_utc": "2026-10-23T19:36:00Z"},
   "Game id not captured in schedule chunks read this session (records verified via standings).", "")

fx("65331685-B-01", "Baseball", "baseball", "MLB World Series Game 1", "2026-10-24T00:00:00Z", "Milwaukee Brewers", "Tampa Bay Rays",
   "American Family Field", {"listed": True, "url": "https://www.olbg.com/betting-tips/Baseball/12", "rendered_time": "today 20:00"},
   {"competition": "World Series G1", "home": "Brewers 103-59 (NL)", "away": "Rays 98-64 (AL)",
    "start_utc": "2026-10-24T00:00:00Z", "venue": "American Family Field", "game_state": "Scheduled",
    "game_id": "849805", "record_home": "103-59", "record_away": "98-64",
    "sources": ["https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-29&hydrate=team,probablePitcher,linescore",
                "https://statsapi.mlb.com/api/v1/standings?leagueId=103,104&season=2026",
                "https://statsapi.mlb.com/api/v1.1/game/849805/feed/live"],
    "read_utc": "2026-10-23T20:05:00Z"},
   "Probables Nick Martinez (TB) v Jacob Misiorowski (MIL); ifNecessary=N so conditional pricing allowed; series 0-0.", "")

fx("65331685-B-02", "Baseball", "baseball", "MLB World Series Game 2", "2026-10-25T00:00:00Z", "Milwaukee Brewers", "Tampa Bay Rays",
   "American Family Field", {"listed": True, "url": "https://www.olbg.com/betting-tips/Baseball/12", "rendered_time": "tomorrow 20:00"},
   {"competition": "World Series G2", "home": "Brewers 103-59 (NL)", "away": "Rays 98-64 (AL)",
    "start_utc": "2026-10-25T00:00:00Z", "venue": "American Family Field", "game_state": "Scheduled",
    "game_id": "849802", "record_home": "103-59", "record_away": "98-64",
    "sources": ["https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-29&hydrate=team,probablePitcher,linescore"],
    "read_utc": "2026-10-23T19:38:00Z"},
   "Probables Drew Rasmussen (TB) v Logan Henderson (MIL).", "")

fx("65331685-B-03", "Baseball", "baseball", "MLB World Series Game 3", "2026-10-27T00:00:00Z", "Tampa Bay Rays", "Milwaukee Brewers",
   "Tropicana Field", {"listed": True, "url": "https://www.olbg.com/betting-tips/Baseball/12", "rendered_time": "2026-10-27 20:00"},
   {"competition": "World Series G3", "home": "Rays 98-64 (AL)", "away": "Brewers 103-59 (NL)",
    "start_utc": "2026-10-27T00:00:00Z", "venue": "Tropicana Field", "game_state": "Scheduled",
    "game_id": "849804", "record_home": "98-64", "record_away": "103-59",
    "sources": ["https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-23&endDate=2026-10-29&hydrate=team,probablePitcher,linescore"],
    "read_utc": "2026-10-23T19:38:00Z"},
   "Probable pitchers not captured for G3 (left blank).", "")

NBA = "https://www.nba.com/games?date=2026-10-23"
for fid, t, home, away, hr, ar, gid in [
    ("65331685-K-01", "2026-10-23T23:00:00Z", "Boston Celtics", "New York Knicks", "0-1", "0-1", "nyk-vs-bos-0022600008"),
    ("65331685-K-02", "2026-10-23T23:00:00Z", "Orlando Magic", "Minnesota Timberwolves", "0-1", "1-0", "min-vs-orl-0022600096"),
    ("65331685-K-03", "2026-10-23T23:00:00Z", "Indiana Pacers", "Dallas Mavericks", "1-0", "0-1", "dal-vs-ind-0022600095"),
    ("65331685-K-04", "2026-10-24T02:00:00Z", "Golden State Warriors", "Memphis Grizzlies", "0-1", "1-0", "mem-vs-gsw-0022600101"),
    ("65331685-K-05", "2026-10-23T23:00:00Z", "Milwaukee Bucks", "Chicago Bulls", "0-1", "0-1", "chi-vs-mil-0022600099"),
    ("65331685-K-06", "2026-10-23T23:00:00Z", "Washington Wizards", "Toronto Raptors", "1-0", "1-0", "tor-vs-was-0022600097"),
    ("65331685-K-07", "2026-10-23T23:00:00Z", "Charlotte Hornets", "Atlanta Hawks", "1-0", "1-0", "atl-vs-cha-0022600094"),
    ("65331685-K-08", "2026-10-24T00:00:00Z", "Miami Heat", "Detroit Pistons", "0-1", "1-0", "det-vs-mia-0022600098"),
    ("65331685-K-09", "2026-10-24T01:30:00Z", "San Antonio Spurs", "Houston Rockets", "0-1", "1-0", "hou-vs-sas-0022600009"),
    ("65331685-K-10", "2026-10-24T01:30:00Z", "Utah Jazz", "New Orleans Pelicans", "0-1", "0-1", "nop-vs-uta-0022600100"),
    ("65331685-K-11", "2026-10-24T02:00:00Z", "Los Angeles Lakers", "LA Clippers", "1-0", "1-0", "lac-vs-lal-0022600102"),
    ("65331685-K-12", "2026-10-24T02:00:00Z", "Sacramento Kings", "Portland Trail Blazers", "0-1", "1-0", "por-vs-sac-0022600103"),
]:
    fx(fid, "Basketball", "basketball", "NBA", t, home, away, "NBA arena",
       {"listed": fid in ("65331685-K-01", "65331685-K-02", "65331685-K-03", "65331685-K-04"),
        "url": "https://www.olbg.com/betting-tips/Basketball/4", "rendered_time": "today 19:00"},
       {"competition": "NBA", "home": f"{home} {hr}", "away": f"{away} {ar}",
        "start_utc": t, "venue": "NBA arena", "game_state": "PREGAME", "game_id": gid,
        "record_home": hr, "record_away": ar, "sources": [NBA], "read_utc": "2026-10-23T19:38:00Z"},
       "Season records are 1-2 game samples; Beta(2,2) shrinkage dominates.", "")

for fid, t, home, away, comp, note, lbl in [
    ("65331685-R-01", "2026-10-24T11:45:00Z", "Vodacom Bulls", "Ulster Rugby", "URC Round 4",
     "Bulls: Pollard, Coetzee (capt), Louw; Ulster: Stockdale, McCloskey, Stewart (capt), Augustus.", ""),
    ("65331685-R-02", "2026-10-24T14:00:00Z", "DHL Stormers", "Scarlets", "URC Round 4",
     "Stormers: Feinberg-Mngomezulu, Roos, de Villiers (capt); Scarlets: Macleod (capt), Anscombe bench; Davies quoted on the Scarlets' impressive start.", ""),
    ("65331685-R-03", "2026-10-24T14:00:00Z", "Benetton Rugby", "Glasgow Warriors", "URC Round 4",
     "Glasgow: Steyn (capt), Tuipulotu, Fagerson, Darge; Benetton: Umaga, Lynagh, Lamaro (capt).", ""),
    ("65331685-R-04", "2026-10-24T17:00:00Z", "Leinster Rugby", "Munster Rugby", "URC Round 4",
     "Aviva Stadium. Leinster: Keenan, Henshaw, Furlong, Ryan, van der Flier, Sheehan (capt), Gibson-Park. Munster: Beirne (capt), Coombes, Casey, Nankivell. McMillan quotes Leinster's experience at the Aviva.", ""),
    ("65331685-R-05", "2026-10-24T18:00:00Z", "Ospreys", "Dragons RFC", "URC Round 4",
     "First competitive URC fixture at the new St Helen's home per URC preview; Ospreys: Watkin, Morris; Dragons: Dyer, Lewis, Carter (capt).", ""),
]:
    rec = {
        "65331685-R-01": ("2-0-1 (126-54)", "0-2-1 (88-93)"),
        "65331685-R-02": ("2-0-1 (81-54)", "1-0-2 (68-85)"),
        "65331685-R-03": ("0-1-2 (64-68)", "2-1-0 (95-72)"),
        "65331685-R-04": ("1-0-2 (75-58)", "1-1-1 (72-74)"),
        "65331685-R-05": ("1-0-2 (81-107)", "1-1-1 (88-83)"),
    }[fid]
    fx(fid, "Rugby Union", "rugby-union", comp, t, home, away, "URC venue",
       {"listed": True, "url": "https://www.olbg.com/betting-tips/Rugby_Union/9", "rendered_time": "tomorrow"},
       {"competition": comp, "home": f"{home} {rec[0]}", "away": f"{away} {rec[1]}",
        "start_utc": t, "venue": "URC venue", "game_state": "Scheduled", "game_id": None,
        "record_home": rec[0], "record_away": rec[1],
        "sources": [URCT, "https://stats.unitedrugby.com/match-centre/table/"], "read_utc": "2026-10-23T20:35:00Z"},
       note, "")

RL = "https://www.nrl.com/news/2026/10/20/world-cup-team-lists-mens-round-2/"
fx("65331685-L-01", "Rugby League", "rugby-league", "RLWC2026 Men's Round 2", "2026-10-24T04:25:00Z", "Papua New Guinea", "Samoa",
   "Santos National Football Stadium, Port Moresby", {"listed": True, "url": "https://www.olbg.com/betting-tips/Rugby_League/10", "rendered_time": "tomorrow 00:25"},
   {"competition": "RLWC2026 R2", "home": "PNG (Biondi-Odo, Rhyse Martin, de Belin)", "away": "Samoa (Tabuai-Fidow, To'o, Tago, Crichton, Luai)",
    "start_utc": "2026-10-24T04:25:00Z", "venue": "Santos National Football Stadium", "game_state": "Scheduled",
    "game_id": None, "record_home": "", "record_away": "",
    "sources": [RL], "read_utc": "2026-10-23T19:45:00Z"},
   "Samoa winger Deine Mariner out (hamstring); Sua Fa'alogo promoted after four tries against France.", "")

fx("65331685-L-02", "Rugby League", "rugby-league", "RLWC2026 Men's Round 2", "2026-10-24T06:35:00Z", "England", "France",
   "HBF Park, Perth", {"listed": True, "url": "https://www.olbg.com/betting-tips/Rugby_League/10", "rendered_time": "tomorrow 02:35"},
   {"competition": "RLWC2026 R2", "home": "England (Brimson, Young, Farnworth, G Williams, Smith, Radley, Thompson)", "away": "France (Lacans, Fages, Garcia)",
    "start_utc": "2026-10-24T06:35:00Z", "venue": "HBF Park", "game_state": "Scheduled", "game_id": None,
    "record_home": "", "record_away": "", "sources": [RL], "read_utc": "2026-10-23T19:45:00Z"},
   "Morgan Knowles injured pre-tournament; Luke Thompson starts at prop; Matty Ashton in for Zach Eckersley in the 24-hour update.", "")

fx("65331685-L-03", "Rugby League", "rugby-league", "RLWC2026 Women's Round 2", "2026-10-24T09:05:00Z", "Australia (Jillaroos)", "England",
   "HBF Park, Perth", {"listed": True, "url": "https://www.olbg.com/betting-tips/Rugby_League/10", "rendered_time": "tomorrow 05:05"},
   {"competition": "RLWC2026 WR2", "home": "Jillaroos", "away": "England",
    "start_utc": "2026-10-24T09:05:00Z", "venue": "HBF Park", "game_state": "Scheduled", "game_id": None,
    "record_home": "", "record_away": "",
    "sources": ["https://www.nrl.com/news/2026/10/20/world-cup-team-lists-womens-round-2/"], "read_utc": "2026-10-23T20:15:00Z"},
   "England backrower Jasmin Strange out for the tournament (ACL at training); Lucy Murray starts. Start time carried from OLBG render (flagged).", "")

fx("65331685-L-04", "Rugby League", "rugby-league", "RLWC2026 Men's Round 2", "2026-10-25T05:05:00Z", "New Zealand", "Cook Islands",
   "One NZ Stadium, Christchurch", {"listed": True, "url": "https://www.olbg.com/betting-tips/Rugby_League/10", "rendered_time": "Sunday 01:05"},
   {"competition": "RLWC2026 R2", "home": "New Zealand (Kini, Isaako, Nicoll-Klokstad, Hughes, Nikorima)", "away": "Cook Islands (Holmes, Iro)",
    "start_utc": "2026-10-25T05:05:00Z", "venue": "One NZ Stadium", "game_state": "Scheduled", "game_id": None,
    "record_home": "", "record_away": "", "sources": [RL], "read_utc": "2026-10-23T19:45:00Z"},
   "", "")

fx("65331685-L-05", "Rugby League", "rugby-league", "RLWC2026 Men's Round 2", "2026-10-25T09:05:00Z", "Australia", "Fiji",
   "Perth", {"listed": True, "url": "https://www.olbg.com/betting-tips/Rugby_League/10", "rendered_time": "Sunday 05:05"},
   {"competition": "RLWC2026 R2", "home": "Australia", "away": "Fiji", "start_utc": "2026-10-25T09:05:00Z",
    "venue": "Perth", "game_state": "Scheduled", "game_id": None, "record_home": "", "record_away": "",
    "sources": [RL], "read_utc": "2026-10-23T19:45:00Z"},
   "Team lists for this fixture sit in a later chunk of the team-lists page that was not read; row retained from the OLBG slate and flagged.", "")

ICC = "https://www.icc-cricket.com/fixtures-results"
fx("65331685-C-01", "Cricket", "cricket", "NZ v India 2nd T20I", "2026-10-24T07:00:00Z", "New Zealand", "India",
   "Hagley Oval, Christchurch", {"listed": True, "url": "https://www.olbg.com/betting-tips/Cricket/7", "rendered_time": "tomorrow 03:00"},
   {"competition": "T20I series (India lead 1-0)", "home": "New Zealand", "away": "India (Iyer c)",
    "start_utc": "2026-10-24T07:00:00Z", "venue": "Hagley Oval", "game_state": "Upcoming", "game_id": "271647",
    "record_home": "0-1 in series", "record_away": "1-0 in series",
    "sources": [ICC, "https://www.icc-cricket.com/news/injury-blow-for-india-ahead-of-second-t20i-with-new-zealand"],
    "read_utc": "2026-10-23T20:15:00Z"},
   "India chased 226 in game 1 (Samson 67, Iyer 42, Dhir 42*); Ishan Kishan out (right adductor strain), Kushagra cover.", "")

fx("65331685-C-02", "Cricket", "cricket", "Pakistan ODI Tri-Series Match 4", "2026-10-25T08:00:00Z", "Pakistan", "England",
   "Gaddafi Stadium, Lahore", {"listed": True, "url": "https://www.olbg.com/betting-tips/Cricket/7", "rendered_time": "Sunday 04:00"},
   {"competition": "ODI Tri-Series 2026/27", "home": "Pakistan (Shaheen Afridi c)", "away": "England (Harry Brook c)",
    "start_utc": "2026-10-25T08:00:00Z", "venue": "Gaddafi Stadium", "game_state": "Upcoming", "game_id": "1550716",
    "record_home": "2-0 in tri-series", "record_away": "0-1 in tri-series",
    "sources": ["https://www.cricinfo.com/series/pakistan-odi-tri-series-2026-27-1550706/pakistan-vs-england-4th-match-1550716/live-cricket-score"],
    "read_utc": "2026-10-23T20:38:00Z"},
   "Pakistan beat Sri Lanka by 37 runs and England by 87 runs (302/9 v 215) inside five days.", "")

for fid, t, home, away, cid in [
    ("65331685-C-03", "2026-10-24T06:45:00Z", "Denmark", "Kuwait", "275474"),
    ("65331685-C-04", "2026-10-24T07:30:00Z", "Namibia", "Ireland", "275411"),
    ("65331685-C-05", "2026-10-24T05:30:00Z", "United Arab Emirates", "Netherlands", "275767"),
]:
    fx(fid, "Cricket", "cricket", "ICC List A / League 2", t, home, away, "ICC event venue",
       {"listed": False},
       {"competition": "ICC fixture", "home": home, "away": away, "start_utc": t, "venue": "ICC event venue",
        "game_state": "Upcoming", "game_id": cid, "record_home": "", "record_away": "",
        "sources": [ICC], "read_utc": "2026-10-23T19:55:00Z"},
       "Listed on the official ICC fixtures page (times converted from the tool clock, flagged).", "")

fx("65331685-S-01", "Snooker", "snooker", "BetVictor Northern Ireland Open SF", "2026-10-24T12:00:00Z", "Kyren Wilson", "Sam Craigie",
   "Belfast", {"listed": True, "url": "https://www.olbg.com/betting-tips/Snooker/8", "rendered_time": "tomorrow 08:00"},
   {"competition": "NI Open SF", "home": "Wilson (QF 6-1 McGill, R3 4-3 Pang)", "away": "Craigie (QF 6-2 Slessor, R3 4-2 Selt)",
    "start_utc": "2026-10-24T12:00:00Z", "venue": "Belfast", "game_state": "Scheduled", "game_id": None,
    "record_home": "frames 10-4 this event (read matches)", "record_away": "frames 18-10 this event (read matches)",
    "sources": ["https://www.wst.tv/matches/"], "read_utc": "2026-10-23T19:55:00Z"},
   "Frame records cover only the matches read this session (Wilson R3+QF; Craigie R2-R4 path read).", "")

fx("65331685-D-01", "Darts", "darts", "Machineseeker European Championship R2", "2026-10-24T12:00:00Z", "Gian van Veen", "Luke Woodhouse",
   "Westfalenhalle, Dortmund", {"listed": True, "url": "https://www.olbg.com/betting-tips/Darts/15", "rendered_time": "tomorrow 08:00"},
   {"competition": "EC 2026 R2", "home": "van Veen (R1 6-4 Gilding; defending champion)", "away": "Woodhouse (R1 6-3 van Duijvenbode; nine-darter)",
    "start_utc": "2026-10-24T12:00:00Z", "venue": "Westfalenhalle", "game_state": "Scheduled", "game_id": None,
    "record_home": "1-0 (6-4)", "record_away": "1-0 (6-3)",
    "sources": ["https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/"],
    "read_utc": "2026-10-23T20:35:00Z"},
   "PDC article bodies sat behind a consent wall in direct fetches; schedule/results taken from search-layer reads of pdc.tv (flagged).", "")

fx("65331685-D-02", "Darts", "darts", "Machineseeker European Championship R2", "2026-10-24T13:00:00Z", "Stephen Bunting", "Kim Huybrechts",
   "Westfalenhalle, Dortmund", {"listed": True, "url": "https://www.olbg.com/betting-tips/Darts/15", "rendered_time": "tomorrow 09:00"},
   {"competition": "EC 2026 R2", "home": "Bunting (R1 6-5 Noppert)", "away": "Huybrechts (R1 6-1 Searle)",
    "start_utc": "2026-10-24T13:00:00Z", "venue": "Westfalenhalle", "game_state": "Scheduled", "game_id": None,
    "record_home": "1-0 (6-5)", "record_away": "1-0 (6-1)",
    "sources": ["https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/"],
    "read_utc": "2026-10-23T20:35:00Z"},
   "Huybrechts inherited the slot in the published Thursday list after Humphries' absence (flagged).", "")

fx("65331685-D-03", "Darts", "darts", "Machineseeker European Championship R2", "2026-10-24T14:00:00Z", "Cameron Menzies", "Gerwyn Price",
   "Westfalenhalle, Dortmund", {"listed": True, "url": "https://www.olbg.com/betting-tips/Darts/15", "rendered_time": "tomorrow 10:00"},
   {"competition": "EC 2026 R2", "home": "Menzies (R1 6-3 Zonneveld)", "away": "Price (R1 6-2 Cross)",
    "start_utc": "2026-10-24T14:00:00Z", "venue": "Westfalenhalle", "game_state": "Scheduled", "game_id": None,
    "record_home": "1-0 (6-3)", "record_away": "1-0 (6-2)",
    "sources": ["https://www.pdc.tv/news/2026/october/19/2026-machineseeker-european-championship-schedule-confirmed/"],
    "read_utc": "2026-10-23T20:35:00Z"},
   "", "")

fx("65331685-G-01", "Golf", "golf", "Butterfield Bermuda Championship R3 matchup", "2026-10-24T11:30:00Z", "Corey Conners", "Seamus Power",
   "Port Royal GC", {"listed": True, "url": "https://www.olbg.com/betting-tips/Golf/5", "rendered_time": "tomorrow 07:30"},
   {"competition": "Bermuda Championship", "home": "Conners -12 (63-67)", "away": "Power -12 (66-64)",
    "start_utc": "2026-10-24T11:30:00Z", "venue": "Port Royal GC", "game_state": "R2 in progress at read", "game_id": None,
    "record_home": "R1 63, R2 67", "record_away": "R1 66, R2 64",
    "sources": ["https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/leaderboard"],
    "read_utc": "2026-10-23T19:55:00Z"},
   "18-hole matchup at published OLBG time; both men tied at -12 after 36 holes. Bookmaker odds column on the leaderboard left blank per repo policy.", "")

fx("65331685-G-02", "Golf", "golf", "Butterfield Bermuda Championship R3 matchup", "2026-10-24T11:45:00Z", "Denny McCarthy", "Emiliano Grillo",
   "Port Royal GC", {"listed": True, "url": "https://www.olbg.com/betting-tips/Golf/5", "rendered_time": "tomorrow 07:45"},
   {"competition": "Bermuda Championship", "home": "McCarthy -11 (68-63)", "away": "Grillo",
    "start_utc": "2026-10-24T11:45:00Z", "venue": "Port Royal GC", "game_state": "R2 in progress at read", "game_id": None,
    "record_home": "R1 68, R2 63", "record_away": "",
    "sources": ["https://www.pgatour.com/tournaments/2026/butterfield-bermuda-championship/R2026528/leaderboard"],
    "read_utc": "2026-10-23T19:55:00Z"},
   "Grillo's round scores were beyond the leaderboard chunk read this session (blank, flagged).", "")

fx("65331685-G-03", "Golf", "golf", "DP World Tour Genesis Championship matchup", "2026-10-24T04:00:00Z", "Matthew Jarvis", "Adrien Rozner",
   "South Korea", {"listed": True, "url": "https://www.olbg.com/betting-tips/Golf/5", "rendered_time": "tomorrow 00:00"},
   {"competition": "Genesis Championship", "home": "Jarvis", "away": "Rozner", "start_utc": "2026-10-24T04:00:00Z",
    "venue": "South Korea", "game_state": "Scheduled", "game_id": None, "record_home": "", "record_away": "",
    "sources": [], "read_utc": None},
   "Official leaderboard for this event was not read this session (unverified, blank inputs).", "unverified")

fx("65331685-A-01", "Gaelic Sports", "gaelic-sports", "Hurling Shinty International", "2026-10-24T17:00:00Z", "Ireland", "Scotland",
   "SuperValu Pairc Ui Chaoimh", {"listed": True, "url": "https://www.olbg.com/betting-tips/Hurling/26", "rendered_time": "tomorrow 13:00"},
   {"competition": "2026 Hurling Shinty International", "home": "Ireland", "away": "Scotland",
    "start_utc": "2026-10-24T17:00:00Z", "venue": "SuperValu Pairc Ui Chaoimh", "game_state": "Scheduled", "game_id": None,
    "record_home": "", "record_away": "",
    "sources": ["https://munster.gaa.ie/fixtures/events-calendar/"], "read_utc": "2026-10-23T20:15:00Z"},
   "Kickoff 18:00 Irish local on the official events calendar (converted). Camogie Shinty International precedes it at 16:00.", "")

fx("65331685-A-02", "Gaelic Sports", "gaelic-sports", "Kerry County Senior Football Championship Final", "2026-10-25T14:00:00Z", "Dr Crokes", "Kenmare Shamrocks",
   "Fitzgerald Stadium, Killarney", {"listed": True, "url": "https://www.olbg.com/betting-tips/Gaelic_Football/25", "rendered_time": "Sunday 10:00"},
   {"competition": "Kerry SFC Final (Bishop Moynihan Cup)", "home": "Dr Crokes (14 titles, last 2024)", "away": "Kenmare Shamrocks (0 titles, first final)",
    "start_utc": "2026-10-25T14:00:00Z", "venue": "Fitzgerald Stadium", "game_state": "Scheduled", "game_id": None,
    "record_home": "", "record_away": "",
    "sources": ["https://munster.gaa.ie/fixtures/events-calendar/", "https://en.wikipedia.org/wiki/2026_Kerry_Senior_Football_Championship"],
    "read_utc": "2026-10-23T20:38:00Z"},
   "First meeting of these clubs in the Kerry final (cross-referenced fixture note); referee S Joy (Laune Rangers) per the championship fixture listing.", "")

fx("65331685-A-03", "Gaelic Sports", "gaelic-sports", "Waterford SFC Final", "2026-10-25T14:30:00Z", "Rathgormack", "The Nire",
   "Fraher Field, Dungarvan", {"listed": False},
   {"competition": "Waterford SFC Final", "home": "Rathgormack", "away": "The Nire", "start_utc": "2026-10-25T14:30:00Z",
    "venue": "Fraher Field", "game_state": "Scheduled", "game_id": None, "record_home": "", "record_away": "",
    "sources": ["https://munster.gaa.ie/fixtures/events-calendar/"], "read_utc": "2026-10-23T20:15:00Z"},
   "", "")

fx("65331685-X-01", "Greyhounds", "greyhounds", "Coral 100 Champion Stakes Final (575m)", "2026-10-23T20:13:00Z", "Grouchos Gregor", "Final field",
   "Romford", {"listed": True, "url": "https://www.olbg.com/betting-tips/Greyhounds/28", "rendered_time": "today 21:13"},
   {"competition": "Coral 100 Champion Stakes Final", "home": "Grouchos Gregor (Wilton)", "away": "Aayamza Legend / Bubbly Holly / Fortanach Col",
    "start_utc": "2026-10-23T20:13:00Z", "venue": "Romford", "game_state": "Scheduled (last race of the card)", "game_id": None,
    "record_home": "semi 35.36 (-20) fastest", "record_away": "semis 35.75 / 35.95 / 2nd in Grouchos' semi",
    "sources": ["https://www.gbgb.org.uk/category-one-glory-beckons-in-coral-100-champion-stakes-final/"],
    "read_utc": "2026-10-23T20:15:00Z"},
   "Category One final, £20,000 to the winner. Newinn Jolly withdrawn (urine infection); four-dog field. OLBG ran a player-versus-field market here (synthetic, flagged).", "")

fx("65331685-M-01", "Motor Racing", "motor-racing", "F1 United States GP (COTA)", "2026-10-25T20:00:00Z", "Race winner", "Circuit of The Americas",
   "COTA, Austin", {"listed": True, "url": "https://www.olbg.com/betting-tips/Motor_Racing/14", "rendered_time": "Sunday 16:00"},
   {"competition": "F1 US GP 2026 (Round 18)", "home": "Verstappen won Malaysia + Singapore", "away": "Antonelli leads the standings",
    "start_utc": "2026-10-25T20:00:00Z", "venue": "COTA", "game_state": "Scheduled", "game_id": None,
    "record_home": "4 of last 5 US GPs won by Verstappen", "record_away": "Antonelli can clinch the title this weekend",
    "sources": ["https://www.formula1.com/en/latest/article/need-to-know-the-most-important-facts-stats-and-trivia-ahead-of-the-2026-united-states-grand-prix.3yCUtnzlXLwOvhVtmsdVRK"],
    "read_utc": "2026-10-23T19:55:00Z"},
   "Qualifying Sat 24 Oct (OLBG render 21:00Z). Title-clinch scenario per F1: Antonelli champion if he wins and Russell finishes ninth or lower and Hamilton fifth or lower.", "")

fx("65331685-M-02", "Motor Racing", "motor-racing", "F1 United States GP Qualifying", "2026-10-24T21:00:00Z", "Qualifying winner", "Circuit of The Americas",
   "COTA, Austin", {"listed": True, "url": "https://www.olbg.com/betting-tips/Motor_Racing/14", "rendered_time": "tomorrow 17:00"},
   {"competition": "F1 US GP 2026 Qualifying", "home": "Last five US GP poles: Verstappen (2025), Norris (2024), Leclerc (2023), Sainz (2022), Verstappen (2021)",
    "away": "Lap record Leclerc 1m36.169 (2019)", "start_utc": "2026-10-24T21:00:00Z", "venue": "COTA",
    "game_state": "Scheduled", "game_id": None, "record_home": "", "record_away": "",
    "sources": ["https://www.formula1.com/en/latest/article/need-to-know-the-most-important-facts-stats-and-trivia-ahead-of-the-2026-united-states-grand-prix.3yCUtnzlXLwOvhVtmsdVRK"],
    "read_utc": "2026-10-23T19:55:00Z"},
   "Pole run to T1 braking point 230m; track-limits hotspot at T19 per the official circuit guide notes.", "")

fx("65331685-T-01", "Tennis", "tennis", "WTA Ningbo SF", "2026-10-24T09:30:00Z", "Elena Rybakina", "Diana Shnaider",
   "Ningbo", {"listed": True, "url": "https://www.olbg.com/betting-tips/Tennis/3", "rendered_time": "tomorrow 05:30"},
   {"competition": "WTA Ningbo 500 SF", "home": "Rybakina (rank 1, seed 1)", "away": "Shnaider (rank 13, seed 6)",
    "start_utc": "2026-10-24T09:30:00Z", "venue": "Ningbo", "game_state": "Scheduled", "game_id": None,
    "record_home": "d. Kudermetova, d. Kawa (draw path)", "record_away": "d. Kalinina, d. Eala, d. Putintseva 7-5 7-6(4)",
    "sources": ["https://wtafiles.wtatennis.com/pdf/draws/2026/2092/MDS.pdf"], "read_utc": "2026-10-23T20:15:00Z"},
   "Swiatek withdrew (left thigh) before the event; start time from OLBG render (flagged).", "")

fx("65331685-T-02", "Tennis", "tennis", "WTA Osaka SF", "2026-10-24T04:30:00Z", "Katie Boulter", "Katerina Siniakova",
   "Osaka", {"listed": True, "url": "https://www.olbg.com/betting-tips/Tennis/3", "rendered_time": "tomorrow 00:30"},
   {"competition": "WTA Osaka 250 SF", "home": "Boulter (rank 54, seed 8)", "away": "Siniakova",
    "start_utc": "2026-10-24T04:30:00Z", "venue": "Osaka", "game_state": "Scheduled", "game_id": None,
    "record_home": "d. Sakatsume 6-3 6-1, d. Golubic 3-6 6-3 6-3", "record_away": "d. Shibahara, d. Linette, d. Stearns 6-4 0-6 4-0 ret",
    "sources": ["https://wtafiles.wtatennis.com/pdf/draws/2026/405/MDS.pdf"], "read_utc": "2026-10-23T20:16:00Z"},
   "Stearns (seed 2) retired with a foot injury in the QF; start time from OLBG render (flagged).", "")

for fid, t, home, away, comp, srcs, note, lbl in [
    ("65331685-V-01", "2026-10-24T16:00:00Z", "PGE GiEK Skra Belchatow", "PGE Projekt Warszawa", "PlusLiga",
     ["https://www.plusliga.pl/table.html"], "Skra beat Trefl Gdansk 3-1 on 17 Oct (read); Projekt opened 3:1 (cross-referenced). OLBG-rendered start time flagged.", ""),
    ("65331685-V-02", "2026-10-24T17:30:00Z", "VC Giesen", "Berlin Recycling Volleys", "Bundesliga",
     [], "Official Bundesliga source not read this session (unverified).", "unverified"),
    ("65331685-V-03", "2026-10-25T16:00:00Z", "Itas Trentino", "Cisterna Volley", "SuperLega",
     ["https://www.legavolley.it/calendario/?idCampionato=999"], "Both won their SuperLega openers on 18 Oct (Trentino 3-0 Modena, Cisterna 3-0 Milano; results cross-referenced).", ""),
    ("65331685-V-04", "2026-10-25T17:00:00Z", "Sir Susa Scai Perugia", "Tinet Prata di Pordenone", "SuperLega",
     ["https://www.legavolley.it/calendario/?idCampionato=999"], "Perugia (defending champions) needed five sets at Cuneo in R1; Prata won its top-flight debut 3-1 over Monza (cross-referenced).", ""),
    ("65331685-V-05", "2026-10-25T17:00:00Z", "Chelm", "Asseco Resovia Rzeszow", "PlusLiga",
     [], "Resovia lost a five-setter at Norwid on 17 Oct (read on the Polish league live-centre); official fixture row not read (flagged).", "unverified"),
]:
    fx(fid, "Volleyball", "volleyball", comp, t, home, away, "Club venue",
       {"listed": True, "url": "https://www.olbg.com/betting-tips/Volleyball/21", "rendered_time": "weekend"},
       {"competition": comp, "home": home, "away": away, "start_utc": t, "venue": "Club venue",
        "game_state": "Scheduled", "game_id": None, "record_home": "", "record_away": "",
        "sources": srcs, "read_utc": "2026-10-23T20:10:00Z" if srcs else None},
       note, lbl)

for fid, t, home, away, comp, note, lbl in [
    ("65331685-N-01", "2026-10-24T17:00:00Z", "HBC Nantes", "Chambery Savoie Mont Blanc HB", "Daikin StarLigue J08",
     "Official LNH kickoff 19:00 CEST (converted 17:00Z); OLBG rendered 18:00Z (one-hour discrepancy, flagged).", ""),
    ("65331685-N-02", "2026-10-25T14:00:00Z", "Saint-Raphael Var Handball", "Paris Saint-Germain Handball", "Daikin StarLigue J08",
     "LNH calendar kickoff 16:00 local Sunday (14:00Z).", ""),
    ("65331685-N-03", "2026-10-25T15:00:00Z", "Montpellier Handball", "Saran Loiret Handball", "Daikin StarLigue J08",
     "LNH calendar kickoff 17:00 local Sunday (15:00Z).", ""),
    ("65331685-N-04", "2026-10-24T16:00:00Z", "HC Erlangen", "THW Kiel", "HBL",
     "Official HBL source not read this session (unverified).", "unverified"),
]:
    rec = {
        "65331685-N-01": ("6-1-0 (244-203)", "2-3-2 (224-231)"),
        "65331685-N-02": ("2-0-5 (207-225)", "7-0-0 (239-190)"),
        "65331685-N-03": ("4-1-2 (234-205)", "3-0-4 (202-216)"),
        "65331685-N-04": ("", ""),
    }[fid]
    fx(fid, "Handball", "handball", comp, t, home, away, "League venue",
       {"listed": True, "url": "https://www.olbg.com/betting-tips/Handball/20", "rendered_time": "weekend"},
       {"competition": comp, "home": f"{home} {rec[0]}", "away": f"{away} {rec[1]}",
        "start_utc": t, "venue": "League venue", "game_state": "Scheduled", "game_id": None,
        "record_home": rec[0], "record_away": rec[1],
        "sources": (["https://www.lnh.fr/daikin-starligue/calendrier", "https://www.lnh.fr/daikin-starligue/classement"] if rec[0] else []),
        "read_utc": "2026-10-23T20:30:00Z" if rec[0] else None},
       note, lbl)

ELAPSED = [
    ("65331685-E-01", "Basketball", "EuroLeague R7", "2026-10-23T18:15:00Z", "Olympiacos Piraeus", "Fenerbahce Tarfin Istanbul",
     "In play at read time (Q3); both 5-1 entering. Oly had won three straight in the series per the official game center."),
    ("65331685-E-02", "Basketball", "EuroLeague R7", "2026-10-23T18:45:00Z", "Paris Basketball", "Valencia Basket",
     "In play at read time (Q2); Paris 1-5, Valencia 5-1 with the league's top offense (98.3 ppg)."),
    ("65331685-E-03", "Tennis", "ATP Brussels QF", "2026-10-23T15:00:00Z", "Arthur Fils", "Alex Michelsen",
     "Completed before read: Fils won 6-4 7-6(12) (sixth match point)."),
    ("65331685-E-04", "Tennis", "ATP Lyon QF", "2026-10-23T15:00:00Z", "Flavio Cobolli", "Brandon Nakashima",
     "Completed before read: Cobolli won 4-6 6-4 6-4."),
    ("65331685-E-05", "Snooker", "NI Open QF", "2026-10-23T13:00:00Z", "Jak Jones", "Scott Donaldson",
     "Live at read (2-2); winner faces the Gilbert/Williams winner."),
    ("65331685-E-06", "Rugby Union", "URC R4", "2026-10-23T18:45:00Z", "Cardiff Rugby", "Hollywoodbets Sharks",
     "In play at read; team lists captured (Winnett, Adams; Esterhuizen capt, Nche/du Toit bench)."),
    ("65331685-E-07", "Rugby Union", "URC R4", "2026-10-23T18:45:00Z", "Connacht Rugby", "Zebre Parma",
     "In play at read; Connacht starting XV read (Hansen, Frawley, Bealham, Prendergast capt; Lancaster cites eight Ireland call-ups)."),
    ("65331685-E-08", "Rugby League", "RLWC2026 R2", "2026-10-23T10:05:00Z", "Tonga", "Lebanon",
     "Full time before read: Tonga 36-0 Lebanon."),
    ("65331685-E-09", "Rugby League", "RLWC2026 WR2", "2026-10-23T06:45:00Z", "Samoa", "Wales",
     "Full time before read: Samoa 76-0 Wales."),
    ("65331685-E-10", "Handball", "StarLigue J08", "2026-10-23T18:00:00Z", "Pays d'Aix Universite Club", "Fenix Toulouse Handball",
     "In play at read (Aix leading 32-26 in the second half on the LNH live centre)."),
]

# ---------------------------------------------------------------- markets ----
S = []


def record_pair(s, gp_w_l):
    """gp_w_l: (W, [D], L) tuple strings like (4,3,2) or (2,0,1)."""
    return gp_w_l


def nhl_markets():
    games = [
        ("65331685-H-01", (4, 3, 2), (3, 6, 0), "Montreal Canadiens", "Chicago Blackhawks"),
        ("65331685-H-02", (7, 2, 0), (5, 4, 1), "Tampa Bay Lightning", "Colorado Avalanche"),
        ("65331685-H-03", (4, 6, 0), (3, 6, 3), "Anaheim Ducks", "Philadelphia Flyers"),
        ("65331685-H-04", (2, 4, 2), (6, 4, 0), "Los Angeles Kings", "New Jersey Devils"),
        ("65331685-H-05", (8, 1, 1), (6, 4, 2), "Edmonton Oilers", "Toronto Maple Leafs"),
        ("65331685-H-06", (8, 4, 0), (3, 5, 0), "Vegas Golden Knights", "Columbus Blue Jackets"),
        ("65331685-H-07", (8, 2, 2), (5, 4, 1), "Carolina Hurricanes", "St. Louis Blues"),
        ("65331685-H-08", (8, 2, 1), (6, 4, 1), "Boston Bruins", "San Jose Sharks"),
    ]
    for fid, aw, hm, an, hn in games:
        gp_a, gp_h = sum(aw), sum(hm)
        a, h = shrunk(aw[0], gp_a), shrunk(hm[0], gp_h)
        p_a = log5(a, h)
        match = f"{an} @ {hn}"
        S.append(sel(fid, "Ice Hockey", match, "match winner (incl. OT)", an, p_a,
                     "Beta(2,2)+log5 on W/(W+L+OTL); no home edge",
                     "OTL counted as defeats per pricing convention."))
        S.append(sel(fid, "Ice Hockey", match, "match winner (incl. OT)", hn, 1 - p_a,
                     "Beta(2,2)+log5 on W/(W+L+OTL); no home edge", ""))
        # goal lines from per-game rates
        ga_r, ha_r = 0, 0
        rates = {
            "65331685-H-01": ((30, 34, 9), (21, 36, 9)),
            "65331685-H-02": ((29, 23, 9), (41, 36, 10)),
            "65331685-H-03": ((27, 33, 10), (20, 29, 12)),
            "65331685-H-04": ((27, 33, 8), (33, 31, 10)),
            "65331685-H-05": ((47, 32, 10), (43, 39, 12)),
            "65331685-H-06": ((47, 36, 12), (20, 29, 8)),
            "65331685-H-07": ((47, 33, 12), (32, 27, 11)),
            "65331685-H-08": ((42, 22, 11), (33, 37, 11)),
        }[fid]
        (gf_a, ga_a, gpa), (gf_h, ga_h, gph) = rates
        lam_a = (gf_a / gpa + ga_h / gph) / 2.0
        lam_h = (gf_h / gph + ga_a / gpa) / 2.0
        for line in (5.5, 6.5):
            p_over = poisson_total_over(line, lam_a, lam_h)
            total_markets(fid, "Ice Hockey", match, f"goals {line}", p_over,
                          "paired per-game rates; independent Poisson, no-tie conditioning",
                          f"expected total {lam_a + lam_h:.2f}")
        exp_m = lam_a - lam_h
        handicap_markets(fid, "Ice Hockey", match, an, hn, exp_m, CONSTANTS["nhl_margin_sd_goals"],
                         (1.5, 2.5),
                         "gaussian margin, sd 1.9 goals (disclosed working constant)",
                         f"expected margin {exp_m:+.2f} for {an}", label="puck line")


def mlb_markets():
    rows = [
        ("65331685-B-01", 98, 64, 103, 59, 736, 650, 832, 618, "Tampa Bay Rays", "Milwaukee Brewers"),
        ("65331685-B-02", 98, 64, 103, 59, 736, 650, 832, 618, "Tampa Bay Rays", "Milwaukee Brewers"),
        ("65331685-B-03", 103, 59, 98, 64, 832, 618, 736, 650, "Milwaukee Brewers", "Tampa Bay Rays"),
    ]
    for fid, wa, la, wh, lh, rsa, raa, rsh, rah, an, hn in rows:
        # B-03 home/away roles flip
        a = shrunk(wa, wa + la)
        h = shrunk(wh, wh + lh)
        p_a = log5(a, h)
        match = f"{an} @ {hn}"
        S.append(sel(fid, "Baseball", match, "match winner (incl. extras)", an, p_a,
                     "Beta(2,2)+log5 on season win pctg; no home edge", ""))
        S.append(sel(fid, "Baseball", match, "match winner (incl. extras)", hn, 1 - p_a,
                     "Beta(2,2)+log5 on season win pctg; no home edge", ""))
        lam_a = (rsa / 162.0 + rah / 162.0) / 2.0
        lam_h = (rsh / 162.0 + raa / 162.0) / 2.0
        exp_m = lam_a - lam_h
        handicap_markets(fid, "Baseball", match, an, hn, exp_m, CONSTANTS["mlb_run_sd"], (1.5, 2.5),
                         "paired run rates; gaussian run-margin approximation, sd 4.3 (disclosed)",
                         f"expected runs {lam_a:.2f} v {lam_h:.2f}", label="run line")
        for t in (6.5, 7.5, 8.5):
            p_over = poisson_total_over(t, lam_a, lam_h)
            total_markets(fid, "Baseball", match, f"runs {t}", p_over,
                          "paired regular-season run rates; independent Poisson", f"expected total {lam_a + lam_h:.2f}")
        if fid == "65331685-B-01":
            p_game_mil = 1 - p_a
            # best-of-7 with constant per-game p: P(win series) = sum_{j=0..3} C(3+j,j) p^4 (1-p)^j
            p_mil_series = sum(math.comb(3 + j, j) * p_game_mil ** 4 * (1 - p_game_mil) ** j for j in range(4))
            S.append(sel("65331685-B-01", "Baseball", "World Series (best of 7)", "to win the series", "Milwaukee Brewers",
                         p_mil_series,
                         "best-of-7 convolution of the per-game log5 edge (constant-p simplification)",
                         "Series probability is an estimate built from the same per-game edges; no quote."))
            S.append(sel("65331685-B-01", "Baseball", "World Series (best of 7)", "to win the series", "Tampa Bay Rays",
                         1 - p_mil_series,
                         "best-of-7 convolution of the per-game log5 edge (constant-p simplification)", ""))


def nba_markets():
    rows = [
        ("65331685-K-01", ("Boston Celtics", "0-1"), ("New York Knicks", "0-1"), 223.0, "Karl-Anthony Towns 19/12/1", "Paul George 38/5/3"),
        ("65331685-K-02", ("Orlando Magic", "0-1"), ("Minnesota Timberwolves", "1-0"), 221.5, "Paolo Banchero 35/7/10", "Anthony Edwards 45/10/3"),
        ("65331685-K-03", ("Indiana Pacers", "1-0"), ("Dallas Mavericks", "0-1"), 228.5, "Pascal Siakam 30/8/1", "Cooper Flagg 32/5/2"),
        ("65331685-K-04", ("Golden State Warriors", "0-1"), ("Memphis Grizzlies", "1-0"), 231.5, "Stephen Curry 23/2/1", "Ty Jerome 45/7/6"),
        ("65331685-K-05", ("Milwaukee Bucks", "0-1"), ("Chicago Bulls", "0-1"), 229.5, "Tyler Herro 24/2/9", "Jalen Smith 15/8/1"),
        ("65331685-K-06", ("Washington Wizards", "1-0"), ("Toronto Raptors", "1-0"), 227.5, "Anthony Davis 34/12/4", "Immanuel Quickley 23/4/7"),
        ("65331685-K-07", ("Charlotte Hornets", "1-0"), ("Atlanta Hawks", "1-0"), 226.5, "Naz Reid 20/11/7", "Jalen Johnson 20/14/6"),
        ("65331685-K-08", ("Miami Heat", "0-1"), ("Detroit Pistons", "1-0"), 224.5, "Giannis Antetokounmpo 35/6/1", "Cade Cunningham 22/4/8"),
        ("65331685-K-09", ("San Antonio Spurs", "0-1"), ("Houston Rockets", "1-0"), 229.5, "Stephon Castle 24/7/1", "Kevin Durant 30/6/3"),
        ("65331685-K-10", ("Utah Jazz", "0-1"), ("New Orleans Pelicans", "0-1"), 225.5, "Lauri Markkanen 18/9/3", "Dejounte Murray 23/3/7"),
        ("65331685-K-11", ("Los Angeles Lakers", "1-0"), ("LA Clippers", "1-0"), 228.5, "Luka Doncic 28/8/7", "Darius Garland 30/1/4"),
        ("65331685-K-12", ("Sacramento Kings", "0-1"), ("Portland Trail Blazers", "1-0"), 226.5, "Domantas Sabonis 14/18/8", "Damian Lillard 25/3/6"),
    ]
    for i, (fid, (hn, hr), (an, ar), base_total, hlead, alead) in enumerate(rows):
        def raw(rec):
            w, l = rec.split("-")
            return int(w), int(l)
        hw, hl = raw(hr)
        aw, al = raw(ar)
        a = shrunk(aw, aw + al)
        h = shrunk(hw, hw + hl)
        p_a = log5(a, h)
        match = f"{an} @ {hn}"
        S.append(sel(fid, "Basketball", match, "match winner", an, p_a,
                     "Beta(2,2)+log5 on opening-week records; no home edge",
                     f"season leaders read: {alead} v {hlead}."))
        S.append(sel(fid, "Basketball", match, "match winner", hn, 1 - p_a,
                     "Beta(2,2)+log5 on opening-week records; no home edge", ""))
        exp_m = (p_a - 0.5) * 2 * CONSTANTS["nba_margin_sd_points"] * 1.25
        handicap_markets(fid, "Basketball", match, an, hn, exp_m, CONSTANTS["nba_margin_sd_points"],
                         (1.5, 3.5, 5.5),
                         "gaussian margin, sd 11.5 (disclosed working constant)",
                         f"expected margin {exp_m:+.1f} for {an}", label="point spread")
        for t in (base_total - 2.5, base_total, base_total + 2.5):
            z = (t - base_total) / 11.0
            p_over = 1 - phi(z)
            total_markets(fid, "Basketball", match, f"points {t:.1f}", p_over,
                          "total centered on the listed market anchor with symmetric 11-point band (disclosed)",
                          "Anchor is the OLBG-rendered total where listed, else a league working anchor; flagged as anchor input.")


def rugby_markets():
    rows = [
        ("65331685-R-01", (2, 0, 1), (0, 2, 1), 126, 54, 88, 93, "Vodacom Bulls", "Ulster Rugby"),
        ("65331685-R-02", (2, 0, 1), (1, 0, 2), 81, 54, 68, 85, "DHL Stormers", "Scarlets"),
        ("65331685-R-03", (0, 1, 2), (2, 1, 0), 64, 68, 95, 72, "Benetton Rugby", "Glasgow Warriors"),
        ("65331685-R-04", (1, 0, 2), (1, 1, 1), 75, 58, 72, 74, "Leinster Rugby", "Munster Rugby"),
        ("65331685-R-05", (1, 0, 2), (1, 1, 1), 81, 107, 88, 83, "Ospreys", "Dragons RFC"),
    ]
    for fid, hw, aw, pfh, pah, pfa, paa, hn, an in rows:
        def rate(wdl):
            w, d, l = wdl
            p = w + d + l
            return shrunk(w + 0.5 * d, p)
        h, a = rate(hw), rate(aw)
        p_h = log5(h, a)
        match = f"{hn} v {an}"
        S.append(sel(fid, "Rugby Union", match, "match winner (80 minutes)", hn, p_h,
                     "Beta(2,2)+log5 on (W+0.5D)/P; draws split; no home edge", ""))
        S.append(sel(fid, "Rugby Union", match, "match winner (80 minutes)", an, 1 - p_h,
                     "Beta(2,2)+log5 on (W+0.5D)/P; draws split; no home edge", ""))
        lam_h = (pfh / 3.0 + paa / 3.0) / 2.0
        lam_a = (pfa / 3.0 + pah / 3.0) / 2.0
        exp_m = lam_h - lam_a
        handicap_markets(fid, "Rugby Union", match, hn, an, exp_m, CONSTANTS["rugby_margin_sd_points"],
                         (2.5, 5.5, 8.5),
                         "gaussian margin, sd 14 (disclosed working constant)",
                         f"expected margin {exp_m:+.1f}; expected total {lam_h + lam_a:.1f}")
        for t in (42.5, 46.5, 50.5):
            p_over = poisson_total_over(t, lam_h, lam_a)
            total_markets(fid, "Rugby Union", match, f"points {t}", p_over,
                          "paired per-game rates; independent Poisson", f"expected total {lam_h + lam_a:.1f}")


def rlwc_markets():
    # elite-spine representation index (documented): 17 = full NRL spine, 4 = mostly domestic
    rows = [
        ("65331685-L-01", "Samoa", "Papua New Guinea", 17, 8, "Samoa field seven current NRL spine/backline players in the official 1-13 (Tabuai-Fidow, To'o, Tago, Crichton, Harris-Tavita, Luai, Molo); PNG start four (Biondi-Odo, Martin, de Belin, Macdonald) from the read list."),
        ("65331685-L-02", "England", "France", 16, 7, "England name nine current NRL/Super League internationals in the starting side (Brimson, Young, Farnworth, G Williams, Smith, Radley, Thompson, Nsemba, Pearce-Paul); France's 1-13 is built around Elite 1 and a small Super League group (Fages, Garcia, Lacans)."),
        ("65331685-L-03", "Australia (Jillaroos)", "England", 18, 12, "Jillaroos are the reigning champions fielding the deepest NRLW list; England lose Strange (ACL) and start Murray in her place."),
        ("65331685-L-04", "New Zealand", "Cook Islands", 17, 8, "Kiwis start five current NRL internationals (Kini, Isaako, Nicoll-Klokstad, Hughes, Nikorima); Cook Islands build around Holmes and Iro."),
        ("65331685-L-05", "Australia", "Fiji", 18, 9, "Kangaroos list unavailable in the chunk read; index carries the wide talent gap flagged as estimate."),
    ]
    for fid, fav, dog, idx_f, idx_d, note in rows:
        p = idx_f ** 1.6 / (idx_f ** 1.6 + idx_d ** 1.6)
        match = f"{fav} v {dog}"
        S.append(sel(fid, "Rugby League", match, "match winner", fav, p,
                     "elite-spine representation index, power 1.6 (disclosed scale)", note))
        S.append(sel(fid, "Rugby League", match, "match winner", dog, 1 - p,
                     "elite-spine representation index, power 1.6 (disclosed scale)", ""))
        exp_m = (p - 0.5) * 2 * 24.0
        handicap_markets(fid, "Rugby League", match, fav, dog, exp_m, 18.0,
                         (6.5, 10.5, 14.5),
                         "gaussian margin, sd 18 league points (disclosed working constant)",
                         f"expected margin {exp_m:+.1f} (index-implied)")


def cricket_markets():
    S.append(sel("65331685-C-01", "Cricket", "New Zealand v India", "match winner (T20I)", "India", 0.6923,
                 "Beta(2,2)+log5 on series results (India won game 1 chasing 226)", "Single completed game input."))
    S.append(sel("65331685-C-01", "Cricket", "New Zealand v India", "match winner (T20I)", "New Zealand", 0.3077,
                 "Beta(2,2)+log5 on series results", "Kishan out for India (adductor), Kushagra added."))
    p_pak = log5(shrunk(2, 3), shrunk(0, 2))
    S.append(sel("65331685-C-02", "Cricket", "Pakistan v England", "match winner (ODI)", "Pakistan", p_pak,
                 "Beta(2,2)+log5 on tri-series results", "Pakistan 2-0 in the tri-series (beat SL by 37, ENG by 87)."))
    S.append(sel("65331685-C-02", "Cricket", "Pakistan v England", "match winner (ODI)", "England", 1 - p_pak,
                 "Beta(2,2)+log5 on tri-series results", ""))
    for fid, a, b in [("65331685-C-03", "Denmark", "Kuwait"), ("65331685-C-04", "Namibia", "Ireland"),
                      ("65331685-C-05", "United Arab Emirates", "Netherlands")]:
        S.append(sel(fid, "Cricket", f"{a} v {b}", "match winner", "not originated", 0.5,
                     "none (no compatible records read)", "Record inputs unavailable; row retained for coverage."))


def snooker_markets():
    w = shrunk(10, 14)  # Wilson frames 10-4 read
    c = shrunk(18, 28)  # Craigie frames 18-10 read
    p_w = log5(w, c)
    S.append(sel("65331685-S-01", "Snooker", "Kyren Wilson v Sam Craigie", "match winner", "Kyren Wilson", p_w,
                 "Beta(2,2)+log5 on frames won in matches read this event", "Wilson 6-1 QF; Craigie 6-2 QF."))
    S.append(sel("65331685-S-01", "Snooker", "Kyren Wilson v Sam Craigie", "match winner", "Sam Craigie", 1 - p_w,
                 "Beta(2,2)+log5 on frames won in matches read this event", ""))
    for line in (7.5, 8.5):
        p_over = 1 - phi((line - 9.4) / 1.6)
        total_markets("65331685-S-01", "Snooker", "Kyren Wilson v Sam Craigie", f"frames {line}", p_over,
                      "frame total band around an 11-frame scheduled distance (disclosed)", "")


def darts_markets():
    rows = [
        ("65331685-D-01", "Gian van Veen", "Luke Woodhouse", 6, 4, 6, 3),
        ("65331685-D-02", "Stephen Bunting", "Kim Huybrechts", 6, 5, 6, 1),
        ("65331685-D-03", "Cameron Menzies", "Gerwyn Price", 6, 3, 6, 2),
    ]
    for fid, an, bn, aw, al, bw, bl in rows:
        a = shrunk(aw, aw + al)
        b = shrunk(bw, bw + bl)
        p_a = log5(a, b)
        S.append(sel(fid, "Darts", f"{an} v {bn}", "match winner", an, p_a,
                     "Beta(2,2)+log5 on first-round leg margin (single-game inputs)", ""))
        S.append(sel(fid, "Darts", f"{an} v {bn}", "match winner", bn, 1 - p_a,
                     "Beta(2,2)+log5 on first-round leg margin (single-game inputs)", ""))
        for line in (9.5, 10.5):
            p_over = 1 - phi((line - 10.2) / 1.1)
            total_markets(fid, "Darts", f"{an} v {bn}", f"legs {line}", p_over,
                          "leg total band around an 11-leg scheduled distance (disclosed)", "")


def golf_markets():
    # R3 18-hole matchup: scores level after 36 holes -> near coin flip; use R2 closing rate with light weight
    p_conners = 0.52
    S.append(sel("65331685-G-01", "Golf", "Corey Conners v Seamus Power (R3)", "matchup winner", "Corey Conners", p_conners,
                 "36-hole level scores; slight weight to Conners' opening 63 (disclosed heuristic)", "Both -12 after two rounds."))
    S.append(sel("65331685-G-01", "Golf", "Corey Conners v Seamus Power (R3)", "matchup winner", "Seamus Power", 1 - p_conners,
                 "36-hole level scores; slight weight to Conners' opening 63 (disclosed heuristic)", "Power closed R2 in 64."))
    S.append(sel("65331685-G-02", "Golf", "Denny McCarthy v Emiliano Grillo (R3)", "matchup winner", "Denny McCarthy", 0.58,
                 "McCarthy 68-63 (-11) with Grillo's rounds unread; opponent input missing (flagged)", "Low-quality input note."))
    S.append(sel("65331685-G-02", "Golf", "Denny McCarthy v Emiliano Grillo (R3)", "matchup winner", "Emiliano Grillo", 0.42,
                 "McCarthy 68-63 (-11) with Grillo's rounds unread; opponent input missing (flagged)", ""))
    S.append(sel("65331685-G-03", "Golf", "Matthew Jarvis v Adrien Rozner", "matchup winner", "not originated", 0.5,
                 "none (no leaderboard read)", "Unverified row."))


def gaelic_markets():
    S.append(sel("65331685-A-02", "Gaelic Sports", "Dr Crokes v Kenmare Shamrocks", "match winner", "Dr Crokes", 0.71,
                 "club pedigree index (titles weighted; Dr Crokes 14 titles/last 2024 v Kenmare 0 titles, first final) - disclosed estimate", ""))
    S.append(sel("65331685-A-02", "Gaelic Sports", "Dr Crokes v Kenmare Shamrocks", "match winner", "Kenmare Shamrocks", 0.29,
                 "club pedigree index (titles weighted) - disclosed estimate", ""))
    S.append(sel("65331685-A-01", "Gaelic Sports", "Ireland v Scotland", "match winner", "not originated", 0.5,
                 "none (hybrid international; no compatible records)", "Row kept for the official fixture record."))
    S.append(sel("65331685-A-03", "Gaelic Sports", "Rathgormack v The Nire", "match winner", "not originated", 0.5,
                 "none (no compatible records)", ""))


def grey_markets():
    # clock logistic k=1.5; Fortanach Col has no read clock -> carry residual mass equally with named hounds
    times = {"Grouchos Gregor": 35.36, "Aayamza Legend": 35.75, "Bubbly Holly": 35.95, "Fortanach Col": None}
    strengths = {k: (math.exp(-1.5 * (v - 35.36)) if v else 0.51) for k, v in times.items()}
    tot = sum(strengths.values())
    for name, st in strengths.items():
        p = st / tot
        S.append(sel("65331685-X-01", "Greyhounds", "Coral 100 Champion Stakes Final", "race winner", name, p,
                     "semi-final clock logistic, k=1.5 (Fortanach Col carries an unmeasured residual)",
                     "Newinn Jolly withdrawn (urine infection)."))
    for line in (35.45, 35.75):
        p_over = 1 - phi((line - 35.55) / 0.28)
        total_markets("65331685-X-01", "Greyhounds", "Coral 100 Champion Stakes Final", f"winning time {line}s", p_over,
                      "clock band around the three read semi times (disclosed)", "")


def motor_markets():
    # no bookmaker prices; disclosed form-and-history share normalization
    drivers = {
        "Max Verstappen": 0.34,
        "Kimi Antonelli": 0.22,
        "George Russell": 0.16,
        "Lewis Hamilton": 0.14,
        "Charles Leclerc": 0.08,
        "Lando Norris": 0.06,
    }
    for d, p in drivers.items():
        S.append(sel("65331685-M-01", "Motor Racing", "F1 United States GP", "race winner", d, p,
                     "form-and-history share: last-two-round wins and COTA win record normalized (disclosed, no quotes)",
                     "Verstappen won Malaysia + Singapore and 4 of the last 5 US GPs; Antonelli leads the standings."))
    S.append(sel("65331685-M-02", "Motor Racing", "F1 US GP Qualifying", "pole position (two-way)", "Max Verstappen", 0.31,
                 "poles-history share (Verstappen 2 of last 5 US GP poles) blended with current form (disclosed)", ""))
    S.append(sel("65331685-M-02", "Motor Racing", "F1 US GP Qualifying", "pole position (two-way)", "Any other driver", 0.69,
                 "poles-history share blended with current form (disclosed)", ""))
    S.append(sel("65331685-M-02", "Motor Racing", "F1 US GP Qualifying", "pole position: Antonelli (two-way)", "Kimi Antonelli", 0.20,
                 "championship-form share (disclosed)", ""))
    S.append(sel("65331685-M-02", "Motor Racing", "F1 US GP Qualifying", "pole position: Antonelli (two-way)", "Any other driver", 0.80,
                 "championship-form share (disclosed)", ""))
    S.append(sel("65331685-M-01", "Motor Racing", "F1 Drivers Championship 2026", "title winner", "Kimi Antonelli", 0.62,
                 "title-clinch scenario math from the official need-to-know page blended with standings lead (disclosed)",
                 "Antonelli can clinch in Austin with a win and specific Russell/Hamilton finishes."))
    S.append(sel("65331685-M-01", "Motor Racing", "F1 Drivers Championship 2026", "title winner", "George Russell", 0.18,
                 "residual share of the standings lead group (disclosed)", ""))
    S.append(sel("65331685-M-01", "Motor Racing", "F1 Drivers Championship 2026", "title winner", "Lewis Hamilton", 0.14,
                 "residual share of the standings lead group (disclosed)", ""))
    S.append(sel("65331685-M-01", "Motor Racing", "F1 Drivers Championship 2026", "title winner", "Any other driver", 0.06,
                 "residual share of the field (disclosed)", ""))


def tennis_markets():
    def rank_elo(r):
        return 1500 + 40 * math.log10(500.0 / r)
    p_ryb = 1 / (1 + 10 ** ((rank_elo(13) - rank_elo(1)) / 400.0))
    S.append(sel("65331685-T-01", "Tennis", "Rybakina v Shnaider", "match winner", "Elena Rybakina", p_ryb,
                 "rank-Elo proxy from official WTA ranks (disclosed formula)", "Rybakina rank 1 v Shnaider rank 13."))
    S.append(sel("65331685-T-01", "Tennis", "Rybakina v Shnaider", "match winner", "Diana Shnaider", 1 - p_ryb,
                 "rank-Elo proxy from official WTA ranks (disclosed formula)", ""))
    p_bou = 1 / (1 + 10 ** ((rank_elo(75) - rank_elo(54)) / 400.0))
    S.append(sel("65331685-T-02", "Tennis", "Boulter v Siniakova", "match winner", "Katie Boulter", p_bou,
                 "rank-Elo proxy; Siniakova singles rank carried at 75 as an explicit placeholder (flagged)",
                 "Siniakova's exact singles rank was not on the draw sheet."))
    S.append(sel("65331685-T-02", "Tennis", "Boulter v Siniakova", "match winner", "Katerina Siniakova", 1 - p_bou,
                 "rank-Elo proxy; Siniakova singles rank carried at 75 as an explicit placeholder (flagged)", ""))
    for fid, a, b, pa in [("65331685-T-01", "Rybakina v Shnaider", "match total sets", 0.58),
                          ("65331685-T-02", "Boulter v Siniakova", "match total sets", 0.61)]:
        total_markets(fid, "Tennis", a, "sets 2.5", pa,
                      "set-length band from the draw path margins (disclosed)", "")


def handball_markets():
    rows = [
        ("65331685-N-01", (6, 1, 0), (2, 3, 2), 244, 203, 224, 231, "HBC Nantes", "Chambery Savoie Mont Blanc HB"),
        ("65331685-N-02", (2, 0, 5), (7, 0, 0), 207, 225, 239, 190, "Saint-Raphael Var Handball", "Paris Saint-Germain Handball"),
        ("65331685-N-03", (4, 1, 2), (3, 0, 4), 234, 205, 202, 216, "Montpellier Handball", "Saran Loiret Handball"),
    ]
    for fid, hw, aw, pfh, pah, pfa, paa, hn, an in rows:
        def rate(wdl):
            w, d, l = wdl
            p = w + d + l
            return shrunk(w + 0.5 * d, p)
        p_h = log5(rate(hw), rate(aw))
        match = f"{hn} v {an}"
        S.append(sel(fid, "Handball", match, "match winner", hn, p_h,
                     "Beta(2,2)+log5 on (W+0.5D)/P; no home edge", ""))
        S.append(sel(fid, "Handball", match, "match winner", an, 1 - p_h,
                     "Beta(2,2)+log5 on (W+0.5D)/P; no home edge", ""))
        lam_h = (pfh / 7.0 + paa / 7.0) / 2.0
        lam_a = (pfa / 7.0 + pah / 7.0) / 2.0
        exp_m = lam_h - lam_a
        handicap_markets(fid, "Handball", match, hn, an, exp_m, CONSTANTS["handball_margin_sd_goals"],
                         (1.5, 2.5, 4.5),
                         "gaussian margin, sd 4 goals (disclosed working constant)",
                         f"expected margin {exp_m:+.1f}; expected total {lam_h + lam_a:.1f}")
        for t in (54.5, 58.5, 62.5):
            p_over = 1 - phi((t - (lam_h + lam_a)) / 5.5)
            total_markets(fid, "Handball", match, f"goals {t}", p_over,
                          "total band, sd 5.5 goals (disclosed working constant)", "")
    S.append(sel("65331685-N-04", "Handball", "HC Erlangen v THW Kiel", "match winner", "not originated", 0.5,
                 "none (no compatible records read)", "Unverified row."))


def volleyball_markets():
    rows = [
        ("65331685-V-01", "PGE GiEK Skra Belchatow", "PGE Projekt Warszawa", (15, 11), (19, 7), True),
        ("65331685-V-03", "Itas Trentino", "Cisterna Volley", (3, 0), (3, 0), False),
        ("65331685-V-04", "Sir Susa Scai Perugia", "Tinet Prata di Pordenone", (3, 2), (3, 1), False),
    ]
    for fid, hn, an, hwl, awl, use_prev in rows:
        # set-share from 2025-26 set records where flagged, else from R1 set scores
        if use_prev:
            h = shrunk(hwl[0], sum(hwl))
            a = shrunk(awl[0], sum(awl))
            note = "2025-26 regular-season set records (cross-referenced) with Beta(2,2); R1 2026-27 wins noted in the row."
        else:
            h = shrunk(hwl[0], sum(hwl))
            a = shrunk(awl[0], sum(awl))
            note = "R1 2026-27 set shares (cross-referenced results) with Beta(2,2)."
        p_h = log5(h, a)
        match = f"{hn} v {an}"
        S.append(sel(fid, "Volleyball", match, "match winner", hn, p_h, "Beta(2,2)+log5 on set share", note))
        S.append(sel(fid, "Volleyball", match, "match winner", an, 1 - p_h, "Beta(2,2)+log5 on set share", ""))
        for line in (3.5, 4.5):
            p_over = 1 - phi((line - 4.1) / 1.0)
            total_markets(fid, "Volleyball", match, f"sets {line}", p_over,
                          "set-count band around a best-of-five (disclosed)", "")
    for fid, m in [("65331685-V-02", "VC Giesen v Berlin Recycling Volleys"), ("65331685-V-05", "Chelm v Asseco Resovia Rzeszow")]:
        S.append(sel(fid, "Volleyball", m, "match winner", "not originated", 0.5, "none", "Unverified row."))


nhl_markets()
mlb_markets()
nba_markets()
rugby_markets()
rlwc_markets()
cricket_markets()
snooker_markets()
darts_markets()
golf_markets()
gaelic_markets()
grey_markets()
motor_markets()
tennis_markets()
handball_markets()
volleyball_markets()

# ---------------------------------------------------------------- lines ------
by_fix = {}
for s in S:
    by_fix.setdefault(s["fixture_id"], []).append(s)

lines = []
for fid, sels in by_fix.items():
    win = [x for x in sels if x["market"].startswith("match winner") or x["market"].startswith("race winner") or x["market"] == "match winner (incl. extras)" or x["market"] == "match winner (80 minutes)" or x["market"] == "match winner (T20I)" or x["market"] == "match winner (ODI)" or x["market"] == "to win the series" or x["market"] == "title winner" or x["market"] == "pole position"]
    fam = [x for x in sels if x["market"] == "match winner (incl. extras)"]
    fam2 = [x for x in sels if x["market"] == "match winner (80 minutes)"]
    fam3 = [x for x in sels if x["market"] == "match winner"]
    fam4 = [x for x in sels if x["market"] in ("match winner (T20I)", "match winner (ODI)", "race winner")]
    prob_sum = 0
    for x in fam + fam2 + fam3 + fam4:
        prob_sum += x["prob"]
    lines.append({
        "fixture_id": fid,
        "selections": sels,
    })

session_line = {
    "session": SESSION,
    "band": {
        "min_prob": 0.70,
        "fair_american_min": -250.0,
        "fair_american_max": 10000.0,
        "rule": "High only if unrounded p>0.70 and -250 <= fair american <= +10000; chalk (p>0.7143) disclosed, never promoted",
    },
    "constants": CONSTANTS,
    "generated_utc": NOW,
    "markets": lines,
}

# ------------------------------------------------------------- selections -----
def top5(sport):
    sels = [x for x in S if x["sport"] == sport and x["prob"] != 0.5 and x["selection"] != "not originated"]
    # one market per fixture for the headline list: prefer the primary winner market
    best = {}
    for x in sels:
        if x["market"] in ("match winner (incl. extras)", "match winner", "match winner (80 minutes)",
                           "match winner (T20I)", "match winner (ODI)", "race winner", "matchup winner",
                           "title winner", "to win the series"):
            key = (x["fixture_id"], x["selection"])
            if key not in best or x["prob"] > best[key]["prob"]:
                best[key] = x
    ranked = sorted(best.values(), key=lambda z: -z["prob"])
    return ranked[:5]


selections = []
for sport in ["Ice Hockey", "Baseball", "Basketball", "Rugby Union", "Rugby League", "Cricket", "Snooker",
              "Darts", "Golf", "Gaelic Sports", "Greyhounds", "Motor Racing", "Tennis", "Handball", "Volleyball"]:
    for x in top5(sport):
        selections.append(x)

# ---------------------------------------------------------------- emit -------
os.makedirs(OUT, exist_ok=True)

harvest = {
    "session": SESSION,
    "collected_utc": NOW,
    "read_channel": CONSTANTS["read_channel"],
    "reads": [{"url": u, "read_utc": t, "takeaway": w} for u, t, w in READS],
}
fixtures_doc = {
    "session": SESSION,
    "generated_utc": NOW,
    "counts": {"rows": len(F), "verified_rows": sum(1 for r in F if r["official"]["sources"] and not r["label"]),
               "elapsed_rows": len(ELAPSED)},
    "fixtures": F,
    "elapsed": [{"id": e[0], "sport": e[1], "competition": e[2], "start_utc": e[3], "home": e[4], "away": e[5], "note": e[6]} for e in ELAPSED],
}
predictions_doc = {"session": SESSION, "policy": {"min_words": 30,
                                                  "banned_words": ["model", "verified", "verification", "algorithm", "our data shows"],
                                                  "uniqueness": "no repeated 6-gram"},
                   "predictions": []}

with open(os.path.join(OUT, "harvest.json"), "w") as f:
    json.dump(harvest, f, indent=1)
with open(os.path.join(OUT, "fixtures.json"), "w") as f:
    json.dump(fixtures_doc, f, indent=1)
with open(os.path.join(OUT, "lines.json"), "w") as f:
    json.dump(session_line, f, indent=1)
with open(os.path.join(OUT, "desk.json"), "w") as f:
    json.dump({"session": SESSION, "generated_utc": NOW,
               "summary": "Official-source desk across 15 OLBG hub sports; zero-vig multi-market origination; High band p>0.70 and -250..+10000.",
               "events": F, "markets": S, "constants": CONSTANTS}, f, indent=1)
print("fixtures:", len(F), "markets:", len(S), "selections:", len(selections))
print("high:", [x for x in S if x["tier"] == "High"])
print("chalk:", [(x["fixture_id"], x["selection"], x["prob"]) for x in S if x["tier"] == "Chalk (disclosed)"][:12])
