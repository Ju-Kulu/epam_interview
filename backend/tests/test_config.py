from app.config import Settings


def test_settings_read_values_from_environment(monkeypatch):
    environment = {
        "APP_ENV": "test",
        "BACKEND_HOST": "127.0.0.1",
        "BACKEND_PORT": "8123",
        "OPENAI_API_KEY": "test-key",
        "OPENAI_MODEL": "test-chat-model",
        "OPENAI_EMBEDDING_MODEL": "test-embedding-model",
        "CHROMA_HOST": "test-chroma",
        "CHROMA_PORT": "8124",
        "CHROMA_COLLECTION": "test_collection",
    }
    for name, value in environment.items():
        monkeypatch.setenv(name, value)

    settings = Settings()

    assert settings.env == "test"
    assert settings.backend_host == "127.0.0.1"
    assert settings.backend_port == 8123
    assert settings.openai_api_key == "test-key"
    assert settings.openai_model == "test-chat-model"
    assert settings.openai_embedding_model == "test-embedding-model"
    assert settings.chroma_host == "test-chroma"
    assert settings.chroma_port == 8124
    assert settings.chroma_collection == "test_collection"


def test_settings_use_local_development_defaults(monkeypatch):
    for name in (
        "APP_ENV",
        "BACKEND_HOST",
        "BACKEND_PORT",
        "OPENAI_API_KEY",
        "OPENAI_MODEL",
        "OPENAI_EMBEDDING_MODEL",
        "CHROMA_HOST",
        "CHROMA_PORT",
        "CHROMA_COLLECTION",
    ):
        monkeypatch.delenv(name, raising=False)

    settings = Settings()

    assert settings.env == "development"
    assert settings.backend_host == "0.0.0.0"
    assert settings.backend_port == 8000
    assert settings.openai_api_key is None
    assert settings.openai_model == "gpt-4o-mini"
    assert settings.openai_embedding_model == "text-embedding-3-small"
    assert settings.chroma_host == "localhost"
    assert settings.chroma_port == 8001
    assert settings.chroma_collection == "knowledge_base"