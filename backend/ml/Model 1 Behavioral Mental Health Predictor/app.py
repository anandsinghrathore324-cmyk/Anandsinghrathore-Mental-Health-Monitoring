from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

# Ensure Flask and Flask-CORS are installed
try:
    from flask import Flask
    from flask_cors import CORS
except ImportError:
    print("Flask or Flask-CORS not found. Attempting to install...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask", "flask-cors"])
    from flask import Flask, request, jsonify
    from flask_cors import CORS

from predict import predict_depression

app = Flask(__name__)
# Enable CORS for all routes to facilitate frontend integration
CORS(app)

def get_risk_level(prob):
    """
    Categorizes the depression risk level based on the probability score.
    - Low: probability < 0.15 (NPV of 91.39%)
    - Medium: 0.15 <= probability <= 0.80
    - High: probability > 0.80 (PPV of 90.72%)
    """
    if prob < 0.15:
        return "Low"
    elif prob <= 0.80:
        return "Medium"
    else:
        return "High"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get JSON input from request
        data = request.get_json()
        if not data:
            return jsonify({"error": "No input data provided"}), 400
            
        # If it's a single dict, convert to list or just predict directly
        # The predict_depression function handles dict, list of dicts, or DataFrame
        predictions, probabilities = predict_depression(data)
        
        # Determine prediction details (assuming single prediction for request)
        if isinstance(data, dict):
            prediction = predictions[0]
            probability = probabilities[0]
            risk_level = get_risk_level(probability)
            
            response = {
                "prediction": prediction,
                "probability": round(probability, 4),
                "risk_level": risk_level
            }
        else:
            # Handle list of dicts (batch predictions)
            response = []
            for pred, prob in zip(predictions, probabilities):
                response.append({
                    "prediction": pred,
                    "probability": round(prob, 4),
                    "risk_level": get_risk_level(prob)
                })
                
        return jsonify(response), 200

    except KeyError as e:
        return jsonify({"error": f"Missing required feature field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"An error occurred during prediction: {str(e)}"}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "message": "Prediction service is up and running"}), 200

if __name__ == '__main__':
    # Run server locally on port 5000
    print("Starting Flask prediction backend server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
