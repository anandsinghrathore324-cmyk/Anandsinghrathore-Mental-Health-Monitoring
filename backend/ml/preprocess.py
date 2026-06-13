import os
import pickle
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class MLPreprocessor:
    """Pre-processing engine for demographic variables and academic pressures."""
    
    def __init__(self):
        self.scaler = None
        # Load pre-fitted scaler from file
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            scaler_path = os.path.join(current_dir, "saved_scaler.pkl")
            if os.path.exists(scaler_path):
                with open(scaler_path, "rb") as f:
                    self.scaler = pickle.load(f)
            else:
                # Fallback to local project path if running from parent dir
                fallback_path = os.path.join("ml", "saved_scaler.pkl")
                if os.path.exists(fallback_path):
                    with open(fallback_path, "rb") as f:
                        self.scaler = pickle.load(f)
        except Exception as e:
            pass
            
        if self.scaler is None:
            self.scaler = StandardScaler()

    def calculate_sleep_deficit(self, sleep_hours: float) -> float:
        """Returns the sleep deficit calculation against ideal 8 hours."""
        return max(0.0, 8.0 - float(sleep_hours))

    def calculate_screen_excess(self, screen_time: float) -> float:
        """Returns screen time exposure index excess compared to 6-hour baseline."""
        return max(0.0, float(screen_time) - 6.0)

    def extract_features(self, data: dict) -> np.ndarray:
        """Transforms client forms inputs into structured demographic arrays."""
        study_hours = float(data.get("study_hours", 6.0))
        sleep_hours = float(data.get("sleep_hours", 7.0))
        screen_time = float(data.get("screen_time", 5.0))
        academic_pressure = float(data.get("academic_pressure", 5.0))
        social_media = float(data.get("social_media_usage", 4.0))
        
        sleep_deficit = self.calculate_sleep_deficit(sleep_hours)
        screen_excess = self.calculate_screen_excess(screen_time)
        
        study_satisfaction = float(data.get("study_satisfaction", 5.0))
        dietary_habits = data.get("dietary_habits", "Moderate")
        dietary_val = 2.0 if dietary_habits == "Healthy" else (1.0 if dietary_habits == "Moderate" else 0.0)
        financial_stress = float(data.get("financial_stress", 5.0))
        family_history = data.get("family_history", "No")
        family_val = 1.0 if family_history == "Yes" else 0.0
        work_hours = float(data.get("work_hours", 0.0))
        
        features_array = np.array([
            study_hours,
            sleep_hours,
            screen_time,
            academic_pressure,
            social_media,
            sleep_deficit,
            screen_excess,
            study_satisfaction,
            dietary_val,
            financial_stress,
            family_val,
            work_hours
        ]).reshape(1, -1)
        
        if self.scaler:
            try:
                # Transform using the pre-fitted scaler
                features_array = self.scaler.transform(features_array)
            except Exception as e:
                # Fallback to raw features if transform fails (e.g. if not fitted)
                pass
                
        return features_array
