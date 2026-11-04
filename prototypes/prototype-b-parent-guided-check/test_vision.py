import copy
from datetime import datetime, timedelta, timezone
import json
import random
import unittest

from streamlit.testing.v1 import AppTest
from vision import (DIRECTIONS, GLASSES, PROTOCOL, fictional_history, import_history,
                    export_history, new_check, record_response, save_check, size_px,
                    summarize, validate_record, window_summary)

NOW = datetime(2026, 10, 30, 12, tzinfo=timezone.utc)
SETUP = {"profile": "Child A", "eye": "Both eyes", "glasses": GLASSES[0],
         "screen": "Home laptop", "distance_mm": 3000, "reference_px": 324}


def completed(at=NOW-timedelta(days=1), correct=12, setup=None):
    check = new_check(setup or SETUP, at, random.Random(11))
    check["practice_complete"] = True
    for i, trial in enumerate(check["trials"]):
        record_response(check, i, trial["target"] if i < correct else "cant_tell", at+timedelta(seconds=i+1))
    return check


class VisionLogicTests(unittest.TestCase):
    def test_calibration_scales_with_distance_and_reference(self):
        self.assertAlmostEqual(size_px(20, SETUP), 16.52, delta=.03)
        self.assertAlmostEqual(size_px(20, {**SETUP, "distance_mm": 1500}), size_px(20, SETUP)/2)
        self.assertAlmostEqual(size_px(20, {**SETUP, "reference_px": 600}), size_px(20, SETUP)*600/324)
        self.assertAlmostEqual(size_px(80, SETUP)/size_px(20, SETUP), 4, delta=.001)
        with self.assertRaises(ValueError):
            new_check({**SETUP, "reference_px": -1})

    def test_practice_pause_and_stale_answer_guards(self):
        c = new_check(SETUP)
        self.assertFalse(record_response(c, 0, "right"))
        c["practice_complete"] = True
        c["paused"] = True
        self.assertFalse(record_response(c, 0, "right"))
        c["paused"] = False
        self.assertTrue(record_response(c, 0, "cant_tell"))
        self.assertFalse(record_response(c, 0, "right"))
        self.assertFalse(record_response(c, 1, "bogus"))
        with self.assertRaises(ValueError):
            summarize(c)

    def test_result_uses_all_trials_and_saves_once(self):
        c = completed(correct=7)
        result = summarize(c)
        self.assertEqual(result["correct"], 7)
        self.assertEqual([r["Correct"] for r in result["levels"]], [4, 3, 0])
        history = []
        self.assertTrue(save_check(history, c))
        self.assertFalse(save_check(history, c))
        self.assertEqual(len(history), 1)
        c["responses"][0]["choice"] = "cant_tell"
        self.assertEqual(summarize(history[0])["correct"], 7)

    def test_windows_include_boundary_and_handle_previous_empty(self):
        # Completion ends 12 seconds after starting.
        boundary = completed(NOW-timedelta(days=7, seconds=12), correct=12)
        previous = completed(NOW-timedelta(days=8), correct=6)
        outside = completed(NOW-timedelta(days=15))
        result = window_summary([boundary, previous, outside], 7, NOW)
        self.assertEqual((result["count"], result["previous_count"]), (1, 1))
        self.assertEqual(result["delta_points"], 50)
        self.assertIsNone(window_summary([boundary], 7, NOW)["delta_points"])
        self.assertEqual(window_summary([outside], 7, NOW)["count"], 0)
        self.assertEqual(window_summary([boundary, previous, outside], None, NOW)["count"], 3)
        for days in (30, 90):
            self.assertEqual(window_summary([boundary], days, NOW)["count"], 1)

    def test_mixed_child_eye_or_setup_is_rejected(self):
        first = completed()
        for key, value in (("profile", "Child B"), ("eye", "Right eye"), ("glasses", GLASSES[1]),
                           ("distance_mm", 1500), ("reference_px", 325), ("screen", "Home tablet")):
            other = completed(setup={**SETUP, key: value})
            with self.assertRaises(ValueError):
                window_summary([first, other], 30, NOW)

    def test_portable_history_roundtrip_and_deduplication(self):
        records = [validate_record(completed(), NOW)]
        restored = import_history(export_history(records), [], NOW)
        self.assertEqual(restored, records)
        self.assertEqual(import_history(export_history(records), restored, NOW), records)
        altered = copy.deepcopy(records)
        altered[0]["responses"][0]["choice"] = "cant_tell"
        with self.assertRaises(ValueError):
            import_history(export_history(altered), records, NOW)

    def test_bad_import_is_atomic_and_rejects_future_or_example(self):
        existing = [validate_record(completed(), NOW)]
        broken = completed(NOW+timedelta(days=1))
        for payload in ({"schema":"unknown", "records":[]},
                        {"schema":"focal-family-history-v1", "records":[completed(), broken]},
                        {"schema":"focal-family-history-v1", "records":fictional_history(NOW)}):
            with self.assertRaises(ValueError):
                import_history(json.dumps(payload), existing, NOW)
            self.assertEqual(len(existing), 1)
        for key, value in (("trials", []), ("completed_at", "2026-10-30"), ("responses", [None]*12)):
            c = completed()
            c[key] = value
            with self.assertRaises(ValueError):
                validate_record(c, NOW)
        with self.assertRaises(ValueError):
            import_history('x'*5_000_001, existing, NOW)


