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
            wellness_val = h.get("wellness", 85)
            
            # Legacy fallback for older logs lacking the new probability/risk fields
            behavioral_prob = h.get("behavioral_probability")
            text_prob = h.get("text_probability")
            combined_prob = h.get("combined_probability")
            risk_lvl = h.get("risk_level")
            
            if combined_prob is None:
                combined_prob = round((100.0 - wellness_val) / 100.0, 4)
            if behavioral_prob is None:
                behavioral_prob = round(combined_prob * 0.4, 4)
            if text_prob is None:
                text_prob = round(combined_prob * 0.6, 4)
                
            if not risk_lvl:
                if wellness_val >= 80:
                    risk_lvl = "Low"
                elif wellness_val >= 60:
                    risk_lvl = "Mild"
                elif wellness_val >= 40:
                    risk_lvl = "Moderate"
                elif wellness_val >= 20:
                    risk_lvl = "High"
                else:
                    risk_lvl = "Critical"
                    
            heatmap_data.append({
                "day": h.get("date", ""),
                "mood": h.get("mood", "joy"),
                "score": wellness_val,
                "journal": h.get("journal", "Logged assessment details."),
                "behavioral_probability": behavioral_prob,
                "text_probability": text_prob,
                "combined_probability": combined_prob,
                "risk_level": risk_lvl
            })
            
        # 3. Compile analytics summaries using consistent risk thresholds
        latest_report = ordered_reports[-1] if ordered_reports else None
        latest_stress = stress_path[-1] if stress_path else 40
        latest_anxiety = anxiety_path[-1] if anxiety_path else 38
        latest_depression = depression_path[-1] if depression_path else 35
        latest_wellness = wellness_path[-1] if wellness_path else 68
        
        latest_burnout = latest_report.get("burnout_score", latest_stress) if latest_report else latest_stress
        latest_academic = latest_report.get("academic_strain", latest_stress) if latest_report else latest_stress
        latest_sleep = latest_report.get("sleep_hours", 7.0) if latest_report else 7.0
        
        # Consistent risk threshold mapping helper (0-20 Low, 20-40 Mild, 40-60 Moderate, 60-80 High, 80-100 Critical)
        def map_score_to_risk(score):
            if score <= 20:
                return "Low"
            elif score <= 40:
                return "Mild"
            elif score <= 60:
                return "Moderate"
            elif score <= 80:
                return "High"
            else:
                return "Critical"
        
        # Sleep Quality classification using realistic categories
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
            "stability_index": int(latest_wellness),
            "sleep_quality": sleep_quality,
            "burnout_threat": map_score_to_risk(latest_burnout),
            "academic_strain": map_score_to_risk(latest_academic),
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
