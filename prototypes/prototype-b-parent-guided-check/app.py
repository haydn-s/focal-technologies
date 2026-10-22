"""Focal Family — independent Streamlit entry point for Prototype B."""

import json
from pathlib import Path

import streamlit as st

from demo import (
    NEXT_STEPS, OBSERVATIONS, QUESTION_OPTIONS, activity_counts, begin_activity, build_summary,
    fictional_example, follow_up_tasks, new_session, record_answer, record_practice_answer,
    refresh_parent_note, set_activity_paused,
)

SESSION_KEY = "focal_family"
ROOT = Path(__file__).resolve().parents[2]
STEPS = ("setup", "game", "observations", "summary")
STEP_LABELS = ("Get ready", "Play together", "Add observations", "Your next step")
CHOICE_GLYPHS = {"Circle": "●", "Square": "■", "Triangle": "▲", "Star": "★"}
SHAPES = {
    "Circle": '<circle cx="60" cy="60" r="37"/>',
    "Square": '<rect x="25" y="25" width="70" height="70" rx="3"/>',
    "Triangle": '<path d="M60 18 L105 100 L15 100 Z"/>',
    "Star": '<path d="M60 10 L73 43 L109 45 L81 68 L90 103 L60 83 L30 103 L39 68 L11 45 L47 43 Z"/>',
}


def reset():
    # All B widgets are namespaced so a reset removes only this demo's state.
    for key in list(st.session_state):
        if key.startswith("family_") or key == SESSION_KEY:
            del st.session_state[key]
    st.session_state[SESSION_KEY] = new_session()


def set_step(step):
    st.session_state[SESSION_KEY]["step"] = step


def answer(index, choice):
    record_answer(st.session_state[SESSION_KEY], index, choice)


def practice_answer(choice):
    record_practice_answer(st.session_state[SESSION_KEY], choice)


def start_picture_game():
    begin_activity(st.session_state[SESSION_KEY])


def pause_picture_game(paused):
    set_activity_paused(st.session_state[SESSION_KEY], paused)


def load_example():
    reset()
    st.session_state[SESSION_KEY] = fictional_example()


def download_requested():
    st.session_state[SESSION_KEY]["summary_download_requested"] = True


def save_message_draft():
    session = st.session_state[SESSION_KEY]
    session["message_draft"] = st.session_state.family_message_draft
    session["summary_revision"] = session.get("summary_revision", 0) + 1
    session["summary_download_requested"] = False


def render_setup(session):
    st.caption("FOR PARENTS AND CHILDREN · ABOUT TWO MINUTES")
    st.title("Make room for a conversation about vision")
    st.markdown(
        "Play a short picture game together, capture what you've noticed, "
        "and leave with a summary you can bring to an eye appointment."
    )
    left, right = st.columns([1.5, 1], gap="large")
    with left:
        with st.form("family_setup"):
            st.subheader("Who's joining you?")
            label = st.selectbox("Child label", ["Child 1", "Child 2", "Child 3"], key="family_label")
            age = st.radio("Age group", ["4–6", "7–10"], horizontal=True, key="family_age")
            glasses = st.radio(
                "Wearing their usual glasses?", ["Yes", "Does not usually wear glasses", "Not today"],
                key="family_glasses",
            )
            st.caption("Use a child label; no name, camera, or account is needed.")
            if st.form_submit_button("Let's play", type="primary", use_container_width=True):
                session["profile"] = {"label": label, "age_group": age, "glasses": glasses}
                session["step"] = "game"
                st.rerun()
    with right:
        st.subheader("A relaxed moment together")
        st.write("1. Sit comfortably so the pictures are easy to see.")
        st.write("2. Ask your child to point to or name the matching shape.")
        st.write("3. Tap their choice, or skip whenever they need a break.")
        st.info("This is a matching activity, not a vision screening. It cannot tell whether your child needs eye care.")
        st.button("Explore a fictional example", on_click=load_example, key="family_example")


