"""Streamlit views for experimental checks and user-managed performance history."""

import csv
import io
from datetime import datetime

import pandas as pd
import altair as alt
import streamlit as st

from vision import (
    DIRECTIONS, EYES, GLASSES, PROFILES, SCREENS, comparison_key, export_history,
    fictional_history, import_history, new_check, record_response, save_check,
    size_px, summarize, window_summary,
)

ARROWS = {"up": "↑ Up", "right": "→ Right", "down": "↓ Down", "left": "← Left"}
ROTATIONS = {"right": 0, "down": 90, "left": 180, "up": 270}


def initialize():
    st.session_state.setdefault("vision_records", [])
    st.session_state.setdefault("vision_check", None)
    if "vision_examples" not in st.session_state:
        st.session_state.vision_examples = fictional_history()


def answer(index, choice):
    check = st.session_state.vision_check
    if check:
        record_response(check, index, choice)


def practice(choice):
    check = st.session_state.vision_check
    if check:
        check["practice_complete"] = choice == "right"


def set_paused(value):
    st.session_state.vision_check["paused"] = value


def restart():
    st.session_state.vision_check = None
    for key in list(st.session_state):
        if key.startswith("vision_confirm_") or key == "vision_practice_choice":
            del st.session_state[key]


def navigate_history():
    st.session_state.family_workspace = "Performance history"
    st.session_state.vision_dataset = "My saved checks"


def optotype(direction, px):
    # Five-unit E, without font rendering or responsive size scaling.
    rotation = ROTATIONS[direction]
    st.markdown(
        '<div style="height:190px;background:white;display:flex;align-items:center;justify-content:center;'
        'border:1px solid #d5e3de;border-radius:16px;margin:16px 0;overflow:auto">'
        f'<svg aria-label="Direction matching symbol" role="img" width="{px:.3f}" height="{px:.3f}" '
        f'style="width:{px:.3f}px;height:{px:.3f}px;flex-shrink:0" viewBox="0 0 5 5">'
        f'<g transform="rotate({rotation} 2.5 2.5)" fill="#111111">'
        '<path d="M0 0H5V1H1V2H5V3H1V4H5V5H0Z"/></g></svg></div>',
        unsafe_allow_html=True,
    )


def render_setup():
    st.write("A parent records which way the child says the E opens. Use a measured distance and the same setup each time.")
    left, right = st.columns(2)
    with left:
        profile = st.selectbox("Child label", PROFILES, key="vision_profile")
        eye = st.selectbox("Eyes used for this check", EYES, key="vision_eye")
        glasses = st.selectbox("Correction during this check", GLASSES, key="vision_glasses")
    with right:
        screen = st.selectbox("Screen setup label", SCREENS, key="vision_screen")
        distance = st.selectbox("Measured viewing distance", ("3 metres", "1.5 metres"), key="vision_distance")
    st.subheader("Match the reference width")
    st.write("Hold an 85.6 mm-wide card beside the bar and adjust its width. No photograph or card details are collected.")
    ref = st.slider("Reference width (CSS pixels)", 160, 600, 324, key="vision_reference")
    st.markdown(f'<div style="overflow-x:auto"><div style="box-sizing:border-box;width:{ref}px;height:24px;'
                'background:#286b70;border:2px solid #16234b"></div></div>', unsafe_allow_html=True)
    st.caption("Keep browser zoom and display settings unchanged after matching. Small screens may require horizontal scrolling.")
    ready = [st.checkbox(label, key=f"vision_confirm_{i}") for i, label in enumerate((
        "The bar matches the card width on this screen.",
        "We measured the viewing distance and will keep it fixed.",
        "The child understands directions. If testing one eye, the other is comfortably covered without pressure.",
        "I understand this experimental task cannot diagnose vision or replace professional screening.",
    ))]
    if st.button("Begin live check", disabled=not all(ready), type="primary", key="vision_begin"):
        st.session_state.vision_check = new_check({"profile": profile, "eye": eye, "glasses": glasses,
            "screen": screen, "distance_mm": 3000 if distance == "3 metres" else 1500, "reference_px": ref})
        st.rerun()


def render_check():
    initialize()
    st.title("Live vision task")
    st.caption("Experimental direction matching with calibrated size geometry. Parent assisted, no camera.")
    st.info("Results describe this task under your setup. They do not diagnose vision, determine a prescription or clear a child from follow-up care.")
    check = st.session_state.vision_check
    if check is None:
        render_setup()
        return
    s = check["setup"]
    st.caption(f"{s['profile']} · {s['eye']} · {s['screen']} · {s['distance_mm']/1000:g} m · {s['glasses']}")
    if check["completed_at"]:
        render_result(check)
        return
    if not check["practice_complete"]:
        st.subheader("Practice the directions")
        optotype("right", 95)
        st.write("This practice E opens to the right. Ask the child to point, then select Right.")
        for col, direction in zip(st.columns(4), DIRECTIONS):
            col.button(ARROWS[direction], key=f"vision_practice_{direction}", on_click=practice, args=(direction,))
        st.button("Discard this check", on_click=restart, key="vision_discard_practice")
        return
    if check["paused"]:
        st.subheader("Check paused")
        st.write("Responses stay in this session. Resume when the child is ready, using the same setup.")
        st.button("Resume check", on_click=set_paused, args=(False,), key="vision_resume")
    else:
        index = len(check["responses"])
        trial = check["trials"][index]
        st.progress(index/len(check["trials"]), text=f"Response {index+1} of {len(check['trials'])}")
        st.subheader("Which way does the E open?")
        optotype(trial["target"], size_px(trial["level"], s))
        for col, direction in zip(st.columns(4), DIRECTIONS):
            col.button(ARROWS[direction], key=f"vision_answer_{index}_{direction}", on_click=answer, args=(index, direction))
        st.button("Can't tell", key=f"vision_cant_{index}", on_click=answer, args=(index, "cant_tell"))
        st.button("Pause check", on_click=set_paused, args=(True,), key="vision_pause")
    st.button("Discard this check", on_click=restart, key="vision_discard")


