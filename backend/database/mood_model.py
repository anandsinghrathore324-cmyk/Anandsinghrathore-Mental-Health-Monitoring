import datetime
from bson import ObjectId
from database.db import db_manager

class MoodModel:
    """Manages the daily mood log logs for heatmap tracking dashboards."""
    
    @staticmethod
    def log_mood(user_id: str, mood: str, wellness: int, date_str: str = None, journal: str = None) -> dict:
        """Saves or updates a daily mood log for rendering the temporal heatmap."""
        # Enforce date format YYYY-MM-DD or default today
        today_str = date_str or datetime.date.today().isoformat()
        
        query = {
            "user_id": ObjectId(user_id) if user_id else None,
            "date": today_str
        }
        
        update = {
            "$set": {
                "mood": mood.strip().lower(),
                "wellness": int(wellness),
                "updated_at": datetime.datetime.utcnow()
            }
        }
        if journal is not None:
            update["$set"]["journal"] = journal.strip()
            
        # Upsert allows seamless re-entries for the same day
        result = db_manager.db.mood_logs.update_one(query, update, upsert=True)
        
        logged_mood = {
            "user_id": user_id,
            "mood": mood.strip().lower(),
            "wellness": int(wellness),
            "date": today_str
        }
        if journal is not None:
            logged_mood["journal"] = journal.strip()
        return logged_mood

    @staticmethod
    def get_mood_heatmap(user_id: str, days: int = 365) -> list:
        """Retrieves user daily mood records sorted chronologically ascending."""
        try:
            cursor = db_manager.db.mood_logs.find(
                {"user_id": ObjectId(user_id)}
            ).sort("date", 1).limit(days)
            
            logs = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["user_id"] = str(doc["user_id"])
                logs.append(doc)
            return logs
        except Exception:
            return []
