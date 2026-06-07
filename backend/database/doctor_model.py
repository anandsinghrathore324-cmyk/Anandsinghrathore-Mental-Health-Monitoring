from database.db import db_manager

class DoctorModel:
    """Manages psychologist and counselor geographic listings and database queries."""
    
    @staticmethod
    def get_all_doctors() -> list:
        """Retrieves a complete listing of verified clinical advisors in the database."""
        try:
            cursor = db_manager.db.doctor_recommendations.find()
            docs = []
            for doc in cursor:
                doc["_id"] = str(doc["_id"])
                docs.append(doc)
            return docs
        except Exception:
            return []

    @staticmethod
    def seed_doctors(doctors_list: list):
        """Seeds initial clinical locations database if empty."""
        try:
            if db_manager.db.doctor_recommendations.count_documents({}) == 0:
                db_manager.db.doctor_recommendations.insert_many(doctors_list)
        except Exception:
            pass
