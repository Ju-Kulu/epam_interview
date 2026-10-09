import sys
from types import SimpleNamespace

import pytest

from app.config import Settings
from app.ingestion import DocumentChunk
from app.vector_store import RetrievedChunk, VectorStore


class FakeCollection:
    def __init__(self):
        self.records = {}
        self.query_calls = []

    def upsert(self, ids, embeddings, documents, metadatas):
        for record_id, embedding, document, metadata in zip(
            ids, embeddings, documents, metadatas
        ):
            self.records[record_id] = {
                "embedding": embedding,
                "document": document,
                "metadata": metadata,
            }

    def query(self, query_embeddings, n_results, include):
        self.query_calls.append(
            {
                "query_embeddings": query_embeddings,
                "n_results": n_results,
                "include": include,
            }
        )
        records = list(self.records.items())[:n_results]
        return {
            "ids": [[chunk_id for chunk_id, _ in records]],
            "documents": [[record["document"] for _, record in records]],
            "metadatas": [[record["metadata"] for _, record in records]],
            "distances": [[0.1 + index for index, _ in enumerate(records)]],
        }


class FakeChromaClient:
    def __init__(self):
        self.collection = FakeCollection()
        self.collection_name = None

    def get_or_create_collection(self, name):
        self.collection_name = name
        return self.collection


class FakeOpenAIClient:
    def __init__(self):
        self.calls = []
        self.embeddings = self

    def create(self, model, input):
        self.calls.append({"model": model, "input": input})
        return SimpleNamespace(
            data=[SimpleNamespace(embedding=[float(index)]) for index, _ in enumerate(input)]
        )


def test_index_chunks_preserves_ids_documents_and_metadata():
    settings = Settings(chroma_collection="test_knowledge_base")
    chroma = FakeChromaClient()
    openai = FakeOpenAIClient()
    store = VectorStore(settings, chroma_client=chroma, openai_client=openai)
    chunks = [
        DocumentChunk(
            chunk_id="authentication-0",
            document="authentication",
            title="Authentication",
            text="OAuth configuration",
        )
    ]

    store.index_chunks(chunks)

    assert chroma.collection_name == "test_knowledge_base"
    assert chroma.collection.records == {
        "authentication-0": {
            "embedding": [0.0],
            "document": "OAuth configuration",
            "metadata": {
                "document": "authentication",
                "title": "Authentication",
                "chunk_id": "authentication-0",
            },
        }
    }


def test_default_chroma_client_uses_configured_http_host_and_port(monkeypatch):
    calls = []

    def fake_http_client(host, port):
        calls.append((host, port))
        return FakeChromaClient()

    monkeypatch.setitem(
        sys.modules,
        "chromadb",
        SimpleNamespace(HttpClient=fake_http_client),
    )
    settings = Settings(chroma_host="chroma-service", chroma_port=8123)

    VectorStore(settings, openai_client=FakeOpenAIClient())

    assert calls == [("chroma-service", 8123)]


def test_index_chunks_uses_configured_embedding_model_and_chunk_text():
    settings = Settings(openai_embedding_model="configured-embedding-model")
    openai = FakeOpenAIClient()
    store = VectorStore(
        settings,
        chroma_client=FakeChromaClient(),
        openai_client=openai,
    )
    chunks = [
        DocumentChunk(
            chunk_id="payments-0",
            document="payments",
            title="Payments",
            text="Invoice retry configuration",
        )
    ]

    store.index_chunks(chunks)

    assert openai.calls == [
        {
            "model": "configured-embedding-model",
            "input": ["Invoice retry configuration"],
        }
    ]


def test_repeated_indexing_upserts_existing_chunk_ids():
    chroma = FakeChromaClient()
    store = VectorStore(
        Settings(),
        chroma_client=chroma,
        openai_client=FakeOpenAIClient(),
    )
    chunk = DocumentChunk(
        chunk_id="integrations-0",
        document="integrations",
        title="Integrations",
        text="Webhook settings",
    )

    store.index_chunks([chunk])
    store.index_chunks([chunk])

    assert list(chroma.collection.records) == ["integrations-0"]


def test_search_embeds_query_and_returns_typed_results():
    settings = Settings(openai_embedding_model="configured-embedding-model")
    chroma = FakeChromaClient()
    openai = FakeOpenAIClient()
    store = VectorStore(settings, chroma_client=chroma, openai_client=openai)
    chunks = [
        DocumentChunk(
            chunk_id="authentication-0",
            document="authentication",
            title="Authentication",
            text="Configure OAuth clients.",
        ),
        DocumentChunk(
            chunk_id="payments-0",
            document="payments",
            title="Payments",
            text="Configure billing retries.",
        ),
    ]
    store.index_chunks(chunks)

    results = store.search("How do I configure OAuth?", top_k=1)

    assert openai.calls[-1] == {
        "model": "configured-embedding-model",
        "input": ["How do I configure OAuth?"],
    }
    assert chroma.collection.query_calls == [
        {
            "query_embeddings": [[0.0]],
            "n_results": 1,
            "include": ["documents", "metadatas", "distances"],
        }
    ]
    assert results == [
        RetrievedChunk(
            chunk_id="authentication-0",
            document="authentication",
            title="Authentication",
            text="Configure OAuth clients.",
            distance=0.1,
        )
    ]


@pytest.mark.parametrize("query", ["", " \n\t "])
def test_search_rejects_empty_query(query):
    store = VectorStore(
        Settings(),
        chroma_client=FakeChromaClient(),
        openai_client=FakeOpenAIClient(),
    )

    with pytest.raises(ValueError, match="query must not be empty"):
        store.search(query)


@pytest.mark.parametrize("top_k", [0, -1])
def test_search_rejects_invalid_top_k(top_k):
    store = VectorStore(
        Settings(),
        chroma_client=FakeChromaClient(),
        openai_client=FakeOpenAIClient(),
    )

    with pytest.raises(ValueError, match="top_k must be greater than 0"):
        store.search("valid question", top_k=top_k)
