import math
from config import Config
from database.doctor_model import DoctorModel

class DoctorService:
    """Invokes clinical referral checks and calculates proximity using Haversine equations."""
    
    @staticmethod
    def calculate_haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Returns distance in km between two GPS nodes using Haversine standard model."""
        R = Config.EARTH_RADIUS_KM
        
        # Radians conversion
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_phi / 2.0) ** 2 +
             math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2.0) ** 2))
             
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return R * c

    @classmethod
    def get_nearby_specialists(cls, user_lat: float, user_lon: float, specialization_filter: str = None) -> list:
        """Finds, calculates distance, and sorts psychologists in proximity order."""
        doctors = DoctorModel.get_all_doctors()
        
        results = []
        for doc in doctors:
            # Check filter
            if specialization_filter and specialization_filter.lower() != "all":
                if doc.get("specialization_type", "").lower() != specialization_filter.lower():
                    continue
            
            doc_lat = float(doc.get("latitude", 0.0))
            doc_lon = float(doc.get("longitude", 0.0))
            
            distance = cls.calculate_haversine(user_lat, user_lon, doc_lat, doc_lon)
            
            # Format return card matching client UI expectations
            results.append({
                "doctor_name": doc.get("doctor_name", "Dr. Verified Specialist"),
                "specialization": doc.get("specialization", "Counselor Psychologist"),
                "specialization_type": doc.get("specialization_type", "general"),
                "experience": int(doc.get("experience", 8)),
                "degrees": doc.get("degrees", "PsyD, Clinician"),
                "certifications": doc.get("certifications", "Licensed Advisor"),
                "achievements": doc.get("achievements", "Distinguished Specialist"),
                "bio": doc.get("bio", "Dedicated to assisting students overcome high stressors and academic challenges."),
                "hospital": doc.get("hospital", "Max Wellness Hub"),
                "rating": float(doc.get("rating", 4.8)),
                "distance": round(distance, 1),
                "open_status": doc.get("open_status", "Online Now"),
                "timing": doc.get("timing", "10:00 - 18:00"),
                "contact_number": doc.get("contact_number", "+91 11 2658 8600"),
                "maps_link": doc.get("maps_link", "https://maps.google.com")
            })
            
        # Sort in proximity order ascending
        return sorted(results, key=lambda d: d["distance"])
