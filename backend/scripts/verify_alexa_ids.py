import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client.patient_data

def verify_alexa_ids():
    """Verify alexa_user_id for all patients."""
    patients = list(db.patients.find({}))
    
    print(f"Found {len(patients)} patients in database")
    
    has_alexa_id = 0
    missing_alexa_id = 0
    
    for patient in patients:
        patient_id = patient.get('id', str(patient.get('_id')))
        patient_name = patient.get('name', f"Patient {patient_id}")
        
        if patient.get('alexa_user_id'):
            has_alexa_id += 1
            print(f"✅ {patient_name} has Alexa ID: {patient['alexa_user_id']}")
        else:
            missing_alexa_id += 1
            print(f"❌ {patient_name} is missing an Alexa ID")
    
    print(f"\nSummary:")
    print(f"- Patients with Alexa ID: {has_alexa_id}")
    print(f"- Patients missing Alexa ID: {missing_alexa_id}")

if __name__ == "__main__":
    verify_alexa_ids() 