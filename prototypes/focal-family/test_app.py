"""
Tests for the Focal Family master prototype.
Covers the parent-note logic, history compatibility with Prototype B, and every clickable
path through the app with Streamlit's AppTest (no browser needed).

Run: python -m unittest discover -p 'test_*.py'
"""

import json
import os
import random
import unittest
from datetime import timedelta

from streamlit.testing.v1 import AppTest

import dmv
import family as fam
import vision

APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
SETUP = {"profile": "Child A", "eye": "Both eyes", "glasses": vision.GLASSES[1], "screen": vision.SCREENS[0],
         "distance_mm": 3000, "reference_px": 324}


def completed_check(correct=12, seed=0, minutes_ago=5):
    now = vision.utc_now()
    check = vision.new_check(SETUP, now - timedelta(minutes=minutes_ago), random.Random(seed))
    check["practice_complete"] = True
    for i, trial in enumerate(check["trials"]):
        choice = trial["target"] if i < correct else "cant_tell"
        vision.record_response(check, i, choice, now - timedelta(minutes=minutes_ago) + timedelta(seconds=i + 1))
    return check


class TestNextStepLogic(unittest.TestCase):
    def test_school_letter_and_concerns_suggest_an_appointment(self):
        for reason in fam.REASONS[:3]:
            self.assertEqual(fam.suggested_next_step(reason), fam.NEXT_STEPS[0])
        self.assertEqual(fam.suggested_next_step(fam.REASONS[3]), fam.NEXT_STEPS[2])

    def test_referral_is_flagged_and_never_cancelled(self):
        self.assertTrue(fam.concern_already_raised(fam.REASONS[0]))
        self.assertTrue(fam.concern_already_raised(fam.REASONS[1]))
        self.assertFalse(fam.concern_already_raised(fam.REASONS[2]))

    def test_suggestion_ignores_the_task_score(self):
        # The suggestion takes only the reason: there is no way to pass a score in.
        import inspect
        self.assertEqual(list(inspect.signature(fam.suggested_next_step).parameters), ["reason"])

    def test_every_next_step_has_a_plan(self):
        for step in fam.NEXT_STEPS:
            self.assertGreaterEqual(len(fam.follow_up_tasks(step)), 2)


class TestParentMessage(unittest.TestCase):
    def base_note(self, **overrides):
        note = {"child": "Child A", "age_group": "7–10", "reason": fam.REASONS[0],
                "observations": [fam.OBSERVATIONS[0]], "timing": fam.TIMING[1], "notes": "",
                "next_step": fam.NEXT_STEPS[0], "recipient": fam.RECIPIENTS[0], "questions": [],
                "custom_question": "", "include_check": True, "tasks": {}}
        note.update(overrides)
        return note

    def test_nurse_message_follows_up_on_the_letter(self):
        text = fam.build_message(self.base_note())
        self.assertIn("vision screening letter", text)
        self.assertIn(fam.OBSERVATIONS[0], text)
        self.assertIn("what follow-up you recommend", text)

    def test_eye_doctor_message_asks_about_coverage(self):
        text = fam.build_message(self.base_note(recipient=fam.RECIPIENTS[1]))
        self.assertIn("arrange an eye appointment", text)
        self.assertIn("vision coverage", text)

    def test_check_result_is_always_labelled_not_a_screening(self):
        summary = vision.summarize(completed_check(9))
        text = fam.build_message(self.base_note(), summary)
        self.assertIn("not a vision screening", text)
        self.assertIn("9 of 12", text)
        self.assertNotIn("not a vision screening", fam.build_message(self.base_note(include_check=False), summary))

    def test_questions_include_a_custom_one(self):
        text = fam.build_message(self.base_note(questions=[fam.QUESTION_OPTIONS[1]], custom_question=" Is it urgent? "))
        self.assertIn(fam.QUESTION_OPTIONS[1], text)
        self.assertIn("- Is it urgent?", text)

    def test_fictional_note_is_labelled_everywhere(self):
        example = fam.fictional_note()
        message = fam.build_message(example)
        self.assertTrue(message.startswith("FICTIONAL EXAMPLE"))
        self.assertIn("Fictional example", fam.build_summary(example, message))

    def test_summary_states_its_limits(self):
        note = self.base_note(tasks={fam.follow_up_tasks(fam.NEXT_STEPS[0])[0]: True})
        text = fam.build_summary(note, "msg", vision.summarize(completed_check(10)), None, "In 3 days")
        self.assertIn("Not a vision screening, diagnosis or medical result", text)
        self.assertIn("cancel a school or professional referral", text)
        self.assertIn("[x] " + fam.follow_up_tasks(fam.NEXT_STEPS[0])[0], text)
        self.assertIn("no reminder is actually sent", text)


