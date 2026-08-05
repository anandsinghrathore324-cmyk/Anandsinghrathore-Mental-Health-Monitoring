import math
from config import Config
from database.doctor_model import DoctorModel

# Google Places live lookup (primary) — falls back to seeded DB if unavailable
try:
    from services.google_places_service import GooglePlacesService
    _PLACES_AVAILABLE = True
except ImportError:
    _PLACES_AVAILABLE = False

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
    def get_nearby_specialists(cls, user_lat: float, user_lon: float, specialization_filter: str = None, min_rating: float = 0.0, sort_by: str = "distance", city_filter: str = None, max_distance_km: float = None) -> list:
        """Finds mental health specialists near the user.

        Priority:
          1. Google Places API  — real, live-rated doctors from Google (primary)
          2. MongoDB seeded DB  — curated fallback if Places API is unavailable/fails

        When a city_filter is provided, local doctors are always shown first.
        If fewer than 3 local results exist the list is padded with the nearest
        high-rated specialists from other cities.
        """
        # ── 1. Try Google Places API ─────────────────────────────────────────
        if _PLACES_AVAILABLE and GooglePlacesService.is_available():
            try:

                live_results = GooglePlacesService.fetch_nearby_specialists(
                    latitude=user_lat,
                    longitude=user_lon,
                    specialization=specialization_filter or "all",
                    city_name=city_filter,
                    radius_m=10000.0,
                    max_results=6,
                )
                if live_results:
                    # Apply min_rating filter
                    if min_rating:
                        live_results = [d for d in live_results if d["rating"] >= float(min_rating)]
                    # Sort
                    if sort_by in ["best_reviewed", "rating", "top_rated"]:
                        live_results.sort(key=lambda d: (-d["rating"], -d["reviews"], d["distance"]))
                    else:
                        live_results.sort(key=lambda d: (d["distance"], -d["rating"]))
                    return live_results[:6]
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Google Places lookup failed, using seeded fallback: {e}")

        # ── 2. Fallback: MongoDB seeded doctor database ──────────────────────
        doctors = DoctorModel.get_all_doctors()
        
        local_results = []
        other_results = []

        c_low = city_filter.strip().lower() if city_filter and city_filter.lower() not in ["all", "any", ""] else None

        for doc in doctors:
            # Specialization filter
            if specialization_filter and specialization_filter.lower() not in ["all", "any", ""]:
                doc_spec = doc.get("specialization_type", "").lower()
                doc_title = doc.get("specialization", "").lower()
                filt = specialization_filter.lower()
                if filt not in doc_spec and filt not in doc_title:
                    continue
            
            # Rating floor filter
            doc_rating = float(doc.get("rating", 4.8))
            if min_rating and doc_rating < float(min_rating):
                continue

            doc_lat = float(doc.get("latitude", 0.0))
            doc_lon = float(doc.get("longitude", 0.0))
            distance = cls.calculate_haversine(user_lat, user_lon, doc_lat, doc_lon)
            
            if max_distance_km and distance > float(max_distance_km):
                continue
            
            rev_count = int(doc.get("reviews", doc.get("reviews_count", 120)))

            card = {
                "doctor_name": doc.get("doctor_name", "Dr. Verified Specialist"),
                "title": doc.get("title", doc.get("specialization", "Counselor Psychologist")),
                "specialization": doc.get("specialization", "Counselor Psychologist"),
                "specialization_type": doc.get("specialization_type", "general"),
                "experience": int(doc.get("experience", 8)),
                "degrees": doc.get("degrees", "PsyD, Clinician"),
                "certifications": doc.get("certifications", "Licensed Advisor"),
                "achievements": doc.get("achievements", "Distinguished Specialist"),
                "bio": doc.get("bio", "Dedicated to assisting students overcome high stressors and academic challenges."),
                "hospital": doc.get("hospital", "Max Wellness Hub"),
                "city": doc.get("city", "India"),
                "rating": doc_rating,
                "reviews": rev_count,
                "reviews_count": rev_count,
                "reviews_summary": doc.get("reviews_summary", "Highly rated by students for empathetic, actionable sessions."),
                "verified": bool(doc.get("verified", True)),
                "distance": round(distance, 1),
                "latitude": doc_lat,
                "longitude": doc_lon,
                "open_status": doc.get("open_status", "Online Now"),
                "timing": doc.get("timing", "10:00 - 18:00"),
                "contact_number": doc.get("contact_number", "+91 11 2658 8600"),
                "maps_link": doc.get("maps_link", f"https://maps.google.com/?q={doc.get('hospital', 'Clinic').replace(' ', '+')}"),
                "source": "seeded_db",
            }

            # Separate into local vs other buckets
            if c_low:
                doc_city = doc.get("city", "").lower()
                doc_hosp = doc.get("hospital", "").lower()
                # Locality expansion: Sanganer, Mansarovar, Sitapura are Jaipur suburbs
                is_suburb_match = ("sanganer" in c_low or "mansarovar" in c_low or "sitapura" in c_low) and ("jaipur" in doc_city or "jaipur" in doc_hosp or "sanganer" in doc_city)
                is_local = c_low in doc_city or c_low in doc_hosp or is_suburb_match
                if is_local:
                    local_results.append(card)
                else:
                    other_results.append(card)
            else:
                # No city filter — treat all as "local"
                local_results.append(card)

        # Sort each bucket
        def _sort_key_reviewed(d):
            return (-d["rating"], -d["reviews"], d["distance"])

        def _sort_key_distance(d):
            return (d["distance"], -d["rating"])

        if sort_by in ["best_reviewed", "rating", "top_rated"]:
            local_results.sort(key=_sort_key_reviewed)
            other_results.sort(key=_sort_key_reviewed)
        else:
            local_results.sort(key=_sort_key_distance)
            other_results.sort(key=_sort_key_distance)

        # Always return local doctors first; pad ONLY with nearby doctors (within 100 km) if < 3 local results
        combined = local_results[:4]
        if len(combined) < 3:
            nearby_others = [d for d in other_results if d["distance"] <= 100.0]
            combined += nearby_others[: 4 - len(combined)]

        return combined

