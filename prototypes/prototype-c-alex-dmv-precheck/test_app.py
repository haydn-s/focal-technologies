"""
Tests for Focal DMV Pre-Check (Prototype C).
Covers the scoring logic, letter sizing, state rules, and the full clickable flow
using Streamlit's AppTest (no browser needed).

Run: python -m unittest test_app.py
"""

import os
import random
import unittest

from streamlit.testing.v1 import AppTest

import app

APP_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")


def answers_for(items, correct_at_state_line, rng=None):
    """All answers right except at the state line, where only `correct_at_state_line` are right."""
    answers = {}
    state_seen = 0
    for idx, item in enumerate(items):
        if item["role"] == "state line":
            if state_seen < correct_at_state_line:
                answers[idx] = item["direction"]
            else:
                answers[idx] = app.CANT_TELL
            state_seen += 1
        else:
            answers[idx] = item["direction"]
    return answers


class TestTestDesign(unittest.TestCase):
    def test_lines_around_state_line(self):
        lines = app.build_test_lines(40)
        self.assertEqual([l["denominator"] for l in lines], [70, 50, 40, 30])
        self.assertEqual([l["letters"] for l in lines], [2, 3, 6, 3])
        self.assertEqual([l["role"] for l in lines], ["warm-up", "warm-up", "state line", "margin"])

    def test_georgia_slots_a_20_60_line_into_the_ladder(self):
        lines = app.build_test_lines(60)
        self.assertEqual([l["denominator"] for l in lines], [100, 70, 60, 50])
        self.assertEqual([l["letters"] for l in lines], [2, 2, 6, 3])
        # Adding Georgia's line must not change the 20/40 test
        self.assertEqual([l["denominator"] for l in app.build_test_lines(40)], [70, 50, 40, 30])

    def test_new_jersey_uses_a_20_50_line(self):
        lines = app.build_test_lines(50)
        self.assertEqual([l["denominator"] for l in lines], [100, 70, 50, 40])
        self.assertEqual([l["role"] for l in lines], ["warm-up", "warm-up", "state line", "margin"])

    def test_items_have_no_repeats_in_a_row_and_cover_all_directions_at_state_line(self):
        for seed in range(200):
            items = app.generate_items(app.build_test_lines(40), random.Random(seed))
            self.assertEqual(len(items), 14)
            for line_idx in range(4):
                dirs = [it["direction"] for it in items if it["line_idx"] == line_idx]
                self.assertTrue(all(a != b for a, b in zip(dirs, dirs[1:])), f"repeat in seed {seed}")
            state_dirs = {it["direction"] for it in items if it["role"] == "state line"}
            self.assertEqual(state_dirs, set(app.DIRECTIONS))

    def test_checks_differ_between_attempts(self):
        a = [it["direction"] for it in app.generate_items(app.build_test_lines(40), random.Random(1))]
        b = [it["direction"] for it in app.generate_items(app.build_test_lines(40), random.Random(2))]
        self.assertNotEqual(a, b, "Each check should use a new letter order so it can't be memorized")


class TestLetterSizing(unittest.TestCase):
    def test_standard_snellen_size(self):
        # A 20/20 letter seen from 20 feet (6096 mm) is about 8.87 mm tall.
        self.assertAlmostEqual(app.letter_height_mm(20, 6096), 8.87, places=2)

    def test_scales_with_line_and_distance(self):
        self.assertAlmostEqual(app.letter_height_mm(40, 3048), 2 * app.letter_height_mm(20, 3048), places=4)
        self.assertAlmostEqual(app.letter_height_mm(40, 1524), app.letter_height_mm(40, 3048) / 2, places=6)

    def test_card_calibration_converts_to_pixels(self):
        mm = app.letter_height_mm(40, 3048)
        px = app.letter_height_px(40, 3048, card_px=app.CARD_WIDTH_MM * 4)  # 4 px per mm
        self.assertAlmostEqual(px, mm * 4, places=6)

    def test_smallest_letter_is_renderable(self):
        # Even at 5 feet on the smallest calibration, the 20/30 E stays above 5 px.
        px = app.letter_height_px(30, app.DISTANCES["5 feet (about 1.5 meters)"], card_px=180)
        self.assertGreater(px, 5)


