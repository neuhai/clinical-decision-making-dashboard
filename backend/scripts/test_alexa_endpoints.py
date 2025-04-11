#!/usr/bin/env python
import requests
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import argparse

load_dotenv()

# Parse command line arguments
parser = argparse.ArgumentParser(description='Test Alexa symptom tracking backend')
parser.add_argument('--port', type=int, default=5002, help='Port the Flask server is running on')
parser.add_argument('--alexa-user-id', type=str, default='test_alexa_user_123', help='Test Alexa user ID')
args = parser.parse_args()

BASE_URL = f"http://localhost:{args.port}"
ALEXA_API_KEY = os.getenv("ALEXA_API_KEY")
ALEXA_USER_ID = args.alexa_user_id

if not ALEXA_API_KEY:
    print("❌ Error: ALEXA_API_KEY environment variable not set.")
    exit(1)

HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": ALEXA_API_KEY
}

print(f"Using API key: {ALEXA_API_KEY}")
print(f"Testing against server at {BASE_URL}")
print(f"Using Alexa User ID: {ALEXA_USER_ID}")

def test_health_check():
    """Test if the server is running and accessible."""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Could not connect to server at {BASE_URL}")
        return False

def create_test_patient():
    """Create a test patient with the given Alexa User ID."""
    try:
        # First check if patient with this Alexa User ID already exists
        response = requests.get(
            f"{BASE_URL}/api/patients/by-alexa-id/{ALEXA_USER_ID}",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            patient = response.json()
            print(f"✅ Found existing patient with Alexa User ID: {ALEXA_USER_ID}")
            print(f"   Patient ID: {patient['_id']}")
            print(f"   Patient Name: {patient.get('name', 'Unknown')}")
            return patient['_id']
            
        # If not found, create a new test patient
        data = {
            "name": "Test Patient",
            "alexa_user_id": ALEXA_USER_ID,
            "date_of_birth": "1980-01-01"
        }
        
        response = requests.post(
            f"{BASE_URL}/api/patients",
            headers=HEADERS,
            json=data
        )
        
        if response.status_code == 201:
            patient_id = response.json().get("_id")
            print(f"✅ Created test patient with ID: {patient_id}")
            return patient_id
        else:
            print(f"❌ Failed to create test patient: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error creating test patient: {str(e)}")
        return None

def send_message(content):
    """Send a message to the Alexa conversation endpoint."""
    try:
        data = {"content": content}
        
        response = requests.post(
            f"{BASE_URL}/api/alexa/user/{ALEXA_USER_ID}/conversation",
            headers=HEADERS,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n🤖 Bot: {result['response']}")
            return result
        else:
            print(f"❌ Error sending message: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error sending message: {str(e)}")
        return None

def get_symptom_states():
    """Get the current symptom states for the user."""
    try:
        response = requests.get(
            f"{BASE_URL}/api/alexa/user/{ALEXA_USER_ID}/symptom_states",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            states = response.json()
            print("\n📊 Current Symptom States:")
            for symptom, data in states.items():
                status = "✓ YES" if data.get("experienced", False) else "✗ NO"
                print(f"   {symptom}: {status}")
            return states
        else:
            print(f"❌ Error getting symptom states: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error getting symptom states: {str(e)}")
        return None

def get_conversation_logs(date=None):
    """Get conversation logs for the user."""
    try:
        url = f"{BASE_URL}/api/alexa/user/{ALEXA_USER_ID}/conversation_logs"
        if date:
            url += f"?date={date}"
            
        response = requests.get(
            url,
            headers=HEADERS
        )
        
        if response.status_code == 200:
            logs = response.json()
            print("\n📝 Conversation Logs:")
            for symptom, data in logs.get("symptom_logs", {}).items():
                status = ""
                if symptom != "General":
                    status = " (✓ YES)" if data.get("experienced", False) else " (✗ NO)"
                print(f"\n   {symptom}{status}:")
                
                if len(data.get("logs", [])) == 0:
                    print("      No logs for this symptom")
                else:
                    for log in data.get("logs", []):
                        role = "🤖" if log["role"] == "bot" else "👤"
                        print(f"      {role} {log['content']}")
            
            return logs
        else:
            print(f"❌ Error getting conversation logs: {response.status_code}")
            print(response.text)
            return None
            
    except Exception as e:
        print(f"❌ Error getting conversation logs: {str(e)}")
        return None

def end_session():
    """End the current session."""
    try:
        response = requests.post(
            f"{BASE_URL}/api/alexa/user/{ALEXA_USER_ID}/session_end",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            print("\n✅ Session ended successfully")
            return True
        else:
            print(f"❌ Error ending session: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error ending session: {str(e)}")
        return False

def run_interactive_test():
    """Run an interactive test of the Alexa conversation."""
    print("\n=== Starting Interactive Test ===")
    print("Type 'exit' to end the conversation")
    print("Type 'states' to check current symptom states")
    print("Type 'logs' to view conversation logs")
    print("Type 'end' to force session end")
    
    while True:
        user_input = input("\n👤 You: ")
        
        if user_input.lower() == 'exit':
            break
        elif user_input.lower() == 'states':
            get_symptom_states()
            continue
        elif user_input.lower() == 'logs':
            get_conversation_logs()
            continue
        elif user_input.lower() == 'end':
            end_session()
            continue
        
        result = send_message(user_input)
        if result and result.get("should_end", False):
            print("\n🤖 The conversation has ended.")
            get_symptom_states()
            get_conversation_logs()
            break

def run_automated_test():
    """Run an automated test scenario."""
    print("\n=== Starting Automated Test ===")
    
    # Predefined conversation flow about symptoms
    conversation = [
        "Hi, I'm not feeling well today",
        "Yes, I've been having some trouble breathing, especially when I walk up the stairs",
        "It started about 3 days ago",
        "Yes, I also noticed my heart racing sometimes",
        "No chest pain, thankfully",
        "I've noticed some swelling in my ankles",
        "Yes, I've been feeling more tired than usual",
        "No, I haven't fainted or felt like I was going to",
        "Thank you for your help"
    ]
    
    for message in conversation:
        print(f"\n👤 You: {message}")
        result = send_message(message)
        time.sleep(1)  # Small delay to make the flow readable
        
        if result and result.get("should_end", False):
            print("\n🤖 The conversation has ended.")
            break
    
    # Get symptom states and logs after conversation
    get_symptom_states()
    get_conversation_logs()

if __name__ == "__main__":
    # Test if server is running
    if not test_health_check():
        print("Please make sure the Flask server is running")
        exit(1)
    
    # Create or find a test patient
    patient_id = create_test_patient()
    if not patient_id:
        print("Could not create or find test patient")
        exit(1)
    
    # Ask user which test to run
    print("\nSelect test mode:")
    print("1. Interactive (you type messages)")
    print("2. Automated (predefined conversation)")
    
    while True:
        try:
            choice = int(input("Enter choice (1/2): "))
            if choice in [1, 2]:
                break
            print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Please enter a number.")
    
    if choice == 1:
        run_interactive_test()
    else:
        run_automated_test()
    
    print("\n=== Test Completed ===") 