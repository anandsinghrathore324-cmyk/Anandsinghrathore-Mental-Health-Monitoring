import pymongo
import logging
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Production-grade MongoDB client connection and index setup manager."""
    
    def __init__(self):
        self.client = None
        self.db = None

    def connect(self, uri: str = None):
        """Establishes connection to MongoDB database instance."""
        connection_uri = uri or Config.MONGO_URI
        try:
            logger.info("Initializing connection to MongoDB secured node...")
            self.client = pymongo.MongoClient(connection_uri, serverSelectionTimeoutMS=2000)
            # Fetch default DB from URI or use aira_wellness
            db_name = pymongo.uri_parser.parse_uri(connection_uri).get("database") or "aira_wellness"
            self.db = self.client[db_name]
            # Trigger server connection check
            self.client.server_info()
            logger.info(f"Successfully connected to MongoDB database: {db_name}")
            self.setup_indexes()
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB instance: {str(e)}")
            if Config.IS_PRODUCTION:
                logger.critical("PRODUCTION FATAL: Cannot connect to MongoDB cluster in production environment. Halting.")
                raise e
            logger.warning("DEVELOPMENT: Local MongoDB unreachable. Deploying in-memory mongomock fallback for local testing...")
            try:
                import mongomock
                self.client = mongomock.MongoClient()
                self.db = self.client["aira_wellness"]
                logger.info("In-memory mongomock development database initialized successfully.")
                self.setup_indexes()
            except Exception as mock_err:
                logger.critical(f"Failed to initialize mongomock fallback: {str(mock_err)}")
                raise e

    def setup_indexes(self):
        """Applies essential indexing patterns to database collections."""
        try:
            logger.info("Applying unique constraints and collection indexes...")
            # Users Unique Indexes
            self.db.users.create_index("email", unique=True)
            
            # Reports Indexes
            self.db.mental_health_reports.create_index("user_id")
            self.db.mental_health_reports.create_index("created_at")
            
            # Chatbot Indexes
            self.db.chatbot_history.create_index("user_id")
            self.db.chatbot_history.create_index("timestamp")
            
            # Mood Logs Indexes
            self.db.mood_logs.create_index("user_id")
            self.db.mood_logs.create_index([("user_id", 1), ("date", 1)], unique=True)
            
            # Geolocation Doctor Indexes
            self.db.doctor_recommendations.create_index([("latitude", 1), ("longitude", 1)])
            self.db.doctor_recommendations.create_index("specialization")

            # OTP Codes Indexes with automatic 5-minute (300s) MongoDB TTL expiry
            self.db.otp_codes.create_index("created_at", expireAfterSeconds=300)
            self.db.otp_codes.create_index("email")
            
            # Geo Location Indexes
            self.db.geo_countries.create_index("iso2", unique=True)
            self.db.geo_countries.create_index("name")
            self.db.geo_states.create_index("country_code")
            self.db.geo_states.create_index([("country_code", 1), ("name", 1)])
            self.db.geo_states.create_index([("country_code", 1), ("state_code", 1)])
            self.db.geo_cities.create_index([("country_code", 1), ("state_code", 1)])
            self.db.geo_cities.create_index([("country_code", 1), ("state_code", 1), ("name", 1)])
            self.db.geo_cities.create_index("state_id")
            self.db.geo_cities.create_index("name")
            
            logger.info("MongoDB indexing completed successfully.")
        except Exception as e:
            logger.warning(f"Indexes deployment failed or already existed: {str(e)}")

# Global database manager instance
db_manager = DatabaseManager()
