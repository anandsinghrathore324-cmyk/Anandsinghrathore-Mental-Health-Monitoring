import os
import re
import sys
import pickle

def clean_text(text):
    if not isinstance(text, str):
        return ""
    # 1. Lowercase
    text = text.lower()
    # 2. Remove URLs
    text = re.sub(r'https?://\S+|www\.\S+', '', text)
    # 3. Remove special characters
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # 4. Remove extra spaces
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def get_risk_level(prob):
    if prob < 0.35:
        return "Low"
    elif prob < 0.65:
        return "Medium"
    elif prob < 0.85:
        return "High"
    else:
        return "Critical"

class MentalHealthTextPredictor:
    def __init__(self, model_path="text_model.pkl", vectorizer_path="text_vectorizer.pkl"):
        if not os.path.exists(model_path) or not os.path.exists(vectorizer_path):
            raise FileNotFoundError("Model or vectorizer file not found. Ensure you ran training first.")
            
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)
            
        with open(vectorizer_path, "rb") as f:
            self.vectorizer = pickle.load(f)

    def predict(self, text):
        cleaned = clean_text(text)
        features = self.vectorizer.transform([cleaned])
        
        # Logistic Regression outputs class probabilities
        # Class 1 corresponds to "mental health indicator"
        probabilities = self.model.predict_proba(features)[0]
        prob_score = probabilities[1]
        
        prediction = int(self.model.predict(features)[0])
        risk_level = get_risk_level(prob_score)
        
        return {
            "prediction": prediction,
            "probability_score": prob_score,
            "risk_level": risk_level
        }

def run_demo():
    print("==================================================")
    print("Mental Health Text Predictor - 5 Sample Test Cases")
    print("==================================================")
    
    test_cases = [
        "I am happy and excited about my future.",
        "Today I went to the park and read a book under a tree.",
        "I'm feeling a bit anxious and stressed about my upcoming exams, but I think I will manage.",
        "I feel lonely and exhausted. Everything seems so overwhelming lately.",
        "nothing look forward life i dont have any reasons to keep going i feel like nothing keeps going next day makes want to end it all"
    ]
    
    predictor = MentalHealthTextPredictor()
    
    for i, test_text in enumerate(test_cases, 1):
        res = predictor.predict(test_text)
        print(f"\nTest Case {i}:")
        print(f"  Input Text : \"{test_text}\"")
        print(f"  Prediction : {res['prediction']} ({'Mental Health Risk' if res['prediction'] == 1 else 'Control/Neutral'})")
        print(f"  Probability: {res['probability_score']:.4f}")
        print(f"  Risk Level : {res['risk_level']}")
    print("\n==================================================")

if __name__ == "__main__":
    # If run with command line argument, predict the input argument
    if len(sys.argv) > 1:
        input_text = sys.argv[1]
        try:
            predictor = MentalHealthTextPredictor()
            res = predictor.predict(input_text)
            print(f"Input Text : \"{input_text}\"")
            print(f"Prediction : {res['prediction']}")
            print(f"Probability: {res['probability_score']:.4f}")
            print(f"Risk Level : {res['risk_level']}")
        except Exception as e:
            print("Error during prediction:", e)
    else:
        run_demo()
