"""
conftest.py - Shared pytest fixtures for the AIRA backend test suite.
"""
from __future__ import annotations
import os, sys, datetime
import jwt, mongomock, pytest
from unittest.mock import patch

_BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

_MOCK_USER_OID = "507f1f77bcf86cd799439011"


@pytest.fixture(scope="session", autouse=True)
def mock_db():
    """Patch pymongo and return in-memory mongomock for the whole session."""
    _client = mongomock.MongoClient()
    _db = _client["aira_wellness"]
    with patch("pymongo.MongoClient", return_value=_client):
        from database.db import db_manager
        db_manager.client = _client
        db_manager.db = _db
        yield _db


@pytest.fixture(autouse=True)
def clean_db(mock_db):
    """Wipe all collections before each test."""
    for name in mock_db.list_collection_names():
        if not name.startswith("system."):
            mock_db[name].delete_many({})
    yield


@pytest.fixture(scope="session")
def app(mock_db):
    """Create Flask test application."""
    with patch("app.seed_database", return_value=None), \
         patch("app.db_manager.connect", return_value=None):
        from app import create_app
        flask_app = create_app()
    flask_app.config.update(TESTING=True)
    return flask_app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_user_id():
    return _MOCK_USER_OID


@pytest.fixture
def auth_headers(mock_db):
    from bson import ObjectId
    from config import Config
    mock_db["users"].update_one(
        {"_id": ObjectId(_MOCK_USER_OID)},
        {"$set": {
            "_id": ObjectId(_MOCK_USER_OID),
            "name": "Test Student",
            "email": "test@aira.edu",
            "password": "$2b$12$KIXBUeJvBCqNxkLhCgKNyuopzBwTz0Bm/9AMXaOJgD8Z.1UKUGpIW",
            "profile_complete": True,
            "age": 21,
            "gender": "Male",
            "created_at": datetime.datetime.utcnow() - datetime.timedelta(days=10)
        }},
        upsert=True,
    )
    payload = {
        "sub": _MOCK_USER_OID,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2),
    }
    token = jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm="HS256")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
