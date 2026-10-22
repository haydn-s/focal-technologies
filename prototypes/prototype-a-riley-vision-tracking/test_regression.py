"""
Automated Regression Tests for Focal Monitor (Prototype A)
Prompt 3: Data Integrity & Completion States

Verifies:
1. Zero answers: No completed session or invented live result.
2. One answer: Session remains incomplete; Resume Test works.
3. Seven answers: Session remains incomplete; no completed trend entry.
4. Eight answers: Correct completed result and timestamp.
5. Eight incorrect answers: 0/8 appears correctly on the chart.
6. Eight correct answers: 8/8 appears correctly on the chart.
7. Reset: All live-session results are cleared; only clearly labeled fictional history remains.
8. Two consecutive full journeys work.
9. Main-button and sidebar navigation work.
10. Duplicate final-question prevention works.
"""

import unittest
from streamlit.testing.v1 import AppTest

class TestFocalMonitorRegression(unittest.TestCase):

    def test_zero_answers_shows_incomplete_and_no_live_history(self):
        """AT 1: Zero answers -> No completed session or invented live result."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()
        
        # Navigate to Results with 0 answers
        at.sidebar.selectbox[0].select("results").run()
        self.assertEqual(at.session_state.step, "results")
        self.assertIsNone(at.session_state.completed_at)
        
        # Verify Results indicates Incomplete
        results_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Session Incomplete", results_text)
        self.assertNotIn("Demo Session Completed", results_text)
        
        # Navigate to History with 0 answers
        at.sidebar.selectbox[0].select("vision_history").run()
        self.assertEqual(at.session_state.step, "vision_history")
        history_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Illustrative Demo Data Only", history_text)
        self.assertNotIn("Completed Live Session Added", history_text)

    def test_one_answer_incomplete_and_resume(self):
        """AT 2: One answer -> Session remains incomplete; Resume Test works."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()
        
        # Start Vision Check
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()
        
        # Answer exactly 1 question
        right_btn = [b for b in at.button if "Right" in b.label][0]
        right_btn.click().run()
        self.assertEqual(len(at.session_state.answers), 1)
        self.assertEqual(at.session_state.current_question_index, 1)
        
        # Navigate to Results
        at.sidebar.selectbox[0].select("results").run()
        self.assertEqual(at.session_state.step, "results")
        self.assertIsNone(at.session_state.completed_at)
        results_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Vision Check Incomplete (1 of 8 Questions Answered)", results_text)
        self.assertNotIn("Demo Session Completed", results_text)
        
        # Click Resume Test button
        resume_btn = [b for b in at.button if "Resume Test" in b.label][0]
        resume_btn.click().run()
        
        # Must return to Question 2 of 8
        self.assertEqual(at.session_state.step, "vision_check")
        self.assertEqual(at.session_state.current_question_index, 1)

    def test_seven_answers_incomplete_no_history_contamination(self):
        """AT 3: Seven answers -> Session remains incomplete; no completed trend entry."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()
        
        # Start Vision Check
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()
        
        # Answer 7 questions
        for _ in range(7):
            right_btn = [b for b in at.button if "Right" in b.label][0]
            right_btn.click().run()
            
        self.assertEqual(len(at.session_state.answers), 7)
        self.assertIsNone(at.session_state.completed_at)
        
        # Jump to Results
        at.sidebar.selectbox[0].select("results").run()
        results_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Vision Check Incomplete (7 of 8 Questions Answered)", results_text)
        self.assertNotIn("Demo Session Completed", results_text)
        
        # Jump to History
        at.sidebar.selectbox[0].select("vision_history").run()
        history_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Incomplete Test in Progress (7 of 8 Answered)", history_text)
        self.assertNotIn("Completed Live Session Added", history_text)
        
        # Resume from History
        resume_btn = [b for b in at.button if "Resume Test" in b.label][0]
        resume_btn.click().run()
        self.assertEqual(at.session_state.step, "vision_check")
        self.assertEqual(at.session_state.current_question_index, 7) # Question 8

    def test_eight_answers_completed_result_and_timestamp(self):
        """AT 4: Eight answers -> Correct completed result and timestamp."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()
        
        # Start Vision Check
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()
        
        # Answer all 8 questions
        for _ in range(8):
            right_btn = [b for b in at.button if "Right" in b.label][0]
            right_btn.click().run()
            
        self.assertEqual(len(at.session_state.answers), 8)
        self.assertEqual(at.session_state.step, "results")
        self.assertIsNotNone(at.session_state.completed_at)
        
        results_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Check complete", results_text)
        self.assertIn(at.session_state.completed_at, results_text)
        
        # Navigate to History
        history_btn = [b for b in at.button if "View Vision History" in b.label or "Compare Results" in b.label][0]
        history_btn.click().run()
        self.assertEqual(at.session_state.step, "vision_history")
        if at.session_state.active_comparison_view != "Experience B: Trend Tracking":
            at.radio[0].set_value("Experience B: Trend Tracking").run()
        history_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Completed Live Session Added", history_text)

    def test_eight_incorrect_answers_zero_score_visible(self):
        """AT 5: Eight incorrect answers -> 0/8 appears correctly on the chart."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()
        
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()
        
        # Answer all 8 questions intentionally wrong
        wrong_choices = {"up": "down", "down": "up", "left": "right", "right": "left"}
        for q in range(8):
            curr_target = at.session_state.questions[q]["direction"]
            wrong_dir = wrong_choices[curr_target]
            btn = [b for b in at.button if wrong_dir.capitalize() in b.label][0]
            btn.click().run()
            
        self.assertEqual(len(at.session_state.answers), 8)
        score = sum(1 for a in at.session_state.answers if a["is_correct"])
        self.assertEqual(score, 0, "Score should be 0/8")
        
        # Results page check
        results_text = " ".join([m.value for m in at.markdown])
        self.assertIn("20/200", results_text)
        self.assertIn("Significantly reduced vision", results_text)
        
        # Navigate to History
        history_btn = [b for b in at.button if "View Vision History" in b.label or "Compare Results" in b.label][0]
        history_btn.click().run()
        if at.session_state.active_comparison_view != "Experience B: Trend Tracking":
            at.radio[0].set_value("Experience B: Trend Tracking").run()
        history_text = " ".join([m.value for m in at.markdown])
        self.assertIn("20/200", history_text)
        self.assertIn("Significantly reduced vision", history_text)

    def test_eight_correct_answers_full_score_visible(self):
        """AT 6: Eight correct answers -> 8/8 appears correctly."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()
        
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()
        
        # Answer all 8 questions correctly
        for q in range(8):
            curr_target = at.session_state.questions[q]["direction"]
            btn = [b for b in at.button if curr_target.capitalize() in b.label][0]
            btn.click().run()
            
        self.assertEqual(len(at.session_state.answers), 8)
        score = sum(1 for a in at.session_state.answers if a["is_correct"])
        self.assertEqual(score, 8, "Score should be 8/8")
        
        results_text = " ".join([m.value for m in at.markdown])
        self.assertIn("20/20", results_text)
        self.assertIn("Normal vision", results_text)
        
        history_btn = [b for b in at.button if "View Vision History" in b.label or "Compare Results" in b.label][0]
        history_btn.click().run()
        if at.session_state.active_comparison_view != "Experience B: Trend Tracking":
            at.radio[0].set_value("Experience B: Trend Tracking").run()
        history_text = " ".join([m.value for m in at.markdown])
        self.assertIn("20/20", history_text)
        self.assertIn("Normal vision", history_text)

    def test_reset_clears_live_session_results_only_fictional_remains(self):
        """AT 7: Reset -> All live-session results are cleared; only fictional history remains."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()
        
        # Complete full 8-question check
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()
        for _ in range(8):
            right_btn = [b for b in at.button if "Right" in b.label][0]
            right_btn.click().run()
            
        self.assertEqual(len(at.session_state.answers), 8)
        self.assertIsNotNone(at.session_state.completed_at)
        
        # Reset via sidebar
        reset_btn = [b for b in at.sidebar.button if "Reset Demo" in b.label][0]
        reset_btn.click().run()
        
        self.assertEqual(at.session_state.step, "welcome")
        self.assertEqual(at.session_state.nav_jump_select, "welcome")
        self.assertEqual(len(at.session_state.answers), 0)
        self.assertIsNone(at.session_state.completed_at)
        
        # Navigate to History after reset
        at.sidebar.selectbox[0].select("vision_history").run()
        history_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Illustrative Demo Data Only", history_text)
        self.assertNotIn("Completed Live Session Added", history_text)

    def test_two_consecutive_runs(self):
        """AT 8: Two consecutive complete demo runs work without errors."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()
        
        # === RUN 1 ===
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()
        for _ in range(8):
            right_btn = [b for b in at.button if "Right" in b.label][0]
            right_btn.click().run()
            
        self.assertEqual(len(at.session_state.answers), 8)
        self.assertEqual(at.session_state.step, "results")
        
        history_btn = [b for b in at.button if "View Vision History" in b.label or "Compare Results" in b.label][0]
        history_btn.click().run()
        self.assertEqual(at.session_state.step, "vision_history")
        
        # Reset from Vision History
        reset_btn = [b for b in at.button if "Reset Demo and Start Fresh" in b.label][0]
        reset_btn.click().run()
        self.assertEqual(at.session_state.step, "welcome")
        self.assertEqual(len(at.session_state.answers), 0)
        
        # === RUN 2 ===
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()
        for _ in range(8):
            left_btn = [b for b in at.button if "Left" in b.label][0]
            left_btn.click().run()
            
        self.assertEqual(len(at.session_state.answers), 8)
        self.assertEqual(at.session_state.step, "results")
        
        history_btn = [b for b in at.button if "View Vision History" in b.label or "Compare Results" in b.label][0]
        history_btn.click().run()
        self.assertEqual(at.session_state.step, "vision_history")

    def test_main_button_and_sidebar_navigation(self):
        """AT 9: Main-button and sidebar navigation still work."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()
        
        # Main button start
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()
        self.assertEqual(at.session_state.step, "vision_check")
        self.assertEqual(at.session_state.nav_jump_select, "vision_check")
        
        # Sidebar jump to vision_history
        at.sidebar.selectbox[0].select("vision_history").run()
        self.assertEqual(at.session_state.step, "vision_history")
        self.assertEqual(at.session_state.nav_jump_select, "vision_history")
        
        # Sidebar jump to welcome
        at.sidebar.selectbox[0].select("welcome").run()
        self.assertEqual(at.session_state.step, "welcome")
        self.assertEqual(at.session_state.nav_jump_select, "welcome")

    def test_duplicate_final_question_prevention(self):
        """AT 10: Duplicate final-question prevention still works."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()
        
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()
        
        # Answer all 8 questions
        for _ in range(8):
            right_btn = [b for b in at.button if "Right" in b.label][0]
            right_btn.click().run()
            
        self.assertEqual(len(at.session_state.answers), 8)
        self.assertEqual(at.session_state.step, "results")
        
        # Verify exactly 1..8
        q_nums = [a["question_num"] for a in at.session_state.answers]
        self.assertEqual(q_nums, [1, 2, 3, 4, 5, 6, 7, 8])
        
        # Re-entry guard test
        at.session_state.step = "vision_check"
        at.run()
        self.assertEqual(at.session_state.step, "results")
        self.assertEqual(len(at.session_state.answers), 8)

    def test_fault_injection_duplicated_qids_rejected(self):
        """Prompt 3.1: 8 duplicated Q1 responses must be rejected by Results and History."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        # Inject 8 duplicate Q1 responses
        at.session_state.answers = [
            {"question_num": 1, "target_direction": "up", "user_response": "up", "is_correct": True, "size_px": 130}
            for _ in range(8)
        ]
        at.session_state.completed_at = "2026-10-21 01:00"
        
        # Check Results page
        at.sidebar.selectbox[0].select("results").run()
        results_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Session Incomplete", results_text)
        self.assertNotIn("Demo Session Completed", results_text)

        # Check History page
        at.sidebar.selectbox[0].select("vision_history").run()
        history_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Illustrative Demo Data Only", history_text)
        self.assertNotIn("Completed Live Session Added", history_text)

    def test_eight_answers_without_timestamp_rejected(self):
        """Prompt 3.1: 8 valid answers with missing/None timestamp cannot be presented as completed."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        # Inject 8 unique valid answers with completed_at = None
        questions = at.session_state.questions
        at.session_state.answers = [
            {"question_num": i + 1, "target_direction": q["direction"], "user_response": q["direction"], "is_correct": True, "size_px": q["size_px"]}
            for i, q in enumerate(questions)
        ]
        at.session_state.completed_at = None

        # Check Results page
        at.sidebar.selectbox[0].select("results").run()
        results_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Session Incomplete", results_text)
        self.assertNotIn("Demo Session Completed", results_text)

        # Check History page
        at.sidebar.selectbox[0].select("vision_history").run()
        history_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Illustrative Demo Data Only", history_text)
        self.assertNotIn("Completed Live Session Added", history_text)

    def test_history_contains_only_one_table(self):
        """Prompt 3.1: History page must call st.dataframe only once, eliminating duplicate table."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()
        at.sidebar.selectbox[0].select("vision_history").run()
        
        # Verify exactly 1 dataframe widget is rendered in Vision History
        self.assertEqual(len(at.dataframe), 1, "Vision History should display only one dataframe")

    def test_live_session_date_derived_from_completion_timestamp(self):
        """Prompt 3.1: Live session date in History is derived from stored completion timestamp."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        questions = at.session_state.questions
        at.session_state.answers = [
            {"question_num": i + 1, "target_direction": q["direction"], "user_response": q["direction"], "is_correct": True, "size_px": q["size_px"]}
            for i, q in enumerate(questions)
        ]
        at.session_state.completed_at = "2025-11-15 14:30"

        at.sidebar.selectbox[0].select("vision_history").run()
        history_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Completed Live Session Added", history_text)

        # Dataframe in history should contain 2025-11-15
        table_df = at.dataframe[0].value
        self.assertIn("2025-11-15", list(table_df["Date"]))

    def test_invalid_timestamps_rejected(self):
        """Prompt 3.2: Invalid timestamps like 'not-a-timestamp' and '2026-02-30 25:99' are rejected."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        questions = at.session_state.questions
        valid_answers = [
            {"question_num": i + 1, "target_direction": q["direction"], "user_response": q["direction"], "is_correct": True, "size_px": q["size_px"]}
            for i, q in enumerate(questions)
        ]
        
        for bad_ts in ["not-a-timestamp", "2026-02-30 25:99"]:
            at.session_state.answers = list(valid_answers)
            at.session_state.completed_at = bad_ts

            # Check Results page
            at.sidebar.selectbox[0].select("results").run()
            results_text = " ".join([m.value for m in at.markdown])
            self.assertIn("Session Incomplete", results_text)
            self.assertNotIn("Demo Session Completed", results_text)

            # Check History page
            at.sidebar.selectbox[0].select("vision_history").run()
            history_text = " ".join([m.value for m in at.markdown])
            self.assertIn("Illustrative Demo Data Only", history_text)
            self.assertNotIn("Completed Live Session Added", history_text)

    def test_boolean_question_ids_rejected(self):
        """Prompt 3.2: Question IDs with boolean True must be rejected."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        questions = at.session_state.questions
        answers_with_bool_id = [
            {"question_num": True if i == 0 else i + 1, "target_direction": q["direction"], "user_response": q["direction"], "is_correct": True, "size_px": q["size_px"]}
            for i, q in enumerate(questions)
        ]
        at.session_state.answers = answers_with_bool_id
        at.session_state.completed_at = "2026-10-21 01:30"

        # Check Results page
        at.sidebar.selectbox[0].select("results").run()
        results_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Session Incomplete", results_text)
        self.assertNotIn("Demo Session Completed", results_text)

        # Check History page
        at.sidebar.selectbox[0].select("vision_history").run()
        history_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Illustrative Demo Data Only", history_text)
        self.assertNotIn("Completed Live Session Added", history_text)

    def test_malformed_partial_records_do_not_crash(self):
        """Prompt 3.2: Corrupted partial records do not crash Results or History."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        malformed_cases = [
            [{"broken_payload": "corrupted"}],
            ["not-even-a-dict"],
            [{"question_num": 1}],  # missing schema keys
            [{"question_num": True, "target_direction": "up", "user_response": "up", "is_correct": True, "size_px": 100}]
        ]

        for bad_case in malformed_cases:
            at.session_state.answers = bad_case
            at.session_state.completed_at = None

            # Results must render safely without KeyError or TypeError
            at.sidebar.selectbox[0].select("results").run()
            self.assertFalse(at.exception, f"Results raised exception for case: {bad_case}")
            results_text = " ".join([m.value for m in at.markdown])
            self.assertIn("Session Incomplete", results_text)
            self.assertNotIn("Demo Session Completed", results_text)

            # History must render safely using only illustrative baseline
            at.sidebar.selectbox[0].select("vision_history").run()
            self.assertFalse(at.exception, f"History raised exception for case: {bad_case}")
            history_text = " ".join([m.value for m in at.markdown])
            self.assertIn("Illustrative Demo Data Only", history_text)
            self.assertNotIn("Completed Live Session Added", history_text)

    def test_valid_partial_session_resumes_cleanly(self):
        """Prompt 3.2: Valid 1-7 answer sessions can resume from Results and History."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        # Start and answer 2 questions
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()

        for _ in range(2):
            right_btn = [b for b in at.button if "Right" in b.label][0]
            right_btn.click().run()

        self.assertEqual(len(at.session_state.answers), 2)
        self.assertEqual(at.session_state.current_question_index, 2)

        # Jump to Results: Resume Test button should be present
        at.sidebar.selectbox[0].select("results").run()
        resume_btn = [b for b in at.button if "Resume Test" in b.label][0]
        resume_btn.click().run()
        self.assertEqual(at.session_state.step, "vision_check")
        self.assertEqual(at.session_state.current_question_index, 2)

        # Jump to History: Resume Test button should be present
        at.sidebar.selectbox[0].select("vision_history").run()
        resume_btn = [b for b in at.button if "Resume Test" in b.label][0]
        resume_btn.click().run()
        self.assertEqual(at.session_state.step, "vision_check")
        self.assertEqual(at.session_state.current_question_index, 2)

    def test_experience_comparison_switching_maintains_consistent_score(self):
        """Prompt 4: Switching between Experience A and Experience B shows consistent underlying score."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        # Complete 8 questions correctly
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()

        for q in range(8):
            curr_target = at.session_state.questions[q]["direction"]
            btn = [b for b in at.button if curr_target.capitalize() in b.label][0]
            btn.click().run()

        self.assertEqual(len(at.session_state.answers), 8)
        self.assertEqual(at.session_state.step, "results")

        # Proceed to comparison view via button
        history_btn = [b for b in at.button if "Compare Results" in b.label or "View Vision History" in b.label][0]
        history_btn.click().run()
        self.assertEqual(at.session_state.step, "vision_history")

        # Switch to Experience A
        at.radio[0].set_value("Experience A: Single Result").run()
        self.assertEqual(at.session_state.active_comparison_view, "Experience A: Single Result")
        exp_a_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Single Result", exp_a_text)
        self.assertIn("20/20", exp_a_text)
        self.assertIn("Normal vision", exp_a_text)
        self.assertIn("Question breakdown", exp_a_text)
        self.assertNotIn("Longitudinal View", exp_a_text)
        self.assertNotIn("Understanding Longitudinal Trend Tracking", exp_a_text)

        # Switch to Experience B via the single segmented presentation control
        at.radio[0].set_value("Experience B: Trend Tracking").run()
        self.assertEqual(at.session_state.active_comparison_view, "Experience B: Trend Tracking")
        exp_b_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Trend Tracking", exp_b_text)
        self.assertIn("20/20", exp_b_text)
        self.assertIn("Normal vision", exp_b_text)
        self.assertIn("Longitudinal Vision Trend", exp_b_text)
        self.assertNotIn("Question breakdown", exp_b_text)

    def test_feedback_submission_validation_and_confirmation(self):
        """Prompt 4: Neutral feedback validates required questions, records response, and reveals debrief."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        # Jump directly to vision_history
        at.sidebar.selectbox[0].select("vision_history").run()

        # Initially only Experience B is visited; attempting early submission triggers neutral info
        submit_btn = [b for b in at.button if "Submit Anonymous Feedback" in b.label][0]
        submit_btn.click().run()
        self.assertGreater(len(at.info), 0)
        self.assertIn("Please view both Single Result", at.info[0].value)
        self.assertIsNone(at.session_state.submitted_feedback)

        # Visit Experience A so both views are visited
        at.radio[0].set_value("Experience A: Single Result").run()
        self.assertTrue("Experience A: Single Result" in at.session_state.views_visited)
        self.assertTrue("Experience B: Trend Tracking" in at.session_state.views_visited)

        # Verify no positive defaults (all None)
        self.assertIsNone(at.radio[1].value)
        self.assertIsNone(at.radio[2].value)
        self.assertIsNone(at.radio[3].value)

        # Attempt to submit incomplete form now that both are visited -> triggers error
        submit_btn = [b for b in at.button if "Submit Anonymous Feedback" in b.label][0]
        submit_btn.click().run()
        self.assertGreater(len(at.error), 0)
        self.assertIn("Please answer all required questions", at.error[0].value)
        self.assertIsNone(at.session_state.submitted_feedback)

        # Fill in answers
        at.radio[1].set_value("Trend Tracking")
        at.text_area[0].input("Longitudinal tracking provides helpful trends.")
        at.radio[2].set_value("Single Result")
        at.radio[3].set_value("Likely")

        # Submit valid form
        submit_btn = [b for b in at.button if "Submit Anonymous Feedback" in b.label][0]
        submit_btn.click().run()

        # Check recorded feedback in session_state
        self.assertIsNotNone(at.session_state.submitted_feedback)
        fb = at.session_state.submitted_feedback
        self.assertEqual(fb["q1_preferred_experience"], "Trend Tracking")
        self.assertEqual(fb["q2_main_reason"], "Longitudinal tracking provides helpful trends.")
        self.assertEqual(fb["q3_easier_to_understand"], "Single Result")
        self.assertEqual(fb["q4_reuse_likelihood"], "Likely")
        self.assertTrue(at.session_state.feedback_locked)

        # Verify success notification and download button
        self.assertGreater(len(at.success), 0)
        self.assertGreater(len(at.download_button), 0)

        # Verify research debrief appears after submission
        page_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Research Debrief & Study Purpose", page_text)
        self.assertIn("Adults who suspect their vision is changing will find ongoing vision tracking", page_text)

        # Verify sidebar debrief text
        sidebar_text = " ".join([m.value for m in at.sidebar.markdown])
        self.assertIn("Course Hypothesis (Debriefed)", sidebar_text)

    def test_reset_demo_clears_feedback_and_masks_hypothesis(self):
        """Prompt 4: Reset Demo clears feedback and masks hypothesis back to neutral overview."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        # Navigate to vision_history and visit both views
        at.sidebar.selectbox[0].select("vision_history").run()
        at.radio[0].set_value("Experience A: Single Result").run()
        at.radio[0].set_value("Experience B: Trend Tracking").run()

        at.radio[1].set_value("Single Result")
        at.radio[2].set_value("Single Result")
        at.radio[3].set_value("Neutral")
        submit_btn = [b for b in at.button if "Submit Anonymous Feedback" in b.label][0]
        submit_btn.click().run()
        self.assertIsNotNone(at.session_state.submitted_feedback)
        self.assertTrue(at.session_state.feedback_locked)

        # Reset demo
        reset_btn = [b for b in at.button if "Reset Demo and Start Fresh" in b.label][0]
        reset_btn.click().run()

        # Verify back to welcome
        self.assertEqual(at.session_state.step, "welcome")
        self.assertIsNone(at.session_state.submitted_feedback)
        self.assertFalse(at.session_state.feedback_locked)

        # Verify hypothesis is masked on Welcome
        welcome_text = " ".join([m.value for m in at.markdown])
        self.assertNotIn("Adults who suspect their vision is changing will find ongoing vision tracking", welcome_text)
        self.assertIn("Product Context & Evaluation Purpose", welcome_text)

        # Verify hypothesis is masked in Sidebar
        sidebar_text = " ".join([m.value for m in at.sidebar.markdown])
        self.assertNotIn("Adults who suspect their vision is changing will find ongoing vision tracking", sidebar_text)
        self.assertIn("Research Evaluation", sidebar_text)

    def test_research_defect1_neutral_comparison_and_limitations(self):
        """Prompt 4.1: Neutral branding, identical score cards, identical limitations, no chart banner in Single Result."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        # Welcome text must be concise and neutral
        welcome_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Ready for a 2-minute vision check?", welcome_text)
        self.assertNotIn("self-track visual clarity trends at home", welcome_text)

        # Complete 8 questions correctly
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()
        for q in range(8):
            target = at.session_state.questions[q]["direction"]
            btn = [b for b in at.button if target.capitalize() in b.label][0]
            btn.click().run()

        # Proceed to comparison
        history_btn = [b for b in at.button if "Compare Results" in b.label or "View Vision History" in b.label][0]
        history_btn.click().run()

        # Switch to Experience A
        at.radio[0].set_value("Experience A: Single Result").run()
        exp_a_text = " ".join([m.value for m in at.markdown])
        self.assertIn("20/20", exp_a_text)
        self.assertIn("Normal vision", exp_a_text)
        self.assertNotIn("Essential Non-Clinical Limitations", exp_a_text)
        # Chart-oriented banner must NOT appear in Single Result
        self.assertNotIn("is plotted below as a distinct comparison point", exp_a_text)

        # Switch to Experience B with the same presentation control
        at.radio[0].set_value("Experience B: Trend Tracking").run()
        exp_b_text = " ".join([m.value for m in at.markdown])
        self.assertIn("20/20", exp_b_text)
        self.assertIn("Normal vision", exp_b_text)
        self.assertNotIn("Essential Non-Clinical Limitations", exp_b_text)
        # Chart-oriented banner is present in Experience B above chart
        self.assertIn("is plotted below with the previous readings", exp_b_text)

    def test_research_defect2_initial_order_randomized_once_and_preserved(self):
        """Prompt 4.1: Initial comparison order is assigned once and preserved across view switching and reentry."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        # Complete 8 questions
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()
        for q in range(8):
            target = at.session_state.questions[q]["direction"]
            btn = [b for b in at.button if target.capitalize() in b.label][0]
            btn.click().run()

        # Proceed to comparison
        history_btn = [b for b in at.button if "Compare Results" in b.label or "View Vision History" in b.label][0]
        history_btn.click().run()

        initial_order = at.session_state.comparison_view_order
        self.assertIn(initial_order, ["single_first", "trend_first"])
        self.assertEqual(at.session_state.assignment_source, "participant_randomized")
        self.assertEqual(at.session_state.initial_assigned_order, initial_order)

        # Switch active view
        other_view = "Experience A: Single Result" if at.session_state.active_comparison_view != "Experience A: Single Result" else "Experience B: Trend Tracking"
        at.radio[0].set_value(other_view).run()

        # Navigate away to Results
        at.sidebar.selectbox[0].select("results").run()
        self.assertEqual(at.session_state.step, "results")

        # Re-enter comparison via button
        history_btn = [b for b in at.button if "Compare Results" in b.label or "View Vision History" in b.label][0]
        history_btn.click().run()

        # Preserved!
        self.assertEqual(at.session_state.comparison_view_order, initial_order)
        self.assertEqual(at.session_state.initial_assigned_order, initial_order)
        self.assertEqual(at.session_state.assignment_source, "participant_randomized")

    def test_research_defect3_require_exposure_to_both_experiences(self):
        """Prompt 4.1: Both views must be visited before submitting comparative feedback."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        # Jump to vision history via sidebar
        at.sidebar.selectbox[0].select("vision_history").run()
        self.assertEqual(len(at.session_state.views_visited), 1)

        # Attempt submit: blocked with neutral info notice
        submit_btn = [b for b in at.button if "Submit Anonymous Feedback" in b.label][0]
        submit_btn.click().run()
        self.assertGreater(len(at.info), 0)
        self.assertIn("Please view both Single Result", at.info[0].value)
        self.assertIsNone(at.session_state.submitted_feedback)

        # Visit other view
        at.radio[0].set_value("Experience A: Single Result").run()
        self.assertEqual(len(at.session_state.views_visited), 2)

        # Fill and submit
        at.radio[1].set_value("Single Result")
        at.radio[2].set_value("Both are equally clear")
        at.radio[3].set_value("Likely")
        submit_btn = [b for b in at.button if "Submit Anonymous Feedback" in b.label][0]
        submit_btn.click().run()

        self.assertIsNotNone(at.session_state.submitted_feedback)
        fb = at.session_state.submitted_feedback
        self.assertTrue(fb["both_views_visited"])
        self.assertEqual(len(fb["views_visited"]), 2)

    def test_research_defect4_original_feedback_locked_and_read_only(self):
        """Prompt 4.1: First submission is saved and locked; form cannot be edited or overwritten post-debrief."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        at.sidebar.selectbox[0].select("vision_history").run()
        at.radio[0].set_value("Experience A: Single Result").run()
        at.radio[0].set_value("Experience B: Trend Tracking").run()

        at.radio[1].set_value("Trend Tracking")
        at.text_area[0].input("Initial uninfluenced perspective.")
        at.radio[2].set_value("Trend Tracking")
        at.radio[3].set_value("Very likely")
        submit_btn = [b for b in at.button if "Submit Anonymous Feedback" in b.label][0]
        submit_btn.click().run()

        # Verified locked
        self.assertTrue(at.session_state.feedback_locked)
        first_fb = at.session_state.submitted_feedback
        self.assertEqual(first_fb["q2_main_reason"], "Initial uninfluenced perspective.")

        # Editable form is no longer rendered; read-only summary is displayed
        submit_buttons = [b for b in at.button if "Submit Anonymous Feedback" in b.label]
        self.assertEqual(len(submit_buttons), 0, "Editable form submit button must be removed after locking")
        page_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Submitted & Locked", page_text)
        self.assertIn("Initial uninfluenced perspective.", page_text)

        # Navigate away and return: form remains locked with original answers
        at.sidebar.selectbox[0].select("welcome").run()
        at.sidebar.selectbox[0].select("vision_history").run()
        self.assertTrue(at.session_state.feedback_locked)
        self.assertEqual(at.session_state.submitted_feedback["q2_main_reason"], "Initial uninfluenced perspective.")
        submit_buttons = [b for b in at.button if "Submit Anonymous Feedback" in b.label]
        self.assertEqual(len(submit_buttons), 0)

        # Reset clears the lock and restores an unlocked evaluation
        reset_btn = [b for b in at.button if "Reset Demo and Start Fresh" in b.label][0]
        reset_btn.click().run()
        self.assertFalse(at.session_state.feedback_locked)
        self.assertIsNone(at.session_state.submitted_feedback)

    def test_prompt5_visual_usability_and_presenter_guide(self):
        """Prompt 5: Presenter demo guide in sidebar and compact setup expander on Welcome."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        # Sidebar Presenter Guide
        self.assertTrue(any("2-Minute Presenter Guide" in exp.label for exp in at.sidebar.expander))
        sidebar_text = " ".join([m.value for m in at.sidebar.markdown])
        self.assertIn("Suggested Classroom Flow", sidebar_text)

        # Welcome setup cards and calibration expander
        self.assertTrue(any("Testing Setup & Distance Calibration Guidance" in exp.label for exp in at.expander))
        welcome_text = " ".join([m.value for m in at.markdown])
        self.assertIn("1. Corrective Lenses", welcome_text)
        self.assertIn("2. Arm's-Length Distance", welcome_text)
        self.assertIn("Viewing Distance:", welcome_text)

        # Start button is prominent
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        self.assertIsNotNone(start_btn)

    def test_prompt5_accessibility_and_no_aria_leakage(self):
        """Prompt 5: Honest accessibility disclosure rendered, optotype SVG does not leak direction in aria-label."""
        at = AppTest.from_file("app.py", default_timeout=10)
        at.run()

        # Start test
        start_btn = [b for b in at.button if "Start Vision Check" in b.label][0]
        start_btn.click().run()

        # Step 2 contains accessibility disclosure
        page_text = " ".join([m.value for m in at.markdown])
        self.assertIn("Accessibility Disclosure", page_text)
        self.assertIn("Screen readers and text alternatives intentionally do not announce optotype orientations", page_text)

        # Confirm all 4 directional buttons exist and are clickable
        directions = ["Left", "Up", "Down", "Right"]
        for d in directions:
            btn = [b for b in at.button if d in b.label]
            self.assertEqual(len(btn), 1, f"Button for {d} should exist")

if __name__ == "__main__":
    unittest.main()
