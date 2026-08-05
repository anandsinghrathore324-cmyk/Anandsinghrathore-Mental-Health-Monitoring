import datetime
from database.user_model import UserModel
from database.report_model import ReportModel
from database.chatbot_model import ChatbotModel

class AssessmentService:
    """Consolidates assessment reports, user profile data, and conversation history."""

    @staticmethod
    def get_assessment_context(user_id: str) -> dict:
        """
        Gathers user profile, latest diagnostic scores, and chat logs for prompt building.

        Args:
            user_id: The student's MongoDB user ID.

        Returns:
            A dictionary containing profile, scores, recommendations, and history keys.
        """
        # 1. Fetch User Profile
        user = UserModel.find_by_id(user_id) or {}
        profile = {}
        if user:
            profile["name"] = user.get("name", "Student")
            profile["gender"] = user.get("gender")
            
            birth_year = user.get("birth_year")
            if birth_year:
                try:
                    profile["age"] = datetime.datetime.now(datetime.timezone.utc).year - int(birth_year)
                except ValueError:
                    pass

        # 2. Fetch Latest Diagnostic Report
        reports = ReportModel.get_user_reports(user_id, limit=1)
        latest_report = reports[0] if reports else None

        if latest_report:
            scores = {
                "stress": latest_report.get("stress_score", 0),
                "anxiety": latest_report.get("anxiety_score", 0),
                "depression": latest_report.get("depression_score", 0),
                "burnout": latest_report.get("burnout_score", 0),
                "wellness": latest_report.get("wellness_score", 100),
                "emotion": latest_report.get("emotion", "Calm"),
                "risk_level": latest_report.get("risk_level", "Low"),
                "prediction_reliability": latest_report.get("explainability", {}).get("prediction_reliability", "High")
            }
            # Reuse recommendations directly from report document if available
            recommendations = latest_report.get("recommendations", [])
        else:
            # Fallback default values if no reports exist yet
            scores = {
                "stress": 0,
                "anxiety": 0,
                "depression": 0,
                "burnout": 0,
                "wellness": 100,
                "emotion": "Calm",
                "risk_level": "Low",
                "prediction_reliability": "High"
            }
            recommendations = []

        # 3. Fetch Conversation History (last 5 sessions/10 turns)
        chats = ChatbotModel.get_chat_history(user_id, limit=5)
        history = []
        for chat in chats:
            if chat.get("message"):
                history.append({"role": "student", "message": chat["message"]})
            if chat.get("response"):
                history.append({"role": "aira", "message": chat["response"]})

        return {
            "student_profile": profile if profile else None,
            "scores": scores,
            "recommendations": recommendations,
            "history": history if history else None
        }
