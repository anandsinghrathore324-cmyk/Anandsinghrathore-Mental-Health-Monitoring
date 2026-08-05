import os
import json
import logging
from database.db import db_manager

logger = logging.getLogger(__name__)

class HotlineModel:
    """Manages country-specific mental health hotlines in the database."""
    
    @staticmethod
    def get_hotline_by_iso2(iso2_code: str) -> dict:
        """Retrieves hotline contact details for a given ISO2 country code."""
        try:
            doc = db_manager.db.mental_health_hotlines.find_one({"iso2": iso2_code.strip().upper()})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception as e:
            logger.error(f"Error querying hotline for ISO2 code {iso2_code}: {str(e)}")
            return None

    @staticmethod
    def seed_hotlines():
        """Seeds the hotlines database from the JSON dataset if empty."""
        try:
            if db_manager.db.mental_health_hotlines.count_documents({}) == 0:
                # Load JSON data from seeds directory
                dir_path = os.path.dirname(os.path.realpath(__file__))
                json_path = os.path.join(dir_path, "seeds", "mental_health_hotlines.json")
                if not os.path.exists(json_path):
                    json_path = os.path.join(dir_path, "mental_health_hotlines.json")
                if os.path.exists(json_path):
                    with open(json_path, "r", encoding="utf-8") as f:
                        hotlines_list = json.load(f)
                    db_manager.db.mental_health_hotlines.insert_many(hotlines_list)
                    logger.info(f"Successfully seeded {len(hotlines_list)} mental health hotlines.")
                else:
                    logger.error(f"JSON data not found at {json_path}")
        except Exception as e:
            logger.error(f"Failed to seed mental health hotlines: {str(e)}")
