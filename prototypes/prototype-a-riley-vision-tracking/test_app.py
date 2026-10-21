"""
Unit tests for Focal Monitor (Prototype A)
Tests logic, optotype generation, data structures, and state transitions.
"""

import unittest
import pandas as pd
import app

class TestFocalMonitor(unittest.TestCase):
    
    def test_generate_questions(self):
        questions = app.generate_questions()
        self.assertEqual(len(questions), 8, "Should generate exactly 8 questions")
        
        valid_directions = {"up", "right", "down", "left"}
        directions_found = set()
        
        for q in questions:
            self.assertIn("id", q)
            self.assertIn("direction", q)
            self.assertIn("size_px", q)
            self.assertIn(q["direction"], valid_directions)
            self.assertGreater(q["size_px"], 0)
            directions_found.add(q["direction"])
            
        # Verify that multiple directions are represented
        self.assertGreaterEqual(len(directions_found), 2, "Questions should have directional variety")
        
    def test_render_tumbling_e_svg(self):
        for direction in ["up", "right", "down", "left"]:
            svg = app.render_tumbling_e_svg(direction, 100)
            self.assertIn("<svg", svg)
            self.assertIn("</svg>", svg)
            self.assertIn("rect", svg)
            self.assertIn(direction, svg)
            
    def test_fictional_records_structure(self):
        records = app.FICTIONAL_RECORDS
        self.assertEqual(len(records), 7, "Should have 7 historical fictional baseline records")
        for rec in records:
            self.assertIn("Date", rec)
            self.assertIn("Session", rec)
            self.assertIn("Correct", rec)
            self.assertIn("Total", rec)
            self.assertIn("Accuracy", rec)
            self.assertIn("Type", rec)
            self.assertEqual(rec["Type"], "Illustrative Demo Data")
            self.assertEqual(rec["Total"], 8)
            self.assertGreaterEqual(rec["Correct"], 0)
            self.assertLessEqual(rec["Correct"], 8)
            
    def test_combined_history_dataframe(self):
        # Simulate adding today's live demo check
        live_record = {
            "Date": "2026-10-21",
            "Session": "Today (Demo Check)",
            "Correct": 7,
            "Total": 8,
            "Accuracy": 87.5,
            "Type": "Your Completed Demo Check",
            "Notes": "Current interactive prototype check"
        }
        combined = list(app.FICTIONAL_RECORDS) + [live_record]
        df = pd.DataFrame(combined)
        
        self.assertEqual(len(df), 8)
        self.assertEqual(len(df[df["Type"] == "Illustrative Demo Data"]), 7)
        self.assertEqual(len(df[df["Type"] == "Your Completed Demo Check"]), 1)
        self.assertEqual(df.iloc[-1]["Session"], "Today (Demo Check)")
        self.assertEqual(df.iloc[-1]["Correct"], 7)

    def test_resume_test(self):
        import streamlit as st
        st.session_state.clear()
        app.initialize_session_state()
        
        # 0 answers -> resumes to index 0
        app.resume_test()
        self.assertEqual(st.session_state.step, "vision_check")
        self.assertEqual(st.session_state.current_question_index, 0)
        
        # 3 answers recorded
        for i in range(3):
            app.record_response("right", i, "right", 100, 8)
        self.assertEqual(len(st.session_state.answers), 3)
        
        # User is at results or history and clicks resume
        st.session_state.step = "results"
        app.resume_test()
        self.assertEqual(st.session_state.step, "vision_check")
        self.assertEqual(st.session_state.current_question_index, 3) # points to Q4
        
        # Complete remaining 5 answers
        for i in range(3, 8):
            app.record_response("right", i, "right", 100, 8)
        self.assertEqual(len(st.session_state.answers), 8)
        
        # Resume when already completed routes to results
        app.resume_test()
        self.assertEqual(st.session_state.step, "results")
        self.assertEqual(st.session_state.current_question_index, 8)

    def test_record_response_idempotency_and_limits(self):
        import streamlit as st
        st.session_state.clear()
        app.initialize_session_state()
        
        # Record answers for questions 1 through 8
        for i in range(8):
            app.record_response("right", i, "right", 100, 8)
            
        self.assertEqual(len(st.session_state.answers), 8)
        self.assertEqual(st.session_state.step, "results")
        self.assertEqual(st.session_state.nav_jump_select, "results")
        self.assertEqual(st.session_state.current_question_index, 8)
        
        # Attempt 9th answer submission (simulate replay or stale event)
        app.record_response("right", 8, "right", 100, 8)
        self.assertEqual(len(st.session_state.answers), 8, "Answers must strictly remain 8")
        
        # Attempt duplicate submission for question 8
        app.record_response("up", 7, "right", 100, 8)
        self.assertEqual(len(st.session_state.answers), 8, "Cannot append duplicate for question 8")

    def test_reset_and_start_vision_check(self):
        import streamlit as st
        st.session_state.clear()
        app.initialize_session_state()
        
        # Simulate some answers
        app.record_response("left", 0, "left", 120, 8)
        self.assertEqual(len(st.session_state.answers), 1)
        
        # Reset
        app.reset_demo()
        self.assertEqual(st.session_state.step, "welcome")
        self.assertEqual(st.session_state.nav_jump_select, "welcome")
        self.assertEqual(len(st.session_state.answers), 0)
        self.assertEqual(st.session_state.current_question_index, 0)
        
        # Start vision check
        app.start_vision_check()
        self.assertEqual(st.session_state.step, "vision_check")
        self.assertEqual(st.session_state.nav_jump_select, "vision_check")
        self.assertEqual(len(st.session_state.answers), 0)

    def test_is_valid_completed_session_valid(self):
        questions = app.generate_questions()
        valid_answers = []
        for i, q in enumerate(questions):
            valid_answers.append({
                "question_num": i + 1,
                "target_direction": q["direction"],
                "user_response": q["direction"],
                "is_correct": True,
                "size_px": q["size_px"]
            })
        timestamp = "2026-10-21 01:30"
        self.assertTrue(app.is_valid_completed_session(valid_answers, timestamp, questions))
        self.assertTrue(app.is_valid_completed_session(valid_answers, timestamp))

    def test_is_valid_completed_session_missing_or_blank_timestamp(self):
        questions = app.generate_questions()
        valid_answers = [
            {"question_num": i + 1, "target_direction": q["direction"], "user_response": q["direction"], "is_correct": True, "size_px": q["size_px"]}
            for i, q in enumerate(questions)
        ]
        self.assertFalse(app.is_valid_completed_session(valid_answers, None, questions))
        self.assertFalse(app.is_valid_completed_session(valid_answers, "", questions))
        self.assertFalse(app.is_valid_completed_session(valid_answers, "   ", questions))
        self.assertFalse(app.is_valid_completed_session(valid_answers, 12345, questions))

    def test_is_valid_completed_session_duplicate_or_missing_qids(self):
        # Fault injection test: 8 duplicate Q1 responses
        timestamp = "2026-10-21 01:30"
        dup_answers = [
            {"question_num": 1, "target_direction": "up", "user_response": "up", "is_correct": True, "size_px": 100}
            for _ in range(8)
        ]
        self.assertFalse(app.is_valid_completed_session(dup_answers, timestamp))

        # Missing Q8, duplicated Q7
        mixed_answers = [
            {"question_num": i if i <= 7 else 7, "target_direction": "up", "user_response": "up", "is_correct": True, "size_px": 100}
            for i in range(1, 9)
        ]
        self.assertFalse(app.is_valid_completed_session(mixed_answers, timestamp))

    def test_is_valid_completed_session_counts(self):
        timestamp = "2026-10-21 01:30"
        self.assertFalse(app.is_valid_completed_session([], timestamp))
        one_answer = [{"question_num": 1, "target_direction": "up", "user_response": "up", "is_correct": True, "size_px": 100}]
        self.assertFalse(app.is_valid_completed_session(one_answer, timestamp))
        seven_answers = [
            {"question_num": i, "target_direction": "up", "user_response": "up", "is_correct": True, "size_px": 100}
            for i in range(1, 8)
        ]
        self.assertFalse(app.is_valid_completed_session(seven_answers, timestamp))

    def test_is_valid_completed_session_schema_integrity(self):
        timestamp = "2026-10-21 01:30"
        base_answers = [
            {"question_num": i, "target_direction": "up", "user_response": "up", "is_correct": True, "size_px": 100}
            for i in range(1, 9)
        ]

        # Missing key
        bad_keys = [dict(a) for a in base_answers]
        del bad_keys[0]["size_px"]
        self.assertFalse(app.is_valid_completed_session(bad_keys, timestamp))

        # Invalid direction string
        bad_dir = [dict(a) for a in base_answers]
        bad_dir[0]["target_direction"] = "diagonal"
        self.assertFalse(app.is_valid_completed_session(bad_dir, timestamp))

        # Inconsistent is_correct
        bad_correct = [dict(a) for a in base_answers]
        bad_correct[0]["is_correct"] = False  # target='up', resp='up'
        self.assertFalse(app.is_valid_completed_session(bad_correct, timestamp))

        # Non-positive size_px
        bad_size = [dict(a) for a in base_answers]
        bad_size[0]["size_px"] = 0
        self.assertFalse(app.is_valid_completed_session(bad_size, timestamp))

        # Not a dict
        bad_elem = list(base_answers)
        bad_elem[0] = "string"
        self.assertFalse(app.is_valid_completed_session(bad_elem, timestamp))

    def test_parse_completion_timestamp(self):
        # Valid
        dt = app.parse_completion_timestamp("2026-10-21 01:30")
        self.assertIsNotNone(dt)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 10)
        self.assertEqual(dt.day, 21)
        self.assertEqual(dt.hour, 1)
        self.assertEqual(dt.minute, 30)

        # Invalid formats
        self.assertIsNone(app.parse_completion_timestamp("not-a-timestamp"))
        self.assertIsNone(app.parse_completion_timestamp("2026-02-30 25:99"))
        self.assertIsNone(app.parse_completion_timestamp("2026-10-21"))
        self.assertIsNone(app.parse_completion_timestamp("2026-10-21 01:30:00"))
        self.assertIsNone(app.parse_completion_timestamp(""))
        self.assertIsNone(app.parse_completion_timestamp("   "))
        self.assertIsNone(app.parse_completion_timestamp(None))
        self.assertIsNone(app.parse_completion_timestamp(12345))

    def test_is_valid_completed_session_invalid_timestamps(self):
        questions = app.generate_questions()
        valid_answers = [
            {"question_num": i + 1, "target_direction": q["direction"], "user_response": q["direction"], "is_correct": True, "size_px": q["size_px"]}
            for i, q in enumerate(questions)
        ]
        self.assertFalse(app.is_valid_completed_session(valid_answers, "not-a-timestamp", questions))
        self.assertFalse(app.is_valid_completed_session(valid_answers, "2026-02-30 25:99", questions))
        self.assertTrue(app.is_valid_completed_session(valid_answers, "2026-10-21 01:30", questions))

    def test_is_valid_completed_session_rejects_boolean_ids_and_sizes(self):
        base_answers = [
            {"question_num": i, "target_direction": "up", "user_response": "up", "is_correct": True, "size_px": 100}
            for i in range(1, 9)
        ]
        timestamp = "2026-10-21 01:30"

        # question_num is True (which Python treats as 1 if not checked strictly)
        bool_qid = [dict(a) for a in base_answers]
        bool_qid[0]["question_num"] = True
        self.assertFalse(app.is_valid_completed_session(bool_qid, timestamp))

        # size_px is True
        bool_size = [dict(a) for a in base_answers]
        bool_size[0]["size_px"] = True
        self.assertFalse(app.is_valid_completed_session(bool_size, timestamp))

        # is_correct is 1 instead of True
        int_correct = [dict(a) for a in base_answers]
        int_correct[0]["is_correct"] = 1
        self.assertFalse(app.is_valid_completed_session(int_correct, timestamp))

    def test_is_valid_partial_session(self):
        questions = app.generate_questions()
        # 3 valid answers
        valid_3 = [
            {"question_num": i + 1, "target_direction": questions[i]["direction"], "user_response": questions[i]["direction"], "is_correct": True, "size_px": questions[i]["size_px"]}
            for i in range(3)
        ]
        self.assertTrue(app.is_valid_partial_session(valid_3, questions))

        # 0 answers -> False
        self.assertFalse(app.is_valid_partial_session([], questions))

        # 8 answers -> False (must be partial, not complete)
        valid_8 = [
            {"question_num": i + 1, "target_direction": questions[i]["direction"], "user_response": questions[i]["direction"], "is_correct": True, "size_px": questions[i]["size_px"]}
            for i in range(8)
        ]
        self.assertFalse(app.is_valid_partial_session(valid_8, questions))

        # Malformed: missing key
        bad_partial = [dict(a) for a in valid_3]
        del bad_partial[0]["target_direction"]
        self.assertFalse(app.is_valid_partial_session(bad_partial, questions))

        # Malformed: non-dict element
        self.assertFalse(app.is_valid_partial_session(["not-a-dict"], questions))
        self.assertFalse(app.is_valid_partial_session([{"broken": 1}], questions))

        # Malformed: boolean question_num
        bad_bool_qid = [dict(a) for a in valid_3]
        bad_bool_qid[0]["question_num"] = True
        self.assertFalse(app.is_valid_partial_session(bad_bool_qid, questions))

        # Malformed: non-contiguous question_nums
        jump_qids = [
            {"question_num": 2, "target_direction": "up", "user_response": "up", "is_correct": True, "size_px": 100}
        ]
        self.assertFalse(app.is_valid_partial_session(jump_qids, questions))

    def test_resume_test_with_corrupted_session_restarts_cleanly(self):
        import streamlit as st
        st.session_state.clear()
        app.initialize_session_state()

        # Inject malformed partial record
        st.session_state.answers = [{"corrupted": "record"}]
        st.session_state.step = "results"

        # Resume test should safely recover by starting fresh rather than crashing
        app.resume_test()
        self.assertEqual(st.session_state.step, "vision_check")
        self.assertEqual(st.session_state.current_question_index, 0)
        self.assertEqual(len(st.session_state.answers), 0)

    def test_proceed_to_comparison_randomizes_and_preserves_order(self):
        """Prompt 4.1: proceed_to_comparison assigns order once and preserves through re-entry."""
        import streamlit as st

        # Over 50 separate evaluations, both randomization orders occur
        observed_orders = set()
        for _ in range(50):
            st.session_state.clear()
            app.initialize_session_state()
            app.proceed_to_comparison()
            self.assertEqual(st.session_state.step, "vision_history")
            self.assertEqual(st.session_state.nav_jump_select, "vision_history")
            self.assertIn(st.session_state.comparison_view_order, ["single_first", "trend_first"])
            self.assertEqual(st.session_state.initial_assigned_order, st.session_state.comparison_view_order)
            self.assertEqual(st.session_state.assignment_source, "participant_randomized")
            if st.session_state.comparison_view_order == "single_first":
                self.assertEqual(st.session_state.active_comparison_view, "Experience A: Single Result")
            else:
                self.assertEqual(st.session_state.active_comparison_view, "Experience B: Trend Tracking")
            observed_orders.add(st.session_state.comparison_view_order)

        self.assertEqual(observed_orders, {"single_first", "trend_first"})

        # Within the same evaluation, multiple re-entries preserve the assigned order
        st.session_state.clear()
        app.initialize_session_state()
        app.proceed_to_comparison()
        assigned_order = st.session_state.comparison_view_order

        # Simulate user navigating away to results and re-entering comparison
        st.session_state.step = "results"
        app.proceed_to_comparison()
        self.assertEqual(st.session_state.comparison_view_order, assigned_order)
        self.assertEqual(st.session_state.initial_assigned_order, assigned_order)

    def test_set_active_view_updates_state(self):
        """Prompt 4: set_active_view synchronizes active view and widget state."""
        import streamlit as st
        st.session_state.clear()
        app.initialize_session_state()

        app.set_active_view("Experience A: Single Result")
        self.assertEqual(st.session_state.active_comparison_view, "Experience A: Single Result")
        self.assertEqual(st.session_state.comparison_view_selector, "Experience A: Single Result")

        app.set_active_view("Experience B: Trend Tracking")
        self.assertEqual(st.session_state.active_comparison_view, "Experience B: Trend Tracking")
        self.assertEqual(st.session_state.comparison_view_selector, "Experience B: Trend Tracking")

    def test_reset_demo_clears_comparison_and_feedback(self):
        """Prompt 4.1: reset_demo clears feedback lock, views visited, and comparison state."""
        import streamlit as st
        st.session_state.clear()
        app.initialize_session_state()

        st.session_state.submitted_feedback = {
            "q1_preferred_experience": "Experience B (Trend Tracking)",
            "q2_main_reason": "Context over time",
            "q3_easier_to_understand": "Experience A (Single Result)",
            "q4_reuse_likelihood": "Likely",
            "initial_assigned_order": "trend_first",
            "assignment_source": "participant_randomized",
            "both_views_visited": True,
            "views_visited": ["Experience B: Trend Tracking", "Experience A: Single Result"],
            "evaluated_score": "8/8",
            "submitted_at": "2026-10-21 02:00:00"
        }
        st.session_state.feedback_locked = True
        st.session_state.views_visited = ["Experience B: Trend Tracking", "Experience A: Single Result"]
        st.session_state.comparison_order_assigned = True
        st.session_state.active_comparison_view = "Experience A: Single Result"
        st.session_state.comparison_view_order = "single_first"
        st.session_state.comparison_view_selector = "Experience A: Single Result"
        st.session_state.completed_at = "2026-10-21 02:00"
        st.session_state.answers = [{"dummy": 1}]

        app.reset_demo()

        self.assertEqual(st.session_state.step, "welcome")
        self.assertEqual(st.session_state.nav_jump_select, "welcome")
        self.assertIsNone(st.session_state.submitted_feedback)
        self.assertFalse(st.session_state.feedback_locked)
        self.assertEqual(st.session_state.views_visited, [])
        self.assertFalse(st.session_state.comparison_order_assigned)
        self.assertIsNone(st.session_state.completed_at)
        self.assertEqual(st.session_state.answers, [])
        self.assertEqual(st.session_state.comparison_view_order, "trend_first")
        self.assertEqual(st.session_state.active_comparison_view, "Experience B: Trend Tracking")

    def test_feedback_schema_json_serializable(self):
        """Prompt 4.1: feedback payload validates schema with exposure status and metadata."""
        import json
        feedback_record = {
            "q1_preferred_experience": "Experience B (Trend Tracking)",
            "q2_main_reason": "Helps detect gradual changes over weeks.",
            "q3_easier_to_understand": "Both are equally clear",
            "q4_reuse_likelihood": "Very likely",
            "initial_assigned_order": "single_first",
            "assignment_source": "participant_randomized",
            "both_views_visited": True,
            "views_visited": ["Experience A: Single Result", "Experience B: Trend Tracking"],
            "evaluated_score": "7/8",
            "submitted_at": "2026-10-21 02:00:00"
        }
        serialized = json.dumps(feedback_record, indent=2)
        deserialized = json.loads(serialized)
        self.assertEqual(deserialized, feedback_record)
        self.assertIn("q1_preferred_experience", deserialized)
        self.assertIn("q2_main_reason", deserialized)
        self.assertIn("q3_easier_to_understand", deserialized)
        self.assertIn("q4_reuse_likelihood", deserialized)
        self.assertIn("initial_assigned_order", deserialized)
        self.assertIn("assignment_source", deserialized)
        self.assertIn("both_views_visited", deserialized)
        self.assertIn("views_visited", deserialized)
        self.assertIn("evaluated_score", deserialized)
        self.assertIn("submitted_at", deserialized)

    def test_render_tumbling_e_svg_accessibility(self):
        """Prompt 5: Optotype SVG does not expose target direction in aria-label."""
        for d in ["up", "right", "down", "left"]:
            svg = app.render_tumbling_e_svg(d, 80)
            self.assertIn('aria-label="Visual Tumbling E demonstration optotype"', svg)
            self.assertNotIn(f'pointing {d}', svg.lower())
            self.assertIn(f'data-direction="{d}"', svg)

    def test_full_width_helper(self):
        """Prompt 5: full_width helper returns valid Streamlit width argument dictionary."""
        kwargs = app.full_width()
        self.assertIsInstance(kwargs, dict)
        self.assertTrue("width" in kwargs or "use_container_width" in kwargs)
        if "width" in kwargs:
            self.assertEqual(kwargs["width"], "stretch")
        else:
            self.assertTrue(kwargs["use_container_width"])

if __name__ == "__main__":
    unittest.main()
