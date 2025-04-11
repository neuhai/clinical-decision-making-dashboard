import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from flask import current_app

# Load prompts from files
PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

def load_prompt(filename):
    try:
        with open(PROMPTS_DIR / filename, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading prompt {filename}: {e}")
        raise

# Load prompts
try:
    conversation_system_prompt = load_prompt("system_prompt.txt")
    key_questions_prompt = load_prompt("key_questions_prompt.txt")
except Exception as e:
    print(f"Failed to load prompts: {e}")
    raise

def get_openai_client():
    """Get an instance of the OpenAI client."""
    api_key = current_app.config.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OpenAI API key is not set")
    
    return OpenAI(api_key=api_key)

def get_conversation_response(messages):
    """Get a response from OpenAI for the conversation."""
    try:
        client = get_openai_client()
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # or gpt-3.5-turbo if preferred
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract the main response and any chain of thought
        assistant_message = response.choices[0].message.content
        
        # No chain of thought in this implementation, but could be added
        chain_of_thoughts = None
        
        return assistant_message, chain_of_thoughts
    
    except Exception as e:
        print(f"Error getting OpenAI response: {str(e)}")
        return "I'm sorry, I encountered an error processing your request.", None

def analyze_symptoms(conversation_logs):
    """Analyze symptom logs using OpenAI."""
    try:
        client = get_openai_client()
        
        # Format conversation for analysis
        formatted_conversation = []
        for log in conversation_logs:
            formatted_conversation.append({
                "id": str(log.get("_id")),
                "role": log.get("role"),
                "content": log.get("content"),
                "created_at": log.get("created_at").isoformat() if log.get("created_at") else None
            })
        
        # Get the analysis prompt
        with open("app/prompts/key_questions_prompt.txt", "r") as f:
            system_prompt = f.read()
        
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the conversation to analyze: {json.dumps(formatted_conversation)}"}
        ]
        
        # Get OpenAI analysis
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # or gpt-3.5-turbo if preferred
            messages=messages,
            temperature=0,
            max_tokens=1000
        )
        
        # Extract JSON from the response
        response_text = response.choices[0].message.content
        
        # Find JSON in the response
        import re
        json_match = re.search(r'```json\n(.*?)\n```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without markdown code blocks
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                raise ValueError("Could not extract JSON from OpenAI response")
        
        # Parse the JSON
        symptom_analysis = json.loads(json_str)
        
        return symptom_analysis
    
    except Exception as e:
        print(f"Error analyzing symptoms: {str(e)}")
        # Return default structure with all symptoms set to false
        return {
            "Shortness of Breath": {"experienced": False, "logs": []},
            "Palpitation": {"experienced": False, "logs": []},
            "Chest Discomfort": {"experienced": False, "logs": []},
            "Swelling": {"experienced": False, "logs": []},
            "Fatigue": {"experienced": False, "logs": []},
            "Syncope": {"experienced": False, "logs": []}
        } 