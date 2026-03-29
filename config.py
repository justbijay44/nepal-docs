import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
TESSERACT_LANG = 'nep'
GEMINI_MODEL = 'gemini-2.0-flash'