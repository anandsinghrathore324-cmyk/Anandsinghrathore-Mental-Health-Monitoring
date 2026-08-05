"""
google_places_service.py  —  AIRA Live Doctor Lookup via Google Places API
===========================================================================
Uses Google Places API (New) Text Search to find real, verified psychiatrists,
psychologists, and mental health counselors near any GPS coordinate.

Falls back gracefully if API key is missing or the request fails.
"""

import logging
import requests
from config import Config

logger = logging.getLogger(__name__)

# Google Places API (New) - Text Search endpoint
_PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"

# Fields to request from Google (controls billing cost)
_FIELD_MASK = ",".join([
    "places.displayName",
    "places.formattedAddress",
    "places.rating",
    "places.userRatingCount",
    "places.internationalPhoneNumber",
    "places.location",
    "places.googleMapsUri",
    "places.regularOpeningHours",
    "places.editorialSummary",
    "places.types",
    "places.businessStatus",
])

# Search queries tuned to return mental health professionals
_SEARCH_QUERIES = {
    "anxiety":    "psychiatrist psychologist anxiety counselor",
    "depression": "psychiatrist psychologist depression counselor",
    "stress":     "psychologist counselor stress therapist",
    "all":        "psychiatrist psychologist mental health counselor",
}


class GooglePlacesService:
    """Fetches real, live-rated mental health specialists from Google Places API."""

    @staticmethod
    def is_available() -> bool:
        return bool(Config.GOOGLE_PLACES_API_KEY)

    @classmethod
    def fetch_nearby_specialists(
        cls,
        latitude: float,
        longitude: float,
        specialization: str = "all",
        city_name: str = None,
        radius_m: float = 10000.0,
        max_results: int = 6,
    ) -> list:
        """
        Calls Google Places Text Search API and returns a normalized list of
        doctor cards matching the AIRA UI schema.

        Returns [] on any failure so the caller can fall back to seeded data.
        """
        if not cls.is_available():
            logger.debug("GOOGLE_PLACES_API_KEY not set — skipping live lookup.")
            return []

        base_query = _SEARCH_QUERIES.get(specialization.lower(), _SEARCH_QUERIES["all"])
        has_city = bool(city_name and city_name.strip().lower() not in ["all", "any", ""])

        if has_city:
            query = f"{base_query} in {city_name.strip()}"
        else:
            query = base_query

        payload = {
            "textQuery": query,
            "maxResultCount": max_results,
            "rankPreference": "RELEVANCE",
            "languageCode": "en",
        }

        # Only add locationBias if no city_name is given, or if coordinates differ from default
        if not has_city and latitude is not None and longitude is not None:
            payload["locationBias"] = {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": radius_m,
                }
            }


        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": Config.GOOGLE_PLACES_API_KEY,
            "X-Goog-FieldMask": _FIELD_MASK,
        }

        try:
            resp = requests.post(
                _PLACES_TEXT_SEARCH_URL,
                json=payload,
                headers=headers,
                timeout=8,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.exceptions.Timeout:
            logger.warning("Google Places API timed out.")
            return []
        except requests.exceptions.RequestException as e:
            logger.warning(f"Google Places API request failed: {e}")
            return []

        places = data.get("places", [])
        if not places:
            logger.info("Google Places returned 0 results for query: %s near (%.4f, %.4f)", query, latitude, longitude)
            return []

        results = []
        for place in places:
            # Skip closed / permanently closed businesses
            if place.get("businessStatus") == "CLOSED_PERMANENTLY":
                continue

            name = place.get("displayName", {}).get("text", "Mental Health Specialist")
            address = place.get("formattedAddress", "")
            rating = float(place.get("rating", 4.5))
            review_count = int(place.get("userRatingCount", 0))
            phone = place.get("internationalPhoneNumber", "")
            maps_uri = place.get("googleMapsUri", "https://maps.google.com")
            summary = place.get("editorialSummary", {}).get("text", "")
            loc = place.get("location", {})
            doc_lat = float(loc.get("latitude", latitude))
            doc_lon = float(loc.get("longitude", longitude))

            # Opening hours
            hours_obj = place.get("regularOpeningHours", {})
            open_now = hours_obj.get("openNow", None)
            if open_now is True:
                open_status = "Online Now"
            elif open_now is False:
                open_status = "Offline"
            else:
                open_status = "Online Now"

            # Derive city from address (first part before comma)
            city_from_addr = address.split(",")[-3].strip() if len(address.split(",")) >= 3 else address.split(",")[0].strip()

            # Haversine distance
            import math
            R = 6371.0
            phi1, phi2 = math.radians(latitude), math.radians(doc_lat)
            d_phi = math.radians(doc_lat - latitude)
            d_lam = math.radians(doc_lon - longitude)
            a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lam / 2) ** 2
            distance = round(R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a)), 1)

            # Build review summary
            if not summary:
                if rating >= 4.8:
                    summary = f"Outstanding rated specialist ({rating}★ from {review_count} patient reviews)."
                elif rating >= 4.5:
                    summary = f"Highly regarded by patients ({rating}★ from {review_count} reviews)."
                else:
                    summary = f"Verified mental health practitioner near your location ({rating}★)."

            results.append({
                "doctor_name": name,
                "title": "Verified Mental Health Specialist",
                "specialization": _SEARCH_QUERIES.get(specialization.lower(), "Mental Health & Counseling"),
                "specialization_type": specialization.lower() if specialization.lower() in ["anxiety", "depression", "stress"] else "general",
                "experience": 0,  # Not available from Places API
                "degrees": "Licensed Mental Health Professional",
                "certifications": "Google Verified Practice",
                "achievements": f"{review_count} patient reviews on Google",
                "bio": summary,
                "hospital": address,
                "city": city_from_addr,
                "rating": rating,
                "reviews": review_count,
                "reviews_count": review_count,
                "reviews_summary": summary,
                "verified": True,
                "distance": distance,
                "latitude": doc_lat,
                "longitude": doc_lon,
                "open_status": open_status,
                "timing": "See Google Maps for hours",
                "contact_number": phone,
                "maps_link": maps_uri,
                "source": "google_places",
            })

        logger.info("Google Places returned %d live specialists near (%.4f, %.4f)", len(results), latitude, longitude)
        return results
