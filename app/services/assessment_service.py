from app.models.assessment import(
    ClaimAssessment,
    IngredientAssessment,
    LabelAssessment,
)

from app.models.label import LabelData

def create_mock_assessment(
        label_data:LabelData,
)-> LabelAssessment:
    claim_assessment=[
        ClaimAssessment(
            claim=claim,
            status="UNABLE_TO_VERIFY",
            explanation=(
                "No verified regulatory or scientific evidence"
            ),
            evidence_ids=[],
        )
        for claim in label_data.claims
    ]
    ingredient_assessments=[
        IngredientAssessment(
            ingredient=ingredient,
            status="UNABLE_TO_VERIFY",
            explanation=(
                "No verified regulatory or scientific evidence "
                "has been provided yet."
            ),
            evidence_ids=[],
        )
        for ingredient in label_data.ingredients
    ]

    return LabelAssessment(
        claims=claim_assessment,
        ingredients=ingredient_assessments,
        overall_summary=(
            "The label was extracted successfully, but evidence "
            "retrieval has not been performed."
        ),
        limitations=[
            "OCR output may contain recognition errors.",
            "No authoritative evidence sources were supplied.",
            "This is not a regulatory or medical conclusion.",
        ],
        evidence=[],
    )