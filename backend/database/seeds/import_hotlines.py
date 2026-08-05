import os
import json
import pymongo
from dotenv import load_dotenv

def import_hotlines():
    # Resolve the path to backend/.env and load it
    seeds_dir = os.path.dirname(os.path.realpath(__file__))
    backend_dir = os.path.dirname(os.path.dirname(seeds_dir))
    env_path = os.path.join(backend_dir, ".env")
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded environment variables from: {env_path}")
    else:
        print("Warning: .env file not found, using default environment configurations.")

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/aira_wellness")
    json_path = os.path.join(db_dir, "mental_health_hotlines.json")
    
    if not os.path.exists(json_path):
        print(f"Error: Dataset not found at {json_path}")
        return
        
    with open(json_path, "r", encoding="utf-8") as f:
        hotlines = json.load(f)
        
    print(f"Connecting to MongoDB instance at: {mongo_uri}")
    try:
        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        # Verify connection
        client.server_info()
    except Exception as err:
        print(f"Error connecting to MongoDB: {err}")
        return
    
    db_name = pymongo.uri_parser.parse_uri(mongo_uri).get("database") or "aira_wellness"
    db = client[db_name]
    collection = db["mental_health_hotlines"]
    
    print("Clearing existing mental health hotlines database records...")
    collection.delete_many({})
    
    print(f"Importing {len(hotlines)} verified mental health hotlines...")
    result = collection.insert_many(hotlines)
    
    print(f"Import completed successfully! Loaded {len(result.inserted_ids)} records into {db_name}.mental_health_hotlines.")

if __name__ == "__main__":
    import_hotlines()
