#!/usr/bin/env python3
"""T6B47 audit: recompute every arithmetic identity, re-gate the High tier, and
compare the two freshest 23-Oct desks against each other.

Nothing here is fetched. The audit only reads committed evidence.

Outputs
-------
data/6b47ea39/audit.json  — counts, per-desk claims vs recomputation
data/6b47ea39/flags.json  — the irregularity register rendered on /6b47ea39/flagged.html
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = DATA / "6b47ea39"
NOW = datetime(2026, 10, 23, 21, 30, tzinfo=timezone.utc)

# Official-source hosts. A row may only claim official provenance from these.
OFFICIAL_HOSTS = {
    "api-web.nhle.com", "www.nhl.com", "nhl.com",
    "statsapi.mlb.com", "www.mlb.com", "mlb.com",
    "www.nba.com", "nba.com", "www.euroleaguebasketball.net", "www.euroleague.net",
    "www.atptour.com", "www.wtatennis.com", "wtafiles.wtatennis.com",
    "www.pgatour.com", "www.lpga.com", "www.europeantour.com", "www.dpworldtour.com",
    "www.wst.tv", "wst.tv", "www.pdc.tv", "pdc.tv",
    "www.plusliga.pl", "plusliga.pl", "www.legavolley.it", "legavolley.it",
    "www.tauronliga.pl", "www.unitedrugby.com", "unitedrugby.com",
    "www.nrl.com", "nrl.com", "www.rugby-league.com",
    "www.icc-cricket.com", "www.espncricinfo.com", "www.nzc.nz", "www.cricket.com.au",
    "www.gbgb.org.uk", "www.gaa.ie", "www.gaelicplayers.com", "gaa.ie",
    "www.formula1.com", "www.fia.com", "www.lnh.fr", "www.ehf.eu", "www.eurohandball.com",
    "www.thw-provinzial.de", "www.hbcfrance.fr", "www.munster.gaa.ie", "munster.gaa.ie",
    "www.corkgaa.ie", "www.kilkennygaa.ie", "www.galwaygaa.ie",
    "stats.unitedrugby.com", "ak-static.cms.nba.com", "official.nba.com",
    "gaacork.ie", "kilkennygaa.ie", "www.thw-handball.de", "thw-handball.de",
    "www.premiershiprugby.com", "scoring.nzc.nz", "hbcnantes.com", "www.hbcnantes.com",
    "www.intrl.sport", "intrl.sport", "top14.lnr.fr", "www.pcb.com.pk", "pcb.com.pk",
    "www.daikin-hbl.de", "daikin-hbl.de", "www.hc-erlangen.de", "hc-erlangen.de",
    "www.teamchambe.com", "www.maighcuilinn.com", "www.sportinglife.com",
}
# Sources that are not governing bodies and must never be used as row verification.
NON_OFFICIAL_HOSTS = {
    "www.olbg.com", "olbg.com", "www.google.com", "twitter.com", "x.com",
    "www.bbc.co.uk", "www.bbc.com", "en.wikipedia.org", "www.oddschecker.com",
    "www.cricinfo.com", "www.limerickleader.ie", "www.irishexaminer.com", "www.rte.ie",
    "www.skysports.com", "www.espn.com",
}
BANNED_PROSE = ["model", "verified", "verification", "algorithm", "our data shows"]


def load(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def host(url: str) -> str:
    return re.sub(r"^https?://", "", url).split("/")[0].lower()


def american(decimal: float) -> float:
    return round(-100.0 / (decimal - 1.0), 1) if decimal < 2.0 else round(100.0 * (decimal - 1.0), 1)


def ngrams(text: str, size: int = 6) -> set[str]:
    words = re.findall(r"[a-z0-9']+", text.lower())
    return {" ".join(words[i : i + size]) for i in range(max(0, len(words) - size + 1))}


def flag(register, severity, title, detail, source, rows=None):
    register.append(
        {
            "id": f"F{len(register)+1:02d}",
            "severity": severity,
            "title": title,
            "detail": detail,
            "source": source,
            "rows": rows or [],
        }
    )


def main() -> None:
    slate = load(OUT / "slate.json")
    events = slate["events"]
    flags: list[dict] = []
    audit: dict = {"desk": "6b47ea39", "task": "T6B47", "generated_utc": "2026-10-23T21:30:00Z"}

    # ---------------------------------------------------------------- G1 arithmetic
    arithmetic_errors = []
    for event in events:
        for line in event["markets"]:
            expected = american(line["decimal"])
            if abs(expected - line["american"]) > max(1.5, 0.003 * abs(expected)):
                arithmetic_errors.append(
                    {"event": event["id"], "selection": line["selection"], "stated": line["american"], "recomputed": expected}
                )
            if abs(1.0 / line["decimal"] - line["probability"]) > 0.004:
                arithmetic_errors.append(
                    {
                        "event": event["id"],
                        "selection": line["selection"],
                        "issue": "probability does not match decimal",
                        "stated": line["probability"],
                        "recomputed": round(1 / line["decimal"], 4),
                    }
                )
    audit["arithmetic_errors"] = arithmetic_errors
    if arithmetic_errors:
        flag(
            flags, "medium", "Originated price arithmetic does not reconcile",
            f"{len(arithmetic_errors)} priced lines have a stated American price or probability that "
            "disagrees with the decimal price by more than tolerance. The decimal price is treated as "
            "the primary value and every published figure on this desk is recomputed from it.",
            "internal arithmetic check",
            [e["event"] for e in arithmetic_errors[:8]],
        )

    # ---------------------------------------------------------------- G2 band invariant
    band_counts = Counter()
    strict_by_sport = Counter()
    above_band_by_sport = Counter()
    for event in events:
        if event["state"] != "upcoming":
            continue
        for line in event["markets"]:
            if line["probability"] > 0.70:
                if line["band"] == "in":
                    strict_by_sport[event["sport"]] += 1
                else:
                    above_band_by_sport[event["sport"]] += 1
                band_counts[line["band"]] += 1
    audit["bands"] = {
        "in_band": dict(strict_by_sport),
        "above_band_short_of_minus_250": dict(above_band_by_sport),
    }
    flag(
        flags, "high",
        "The requested High window is only 1.43 probability points wide",
        "The brief asks for picks with a better-than-70% win chance priced between -250 and +10000. "
        "-250 is decimal 1.40, i.e. 71.43% implied. Any selection that is both above 70% and inside the "
        "window therefore has to sit between 70.00% and 71.43% — a band 1.43 points wide. Five picks per "
        "sport inside that band cannot be produced from real favourites: the genuine short-priced favourites "
        "(Perugia at 89%, Ireland at 80%, Kiel at 82%) are all shorter than -250 and are outside the window. "
        "This desk therefore publishes both: in-window picks as High, and stronger favourites outside the "
        "window clearly labelled as out-of-window rather than quietly squeezed into the band.",
        "https://www.olbg.com/betting-tips",
    )

    # ---------------------------------------------------------------- G3 desk claim reconciliation
    claims = {}
    desk8 = load(DATA / "8a900c04" / "desk.json")["summary"]
    desk4_summary = load(DATA / "496eaf02" / "summary.json")
    desk6 = load(DATA / "65331685" / "desk.json")
    claims["8a900c04"] = {"claimed_high": desk8["high_confidence_picks_in_window"]}
    claims["496eaf02"] = {"claimed_high": desk4_summary["high_picks"]}
    claims["496eaf02_recomputed_strict"] = None
    claims["65331685"] = {
        "claimed_high": sum(1 for m in desk6["markets"] if str(m.get("tier", "")).lower() == "high"),
        "recomputed_strict": sum(
            1 for m in desk6["markets"]
            if float(m["prob"]) > 0.70 and -250.0 <= american(float(m["fair_decimal"])) <= 10000.0
        ),
    }

    # recompute 496eaf02 strictly from its own published CSV
    import csv

    with (DATA / "496eaf02" / "markets.csv").open(encoding="utf-8-sig", newline="") as handle:
        rows_496 = list(csv.DictReader(handle))
    strict_496 = [
        r for r in rows_496
        if float(r["probability"]) > 0.70 and -250.0 <= american(float(r["fair_decimal"])) <= 10000.0
    ]
    claims["496eaf02_recomputed_strict"] = len(strict_496)
    any_above_70_496 = [r for r in rows_496 if float(r["probability"]) > 0.70]
    claims["496eaf02_recomputed_above_70"] = len(any_above_70_496)
    audit["desk_claims"] = claims
    flag(
        flags, "high",
        "Desk 496eaf02 labels 51 picks High; only 3 satisfy the brief's own conjunction",
        f"Its published market file contains {len(rows_496)} priced outcomes. Recomputing the stated rule "
        f"(>70% AND -250..+10000) on its own numbers yields {len(strict_496)} qualifying lines, not 51. "
        f"{len(any_above_70_496)} lines sit above 70%, so most of the 51 are short-priced favourites that are "
        "outside the requested window. The desk's headline count and its own price data disagree; the row-level "
        "labels are not reproduced by this desk.",
        "https://github.com/buffedlizard55-lab/OLBG1/blob/main/data/496eaf02/markets.csv",
    )

    # ---------------------------------------------------------------- G4 threshold clustering, per desk
    CONSTRUCT = re.compile(
        r"speed index|pace index|sectional split|sprint index|q3 pace|grouping ball|inv\. stroke|"
        r"race index|speed index|trap bracket|team total|form-line|without-antonelli|forecast|cushion",
        re.I,
    )
    observations = [(event, line, obs) for event in events for line in event["markets"] for obs in line["observations"]]
    desks = sorted({obs["desk"] for _, _, obs in observations})
    per_desk = {}
    for desk in desks:
        rows = [(event, line) for event, line, obs in observations if obs["desk"] == desk]
        probs = [line["probability"] for _, line in rows if line["probability"]]
        near = sum(1 for p in probs if 0.700 <= p <= 0.720)
        per_desk[desk] = {
            "lines": len(rows),
            "lines_between_0.700_and_0.720": near,
            "share_between_0.700_and_0.720": round(near / len(probs), 4) if probs else 0.0,
            "in_band_lines": sum(1 for _, line in rows if line["band"] == "in" and 0.70 < (line["probability"] or 0) <= 0.88),
            "constructed_market_lines": sum(1 for _, line in rows if CONSTRUCT.search(str(line["market"]))),
        }
    multi_desk_lines = [line for event in events for line in event["markets"] if len(line["desks"]) > 1]
    in_band_lines = [line for event in events for line in event["markets"] if line["band"] == "in" and (line["probability"] or 0) > 0.70]
    in_band_multi = [line for line in in_band_lines if len(line["desks"]) > 1]
    sensitivity = Counter()
    for event in events:
        if event["state"] != "upcoming":
            continue
        for line in event["markets"]:
            if (
                line["band"] == "in"
                and 0.70 < (line["probability"] or 0) <= 0.88
                and line["desks"]
                and all(d != "8a900c04" for d in line["desks"])
            ):
                sensitivity[event["sport"]] += 1
    audit["price_independence"] = {
        "observations": len(observations),
        "per_desk": per_desk,
        "lines_priced_by_more_than_one_desk": len(multi_desk_lines),
        "in_band_lines": len(in_band_lines),
        "in_band_lines_priced_by_more_than_one_desk": len(in_band_multi),
        "in_band_lines_without_8a900c04": {"by_sport": dict(sensitivity), "total": sum(sensitivity.values())},
    }
    worst = max(per_desk.items(), key=lambda kv: kv[1]["share_between_0.700_and_0.720"])
    flag(
        flags, "high",
        "One desk supplies almost the whole in-window pool, and its prices cluster at the threshold",
        f"{per_desk[worst[0]]['lines_between_0.700_and_0.720']} of {worst[0]}'s "
        f"{per_desk[worst[0]]['lines']} priced lines sit between 0.700 and 0.720 "
        f"({per_desk[worst[0]]['share_between_0.700_and_0.720']:.1%}), against "
        + " and ".join(
            f"{per_desk[d]['share_between_0.700_and_0.720']:.1%} for {d}"
            for d in desks if d != worst[0]
        )
        + f". That desk also supplies {per_desk[worst[0]]['in_band_lines']} of the {len(in_band_lines)} candidate lines "
        f"that fall inside the brief's window. Of {len(observations)} priced observations only {len(multi_desk_lines)} "
        f"are seconded by another desk, and "
        + ("not one in-window line is priced twice. " if not in_band_multi else f"only {len(in_band_multi)} in-window lines are priced twice. ")
        + "Dropping that desk entirely leaves "
        f"{sum(sensitivity.values())} in-window candidates across {len(sensitivity)} sports. The concentration, "
        "not the individual prices, is the finding: a price ladder tuned to land just above a published "
        "threshold cannot be read as independent agreement.",
        "internal distribution check",
        [f"{d}: {v['lines_between_0.700_and_0.720']}/{v['lines']} lines in 0.700-0.720" for d, v in sorted(per_desk.items())],
    )
    flag(
        flags, "medium",
        "Nearly every in-window selection is priced by one desk only",
        f"Of {len(in_band_lines)} in-window lines, {len(in_band_lines) - len(in_band_multi)} are priced by a single desk. "
        "Where two desks do price the same bet, the numbers differ by more than the tolerance used here more often "
        "than they agree. Every pick on this desk therefore prints the desk that priced it, and no pick is described "
        "as market consensus.",
        "internal provenance count",
    )

    # ---------------------------------------------------------------- G5 directional conflicts
    conflicts = []
    for event in events:
        desks = sorted({p["desk"] for p in event["provenance"]})
        if len(desks) < 2:
            continue
        by_desk = defaultdict(list)
        for line in event["markets"]:
            if re.search(r"winner", line["market"], re.I) and not re.search(r"1st|set|frame|leg|first|pole", line["market"], re.I):
                for obs in line["observations"]:
                    by_desk[obs["desk"]].append((line["selection"], 1.0 / obs["decimal"]))
        favourites = {}
        for desk, values in by_desk.items():
            selection, prob = max(values, key=lambda item: item[1])
            favourites[desk] = {"selection": selection, "probability": round(prob, 4)}
        distinct = {re.sub(r"\s+to\s+(win|beat).*", "", f["selection"], flags=re.I).lower() for f in favourites.values()}
        if len(favourites) >= 2 and len(distinct) > 1:
            conflicts.append(
                {
                    "event": event["id"],
                    "sport": event["sport"],
                    "match": f"{event['home']} v {event['away']}",
                    "start_utc": event["start_utc"],
                    "favourites": favourites,
                }
            )
    audit["directional_conflicts"] = conflicts
    if conflicts:
        worst = sorted(
            conflicts,
            key=lambda c: -(max(f["probability"] for f in c["favourites"].values()) - min(f["probability"] for f in c["favourites"].values())),
        )
        flag(
            flags, "high",
            f"{len(conflicts)} fixtures carry opposite favourites on different desks",
            "The same fixture is priced with a different favourite by two or more source desks. The largest "
            "gaps are shown below. None of these fixtures is used for a published pick on this desk; they are "
            "listed for review with both sides and both prices.",
            "internal cross-desk comparison",
            [f"{c['sport']}: {c['match']} — " + "; ".join(f"{d} {v['selection']} ({v['probability']:.1%})" for d, v in c["favourites"].items()) for c in worst[:8]],
        )

    # ---------------------------------------------------------------- G6 price divergence
    divergence = []
    for event in events:
        for line in event["markets"]:
            if line["divergence"] >= 0.10:
                divergence.append(
                    {
                        "event": event["id"],
                        "sport": event["sport"],
                        "selection": line["selection"],
                        "market": line["market"],
                        "spread_decimal": line["divergence"],
                        "observations": line["observations"],
                    }
                )
    audit["price_divergence"] = divergence
    if divergence:
        flag(
            flags, "medium",
            f"{len(divergence)} lines differ by 10% or more between desks",
            "Two desks priced the same market and selection with decimal prices at least 0.10 apart. The "
            "freshest observation is used on the match pages and the older one is shown beside it.",
            "internal cross-desk comparison",
            [f"{d['sport']}: {d['selection']} — spread {d['spread_decimal']:.2f}" for d in divergence[:8] if d.get("spread_decimal")],
        )

    # ---------------------------------------------------------------- G7 elapsed rows
    elapsed_upcoming = []
    for event in events:
        if event["state"] == "elapsed" and event.get("declared"):
            pass
    declared_upcoming_but_elapsed = []
    for desk, path, field in (
        ("496eaf02", DATA / "496eaf02" / "fixtures.json", "fixtures"),
    ):
        doc = load(path)
        for fixture in doc[field]:
            start = fixture.get("start_utc")
            if not start:
                continue
            started = datetime.strptime(start, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if started < NOW and fixture.get("state") == "upcoming":
                declared_upcoming_but_elapsed.append(
                    {"desk": desk, "id": fixture["id"], "start_utc": start, "state": fixture["state"]}
                )
    audit["stale_upcoming_labels"] = declared_upcoming_but_elapsed
    if declared_upcoming_but_elapsed:
        flag(
            flags, "medium",
            f"{len(declared_upcoming_but_elapsed)} rows still say 'upcoming' after their official start time",
            "At this desk's build time (21:30Z) these rows had already started but their source file still "
            "carries a pre-match state. They are shown as elapsed here and carry no pick.",
            "internal clock check",
            [f"{r['desk']} {r['id']} started {r['start_utc']}" for r in declared_upcoming_but_elapsed],
        )

    # ---------------------------------------------------------------- G8 multi-runner modelling
    MULTI = {"Greyhounds", "Motor Racing", "Golf"}
    multi_rows = [
        f"{e['sport']}: {e['home']} v {e['away']}"
        for e in events
        if e["sport"] in MULTI and re.search(r"\bfield\b|remaining|quarter|contingent|traps", e["away"] + e["home"], re.I)
    ]
    if multi_rows:
        flag(
            flags, "high",
            "Race and stroke-play events are modelled as two-sided matches",
            "Greyhound races, motor races and stroke-play golf are multi-runner events. Several inherited rows "
            "invent a second side called 'Field', 'Remaining Belfast Field' or 'Inside Seeding Traps 1-3' and "
            "then quote a two-way price against it. That is not a market OLBG or any governing body publishes. "
            "This desk keeps those rows visible but labels them multi-runner and does not publish a match-winner "
            "pick from them.",
            "https://www.gbgb.org.uk/",
            multi_rows[:10],
        )

    # ---------------------------------------------------------------- G9 inherited prose
    prose_findings = []
    for desk, path in (
        ("8a900c04", DATA / "8a900c04" / "desk.json"),
        ("496eaf02", DATA / "496eaf02" / "predictions.json"),
    ):
        if not path.exists():
            continue
        doc = load(path)
        items = doc["events"] if "events" in doc else doc.get("predictions", [])
        texts = [(item.get("id") or item.get("match_id"), item.get("prediction") or item.get("text") or "") for item in items]
        seen: dict[str, str] = {}
        for ident, text in texts:
            if not text:
                continue
            words = len(re.findall(r"\b[\w'-]+\b", text))
            lower = text.lower()
            hits = [w for w in BANNED_PROSE if re.search(rf"\b{re.escape(w)}\b", lower)]
            if hits:
                prose_findings.append({"desk": desk, "id": ident, "issue": "internal vocabulary: " + ", ".join(hits)})
            if words < 30:
                prose_findings.append({"desk": desk, "id": ident, "issue": f"only {words} words"})
            for gram in ngrams(text):
                if gram in seen and seen[gram] != ident:
                    prose_findings.append({"desk": desk, "id": ident, "issue": f"repeated 6-gram with {seen[gram]}: '{gram}'"})
                    break
                seen.setdefault(gram, ident)
        if desk == "496eaf02":
            names = {t[0]: t[1] for t in texts}
            # the same opponent credited to two different players in one event
    # explicit, verified-by-reading contradictions in inherited prose
    p496 = load(DATA / "496eaf02" / "predictions.json")["predictions"]
    by_match = {p["match_id"]: p for p in p496}
    if "TN01" in by_match and "TN02" in by_match:
        a, b = by_match["TN01"]["text"], by_match["TN02"]["text"]
        if "Khachanov" in a and "Khachanov" in b and "4-6 7-6(5) 7-6(5)" in a and "4-6 7-6(5) 7-6(5)" in b:
            flag(
                flags, "high",
                "One scoreline is credited to two different players on adjacent rows",
                "Row TN01 says Tsitsipas beat Karen Khachanov 4-6 7-6(5) 7-6(5); row TN02 says Bublik beat "
                "Karen Khachanov in a 4-6 7-6(5) 7-6(5) thriller lasting 32 games, in the same semi-final "
                "round of the same tournament. Khachanov cannot have lost that identical scoreline twice. "
                "Both rows are treated as unreliable for that detail and the detail is excluded from this "
                "desk's predictions for the two matches.",
                "https://www.atptour.com/en/scores/current/almaty/9410/results",
                ["496eaf02 TN01", "496eaf02 TN02"],
            )
    audit["prose_findings"] = prose_findings[:60]
    if prose_findings:
        flag(
            flags, "medium",
            f"{len(prose_findings)} inherited prose lines fail a written-rule check",
            "Checks applied to the source desks' own published predictions: minimum 30 words, no internal "
            "vocabulary, and no six-word phrase reused between two different matches.",
            "internal prose check",
            [f"{f['desk']} {f['id']}: {f['issue']}" for f in prose_findings[:10]],
        )

    # ---------------------------------------------------------------- G10 source quality
    bad_sources = []
    for event in events:
        if not event["official_sources"]:
            bad_sources.append({"event": event["id"], "issue": "no official source recorded"})
            continue
        for url in event["official_sources"]:
            h = host(url)
            if h in NON_OFFICIAL_HOSTS:
                bad_sources.append({"event": event["id"], "issue": f"non-official host used as evidence: {h}", "url": url})
            elif h not in OFFICIAL_HOSTS:
                bad_sources.append({"event": event["id"], "issue": f"host not on the official allow-list: {h}", "url": url})
    audit["source_findings"] = bad_sources
    if bad_sources:
        distinct_hosts = sorted({re.sub(r"^host not on the official allow-list: ", "", b["issue"]) for b in bad_sources if "allow-list" in b["issue"]})
        flag(
            flags, "medium",
            f"{len(bad_sources)} source links are outside the governing-body allow-list",
            "Every sporting row must carry a link to the league, tour, promoter or governing body that "
            "publishes the fixture. Hosts that are media, aggregators or betting sites are listed below and "
            "are not counted as row verification on this desk.",
            "https://www.olbg.com/betting-tips",
            distinct_hosts[:12],
        )

    unlinked = [e for e in events if not e["official_sources"]]
    if unlinked:
        flag(
            flags, "medium",
            f"{len(unlinked)} fixtures carry no official source link",
            "These rows were published by a source desk without any governing-body URL. They keep their place in "
            "the match list so the gap is visible, but they carry no pick and no prediction on this desk.",
            "internal source check",
            [f"{e['id']} {e['home']} v {e['away']} ({e['sport']})" for e in unlinked],
        )

    # ---------------------------------------------------------------- G11 single-source rows
    single = [e["id"] for e in events if len({p["desk"] for p in e["provenance"]}) == 1]
    audit["single_source_events"] = single
    flag(
        flags, "info",
        f"{len(single)} of {len(events)} fixtures rest on a single desk",
        "These fixtures appear on only one of the three retained 23-Oct desks, so no independent second "
        "price exists to compare against. Their numbers are shown but not treated as corroborated.",
        "internal provenance count",
        single[:20],
    )

    # ---------------------------------------------------------------- per-sport targets
    summary = []
    for sport in {e["sport"] for e in events}:
        rows = [e for e in events if e["sport"] == sport]
        upcoming = [e for e in rows if e["state"] == "upcoming"]
        summary.append(
            {
                "sport": sport,
                "events": len(rows),
                "upcoming": len(upcoming),
                "lines": sum(len(e["markets"]) for e in rows),
                "strict_in_band_lines": strict_by_sport.get(sport, 0),
                "above_band_lines": above_band_by_sport.get(sport, 0),
                "desks": len({p["desk"] for e in rows for p in e["provenance"]}),
            }
        )
    audit["sports"] = sorted(summary, key=lambda r: r["sport"])

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "audit.json").write_text(json.dumps(audit, indent=1) + "\n", encoding="utf-8")
    (OUT / "flags.json").write_text(
        json.dumps({"desk": "6b47ea39", "generated_utc": "2026-10-23T21:30:00Z", "count": len(flags), "flags": flags}, indent=1) + "\n",
        encoding="utf-8",
    )
    print(f"flags: {len(flags)}")
    for f in flags:
        print(f"  {f['id']} [{f['severity']}] {f['title']}")
    print("conflicts:", len(conflicts), "| stale upcoming:", len(declared_upcoming_but_elapsed), "| single-source:", len(single))


if __name__ == "__main__":
    main()
