import pytest

from app import config


def test_openrouter_model_has_default():
    assert config.OPENROUTER_MODEL


def test_openrouter_config_requires_api_key(monkeypatch):
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", None)

    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY is missing"):
        config.validate_openrouter_config()


def test_openrouter_config_accepts_api_key(monkeypatch):
    monkeypatch.setattr(config, "OPENROUTER_API_KEY", "test-key")

    config.validate_openrouter_config()