class TestScoring(unittest.TestCase):
    def setUp(self):
        self.items = app.generate_items(app.build_test_lines(40), random.Random(7))

    def test_all_correct_is_on_track_with_margin(self):
        result = app.score_attempt(self.items, answers_for(self.items, 6))
        self.assertEqual(result["verdict"], "on_track")
        self.assertTrue(result["margin_read"])
        self.assertEqual(result["state_correct"], 6)

    def test_five_of_six_is_on_track(self):
        self.assertEqual(app.score_attempt(self.items, answers_for(self.items, 5))["verdict"], "on_track")

    def test_four_of_six_is_close(self):
        answers = answers_for(self.items, 4)
        # The margin line is not shown after a non-pass
        for idx, it in enumerate(self.items):
            if it["role"] == "margin":
                answers.pop(idx)
        result = app.score_attempt(self.items, answers)
        self.assertEqual(result["verdict"], "close")
        self.assertFalse(result["margin_read"])
        margin = [l for l in result["lines"] if l["role"] == "margin"][0]
        self.assertEqual(margin["status"], "skipped")

    def test_three_or_fewer_is_not_yet(self):
        for correct in range(0, 4):
            self.assertEqual(app.score_attempt(self.items, answers_for(self.items, correct))["verdict"], "not_yet")

    def test_cant_tell_counts_as_not_read(self):
        answers = {i: app.CANT_TELL for i in range(len(self.items))}
        result = app.score_attempt(self.items, answers)
        self.assertEqual(result["state_correct"], 0)
        self.assertEqual(result["verdict"], "not_yet")

    def test_margin_line_only_after_clear_pass(self):
        state_idx = [i for i, it in enumerate(self.items) if it["role"] == "state line"]
        last_state = state_idx[-1]
        passing = answers_for(self.items, 6)
        failing = answers_for(self.items, 4)
        passing_so_far = {i: a for i, a in passing.items() if i <= last_state}
        failing_so_far = {i: a for i, a in failing.items() if i <= last_state}
        self.assertEqual(app.next_item_index(self.items, passing_so_far, last_state), last_state + 1)
        self.assertIsNone(app.next_item_index(self.items, failing_so_far, last_state))

    def test_pure_guessing_rarely_passes(self):
        rng = random.Random(0)
        passes = 0
        trials = 4000
        for _ in range(trials):
            answers = {i: rng.choice(app.DIRECTIONS) for i in range(len(self.items))}
            if app.score_attempt(self.items, answers)["verdict"] == "on_track":
                passes += 1
        self.assertLess(passes / trials, 0.02, "A guesser should almost never be told they're on track")


class TestOverallResult(unittest.TestCase):
    def test_single_attempt(self):
        self.assertEqual(app.overall_result([{"verdict": "close"}]), {"verdict": "close", "consistency": "single"})

    def test_retake_that_agrees(self):
        r = app.overall_result([{"verdict": "on_track"}, {"verdict": "on_track"}])
        self.assertEqual(r, {"verdict": "on_track", "consistency": "consistent"})

    def test_retake_never_keeps_the_better_score(self):
        r = app.overall_result([{"verdict": "not_yet"}, {"verdict": "on_track"}])
        self.assertEqual(r["verdict"], "mixed")

    def test_two_non_passes_share_a_next_step(self):
        r = app.overall_result([{"verdict": "close"}, {"verdict": "not_yet"}])
        self.assertEqual(r, {"verdict": "not_yet", "consistency": "same_next_step"})


class TestStateRules(unittest.TestCase):
    def test_every_state_is_complete(self):
        required = {"abbr", "possessive", "line", "rule", "glasses", "if_missed", "bring", "source_name", "source_url"}
        for name, state in app.STATES.items():
            self.assertTrue(required <= set(state), name)
            lines = app.build_test_lines(state["line"])
            self.assertEqual([l["role"] for l in lines], ["warm-up", "warm-up", "state line", "margin"], name)
            # The rule card must name the line the check actually tests
            self.assertIn(f"20/{state['line']}", state["rule"], name)
            if state["source_url"]:
                self.assertTrue(state["source_url"].startswith("https://"), name)

    def test_summary_text_is_honest(self):
        items = app.generate_items(app.build_test_lines(40), random.Random(3))
        attempt = app.score_attempt(items, answers_for(items, 6))
        text = app.build_summary_text("California", [attempt], app.overall_result([attempt]),
                                      app.GLASSES_OPTIONS[0], list(app.DISTANCES)[0], "Oct 21, 2026")
        self.assertIn("not an official or medical result", text)
        self.assertIn("California", text)
        self.assertIn("6 of 6", text)


# -----------------------------------------------------------------------------
# End-to-end flow with Streamlit AppTest
# -----------------------------------------------------------------------------
def all_markdown(at):
    return " ".join(m.value for m in at.markdown)


def go_to_check(at, state="North Carolina"):
    at.button(key="btn_start").click().run()
    if state != "North Carolina":
        at.selectbox(key="w_state").select(state).run()
    for key in app.SETUP_CHECKLIST:
        at.checkbox(key=key).check().run()
    at.button(key="btn_begin").click().run()


def answer_until_done(at, correct_at_state_line):
    state_seen = 0
    for _ in range(30):
        if at.session_state["page"] != "check":
            return
        item = at.session_state["check_items"][at.session_state["item_idx"]]
        if item["role"] == "state line":
            key = f"ans_{item['direction']}" if state_seen < correct_at_state_line else "ans_cant_tell"
            state_seen += 1
        else:
            key = f"ans_{item['direction']}"
        at.button(key=key).click().run()
    raise AssertionError("Check never finished")


