from app.models.research import ProductResearchReport


def test_research_report_accepts_valid_data():
    report = ProductResearchReport(
        product_name="Example Product",
        product_category="cosmetic",
        ingredients=[
            {
                "ingredient": "Glycerin",
                "identity": "Glycerol",
                "function": "Humectant",
                "natural_or_synthetic": "Can be natural or synthetic",
                "potential_benefits": [
                    "May help retain moisture in skin"
                ],
                "potential_concerns": [],
                "long_term_evidence": (
                    "No conclusion without concentration and exposure data."
                ),
                "status": "REVIEW",
                "explanation": (
                    "The available label does not provide concentration."
                ),
                "source_ids": ["source-1"],
            }
        ],
        claims=[],
        sources=[
            {
                "source_id": "source-1",
                "title": "Example scientific source",
                "url": "https://example.com/source",
                "source_type": "SCIENTIFIC",
                "publisher": "Example Publisher",
                "publication_date": None,
                "jurisdiction": None,
                "quoted_text": "Example evidence.",
                "relevance": "Discusses the ingredient function.",
            }
        ],
        overall_summary="Review required.",
        limitations=["Concentration was not available."],
    )

    assert report.jurisdiction == "India"
    assert report.ingredients[0].status == "REVIEW"
    assert report.sources[0].source_type == "SCIENTIFIC"


def test_research_report_uses_unable_to_verify():
    report = ProductResearchReport(
        product_category="unknown",
        ingredients=[],
        claims=[],
        sources=[],
        overall_summary="Unable to verify.",
        limitations=["OCR was incomplete."],
    )

    assert report.ingredients == []
    assert report.claims == []
    assert report.sources == []