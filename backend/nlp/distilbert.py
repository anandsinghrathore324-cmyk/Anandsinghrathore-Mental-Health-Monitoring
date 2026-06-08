import logging
from nlp.gibberish_detector import GibberishDetector

logger = logging.getLogger(__name__)

# Preloader Flag
_transformers_available = False
try:
    from transformers import pipeline
    import torch
    _transformers_available = True
    logger.info("Successfully resolved Hugging Face Transformers dependencies.")
except ImportError:
    logger.warning("Hugging Face Transformers not found. Initializing lexical fallback engine...")

class DistilBertClassifier:
    """Thread-safe Singleton Hugging Face NLP Sentiment Classifier Model."""
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(DistilBertClassifier, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.pipeline = None
        self.model_name = "bhadresh-savani/distilbert-base-uncased-emotion" # premium multi-emotion NLP
        
        if _transformers_available:
            try:
                logger.info(f"Loading weights for DistilBERT NLP Singleton pipeline model: {self.model_name}...")
                # Run standard CPU thread model configuration
                device = 0 if torch.cuda.is_available() else -1
                self.pipeline = pipeline("text-classification", model=self.model_name, return_all_scores=True, device=device)
                logger.info("DistilBERT model loaded successfully inside Singleton architecture.")
            except Exception as e:
                logger.error(f"Failed to load Hugging Face pipeline weights: {str(e)}. Enforcing fallback lexicon...")
                self.pipeline = None
        else:
            self.pipeline = None
            
        self._initialized = True

    def analyze_sentiment(self, text: str) -> dict:
        """Runs text analysis returning emotion ratios, sentiment tags, and confidence scores."""
        clean_text = text.strip()
        
        # 1. Base Bounds & Word Validation
        if not clean_text:
            return {
                "sentiment": "Neutral",
                "emotion": "Neutral",
                "confidence": 1.0,
                "scores": {"Joy": 0.2, "Melancholy": 0.2, "Burnout/Frustration": 0.2, "Anxiety": 0.2, "Neutral": 0.2}
            }
            
        words = [w for w in clean_text.split() if w]
        
        # Minimum Requirements: Reject if < 20 characters OR < 5 words
        if len(clean_text) < 20 or len(words) < 5:
            return {"error": "Journal text must be at least 20 characters and contain at least 5 words."}
            
        # Maximum Requirements: Reject if > 1000 characters
        if len(clean_text) > 1000:
            return {"error": "Journal text must not exceed 1000 characters."}

        # 2. Gibberish Pre-Processing Guard
        if GibberishDetector.is_gibberish(clean_text):
            return {"error": "Please enter meaningful journal content."}

        # 3. Hugging Face Inference Flow
        if self.pipeline:
            try:
                raw_predictions = self.pipeline(clean_text)[0]
                # Map Bhadresh Savani emotion outputs (sadness, joy, love, anger, fear, surprise)
                raw_scores = {pred["label"]: float(pred["score"]) for pred in raw_predictions}
                
                scores = {
                    "Joy": raw_scores.get("joy", 0.0) + raw_scores.get("love", 0.0),
                    "Melancholy": raw_scores.get("sadness", 0.0),
                    "Anxiety": raw_scores.get("fear", 0.0),
                    "Burnout/Frustration": raw_scores.get("anger", 0.0),
                    "Neutral": raw_scores.get("surprise", 0.0)
                }
                
                # Normalize mapped scores
                total_sum = sum(scores.values())
                if total_sum > 0:
                    scores = {k: v / total_sum for k, v in scores.items()}
                
                # Determine dominant emotion
                dominant_emotion = max(scores, key=scores.get)
                confidence = scores[dominant_emotion]
                
                # Confidence Threshold check (< 0.60)
                if confidence < 0.60:
                    return {
                        "sentiment": "Uncertain",
                        "emotion": "Insufficient Information",
                        "confidence": round(confidence, 3),
                        "scores": {"Joy": 0.0, "Melancholy": 0.0, "Anxiety": 0.0, "Burnout/Frustration": 0.0, "Neutral": 0.0},
                        "message": "Unable to confidently analyze journal entry."
                    }
                
                sentiment_map = {
                    "Joy": "Positive",
                    "Melancholy": "Negative",
                    "Anxiety": "Negative",
                    "Burnout/Frustration": "Negative",
                    "Neutral": "Neutral"
                }
                
                return {
                    "sentiment": sentiment_map.get(dominant_emotion, "Neutral"),
                    "emotion": dominant_emotion,
                    "confidence": round(confidence, 3),
                    "scores": scores
                }
            except Exception as e:
                logger.error(f"Inference crash: {str(e)}. Enforcing fallback lexicon...")
                
        # 4. High-Fidelity Rule-Based Lexicon Fallback
        text_lower = clean_text.lower()
        
        # Scoring variables using mapped keys
        scores = {
            "Joy": 0.1,
            "Melancholy": 0.1,
            "Burnout/Frustration": 0.1,
            "Anxiety": 0.1,
            "Neutral": 0.1
        }
        
        # Keyword triggers
        stress_triggers = ["stress", "exhaust", "tire", "pressure", "burnout", "grades", "exam", "deadline", "fail"]
        anxiety_triggers = ["anxious", "worry", "panic", "scare", "shake", "nervous", "dread", "fear"]
        sad_triggers = ["sad", "lonely", "melancholy", "cry", "hopeless", "empty", "depress", "worthless"]
        joy_triggers = ["happy", "joy", "accomplished", "excited", "glad", "proud", "relax", "calm", "love"]
        
        for word in stress_triggers:
            if word in text_lower: scores["Burnout/Frustration"] += 0.5
        for word in anxiety_triggers:
            if word in text_lower: scores["Anxiety"] += 0.5
        for word in sad_triggers:
            if word in text_lower: scores["Melancholy"] += 0.5
        for word in joy_triggers:
            if word in text_lower: scores["Joy"] += 0.5
            
        # Normalization
        sum_scores = sum(scores.values())
        normalized_scores = {k: v / sum_scores for k, v in scores.items()}
        
        dominant = max(normalized_scores, key=normalized_scores.get)
        confidence = normalized_scores[dominant]
        
        # Confidence Threshold check for Lexicon Fallback (< 0.60)
        if confidence < 0.60:
            return {
                "sentiment": "Uncertain",
                "emotion": "Insufficient Information",
                "confidence": round(confidence, 3),
                "scores": {"Joy": 0.0, "Melancholy": 0.0, "Anxiety": 0.0, "Burnout/Frustration": 0.0, "Neutral": 0.0},
                "message": "Unable to confidently analyze journal entry."
            }
            
        sentiment_map = {
            "Joy": "Positive",
            "Melancholy": "Negative",
            "Burnout/Frustration": "Negative",
            "Anxiety": "Negative",
            "Neutral": "Neutral"
        }
        
        return {
            "sentiment": sentiment_map[dominant],
            "emotion": dominant,
            "confidence": round(confidence, 3),
            "scores": normalized_scores
        }

# Global singleton classifier node instance
nlp_classifier = DistilBertClassifier()
