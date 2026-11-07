import json
from unittest.mock import patch

import pytest

from app.models.label import LabelData
from app.services.openrouter_client import (
    OpenRouterConfigurationError,
    assess_label_with_openrouter,
)


def test_client_requires_api_key(monkeypatch):
    monkeypatch.delenv(
        "OPENROUTER_API_KEY",
        raising=False,
    )

    label_data = LabelData(
        claims=["Kills bacteria"],
        raw_text="Kills bacteria",
    )

    with pytest.raises(OpenRouterConfigurationError):
        assess_label_with_openrouter(label_data)


def test_client_validates_llm_json_response(monkeypatch):
    monkeypatch.setenv(
        "OPENROUTER_API_KEY",
        "test-key",
    )

    fake_assessment = {
        "claims": [
            {
                "claim": "Kills bacteria",
                "status": "UNABLE_TO_VERIFY",
                "explanation": "No evidence was supplied.",
                "evidence_ids": [],
            }
        ],
        "ingredients": [],
        "overall_summary": "Unable to verify.",
        "limitations": ["No evidence was supplied."],
        "evidence": [],
    }

    fake_response_body = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(fake_assessment)
                }
            }
        ]
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
                fake_response_body
            ).encode("utf-8")

    label_data = LabelData(
        claims=["Kills bacteria"],
        raw_text="Kills bacteria",
    )

    def fake_urlopen(request, timeout):
        assert request.get_header("Authorization") == "Bearer test-key"
        assert timeout == 60
        return FakeResponse()

    with patch(
        "app.services.openrouter_client.urlopen",
        side_effect=fake_urlopen,
    ):
        result = assess_label_with_openrouter(label_data)

    assert result.claims[0].status == "UNABLE_TO_VERIFY"
    assert result.claims[0].evidence_ids == []