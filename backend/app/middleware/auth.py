from functools import wraps
from flask import request, jsonify, current_app

def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        # Get the list of valid API keys from the app config
        valid_api_keys = current_app.config.get('VALID_API_KEYS', [])
        
        if not api_key or api_key not in valid_api_keys:
            return jsonify({"error": "Invalid or missing API key"}), 401
        
        return f(*args, **kwargs)
    
    return decorated 