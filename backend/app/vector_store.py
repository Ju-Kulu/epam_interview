"""Persistent ChromaDB storage for embedded document chunks."""

from dataclasses import dataclass
from typing import Any

from app.config import Settings, get_settings
from app.ingestion import DocumentChunk


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    document: str
    title: str | None
    text: str
    distance: float


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

    def search(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
        """Return the nearest stored chunks for a query."""
        if not query.strip():
            raise ValueError("query must not be empty or whitespace-only.")
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        response = self._openai_client.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=[query],
        )
        query_embedding = response.data[0].embedding
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        retrieved = []
        for chunk_id, text, metadata, distance in zip(
            results["ids"][0],
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ):
            retrieved.append(
                RetrievedChunk(
                    chunk_id=metadata.get("chunk_id", chunk_id),
                    document=metadata["document"],
                    title=metadata.get("title") or None,
                    text=text,
                    distance=distance,
                )
            )
        return retrieved
