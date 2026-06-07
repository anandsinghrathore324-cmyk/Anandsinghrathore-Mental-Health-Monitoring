import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

class MLPreprocessor:
    """Pre-processing engine for demographic variables and academic pressures."""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.fitted = False

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
        
        features_array = np.array([
            study_hours,
            sleep_hours,
            screen_time,
            academic_pressure,
            social_media,
            sleep_deficit,
            screen_excess
        ]).reshape(1, -1)
        
        return features_array
