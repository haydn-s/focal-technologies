"""
Focal Family - master prototype
Course: Duke University MENG 570 (Product Management)
Persona: Parent Pat (working parent of children aged 4-10), the investor pitch's user.

Combines the three class prototypes:
  - Prototype C: look and feel, screen calibration, honest "Can't tell", clear next-step plan.
  - Prototype B: parent and child doing it together, observations and a prepared parent note,
    plus its live direction task and history engine (vision.py, copied unchanged).
  - Prototype A: comparing results over time (7/30/90-day windows).

Boundary kept from B and the pitch: the task never diagnoses, scores acuity or clears a child.
The suggested next step comes from the parent's reason for checking, never from the task.

Technology: Streamlit, pandas and Altair. No accounts, database or external services.
"""

import csv
import inspect
import io
from datetime import datetime

import altair as alt
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

import family as fam
from vision import (
    DIRECTIONS, EYES, GLASSES, LEVELS, PROFILES, SCREENS, comparison_key, export_history,
    fictional_history, import_history, new_check, record_response, save_check, size_px,
    summarize, window_summary,
)


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

ARROW_ORDER = ("left", "up", "down", "right")
ARROWS = {"left": "←", "up": "↑", "down": "↓", "right": "→"}
ROTATIONS = {"right": 0, "down": 90, "left": 180, "up": 270}
SIZE_NAMES = {80: "Large", 40: "Medium", 20: "Small"}
DISTANCES = {"3 metres (about 10 feet)": 3000, "1.5 metres (about 5 feet)": 1500}
WINDOWS = ("7 days", "30 days", "90 days", "All time")
DATASETS = ("My saved checks", "Fictional example")

SETUP_CHECKLIST = (
    "The blue box matches the card's width on this screen.",
    "We measured the distance and will keep it the same.",
    "My child knows left, right, up and down, or will point. If we're testing one eye, the other is covered gently.",
    "I understand this is a practice task. It can't diagnose vision or replace a professional screening.",
)

# Widget keys that keep their values when the person moves between pages. Streamlit drops
# a widget's state on any run where the widget isn't drawn; re-assigning keeps it.
KEEP_PREFIXES = ("w_", "n_", "h_")
WIDGET_DEFAULTS = {
    "w_child": PROFILES[0],
    "w_age": fam.AGE_GROUPS[1],
    "w_reason": fam.REASONS[0],
    "w_eye": EYES[0],
    "w_glasses": GLASSES[1],
    "w_screen": SCREENS[0],
    "w_card": 324,
    "w_distance": list(DISTANCES)[0],
    "n_timing": fam.TIMING[3],
    "n_notes": "",
    "n_questions": [],
    "n_custom": "",
    "n_include_check": True,
    "h_dataset": DATASETS[0],
    "h_window": WINDOWS[1],
}


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


