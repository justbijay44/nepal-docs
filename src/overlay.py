import cv2
import numpy as np
import pytesseract
from PIL import Image, ImageDraw, ImageFont
from config import TESSERACT_CMD, TESSERACT_LANG
from groq import Groq
from src.utils.logger import logger

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def get_lines(image_path):
    img = cv2.imread(image_path)

    if img is None:
        pil_img = Image.open(image_path)
        img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=7)
    binary = cv2.adaptiveThreshold(
        denoised, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY, 31, 11
    )

    data = pytesseract.image_to_data(
        binary,
        lang=TESSERACT_LANG,
        output_type=pytesseract.Output.DATAFRAME
    )

    lines_data = data[data['level'] == 4].copy()
    lines_data = lines_data[lines_data['height'] < 60]
    lines_data = lines_data.reset_index(drop=True)

    words_data = data[data['level'] == 5].copy()
    words_data = words_data[words_data['text'].notna()]
    words_data = words_data[words_data['text'].str.strip() != '']

    results = []
    for _, row in lines_data.iterrows():
        words = words_data[
            (words_data['block_num'] == row['block_num']) &
            (words_data['par_num'] == row['par_num']) &
            (words_data['line_num'] == row['line_num'])
        ]

        text = ' '.join(words['text'].tolist()).strip()
        if text:
            results.append({
                'x': int(row['left']),
                'y': int(row['top']),
                'w': int(row['width']),
                'h': int(row['height']),
                'nepali_text': text
            })

    logger.info(f"Detected {len(results)} lines")
    return img, results

def translate_lines(lines, client, model):
    logger.info(f"Translating len{lines} lines in batches")
    translations = [''] * len(lines)
    batch_size = 10

    for start in range(0, len(lines), batch_size):
        batch = lines[start: start + batch_size]
        nepali_lines = [l['nepali_text'] for l in batch]
        numbered = '\n'.join([f"{idx}:{text}" for idx, text in enumerate(nepali_lines)])

        prompt = f"""
            You are a Nepali language expert. Translate each numbered Nepali line into simple English.
            Rules:
            - Return exactly {len(batch)} lines
            - Format: number:translation (example: 0:The government of Nepal)
            - Numbers start from 0
            - Use colon not period after number
            - Keep each translation short, one line only
            - Return ONLY the translations, no extra text

            {numbered}
        """

        response = client.chat.completions.create(
            model=model,
            messages = [{"role": "user", "content": prompt}] 
        )

        result_text = response.choices[0].message.content.strip()
        batch_translation = []
        for line in result_text.split('\n'):
            line = line.strip()
            if not line:
                continue

            if ':' in line:
                parts = line.split(':', 1)
                try:
                    int(parts[0].strip())
                    batch_translation.append(parts[1].strip())
                except:
                    pass
        
        for i, t in enumerate(batch_translation):
            if start + i < len(translations):
                translations[start + i] = t

    logger.info("Translation Complete")
    return translations

def draw_overlay(img, lines, translations):
    logger.info("Drawing overlay on image")
    pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    img_width = pil_img.width

    try:
        font = ImageFont.truetype('arial.ttf', size=13)
    except:
        font = ImageFont.load_default()

    PADDING = 12

    for i, line in enumerate(lines):
        x, y, w, h = line['x'], line['y'], line['w'], line['h']
        translated = translations[i] if i < len(translations) else ""

        x0, y0 = max(0, x - PADDING), max(0, y - PADDING)
        x1, y1 = img_width - PADDING, max(y0 + 1, y + h + PADDING)

        draw.rectangle([x0, y0, x1, y1], fill='white')
        draw.text((x0, y0),translated, fill='black', font=font)

    logger.info("Overlay complete")
    return pil_img