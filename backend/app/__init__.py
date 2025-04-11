from flask import Flask, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import os
from dotenv import load_dotenv
from app.config import Config

# Load environment variables
load_dotenv()

def create_app(test_config=None):
    """Application Factory Function"""
    app = Flask(__name__)
    
    # Set debug mode
    app.debug = True
    
    # Set up CORS - allow all origins for now
    CORS(app)
    
    # Load configuration
    if test_config is None:
        app.config.from_object(Config)
    else:
        app.config.from_mapping(test_config)
    
    # Initialize MongoDB
    try:
        client = MongoClient(app.config["MONGO_URI"])
        # Test connection
        client.admin.command('ping')
        app.db = client.get_default_database()
        print("✅ Connected to MongoDB successfully")
    except Exception as e:
        print(f"❌ MongoDB connection error: {e}")
        # Continue anyway to allow the API to start
    
    # Import and register blueprints
    try:
        from app.routes import misc, alexa, patients, daily_summary
        app.register_blueprint(misc.bp)
        app.register_blueprint(alexa.bp)
        app.register_blueprint(patients.bp)
        app.register_blueprint(daily_summary.bp)
        
        # Start background tasks for database updates
        from app.tasks.background_tasks import start_background_tasks
        start_background_tasks()
        print("✅ Started background database update tasks")
        
        # Print registered routes for debugging
        print("\n🔍 Registered Routes:")
        for rule in app.url_map.iter_rules():
            print(f"  {rule.endpoint} -> {rule.rule} [{', '.join(rule.methods)}]")
        
    except ImportError as e:
        print(f"❌ Error importing blueprints: {e}")
    
    # Default health check route
    @app.route('/')
    def index():
        return "Flask API is running correctly!", 200
    
    @app.route('/api/health')
    def health():
        return jsonify({
            "status": "OK",
            "mongodb": "connected" if 'db' in app.__dict__ else "not connected"
        })

    return app
