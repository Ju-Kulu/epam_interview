from functools import lru_cache
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings placeholder.

    Real configuration values will be wired in once the backend implementation starts.
    """

    app_name: str = "enterprise-kb-rag-chatbot"
    env: str = "development"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    openai_api_key: str | None = Field(default=None, description="API key for the LLM provider.")
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    chroma_host: str = "localhost"
    chroma_port: int = 8001
    chroma_collection: str = "knowledge_base"
    chroma_persist_directory: str = "./chroma_data"


@lru_cache
def get_settings() -> Settings:
    return Settings()
