#!/usr/bin/env python3
"""Session e6716490-olbg1 — assemble the consolidated desk dataset.

Reads two already-verified, source-linked fixture registers from the repository
(read-only) and normalises them into one desk:

  * ``data/984d417f/fixtures.json``  — 17-sport register with 0-100 strength
    inputs, per-row official source lists, ``unverified_fields`` and ``flags``.
  * ``data/f71557b5/fixtures.json``  — newer 14-sport register with sport-specific
    numeric inputs (points %, run rates, seeds, published percentages).

Nothing is fetched from the network here.  Every value that reaches this dataset
originates in one of those two registers, each of which carries the official
governing-body URL it was read from.  The dataset records, per row, which desk it
came from and whether this session re-read the source (see
``data/e6716490/verification.json``, written by hand from live fetches).

Output: ``data/e6716490/fixtures.json``
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "e6716490"

TODAY = "2026-10-22"

# OLBG sport taxonomy: slug -> (display name, OLBG sport id)
SPORTS = {
    "tennis": ("Tennis", 3),
    "basketball": ("Basketball", 4),
    "golf": ("Golf", 5),
    "cricket": ("Cricket", 7),
    "snooker": ("Snooker", 8),
    "rugby-union": ("Rugby Union", 9),
    "rugby-league": ("Rugby League", 10),
    "baseball": ("Baseball", 12),
    "ice-hockey": ("Ice Hockey", 13),
    "motor-racing": ("Motor Racing", 14),
    "darts": ("Darts", 15),
    "handball": ("Handball", 20),
    "volleyball": ("Volleyball", 21),
    "aussie-rules": ("Aussie Rules", 22),
    "esports": ("eSports", 23),
    "gaelic-football": ("Gaelic Football", 25),
    "greyhounds": ("Greyhounds", 28),
}

# Sports the brief excludes. Listed so the reverse-engineering page can prove the
# exclusion was applied rather than silently dropped.
EXCLUDED = [
    ("Football / Soccer", 1),
    ("Horse Racing", 2),
    ("American Football", 11),
    ("Boxing", 16),
    ("Cycling", 17),
    ("Hurling", 26),
    ("Specials / Entertainment", 18),
    ("UFC / MMA", None),
]


def norm_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (value or "").lower())


import unicodedata

STOP_TOKENS = {
    "fc", "hc", "sc", "bc", "kk", "cf", "ac", "afc", "cd", "sd", "ud", "bc", "basketball",
    "handball", "hb", "håndball", "rugby", "club", "de", "the", "team", "sporting",
    "istanbul", "athens", "vitoria", "gasteiz", "tel", "aviv", "munich", "madrid",
    "kaunas", "villeurbanne", "london", "paris",
}
GRADE_TOKENS = {"a", "b", "ii", "women", "womens", "w", "u19", "u20", "u21", "reserves", "xi"}


def fold(value: str) -> str:
    value = unicodedata.normalize("NFKD", value or "")
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9 ]", " ", value.lower())


def tokens(value: str) -> frozenset:
    words = [w for w in fold(value).split() if w and w not in STOP_TOKENS and len(w) > 1]
    return frozenset(words)


def names_match(a: str, b: str) -> bool:
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return norm_name(a) == norm_name(b)
    if ta == tb:
        return True
    # Grade / gender markers must match exactly, or "New Zealand A" would merge
    # into "New Zealand" and "Australia Women" into "Australia".
    fold_a = set(fold(a).split())
    fold_b = set(fold(b).split())
    if (fold_a & GRADE_TOKENS) != (fold_b & GRADE_TOKENS):
        return False
    if ta <= tb or tb <= ta:
        return True
    shared = ta & tb
    return len(shared) >= 2 and len(shared) / len(ta | tb) >= 0.5


def dedupe_key(row: dict) -> tuple:
    return (
        row["sport"],
        norm_name(row["home"]),
        norm_name(row["away"]),
        (row.get("start_utc") or row.get("date_local") or "")[:13],
    )


def load(path: Path) -> list[dict]:
    with path.open() as fh:
        blob = json.load(fh)
    return blob.get("fixtures") or blob.get("items") or []


def from_984(row: dict, index: int) -> dict:
    inputs = row.get("inputs") or {}
    rating_h = (inputs.get("home") or {}).get("rating")
    rating_a = (inputs.get("away") or {}).get("rating")
    return {
        "id": row["id"],
        "sport": row["sport"],
        "competition": row.get("competition") or "",
        "stage": row.get("stage") or "",
        "kind": row.get("kind") or "h2h",
        "home": row.get("home") or "",
        "away": row.get("away") or "",
        "venue": row.get("venue") or "",
        "neutral": bool(row.get("neutral")),
        "start_utc": row.get("start_utc") or "",
        "date_local": (row.get("date_local") or "")[:10],
        "status": row.get("status") or "verified",
        "inputs": {
            "home": {
                "label": (inputs.get("home") or {}).get("label") or "",
                "value": (inputs.get("home") or {}).get("value") or "",
                "rating": rating_h,
            },
            "away": {
                "label": (inputs.get("away") or {}).get("label") or "",
                "value": (inputs.get("away") or {}).get("value") or "",
                "rating": rating_a,
            },
        },
        "sources": [
            {"name": s.get("name") or "Official source", "url": s.get("url") or ""}
            for s in (row.get("sources") or [])
        ],
        "unverified_fields": list(row.get("unverified_fields") or []),
        "flags": list(row.get("flags") or []),
        "provenance": {
            "desk": "984d417f-olbg1",
            "file": "data/984d417f/fixtures.json",
            "row": index,
            "register_read": "2026-10-22",
        },
        "notes": [],
    }


# ---------------------------------------------------------------------------
# f71557b5 rows carry sport-specific numeric inputs.  Convert each one to the
# desk's common 0-100 strength scale using a documented, deterministic rule so a
# single win-probability engine can price every sport.  The rule is printed on
# the methodology page.
# ---------------------------------------------------------------------------
def strength_from_f7(row: dict) -> tuple[float | None, float | None, str]:
    m = row.get("model") or {}
    kind = m.get("kind")
    try:
        if kind == "nhl":
            h = round(100 * float(m["home_ppg"]) / 2.0, 2)
            a = round(100 * float(m["away_ppg"]) / 2.0, 2)
            return h, a, "points per game / 2.0 x 100"
        if kind == "mlb":
            h = round(69.5, 2)
            a = round(53.5, 2)
            return None, None, "run-rate inputs kept separate; ratings deferred to run model"
        if kind == "euroleague":
            h = round(50 + 25 * (float(m["home_w"]) - float(m["home_l"])) / max(1.0, float(m["home_w"]) + float(m["home_l"])), 2)
            a = round(50 + 25 * (float(m["away_w"]) - float(m["away_l"])) / max(1.0, float(m["away_w"]) + float(m["away_l"])), 2)
            return h, a, "50 + 25 x win-loss differential share"
        if kind == "lnr_published":
            return None, None, "published 1X2 percentages used directly"
        if kind == "darts":
            sh, sa = m.get("seed_home"), m.get("seed_away")
            if sh and sa:
                # European Tour seeds run 1..32; linear strength on the seed ladder.
                return round(100 * (33 - sh) / 32, 2), round(100 * (33 - sa) / 32, 2), "(33 - seed) / 32 x 100"
            return None, None, ""
        if kind == "snooker":
            h = 72.0 if m.get("home_top16") else 52.0
            a = 72.0 if m.get("away_top16") else 52.0
            return h, a, "72 for a verified world top-16 player, 52 otherwise"
    except (KeyError, TypeError, ValueError):
        return None, None, ""
    return None, None, ""


def from_f7(row: dict, index: int) -> dict:
    h, a, rule = strength_from_f7(row)
    m = row.get("model") or {}
    evidence_home = ""
    evidence_away = ""
    for ev in row.get("evidence") or []:
        label = (ev.get("label") or "").lower()
        if "home" in label and not evidence_home:
            evidence_home = ev.get("value") or ""
        elif "away" in label and not evidence_away:
            evidence_away = ev.get("value") or ""
    return {
        "id": row["id"],
        "sport": row["sport"],
        "competition": row.get("competition") or "",
        "stage": (row.get("round") or "").strip(),
        "kind": "field" if row.get("event_only") else "h2h",
        "home": row.get("home") or "",
        "away": row.get("away") or "",
        "venue": row.get("venue") or "",
        "neutral": False,
        "start_utc": row.get("start_utc") or "",
        "date_local": (row.get("start_utc") or "")[:10],
        "status": row.get("status") or "verified",
        "inputs": {
            "home": {
                "label": m.get("kind") or "verified input",
                "value": evidence_home or (m.get("note") or ""),
                "rating": h,
            },
            "away": {
                "label": m.get("kind") or "verified input",
                "value": evidence_away or (m.get("note") or ""),
                "rating": a,
            },
        },
        "sources": [
            {"name": s.get("name") or "Official source", "url": s.get("url") or ""}
            for s in (row.get("sources") or [])
        ],
        "unverified_fields": [],
        "flags": [f.get("text") if isinstance(f, dict) else str(f) for f in (row.get("flags") or [])],
        "provenance": {
            "desk": "f71557b5-olbg1",
            "file": "data/f71557b5/fixtures.json",
            "row": index,
            "register_read": "2026-10-22",
        },
        "notes": [],
        "model_raw": m,
        "strength_rule": rule,
    }


def cross_desk_conflicts(rows: list[dict]) -> list[dict]:
    """Compare rows that describe the same fixture from both registers."""
    by_key: dict[tuple, list[dict]] = {}
    for r in rows:
        by_key.setdefault(dedupe_key(r), []).append(r)
    conflicts = []
    for key, group in by_key.items():
        desks = {g["provenance"]["desk"] for g in group}
        if len(group) < 2 or len(desks) < 2:
            continue
        values = {}
        for g in group:
            d = g["provenance"]["desk"]
            values[d] = (g["inputs"]["home"]["value"], g["inputs"]["away"]["value"])
        distinct = set(values.values())
        if len(distinct) > 1:
            conflicts.append(
                {
                    "fixture": f"{group[0]['home']} v {group[0]['away']}",
                    "sport": group[0]["sport"],
                    "values": {d: v for d, v in values.items()},
                    "sources": {
                        g["provenance"]["desk"]: [s["url"] for s in g["sources"][:2]] for g in group
                    },
                }
            )
    return conflicts


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)

    rows: list[dict] = []
    for i, row in enumerate(load(ROOT / "data" / "984d417f" / "fixtures.json")):
        if (row.get("date_local") or "")[:10] < TODAY:
            continue  # expired before the desk read date
        rows.append(from_984(row, i))
    for i, row in enumerate(load(ROOT / "data" / "f71557b5" / "fixtures.json")):
        r = from_f7(row, i)
        if r["date_local"] and r["date_local"] < TODAY:
            continue
        rows.append(r)

    # ---- merge duplicates across the two registers -------------------------
    # A dateless register row (darts/snooker/golf cards publish no clock) is the
    # same fixture as the dated row for the same pairing, so it merges into it.
    # Field/outright cards are matched on venue (or competition when no venue is
    # published).  Nothing is discarded: sources, flags and the losing row's input
    # values are all carried on the surviving row.
    def same_fixture(a: dict, b: dict) -> bool:
        if a["sport"] != b["sport"]:
            return False
        if (a["kind"] == "field") != (b["kind"] == "field"):
            return False
        if a["kind"] == "field":
            va = norm_name(a["venue"]) or norm_name(a["competition"])
            vb = norm_name(b["venue"]) or norm_name(b["competition"])
            return bool(va) and (va == vb or norm_name(a["competition"]) == norm_name(b["competition"]))
        if not (names_match(a["home"], b["home"]) and names_match(a["away"], b["away"])):
            return False
        da, db = a["date_local"], b["date_local"]
        return not da or not db or da == db

    groups: list[list[dict]] = []
    for r in rows:
        for g in groups:
            if any(same_fixture(r, member) for member in g):
                g.append(r)
                break
        else:
            groups.append([r])

    merged: list[dict] = []
    for group in groups:
        if group[0]["kind"] == "field":
            base = max(group, key=lambda r: (len(r["sources"]), bool(r["date_local"]),
                                             r["provenance"]["desk"] == "f71557b5-olbg1"))
            others = [g for g in group if g is not base]
        else:
            dated = sorted([g for g in group if g["date_local"]], key=lambda g: g["date_local"])
            if not dated:
                base = group[0]
                others = group[1:]
            else:
                base = dated[0]
                others = [g for g in group if g is not base]
                if len(dated) > 1:
                    base["notes"].append(
                        "Register lists more than one meeting of this pairing "
                        f"({', '.join(g['date_local'] for g in dated)}); this row is the earliest."
                    )
        urls = {s["url"] for s in base["sources"]}
        for o in others:
            for src in o["sources"]:
                if src["url"] and src["url"] not in urls:
                    base["sources"].append(src)
                    urls.add(src["url"])
            for f in o["flags"]:
                if f not in base["flags"]:
                    base["flags"].append(f)
            for u in o["unverified_fields"]:
                if u not in base["unverified_fields"]:
                    base["unverified_fields"].append(u)
            base.setdefault("superseded", []).append(
                {
                    "desk": o["provenance"]["desk"],
                    "date_local": o["date_local"],
                    "home": o["inputs"]["home"]["value"],
                    "away": o["inputs"]["away"]["value"],
                    "urls": [s["url"] for s in o["sources"]],
                }
            )
            if not base["date_local"] and o["date_local"]:
                base["date_local"] = o["date_local"]
        if base.get("superseded"):
            base["flags"].append(
                "Two repository registers describe this fixture in different words; both readings "
                "and both source lists are shown on the row and the disagreement is logged as a "
                "cross-desk irregularity."
            )
        merged.append(base)
    fixtures = merged
    conflicts = cross_desk_conflicts(rows)

    fixtures = sorted(
        fixtures,
        key=lambda r: (r["start_utc"] or "9999", SPORTS.get(r["sport"], ("", 0))[1], r["home"]),
    )

    # Every row must point at at least one official page; a row that cannot is
    # flagged rather than published with a guess.
    for r in fixtures:
        r["sources"] = [s for s in r["sources"] if s["url"]]
        if not r["sources"]:
            r["flags"].append("No official source URL survived normalisation — row is not priced.")
            r["status"] = "flagged"

    by_sport: dict[str, int] = {}
    for r in fixtures:
        by_sport[r["sport"]] = by_sport.get(r["sport"], 0) + 1

    blob = {
        "session": "e6716490-olbg1",
        "generated_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "read_date": TODAY,
        "rules": [
            "official governing-body, league, tour or organiser pages only",
            "blank beats wrong: unconfirmed fields stay empty and are flagged",
            "model output is labelled as an originated estimate, never as a sourced fact",
            "one-sided inputs never carry a strength edge",
        ],
        "sports": {slug: {"name": name, "olbg_id": oid} for slug, (name, oid) in SPORTS.items()},
        "excluded": [{"name": n, "olbg_id": i} for n, i in EXCLUDED],
        "count": len(fixtures),
        "by_sport": by_sport,
        "cross_desk_conflicts": conflicts,
        "fixtures": fixtures,
    }
    with (OUT / "fixtures.json").open("w") as fh:
        json.dump(blob, fh, indent=1, ensure_ascii=False)
    print(f"wrote {OUT/'fixtures.json'}: {len(fixtures)} fixtures, {len(by_sport)} sports, "
          f"{len(conflicts)} cross-desk conflicts")
    for s in sorted(by_sport, key=lambda x: SPORTS[x][1]):
        print(f"  {SPORTS[s][0]:16} {by_sport[s]:3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
