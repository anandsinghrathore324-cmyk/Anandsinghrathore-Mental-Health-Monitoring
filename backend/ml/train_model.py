import pickle
import numpy as np
import logging
from sklearn.linear_model import Ridge
from ml.preprocess import MLPreprocessor

logger = logging.getLogger(__name__)

def train_and_save_model():
    """Simulates training of a Ridge Regression index classifier and pickle-saves weights."""
    try:
        logger.info("Initializing simulated ML Ridge Regression training sequence...")
        
        # 100 mock student profiles
        np.random.seed(42)
        X_mock = np.random.rand(100, 7) * 10
        # Target Wellness index scores
        y_mock = 100 - (X_mock[:, 3] * 4 + X_mock[:, 5] * 3 - X_mock[:, 1] * 2)
        y_mock = np.clip(y_mock, 10, 100)
        
        model = Ridge(alpha=1.0)
        model.fit(X_mock, y_mock)
        
        logger.info(" Ridge Regression model trained successfully.")
        
        # Save model pickle
        with open("ml/saved_model.pkl", "wb") as f:
            pickle.dump(model, f)
            
        logger.info("Pickle weights successfully compiled at: ml/saved_model.pkl")
    except Exception as e:
        logger.error(f"Failed to execute training pipelines: {str(e)}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    train_and_save_model()