class TestClickableFlow(unittest.TestCase):
    def new_app(self):
        at = AppTest.from_file(APP_PATH, default_timeout=30)
        at.run()
        self.assertFalse(at.exception)
        return at

    def test_welcome_page_explains_itself(self):
        at = self.new_app()
        text = all_markdown(at)
        self.assertIn("Will you pass the DMV eye test?", text)
        self.assertIn("Free · no sign-up · no ads", text)

    def test_start_is_locked_until_setup_is_confirmed(self):
        at = self.new_app()
        at.button(key="btn_start").click().run()
        self.assertTrue(at.button(key="btn_begin").disabled)
        for key in app.SETUP_CHECKLIST:
            at.checkbox(key=key).check().run()
        self.assertFalse(at.button(key="btn_begin").disabled)

    def test_passing_flow_then_feedback(self):
        at = self.new_app()
        go_to_check(at)
        self.assertEqual(at.session_state["page"], "check")
        answer_until_done(at, 6)
        self.assertFalse(at.exception)
        self.assertEqual(at.session_state["page"], "result")
        text = all_markdown(at)
        self.assertIn("on track for North Carolina", text)
        self.assertIn("go to the DMV as planned", text)
        # No retake offered for a clear pass
        self.assertEqual(len([b for b in at.button if b.key == "btn_retake"]), 0)

        at.button(key="btn_to_feedback").click().run()
        self.assertTrue(at.button(key="btn_submit_feedback").disabled)
        for key, (_, options) in app.FEEDBACK_QUESTIONS.items():
            at.radio(key=key).set_value(options[-1]).run()
        at.button(key="btn_submit_feedback").click().run()
        self.assertFalse(at.exception)
        self.assertTrue(at.session_state["feedback_locked"])
        payload = at.session_state["feedback_payload"]
        self.assertEqual(payload["overall_verdict"], "on_track")
        self.assertEqual(payload["attempts"][0]["state_line_correct"], 6)

    def test_state_choice_survives_the_check(self):
        at = self.new_app()
        go_to_check(at, state="California")
        answer_until_done(at, 6)
        self.assertEqual(at.session_state["state_name"], "California")
        self.assertIn("on track for California", all_markdown(at))

    def test_failing_flow_gives_next_steps_reminder_and_one_retake(self):
        at = self.new_app()
        go_to_check(at, state="New York")
        answer_until_done(at, 2)
        text = all_markdown(at)
        self.assertIn("might not pass New York", text)
        self.assertIn("see an eye doctor before your DMV visit", text)
        self.assertIn("MV-619", text)
        # The margin line is skipped after a non-pass: 2 + 3 + 6 letters
        self.assertEqual(len(at.session_state["answers"]), 11)

        at.button(key="remind_In 3 days").click().run()
        self.assertEqual(at.session_state["reminder"], "In 3 days")

        # Retake goes back through setup, and the second result is combined honestly
        at.button(key="btn_retake").click().run()
        self.assertEqual(at.session_state["page"], "setup")
        for key in app.SETUP_CHECKLIST:
            at.checkbox(key=key).check().run()
        at.button(key="btn_begin").click().run()
        answer_until_done(at, 6)
        self.assertEqual(len(at.session_state["attempts"]), 2)
        self.assertIn("Your two checks didn't agree", all_markdown(at))
        self.assertEqual(len([b for b in at.button if b.key == "btn_retake"]), 0)

    def test_close_result(self):
        at = self.new_app()
        go_to_check(at)
        answer_until_done(at, 4)
        self.assertIn("You're right at the line", all_markdown(at))

    def test_georgia_shows_and_tests_its_own_20_60_line(self):
        at = self.new_app()
        at.button(key="btn_start").click().run()
        at.selectbox(key="w_state").select("Georgia").run()
        self.assertIn("20/60", all_markdown(at))
        for key in app.SETUP_CHECKLIST:
            at.checkbox(key=key).check().run()
        at.button(key="btn_begin").click().run()
        state_lines = {it["denominator"] for it in at.session_state["check_items"] if it["role"] == "state line"}
        self.assertEqual(state_lines, {60})
        answer_until_done(at, 6)
        text = all_markdown(at)
        self.assertIn("on track for Georgia", text)
        self.assertIn("20/60 · Georgia's line", text)

    def test_new_jersey_miss_names_form_st_14(self):
        at = self.new_app()
        go_to_check(at, state="New Jersey")
        answer_until_done(at, 2)
        text = all_markdown(at)
        self.assertIn("might not pass New Jersey", text)
        self.assertIn("ST-14", text)

    def test_start_over_resets_everything(self):
        at = self.new_app()
        go_to_check(at, state="Texas")
        answer_until_done(at, 6)
        at.button(key="btn_result_restart").click().run()
        self.assertEqual(at.session_state["page"], "welcome")
        self.assertEqual(at.session_state["attempts"], [])
        self.assertEqual(at.session_state["state_name"], "North Carolina")


if __name__ == "__main__":
    unittest.main()
