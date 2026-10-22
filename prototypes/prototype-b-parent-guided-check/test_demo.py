import unittest

from streamlit.testing.v1 import AppTest

from demo import NEXT_STEPS, OBSERVATIONS, QUESTION_OPTIONS, SYMBOLS, activity_counts, begin_activity, build_parent_message, build_summary, fictional_example, new_session, record_answer, record_practice_answer, refresh_parent_note, set_activity_paused


class SessionTests(unittest.TestCase):
    def test_independent_sessions_include_all_four_shapes(self):
        first, second = new_session(), new_session()
        self.assertEqual(len(first["questions"]), 6)
        self.assertEqual({q["target"] for q in first["questions"]}, set(SYMBOLS))
        for question in first["questions"]:
            self.assertCountEqual(question["choices"], SYMBOLS)
        first["observations"].append(OBSERVATIONS[0])
        self.assertEqual(second["observations"], [])

    def test_stale_double_click_and_invalid_choices_do_not_advance(self):
        session = new_session()
        self.assertFalse(record_answer(session, 0, "Circle"))
        session["step"] = "game"
        session["practice_complete"] = True
        begin_activity(session)
        self.assertFalse(record_answer(session, 0, "Invalid"))
        self.assertFalse(record_answer(session, 2, "Circle"))
        self.assertTrue(record_answer(session, 0, session["questions"][0]["target"]))
        self.assertFalse(record_answer(session, 0, session["questions"][0]["target"]))
        self.assertEqual(len(session["answers"]), 1)

    def test_all_skips_complete_activity_without_clinical_result(self):
        session = new_session()
        session["step"] = "game"
        session["practice_complete"] = True
        begin_activity(session)
        for index in range(6):
            self.assertTrue(record_answer(session, index, None))
        self.assertEqual(session["step"], "observations")
        self.assertEqual(activity_counts(session), {"completed": 6, "matched": 0, "skipped": 6, "total": 6})
        self.assertFalse(record_answer(session, 6, None))
        self.assertIn("cannot establish whether a child needs eye care", build_summary(session))
        self.assertNotIn("20/20", build_summary(session))

    def test_export_preserves_parent_choice_and_example_provenance(self):
        session = fictional_example()
        session["next_step"] = NEXT_STEPS[2]
        session["notes"] = "My own observation"
        summary = build_summary(session)
        self.assertIn("Data: Fictional example", summary)
        self.assertIn(NEXT_STEPS[2], summary)
        self.assertIn("My own observation", summary)
        self.assertNotIn("Choose an appointment time", summary)
        self.assertIn("4 matched; 2 skipped", summary)

    def test_parent_message_uses_observations_and_parent_questions(self):
        session = fictional_example()
        session["next_step"] = NEXT_STEPS[1]
        session["questions_to_ask"] = [QUESTION_OPTIONS[0]]
        session["custom_question"] = "Can I bring the letter?"
        message = build_parent_message(session)
        self.assertIn("school vision screening", message)
        self.assertIn(OBSERVATIONS[0], message)
        self.assertIn(QUESTION_OPTIONS[0], message)
        self.assertIn("Can I bring the letter?", message)
        self.assertIn("Fictional example", message)
        self.assertNotIn("4 matched", message)
        self.assertNotIn("20/", message)

    def test_regenerated_note_invalidates_prior_download_and_export_honors_edits(self):
        session = fictional_example()
        old_revision = session["summary_revision"]
        session["summary_download_requested"] = True
        session["notes"] = "A changed observation"
        refresh_parent_note(session)
        self.assertIn("A changed observation", session["message_draft"])
        self.assertGreater(session["summary_revision"], old_revision)
        self.assertFalse(session["summary_download_requested"])
        session["message_draft"] = "My edited note"
        self.assertIn("My edited note", build_summary(session))

    def test_practice_is_separate_and_required_before_activity(self):
        session = new_session()
        session["step"] = "game"
        self.assertFalse(begin_activity(session))
        self.assertFalse(record_answer(session, 0, "Circle"))
        record_practice_answer(session, "Square")
        self.assertFalse(session["practice_complete"])
        record_practice_answer(session, "Circle")
        self.assertTrue(session["practice_complete"])
        self.assertEqual(session["answers"], [])
        self.assertTrue(begin_activity(session))
        self.assertFalse(record_practice_answer(session, "Square"))

    def test_paused_activity_rejects_stale_answers_and_resumes_same_picture(self):
        session = fictional_example()
        session["step"] = "game"
        session["answers"] = session["answers"][:1]
        self.assertTrue(set_activity_paused(session, True))
        self.assertFalse(record_answer(session, 1, session["questions"][1]["target"]))
        self.assertEqual(len(session["answers"]), 1)
        self.assertTrue(set_activity_paused(session, False))
        self.assertTrue(record_answer(session, 1, session["questions"][1]["target"]))
        self.assertEqual(len(session["answers"]), 2)


