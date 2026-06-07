import os
import json
import pymongo
from dotenv import load_dotenv

def import_geo_data():
    # Resolve backend directory and load .env file
    db_dir = os.path.dirname(os.path.realpath(__file__))
    backend_dir = os.path.dirname(db_dir)
    env_path = os.path.join(backend_dir, ".env")
    
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"Loaded environment variables from: {env_path}")
    else:
        print("Warning: .env file not found, using default environment configurations.")

    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/aira_wellness")
    db_name = pymongo.uri_parser.parse_uri(mongo_uri).get("database") or "aira_wellness"
    
    # Path to Kaggle downloaded files
    dataset_dir = r"C:\Users\ajays\.cache\kagglehub\datasets\tanweerulhaque\countries-states-cities-dataset\versions\1\countries states cities database\JSON"
    
    countries_path = os.path.join(dataset_dir, "countries.json")
    states_path = os.path.join(dataset_dir, "states.json")
    cities_path = os.path.join(dataset_dir, "cities.json")
    
    # Verify files exist
    for path in [countries_path, states_path, cities_path]:
        if not os.path.exists(path):
            print(f"Error: Required dataset file not found at: {path}")
            return
            
    print(f"Connecting to MongoDB at: {mongo_uri}")
    try:
        client = pymongo.MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        client.server_info()
    except Exception as err:
        print(f"Failed to connect to MongoDB: {err}")
        return
        
    db = client[db_name]
    
    # 1. Import countries
    print("Reading countries.json...")
    with open(countries_path, "r", encoding="utf-8") as f:
        countries = json.load(f)
    print(f"Loaded {len(countries)} countries from JSON.")
    
    print("Seeding geo_countries collection...")
    db.geo_countries.delete_many({})
    if countries:
        db.geo_countries.insert_many(countries)
        print("Successfully seeded geo_countries collection.")
        
    # 2. Import states
    print("Reading states.json...")
    with open(states_path, "r", encoding="utf-8") as f:
        states = json.load(f)
    print(f"Loaded {len(states)} states from JSON.")
    
    print("Seeding geo_states collection...")
    db.geo_states.delete_many({})
    if states:
        db.geo_states.insert_many(states)
        print("Successfully seeded geo_states collection.")
        
    # 3. Import cities
    print("Reading cities.json...")
    with open(cities_path, "r", encoding="utf-8") as f:
        cities = json.load(f)
    print(f"Loaded {len(cities)} cities from JSON.")
    
    print("Seeding geo_cities collection (inserting in chunks)...")
    db.geo_cities.delete_many({})
    if cities:
        # Bulk insert in chunks to prevent memory/BSON payload issues
        chunk_size = 20000
        for i in range(0, len(cities), chunk_size):
            chunk = cities[i:i + chunk_size]
            db.geo_cities.insert_many(chunk)
            print(f"Seeded cities {i} to {min(i + chunk_size, len(cities))}")
        print("Successfully seeded geo_cities collection.")

    # 4. Set up Indexes
    print("Creating indexes on geo collections...")
    try:
        # Country indexes
        db.geo_countries.create_index("iso2", unique=True)
        db.geo_countries.create_index("name")
        
        # State indexes
        db.geo_states.create_index("country_code")
        db.geo_states.create_index([("country_code", 1), ("name", 1)])
        db.geo_states.create_index([("country_code", 1), ("state_code", 1)])
        
        # City indexes
        db.geo_cities.create_index([("country_code", 1), ("state_code", 1)])
        db.geo_cities.create_index([("country_code", 1), ("state_code", 1), ("name", 1)])
        db.geo_cities.create_index("state_id")
        db.geo_cities.create_index("name")
        print("Geolocation indexing completed successfully.")
    except Exception as idx_err:
        print(f"Error creating indexes: {idx_err}")
        
    print("Dataset import and database configuration completed successfully!")

if __name__ == "__main__":
    import_geo_data()
