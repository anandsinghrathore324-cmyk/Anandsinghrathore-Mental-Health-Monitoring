import os
from dotenv import load_dotenv

# Load environment variables from backend/.env explicitly, falling back to default cwd loading
base_dir = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(base_dir, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()

class Config:
    """Production-grade configuration settings utilizing environment variables."""
    
    # Flask Secrets & Security Configurations
    SECRET_KEY = os.getenv("SECRET_KEY", "aira-super-secret-quantum-key-2026")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "aira-super-secret-jwt-signature-key-2026")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))
    
    # MongoDB Connection Config
    MONGO_URI = os.getenv("MONGO_URI")
    IS_PRODUCTION = os.getenv("RENDER") == "true" or os.getenv("FLASK_ENV") == "production"

    if IS_PRODUCTION:
        if not MONGO_URI:
            raise ValueError("MONGO_URI environment variable is missing in production environment (Render)!")
        if "localhost" in MONGO_URI or "127.0.0.1" in MONGO_URI:
            raise ValueError("MONGO_URI cannot point to localhost/127.0.0.1 in production environment (Render)!")
    else:
        if not MONGO_URI:
            MONGO_URI = "mongodb://localhost:27017/aira_wellness"
    
    # Logging Configurations
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_PATH = os.getenv("LOG_FILE_PATH", "logs/backend.log")

    # Geolocation / Haversine Defaults
    EARTH_RADIUS_KM = 6371.0

    # Gmail SMTP Configurations
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SMTP_EMAIL = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
