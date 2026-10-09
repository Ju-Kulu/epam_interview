from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(populate_by_name=True)

    app_name: str = "enterprise-kb-rag-chatbot"
    env: str = Field(default="development", validation_alias="APP_ENV")
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    openai_api_key: str | None = Field(default=None, description="API key for the LLM provider.")
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection: str = "knowledge_base"


@lru_cache
def get_settings() -> Settings:
    return Settings()
