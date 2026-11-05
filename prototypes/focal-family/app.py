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

Secondary option: Prototype C's DMV pre-check (dmv.py), for a teen's learner's permit or a
parent's renewal. It sits behind an "Also from Focal" card so the family flow stays the focus.

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

import dmv
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
# Palette from the team's React UI candidate (prototypes/focal-family-ui) and the Focal logo.
NAVY = "#10265F"
BLUE = "#3E9BE0"
INK = "#20304D"
MUTED = "#5B6578"
PAPER = "#F7F5F0"
LINE = "rgba(32,48,77,0.12)"

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
KEEP_PREFIXES = ("w_", "n_", "h_", "d_")
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
    "d_state": list(dmv.STATES)[0],
    "d_glasses": dmv.GLASSES_OPTIONS[0],
}

DMV_CHECKLIST = (
    "The room is well lit and there's no glare on the screen.",
    "We can be at the distance we picked (a helper can tap the arrows).",
    "If a letter is unclear, we'll tap \"Can't tell\" instead of guessing.",
)


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


SERIF = "'Fraunces', Georgia, serif"
MONO = "'JetBrains Mono', ui-monospace, Menlo, monospace"
CARD_SHADOW = "0 1px 3px rgba(32,48,77,0.03), 0 14px 32px -10px rgba(32,48,77,0.07)"


