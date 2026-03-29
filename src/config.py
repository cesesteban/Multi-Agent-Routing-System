import os
from typing import Optional
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "lm_studio").lower()
    MODEL_NAME = os.getenv("MODEL_NAME", "local-model")
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY") # Gemini
    
    # LM Studio
    LM_STUDIO_BASE_URL = os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")

    @classmethod
    def validate(cls):
        """Simple validation to ensure keys are present for chosen provider."""
        if cls.LLM_PROVIDER == "openai" and not cls.OPENAI_API_KEY:
            print("WARNING: OPENAI_API_KEY is not set.")
        elif cls.LLM_PROVIDER == "groq" and not cls.GROQ_API_KEY:
            print("WARNING: GROQ_API_KEY is not set.")
        elif cls.LLM_PROVIDER == "gemini" and not cls.GOOGLE_API_KEY:
            print("WARNING: GOOGLE_API_KEY is not set.")
