import os
import time
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client.patient_data

def test_auto_update():
    # Create a test patient without an Alexa ID
    print("Creating test patient...")
    result = db.patients.insert_one({
        "name": f"Test Patient - {datetime.utcnow().isoformat()}",
        "created_at": datetime.utcnow()
    })
    
    patient_id = result.inserted_id
    print(f"Created test patient with ID: {patient_id}")
    
    # Wait for background task to run (typically 15-20 seconds)
    print("Waiting for background task to run (20 seconds)...")
    time.sleep(20)
    
    # Check if Alexa ID was assigned
    updated_patient = db.patients.find_one({"_id": patient_id})
    
    if updated_patient and "alexa_user_id" in updated_patient and updated_patient["alexa_user_id"]:
        print(f"✅ SUCCESS: Alexa ID assigned: {updated_patient['alexa_user_id']}")
        
        # Check for log entry
        log_entry = db.alexa_id_logs.find_one({"patient_id": str(patient_id)})
        if log_entry:
            print(f"✅ SUCCESS: Log entry created at {log_entry.get('created_at')}")
        else:
            print("❌ FAILED: No log entry created")
    else:
        print("❌ FAILED: No Alexa ID assigned after waiting")
    
    # Ask if we should clean up
    clean = input("Clean up test patient? (y/n): ").lower() == 'y'
    if clean:
        db.patients.delete_one({"_id": patient_id})
        db.alexa_id_logs.delete_many({"patient_id": str(patient_id)})
        print(f"✅ Test patient with ID {patient_id} removed from database")

if __name__ == "__main__":
    test_auto_update() 