def inject_css():
    """The look follows the team's React UI candidate: warm paper, white cards, navy, Fraunces headlines.
    Colors are fixed (see .streamlit/config.toml), so the app is light even on a dark-mode laptop."""
    html(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=JetBrains+Mono:wght@400;500&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap');
html, body, .stApp, [class*="css"] {{ font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
.stApp {{ background: {PAPER}; color: {INK}; }}
#MainMenu, footer, header[data-testid="stHeader"] {{ display: none !important; }}
.block-container, .stMainBlockContainer {{ padding-top: 0 !important; padding-bottom: 2.5rem !important; max-width: 780px; }}
h1, h2, h3, h4 {{ color: {INK}; }}
[data-testid="stMarkdownContainer"] h3 {{ font-family: {SERIF}; font-weight: 600; letter-spacing: -0.01em; }}

/* Buttons */
[data-testid="stBaseButton-primary"] {{ background: {NAVY} !important; border: 1px solid {NAVY} !important; color: #FFFFFF !important;
  min-height: 3rem; font-weight: 600; box-shadow: 0 8px 18px -10px rgba(16,38,95,0.55); transition: transform 160ms ease, background 160ms ease; }}
[data-testid="stBaseButton-primary"] p {{ font-weight: 600; }}
[data-testid="stBaseButton-primary"]:hover {{ background: #1B3578 !important; border-color: #1B3578 !important; transform: translateY(-1px); }}
[data-testid="stBaseButton-primary"]:disabled {{ background: #A9B2C8 !important; border-color: #A9B2C8 !important; box-shadow: none; transform: none; cursor: not-allowed; }}
[data-testid="stBaseButton-secondary"] {{ background: #FFFFFF !important; border: 1px solid {LINE} !important; color: {INK} !important; min-height: 2.75rem;
  transition: transform 160ms ease, border-color 160ms ease; }}
[data-testid="stBaseButton-secondary"]:hover {{ border-color: {NAVY} !important; color: {NAVY} !important; transform: translateY(-1px); }}
[data-testid="stBaseButton-tertiary"] p {{ font-size: 0.9rem; color: {INK}; }}
[data-testid="stBaseButton-tertiary"]:hover p {{ color: {NAVY}; }}

/* Choices as chips, like the React UI */
div[role="radiogroup"] {{ gap: 8px; flex-wrap: wrap; }}
label[data-testid="stRadioOption"] {{ background: #FFFFFF; border: 1px solid {LINE}; border-radius: 12px; padding: 9px 14px;
  margin: 0 !important; transition: border-color 160ms ease, background 160ms ease; }}
label[data-testid="stRadioOption"]:hover {{ border-color: rgba(16,38,95,0.45); }}
label[data-testid="stRadioOption"][data-selected="true"] {{ background: #EEF1F8; border-color: {NAVY}; box-shadow: inset 0 0 0 1px {NAVY}; }}
label[data-testid="stRadioOption"][data-selected="true"] p {{ font-weight: 600; color: {NAVY}; }}
label[data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) {{ display: none; }}
[class*="st-key-chk_"], [class*="st-key-dchk_"], [class*="st-key-n_obs_"], [class*="st-key-n_task_"] {{ width: 100% !important; }}
[class*="st-key-chk_"] .stCheckbox, [class*="st-key-dchk_"] .stCheckbox, [class*="st-key-n_obs_"] .stCheckbox {{ width: 100%; }}
[class*="st-key-chk_"] label, [class*="st-key-dchk_"] label, [class*="st-key-n_obs_"] label {{ background: #FFFFFF; border: 1px solid {LINE};
  border-radius: 12px; padding: 10px 12px; width: 100%; box-sizing: border-box; transition: border-color 160ms ease, background 160ms ease; }}
[class*="st-key-chk_"] label:has(input:checked), [class*="st-key-dchk_"] label:has(input:checked), [class*="st-key-n_obs_"] label:has(input:checked) {{
  background: #EEF1F8; border-color: {NAVY}; }}
[data-testid="stSliderThumbValue"], [data-testid="stSliderTickBarMin"], [data-testid="stSliderTickBarMax"] {{ display: none; }}
[data-testid="stExpander"] details {{ background: #FFFFFF; border: 1px solid {LINE}; border-radius: 14px; }}

/* Section cards (keyed containers) */
[class*="st-key-card_"] {{ background: #FFFFFF; border: 1px solid {LINE}; border-radius: 18px; padding: 20px 22px 18px 22px; box-shadow: {CARD_SHADOW}; }}
.fc-sec {{ font-weight: 600; font-size: 1.02rem; color: {INK}; margin: 0 0 2px 0; }}
.fc-sec .n {{ font-family: {SERIF}; color: {NAVY}; margin-right: 6px; }}

/* Top bar */
.st-key-topbar {{ background: rgba(255,255,255,0.92); border-bottom: 1px solid {LINE}; width: 100vw !important; max-width: 100vw !important;
  margin: 0 0 22px calc(50% - 50vw); padding: 12px calc(50vw - 50%) 10px calc(50vw - 50%); box-sizing: border-box; }}
/* Style blocks and the scroll helper take no space, so the top bar sits at the very top */
[data-testid="stElementContainer"]:has(style) {{ display: none; }}
[data-testid="stElementContainer"]:has([data-testid="stIFrame"]), [data-testid="stElementContainer"]:has(iframe[height="0"]) {{
  position: absolute !important; top: 0; left: 0; width: 1px !important; height: 1px !important; overflow: hidden; opacity: 0; pointer-events: none; }}
.st-key-topbar [data-testid="stHorizontalBlock"] {{ align-items: center; }}
.st-key-topbar [data-testid="stBaseButton-primary"] {{ min-height: 2.5rem; }}
.fc-lockup {{ display: flex; align-items: center; gap: 9px; }}
.fc-lockup .name {{ font-family: 'Archivo', 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 1.28rem; color: {NAVY}; line-height: 1; }}
.fc-lockup .tag {{ font-size: 0.6rem; letter-spacing: 0.08em; color: {BLUE}; margin-top: 2px; }}
[data-testid="stMain"] {{ overflow-x: hidden; }}

/* Step tabs */
.fc-eyebrow {{ font-size: 0.74rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: {NAVY}; margin-bottom: 6px; }}
.fc-steps {{ display: flex; gap: 8px; margin: 2px 0 20px 0; }}
.fc-step {{ flex: 1; font-size: 0.8rem; font-weight: 500; padding: 9px 12px; border-radius: 10px; background: #FFFFFF; color: {MUTED}; border: 1px solid {LINE}; }}
.fc-step.on {{ background: {NAVY}; color: #FFFFFF; border-color: {NAVY}; font-weight: 600; }}
.fc-step.done {{ background: #EEF1F8; color: {NAVY}; border-color: rgba(16,38,95,0.25); }}

/* Welcome */
.fc-hero {{ padding: 26px 0 6px 0; }}
.fc-hero h1 {{ font-family: {SERIF}; font-weight: 600; color: {INK}; font-size: 3.05rem; line-height: 1.08; letter-spacing: -0.02em; margin: 0 0 18px 0; padding: 0; }}
.fc-hero h1 .accent {{ color: {NAVY}; text-decoration: underline; text-decoration-color: rgba(62,155,224,0.45); text-decoration-thickness: 3px; text-underline-offset: 7px; }}
.fc-hero p {{ color: {MUTED}; font-size: 1.12rem; line-height: 1.6; margin: 0 0 6px 0; max-width: 34rem; }}
.fc-promise {{ color: {MUTED}; font-size: 0.86rem; margin-top: 2px; }}
.fc-plancard {{ background: #FFFFFF; border: 1px solid {LINE}; border-radius: 20px; padding: 20px 22px; box-shadow: 0 30px 60px -28px rgba(32,48,77,0.28); margin-top: 26px; }}
.fc-plancard .head {{ display: flex; align-items: center; justify-content: space-between; gap: 8px; padding-bottom: 12px; border-bottom: 1px solid {LINE}; }}
.fc-plancard .title {{ display: flex; align-items: center; gap: 10px; font-weight: 600; color: {INK}; }}
.fc-plancard .icon {{ width: 34px; height: 34px; border-radius: 10px; background: #EEF1F8; display: flex; align-items: center; justify-content: center; }}
.fc-tag {{ font-size: 0.72rem; color: {MUTED}; background: #F3F0E9; border-radius: 8px; padding: 3px 9px; white-space: nowrap; }}
.fc-plancard .lab {{ font-size: 0.7rem; font-weight: 700; letter-spacing: 0.09em; text-transform: uppercase; color: {MUTED}; margin: 14px 0 6px 0; }}
.fc-plancard ul {{ list-style: none; padding: 0; margin: 0; }}
.fc-plancard li {{ font-size: 0.9rem; color: {INK}; margin: 0 0 5px 0; padding-left: 18px; position: relative; }}
.fc-plancard li.dot::before {{ content: ""; position: absolute; left: 3px; top: 8px; width: 6px; height: 6px; border-radius: 50%; background: {NAVY}; }}
.fc-plancard li.tick::before {{ content: "✓"; position: absolute; left: 0; top: 0; font-size: 0.8rem; color: {NAVY}; font-weight: 700; }}
.fc-plancard .quote {{ background: #F7F5F0; border-radius: 12px; padding: 12px 14px; margin-top: 14px; font-size: 0.86rem; color: {INK}; }}
.fc-plancard .quote b {{ display: block; font-size: 0.78rem; margin-bottom: 4px; }}
.fc-howto {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }}
.fc-howto div {{ background: #FFFFFF; border: 1px solid {LINE}; border-radius: 16px; padding: 16px 16px 14px 16px; color: {MUTED}; font-size: 0.88rem; box-shadow: {CARD_SHADOW}; }}
.fc-howto .s {{ display: block; font-size: 0.7rem; font-weight: 700; letter-spacing: 0.09em; color: {NAVY}; margin-bottom: 6px; }}
.fc-howto b {{ display: block; color: {INK}; font-size: 0.98rem; margin-bottom: 4px; }}
.fc-sectionhead {{ display: flex; justify-content: space-between; align-items: baseline; border-top: 1px solid {LINE}; padding-top: 22px; margin: 26px 0 14px 0; }}
.fc-sectionhead .h {{ font-family: {SERIF}; font-weight: 600; font-size: 1.4rem; color: {INK}; }}
.fc-sectionhead span {{ font-size: 0.82rem; color: {MUTED}; }}

/* Cards and notices */
.fc-card {{ background: #FFFFFF; color: {INK}; border: 1px solid {LINE}; border-radius: 18px; padding: 18px 20px; margin-bottom: 12px; box-shadow: {CARD_SHADOW}; }}
.fc-card h3, .fc-card h4 {{ color: {INK}; margin: 0 0 6px 0; padding: 0; }}
.fc-card h4 {{ font-size: 1.02rem; }}
.fc-card p, .fc-card li {{ color: {INK}; font-size: 0.94rem; }}
.fc-card .muted, .muted {{ color: {MUTED}; font-size: 0.85rem; }}
.fc-card a {{ color: {NAVY}; }}
.fc-keep {{ border-radius: 14px; padding: 14px 18px; margin-bottom: 12px; background: #EAF1EE; border: 1px solid #C7DAD2; }}
.fc-keep b, .fc-keep p {{ color: #1F4A44; margin: 0; font-size: 0.95rem; }}
.fc-fiction {{ border-radius: 14px; padding: 12px 16px; margin-bottom: 12px; background: #FBF1E6; border: 1px dashed #D9A16E; color: #6B3A10; font-size: 0.92rem; }}

/* Calibration and room */
.fc-calib {{ background: {PAPER}; border: 1px dashed rgba(16,38,95,0.25); border-radius: 14px; padding: 18px 8px; overflow-x: auto; }}
.fc-idcard {{ border: 3px solid {BLUE}; border-radius: 12px; background: rgba(62,155,224,0.10); margin: 0 auto; display: flex; align-items: center; justify-content: center; color: {NAVY}; font-weight: 600; font-size: 0.85rem; }}
.fc-room {{ background: {PAPER}; border: 1px solid {LINE}; border-radius: 14px; padding: 8px; margin: 6px 0 4px 0; }}
.fc-room svg {{ width: 100%; height: auto; display: block; }}

/* Check */
.fc-chart {{ background: #FFFFFF; border: 1px solid {LINE}; border-radius: 18px; display: flex; align-items: center; justify-content: center; margin: 0 0 10px 0; overflow: auto; box-shadow: {CARD_SHADOW}; }}
.fc-progress {{ display: flex; justify-content: space-between; align-items: baseline; font-size: 0.84rem; color: {MUTED}; margin-bottom: 6px; }}
.fc-progress .count {{ font-family: {MONO}; font-weight: 500; color: {INK}; font-size: 0.95rem; }}
.fc-bar {{ height: 6px; border-radius: 999px; background: #E6E2DA; overflow: hidden; margin-bottom: 16px; }}
.fc-bar > div {{ height: 100%; background: {BLUE}; border-radius: 999px; transition: width 300ms ease; }}
.fc-roles {{ display: grid; grid-template-columns: 1fr 1fr; gap: 0; background: #FFFFFF; border: 1px solid {LINE}; border-radius: 16px; margin-bottom: 14px; box-shadow: {CARD_SHADOW}; }}
.fc-roles div {{ padding: 12px 16px; font-size: 0.86rem; color: {INK}; }}
.fc-roles div + div {{ border-left: 1px solid {LINE}; }}
.fc-roles b {{ display: block; font-size: 0.7rem; letter-spacing: 0.08em; text-transform: uppercase; color: {MUTED}; margin-bottom: 4px; }}
.fc-sizecap {{ text-align: center; font-size: 0.78rem; color: {MUTED}; margin: -2px 0 8px 0; }}
.fc-ask {{ text-align: center; font-weight: 600; color: {INK}; margin: 4px 0 10px 0; }}
.fc-mid {{ height: 3.6rem; display: flex; align-items: center; justify-content: center; border-radius: 12px; background: {PAPER};
  font-family: {MONO}; font-size: 0.78rem; color: {MUTED}; }}
[class*="st-key-ans_"] button, [class*="st-key-prac_"] button, [class*="st-key-dmv_ans_"] button {{ min-height: 3.6rem; background: #FBFAF7 !important; }}
[class*="st-key-ans_"]:not(.st-key-ans_cant_tell) button p, [class*="st-key-prac_"] button p,
[class*="st-key-dmv_ans_"]:not(.st-key-dmv_ans_cant_tell) button p {{ font-size: 1.02rem; font-weight: 600; }}
.st-key-ans_cant_tell button, .st-key-dmv_ans_cant_tell button {{ min-height: 2.75rem; background: #FFFFFF !important; }}

/* Results */
.fc-verdict {{ background: #FFFFFF; border: 1px solid {LINE}; border-radius: 20px; padding: 22px 22px 18px 22px; margin-bottom: 12px; box-shadow: {CARD_SHADOW}; }}
.fc-verdict h2 {{ font-family: {SERIF}; font-weight: 600; font-size: 1.85rem; line-height: 1.18; letter-spacing: -0.01em; margin: 0 0 8px 0; padding: 0; color: {INK}; }}
.fc-verdict p {{ margin: 0 0 6px 0; font-size: 0.98rem; color: {MUTED}; }}
.fc-metrics {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin: 12px 0; }}
.fc-metric {{ background: {PAPER}; border: 1px solid {LINE}; border-radius: 14px; padding: 12px 14px; }}
.fc-metric .v {{ font-family: {MONO}; font-size: 1.3rem; font-weight: 500; color: {INK}; line-height: 1.25; }}
.fc-metric .v small {{ font-size: 0.78rem; color: {MUTED}; }}
.fc-metric .l {{ font-size: 0.76rem; color: {MUTED}; }}
.fc-ladder {{ width: 100%; border-collapse: collapse; border: none !important; margin: 4px 0 0 0; }}
.fc-ladder tr, .fc-ladder td {{ border-left: none !important; border-right: none !important; border-top: none !important; background: transparent; }}
.fc-ladder td {{ padding: 9px 6px; border-bottom: 1px solid #EFECE5; color: {INK}; font-size: 0.9rem; vertical-align: middle; }}
.fc-ladder td.num {{ font-family: {MONO}; }}
.fc-minibar {{ height: 8px; width: 100%; min-width: 80px; background: #ECE8E0; border-radius: 999px; overflow: hidden; }}
.fc-minibar > div {{ height: 100%; background: {NAVY}; border-radius: 999px; }}
.fc-v-on_track {{ background: #EEF6F2; border-color: #C3DFD1; }}
.fc-v-on_track h2, .fc-v-on_track p {{ color: #17503B; }}
.fc-v-close, .fc-v-mixed {{ background: #FCF4E6; border-color: #EDD5A8; }}
.fc-v-close h2, .fc-v-close p, .fc-v-mixed h2, .fc-v-mixed p {{ color: #5C3B00; }}
.fc-rule {{ border-left: 5px solid {BLUE}; }}
.fc-rule .line {{ font-family: {SERIF}; font-size: 1.6rem; font-weight: 600; color: {NAVY}; }}
.fc-also {{ border-style: dashed; box-shadow: none; background: rgba(255,255,255,0.7); }}
.fc-also .eyebrow {{ font-size: 0.72rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: {NAVY}; }}
.fc-badge {{ display: inline-block; padding: 2px 9px; border-radius: 999px; font-size: 0.76rem; font-weight: 600; }}
.fc-b-read {{ background: #DDF1E6; color: #134D38; }}
.fc-b-close {{ background: #FCEBC8; color: #5C3B00; }}
.fc-b-missed {{ background: #E8ECF5; color: {NAVY}; }}
.fc-b-skipped {{ background: #F1F0EC; color: #8A8F9A; }}
.fc-ladder tr.state td {{ background: #EEF1F8; font-weight: 600; }}
.fc-plan ol {{ padding-left: 1.2rem; margin: 6px 0 0 0; }}
.fc-plan li {{ margin-bottom: 8px; }}
.fc-footer {{ font-size: 0.75rem; color: {MUTED}; text-align: center; margin-top: 30px; padding-top: 16px; border-top: 1px solid {LINE}; }}
[data-testid="stToast"] {{ background: {NAVY} !important; color: #FFFFFF !important; border-radius: 999px; }}
[data-testid="stToast"] p {{ color: #FFFFFF !important; }}

/* Keep button rows side by side on phones; let the check's two halves stack */
div[data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap !important; gap: 0.6rem !important; }}
div[data-testid="column"], div[data-testid="stColumn"] {{ min-width: 0 !important; }}
@media (max-width: 640px) {{
  .fc-howto {{ grid-template-columns: repeat(2, 1fr); }}
  .fc-hero h1 {{ font-size: 2.1rem; }}
  .fc-metrics {{ grid-template-columns: 1fr; }}
  .fc-roles {{ grid-template-columns: 1fr; }}
  .fc-roles div + div {{ border-left: none; border-top: 1px solid {LINE}; }}
  .fc-steps .fc-step {{ font-size: 0.7rem; padding: 8px 6px; }}
  .st-key-hero > div > [data-testid="stHorizontalBlock"], .st-key-checkrow > div > [data-testid="stHorizontalBlock"],
  .st-key-hero [data-testid="stHorizontalBlock"]:first-of-type, .st-key-checkrow [data-testid="stHorizontalBlock"]:first-of-type,
  .st-key-lower [data-testid="stHorizontalBlock"]:first-of-type {{ flex-wrap: wrap !important; }}
  .st-key-hero [data-testid="stHorizontalBlock"]:first-of-type > [data-testid="stColumn"],
  .st-key-checkrow [data-testid="stHorizontalBlock"]:first-of-type > [data-testid="stColumn"],
  .st-key-lower [data-testid="stHorizontalBlock"]:first-of-type > [data-testid="stColumn"] {{ flex: 1 1 100% !important; width: 100% !important; }}
  .st-key-topbar [data-testid="stColumn"]:not(:first-child):not(:last-child) {{ display: none; }}
  /* ...but the arrow pad keeps its three columns */
  .st-key-checkrow [data-testid="stColumn"] [data-testid="stHorizontalBlock"] {{ flex-wrap: nowrap !important; }}
  .st-key-checkrow [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {{ flex: 1 1 0 !important; width: auto !important; }}
}}
</style>""")


STEPS = [("setup", "1 · Set up"), ("check", "2 · Check"), ("history", "3 · History"), ("note", "4 · Note")]
PAGE_STEP = {"setup": "setup", "practice": "check", "check": "check", "result": "check",
             "history": "history", "note": "note"}
DMV_STEPS = [("dmv_setup", "1 · Set up"), ("dmv_check", "2 · Check"), ("dmv_result", "3 · Result")]
NAV = [("welcome", "Welcome"), ("setup", "Set up"), ("history", "History"), ("note", "Parent note")]
NAV_ACTIVE = {"welcome": "welcome", "setup": "setup", "practice": "setup", "check": "setup", "result": "setup",
              "history": "history", "note": "note"}


def render_top_bar(page: str):
    """Logo lockup, page links and a standing call to action, as in the React UI."""
    active = NAV_ACTIVE.get(page)
    if active:
        html(f"""<style>.st-key-nav_{active} p {{ font-weight: 600 !important; color: {NAVY} !important;
text-decoration: underline; text-decoration-thickness: 2px; text-underline-offset: 6px; }}</style>""")
    with st.container(key="topbar"):
        cols = st.columns([2.4, 0.95, 0.85, 0.85, 1.05, 2.1], vertical_alignment="center")
        with cols[0]:
            html(f"""<div class="fc-lockup">{focal_logo_svg(32)}<div><div class="name">Focal</div>
<div class="tag">Technologies</div></div></div>""")
        for col, (target, label) in zip(cols[1:5], NAV):
            with col:
                st.button(label, key=f"nav_{target}", type="tertiary", on_click=go, args=(target,))
        with cols[5]:
            if page.startswith("dmv_"):
                st.button("Back to Focal Family", key="nav_cta_family", on_click=go, args=("welcome",), **full_width())
            else:
                st.button("Start a check", key="nav_cta", type="primary", on_click=go, args=("setup",),
                          **full_width())


def render_brand_and_steps(page: str):
    render_top_bar(page)
    if page.startswith("dmv_"):
        steps, active = DMV_STEPS, page
        html('<div class="fc-eyebrow">Also from Focal · DMV vision pre-check</div>')
    else:
        steps, active = STEPS, PAGE_STEP.get(page)
    if active is None:
        return
    pos = [k for k, _ in steps].index(active)
    pills = "".join(
        f'<div class="fc-step {"on" if i == pos else ("done" if i < pos else "")}">{label}{" ✓" if i < pos else ""}</div>'
        for i, (_, label) in enumerate(steps)
    )
    html(f'<div class="fc-steps">{pills}</div>')


def section(number, title: str, hint: str = ""):
    """A numbered section heading inside a card."""
    num = f'<span class="n">{number}.</span>' if number else ""
    html(f'<div class="fc-sec">{num}{title}</div>')
    if hint:
        st.caption(hint)


def room_svg(distance_label: str) -> str:
    """Top-down sketch of the room: screen on a table, child at the floor mark, parent off to the side."""
    short = distance_label.split(" (")[0]
    return f"""<svg viewBox="0 0 640 210" role="img" aria-label="Room layout: child stands {short} from the screen; parent sits to the side">
<rect x="0" y="0" width="640" height="210" rx="12" fill="#FFFFFF"/>
<rect x="34" y="52" width="70" height="96" rx="8" fill="none" stroke="{INK}" stroke-width="1.6"/>
<rect x="88" y="78" width="8" height="44" rx="2" fill="{NAVY}"/>
<text x="69" y="44" text-anchor="middle" font-size="12" fill="{MUTED}">Screen on a table</text>
<line x1="104" y1="100" x2="520" y2="100" stroke="{NAVY}" stroke-width="1.6" stroke-dasharray="6 6"/>
<rect x="240" y="84" width="150" height="32" rx="8" fill="#FFFFFF" stroke="{NAVY}" stroke-width="1.4"/>
<text x="315" y="105" text-anchor="middle" font-size="14" font-weight="600" fill="{NAVY}">{short}</text>
<text x="315" y="72" text-anchor="middle" font-size="11" fill="{MUTED}" letter-spacing="1">CLEAR SIGHTLINE · DON'T BLOCK IT</text>
<circle cx="540" cy="100" r="20" fill="#EEF1F8" stroke="{NAVY}" stroke-width="1.6"/>
<circle cx="540" cy="100" r="8" fill="{NAVY}"/>
<text x="540" y="146" text-anchor="middle" font-size="12" font-weight="600" fill="{INK}">Child at the floor mark</text>
<text x="540" y="162" text-anchor="middle" font-size="11" fill="{MUTED}">points the way the E opens</text>
<circle cx="200" cy="176" r="12" fill="#FFFFFF" stroke="{INK}" stroke-width="1.6"/>
<circle cx="200" cy="176" r="5" fill="{INK}"/>
<line x1="200" y1="164" x2="120" y2="128" stroke="{MUTED}" stroke-width="1.2" stroke-dasharray="3 4"/>
<text x="222" y="174" font-size="12" font-weight="600" fill="{INK}">You sit to the side</text>
<text x="222" y="189" font-size="11" fill="{MUTED}">and tap the arrow your child points to</text>
</svg>"""


def direction_pad(prefix: str, callback, args_for, center: str = ""):
    """Up, left, right and down in a cross, like the React UI. Keys stay prefix + direction."""
    blank = '<div style="height:3.6rem;"></div>'
    for row in (("", "up", ""), ("left", "mid", "right"), ("", "down", "")):
        cols = st.columns(3)
        for col, cell in zip(cols, row):
            with col:
                if cell in DIRECTIONS:
                    st.button(f"{ARROWS[cell]}  {cell.capitalize()}", key=f"{prefix}{cell}", help=cell.capitalize(),
                              on_click=callback, args=args_for(cell), **full_width())
                elif cell == "mid":
                    html(f'<div class="fc-mid">{center}</div>')
                else:
                    html(blank)


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
    ss.setdefault("dmv_items", [])
    ss.setdefault("dmv_idx", 0)
    ss.setdefault("dmv_answers", {})
    ss.setdefault("dmv_attempts", [])
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
        st.session_state.toast = "Check saved to your history"
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
    ss.toast = "Filled with a fictional example, labeled as one"


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
    st.session_state.scroll_count = st.session_state.get("scroll_count", 0) + 1
    # A different script each time, so the browser can't reuse the previous frame without running it.
    # It runs a few times because the new page can finish drawing after the first scroll.
    script = (f"<!-- {page} {st.session_state.scroll_count} -->"
              "<script>const toTop = () => { const d = window.parent.document;"
              "(d.querySelector('[data-testid=\"stMain\"]') || d.querySelector('section.main') || d.body).scrollTo(0, 0);"
              "window.parent.scrollTo(0, 0); };"
              "toTop(); [80, 250, 600].forEach(ms => setTimeout(toTop, ms));</script>")
    if hasattr(st, "iframe"):
        st.iframe(script, height=1)
    else:
        components.html(script, height=0)


def set_reminder(choice: str):
    st.session_state.reminder = choice
    st.session_state.toast = f"Reminder set for {choice.lower()} (simulated)"


def start_dmv_check():
    state = dmv.STATES[st.session_state.d_state]
    st.session_state.dmv_items = dmv.generate_items(dmv.build_test_lines(state["line"]))
    st.session_state.dmv_idx = 0
    st.session_state.dmv_answers = {}
    st.session_state.page = "dmv_check"


def dmv_answer(answer_value: str, expected_idx: int):
    """Records one DMV answer. Ignores stale clicks so a double tap can't answer twice."""
    ss = st.session_state
    if ss.page != "dmv_check" or ss.dmv_idx != expected_idx:
        return
    answers = dict(ss.dmv_answers)
    answers[expected_idx] = answer_value
    ss.dmv_answers = answers
    nxt = dmv.next_item_index(ss.dmv_items, answers, expected_idx)
    if nxt is None:
        attempt = dmv.score_attempt(ss.dmv_items, answers)
        ss.dmv_attempts = ss.dmv_attempts + [attempt]
        ss.page = "dmv_result"
    else:
        ss.dmv_idx = nxt


def start_dmv_over():
    st.session_state.dmv_attempts = []
    st.session_state.dmv_items = []
    st.session_state.page = "dmv_setup"


def reset_demo():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_session_state()


# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
PLAN_ICON = (f'<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="{NAVY}" stroke-width="1.8" '
             'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 '
             '2-2V8z"/><path d="M14 3v5h5"/><path d="M9 13h6M9 17h4"/></svg>')


def page_welcome():
    # The welcome page is wider, with a soft brand-colored glow behind the example card.
    html(f"""<style>.block-container, .stMainBlockContainer {{ max-width: 1120px !important; }}
.stApp {{ background: radial-gradient(42rem 30rem at 82% 14%, rgba(62,155,224,0.13), transparent 70%),
radial-gradient(34rem 26rem at 96% 62%, rgba(242,205,174,0.38), transparent 70%), {PAPER} !important; }}</style>""")
    render_brand_and_steps("welcome")
    with st.container(key="hero"):
        left, right = st.columns([1.2, 1], gap="large")
        with left:
            html("""<div class="fc-hero"><div class="fc-eyebrow">For parents of children 4–10</div>
<h1>Got a school vision letter?<br><span class="accent">Make the next step easy.</span></h1>
<p>Do a short check together at home, see how it changes over time, and leave with a note
ready for the school nurse or eye doctor.</p></div>""")
            b1, b2 = st.columns([1.15, 1])
            with b1:
                st.button("Start a check together  →", type="primary", key="btn_start", on_click=go, args=("setup",),
                          **full_width())
            with b2:
                st.button("Prepare a parent note", key="btn_welcome_note", on_click=go, args=("note",), **full_width())
            html('<div class="fc-promise">Free for families · No account · No camera · Not a diagnosis: a prepared next step</div>')
            st.button("See saved history", key="btn_welcome_history", type="tertiary", on_click=go, args=("history",))
        with right:
            html(f"""<div class="fc-plancard"><div class="head"><div class="title"><div class="icon">{PLAN_ICON}</div>
Your next-step plan</div><span class="fc-tag">Illustrative example</span></div>
<div class="lab">What you noticed</div><ul>
<li class="dot">A school vision letter came home</li>
<li class="dot">Moves closer to the TV or tablet</li></ul>
<div class="lab">Your plan</div><ul>
<li class="tick">Book an eye exam and bring the school letter</li>
<li class="tick">Tell the school nurse when it's booked</li></ul>
<div class="quote"><b>Ready-to-send note</b>"We're booking an eye exam after the school's vision letter. At home,
our practice check matched 10 of 12 directions; the smallest letters were the hardest."</div></div>""")

    html("""<div class="fc-sectionhead"><div class="h">How Focal Family works</div><span>Set up → check together → compare → send a note</span></div>
<div class="fc-howto">
<div><span class="s">STEP 1</span><b>Set up together</b>Size the letters to your screen with any bank card, and measure the distance. About a minute.</div>
<div><span class="s">STEP 2</span><b>Check together</b>One practice letter, then 12 quick ones. Your child points; you tap.</div>
<div><span class="s">STEP 3</span><b>Compare over time</b>Save each check and see 7, 30 and 90-day changes with the same setup.</div>
<div><span class="s">STEP 4</span><b>Send a note</b>Leave with a plan and a message ready for the school nurse or eye doctor.</div>
</div>""")

    with st.container(key="lower"):
        left, right = st.columns(2, gap="large")
        with left:
            html("""<div class="fc-card fc-also" style="margin-top:22px;"><div class="eyebrow">Also from Focal</div>
<h4>Getting a driver's license in the family?</h4>
<p>A teen's learner's permit or your own renewal: check against your state's real DMV vision line
before you wait in line.</p></div>""")
            st.button("Try the DMV pre-check", key="btn_dmv", on_click=start_dmv_over)
        with right:
            html('<div style="height:22px;"></div>')
            page_welcome_expanders()
    render_footer()


def page_welcome_expanders():
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


def render_calibration(number: int):
    """Card calibration shared by the family check and the DMV pre-check (same setting)."""
    section(number, "Size the letters to your screen",
            "Hold any bank card or ID flat against the screen. Slide until the blue box is exactly as wide as the card.")
    card_px = st.session_state.w_card
    html(f"""<div class="fc-calib"><div class="fc-idcard" style="width:{card_px}px; height:{card_px * 53.98 / 85.6:.0f}px;">Match your card here</div></div>""")
    st.slider("Card width", min_value=160, max_value=600, key="w_card", label_visibility="collapsed")


def page_setup():
    render_brand_and_steps("setup")
    html('<div class="fc-eyebrow">Guided setup · about a minute</div>')
    st.markdown("### Set up your check together")

    with st.container(key="card_who"):
        section(1, "Who's checking today?", "Use a label, not a name. Nothing identifies your child.")
        left, right = st.columns([1, 1.3])
        with left:
            st.selectbox("Child label", PROFILES, key="w_child")
        with right:
            st.radio("Age group", fam.AGE_GROUPS, key="w_age", horizontal=True)
        st.radio("What brings you here?", fam.REASONS, key="w_reason", horizontal=True)
        if fam.concern_already_raised(st.session_state.w_reason):
            html("""<div class="fc-keep" style="margin:4px 0 0 0;"><p><b>Good to know.</b> We'll keep that follow-up
front and center: this check never replaces it.</p></div>""")

    with st.container(key="card_eyes"):
        section(2, "Which eyes, and with glasses?")
        st.radio("Eyes for this check", EYES, key="w_eye", horizontal=True)
        st.radio("Glasses or contacts", GLASSES, key="w_glasses", horizontal=True)

    with st.container(key="card_screen"):
        render_calibration(3)
        st.selectbox("Which screen is this?", SCREENS, key="w_screen")
        st.caption("Keep the same screen and browser zoom next time, so checks can be compared.")

    with st.container(key="card_room"):
        section(4, "Set up the room", "Your child stands at the measured distance and points. You sit to the side and tap.")
        st.radio("Distance", list(DISTANCES), key="w_distance", horizontal=True, label_visibility="collapsed")
        html(f'<div class="fc-room">{room_svg(st.session_state.w_distance)}</div>')

    with st.container(key="card_ready"):
        section(5, "Ready to begin", "A good setup is what makes a comparison fair.")
        # A list, not a generator: every box must be drawn even when an earlier one is unticked.
        ready = all([st.checkbox(label, key=f"chk_{i}") for i, label in enumerate(SETUP_CHECKLIST)])
        st.button("Start practice  →", type="primary", key="btn_begin", on_click=start_check, disabled=not ready,
                  **full_width())
        if not ready:
            st.caption("Tick all four boxes to start.")
    st.button("← Back", key="btn_setup_back", on_click=go, args=("welcome",))
    render_footer()


def page_practice():
    render_brand_and_steps("practice")
    html('<div class="fc-eyebrow">Practice · doesn\'t count</div>')
    st.markdown("### Practice together")
    st.write("Ask your child to point the way the arms of the E point. Then tap the same arrow.")
    with st.container(key="checkrow"):
        left, right = st.columns(2, gap="large")
        with left:
            html(f'<div class="fc-chart" style="height:260px;">{tumbling_e_svg("right", 110)}</div>')
            html('<div class="fc-sizecap">A big practice letter, sized for teaching, not testing</div>')
        with right:
            html('<div class="fc-ask">Which way did your child point?</div>')
            direction_pad("prac_", practice, lambda d: (d,), "Practice")
    if st.session_state.practice_miss:
        st.info("Not quite. This one points right →. Try again together.")
    st.caption("The real check starts after one correct practice answer.")
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
    box_h = max(260, biggest + 70)
    distance = f"{setup['distance_mm'] / 1000:g} m"
    html(f"""<div class="fc-progress"><span>{setup['profile']} · {setup['eye']} · {setup['glasses']} · {distance}</span>
<span class="count">Letter {index + 1} of {total}</span></div>
<div class="fc-bar"><div style="width:{100 * index / total:.0f}%;"></div></div>""")
    html(f"""<div class="fc-roles"><div><b>Your child</b>Stays at the {distance} mark and points the way the E opens.</div>
<div><b>You</b>Sit to the side, tap the direction they point, and don't hint.</div></div>""")
    with st.container(key="checkrow"):
        left, right = st.columns(2, gap="large")
        with left:
            html(f'<div class="fc-chart" style="height:{box_h:.0f}px;">{tumbling_e_svg(trial["target"], size_px(trial["level"], setup))}</div>')
            html(f'<div class="fc-sizecap">{SIZE_NAMES[trial["level"]]} letters · drawn to size for your screen and distance</div>')
        with right:
            html('<div class="fc-ask">Which way did your child point?</div>')
            direction_pad("ans_", answer, lambda d: (index, d), f"{index + 1} / {total}")
            st.button("Can't tell", key="ans_cant_tell", on_click=answer, args=(index, "cant_tell"), **full_width())
            st.caption("Not sure? Tap \"Can't tell\". A lucky guess only hides what you want to see.")
    left, right = st.columns(2)
    with left:
        st.button("Pause", key="btn_pause", on_click=set_paused, args=(True,), **full_width())
    with right:
        st.button("Discard", key="btn_discard", on_click=discard_check, **full_width())
    render_footer()


def size_rows_html(summary):
    rows = ""
    for level, row in zip(LEVELS, summary["levels"]):
        pct = 100 * row["Correct"] / row["Trials"]
        rows += (f'<tr><td><b>{SIZE_NAMES[level]}</b> <span class="muted">({row["Task size"].split()[0]} size)</span></td>'
                 f'<td style="width:45%;"><div class="fc-minibar"><div style="width:{pct:.0f}%;"></div></div></td>'
                 f'<td class="num" style="text-align:right; white-space:nowrap;">{row["Correct"]} of {row["Trials"]}</td></tr>')
    return f'<table class="fc-ladder">{rows}</table>'


def page_result():
    render_brand_and_steps("result")
    check = st.session_state.check
    summary = summarize(check)
    child = check["setup"]["profile"]
    sizes = " · ".join(f"{SIZE_NAMES[level][:3] if level == 40 else SIZE_NAMES[level]} {row['Correct']}/{row['Trials']}"
                       for level, row in zip(LEVELS, summary["levels"]))
    cant_tell = sum(r["choice"] == "cant_tell" for r in check["responses"])
    html(f"""<div class="fc-verdict"><div class="fc-eyebrow">Check complete · a record, not a verdict</div>
<h2>{child} matched {summary['correct']} of {summary['total']} directions</h2>
<p>Here's how today's practice check went. Save it to see how it compares over time, then turn it into a note.</p>
<div class="fc-metrics">
<div class="fc-metric"><div class="l">Letters shown</div><div class="v">{summary['total']} of {summary['total']}</div></div>
<div class="fc-metric"><div class="l">Directions matched</div><div class="v">{summary['correct']} <small>({cant_tell} can't tell)</small></div></div>
<div class="fc-metric"><div class="l">By size</div><div class="v" style="font-size:0.95rem;">{sizes}</div></div>
</div></div>""")

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
    html('<div class="fc-eyebrow">Results over time</div>')
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
        chart = alt.Chart(frame).mark_line(point=alt.OverlayMarkDef(size=70, filled=True), color=NAVY, strokeWidth=3).encode(
            x=alt.X("Date (UTC):T", title=None, scale=alt.Scale(type="utc")),
            y=alt.Y("Letters matched (%):Q", scale=alt.Scale(domain=[0, 100]), title="Letters matched (%)"),
            tooltip=[alt.Tooltip("Date (UTC):T", format="%b %d, %Y"), "Letters matched (%):Q"],
        ).properties(height=220)
        with st.container(key="card_chart"):
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
    html('<div class="fc-eyebrow">Parent note · ready to send</div>')
    st.markdown("### Make the next step easy")
    if ss.note_fictional:
        html("""<div class="fc-fiction"><b>Fictional example.</b> This note is made up for a demo. Clear it to write your own.</div>""")
        st.button("Clear the example", key="btn_clear_example", on_click=clear_fictional_note)
    else:
        st.caption("Your answers stay on this page until you download them.")

    if fam.concern_already_raised(ss.w_reason):
        html("""<div class="fc-keep"><p><b>Keep the follow-up you were asked for.</b> This note helps you act on it.
Nothing here replaces it.</p></div>""")

    with st.container(key="card_noticed"):
        section(1, "What have you noticed?", "Tick what you've seen at home or school. Only what you choose goes in the note.")
        for i, observation in enumerate(fam.OBSERVATIONS):
            st.checkbox(observation, key=f"n_obs_{i}")
        st.selectbox("When did you notice it?", fam.TIMING, key="n_timing")
        st.text_area("Anything else? (optional, no names please)", key="n_notes", max_chars=600, height=90)

    with st.container(key="card_next"):
        section(2, "Your next step")
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

    with st.container(key="card_message"):
        section(3, "Your message", "It writes itself from your answers until you edit it.")
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
# DMV pre-check (secondary option, from Prototype C)
# -----------------------------------------------------------------------------
def page_dmv_setup():
    render_brand_and_steps("dmv_setup")
    ss = st.session_state
    st.markdown("### Will you pass the DMV eye test?")
    st.caption("For a teen getting a learner's permit, or a parent renewing a license. "
               "This is a practice check against your state's real line, not an official result.")

    with st.container(key="card_dmv_state"):
        section(1, "Which state is the license from?")
        st.selectbox("State", list(dmv.STATES), key="d_state", label_visibility="collapsed")
    state = dmv.STATES[ss.d_state]
    source = (
        f'<p class="muted">Source: <a href="{state["source_url"]}" target="_blank">{state["source_name"]}</a> · '
        f'checked {dmv.RULES_CHECKED}. Rules can change; the DMV has the final word.</p>'
        if state["source_url"] else '<p class="muted">We only have exact rules for a few states in this prototype.</p>'
    )
    html(f"""<div class="fc-card fc-rule"><div class="muted">The line to read</div>
<div class="line">20/{state['line']}</div><p>{state['rule']} {state['glasses']}</p>{source}</div>""")

    with st.container(key="card_dmv_glasses"):
        section(2, "Glasses or contacts for driving?")
        st.radio("Glasses", dmv.GLASSES_OPTIONS, key="d_glasses", label_visibility="collapsed")

    with st.container(key="card_dmv_screen"):
        render_calibration(3)

    with st.container(key="card_dmv_room"):
        section(4, "How far from the screen?")
        st.radio("DMV distance", list(DISTANCES), key="w_distance", horizontal=True, label_visibility="collapsed")

    with st.container(key="card_dmv_ready"):
        section(5, "Before you start")
        ready = all([st.checkbox(label, key=f"dchk_{i}") for i, label in enumerate(DMV_CHECKLIST)])
        st.button("Start the DMV check  →", type="primary", key="btn_dmv_begin", on_click=start_dmv_check,
                  disabled=not ready, **full_width())
    st.button("← Back to Focal Family", key="btn_dmv_home", on_click=go, args=("welcome",))
    render_footer()


def page_dmv_check():
    render_brand_and_steps("dmv_check")
    ss = st.session_state
    items, idx, answers = ss.dmv_items, ss.dmv_idx, ss.dmv_answers
    item = items[idx]
    distance_mm = DISTANCES[ss.w_distance]
    size = dmv.letter_height_px(item["denominator"], distance_mm, ss.w_card)
    biggest = max(dmv.letter_height_px(it["denominator"], distance_mm, ss.w_card) for it in items)

    state_idx = [i for i, it in enumerate(items) if it["role"] == "state line"]
    state_done = all(i in answers for i in state_idx)
    total = sum(1 for i, it in enumerate(items)
                if it["role"] != "margin" or not state_done or dmv.should_show_item(items, answers, i))
    html(f"""<div class="fc-progress"><span>Letters get smaller as you go</span>
<span class="count">Letter {len(answers) + 1} of {total}</span></div>
<div class="fc-bar"><div style="width:{100 * len(answers) / max(total, 1):.0f}%;"></div></div>""")
    with st.container(key="checkrow"):
        left, right = st.columns(2, gap="large")
        with left:
            html(f'<div class="fc-chart" style="height:{max(260, biggest + 70):.0f}px;">{tumbling_e_svg(item["direction"], size)}</div>')
            html(f'<div class="fc-sizecap">20/{item["denominator"]} line · drawn to size for your screen and distance</div>')
        with right:
            html('<div class="fc-ask">Which way do the arms of the E point?</div>')
            direction_pad("dmv_ans_", dmv_answer, lambda d: (d, idx), f"{len(answers) + 1} / {total}")
            st.button("Can't tell", key="dmv_ans_cant_tell", on_click=dmv_answer, args=(dmv.CANT_TELL, idx), **full_width())
            st.caption("Not sure? Tap \"Can't tell\". A guess that happens to be right only fools you.")
    st.button("Stop and start over", key="btn_dmv_stop", on_click=start_dmv_over)
    render_footer()


def dmv_ladder_html(attempt, possessive):
    labels = {"read": "Read", "close": "Too close to call", "missed": "Not read", "skipped": "Not needed"}
    rows = ""
    for line in attempt["lines"]:
        is_state = line["role"] == "state line"
        note = f" · {possessive} line" if is_state else ""
        score = f"{line['correct']} of {line['shown']}" if line["shown"] else "-"
        rows += (f'<tr class="{"state" if is_state else ""}"><td>20/{line["denominator"]}{note}</td><td>{score}</td>'
                 f'<td style="text-align:right;"><span class="fc-badge fc-b-{line["status"]}">{labels[line["status"]]}</span></td></tr>')
    return f'<table class="fc-ladder">{rows}</table>'


def page_dmv_result():
    render_brand_and_steps("dmv_result")
    ss = st.session_state
    attempts = ss.dmv_attempts
    latest = attempts[-1]
    overall = dmv.overall_result(attempts)
    verdict = overall["verdict"]
    state = dmv.STATES[ss.d_state]
    possessive, line = state["possessive"], f"20/{state['line']}"
    score = f"{latest['state_correct']} of {latest['state_total']} letters"

    if verdict == "on_track":
        title = f"On track for {possessive} vision screening"
        body = f"You read the {line} line, {possessive} line: {score}."
        body += (" You also read the smaller line below it." if latest["margin_read"]
                 else " You're just over the line, so there isn't much room to spare.")
    elif verdict == "close":
        title = "Right at the line"
        body = f"{score} at the {line} line. That's too close to call: lighting, distance or a tired day could tip it."
    elif verdict == "not_yet":
        title = f"Might not pass {possessive} screening yet"
        body = f"{score} at the {line} line. Better to find out here than at the counter. Often it just means glasses."
    else:
        title = "The two checks didn't agree"
        body = "One cleared the line and one didn't. We won't keep the better one: let an eye doctor settle it."
    if overall["consistency"] == "consistent":
        body += " Both checks agreed."
    html(f'<div class="fc-verdict fc-v-{verdict}"><h2>{title}</h2><p>{body}</p></div>')
    html(f"""<div class="fc-card"><h4>What you read</h4>{dmv_ladder_html(latest, possessive)}
<p class="muted" style="margin-top:8px;">Both eyes together · {ss.w_distance.split(' (')[0]} ·
{'with' if ss.d_glasses == dmv.GLASSES_OPTIONS[1] else 'without'} glasses or contacts</p></div>""")

    if verdict == "on_track":
        html("""<div class="fc-card fc-plan"><h4>Next step: go to the DMV as planned</h4><ol>
<li><b>Expect a quick screening.</b> The DMV still tests you at the counter.</li>
<li><b>Night driving feels blurry?</b> This doesn't test glare or night vision. An eye exam is still worth it.</li>
</ol><p class="muted">On track for the DMV line doesn't mean eyes are fine overall. It doesn't replace an eye exam.</p></div>""")
    else:
        html(f"""<div class="fc-card fc-plan"><h4>Next step: see an eye doctor before the DMV</h4><ol>
<li><b>Find an eye exam.</b> <a href="https://www.google.com/maps/search/optometrist+near+me" target="_blank">Open a map of optometrists near you</a>.</li>
<li><b>Know the cost before you book.</b> Ask for the price, and check the family insurance card or app for vision coverage.</li>
<li><b>What the DMV needs.</b> {state['if_missed']} {state['bring']}</li>
</ol></div>""")
        st.markdown("**Remind me to book an eye exam**")
        rcols = st.columns(len(fam.REMINDERS))
        for col, choice in zip(rcols, fam.REMINDERS):
            with col:
                st.button(choice, key=f"btn_dmv_remind_{choice}", on_click=set_reminder, args=(choice,), **full_width())
        if ss.reminder:
            st.success(f"Reminder set for {ss.reminder.lower()}. (Prototype: no reminder is actually sent.)")

    with st.expander("Copy a summary for the family or an eye doctor"):
        st.code(dmv.build_summary_text(ss.d_state, attempts, overall, ss.d_glasses, ss.w_distance,
                                       datetime.now().strftime("%b %d, %Y")), language=None)
    with st.expander("Limits of this check"):
        st.markdown(
            "- A practice check, not an eye exam or an official DMV result.\n"
            "- Tests both eyes together. Many DMV machines also test each eye.\n"
            "- Doesn't test side vision, color, glare or night vision.\n"
            f"- State rules summarize official sources, checked {dmv.RULES_CHECKED}."
        )
    if verdict != "on_track" and len(attempts) < 2:
        st.caption("Not sure the setup was right? Take it once more. Both results are shown; we don't keep the better one.")
        st.button("Retake the check", key="btn_dmv_retake", on_click=go, args=("dmv_setup",), **full_width())
    left, right = st.columns(2)
    with left:
        st.button("← Focal Family home", key="btn_dmv_result_home", on_click=go, args=("welcome",), **full_width())
    with right:
        st.button("New DMV check", key="btn_dmv_new", on_click=start_dmv_over, **full_width())
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
    if page == "dmv_check" and not st.session_state.dmv_items:
        page = "dmv_setup"
    if page == "dmv_result" and not st.session_state.dmv_attempts:
        page = "dmv_setup"

    scroll_to_top_on_page_change(page)
    {
        "welcome": page_welcome,
        "setup": page_setup,
        "practice": page_practice,
        "check": page_check,
        "result": page_result,
        "history": page_history,
        "note": page_note,
        "dmv_setup": page_dmv_setup,
        "dmv_check": page_dmv_check,
        "dmv_result": page_dmv_result,
    }[page]()
    message = st.session_state.pop("toast", None)
    if message:
        st.toast(message, icon=":material/check_circle:")


if __name__ == "__main__":
    main()
