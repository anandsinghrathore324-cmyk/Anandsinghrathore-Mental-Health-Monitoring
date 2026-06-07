import re
from database.db import db_manager

class GeoModel:
    """Manages country, state, and city database queries and search operations."""

    @staticmethod
    def get_all_countries() -> list:
        """Retrieves a list of all countries sorted by name."""
        try:
            cursor = db_manager.db.geo_countries.find(
                {}, 
                {"_id": 0, "id": 1, "name": 1, "iso2": 1, "emoji": 1}
            ).sort("name", 1)
            return list(cursor)
        except Exception:
            return []

    @staticmethod
    def get_states_by_country(country_code: str) -> list:
        """Retrieves all states/provinces for a given country code (ISO2)."""
        try:
            # Country code is stored uppercase in the database
            cc = country_code.upper()
            cursor = db_manager.db.geo_states.find(
                {"country_code": cc},
                {"_id": 0, "id": 1, "name": 1, "state_code": 1, "country_code": 1}
            ).sort("name", 1)
            return list(cursor)
        except Exception:
            return []

    @staticmethod
    def get_cities_by_state(country_code: str, state_code: str) -> list:
        """Retrieves all cities for a given country and state code."""
        try:
            cc = country_code.upper()
            sc = state_code.upper()
            cursor = db_manager.db.geo_cities.find(
                {"country_code": cc, "state_code": sc},
                {"_id": 0, "id": 1, "name": 1, "state_code": 1, "country_code": 1, "latitude": 1, "longitude": 1}
            ).sort("name", 1)
            return list(cursor)
        except Exception:
            return []

    @staticmethod
    def search_countries(query: str) -> list:
        """Searches countries by name using case-insensitive prefix match."""
        try:
            safe_query = re.escape(query)
            cursor = db_manager.db.geo_countries.find(
                {"name": {"$regex": f"^{safe_query}", "$options": "i"}},
                {"_id": 0, "id": 1, "name": 1, "iso2": 1, "emoji": 1}
            ).sort("name", 1).limit(50)
            return list(cursor)
        except Exception:
            return []

    @staticmethod
    def search_states(country_code: str, query: str) -> list:
        """Searches states within a country by name using case-insensitive prefix match."""
        try:
            cc = country_code.upper()
            safe_query = re.escape(query)
            cursor = db_manager.db.geo_states.find(
                {
                    "country_code": cc,
                    "name": {"$regex": f"^{safe_query}", "$options": "i"}
                },
                {"_id": 0, "id": 1, "name": 1, "state_code": 1, "country_code": 1}
            ).sort("name", 1).limit(50)
            return list(cursor)
        except Exception:
            return []

    @staticmethod
    def search_cities(country_code: str, state_code: str, query: str) -> list:
        """Searches cities within a state and country by name using case-insensitive prefix match."""
        try:
            cc = country_code.upper()
            sc = state_code.upper()
            safe_query = re.escape(query)
            cursor = db_manager.db.geo_cities.find(
                {
                    "country_code": cc,
                    "state_code": sc,
                    "name": {"$regex": f"^{safe_query}", "$options": "i"}
                },
                {"_id": 0, "id": 1, "name": 1, "state_code": 1, "country_code": 1, "latitude": 1, "longitude": 1}
            ).sort("name", 1).limit(50)
            return list(cursor)
        except Exception:
            return []

    @staticmethod
    def seed_check():
        """Checks if geo data collections are seeded, prints warning if not."""
        try:
            countries_cnt = db_manager.db.geo_countries.count_documents({})
            states_cnt = db_manager.db.geo_states.count_documents({})
            cities_cnt = db_manager.db.geo_cities.count_documents({})
            if countries_cnt == 0 or states_cnt == 0 or cities_cnt == 0:
                print("Warning: Geolocation collections (geo_countries, geo_states, geo_cities) are empty!")
                print("Please run python backend/database/import_geo_data.py to seed geolocation data.")
        except Exception as e:
            print(f"Error checking geo data seeding status: {e}")
