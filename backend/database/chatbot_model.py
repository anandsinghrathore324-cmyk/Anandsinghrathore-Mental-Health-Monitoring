import datetime
from bson import ObjectId
from database.db import db_manager

class ChatbotModel:
    """Manages secure chatbot dialog loops and storage patterns."""
    
    @staticmethod
    def save_chat(user_id: str, message: str, response: str) -> dict:
        """Saves a conversation session between a student user and Aira assistant."""
        chat_doc = {
            "user_id": ObjectId(user_id) if user_id else None,
            "message": message.strip(),
            "response": response.strip(),
            "timestamp": datetime.datetime.utcnow()
        }
        
        result = db_manager.db.chatbot_history.insert_one(chat_doc)
        chat_doc["_id"] = str(result.inserted_id)
        if chat_doc["user_id"]:
            chat_doc["user_id"] = str(chat_doc["user_id"])
        return chat_doc

    @staticmethod
    def get_chat_history(user_id: str, limit: int = 20) -> list:
        """Fetches the conversation dialog log history between Aira and a user."""
        try:
            cursor = db_manager.db.chatbot_history.find(
                {"user_id": ObjectId(user_id)}
            ).sort("timestamp", 1).limit(limit) # sorted chronologically ascending
            
            chats = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["user_id"] = str(doc["user_id"])
                doc["timestamp"] = doc["timestamp"].isoformat()
                chats.append(doc)
            return chats
        except Exception:
            return []
