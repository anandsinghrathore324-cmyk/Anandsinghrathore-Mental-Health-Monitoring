import os
import pickle
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
print("Current dir:", current_dir)
model_path = os.path.join(current_dir, "ml", "saved_model.pkl")
print("Model path:", model_path)
print("Model path exists:", os.path.exists(model_path))

try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    print("Model loaded successfully:", model)
    print("Coefficients:", model.coef_)
except Exception as e:
    print("Error loading model:", e)
