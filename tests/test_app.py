import unittest

from fastapi import HTTPException

from src.app import activities, signup_for_activity, unregister_from_activity


class SignupCapacityTests(unittest.TestCase):
    activity_name = "Capacity Test"

    def setUp(self):
        activities[self.activity_name] = {
            "description": "Test activity",
            "schedule": "Test schedule",
            "max_participants": 2,
            "participants": ["full@example.com"],
        }

    def tearDown(self):
        activities.pop(self.activity_name, None)

    def test_accepts_last_available_spot(self):
        result = signup_for_activity(self.activity_name, "last@example.com")

        self.assertIn("last@example.com", result["message"])
        self.assertEqual(
            activities[self.activity_name]["participants"],
            ["full@example.com", "last@example.com"],
        )

    def test_rejects_registration_when_full(self):
        signup_for_activity(self.activity_name, "last@example.com")

        with self.assertRaises(HTTPException) as context:
            signup_for_activity(self.activity_name, "new@example.com")

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(context.exception.detail, "Activity is full")

    def test_rejects_duplicate_registration(self):
        with self.assertRaises(HTTPException) as context:
            signup_for_activity(self.activity_name, "full@example.com")

        self.assertEqual(context.exception.status_code, 400)

    def test_unregister_preserves_capacity_behavior(self):
        signup_for_activity(self.activity_name, "last@example.com")

        unregister_from_activity(self.activity_name, "last@example.com")

        self.assertEqual(
            activities[self.activity_name]["participants"],
            ["full@example.com"],
        )


if __name__ == "__main__":
    unittest.main()