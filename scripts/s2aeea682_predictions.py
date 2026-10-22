"""Bespoke, evidence-bounded prose for each featured High selection."""
import re

TEXTS = {
    "mlb-849805": (
        "Milwaukee reach Game 1 with four consecutive NLCS wins over Los Angeles, the latest 6-4 on "
        "15 October, while Tampa Bay’s most recent final was a 7-3 home win against Cleveland on 19 October. "
        "Christian Yelich is on Milwaukee’s active roster and Junior Caminero on Tampa Bay’s; neither is being "
        "treated as a confirmed starter. The regular-season scoring model centres at 8.75 combined runs, so my "
        "selection is Under 10 total runs, with exactly ten refunded."
    ),
    "mlb-849802": (
        "Game 2 keeps the clubs at American Family Field, where Milwaukee’s official regular-season home split "
        "is 55-26; Tampa Bay’s away split is 43-38. The Brewers also own an 8-2 last-ten mark compared with 5-5 "
        "for the Rays. William Contreras and Yandy Díaz appear on the respective active rosters, while recent "
        "finals include Milwaukee’s 6-2 win at Dodger Stadium and Tampa Bay’s 3-1 win at Cleveland. Under 10 "
        "runs is the play; ten is a push."
    ),
    "mlb-849804": (
        "The venue changes to Tropicana Field for Game 3, and Tampa Bay’s official log shows a 7-3 win over "
        "Cleveland there on 19 October after a 3-1 victory at Cleveland one day earlier. Milwaukee’s most recent "
        "road results were 6-2 and 6-4 at Los Angeles. Jonathan Aranda and Jackson Chourio are active-roster "
        "names, not projected lineup locks. With no pitcher or park adjustment invented, the originated total "
        "remains Under 10 runs; exactly ten returns the stake."
    ),
    "mlb-849803": (
        "Recent form is less one-sided than the season records suggest: Tampa Bay have won three straight listed "
        "finals, while Milwaukee swept the four NLCS games shown on its official October schedule. Drew Rasmussen "
        "and Brice Turang are on the active rosters, but this preview makes no starting-pitcher assumption. The "
        "Rays’ latest three scorelines were 7-3, 3-1 and 7-3; Milwaukee last won 6-4. For Game 4, take Under 10 "
        "total runs, with a refund at ten."
    ),
}

FACTS = {
    "mlb-849805": [
        ("team","World Series Game 1, Tampa Bay at Milwaukee, American Family Field, 24 October 00:00 UTC","mlb-schedule"),
        ("form","Milwaukee won all four listed NLCS games against Los Angeles; latest 6-4 on 15 October","mlb-mil-form"),
        ("history","Tampa Bay's latest final was 7-3 against Cleveland on 19 October","mlb-tb-form"),
        ("player","Christian Yelich is on Milwaukee's active roster","mlb-mil-roster"),
        ("player","Junior Caminero is on Tampa Bay's active roster","mlb-tb-roster"),
        ("selection","Under 10 is an originated model selection; exactly 10 is refunded","mlb-al"),
    ],
    "mlb-849802": [
        ("team","Game 2 remains at American Family Field on 25 October 00:00 UTC","mlb-schedule"),
        ("form","Milwaukee 55-26 at home and 8-2 last ten","mlb-nl"),
        ("form","Tampa Bay 43-38 away and 5-5 last ten","mlb-al"),
        ("history","Milwaukee won 6-2 at Los Angeles","mlb-mil-form"),
        ("history","Tampa Bay won 3-1 at Cleveland on 18 October","mlb-tb-form"),
        ("player","William Contreras is on Milwaukee's active roster","mlb-mil-roster"),
        ("player","Yandy Díaz is on Tampa Bay's active roster","mlb-tb-roster"),
    ],
    "mlb-849804": [
        ("team","World Series Game 3 is at Tropicana Field on 27 October 00:00 UTC","mlb-schedule"),
        ("form","Tampa Bay won 7-3 at home on 19 October after a 3-1 win at Cleveland on 18 October","mlb-tb-form"),
        ("history","Milwaukee's last two road finals were 6-2 and 6-4 at Los Angeles","mlb-mil-form"),
        ("player","Jonathan Aranda is on Tampa Bay's active roster","mlb-tb-roster"),
        ("player","Jackson Chourio is on Milwaukee's active roster","mlb-mil-roster"),
        ("selection","Under 10 is an originated model selection; exactly 10 is refunded","mlb-nl"),
    ],
    "mlb-849803": [
        ("team","World Series Game 4, Milwaukee at Tampa Bay, 28 October 00:00 UTC","mlb-schedule"),
        ("form","Tampa Bay's last three listed finals are wins","mlb-tb-form"),
        ("form","Milwaukee won all four listed NLCS games","mlb-mil-form"),
        ("history","Tampa Bay's last three scorelines are 7-3, 3-1 and 7-3","mlb-tb-form"),
        ("history","Milwaukee's latest final is 6-4 at Los Angeles","mlb-mil-form"),
        ("player","Drew Rasmussen is on Tampa Bay's active roster","mlb-tb-roster"),
        ("player","Brice Turang is on Milwaukee's active roster","mlb-mil-roster"),
    ],
}


