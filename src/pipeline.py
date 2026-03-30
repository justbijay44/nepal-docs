import io
import time
import mlflow
from src.ocr import extract_text
from src.explainer import explain_doc
from src.overlay import get_lines, translate_lines, draw_overlay
from src.utils.logger import logger
from groq import Groq
from config import GROQ_MODEL, MLFLOW_TRACKING_URI, GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

def run_pipeline(image_path):
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)

    experiment_name = "nepali-doc-explainer"
    if not mlflow.get_experiment_by_name(experiment_name):
        mlflow.create_experiment(experiment_name)
    mlflow.set_experiment(experiment_name)

    with mlflow.start_run():
        try:
            logger.info(f"Pipeline started for: {image_path}")
            mlflow.log_param("model", GROQ_MODEL)
            mlflow.log_param("image_path", str(image_path))

            ocr_start = time.time()
            text = extract_text(image_path)
            ocr_time = time.time() - ocr_start
            
            if not text:
                logger.warning("No text extracted from image")
                mlflow.log_metric("ocr_char_count", 0)
                mlflow.log_metric("success", 0)
                return None, "Couldn't extract text from image."
            
            mlflow.log_metric("ocr_char_count", len(text))
            mlflow.log_metric("ocr_time_seconds", round(ocr_time, 3))

            llm_start = time.time()
            explanation = explain_doc(text)
            llm_time = time.time() - llm_start

            mlflow.log_metric("llm_time_seconds", round(llm_time, 3))
            mlflow.log_metric("success", 1)

            logger.info("Pipeline created successfully")
            return text, explanation
        
        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            mlflow.log_metric("success", 0)
            mlflow.log_param("error", str(e))
            return None, f"Something went wrong: {str(e)}"
        
def run_overlay_pipeline(image_path):
    try:
        logger.info(f"Overlay pipeline started: {image_path}")

        img, lines = get_lines(image_path)
        if not lines:
            return None, "No lines were detected"
        
        translations = translate_lines(lines, client, GROQ_MODEL)
        result_img = draw_overlay(img, lines, translations)
        return result_img, None
    
    except Exception as e:
        logger.error(f"Overlay pipeline failed: {e}")
        return None, f"Something went wrong: {str(e)}"