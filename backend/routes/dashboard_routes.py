from flask import Blueprint, jsonify
from middleware.auth_middleware import token_required
from services.dashboard_service import DashboardService

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard-data", methods=["GET"])
@token_required
def dashboard_data(current_user):
    """Endpoint fetching, sorting, and aggregating recent diagnostic metrics for Chart.js and Mood Heatmaps."""
    try:
        metrics = DashboardService.compile_dashboard_metrics(current_user["_id"])
        return jsonify({
            "status": "success",
            "metrics": metrics
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Dashboard aggregate logic failed: {str(e)}"
        }), 500
