"""ChromaDB HTTP storage for embedded document chunks."""

import hashlib
import math
from dataclasses import dataclass
from typing import Any

import httpx

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

        if self.settings.ai_provider == "openai":
            if not self.settings.openai_api_key or not self.settings.openai_api_key.strip():
                raise ValueError("OPENAI_API_KEY is required when AI_PROVIDER is 'openai'.")
            if openai_client is None:
                try:
                    from openai import OpenAI

                    openai_client = OpenAI(api_key=self.settings.openai_api_key)
                except Exception as exc:
                    raise RuntimeError(
                        "Could not initialize the OpenAI embedding client. Verify "
                        "OPENAI_API_KEY and the OpenAI SDK installation."
                    ) from exc
        elif self.settings.ai_provider != "ollama":
            raise ValueError(f"Unsupported AI_PROVIDER '{self.settings.ai_provider}'.")

        self._openai_client = openai_client

        if chroma_client is None:
            import chromadb

            chroma_client = chromadb.HttpClient(
                host=self.settings.chroma_host,
                port=self.settings.chroma_port,
            )

        self._collection = chroma_client.get_or_create_collection(
            name=self._embedding_collection_name()
        )

    def _embedding_collection_name(self) -> str:
        if self.settings.ai_provider == "ollama":
            model = self.settings.ollama_embedding_model
        else:
            model = self.settings.openai_embedding_model
        fingerprint = hashlib.sha256(
            f"{self.settings.ai_provider}:{model}".encode("utf-8")
        ).hexdigest()[:12]
        return f"{self.settings.chroma_collection}_{self.settings.ai_provider}_{fingerprint}"

    def _embed_texts(self, texts: list[str]) -> list[list[float]]:
        if self.settings.ai_provider == "ollama":
            endpoint = f"{self.settings.ollama_base_url.rstrip('/')}/api/embed"
            try:
                response = httpx.post(
                    endpoint,
                    json={"model": self.settings.ollama_embedding_model, "input": texts},
                    timeout=60.0,
                )
                response.raise_for_status()
                payload = response.json()
            except (httpx.HTTPError, ValueError) as exc:
                raise RuntimeError(
                    f"Ollama embedding request failed at {endpoint}. Verify Ollama is "
                    f"running and model '{self.settings.ollama_embedding_model}' is available."
                ) from exc
            embeddings = payload.get("embeddings") if isinstance(payload, dict) else None
        else:
            try:
                response = self._openai_client.embeddings.create(
                    model=self.settings.openai_embedding_model,
                    input=texts,
                )
                embeddings = [item.embedding for item in response.data]
            except Exception as exc:
                raise RuntimeError(
                    f"OpenAI embedding request failed with model "
                    f"'{self.settings.openai_embedding_model}'. Verify OPENAI_API_KEY, "
                    "model access, and network connectivity."
                ) from exc

        return self._validate_embeddings(embeddings, expected_count=len(texts))

    def _validate_embeddings(self, embeddings: Any, expected_count: int) -> list[list[float]]:
        if not isinstance(embeddings, list) or len(embeddings) != expected_count:
            raise RuntimeError(
                f"{self.settings.ai_provider} returned an invalid number of embeddings; "
                "verify the embedding service response."
            )

        validated = []
        for embedding in embeddings:
            if not isinstance(embedding, list) or not embedding:
                raise RuntimeError(
                    f"{self.settings.ai_provider} returned an empty or invalid embedding."
                )
            if any(
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
                for value in embedding
            ):
                raise RuntimeError(
                    f"{self.settings.ai_provider} returned non-numeric embedding values."
                )
            validated.append([float(value) for value in embedding])
        return validated

    def index_chunks(self, chunks: list[DocumentChunk]) -> None:
        """Upsert chunks and remove obsolete chunks for represented documents."""
        if not chunks:
            return

        texts = [chunk.text for chunk in chunks]
        embeddings = self._embed_texts(texts)
        incoming_ids_by_document: dict[str, set[str]] = {}
        for chunk in chunks:
            incoming_ids_by_document.setdefault(chunk.document, set()).add(chunk.chunk_id)

        self._collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            embeddings=embeddings,
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

        for document, incoming_ids in incoming_ids_by_document.items():
            existing = self._collection.get(
                where={"document": document},
                include=["metadatas"],
            )
            stale_ids = [
                chunk_id
                for chunk_id, metadata in zip(existing["ids"], existing["metadatas"])
                if chunk_id not in incoming_ids
                and metadata
                and metadata.get("document") == document
            ]
            if stale_ids:
                self._collection.delete(ids=stale_ids)

    def search(self, query: str, top_k: int = 3) -> list[RetrievedChunk]:
        """Return the nearest stored chunks for a query."""
        if not query.strip():
            raise ValueError("query must not be empty or whitespace-only.")
        if top_k <= 0:
            raise ValueError("top_k must be greater than 0.")

        query_embedding = self._embed_texts([query])[0]
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