class JourneyTests(unittest.TestCase):
    def setUp(self):
        self.at = AppTest.from_file("app.py", default_timeout=15).run()
        self.assertEqual(list(self.at.exception), [])

    def press(self, label):
        next(button for button in self.at.button if button.label == label).click().run()
        self.assertEqual(list(self.at.exception), [])

    def start_game(self):
        self.press("Let's play")
        self.at.button(key="family_practice_Circle").click().run()
        self.press("Start the picture game")

    def play(self, skip=False):
        self.start_game()
        for index in range(6):
            session = self.at.session_state["focal_family"]
            if skip:
                self.at.button(key=f"family_skip_{index}").click().run()
            else:
                target = session["questions"][index]["target"]
                self.at.button(key=f"family_answer_{index}_{target}").click().run()
            self.assertEqual(list(self.at.exception), [])

    def test_full_journey_edits_and_reset(self):
        self.play()
        self.at.checkbox(key="family_observation_0").check()
        self.at.text_area(key="family_notes").input("Moved closer to the book")
        self.at.radio(key="family_next_step").set_value(NEXT_STEPS[0])
        self.press("Create my summary")
        session = self.at.session_state["focal_family"]
        self.assertEqual(session["step"], "summary")
        self.assertEqual(activity_counts(session)["matched"], 6)
        self.assertIn("Moved closer", build_summary(session))
        self.at.checkbox(key="family_task_0_0").check().run()
        self.assertIn("[x] Find a provider", build_summary(self.at.session_state["focal_family"]))
        self.press("Edit my observations")
        self.assertEqual(self.at.text_area(key="family_notes").value, "Moved closer to the book")
        self.at.radio(key="family_next_step").set_value(NEXT_STEPS[1])
        self.press("Create my summary")
        self.assertFalse(self.at.checkbox(key="family_task_1_0").value)
        self.press("Start over")
        fresh = self.at.session_state["focal_family"]
        self.assertEqual(fresh["step"], "setup")
        for key in ("answers", "observations", "tasks"):
            self.assertFalse(fresh[key])
        self.assertIsNone(fresh["feedback"])
        self.assertFalse(fresh["summary_download_requested"])
        self.play(skip=True)
        self.assertEqual(activity_counts(self.at.session_state["focal_family"])["skipped"], 6)

    def test_missing_next_step_preserves_input_and_allows_uncertainty(self):
        self.play(skip=True)
        self.at.text_area(key="family_notes").input("A note to keep")
        self.press("Create my summary")
        self.assertEqual(self.at.session_state["focal_family"]["step"], "observations")
        self.assertEqual(self.at.text_area(key="family_notes").value, "A note to keep")
        self.at.radio(key="family_next_step").set_value(NEXT_STEPS[3])
        self.press("Create my summary")
        self.assertEqual(self.at.session_state["focal_family"]["next_step"], NEXT_STEPS[3])

    def test_example_feedback_is_neutral_and_preserved_until_reset(self):
        self.press("Explore a fictional example")
        self.assertTrue(any("Fictional example" in warning.value for warning in self.at.warning))
        self.assertIsNone(self.at.radio(key="family_usefulness").value)
        self.assertIsNone(self.at.radio(key="family_reuse").value)
        self.assertIsNone(self.at.radio(key="family_clarity").value)
        self.press("Save feedback")
        self.assertIsNone(self.at.session_state["focal_family"]["feedback"])
        self.at.radio(key="family_usefulness").set_value("Not at all useful")
        self.at.radio(key="family_reuse").set_value("No")
        self.at.radio(key="family_clarity").set_value("Very unclear")
        self.at.text_area(key="family_barriers").input("Finding time to arrange a visit")
        self.at.text_area(key="family_comment").input("Prefer another approach")
        self.press("Save feedback")
        original = dict(self.at.session_state["focal_family"]["feedback"])
        self.assertEqual(original["reuse"], "No")
        self.assertEqual(original["next_step_clarity"], "Very unclear")
        self.assertEqual(original["follow_through_barrier"], "Finding time to arrange a visit")
        self.assertFalse(any(button.label == "Save feedback" for button in self.at.button))
        self.press("Edit my observations")
        self.press("Create my summary")
        self.assertEqual(self.at.session_state["focal_family"]["feedback"], original)
        self.press("Start over")
        self.assertEqual(self.at.session_state["focal_family"]["source"], "current_session")
        self.assertIsNone(self.at.session_state["focal_family"]["feedback"])

    def test_parent_questions_and_edited_draft_are_in_summary_and_reset(self):
        self.press("Explore a fictional example")
        self.at.multiselect(key="family_question_selection").select(QUESTION_OPTIONS[1])
        self.at.text_area(key="family_custom_question").input("Can I bring the letter?")
        self.press("Update questions and regenerate draft")
        session = self.at.session_state["focal_family"]
        self.assertIn(QUESTION_OPTIONS[1], session["message_draft"])
        self.assertIn("Can I bring the letter?", build_summary(session))
        self.at.text_area(key="family_message_draft").input("My own carefully edited note").run()
        self.assertEqual(list(self.at.exception), [])
        self.assertIn("My own carefully edited note", build_summary(self.at.session_state["focal_family"]))
        self.press("Start over")
        fresh = self.at.session_state["focal_family"]
        self.assertEqual(fresh["questions_to_ask"], [])
        self.assertEqual(fresh["custom_question"], "")
        self.assertEqual(fresh["message_draft"], "")

    def test_feedback_keeps_original_context_after_next_step_changes(self):
        self.press("Explore a fictional example")
        self.at.radio(key="family_usefulness").set_value("Moderately useful")
        self.at.radio(key="family_reuse").set_value("Not sure")
        self.at.radio(key="family_clarity").set_value("Somewhat clear")
        self.press("Save feedback")
        original = dict(self.at.session_state["focal_family"]["feedback"]["evaluated_context"])
        self.assertEqual(original["next_step"], NEXT_STEPS[0])
        self.press("Edit my observations")
        self.at.radio(key="family_next_step").set_value(NEXT_STEPS[1])
        self.press("Create my summary")
        session = self.at.session_state["focal_family"]
        self.assertEqual(session["next_step"], NEXT_STEPS[1])
        self.assertEqual(session["feedback"]["evaluated_context"], original)

    def test_practice_cannot_advance_six_picture_count(self):
        self.press("Let's play")
        self.at.button(key="family_practice_Square").click().run()
        self.assertTrue(self.at.button(key="family_begin_activity").disabled)
        self.assertEqual(self.at.session_state["focal_family"]["answers"], [])
        self.at.button(key="family_practice_Circle").click().run()
        self.press("Start the picture game")
        self.assertEqual(self.at.session_state["focal_family"]["answers"], [])

    def test_break_and_resume_preserve_completed_picture(self):
        self.start_game()
        self.at.button(key="family_skip_0").click().run()
        self.press("Take a break")
        self.assertTrue(self.at.session_state["focal_family"]["paused"])
        self.assertFalse(any(button.key and button.key.startswith("family_answer_") for button in self.at.button))
        self.press("Resume the picture game")
        self.assertFalse(self.at.session_state["focal_family"]["paused"])
        self.assertEqual(len(self.at.session_state["focal_family"]["answers"]), 1)
        self.at.button(key="family_skip_1").click().run()
        self.assertEqual(len(self.at.session_state["focal_family"]["answers"]), 2)


if __name__ == "__main__":
    unittest.main()
