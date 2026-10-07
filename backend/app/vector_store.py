"""Persistent ChromaDB storage for embedded document chunks."""

from typing import Any

from app.config import Settings, get_settings
from app.ingestion import DocumentChunk


class VectorStore:
    def __init__(
        self,
        settings: Settings | None = None,
        *,
        chroma_client: Any | None = None,
        openai_client: Any | None = None,
    ) -> None:
        self.settings = settings or get_settings()

        if chroma_client is None:
            import chromadb

            chroma_client = chromadb.PersistentClient(
                path=self.settings.chroma_persist_directory
            )

        if openai_client is None:
            from openai import OpenAI

            openai_client = OpenAI(api_key=self.settings.openai_api_key)

        self._openai_client = openai_client
        self._collection = chroma_client.get_or_create_collection(
            name=self.settings.chroma_collection
        )

    def index_chunks(self, chunks: list[DocumentChunk]) -> None:
        """Embed and upsert chunks, using their deterministic IDs as record IDs."""
        if not chunks:
            return

        texts = [chunk.text for chunk in chunks]
        response = self._openai_client.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=texts,
        )
        self._collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            embeddings=[item.embedding for item in response.data],
            documents=texts,
            metadatas=[
                {
                    "document": chunk.document,
                    "title": chunk.title or "",
                    "chunk_id": chunk.chunk_id,
                }
                for chunk in chunks
            ],
        )