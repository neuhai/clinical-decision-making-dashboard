import requests
import os
import json
import time
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Setup MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.patient_data

BASE_URL = "http://localhost:5002"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": os.getenv("ALEXA_API_KEY")
}

def check_server_running():
    """Check if the Flask server is running."""
    try:
        response = requests.get(f"{BASE_URL}/")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running. Please start the Flask server first.")
        return False

def get_test_alexa_user_id():
    """Get first available Alexa user ID from the database."""
    try:
        # Find first patient with an alexa_user_id
        patient = db.patients.find_one({"alexa_user_id": {"$exists": True}})
        if patient and patient.get("alexa_user_id"):
            print(f"✅ Found test patient: {patient.get('name', 'Unknown')} with Alexa ID: {patient['alexa_user_id']}")
            return patient["alexa_user_id"]
        else:
            print("❌ No patients found with Alexa IDs")
            return None
    except Exception as e:
        print(f"❌ Error accessing database: {e}")
        return None

def print_conversation(message_obj):
    """Pretty print a conversation message."""
    role = message_obj.get("role", "unknown")
    content = message_obj.get("content", "")
    icon = "🤖" if role == "bot" else "👤"
    print(f"{icon} {content}")

def test_chat_interaction(alexa_user_id):
    """Test interactive chat with the backend model."""
    if not alexa_user_id:
        print("❌ No Alexa user ID available for testing")
        return

    print("\n=== Starting Interactive Chat Test ===")
    print(f"Using Alexa User ID: {alexa_user_id}")
    print("Type 'quit' to end the conversation")

    # Get initial message
    try:
        response = requests.get(
            f"{BASE_URL}/api/alexa/user/{alexa_user_id}/last_message",
            headers=HEADERS
        )
        response.raise_for_status()
        initial_message = response.json().get("last_message", {})
        print_conversation(initial_message)
    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting initial message: {e}")
        return

    # Interactive chat loop
    while True:
        # Get user input
        user_input = input("\n👤 Enter your message: ").strip()
        if user_input.lower() == 'quit':
            break

        try:
            # Send user message
            response = requests.post(
                f"{BASE_URL}/api/alexa/user/{alexa_user_id}/conversation",
                headers=HEADERS,
                json={"content": user_input}
            )
            response.raise_for_status()
            
            # Print bot response
            bot_response = response.json()
            print(f"\n🤖 {bot_response.get('response', 'No response')}")

            # Check if conversation should end
            if bot_response.get("should_end", False):
                print("\n=== Conversation Ended ===")
                
                # Get final symptom states
                states_response = requests.get(
                    f"{BASE_URL}/api/alexa/user/{alexa_user_id}/symptom_states",
                    headers=HEADERS
                )
                states_response.raise_for_status()
                symptom_states = states_response.json()
                
                print("\nFinal Symptom Analysis:")
                for symptom, data in symptom_states.items():
                    experienced = "✅ Reported" if data.get("experienced") else "❌ Not Reported"
                    print(f"{symptom}: {experienced}")
                break

        except requests.exceptions.RequestException as e:
            print(f"❌ Error in conversation: {e}")
            break

def main():
    """Main test function."""
    print("=== Alexa API Test Script ===")
    
    if not check_server_running():
        return

    alexa_user_id = get_test_alexa_user_id()
    if not alexa_user_id:
        return

    while True:
        print("\nTest Options:")
        print("1. Start interactive chat")
        print("2. View current symptom states")
        print("3. View conversation history")
        print("4. Quit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            test_chat_interaction(alexa_user_id)
        elif choice == "2":
            try:
                response = requests.get(
                    f"{BASE_URL}/api/alexa/user/{alexa_user_id}/symptom_states",
                    headers=HEADERS
                )
                response.raise_for_status()
                states = response.json()
                print("\nCurrent Symptom States:")
                for symptom, data in states.items():
                    experienced = "✅ Reported" if data.get("experienced") else "❌ Not Reported"
                    print(f"{symptom}: {experienced}")
            except requests.exceptions.RequestException as e:
                print(f"❌ Error getting symptom states: {e}")
        elif choice == "3":
            try:
                response = requests.get(
                    f"{BASE_URL}/api/alexa/user/{alexa_user_id}/conversation_logs",
                    headers=HEADERS
                )
                response.raise_for_status()
                logs = response.json().get("conversations", {})
                print("\nConversation History:")
                for category, messages in logs.items():
                    if messages:
                        print(f"\n=== {category} ===")
                        for msg in messages:
                            print_conversation(msg)
            except requests.exceptions.RequestException as e:
                print(f"❌ Error getting conversation logs: {e}")
        elif choice == "4":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()