def words(text):
    return re.findall(r"\b[\w’'-]+\b",text,flags=re.UNICODE)


def ngrams(text,n=8):
    w = [x.casefold() for x in words(text)]
    return {" ".join(w[i:i+n]) for i in range(len(w)-n+1)}


def attach(fixtures,featured):
    predictions = []
    by_id = {f["id"]:f for f in fixtures}
    for i,high in enumerate(featured,1):
        fid = high["fixture_id"]
        if fid not in TEXTS:
            raise ValueError(f"No bespoke prediction authored for featured High {fid}")
        text = TEXTS[fid]
        f = by_id[fid]
        predictions.append({"id":f"P-2AEE-{i:02d}","fixture_id":fid,"market_id":high["market_id"],
                            "sport":f["sport"],"selection":high["selection"],"tier":"High",
                            "probability":high["probability"],"fair_american":high["fair_american"],
                            "text":text,"word_count":len(words(text)),
                            "facts":[{"kind":kind,"claim":claim,"source_id":src} for kind,claim,src in FACTS[fid]],
                            "official_link":f["official_link"]})
    return predictions


def check(desk):
    problems = []
    predictions = desk["predictions"]
    featured = desk["featured_high"]
    if len(predictions) != len(featured):
        problems.append("featured High / prediction count mismatch")
    if {p["fixture_id"] for p in predictions} != {h["fixture_id"] for h in featured}:
        problems.append("featured High / prediction fixture IDs differ")
    seen = {}
    for p in predictions:
        if p["word_count"] < 30 or len(words(p["text"])) < 30:
            problems.append(f"{p['id']} is under 30 words")
        if p["word_count"] != len(words(p["text"])):
            problems.append(f"{p['id']} word count mismatch")
        if p["probability"] <= .70 or not (-250 <= p["fair_american"] <= 10000):
            problems.append(f"{p['id']} fails High probability/window")
        if "under 10" not in p["text"].casefold():
            problems.append(f"{p['id']} selection is not obvious in prose")
        kinds = {f["kind"] for f in p["facts"]}
        for required in ("team","player","form","history"):
            if required not in kinds:
                problems.append(f"{p['id']} lacks {required} evidence")
        for fact in p["facts"]:
            if fact["source_id"] not in {s["id"] for s in desk["sources"] if s["official"]}:
                problems.append(f"{p['id']} fact lacks official source")
        for gram in ngrams(p["text"]):
            if gram in seen:
                problems.append(f"repeated 8-gram between {seen[gram]} and {p['id']}: {gram}")
            seen[gram] = p["id"]
    return problems
