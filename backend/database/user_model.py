import datetime
import bcrypt
from bson import ObjectId
from database.db import db_manager

class UserModel:
    """Manages user registration, secure hashing, and database lookups."""
    
    @staticmethod
    def create_user(name: str, email: str, password: str) -> dict:
        """Hashes the password and inserts a new user record into the database."""
        # Secure salt-hashed password keys
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))
        hashed_password = hashed_bytes.decode('utf-8')
        
        user_doc = {
            "name": name.strip(),
            "email": email.strip().lower(),
            "password": hashed_password,
            "created_at": datetime.datetime.utcnow()
        }
        
        result = db_manager.db.users.insert_one(user_doc)
        user_doc["_id"] = str(result.inserted_id)
        # Clear password for returns
        user_doc.pop("password", None)
        return user_doc

    @staticmethod
    def find_by_email(email: str) -> dict:
        """Finds a user document by their email address."""
        user = db_manager.db.users.find_one({"email": email.strip().lower()})
        if user:
            user["_id"] = str(user["_id"])
        return user

    @staticmethod
    def find_by_id(user_id: str) -> dict:
        """Finds a user document by their MongoDB ObjectId string."""
        try:
            user = db_manager.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user["_id"] = str(user["_id"])
                user.pop("password", None) # Remove password for security
            return user
        except Exception:
            return None

    @staticmethod
    def verify_password(stored_password: str, provided_password: str) -> bool:
        """Verifies if the provided password matches the secure hashed password."""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

    @staticmethod
    def update_password(email: str, new_password: str) -> bool:
        """Hashes the new password and updates the user's document inside MongoDB."""
        hashed_bytes = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt(12))
        hashed_password = hashed_bytes.decode('utf-8')
        
        result = db_manager.db.users.update_one(
            {"email": email.strip().lower()},
            {"$set": {"password": hashed_password}}
        )
        return result.modified_count > 0
