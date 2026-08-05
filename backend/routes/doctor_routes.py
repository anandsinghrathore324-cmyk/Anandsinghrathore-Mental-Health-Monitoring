from flask import Blueprint, request, jsonify
from middleware.auth_middleware import token_required
from services.doctor_service import DoctorService

doctor_bp = Blueprint("doctor", __name__)

@doctor_bp.route("/nearby-doctors", methods=["POST"])
@token_required
def nearby_doctors(current_user):
    """Endpoint calculating spatial distance to psychologists using Haversine equations."""
    data = request.get_json() or {}
    
    city = data.get("city")
    lat_in = data.get("latitude")
    lon_in = data.get("longitude")

    try:
        user_lat = float(lat_in) if lat_in is not None else None
        user_lon = float(lon_in) if lon_in is not None else None
    except (ValueError, TypeError):
        user_lat, user_lon = None, None

    # Fallback to defaults only if neither lat/lon nor city is specified
    if user_lat is None and user_lon is None and not city:
        user_lat, user_lon = 26.9124, 75.7873
        
    specialization = data.get("specialization", "all")
    sort_by = data.get("sort_by", "distance")
    min_rating = float(data.get("min_rating", 0.0))
    
    try:
        specialists = DoctorService.get_nearby_specialists(
            user_lat=user_lat,
            user_lon=user_lon,
            specialization_filter=specialization,
            min_rating=min_rating,
            sort_by=sort_by,
            city_filter=city
        )
        return jsonify({
            "status": "success",
            "specialists": specialists
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Haversine calculation pipeline failed: {str(e)}"
        }), 500


@doctor_bp.route("/public/nearby-doctors", methods=["GET", "POST"])
def public_nearby_doctors():
    """Public endpoint for guest students to find nearby top-reviewed psychologists."""
    if request.method == "POST":
        data = request.get_json() or {}
        lat_in = data.get("latitude")
        lon_in = data.get("longitude")
        spec = data.get("specialization", "all")
        sort = data.get("sort_by", "best_reviewed")
        rating = float(data.get("min_rating", 0.0))
        city = data.get("city")
    else:
        lat_in = request.args.get("lat", request.args.get("latitude"))
        lon_in = request.args.get("lon", request.args.get("longitude"))
        spec = request.args.get("specialization", "all")
        sort = request.args.get("sort_by", "best_reviewed")
        rating = float(request.args.get("min_rating", 0.0))
        city = request.args.get("city")

    try:
        user_lat = float(lat_in) if lat_in is not None else None
        user_lon = float(lon_in) if lon_in is not None else None
    except (ValueError, TypeError):
        user_lat, user_lon = None, None

    if user_lat is None and user_lon is None and not city:
        user_lat, user_lon = 26.9124, 75.7873


    try:
        specialists = DoctorService.get_nearby_specialists(
            user_lat=user_lat,
            user_lon=user_lon,
            specialization_filter=spec,
            min_rating=rating,
            sort_by=sort,
            city_filter=city
        )
        return jsonify({
            "status": "success",
            "specialists": specialists
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Location referral lookup failed: {str(e)}"
        }), 500
