import pickle
import numpy as np
import os
import logging
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)

def train_and_save_model():
    """Generates a representative dataset, fits StandardScaler and Ridge regression, and saves both."""
    try:
        logger.info("Initializing simulated ML Ridge Regression training sequence...")
        
        # 200 mock student profiles with representative ranges
        np.random.seed(42)
        n_samples = 200
        
        study_hours = np.random.uniform(0.0, 16.0, n_samples)
        sleep_hours = np.random.uniform(0.0, 14.0, n_samples)
        screen_time = np.random.uniform(0.0, 16.0, n_samples)
        academic_pressure = np.random.uniform(1.0, 10.0, n_samples)
        social_media = np.random.uniform(0.0, 10.0, n_samples)
        
        sleep_deficit = np.array([max(0.0, 8.0 - s) for s in sleep_hours])
        screen_excess = np.array([max(0.0, sc - 6.0) for sc in screen_time])
        
        study_satisfaction = np.random.uniform(1.0, 10.0, n_samples)
        # dietary_habits: 2 = Healthy, 1 = Moderate, 0 = Unhealthy
        dietary_habits = np.random.choice([0.0, 1.0, 2.0], size=n_samples, p=[0.2, 0.5, 0.3])
        financial_stress = np.random.uniform(1.0, 10.0, n_samples)
        # family_history: 1 = Yes, 0 = No
        family_history = np.random.choice([0.0, 1.0], size=n_samples, p=[0.7, 0.3])
        work_hours = np.random.uniform(0.0, 12.0, n_samples)
        
        X = np.column_stack([
            study_hours,
            sleep_hours,
            screen_time,
            academic_pressure,
            social_media,
            sleep_deficit,
            screen_excess,
            study_satisfaction,
            dietary_habits,
            financial_stress,
            family_history,
            work_hours
        ])
        
        # Wellness target formula (higher is better, range ~0-100)
        # Academic pressure reduces wellness (coef: -2.5)
        # Sleep deficit reduces wellness (coef: -2.0)
        # Screen excess reduces wellness (coef: -1.5)
        # Social media reduces wellness (coef: -1.0)
        # Sleep hours increases wellness (coef: +1.5)
        # Financial stress reduces wellness (coef: -2.5)
        # Study satisfaction increases wellness (coef: +2.0)
        # Dietary habits: Unhealthy/0.0 decreases wellness, Healthy/2.0 increases wellness
        # Family history: 1.0 decreases wellness
        # Work hours reduces wellness (coef: -1.5)
        y = 100.0 - (
            academic_pressure * 2.5 +
            sleep_deficit * 2.0 +
            screen_excess * 1.5 +
            social_media * 1.0 -
            sleep_hours * 1.5 +
            financial_stress * 2.5 -
            study_satisfaction * 2.0 +
            (2.0 - dietary_habits) * 2.5 +
            family_history * 5.0 +
            work_hours * 1.5
        )
        y = np.clip(y, 10, 100)
        
        # Fit scaler
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Fit Ridge Regression
        model = Ridge(alpha=1.0)
        model.fit(X_scaled, y)
        
        logger.info(f"Ridge Regression model trained successfully. Coefficients: {model.coef_}")
        
        # Ensure directories exist
        os.makedirs("backend/ml", exist_ok=True)
        os.makedirs("ml", exist_ok=True)
        
        # Save scaler
        scaler_path = "backend/ml/saved_scaler.pkl"
        with open(scaler_path, "wb") as f:
            pickle.dump(scaler, f)
        logger.info(f"StandardScaler successfully saved at: {scaler_path}")
        
        # Also write to ml/saved_scaler.pkl for compatibility with relative working dir
        with open("ml/saved_scaler.pkl", "wb") as f:
            pickle.dump(scaler, f)
            
        # Save model pickle
        model_path = "backend/ml/saved_model.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(model, f)
        logger.info(f"Pickle weights successfully compiled at: {model_path}")
        
        with open("ml/saved_model.pkl", "wb") as f:
            pickle.dump(model, f)
            
    except Exception as e:
        logger.error(f"Failed to execute training pipelines: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train_and_save_model()
