"""
Focal DMV Pre-Check - Prototype C
Course: Duke University MENG 570 (Product Management)
Target Persona: Anxious Applicant Alex (first-time license applicant, 18-23)
Hypothesis: People with a DMV vision screening coming up will prefer, and act on,
            a free check that answers "Will I pass my state's test?" with a clear
            next step, over a general vision score.

Technology: Streamlit only. No accounts, no database, no external services.
"""

import inspect
import json
import math
import random
from datetime import datetime

import streamlit as st

# Responsive widget width across Streamlit versions without deprecation warnings
def full_width(widget=st.button):
    """Returns a full-width argument compatible with old and new Streamlit versions."""
    if "width" in inspect.signature(widget).parameters:
        return {"width": "stretch"}
    return {"use_container_width": True}


# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------
NAVY = "#15245C"
BLUE = "#5A9AD8"
INK = "#14213D"
MUTED = "#55617A"

# An ID-1 card (credit card, student ID, learner's permit) is 85.6 mm wide.
CARD_WIDTH_MM = 85.6
# 85.6 mm at the CSS reference resolution of 96 px per inch.
DEFAULT_CARD_PX = 323

DISTANCES = {
    "10 feet (about 3 meters)": 3048,
    "5 feet (about 1.5 meters)": 1524,
}

DIRECTIONS = ["left", "up", "down", "right"]
ARROWS = {"left": "←", "up": "↑", "down": "↓", "right": "→"}
CANT_TELL = "cant_tell"

# Snellen lines from large to small (the "x" in 20/x)
SNELLEN_LADDER = [100, 70, 50, 40, 30, 25, 20]

# Scoring at the state line (6 letters). With 4 possible directions, a pure
# guesser reaches 5/6 less than 1% of the time and 4/6 about 4% of the time.
STATE_LINE_LETTERS = 6
ON_TRACK_MIN = 5
CLOSE_MIN = 4

# Summaries of official rules, checked October 2026. Every state below draws the
# "pass at the counter with no extra steps" line at 20/40.
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

SETUP_CHECKLIST = {
    "chk_light": "The room is well lit and there's no glare on the screen.",
    "chk_distance": "I can be at the distance I picked (or a friend will tap the arrows for me).",
    "chk_honest": "If I can't tell which way a letter points, I'll tap \"Can't tell\" instead of guessing.",
}


# -----------------------------------------------------------------------------
# Test logic (pure functions, covered by test_app.py)
# -----------------------------------------------------------------------------
def build_test_lines(state_line: int = 40):
    """Two warm-up lines above the state line, the state line, and one line below it."""
    idx = SNELLEN_LADDER.index(state_line)
    lines = []
    for denom in SNELLEN_LADDER[max(0, idx - 2):idx]:
        lines.append({"denominator": denom, "letters": 2 if denom > 50 else 3, "role": "warm-up"})
    lines.append({"denominator": state_line, "letters": STATE_LINE_LETTERS, "role": "state line"})
    if idx + 1 < len(SNELLEN_LADDER):
        lines.append({"denominator": SNELLEN_LADDER[idx + 1], "letters": 3, "role": "margin"})
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


# -----------------------------------------------------------------------------
# Rendering helpers
# -----------------------------------------------------------------------------
def html(markup: str):
    """Renders raw HTML. Lines are stripped so Markdown never turns indented HTML into code."""
    cleaned = "\n".join(line.strip() for line in markup.splitlines() if line.strip())
    st.markdown(cleaned, unsafe_allow_html=True)


def focal_logo_svg(size: int = 34) -> str:
    """The Focal mark, same geometry and colors as assets/brand/focal-lockup.svg."""
    return f"""<svg width="{size}" height="{size}" viewBox="8 14 64 64" aria-hidden="true">
<circle cx="40" cy="46" r="28" fill="none" stroke="#10265F" stroke-width="4.4" stroke-dasharray="23.2 6.12" transform="rotate(15 40 46)"/>
<circle cx="40" cy="46" r="21.2" fill="#FFFFFF"/>
<circle cx="40" cy="46" r="14.5" fill="#3E9BE0"/>
<circle cx="40" cy="46" r="6.3" fill="#071634"/>
</svg>"""


