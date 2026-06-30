import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from text_predict import MentalHealthTextPredictor

app = Flask(__name__)
# Enable CORS support
CORS(app)

# Initialize predictor
predictor = None
try:
    predictor = MentalHealthTextPredictor(
        model_path="text_model.pkl",
        vectorizer_path="text_vectorizer.pkl"
    )
    print("Model and vectorizer loaded successfully.")
except Exception as e:
    print(f"CRITICAL: Failed to load model or vectorizer: {e}")

@app.route('/health', methods=['GET'])
def health():
    if predictor is None:
        return jsonify({
            "status": "unhealthy",
            "error": "Model files could not be loaded."
        }), 500
    return jsonify({
        "status": "healthy"
    }), 200

@app.route('/text-predict', methods=['POST'])
def predict():
    if predictor is None:
        return jsonify({
            "error": "Model predictor not initialized."
        }), 500
        
    # Error Handling for JSON parsing
    try:
        data = request.get_json()
    except Exception:
        return jsonify({
            "error": "Malformed JSON request."
        }), 400
        
    # Error Handling for missing parameter
    if not data or 'text' not in data:
        return jsonify({
            "error": "Missing required parameter 'text' in request body."
        }), 400
        
    text = data['text']
    
    # Error Handling for invalid type
    if not isinstance(text, str):
        return jsonify({
            "error": "Parameter 'text' must be a string."
        }), 400
        
    # Error Handling for empty content
    if not text.strip():
        return jsonify({
            "error": "Parameter 'text' cannot be empty or only spaces."
        }), 400
        
    try:
        res = predictor.predict(text)
        
        # Map binary label prediction to string:
        # 1 -> Mental Health Risk
        # 0 -> Control/Neutral
        label_str = "Mental Health Risk" if res['prediction'] == 1 else "Control/Neutral"
        
        return jsonify({
            "prediction": label_str,
            "probability": round(res['probability_score'], 4),
            "risk_level": res['risk_level']
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": f"Prediction failed: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Run on port 5002
    app.run(host='0.0.0.0', port=5002, debug=False)
