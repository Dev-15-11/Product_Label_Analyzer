from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image, UnidentifiedImageError

from app.models.analysis import AnalysisResponse
from app.models.assessment import LabelAssessment
from app.services.label_analysis import analyze_label_image
from app.services.openrouter_client import (
    OpenRouterConfigurationError,
    OpenRouterResponseError,
    assess_label_with_openrouter,
)
from app.services.research_client import (
    ResearchConfigurationError,
    ResearchResponseError,
    research_label_json,
)
from app.services.pdf_report import generate_research_pdf

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 10 * 1024 * 1024
MIN_IMAGE_DIMENSION = 100
MAX_IMAGE_DIMENSION = 8000


app = FastAPI(
    title="Product Label Analyzer",
    description="An evidence-grounded product label analysis API",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {
        "message": "Product Label Analyzer API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }


def validate_image_dimensions(image: Image.Image) -> tuple[int, int]:
    width, height = image.size

    if (
        width < MIN_IMAGE_DIMENSION
        or height < MIN_IMAGE_DIMENSION
        or width > MAX_IMAGE_DIMENSION
        or height > MAX_IMAGE_DIMENSION
    ):
        raise HTTPException(
            status_code=400,
            detail="Image dimensions must be between 100 and 8000 pixels",
        )

    return width, height


def build_analysis_response(
    *,
    original_filename: str,
    saved_filename: str,
    content_type: str,
    width: int,
    height: int,
    size_bytes: int,
    analysis_result: dict,
) -> dict:
    return {
        "original_filename": original_filename,
        "saved_filename": saved_filename,
        "content_type": content_type,
        "width": width,
        "height": height,
        "size_bytes": size_bytes,
        "processed_filename": analysis_result["processed_filename"],
        "extracted_text": analysis_result["extracted_text"],
        "ocr_confidence": analysis_result["ocr_confidence"],
        "ocr_review_status": analysis_result["ocr_review_status"],
        "label_data": analysis_result["label_data"].model_dump(),
        "normalized_ingredients": analysis_result[
            "normalized_ingredients"
        ],
    }


@app.post("/upload-label", response_class=StreamingResponse)
async def upload_label(file: UploadFile = File(...)):
    if file.content_type not in {"image/jpeg", "image/png"}:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG images are supported",
        )

    file_bytes = await file.read()

    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail="Image file is too large. Maximum size is 10 MB",
        )

    file_extension = (
        ".jpg"
        if file.content_type == "image/jpeg"
        else ".png"
    )

    saved_filename = f"{uuid4()}{file_extension}"
    saved_path = UPLOAD_DIR / saved_filename
    saved_path.write_bytes(file_bytes)

    try:
        with Image.open(saved_path) as image:
            image_width, image_height = validate_image_dimensions(image)
            image.verify()

    except UnidentifiedImageError:
        saved_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=400,
            detail="The uploaded file is not a valid image",
        )

    analysis_result = analyze_label_image(saved_path)

    analysis_response = build_analysis_response(
        original_filename=file.filename or saved_filename,
        saved_filename=saved_filename,
        content_type=file.content_type,
        width=image_width,
        height=image_height,
        size_bytes=len(file_bytes),
        analysis_result=analysis_result,
    )

    try:
        research_report = research_label_json(analysis_response)
    except ResearchConfigurationError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error
    except ResearchResponseError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error

    pdf_buffer = generate_research_pdf(
        research_report,
        original_filename=file.filename or saved_filename,
    )

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": (
                f'attachment; filename="{Path(file.filename or saved_filename).stem}_research_report.pdf"'
            )
        },
    )


@app.post(
    "/analyze-label/{saved_filename}",
    response_model=AnalysisResponse,
)
def analyze_saved_label(saved_filename: str):
    requested_path = Path(saved_filename)

    if requested_path.name != saved_filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )

    if requested_path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG images can be analyzed",
        )

    saved_path = UPLOAD_DIR / requested_path

    if not saved_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Saved image was not found",
        )

    try:
        with Image.open(saved_path) as image:
            image_width, image_height = validate_image_dimensions(image)
            image.verify()

    except UnidentifiedImageError:
        raise HTTPException(
            status_code=400,
            detail="The saved file is not a valid image",
        )

    content_type = (
        "image/png"
        if saved_path.suffix.lower() == ".png"
        else "image/jpeg"
    )

    analysis_result = analyze_label_image(saved_path)

    return build_analysis_response(
        original_filename=saved_filename,
        saved_filename=saved_filename,
        content_type=content_type,
        width=image_width,
        height=image_height,
        size_bytes=saved_path.stat().st_size,
        analysis_result=analysis_result,
    )
@app.post(
    "/assess-label/{saved_filename}",
    response_model=LabelAssessment,
)


def assess_saved_label(saved_filename: str):
    requested_path = Path(saved_filename)

    if requested_path.name != saved_filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename",
        )

    if requested_path.suffix.lower() not in {
        ".jpg",
        ".jpeg",
        ".png",
    }:
        raise HTTPException(
            status_code=400,
            detail="Only JPEG and PNG images can be assessed",
        )

    saved_path = UPLOAD_DIR / requested_path

    if not saved_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Saved image was not found",
        )

    analysis_result = analyze_label_image(saved_path)

    try:
        assessment = assess_label_with_openrouter(
            label_data=analysis_result["label_data"],
            evidence=[],
        )

    except OpenRouterConfigurationError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error),
        ) from error

    except OpenRouterResponseError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error

    return assessment
