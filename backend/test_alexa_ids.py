import os
import sys
import uuid
from pymongo import MongoClient
from dotenv import load_dotenv

# Get the current script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
# Add the parent directory to the Python path
sys.path.append(os.path.join(script_dir, '..'))

load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client.patient_data

def add_alexa_id():
    """Add test Alexa user ID to all patients who don't have one."""
    patients = db.patients.find({"alexa_user_id": {"$exists": False}})
    count = 0
    alexa_ids = []
    
    for patient in patients:
        # Generate a fake Alexa ID
        alexa_id = f"amzn1.ask.account.test.{uuid.uuid4().hex[:8]}"
        
        # Update the patient record
        result = db.patients.update_one(
            {"_id": patient["_id"]},
            {"$set": {"alexa_user_id": alexa_id}}
        )
        
        if result.modified_count > 0:
            count += 1
            print(f"Added Alexa ID to patient {patient.get('name', patient.get('id'))}: {alexa_id}")
            alexa_ids.append(alexa_id)
    
    print(f"Total patients updated: {count}")
    
    if alexa_ids:
        print("\nTest with these IDs:")
        for alexa_id in alexa_ids:
            print(f"- {alexa_id}")

if __name__ == "__main__":
    add_alexa_id()
