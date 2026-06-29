"""
prediction_service.py  —  AIRA Core Prediction Engine
=======================================================
Loads both real ML models DIRECTLY in-process:
  • Model 1: Logistic Regression (trained on Student Depression Dataset, ~80% accuracy)
  • Model 2: TF-IDF + Logistic Regression (trained on Mental Health Corpus)
  • NLP    : DistilBERT (if transformers installed) OR lexical keyword fallback

No separate microservices on ports 5001/5002 needed.
"""

import os
import re
import pickle
import numpy as np
import logging
import pandas as pd
from pathlib import Path

logger = logging.getLogger(__name__)

# ── Resolve absolute paths relative to this file ────────────────────────────
_HERE        = Path(__file__).parent.resolve()              # backend/services/
_BACKEND_DIR = _HERE.parent                                  # backend/
_PROJECT_ROOT = _BACKEND_DIR.parent                          # project root

# Model 1 — Behavioral Logistic Regression (real Kaggle-trained model)
_BEHAV_MODEL_PATH = _PROJECT_ROOT / "ml" / "Model 1 Behavioral Mental Health Predictor" / "models" / "risk_model.pkl"
_BEHAV_PREP_PATH  = _PROJECT_ROOT / "ml" / "Model 1 Behavioral Mental Health Predictor" / "preprocessed" / "preprocessor.joblib"

# Model 2 — TF-IDF + Logistic Regression text classifier
_TEXT_MODEL_PATH      = _PROJECT_ROOT / "ml" / "Model 2  Text Mental Health Model" / "text_model.pkl"
_TEXT_VECTORIZER_PATH = _PROJECT_ROOT / "ml" / "Model 2  Text Mental Health Model" / "text_vectorizer.pkl"

FEATURE_COLUMNS = [
    "Age", "Gender", "Academic Pressure", "Study Satisfaction",
    "Sleep Duration", "Dietary Habits", "Work/Study Hours",
    "Financial Stress", "Family History of Mental Illness"
]


