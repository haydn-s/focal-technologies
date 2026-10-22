"""
Focal Monitor - Prototype A
Course: Duke University MENG 570 (Product Management)
Target Persona: Riley (Adult who wears glasses/contacts and notices possible vision changes)
Hypothesis: Adults who suspect their vision is changing will find ongoing vision tracking
            more useful than receiving a single test result.

Technology: Streamlit + Pandas + Altair
Author: Product Prototyping Specialist
"""

import random
import json
import inspect
from datetime import datetime
import streamlit as st
import pandas as pd
import altair as alt

# Helper for responsive widget width across Streamlit versions without deprecation warnings
_HAS_ST_WIDTH = "width" in inspect.signature(st.button).parameters

def full_width():
    """Returns responsive width argument compatible across Streamlit versions without deprecation warnings."""
    return {"width": "stretch"} if _HAS_ST_WIDTH else {"use_container_width": True}


# -----------------------------------------------------------------------------
# Constant Data & Demo Specifications
# -----------------------------------------------------------------------------
DIRECTIONS = ["up", "right", "down", "left"]
DIRECTION_LABELS = {
    "up": "⬆️ Up",
    "right": "➡️ Right",
    "down": "⬇️ Down",
    "left": "⬅️ Left"
}

# 8 Tumbling-E sizes in px (illustrative dynamic difficulty scaling)
DEMO_SIZES = [130, 110, 95, 80, 68, 58, 48, 40]

# Product-demo mapping from the eight progressively smaller prompts to a familiar
# visual-acuity result. The UI intentionally presents the result, not quiz points.
DEMO_VISION_RESULTS = {
    0: {"acuity": "20/200", "status": "Significantly reduced vision", "message": "Visual clarity was limited at the larger sizes."},
    1: {"acuity": "20/160", "status": "Significantly reduced vision", "message": "Visual clarity was limited at the larger sizes."},
    2: {"acuity": "20/100", "status": "Reduced vision", "message": "Visual clarity decreased early in the check."},
    3: {"acuity": "20/70", "status": "Reduced vision", "message": "Visual clarity decreased before the smaller sizes."},
    4: {"acuity": "20/50", "status": "Moderately reduced vision", "message": "Some of the smaller shapes were difficult to identify."},
    5: {"acuity": "20/40", "status": "Mildly reduced vision", "message": "Visual clarity was good through the mid-size shapes."},
    6: {"acuity": "20/30", "status": "Slightly reduced vision", "message": "Visual clarity remained strong through most sizes."},
    7: {"acuity": "20/25", "status": "Near-normal vision", "message": "Visual clarity was strong through the smaller sizes."},
    8: {"acuity": "20/20", "status": "Normal vision", "message": "Visual clarity remained strong through the smallest size."},
}
ACUITY_ORDER = ["20/20", "20/25", "20/30", "20/40", "20/50", "20/70", "20/100", "20/160", "20/200"]

# Fictional example baseline history representing persona "Riley" over 7 previous checks
FICTIONAL_RECORDS = [
    {"Date": "2026-09-03", "Session": "Week 1", "Correct": 8, "Total": 8, "Accuracy": 100.0, "Type": "Illustrative Demo Data", "Notes": "Initial baseline check with contacts"},
    {"Date": "2026-09-10", "Session": "Week 2", "Correct": 7, "Total": 8, "Accuracy": 87.5, "Type": "Illustrative Demo Data", "Notes": "Routine check; morning lighting"},
    {"Date": "2026-09-17", "Session": "Week 3", "Correct": 8, "Total": 8, "Accuracy": 100.0, "Type": "Illustrative Demo Data", "Notes": "Comfortable screen distance"},
    {"Date": "2026-09-24", "Session": "Week 4", "Correct": 7, "Total": 8, "Accuracy": 87.5, "Type": "Illustrative Demo Data", "Notes": "Late afternoon check"},
    {"Date": "2026-10-01", "Session": "Week 5", "Correct": 6, "Total": 8, "Accuracy": 75.0, "Type": "Illustrative Demo Data", "Notes": "Noticed end-of-day eye strain"},
    {"Date": "2026-10-08", "Session": "Week 6", "Correct": 7, "Total": 8, "Accuracy": 87.5, "Type": "Illustrative Demo Data", "Notes": "Consistent with baseline"},
    {"Date": "2026-10-15", "Session": "Week 7", "Correct": 7, "Total": 8, "Accuracy": 87.5, "Type": "Illustrative Demo Data", "Notes": "Prior week check"}
]


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------
def generate_questions():
    """Generates 8 randomized Tumbling E questions with decreasing sizes."""
    orientations = [random.choice(DIRECTIONS) for _ in range(8)]
    # Ensure directional variety across the 8 items
    missing = set(DIRECTIONS) - set(orientations)
    for idx, d in enumerate(missing):
        orientations[idx] = d
    random.shuffle(orientations)
    
    questions = []
    for i in range(8):
        questions.append({
            "id": i + 1,
            "direction": orientations[i],
            "size_px": DEMO_SIZES[i]
        })
    return questions


def get_demo_vision_result(correct_count: int, total_questions: int = 8) -> dict:
    """Translates demo performance into the visual-acuity result shown by the prototype."""
    if type(correct_count) is not int or type(total_questions) is not int or total_questions <= 0:
        raise ValueError("correct_count and total_questions must be valid integers")

    bounded_correct = min(max(correct_count, 0), total_questions)
    mapped_level = round((bounded_correct / total_questions) * 8)
    return DEMO_VISION_RESULTS[mapped_level].copy()


def render_tumbling_e_svg(direction: str, size_px: int) -> str:
    """
    Renders an SVG string of a standard 5x5 Tumbling E optotype rotated in the given direction.
    - 'right': base orientation (arms point to the right)
    - 'down': 90 deg clockwise (arms point down)
    - 'left': 180 deg (arms point to the left)
    - 'up': 270 deg (arms point up)

    Accessibility Note: Uses a non-disclosing aria-label to prevent leaking answers to assistive tools,
    while storing data-direction for internal DOM testing verification.
    """
    rotation_angles = {
        "right": 0,
        "down": 90,
        "left": 180,
        "up": 270
    }
    angle = rotation_angles.get(direction.lower(), 0)
    
    svg = f"""<div style="display:flex; justify-content:center; align-items:center; width:100%; min-height:{max(size_px + 20, 160)}px;" data-direction="{direction}">
<svg width="{size_px}" height="{size_px}" viewBox="0 0 50 50" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Visual Tumbling E demonstration optotype">
<g transform="rotate({angle} 25 25)">
<!-- Snellen 5x5 grid Tumbling E: Left vertical spine and 3 horizontal bars -->
<rect x="0" y="0" width="10" height="50" fill="#0F172A" />
<rect x="10" y="0" width="40" height="10" fill="#0F172A" />
<rect x="10" y="20" width="40" height="10" fill="#0F172A" />
<rect x="10" y="40" width="40" height="10" fill="#0F172A" />
</g>
</svg>
</div>"""
    return svg


def initialize_session_state():
    """Initializes all necessary session state variables."""
    if "step" not in st.session_state:
        st.session_state.step = "welcome"
    if "nav_jump_select" not in st.session_state:
        st.session_state.nav_jump_select = "welcome"
    if "questions" not in st.session_state:
        st.session_state.questions = generate_questions()
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0
    if "answers" not in st.session_state:
        st.session_state.answers = []
    if "submitted_feedback" not in st.session_state:
        st.session_state.submitted_feedback = None
    if "feedback_locked" not in st.session_state:
        st.session_state.feedback_locked = False
    if "completed_at" not in st.session_state:
        st.session_state.completed_at = None
    if "comparison_order_assigned" not in st.session_state:
        st.session_state.comparison_order_assigned = False
    if "comparison_view_order" not in st.session_state:
        st.session_state.comparison_view_order = "trend_first"
    if "initial_assigned_order" not in st.session_state:
        st.session_state.initial_assigned_order = None
    if "assignment_source" not in st.session_state:
        st.session_state.assignment_source = "default"
    if "active_comparison_view" not in st.session_state:
        st.session_state.active_comparison_view = "Experience B: Trend Tracking"
    if "comparison_view_selector" not in st.session_state:
        st.session_state.comparison_view_selector = "Experience B: Trend Tracking"
    if "views_visited" not in st.session_state:
        st.session_state.views_visited = []


