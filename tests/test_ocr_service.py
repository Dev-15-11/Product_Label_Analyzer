from pathlib import Path

from PIL import Image

from app.services import ocr_service


def test_extract_text_marks_missing_confidence_for_review(
    tmp_path: Path,
    monkeypatch,
):
    image_path = tmp_path / "label.png"
    Image.new("RGB", (100, 100)).save(image_path)

    monkeypatch.setattr(
        ocr_service.pytesseract,
        "image_to_string",
        lambda image: "",
    )
    monkeypatch.setattr(
        ocr_service.pytesseract,
        "image_to_data",
        lambda image, output_type: {"conf": []},
    )

    result = ocr_service.extract_text(image_path)

    assert result == {
        "text": "",
        "average_confidence": 0.0,
        "review_status": "low_confidence",
    }
