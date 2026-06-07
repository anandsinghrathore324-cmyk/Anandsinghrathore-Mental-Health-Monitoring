import datetime
from database.report_model import ReportModel
from database.mood_model import MoodModel

class DashboardService:
    """Aggregates student logs, daily mood indexes, and formats lists for Chart.js."""
    
    @staticmethod
    def compile_dashboard_metrics(user_id: str) -> dict:
        """Retrieves and compiles a complete suite of weekly stress timelines and calendar cells."""
        # 0. Fetch user to obtain registration date
        from database.user_model import UserModel
        user = UserModel.find_by_id(user_id)
        if user and "created_at" in user:
            created_at_val = user["created_at"]
            if isinstance(created_at_val, datetime.datetime):
                registration_date = created_at_val.date().isoformat()
            else:
                try:
                    registration_date = datetime.datetime.fromisoformat(created_at_val).date().isoformat()
                except Exception:
                    registration_date = str(created_at_val)[:10]
        else:
            registration_date = datetime.date.today().isoformat()

        # 1. Fetch recent diagnostic reports
        reports = ReportModel.get_user_reports(user_id, limit=200)
        
        # Sort chronologically ascending for timeline paths
        ordered_reports = list(reversed(reports))
        
        # Formulate chart lists
        stress_path = [r["stress_score"] for r in ordered_reports]
        anxiety_path = [r["anxiety_score"] for r in ordered_reports]
        depression_path = [r["depression_score"] for r in ordered_reports]
        wellness_path = [r["wellness_score"] for r in ordered_reports]
        
        timeline_labels = []
        for idx, r in enumerate(ordered_reports):
            # Parse created_at ISO string
            try:
                dt = datetime.datetime.fromisoformat(r["created_at"])
                timeline_labels.append(dt.strftime("%B %d, %I:%M %p"))
            except Exception:
                timeline_labels.append(f"Scan {idx+1}")
                
        timeline_dates = [r["created_at"] for r in ordered_reports]
        # Pad fallback defaults if empty
        if not reports:
            stress_path = []
            anxiety_path = []
            depression_path = []
            wellness_path = []
            timeline_labels = []
            timeline_dates = []

        # 2. Fetch mood history calendar logs
        heatmap_logs = MoodModel.get_mood_heatmap(user_id, days=365)
        
        heatmap_data = []
        for h in heatmap_logs:
            heatmap_data.append({
                "day": h.get("date", ""),
                "mood": h.get("mood", "joy"),
                "score": h.get("wellness", 85),
                "journal": h.get("journal", "Logged assessment details.")
            })
            
        # 3. Compile analytics summaries
        latest_stress = stress_path[-1] if stress_path else 40
        latest_anxiety = anxiety_path[-1] if anxiety_path else 38
        latest_depression = depression_path[-1] if depression_path else 35
        latest_wellness = wellness_path[-1] if wellness_path else 68
        
        # Sleep Quality classification using realistic categories (Issue 3)
        latest_report = ordered_reports[-1] if ordered_reports else None
        latest_sleep = latest_report.get("sleep_hours", 7.0) if latest_report else 7.0
        
        if latest_sleep <= 3:
            sleep_quality = "Critical Sleep Deprivation"
        elif latest_sleep <= 5:
            sleep_quality = "Poor Sleep"
        elif latest_sleep <= 9:
            sleep_quality = "Healthy Sleep"
        elif latest_sleep <= 12:
            sleep_quality = "Excessive Sleep"
        else:
            sleep_quality = "Very Excessive Sleep Pattern"
            
        # Primary emotion
        primary_emo = latest_report.get("emotion", "Calm") if latest_report else "Calm"
            
        summary = {
            "stability_index": int(latest_wellness * 0.9),
            "sleep_quality": sleep_quality,
            "burnout_threat": "High" if latest_stress > 65 else "Medium" if latest_stress > 40 else "Low",
            "academic_strain": "Severe" if latest_stress > 70 else "High" if latest_stress > 50 else "Low",
            "social_balance": "Balanced" if latest_wellness >= 60 else "Strained",
            "primary_emotion": primary_emo,
            "emotion_scores": latest_report.get("emotion_scores") if latest_report else None
        }
 
        return {
            "timeline": {
                "labels": timeline_labels,
                "dates": timeline_dates,
                "stress": stress_path,
                "anxiety": anxiety_path,
                "depression": depression_path,
                "wellness": wellness_path
            },
            "heatmap": heatmap_data,
            "summary": summary,
            "registration_date": registration_date,
            "today": datetime.date.today().isoformat()
        }
