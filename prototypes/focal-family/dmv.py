"""
DMV pre-check logic: state rules, test design, scoring and the honest retake.

Copied from Prototype C (prototype-c-alex-dmv-precheck/app.py), where it is tested and
was demoed in class, so the master app deploys on its own. State rules were checked
against official sources in October 2026; see Prototype C's README for the full table.
"""

import math
import random

CARD_WIDTH_MM = 85.6
# 85.6 mm at the CSS reference resolution of 96 px per inch.
DEFAULT_CARD_PX = 323

DIRECTIONS = ["left", "up", "down", "right"]
CANT_TELL = "cant_tell"

# Snellen lines from large to small (the "x" in 20/x)
SNELLEN_LADDER = [100, 70, 50, 40, 30, 25, 20]

# Scoring at the state line (6 letters). With 4 possible directions, a pure
# guesser reaches 5/6 less than 1% of the time and 4/6 about 4% of the time.
STATE_LINE_LETTERS = 6
ON_TRACK_MIN = 5
CLOSE_MIN = 4

# Summaries of official rules, checked October 2026. Most states draw the
# "pass at the counter with no extra steps" line at 20/40; Georgia (20/60) and
# New Jersey (20/50) do not, which is why the check is built around each state's line.
RULES_CHECKED = "October 2026"
STATES = {
    "North Carolina": {
        "abbr": "NC",
        "possessive": "North Carolina's",
        "line": 40,
        "rule": "20/40 or better in either eye or both eyes together for a license without restrictions.",
        "glasses": "Glasses or contacts are allowed. If you need them to reach 20/40, your license will require them.",
        "if_missed": "Below 20/40, North Carolina restricts the license to corrective lenses, so you would need glasses or contacts before you can pass.",
        "bring": "Get glasses or contacts if the eye doctor prescribes them, and wear them for the DMV screening.",
        "source_name": "NC DMV rule 19A NCAC 03B .0201",
        "source_url": "https://www.ncdot.gov/about-us/how-we-operate/policy-process/rules/Documents/19a-ncac-03b-0201-emergency-rule.pdf",
    },
    "California": {
        "abbr": "CA",
        "possessive": "California's",
        "line": 40,
        "rule": "20/40 with both eyes together, and 20/40 in one eye with at least 20/70 in the other.",
        "glasses": "Glasses or contacts are allowed.",
        "if_missed": "If you don't meet the standard, the DMV refers you to an eye doctor, who fills out a Report of Vision Examination (form DL 62).",
        "bring": "Ask the eye doctor to complete form DL 62 (Report of Vision Examination) and bring it to the DMV.",
        "source_name": "California DMV vision standards",
        "source_url": "https://www.dmv.ca.gov/portal/?p=1733",
    },
    "Florida": {
        "abbr": "FL",
        "possessive": "Florida's",
        "line": 40,
        "rule": "The legal minimum is 20/70, but at 20/50 or worse in either eye an eye specialist must complete Form 72010, so 20/40 is the line to pass with no extra paperwork.",
        "glasses": "Glasses or contacts are allowed. If you need them, your license will require them.",
        "if_missed": "At 20/50 or worse in either eye, an eye specialist must complete FLHSMV Form 72010 before you are licensed.",
        "bring": "Ask the eye specialist to complete FLHSMV Form 72010 and bring it with you.",
        "source_name": "FLHSMV vision standards",
        "source_url": "https://flhsmv.gov/ddl/vision.html",
    },
    "Georgia": {
        "abbr": "GA",
        "possessive": "Georgia's",
        "line": 60,
        "rule": "20/60 in at least one eye, plus a field of vision of at least 140 degrees.",
        "glasses": "Glasses or contacts are allowed.",
        "if_missed": "If you don't meet the standard at the counter, plan on an eye doctor visit before you are licensed.",
        "bring": "Ask the eye doctor whether you need Georgia's Vision Report Form (DDS-MR-274), and bring it with you.",
        "source_name": "Georgia DDS medical and vision information",
        "source_url": "https://dds.georgia.gov/node/1846",
    },
    "New Jersey": {
        "abbr": "NJ",
        "possessive": "New Jersey's",
        "line": 50,
        "rule": "20/50 visual acuity, with or without glasses or contacts.",
        "glasses": "If you need glasses or contacts to pass, your license will require them while driving.",
        "if_missed": "If you fail the MVC vision test, you visit your doctor and complete Form ST-14.",
        "bring": "Bring the completed Form ST-14 back to the MVC.",
        "source_name": "NJ MVC vision test",
        "source_url": "https://www.nj.gov/mvc/license/visiontest.htm",
    },
    "New York": {
        "abbr": "NY",
        "possessive": "New York's",
        "line": 40,
        "rule": "At least 20/40 in either eye or both eyes.",
        "glasses": "Glasses or contacts are allowed.",
        "if_missed": "If your best vision with glasses is below 20/40 but not below 20/70, an eye doctor completes form MV-80L for DMV review.",
        "bring": "Ask the eye doctor to complete form MV-619 (or MV-80L if your vision is below 20/40 with glasses), or to submit your result through the DMV Online Vision Registry.",
        "source_name": "NY DMV vision requirements and restrictions",
        "source_url": "https://dmv.ny.gov/driver-license/vision-requirements-and-restrictions",
    },
    "Texas": {
        "abbr": "TX",
        "possessive": "Texas's",
        "line": 40,
        "rule": "20/40 or better in each eye and both eyes together for a license with no vision restrictions.",
        "glasses": "If you need glasses or contacts to reach the standard, your license will require them.",
        "if_missed": "Lower scores can lead to a referral to an eye specialist, or limits such as daytime-only driving.",
        "bring": "Bring your glasses or contacts, and any statement your eye specialist gives you, to the DPS office.",
        "source_name": "37 Tex. Admin. Code § 15.51 (Vision Tests)",
        "source_url": "https://www.law.cornell.edu/regulations/texas/37-Tex-Admin-Code-SS-15-51",
    },
    "Another state": {
        "abbr": "your state",
        "possessive": "your state's",
        "line": 40,
        "rule": "Most U.S. states use 20/40 as the line for a license without restrictions. Rules differ, so check your state DMV's website for the exact standard.",
        "glasses": "Every state allows glasses or contacts. Your license will note it if you need them.",
        "if_missed": "Most states ask for a vision report from an eye doctor if you miss the standard at the counter.",
        "bring": "Ask the eye doctor whether your DMV has a vision report form, and bring it with you.",
        "source_name": None,
        "source_url": None,
    },
}

