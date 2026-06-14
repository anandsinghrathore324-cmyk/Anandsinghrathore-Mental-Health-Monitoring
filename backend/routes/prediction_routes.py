from flask import Blueprint, request, jsonify
from database.report_model import ReportModel
from database.mood_model import MoodModel
from middleware.auth_middleware import token_required
from middleware.validation import validate_prediction_input
from services.prediction_service import prediction_service

prediction_bp = Blueprint("prediction", __name__)

@prediction_bp.route("/predict", methods=["POST"])
@token_required
@validate_prediction_input
def predict(current_user):
    """Endpoint that runs the hybrid ML/rule-based diagnostic assessment and records the result."""
    data = request.get_json() or {}
    
    try:
        # Run prediction diagnostic service
        metrics = prediction_service.run_assessment(data)
        
        # Explainability data
        explainability = {
            "top_positive_factors": metrics.get("top_positive_factors", []),
            "top_negative_factors": metrics.get("top_negative_factors", []),
            "prediction_reliability": metrics.get("prediction_reliability", "High"),
            "crisis_triggered": metrics.get("crisis_triggered", False)
        }
        
        # Save to mental_health_reports database
        report = ReportModel.create_report(
            user_id=current_user["_id"],
            stress=metrics["stress"],
            anxiety=metrics["anxiety"],
            depression=metrics["depression"],
            burnout=metrics["burnout"],
            wellness=metrics["wellness"],
            emotion=metrics["emotion"],
            risk=metrics["risk"],
            sleep_hours=float(data.get("sleep_hours", 7.0)),
            emotion_scores=metrics.get("emotion_scores"),
            explainability=explainability,
            study_satisfaction=int(data.get("study_satisfaction", 5)) if data.get("study_satisfaction") is not None else None,
            dietary_habits=data.get("dietary_habits"),
            financial_stress=int(data.get("financial_stress", 5)) if data.get("financial_stress") is not None else None,
            family_history=data.get("family_history"),
            work_hours=float(data.get("work_hours", 0.0)) if data.get("work_hours") is not None else None,
            behavioral_probability=metrics["behavioral_probability"],
            text_probability=metrics["text_probability"],
            combined_probability=metrics["combined_probability"]
        )
        
        # Log mood heatmap entry for today
        mood = data.get("mood", metrics["emotion"]).strip().lower()
        journal_text = data.get("text", "").strip() or "Submitted today's diagnostic assessment."
        MoodModel.log_mood(
            user_id=current_user["_id"],
            mood=mood,
            wellness=metrics["wellness"],
            journal=journal_text,
            behavioral_probability=metrics["behavioral_probability"],
            text_probability=metrics["text_probability"],
            combined_probability=metrics["combined_probability"],
            risk_level=metrics["risk_level"]
        )
        
        from flask import g
        warnings = getattr(g, "warnings", [])
        return jsonify({
            "status": "success",
            "message": "Neural diagnostics successfully analyzed and logged.",
            "metrics": metrics,
            "warnings": warnings,
            "report_id": report["_id"]
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Diagnostics computational pipeline failed: {str(e)}"
        }), 500

@prediction_bp.route("/analyze-text", methods=["POST"])
@token_required
def analyze_text(current_user):
    """Endpoint specifically for on-demand DistilBERT sentiment extraction."""
    data = request.get_json() or {}
    text = data.get("text", "").strip()
    
    if not text:
        return jsonify({
            "status": "error",
            "message": "Missing text payload for sentiment analysis."
        }), 400
        
    try:
        from services.nlp_service import NlpService
        nlp_res = NlpService.analyze_diary_entry(text)
        return jsonify({
            "status": "success",
            "nlp": nlp_res
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"NLP pipeline error: {str(e)}"
        }), 500
