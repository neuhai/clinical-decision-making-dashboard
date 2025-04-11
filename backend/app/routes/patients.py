from flask import Blueprint, jsonify, request, current_app
from datetime import datetime
import json
from bson import ObjectId
from app.middleware.auth import api_key_required

bp = Blueprint('patients', __name__)

@bp.route('/api/patients', methods=['GET'])
def get_all_patients():
    """Get all patients with basic information for the sidebar."""
    try:
        # Only fetch fields needed for the sidebar to improve performance
        patients = list(current_app.db.patients.find({}, {
            'id': 1, 
            'name': 1, 
            'age': 1, 
            'gender': 1, 
            'riskLevel': 1,
            '_id': 0  # Exclude MongoDB's _id field
        }))
        
        if not patients:
            # Return empty array instead of 404 to allow for empty patient list
            return jsonify([])
        
        return jsonify(patients)
    except Exception as e:
        print(f"Error fetching patients: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/api/patients/<patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get a single patient by ID with full details."""
    try:
        patient = current_app.db.patients.find_one({"id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        # Convert ObjectId to string for JSON serialization
        if '_id' in patient:
            patient['_id'] = str(patient['_id'])
        
        return jsonify(patient)
    except Exception as e:
        print(f"Error fetching patient {patient_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route('/api/patients/<patient_id>/wearable-data', methods=['GET'])
def get_wearable_data(patient_id):
    """Get wearable sensor data for a specific patient."""
    try:
        patient = current_app.db.patients.find_one({"id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        wearable_data = patient.get('wearableSensorData')
        if not wearable_data:
            return jsonify({"error": "Wearable sensor data not found"}), 404
        
        return jsonify(wearable_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/patients/<patient_id>/risk-prediction', methods=['GET'])
def get_risk_prediction(patient_id):
    """Get AI risk prediction for a specific patient."""
    try:
        patient = current_app.db.patients.find_one({"id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        risk_prediction = patient.get('aiRiskPrediction')
        if not risk_prediction:
            return jsonify({"error": "Risk prediction data not found"}), 404
        
        return jsonify(risk_prediction)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/patients/<patient_id>/conversation-log', methods=['GET'])
def get_conversation_log(patient_id):
    """Get conversation log for a specific patient."""
    try:
        # Get date parameter (optional)
        date = request.args.get('date')
        
        patient = current_app.db.patients.find_one({"id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        conversation_log = patient.get('conversationLog')
        if not conversation_log:
            return jsonify({"error": "Conversation log not found"}), 404
        
        # If date is specified and doesn't match, return 404
        if date and 'date' in conversation_log:
            # Convert date formats for comparison if needed
            if '-' in date and '/' in conversation_log['date']:
                date_parts = date.split('-')
                db_date = f"{date_parts[1]}/{date_parts[2]}/{date_parts[0]}"
                if db_date != conversation_log['date']:
                    return jsonify({"error": f"No conversation log for date {date}"}), 404
            elif '/' in date and '-' in conversation_log['date']:
                date_parts = date.split('/')
                db_date = f"{date_parts[2]}-{date_parts[0]}-{date_parts[1]}"
                if db_date != conversation_log['date']:
                    return jsonify({"error": f"No conversation log for date {date}"}), 404
            elif date != conversation_log['date']:
                return jsonify({"error": f"No conversation log for date {date}"}), 404
        
        return jsonify(conversation_log)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/patients/<patient_id>/available-dates', methods=['GET'])
def get_available_dates(patient_id):
    """Get dates with available data for a specific patient."""
    try:
        patient = current_app.db.patients.find_one({"id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404
        
        dates = set()
        
        # Collect dates from wearable data
        if 'wearableSensorData' in patient:
            for sensor_type in ['heartRate', 'respiration', 'spo2', 'skinTemperature']:
                if sensor_type in patient['wearableSensorData'] and '10days' in patient['wearableSensorData'][sensor_type]:
                    for entry in patient['wearableSensorData'][sensor_type]['10days']:
                        if 'date' in entry:
                            dates.add(entry['date'])
        
        # Add conversation log date
        if 'conversationLog' in patient and 'date' in patient['conversationLog']:
            date_str = patient['conversationLog']['date']
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) == 3:
                    date_str = f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            dates.add(date_str)
        
        # Add risk prediction dates
        if 'aiRiskPrediction' in patient:
            # Add historical data dates
            if 'historicalData' in patient['aiRiskPrediction']:
                for entry in patient['aiRiskPrediction']['historicalData']:
                    if 'date' in entry:
                        dates.add(entry['date'])
        
        # Convert to list and sort
        date_list = sorted(list(dates))
        
        return jsonify({"dates": date_list})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@bp.route('/api/test', methods=['GET'])
def test_endpoint():
    """Simple endpoint to verify API is working."""
    return jsonify({"message": "API is working!"})

@bp.route("/api/patients", methods=["POST"])
@api_key_required
def create_patient():
    """Create a new patient."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data"}), 400
        
        # Extract fields
        name = data.get('name')
        alexa_user_id = data.get('alexa_user_id')
        date_of_birth = data.get('date_of_birth')
        
        if not name or not alexa_user_id:
            return jsonify({"error": "Name and Alexa User ID are required"}), 400
        
        # Check if patient with this Alexa User ID already exists
        existing = current_app.db.patients.find_one({"alexa_user_id": alexa_user_id})
        if existing:
            return jsonify({"error": f"Patient with Alexa User ID {alexa_user_id} already exists"}), 409
        
        # Create patient document
        patient = {
            "name": name,
            "alexa_user_id": alexa_user_id,
            "date_of_birth": date_of_birth,
            "alexa_id_added_at": datetime.utcnow(),
            "conversation_ended": False,
            "symptom_states": {}
        }
        
        # Insert into database
        result = current_app.db.patients.insert_one(patient)
        patient_id = str(result.inserted_id)
        
        return jsonify({"_id": patient_id, "message": "Patient created successfully"}), 201
    
    except Exception as e:
        print(f"Error creating patient: {str(e)}")
        return jsonify({"error": str(e)}), 500

@bp.route("/api/patients/by-alexa-id/<alexa_user_id>", methods=["GET"])
@api_key_required
def get_patient_by_alexa_id(alexa_user_id):
    """Get a patient by Alexa User ID."""
    try:
        patient = current_app.db.patients.find_one({"alexa_user_id": alexa_user_id})
        if not patient:
            return jsonify({"error": f"Patient with Alexa User ID {alexa_user_id} not found"}), 404
        
        # Convert MongoDB document to JSON
        patient["_id"] = str(patient["_id"])
        
        # Convert datetime objects
        if "alexa_id_added_at" in patient:
            patient["alexa_id_added_at"] = patient["alexa_id_added_at"].isoformat()
        
        if "last_conversation_date" in patient:
            patient["last_conversation_date"] = patient["last_conversation_date"].isoformat()
        
        return jsonify(patient), 200
    
    except Exception as e:
        print(f"Error getting patient: {str(e)}")
        return jsonify({"error": str(e)}), 500
