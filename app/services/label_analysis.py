from pathlib import Path

from app.services.image_preprocessor import preprocess_image
from app.services.ingredient_normalizer import normalize_ingredients
from app.services.label_parser import parse_label_text
from app.services.ocr_service import extract_text


PROCESSED_DIR = Path("data/processed")


def analyze_label_image(image_path: Path) -> dict:
    processed_path = preprocess_image(
        input_path=image_path,
        output_directory=PROCESSED_DIR,
    )

    ocr_result = extract_text(processed_path)

    label_data = parse_label_text(ocr_result["text"])

    normalized_ingredients = normalize_ingredients(
        label_data.ingredients
    )

    return {
        "processed_filename": processed_path.name,
        "extracted_text": ocr_result["text"],
        "ocr_confidence": ocr_result["average_confidence"],
        "ocr_review_status": ocr_result["review_status"],
        "label_data": label_data,
        "normalized_ingredients": normalized_ingredients,
    }