from google import genai
from groq import Groq
from config import GEMINI_API_KEY, GEMINI_MODEL, GROQ_API_KEY, GROQ_MODEL
from src.utils.logger import logger

# client = genai.Client(api_key=GEMINI_API_KEY)
client = Groq(api_key=GROQ_API_KEY)

def explain_doc(nepali_text):
    try:
        prompt = f"""
            You are an expert in Nepali language including formal, legal and bureaucratic Nepali.

            A user has scanned an official Nepali document. Your job is to explain clearly 
            in simple English what this document is actually saying — the real meaning, 
            not just a word for word translation. Ignore any garbled or unreadable characters.

            Structure your response like this:
            📄 Document Type:
            📝 Simple Summary:
            ⚠️ Important Points:
            ❓ Difficult Terms Explained:

            Nepali Text:
            {nepali_text}
        """
        # response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role":"user",
                "content": prompt}
            ])
        logger.info("LLM explanation received successfully")
        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"LLm explanation failed: {e}")
        raise