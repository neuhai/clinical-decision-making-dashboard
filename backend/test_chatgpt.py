# test_chatgpt.py
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with the API key from the .env file
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def test_chatgpt():
    """Test the OpenAI API with a basic request."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": "Hello! Can you confirm that the API is working?"}
            ]
        )
        print("✅ GPT-4 Response:", response.choices[0].message.content)
    except Exception as e:
        print("❌ Error:", e)

# Run the test when the file is executed
if __name__ == "__main__":
    test_chatgpt()