def render_result(check):
    result = summarize(check)
    st.subheader("This check's performance")
    a, b = st.columns(2)
    a.metric("Correct directions", f"{result['correct']} / {result['total']}")
    b.metric("Task accuracy", f"{result['accuracy']:.1f}%")
    st.dataframe(result["levels"], hide_index=True, width="stretch")
    st.caption("20/x labels describe symbol geometry only. They are not an acuity score. Attention, assistance, chance and setup affect responses.")
    if any(r["id"] == check["id"] for r in st.session_state.vision_records):
        st.success("Saved once in this browser session. Export history to keep it after leaving.")
    elif st.button("Save this check to history", type="primary", key="vision_save"):
        try:
            save_check(st.session_state.vision_records, check)
            st.rerun()
        except ValueError as error:
            st.error(str(error))
    st.button("View performance history", on_click=navigate_history, key="vision_to_history")
    st.button("Start another check", on_click=restart, key="vision_another")
    st.write("Bring concerns and any existing referral to an eye-care professional. A high task score does not rule out an eye problem.")


def render_history():
    initialize()
    st.title("Performance over time")
    st.write("Compare direction-matching performance for the same child, eye and setup.")
    dataset = st.radio("History source", ("My saved checks", "Fictional example history"), key="vision_dataset", horizontal=True)
    example = dataset == "Fictional example history"
    if example:
        st.warning("Fictional example history: every date and response below is made up. This does not show improvement in a real child's vision.")
        records = st.session_state.vision_examples
    else:
        records = st.session_state.vision_records
        st.caption("History stays in this browser session. Download a JSON copy and restore it on a future visit. No shared patient database.")
        with st.expander("Restore a saved history file"):
            uploaded = st.file_uploader("Focal history JSON", type="json", max_upload_size=5, key="vision_upload")
            if st.button("Import history", disabled=uploaded is None, key="vision_import"):
                try:
                    merged = import_history(uploaded.getvalue(), records)
                    added = len(merged)-len(records)
                    st.session_state.vision_records = merged
                    records = merged
                    st.success(f"Restored {added} additional checks. Duplicate records were not added.")
                except (ValueError, RecursionError) as error:
                    st.error(str(error))
        st.download_button("Download history JSON", export_history(records), "focal-family-history.json", "application/json", key="vision_export_json")
    if not records:
        st.info("No saved live checks yet. Complete a live task and save the result, or choose the fictional example to explore the chart.")
        return
    profiles = sorted({r["setup"]["profile"] for r in records})
    if st.session_state.get("vision_history_profile") not in profiles:
        st.session_state.pop("vision_history_profile", None)
    profile = st.selectbox("Child", profiles, key="vision_history_profile")
    child_records = [r for r in records if r["setup"]["profile"] == profile]
    groups = {}
    for r in child_records:
        groups.setdefault(comparison_key(r), []).append(r)
    def label(key):
        _, _, _, eye, glasses, screen, distance, ref = key
        return f"{eye} / {glasses} / {screen} / {distance/1000:g} m / {ref} px reference"
    group_key = f"vision_history_setup_{'example' if example else 'live'}_{profile}"
    if st.session_state.get(group_key) not in groups:
        st.session_state.pop(group_key, None)
    group = st.selectbox("Comparable setup", list(groups), format_func=label, key=group_key)
    window = st.selectbox("Time window", ("7 days", "30 days", "90 days", "All time"), index=1, key="vision_window")
    days = None if window == "All time" else int(window.split()[0])
    summary = window_summary(groups[group], days)
    a, b, c = st.columns(3)
    a.metric("Checks in window", summary["count"])
    b.metric("Average task accuracy", "—" if summary["average"] is None else f"{summary['average']:.1f}%")
    c.metric("Change vs previous window", "—" if summary["delta_points"] is None else f"{summary['delta_points']:+.1f} points")
    st.caption(f"Previous equal window: {summary['previous_count']} checks. Dates use UTC. Comparisons require the same correction, distance and reference width.")
    rows = [{"Date (UTC)": datetime.fromisoformat(r["completed_at"]),
             "Task accuracy (%)": round(summarize(r)["accuracy"], 1),
             "Correct": summarize(r)["correct"], "Trials": 12,
             "Source": "Fictional example" if example else "Live task"} for r in summary["records"]]
    if rows:
        frame = pd.DataFrame(rows)
        chart = alt.Chart(frame).mark_line(point=True).encode(
            x=alt.X("Date (UTC):T", scale=alt.Scale(type="utc")),
            y=alt.Y("Task accuracy (%):Q", scale=alt.Scale(domain=[0, 100])),
            tooltip=[alt.Tooltip("Date (UTC):T", format="%Y-%m-%d %H:%M UTC"), "Task accuracy (%):Q"],
        ).properties(height=230)
        st.altair_chart(chart, width="stretch")
        st.dataframe(frame, hide_index=True, width="stretch")
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
        st.download_button("Download this window CSV", buffer.getvalue(), "focal-family-performance.csv", "text/csv", key="vision_export_csv")
    else:
        st.info("No checks in this window. Choose a longer window or complete another live check.")
    st.info("A change in task accuracy can reflect attention, guessing, learning or setup. It does not establish a change in eyesight.")
    if not example:
        confirm = st.checkbox("Delete all saved live checks in this browser session", key="vision_delete_confirm")
        if st.button("Clear saved history", disabled=not confirm, key="vision_clear"):
            st.session_state.vision_records = []
            st.rerun()
