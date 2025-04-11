import time
import logging
import threading
import schedule
from datetime import datetime
import uuid
import os
from flask import current_app
from pymongo import MongoClient
from bson import ObjectId

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    """Get a MongoDB connection, either from current_app or create a new one"""
    try:
        if current_app and hasattr(current_app, 'db'):
            return current_app.db
        else:
            # Fallback if outside application context
            from dotenv import load_dotenv
            load_dotenv()
            client = MongoClient(os.getenv("MONGO_URI"))
            return client.patient_data
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise

def sync_alexa_ids():
    """
    Check for patients without Alexa IDs and assign them.
    Returns list of newly assigned IDs.
    """
    try:
        db = get_db_connection()
        
        # Find patients without Alexa IDs
        patients = list(db.patients.find({"alexa_user_id": {"$exists": False}}))
        
        # Also find patients with empty Alexa IDs
        patients_empty_id = list(db.patients.find({"alexa_user_id": ""}))
        
        # Combine both lists
        patients.extend(patients_empty_id)
        
        if not patients:
            logger.info("No patients found without Alexa user IDs")
            return []
        
        logger.info(f"Found {len(patients)} patients without Alexa user IDs")
        new_alexa_ids = []
        
        for patient in patients:
            # Generate a new Alexa ID
            alexa_id = f"amzn1.ask.account.auto.{uuid.uuid4().hex[:8]}"
            
            # Update the patient record
            result = db.patients.update_one(
                {"_id": patient["_id"]},
                {
                    "$set": {
                        "alexa_user_id": alexa_id,
                        "alexa_id_added_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                patient_name = patient.get('name', f"Patient {str(patient['_id'])}")
                logger.info(f"Added Alexa ID to patient {patient_name}: {alexa_id}")
                
                # Create a log of this assignment
                db.alexa_id_logs.insert_one({
                    "patient_id": str(patient["_id"]),
                    "alexa_user_id": alexa_id,
                    "created_at": datetime.utcnow()
                })
                
                new_alexa_ids.append({
                    "patient_id": str(patient["_id"]),
                    "patient_name": patient_name,
                    "alexa_id": alexa_id
                })
        
        return new_alexa_ids
    
    except Exception as e:
        logger.error(f"Error during Alexa ID sync: {str(e)}")
        return []

def update_database():
    """Main database update function that runs periodically"""
    logger.info(f"Database update check started at {datetime.now()}")
    
    try:
        # Sync Alexa IDs
        new_alexa_ids = sync_alexa_ids()
        
        if new_alexa_ids:
            logger.info(f"Database updated with {len(new_alexa_ids)} new Alexa IDs")
        else:
            logger.info("No database updates required")
    except Exception as e:
        logger.error(f"Error in database update: {str(e)}")

def run_scheduler():
    """Run the scheduler continuously"""
    # Initial run on startup
    update_database()
    
    # Schedule regular updates (every 15 seconds in this case)
    schedule.every(15).seconds.do(update_database)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

def start_background_tasks():
    """Start background tasks in a separate thread"""
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    logger.info("Background database update scheduler started") 