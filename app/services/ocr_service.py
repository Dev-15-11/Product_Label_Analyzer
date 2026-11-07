import os
from pathlib import Path

import pytesseract
from PIL import Image
from pytesseract import Output
from dotenv import load_dotenv


load_dotenv()

if tesseract_cmd := os.getenv("TESSERACT_CMD"):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd


def extract_text(image_path: Path) -> dict:
    with Image.open(image_path) as image:
        text = pytesseract.image_to_string(image)

        data = pytesseract.image_to_data(
            image,
            output_type=Output.DICT,
        )

    confidence_values = []

    for confidence in data["conf"]:
        try:
            confidence_value = float(confidence)

            if confidence_value >= 0:
                confidence_values.append(confidence_value)

        except ValueError:
            continue

    average_confidence = 0.0
    review_status = "low_confidence"

    if confidence_values:
        average_confidence = (
            sum(confidence_values) / len(confidence_values)
        )
        if average_confidence >= 80:
            review_status = "good"
        elif average_confidence >= 60:
            review_status = "needs_review"
        else:
           review_status = "low_confidence"

    return {
        "text": text.strip(),
        "average_confidence": round(average_confidence, 2),
        "review_status": review_status,
    }