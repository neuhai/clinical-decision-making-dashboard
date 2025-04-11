import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

client = MongoClient(os.getenv("MONGO_URI"))
db = client.patient_data

def load_initial_data():
    """Load patient data into MongoDB."""
    with open("../../frontend/src/assets/patients.json", "r") as file:
        patients = json.load(file)
        db.patients.insert_many(patients)
        print("✅ Patient data imported successfully.")

def clear_db():
    """Clear the database."""
    db.patients.delete_many({})
    print("✅ Database cleared.")

if __name__ == "__main__":
    load_initial_data()