def _clean_text(text: str) -> str:
    """Matches exact cleaning used during text model training."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


class PredictionService:
    """
    Loads both real ML models at startup and runs direct in-process inference.
    Falls back to calibrated math formulas if model files are missing.
    """

    def __init__(self):
        # ── Load Behavioral Model (Model 1) ──────────────────────────────────
        self._behav_model        = None
        self._behav_preprocessor = None
        self._behav_ready        = False
        self._load_behavioral_model()

        # ── Load Text Model (Model 2) ─────────────────────────────────────────
        self._text_model      = None
        self._text_vectorizer = None
        self._text_ready      = False
        self._load_text_model()

        # ── NLP (DistilBERT or lexical fallback — handled in nlp_service.py) ─
        from services.nlp_service import NlpService
        self._nlp = NlpService

    # ─────────────────────────────────────────────────────────────────────────
    # Model loaders
    # ─────────────────────────────────────────────────────────────────────────

    def _load_behavioral_model(self):
        try:
            import joblib
            if not _BEHAV_MODEL_PATH.exists():
                raise FileNotFoundError(f"risk_model.pkl not found at {_BEHAV_MODEL_PATH}")
            if not _BEHAV_PREP_PATH.exists():
                raise FileNotFoundError(f"preprocessor.joblib not found at {_BEHAV_PREP_PATH}")

            self._behav_model        = joblib.load(_BEHAV_MODEL_PATH)
            self._behav_preprocessor = joblib.load(_BEHAV_PREP_PATH)
            self._behav_ready        = True
            logger.info("✅ Behavioral model (Model 1 — LR, Kaggle-trained) loaded successfully.")
        except Exception as e:
            logger.warning(f"⚠️  Behavioral model not loaded: {e}. Math fallback will be used.")

    def _load_text_model(self):
        try:
            if not _TEXT_MODEL_PATH.exists():
                raise FileNotFoundError(f"text_model.pkl not found at {_TEXT_MODEL_PATH}")
            if not _TEXT_VECTORIZER_PATH.exists():
                raise FileNotFoundError(f"text_vectorizer.pkl not found at {_TEXT_VECTORIZER_PATH}")

            with open(_TEXT_MODEL_PATH, "rb") as f:
                self._text_model = pickle.load(f)
            with open(_TEXT_VECTORIZER_PATH, "rb") as f:
                self._text_vectorizer = pickle.load(f)
            self._text_ready = True
            logger.info("✅ Text classifier model (Model 2 — TF-IDF + LR) loaded successfully.")
        except Exception as e:
            logger.warning(f"⚠️  Text model not loaded: {e}. NLP emotion fallback will be used.")

    # ─────────────────────────────────────────────────────────────────────────
    # Inference helpers
    # ─────────────────────────────────────────────────────────────────────────

    def _predict_behavioral(self, data: dict,
                            sleep_deficit: float,
                            academic_pressure_raw: int,
                            study_satisfaction_raw: int,
                            financial_stress_raw: int,
                            work_hours: float,
                            family_history: str) -> tuple[float, str]:
        """
        Returns (probability_of_depression [0-1], reliability_label).
        Tries real model first; falls back to deterministic formula.
        """
        if self._behav_ready:
            try:
                age          = float(data.get("age", 21.0))
                gender       = data.get("gender", "Male")
                sleep_hours  = float(data.get("sleep_hours", 7.0))
                screen_time  = float(data.get("screen_time", 5.0))
                dietary_habits = data.get("dietary_habits", "Moderate")

                # Map sleep hours → categorical string (matches training labels)
                if sleep_hours < 5.0:
                    sleep_dur = "Less than 5 hours"
                elif sleep_hours <= 6.0:
                    sleep_dur = "5-6 hours"
                elif sleep_hours <= 8.0:
                    sleep_dur = "7-8 hours"
                else:
                    sleep_dur = "More than 8 hours"

                # Map gender
                g_lower = gender.lower() if isinstance(gender, str) else ""
                gender_mapped = "Female" if "female" in g_lower else "Male"

                # Map dietary habits
                d_lower = dietary_habits.lower() if isinstance(dietary_habits, str) else ""
                if "healthy" in d_lower:
                    dietary_mapped = "Healthy"
                elif "unhealthy" in d_lower:
                    dietary_mapped = "Unhealthy"
                else:
                    dietary_mapped = "Moderate"

                # Scale to model's range (0-5 scale)
                acad_scaled = float(academic_pressure_raw) / 2.0
                sat_scaled  = float(study_satisfaction_raw) / 2.0
                fin_scaled  = float(financial_stress_raw) / 2.0

                family_mapped = "Yes" if str(family_history).lower() == "yes" else "No"
                study_hours = float(data.get("study_hours", 6.0))
                work_study  = work_hours + study_hours

                row = {
                    "Age":                             age,
                    "Gender":                          gender_mapped,
                    "Academic Pressure":               acad_scaled,
                    "Study Satisfaction":              sat_scaled,
                    "Sleep Duration":                  sleep_dur,
                    "Dietary Habits":                  dietary_mapped,
                    "Work/Study Hours":                work_study,
                    "Financial Stress":                fin_scaled,
                    "Family History of Mental Illness": family_mapped
                }

                df_input = pd.DataFrame([row])[FEATURE_COLUMNS]
                X_prep   = self._behav_preprocessor.transform(df_input)

                # Reconstruct feature names (needed for sklearn model with feature_names_in_)
                try:
                    numeric_feats = ["Age", "Academic Pressure", "Study Satisfaction",
                                     "Work/Study Hours", "Financial Stress"]
                    cat_enc   = self._behav_preprocessor.named_transformers_["cat"].named_steps["onehot"]
                    cat_feats = ["Gender", "Sleep Duration", "Dietary Habits",
                                 "Family History of Mental Illness"]
                    enc_names = cat_enc.get_feature_names_out(cat_feats).tolist()
                    all_names = numeric_feats + enc_names
                    X_prep = pd.DataFrame(X_prep, columns=all_names)
                except Exception:
                    pass  # Fall through with raw numpy array

                prob = float(self._behav_model.predict_proba(X_prep)[0][1])
                logger.info(f"🤖 Behavioral model prediction: {prob:.4f} (REAL MODEL)")
                return prob, "High"

            except Exception as e:
                logger.warning(f"Behavioral model inference failed: {e}. Using math fallback.")

        # ── Math fallback (deterministic) ────────────────────────────────────
        score = (
            academic_pressure_raw * 6.0 +
            financial_stress_raw  * 4.0 +
            (10 - study_satisfaction_raw) * 3.0 +
            sleep_deficit * 5.0 +
            work_hours * 1.5
        )
        if str(family_history).lower() == "yes":
            score += 10
        prob = float(np.clip(score / 213.0, 0.0, 1.0))
        logger.info(f"📐 Behavioral fallback (math formula): {prob:.4f}")
        return prob, "Medium"

    def _predict_text(self, diary_text: str, joy_score: float) -> tuple[float, str]:
        """
        Returns (probability_of_mental_health_risk [0-1], reliability_label).
        Tries real text model first; falls back to (1 - joy_score).
        """
        if self._text_ready and diary_text.strip():
            try:
                cleaned  = _clean_text(diary_text)
                features = self._text_vectorizer.transform([cleaned])
                prob     = float(self._text_model.predict_proba(features)[0][1])
                logger.info(f"🤖 Text model prediction: {prob:.4f} (REAL MODEL)")
                return prob, "High"
            except Exception as e:
                logger.warning(f"Text model inference failed: {e}. Using NLP fallback.")

        # ── Fallback: invert joy score ────────────────────────────────────────
        prob = float(np.clip(1.0 - joy_score, 0.0, 1.0))
        logger.info(f"📐 Text fallback (1 - joy_score): {prob:.4f}")
        return prob, "Medium"

    # ─────────────────────────────────────────────────────────────────────────
    # Main assessment
    # ─────────────────────────────────────────────────────────────────────────

    def run_assessment(self, data: dict) -> dict:
        """Executes full diagnostic combining ML models + rule-based risk scores."""

        # 1. Capture all inputs
        age                 = float(data.get("age", 21.0))
        gender              = data.get("gender", "Male")
        study_hours         = float(data.get("study_hours", 6.0))
        sleep_hours         = float(data.get("sleep_hours", 7.0))
        screen_time         = float(data.get("screen_time", 5.0))
        academic_pressure   = int(data.get("academic_pressure", 5))
        input_stress        = int(data.get("stress_level", 5))
        input_anxiety       = int(data.get("anxiety_level", 5))
        mood                = data.get("mood", "calm").strip().lower()
        diary_text          = data.get("text", "").strip()
        study_satisfaction  = int(data.get("study_satisfaction", 5))
        dietary_habits      = data.get("dietary_habits", "Moderate")
        financial_stress    = int(data.get("financial_stress", 5))
        family_history      = data.get("family_history", "No")
        work_hours          = float(data.get("work_hours", 0.0))

        # 2. Derived features
        sleep_deficit = max(0.0, 8.0 - sleep_hours)
        screen_excess = max(0.0, screen_time - 6.0)

        # 3. NLP Sentiment Analysis (DistilBERT or lexical fallback)
        nlp_res      = self._nlp.analyze_diary_entry(diary_text)
        emotion      = nlp_res.get("emotion", "Neutral")
        sentiment    = nlp_res.get("sentiment", "Neutral")
        emotion_scores = nlp_res.get("scores", {})
        joy_score    = emotion_scores.get("Joy", 0.5)

        # 4. Rule-based sub-scores (normalised 0-100)
        base_stress = (
            input_stress * 5.0 +
            academic_pressure * 3.0 +
            sleep_deficit * 4.0 +
            financial_stress * 3.0 +
            (10 - study_satisfaction) * 2.0 +
            work_hours * 1.5
        )
        if sentiment == "Negative":
            base_stress += 8
        if "exam" in diary_text.lower() or "deadline" in diary_text.lower():
            base_stress += 6
        final_stress = int(np.clip((base_stress / 200.0) * 100, 0, 100))

        base_anxiety = (
            input_anxiety * 6.0 +
            academic_pressure * 2.0 +
            sleep_deficit * 3.0 +
            financial_stress * 3.0
        )
        if str(family_history).lower() == "yes":
            base_anxiety += 10
        if "panic" in diary_text.lower() or "scared" in diary_text.lower():
            base_anxiety += 12
        final_anxiety = int(np.clip((base_anxiety / 156.0) * 100, 0, 100))

        base_burnout = (
            final_stress * 0.4 +
            screen_excess * 3.0 +
            sleep_deficit * 4.0 +
            (10 - study_satisfaction) * 2.0 +
            work_hours * 2.0
        )
        final_burnout = int(np.clip((base_burnout / 192.0) * 100, 0, 100))

        base_strain = (
            academic_pressure * 6.0 +
            study_hours * 2.0 +
            work_hours * 1.5 +
            (10 - study_satisfaction) * 2.0
        )
        final_academic_strain = int(np.clip((base_strain / 162.0) * 100, 0, 100))

        # 5. ML model predictions (real or fallback)
        behav_prob, behav_reliability = self._predict_behavioral(
            data, sleep_deficit, academic_pressure,
            study_satisfaction, financial_stress, work_hours, family_history
        )
        text_prob, text_reliability = self._predict_text(diary_text, joy_score)

        # 6. Determine overall reliability
        if behav_reliability == "High" and text_reliability == "High":
            prediction_reliability = "High"
        elif behav_reliability == "High" or text_reliability == "High":
            prediction_reliability = "Medium"
        else:
            prediction_reliability = "Low"

        if emotion == "Insufficient Information":
            # Diary was too vague — downgrade reliability
            if prediction_reliability == "High":
                prediction_reliability = "Medium"

        # 7. Blended wellness score
        combined_probability = (0.4 * behav_prob) + (0.6 * text_prob)
        final_wellness       = int(np.clip((1.0 - combined_probability) * 100, 0, 100))

        # 8. Crisis override
        crisis_words = [
            "suicide", "kill myself", "self-harm", "end my life", "want to die",
            "harm myself", "cutting", "harming myself"
        ]
        is_crisis = any(cw in diary_text.lower() for cw in crisis_words)
        if is_crisis:
            final_wellness       = min(final_wellness, 15)
            combined_probability = max(combined_probability, 0.85)
            logger.warning("🚨 Clinical crisis indicators detected. Wellness index overridden.")

        # 9. Risk level
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

        # 10. Depression score derived from behavioral model probability
        final_depression = min(98, max(4, int(behav_prob * 100)))

        # 11. Explainability factors
        top_positive_factors = []
        top_negative_factors = []
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
        if self._behav_ready:
            top_negative_factors.append("Behavioral model: real Kaggle-trained LR (79.8% acc)")
        if self._text_ready:
            top_negative_factors.append("Text model: real TF-IDF + LR classifier")

        # 12. Recommendations
        recommendations = []

        if risk_level == "Low":
            recommendations.append({
                "title": "Maintain Current Wellness Routines",
                "description": "Your wellness score is high! Keep up your healthy sleep, study, and life balance to maintain this positive trend.",
                "icon": "fa-heart", "color": "var(--neon-emerald)", "category": "Risk-based"
            })
        elif risk_level == "Mild":
            recommendations.append({
                "title": "Build Resilience & Support Networks",
                "description": "You are experiencing mild mental strain. Consider sharing your workload with friends or peers and practicing daily relaxation techniques.",
                "icon": "fa-users", "color": "var(--neon-cyan)", "category": "Risk-based"
            })
        elif risk_level == "Moderate":
            recommendations.append({
                "title": "Proactive Stress Management",
                "description": "Your stress and workload saturation levels are registering moderate anxiety indicators. Set boundaries and allocate dedicated time for self-care.",
                "icon": "fa-shield-heart", "color": "var(--neon-orange)", "category": "Risk-based"
            })
        elif risk_level == "High":
            recommendations.append({
                "title": "Structured Cognitive De-escalation",
                "description": "High saturation levels identified. System detects critical anxiety/depression warnings. AI recommends immediate workload reduction and counselor consultation.",
                "icon": "fa-triangle-exclamation", "color": "var(--neon-rose)", "category": "Risk-based"
            })
        elif risk_level == "Critical":
            recommendations.append({
                "title": "Urgent Support Recommendation",
                "description": "Your wellness indicators are at a critical level. We strongly recommend talking to a counselor or calling a crisis line immediately.",
                "icon": "fa-circle-exclamation", "color": "var(--neon-rose)", "category": "Risk-based"
            })

        if sleep_hours < 7.0:
            recommendations.append({
                "title": "Optimize Sleep Hygiene",
                "description": f"You are averaging {sleep_hours:.1f} hours of sleep. Aim for 7-9 hours of consistent sleep and limit screen use 30 minutes before bedtime.",
                "icon": "fa-bed", "color": "var(--neon-cyan)", "category": "Sleep Improvement"
            })
        if academic_pressure >= 7:
            recommendations.append({
                "title": "Structure Your Study Strategy",
                "description": f"Academic pressure is high ({academic_pressure}/10). Break large tasks into smaller steps, prioritize, and take 5-minute study breaks.",
                "icon": "fa-graduation-cap", "color": "var(--neon-purple)", "category": "Study Management"
            })
        if financial_stress >= 7:
            recommendations.append({
                "title": "Financial Support & Resources",
                "description": f"Financial stress is elevated ({financial_stress}/10). Connect with student financial services or explore budgeting applications.",
                "icon": "fa-wallet", "color": "var(--neon-orange)", "category": "Financial Support"
            })
        if input_anxiety >= 7 or final_anxiety >= 70 or text_prob > 0.6:
            recommendations.append({
                "title": "Practice Mindfulness & Breathing",
                "description": "High anxiety or emotional strain detected. Utilize our Guided Breathing center for Box Breathing or the 4-7-8 method.",
                "icon": "fa-wind", "color": "var(--neon-cyan)", "category": "Breathing & Mindfulness"
            })
        if study_satisfaction <= 4:
            recommendations.append({
                "title": "Academic Counseling & Guidance",
                "description": f"Your study satisfaction is low ({study_satisfaction}/10). Schedule an advisory session to review your curriculum and course objectives.",
                "icon": "fa-chalkboard-user", "color": "var(--neon-purple)", "category": "Academic Counseling"
            })

        general_pool = [
            {
                "title": "Incorporate Daily Physical Activity",
                "description": "A simple 15-minute walk can release endorphins, lower stress hormones, and improve cognitive performance.",
                "icon": "fa-person-running", "color": "var(--neon-emerald)", "category": "General Wellness"
            },
            {
                "title": "Nourish and Hydrate Your Body",
                "description": "Eating regular, balanced meals and staying hydrated stabilizes blood sugar and energy levels throughout the day.",
                "icon": "fa-apple-whole", "color": "var(--neon-cyan)", "category": "Healthy Lifestyle"
            },
            {
                "title": "Practice Digital Boundaries",
                "description": f"With {screen_time:.1f} hours of daily screen time, setting app limits can significantly reduce digital fatigue.",
                "icon": "fa-mobile-screen", "color": "var(--neon-purple)", "category": "Digital Wellness"
            },
            {
                "title": "Schedule Routine Social Connections",
                "description": "Connecting with friends or family serves as an emotional buffer. Reach out to a peer or family member today.",
                "icon": "fa-comments", "color": "var(--neon-orange)", "category": "Social Connection"
            },
            {
                "title": "Decompress with Creative Hobbies",
                "description": "Set aside time daily for non-academic interests, music, or reading to allow your mind to fully decompress.",
                "icon": "fa-music", "color": "var(--neon-pink)", "category": "Stress Relief"
            },
        ]
        for item in general_pool:
            if len(recommendations) >= 5:
                break
            if not any(r["title"] == item["title"] for r in recommendations):
                recommendations.append(item)

        logger.info(
            f"📋 Assessment complete | Wellness={final_wellness} | Risk={risk_level} | "
            f"BehavProb={behav_prob:.3f} | TextProb={text_prob:.3f} | "
            f"BehavModel={'REAL' if self._behav_ready else 'FALLBACK'} | "
            f"TextModel={'REAL' if self._text_ready else 'FALLBACK'}"
        )

        return {
            "stress":                 final_stress,
            "anxiety":                final_anxiety,
            "depression":             final_depression,
            "burnout":                final_burnout,
            "academic_strain":        final_academic_strain,
            "wellness":               final_wellness,
            "emotion":                emotion,
            "risk":                   risk_level,
            "risk_level":             risk_level,
            "final_risk_level":       risk_level,
            "emotion_scores":         emotion_scores,
            "top_positive_factors":   top_positive_factors,
            "top_negative_factors":   top_negative_factors,
            "prediction_reliability": prediction_reliability,
            "crisis_triggered":       is_crisis,
            "behavioral_probability": round(behav_prob, 4),
            "text_probability":       round(text_prob, 4),
            "combined_probability":   round(combined_probability, 4),
            "model_status": {
                "behavioral_model": "real" if self._behav_ready else "math_fallback",
                "text_model":       "real" if self._text_ready  else "nlp_fallback",
                "nlp_model":        "distilbert" if hasattr(self, '_nlp') else "lexical"
            },
            "recommendations":        recommendations
        }


# Global singleton
prediction_service = PredictionService()
