import unittest
from unittest.mock import patch, MagicMock
import jwt
import datetime
from bson import ObjectId
import sys
import os

# Add backend directory to sys.path so we can import from app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from config import Config

class TestValidationLayer(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Prevent actually connecting to MongoDB or seeding it during app creation
        cls.patch_db = patch("database.db.db_manager.connect")
        cls.patch_seed = patch("app.seed_database")
        cls.patch_db.start()
        cls.patch_seed.start()
        
        cls.app = create_app()
        cls.client = cls.app.test_client()
        
        # Generate a mock JWT token
        payload = {
            "sub": "507f1f77bcf86cd799439011",
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        }
        cls.token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")
        cls.headers = {
            "Authorization": f"Bearer {cls.token}"
        }

    @classmethod
    def tearDownClass(cls):
        cls.patch_db.stop()
        cls.patch_seed.stop()

    def setUp(self):
        # Setup mocks for User, Report, and Mood models
        self.patch_find_user = patch("database.user_model.UserModel.find_by_id")
        self.mock_find_user = self.patch_find_user.start()
        self.addCleanup(self.patch_find_user.stop)
        self.mock_find_user.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "email": "test@student.com",
            "name": "Test Student",
            "birth_year": 2003,
            "gender": "Male"
        }
        
        self.patch_create_report = patch("database.report_model.ReportModel.create_report")
        self.mock_create_report = self.patch_create_report.start()
        self.addCleanup(self.patch_create_report.stop)
        self.mock_create_report.return_value = {"_id": "mock_report_id"}

        self.patch_log_mood = patch("database.mood_model.MoodModel.log_mood")
        self.mock_log_mood = self.patch_log_mood.start()
        self.addCleanup(self.patch_log_mood.stop)
        self.mock_log_mood.return_value = None

        self.patch_requests_post = patch("requests.post")
        self.mock_requests_post = self.patch_requests_post.start()
        self.addCleanup(self.patch_requests_post.stop)
        
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"probability": 0.25}
        self.mock_requests_post.return_value = mock_resp

    def test_valid_input_passes(self):
        """Verify that a valid set of parameters successfully passes validation."""
        valid_payload = {
            "text": "I feel extremely happy and proud of my work today. I feel calm and relaxed."
        }
        response = self.client.post("/api/predict", json=valid_payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("metrics", data)
        self.assertIn("final_risk_level", data["metrics"])
        self.assertIn(data["metrics"]["final_risk_level"], ["Low", "Moderate", "High"])

    def test_text_too_short(self):
        """Verify text with < 20 characters is rejected."""
        payload = {
            "text": "tea hello fun day" # < 20 chars
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("must be at least 20 characters", response.get_json()["message"])

    def test_text_only_numbers_rejected(self):
        """Verify text consisting of only numbers is rejected."""
        payload = {
            "text": "12345 67890 12345 67890 12345 67890" # only numbers
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Journal text cannot consist of only numbers", response.get_json()["message"])

    def test_text_only_symbols_rejected(self):
        """Verify text consisting of only symbols is rejected."""
        payload = {
            "text": "!!! @@@ ### $$$ %%% ^^^ &&& *** (((" # only symbols
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Journal text cannot consist of only symbols", response.get_json()["message"])

    def test_text_character_repetition_rejected(self):
        """Verify text with character repetitions is rejected."""
        payload = {
            "text": "I feel extremely tired today. sssssssssssso tired."
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("keyboard spam detected", response.get_json()["message"])

    def test_text_word_repetition_rejected(self):
        """Verify text with consecutive identical words repeated is rejected."""
        payload = {
            "text": "I feel tired tired tired tired today and exhausted."
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("repeated nonsense tokens detected", response.get_json()["message"])

    def test_crisis_safety_override(self):
        """Verify crisis text trigger overrides risk level to High with crisis flag."""
        payload = {
            "text": "I feel extremely desperate and I want to commit suicide today."
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["metrics"]["crisis_triggered"])
        self.assertEqual(data["metrics"]["final_risk_level"], "High")
        self.assertIn("helplines", data["metrics"])

    def test_gibberish_text_rejected(self):
        """Verify gibberish pre-processing detection blocks gibberish texts."""
        payload = {
            "text": "sjdkvndibjsndbi asdasdasd qwertyqwerty zxczxczxcvbnm mnbvcxzlkjhg"
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Please enter meaningful journal content", response.get_json()["message"])

if __name__ == "__main__":
    unittest.main()
