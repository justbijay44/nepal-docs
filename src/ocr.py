import cv2
import pytesseract
from config import TESSERACT_CMD, TESSERACT_LANG
from PIL import Image
import numpy as np
from src.utils.logger import logger

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def preprocess_image(image_path):
    logger.info(f"Preprocessing image: {image_path}")
    img = cv2.imread(image_path)

    if img is None:
        logger.warning(f"cv2.imread failed, trying PIL fallback")
        pil_img = Image.open(image_path)
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_BAYER_RG2BGR)

    if img is None:
        logger.error("Image failed to load")
        raise ValueError("Image not found or failed to load")
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=7)
    binary = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 11
    )
    logger.info("Image preprocessing complete")
    return binary

def extract_text(image_path):
    try:
        processed = preprocess_image(image_path)
        text = pytesseract.image_to_string(processed, lang=TESSERACT_LANG)
        logger.info(f"OCR extracted {len(text)} characters")
        return text.strip()
    except Exception as e:
        logger.error(f"OCR failed: {e}")
        raise