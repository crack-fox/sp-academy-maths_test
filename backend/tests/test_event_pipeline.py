import unittest

from backend.analytics import compute_funnel, compute_student_stats, get_student_stats, segment_funnel
from backend.event_schema import validate_event
from backend.sample_events import generate_sample_events


class EventPipelineTests(unittest.TestCase):
    def setUp(self):
        self.events = generate_sample_events()

    def test_schema_validation_accepts_valid_event(self):
        ok, errors = validate_event(self.events[0])
        self.assertTrue(ok)
        self.assertEqual(errors, [])

    def test_schema_validation_rejects_invalid_event(self):
        bad_event = {
            "event_id": "not-uuid",
            "session_id": 123,
            "student_id": "Raphael",
            "event_name": "unsupported",
            "timestamp": "today",
            "metadata": "bad",
        }
        ok, errors = validate_event(bad_event)
        self.assertFalse(ok)
        self.assertGreaterEqual(len(errors), 4)

    def test_compute_funnel(self):
        funnel = compute_funnel(self.events)
        self.assertEqual(funnel["start_rate"], 1.0)
        self.assertEqual(funnel["completion_rate"], 1.0)
        self.assertEqual(funnel["upgrade_rate"], 0.5)
        self.assertEqual(funnel["conversion_rate"], 1.0)

    def test_compute_student_stats(self):
        stats = compute_student_stats(self.events, "Raphael")
        self.assertEqual(stats["total_xp"], 15.0)
        self.assertEqual(stats["accuracy"], 0.5)
        self.assertEqual(stats["total_questions_answered"], 2)

    def test_get_student_stats_by_session(self):
        stats = get_student_stats(self.events, "sess_1", "Raphael")
        self.assertEqual(stats["total_xp"], 65.0)
        self.assertEqual(stats["total_questions"], 12)
        self.assertEqual(stats["correct_answers"], 9)
        self.assertEqual(stats["accuracy"], 0.75)

    def test_get_student_stats_handles_missing(self):
        stats = get_student_stats(self.events, "sess_new", "NewStudent")
        self.assertEqual(stats["total_xp"], 0.0)
        self.assertEqual(stats["total_questions"], 0)
        self.assertEqual(stats["correct_answers"], 0)
        self.assertEqual(stats["accuracy"], 0.0)

    def test_segment_funnel(self):
        segmented = segment_funnel(self.events, "device")
        self.assertIn("desktop", segmented)
        self.assertIn("mobile", segmented)
        self.assertEqual(segmented["desktop"]["conversion_rate"], 1.0)


if __name__ == "__main__":
    unittest.main()
