import datetime
from bson import ObjectId
from database.db import db_manager

class ReportModel:
    """Manages mental health assessments storage and retrieval operations."""
    
    @staticmethod
    def create_report(user_id: str, stress: int, anxiety: int, depression: int, 
                      burnout: int, wellness: int, emotion: str, risk: str,
                      sleep_hours: float = None, emotion_scores: dict = None,
                      explainability: dict = None, study_satisfaction: int = None,
                      dietary_habits: str = None, financial_stress: int = None,
                      family_history: str = None, work_hours: float = None,
                      behavioral_probability: float = None, text_probability: float = None,
                      combined_probability: float = None) -> dict:
        """Inserts a new diagnostic mental health report for a student user."""
        report_doc = {
            "user_id": ObjectId(user_id) if user_id else None,
            "stress_score": int(stress),
            "anxiety_score": int(anxiety),
            "depression_score": int(depression),
            "burnout_score": int(burnout),
            "wellness_score": int(wellness),
            "emotion": emotion.strip(),
            "risk_level": risk.strip(),
            "created_at": datetime.datetime.utcnow()
        }
        if behavioral_probability is not None:
            report_doc["behavioral_probability"] = float(behavioral_probability)
        if text_probability is not None:
            report_doc["text_probability"] = float(text_probability)
        if combined_probability is not None:
            report_doc["combined_probability"] = float(combined_probability)
            
        if sleep_hours is not None:
            report_doc["sleep_hours"] = float(sleep_hours)
        if emotion_scores is not None:
            report_doc["emotion_scores"] = emotion_scores
        if explainability is not None:
            report_doc["explainability"] = explainability
        if study_satisfaction is not None:
            report_doc["study_satisfaction"] = int(study_satisfaction)
        if dietary_habits is not None:
            report_doc["dietary_habits"] = dietary_habits.strip()
        if financial_stress is not None:
            report_doc["financial_stress"] = int(financial_stress)
        if family_history is not None:
            report_doc["family_history"] = family_history.strip()
        if work_hours is not None:
            report_doc["work_hours"] = float(work_hours)
            
        result = db_manager.db.mental_health_reports.insert_one(report_doc)
        report_doc["_id"] = str(result.inserted_id)
        if report_doc["user_id"]:
            report_doc["user_id"] = str(report_doc["user_id"])
        return report_doc

    @staticmethod
    def get_user_reports(user_id: str, limit: int = 200) -> list:
        """Retrieves a list of reports sorted chronologically descending for a user."""
        try:
            cursor = db_manager.db.mental_health_reports.find(
                {"user_id": ObjectId(user_id)}
            ).sort("created_at", -1).limit(limit)
            
            reports = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                doc["user_id"] = str(doc["user_id"])
                doc["created_at"] = doc["created_at"].isoformat()
                reports.append(doc)
            return reports
        except Exception:
            return []
