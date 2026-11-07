import json
from unittest.mock import patch

import pytest

from app.services.research_client import (
    ResearchConfigurationError,
    ResearchResponseError,
    research_label_json,
)


def test_research_client_requires_api_key(monkeypatch):
    monkeypatch.delenv(
        "OPENROUTER_API_KEY",
        raising=False,
    )

    with pytest.raises(ResearchConfigurationError):
        research_label_json(
            {
                "extracted_text": "Ingredients: Water",
                "ocr_confidence": 80.0,
                "label_data": {
                    "ingredients": ["Water"],
                    "claims": [],
                },
            }
        )


def test_research_client_validates_response(monkeypatch):
    monkeypatch.setenv(
        "OPENROUTER_API_KEY",
        "test-key",
    )

    fake_report = {
        "product_name": "Example Product",
        "product_category": "cosmetic",
        "jurisdiction": "India",
        "ingredients": [],
        "claims": [
            {
                "claim": "Moisturizing",
                "claim_type": "cosmetic",
                "status": "REVIEW",
                "explanation": "Evidence requires review.",
                "source_ids": [],
            }
        ],
        "sources": [],
        "overall_summary": "Review required.",
        "limitations": [
            "No verified source was supplied in this test.",
        ],
    }

    fake_response_body = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(fake_report),
                },
            },
        ],
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exception_type,
            exception_value,
            traceback,
        ):
            return False

        def read(self):
            return json.dumps(
                fake_response_body,
            ).encode("utf-8")

    def fake_urlopen(request, timeout):
        assert request.get_header("Authorization") == "Bearer test-key"
        assert timeout == 120
        return FakeResponse()

    with patch(
        "app.services.research_client.urlopen",
        side_effect=fake_urlopen,
    ):
        result = research_label_json(
            {
                "extracted_text": "Moisturizing",
                "ocr_confidence": 70.0,
                "label_data": {
                    "ingredients": [],
                    "claims": ["Moisturizing"],
                },
            }
        )

    assert result.jurisdiction == "India"
    assert result.claims[0].status == "REVIEW"


def test_research_client_rejects_invalid_response(monkeypatch):
    monkeypatch.setenv(
        "OPENROUTER_API_KEY",
        "test-key",
    )

    fake_response_body = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(
                        {
                            "product_category": "cosmetic",
                        }
                    ),
                },
            },
        ],
    }

    class FakeResponse:
        def __enter__(self):
            return self

        def __exit__(
            self,
            exception_type,
            exception_value,
            traceback,
        ):
            return False

        def read(self):
            return json.dumps(
                fake_response_body,
            ).encode("utf-8")

    with patch(
        "app.services.research_client.urlopen",
        return_value=FakeResponse(),
    ):
        with pytest.raises(ResearchResponseError):
            research_label_json(
                {
                    "extracted_text": "Unknown",
                    "label_data": {},
                }
            )