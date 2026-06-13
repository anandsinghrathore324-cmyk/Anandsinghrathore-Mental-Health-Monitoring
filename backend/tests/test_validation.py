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
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
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
        self.mock_find_user.return_value = {
            "_id": ObjectId("507f1f77bcf86cd799439011"),
            "email": "test@student.com",
            "name": "Test Student"
        }
        
        self.patch_create_report = patch("database.report_model.ReportModel.create_report")
        self.mock_create_report = self.patch_create_report.start()
        self.mock_create_report.return_value = {"_id": "mock_report_id"}

        self.patch_log_mood = patch("database.mood_model.MoodModel.log_mood")
        self.mock_log_mood = self.patch_log_mood.start()
        self.mock_log_mood.return_value = None

    def test_valid_input_passes(self):
        """Verify that a valid set of parameters successfully passes validation."""
        valid_payload = {
            "age": 20,
            "gender": "Male",
            "academic_pressure": 5,
            "study_satisfaction": 5,
            "dietary_habits": "Moderate",
            "financial_stress": 5,
            "family_history": "No",
            "work_hours": 4.0,
            "anxiety_level": 5,
            "stress_level": 5,
            "study_hours": 6.0,
            "sleep_hours": 8.0,
            "screen_time": 5.0,
            "social_media_usage": 4.0,
            "mood": "calm",
            # Include lexicon trigger words like 'happy', 'proud', 'calm' to ensure high confidence (> 0.60)
            "text": "I feel extremely happy and proud of my work today. I feel calm and relaxed."
        }
        response = self.client.post("/api/predict", json=valid_payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("metrics", data)
        self.assertIn("top_positive_factors", data["metrics"])
        self.assertIn("top_negative_factors", data["metrics"])
        self.assertEqual(data["metrics"]["prediction_reliability"], "High")

    def test_invalid_age(self):
        """Verify age validation fails outside 13-100 bounds."""
        payload = {
            "age": 12,  # Under 13
            "gender": "Male",
            "academic_pressure": 5,
            "study_satisfaction": 5,
            "dietary_habits": "Moderate",
            "financial_stress": 5,
            "family_history": "No",
            "work_hours": 4.0,
            "anxiety_level": 5,
            "stress_level": 5,
            "study_hours": 6.0,
            "sleep_hours": 8.0,
            "screen_time": 5.0,
            "text": "I feel extremely happy and proud of my work today. I feel calm and relaxed."
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Age must be between 13 and 100", response.get_json()["message"])

    def test_invalid_gender(self):
        """Verify gender validation rejects unlisted values."""
        payload = {
            "age": 20,
            "gender": "InvalidGenderOption",
            "academic_pressure": 5,
            "study_satisfaction": 5,
            "dietary_habits": "Moderate",
            "financial_stress": 5,
            "family_history": "No",
            "work_hours": 4.0,
            "anxiety_level": 5,
            "stress_level": 5,
            "study_hours": 6.0,
            "sleep_hours": 8.0,
            "screen_time": 5.0,
            "text": "I feel extremely happy and proud of my work today. I feel calm and relaxed."
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Gender must be one of", response.get_json()["message"])

    def test_invalid_numeric_bounds(self):
        """Verify numeric parameter bounds (e.g. academic_pressure 1-10)."""
        payload = {
            "age": 20,
            "gender": "Male",
            "academic_pressure": 11,  # Out of bounds
            "study_satisfaction": 5,
            "dietary_habits": "Moderate",
            "financial_stress": 5,
            "family_history": "No",
            "work_hours": 4.0,
            "anxiety_level": 5,
            "stress_level": 5,
            "study_hours": 6.0,
            "sleep_hours": 8.0,
            "screen_time": 5.0,
            "text": "I feel extremely happy and proud of my work today. I feel calm and relaxed."
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Academic pressure must be between 1 and 10", response.get_json()["message"])

    def test_combined_workload_hours_exceeded(self):
        """Verify workload validation rejects study + sleep + screen + work > 24 hours."""
        payload = {
            "age": 20,
            "gender": "Male",
            "academic_pressure": 5,
            "study_satisfaction": 5,
            "dietary_habits": "Moderate",
            "financial_stress": 5,
            "family_history": "No",
            "work_hours": 5.0,
            "anxiety_level": 5,
            "stress_level": 5,
            "study_hours": 10.0,
            "sleep_hours": 6.0,
            "screen_time": 4.0,  # Sum = 25 hours > 24
            "text": "I feel extremely happy and proud of my work today. I feel calm and relaxed."
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Combined study hours, sleep hours, screen time, and work hours cannot exceed 24 hours", response.get_json()["message"])

    def test_gibberish_text_rejected(self):
        """Verify gibberish pre-processing detection blocks gibberish texts."""
        payload = {
            "age": 20,
            "gender": "Male",
            "academic_pressure": 5,
            "study_satisfaction": 5,
            "dietary_habits": "Moderate",
            "financial_stress": 5,
            "family_history": "No",
            "work_hours": 4.0,
            "anxiety_level": 5,
            "stress_level": 5,
            "study_hours": 6.0,
            "sleep_hours": 8.0,
            "screen_time": 5.0,
            # Ensure text meets min length (>=20) and word count (>=5), but is gibberish
            "text": "sjdkvndibjsndbi asdasdasd qwertyqwerty zxczxczxcvbnm mnbvcxzlkjhg"
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Please enter meaningful journal content", response.get_json()["message"])

    def test_text_too_short(self):
        """Verify text with < 20 characters is rejected."""
        payload = {
            "age": 20,
            "gender": "Male",
            "academic_pressure": 5,
            "study_satisfaction": 5,
            "dietary_habits": "Moderate",
            "financial_stress": 5,
            "family_history": "No",
            "work_hours": 4.0,
            "anxiety_level": 5,
            "stress_level": 5,
            "study_hours": 6.0,
            "sleep_hours": 8.0,
            "screen_time": 5.0,
            "text": "tea hello fun day" # < 20 chars
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("must be at least 20 characters and contain at least 5 words", response.get_json()["message"])

    def test_crisis_safety_override(self):
        """Verify Option B crisis text trigger overrides wellness to < 30."""
        payload = {
            "age": 20,
            "gender": "Male",
            "academic_pressure": 1,  # Low pressure/stress should lead to high wellness
            "study_satisfaction": 5,
            "dietary_habits": "Moderate",
            "financial_stress": 5,
            "family_history": "No",
            "work_hours": 4.0,
            "anxiety_level": 1,
            "stress_level": 1,
            "study_hours": 2.0,
            "sleep_hours": 8.0,
            "screen_time": 2.0,
            # Ensure text meets length/word criteria and has crisis triggers
            "text": "I feel extremely desperate and I want to commit suicide today."
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["metrics"]["crisis_triggered"])
        self.assertLess(data["metrics"]["wellness"], 30)
        self.assertEqual(data["metrics"]["risk"], "High")

    def test_invalid_study_satisfaction(self):
        """Verify study_satisfaction validation fails outside 1-10 bounds."""
        payload = {
            "age": 20,
            "gender": "Male",
            "academic_pressure": 5,
            "study_satisfaction": 11,  # Out of bounds
            "dietary_habits": "Moderate",
            "financial_stress": 5,
            "family_history": "No",
            "work_hours": 4.0,
            "anxiety_level": 5,
            "stress_level": 5,
            "study_hours": 6.0,
            "sleep_hours": 8.0,
            "screen_time": 5.0,
            "text": "I feel extremely happy and proud of my work today. I feel calm and relaxed."
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Study satisfaction must be between 1 and 10", response.get_json()["message"])

    def test_invalid_dietary_habits(self):
        """Verify dietary_habits validation fails with invalid choice."""
        payload = {
            "age": 20,
            "gender": "Male",
            "academic_pressure": 5,
            "study_satisfaction": 5,
            "dietary_habits": "JunkFood",  # Invalid
            "financial_stress": 5,
            "family_history": "No",
            "work_hours": 4.0,
            "anxiety_level": 5,
            "stress_level": 5,
            "study_hours": 6.0,
            "sleep_hours": 8.0,
            "screen_time": 5.0,
            "text": "I feel extremely happy and proud of my work today. I feel calm and relaxed."
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Dietary habits must be one of", response.get_json()["message"])

    def test_invalid_financial_stress(self):
        """Verify financial_stress validation fails outside 1-10 bounds."""
        payload = {
            "age": 20,
            "gender": "Male",
            "academic_pressure": 5,
            "study_satisfaction": 5,
            "dietary_habits": "Moderate",
            "financial_stress": -1,  # Out of bounds
            "family_history": "No",
            "work_hours": 4.0,
            "anxiety_level": 5,
            "stress_level": 5,
            "study_hours": 6.0,
            "sleep_hours": 8.0,
            "screen_time": 5.0,
            "text": "I feel extremely happy and proud of my work today. I feel calm and relaxed."
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Financial stress must be between 1 and 10", response.get_json()["message"])

    def test_invalid_family_history(self):
        """Verify family_history validation fails with invalid choice."""
        payload = {
            "age": 20,
            "gender": "Male",
            "academic_pressure": 5,
            "study_satisfaction": 5,
            "dietary_habits": "Moderate",
            "financial_stress": 5,
            "family_history": "Maybe",  # Invalid
            "work_hours": 4.0,
            "anxiety_level": 5,
            "stress_level": 5,
            "study_hours": 6.0,
            "sleep_hours": 8.0,
            "screen_time": 5.0,
            "text": "I feel extremely happy and proud of my work today. I feel calm and relaxed."
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Family history of mental illness must be one of", response.get_json()["message"])

    def test_invalid_work_hours(self):
        """Verify work_hours validation fails outside 0-16 bounds."""
        payload = {
            "age": 20,
            "gender": "Male",
            "academic_pressure": 5,
            "study_satisfaction": 5,
            "dietary_habits": "Moderate",
            "financial_stress": 5,
            "family_history": "No",
            "work_hours": 17.0,  # Out of bounds
            "anxiety_level": 5,
            "stress_level": 5,
            "study_hours": 6.0,
            "sleep_hours": 8.0,
            "screen_time": 5.0,
            "text": "I feel extremely happy and proud of my work today. I feel calm and relaxed."
        }
        response = self.client.post("/api/predict", json=payload, headers=self.headers)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Work hours must be between 0.0 and 16.0", response.get_json()["message"])

if __name__ == "__main__":
    unittest.main()
