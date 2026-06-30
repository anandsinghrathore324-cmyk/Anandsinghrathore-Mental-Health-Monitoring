"""
test_pytest_routes.py - Flask route integration tests for AIRA backend.
"""
from __future__ import annotations
import os, sys, datetime
import pytest
from unittest.mock import patch, MagicMock
from bson import ObjectId

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)


# ─────────────────────────────────────────────────────────────────────────────
# Auth Routes
# ─────────────────────────────────────────────────────────────────────────────
class TestAuthRoutes:
    def test_signup_success(self, client, mock_db):
        resp = client.post("/api/signup", json={
            "name": "Alice Doe", "email": "alice@aira.edu", "password": "SecurePass123!"
        })
        assert resp.status_code == 201
        assert resp.get_json()["status"] == "success"

    def test_signup_missing_fields_returns_400(self, client):
        resp = client.post("/api/signup", json={"name": "Alice"})
        assert resp.status_code == 400

    def test_signup_duplicate_email_returns_400(self, client, mock_db):
        client.post("/api/signup", json={
            "name": "Alice", "email": "dup@test.com", "password": "Pass123!"
        })
        resp = client.post("/api/signup", json={
            "name": "Alice2", "email": "dup@test.com", "password": "Pass456!"
        })
        assert resp.status_code == 400

    def test_login_success(self, client, mock_db):
        client.post("/api/signup", json={
            "name": "Bob", "email": "bob@aira.edu", "password": "BobPass123!"
        })
        resp = client.post("/api/login", json={
            "email": "bob@aira.edu", "password": "BobPass123!"
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "token" in data and data["status"] == "success"

    def test_login_wrong_password_returns_401(self, client, mock_db):
        client.post("/api/signup", json={
            "name": "Charlie", "email": "charlie@aira.edu", "password": "CorrectPass!"
        })
        resp = client.post("/api/login", json={
            "email": "charlie@aira.edu", "password": "WrongPass!"
        })
        assert resp.status_code == 401

    def test_login_unknown_email_returns_401(self, client, mock_db):
        resp = client.post("/api/login", json={
            "email": "unknown@aira.edu", "password": "Whatever!"
        })
        assert resp.status_code == 401

    def test_login_missing_fields_returns_400(self, client):
        resp = client.post("/api/login", json={"email": "x@x.com"})
        assert resp.status_code == 400

    def test_profile_endpoint_requires_auth(self, client):
        assert client.get("/api/profile").status_code == 401

    def test_profile_with_valid_token(self, client, auth_headers, mock_db):
        assert client.get("/api/profile", headers=auth_headers).status_code == 200

    def test_logout_requires_auth(self, client):
        assert client.post("/api/logout").status_code == 401

    def test_logout_with_valid_token(self, client, auth_headers, mock_db):
        assert client.post("/api/logout", headers=auth_headers).status_code == 200

    def test_request_otp_missing_email_returns_400(self, client):
        assert client.post("/api/request-otp", json={}).status_code == 400

    def test_request_otp_valid_email_stores_otp(self, client, mock_db):
        with patch("services.email_service.EmailService.send_otp", return_value=(True, "")):
            resp = client.post("/api/request-otp", json={"email": "test@aira.edu"})
        assert resp.status_code == 200

    def test_verify_otp_missing_fields_returns_400(self, client):
        assert client.post("/api/verify-otp", json={"email": "test@aira.edu"}).status_code == 400

    def test_verify_otp_correct_otp_returns_200(self, client, mock_db):
        mock_db["otp_codes"].insert_one({
            "email": "correct@test.com",
            "otp": "654321",
            "created_at": datetime.datetime.utcnow()
        })
        resp = client.post("/api/verify-otp", json={
            "email": "correct@test.com", "otp": "654321"
        })
        assert resp.status_code == 200

    def test_verify_otp_wrong_code_returns_401(self, client, mock_db):
        mock_db["otp_codes"].insert_one({
            "email": "otp@test.com", "otp": "123456",
            "created_at": datetime.datetime.utcnow()
        })
        resp = client.post("/api/verify-otp", json={
            "email": "otp@test.com", "otp": "999999"
        })
        assert resp.status_code == 401

    def test_profile_status_requires_auth(self, client):
        assert client.get("/api/profile-status").status_code == 401

    def test_profile_status_with_valid_auth(self, client, auth_headers, mock_db):
        assert client.get("/api/profile-status", headers=auth_headers).status_code == 200

    def test_save_profile_requires_auth(self, client):
        assert client.post("/api/save-profile", json={}).status_code == 401

    def test_expired_jwt_returns_401(self, client, mock_db):
        import jwt
        from config import Config
        payload = {
            "sub": "507f1f77bcf86cd799439011",
            "exp": datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        }
        token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")
        assert client.get("/api/profile",
                          headers={"Authorization": f"Bearer {token}"}).status_code == 401

    def test_invalid_token_returns_401(self, client):
        assert client.get("/api/profile",
                          headers={"Authorization": "Bearer invalid.token.here"}).status_code == 401

    def test_reset_password_missing_fields_returns_400(self, client):
        assert client.post("/api/reset-password",
                           json={"email": "x@x.com"}).status_code == 400

    def test_signup_otp_verify_missing_fields(self, client):
        assert client.post("/api/signup-verify-otp",
                           json={"email": "x@x.com"}).status_code == 400

    def test_signup_otp_request_valid_email(self, client, mock_db):
        with patch("services.email_service.EmailService.send_otp", return_value=(True, "")):
            resp = client.post("/api/signup-request-otp", json={"name": "New User", "email": "new@test.com"})
            assert resp.status_code == 200

    # New Auth Routes Tests
    def test_reset_password_success(self, client, mock_db):
        mock_db["users"].insert_one({
            "name": "Jane", "email": "jane@aira.edu", "password": "oldpassword"
        })
        resp = client.post("/api/reset-password", json={
            "email": "jane@aira.edu", "password": "NewSecurePassword123!"
        })
        assert resp.status_code == 200

    def test_reset_password_user_not_found(self, client):
        resp = client.post("/api/reset-password", json={
            "email": "ghost@aira.edu", "password": "NewPassword!"
        })
        assert resp.status_code == 404

    def test_save_profile_success(self, client, auth_headers, mock_db):
        resp = client.post("/api/save-profile", json={
            "gender": "Female", "birth_year": 2000, "name": "Jane Doe"
        }, headers=auth_headers)
        assert resp.status_code == 200

    def test_save_profile_invalid_gender(self, client, auth_headers):
        resp = client.post("/api/save-profile", json={
            "gender": "Alien", "birth_year": 2000
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_save_profile_invalid_birth_year(self, client, auth_headers):
        resp = client.post("/api/save-profile", json={
            "gender": "Female", "birth_year": "invalid-year"
        }, headers=auth_headers)
        assert resp.status_code == 400

    def test_save_profile_out_of_bounds_age(self, client, auth_headers):
        resp = client.post("/api/save-profile", json={
            "gender": "Female", "birth_year": 1950  # age > 60
        }, headers=auth_headers)
        assert resp.status_code == 400

# ─────────────────────────────────────────────────────────────────────────────
# Prediction Routes and validation error middleware tests
# ─────────────────────────────────────────────────────────────────────────────
class TestPredictionRoutes:
    def _payload(self, **overrides):
        base = {
            "age": 21, "gender": "Male", "academic_pressure": 7,
            "study_satisfaction": 5, "sleep_hours": 6.0,
            "study_hours": 4.0, "screen_time": 3.0, "work_hours": 2.0,
            "dietary_habits": "Moderate", "financial_stress": 4,
            "family_history": "No",
            "text": "I feel very anxious about my upcoming exams",
            "anxiety_level": 6, "stress_level": 7,
        }
        base.update(overrides)
        return base

    def test_predict_requires_auth(self, client):
        assert client.post("/api/predict", json=self._payload()).status_code == 401

    def test_predict_valid_returns_200(self, client, auth_headers):
        resp = client.post("/api/predict", json=self._payload(), headers=auth_headers)
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "success"

    def test_predict_missing_age_profile_incomplete_returns_400(self, client, auth_headers, mock_db):
        # Remove age from payload and remove age/birth_year from user profile in db to hit line 22-26 in validation.py
        mock_db["users"].update_one(
            {"email": "test@aira.edu"},
            {"$unset": {"age": "", "birth_year": ""}}
        )
        payload = self._payload()
        del payload["age"]
        resp = client.post("/api/predict", json=payload, headers=auth_headers)
        assert resp.status_code == 400
        assert "Age not found" in resp.get_json()["message"]

    def test_predict_missing_age_but_profile_has_birth_year_success(self, client, auth_headers, mock_db):
        # Remove age from payload but set birth_year in db to hit line 19-20 in validation.py
        mock_db["users"].update_one(
            {"email": "test@aira.edu"},
            {"$set": {"birth_year": 2000, "gender": "Male"}}
        )
        payload = self._payload()
        del payload["age"]
        resp = client.post("/api/predict", json=payload, headers=auth_headers)
        assert resp.status_code == 200

    def test_predict_invalid_age_int_returns_400(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(age="not-an-int"),
                           headers=auth_headers).status_code == 400

    def test_predict_invalid_age_out_of_bounds(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(age=5),
                           headers=auth_headers).status_code == 400

    def test_predict_missing_gender_profile_incomplete_returns_400(self, client, auth_headers, mock_db):
        # Remove gender from payload and database to hit line 42-45 in validation.py
        mock_db["users"].update_one(
            {"email": "test@aira.edu"},
            {"$unset": {"gender": ""}}
        )
        payload = self._payload()
        del payload["gender"]
        resp = client.post("/api/predict", json=payload, headers=auth_headers)
        assert resp.status_code == 400
        assert "Gender not found" in resp.get_json()["message"]

    def test_predict_missing_gender_but_profile_has_gender_success(self, client, auth_headers, mock_db):
        mock_db["users"].update_one(
            {"email": "test@aira.edu"},
            {"$set": {"gender": "Female", "birth_year": 2000}}
        )
        payload = self._payload()
        del payload["gender"]
        resp = client.post("/api/predict", json=payload, headers=auth_headers)
        assert resp.status_code == 200

    def test_predict_invalid_gender_val(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(gender="Alien"),
                           headers=auth_headers).status_code == 400

    def test_predict_missing_academic_pressure(self, client, auth_headers):
        payload = self._payload()
        del payload["academic_pressure"]
        assert client.post("/api/predict", json=payload, headers=auth_headers).status_code == 400

    def test_predict_invalid_academic_pressure_val(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(academic_pressure=15),
                           headers=auth_headers).status_code == 400

    def test_predict_missing_study_satisfaction(self, client, auth_headers):
        payload = self._payload()
        del payload["study_satisfaction"]
        assert client.post("/api/predict", json=payload, headers=auth_headers).status_code == 400

    def test_predict_missing_dietary_habits(self, client, auth_headers):
        payload = self._payload()
        del payload["dietary_habits"]
        assert client.post("/api/predict", json=payload, headers=auth_headers).status_code == 400

    def test_predict_invalid_dietary_habits_val(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(dietary_habits="Trash"),
                           headers=auth_headers).status_code == 400

    def test_predict_missing_anxiety_level(self, client, auth_headers):
        payload = self._payload()
        del payload["anxiety_level"]
        assert client.post("/api/predict", json=payload, headers=auth_headers).status_code == 400

    def test_predict_missing_stress_level(self, client, auth_headers):
        payload = self._payload()
        del payload["stress_level"]
        assert client.post("/api/predict", json=payload, headers=auth_headers).status_code == 400

    def test_predict_missing_financial_stress(self, client, auth_headers):
        payload = self._payload()
        del payload["financial_stress"]
        assert client.post("/api/predict", json=payload, headers=auth_headers).status_code == 400

    def test_predict_missing_family_history(self, client, auth_headers):
        payload = self._payload()
        del payload["family_history"]
        assert client.post("/api/predict", json=payload, headers=auth_headers).status_code == 400

    def test_predict_invalid_family_history_val(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(family_history="Maybe"),
                           headers=auth_headers).status_code == 400

    def test_predict_missing_study_hours(self, client, auth_headers):
        payload = self._payload()
        del payload["study_hours"]
        assert client.post("/api/predict", json=payload, headers=auth_headers).status_code == 400

    def test_predict_missing_sleep_hours(self, client, auth_headers):
        payload = self._payload()
        del payload["sleep_hours"]
        assert client.post("/api/predict", json=payload, headers=auth_headers).status_code == 400

    def test_predict_missing_screen_time(self, client, auth_headers):
        payload = self._payload()
        del payload["screen_time"]
        assert client.post("/api/predict", json=payload, headers=auth_headers).status_code == 400

    def test_predict_missing_work_hours(self, client, auth_headers):
        payload = self._payload()
        del payload["work_hours"]
        assert client.post("/api/predict", json=payload, headers=auth_headers).status_code == 400

    def test_predict_work_hours_too_high_returns_400(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(work_hours=25.0),
                           headers=auth_headers).status_code == 400

    def test_predict_soft_warnings_combined_hours(self, client, auth_headers):
        # Combined sleep study work > 24
        resp = client.post("/api/predict", json=self._payload(sleep_hours=10.0, study_hours=10.0, work_hours=10.0), headers=auth_headers)
        assert resp.status_code == 200
        assert "warnings" in resp.get_json()

    def test_predict_soft_warnings_individual_high_values(self, client, auth_headers):
        # sleep study work screen high
        resp = client.post("/api/predict", json=self._payload(sleep_hours=17.0, study_hours=17.0, screen_time=19.0), headers=auth_headers)
        assert resp.status_code == 200
        assert len(resp.get_json()["warnings"]) > 0

    def test_predict_missing_journal_text(self, client, auth_headers):
        payload = self._payload()
        del payload["text"]
        assert client.post("/api/predict", json=payload, headers=auth_headers).status_code == 400

    def test_predict_short_journal_text(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(text="Too short."),
                           headers=auth_headers).status_code == 400

    def test_predict_short_words_journal_text(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(text="Short four words."),
                           headers=auth_headers).status_code == 400

    def test_predict_long_journal_text(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(text="stressed " * 110),
                           headers=auth_headers).status_code == 400

    def test_predict_only_numbers_journal_text(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(text="1234567890 1234567890 1234567890"),
                           headers=auth_headers).status_code == 400

    def test_predict_only_symbols_journal_text(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(text="!!! !!! !!! !!! !!! !!! !!! !!! !!!"),
                           headers=auth_headers).status_code == 400

    def test_predict_keyboard_spam_journal_text(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(text="I feel very stresseddddd today and cannot sleep."),
                           headers=auth_headers).status_code == 400

    def test_predict_repeated_tokens_journal_text(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(text="I am stressed stressed stressed stressed stressed today."),
                           headers=auth_headers).status_code == 400

    def test_predict_low_unique_word_ratio_journal_text(self, client, auth_headers):
        assert client.post("/api/predict", json=self._payload(text="stressed today stressed today stressed today stressed today stressed today"),
                           headers=auth_headers).status_code == 400

    def test_predict_gibberish_diary_returns_400(self, client, auth_headers):
        assert client.post("/api/predict",
                           json=self._payload(text="xkzq wvlm bfjp dtrs mnpq"),
                           headers=auth_headers).status_code == 400

    def test_predict_response_has_metrics(self, client, auth_headers):
        resp = client.post("/api/predict", json=self._payload(), headers=auth_headers)
        assert resp.status_code == 200
        assert "metrics" in resp.get_json()

    def test_analyze_text_requires_auth(self, client):
        assert client.post("/api/analyze-text",
                           json={"text": "I feel sad"}).status_code == 401

    def test_analyze_text_empty_returns_400(self, client, auth_headers):
        assert client.post("/api/analyze-text", json={"text": ""},
                           headers=auth_headers).status_code == 400

    def test_analyze_text_valid_returns_200(self, client, auth_headers):
        resp = client.post("/api/analyze-text",
                           json={"text": "I feel very anxious and stressed"},
                           headers=auth_headers)
        assert resp.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# Chatbot Routes
# ─────────────────────────────────────────────────────────────────────────────
class TestChatbotRoutes:
    def test_chatbot_requires_auth(self, client):
        assert client.post("/api/chatbot", json={"message": "Hello"}).status_code == 401

    def test_chatbot_empty_message_returns_400(self, client, auth_headers):
        assert client.post("/api/chatbot", json={"message": ""},
                           headers=auth_headers).status_code == 400

    def test_chatbot_valid_message_returns_200(self, client, auth_headers):
        with patch("chatbot.conversation_orchestrator.ConversationOrchestrator.orchestrate",
                   return_value="I hear you. How can I support you today?"):
            resp = client.post("/api/chatbot",
                               json={"message": "I feel stressed"},
                               headers=auth_headers)
        assert resp.status_code == 200

    def test_chat_history_requires_auth(self, client):
        assert client.get("/api/chat-history").status_code == 401

    def test_chat_history_returns_200(self, client, auth_headers, mock_db):
        assert client.get("/api/chat-history", headers=auth_headers).status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# Doctor Routes
# ─────────────────────────────────────────────────────────────────────────────
class TestDoctorRoutes:
    def test_nearby_doctors_requires_auth(self, client):
        assert client.post("/api/nearby-doctors",
                           json={"latitude": 28.6, "longitude": 77.2}).status_code == 401

    def test_nearby_doctors_returns_200_with_auth(self, client, auth_headers, mock_db):
        mock_db["doctors"].insert_one({
            "doctor_name": "Dr. Test", "latitude": 28.62, "longitude": 77.21,
            "specialization": "Psychologist", "specialization_type": "general",
            "experience": 8, "rating": 4.7, "hospital": "Test Hospital"
        })
        resp = client.post("/api/nearby-doctors",
                           json={"latitude": 28.6139, "longitude": 77.2090},
                           headers=auth_headers)
        assert resp.status_code == 200

    def test_nearby_doctors_invalid_lat_lon_returns_400(self, client, auth_headers):
        resp = client.post("/api/nearby-doctors",
                           json={"latitude": "abc", "longitude": "def"},
                           headers=auth_headers)
        assert resp.status_code == 400

    def test_nearby_doctors_response_has_specialists_key(self, client, auth_headers, mock_db):
        resp = client.post("/api/nearby-doctors",
                           json={"latitude": 28.6139, "longitude": 77.2090},
                           headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "specialists" in data


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard Routes
# ─────────────────────────────────────────────────────────────────────────────
class TestDashboardRoutes:
    def test_dashboard_requires_auth(self, client):
        assert client.get("/api/dashboard-data").status_code == 401

    def test_dashboard_returns_200(self, client, auth_headers, mock_db):
        assert client.get("/api/dashboard-data", headers=auth_headers).status_code == 200

    def test_dashboard_has_success_status(self, client, auth_headers, mock_db):
        data = client.get("/api/dashboard-data", headers=auth_headers).get_json()
        assert data.get("status") == "success"


# ─────────────────────────────────────────────────────────────────────────────
# Hotline Routes
# ─────────────────────────────────────────────────────────────────────────────
class TestHotlineRoutes:
    def test_hotline_valid_country_code(self, client, mock_db):
        mock_db["mental_health_hotlines"].insert_one({
            "iso2": "IN", "country": "India",
            "hotline_numbers": ["iCall: 9152987821"],
            "website": "https://icallhelpline.org"
        })
        assert client.get("/api/hotlines/IN").status_code == 200

    def test_hotline_unknown_country_returns_404(self, client, mock_db):
        assert client.get("/api/hotlines/XX").status_code == 404

    def test_hotline_us_country(self, client, mock_db):
        mock_db["mental_health_hotlines"].insert_one({
            "iso2": "US", "country": "United States", "hotline_numbers": ["988"],
        })
        assert client.get("/api/hotlines/US").status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# Geo Routes
# ─────────────────────────────────────────────────────────────────────────────
class TestGeoRoutes:
    def test_get_countries_returns_200(self, client, mock_db):
        mock_db["geo_countries"].insert_one({"iso2": "IN", "name": "India"})
        # Call twice to hit TTL cache
        client.get("/api/countries")
        assert client.get("/api/countries").status_code == 200

    def test_get_states_valid_country(self, client, mock_db):
        mock_db["geo_states"].insert_one({
            "country_code": "IN", "state_code": "MH", "name": "Maharashtra"
        })
        # Call twice to hit TTL cache
        client.get("/api/states/IN")
        assert client.get("/api/states/IN").status_code == 200

    def test_get_states_invalid_country_code(self, client):
        assert client.get("/api/states/INVALID").status_code == 400

    def test_get_cities_valid(self, client, mock_db):
        mock_db["geo_cities"].insert_one({
            "country_code": "IN", "state_code": "MH", "name": "Mumbai"
        })
        # Call twice to hit TTL cache
        client.get("/api/cities/IN/MH")
        assert client.get("/api/cities/IN/MH").status_code == 200

    def test_get_cities_invalid_country_code(self, client):
        assert client.get("/api/cities/X/MH").status_code == 400

    def test_search_countries_empty_query(self, client):
        resp = client.get("/api/countries/search?q=")
        assert resp.status_code == 200 and resp.get_json() == []

    def test_search_countries_non_empty_query(self, client, mock_db):
        mock_db["geo_countries"].insert_one({"iso2": "IN", "name": "India"})
        resp = client.get("/api/countries/search?q=Ind")
        assert resp.status_code == 200

    def test_search_states_empty_query(self, client):
        assert client.get("/api/states/IN/search?q=").status_code == 200

    def test_search_states_non_empty_query(self, client, mock_db):
        mock_db["geo_states"].insert_one({
            "country_code": "IN", "state_code": "MH", "name": "Maharashtra"
        })
        resp = client.get("/api/states/IN/search?q=Maha")
        assert resp.status_code == 200

    def test_search_cities_empty_query(self, client):
        assert client.get("/api/cities/IN/MH/search?q=").status_code == 200

    def test_search_cities_non_empty_query(self, client, mock_db):
        mock_db["geo_cities"].insert_one({
            "country_code": "IN", "state_code": "MH", "name": "Mumbai"
        })
        resp = client.get("/api/cities/IN/MH/search?q=Mum")
        assert resp.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# Auth Middleware
# ─────────────────────────────────────────────────────────────────────────────
class TestAuthMiddleware:
    def test_missing_header_returns_401(self, client):
        assert client.get("/api/profile").status_code == 401

    def test_malformed_bearer_returns_401(self, client):
        assert client.get("/api/profile",
                          headers={"Authorization": "NotBearer token123"}).status_code == 401

    def test_valid_token_passes(self, client, auth_headers, mock_db):
        assert client.get("/api/profile", headers=auth_headers).status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# Error Handlers
# ─────────────────────────────────────────────────────────────────────────────
class TestErrorHandlers:
    def test_nonexistent_endpoint_returns_404(self, client):
        resp = client.get("/api/nonexistent-endpoint-xyz")
        assert resp.status_code == 404
        assert resp.get_json()["status"] == "error"