def tumbling_e_svg(direction: str, size_px_value: float) -> str:
    """Five-unit E (same path as Prototype B), drawn at an exact CSS size, never scaled to fit."""
    return (f'<svg role="img" aria-label="Letter E, direction hidden" width="{size_px_value:.3f}" '
            f'height="{size_px_value:.3f}" style="width:{size_px_value:.3f}px;height:{size_px_value:.3f}px;'
            f'flex-shrink:0" viewBox="0 0 5 5"><g transform="rotate({ROTATIONS[direction]} 2.5 2.5)" '
            'fill="#000000"><path d="M0 0H5V1H1V2H5V3H1V4H5V5H0Z"/></g></svg>')


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
.fc-hero .eyebrow {{ font-size: 0.76rem; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: #9CC4EE; margin-bottom: 8px; }}
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
.fc-calib {{ background: #F3F6FB; border-radius: 12px; padding: 18px 8px; overflow-x: auto; }}
.fc-idcard {{ border: 3px solid {BLUE}; border-radius: 12px; background: rgba(90,154,216,0.12); margin: 0 auto; display: flex; align-items: center; justify-content: center; color: {NAVY}; font-weight: 600; font-size: 0.85rem; }}
.fc-chart {{ background: #FFFFFF; border: 1px solid #DCE4F0; border-radius: 16px; display: flex; align-items: center; justify-content: center; margin: 8px 0 14px 0; overflow: auto; }}
.fc-progress {{ display: flex; justify-content: space-between; font-size: 0.82rem; margin-bottom: 4px; opacity: 0.85; }}
.fc-bar {{ height: 8px; border-radius: 999px; background: #E3E9F3; overflow: hidden; margin-bottom: 6px; }}
.fc-bar > div {{ height: 100%; background: {BLUE}; border-radius: 999px; }}
.fc-verdict {{ border-radius: 16px; padding: 20px 20px 16px 20px; margin-bottom: 12px; background: #EAF1FB; border: 1px solid #C2D5EE; }}
.fc-verdict h2 {{ font-family: 'Source Serif 4', Georgia, serif; font-size: 1.6rem; line-height: 1.2; margin: 0 0 8px 0; padding: 0; color: {NAVY}; }}
.fc-verdict p {{ margin: 0 0 6px 0; font-size: 0.98rem; color: {NAVY}; }}
.fc-keep {{ border-radius: 14px; padding: 14px 18px; margin-bottom: 12px; background: #FFF5E3; border: 1px solid #F2D49B; color: #5C3B00; }}
.fc-keep b, .fc-keep p {{ color: #5C3B00; margin: 0; font-size: 0.95rem; }}
.fc-fiction {{ border-radius: 14px; padding: 12px 16px; margin-bottom: 12px; background: #FDEFE7; border: 1px dashed #D9895A; color: #6B2E0B; font-size: 0.92rem; }}
.fc-ladder {{ width: 100%; border-collapse: collapse; }}
.fc-ladder td {{ padding: 8px 6px; border-bottom: 1px solid #EDF1F7; color: {INK}; font-size: 0.9rem; vertical-align: middle; }}
.fc-minibar {{ height: 8px; width: 100%; min-width: 80px; background: #E3E9F3; border-radius: 999px; overflow: hidden; }}
.fc-minibar > div {{ height: 100%; background: {NAVY}; border-radius: 999px; }}
.fc-metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 12px; }}
.fc-metric {{ background: #FFFFFF; border: 1px solid #DCE4F0; border-radius: 14px; padding: 12px 14px; }}
.fc-metric .v {{ font-family: 'Source Serif 4', Georgia, serif; font-size: 1.5rem; font-weight: 700; color: {NAVY}; line-height: 1.2; }}
.fc-metric .l {{ font-size: 0.78rem; color: {MUTED}; }}
.fc-plan ol {{ padding-left: 1.2rem; margin: 6px 0 0 0; }}
.fc-plan li {{ margin-bottom: 8px; }}
.fc-footer {{ font-size: 0.75rem; opacity: 0.7; text-align: center; margin-top: 28px; }}
@media (max-width: 560px) {{ .fc-howto {{ grid-template-columns: repeat(2, 1fr); }} .fc-hero h1 {{ font-size: 1.6rem; }} .fc-metrics {{ grid-template-columns: 1fr; }} }}
/* Keep button rows side by side on phones */
div[data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap !important; gap: 0.5rem !important; }}
div[data-testid="column"], div[data-testid="stColumn"] {{ min-width: 0 !important; }}
[class*="st-key-ans_"]:not(.st-key-ans_cant_tell) button p, [class*="st-key-prac_"] button p {{ font-size: 1.5rem; font-weight: 700; }}
</style>""")


STEPS = [("setup", "1 · Set up"), ("check", "2 · Check"), ("history", "3 · History"), ("note", "4 · Note")]
PAGE_STEP = {"setup": "setup", "practice": "check", "check": "check", "result": "check",
             "history": "history", "note": "note"}


def render_brand_and_steps(page: str):
    html(f"""<div class="fc-brand"><div class="fc-logo">{focal_logo_svg()}</div><div><div class="fc-brand-name">FOCAL</div>
<div class="fc-brand-tag">Focal Family · a prepared next step for parents</div></div></div>""")
    active = PAGE_STEP.get(page)
    if active is None:
        return
    pos = [k for k, _ in STEPS].index(active)
    pills = "".join(
        f'<div class="fc-step {"on" if i == pos else ("done" if i < pos else "")}">{label}</div>'
        for i, (_, label) in enumerate(STEPS)
    )
    html(f'<div class="fc-steps">{pills}</div>')


def render_footer():
    html("""<div class="fc-footer">Focal Family · Duke MENG 570 · A student prototype, not a medical device or a
vision screening. Free for families. Nothing you enter is stored after you leave unless you download it.</div>""")


# -----------------------------------------------------------------------------
# Session state & navigation
# -----------------------------------------------------------------------------
def initialize_session_state():
    ss = st.session_state
    ss.setdefault("page", "welcome")
    ss.setdefault("check", None)
    ss.setdefault("records", [])
    ss.setdefault("reminder", None)
    ss.setdefault("practice_miss", False)
    ss.setdefault("note_fictional", False)
    if "examples" not in ss:
        ss.examples = fictional_history()
    for key, value in WIDGET_DEFAULTS.items():
        ss.setdefault(key, value.copy() if isinstance(value, list) else value)


def keep_widget_state():
    for key in list(st.session_state.keys()):
        if key.startswith(KEEP_PREFIXES):
            st.session_state[key] = st.session_state[key]


def go(page: str):
    st.session_state.page = page


def current_setup():
    ss = st.session_state
    return {"profile": ss.w_child, "eye": ss.w_eye, "glasses": ss.w_glasses, "screen": ss.w_screen,
            "distance_mm": DISTANCES[ss.w_distance], "reference_px": int(ss.w_card)}


def start_check():
    st.session_state.check = new_check(current_setup())
    st.session_state.practice_miss = False
    st.session_state.page = "practice"


def practice(choice: str):
    check = st.session_state.check
    if not check:
        return
    if choice == "right":
        check["practice_complete"] = True
        st.session_state.practice_miss = False
        st.session_state.page = "check"
    else:
        st.session_state.practice_miss = True


def answer(index: int, choice: str):
    """Records one answer. vision.record_response ignores stale or repeated clicks."""
    check = st.session_state.check
    if check and record_response(check, index, choice) and check["completed_at"]:
        st.session_state.page = "result"


def set_paused(value: bool):
    if st.session_state.check:
        st.session_state.check["paused"] = value


def discard_check():
    st.session_state.check = None
    st.session_state.page = "setup"


def save_and_view_history():
    check = st.session_state.check
    if check and not any(r["id"] == check["id"] for r in st.session_state.records):
        save_check(st.session_state.records, check)
    st.session_state.h_dataset = DATASETS[0]
    if check:
        st.session_state.h_child = check["setup"]["profile"]
    st.session_state.page = "history"


def latest_summary():
    """The most recent completed live check: the current one, else the newest saved one."""
    check = st.session_state.check
    if check and check.get("completed_at"):
        return summarize(check)
    if st.session_state.records:
        return summarize(st.session_state.records[-1])
    return None


def note_from_state():
    ss = st.session_state
    next_step = ss.get("n_next") or fam.suggested_next_step(ss.w_reason)
    return {
        "fictional": ss.note_fictional,
        "child": ss.w_child,
        "age_group": ss.w_age,
        "reason": ss.w_reason,
        "observations": [o for i, o in enumerate(fam.OBSERVATIONS) if ss.get(f"n_obs_{i}")],
        "timing": ss.n_timing,
        "notes": ss.n_notes,
        "next_step": next_step,
        "recipient": ss.get("n_recipient") or fam.suggested_recipient(ss.w_reason),
        "questions": list(ss.n_questions),
        "custom_question": ss.n_custom,
        "include_check": ss.n_include_check and not ss.note_fictional,
        "tasks": {task: bool(ss.get(task_key(next_step, i)))
                  for i, task in enumerate(fam.follow_up_tasks(next_step))},
    }


def task_key(next_step, index):
    # The route is part of the key so ticks never carry over to another next step.
    return f"n_task_{fam.NEXT_STEPS.index(next_step)}_{index}"


def rewrite_message():
    message = fam.build_message(note_from_state(), latest_summary())
    st.session_state.n_message = message
    st.session_state.message_generated = message


def load_fictional_note():
    example = fam.fictional_note()
    ss = st.session_state
    ss.note_fictional = True
    ss.w_child, ss.w_age, ss.w_reason = example["child"], example["age_group"], example["reason"]
    for i, observation in enumerate(fam.OBSERVATIONS):
        ss[f"n_obs_{i}"] = observation in example["observations"]
    ss.n_timing, ss.n_notes = example["timing"], example["notes"]
    ss.n_next, ss.n_recipient = example["next_step"], example["recipient"]
    ss.n_questions, ss.n_custom = list(example["questions"]), example["custom_question"]
    ss.n_message = ss.message_generated = fam.build_message(example)


def clear_fictional_note():
    ss = st.session_state
    ss.note_fictional = False
    for i in range(len(fam.OBSERVATIONS)):
        ss[f"n_obs_{i}"] = False
    ss.n_timing, ss.n_notes, ss.n_questions, ss.n_custom = fam.TIMING[3], "", [], ""
    ss.n_next = fam.suggested_next_step(ss.w_reason)
    ss.n_recipient = fam.suggested_recipient(ss.w_reason)
    rewrite_message()


def scroll_to_top_on_page_change(page: str):
    """Streamlit keeps the scroll position between pages; start each new page at the top."""
    if st.session_state.get("last_page") == page:
        return
    st.session_state.last_page = page
    script = ("<script>const d = window.parent.document;"
              "(d.querySelector('[data-testid=\"stMain\"]') || d.querySelector('section.main') || d.body).scrollTo(0, 0);"
              "window.parent.scrollTo(0, 0);</script>")
    if hasattr(st, "iframe"):
        st.iframe(script, height=1)
    else:
        components.html(script, height=0)


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
<div class="eyebrow">Focal Family · for parents of children 4–10</div>
<h1>Got a school vision letter? Make the next step easy.</h1>
<p>Do a short check together at home, see how it changes over time, and leave with a note
ready for the school nurse or eye doctor.</p>
<div class="fc-chips">
<span class="fc-chip">Free for families</span>
<span class="fc-chip">No account · no camera</span>
<span class="fc-chip">Not a diagnosis: a prepared next step</span>
</div></div>""")

    html("""<div class="fc-card"><h4>How it works</h4>
<div class="fc-howto">
<div><b>1</b>Set up your screen and distance (1 minute)</div>
<div><b>2</b>Practice, then 12 quick letters together</div>
<div><b>3</b>Save it and compare over time</div>
<div><b>4</b>Leave with a note that's ready to send</div>
</div></div>""")

    st.button("Start a check together  →", type="primary", key="btn_start", on_click=go, args=("setup",), **full_width())
    left, right = st.columns(2)
    with left:
        st.button("See saved history", key="btn_welcome_history", on_click=go, args=("history",), **full_width())
    with right:
        st.button("Prepare a parent note", key="btn_welcome_note", on_click=go, args=("note",), **full_width())

    with st.expander("Why should I trust this?"):
        st.markdown(
            "- **Letters are sized for your screen.** You match a box to any bank card or ID, and each E is drawn at the size an eye chart uses for your distance.\n"
            "- **Fair comparisons only.** History compares checks done with the same child, eye, glasses, screen and distance.\n"
            "- **Guessing doesn't help.** \"Can't tell\" counts as a miss, so every check has the same 12 letters.\n"
            "- **You stay in control.** No account and no camera. Your history stays in this browser visit unless you download it."
        )
    with st.expander("What this is not"):
        st.markdown(
            "This is a practice task built by Duke students as a product prototype. It is **not** a vision screening, "
            "it can't diagnose anything, and it can't clear a child from a school or professional referral. Labels like "
            "20/40 describe the size of the letter, not your child's eyesight. A good result never cancels follow-up care."
        )
    with st.expander("For schools (proposed pilot)"):
        st.markdown(
            "Focal Family is free for families. Schools would license it to support follow-up after a screening "
            "(proposed: \\$2,400 per school per year). A 10-site pilot would measure whether more families complete "
            "their next step within 30 days, and how much staff follow-up time it saves. No school partnerships or "
            "pilots exist yet: these are the team's proposals."
        )
    render_footer()


def page_setup():
    render_brand_and_steps("setup")
    st.markdown("### Set up your check")

    st.markdown("**1. Who's checking today?**")
    left, right = st.columns(2)
    with left:
        st.selectbox("Child label", PROFILES, key="w_child")
    with right:
        st.radio("Age group", fam.AGE_GROUPS, key="w_age", horizontal=True)
    st.radio("What brings you here?", fam.REASONS, key="w_reason")
    st.caption("Use a label, not a name. Nothing identifies your child.")
    if fam.concern_already_raised(st.session_state.w_reason):
        st.caption("Good to know. We'll keep that follow-up front and center: this check never replaces it.")

    st.markdown("**2. Which eyes, and with glasses?**")
    st.radio("Eyes for this check", EYES, key="w_eye", horizontal=True)
    st.radio("Glasses or contacts", GLASSES, key="w_glasses", horizontal=True)

    st.markdown("**3. Size the letters to your screen**")
    st.caption("Hold any bank card or ID flat against the screen. Slide until the blue box is exactly as wide as the card.")
    card_px = st.session_state.w_card
    html(f"""<div class="fc-calib"><div class="fc-idcard" style="width:{card_px}px; height:{card_px * 53.98 / 85.6:.0f}px;">Match your card here</div></div>""")
    st.slider("Card width", min_value=160, max_value=600, key="w_card", label_visibility="collapsed")
    st.selectbox("Which screen is this?", SCREENS, key="w_screen")
    st.caption("Keep the same screen and browser zoom next time, so checks can be compared.")

    st.markdown("**4. How far from the screen?**")
    st.radio("Distance", list(DISTANCES), key="w_distance", label_visibility="collapsed")
    st.caption("Your child stands at the measured distance and points. You tap the matching arrow.")

    st.markdown("**5. Before you start**")
    # A list, not a generator: every box must be drawn even when an earlier one is unticked.
    ready = all([st.checkbox(label, key=f"chk_{i}") for i, label in enumerate(SETUP_CHECKLIST)])
    st.button("Start practice  →", type="primary", key="btn_begin", on_click=start_check, disabled=not ready, **full_width())
    if not ready:
        st.caption("Tick all four boxes to start. A good setup is what makes a comparison fair.")
    st.button("← Back", key="btn_setup_back", on_click=go, args=("welcome",))
    render_footer()


def page_practice():
    render_brand_and_steps("practice")
    st.markdown("### Practice together")
    st.write("Ask your child to point the way the arms of the E point. Then tap the same arrow.")
    html(f'<div class="fc-chart" style="height:200px;">{tumbling_e_svg("right", 95)}</div>')
    cols = st.columns(4)
    for col, direction in zip(cols, ARROW_ORDER):
        with col:
            st.button(ARROWS[direction], key=f"prac_{direction}", help=direction.capitalize(),
                      on_click=practice, args=(direction,), **full_width())
    if st.session_state.practice_miss:
        st.info("Not quite. This one points right →. Try again together.")
    st.caption("Practice doesn't count. The real check starts after this.")
    st.button("← Back to setup", key="btn_practice_back", on_click=discard_check)
    render_footer()


def page_check():
    render_brand_and_steps("check")
    check = st.session_state.check
    setup = check["setup"]
    index = len(check["responses"])
    total = len(check["trials"])

    if check["paused"]:
        html(f"""<div class="fc-card"><h4>Paused</h4><p>Take the time you need. You'll pick up at letter
{index + 1} of {total}, with the same setup.</p></div>""")
        st.button("Resume", type="primary", key="btn_resume", on_click=set_paused, args=(False,), **full_width())
        st.button("Discard this check", key="btn_discard_paused", on_click=discard_check)
        render_footer()
        return

    trial = check["trials"][index]
    biggest = size_px(max(LEVELS), setup)
    box_h = max(200, biggest + 60)
    html(f"""<div class="fc-progress"><span>Letter {index + 1} of {total}</span>
<span>{SIZE_NAMES[trial['level']]} letters</span></div>
<div class="fc-bar"><div style="width:{100 * index / total:.0f}%;"></div></div>""")
    html(f'<div class="fc-chart" style="height:{box_h:.0f}px;">{tumbling_e_svg(trial["target"], size_px(trial["level"], setup))}</div>')
    st.markdown("<p style='text-align:center; font-weight:600; margin:0 0 8px 0;'>Which way do the arms of the E point?</p>",
                unsafe_allow_html=True)
    cols = st.columns(4)
    for col, direction in zip(cols, ARROW_ORDER):
        with col:
            st.button(ARROWS[direction], key=f"ans_{direction}", help=direction.capitalize(),
                      on_click=answer, args=(index, direction), **full_width())
    st.button("Can't tell", key="ans_cant_tell", on_click=answer, args=(index, "cant_tell"), **full_width())
    st.caption("Not sure? Tap \"Can't tell\". A lucky guess only hides what you want to see.")
    left, right = st.columns(2)
    with left:
        st.button("Pause", key="btn_pause", on_click=set_paused, args=(True,), **full_width())
    with right:
        st.button("Discard", key="btn_discard", on_click=discard_check, **full_width())
    st.caption(f"{setup['profile']} · {setup['eye']} · {setup['glasses']} · {setup['distance_mm'] / 1000:g} m")
    render_footer()


def size_rows_html(summary):
    rows = ""
    for level, row in zip(LEVELS, summary["levels"]):
        pct = 100 * row["Correct"] / row["Trials"]
        rows += (f'<tr><td><b>{SIZE_NAMES[level]}</b> <span class="muted">({row["Task size"].split()[0]} size)</span></td>'
                 f'<td style="width:45%;"><div class="fc-minibar"><div style="width:{pct:.0f}%;"></div></div></td>'
                 f'<td style="text-align:right; white-space:nowrap;">{row["Correct"]} of {row["Trials"]}</td></tr>')
    return f'<table class="fc-ladder">{rows}</table>'


def page_result():
    render_brand_and_steps("result")
    check = st.session_state.check
    summary = summarize(check)
    child = check["setup"]["profile"]
    sizes = " · ".join(f"{SIZE_NAMES[level]} {row['Correct']}/{row['Trials']}" for level, row in zip(LEVELS, summary["levels"]))
    html(f"""<div class="fc-verdict"><h2>{child} matched {summary['correct']} of {summary['total']} directions</h2>
<p>{sizes}</p><p>Save it to see how it compares over time, then turn it into a note.</p></div>""")

    if fam.concern_already_raised(st.session_state.w_reason):
        html("""<div class="fc-keep"><p><b>Keep the follow-up you were asked for.</b> A school or professional already
raised a concern. Whatever this practice check shows, it can't cancel that referral.</p></div>""")

    html(f"""<div class="fc-card"><h4>By letter size</h4>{size_rows_html(summary)}
<p class="muted" style="margin-top:8px;">{check['setup']['eye']} · {check['setup']['glasses']} ·
{check['setup']['distance_mm'] / 1000:g} m · {check['setup']['screen']}</p></div>""")

    with st.expander("What this does and doesn't tell you"):
        st.markdown(
            "- It shows how this practice task went today, with this setup.\n"
            "- Attention, tiredness, guessing, learning and setup all change results.\n"
            "- The 20/80, 20/40 and 20/20 labels describe letter size only. They are not an eyesight score.\n"
            "- A high score doesn't rule out an eye problem. A low one doesn't mean there is one."
        )

    saved = any(r["id"] == check["id"] for r in st.session_state.records)
    label = "See it in your history  →" if saved else "Save and see your history  →"
    st.button(label, type="primary", key="btn_save", on_click=save_and_view_history, **full_width())
    left, right = st.columns(2)
    with left:
        st.button("Start another check", key="btn_another", on_click=discard_check, **full_width())
    with right:
        st.button("Skip to the parent note", key="btn_result_note", on_click=go, args=("note",), **full_width())
    render_footer()


def metric_cards(items):
    cells = "".join(f'<div class="fc-metric"><div class="v">{value}</div><div class="l">{label}</div></div>'
                    for label, value in items)
    html(f'<div class="fc-metrics">{cells}</div>')


def page_history():
    render_brand_and_steps("history")
    st.markdown("### How it's going over time")
    st.caption("Compare checks for the same child, eye and setup.")
    ss = st.session_state
    st.radio("History", DATASETS, key="h_dataset", horizontal=True, label_visibility="collapsed")
    example = ss.h_dataset == DATASETS[1]

    if example:
        html("""<div class="fc-fiction"><b>Fictional example.</b> Every date and answer below is made up, to show how
comparisons work. It isn't a real child and doesn't show a change in anyone's eyesight.</div>""")
        records = ss.examples
    else:
        records = ss.records
        with st.expander("Keep or restore your history"):
            st.caption("History lives in this browser visit only. Download it to keep it, then restore it next time.")
            st.download_button("Download history (JSON)", export_history(records), "focal-family-history.json",
                               "application/json", key="btn_export_json", **full_width(st.download_button))
            uploaded = st.file_uploader("Restore a Focal history file", type="json", key="upload_history")
            if st.button("Restore history", disabled=uploaded is None, key="btn_import"):
                try:
                    merged = import_history(uploaded.getvalue(), records)
                    added = len(merged) - len(records)
                    ss.records = merged
                    records = merged
                    st.success(f"Restored {added} more check{'s' if added != 1 else ''}. Duplicates were skipped.")
                except (ValueError, RecursionError) as error:
                    st.error(str(error))

    if not records:
        html("""<div class="fc-card"><h4>No saved checks yet</h4><p>Do a check together and save it. Or pick
<b>Fictional example</b> above to see how comparisons over time work.</p></div>""")
        st.button("Start a check together  →", type="primary", key="btn_history_start", on_click=go, args=("setup",), **full_width())
        st.button("Prepare a parent note", key="btn_history_note_empty", on_click=go, args=("note",))
        render_footer()
        return

    children = sorted({r["setup"]["profile"] for r in records})
    if ss.get("h_child") not in children:
        ss.pop("h_child", None)
    child = st.selectbox("Child", children, key="h_child")
    groups = {}
    for record in records:
        if record["setup"]["profile"] == child:
            groups.setdefault(comparison_key(record), []).append(record)

    def label(key):
        _, _, _, eye, glasses, screen, distance, ref = key
        return f"{eye} · {glasses} · {screen} · {distance / 1000:g} m"

    group_key = f"h_group_{'example' if example else 'live'}_{child.replace(' ', '_')}"
    if ss.get(group_key) not in groups:
        ss.pop(group_key, None)
    group = st.selectbox("Same setup", list(groups), format_func=label, key=group_key)
    st.radio("Time window", WINDOWS, key="h_window", horizontal=True)
    days = None if ss.h_window == "All time" else int(ss.h_window.split()[0])
    summary = window_summary(groups[group], days)

    change = "—" if summary["delta_points"] is None else f"{summary['delta_points']:+.0f} pts"
    average = "—" if summary["average"] is None else f"{summary['average']:.0f}%"
    metric_cards([("Checks in this window", summary["count"]), ("Average letters matched", average),
                  ("Change vs the window before", change)])
    if days and summary["delta_points"] is None:
        st.caption(f"A comparison needs checks in the {days} days before this window too. There were {summary['previous_count']}.")

    rows = [{"Date (UTC)": datetime.fromisoformat(r["completed_at"]),
             "Letters matched (%)": round(summarize(r)["accuracy"], 1),
             "Matched": summarize(r)["correct"], "Of": 12,
             "Source": "Fictional example" if example else "Live check"} for r in summary["records"]]
    if rows:
        frame = pd.DataFrame(rows)
        chart = alt.Chart(frame).mark_line(point=alt.OverlayMarkDef(size=70, filled=True), color="#1F65A8", strokeWidth=3).encode(
            x=alt.X("Date (UTC):T", title=None, scale=alt.Scale(type="utc")),
            y=alt.Y("Letters matched (%):Q", scale=alt.Scale(domain=[0, 100]), title="Letters matched (%)"),
            tooltip=[alt.Tooltip("Date (UTC):T", format="%b %d, %Y"), "Letters matched (%):Q"],
        ).properties(height=220)
        st.altair_chart(chart, **full_width(st.altair_chart))
        with st.expander("See the dated checks"):
            st.dataframe(frame, hide_index=True, **full_width(st.dataframe))
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
            st.download_button("Download this window (CSV)", buffer.getvalue(), "focal-family-window.csv", "text/csv",
                               key="btn_export_csv")
    else:
        st.info("No checks in this window. Pick a longer window or do another check.")
    st.caption("Changes can come from attention, guessing, learning or setup. They don't show a change in eyesight.")

    st.button("Turn this into a parent note  →", type="primary", key="btn_history_note", on_click=go, args=("note",), **full_width())
    st.button("Start another check", key="btn_history_another", on_click=go, args=("setup",))
    if not example:
        with st.expander("Clear saved history"):
            confirm = st.checkbox("Delete all saved checks from this browser visit", key="confirm_clear")
            if st.button("Clear history", disabled=not confirm, key="btn_clear"):
                ss.records = []
                st.rerun()
    render_footer()


def page_note():
    render_brand_and_steps("note")
    ss = st.session_state
    ss.setdefault("n_next", fam.suggested_next_step(ss.w_reason))
    ss.setdefault("n_recipient", fam.suggested_recipient(ss.w_reason))
    st.markdown("### Make the next step easy")
    if ss.note_fictional:
        html("""<div class="fc-fiction"><b>Fictional example.</b> This note is made up for a demo. Clear it to write your own.</div>""")
        st.button("Clear the example", key="btn_clear_example", on_click=clear_fictional_note)
    else:
        st.caption("Your answers stay on this page until you download them.")

    if fam.concern_already_raised(ss.w_reason):
        html("""<div class="fc-keep"><p><b>Keep the follow-up you were asked for.</b> This note helps you act on it.
Nothing here replaces it.</p></div>""")

    st.markdown("**1. What have you noticed?**")
    for i, observation in enumerate(fam.OBSERVATIONS):
        st.checkbox(observation, key=f"n_obs_{i}")
    st.selectbox("When did you notice it?", fam.TIMING, key="n_timing")
    st.text_area("Anything else? (optional, no names please)", key="n_notes", max_chars=600, height=90)

    st.markdown("**2. Your next step**")
    st.radio("Next step", fam.NEXT_STEPS, key="n_next", label_visibility="collapsed")
    if ss.n_next == fam.suggested_next_step(ss.w_reason):
        st.caption(f"Suggested because: {ss.w_reason.lower()}. You can change it.")
    with st.container(border=True):
        st.markdown("**Your plan** · tick things off as you go")
        for i, task in enumerate(fam.follow_up_tasks(ss.n_next)):
            st.checkbox(task, key=task_key(ss.n_next, i))
    st.markdown("**Remind me**")
    rcols = st.columns(len(fam.REMINDERS))
    for col, choice in zip(rcols, fam.REMINDERS):
        with col:
            st.button(choice, key=f"btn_remind_{choice}", on_click=set_reminder, args=(choice,), **full_width())
    if ss.reminder:
        st.success(f"Reminder set for {ss.reminder.lower()}. (Prototype: no reminder is actually sent.)")

    st.markdown("**3. Your message**")
    st.radio("Who is it for?", fam.RECIPIENTS, key="n_recipient", horizontal=True)
    st.multiselect("Questions I'd like to ask", fam.QUESTION_OPTIONS, key="n_questions")
    st.text_input("A question of my own (optional)", key="n_custom", max_chars=300)
    summary = latest_summary()
    if summary and not ss.note_fictional:
        st.checkbox("Include my latest practice check (labelled as not a screening)", key="n_include_check")
    # The draft follows the answers above until the parent edits it by hand.
    generated = fam.build_message(note_from_state(), summary)
    if "n_message" not in ss or ss.n_message == ss.get("message_generated"):
        ss.n_message = generated
    ss.message_generated = generated
    st.text_area("Message draft (edit freely)", key="n_message", height=280, max_chars=4000)
    if ss.n_message != generated:
        st.caption("You've edited the draft, so it no longer updates on its own.")
        st.button("Rewrite the message from my answers", key="btn_rewrite", on_click=rewrite_message)
    st.caption("This is your draft. Nothing is sent. Copy it into an email or the school's portal.")

    note = note_from_state()
    history_line = (f"Saved practice checks this visit: {len(ss.records)}." if ss.records and not ss.note_fictional else None)
    take_home = fam.build_summary(note, ss.n_message, None if ss.note_fictional else summary, history_line, ss.reminder)
    left, right = st.columns(2)
    with left:
        st.download_button("Download my note", take_home, "focal-family-note.txt", "text/plain", type="primary",
                           key="btn_download_note", **full_width(st.download_button))
    with right:
        st.download_button("Download message", ss.n_message, "focal-family-message.txt", "text/plain",
                           key="btn_download_message", **full_width(st.download_button))
    if not ss.note_fictional:
        st.button("Fill with a fictional example (for demos)", key="btn_example", on_click=load_fictional_note)
    with st.expander("Preview the take-home note"):
        st.text(take_home)

    st.divider()
    left, right = st.columns(2)
    with left:
        st.button("← History", key="btn_note_history", on_click=go, args=("history",), **full_width())
    with right:
        st.button("Start over", key="btn_note_restart", on_click=reset_demo, **full_width())
    render_footer()


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    st.set_page_config(
        page_title="Focal Family · a prepared next step for parents",
        page_icon="👁️",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    initialize_session_state()
    keep_widget_state()
    inject_css()

    page = st.session_state.page
    check = st.session_state.check
    if page in ("practice", "check", "result") and check is None:
        page = "setup"
    elif page == "practice" and check["practice_complete"]:
        page = "check"
    elif page == "check" and check["completed_at"]:
        page = "result"
    elif page == "result" and not check["completed_at"]:
        page = "check"

    scroll_to_top_on_page_change(page)
    {
        "welcome": page_welcome,
        "setup": page_setup,
        "practice": page_practice,
        "check": page_check,
        "result": page_result,
        "history": page_history,
        "note": page_note,
    }[page]()


if __name__ == "__main__":
    main()
