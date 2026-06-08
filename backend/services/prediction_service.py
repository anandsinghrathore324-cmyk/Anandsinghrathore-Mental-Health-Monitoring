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
        self.model = None
        
        # Load pre-trained Ridge regression model
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(current_dir, "..", "ml", "saved_model.pkl")
            if os.path.exists(model_path):
                with open(model_path, "rb") as f:
                    self.model = pickle.load(f)
                logger.info("Successfully loaded Ridge Regression pickle weights from route absolute path.")
            else:
                fallback_path = os.path.join("ml", "saved_model.pkl")
                if os.path.exists(fallback_path):
                    with open(fallback_path, "rb") as f:
                        self.model = pickle.load(f)
                    logger.info("Successfully loaded Ridge Regression pickle weights from fallback path.")
                else:
                    logger.warning("Could not find saved_model.pkl file. Enforcing rule-based calculations...")
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
        emotion = nlp_res.get("emotion", "Neutral")
        sentiment = nlp_res.get("sentiment", "Neutral")

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

        # 3. Overall Wellness Index (Option B: ML-primary baseline)
        features = self.preprocessor.extract_features(data)
        
        # Explainability lists
        feature_names = [
            "Study hours",
            "Sleep hours",
            "Screen time",
            "Academic pressure",
            "Social media usage",
            "Sleep deficit",
            "Screen excess"
        ]
        
        top_positive_factors = []
        top_negative_factors = []
        prediction_reliability = "High"
        
        if self.model:
            try:
                # Ridge model predict
                ml_wellness = float(self.model.predict(features)[0])
                final_wellness = int(np.clip(ml_wellness, 0, 100))
                
                # Model explainability: compute coef * scaled_val contribution
                if hasattr(self.model, "coef_"):
                    coefs = self.model.coef_
                    scaled_vals = features[0]
                    contributions = coefs * scaled_vals
                    
                    paired = list(zip(feature_names, contributions))
                    pos_paired = [p for p in paired if p[1] > 0]
                    neg_paired = [p for p in paired if p[1] < 0]
                    
                    # Sort positive: descending
                    pos_paired.sort(key=lambda x: x[1], reverse=True)
                    # Sort negative: ascending
                    neg_paired.sort(key=lambda x: x[1])
                    
                    top_positive_factors = [f"{name} (contribution: {val:+.2f})" for name, val in pos_paired]
                    top_negative_factors = [f"{name} (contribution: {val:+.2f})" for name, val in neg_paired]
            except Exception as e:
                logger.error(f"Ridge prediction failed: {str(e)}. Defaulting to pure rule-math.")
                risk_score = (final_stress * 0.4) + (final_anxiety * 0.4) + (final_depression * 0.2)
                final_wellness = int(np.clip(100.0 - risk_score, 0, 100))
                prediction_reliability = "Medium"
        else:
            risk_score = (final_stress * 0.4) + (final_anxiety * 0.4) + (final_depression * 0.2)
            final_wellness = int(np.clip(100.0 - risk_score, 0, 100))
            prediction_reliability = "Medium"

        # 4. Clinical safety overrides
        crisis_words = ["suicide", "kill myself", "self-harm", "end my life", "want to die", "harm myself", "cutting", "harming myself"]
        is_crisis = any(cw in diary_text.lower() for cw in crisis_words)
        
        if is_crisis:
            # Overrides to force High Risk classification
            final_wellness = min(final_wellness, 25)
            logger.warning("Clinical crisis indicators detected. Wellness Index overridden.")

        # Set prediction reliability to Medium if NLP confidence was low
        if emotion == "Insufficient Information":
            prediction_reliability = "Medium"

        # Risk Classification
        if final_wellness >= 75:
            risk_level = "Low"
        elif final_wellness >= 50:
            risk_level = "Moderate"
        else:
            risk_level = "High"

        return {
            "stress": final_stress,
            "anxiety": final_anxiety,
            "depression": final_depression,
            "burnout": final_burnout,
            "wellness": final_wellness,
            "emotion": emotion,
            "risk": risk_level,
            "emotion_scores": nlp_res.get("scores", {}),
            "top_positive_factors": top_positive_factors,
            "top_negative_factors": top_negative_factors,
            "prediction_reliability": prediction_reliability,
            "crisis_triggered": is_crisis
        }

# Global singleton prediction service instance
prediction_service = PredictionService()