def render_practice(session):
    st.caption("PLAY TOGETHER · PRACTICE")
    st.title("Try one picture together")
    st.write("This picture is a circle. Ask your child to point to it or say its name, then tap Circle below.")
    st.markdown(
        '<div class="picture-stage"><svg viewBox="0 0 120 120" width="150" height="150" '
        'role="img" aria-label="Practice circle"><g fill="#183c43">'
        + SHAPES["Circle"] + '</g></svg></div>', unsafe_allow_html=True,
    )
    for col, choice in zip(st.columns(4), CHOICE_GLYPHS):
        col.button(
            f"{CHOICE_GLYPHS[choice]} {choice}", key=f"family_practice_{choice}",
            on_click=practice_answer, args=(choice,), use_container_width=True,
        )
    if session.get("practice_complete"):
        st.success("That's it. You can help with the buttons, and skip a picture whenever your child wants.")
    elif session.get("practice_answer"):
        st.info("Try Circle for this practice picture. Practice is just for learning how the buttons work.")
    st.button(
        "Start the picture game", type="primary", key="family_begin_activity",
        disabled=not session.get("practice_complete"), on_click=start_picture_game,
        use_container_width=True,
    )
    st.caption("Practice is separate from the six-picture activity.")


def render_game(session):
    if not session.get("practice_dismissed"):
        render_practice(session)
        return
    index = len(session["answers"])
    total = len(session["questions"])
    if session.get("paused"):
        st.caption("TAKE A BREAK")
        st.title("Take the time you need")
        st.write("Your picture choices are saved for this visit. Resume whenever you're ready.")
        st.progress(index / total, text=f"{index} of {total} pictures explored")
        st.button(
            "Resume the picture game", type="primary", key="family_resume_activity",
            on_click=pause_picture_game, args=(False,), use_container_width=True,
        )
        return
    if index >= total:
        set_step("observations")
        st.rerun()
    question = session["questions"][index]
    st.caption(f"PLAY TOGETHER · PICTURE {index + 1} OF {total}")
    st.title("Can you find the same shape?")
    st.write("Ask your child to point or say their choice. You can tap it for them.")
    st.progress(index / total, text=f"{index} of {total} pictures explored")
    # These fixed-size shapes demonstrate the interaction; they are not optotypes.
    st.markdown(
        '<div class="picture-stage"><svg viewBox="0 0 120 120" width="150" height="150" '
        'role="img" aria-label="Picture to match"><g fill="#183c43">'
        + SHAPES[question["target"]] + '</g></svg></div>', unsafe_allow_html=True,
    )
    for col, choice in zip(st.columns(4), question["choices"]):
        col.button(
            f"{CHOICE_GLYPHS[choice]} {choice}", key=f"family_answer_{index}_{choice}", on_click=answer,
            args=(index, choice), use_container_width=True,
        )
    st.button("Skip this picture", key=f"family_skip_{index}", on_click=answer, args=(index, None))
    st.button("Take a break", key="family_pause_activity", on_click=pause_picture_game, args=(True,))
    st.caption("Every picture stays large. There is no timer, pass mark, or clinical result.")


def render_observations(session):
    st.caption("YOUR PERSPECTIVE")
    st.title("What have you noticed?")
    st.write("Your observations add context that a picture game cannot capture.")
    with st.form("family_observations"):
        st.markdown("**Select anything you have noticed. Leaving these blank is fine.**")
        selected = [
            observation for index, observation in enumerate(OBSERVATIONS)
            if st.checkbox(
                observation, value=observation in session["observations"],
                key=f"family_observation_{index}",
            )
        ]
        timing_options = ["Not sure", "During this activity only", "Within the past week", "Within the past month", "For longer than a month"]
        timing = st.selectbox(
            "When did you notice this?", timing_options,
            index=timing_options.index(session["timing"]), key="family_timing",
        )
        notes = st.text_area(
            "Anything else to bring up?", value=session["notes"], max_chars=800,
            placeholder="For example: moved closer to a book after school. Avoid names and identifying details.",
            key="family_notes",
        )
        next_step = st.radio(
            "What would you like to do next?", NEXT_STEPS,
            index=NEXT_STEPS.index(session["next_step"]) if session["next_step"] else None,
            key="family_next_step",
        )
        st.caption("This is your choice. The activity does not recommend a course of care.")
        if st.form_submit_button("Create my summary", type="primary", use_container_width=True):
            # Preserve all entered observations even when a next step is missing.
            session.update({"observations": selected, "timing": timing, "notes": notes.strip()})
            if next_step is None:
                st.info("Choose a next step, including 'I'm not sure yet', to shape your summary.")
            else:
                session["next_step"] = next_step
                refresh_parent_note(session)
                st.session_state.pop("family_message_draft", None)
                session["step"] = "summary"
                st.rerun()


