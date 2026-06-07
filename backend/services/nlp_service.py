from nlp.distilbert import nlp_classifier

class NlpService:
    """Production NLP sentiment analyzer service wrapping the DistilBERT model."""
    
    @staticmethod
    def analyze_diary_entry(text: str) -> dict:
        """Invokes singleton classifier model and returns clean sentiment outputs."""
        return nlp_classifier.analyze_sentiment(text)
