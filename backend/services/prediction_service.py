import pickle
import numpy as np
import os
import logging
from ml.preprocess import MLPreprocessor
from services.nlp_service import NlpService

logger = logging.getLogger(__name__)

class PredictionService:
    """Predictive logic engine assessing student mental health threats using ML and rules."""
    
    def __init__(self):
        self.preprocessor = MLPreprocessor()
        # Disable Ridge regression model loading as per prediction refactor
        self.model = None
        logger.info("Ridge Regression model loading disabled.")

    def run_assessment(self, data: dict) -> dict:
        """Executes full diagnostic scanning combining workload variables and NLP sentiment logs."""
        import requests
        
        # 1. Capture variables
        age = float(data.get("age", 21.0))
        gender = data.get("gender", "Male")
        study_hours = float(data.get("study_hours", 6.0))
        sleep_hours = float(data.get("sleep_hours", 7.0))
        screen_time = float(data.get("screen_time", 5.0))
        academic_pressure = int(data.get("academic_pressure", 5))
        input_stress = int(data.get("stress_level", 5))
        input_anxiety = int(data.get("anxiety_level", 5))
        mood = data.get("mood", "calm").strip().lower()
        diary_text = data.get("text", "").strip()

        # Capture new variables
        study_satisfaction = int(data.get("study_satisfaction", 5))
        dietary_habits = data.get("dietary_habits", "Moderate")
        financial_stress = int(data.get("financial_stress", 5))
        family_history = data.get("family_history", "No")
        work_hours = float(data.get("work_hours", 0.0))

        # 2. Math Risk Equations
        sleep_deficit = self.preprocessor.calculate_sleep_deficit(sleep_hours)
        screen_excess = self.preprocessor.calculate_screen_excess(screen_time)

        # Always invoke local NLP sentiment as fallback/emotion metadata source
        nlp_res = NlpService.analyze_diary_entry(diary_text)
        emotion = nlp_res.get("emotion", "Neutral")
        sentiment = nlp_res.get("sentiment", "Neutral")
        emotion_scores = nlp_res.get("scores", {})

        # 2a. Stress score (Derived Indicator - normalized 0-100)
        base_stress = (input_stress * 5.0) + (academic_pressure * 3.0) + (sleep_deficit * 4.0) + (financial_stress * 3.0) + ((10 - study_satisfaction) * 2.0) + (work_hours * 1.5)
        if sentiment == "Negative":
            base_stress += 8
        if "exam" in diary_text.lower() or "deadline" in diary_text.lower():
            base_stress += 6
        # Max base_stress without text modifiers: 50 + 30 + 32 + 30 + 18 + 36 = 186
        # Max possible base_stress with modifiers: 186 + 14 = 200
        final_stress = int(np.clip((base_stress / 200.0) * 100, 0, 100))

        # 2b. Anxiety score (Derived Indicator - normalized 0-100)
        base_anxiety = (input_anxiety * 6.0) + (academic_pressure * 2.0) + (sleep_deficit * 3.0) + (financial_stress * 3.0)
        if family_history == "Yes":
            base_anxiety += 10
        if "panic" in diary_text.lower() or "scared" in diary_text.lower():
            base_anxiety += 12
        # Max base_anxiety with modifiers: 60 + 20 + 24 + 30 + 10 + 12 = 156
        final_anxiety = int(np.clip((base_anxiety / 156.0) * 100, 0, 100))

        # 2c. Burnout score (Derived Indicator - normalized 0-100)
        base_burnout = (final_stress * 0.4) + (screen_excess * 3.0) + (sleep_deficit * 4.0) + ((10 - study_satisfaction) * 2.0) + (work_hours * 2.0)
        # Max base_burnout: 40 + 54 + 32 + 18 + 48 = 192
        final_burnout = int(np.clip((base_burnout / 192.0) * 100, 0, 100))

        # 2d. Academic Strain (Derived Indicator - normalized 0-100)
        base_strain = (academic_pressure * 6.0) + (study_hours * 2.0) + (work_hours * 1.5) + ((10 - study_satisfaction) * 2.0)
        # Max base_strain: 60 + 48 + 36 + 18 = 162
        final_academic_strain = int(np.clip((base_strain / 162.0) * 100, 0, 100))

        # Explainability lists
        top_positive_factors = []
        top_negative_factors = []
        prediction_reliability = "High"
        
        # Determine top positive & negative factors based on rules since model is disabled
        if sleep_hours < 6.0:
            top_positive_factors.append("Low sleep duration (high fatigue)")
        else:
            top_negative_factors.append("Adequate sleep hygiene")
        if academic_pressure >= 7:
            top_positive_factors.append("Elevated academic pressure")
        else:
            top_negative_factors.append("Manageable academic pressure")
        if financial_stress >= 7:
            top_positive_factors.append("High financial stress")
        if study_satisfaction <= 4:
            top_positive_factors.append("Low study satisfaction")
        else:
            top_negative_factors.append("Satisfying academic path")

        # 3. Call External API Model microservices
        behavioral_probability = None
        text_probability = None

        # A. Call Behavioral Model API (Port 5001)
        try:
            # Map Sleep Hours (numeric) to Sleep Duration (categorical string)
            if sleep_hours < 5.0:
                sleep_duration_str = "Less than 5 hours"
            elif sleep_hours <= 6.0:
                sleep_duration_str = "5-6 hours"
            elif sleep_hours <= 8.0:
                sleep_duration_str = "7-8 hours"
            else:
                sleep_duration_str = "More than 8 hours"

            # Map Gender to model expectations
            gender_mapped = "Male"
            if isinstance(gender, str):
                g_lower = gender.lower()
                if "female" in g_lower:
                    gender_mapped = "Female"
                elif "male" in g_lower:
                    gender_mapped = "Male"

            # Map Dietary Habits
            dietary_mapped = "Moderate"
            if isinstance(dietary_habits, str):
                d_lower = dietary_habits.lower()
                if "healthy" in d_lower:
                    dietary_mapped = "Healthy"
                elif "unhealthy" in d_lower:
                    dietary_mapped = "Unhealthy"

            # Scale Academic Pressure (1-10 to 0.0-5.0), Study Satisfaction (1-10 to 0.0-5.0), and Financial Stress (1-10 to 1.0-5.0)
            academic_pressure_scaled = float(academic_pressure) / 2.0
            study_satisfaction_scaled = float(study_satisfaction) / 2.0
            financial_stress_scaled = float(financial_stress) / 2.0

            # Map Family History
            family_history_mapped = "No"
            if isinstance(family_history, str):
                fh_lower = family_history.lower()
                if fh_lower in ["yes", "no"]:
                    family_history_mapped = fh_lower.capitalize()

            # Work/Study Hours (Sum of work hours and study hours)
            work_study_hours = float(work_hours) + float(study_hours)

            behavioral_payload = {
                "Age": float(age),
                "Gender": gender_mapped,
                "Academic Pressure": academic_pressure_scaled,
                "Study Satisfaction": study_satisfaction_scaled,
                "Sleep Duration": sleep_duration_str,
                "Dietary Habits": dietary_mapped,
                "Work/Study Hours": work_study_hours,
                "Financial Stress": financial_stress_scaled,
                "Family History of Mental Illness": family_history_mapped
            }

            logger.info("Calling Behavioral Model API at http://127.0.0.1:5001/predict ...")
            response = requests.post("http://127.0.0.1:5001/predict", json=behavioral_payload, timeout=2.0)
            if response.status_code == 200:
                res_data = response.json()
                if isinstance(res_data, list) and len(res_data) > 0:
                    res_data = res_data[0]
                behavioral_probability = float(res_data.get("probability", 0.5))
                logger.info(f"Behavioral API prediction received. Probability: {behavioral_probability}")
            else:
                logger.warning(f"Behavioral API returned status code {response.status_code}. Activating local fallback.")
        except Exception as e:
            logger.warning(f"Failed to connect to Behavioral API: {str(e)}. Activating local fallback.")

        if behavioral_probability is None:
            # Deterministic behavioral fallback formula: maps demographics and stress directly
            fallback_score = (academic_pressure * 6.0) + (financial_stress * 4.0) + ((10 - study_satisfaction) * 3.0) + (sleep_deficit * 5.0) + (work_hours * 1.5)
            if family_history == "Yes":
                fallback_score += 10
            # Max is 60 + 40 + 27 + 40 + 36 + 10 = 213
            behavioral_probability = np.clip(fallback_score / 213.0, 0.0, 1.0)
            prediction_reliability = "Medium"

        # B. Call Text Model API (Port 5002)
        try:
            logger.info("Calling Text Model API at http://127.0.0.1:5002/text-predict ...")
            response = requests.post("http://127.0.0.1:5002/text-predict", json={"text": diary_text}, timeout=2.0)
            if response.status_code == 200:
                res_data = response.json()
                text_probability = float(res_data.get("probability", 0.5))
                logger.info(f"Text API prediction received. Probability: {text_probability}")
            else:
                logger.warning(f"Text API returned status code {response.status_code}. Activating local fallback.")
        except Exception as e:
            logger.warning(f"Failed to connect to Text API: {str(e)}. Activating local fallback.")

        if text_probability is None:
            # Fallback based on local NLP sentiment (1.0 - Joy probability)
            text_probability = 1.0 - emotion_scores.get("Joy", 0.5)
            prediction_reliability = "Medium"

        # 4. Compute Combined Mental Health Score
        combined_probability = (0.4 * behavioral_probability) + (0.6 * text_probability)
        final_wellness = int(np.clip((1.0 - combined_probability) * 100, 0, 100))

        # Dynamic override for clinical safety
        crisis_words = ["suicide", "kill myself", "self-harm", "end my life", "want to die", "harm myself", "cutting", "harming myself"]
        is_crisis = any(cw in diary_text.lower() for cw in crisis_words)
        if is_crisis:
            final_wellness = min(final_wellness, 15)
            combined_probability = max(combined_probability, 0.85)
            logger.warning("Clinical crisis indicators detected. Wellness Index overridden.")

        if emotion == "Insufficient Information":
            prediction_reliability = "Medium"

        # Categorize risk level based on combined probability (wellness-aligned risk thresholds)
        # Low: wellness >= 80 (combined_probability <= 0.2)
        # Mild: 60 <= wellness < 80 (0.2 < combined_probability <= 0.4)
        # Moderate: 40 <= wellness < 60 (0.4 < combined_probability <= 0.6)
        # High: 20 <= wellness < 40 (0.6 < combined_probability <= 0.8)
        # Critical: wellness < 20 (combined_probability > 0.8)
        if final_wellness >= 80:
            risk_level = "Low"
        elif final_wellness >= 60:
            risk_level = "Mild"
        elif final_wellness >= 40:
            risk_level = "Moderate"
        elif final_wellness >= 20:
            risk_level = "High"
        else:
            risk_level = "Critical"

        # Update depression value using the behavioral model's probability
        final_depression = min(98, max(4, int(behavioral_probability * 100)))

        recommendations = []
        
        # 1. Risk-based recommendations
        if risk_level == "Low":
            recommendations.append({
                "title": "Maintain Current Wellness Routines",
                "description": "Your wellness score is high! Keep up your healthy sleep, study, and life balance to maintain this positive trend.",
                "icon": "fa-heart",
                "color": "var(--neon-emerald)",
                "category": "Risk-based"
            })
        elif risk_level == "Mild":
            recommendations.append({
                "title": "Build Resilience & Support Networks",
                "description": "You are experiencing mild mental strain. Consider sharing your workload with friends or peers and practicing daily relaxation techniques.",
                "icon": "fa-users",
                "color": "var(--neon-cyan)",
                "category": "Risk-based"
            })
        elif risk_level == "Moderate":
            recommendations.append({
                "title": "Proactive Stress Management",
                "description": "Your stress and workload saturation levels are registering moderate anxiety indicators. Set boundaries and allocate dedicated time for self-care.",
                "icon": "fa-shield-heart",
                "color": "var(--neon-orange)",
                "category": "Risk-based"
            })
        elif risk_level == "High":
            recommendations.append({
                "title": "Structured Cognitive De-escalation",
                "description": "High saturation levels identified. System detects critical anxiety/depression warnings. AI recommends immediate workload reduction and counselor consultation.",
                "icon": "fa-triangle-exclamation",
                "color": "var(--neon-rose)",
                "category": "Risk-based"
            })
        elif risk_level == "Critical":
            recommendations.append({
                "title": "Urgent Support Recommendation",
                "description": "Your wellness indicators are at a critical level. We strongly recommend talking to a counselor or calling a crisis line immediately.",
                "icon": "fa-circle-exclamation",
                "color": "var(--neon-rose)",
                "category": "Risk-based"
            })

        # 2. Factor-based recommendations
        # Poor sleep -> sleep improvement advice
        if sleep_hours < 7.0:
            recommendations.append({
                "title": "Optimize Sleep Hygiene",
                "description": f"You are averaging {sleep_hours:.1f} hours of sleep. Aim for 7-9 hours of consistent sleep and limit screen use 30 minutes before bedtime.",
                "icon": "fa-bed",
                "color": "var(--neon-cyan)",
                "category": "Sleep Improvement"
            })

        # High academic pressure -> study management advice
        if academic_pressure >= 7:
            recommendations.append({
                "title": "Structure Your Study Strategy",
                "description": f"Academic pressure is high ({academic_pressure}/10). Break large tasks into smaller steps, prioritize, and take 5-minute study breaks.",
                "icon": "fa-graduation-cap",
                "color": "var(--neon-purple)",
                "category": "Study Management"
            })

        # High financial stress -> financial support advice
        if financial_stress >= 7:
            recommendations.append({
                "title": "Financial Support & Resources",
                "description": f"Financial stress is elevated ({financial_stress}/10). Connect with student financial services or explore budgeting applications.",
                "icon": "fa-wallet",
                "color": "var(--neon-orange)",
                "category": "Financial Support"
            })

        # High anxiety -> breathing and mindfulness advice
        if input_anxiety >= 7 or final_anxiety >= 70 or text_probability > 0.6:
            recommendations.append({
                "title": "Practice Mindfulness & Breathing",
                "description": "High anxiety or emotional strain detected. Utilize our Guided Breathing center for Box Breathing or the 4-7-8 method.",
                "icon": "fa-wind",
                "color": "var(--neon-cyan)",
                "category": "Breathing & Mindfulness"
            })

        # Low study satisfaction -> academic counseling advice
        if study_satisfaction <= 4:
            recommendations.append({
                "title": "Academic Counseling & Guidance",
                "description": f"Your study satisfaction is low ({study_satisfaction}/10). Schedule an advisory session to review your curriculum and course objectives.",
                "icon": "fa-chalkboard-user",
                "color": "var(--neon-purple)",
                "category": "Academic Counseling"
            })

        # 3. Fill up to reach 5-10 recommendations if we have fewer than 5
        general_pool = [
            {
                "title": "Incorporate Daily Physical Activity",
                "description": "A simple 15-minute walk can release endorphins, lower stress hormones, and improve cognitive performance.",
                "icon": "fa-person-running",
                "color": "var(--neon-emerald)",
                "category": "General Wellness"
            },
            {
                "title": "Nourish and Hydrate Your Body",
                "description": "Eating regular, balanced meals and staying hydrated stabilizes blood sugar and energy levels throughout the day.",
                "icon": "fa-apple-whole",
                "color": "var(--neon-cyan)",
                "category": "Healthy Lifestyle"
            },
            {
                "title": "Practice Digital Boundaries",
                "description": f"With {screen_time:.1f} hours of daily screen time, setting app limits can significantly reduce digital fatigue.",
                "icon": "fa-mobile-screen",
                "color": "var(--neon-purple)",
                "category": "Digital Wellness"
            },
            {
                "title": "Schedule Routine Social Connections",
                "description": "Connecting with friends or family serves as an emotional buffer. Reach out to a peer or family member today.",
                "icon": "fa-comments",
                "color": "var(--neon-orange)",
                "category": "Social Connection"
            },
            {
                "title": "Decompress with Creative Hobbies",
                "description": "Set aside time daily for non-academic interests, music, or reading to allow your mind to fully decompress.",
                "icon": "fa-music",
                "color": "var(--neon-pink)",
                "category": "Stress Relief"
            }
        ]

        for item in general_pool:
            if len(recommendations) >= 5:
                break
            # Avoid duplicate titles
            if not any(r["title"] == item["title"] for r in recommendations):
                recommendations.append(item)

        return {
            "stress": final_stress,
            "anxiety": final_anxiety,
            "depression": final_depression,
            "burnout": final_burnout,
            "academic_strain": final_academic_strain,
            "wellness": final_wellness,
            "emotion": emotion,
            "risk": risk_level,
            "risk_level": risk_level,
            "final_risk_level": risk_level,
            "emotion_scores": emotion_scores,
            "top_positive_factors": top_positive_factors,
            "top_negative_factors": top_negative_factors,
            "prediction_reliability": prediction_reliability,
            "crisis_triggered": is_crisis,
            "behavioral_probability": round(behavioral_probability, 4),
            "text_probability": round(text_probability, 4),
            "combined_probability": round(combined_probability, 4),
            "recommendations": recommendations
        }


# Global singleton prediction service instance
prediction_service = PredictionService()