def render_feedback(session):
    st.subheader("Help shape Focal Family")
    if session["feedback"] is not None:
        st.success("Your feedback is recorded in this session. Download a copy below to share with the team.")
        st.write(f"Usefulness: {session['feedback']['usefulness']}")
        st.write(f"Would use again: {session['feedback']['reuse']}")
        st.write(f"Next-step clarity: {session['feedback'].get('next_step_clarity', 'Not asked in this earlier session')}")
        st.json(session["feedback"], expanded=False)
    else:
        with st.form("family_feedback"):
            usefulness = st.radio(
                "How useful was this experience?",
                ["Not at all useful", "Slightly useful", "Moderately useful", "Very useful", "Extremely useful"],
                index=None, key="family_usefulness",
            )
            reuse = st.radio(
                "Would you use an experience like this again?",
                ["Yes", "No", "Not sure"], index=None, horizontal=True, key="family_reuse",
            )
            clarity = st.radio(
                "How clear is the next step you would take?",
                ["Very unclear", "Somewhat unclear", "Neither clear nor unclear", "Somewhat clear", "Very clear", "Not sure"],
                index=None, key="family_clarity",
            )
            barriers = st.text_area(
                "What, if anything, could make it difficult to follow through?",
                max_chars=800, key="family_barriers",
            )
            comment = st.text_area("What helped, or what was missing?", max_chars=800, key="family_comment")
            if st.form_submit_button("Save feedback", key="family_save_feedback"):
                if usefulness is None or reuse is None or clarity is None:
                    st.info("Please answer all three choice questions. Any answer is welcome.")
                else:
                    session["feedback"] = {
                        "usefulness": usefulness, "reuse": reuse, "comment": comment.strip(),
                        "next_step_clarity": clarity, "follow_through_barrier": barriers.strip(),
                        "evaluated_context": {
                            "source": session["source"],
                            "next_step": session["next_step"],
                            "observations": list(session["observations"]),
                            "notes": session["notes"],
                            "questions_to_ask": list(session.get("questions_to_ask", [])),
                            "custom_question": session.get("custom_question", ""),
                            "message_draft": session.get("message_draft", ""),
                            "activity": activity_counts(session),
                            "summary_revision": session.get("summary_revision", 0),
                            "summary_download_requested": session["summary_download_requested"],
                        },
                    }
                    st.rerun()
    st.download_button(
        "Download session and feedback", data=json.dumps(session, indent=2),
        file_name="focal-family-session.json", mime="application/json", key="family_session_export",
    )
    st.caption("Feedback is saved for this visit only. Download and share the file with the team to submit it.")


