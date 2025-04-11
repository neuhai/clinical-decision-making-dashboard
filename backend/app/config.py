import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # MongoDB configuration
    MONGO_URI = os.getenv('MONGO_URI')
    
    # OpenAI configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Alexa API key configuration
    ALEXA_API_KEY = os.getenv("ALEXA_API_KEY")
    
    # List of valid API keys for authenticating requests
    VALID_API_KEYS = [ALEXA_API_KEY]
    
    DEBUG = True