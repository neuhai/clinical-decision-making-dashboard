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

def add_alexa_ids():
    """Add test Alexa user ID to all patients who don't have one."""
    patients = list(db.patients.find({}))
    count = 0
    alexa_ids = []
    
    print(f"Found {len(patients)} patients in database")
    
    for patient in patients:
        patient_id = patient.get('id', str(patient.get('_id')))
        patient_name = patient.get('name', f"Patient {patient_id}")
        
        # Skip if already has alexa_user_id
        if patient.get('alexa_user_id'):
            print(f"Patient {patient_name} already has Alexa ID: {patient['alexa_user_id']}")
            alexa_ids.append((patient_name, patient['alexa_user_id']))
            continue
        
        # Generate a fake Alexa ID
        alexa_id = f"amzn1.ask.account.test.{uuid.uuid4().hex[:8]}"
        
        # Update the patient record
        result = db.patients.update_one(
            {"_id": patient["_id"]},
            {"$set": {"alexa_user_id": alexa_id}}
        )
        
        if result.modified_count > 0:
            count += 1
            print(f"Added Alexa ID to patient {patient_name}: {alexa_id}")
            alexa_ids.append((patient_name, alexa_id))
    
    print(f"\nTotal patients updated: {count}")
    
    if alexa_ids:
        print("\nAvailable Test IDs:")
        for name, alexa_id in alexa_ids:
            print(f"- {name}: {alexa_id}")

if __name__ == "__main__":
    add_alexa_ids() 