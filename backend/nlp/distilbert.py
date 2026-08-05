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
                device = 0 if torch.cuda.is_available() else -1
                # top_k=None replaces deprecated return_all_scores=True in transformers >=4.30
                self.pipeline = pipeline(
                    "text-classification",
                    model=self.model_name,
                    top_k=None,
                    device=device
                )
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
                output = self.pipeline(clean_text)
                # Normalise: top_k=None on a single string returns [[{...},...]]
                # Unwrap outer list if needed so we always have [{label, score}, ...]
                raw_predictions = output[0] if isinstance(output[0], list) else output
                raw_scores = {pred["label"]: float(pred["score"]) for pred in raw_predictions}
                
                joy_val = raw_scores.get("joy", 0.0) + raw_scores.get("love", 0.0)
                sadness_val = raw_scores.get("sadness", 0.0)
                fear_val = raw_scores.get("fear", 0.0)
                anger_val = raw_scores.get("anger", 0.0)
                neutral_val = raw_scores.get("surprise", 0.0)
                
                total_sum = joy_val + sadness_val + fear_val + anger_val + neutral_val
                if total_sum > 0:
                    joy_val /= total_sum
                    sadness_val /= total_sum
                    fear_val /= total_sum
                    anger_val /= total_sum
                    neutral_val /= total_sum
                
                scores = {
                    "Joy": round(joy_val, 4),
                    "Sadness": round(sadness_val, 4),
                    "Melancholy": round(sadness_val, 4),
                    "Fear": round(fear_val, 4),
                    "Anxiety": round(fear_val, 4),
                    "Anger": round(anger_val, 4),
                    "Burnout/Frustration": round(anger_val, 4),
                    "Neutral": round(neutral_val, 4)
                }
                
                # Determine dominant emotion
                primary_map = {
                    "Joy": joy_val,
                    "Melancholy": sadness_val,
                    "Sadness": sadness_val,
                    "Anxiety": fear_val,
                    "Burnout/Frustration": anger_val,
                    "Neutral": neutral_val
                }
                dominant_emotion = max(primary_map, key=primary_map.get)
                confidence = primary_map[dominant_emotion]
                
                if confidence < 0.35:
                    final_sentiment = "Uncertain"
                elif dominant_emotion in ["Joy"]:
                    final_sentiment = "Positive"
                elif dominant_emotion in ["Melancholy", "Sadness", "Anxiety", "Fear", "Burnout/Frustration", "Anger"]:
                    final_sentiment = "Negative"
                else:
                    final_sentiment = "Neutral"
                
                return {
                    "sentiment": final_sentiment,
                    "emotion": dominant_emotion,
                    "confidence": round(confidence, 3),
                    "scores": scores
                }
            except Exception as e:
                logger.error(f"Inference crash: {str(e)}. Enforcing fallback lexicon...")
                
        # 4. High-Fidelity Rule-Based Lexicon Fallback
        text_lower = clean_text.lower()
        
        # Base prior weights
        joy_weight = 0.05
        sadness_weight = 0.05
        fear_weight = 0.05
        anger_weight = 0.05
        neutral_weight = 0.20
        
        # Keyword triggers
        mild_stress = ["grades", "exam", "deadline", "midterm", "assignment", "busy", "workload", "study", "tired", "pressure"]
        severe_stress = ["burnout", "breakdown", "drowning", "suffocating", "cannot cope", "exhausted", "overwhelmed"]
        
        mild_anxiety = ["worry", "worried", "nervous", "restless", "trouble sleeping", "insomnia", "uneasy", "stressed", "stress"]
        severe_anxiety = ["anxious", "anxiety", "panic", "panicking", "scared", "shaking", "dread", "heart racing", "paralyzed", "terrified"]
        
        mild_sadness = ["sad", "lonely", "alone", "isolated", "gloomy", "down"]
        severe_depression = ["hopeless", "empty", "depress", "depressed", "depression", "worthless", "miserable", "giving up", "no point", "lost", "crying", "despair"]
        
        joy_triggers = [
            "happy", "joy", "accomplished", "excited", "glad", "proud", "relax",
            "relaxed", "calm", "peace", "peaceful", "love", "great", "motivated",
            "productive", "wonderful", "refreshing", "good", "confident", "thriving", "hopeful"
        ]
        
        for word in mild_stress:
            if word in text_lower:
                anger_weight += 0.12
                fear_weight += 0.08
        for word in severe_stress:
            if word in text_lower:
                anger_weight += 0.55
                fear_weight += 0.30
                
        for word in mild_anxiety:
            if word in text_lower:
                fear_weight += 0.18
                anger_weight += 0.08
        for word in severe_anxiety:
            if word in text_lower:
                fear_weight += 0.65
                anger_weight += 0.15
                
        for word in mild_sadness:
            if word in text_lower:
                sadness_weight += 0.20
        for word in severe_depression:
            if word in text_lower:
                sadness_weight += 0.75
                fear_weight += 0.15
                
        for word in joy_triggers:
            if word in text_lower:
                joy_weight += 0.65
                
        sum_weights = joy_weight + sadness_weight + fear_weight + anger_weight + neutral_weight
        joy_val = joy_weight / sum_weights
        sadness_val = sadness_weight / sum_weights
        fear_val = fear_weight / sum_weights
        anger_val = anger_weight / sum_weights
        neutral_val = neutral_weight / sum_weights
        
        scores = {
            "Joy": round(joy_val, 4),
            "Sadness": round(sadness_val, 4),
            "Melancholy": round(sadness_val, 4),
            "Fear": round(fear_val, 4),
            "Anxiety": round(fear_val, 4),
            "Anger": round(anger_val, 4),
            "Burnout/Frustration": round(anger_val, 4),
            "Neutral": round(neutral_val, 4)
        }
        
        primary_map = {
            "Joy": joy_val,
            "Melancholy": sadness_val,
            "Sadness": sadness_val,
            "Anxiety": fear_val,
            "Burnout/Frustration": anger_val,
            "Neutral": neutral_val
        }
        dominant = max(primary_map, key=primary_map.get)
        confidence = primary_map[dominant]
        
        # Check if text had any emotional trigger words or was completely flat
        has_triggers = any(w in text_lower for w in mild_stress + severe_stress + mild_anxiety + severe_anxiety + mild_sadness + severe_depression + joy_triggers)
        if not has_triggers or confidence < 0.35:
            final_sentiment = "Uncertain"
        elif dominant in ["Joy"]:
            final_sentiment = "Positive"
        elif dominant in ["Melancholy", "Sadness", "Anxiety", "Fear", "Burnout/Frustration", "Anger"]:
            final_sentiment = "Negative"
        else:
            final_sentiment = "Neutral"
        
        return {
            "sentiment": final_sentiment,
            "emotion": dominant,
            "confidence": round(confidence, 3),
            "scores": scores
        }

# Global singleton classifier node instance
nlp_classifier = DistilBertClassifier()
