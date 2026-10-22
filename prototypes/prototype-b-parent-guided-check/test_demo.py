import unittest

from streamlit.testing.v1 import AppTest

from demo import NEXT_STEPS, OBSERVATIONS, SYMBOLS, activity_counts, build_summary, fictional_example, new_session, record_answer


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
        self.assertFalse(record_answer(session, 0, "Invalid"))
        self.assertFalse(record_answer(session, 2, "Circle"))
        self.assertTrue(record_answer(session, 0, session["questions"][0]["target"]))
        self.assertFalse(record_answer(session, 0, session["questions"][0]["target"]))
        self.assertEqual(len(session["answers"]), 1)

    def test_all_skips_complete_activity_without_clinical_result(self):
        session = new_session()
        session["step"] = "game"
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


class JourneyTests(unittest.TestCase):
    def setUp(self):
        self.at = AppTest.from_file("app.py", default_timeout=15).run()
        self.assertEqual(list(self.at.exception), [])

    def press(self, label):
        next(button for button in self.at.button if button.label == label).click().run()
        self.assertEqual(list(self.at.exception), [])

    def play(self, skip=False):
        self.press("Let's play")
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
        self.press("Save feedback")
        self.assertIsNone(self.at.session_state["focal_family"]["feedback"])
        self.at.radio(key="family_usefulness").set_value("Not at all useful")
        self.at.radio(key="family_reuse").set_value("No")
        self.at.text_area(key="family_comment").input("Prefer another approach")
        self.press("Save feedback")
        original = dict(self.at.session_state["focal_family"]["feedback"])
        self.assertEqual(original["reuse"], "No")
        self.assertFalse(any(button.label == "Save feedback" for button in self.at.button))
        self.press("Edit my observations")
        self.press("Create my summary")
        self.assertEqual(self.at.session_state["focal_family"]["feedback"], original)
        self.press("Start over")
        self.assertEqual(self.at.session_state["focal_family"]["source"], "current_session")
        self.assertIsNone(self.at.session_state["focal_family"]["feedback"])


if __name__ == "__main__":
    unittest.main()