class TestHistoryCompatibility(unittest.TestCase):
    def test_engine_matches_prototype_b(self):
        here = os.path.dirname(os.path.abspath(__file__))
        b_path = os.path.join(here, "..", "prototype-b-parent-guided-check", "vision.py")
        if not os.path.exists(b_path):
            self.skipTest("Prototype B is not in this checkout")
        with open(os.path.join(here, "vision.py")) as f:
            ours = f.read().split('"""', 2)[2]
        with open(b_path) as f:
            theirs = f.read().split('"""', 2)[2]
        self.assertEqual(ours, theirs, "vision.py should stay identical to Prototype B's engine")

    def test_history_round_trip(self):
        records = []
        vision.save_check(records, completed_check(11, seed=1))
        restored = vision.import_history(vision.export_history(records), [])
        self.assertEqual(len(restored), 1)
        self.assertEqual(vision.summarize(restored[0])["correct"], 11)

    def test_fictional_history_cannot_be_imported_as_live(self):
        payload = json.dumps({"schema": "focal-family-history-v1", "records": vision.fictional_history()[:1]})
        with self.assertRaises(ValueError):
            vision.import_history(payload, [])


class TestDmvLogic(unittest.TestCase):
    def test_state_lines(self):
        self.assertEqual([l["denominator"] for l in dmv.build_test_lines(40)], [70, 50, 40, 30])
        self.assertEqual([l["denominator"] for l in dmv.build_test_lines(60)], [100, 70, 60, 50])
        self.assertEqual(dmv.STATES["Georgia"]["line"], 60)
        self.assertEqual(dmv.STATES["New Jersey"]["line"], 50)

    def test_scoring_thresholds_and_honest_retake(self):
        items = dmv.generate_items(dmv.build_test_lines(40), random.Random(3))

        def answers(correct_at_line):
            out, seen = {}, 0
            for i, item in enumerate(items):
                if item["role"] == "state line":
                    out[i] = item["direction"] if seen < correct_at_line else dmv.CANT_TELL
                    seen += 1
                elif item["role"] != "margin":
                    out[i] = item["direction"]
            return out

        self.assertEqual(dmv.score_attempt(items, answers(5))["verdict"], "on_track")
        self.assertEqual(dmv.score_attempt(items, answers(4))["verdict"], "close")
        self.assertEqual(dmv.score_attempt(items, answers(3))["verdict"], "not_yet")
        self.assertEqual(dmv.overall_result([{"verdict": "not_yet"}, {"verdict": "on_track"}])["verdict"], "mixed")


class TestLook(unittest.TestCase):
    def test_theme_is_light_and_only_for_this_app(self):
        # The look follows the team's React UI. It must stay light on a dark-mode laptop, and live
        # next to app.py so Prototypes A, B and C keep their own themes.
        import tomllib
        here = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(here, ".streamlit", "config.toml"), "rb") as handle:
            theme = tomllib.load(handle)["theme"]
        self.assertEqual(theme["base"], "light")
        self.assertEqual(theme["primaryColor"], "#10265F")
        self.assertFalse(os.path.exists(os.path.join(here, "..", "..", ".streamlit", "config.toml")))


# -----------------------------------------------------------------------------
# Clickable flows
# -----------------------------------------------------------------------------
def all_markdown(at):
    return " ".join(m.value for m in at.markdown)


def go_to_check(at):
    at.button(key="btn_start").click().run()
    for i in range(4):
        at.checkbox(key=f"chk_{i}").check().run()
    at.button(key="btn_begin").click().run()
    at.button(key="prac_right").click().run()


def answer_all(at, correct=12):
    for i in range(12):
        check = at.session_state["check"]
        trial = check["trials"][len(check["responses"])]
        at.button(key=f"ans_{trial['target']}" if i < correct else "ans_cant_tell").click().run()


def go_to_dmv_check(at, state=None):
    at.button(key="btn_dmv").click().run()
    if state:
        at.selectbox(key="d_state").select(state).run()
    for i in range(3):
        at.checkbox(key=f"dchk_{i}").check().run()
    at.button(key="btn_dmv_begin").click().run()


def dmv_answer_all(at, correct_at_line=6):
    seen = 0
    for _ in range(20):
        if at.session_state["page"] != "dmv_check":
            return
        item = at.session_state["dmv_items"][at.session_state["dmv_idx"]]
        key = f"dmv_ans_{item['direction']}"
        if item["role"] == "state line":
            if seen >= correct_at_line:
                key = "dmv_ans_cant_tell"
            seen += 1
        at.button(key=key).click().run()
    raise AssertionError("DMV check never finished")


