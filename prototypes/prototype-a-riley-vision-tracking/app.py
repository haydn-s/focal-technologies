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
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.stMainBlockContainer {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* Top Banner / Hero Card */
.hero-card {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
    border-radius: 10px;
    padding: 8px 14px;
    color: #F8FAFC;
    margin-bottom: 6px;
    border-left: 5px solid #0284C7;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.hero-title {
    font-size: 1.25rem;
    font-weight: 700;
    color: #FFFFFF;
    margin: 0 0 2px 0;
    letter-spacing: -0.01em;
}

.hero-subtitle {
    font-size: 0.82rem;
    color: #CBD5E1;
    margin: 0;
}

/* Healthcare disclaimer alert box - High Contrast */
.disclaimer-card {
    background-color: #FFFBEB;
    border: 1px solid #FCD34D;
    border-left: 5px solid #D97706;
    border-radius: 6px;
    padding: 6px 10px;
    color: #92400E;
    font-size: 0.78rem;
    line-height: 1.35;
    margin-bottom: 6px;
}

/* Metric & Instruction cards - Theme Responsive */
.info-card {
    background-color: rgba(128, 128, 128, 0.08);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 10px;
    padding: 10px 14px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    margin-bottom: 8px;
    color: inherit;
}

.info-card-header {
    font-weight: 600;
    font-size: 0.92rem;
    color: inherit;
    margin-bottom: 3px;
}

.info-card-body {
    color: inherit;
    opacity: 0.9;
    font-size: 0.84rem;
    line-height: 1.4;
    margin: 0;
}

/* Tumbling E test display stage */
.optotype-stage {
    background-color: #FFFFFF;
    border: 2px solid #CBD5E1;
    border-radius: 14px;
    padding: 26px 20px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    margin: 14px auto;
    min-height: 220px;
}

/* Badges */
.badge-demo {
    display: inline-block;
    background-color: #E0F2FE;
    color: #0369A1;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    padding: 3px 9px;
    border-radius: 9999px;
    margin-bottom: 8px;
}

/* Sidebar Theme-Aware Typography */
.sidebar-body-text {
    font-size: 0.85rem;
    color: inherit;
    opacity: 0.9;
    line-height: 1.45;
    margin-bottom: 12px;
}

.sidebar-step-inactive {
    color: inherit;
    opacity: 0.7;
    font-size: 0.88rem;
    padding: 2px 0;
}

.sidebar-footer-note {
    font-size: 0.76rem;
    color: inherit;
    opacity: 0.8;
    text-align: center;
    line-height: 1.4;
}

/* Accessibility Note */
.accessibility-note {
    background-color: rgba(128, 128, 128, 0.08);
    border: 1px solid rgba(128, 128, 128, 0.2);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: inherit;
    opacity: 0.9;
    line-height: 1.45;
    margin-top: 12px;
}

/* Touch-friendly, accessible button styling */
div[data-testid="stButton"] > button {
    border-radius: 8px;
    font-weight: 600;
    min-height: 42px;
    transition: all 0.15s ease-in-out;
    white-space: normal;
    word-break: break-word;
}

/* High-contrast primary button styling (Focal brand identity, >= 4.5:1 contrast) */
button[kind="primary"],
button[data-testid="stBaseButton-primary"],
div[data-testid="stFormSubmitButton"] > button {
    background-color: #0369A1 !important;
    border: 1px solid #0369A1 !important;
    color: #FFFFFF !important;
}

button[kind="primary"]:hover,
button[data-testid="stBaseButton-primary"]:hover,
div[data-testid="stFormSubmitButton"] > button:hover {
    background-color: #075985 !important;
    border-color: #075985 !important;
    color: #FFFFFF !important;
}

button[kind="primary"]:active,
button[data-testid="stBaseButton-primary"]:active,
div[data-testid="stFormSubmitButton"] > button:active {
    background-color: #0C4A6E !important;
    border-color: #0C4A6E !important;
    color: #FFFFFF !important;
}

button[kind="primary"]:focus:not(:focus-visible),
button[data-testid="stBaseButton-primary"]:focus:not(:focus-visible) {
    box-shadow: 0 0 0 0.2rem rgba(3, 105, 161, 0.4) !important;
}
</style>""", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # Sidebar
    # -------------------------------------------------------------------------
    with st.sidebar:
        st.markdown("### 👁️ **Focal Monitor**")
        st.caption("Duke University • MENG 570 Product Management")
        st.markdown("---")
        
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
        
        st.markdown("---")
        st.markdown("**Demo Progress Flow**")
        
        step_labels = {
            "welcome": "1. Welcome & Setup",
            "vision_check": "2. Vision Check (8 Items)",
            "results": "3. Immediate Results",
            "vision_history": "4. Compare Experiences & Feedback"
        }
        
        current_step = st.session_state.step
        for key, name in step_labels.items():
            if key == current_step:
                st.markdown(f"👉 **{name}**")
            else:
                st.markdown(f"<div class='sidebar-step-inactive'>{name}</div>", unsafe_allow_html=True)
                
        st.markdown("---")
        
        # Evaluator Quick Jump
        st.markdown("**Evaluator Navigation**")
        def on_nav_jump():
            st.session_state.step = st.session_state.nav_jump_select

        st.selectbox(
            "Jump directly to step:",
            options=["welcome", "vision_check", "results", "vision_history"],
            format_func=lambda s: step_labels[s],
            key="nav_jump_select",
            on_change=on_nav_jump
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.button("🔄 Reset Demo", on_click=reset_demo, help="Clear responses and restart from Step 1", **full_width())

        # 2-Minute Presenter Demo Guide
        with st.expander("⏱️ 2-Minute Presenter Guide", expanded=False):
            st.markdown(
                "**Rehearsed Classroom Flow (~2 min):**\n\n"
                "1. **0:00–0:25 Problem:** Welcome screen shows persona Riley (corrective lens wearer noticing vision drift between exams).\n"
                "2. **0:25–0:55 Vision Check:** Click *Start Vision Check*. Answer 8 tumbling-E optotypes with progressive sizing.\n"
                "3. **0:55–1:15 Results:** Review immediate score card, item breakdown, and non-clinical limitations.\n"
                "4. **1:15–1:45 Comparison:** Click *Compare Experiences*. Switch between **Experience A (Single Result)** and **Experience B (Trend Tracking)** to contrast snapshot vs 7-week baseline context.\n"
                "5. **1:45–2:00 Feedback & Debrief:** Submit neutral feedback, observe locking and JSON export, and reveal research debrief."
            )

        st.markdown("---")
        st.markdown(
            "<div class='sidebar-footer-note'>"
            "⚠️ Non-clinical interactive prototype.<br>Not a medical device. No personal health data collected."
            "</div>",
            unsafe_allow_html=True
        )

    # -------------------------------------------------------------------------
    # Top Header Banner
    # -------------------------------------------------------------------------
    st.markdown("""
    <div class="hero-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap;">
            <div>
                <div class="hero-title">Focal Monitor <span style="font-size:0.95rem; font-weight:500; background:#0284C7; padding:2px 8px; border-radius:4px; margin-left:8px; vertical-align:middle;">Prototype A</span></div>
                <p class="hero-subtitle">Focal Vision Check & Result Comparison • Duke University MENG 570</p>
            </div>
            <div style="text-align: right; margin-top: 4px;">
                <span class="badge-demo">Academic PM Prototype</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Prominent Medical Disclaimer
    st.markdown("""
    <div class="disclaimer-card">
        <strong>⚠️ Medical & Regulatory Notice:</strong> 
        Focal Monitor is an educational, non-clinical software prototype. 
        It does <strong>not</strong> provide medical diagnoses, clinical visual acuity measurements (such as 20/20 or LogMAR), 
        or corrective lens prescriptions. It is <strong>not</strong> a substitute for comprehensive in-person eye examinations 
        by a licensed optometrist or ophthalmologist.
    </div>
    """, unsafe_allow_html=True)

    # =========================================================================
    # STEP 1: WELCOME & SETUP
    # =========================================================================
    if st.session_state.step == "welcome":
        st.markdown("<h3 style='margin:0 0 2px 0; font-size:1.2rem;'>Step 1: Welcome to Focal Monitor</h3>", unsafe_allow_html=True)
        st.markdown(
            "<p style='margin:0 0 8px 0; font-size:0.88rem; line-height:1.4;'>"
            "Focal Monitor enables adults like <strong>Riley</strong> to check visual clarity at home and compare "
            "result presentation formats between regular eye doctor visits."
            "</p>",
            unsafe_allow_html=True
        )
        
        col1, col2 = st.columns([3, 2], gap="large")
        
        with col1:
            st.markdown("<h4 style='margin:0 0 6px 0; font-size:1.02rem;'>Setup & Environment Instructions</h4>", unsafe_allow_html=True)
            
            st.markdown("""<div style="display:flex; flex-direction:column; gap:5px; margin-bottom:8px;">
<div class="info-card" style="padding:5px 8px; margin:0; display:flex; align-items:center; justify-content:space-between; gap:6px;">
<span class="info-card-header" style="margin:0; font-size:0.83rem; white-space:nowrap;">👓 1. Corrective Lenses</span>
<span class="info-card-body" style="font-size:0.80rem; text-align:right;">Keep glasses/contacts on</span>
</div>
<div class="info-card" style="padding:5px 8px; margin:0; display:flex; align-items:center; justify-content:space-between; gap:6px;">
<span class="info-card-header" style="margin:0; font-size:0.83rem; white-space:nowrap;">📏 2. Arm's-Length Distance</span>
<span class="info-card-body" style="font-size:0.80rem; text-align:right;">~20–24 in (50–60 cm)</span>
</div>
<div class="info-card" style="padding:5px 8px; margin:0; display:flex; align-items:center; justify-content:space-between; gap:6px;">
<span class="info-card-header" style="margin:0; font-size:0.83rem; white-space:nowrap;">💡 3. Screen Lighting</span>
<span class="info-card-body" style="font-size:0.80rem; text-align:right;">Comfortable, glare-free</span>
</div>
<div class="info-card" style="padding:5px 8px; margin:0; display:flex; align-items:center; justify-content:space-between; gap:6px;">
<span class="info-card-header" style="margin:0; font-size:0.83rem; white-space:nowrap;">🎯 4. Interactive Task</span>
<span class="info-card-body" style="font-size:0.80rem; text-align:right;">Identify prong direction</span>
</div>
</div>""", unsafe_allow_html=True)
            
            st.button("🚀 Start Vision Check", type="primary", on_click=start_vision_check, **full_width())
            
            with st.expander("📖 Testing Setup & Distance Calibration Guidance", expanded=False):
                st.markdown(
                    "- **Viewing Distance:** Sit comfortably at approximately arm's length (20–24 inches or 50–60 cm). Keep your posture upright.\n"
                    "- **Lenses:** If you use separate reading or computer glasses, wear whichever lenses you typically use at this screen distance.\n"
                    "- **Display Position:** Place monitor at eye level or slightly below, avoiding direct sunlight or backlighting glare.\n"
                    "- **Pacing:** Each of the 8 optotypes appears immediately after your response; take whatever time is comfortable."
                )

        with col2:
            st.markdown("#### Product Context & Evaluation Purpose")
            st.info(
                "**Evaluation Study Overview:**\n\n"
                "This prototype evaluates **two distinct ways of presenting demonstration vision-check information** "
                "for adult users like Riley who monitor visual clarity between regular professional eye exams.\n\n"
                "After completing 8 demonstration tumbling-E questions, you will review and compare two different result experiences, "
                "then provide objective feedback on which presentation format you find more useful and clear."
            )
            
            st.markdown("""<div class="info-card" style="padding:14px; font-size:0.85rem;">
<strong style="color:inherit;">🔒 Privacy & Safety Safeguards:</strong>
<ul style="margin-top:6px; padding-left:18px; color:inherit; opacity:0.9;">
<li>No personal medical information or identifiers are collected.</li>
<li>No external APIs, databases, or cookies are utilized.</li>
<li>All interactions execute strictly within your local session memory.</li>
</ul>
</div>""", unsafe_allow_html=True)

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
            
        st.markdown("### Step 2: Interactive Vision Check")
        
        progress_val = curr_idx / total_q
        st.progress(progress_val)
        
        col_stat1, col_stat2 = st.columns([1, 1])
        with col_stat1:
            st.markdown(f"**Question {curr_idx + 1} of {total_q}**")
        with col_stat2:
            st.markdown(
                f"<div style='text-align:right; color:inherit; opacity:0.85; font-size:0.88rem;'>"
                f"Completed: {curr_idx} &nbsp;|&nbsp; Remaining: {total_q - curr_idx}</div>",
                unsafe_allow_html=True
            )
            
        curr_q = st.session_state.questions[curr_idx]
        target_dir = curr_q["direction"]
        size_px = curr_q["size_px"]
        
        # Explicit illustrative demonstration disclaimer
        st.markdown(
            f"""<div style="background-color:#EFF6FF; border:1px solid #BFDBFE; border-radius:8px; padding:10px 14px; font-size:0.84rem; color:#1E40AF; margin-bottom:12px;">
ℹ️ <strong>Demonstration Sizing (Level {curr_idx + 1} of {total_q}):</strong> 
Optotype scale reduces to demonstrate interactive difficulty progression. 
<em>This is an illustrative demonstration only and does not represent calibrated clinical visual acuity.</em>
</div>""",
            unsafe_allow_html=True
        )
        
        # Optotype Stage Card
        st.markdown(
            f"""<div class="optotype-stage">
<div style="font-size:0.88rem; color:#334155; margin-bottom:12px; font-weight:600;">
Which direction are the open prongs of the 'E' facing?
</div>
{render_tumbling_e_svg(target_dir, size_px)}
</div>""",
            unsafe_allow_html=True
        )
        
        # Interactive Directional Response Controls
        st.markdown("<p style='text-align:center; font-weight:600; color:inherit; margin-top:6px;'>Select the direction of the open prongs:</p>", unsafe_allow_html=True)
        
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
                
        # Honest Accessibility Disclosure Note
        st.markdown("""<div class="accessibility-note">
♿ <strong>Accessibility Disclosure:</strong> This vision check relies on visual resolution of high-contrast optotypes on your screen. 
Screen readers and text alternatives intentionally do not announce optotype orientations during the test to preserve testing validity. 
Users who require non-visual interfaces or specialized clinical testing should consult a licensed optometrist or ophthalmologist.
</div>""", unsafe_allow_html=True)

    # =========================================================================
    # STEP 3: RESULTS & DEMO LIMITATIONS
    # =========================================================================
    elif st.session_state.step == "results":
        st.markdown("### Step 3: Vision Check Results")
        
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
                    f"to generate demonstration accuracy results. No score or completion timestamp has been recorded for this session."
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
        accuracy_pct = round((correct_count / total_answers) * 100, 1)
        
        # Score Summary Card
        st.markdown(
            f"""<div class="info-card" style="border-left:6px solid #0284C7; padding:20px; margin-bottom:18px;">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
<div>
<span class="badge-demo">Demo Session Completed</span>
<h2 style="margin:4px 0 0 0; color:inherit;">Interactive Demo Score: {correct_count} / {total_answers} Correct</h2>
<p style="color:inherit; opacity:0.9; margin:4px 0 0 0; font-size:0.92rem;">
Overall demonstration question accuracy: <strong>{accuracy_pct}%</strong>
</p>
</div>
<div style="text-align:right; font-size:0.85rem; color:inherit; opacity:0.85; margin-top:8px;">
Completed: {st.session_state.completed_at or 'Session Recorded'}
</div>
</div>
</div>""",
            unsafe_allow_html=True
        )
        
        # Two Columns: Detailed Breakdown vs Educational Limitations
        col_res1, col_res2 = st.columns([1, 1], gap="large")
        
        with col_res1:
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
            st.caption("Demo sizing levels demonstrate responsive scaling; they do not correspond to Snellen acuity.")

        with col_res2:
            st.markdown("#### ⚠️ Essential Non-Clinical Limitations")
            st.markdown("""<div class="info-card" style="border-left: 5px solid #0284C7;">
<strong style="color:inherit; font-size:0.95rem;">Why this score is NOT a medical measurement:</strong>
<ul style="color:inherit; opacity:0.9; font-size:0.88rem; line-height:1.55; margin-top:8px; padding-left:18px;">
<li><strong>No Visual Acuity Rating:</strong> This score represents simple demonstration accuracy only. It does <em>not</em> calculate 20/20, LogMAR, or Snellen fractions.</li>
<li><strong>No Prescriptions or Diagnostics:</strong> Focal cannot diagnose refractive errors (astigmatism, myopia, hyperopia, presbyopia) or organic eye pathology (glaucoma, cataracts, macular changes).</li>
<li><strong>Screen Calibration Limits:</strong> Consumer computer screens vary widely in resolution, pixel pitch, brightness, and distance. Without hardware calibration, true visual angle cannot be measured.</li>
<li><strong>Professional Recommendation:</strong> If you notice vision changes or eye discomfort, schedule a comprehensive in-person exam with a licensed optometrist or ophthalmologist.</li>
</ul>
</div>""", unsafe_allow_html=True)
            
        st.markdown("---")
        
        # Transition to Step 4
        col_nav1, col_nav2 = st.columns([2, 1])
        with col_nav1:
            st.markdown(
                "**Next Step:** Compare **Experience A (Single Result)** and **Experience B (Trend Tracking)** "
                "to evaluate how different presentation formats affect clarity and usefulness."
            )
        with col_nav2:
            st.button("📊 View Vision History & Compare Experiences ➡️", type="primary", on_click=proceed_to_comparison, **full_width())

    # =========================================================================
    # STEP 4: EXPERIENCE COMPARISON & EVALUATION FEEDBACK
    # =========================================================================
    elif st.session_state.step == "vision_history":
        st.markdown("### Step 4: Compare Result Experiences & Evaluation Feedback")
        
        # Narrative Context for Riley
        st.markdown("""<div class="info-card" style="padding:16px; margin-bottom:18px;">
<strong style="color:inherit;">Persona Context: Riley's Vision Journey</strong><br>
<span style="color:inherit; opacity:0.9; font-size:0.9rem;">
Riley checks visual clarity periodically between annual eye exams. 
Below, you will evaluate <strong>two distinct presentation formats</strong> (Experience A and Experience B) 
using the <strong>same underlying demonstration check score</strong> to compare how each format communicates vision-check results.
</span>
</div>""", unsafe_allow_html=True)
        
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
            current_notes = f"Your live session ({current_correct}/{total_q} correct)"
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
Partial scores are excluded from completed evaluation to maintain data integrity. 
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
        st.markdown("---")
        st.markdown("#### Direct Presentation Comparison")
        st.markdown(
            "<span style='color:inherit; opacity:0.9; font-size:0.92rem;'>"
            "Inspect both experiences below. Both views use the <strong>exact same demonstration score</strong> "
            f"({current_correct}/{total_q} Correct). Switch between views to evaluate single-result clarity versus trend context."
            "</span>",
            unsafe_allow_html=True
        )

        display_options = (
            ["Experience B: Trend Tracking", "Experience A: Single Result"]
            if st.session_state.comparison_view_order == "trend_first"
            else ["Experience A: Single Result", "Experience B: Trend Tracking"]
        )
        
        if st.session_state.get("comparison_view_selector") != st.session_state.active_comparison_view:
            st.session_state.comparison_view_selector = st.session_state.active_comparison_view

        col_sw1, col_sw2 = st.columns([3, 2], gap="medium")
        with col_sw1:
            def on_view_radio_change():
                st.session_state.active_comparison_view = st.session_state.comparison_view_selector

            selected_radio = st.radio(
                "Choose presentation format to inspect:",
                options=display_options,
                horizontal=True,
                key="comparison_view_selector",
                on_change=on_view_radio_change
            )
            st.session_state.active_comparison_view = selected_radio

        with col_sw2:
            if st.session_state.active_comparison_view == "Experience A: Single Result":
                st.button(
                    "Switch to Experience B ➡️",
                    on_click=set_active_view,
                    args=("Experience B: Trend Tracking",),
                    **full_width()
                )
            else:
                st.button(
                    "⬅️ Switch to Experience A",
                    on_click=set_active_view,
                    args=("Experience A: Single Result",),
                    **full_width()
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # EXPERIENCE A: SINGLE RESULT VIEW
        # ---------------------------------------------------------------------
        if st.session_state.active_comparison_view == "Experience A: Single Result":
            st.markdown(
                f"""<div class="info-card" style="border-left:6px solid #0284C7; padding:20px; margin-bottom:16px;">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
<div>
<span class="badge-demo">Experience A: Single Result</span>
<h3 style="margin:4px 0 0 0; color:inherit;">Demonstration Score: {current_correct} / {total_q} Correct</h3>
<p style="color:inherit; opacity:0.9; margin:4px 0 0 0; font-size:0.92rem;">
Overall accuracy for this check: <strong>{current_accuracy}%</strong> • Recorded Date: <strong>{current_date}</strong>
</p>
</div>
<div style="text-align:right; font-size:0.85rem; color:inherit; opacity:0.85; margin-top:6px;">
Classification: <strong>{current_type}</strong>
</div>
</div>
</div>""",
                unsafe_allow_html=True
            )

            col_exp_a1, col_exp_a2 = st.columns([1, 1], gap="large")
            with col_exp_a1:
                st.markdown("##### Single Check Questions Breakdown")
                breakdown_df = pd.DataFrame(current_breakdown)
                st.dataframe(breakdown_df, hide_index=True, **full_width())
                st.caption("Demonstrates isolated question accuracy without historical context.")

            with col_exp_a2:
                st.markdown("##### ⚠️ Essential Non-Clinical Limitations")
                st.markdown("""<div class="info-card" style="border-left: 5px solid #0284C7;">
<strong style="color:inherit; font-size:0.95rem;">Understanding Vision Check Results:</strong>
<ul style="color:inherit; opacity:0.9; font-size:0.88rem; line-height:1.55; margin-top:8px; padding-left:18px;">
<li><strong>Snapshot Accuracy Only:</strong> Represents demonstration accuracy for one interactive test. Does not estimate 20/20, LogMAR, or refractive acuity.</li>
<li><strong>No Prescriptions or Medical Diagnosis:</strong> Cannot detect astigmatism, myopia, hyperopia, or organic ocular pathology.</li>
<li><strong>Uncalibrated Hardware:</strong> Display pixel pitch, brightness, and user viewing distance are not clinically calibrated.</li>
<li><strong>Professional Exam Needed:</strong> If you suspect vision changes, schedule an in-person exam with a licensed optometrist or ophthalmologist.</li>
</ul>
</div>""", unsafe_allow_html=True)

            st.caption("ℹ️ Experience A displays only this isolated demonstration result. Historical baseline context and trend lines are excluded.")

        # ---------------------------------------------------------------------
        # EXPERIENCE B: TREND TRACKING VIEW
        # ---------------------------------------------------------------------
        else:
            st.markdown(
                f"""<div class="info-card" style="border-left:6px solid #0284C7; padding:20px; margin-bottom:16px;">
<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap;">
<div>
<span class="badge-demo">Experience B: Trend Tracking</span>
<h3 style="margin:4px 0 0 0; color:inherit;">Demonstration Score: {current_correct} / {total_q} Correct</h3>
<p style="color:inherit; opacity:0.9; margin:4px 0 0 0; font-size:0.92rem;">
Overall accuracy for this check: <strong>{current_accuracy}%</strong> • Recorded Date: <strong>{current_date}</strong>
</p>
</div>
<div style="text-align:right; font-size:0.85rem; color:inherit; opacity:0.85; margin-top:6px;">
Classification: <strong>{current_type}</strong>
</div>
</div>
</div>""",
                unsafe_allow_html=True
            )

            # Informational status banner for Experience B
            if has_completed_session:
                st.markdown(
                    f"""<div style="background-color:#F0FDF4; border:1px solid #86EFAC; border-left:6px solid #16A34A; border-radius:10px; padding:14px 18px; margin-bottom:18px;">
<strong style="color:#166534;">✅ Completed Live Session Added:</strong> 
<span style="color:#14532D; font-size:0.9rem;">
Your completed check score (<strong>{current_correct}/{total_q} Correct — {current_accuracy}%</strong>) 
is plotted below as a distinct comparison point against Riley's illustrative demo baseline.
</span>
</div>""",
                    unsafe_allow_html=True
                )
            elif not is_partial:
                st.markdown(
                    """<div style="background-color:#EFF6FF; border:1px solid #BFDBFE; border-left:6px solid #0284C7; border-radius:10px; padding:14px 18px; margin-bottom:18px;">
<strong style="color:#1E40AF;">ℹ️ Illustrative Demo Data Only:</strong> 
<span style="color:#1E3A8A; font-size:0.9rem;">
No completed live check is currently recorded. The chart below displays only fictional example records 
('Illustrative Demo Data') for persona Riley.
</span>
</div>""",
                    unsafe_allow_html=True
                )
                st.button("🚀 Start Vision Check (8 Questions)", type="primary", on_click=start_vision_check, key="btn_start_from_b", **full_width())
                st.markdown("<br>", unsafe_allow_html=True)

            # Data for Trend Chart
            df_fictional = pd.DataFrame(FICTIONAL_RECORDS)
            if has_completed_session:
                live_record = {
                    "Date": current_date,
                    "Session": "Today (Demo Check)",
                    "Correct": current_correct,
                    "Total": total_q,
                    "Accuracy": current_accuracy,
                    "Type": "Your Completed Demo Check",
                    "Notes": current_notes
                }
                df_all = pd.concat([df_fictional, pd.DataFrame([live_record])], ignore_index=True)
            else:
                df_all = df_fictional

            st.markdown("##### Longitudinal Vision Trend")
            st.caption("Tracking 8-question check results on a 0–8 scale. Fictional baseline and live user data are strictly distinguished.")

            line_chart = alt.Chart(df_fictional).mark_line(
                color="#94A3B8",
                strokeDash=[4, 4],
                strokeWidth=2
            ).encode(
                x=alt.X("Session:N", sort=None, title="Session / Timeline"),
                y=alt.Y(
                    "Correct:Q",
                    scale=alt.Scale(domain=[-0.5, 8.5]),
                    axis=alt.Axis(values=[0, 1, 2, 3, 4, 5, 6, 7, 8], title="Correct Responses (out of 8)")
                )
            )

            points_chart = alt.Chart(df_all).mark_point(
                size=180,
                filled=True
            ).encode(
                x=alt.X("Session:N", sort=None),
                y=alt.Y(
                    "Correct:Q",
                    scale=alt.Scale(domain=[-0.5, 8.5]),
                    axis=alt.Axis(values=[0, 1, 2, 3, 4, 5, 6, 7, 8])
                ),
                color=alt.Color(
                    "Type:N",
                    scale=alt.Scale(
                        domain=["Illustrative Demo Data", "Your Completed Demo Check"],
                        range=["#0284C7", "#EA580C"]
                    ),
                    legend=alt.Legend(
                        title="Data Classification",
                        orient="top",
                        direction="vertical",
                        columns=1,
                        labelLimit=350,
                        titleLimit=350
                    )
                ),
                shape=alt.Shape(
                    "Type:N",
                    scale=alt.Scale(
                        domain=["Illustrative Demo Data", "Your Completed Demo Check"],
                        range=["circle", "diamond"]
                    ),
                    legend=alt.Legend(
                        title="Data Classification",
                        orient="top",
                        direction="vertical",
                        columns=1,
                        labelLimit=350,
                        titleLimit=350
                    )
                ),
                tooltip=[
                    alt.Tooltip("Session:N", title="Session"),
                    alt.Tooltip("Date:N", title="Recorded Date"),
                    alt.Tooltip("Correct:Q", title="Correct Answers"),
                    alt.Tooltip("Total:Q", title="Total Questions"),
                    alt.Tooltip("Accuracy:Q", title="Accuracy %"),
                    alt.Tooltip("Type:N", title="Data Classification"),
                    alt.Tooltip("Notes:N", title="Context Notes")
                ]
            )

            final_chart = (line_chart + points_chart).properties(
                height=320,
                width="container"
            ).configure_axis(
                labelFontSize=11,
                titleFontSize=12
            )

            st.altair_chart(final_chart, **full_width())

            st.markdown(
                "<div style='font-size:0.8rem; color:inherit; opacity:0.85; margin-top:-8px; margin-bottom:16px;'>"
                "ℹ️ <em>Illustrative Baseline Notice: Historical entries (Weeks 1–7) represent fictional example data created for "
                "persona Riley and do not represent verified medical measurements. If completed, your live session score is displayed as "
                "an isolated comparison point and is not connected to historical data.</em>"
                "</div>",
                unsafe_allow_html=True
            )

            with st.expander("📋 View Complete Tabular Records", expanded=False):
                table_df = df_all[["Session", "Date", "Correct", "Total", "Accuracy", "Type", "Notes"]].copy()
                table_df["Accuracy"] = table_df["Accuracy"].apply(lambda v: f"{v}%")
                st.dataframe(table_df, hide_index=True, **full_width())

            st.markdown("##### ⚠️ Essential Non-Clinical Limitations")
            st.markdown("""<div class="info-card" style="border-left: 5px solid #0284C7; margin-top:8px;">
<strong style="color:inherit; font-size:0.95rem;">Understanding Vision Check Results:</strong>
<ul style="color:inherit; opacity:0.9; font-size:0.88rem; line-height:1.55; margin-top:8px; padding-left:18px;">
<li><strong>Snapshot Accuracy Only:</strong> Represents demonstration accuracy for one interactive test. Does not estimate 20/20, LogMAR, or refractive acuity.</li>
<li><strong>No Prescriptions or Medical Diagnosis:</strong> Cannot detect astigmatism, myopia, hyperopia, or organic ocular pathology.</li>
<li><strong>Uncalibrated Hardware:</strong> Display pixel pitch, brightness, and user viewing distance are not clinically calibrated.</li>
<li><strong>Professional Exam Needed:</strong> If you suspect vision changes, schedule an in-person exam with a licensed optometrist or ophthalmologist.</li>
</ul>
</div>""", unsafe_allow_html=True)

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
                "Please provide your objective perspective on the two presentation experiences above. "
                "Your feedback is anonymous and helps our product management team understand user preferences between "
                "single test results and ongoing trend tracking."
                "</span>",
                unsafe_allow_html=True
            )

            if not has_visited_both:
                st.markdown(
                    "<div class='info-card' style='border-radius:6px; padding:10px 14px; margin-top:10px; margin-bottom:12px; font-size:0.86rem; color:inherit; opacity:0.9;'>"
                    "ℹ️ <em>Please explore both Experience A and Experience B using the switcher above before submitting feedback.</em>"
                    "</div>",
                    unsafe_allow_html=True
                )

            with st.form("hypothesis_feedback_form"):
                q1_response = st.radio(
                    "1. Which format did you find more useful for monitoring your vision? *",
                    options=[
                        "Experience A (Single Result)",
                        "Experience B (Trend Tracking)",
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
                        "Experience A (Single Result)",
                        "Experience B (Trend Tracking)",
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
                        st.info("ℹ️ Please view both Experience A (Single Result) and Experience B (Trend Tracking) using the switcher above before submitting your comparative feedback.")
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
                            "evaluated_score": f"{current_correct}/{total_q}",
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
