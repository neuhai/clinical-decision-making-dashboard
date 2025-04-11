import json
import os
import sys
from pymongo import MongoClient
from dotenv import load_dotenv

# Get the parent directory
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
# Add the parent directory to sys.path
sys.path.insert(0, parent_dir)

# Load environment variables from .env file
load_dotenv(os.path.join(parent_dir, '.env'))

def seed_database():
    """Import patient data from JSON file to MongoDB."""
    # Get MongoDB URI from environment variables
    mongo_uri = os.getenv('MONGO_URI')
    if not mongo_uri:
        print("Error: MONGO_URI not found in environment variables.")
        return False
    
    # Connect to MongoDB
    try:
        client = MongoClient(mongo_uri)
        db = client.patient_data
        print("✅ Connected to MongoDB")
        
        # Test the connection
        client.admin.command('ping')
        print("✅ MongoDB server is available")
        
        # Find the patients.json file
        json_path = '../../src/assets/patients.json'
        abs_json_path = os.path.abspath(os.path.join(script_dir, json_path))
        
        # Read the patients.json file
        try:
            with open(abs_json_path, 'r') as f:
                patients_data = json.load(f)
                print(f"✅ Loaded patient data from {abs_json_path}")
        except Exception as e:
            print(f"Error reading patients.json: {e}")
            return False
        
        # Check if patients collection exists
        if 'patients' in db.list_collection_names():
            # Drop the existing collection
            db.patients.drop()
            print("✅ Dropped existing patients collection")
        
        # Insert data into patients collection
        result = db.patients.insert_many(patients_data)
        print(f"✅ Inserted {len(result.inserted_ids)} patient records into database")
        
        # Create indexes for faster queries
        db.patients.create_index("id")
        print("✅ Created index on patient id field")
        
        # Log the inserted data
        print("\nDatabase now contains:")
        for patient in db.patients.find():
            print(f"  - Patient: {patient['name']} (ID: {patient['id']})")
        
        return True
        
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return False
    finally:
        if 'client' in locals():
            client.close()
            print("✅ Database connection closed")

if __name__ == "__main__":
    print("Starting database seeding process...")
    success = seed_database()
    if success:
        print("\n✅ Database seeding completed successfully!")
    else:
        print("\n❌ Database seeding failed.")
