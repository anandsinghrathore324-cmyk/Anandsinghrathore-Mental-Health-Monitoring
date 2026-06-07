import time
from flask import Blueprint, jsonify, request
from database.geo_model import GeoModel

geo_bp = Blueprint("geo", __name__)

class SimpleTTLCache:
    """A thread-safe-ish simple in-memory TTL cache."""
    def __init__(self):
        self.cache = {}

    def get(self, key):
        if key in self.cache:
            val, expiry = self.cache[key]
            if time.time() < expiry:
                return val
            else:
                del self.cache[key]
        return None

    def set(self, key, value, ttl_seconds):
        self.cache[key] = (value, time.time() + ttl_seconds)

# Cache instance
api_cache = SimpleTTLCache()

@geo_bp.route("/countries", methods=["GET"])
def get_countries():
    """Retrieve all countries (cached for 1 hour)."""
    cache_key = "all_countries"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    countries = GeoModel.get_all_countries()
    api_cache.set(cache_key, countries, 3600)  # 1 hour
    return jsonify(countries), 200

@geo_bp.route("/states/<country_code>", methods=["GET"])
def get_states(country_code):
    """Retrieve states/provinces for a country (cached for 30 minutes)."""
    if not country_code or len(country_code) != 2:
        return jsonify({
            "status": "error",
            "message": "Invalid country code. Must be a 2-character ISO code."
        }), 400

    cc = country_code.upper()
    cache_key = f"states_{cc}"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    states = GeoModel.get_states_by_country(cc)
    api_cache.set(cache_key, states, 1800)  # 30 minutes
    return jsonify(states), 200

@geo_bp.route("/cities/<country_code>/<state_code>", methods=["GET"])
def get_cities(country_code, state_code):
    """Retrieve cities for a country and state (cached for 30 minutes)."""
    if not country_code or len(country_code) != 2 or not state_code:
        return jsonify({
            "status": "error",
            "message": "Invalid country or state code parameters."
        }), 400

    cc = country_code.upper()
    sc = state_code.upper()
    cache_key = f"cities_{cc}_{sc}"
    cached = api_cache.get(cache_key)
    if cached is not None:
        return jsonify(cached), 200

    cities = GeoModel.get_cities_by_state(cc, sc)
    api_cache.set(cache_key, cities, 1800)  # 30 minutes
    return jsonify(cities), 200

@geo_bp.route("/countries/search", methods=["GET"])
def search_countries():
    """Search countries by name (no cache)."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([]), 200
    countries = GeoModel.search_countries(query)
    return jsonify(countries), 200

@geo_bp.route("/states/<country_code>/search", methods=["GET"])
def search_states(country_code):
    """Search states within a country (no cache)."""
    query = request.args.get("q", "").strip()
    if not country_code or len(country_code) != 2:
        return jsonify({
            "status": "error",
            "message": "Invalid country code."
        }), 400
    if not query:
        return jsonify([]), 200
    states = GeoModel.search_states(country_code, query)
    return jsonify(states), 200

@geo_bp.route("/cities/<country_code>/<state_code>/search", methods=["GET"])
def search_cities(country_code, state_code):
    """Search cities within a state and country (no cache)."""
    query = request.args.get("q", "").strip()
    if not country_code or len(country_code) != 2 or not state_code:
        return jsonify({
            "status": "error",
            "message": "Invalid country or state code parameters."
        }), 400
    if not query:
        return jsonify([]), 200
    cities = GeoModel.search_cities(country_code, state_code, query)
    return jsonify(cities), 200
