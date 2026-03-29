import os
from dotenv import load_dotenv

load_dotenv()

TESSERACT_LANG = 'nep'
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = 'gemini-2.0-flash'

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = 'llama-3.1-8b-instant'

MLFLOW_TRACKING_URI = "sqlite:///mlflow.db"
