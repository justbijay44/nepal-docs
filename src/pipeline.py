from .ocr import extract_text
from .explainer import explain_doc
from src.utils.logger import logger

def run_pipeline(image_path):
    try:
        logger.info(f"Pipeline started for: {image_path}")
        
        text = extract_text(image_path)
        if not text:
            logger.warning("No text extracted from image")
            return None, "Couldn't extract text from image."
        
        explanation = explain_doc(text)
        logger.info("Pipeline created successfully")
        return text, explanation
    
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        return None, f"Something went wrong: {str(e)}"