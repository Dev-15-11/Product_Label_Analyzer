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