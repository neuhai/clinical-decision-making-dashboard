import requests
import os
import json
import time
import argparse
from dotenv import load_dotenv

load_dotenv()

# Parse command line arguments
parser = argparse.ArgumentParser(description='Test Alexa symptom tracking')
parser.add_argument('--port', type=int, default=5002, help='Port the Flask server is running on')
args = parser.parse_args()

BASE_URL = f"http://localhost:{args.port}"
API_KEY = os.getenv("ALEXA_API_KEY")

if not API_KEY:
    print("❌ Error: ALEXA_API_KEY environment variable not set.")
    exit(1)

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

print(f"Using API key: {API_KEY}")
print(f"Testing against server at {BASE_URL}")

def get_test_alexa_user_id():
    """Get a test Alexa user ID from the environment or database."""
    # Try to get from env var first
    alexa_id = os.getenv("TEST_ALEXA_USER_ID")
    if alexa_id:
        return alexa_id
    
    # Otherwise, try to fetch from the database
    try:
        from pymongo import MongoClient
        client = MongoClient(os.getenv("MONGO_URI"))
        db = client.patient_data
        
        # Get first patient with an Alexa ID
        patient = db.patients.find_one({"alexa_user_id": {"$exists": True}})
        if patient and patient.get("alexa_user_id"):
            return patient["alexa_user_id"]
    except Exception as e:
        print(f"Error getting Alexa ID from database: {e}")
    
    print("❌ No Alexa ID found. Please set TEST_ALEXA_USER_ID env var or add IDs to database.")
    return None

def test_symptom_conversation():
    """Test the symptom conversation flow with Alexa."""
    alexa_user_id = get_test_alexa_user_id()
    if not alexa_user_id:
        return
    
    print(f"Testing with Alexa user ID: {alexa_user_id}")
    
    # Start a conversation loop
    conversation_active = True
    
    while conversation_active:
        # Get user input
        user_input = input("\n🗣️ Enter what the user would say (or 'quit' to exit): ")
        if user_input.lower() == 'quit':
            break
        
        # Send the message
        try:
            response = requests.post(
                f"{BASE_URL}/api/alexa/user/{alexa_user_id}/conversation",
                headers=HEADERS,
                json={"content": user_input}
            )
            
            if not response.ok:
                print(f"❌ Error: {response.status_code} - {response.text}")
                continue
            
            data = response.json()
            print(f"\n🤖 Assistant: {data['response']}")
            
            # Check if the conversation should end
            if data.get("should_end", False):
                print("\n✅ Conversation complete. Checking symptom states...")
                conversation_active = False
                
                # Get the symptom states
                states_response = requests.get(
                    f"{BASE_URL}/api/alexa/user/{alexa_user_id}/symptom_states",
                    headers=HEADERS
                )
                
                if states_response.ok:
                    symptom_states = states_response.json()
                    print("\n📊 Symptom Analysis:")
                    for symptom, data in symptom_states.items():
                        status = "✅ Reported" if data.get("experienced") else "❌ Not Reported"
                        print(f"{symptom}: {status}")
                else:
                    print(f"❌ Error getting symptom states: {states_response.status_code}")
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_symptom_conversation() 