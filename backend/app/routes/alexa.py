from flask import Blueprint, jsonify, request, current_app
from datetime import datetime, timedelta
from functools import wraps
from ..utils.openai_utils import get_conversation_response, analyze_symptoms, get_openai_client
from ..models.conversation import ConversationHelper
from bson import ObjectId
import os
import json
from app.middleware.auth import api_key_required

bp = Blueprint('alexa', __name__)

@bp.route("/api/alexa/user/<alexa_user_id>/conversation", methods=["POST"])
@api_key_required
def create_conversation_log(alexa_user_id):
    """Create a conversation log entry and generate response from OpenAI."""
    try:
        data = request.get_json()
        if not data or 'content' not in data:
            return jsonify({"error": "Missing content"}), 400

        print(f"Received message: {data['content']}")  # Debug print

        # Find patient
        patient = current_app.db.patients.find_one({"alexa_user_id": alexa_user_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        # Create and store user message
        user_msg = ConversationHelper.create_user_message(
            patient_id=str(patient["_id"]),
            content=data['content']
        )
        current_app.db.conversation_logs.insert_one(user_msg)

        # Get conversation history for this patient from today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        conversation_logs = list(
            current_app.db.conversation_logs.find({
                "patient_id": str(patient["_id"]),
                "created_at": {"$gte": today_start}
            }).sort("created_at", 1)
        )

        # Format logs for OpenAI
        formatted_logs = []
        for log in conversation_logs:
            formatted_logs.append({
                "role": log["role"],
                "content": log["content"]
            })
        
        # Add system message if this is the start of conversation
        if len(formatted_logs) <= 1:
            with open("app/prompts/system_prompt.txt", "r") as f:
                system_prompt = f.read()
                
            formatted_logs.insert(0, {
                "role": "system",
                "content": system_prompt
            })

        # Get response from OpenAI
        response_text, chain_of_thoughts = get_conversation_response(formatted_logs)
        
        # Check if conversation should end
        should_end = "CONVERSATION_END" in response_text
        
        # Remove the CONVERSATION_END marker before sending to client
        cleaned_response = response_text.replace("CONVERSATION_END", "").strip()
        
        # Store bot response
        bot_msg = ConversationHelper.create_bot_message(
            patient_id=str(patient["_id"]),
            content=cleaned_response,
            chain_of_thoughts=chain_of_thoughts
        )
        current_app.db.conversation_logs.insert_one(bot_msg)
        
        # If conversation is ending, analyze symptoms
        if should_end:
            # Analyze symptoms from today's conversation
            symptom_analysis = analyze_symptoms(conversation_logs)
            
            # Store the symptom states for today's date
            today_date = datetime.utcnow().strftime("%Y-%m-%d")
            
            # Update patient document with symptom states
            current_app.db.patients.update_one(
                {"_id": patient["_id"]},
                {
                    "$set": {
                        f"symptom_states.{today_date}": symptom_analysis,
                        "last_conversation_date": datetime.utcnow(),
                        "conversation_ended": True
                    }
                }
            )
        
        return jsonify({
            "response": cleaned_response,
            "should_end": should_end
        })

    except Exception as e:
        print(f"Error in conversation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route("/api/alexa/user/<alexa_user_id>/last_message", methods=["GET"])
@api_key_required
def get_last_message(alexa_user_id):
    """Get the last message exchange for a user."""
    try:
        patient = current_app.db.patients.find_one({"alexa_user_id": alexa_user_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Get the latest bot message
        last_message = current_app.db.conversation_logs.find_one(
            {
                "patient_id": str(patient["_id"]), 
                "role": "bot"
            }, 
            sort=[("created_at", -1)]
        )
        
        if not last_message:
            # No previous conversation, create a welcome message
            welcome_msg = "Hello, thanks for checking in with the health monitor. How are you feeling today?"
            return jsonify({
                "message": "success",
                "last_message": {
                    "role": "bot",
                    "content": welcome_msg,
                    "created_at": datetime.utcnow().isoformat()
                }
            })
        
        # Check if the conversation was already ended
        if "CONVERSATION_END" in last_message.get("content", ""):
            # Start a new conversation
            welcome_msg = "Hello, thanks for checking in again. How have you been feeling since we last spoke?"
            return jsonify({
                "message": "success",
                "last_message": {
                    "role": "bot",
                    "content": welcome_msg,
                    "created_at": datetime.utcnow().isoformat()
                }
            })
        
        # Return the last message
        return jsonify({
            "message": "success",
            "last_message": ConversationHelper.format_for_frontend(last_message)
        })
        
    except Exception as e:
        print(f"Error retrieving last message: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route("/api/alexa/user/<alexa_user_id>/conversation_logs", methods=["GET"])
@api_key_required
def get_conversation_logs(alexa_user_id):
    """Get conversation logs for a user, organized by symptom category."""
    try:
        # Get date from query parameters
        date = request.args.get('date', datetime.utcnow().strftime("%Y-%m-%d"))
        
        # Find patient
        patient = current_app.db.patients.find_one({"alexa_user_id": alexa_user_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Get start and end of the requested date
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        day_start = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Get all logs for this patient on the specified date
        logs = list(current_app.db.conversation_logs.find({
            "patient_id": str(patient["_id"]),
            "created_at": {
                "$gte": day_start,
                "$lte": day_end
            }
        }).sort("created_at", 1))
        
        # Format logs for frontend
        formatted_logs = [ConversationHelper.format_for_frontend(log) for log in logs]
        
        # Get symptom states for this date
        symptom_states = patient.get("symptom_states", {}).get(date, {})
        
        # Organize logs by symptom
        symptom_logs = {}
        for symptom in ConversationHelper.SYMPTOM_CATEGORIES:
            # Get log IDs for this symptom from symptom states
            log_ids = symptom_states.get(symptom, {}).get("logs", [])
            
            # Filter logs by IDs
            symptom_logs[symptom] = {
                "logs": [log for log in formatted_logs if log["id"] in log_ids],
                "experienced": symptom_states.get(symptom, {}).get("experienced", False)
            }
        
        # Also include a "general" category for logs not associated with specific symptoms
        specific_log_ids = []
        for symptom_data in symptom_states.values():
            specific_log_ids.extend(symptom_data.get("logs", []))
        
        general_logs = [log for log in formatted_logs if log["id"] not in specific_log_ids]
        symptom_logs["General"] = {
            "logs": general_logs,
            "experienced": None  # No "experienced" status for general conversation
        }
        
        return jsonify({
            "date": date,
            "symptom_logs": symptom_logs,
            "all_logs": formatted_logs
        })
        
    except Exception as e:
        print(f"Error getting conversation logs: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route("/api/alexa/user/<alexa_user_id>/session_end", methods=["POST"])
@api_key_required
def session_end(alexa_user_id):
    """Handle end of conversation session."""
    try:
        patient = current_app.db.patients.find_one({"alexa_user_id": alexa_user_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        # Get all conversation logs for final analysis
        conversation_logs = list(
            current_app.db.conversation_logs.find(
                {"patient_id": str(patient["_id"])}
            ).sort("created_at", 1)
        )

        # Format logs for analysis
        formatted_logs = [ConversationHelper.format_for_frontend(log) for log in conversation_logs]
        
        # Analyze symptoms
        symptom_analysis = analyze_symptoms(formatted_logs)

        # Update patient document
        current_app.db.patients.update_one(
            {"_id": patient["_id"]},
            {
                "$set": {
                    "symptom_states": symptom_analysis,
                    "last_conversation_date": datetime.utcnow(),
                    "conversation_ended": True
                }
            }
        )

        return jsonify({"message": "Session ended successfully"})

    except Exception as e:
        print(f"Error ending session: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route("/api/alexa/user/<alexa_user_id>/symptom_states", methods=["GET"])
@api_key_required
def get_symptom_states(alexa_user_id):
    """Get current symptom states for a user."""
    try:
        # Get the date from query parameters or use today's date
        date = request.args.get('date', datetime.utcnow().strftime("%Y-%m-%d"))
        
        patient = current_app.db.patients.find_one({"alexa_user_id": alexa_user_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        # Get symptom states for the requested date
        symptom_states = patient.get("symptom_states", {}).get(date, {})
        
        # If no symptom states exist for this date, return default structure
        if not symptom_states:
            symptom_states = {
                "Shortness of Breath": {"experienced": False, "logs": []},
                "Palpitation": {"experienced": False, "logs": []},
                "Chest Discomfort": {"experienced": False, "logs": []},
                "Swelling": {"experienced": False, "logs": []},
                "Fatigue": {"experienced": False, "logs": []},
                "Syncope": {"experienced": False, "logs": []}
            }

        return jsonify(symptom_states)

    except Exception as e:
        print(f"Error getting symptom states: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route("/api/alexa/test_openai", methods=["GET"])
@api_key_required
def test_openai():
    """Test OpenAI connection"""
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": "Say 'OpenAI is working!'"}
            ],
            max_tokens=20
        )
        return jsonify({"status": "success", "response": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@bp.route("/api/alexa/updates", methods=["GET"])
@api_key_required
def get_alexa_updates():
    """Check for recent updates to Alexa user IDs."""
    try:
        # Get the timestamp from the request query parameter
        # Default to 1 minute ago if not provided
        from_time_str = request.args.get('from_time')
        
        if from_time_str:
            from_time = datetime.fromisoformat(from_time_str.replace('Z', '+00:00'))
        else:
            from_time = datetime.utcnow() - timedelta(minutes=1)
        
        # Find patients with Alexa IDs added after the specified time
        updated_patients = list(current_app.db.patients.find({
            "alexa_id_added_at": {"$gte": from_time}
        }))
        
        # Format the response
        updates = []
        for patient in updated_patients:
            updates.append({
                "patient_id": str(patient["_id"]),
                "patient_name": patient.get("name", "Unknown"),
                "alexa_user_id": patient.get("alexa_user_id"),
                "updated_at": patient.get("alexa_id_added_at").isoformat()
            })
        
        return jsonify({
            "updates": updates,
            "server_time": datetime.utcnow().isoformat()
        })
    
    except Exception as e:
        print(f"Error getting Alexa updates: {str(e)}")
        return jsonify({"error": str(e)}), 500