GLASSES_OPTIONS = [
    "No, I don't wear glasses or contacts",
    "Yes, and I'm wearing them for this check",
]



# -----------------------------------------------------------------------------
# Test logic (pure functions, covered by test_app.py)
# -----------------------------------------------------------------------------
def build_test_lines(state_line: int = 40):
    """Two warm-up lines above the state line, the state line, and one line below it.
    A state line that isn't on the standard ladder (Georgia's 20/60) is slotted into it."""
    ladder = sorted(set(SNELLEN_LADDER) | {state_line}, reverse=True)
    idx = ladder.index(state_line)
    lines = []
    for denom in ladder[max(0, idx - 2):idx]:
        lines.append({"denominator": denom, "letters": 2 if denom > 50 else 3, "role": "warm-up"})
    lines.append({"denominator": state_line, "letters": STATE_LINE_LETTERS, "role": "state line"})
    if idx + 1 < len(ladder):
        lines.append({"denominator": ladder[idx + 1], "letters": 3, "role": "margin"})
    return lines


def random_directions(count: int, rng: random.Random, cover_all: bool = False):
    """Random directions with no direction twice in a row. With cover_all, every direction appears."""
    for _ in range(200):
        dirs = [rng.choice(DIRECTIONS) for _ in range(count)]
        if any(a == b for a, b in zip(dirs, dirs[1:])):
            continue
        if cover_all and count >= len(DIRECTIONS) and set(dirs) != set(DIRECTIONS):
            continue
        return dirs
    # Fallback: a shuffled cycle always satisfies both rules
    base = DIRECTIONS[:]
    rng.shuffle(base)
    return [base[i % len(base)] for i in range(count)]


def generate_items(lines, rng=None):
    """One item per letter, in order from the largest line to the smallest."""
    rng = rng or random.Random()
    items = []
    for line_idx, line in enumerate(lines):
        dirs = random_directions(line["letters"], rng, cover_all=line["role"] == "state line")
        for d in dirs:
            items.append({
                "line_idx": line_idx,
                "denominator": line["denominator"],
                "role": line["role"],
                "direction": d,
            })
    return items


