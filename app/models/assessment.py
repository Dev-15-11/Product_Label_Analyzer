from typing import Literal

from pydantic import BaseModel, Field


AssessmentStatus = Literal[
    "PASS",
    "FAIL",
    "REVIEW",
    "UNABLE_TO_VERIFY",
    "NOT_APPLICABLE",
]


class EvidenceItem(BaseModel):
    evidence_id: str
    source_title: str
    source_url: str
    quoted_text: str
    jurisdiction: str | None = None


class ClaimAssessment(BaseModel):
    claim: str
    status: AssessmentStatus
    explanation: str
    evidence_ids: list[str] = Field(default_factory=list)


class IngredientAssessment(BaseModel):
    ingredient: str
    status: AssessmentStatus
    explanation: str
    evidence_ids: list[str] = Field(default_factory=list)


class LabelAssessment(BaseModel):
    claims: list[ClaimAssessment] = Field(default_factory=list)
    ingredients: list[IngredientAssessment] = Field(
        default_factory=list
    )
    overall_summary: str
    limitations: list[str] = Field(default_factory=list)
    evidence: list[EvidenceItem] = Field(default_factory=list)