class TestClickableFlow(unittest.TestCase):
    def new_app(self):
        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        self.assertFalse(at.exception)
        return at

    def test_scroll_helper_changes_on_every_page(self):
        # A repeated script lets the browser reuse the old frame, so the new page wouldn't open at the top.
        at = self.new_app()
        at.button(key="btn_start").click().run()
        at.button(key="nav_welcome").click().run()
        self.assertEqual(at.session_state["scroll_count"], 3)

    def test_projector_sized_calibration_works(self):
        # On a projector a bank card spans only a few dozen pixels.
        at = self.new_app()
        at.button(key="btn_start").click().run()
        at.slider(key="w_card").set_value(30).run()
        for _ in range(5):
            at.button(key="btn_card_minus").click().run()
        self.assertEqual(at.session_state["w_card"], 24)  # never below the minimum
        at.button(key="btn_card_plus").click().run()
        self.assertEqual(at.session_state["w_card"], 26)
        for i in range(4):
            at.checkbox(key=f"chk_{i}").check().run()
        at.button(key="btn_begin").click().run()
        at.button(key="prac_right").click().run()
        answer_all(at, correct=12)
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["check"]["setup"]["reference_px"], 26)
        self.assertIn("matched 12 of 12 directions", all_markdown(at))

    def test_welcome_speaks_to_parents(self):
        at = self.new_app()
        text = all_markdown(at)
        self.assertIn("Got a school vision letter?", text)
        self.assertIn("Free for families", text)

    def test_setup_locks_until_confirmed_and_practice_must_be_right(self):
        at = self.new_app()
        at.button(key="btn_start").click().run()
        self.assertTrue(at.button(key="btn_begin").disabled)
        for i in range(4):
            at.checkbox(key=f"chk_{i}").check().run()
        at.button(key="btn_begin").click().run()
        self.assertEqual(at.session_state["page"], "practice")
        at.button(key="prac_left").click().run()
        self.assertEqual(at.session_state["page"], "practice")
        self.assertTrue(at.session_state["practice_miss"])
        at.button(key="prac_right").click().run()
        self.assertEqual(at.session_state["page"], "check")

    def test_demo_path_check_save_history_note(self):
        at = self.new_app()
        go_to_check(at)
        answer_all(at, correct=10)
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["page"], "result")
        text = all_markdown(at)
        self.assertIn("matched 10 of 12 directions", text)
        self.assertIn("Keep the follow-up you were asked for", text)

        at.button(key="btn_save").click().run()
        self.assertEqual(at.session_state["page"], "history")
        self.assertEqual(len(at.session_state["records"]), 1)
        # Saving twice never duplicates
        at.button(key="btn_history_another").click().run()
        at.session_state["page"] = "result"
        at.run()
        at.button(key="btn_save").click().run()
        self.assertEqual(len(at.session_state["records"]), 1)

        at.button(key="btn_history_note").click().run()
        self.assertEqual(at.session_state["page"], "note")
        message = at.text_area(key="n_message").value
        self.assertIn("vision screening letter", message)
        self.assertIn("10 of 12", message)

    def test_cant_tell_counts_as_a_miss(self):
        at = self.new_app()
        go_to_check(at)
        answer_all(at, correct=0)
        self.assertIn("matched 0 of 12 directions", all_markdown(at))

    def test_pause_keeps_the_place(self):
        at = self.new_app()
        go_to_check(at)
        check = at.session_state["check"]
        at.button(key=f"ans_{check['trials'][0]['target']}").click().run()
        at.button(key="btn_pause").click().run()
        self.assertIn("Paused", all_markdown(at))
        at.button(key="btn_resume").click().run()
        self.assertEqual(len(at.session_state["check"]["responses"]), 1)
        self.assertIn("Letter 2 of 12", all_markdown(at))

    def test_setup_choices_survive_the_check(self):
        at = self.new_app()
        at.button(key="btn_start").click().run()
        at.selectbox(key="w_child").select("Child B").run()
        at.radio(key="w_reason").set_value(fam.REASONS[3]).run()
        for i in range(4):
            at.checkbox(key=f"chk_{i}").check().run()
        at.button(key="btn_begin").click().run()
        at.button(key="prac_right").click().run()
        answer_all(at)
        self.assertEqual(at.session_state["check"]["setup"]["profile"], "Child B")
        self.assertEqual(at.session_state["w_reason"], fam.REASONS[3])
        self.assertNotIn("Keep the follow-up you were asked for", all_markdown(at))

    def test_fictional_history_stays_separate(self):
        at = self.new_app()
        at.button(key="btn_welcome_history").click().run()
        self.assertIn("No saved checks yet", all_markdown(at))
        at.radio(key="h_dataset").set_value("Fictional example").run()
        self.assertFalse(at.exception)
        self.assertIn("Fictional example.", all_markdown(at))
        for window in ("7 days", "30 days", "90 days", "All time"):
            at.radio(key="h_window").set_value(window).run()
            self.assertFalse(at.exception, window)
        self.assertEqual(at.session_state["records"], [])

    def test_note_draft_follows_answers_until_edited(self):
        at = self.new_app()
        at.button(key="btn_welcome_note").click().run()
        self.assertNotIn(fam.OBSERVATIONS[1], at.text_area(key="n_message").value)
        at.checkbox(key="n_obs_1").check().run()
        self.assertIn(fam.OBSERVATIONS[1], at.text_area(key="n_message").value)
        at.text_area(key="n_message").input("My own words.").run()
        at.checkbox(key="n_obs_2").check().run()
        self.assertEqual(at.text_area(key="n_message").value, "My own words.")
        at.button(key="btn_rewrite").click().run()
        self.assertIn(fam.OBSERVATIONS[2], at.text_area(key="n_message").value)

    def test_fictional_note_loads_and_clears(self):
        at = self.new_app()
        at.button(key="btn_welcome_note").click().run()
        at.button(key="btn_example").click().run()
        self.assertTrue(at.session_state["note_fictional"])
        self.assertTrue(at.text_area(key="n_message").value.startswith("FICTIONAL EXAMPLE"))
        at.button(key="btn_clear_example").click().run()
        self.assertFalse(at.session_state["note_fictional"])
        self.assertFalse(at.text_area(key="n_message").value.startswith("FICTIONAL EXAMPLE"))

    def test_reminder_is_simulated(self):
        at = self.new_app()
        at.button(key="btn_welcome_note").click().run()
        at.button(key="btn_remind_In 3 days").click().run()
        self.assertEqual(at.session_state["reminder"], "In 3 days")
        self.assertTrue(any("no reminder is actually sent" in s.value for s in at.success))

    def test_dmv_is_a_secondary_option_on_the_welcome_page(self):
        at = self.new_app()
        text = all_markdown(at)
        self.assertIn("Also from Focal", text)
        self.assertLess(text.index("Got a school vision letter?"), text.index("Also from Focal"))

    def test_dmv_georgia_uses_its_own_line_and_can_pass(self):
        at = self.new_app()
        at.button(key="btn_dmv").click().run()
        at.selectbox(key="d_state").select("Georgia").run()
        self.assertIn("20/60", all_markdown(at))
        for i in range(3):
            at.checkbox(key=f"dchk_{i}").check().run()
        at.button(key="btn_dmv_begin").click().run()
        dmv_answer_all(at, 6)
        self.assertFalse(at.exception)
        text = all_markdown(at)
        self.assertIn("On track for Georgia's vision screening", text)
        self.assertIn("20/60 · Georgia's line", text)

    def test_dmv_miss_gives_a_plan_and_one_honest_retake(self):
        at = self.new_app()
        go_to_dmv_check(at, "New Jersey")
        dmv_answer_all(at, 2)
        text = all_markdown(at)
        self.assertIn("Might not pass New Jersey's screening yet", text)
        self.assertIn("ST-14", text)
        at.button(key="btn_dmv_retake").click().run()
        for i in range(3):
            at.checkbox(key=f"dchk_{i}").check().run()
        at.button(key="btn_dmv_begin").click().run()
        dmv_answer_all(at, 6)
        self.assertIn("The two checks didn't agree", all_markdown(at))
        self.assertEqual(len([b for b in at.button if b.key == "btn_dmv_retake"]), 0)

    def test_dmv_does_not_touch_family_history(self):
        at = self.new_app()
        go_to_dmv_check(at)
        dmv_answer_all(at, 6)
        at.button(key="btn_dmv_result_home").click().run()
        self.assertEqual(at.session_state["page"], "welcome")
        self.assertEqual(at.session_state["records"], [])
        # Starting the DMV check again from home starts fresh, not as a retake
        at.button(key="btn_dmv").click().run()
        self.assertEqual(at.session_state["dmv_attempts"], [])

    def test_start_over_resets_everything(self):
        at = self.new_app()
        go_to_check(at)
        answer_all(at)
        at.button(key="btn_save").click().run()
        at.button(key="btn_history_note").click().run()
        at.button(key="btn_note_restart").click().run()
        self.assertEqual(at.session_state["page"], "welcome")
        self.assertEqual(at.session_state["records"], [])
        self.assertIsNone(at.session_state["check"])


if __name__ == "__main__":
    unittest.main()
