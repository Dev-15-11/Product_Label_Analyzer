from typing import Literal

from pydantic import BaseModel, Field


SourceType = Literal[
    "REGULATORY",
    "SCIENTIFIC",
    "NEWS",
    "OTHER",
]

ResearchStatus = Literal[
    "SUPPORTED",
    "NOT_SUPPORTED",
    "MIXED",
    "REVIEW",
    "UNABLE_TO_VERIFY",
]


class ResearchSource(BaseModel):
    source_id: str
    title: str
    url: str
    source_type: SourceType
    publisher: str
    publication_date: str | None = None
    jurisdiction: str | None = None
    quoted_text: str
    relevance: str


class IngredientFinding(BaseModel):
    ingredient: str
    identity: str
    function: str
    natural_or_synthetic: str
    potential_benefits: list[str] = Field(default_factory=list)
    potential_concerns: list[str] = Field(default_factory=list)
    long_term_evidence: str
    status: ResearchStatus
    explanation: str
    source_ids: list[str] = Field(default_factory=list)


class ClaimFinding(BaseModel):
    claim: str
    claim_type: str
    status: ResearchStatus
    explanation: str
    source_ids: list[str] = Field(default_factory=list)


class ProductResearchReport(BaseModel):
    product_name: str | None = None
    product_category: str
    jurisdiction: str = "India"
    ingredients: list[IngredientFinding] = Field(
        default_factory=list
    )
    claims: list[ClaimFinding] = Field(default_factory=list)
    sources: list[ResearchSource] = Field(default_factory=list)
    overall_summary: str
    limitations: list[str] = Field(default_factory=list)