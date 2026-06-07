import pickle
import numpy as np
import logging
from ml.preprocess import MLPreprocessor
from services.nlp_service import NlpService

logger = logging.getLogger(__name__)

class PredictionService:
    """Predictive logic engine assessing student mental health threats."""
    
    def __init__(self):
        self.preprocessor = MLPreprocessor()
        self.model = None
        
        # Load pre-trained Ridge regression model
        try:
            with open("ml/saved_model.pkl", "rb") as f:
                self.model = pickle.load(f)
            logger.info("Successfully loaded Ridge Regression pickle weights.")
        except Exception as e:
            logger.warning(f"Could not load Ridge model: {str(e)}. Enforcing formula math...")

    def run_assessment(self, data: dict) -> dict:
        """Executes full diagnostic scanning combining workload variables and NLP sentiment logs."""
        # 1. Capture variables
        study_hours = float(data.get("study_hours", 6.0))
        sleep_hours = float(data.get("sleep_hours", 7.0))
        screen_time = float(data.get("screen_time", 5.0))
        academic_pressure = int(data.get("academic_pressure", 5))
        input_stress = int(data.get("stress_level", 5))
        input_anxiety = int(data.get("anxiety_level", 5))
        mood = data.get("mood", "calm").strip().lower()
        diary_text = data.get("text", "").strip()

        # 2. Math Risk Equations
        sleep_deficit = self.preprocessor.calculate_sleep_deficit(sleep_hours)
        screen_excess = self.preprocessor.calculate_screen_excess(screen_time)

        # NLP Text impact
        nlp_res = NlpService.analyze_diary_entry(diary_text)
        emotion = nlp_res["emotion"]
        sentiment = nlp_res["sentiment"]

        # 2a. Stress score
        base_stress = (input_stress * 6) + (academic_pressure * 3) + (sleep_deficit * 5)
        if sentiment == "Negative":
            base_stress += 8
        if "exam" in diary_text.lower() or "deadline" in diary_text.lower():
            base_stress += 6
        final_stress = min(98, max(8, int(base_stress)))

        # 2b. Anxiety score
        base_anxiety = (input_anxiety * 7) + (academic_pressure * 2) + (sleep_deficit * 3)
        if "panic" in diary_text.lower() or "scared" in diary_text.lower():
            base_anxiety += 12
        final_anxiety = min(99, max(5, int(base_anxiety)))

        # 2c. Depression score
        base_depression = (sleep_deficit * 6) + (screen_excess * 4) + (academic_pressure * 2)
        if mood in ["sad", "melancholy"]:
            base_depression += 20
        if "hopeless" in diary_text.lower() or "worthless" in diary_text.lower():
            base_depression += 20
        final_depression = min(98, max(4, int(base_depression)))

        # 2d. Burnout score
        base_burnout = (final_stress * 0.6) + (screen_excess * 3) + (sleep_deficit * 4)
        final_burnout = min(98, max(5, int(base_burnout)))

        # 3. Overall Wellness Index (Issue 5)
        # Blends Ridge regression predictions with hard equations for absolute robustness
        risk_score = (final_stress * 0.4) + (final_anxiety * 0.4) + (final_depression * 0.2)
        base_wellness = 100.0 - risk_score
        
        if self.model:
            try:
                features = self.preprocessor.extract_features(data)
                ml_wellness = float(self.model.predict(features)[0])
                # Blended weighting (80% math rules, 20% Ridge model)
                final_wellness = int(np.clip((base_wellness * 0.8) + (ml_wellness * 0.2), 0, 100))
            except Exception as e:
                logger.error(f"Ridge prediction failed: {str(e)}. Defaulting to pure rule-math.")
                final_wellness = int(np.clip(base_wellness, 0, 100))
        else:
            final_wellness = int(np.clip(base_wellness, 0, 100))

        # Risk Classification
        if final_wellness >= 75:
            risk_level = "Low"
        elif final_wellness >= 50:
            risk_level = "Moderate"
        else:
            risk_level = "High"

        # Dom emotion is determined using the highest emotion probability (Issue 1)
        # Mapped emotion is preserved from nlp_res to prevent contradictions (Issue 7)

        return {
            "stress": final_stress,
            "anxiety": final_anxiety,
            "depression": final_depression,
            "burnout": final_burnout,
            "wellness": final_wellness,
            "emotion": emotion,
            "risk": risk_level,
            "emotion_scores": nlp_res.get("scores", {})
        }

# Global singleton prediction service instance
prediction_service = PredictionService()