class VisionJourneyTests(unittest.TestCase):
    def setUp(self):
        self.at = AppTest.from_file("app.py", default_timeout=20).run()
        self.at.radio(key="family_workspace").set_value("Live vision check").run()

    def press(self, key):
        self.at.button(key=key).click().run()
        self.assertEqual(list(self.at.exception), [])

    def begin(self):
        self.assertTrue(self.at.button(key="vision_begin").disabled)
        for i in range(4):
            self.at.checkbox(key=f"vision_confirm_{i}").check()
        self.at.run()
        self.press("vision_begin")
        self.press("vision_practice_right")

    def test_live_check_save_history_another_and_parent_activity(self):
        self.begin()
        for i in range(12):
            c = self.at.session_state["vision_check"]
            self.press(f"vision_answer_{i}_{c['trials'][i]['target']}")
        self.assertEqual(summarize(self.at.session_state["vision_check"])["correct"], 12)
        self.press("vision_save")
        self.assertEqual(len(self.at.session_state["vision_records"]), 1)
        self.assertFalse(any(b.key == "vision_save" for b in self.at.button))
        self.press("vision_to_history")
        self.assertEqual(self.at.radio(key="vision_dataset").value, "My saved checks")
        self.assertEqual(self.at.metric[0].value, "1")
        self.at.selectbox(key="vision_window").set_value("All time").run()
        self.assertEqual(list(self.at.exception), [])
        self.at.radio(key="family_workspace").set_value("Parent activity").run()
        self.press("family_reset")
        self.assertEqual(len(self.at.session_state["vision_records"]), 1)

    def test_pause_discard_and_new_check(self):
        self.begin()
        self.press("vision_cant_0")
        self.press("vision_pause")
        self.assertFalse(any(str(b.key).startswith('vision_answer_') for b in self.at.button))
        self.press("vision_resume")
        self.assertEqual(len(self.at.session_state["vision_check"]["responses"]), 1)
        self.press("vision_discard")
        self.assertIsNone(self.at.session_state["vision_check"])
        self.assertEqual(self.at.session_state["vision_records"], [])
        self.assertTrue(self.at.button(key="vision_begin").disabled)

    def test_example_never_enters_live_history_and_clear_is_explicit(self):
        self.at.radio(key="family_workspace").set_value("Performance history").run()
        self.assertEqual(self.at.session_state["vision_records"], [])
        self.at.radio(key="vision_dataset").set_value("Fictional example history").run()
        self.assertTrue(any('Fictional' in w.value for w in self.at.warning))
        self.assertEqual(self.at.session_state["vision_records"], [])
        for window in ("7 days", "90 days", "All time"):
            self.at.selectbox(key="vision_window").set_value(window).run()
            self.assertEqual(list(self.at.exception), [])
        self.at.session_state["vision_records"] = [validate_record(completed(), NOW)]
        self.at.radio(key="vision_dataset").set_value("My saved checks").run()
        self.assertTrue(self.at.button(key="vision_clear").disabled)
        self.at.checkbox(key="vision_delete_confirm").check().run()
        self.press("vision_clear")
        self.assertEqual(self.at.session_state["vision_records"], [])


if __name__ == "__main__":
    unittest.main()
