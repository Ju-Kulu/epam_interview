import pytest
from pydantic import ValidationError

from app.config import Settings


SETTINGS_ENVIRONMENT_VARIABLES = (
    "APP_NAME",
    "APP_ENV",
    "AI_PROVIDER",
    "BACKEND_HOST",
    "BACKEND_PORT",
    "OPENAI_API_KEY",
    "OPENAI_MODEL",
    "OPENAI_EMBEDDING_MODEL",
    "OLLAMA_BASE_URL",
    "OLLAMA_CHAT_MODEL",
    "OLLAMA_EMBEDDING_MODEL",
    "CHROMA_HOST",
    "CHROMA_PORT",
    "CHROMA_COLLECTION",
)


@pytest.fixture(autouse=True)
def clear_settings_environment(monkeypatch):
    for name in SETTINGS_ENVIRONMENT_VARIABLES:
        monkeypatch.delenv(name, raising=False)


def test_settings_read_values_from_environment(monkeypatch):
    environment = {
        "APP_ENV": "test",
        "AI_PROVIDER": "openai",
        "BACKEND_HOST": "127.0.0.1",
        "BACKEND_PORT": "8123",
        "OPENAI_API_KEY": "test-key",
        "OPENAI_MODEL": "test-chat-model",
        "OPENAI_EMBEDDING_MODEL": "test-embedding-model",
        "OLLAMA_BASE_URL": "http://ollama-test:11434",
        "OLLAMA_CHAT_MODEL": "test-chat",
        "OLLAMA_EMBEDDING_MODEL": "test-embedding",
        "CHROMA_HOST": "test-chroma",
        "CHROMA_PORT": "8124",
        "CHROMA_COLLECTION": "test_collection",
    }
    for name, value in environment.items():
        monkeypatch.setenv(name, value)

    settings = Settings()

    assert settings.env == "test"
    assert settings.ai_provider == "openai"
    assert settings.backend_host == "127.0.0.1"
    assert settings.backend_port == 8123
    assert settings.openai_api_key == "test-key"
    assert settings.openai_model == "test-chat-model"
    assert settings.openai_embedding_model == "test-embedding-model"
    assert settings.ollama_base_url == "http://ollama-test:11434"
    assert settings.ollama_chat_model == "test-chat"
    assert settings.ollama_embedding_model == "test-embedding"
    assert settings.chroma_host == "test-chroma"
    assert settings.chroma_port == 8124
    assert settings.chroma_collection == "test_collection"


def test_settings_use_local_development_defaults(monkeypatch):
    settings = Settings()

    assert settings.env == "development"
    assert settings.backend_host == "0.0.0.0"
    assert settings.backend_port == 8000
    assert settings.ai_provider == "ollama"
    assert settings.openai_api_key is None
    assert settings.openai_model == "gpt-4o-mini"
    assert settings.openai_embedding_model == "text-embedding-3-small"
    assert settings.ollama_base_url == "http://host.docker.internal:11434"
    assert settings.ollama_chat_model == "llama3.2"
    assert settings.ollama_embedding_model == "nomic-embed-text"
    assert settings.chroma_host == "localhost"
    assert settings.chroma_port == 8001
    assert settings.chroma_collection == "knowledge_base"


def test_settings_accept_supported_ai_providers(monkeypatch):
    for provider in ("ollama", "openai"):
        monkeypatch.setenv("AI_PROVIDER", provider)
        assert Settings().ai_provider == provider


def test_settings_normalize_ai_provider_case(monkeypatch):
    for provider in ("OLLAMA", "OpenAI"):
        monkeypatch.setenv("AI_PROVIDER", provider)
        assert Settings().ai_provider == provider.lower()


def test_settings_reject_unsupported_ai_provider(monkeypatch):
    monkeypatch.setenv("AI_PROVIDER", "anthropic")

    with pytest.raises(ValidationError, match="AI_PROVIDER must be either 'ollama' or 'openai'"):
        Settings()
