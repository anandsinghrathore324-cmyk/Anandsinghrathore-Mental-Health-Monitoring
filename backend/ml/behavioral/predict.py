import pandas as pd
import numpy as np
import pickle
import joblib

# File paths
MODEL_PATH = "models/risk_model.pkl"
PREPROCESSOR_PATH = "preprocessed/preprocessor.joblib"

# Define the expected feature order (must match preprocess.py)
FEATURE_COLUMNS = [
    "Age",
    "Gender",
    "Academic Pressure",
    "Study Satisfaction",
    "Sleep Duration",
    "Dietary Habits",
    "Work/Study Hours",
    "Financial Stress",
    "Family History of Mental Illness"
]

def load_prediction_assets():
    """Loads the trained model and preprocessing pipeline assets."""
    try:
        model = joblib.load(MODEL_PATH)
    except Exception:
        # Fallback to pickle if joblib fails
        with open(MODEL_PATH, "rb") as f:
            model = pickle.load(f)
            
    preprocessor = joblib.load(PREPROCESSOR_PATH)
    return model, preprocessor

def predict_depression(input_data):
    """
    Accepts user input data and returns the depression prediction and probability score.
    
    Parameters:
    input_data (dict or pd.DataFrame): Input features for one or more students.
        Expected keys/columns:
        - Age (numeric)
        - Gender (string: 'Male', 'Female')
        - Academic Pressure (numeric: 0.0 - 5.0)
        - Study Satisfaction (numeric: 0.0 - 5.0)
        - Sleep Duration (string: 'Less than 5 hours', '5-6 hours', '7-8 hours', 'More than 8 hours', 'Others')
        - Dietary Habits (string: 'Healthy', 'Moderate', 'Unhealthy', 'Others')
        - Work/Study Hours (numeric)
        - Financial Stress (numeric: 1.0 - 5.0)
        - Family History of Mental Illness (string: 'Yes', 'No')
    
    Returns:
    predictions (list): List of predictions ('Depressed' or 'Not Depressed')
    probabilities (list): List of probability scores (float)
    """
    model, preprocessor = load_prediction_assets()
    
    # Convert dictionary to DataFrame if necessary
    if isinstance(input_data, dict):
        df_input = pd.DataFrame([input_data])
    elif isinstance(input_data, list):
        df_input = pd.DataFrame(input_data)
    else:
        df_input = input_data.copy()
        
    # Ensure correct column order
    df_input = df_input[FEATURE_COLUMNS]
    
    # Preprocess the input
    X_preprocessed = preprocessor.transform(df_input)
    
    # Get feature names from preprocessor to align with model's expected feature names
    try:
        numeric_features = ["Age", "Academic Pressure", "Study Satisfaction", "Work/Study Hours", "Financial Stress"]
        cat_encoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
        categorical_features = ["Gender", "Sleep Duration", "Dietary Habits", "Family History of Mental Illness"]
        encoded_cat_names = cat_encoder.get_feature_names_out(categorical_features).tolist()
        all_feature_names = numeric_features + encoded_cat_names
        X_preprocessed_df = pd.DataFrame(X_preprocessed, columns=all_feature_names)
    except Exception:
        # Fallback to raw numpy array if names retrieval fails
        X_preprocessed_df = X_preprocessed
        
    # Get predictions and probabilities
    preds = model.predict(X_preprocessed_df)
    probs = model.predict_proba(X_preprocessed_df)[:, 1]
    
    # Map raw 0/1 predictions to human-readable strings
    prediction_labels = ["Depressed" if p == 1 else "Not Depressed" for p in preds]
    
    return prediction_labels, probs.tolist()

if __name__ == "__main__":
    # Define 3 sample test cases
    sample_test_cases = [
        {
            "Age": 20.0,
            "Gender": "Female",
            "Academic Pressure": 5.0,
            "Study Satisfaction": 1.0,
            "Sleep Duration": "Less than 5 hours",
            "Dietary Habits": "Unhealthy",
            "Work/Study Hours": 10.0,
            "Financial Stress": 5.0,
            "Family History of Mental Illness": "Yes"
        },
        {
            "Age": 22.0,
            "Gender": "Male",
            "Academic Pressure": 1.0,
            "Study Satisfaction": 5.0,
            "Sleep Duration": "7-8 hours",
            "Dietary Habits": "Healthy",
            "Work/Study Hours": 4.0,
            "Financial Stress": 1.0,
            "Family History of Mental Illness": "No"
        },
        {
            "Age": 28.0,
            "Gender": "Female",
            "Academic Pressure": 3.0,
            "Study Satisfaction": 3.0,
            "Sleep Duration": "5-6 hours",
            "Dietary Habits": "Moderate",
            "Work/Study Hours": 6.0,
            "Financial Stress": 3.0,
            "Family History of Mental Illness": "No"
        }
    ]
    
    print("--- Running Predictor with Sample Test Cases ---")
    predictions, probabilities = predict_depression(sample_test_cases)
    
    for i, (case, pred, prob) in enumerate(zip(sample_test_cases, predictions, probabilities)):
        print(f"\nTest Case {i+1}:")
        print(f"  Inputs: Age={case['Age']}, Gender={case['Gender']}, Academic Pressure={case['Academic Pressure']}, Study Satisfaction={case['Study Satisfaction']}, Sleep={case['Sleep Duration']}, Diet={case['Dietary Habits']}, Study Hours={case['Work/Study Hours']}, Financial Stress={case['Financial Stress']}, Family History={case['Family History of Mental Illness']}")
        print(f"  Result: {pred}")
        print(f"  Depression Probability Score: {prob:.4f}")