def navigate_to(new_step: str):
    """Programmatically updates the active page and keeps the sidebar in sync."""
    st.session_state.step = new_step
    st.session_state.nav_jump_select = new_step


def set_active_view(view_name: str):
    """Updates the active comparison view and synchronizes widget state."""
    st.session_state.active_comparison_view = view_name
    st.session_state.comparison_view_selector = view_name


def proceed_to_comparison():
    """Transitions from Step 3 to Step 4, assigning comparison order once per evaluation."""
    if not st.session_state.get("comparison_order_assigned", False):
        order = random.choice(["single_first", "trend_first"])
        st.session_state.comparison_view_order = order
        st.session_state.initial_assigned_order = order
        initial_view = (
            "Experience A: Single Result" if order == "single_first" else "Experience B: Trend Tracking"
        )
        st.session_state.active_comparison_view = initial_view
        st.session_state.comparison_view_selector = initial_view
        st.session_state.comparison_order_assigned = True
        st.session_state.assignment_source = "participant_randomized"
    
    st.session_state.step = "vision_history"
    st.session_state.nav_jump_select = "vision_history"


def reset_demo():
    """Resets the demo state to initial welcome screen with fresh randomized questions."""
    st.session_state.step = "welcome"
    st.session_state.nav_jump_select = "welcome"
    st.session_state.questions = generate_questions()
    st.session_state.current_question_index = 0
    st.session_state.answers = []
    st.session_state.submitted_feedback = None
    st.session_state.feedback_locked = False
    st.session_state.completed_at = None
    st.session_state.comparison_order_assigned = False
    st.session_state.comparison_view_order = "trend_first"
    st.session_state.initial_assigned_order = None
    st.session_state.assignment_source = "default"
    st.session_state.active_comparison_view = "Experience B: Trend Tracking"
    st.session_state.views_visited = []
    if "comparison_view_selector" in st.session_state:
        st.session_state.comparison_view_selector = "Experience B: Trend Tracking"


def start_vision_check():
    """Starts the vision check from question 1 for a new evaluation."""
    st.session_state.current_question_index = 0
    st.session_state.answers = []
    st.session_state.completed_at = None
    st.session_state.step = "vision_check"
    st.session_state.nav_jump_select = "vision_check"
    st.session_state.submitted_feedback = None
    st.session_state.feedback_locked = False
    st.session_state.comparison_order_assigned = False
    st.session_state.comparison_view_order = "trend_first"
    st.session_state.initial_assigned_order = None
    st.session_state.assignment_source = "default"
    st.session_state.views_visited = []


COMPLETION_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"


def parse_completion_timestamp(timestamp_val):
    """
    Parses a completion timestamp strictly against '%Y-%m-%d %H:%M'.
    Returns datetime object if valid, None otherwise.
    """
    if not isinstance(timestamp_val, str) or not timestamp_val.strip():
        return None
    try:
        return datetime.strptime(timestamp_val.strip(), COMPLETION_TIMESTAMP_FORMAT)
    except (ValueError, TypeError):
        return None


def is_valid_partial_session(answers, questions=None) -> bool:
    """
    Validates whether a session contains a valid, uncorrupted partial test progression (1 to 7 answers).

    Requirements:
    - answers must be a list with length between 1 and 7 (inclusive).
    - Every answer must be a dict containing all required schema keys:
        * question_num (exact int 1..7, not bool)
        * target_direction in DIRECTIONS
        * user_response in DIRECTIONS
        * is_correct (exact bool) matching (user_response == target_direction)
        * size_px (exact positive int, not bool)
    - question_nums must be contiguous unique integers from 1 to len(answers).
    """
    if not isinstance(answers, list):
        return False

    ans_count = len(answers)
    if ans_count < 1 or ans_count >= 8:
        return False

    expected_q_nums = list(range(1, ans_count + 1))
    seen_q_nums = []

    for a in answers:
        if not isinstance(a, dict):
            return False
        required_keys = {"question_num", "target_direction", "user_response", "is_correct", "size_px"}
        if not required_keys.issubset(a.keys()):
            return False

        q_num = a["question_num"]
        if type(q_num) is not int or q_num < 1 or q_num > 8:
            return False
        seen_q_nums.append(q_num)

        target = a["target_direction"]
        user_resp = a["user_response"]
        if target not in DIRECTIONS or user_resp not in DIRECTIONS:
            return False

        if type(a["is_correct"]) is not bool or a["is_correct"] != (user_resp == target):
            return False

        if type(a["size_px"]) is not int or a["size_px"] <= 0:
            return False

    return seen_q_nums == expected_q_nums


def is_valid_completed_session(answers, completed_at, questions=None) -> bool:
    """
    Strictly validates whether a session represents a completed, uncorrupted vision check.

    Requirements:
    - completed_at must parse strictly as '%Y-%m-%d %H:%M'.
    - answers must be a list of exactly 8 question response dictionaries.
    - Question IDs must be exact integers 1 through 8 (explicitly excluding booleans).
    - Each record must match the application question schema:
        * question_num (exact int 1..8, not bool)
        * target_direction in DIRECTIONS
        * user_response in DIRECTIONS
        * is_correct (exact bool) matching (user_response == target_direction)
        * size_px (exact positive int, not bool)
    """
    if parse_completion_timestamp(completed_at) is None:
        return False
    if not isinstance(answers, list) or len(answers) != 8:
        return False

    q_nums = set()
    for a in answers:
        if not isinstance(a, dict):
            return False
        required_keys = {"question_num", "target_direction", "user_response", "is_correct", "size_px"}
        if not required_keys.issubset(a.keys()):
            return False
        q_num = a["question_num"]
        if type(q_num) is not int or q_num < 1 or q_num > 8:
            return False
        q_nums.add(q_num)
        target = a["target_direction"]
        user_resp = a["user_response"]
        if target not in DIRECTIONS or user_resp not in DIRECTIONS:
            return False
        if type(a["is_correct"]) is not bool or a["is_correct"] != (user_resp == target):
            return False
        if type(a["size_px"]) is not int or a["size_px"] <= 0:
            return False

    return q_nums == set(range(1, 9))


def resume_test():
    """Resumes an incomplete vision check from the next unanswered question."""
    questions = st.session_state.questions if isinstance(st.session_state.questions, list) else []
    total_q = len(questions) if questions else 8
    answers = st.session_state.answers

    if is_valid_partial_session(answers, questions):
        st.session_state.current_question_index = len(answers)
        st.session_state.step = "vision_check"
        st.session_state.nav_jump_select = "vision_check"
    elif is_valid_completed_session(answers, st.session_state.completed_at, questions):
        st.session_state.current_question_index = total_q
        st.session_state.step = "results"
        st.session_state.nav_jump_select = "results"
    else:
        # Invalid, corrupted, or unstarted session -> restart cleanly
        start_vision_check()


