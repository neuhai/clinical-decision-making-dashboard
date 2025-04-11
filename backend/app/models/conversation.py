from datetime import datetime
from bson import ObjectId
import json

class ConversationHelper:
    """Helper class for conversation-related operations."""
    
    SYMPTOM_CATEGORIES = [
        "Shortness of Breath",
        "Palpitation",
        "Chest Discomfort",
        "Swelling",
        "Fatigue",
        "Syncope"
    ]
    
    @staticmethod
    def create_user_message(patient_id, content):
        """Create a user message document."""
        return {
            "_id": ObjectId(),
            "patient_id": patient_id,
            "role": "user",
            "content": content,
            "created_at": datetime.utcnow()
        }
    
    @staticmethod
    def create_bot_message(patient_id, content, chain_of_thoughts=None):
        """Create a bot message document."""
        message = {
            "_id": ObjectId(),
            "patient_id": patient_id,
            "role": "bot",
            "content": content,
            "created_at": datetime.utcnow()
        }
        
        if chain_of_thoughts:
            message["chain_of_thoughts"] = chain_of_thoughts
            
        return message
    
    @staticmethod
    def format_for_frontend(log):
        """Format a log document for frontend consumption."""
        # Convert ObjectId to string
        log_id = str(log["_id"]) if "_id" in log else None
        
        # Create formatted log
        formatted = {
            "id": log_id,
            "role": log.get("role"),
            "content": log.get("content"),
            "created_at": log.get("created_at").isoformat() if log.get("created_at") else None
        }
        
        if "chain_of_thoughts" in log:
            formatted["chain_of_thoughts"] = log["chain_of_thoughts"]
            
        return formatted
    
    @staticmethod
    def json_encoder(obj):
        """Custom JSON encoder for MongoDB documents."""
        if isinstance(obj, ObjectId):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

    @staticmethod
    def get_initial_symptom_states():
        """Get initial symptom states structure"""
        return {
            "Shortness of Breath": {"experienced": False, "logs": []},
            "Palpitation": {"experienced": False, "logs": []},
            "Chest Discomfort": {"experienced": False, "logs": []},
            "Swelling": {"experienced": False, "logs": []},
            "Fatigue": {"experienced": False, "logs": []},
            "Syncope": {"experienced": False, "logs": []}
        } 