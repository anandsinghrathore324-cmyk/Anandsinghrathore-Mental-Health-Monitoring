from database.db import db_manager

class DoctorModel:
    """Manages psychologist and counselor geographic listings and database queries."""
    
    @staticmethod
    def get_all_doctors() -> list:
        """Retrieves a complete listing of verified clinical advisors in the database."""
        try:
            if db_manager.db is None:
                db_manager.connect()
            cursor = db_manager.db.doctor_recommendations.find()
            docs = [doc for doc in cursor]
            if not docs and hasattr(db_manager.db, "doctors"):
                cursor = db_manager.db.doctors.find()
                docs = [doc for doc in cursor]
            
            for doc in docs:
                doc["_id"] = str(doc["_id"])
            return docs
        except Exception:
            return []


    @staticmethod
    def get_doctors_by_city(city_name: str) -> list:
        """Retrieves doctors located within or servicing a specific city."""
        all_docs = DoctorModel.get_all_doctors()
        if not city_name or city_name.lower() in ["all", "any", ""]:
            return all_docs
        c_lower = city_name.strip().lower()
        return [
            d for d in all_docs
            if c_lower in d.get("city", "").lower() or c_lower in d.get("hospital", "").lower()
        ]

    @staticmethod
    def get_top_rated_doctors(min_rating: float = 4.7, limit: int = 10) -> list:
        """Returns top-reviewed verified specialists sorted by rating and review count."""
        all_docs = DoctorModel.get_all_doctors()
        filtered = [d for d in all_docs if float(d.get("rating", 0.0)) >= min_rating]
        return sorted(
            filtered,
            key=lambda d: (float(d.get("rating", 0.0)), int(d.get("reviews", d.get("reviews_count", 0)))),
            reverse=True
        )[:limit]

    @staticmethod
    def seed_doctors(doctors_list: list):
        """Seeds initial clinical locations database if empty."""
        try:
            if db_manager.db.doctor_recommendations.count_documents({}) == 0:
                db_manager.db.doctor_recommendations.insert_many(doctors_list)
        except Exception:
            pass
