from app.models.assessment import LabelAssessment


def test_assessment_schema_accepts_valid_data():
    assessment = LabelAssessment(
        claims=[
            {
                "claim": "No bleach",
                "status": "REVIEW",
                "explanation": "Requires verification against the applicable rule.",
                "evidence_ids": ["source-1"],
            }
        ],
        ingredients=[],
        overall_summary="Further review is required.",
        limitations=["OCR confidence is moderate."],
        evidence=[
            {
                "evidence_id": "source-1",
                "source_title": "Example source",
                "source_url": "https://example.com",
                "quoted_text": "Example quoted passage",
                "jurisdiction": "India",
            }
        ],
    )

    assert assessment.claims[0].status == "REVIEW"
    assert assessment.evidence[0].evidence_id == "source-1"


def test_assessment_schema_rejects_invalid_status():
    invalid_data = {
        "claims": [
            {
                "claim": "No bleach",
                "status": "MAYBE",
                "explanation": "Invalid status",
                "evidence_ids": [],
            }
        ],
        "ingredients": [],
        "overall_summary": "Summary",
        "limitations": [],
        "evidence": [],
    }

    try:
        LabelAssessment.model_validate(invalid_data)
    except ValueError:
        pass
    else:
        raise AssertionError("Invalid status should be rejected")
    from app.models.label import LabelData
from app.models.label import LabelData
from app.services.assessment_service import create_mock_assessment


def test_mock_assessment_marks_claims_unable_to_verify():
    label_data = LabelData(
        claims=["Kills bacteria"],
        raw_text="Kills bacteria",
    )

    result = create_mock_assessment(label_data)

    assert len(result.claims) == 1
    assert result.claims[0].status == "UNABLE_TO_VERIFY"
    assert result.claims[0].evidence_ids == []


def test_mock_assessment_handles_empty_label_data():
    label_data = LabelData(
        raw_text="No structured fields found",
    )

    result = create_mock_assessment(label_data)

    assert result.claims == []
    assert result.ingredients == []
    assert result.evidence == []