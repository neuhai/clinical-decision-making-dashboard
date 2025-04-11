import os
from flask import Flask
from dotenv import load_dotenv
from pymongo import MongoClient
from flask_cors import CORS

def create_app():
    # Load environment variables
    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    # Load configuration
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

    # Connect to MongoDB
    client = MongoClient(app.config["MONGO_URI"])
    app.db = client.patient_data

    # Import and register blueprints
    from app.routes.daily_summary import bp as daily_summary_bp
    from app.routes.patients import bp as patients_bp
    from app.routes.alexa import bp as alexa_bp

    app.register_blueprint(daily_summary_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(alexa_bp)
    
    # Start background tasks for database updates
    from app.tasks.background_tasks import start_background_tasks
    start_background_tasks()
    print("✅ Started background database update tasks")

    # Print routes for debugging
    print("\nRegistered Routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.endpoint} -> {rule.rule} [{', '.join(rule.methods - {'OPTIONS', 'HEAD'})}]")

    @app.route('/')
    def index():
        return "Flask API is running correctly!", 200

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5002, debug=True)
