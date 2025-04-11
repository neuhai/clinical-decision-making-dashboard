from flask import Flask
from pymongo import MongoClient
from .config import Config
from flask_cors import CORS
import os

def create_app():
    """Application Factory Function"""
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # Import routes
    from app.routes.daily_summary import bp as daily_summary_bp
    from app.routes.patients import bp as patients_bp

    # Initialize MongoDB
    client = MongoClient(app.config["MONGO_URI"])
    app.db = client.patient_data
    print("✅ Connected to MongoDB")

    # Register blueprints
    app.register_blueprint(daily_summary_bp)
    app.register_blueprint(patients_bp)
    
    # Default health check route
    @app.route('/')
    def index():
        return "Flask API is running correctly!", 200

    return app
