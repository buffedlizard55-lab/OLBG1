"""Build the T2988 desk (`/2988bd19/`) from verified data in s2988bd19_data.py.

Every price is an independent model estimate. No bookmaker price, no borrowed rating and
no value from another session's file is used. Unverified fixtures stay blank.
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import s2988bd19_data as D

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "2988bd19"
DATA = ROOT / "data" / "2988bd19"
REPO = "https://github.com/buffedlizard55-lab/OLBG1"
LIVE = "https://buffedlizard55-lab.github.io/OLBG1/"
SLUG = "2988bd19"

HIGH_SELECTIONS = {
    ("nhl-2026020155", "home_+1.5"),   # Toronto +1.5 vs NY Rangers, 70.64%
    ("nhl-2026020156", "away_over_1.5"),  # San Jose over 1.5 team goals at Ottawa, 71.27%
}


def e(v):
    return html.escape("" if v is None else str(v), quote=True)


def pct(p, dp=2):
    return f"{p*100:.{dp}f}%"


def money(p):
    a = D.american(p)
    return f"{a:+.0f}".replace("+", "+") if a > 0 else f"{a:.0f}"


def dec(p):
    return f"{1/p:.3f}"


# ------------------------------------------------------------------ fixtures & markets
def build():
    fixtures = []
    markets = []
    for gid, away, home, start, venue in D.NHL_GAMES:
        fid = f"nhl-{gid}"
        fixtures.append(dict(
            id=fid, sport="ice-hockey", competition="NHL", stage="Regular season",
            away=away, away_name=D.NHL_TEAMS[away][0], home=home, home_name=D.NHL_TEAMS[home][0],
            start_utc=start, venue=venue, verification="official", priced=True,
            official_url="https://api-web.nhle.com/v1/schedule/2026-10-22",
            official_label=f"NHL game {gid}",
            extra_url=f"https://www.nhl.com/gamecenter/{away.lower()}-vs-{home.lower()}/2026/10/22/{gid}",
            sources=["nhl-schedule", "nhl-team-summary", "nhl-standings"],
            note="Game id, venue and startTimeUTC read from the NHL schedule feed.",
        ))
        lh, la = D.nhl_lambdas(away, home)
        probs = D.two_way(lh, la)
        markets.append(_markets_for(fid, "ice-hockey", home, away, lh, la, probs, nhl=True))

    for gpk, away, home, start, venue, sdate in D.MLB_GAMES:
        fid = f"mlb-{gpk}"
        fixtures.append(dict(
            id=fid, sport="baseball", competition="MLB", stage="World Series",
            away=away, away_name=D.MLB_TEAMS[away][0], home=home, home_name=D.MLB_TEAMS[home][0],
            start_utc=start, venue=venue, verification="official", priced=True,
            official_url="https://statsapi.mlb.com/api/v1/schedule?sportId=1&startDate=2026-10-18&endDate=2026-10-30",
            official_label=f"MLB gamePk {gpk}",
            extra_url="https://www.mlb.com/postseason",
            sources=["mlb-schedule", "mlb-standings", "mlb-mil-hitting", "mlb-mil-pitching"],
            note=f"Status read as Scheduled for source date {sdate}; later games are played only if the series continues.",
        ))
        lh, la = D.mlb_lambdas(away, home)
        probs = D.two_way(lh, la)
        markets.append(_markets_for(fid, "baseball", home, away, lh, la, probs, nhl=False))

    for gid, away, home, start, venue, local in D.NBA_GAMES:
        fixtures.append(dict(
            id=f"nba-{gid}", sport="basketball", competition="NBA", stage="Regular season",
            away=away, away_name=away, home=home, home_name=home,
            start_utc=start, venue=venue, verification="official", priced=False,
            official_url="https://www.nba.com/schedule?date=10%2F22%2F2026",
            official_label=f"NBA game {gid} ({local})",
            extra_url="https://www.nba.com/standings",
            sources=["nba-schedule", "nba-standings"],
            note="Fixture confirmed by the NBA schedule page. No price: one-game sample, Denver's record not read, and no default rating is inserted.",
        ))

    discovered = []
    for i, (sport, comp, a, b, date, time_txt, note) in enumerate(D.DISCOVERED, start=1):
        discovered.append(dict(
            id=f"disc-{i:02d}", sport=sport, competition=comp, away=a, home=b,
            away_name=a, home_name=b, start_utc=None, venue="",
            start_local=f"{date} · {time_txt}", verification="discovery", priced=False,
            official_url=None, official_label="", extra_url=None,
            sources=["olbg-home"], note=note,
        ))
    return fixtures, markets, discovered


def _markets_for(fid, sport, home, away, lh, la, probs, nhl):
    groups = []
    if nhl:
        groups.append(("Money line (incl. OT/SO)", [("home_ml", f"{home} to win"), ("away_ml", f"{away} to win")]))
        groups.append(("Puck line -1.5 / +1.5", [
            ("home_-1.5", f"{home} -1.5"), ("away_+1.5", f"{away} +1.5"),
            ("home_+1.5", f"{home} +1.5"), ("away_-1.5", f"{away} -1.5")]))
        groups.append(("Match total, 4 half-point rungs", [
            (f"over_{l}", f"Over {l}") for l in (4.5, 5.5, 6.5, 7.5)] + [
            (f"under_{l}", f"Under {l}") for l in (4.5, 5.5, 6.5, 7.5)]))
        groups.append(("Team totals, 1.5 to 4.5", [
            (f"home_over_{l}", f"{home} over {l}") for l in (1.5, 2.5, 3.5, 4.5)] + [
            (f"home_under_{l}", f"{home} under {l}") for l in (1.5, 2.5, 3.5, 4.5)] + [
            (f"away_over_{l}", f"{away} over {l}") for l in (1.5, 2.5, 3.5, 4.5)] + [
            (f"away_under_{l}", f"{away} under {l}") for l in (1.5, 2.5, 3.5, 4.5)]))
        groups.append(("First-period total (lambda/3)", [
            (f"p1_over_{l}", f"1st period over {l}") for l in (1.5, 2.5)] + [
            (f"p1_under_{l}", f"1st period under {l}") for l in (1.5, 2.5)]))
    else:
        groups.append(("Money line", [("home_ml", f"{home} to win"), ("away_ml", f"{away} to win")]))
        groups.append(("Run line -1.5 / +1.5", [
            ("home_-1.5", f"{home} -1.5"), ("away_+1.5", f"{away} +1.5"),
            ("home_+1.5", f"{home} +1.5"), ("away_-1.5", f"{away} -1.5")]))
        groups.append(("Alternate run line -2.5 / +2.5", [
            ("home_-2.5", f"{home} -2.5"), ("away_+2.5", f"{away} +2.5"),
            ("home_+2.5", f"{home} +2.5"), ("away_-2.5", f"{away} -2.5")]))
        groups.append(("Match total, 7.5 to 11.5", [
            (f"over_{l}", f"Over {l}") for l in (7.5, 8.5, 9.5, 10.5, 11.5)] + [
            (f"under_{l}", f"Under {l}") for l in (7.5, 8.5, 9.5, 10.5, 11.5)]))
        groups.append(("Team totals, 2.5 to 4.5", [
            (f"home_over_{l}", f"{home} over {l}") for l in (2.5, 3.5, 4.5)] + [
            (f"home_under_{l}", f"{home} under {l}") for l in (2.5, 3.5, 4.5)] + [
            (f"away_over_{l}", f"{away} over {l}") for l in (2.5, 3.5, 4.5)] + [
            (f"away_under_{l}", f"{away} under {l}") for l in (2.5, 3.5, 4.5)]))
    out = dict(id=fid, sport=sport, lambda_home=round(lh, 8), lambda_away=round(la, 8),
               total=round(lh + la, 8), groups=[], selections=[])
    for name, sel in groups:
        g = dict(market=name, selections=[])
        for key, label in sel:
            p = round(probs[key], 6)
            sid = f"{fid}:{key}"
            tier, tier_note = classify(sid, p)
            row = dict(id=sid, key=key, label=label, p=p, fair_decimal=round(1.0 / p, 4),
                       american=round(D.american(p), 2), tier=tier, tier_note=tier_note,
                       band=D.band_note(p))
            g["selections"].append(row)
            out["selections"].append(row)
        out["groups"].append(g)
    return out


def classify(sid, p):
    if sid in {f"{f}:{k}" for f, k in HIGH_SELECTIONS}:
        return "High", "in band and supported by verified player, form and recent-result evidence"
    if 0.70 < p <= 0.7142857:
        return "Medium", "inside the band but capped: no player-level or recent-result evidence was read for this selection"
    if p > 0.7142857:
        return "Medium", "above the band: the fair price is shorter than -250"
    if p >= 0.60:
        return "Medium", "60-70% range"
    return "Low", "below 60%"


# ------------------------------------------------------------------ picks & predictions
PREDICTIONS = [
    dict(
        id="P-2988-01", fixture="nhl-2026020155", selection="nhl-2026020155:home_+1.5",
        title="Toronto +1.5 on the puck line against the Rangers",
        selection_label="Toronto Maple Leafs +1.5 (puck line)",
        body=("Selection: Toronto Maple Leafs +1.5 on the puck line against the New York Rangers at "
              "Scotiabank Arena. Toronto are 5-4-2 through eleven games, have scored 38 goals at 3.45 per "
              "game and conceded 34, and they beat San Jose 3-1 on 19 October. Auston Matthews has 8 goals "
              "and 18 points in eleven games on 33 shots, with William Nylander adding 6 goals and 15 points. "
              "The Rangers are 7-3-1 and beat Anaheim 5-2, so this line needs the Leafs to avoid a two-goal "
              "defeat rather than to win."),
        facts=[
            ("Toronto record 5-4-2, 38 goals for, 34 against in 11 games", "nhl-team-summary"),
            ("Toronto beat San Jose 3-1 on 19 October", "nhl-scoreboard"),
            ("Matthews 8 goals, 18 points, 33 shots; Nylander 6 goals, 15 points", "nhl-skaters-tor"),
            ("Rangers 7-3-1; beat Anaheim 5-2 on 19 October", "nhl-team-summary"),
            ("Rangers skaters: Lafreniere 7+6, Fox 0+10, Zibanejad 2+7", "nhl-skaters-nyr"),
        ],
        model_note=("Expected goals from the club rates: Toronto 2.82, Rangers 3.05. The model gives "
                    "Toronto a 23.2% chance of winning by two or more, so +1.5 lands at 70.64% (fair -241)."),
    ),
    dict(
        id="P-2988-02", fixture="nhl-2026020156", selection="nhl-2026020156:away_over_1.5",
        title="San Jose to score two or more at Ottawa",
        selection_label="San Jose Sharks over 1.5 team goals",
        body=("Selection: San Jose Sharks to score over 1.5 goals, meaning two or more, against the Ottawa "
              "Senators at Canadian Tire Centre. San Jose have 26 goals in ten games and Macklin Celebrini "
              "leads them with 5 goals, 9 assists and 14 points in eight appearances on 37 shots. The Sharks "
              "scored four in a 4-3 overtime win at Montreal on 20 October, a night after a 3-1 loss at "
              "Toronto, and Ottawa have conceded 24 goals in ten games, so two goals is a measured ask."),
        facts=[
            ("San Jose 26 goals in 10 games", "nhl-team-summary"),
            ("Celebrini 5 goals, 9 assists, 14 points, 37 shots in 8 games", "nhl-skaters-sjs"),
            ("Sharks won 4-3 in overtime at Montreal on 20 October", "nhl-scoreboard"),
            ("Sharks lost 3-1 at Toronto on 19 October", "nhl-scoreboard"),
            ("Ottawa conceded 24 goals in 10 games (2.40 per game)", "nhl-team-summary"),
        ],
        model_note=("Sharks scoring rate is modelled at 2.50 goals; P(2 or more) = 71.27% on the independent "
                    "Poisson line, a fair price of -248."),
    ),
]

FLAGS = [
    dict(id="F-2988-01", severity="high",
         title="The brief's two High rules only overlap in a 1.43-point window",
         detail=("A probability above 70% implies a fair price shorter than -233.33; a fair price no shorter "
                 "than -250 implies a probability at or below 71.4286%. Obeying both at once leaves "
                 "70.00%-71.43%. 127 of the 600 priced selections clear 70%; seven sit inside the window; "
                 "two carry complete evidence and are labelled High. The five in-window selections labelled "
                 "Medium are listed on the High-confidence page with the reason each was capped."),
         sources=["nhl-team-summary"]),
    dict(id="F-2988-02", severity="medium",
         title="NBA fixtures are officially confirmed but deliberately unpriced",
         detail=("The NBA schedule page confirms Cleveland at Philadelphia (23:00Z) and Denver at Oklahoma "
                 "City (01:30Z). No price is published: the 2026-27 sample is one game, Denver's record was "
                 "not read, and this desk does not insert a default rating."),
         sources=["nba-schedule", "nba-standings"]),
    dict(id="F-2988-03", severity="high",
         title="EuroLeague fixtures are not confirmed on the official game centre",
         detail=("The official standings page rendered all 20 clubs, but the game centre returned club "
                 "filters and logos only, with no fixture rows. Three EuroLeague fixtures listed by OLBG are "
                 "therefore published as discovery-only and unpriced. Their linked records are official."),
         sources=["el-standings", "el-game-center", "olbg-basketball"]),
    dict(id="F-2988-04", severity="medium",
         title="Darts listings could not be verified: the PDC site returned a consent wall",
         detail=("Three darts matches were discovered through OLBG. pdc.tv returned a cookie-consent page "
                 "with no fixture content on this read, so no darts fixture is verified and no darts price "
                 "is published."),
         sources=["pdc", "olbg-home"]),
    dict(id="F-2988-05", severity="medium",
         title="Tennis fixtures are unverified: ATP's current-scores page showed completed matches only",
         detail=("atptour.com/en/scores/current rendered six completed round-of-16 matches and no upcoming "
                 "order of play. Fifteen tennis listings carried over from OLBG are published as discovery "
                 "only, with blank prices."),
         sources=["atp-current", "olbg-tennis"]),
    dict(id="F-2988-06", severity="medium",
         title="MLB prices use full-season run rates, not postseason inputs",
         detail=("Both World Series teams' rates come from 162 regular-season games. Starting pitchers, "
                 "bullpen usage, park effects and postseason form are not modelled, so no MLB selection is "
                 "labelled High and the caveat is printed on every MLB market block."),
         sources=["mlb-standings", "mlb-mil-hitting", "mlb-mil-pitching"]),
    dict(id="F-2988-07", severity="medium",
         title="NHL model has no goaltender, injury, rest or home-ice adjustment",
         detail=("The NHL line uses club goals for and against per game only. Goaltender starts, injuries, "
                 "back-to-backs and home-ice advantage are absent, so every NHL price carries model risk "
                 "that is not quantified here."),
         sources=["nhl-team-summary"]),
    dict(id="F-2988-08", severity="low",
         title="Anaheim +1.5 at New Jersey misses the band by 0.05 points",
         detail=("The model computes 71.48% for Anaheim +1.5, a fair price of -250.6, which rounds to -251 "
                 "and is therefore outside the -250 floor. It is published as Medium rather than re-rounded "
                 "into the band."),
         sources=["nhl-team-summary"]),
    dict(id="F-2988-09", severity="low",
         title="Later World Series games are conditional",
         detail=("Games 2-6 are scheduled by MLB in advance; they are only played if the series continues. "
                 "The feed returns status Scheduled, which is a schedule entry, not a guarantee that the "
                 "game takes place. Their model prices carry that caveat."),
         sources=["mlb-schedule"]),
    dict(id="F-2988-10", severity="info",
         title="OLBG tip shares are votes, not probabilities",
         detail=("OLBG was used for discovery only. Its percentage next to a selection is the share of "
                 "community tips, not a modelled chance, and it is never used as an input to a price."),
         sources=["olbg-nhl", "olbg-mlb"]),
    dict(id="F-2988-11", severity="high",
         title="Eleven in-scope sports had no official read in this session",
         detail=("Snooker (OLBG hub returned no tips), rugby union (fixtures URL 404), rugby league, golf, "
                 "handball, volleyball, Australian rules, eSports, Gaelic football, greyhounds and motor "
                 "racing have no verified fixture here. They are shown as gaps, not as empty slates."),
         sources=["olbg-snooker", "urc"]),
    dict(id="F-2988-13", severity="info",
         title="Per-request read timestamps were removed and replaced by one read window",
         detail=("A first draft of this desk stamped every source with a minute-level read time. The fetch "
                 "tool does not expose per-request HTTP metadata, so those stamps would have been invented. "
                 "They are replaced by one honest observation window (20:48Z-20:59Z on 22 Oct 2026) plus the "
                 "order in which the reads were issued. No fixture, price or prediction changed."),
         sources=["olbg-home"]),
    dict(id="F-2988-12", severity="info",
         title="Prices are our own estimates, not bookmaker offers",
         detail=("Every price is 1/p from the stated model with no margin. Nothing here is an available "
                 "quote, a bet, or a claim of an edge against a bookmaker."),
         sources=["nhl-team-summary", "mlb-standings"]),
]

REPO_REVIEW = [
    dict(id="R-2988-01", severity="medium", title="Duplicate section numbers in COORDINATION.md",
         detail="Section 4 appears twice (lines 185 and 2330), section 13 twice (722 and 729) and section 43 twice (2160 and 2525).",
         evidence="COORDINATION.md:185,2330,722,729,2160,2525"),
    dict(id="R-2988-02", severity="medium", title="Duplicate task identifiers",
         detail="T63 is claimed by two rows (lines 123 and 125) and T64 by two (129 and 2941); T1-T7 each appear twice because a second recap table repeats the board.",
         evidence="COORDINATION.md:123,125,129,2941,69-75,259-265"),
    dict(id="R-2988-03", severity="medium", title="Six rows still marked in progress beyond the 60-minute rule",
         detail="T9 (started 2026-10-21T05:26Z), T19, T51, T52, T-FEC (whose own text says DONE) and T97DC remain 'in progress' on a board whose §0.4 allows takeover after 60 minutes without a commit.",
         evidence="COORDINATION.md:77,89,112,113,133,134"),
    dict(id="R-2988-04", severity="low", title="Seventeen published pages exceed 200 KB",
         detail="The largest is 1a421e41/markets.html at 1,064,556 bytes; four more exceed 700 KB. Large pages slow first paint on mobile but are not broken.",
         evidence="1a421e41/markets.html, f71557b5/markets.html, verification.html"),
    dict(id="R-2988-05", severity="info", title="Repository link and provenance gate passes",
         detail="scripts/validate.py reported 134 primary fixtures, 126 H2H line books, 30 legacy high-confidence predictions and 765 published pages checked with 0 errors and 3 pre-existing warnings in f7fa77fc/flagged.html.",
         evidence="scripts/validate.py output, 2026-10-22T21:30Z"),
    dict(id="R-2988-06", severity="info", title="Legacy desks are archives, not current evidence",
         detail="This desk did not re-fetch or re-certify any other session's rows. Where a legacy desk labels a selection High, that label remains that session's claim.",
         evidence="data/*/desk.json, 1a421e41/, d7d19a67/, 7f000cb6/ etc."),
    dict(id="R-2988-07", severity="low", title="This session's claim was written before the work",
         detail="The T2988 row and §60 were committed and pushed before any data file was created, per §0.3 of the board.",
         evidence="COORDINATION.md:137, commit 12a18ad"),
    dict(id="R-2988-08", severity="info", title="No shared file was edited",
         detail="Only data/2988bd19/**, scripts/s2988bd19_*.py, 2988bd19/**, reports/SESSION_2988BD19.md and append-only COORDINATION.md are touched by this session.",
         evidence="git diff --name-only origin/main...HEAD"),
]


# ------------------------------------------------------------------ summary structures
def summarise(fixtures, markets, discovered):
    by_id = {m["id"]: m for m in markets}
    picks = []
    for f in fixtures:
        m = by_id.get(f["id"])
        if not m:
            continue
        ml = [s for s in m["selections"] if s["key"] in ("home_ml", "away_ml")]
        best = max(ml, key=lambda s: s["p"])
        picks.append(dict(fixture_id=f["id"], selection=best["label"], p=best["p"],
                          fair_decimal=best["fair_decimal"], american=best["american"],
                          tier=best["tier"], tier_note=best["tier_note"]))
    all_sel = [s for m in markets for s in m["selections"]]
    high = [s for s in all_sel if s["tier"] == "High"]
    in_band = [s for s in all_sel if 0.70 < s["p"] <= 0.7142857]
    return dict(picks=picks, selections=all_sel, high=high, in_band=in_band,
                above_70=[s for s in all_sel if s["p"] > 0.70],
                above_band=[s for s in all_sel if s["p"] > 0.7142857])


def coverage(fixtures, discovered):
    rows = []
    counts = {}
    for f in fixtures:
        c = counts.setdefault(f["sport"], dict(listings=0, verified=0, priced=0, high=0))
        c["listings"] += 1
        if f["verification"] == "official":
            c["verified"] += 1
            if f.get("priced"):
                c["priced"] += 1
    for d in discovered:
        c = counts.setdefault(d["sport"], dict(listings=0, verified=0, priced=0, high=0))
        c["listings"] += 1
    for s, _ in D.SPORTS:
        c = counts.get(s, dict(listings=0, verified=0, priced=0, high=0))
        if s == "ice-hockey":
            note = "Full 12-game NHL slate read from the league schedule feed; every club's totals read from the NHL stats API."
            status = "Covered"
        elif s == "baseball":
            note = "Six World Series fixtures read from the MLB schedule API; run rates from official season totals."
            status = "Covered"
        elif s == "basketball":
            note = "Two NBA fixtures confirmed, unpriced (one-game sample). Three EuroLeague fixtures discovery-only: the official game centre rendered no fixture rows."
            status = "Partial"
        elif s == "tennis":
            note = "15 OLBG listings, none confirmed: the ATP current-scores page showed completed matches only."
            status = "Discovery only"
        elif s == "cricket":
            note = "Three OLBG listings, none confirmed: no governing-body fixture page was read."
            status = "Discovery only"
        elif s == "darts":
            note = "Three OLBG listings, none confirmed: the PDC site returned a consent wall."
            status = "Discovery only"
        elif s == "snooker":
            note = "OLBG's snooker hub returned 'No tips found'; no official read."
            status = "No fixture found"
        else:
            note = "No official source read in this session. Published as a gap, not as an empty fixture list."
            status = "Gap"
        rows.append(dict(sport=s, name=D.SPORT_NAME[s], status=status, listings=c["listings"],
                         verified=c["verified"], priced=c["priced"], high=c["high"], note=note))
    return rows