def record_response(selected_direction: str, curr_idx: int, target_dir: str, size_px: int, total_q: int):
    """Records an interactive answer with strict idempotency."""
    answers = st.session_state.answers
    if not isinstance(answers, list) or len(answers) >= total_q or curr_idx >= total_q:
        st.session_state.current_question_index = total_q
        st.session_state.step = "results"
        st.session_state.nav_jump_select = "results"
        return

    q_num = curr_idx + 1
    already_recorded = {
        a["question_num"] for a in answers
        if isinstance(a, dict) and type(a.get("question_num")) is int
    }
    if q_num not in already_recorded:
        is_correct = (selected_direction == target_dir)
        st.session_state.answers.append({
            "question_num": q_num,
            "target_direction": target_dir,
            "user_response": selected_direction,
            "is_correct": is_correct,
            "size_px": size_px
        })

    new_idx = curr_idx + 1
    st.session_state.current_question_index = min(new_idx, total_q)

    if len(st.session_state.answers) >= total_q or new_idx >= total_q:
        st.session_state.completed_at = datetime.now().strftime(COMPLETION_TIMESTAMP_FORMAT)
        st.session_state.step = "results"
        st.session_state.nav_jump_select = "results"


# -----------------------------------------------------------------------------
# Main Application Flow
# -----------------------------------------------------------------------------
def main():
    # Page Setup
    st.set_page_config(
        page_title="Focal Monitor | At-Home Vision Tracking Prototype",
        page_icon="👁️",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize State
    initialize_session_state()

    # Guard: If in vision_check but all questions are answered, route to results
    total_q = len(st.session_state.questions)
    if st.session_state.step == "vision_check" and (
        len(st.session_state.answers) >= total_q or 
        st.session_state.current_question_index >= total_q
    ):
        st.session_state.step = "results"
        st.session_state.current_question_index = total_q

    # Ensure sidebar selectbox state is in sync with canonical st.session_state.step
    if "nav_jump_select" not in st.session_state or st.session_state.nav_jump_select != st.session_state.step:
        st.session_state.nav_jump_select = st.session_state.step
    st.markdown("""<style>
:root {
    --focal-navy: #102A43;
    --focal-blue: #0B74B8;
    --focal-blue-dark: #075985;
    --focal-sky: #EAF5FB;
    --focal-ink: #172B3A;
    --focal-muted: #5D7080;
    --focal-line: #D9E4EA;
    --focal-surface: #FFFFFF;
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Inter, Roboto, Helvetica, Arial, sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 76% -10%, rgba(14, 165, 233, 0.08), transparent 26rem),
        #FBFDFE;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stToolbar"] {
    display: flex;
}

[data-testid="stDeployButton"],
[data-testid="stMainMenu"] {
    display: none !important;
}

[data-testid="stSidebarCollapseButton"],
[data-testid="stExpandSidebarButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
}

[data-testid="stSidebarCollapseButton"] button,
[data-testid="stExpandSidebarButton"] button {
    border: 1px solid var(--focal-line) !important;
    border-radius: 10px !important;
    background: rgba(255, 255, 255, 0.92) !important;
    box-shadow: 0 3px 12px rgba(16, 42, 67, 0.08) !important;
}

.stMainBlockContainer {
    max-width: 1240px;
    padding-top: 1.35rem !important;
    padding-right: 2.25rem !important;
    padding-bottom: 4rem !important;
    padding-left: 2.25rem !important;
}

[data-testid="stSidebar"] {
    background: #F4F8FA;
    border-right: 1px solid var(--focal-line);
}

[data-testid="stSidebar"] > div:first-child {
    width: 19rem;
}

[data-testid="stSidebarContent"] {
    padding-top: 1.35rem;
}

[data-testid="stSidebar"] hr {
    margin: 1rem 0;
    border-color: var(--focal-line);
}

/* Welcome screen */
.welcome-intro {
    max-width: 760px;
    margin: 10px 0 20px;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    padding: 5px 9px;
    border-radius: 999px;
    color: #075985;
    background: #E0F2FE;
    font-size: 0.69rem;
    font-weight: 800;
    letter-spacing: 0.09em;
    text-transform: uppercase;
}

.welcome-title {
    margin: 10px 0 8px;
    color: var(--focal-ink);
    font-size: clamp(2rem, 4vw, 3.15rem);
    line-height: 1.03;
    letter-spacing: -0.045em;
    font-weight: 780;
}

.welcome-copy {
    max-width: 690px;
    margin: 0;
    color: var(--focal-muted);
    font-size: 1rem;
    line-height: 1.6;
}

.panel-heading {
    margin: 0 0 4px;
    color: var(--focal-ink);
    font-size: 1.02rem;
    font-weight: 730;
}

.setup-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin: 10px 0 14px;
}

.setup-item {
    display: grid;
    grid-template-columns: 38px minmax(0, 1fr) auto;
    align-items: center;
    gap: 11px;
    min-height: 58px;
    padding: 8px 12px;
    background: #FFFFFF;
    border: 1px solid var(--focal-line);
    border-radius: 13px;
    box-shadow: 0 2px 8px rgba(16, 42, 67, 0.035);
}

.setup-icon {
    display: grid;
    place-items: center;
    width: 36px;
    height: 36px;
    border-radius: 10px;
    background: var(--focal-sky);
    font-size: 1rem;
}

.setup-label {
    color: var(--focal-ink);
    font-size: 0.86rem;
    font-weight: 690;
}

.setup-value {
    color: var(--focal-muted);
    font-size: 0.79rem;
    text-align: right;
}

.page-intro {
    margin: 18px 0 20px;
}

.page-title {
    margin: 7px 0 5px;
    color: var(--focal-ink);
    font-size: clamp(1.75rem, 3vw, 2.4rem);
    line-height: 1.1;
    letter-spacing: -0.035em;
}

.page-copy {
    margin: 0;
    color: var(--focal-muted);
    font-size: 0.92rem;
}

.view-label {
    margin: 8px 0 6px;
    color: var(--focal-muted);
    font-size: 0.75rem;
    font-weight: 750;
    letter-spacing: 0.07em;
    text-transform: uppercase;
}

.result-card {
    display: grid;
    grid-template-columns: minmax(170px, 0.75fr) minmax(260px, 1.25fr) auto;
    align-items: center;
    gap: 24px;
    margin: 16px 0;
    padding: 22px 24px;
    background: #FFFFFF;
    border: 1px solid var(--focal-line);
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(16, 42, 67, 0.06);
}

.result-score {
    color: var(--focal-ink);
    font-size: 3.5rem;
    line-height: 1;
    font-weight: 790;
    letter-spacing: -0.055em;
    white-space: nowrap;
}

.result-score span {
    color: #8A9AA5;
    font-size: 1.55rem;
    font-weight: 650;
    letter-spacing: -0.02em;
}

.result-summary strong {
    display: block;
    color: var(--focal-ink);
    font-size: 1rem;
    margin-bottom: 4px;
}

.result-summary p,
.result-meta {
    margin: 0;
    color: var(--focal-muted);
    font-size: 0.78rem;
    line-height: 1.5;
}

.result-meta {
    text-align: right;
}

.result-note {
    margin: -6px 0 14px;
    padding: 9px 12px;
    border-radius: 10px;
    background: #F3F8FB;
    color: #476579;
    font-size: 0.78rem;
    line-height: 1.45;
}

.chart-legend {
    display: flex;
    align-items: center;
    gap: 18px;
    margin: 8px 0 -2px;
    color: var(--focal-muted);
    font-size: 0.78rem;
    font-weight: 620;
}

.chart-legend-item {
    display: inline-flex;
    align-items: center;
    gap: 7px;
}

.chart-legend-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    background: #3B82B8;
}

.chart-legend-diamond {
    width: 10px;
    height: 10px;
    border-radius: 2px;
    background: #F07F5A;
    transform: rotate(45deg);
}

div[data-testid="stVegaLiteChart"] {
    margin-top: 8px;
    padding: 12px 10px 2px;
    background: linear-gradient(180deg, #FFFFFF 0%, #FAFCFD 100%);
    border: 1px solid var(--focal-line);
    border-radius: 16px;
    box-shadow: 0 8px 24px rgba(16, 42, 67, 0.055);
    overflow: hidden;
}

/* Turn the comparison radio into one compact segmented control. */
div[data-testid="stRadio"] div[role="radiogroup"] {
    display: inline-flex;
    gap: 4px;
    padding: 4px;
    border: 1px solid var(--focal-line);
    border-radius: 12px;
    background: #F3F7F9;
}

div[data-testid="stRadio"] div[role="radiogroup"] label {
    margin: 0;
    padding: 8px 13px;
    border-radius: 9px;
    transition: background 0.15s ease, box-shadow 0.15s ease;
}

div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
    background: #FFFFFF;
    box-shadow: 0 2px 7px rgba(16, 42, 67, 0.1);
}

div[data-testid="stRadio"] input[type="radio"] {
    accent-color: var(--focal-blue);
}

/* Reusable app cards */
.info-card {
    background-color: rgba(255, 255, 255, 0.82);
    border: 1px solid var(--focal-line);
    border-radius: 14px;
    padding: 12px 15px;
    box-shadow: 0 3px 12px rgba(16, 42, 67, 0.04);
    margin-bottom: 10px;
    color: inherit;
}

.info-card-header {
    font-weight: 680;
    font-size: 0.92rem;
    color: inherit;
    margin-bottom: 3px;
}

.info-card-body {
    color: inherit;
    opacity: 0.84;
    font-size: 0.84rem;
    line-height: 1.45;
    margin: 0;
}

.optotype-stage {
    background-color: #FFFFFF;
    border: 1px solid var(--focal-line);
    border-radius: 18px;
    padding: 26px 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 12px 30px rgba(16, 42, 67, 0.08);
    margin: 14px auto;
    min-height: 220px;
}

.badge-demo {
    display: inline-block;
    background-color: #E0F2FE;
    color: #0369A1;
    font-size: 0.69rem;
    font-weight: 750;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    padding: 4px 9px;
    border-radius: 9999px;
    margin-bottom: 8px;
}

/* Sidebar */
.sidebar-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 4px;
}

.sidebar-logo {
    display: grid;
    place-items: center;
    width: 38px;
    height: 38px;
    border-radius: 12px;
    color: #FFFFFF;
    background: linear-gradient(145deg, #075985, #0EA5E9);
    box-shadow: 0 7px 16px rgba(3, 105, 161, 0.22);
}

.sidebar-brand-name {
    color: var(--focal-ink);
    font-size: 1rem;
    font-weight: 770;
    letter-spacing: -0.02em;
}

.sidebar-brand-subtitle {
    color: var(--focal-muted);
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.sidebar-section-label {
    margin: 14px 0 8px;
    color: #7B8C98;
    font-size: 0.67rem;
    font-weight: 800;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.progress-step {
    display: grid;
    grid-template-columns: 28px minmax(0, 1fr);
    align-items: center;
    gap: 9px;
    min-height: 42px;
    margin: 4px 0;
    padding: 6px 8px;
    border-radius: 11px;
    color: #758591;
    font-size: 0.79rem;
    font-weight: 570;
}

.progress-step .step-number {
    display: grid;
    place-items: center;
    width: 27px;
    height: 27px;
    border-radius: 9px;
    background: #E5EDF1;
    color: #637684;
    font-size: 0.72rem;
    font-weight: 760;
}

.progress-step.is-active {
    background: #E4F2F9;
    color: #075985;
    font-weight: 720;
}

.progress-step.is-active .step-number {
    color: #FFFFFF;
    background: var(--focal-blue);
    box-shadow: 0 5px 12px rgba(11, 116, 184, 0.22);
}

.progress-step.is-complete {
    color: #3F596A;
}

.progress-step.is-complete .step-number {
    color: #166534;
    background: #DCFCE7;
}

.sidebar-body-text {
    font-size: 0.8rem;
    color: var(--focal-muted);
    line-height: 1.5;
    margin-bottom: 10px;
}

.sidebar-footer-note {
    margin-top: 16px;
    font-size: 0.7rem;
    color: #71838F;
    text-align: center;
    line-height: 1.5;
}

/* Native controls */
div[data-testid="stButton"] > button,
div[data-testid="stFormSubmitButton"] > button,
div[data-testid="stDownloadButton"] > button {
    border-radius: 11px;
    font-weight: 670;
    min-height: 44px;
    border-color: #CAD9E1;
    transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
    white-space: normal;
    word-break: break-word;
}

div[data-testid="stButton"] > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-1px);
    border-color: #7DB9D7;
    box-shadow: 0 6px 16px rgba(16, 42, 67, 0.09);
}

button[kind="primary"],
button[data-testid="stBaseButton-primary"],
div[data-testid="stFormSubmitButton"] > button {
    background: linear-gradient(120deg, #075985, #0B74B8) !important;
    border: 1px solid #075985 !important;
    color: #FFFFFF !important;
    min-height: 48px;
    box-shadow: 0 8px 20px rgba(3, 105, 161, 0.2);
}

button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background: linear-gradient(120deg, #064C73, #08689F) !important;
    border-color: #064C73 !important;
    color: #FFFFFF !important;
}

button[kind="primary"]:focus-visible,
button[data-testid="stBaseButton-primary"]:focus-visible {
    box-shadow: 0 0 0 0.22rem rgba(14, 165, 233, 0.35) !important;
}

div[data-testid="stExpander"] {
    border-color: var(--focal-line);
    border-radius: 12px;
    background: rgba(255,255,255,0.72);
}

@media (max-width: 900px) {
    .stMainBlockContainer {
        padding-right: 1rem !important;
        padding-left: 1rem !important;
    }
    .welcome-title {
        font-size: 2.25rem;
    }
    .result-card {
        grid-template-columns: 1fr 1.5fr;
    }
    .result-meta {
        grid-column: 1 / -1;
        text-align: left;
    }
}

@media (max-width: 560px) {
    .setup-item {
        grid-template-columns: 34px minmax(0, 1fr);
    }
    .setup-value {
        grid-column: 2;
        text-align: left;
    }
    .result-card {
        grid-template-columns: 1fr;
        gap: 12px;
        padding: 18px;
    }
    .result-meta {
        grid-column: auto;
    }
}
</style>""", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Sidebar
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.markdown(
            """<div class="sidebar-brand">
<div class="sidebar-logo" aria-hidden="true">◉</div>
<div>
<div class="sidebar-brand-name">Focal Monitor</div>
<div class="sidebar-brand-subtitle">Vision clarity companion</div>
</div>
</div>""",
            unsafe_allow_html=True
        )
        st.caption("Duke University • MENG 570")
        st.markdown("<div class='sidebar-section-label'>Your progress</div>", unsafe_allow_html=True)

        step_labels = {
            "welcome": "1. Welcome & Setup",
            "vision_check": "2. Vision Check (8 Items)",
            "results": "3. Immediate Results",
            "vision_history": "4. Compare Results & Feedback"
        }

        step_order = list(step_labels)
        current_step = st.session_state.step
        current_position = step_order.index(current_step) if current_step in step_order else 0
        for index, (key, name) in enumerate(step_labels.items()):
            state_class = "is-active" if key == current_step else "is-complete" if index < current_position else ""
            number_content = "✓" if index < current_position else str(index + 1)
            display_name = name.split(". ", 1)[-1]
            st.markdown(
                f"<div class='progress-step {state_class}'><span class='step-number'>{number_content}</span>"
                f"<span>{display_name}</span></div>",
                unsafe_allow_html=True
            )

        with st.expander("About this research", expanded=False):
            st.markdown("**User Persona: Riley**")
            st.markdown(
                "<div class='sidebar-body-text'>"
                "Adult wearing corrective glasses/contacts who notices possible subtle vision changes "
                "between annual professional eye doctor visits."
                "</div>",
                unsafe_allow_html=True
            )
            if st.session_state.submitted_feedback:
                st.markdown("**Course Hypothesis (Debriefed)**")
                st.markdown(
                    "<div class='sidebar-body-text' style='font-style:italic;'>"
                    "“Adults who suspect their vision is changing will find ongoing vision tracking "
                    "more useful than receiving a single test result.”"
                    "</div>",
                    unsafe_allow_html=True
                )
            else:
                st.markdown("**Research Evaluation**")
                st.markdown(
                    "<div class='sidebar-body-text'>"
                    "Evaluating two distinct presentation formats for demonstration vision-check results."
                    "</div>",
                    unsafe_allow_html=True
                )

        # Evaluator Quick Jump remains available, but is visually secondary for participants.
        with st.expander("Evaluator Navigation", expanded=False):
            def on_nav_jump():
                st.session_state.step = st.session_state.nav_jump_select

            st.selectbox(
                "Jump directly to step:",
                options=["welcome", "vision_check", "results", "vision_history"],
                format_func=lambda s: step_labels[s],
                key="nav_jump_select",
                on_change=on_nav_jump
            )
            st.button("🔄 Reset Demo", on_click=reset_demo, help="Clear responses and restart from Step 1", **full_width())

        # 2-Minute Presenter Demo Guide
        with st.expander("⏱️ 2-Minute Presenter Guide", expanded=False):
            st.markdown(
                "**Rehearsed Classroom Flow (~2 min):**\n\n"
                "1. **0:00–0:25 Problem:** Welcome screen shows persona Riley (corrective lens wearer noticing vision drift between exams).\n"
                "2. **0:25–0:55 Vision Check:** Click *Start Vision Check*. Answer 8 tumbling-E optotypes with progressive sizing.\n"
                "3. **0:55–1:15 Results:** Review the immediate vision result and optional item breakdown.\n"
                "4. **1:15–1:45 Comparison:** Click *Compare Results*. Switch between **Single Result** and **Trend Tracking** to contrast snapshot vs 7-week baseline context.\n"
                "5. **1:45–2:00 Feedback & Debrief:** Submit neutral feedback, observe locking and JSON export, and reveal research debrief."
            )

        st.markdown(
            "<div class='sidebar-footer-note'>"
            "No account required · Demo session"
            "</div>",
            unsafe_allow_html=True
        )

    # =========================================================================
    # STEP 1: WELCOME & SETUP
    # =========================================================================
    if st.session_state.step == "welcome":
        _, focus_col, _ = st.columns([1, 5, 1])

        with focus_col:
            st.markdown("""<section class="welcome-intro">
<span class="eyebrow">Step 1 of 4</span>
<h1 class="welcome-title">Ready for a 2-minute vision check?</h1>
<p class="welcome-copy">Set up your screen, then identify the open direction of eight E shapes.</p>
</section>
<div class="panel-heading">Before you begin</div>
<div class="setup-list">
    <div class="setup-item">
        <span class="setup-icon" aria-hidden="true">👓</span>
        <span class="setup-label">1. Corrective Lenses</span>
        <span class="setup-value">Keep glasses or contacts on</span>
    </div>
    <div class="setup-item">
        <span class="setup-icon" aria-hidden="true">↔</span>
        <span class="setup-label">2. Arm's-Length Distance</span>
        <span class="setup-value">20–24 in · 50–60 cm</span>
    </div>
    <div class="setup-item">
        <span class="setup-icon" aria-hidden="true">☀</span>
        <span class="setup-label">3. Screen Lighting</span>
        <span class="setup-value">Comfortable and glare-free</span>
    </div>
    <div class="setup-item">
        <span class="setup-icon" aria-hidden="true">E</span>
        <span class="setup-label">4. Interactive Task</span>
        <span class="setup-value">Identify the open direction</span>
    </div>
</div>""", unsafe_allow_html=True)

            st.button("Start Vision Check  →", type="primary", on_click=start_vision_check, **full_width())

            with st.expander("📖 Testing Setup & Distance Calibration Guidance", expanded=False):
                st.markdown(
                    "- **Viewing Distance:** Sit comfortably at approximately arm's length (20–24 inches or 50–60 cm). Keep your posture upright.\n"
                    "- **Lenses:** If you use separate reading or computer glasses, wear whichever lenses you typically use at this screen distance.\n"
                    "- **Display Position:** Place monitor at eye level or slightly below, avoiding direct sunlight or backlighting glare.\n"
                    "- **Pacing:** Each of the 8 optotypes appears immediately after your response; take whatever time is comfortable."
                )

            with st.expander("What happens after the check?", expanded=False):
                st.markdown(
                    "**Product Context & Evaluation Purpose**\n\n"
                    "1. Review your vision result.\n"
                    "2. Compare the same result as a single reading and with trend context.\n"
                    "3. Share anonymous product feedback.\n\n"
                    "No name or account is required."
                )

    # =========================================================================
    # STEP 2: VISION CHECK (8 Interactive Tumbling-E Questions)
    # =========================================================================
    elif st.session_state.step == "vision_check":
        curr_idx = st.session_state.current_question_index
        total_q = len(st.session_state.questions)
        
        # Ensure index & completion safety (Idempotency)
        if len(st.session_state.answers) >= total_q or curr_idx >= total_q:
            st.session_state.current_question_index = total_q
            navigate_to("results")
            return
            
        st.markdown(
            f"""<section class="page-intro">
<span class="eyebrow">Question {curr_idx + 1} of {total_q}</span>
<h1 class="page-title">Which direction is the E open?</h1>
</section>""",
            unsafe_allow_html=True
        )
        st.progress((curr_idx + 1) / total_q)

        curr_q = st.session_state.questions[curr_idx]
        target_dir = curr_q["direction"]
        size_px = curr_q["size_px"]

        # Optotype Stage Card
        st.markdown(
            f"""<div class="optotype-stage">
{render_tumbling_e_svg(target_dir, size_px)}
</div>""",
            unsafe_allow_html=True
        )

        # Direction buttons in an intuitive layout
        btn_col1, btn_col2, btn_col3, btn_col4 = st.columns(4)
        
        with btn_col1:
            st.button(
                "⬅️ Left",
                key=f"btn_left_{curr_idx}",
                on_click=record_response,
                args=("left", curr_idx, target_dir, size_px, total_q),
                **full_width()
            )
        with btn_col2:
            st.button(
                "⬆️ Up",
                key=f"btn_up_{curr_idx}",
                on_click=record_response,
                args=("up", curr_idx, target_dir, size_px, total_q),
                **full_width()
            )
        with btn_col3:
            st.button(
                "⬇️ Down",
                key=f"btn_down_{curr_idx}",
                on_click=record_response,
                args=("down", curr_idx, target_dir, size_px, total_q),
                **full_width()
            )
        with btn_col4:
            st.button(
                "➡️ Right",
                key=f"btn_right_{curr_idx}",
                on_click=record_response,
                args=("right", curr_idx, target_dir, size_px, total_q),
                **full_width()
            )
                
        with st.expander("About this demonstration", expanded=False):
            st.markdown(
                f"**Size {curr_idx + 1} of {total_q}:** The E becomes smaller as the check progresses.\n\n"
                "**Accessibility Disclosure:** This task relies on visual resolution of high-contrast optotypes. "
                "Screen readers and text alternatives intentionally do not announce optotype orientations during the test "
                "to preserve the interaction."
            )

    # =========================================================================
    # STEP 3: RESULTS & DEMO LIMITATIONS
    # =========================================================================
    elif st.session_state.step == "results":
        st.markdown("""<section class="page-intro">
<span class="eyebrow">Step 3 of 4</span>
<h1 class="page-title">Your result</h1>
</section>""", unsafe_allow_html=True)
        
        answers = st.session_state.answers
        questions = st.session_state.questions
        total_answers = len(answers) if isinstance(answers, list) else 0
        total_q = len(questions) if isinstance(questions, list) else 8
        is_complete = is_valid_completed_session(answers, st.session_state.completed_at, questions)
        
        # Check if session is incomplete or invalid
        if not is_complete:
            is_partial = is_valid_partial_session(answers, questions)
            
            if is_partial:
                header_text = f"Vision Check Incomplete ({total_answers} of {total_q} Questions Answered)"
                body_text = (
                    f"A completed test must contain exactly {total_q} valid, unique question responses "
                    f"to generate a vision result. No result or completion timestamp has been recorded for this session."
                )
            else:
                header_text = f"Vision Check Incomplete ({total_answers} of {total_q} Questions Answered)"
                body_text = (
                    f"A completed test must contain exactly {total_q} valid, unique question responses with an authentic completion timestamp. "
                    f"The current session data does not meet completion validation criteria. Please start or resume a valid check."
                )

            st.markdown(
                f"""<div style="background-color:#FFFBEB; border:1px solid #FCD34D; border-left:6px solid #F59E0B; border-radius:12px; padding:20px; margin-bottom:18px;">
<span style="display:inline-block; background-color:#FEF3C7; color:#92400E; font-size:0.75rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; padding:3px 10px; border-radius:9999px; margin-bottom:8px;">
⚠️ Session Incomplete
</span>
<h2 style="margin:4px 0 6px 0; color:#0F172A;">{header_text}</h2>
<p style="color:#475569; margin:0 0 14px 0; font-size:0.92rem; line-height:1.5;">
{body_text}
</p>
</div>""",
                unsafe_allow_html=True
            )
            
            col_inc1, col_inc2 = st.columns([1, 1], gap="medium")
            with col_inc1:
                if is_partial:
                    st.button(f"▶️ Resume Test (Continue from Q{total_answers + 1})", type="primary", on_click=resume_test, **full_width())
                else:
                    st.button("🚀 Start Vision Check (Begin Q1)", type="primary", on_click=start_vision_check, **full_width())
            with col_inc2:
                st.button("📊 View Vision History (Baseline Only) ➡️", on_click=navigate_to, args=("vision_history",), **full_width())
                
            if is_partial:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### Partial Responses Recorded So Far")
                breakdown_rows = []
                for a in answers:
                    breakdown_rows.append({
                        "Question": f"Q{a['question_num']}",
                        "Target Direction": DIRECTION_LABELS.get(a['target_direction'], a['target_direction']),
                        "Your Response": DIRECTION_LABELS.get(a['user_response'], a['user_response']),
                        "Result": "✅ Correct" if a['is_correct'] else "❌ Missed",
                        "Demo Sizing": f"{a['size_px']}px"
                    })
                st.dataframe(pd.DataFrame(breakdown_rows), hide_index=True, **full_width())
                st.caption(f"Progress: {total_answers}/{total_q} questions. Finish remaining {total_q - total_answers} questions to see full results.")
            return
            
        # Completed Session Results (Exactly 8 questions answered)
        correct_count = sum(1 for a in answers if a["is_correct"])
        vision_result = get_demo_vision_result(correct_count, total_answers)
        
        # Score Summary Card
        st.markdown(
            f"""<div class="result-card">
<div>
    <span class="badge-demo">Check complete</span>
    <div class="result-score">{vision_result['acuity']}</div>
</div>
<div class="result-summary">
    <strong>{vision_result['status']}</strong>
    <p>{vision_result['message']}</p>
</div>
<div class="result-meta">{st.session_state.completed_at or 'Session recorded'}<br><strong>Vision result</strong></div>
</div>""",
            unsafe_allow_html=True
        )

        with st.expander("View question breakdown", expanded=False):
            st.markdown("#### Demo Questions Breakdown")
            breakdown_rows = []
            for a in answers:
                breakdown_rows.append({
                    "Question": f"Q{a['question_num']}",
                    "Target Direction": DIRECTION_LABELS.get(a['target_direction'], a['target_direction']),
                    "Your Response": DIRECTION_LABELS.get(a['user_response'], a['user_response']),
                    "Result": "✅ Correct" if a['is_correct'] else "❌ Missed",
                    "Demo Sizing": f"{a['size_px']}px"
                })
                
            breakdown_df = pd.DataFrame(breakdown_rows)
            st.dataframe(breakdown_df, hide_index=True, **full_width())
            st.caption("Responses across eight progressively smaller E shapes.")

        # Transition to Step 4
        st.button("Compare Results  →", type="primary", on_click=proceed_to_comparison, **full_width())

    # =========================================================================
    # STEP 4: EXPERIENCE COMPARISON & EVALUATION FEEDBACK
    # =========================================================================
    elif st.session_state.step == "vision_history":
        st.markdown("""<section class="page-intro">
<span class="eyebrow">Step 4 of 4</span>
<h1 class="page-title">Compare your result</h1>
<p class="page-copy">The vision result stays the same. Only the presentation changes.</p>
</section>""", unsafe_allow_html=True)
        
        # Determine whether a completed live session exists
        answers = st.session_state.answers
        questions = st.session_state.questions
        total_q = len(questions) if isinstance(questions, list) else 8
        has_completed_session = is_valid_completed_session(answers, st.session_state.completed_at, questions)
        is_partial = is_valid_partial_session(answers, questions)
        
        # Determine underlying current result for BOTH experiences
        if has_completed_session:
            current_correct = sum(1 for a in answers if a["is_correct"])
            current_accuracy = round((current_correct / total_q) * 100, 1)
            parsed_dt = parse_completion_timestamp(st.session_state.completed_at)
            current_date = parsed_dt.strftime("%Y-%m-%d") if parsed_dt else datetime.now().strftime("%Y-%m-%d")
            current_timestamp = st.session_state.completed_at
            current_type = "Your Completed Demo Check"
            current_breakdown = [
                {
                    "Question": f"Q{a['question_num']}",
                    "Target Direction": DIRECTION_LABELS.get(a['target_direction'], a['target_direction']),
                    "Your Response": DIRECTION_LABELS.get(a['user_response'], a['user_response']),
                    "Result": "✅ Correct" if a['is_correct'] else "❌ Missed",
                    "Demo Sizing": f"{a['size_px']}px"
                }
                for a in answers
            ]
        else:
            current_correct = 7
            current_accuracy = 87.5
            current_date = "2026-10-18"
            current_timestamp = "2026-10-18 10:15 (Illustrative)"
            current_type = "Illustrative Demo Data"
            current_notes = "Prior week check"
            current_breakdown = [
                {"Question": "Q1", "Target Direction": "Right", "Your Response": "Right", "Result": "✅ Correct", "Demo Sizing": "130px"},
                {"Question": "Q2", "Target Direction": "Up", "Your Response": "Up", "Result": "✅ Correct", "Demo Sizing": "115px"},
                {"Question": "Q3", "Target Direction": "Left", "Your Response": "Left", "Result": "✅ Correct", "Demo Sizing": "100px"},
                {"Question": "Q4", "Target Direction": "Down", "Your Response": "Down", "Result": "✅ Correct", "Demo Sizing": "85px"},
                {"Question": "Q5", "Target Direction": "Right", "Your Response": "Right", "Result": "✅ Correct", "Demo Sizing": "70px"},
                {"Question": "Q6", "Target Direction": "Left", "Your Response": "Left", "Result": "✅ Correct", "Demo Sizing": "55px"},
                {"Question": "Q7", "Target Direction": "Up", "Your Response": "Right", "Result": "❌ Missed", "Demo Sizing": "45px"},
                {"Question": "Q8", "Target Direction": "Down", "Your Response": "Down", "Result": "✅ Correct", "Demo Sizing": "40px"}
            ]

        current_vision = get_demo_vision_result(current_correct, total_q)
        if has_completed_session:
            current_notes = f"Your vision result ({current_vision['acuity']})"

        # Step 4 State Tracking: Researcher preview and view exposure
        if not st.session_state.get("comparison_order_assigned", False):
            st.session_state.comparison_order_assigned = True
            st.session_state.assignment_source = "researcher_sidebar"
            st.session_state.initial_assigned_order = st.session_state.comparison_view_order

        if "views_visited" not in st.session_state:
            st.session_state.views_visited = []
        if st.session_state.active_comparison_view not in st.session_state.views_visited:
            st.session_state.views_visited.append(st.session_state.active_comparison_view)

        has_visited_both = (
            "Experience A: Single Result" in st.session_state.views_visited
            and "Experience B: Trend Tracking" in st.session_state.views_visited
        )

        # Informational / Status Banner for Incomplete Session
        if is_partial:
            st.markdown(
                f"""<div style="background-color:#FFFBEB; border:1px solid #FCD34D; border-left:6px solid #F59E0B; border-radius:10px; padding:14px 18px; margin-bottom:18px;">
<strong style="color:#92400E;">⚠️ Incomplete Test in Progress ({len(answers)} of {total_q} Answered):</strong> 
<span style="color:#78350F; font-size:0.9rem;">
Partial responses are excluded from completed results.
Only completed 8-question sessions appear in completed results.
</span>
</div>""",
                unsafe_allow_html=True
            )
            st.button(f"▶️ Resume Test (Continue from Q{len(answers) + 1})", type="primary", on_click=resume_test, **full_width())
            st.markdown("<br>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # View Switcher & Presentation Order
        # ---------------------------------------------------------------------
        st.markdown("<div class='view-label'>Choose a result view</div>", unsafe_allow_html=True)

        display_options = (
            ["Experience B: Trend Tracking", "Experience A: Single Result"]
            if st.session_state.comparison_view_order == "trend_first"
            else ["Experience A: Single Result", "Experience B: Trend Tracking"]
        )
        
        if st.session_state.get("comparison_view_selector") != st.session_state.active_comparison_view:
            st.session_state.comparison_view_selector = st.session_state.active_comparison_view

        def on_view_radio_change():
            st.session_state.active_comparison_view = st.session_state.comparison_view_selector

        selected_radio = st.radio(
            "Choose presentation format to inspect:",
            options=display_options,
            format_func=lambda option: option.split(": ", 1)[1],
            horizontal=True,
            key="comparison_view_selector",
            on_change=on_view_radio_change,
            label_visibility="collapsed"
        )
        st.session_state.active_comparison_view = selected_radio

        # ---------------------------------------------------------------------
        # EXPERIENCE A: SINGLE RESULT VIEW
        # ---------------------------------------------------------------------
        if st.session_state.active_comparison_view == "Experience A: Single Result":
            st.markdown(
                f"""<div class="result-card">
<div>
    <span class="badge-demo">Single Result</span>
    <div class="result-score">{current_vision['acuity']}</div>
</div>
<div class="result-summary">
    <strong>{current_vision['status']}</strong>
    <p>{current_vision['message']}</p>
</div>
<div class="result-meta">{current_date}<br><strong>{current_type}</strong></div>
</div>""",
                unsafe_allow_html=True
            )

            st.markdown("##### Question breakdown")
            breakdown_df = pd.DataFrame(current_breakdown)
            st.dataframe(breakdown_df, hide_index=True, **full_width())

        # ---------------------------------------------------------------------
        # EXPERIENCE B: TREND TRACKING VIEW
        # ---------------------------------------------------------------------
        else:
            st.markdown(
                f"""<div class="result-card">
<div>
    <span class="badge-demo">Trend Tracking</span>
    <div class="result-score">{current_vision['acuity']}</div>
</div>
<div class="result-summary">
    <strong>{current_vision['status']}</strong>
    <p>{current_vision['message']}</p>
</div>
<div class="result-meta">{current_date}<br><strong>{current_type}</strong></div>
</div>""",
                unsafe_allow_html=True
            )

            # Informational status banner for Experience B
            if has_completed_session:
                st.markdown(
                    f"""<div class="result-note"><strong>Completed Live Session Added.</strong>
Your {current_vision['acuity']} result is plotted below with the previous readings.</div>""",
                    unsafe_allow_html=True
                )
            elif not is_partial:
                st.markdown(
                    """<div class="result-note"><strong>Illustrative Demo Data Only.</strong>
No completed check is recorded, so the chart contains fictional example records only.</div>""",
                    unsafe_allow_html=True
                )
                st.button("🚀 Start Vision Check (8 Questions)", type="primary", on_click=start_vision_check, key="btn_start_from_b", **full_width())
                st.markdown("<br>", unsafe_allow_html=True)

            # Data for Trend Chart
            df_fictional = pd.DataFrame(FICTIONAL_RECORDS)
            df_fictional["Acuity"] = df_fictional.apply(
                lambda row: get_demo_vision_result(int(row["Correct"]), int(row["Total"]))["acuity"],
                axis=1
            )
            if has_completed_session:
                live_record = {
                    "Date": current_date,
                    "Session": "Today",
                    "Correct": current_correct,
                    "Total": total_q,
                    "Accuracy": current_accuracy,
                    "Acuity": current_vision["acuity"],
                    "Type": "Your Completed Demo Check",
                    "Notes": current_notes
                }
                df_all = pd.concat([df_fictional, pd.DataFrame([live_record])], ignore_index=True)
            else:
                df_all = df_fictional

            st.markdown("##### Longitudinal Vision Trend")
            st.caption("See how the vision result changes across sessions.")
            st.markdown(
                """<div class="chart-legend">
<span class="chart-legend-item"><span class="chart-legend-dot"></span>Previous results</span>
<span class="chart-legend-item"><span class="chart-legend-diamond"></span>Current result</span>
</div>""",
                unsafe_allow_html=True
            )

            x_axis = alt.X(
                "Session:N",
                sort=None,
                title=None,
                axis=alt.Axis(
                    labelAngle=0,
                    labelPadding=12,
                    labelColor="#607487",
                    labelFontSize=12,
                    tickSize=0,
                    domain=False
                )
            )
            y_axis = alt.Y(
                "Acuity:N",
                sort=ACUITY_ORDER,
                title=None,
                axis=alt.Axis(
                    labelPadding=12,
                    labelColor="#607487",
                    labelFontSize=12,
                    tickSize=0,
                    domain=False,
                    grid=True,
                    gridColor="#E3EDF2",
                    gridDash=[3, 4],
                    gridOpacity=1
                )
            )

            area_chart = alt.Chart(df_fictional).mark_area(
                color="#3B82B8",
                opacity=0.08,
                interpolate="monotone"
            ).encode(
                x=x_axis,
                y=y_axis
            )

            line_chart = alt.Chart(df_fictional).mark_line(
                color="#3B82B8",
                strokeWidth=3,
                interpolate="monotone"
            ).encode(
                x=x_axis,
                y=y_axis
            )

            history_points = alt.Chart(df_fictional).mark_circle(
                size=120,
                color="#3B82B8",
                opacity=1,
                stroke="#FFFFFF",
                strokeWidth=2
            ).encode(
                x=x_axis,
                y=y_axis,
                tooltip=[
                    alt.Tooltip("Session:N", title="Session"),
                    alt.Tooltip("Date:N", title="Recorded Date"),
                    alt.Tooltip("Acuity:N", title="Vision Result"),
                    alt.Tooltip("Notes:N", title="Context Notes")
                ]
            )

            chart_layers = area_chart + line_chart + history_points

            if has_completed_session:
                current_df = df_all[df_all["Type"] == "Your Completed Demo Check"]
                current_point = alt.Chart(current_df).mark_point(
                    size=260,
                    shape="diamond",
                    filled=True,
                    color="#F07F5A",
                    stroke="#FFFFFF",
                    strokeWidth=3
                ).encode(
                    x=x_axis,
                    y=y_axis,
                    tooltip=[
                        alt.Tooltip("Session:N", title="Session"),
                        alt.Tooltip("Date:N", title="Recorded Date"),
                        alt.Tooltip("Acuity:N", title="Vision Result"),
                        alt.Tooltip("Notes:N", title="Context Notes")
                    ]
                )
                current_label = alt.Chart(current_df).mark_text(
                    dy=-22,
                    color="#C85232",
                    fontSize=13,
                    fontWeight=700
                ).encode(
                    x=x_axis,
                    y=y_axis,
                    text=alt.Text("Acuity:N")
                )
                chart_layers = chart_layers + current_point + current_label

            final_chart = chart_layers.properties(
                height=270,
                width="container"
            ).configure_view(
                strokeWidth=0
            )

            st.altair_chart(final_chart, **full_width())

            with st.expander("Data details & complete records", expanded=False):
                st.markdown(
                    "Historical entries (Weeks 1–7) are sample readings for Riley. "
                    "Your completed check is added as today's result."
                )
                table_df = df_all[["Session", "Date", "Acuity", "Type", "Notes"]].copy()
                table_df = table_df.rename(columns={"Acuity": "Vision Result"})
                st.dataframe(table_df, hide_index=True, **full_width())

        st.markdown("---")

        # ---------------------------------------------------------------------
        # Evaluation Feedback (Locked after initial submission)
        # ---------------------------------------------------------------------
        if st.session_state.get("feedback_locked", False) and st.session_state.submitted_feedback:
            fb = st.session_state.submitted_feedback
            st.markdown("#### Product Comparison & Evaluation Feedback (Submitted & Locked)")
            st.success("✅ Thank you! Your original evaluation feedback has been recorded and locked.")

            st.markdown(f"""<div style="background-color:#F0FDF4; border:1px solid #86EFAC; border-radius:8px; padding:16px; margin-top:12px; margin-bottom:16px;">
<strong style="color:#166534;">📋 Summary of Your Original Evaluation:</strong>
<ul style="color:#14532D; font-size:0.88rem; margin-top:8px; padding-left:18px;">
<li><strong>Preferred Format:</strong> {fb['q1_preferred_experience']}</li>
<li><strong>Main Reason:</strong> {fb['q2_main_reason'] if fb['q2_main_reason'] else '<em>(None provided)</em>'}</li>
<li><strong>Easier to Understand:</strong> {fb['q3_easier_to_understand']}</li>
<li><strong>Likelihood to Use Regularly:</strong> {fb['q4_reuse_likelihood']}</li>
<li><strong>Assigned Initial Order:</strong> {fb.get('initial_assigned_order', 'N/A')} ({fb.get('assignment_source', 'N/A')})</li>
<li><strong>Both Views Visited:</strong> {'Yes' if fb.get('both_views_visited') else 'No'}</li>
<li><strong>Recorded Timestamp:</strong> {fb['submitted_at']}</li>
</ul>
<div style="font-size:0.8rem; color:#15803D; margin-top:8px;">
🔒 <em>This response is locked to preserve pre-debrief research validity and cannot be modified.</em>
</div>
</div>""", unsafe_allow_html=True)

            # Download Anonymous Session Data
            fb_json = json.dumps(fb, indent=2)
            st.download_button(
                label="📥 Download Anonymous Session Response (JSON)",
                data=fb_json,
                file_name="focal_monitor_anonymous_feedback.json",
                mime="application/json",
                **full_width()
            )

            # Research Debrief Card
            st.markdown("""<div style="background-color:#EFF6FF; border:1px solid #BFDBFE; border-left:6px solid #0284C7; border-radius:10px; padding:18px; margin-top:16px;">
<h4 style="margin:0 0 8px 0; color:#1E3A8A;">🎓 Research Debrief & Study Purpose</h4>
<p style="color:#1E40AF; font-size:0.9rem; line-height:1.55; margin:0 0 10px 0;">
Now that you have submitted your evaluation, here is the context behind this product experiment:
</p>
<div style="background:#FFFFFF; border:1px solid #DBEAFE; border-radius:6px; padding:12px; margin-bottom:10px; font-size:0.88rem; color:#1E3A8A;">
<strong>Core Testing Hypothesis:</strong><br>
<em>“Adults who suspect their vision is changing will find ongoing vision tracking more useful than receiving a single test result.”</em>
</div>
<p style="color:#1E3A8A; font-size:0.88rem; line-height:1.55; margin:0;">
In digital health tools, product teams frequently assume that providing longitudinal tracking is inherently superior. 
However, ongoing tracking can also introduce anxiety or cognitive overhead if users feel burdened by monitoring noise. 
By presenting both <strong>Single Result</strong> and <strong>Trend Tracking</strong> with identical underlying data, 
this study measures whether adult corrective-lens wearers (persona Riley) genuinely prefer longitudinal tracking or favor a simpler, faster interaction.
</p>
</div>""", unsafe_allow_html=True)

        else:
            # Render Editable Form
            st.markdown("#### Product Comparison & Evaluation Feedback")
            st.markdown(
                "<span style='color:inherit; opacity:0.9; font-size:0.92rem;'>"
                "Please provide your objective perspective on the two result views above. "
                "Your feedback is anonymous and helps our product management team understand user preferences between "
                "single test results and ongoing trend tracking."
                "</span>",
                unsafe_allow_html=True
            )

            if not has_visited_both:
                st.markdown(
                    "<div class='info-card' style='border-radius:6px; padding:10px 14px; margin-top:10px; margin-bottom:12px; font-size:0.86rem; color:inherit; opacity:0.9;'>"
                    "ℹ️ <em>Please explore both Single Result and Trend Tracking before submitting feedback.</em>"
                    "</div>",
                    unsafe_allow_html=True
                )

            with st.form("hypothesis_feedback_form"):
                q1_response = st.radio(
                    "1. Which format did you find more useful for monitoring your vision? *",
                    options=[
                        "Single Result",
                        "Trend Tracking",
                        "Both are equally useful",
                        "Neither is useful",
                        "Not sure"
                    ],
                    index=None
                )

                q2_response = st.text_area(
                    "2. What is the main reason for your preference?",
                    placeholder="Explain the primary reason for your preference, or what factors influenced your decision..."
                )

                q3_response = st.radio(
                    "3. Which format was easier to understand at a glance? *",
                    options=[
                        "Single Result",
                        "Trend Tracking",
                        "Both are equally clear",
                        "Neither is clear",
                        "Not sure"
                    ],
                    index=None
                )

                q4_response = st.radio(
                    "4. How likely would you be to use a vision-tracking tool like this regularly? *",
                    options=[
                        "Very unlikely",
                        "Unlikely",
                        "Neutral",
                        "Likely",
                        "Very likely"
                    ],
                    index=None
                )

                submit_feedback = st.form_submit_button("Submit Anonymous Feedback", type="primary")

                if submit_feedback:
                    if not has_visited_both:
                        st.info("ℹ️ Please view both Single Result and Trend Tracking before submitting your comparative feedback.")
                    elif q1_response is None or q3_response is None or q4_response is None:
                        st.error("⚠️ Please answer all required questions (Questions 1, 3, and 4) before submitting.")
                    else:
                        st.session_state.submitted_feedback = {
                            "q1_preferred_experience": q1_response,
                            "q2_main_reason": q2_response.strip() if q2_response else "",
                            "q3_easier_to_understand": q3_response,
                            "q4_reuse_likelihood": q4_response,
                            "initial_assigned_order": st.session_state.initial_assigned_order,
                            "assignment_source": st.session_state.assignment_source,
                            "both_views_visited": True,
                            "views_visited": list(st.session_state.views_visited),
                            "evaluated_score": current_vision["acuity"],
                            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }
                        st.session_state.feedback_locked = True
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Working Reset Demo Button
        col_rst1, col_rst2, col_rst3 = st.columns([1, 2, 1])
        with col_rst2:
            st.button("🔄 Reset Demo and Start Fresh", on_click=reset_demo, **full_width())


if __name__ == "__main__":
    main()