def render_summary(session):
    st.caption("A SUMMARY YOU CAN TAKE WITH YOU")
    st.title("Your observations, ready for the next conversation")
    st.write(f"**Your choice:** {session['next_step']}")
    left, right = st.columns([1.15, 1], gap="large")
    with left:
        st.subheader("What you noticed")
        if session["observations"]:
            for observation in session["observations"]:
                st.write(f"• {observation}")
        else:
            st.write("No observations selected.")
        st.write(f"**When:** {session['timing']}")
        if session["notes"]:
            st.write(session["notes"])
        counts = activity_counts(session)
        st.caption(
            f"Picture game: {counts['matched']} matched · {counts['skipped']} skipped "
            f"· {counts['completed']} of {counts['total']} explored"
        )
        st.info("The game is not a vision screening. A matching score cannot establish whether a child needs eye care.")
        st.button("Edit my observations", on_click=set_step, args=("observations",), key="family_edit")
    with right:
        st.subheader("Make your next step easier")
        for index, task in enumerate(follow_up_tasks(session["next_step"])):
            # Include the chosen route in the key so another route cannot inherit ticks.
            key = f"family_task_{NEXT_STEPS.index(session['next_step'])}_{index}"
            session["tasks"][task] = st.checkbox(task, value=session["tasks"].get(task, False), key=key)
    with st.expander("Add questions and prepare a message", expanded=False):
        st.write("Choose what you want to ask, then edit a note you can take to your next conversation.")
        with st.form("family_questions"):
            selected = st.multiselect(
                "Questions I'd like to ask", QUESTION_OPTIONS,
                default=session.get("questions_to_ask", []), key="family_question_selection",
            )
            custom = st.text_area(
                "A question of my own (optional)", value=session.get("custom_question", ""),
                max_chars=400, key="family_custom_question",
            )
            if st.form_submit_button("Update questions and regenerate draft"):
                session["questions_to_ask"] = selected
                session["custom_question"] = custom.strip()
                refresh_parent_note(session)
                st.session_state.pop("family_message_draft", None)
                st.rerun()
        if "family_message_draft" not in st.session_state:
            st.session_state.family_message_draft = session.get("message_draft", "")
        st.text_area(
            "My message draft", key="family_message_draft", height=230,
            on_change=save_message_draft, max_chars=3000,
        )
        st.caption("This is your draft. You decide what to share and whom to contact. Nothing is sent by the app.")
    download_col, note_col = st.columns(2)
    with download_col:
        st.download_button(
            "Download my summary", data=build_summary(session), file_name="focal-family-summary.txt",
            mime="text/plain", type="primary", use_container_width=True,
            on_click=download_requested, key="family_summary_export",
        )
    with note_col:
        st.download_button(
            "Download message draft", data=session.get("message_draft", ""),
            file_name="focal-family-parent-note.txt", mime="text/plain",
            key="family_note_export", use_container_width=True,
        )
    st.caption("Nothing is booked or sent. These downloads help you prepare.")
    with st.expander("Preview the take-home summary"):
        st.text(build_summary(session))
    st.divider()
    render_feedback(session)


def main():
    st.set_page_config(page_title="Focal Family | Parent check-in", page_icon="◉", layout="wide")
    if SESSION_KEY not in st.session_state:
        st.session_state[SESSION_KEY] = new_session()
    session = st.session_state[SESSION_KEY]
    st.markdown("""<style>
    .block-container { max-width: 1080px; padding-top: 4rem; padding-bottom: 3rem; }
    h1 { max-width: 820px; letter-spacing: -0.035em; }
    [data-testid="stSidebar"] [data-testid="stImage"] {
        background: white; border-radius: 12px; padding: 0.5rem;
    }
    .stButton > button, .stDownloadButton > button, .stFormSubmitButton > button {
        border-radius: 12px; min-height: 46px;
    }
    button[kind="primary"], button[kind="primaryFormSubmit"] {
        background-color: #276c66; border-color: #276c66; color: white;
    }
    [class*="st-key-family_answer_"] button p { font-size: 1.35rem; }
    .picture-stage { display: flex; justify-content: center; align-items: center;
        min-height: 240px; background: #fff; border: 1px solid #d5e3de;
        border-radius: 22px; margin: 1.1rem 0 1.5rem; }
    </style>""", unsafe_allow_html=True)
    with st.sidebar:
        logo = ROOT / "assets" / "brand" / "focal-lockup.svg"
        if logo.exists():
            st.image(str(logo), width=170)
        st.subheader("Focal Family")
        st.caption("Prototype B · Parent Pat")
        current = STEPS.index(session["step"])
        for index, label in enumerate(STEP_LABELS):
            st.write(f"{'●' if index == current else '✓' if index < current else '○'} {index + 1}. {label}")
        st.divider()
        st.write("A parent and child experience for capturing observations and preparing a next step.")
        st.caption("No account or camera. Session data clears when you start over or the app session ends.")
        st.button("Start over", on_click=reset, key="family_reset", use_container_width=True)
    if session["source"] == "fictional_example":
        st.warning("Fictional example: the child, activity responses, and observations below are made up. Start over to try your own session.")
    {
        "setup": render_setup,
        "game": render_game,
        "observations": render_observations,
        "summary": render_summary,
    }[session["step"]](session)
    st.caption("FOCAL TECHNOLOGIES · MENG 570 · Academic product prototype")


if __name__ == "__main__":
    main()
