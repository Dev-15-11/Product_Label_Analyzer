from pydantic import BaseModel

from app.models.research import ProductResearchReport
from app.models.label import LabelData


class AnalysisResponse(BaseModel):
    original_filename: str
    saved_filename: str
    processed_filename: str
    content_type: str
    width: int
    height: int
    size_bytes: int
    extracted_text: str
    ocr_confidence: float
    ocr_review_status: str
    label_data: LabelData
    normalized_ingredients: list[str]
    research_report: ProductResearchReport | None = None