def tumbling_e_svg(direction: str, size_px: float) -> str:
    """A 5x5 Tumbling E. The base glyph points right; it is rotated for the other directions."""
    angle = {"right": 0, "down": 90, "left": 180, "up": 270}[direction]
    return f"""<svg width="{size_px:.2f}" height="{size_px:.2f}" viewBox="0 0 50 50" role="img" aria-label="Letter E, direction hidden">
<g transform="rotate({angle} 25 25)" fill="#000000">
<rect x="0" y="0" width="10" height="50"/>
<rect x="10" y="0" width="40" height="10"/>
<rect x="10" y="20" width="40" height="10"/>
<rect x="10" y="40" width="40" height="10"/>
</g>
</svg>"""


def inject_css():
    html(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Source+Serif+4:wght@600;700&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
#MainMenu, footer {{ visibility: hidden; }}
.block-container, .stMainBlockContainer {{ padding-top: 3.2rem !important; padding-bottom: 2.5rem !important; max-width: 720px; }}
button[kind="primary"], [data-testid="stBaseButton-primary"] {{ background-color: {NAVY} !important; border-color: {NAVY} !important; color: #FFFFFF !important; }}
button[kind="primary"]:hover, [data-testid="stBaseButton-primary"]:hover {{ background-color: #22357F !important; border-color: #22357F !important; }}
button[kind="primary"]:disabled, [data-testid="stBaseButton-primary"]:disabled {{ background-color: #8E9BBE !important; border-color: #8E9BBE !important; opacity: 0.6; cursor: not-allowed; }}
[data-testid="stSliderThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {{ display: none; }}
.fc-brand {{ display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }}
.fc-logo {{ background: #FFFFFF; border-radius: 50%; width: 42px; height: 42px; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 0 1px #DCE4F0; }}
.fc-brand-name {{ font-family: 'Source Serif 4', Georgia, serif; font-weight: 700; font-size: 1.35rem; letter-spacing: 0.04em; }}
.fc-brand-tag {{ font-size: 0.8rem; opacity: 0.75; }}
.fc-steps {{ display: flex; gap: 6px; margin: 6px 0 18px 0; }}
.fc-step {{ flex: 1; text-align: center; font-size: 0.74rem; font-weight: 600; padding: 6px 4px; border-radius: 999px; background: #E3E9F3; color: {MUTED}; }}
.fc-step.on {{ background: {NAVY}; color: #FFFFFF; }}
.fc-step.done {{ background: #C9D9F0; color: {NAVY}; }}
.fc-hero {{ background: {NAVY}; color: #FFFFFF; border-radius: 18px; padding: 26px 24px 22px 24px; margin-bottom: 14px; }}
.fc-hero h1 {{ font-family: 'Source Serif 4', Georgia, serif; color: #FFFFFF; font-size: 2.0rem; line-height: 1.15; margin: 0 0 10px 0; padding: 0; }}
.fc-hero p {{ color: #D6E2F5; font-size: 1.02rem; margin: 0; }}
.fc-chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }}
.fc-chip {{ background: rgba(255,255,255,0.12); color: #FFFFFF; border: 1px solid rgba(255,255,255,0.25); border-radius: 999px; padding: 5px 12px; font-size: 0.82rem; font-weight: 500; }}
.fc-card {{ background: #FFFFFF; color: {INK}; border: 1px solid #DCE4F0; border-radius: 14px; padding: 16px 18px; margin-bottom: 12px; }}
.fc-card h3, .fc-card h4 {{ color: {INK}; margin: 0 0 6px 0; padding: 0; }}
.fc-card p, .fc-card li {{ color: {INK}; font-size: 0.94rem; }}
.fc-card .muted {{ color: {MUTED}; font-size: 0.85rem; }}
.fc-card a {{ color: #1F5FB0; }}
.fc-howto {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }}
.fc-howto div {{ background: #F3F6FB; border-radius: 12px; padding: 12px 10px; color: {INK}; font-size: 0.85rem; }}
.fc-howto b {{ display: block; color: {NAVY}; font-size: 1.15rem; margin-bottom: 2px; }}
@media (max-width: 560px) {{ .fc-howto {{ grid-template-columns: repeat(2, 1fr); }} .fc-hero h1 {{ font-size: 1.6rem; }} }}
.fc-rule {{ border-left: 5px solid {BLUE}; }}
.fc-rule .line {{ font-family: 'Source Serif 4', Georgia, serif; font-size: 1.5rem; font-weight: 700; color: {NAVY}; }}
.fc-calib {{ background: #F3F6FB; border-radius: 12px; padding: 18px 8px; overflow-x: auto; }}
.fc-idcard {{ border: 3px solid {BLUE}; border-radius: 12px; background: rgba(90,154,216,0.12); margin: 0 auto; display: flex; align-items: center; justify-content: center; color: {NAVY}; font-weight: 600; font-size: 0.85rem; }}
.fc-chart {{ background: #FFFFFF; border: 1px solid #DCE4F0; border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 8px 0 14px 0; }}
.fc-progress {{ display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 4px; opacity: 0.85; }}
.fc-bar {{ height: 8px; border-radius: 999px; background: #E3E9F3; overflow: hidden; margin-bottom: 6px; }}
.fc-bar > div {{ height: 100%; background: {BLUE}; border-radius: 999px; }}
.fc-verdict {{ border-radius: 16px; padding: 20px 20px 16px 20px; margin-bottom: 12px; }}
.fc-verdict h2 {{ font-family: 'Source Serif 4', Georgia, serif; font-size: 1.6rem; line-height: 1.2; margin: 0 0 8px 0; padding: 0; }}
.fc-verdict p {{ margin: 0 0 6px 0; font-size: 0.98rem; }}
.fc-v-on_track {{ background: #E7F4EE; border: 1px solid #B9DFCB; }}
.fc-v-on_track h2, .fc-v-on_track p {{ color: #134D38; }}
.fc-v-close, .fc-v-mixed {{ background: #FFF5E3; border: 1px solid #F2D49B; }}
.fc-v-close h2, .fc-v-close p, .fc-v-mixed h2, .fc-v-mixed p {{ color: #5C3B00; }}
.fc-v-not_yet {{ background: #EAF1FB; border: 1px solid #C2D5EE; }}
.fc-v-not_yet h2, .fc-v-not_yet p {{ color: {NAVY}; }}
.fc-ladder {{ width: 100%; border-collapse: collapse; }}
.fc-ladder td {{ padding: 7px 6px; border-bottom: 1px solid #EDF1F7; color: {INK}; font-size: 0.9rem; }}
.fc-ladder tr.state td {{ background: #EEF4FC; font-weight: 600; }}
.fc-badge {{ display: inline-block; padding: 2px 9px; border-radius: 999px; font-size: 0.76rem; font-weight: 600; }}
.fc-b-read {{ background: #DDF1E6; color: #134D38; }}
.fc-b-close {{ background: #FCEBC8; color: #5C3B00; }}
.fc-b-missed {{ background: #E3E9F3; color: {NAVY}; }}
.fc-b-skipped {{ background: #F1F3F6; color: #8A93A5; }}
.fc-plan ol {{ padding-left: 1.2rem; margin: 6px 0 0 0; }}
.fc-plan li {{ margin-bottom: 8px; }}
.fc-footer {{ font-size: 0.75rem; opacity: 0.7; text-align: center; margin-top: 28px; }}
/* Keep the arrow and reminder button rows side by side on phones */
div[data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap !important; gap: 0.5rem !important; }}
div[data-testid="column"], div[data-testid="stColumn"] {{ min-width: 0 !important; }}
[class*="st-key-ans_"]:not(.st-key-ans_cant_tell) button p {{ font-size: 1.5rem; font-weight: 700; }}
</style>""")


def render_brand_and_steps(active: str):
    order = [("setup", "1 · Setup"), ("check", "2 · Check"), ("result", "3 · Result")]
    keys = [k for k, _ in order]
    pos = keys.index(active) if active in keys else (len(keys) if active == "feedback" else -1)
    steps = ""
    for i, (_, label) in enumerate(order):
        cls = "on" if i == pos else ("done" if i < pos else "")
        steps += f'<div class="fc-step {cls}">{label}</div>'
    html(f"""<div class="fc-brand"><div class="fc-logo">{focal_logo_svg()}</div><div><div class="fc-brand-name">FOCAL</div>
<div class="fc-brand-tag">DMV Vision Pre-Check</div></div></div>""")
    if pos >= 0:
        html(f'<div class="fc-steps">{steps}</div>')


def render_footer():
    html("""<div class="fc-footer">Focal Prototype C · Duke MENG 570 · A student prototype, not a medical device
or an official DMV test. Nothing you enter is stored.</div>""")


# -----------------------------------------------------------------------------
# Session state & navigation
# -----------------------------------------------------------------------------
DEFAULTS = {
    "page": "welcome",
    "state_name": "North Carolina",
    "glasses": GLASSES_OPTIONS[0],
    "card_px": DEFAULT_CARD_PX,
    "distance_label": list(DISTANCES)[0],
    "check_items": [],
    "item_idx": 0,
    "answers": {},
    "attempts": [],
    "started_at": None,
    "reminder": None,
    "feedback_locked": False,
    "feedback_payload": None,
}


def initialize_session_state():
    for key, value in DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value.copy() if isinstance(value, (dict, list)) else value


def go(page: str):
    st.session_state.page = page


def persist(widget_key: str, store_key: str):
    """Copies a widget value into a plain key, because Streamlit drops widget
    state on pages where the widget isn't shown."""
    st.session_state[store_key] = st.session_state[widget_key]


def start_check():
    state = STATES[st.session_state.state_name]
    st.session_state.check_items = generate_items(build_test_lines(state["line"]))
    st.session_state.item_idx = 0
    st.session_state.answers = {}
    st.session_state.started_at = datetime.now().isoformat(timespec="seconds")
    st.session_state.page = "check"


def record_answer(answer: str, expected_idx: int):
    """Records one answer. Ignores stale clicks so a double tap can't answer twice."""
    if st.session_state.page != "check" or st.session_state.item_idx != expected_idx:
        return
    answers = dict(st.session_state.answers)
    answers[expected_idx] = answer
    st.session_state.answers = answers
    nxt = next_item_index(st.session_state.check_items, answers, expected_idx)
    if nxt is None:
        attempt = score_attempt(st.session_state.check_items, answers)
        attempt["finished_at"] = datetime.now().isoformat(timespec="seconds")
        st.session_state.attempts = st.session_state.attempts + [attempt]
        st.session_state.page = "result"
    else:
        st.session_state.item_idx = nxt


def set_reminder(choice: str):
    st.session_state.reminder = choice


def reset_demo():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()


# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
def page_welcome():
    render_brand_and_steps("welcome")
    html("""<div class="fc-hero">
<h1>Will you pass the DMV eye test?</h1>
<p>Find out in about 2 minutes, before you wait in line. We check you against
your state's actual vision standard and tell you what to do next.</p>
<div class="fc-chips">
<span class="fc-chip">Free · no sign-up · no ads</span>
<span class="fc-chip">Your state's real standard</span>
<span class="fc-chip">No lucky guesses</span>
</div></div>""")

    html("""<div class="fc-card"><h4>How it works</h4>
<div class="fc-howto">
<div><b>1</b>Pick the state you're getting your license in</div>
<div><b>2</b>Size the letters to your screen (30 seconds)</div>
<div><b>3</b>Say which way about 14 letters point</div>
<div><b>4</b>Get a clear answer and your next step</div>
</div></div>""")

    st.button("Start the pre-check  →", type="primary", key="btn_start", on_click=go, args=("setup",), **full_width())

    with st.expander("Why should I trust this?"):
        st.markdown(
            "- **It checks against your state's rule.** You'll see the exact line your DMV uses and a link to the official source.\n"
            "- **Letters are sized for your screen.** You match a card on screen to a real ID card, so a laptop and a phone show the same real size.\n"
            "- **No lucky guesses.** You get 6 letters at the line that decides your result. Guessing your way to a pass happens less than 1% of the time.\n"
            "- **It tells you when it isn't sure.** If you're right at the line, or two checks disagree, it says so instead of picking an answer.\n"
            "- **Nothing to sell you.** No glasses store and no ads. If you need an eye doctor, we help you find one."
        )
    with st.expander("What this is not"):
        st.markdown(
            "This is a practice check built by Duke students as a product prototype. It has **not** been validated "
            "against clinical equipment yet. It is not an eye exam, it is not accepted by any DMV, and the DMV will still "
            "test you at the counter. It only tests both eyes together. It does not test each eye, side vision, color or night vision."
        )
    render_footer()


def page_setup():
    render_brand_and_steps("setup")
    st.markdown("### Set up your check")

    # 1. State
    st.markdown("**1. Where are you getting your license?**")
    names = list(STATES)
    st.selectbox("State", names, index=names.index(st.session_state.state_name), key="w_state",
                 on_change=persist, args=("w_state", "state_name"), label_visibility="collapsed")
    state = STATES[st.session_state.state_name]
    source = (
        f'<p class="muted">Source: <a href="{state["source_url"]}" target="_blank">{state["source_name"]}</a> · checked {RULES_CHECKED}. Rules can change; your DMV has the final word.</p>'
        if state["source_url"] else
        '<p class="muted">We only have exact rules for a few states in this prototype.</p>'
    )
    html(f"""<div class="fc-card fc-rule">
<div class="muted">The line you need to read</div>
<div class="line">20/{state['line']}</div>
<p>{state['rule']} {state['glasses']}</p>
{source}</div>""")

    # 2. Glasses
    st.markdown("**2. Do you drive with glasses or contacts?**")
    st.radio("Glasses", GLASSES_OPTIONS, index=GLASSES_OPTIONS.index(st.session_state.glasses), key="w_glasses",
             on_change=persist, args=("w_glasses", "glasses"), label_visibility="collapsed")
    if st.session_state.glasses == GLASSES_OPTIONS[1]:
        st.caption("Good. Test the way you'll drive. The DMV tests you with them on too.")

    # 3. Screen calibration
    st.markdown("**3. Size the letters to your screen**")
    st.caption(
        "Hold any bank card, student ID or learner's permit flat against the screen. "
        "Slide until the blue box is exactly as wide as your card."
    )
    card_px = st.session_state.card_px
    html(f"""<div class="fc-calib"><div class="fc-idcard" style="width:{card_px}px; height:{card_px * 53.98 / 85.6:.0f}px;">Match your card here</div></div>""")
    st.slider("Card width", min_value=180, max_value=560, value=st.session_state.card_px, key="w_card",
              on_change=persist, args=("w_card", "card_px"), label_visibility="collapsed")
    st.caption("No card handy? Leave it as is. Most laptop screens are close.")

    # 4. Distance
    st.markdown("**4. How far from the screen will you be?**")
    distances = list(DISTANCES)
    st.radio("Distance", distances, index=distances.index(st.session_state.distance_label), key="w_distance",
             on_change=persist, args=("w_distance", "distance_label"), label_visibility="collapsed")
    st.caption(
        "The DMV tests distance vision, so step back. Letters are sized for the distance you pick. "
        "Tip: ask a friend to tap the arrow you point to, or use a wireless mouse."
    )

    # 5. Checklist
    st.markdown("**5. Before you start**")
    for key, label in SETUP_CHECKLIST.items():
        st.checkbox(label, key=key)
    ready = all(st.session_state.get(k, False) for k in SETUP_CHECKLIST)

    st.button("Start the check  →", type="primary", key="btn_begin", on_click=start_check, disabled=not ready, **full_width())
    if not ready:
        st.caption("Tick all three boxes to start. A good setup is what makes the result worth trusting.")
    st.button("← Back", key="btn_setup_back", on_click=go, args=("welcome",))
    render_footer()


def page_check():
    render_brand_and_steps("check")
    items = st.session_state.check_items
    idx = st.session_state.item_idx
    item = items[idx]
    distance_mm = DISTANCES[st.session_state.distance_label]
    size = letter_height_px(item["denominator"], distance_mm, st.session_state.card_px)
    biggest = max(letter_height_px(it["denominator"], distance_mm, st.session_state.card_px) for it in items)
    box_h = max(180, biggest + 60)

    answers = st.session_state.answers
    answered = len(answers)
    state_idx = [i for i, it in enumerate(items) if it["role"] == "state line"]
    state_done = all(i in answers for i in state_idx)
    total = sum(
        1 for i, it in enumerate(items)
        if it["role"] != "margin" or not state_done or should_show_item(items, answers, i)
    )
    pct = 100 * answered / max(total, 1)
    html(f"""<div class="fc-progress"><span>Letter {answered + 1} of {total}</span>
<span>Letters get smaller as you go</span></div>
<div class="fc-bar"><div style="width:{pct:.0f}%;"></div></div>""")

    html(f'<div class="fc-chart" style="height:{box_h:.0f}px;">{tumbling_e_svg(item["direction"], size)}</div>')
    st.markdown(
        "<p style='text-align:center; font-weight:600; margin:0 0 8px 0;'>Which way do the arms of the E point?</p>",
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    for col, direction in zip(cols, DIRECTIONS):
        with col:
            st.button(
                ARROWS[direction],
                key=f"ans_{direction}",
                help=direction.capitalize(),
                on_click=record_answer,
                args=(direction, idx),
                **full_width(),
            )
    st.button("Can't tell", key="ans_cant_tell", on_click=record_answer, args=(CANT_TELL, idx), **full_width())
    st.caption("Not sure? Tap \"Can't tell\". A guess that happens to be right only fools you.")

    st.button("Stop and start over", key="btn_check_restart", on_click=reset_demo)
    render_footer()


def ladder_html(attempt, possessive):
    rows = ""
    labels = {"read": "Read", "close": "Too close to call", "missed": "Not read", "skipped": "Not needed"}
    for line in attempt["lines"]:
        is_state = line["role"] == "state line"
        name = f"20/{line['denominator']}"
        note = f" · {possessive} line" if is_state else ""
        score = f"{line['correct']} of {line['shown']}" if line["shown"] else "-"
        rows += (
            f'<tr class="{"state" if is_state else ""}"><td>{name}{note}</td><td>{score}</td>'
            f'<td style="text-align:right;"><span class="fc-badge fc-b-{line["status"]}">{labels[line["status"]]}</span></td></tr>'
        )
    return f'<table class="fc-ladder">{rows}</table>'


def page_result():
    render_brand_and_steps("result")
    attempts = st.session_state.attempts
    latest = attempts[-1]
    overall = overall_result(attempts)
    verdict = overall["verdict"]
    state_name = st.session_state.state_name
    state = STATES[state_name]
    possessive = state["possessive"]
    line = f"20/{state['line']}"
    wears_glasses = st.session_state.glasses == GLASSES_OPTIONS[1]
    score = f"{latest['state_correct']} of {latest['state_total']} letters"

    # Headline
    if verdict == "on_track":
        title = f"You're on track for {possessive} vision screening"
        body = f"You read the {line} line, {possessive} line: {score}."
        if latest["margin_read"]:
            body += " You also read the smaller line below it, so you have some room to spare."
        else:
            body += " You're just over the line, so there isn't much room to spare."
    elif verdict == "close":
        title = "You're right at the line"
        body = (f"You got {score} at the {line} line. That's too close to call. "
                "Lighting, distance or a tired day could tip it either way at the counter.")
    elif verdict == "not_yet":
        title = f"You might not pass {possessive} vision screening yet"
        body = (f"You got {score} at the {line} line. Better to find out here than at the counter. "
                "Often this just means you need glasses or contacts.")
    else:
        title = "Your two checks didn't agree"
        body = ("One check cleared the line and the other didn't. We won't just keep the better one: "
                "results that move around are a sign to let an eye doctor settle it.")
    if overall["consistency"] == "consistent":
        body += " Both of your checks agreed."
    elif overall["consistency"] == "same_next_step":
        body += " Neither of your checks cleared the line."
    html(f'<div class="fc-verdict fc-v-{verdict}"><h2>{title}</h2><p>{body}</p></div>')

    # What we measured
    html(f"""<div class="fc-card"><h4>What you read</h4>{ladder_html(latest, possessive)}
<p class="muted" style="margin-top:8px;">Both eyes together · {st.session_state.distance_label.split(' (')[0]} away ·
{'with' if wears_glasses else 'without'} glasses or contacts</p></div>""")
    if len(attempts) > 1:
        st.caption("Your checks: " + "  ·  ".join(
            f"Check {i}: {a['state_correct']}/{a['state_total']} at {line}" for i, a in enumerate(attempts, start=1)
        ))

    # Next step
    if verdict == "on_track":
        glasses_line = (
            "<li><b>Wear your glasses or contacts</b> to the DMV. Your license will say you need them to drive.</li>"
            if wears_glasses else ""
        )
        html(f"""<div class="fc-card fc-plan"><h4>Your next step: go to the DMV as planned</h4><ol>
{glasses_line}
<li><b>Expect a quick screening.</b> The DMV still tests you at the counter. It usually takes about a minute.</li>
<li><b>Night driving feels blurry?</b> This check doesn't test glare or night vision. If signs look fuzzy at night, an eye exam is still worth it.</li>
</ol><p class="muted">On track for the DMV line doesn't mean your eyes are fine overall. It only means you'll likely meet this one standard. It doesn't replace an eye exam.</p></div>""")
    else:
        html(f"""<div class="fc-card fc-plan"><h4>Your next step: see an eye doctor before your DMV visit</h4><ol>
<li><b>Find an eye exam.</b> Ask your campus health center whether it offers eye exams or referrals, or look for an optometrist near you.
<a href="https://www.google.com/maps/search/optometrist+near+me" target="_blank">Open a map of optometrists near me</a>.</li>
<li><b>Know the cost before you book.</b> Ask for the price when you call. If you're on a parent's plan, check the insurance card or app for vision coverage.</li>
<li><b>What the DMV needs.</b> {state['if_missed']} {state['bring']}</li>
<li><b>Then book your DMV visit</b> and take this check again first if you like.</li>
</ol></div>""")

        with st.expander("Need the insurance info? Copy a message for your parent"):
            st.code(
                "Hey! I did a practice vision check for my driver's license and it says I should get my eyes "
                "checked before I go to the DMV. Could you send me a photo of the insurance card (front and back) "
                "so I can book an eye exam? Thanks!",
                language=None,
            )

        st.markdown("**Remind me to book an eye exam**")
        rcols = st.columns(3)
        for col, choice in zip(rcols, ["Tomorrow", "In 3 days", "In 1 week"]):
            with col:
                st.button(choice, key=f"remind_{choice}", on_click=set_reminder, args=(choice,), **full_width())
        if st.session_state.reminder:
            st.success(f"Reminder set for {st.session_state.reminder.lower()}. (Prototype: no message is actually sent.)")

    # Summary to share
    when = datetime.now().strftime("%b %d, %Y")
    summary = build_summary_text(
        state_name, attempts, overall, st.session_state.glasses, st.session_state.distance_label, when
    )
    with st.expander("Copy a summary to show a parent or eye doctor"):
        st.code(summary, language=None)

    with st.expander("Limits of this check"):
        st.markdown(
            "- It is a practice check, not an eye exam and not an official DMV result.\n"
            "- It tests both eyes together. Many DMV machines also test each eye.\n"
            "- It does not test side vision, color, glare or night vision.\n"
            "- It has not been validated against clinical equipment yet.\n"
            f"- State rules are summarized from official sources, checked {RULES_CHECKED}. Your DMV has the final word."
        )

    # Retake: one honest retake for anything other than a clear pass
    if verdict != "on_track" and len(attempts) < 2:
        st.markdown("**Not sure your setup was right?**")
        st.caption("You can take it once more. We'll show both results side by side. We don't just keep the better one.")
        st.button("Retake the check", key="btn_retake", on_click=go, args=("setup",), **full_width())

    st.divider()
    st.button("Tell us what you thought (30 seconds)  →", type="primary", key="btn_to_feedback",
              on_click=go, args=("feedback",), **full_width())
    st.button("Start over", key="btn_result_restart", on_click=reset_demo)
    render_footer()


FEEDBACK_QUESTIONS = {
    "fb_situation": ("Which best describes you right now?", [
        "I'm getting my first license soon",
        "I'm renewing my license soon",
        "No DMV visit coming up",
        "Other",
    ]),
    "fb_use": ("Before a DMV visit, how likely would you be to use a check like this?", [
        "Very unlikely", "Unlikely", "Not sure", "Likely", "Very likely",
    ]),
    "fb_clarity": ("After the check, did you know whether you'd likely pass?", [
        "Yes, clearly", "Somewhat", "No",
    ]),
    "fb_trust": ("How much would you trust this result when deciding whether to see an eye doctor first?", [
        "Not at all", "A little", "Somewhat", "Quite a bit", "Completely",
    ]),
    "fb_action": ("If your result said to see an eye doctor first, what would you most likely do?", [
        "Book an eye exam within a week",
        "Book one, but after my DMV visit",
        "Go to the DMV anyway and see what happens",
        "Talk to a parent or friend first",
        "Nothing for now",
    ]),
    "fb_compare": ("Compared with an online eye test that just gives a score (like \"20/30\"), this check is...", [
        "Less useful", "About as useful", "More useful",
    ]),
}


def page_feedback():
    render_brand_and_steps("feedback")
    st.markdown("### Help us improve this check")
    st.caption("This is a student prototype testing one idea. There are no right answers, and nothing is stored unless you download it.")

    locked = st.session_state.feedback_locked
    if not locked:
        for key, (question, options) in FEEDBACK_QUESTIONS.items():
            st.radio(question, options, index=None, key=key)
        st.text_area("What would make you trust a check like this more? (optional)", key="fb_trust_more")

    answered = all(st.session_state.get(k) is not None for k in FEEDBACK_QUESTIONS)
    if not locked:
        if st.button("Submit feedback", type="primary", key="btn_submit_feedback", disabled=not answered, **full_width()):
            attempts = st.session_state.attempts
            overall = overall_result(attempts) if attempts else None
            st.session_state.feedback_payload = {
                "prototype": "C - DMV Pre-Check (Alex)",
                "submitted_at": datetime.now().isoformat(timespec="seconds"),
                "state": st.session_state.state_name,
                "distance": st.session_state.distance_label,
                "wears_glasses": st.session_state.glasses == GLASSES_OPTIONS[1],
                "attempts": [
                    {"state_line_correct": a["state_correct"], "state_line_total": a["state_total"], "verdict": a["verdict"]}
                    for a in attempts
                ],
                "overall_verdict": overall["verdict"] if overall else None,
                "reminder_set": st.session_state.reminder,
                "answers": {k: st.session_state.get(k) for k in FEEDBACK_QUESTIONS},
                "trust_more": st.session_state.get("fb_trust_more", ""),
            }
            st.session_state.feedback_locked = True
            st.rerun()
        if not answered:
            st.caption("Answer all six questions to submit.")
    else:
        st.success("Thanks! Your answers are below. Download them to share with the Focal team.")
        given = st.session_state.feedback_payload["answers"]
        st.markdown("\n".join(f"- {question} **{given[key]}**" for key, (question, _) in FEEDBACK_QUESTIONS.items()))
        payload = json.dumps(st.session_state.feedback_payload, indent=2)
        st.download_button("Download my answers (JSON)", payload, file_name="focal_prototype_c_feedback.json",
                           mime="application/json", key="btn_download", **full_width(st.download_button))

    st.button("← Back to my result", key="btn_fb_back", on_click=go, args=("result",),
              disabled=not st.session_state.attempts)
    st.button("Start over", key="btn_fb_restart", on_click=reset_demo)
    render_footer()


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Focal · Will I pass my DMV eye test?",
        page_icon="👁️",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    initialize_session_state()
    inject_css()

    page = st.session_state.page
    if page == "check" and not st.session_state.check_items:
        page = "setup"
    if page in ("result",) and not st.session_state.attempts:
        page = "welcome"

    {
        "welcome": page_welcome,
        "setup": page_setup,
        "check": page_check,
        "result": page_result,
        "feedback": page_feedback,
    }[page]()


if __name__ == "__main__":
    main()