def letter_height_mm(denominator: int, distance_mm: float) -> float:
    """Height of a Snellen E for 20/denominator at a distance. A 20/20 E spans 5 arcminutes."""
    arcmin = 5.0 * denominator / 20.0
    return 2.0 * distance_mm * math.tan(math.radians(arcmin / 60.0) / 2.0)


def letter_height_px(denominator: int, distance_mm: float, card_px: float) -> float:
    """Converts the physical letter height to CSS pixels using the card calibration."""
    px_per_mm = card_px / CARD_WIDTH_MM
    return letter_height_mm(denominator, distance_mm) * px_per_mm


def score_attempt(items, answers):
    """
    Scores one attempt. `answers` maps item index -> answer ("up", ..., or CANT_TELL).
    Returns per-line results and the verdict at the state line.
    """
    lines = {}
    for idx, item in enumerate(items):
        line = lines.setdefault(item["line_idx"], {
            "denominator": item["denominator"],
            "role": item["role"],
            "shown": 0,
            "correct": 0,
            "total": 0,
        })
        line["total"] += 1
        if idx in answers:
            line["shown"] += 1
            if answers[idx] == item["direction"]:
                line["correct"] += 1

    line_list = [lines[k] for k in sorted(lines)]
    state = next(l for l in line_list if l["role"] == "state line")
    if state["correct"] >= ON_TRACK_MIN:
        verdict = "on_track"
    elif state["correct"] >= CLOSE_MIN:
        verdict = "close"
    else:
        verdict = "not_yet"

    margin = next((l for l in line_list if l["role"] == "margin"), None)
    margin_read = bool(margin and margin["shown"] and margin["correct"] >= 2)

    for line in line_list:
        if line["shown"] == 0:
            line["status"] = "skipped"
        elif line["role"] == "state line":
            line["status"] = "read" if verdict == "on_track" else ("close" if verdict == "close" else "missed")
        else:
            line["status"] = "read" if line["correct"] * 2 > line["shown"] else "missed"

    return {
        "lines": line_list,
        "state_correct": state["correct"],
        "state_total": state["total"],
        "state_denominator": state["denominator"],
        "verdict": verdict,
        "margin_read": margin_read,
    }


def should_show_item(items, answers, idx):
    """The line below the state line is only shown after a clear pass, to measure the margin."""
    if items[idx]["role"] != "margin":
        return True
    state_idx = [i for i, it in enumerate(items) if it["role"] == "state line"]
    correct = sum(1 for i in state_idx if answers.get(i) == items[i]["direction"])
    return correct >= ON_TRACK_MIN


def next_item_index(items, answers, current):
    """Index of the next item to show after `current`, or None if the check is done."""
    idx = current + 1
    while idx < len(items):
        if should_show_item(items, answers, idx):
            return idx
        idx += 1
    return None


def overall_result(attempts):
    """
    Combines up to two attempts. A retake never just keeps the best score:
    if one check clears the line and the other doesn't, the result says so.
    """
    verdicts = [a["verdict"] for a in attempts]
    if len(verdicts) == 1:
        return {"verdict": verdicts[0], "consistency": "single"}
    first, last = verdicts[-2], verdicts[-1]
    if first == last:
        return {"verdict": last, "consistency": "consistent"}
    if "on_track" in (first, last):
        return {"verdict": "mixed", "consistency": "mixed"}
    # Neither check cleared the line, so both point to the same next step.
    return {"verdict": last, "consistency": "same_next_step"}


def build_summary_text(state_name, attempts, overall, glasses, distance_label, when):
    """Plain-text summary the user can copy for a parent or an eye doctor."""
    state = STATES[state_name]
    verdict_words = {
        "on_track": "On track to pass",
        "close": "Right at the line (too close to call)",
        "not_yet": "Might not pass yet; see an eye doctor first",
        "mixed": "Two checks disagreed; see an eye doctor to be sure",
    }
    lines = [
        "Focal DMV Pre-Check (practice check, not an official or medical result)",
        f"Date: {when}",
        f"State: {state_name} (line used: 20/{state['line']})",
        f"Result: {verdict_words[overall['verdict']]}",
    ]
    for i, a in enumerate(attempts, start=1):
        lines.append(f"Check {i}: {a['state_correct']} of {a['state_total']} letters correct at the 20/{a['state_denominator']} line")
    lines.append(f"Setup: both eyes together, {distance_label.split(' (')[0]} from a calibrated screen, {'with' if glasses == GLASSES_OPTIONS[1] else 'without'} glasses or contacts")
    return "\n".join(lines)
