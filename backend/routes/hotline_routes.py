from flask import Blueprint, jsonify
from database.hotline_model import HotlineModel

hotline_bp = Blueprint("hotline", __name__)

@hotline_bp.route("/hotlines/<country_code>", methods=["GET"])
def get_hotline(country_code):
    """API endpoint returning crisis support contacts for the requested country code."""
    if not country_code:
        return jsonify({
            "status": "error",
            "message": "Country code parameter is required."
        }), 400
        
    hotline = HotlineModel.get_hotline_by_iso2(country_code)
    
    if hotline:
        # Exclude internal MongoDB _id if present
        hotline.pop("_id", None)
        return jsonify(hotline), 200
    else:
        return jsonify({
            "status": "error",
            "message": f"No verified mental health hotlines found for country code: {country_code}"
        }), 404
