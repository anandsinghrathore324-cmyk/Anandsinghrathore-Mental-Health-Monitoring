from flask import Blueprint, request, jsonify
from middleware.auth_middleware import token_required
from services.doctor_service import DoctorService

doctor_bp = Blueprint("doctor", __name__)

@doctor_bp.route("/nearby-doctors", methods=["POST"])
@token_required
def nearby_doctors(current_user):
    """Endpoint calculating spatial distance to psychologists using Haversine equations."""
    data = request.get_json() or {}
    
    try:
        user_lat = float(data.get("latitude", 28.6139)) # Default Delhi coordinates
        user_lon = float(data.get("longitude", 77.2090))
    except ValueError:
        return jsonify({
            "status": "error",
            "message": "Latitude and longitude must be valid floating point values."
        }), 400
        
    specialization = data.get("specialization", "all")
    
    try:
        specialists = DoctorService.get_nearby_specialists(user_lat, user_lon, specialization)
        return jsonify({
            "status": "success",
            "specialists": specialists
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Haversine calculation pipeline failed: {str(e)}"
        }), 500
