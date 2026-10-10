from functools import lru_cache
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        populate_by_name=True,
        extra="ignore",
    )

    app_name: str = "enterprise-kb-rag-chatbot"
    env: str = Field(default="development", validation_alias="APP_ENV")
    ai_provider: str = Field(default="ollama")
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    openai_api_key: str | None = Field(default=None, description="API key for the LLM provider.")
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    ollama_base_url: str = "http://host.docker.internal:11434"
    ollama_chat_model: str = "llama3.2"
    ollama_embedding_model: str = "nomic-embed-text"
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection: str = "knowledge_base"

    @field_validator("ai_provider", mode="before")
    @classmethod
    def validate_ai_provider(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("AI_PROVIDER must be either 'ollama' or 'openai'.")

        provider = value.strip().lower()
        if provider not in {"ollama", "openai"}:
            raise ValueError("AI_PROVIDER must be either 'ollama' or 'openai'.")
        return provider


@lru_cache
def get_settings() -> Settings:
    return Settings()
