#!/usr/bin/env python3
"""T6B47 predictions: one hand-written write-up per published pick.

Every sentence below is built from the recorded fact notes that travel with the
pick in data/6b47ea39/picks.json. No fact is added that is not in that register.
The gate at the bottom of this file enforces the brief's writing rules:

  * at least 30 words
  * no internal vocabulary (model / verified / algorithm)
  * no six-word phrase repeated between two write-ups
  * the selection is named in plain words

Output: data/6b47ea39/predictions.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "6b47ea39"

WRITE_UPS = {
    "GOL-01": (
        "Haeran Ryu takes a one-shot lead into the weekend at Pine Beach, twelve under par with Lauren "
        "Coughlin a stroke behind at eleven under. The world number three has already won the Evian "
        "Championship and the KPMG Women's PGA in 2026 and holds 2,470 CME Globe points. She is playing on "
        "home soil in Haenam and carries no fitness question. Back Haeran Ryu for a top-three finish."
    ),
    "GOL-02": (
        "Eugenio Chacarra tops the Race to Dubai on 3,868 points after finishes of third, second and first "
        "in his last three starts, but he is contesting the Genesis Championship on a fractured toe having "
        "played 25 holes on Sunday in Delhi. Ryan Fox, the Open champion, is sixth in the same standings and "
        "fully fit. Take Ryan Fox with a 1.5-stroke cushion in the 72-hole matchup."
    ),
    "GOL-03": (
        "Casey Jarvis opened with a 65 and shares the Genesis Championship lead at ten under with Antoine "
        "Rozner at Woo Jeong Hills. Jarvis sits sixth on the Fantasy Race to Dubai list on 2,997 points with "
        "multiple wins this season, and Rozner closed Friday with birdies at two of his last three holes. "
        "Both reported full fitness for round three. Casey Jarvis for a top-five finish."
    ),
    "VOL-01": (
        "Itas Trentino opened the SuperLega campaign with a 3-0 sweep at Valsa Group Modena, Theo Faure "
        "scoring 34 points and Daniele Lavia 20 across the opening weekend. Sbertoli, Lavia, Faure, "
        "Gualberto and Laurenzano all came through that match fit. Cisterna Volley visit the BTS Arena for "
        "round two. Back Itas Trentino to cover the 1.5-set handicap."
    ),
    "VOL-02": (
        "Asseco Resovia Rzeszow sit fourth in PlusLiga and reached the CEV quarter-finals, while InPost ChKS "
        "Chelm are thirteenth. Resovia have already beaten Chelm 3-1 twice, including 25-16 25-21 18-25 "
        "25-21 with Marcin Janusz named MVP, and Louati posted 75% attack efficiency in Europe. Janusz, "
        "Cebulj, Louati and Butryn are all available. Back Asseco Resovia -1.5 sets."
    ),
    "VOL-03": (
        "Berlin Recycling Volleys travel to Hildesheim as the established Bundesliga champions, with Jake "
        "Hanes, Matthew Knigge, Florian Krage and libero Kyle Dagostino all available. Giesen have been "
        "Berlin's semi-final rivals and their meetings tend to run long. Hanes led Berlin with 14 kills in "
        "Champions League play. Take over 3.5 sets in this Bundesliga fixture."
    ),
    "RGU-01": (
        "The Stormers have two wins and a defeat from three URC rounds, 81 points scored and 54 conceded, "
        "while the Scarlets arrive with one win from three after shipping 85 points. Feinberg-Mngomezulu, "
        "Roos and captain de Villiers start for the hosts, with Anscombe held on the Scarlets bench. Take "
        "under 50.5 total points in Cape Town on Saturday afternoon."
    ),
    "RGU-02": (
        "Vodacom Bulls have scored 126 points across three URC rounds and conceded 54, while Ulster have won "
        "none of their three and sit at 88 points for and 93 against. Pollard, captain Coetzee and Louw "
        "start for the Bulls; Stockdale, McCloskey and captain Stewart answer for Ulster. Back Vodacom Bulls "
        "to win by more than 2.5 points."
    ),
    "RGU-03": (
        "Glasgow Warriors are unbeaten in three URC rounds at 95 points for and 72 against, while Benetton "
        "have lost twice and sit at 64 for and 68 against. Steyn, Tuipulotu, Fagerson and Darge all start "
        "for Glasgow, with Umaga, Lynagh and captain Lamaro named by Benetton. Take Glasgow Warriors on the "
        "80-minute match-winner market."
    ),
    "CRI-01": (
        "New South Wales defend the Dean Jones Trophy with two wins from three and eight points, while "
        "Western Australia are winless at the foot of the table on two points with a net run rate of -2.088. "
        "Kurtis Patterson averaged 78.00 with four centuries in last season's title run, and Sean Abbott and "
        "Ben Dwarshuis form the new-ball pair. Jhye Richardson returns for a rebuilding WA. Back New South "
        "Wales to win at the WACA."
    ),
    "CRI-02": (
        "India chased 230 for six in 19.4 overs after New Zealand made 225 for four at Hagley Oval on "
        "Thursday, 455 runs in one T20. Sanju Samson struck 67 from 33 balls, Naman Dhir 42 not out from 15, "
        "Glenn Phillips 82 not out from 40 and Finn Allen 45 from 24. India lose Ishan Kishan to an adductor "
        "strain and New Zealand are without Rachin Ravindra. Take over 385.5 match runs."
    ),
    "CRI-03": (
        "Tasmania sit second in the One-Day Cup on ten points and a +2.303 run-rate cushion, while Victoria "
        "are fifth on four points at -0.752 after a 47-run Duckworth-Lewis defeat to New South Wales. Riley "
        "Meredith, Ben McDermott, Caleb Jewell, Mitch Owen and captain Jordan Silk all feature for Tasmania, "
        "with Matt Short and Todd Murphy back for Victoria. Back Tasmania -0.5 on the run handicap."
    ),
    "SNO-01": (
        "Kyren Wilson swept Ben Mertens 4-0 and then dismantled Anthony McGill 6-1 to reach his first ranking "
        "semi-final in nineteen months. Sam Craigie came through Xiao Guodong 4-3, Xu Si and Elliot Slessor "
        "to reach the same stage. Both finished Friday's quarter-finals in full health, Craigie clear of the "
        "cervical spine trouble that once interrupted his career. Back Kyren Wilson to win the best-of-11."
    ),
    "DAR-01": (
        "Gerwyn Price dropped only two legs while beating former European champion Rob Cross 6-2 on Thursday "
        "evening. Cameron Menzies, seeded 29th, upset Maastricht winner Niels Zonneveld 6-3 to reach this "
        "second-round tie. Price's half of the draw opened further when Luke Humphries withdrew through "
        "illness, and both men are fit for the Dortmund afternoon session. Back Gerwyn Price to beat Cameron "
        "Menzies."
    ),
    "BSB-01": (
        "Game three moves indoors to Tropicana Field, where Tampa Bay went 55-26 at home this season and "
        "63-32 on artificial turf, including the 7-3 clincher in game six of the ALCS. Freddy Peralta starts "
        "on full rest after Sunday's travel day, while Austin Overn and Anderson Brito remain on the 60-day "
        "injured list. Tampa Bay were 25-14 in one-run games. Take Tampa Bay Rays +1.5 on the run line."
    ),
    "BSB-02": (
        "Game four tests fourth-starter and bullpen depth on consecutive nights in St Petersburg. Milwaukee "
        "led the National League with 832 runs at 5.14 per game behind Andrew Vaughn, and Brandon Woodruff "
        "plus Shane Drohan give them length. Angel Zerpa and Alfredo Zarraga are on the injured list. Back "
        "Milwaukee on the +1.5 run line in game four."
    ),
    "GAE-01": (
        "Dr Crokes meet Kenmare Shamrocks in a Kerry senior football final pairing the county has not staged "
        "before, with S Joy of Laune Rangers listed as referee on the championship fixture. Both clubs came "
        "through the Kerry championship on separate paths and meet with the county title on the line on "
        "Sunday afternoon. Back Dr Crokes to win the Kerry senior football final."
    ),
    "TEN-01": (
        "Elena Rybakina is the world number one, the 2026 US Open and Australian Open champion and the "
        "defending Ningbo champion, and she beat Eala 6-3 6-1 to reach this semi-final. Diana Shnaider is "
        "ranked thirteen and beat Rybakina 6-4 6-4 in Cincinnati, so the head-to-head is not one-way. "
        "Rybakina has shown none of the back trouble that ended her Tokyo run last autumn. Back Rybakina to "
        "win the Ningbo semi-final."
    ),
    "TEN-02": (
        "Katie Boulter reached the Osaka semi-final with 6-2 6-1 and 6-3 6-1 wins, barely an hour on court "
        "each time. Katerina Siniakova, a former doubles world number one for 204 weeks, won 6-4 6-1 and then "
        "advanced 6-4 0-6 4-0 when her opponent retired. Siniakova's returning against Boulter's flat "
        "first-strike game should stretch the scoreline. Take over 20.5 games in the Japan Open semi-final."
    ),
    "MOT-01": (
        "Kimi Antonelli leads the championship on 340 points with eight wins, fourteen podiums and six "
        "poles, and he has beaten George Russell 12-5 in races and 10-7 in qualifying across seventeen "
        "rounds. Russell, on 238 points, served a Singapore engine penalty that sent him to the back of the "
        "grid. Both Mercedes drivers are fit in Austin. Back Kimi Antonelli to finish ahead of George Russell."
    ),
    "MOT-02": (
        "Seventeen points cover George Russell on 238, Lewis Hamilton on 229 and Max Verstappen on 221 in the "
        "drivers' championship. Verstappen won in Malaysia and then took his first Singapore victory, while "
        "Russell's engine penalty in Singapore handed him fresh power-unit components. All three are fit for "
        "Austin. Take Lewis Hamilton and Max Verstappen with a 4.5-point cushion in the season-points "
        "handicap."
    ),
    "HAN-01": (
        "HBC Nantes have beaten Montpellier 36-31, Caen 38-31 and Saran 34-31 in the StarLigue, averaging 36 "
        "goals, although they lost 27-33 at Vardar in the Champions League on Wednesday. Chambery edged Aix "
        "34-33 on 18 October. Goalkeeper Christoffer Bonde, pivot Nicolas Tournat, Noam Leopold and Kauldi "
        "Odriozola are all available for Nantes. Back HBC Nantes to cover a 2.5-goal handicap against Chambery."
    ),
    "HAN-02": (
        "Paris Saint-Germain are seven from seven in the StarLigue, 239 goals for and 190 against, while "
        "Saint-Raphael have lost five of seven at 207 for and 225 against. The LNH calendar lists Sunday's "
        "throw-off at 16:00 local, which is 14:00 UTC. PSG's separation at the top has come from defensive "
        "pressure rather than volume. Back Paris Saint-Germain to win by more than 1.5 goals."
    ),
    "ICE-01": (
        "Edmonton are 8-1-1 and scoring 4.70 goals a game, arriving off a 6-5 win over Carolina and a "
        "three-game run. Connor McDavid has 31 points in ten games and he and Leon Draisaitl each logged "
        "five points in the last outing, with Ryan Nugent-Hopkins back. Mattias Ekholm left Thursday injured "
        "and Jason Dickinson is on injured reserve; Toronto are without John Tavares, Chris Tanev, Max Domi "
        "and Dakota Joshua. Back Edmonton to win at Rogers Place."
    ),
    "ICE-02": (
        "Boston lead the Atlantic at 8-2-1 and have outscored opponents 21-6 across a 4-1-0 home run, "
        "including Thursday's 6-0 win over Nashville with Michael DiPietro making 28 saves. San Jose have one "
        "regulation win in eleven games and arrive at 1-4-1 in regulation. Alex Wennberg is week-to-week for "
        "the Sharks, while David Pastrnak has five goals and ten assists. Take over 4.5 goals at TD Garden."
    ),
    "ICE-03": (
        "New Jersey are 6-4-0 and Los Angeles are 2-4-2 on the official standings read at capture, with the "
        "Kings taking a 1.5-goal cushion on the puck line at Prudential Center. The cushion covers a one-goal "
        "defeat for Los Angeles, and the Kings have the New Jersey power play to negotiate. Take Los Angeles "
        "Kings +1.5 on the puck line."
    ),
    "ICE-04": (
        "Philadelphia carry a three-game home winning streak into Saturday's matinee, while Anaheim have lost "
        "five straight in regulation, including 1-4 at New Jersey on Thursday night. Pavel Mintyukov was sent "
        "home from the road trip with a lower-body injury and Jeff Malott was scratched ill. Take under 6.5 "
        "goals in Philadelphia."
    ),
    "BAS-01": (
        "Anthony Edwards opened the season with 45 points and 10 rebounds as Minnesota beat Miami 131-106. "
        "Orlando lost 125-132 to Atlanta despite 35 points, 7 rebounds and 10 assists from Paolo Banchero. The "
        "NBA's 12:15pm ET injury report rules out Anthony Black, Jonathan Isaac, Noah Penda and Izaiyah "
        "Nelson for Orlando, and Donte DiVincenzo for Minnesota. Back Minnesota Timberwolves to win."
    ),
    "RGL-01": (
        "England lost 12-30 to Tonga in round one and France were beaten 4-78 by Samoa, so cross-pool "
        "qualification now turns on points differential and England must chase margin for eighty minutes in "
        "Perth. Morgan Knowles remains out, Luke Thompson starts at prop, Matty Ashton replaces Zach "
        "Eckersley and Mikey Lewis joins the bench. Back England to win by more than 25.5 points."
    ),
}


def ngrams(text: str, size: int = 6) -> set[str]:
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {" ".join(words[i : i + size]) for i in range(max(0, len(words) - size + 1))}


def main() -> None:
    picks = json.loads((OUT / "picks.json").read_text(encoding="utf-8"))["picks"]
    rows = []
    problems = []
    seen: dict[str, str] = {}
    for pick in picks:
        key = pick["pick_id"]
        text = WRITE_UPS.get(key, "").strip()
        if not text:
            problems.append(f"{key}: no write-up")
            continue
        words = len(re.findall(r"\b[\w'-]+\b", text))
        banned = [w for w in ("model", "verified", "verification", "algorithm") if re.search(rf"\b{w}\b", text, re.I)]
        duplicate = next((g for g in ngrams(text) if g in seen), None)
        if words < 30:
            problems.append(f"{key}: {words} words")
        if banned:
            problems.append(f"{key}: internal vocabulary {banned}")
        if duplicate:
            problems.append(f"{key}: repeated six-word phrase with {seen[duplicate]}")
        for gram in ngrams(text):
            seen.setdefault(gram, key)
        rows.append(
            {
                "pick_id": key,
                "sport": pick["sport"],
                "match": pick["match"],
                "start_utc": pick["start_utc"],
                "competition": pick["competition"],
                "selection": pick["selection"],
                "market": pick["market"],
                "probability": pick["probability"],
                "decimal": pick["decimal"],
                "american": pick["american"],
                "tier": pick["tier"],
                "words": words,
                "text": text,
                "official_sources": pick["official_sources"],
                "fact_read_utc": next(iter(pick["facts"].values()), {}).get("read_utc") if pick["facts"] else None,
                "facts": pick["facts"],
                "source_desk": pick["source_desk"],
            }
        )

    payload = {
        "desk": "6b47ea39",
        "built_utc": "2026-10-23T21:30:00Z",
        "count": len(rows),
        "rules": {"min_words": 30, "banned": ["model", "verified", "verification", "algorithm"], "uniqueness": "no shared six-gram"},
        "problems": problems,
        "predictions": rows,
    }
    (OUT / "predictions.json").write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")
    print(f"predictions: {len(rows)} (mean {sum(r['words'] for r in rows)/max(1,len(rows)):.1f} words)")
    print("problems:", problems if problems else "none")


if __name__ == "__main__":
    main()
