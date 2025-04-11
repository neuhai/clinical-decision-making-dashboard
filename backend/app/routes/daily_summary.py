from flask import Blueprint, request, jsonify, current_app
import os
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

bp = Blueprint('daily_summary', __name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_summary(wearable_data, symptoms_data, date):
    """Generate a health summary using OpenAI's GPT-4."""
    prompt = f"""
    Generate a concise health summary based on the following patient data for {date}:
    Wearable Data: {wearable_data}
    Symptoms: {symptoms_data}
    Provide a brief summary focusing on health insights, avoiding unnecessary repetition.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful health assistant summarizing patient data."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        summary = response.choices[0].message.content
        return summary.strip()
    except Exception as e:
        return str(e)

@bp.route('/api/daily-summary/<patient_id>', methods=['GET'])
def get_daily_summary(patient_id):
    """
    Fetch a daily health summary for a patient using OpenAI's API.
    """
    try:
        # Get the date from the query parameter or default to today
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))

        # Fetch patient data
        patient = current_app.db.patients.find_one({"id": patient_id})
        if not patient:
            return jsonify({"error": "Patient not found"}), 404

        # Extract data
        wearable_data = patient.get("wearableSensorData", {})
        symptoms_data = patient.get("conversationLog", {})

        # Generate the summary with the date included
        summary = generate_summary(wearable_data, symptoms_data, date)
        return jsonify({"date": date, "summary": summary})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


