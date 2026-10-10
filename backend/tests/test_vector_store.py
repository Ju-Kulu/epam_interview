import sys
from types import SimpleNamespace

import httpx
import pytest

from app.config import Settings
from app.ingestion import DocumentChunk
from app.vector_store import RetrievedChunk, VectorStore


class FakeCollection:
    def __init__(self):
        self.records = {}
        self.query_calls = []
        self.get_calls = []
        self.delete_calls = []
        self.fail_upsert = False

    def upsert(self, ids, embeddings, documents, metadatas):
        if self.fail_upsert:
            raise RuntimeError("upsert failed")
        for record_id, embedding, document, metadata in zip(
            ids, embeddings, documents, metadatas
        ):
            self.records[record_id] = {
                "embedding": embedding,
                "document": document,
                "metadata": metadata,
            }

    def get(self, where, include):
        self.get_calls.append({"where": where, "include": include})
        matching = [
            (record_id, record)
            for record_id, record in self.records.items()
            if record["metadata"].get("document") == where["document"]
        ]
        return {
            "ids": [record_id for record_id, _ in matching],
            "metadatas": [record["metadata"] for _, record in matching],
        }

    def delete(self, ids):
        self.delete_calls.append(list(ids))
        for record_id in ids:
            self.records.pop(record_id, None)

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


class FakeHttpResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            request = httpx.Request("POST", "http://ollama-test/api/embed")
            response = httpx.Response(self.status_code, request=request)
            raise httpx.HTTPStatusError("Ollama request failed", request=request, response=response)

    def json(self):
        return self.payload


def test_index_chunks_preserves_ids_documents_and_metadata():
    settings = Settings(
        ai_provider="openai",
        openai_api_key="test-key",
        chroma_collection="test_knowledge_base",
    )
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

    assert chroma.collection_name.startswith("test_knowledge_base_openai_")
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
    settings = Settings(
        ai_provider="openai",
        openai_api_key="test-key",
        openai_embedding_model="configured-embedding-model",
    )
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
    store.search("Invoice retry configuration")

    assert [call["model"] for call in openai.calls] == [
        "configured-embedding-model",
        "configured-embedding-model",
    ]
    assert openai.calls[0]["input"] == ["Invoice retry configuration"]
    assert openai.calls[1]["input"] == ["Invoice retry configuration"]


def test_repeated_indexing_upserts_existing_chunk_ids():
    chroma = FakeChromaClient()
    store = VectorStore(
        Settings(ai_provider="openai", openai_api_key="test-key"),
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


def test_reindexing_removes_stale_chunks_and_preserves_unrelated_documents():
    chroma = FakeChromaClient()
    store = VectorStore(
        Settings(ai_provider="openai", openai_api_key="test-key"),
        chroma_client=chroma,
        openai_client=FakeOpenAIClient(),
    )
    store.index_chunks(
        [
            DocumentChunk("auth-0", "authentication", "Authentication", "old first"),
            DocumentChunk("auth-1", "authentication", "Authentication", "old second"),
            DocumentChunk("payments-0", "payments", "Payments", "payment info"),
        ]
    )

    store.index_chunks(
        [
            DocumentChunk("auth-0", "authentication", "Authentication", "updated first"),
            DocumentChunk("auth-2", "authentication", "Authentication", "new second"),
        ]
    )

    records = chroma.collection.records
    assert set(records) == {"auth-0", "auth-2", "payments-0"}
    assert records["auth-0"]["document"] == "updated first"
    assert records["auth-2"]["metadata"] == {
        "document": "authentication",
        "title": "Authentication",
        "chunk_id": "auth-2",
    }
    assert chroma.collection.delete_calls == [["auth-1"]]


def test_embedding_failure_does_not_modify_existing_records(monkeypatch):
    chroma = FakeChromaClient()
    store = VectorStore(
        Settings(ai_provider="openai", openai_api_key="test-key"),
        chroma_client=chroma,
        openai_client=FakeOpenAIClient(),
    )
    existing_chunk = DocumentChunk("auth-0", "authentication", None, "existing")
    store.index_chunks([existing_chunk])
    existing_records = dict(chroma.collection.records)
    monkeypatch.setattr(
        store,
        "_embed_texts",
        lambda texts: (_ for _ in ()).throw(RuntimeError("embedding failed")),
    )

    with pytest.raises(RuntimeError, match="embedding failed"):
        store.index_chunks(
            [DocumentChunk("auth-1", "authentication", None, "replacement")]
        )

    assert chroma.collection.records == existing_records
    assert chroma.collection.delete_calls == []


def test_upsert_failure_does_not_attempt_stale_deletion():
    chroma = FakeChromaClient()
    store = VectorStore(
        Settings(ai_provider="openai", openai_api_key="test-key"),
        chroma_client=chroma,
        openai_client=FakeOpenAIClient(),
    )
    existing_chunk = DocumentChunk("auth-0", "authentication", None, "existing")
    store.index_chunks([existing_chunk])
    existing_records = dict(chroma.collection.records)
    chroma.collection.fail_upsert = True

    with pytest.raises(RuntimeError, match="upsert failed"):
        store.index_chunks(
            [DocumentChunk("auth-1", "authentication", None, "replacement")]
        )

    assert chroma.collection.records == existing_records
    assert chroma.collection.delete_calls == []


def test_empty_indexing_does_not_read_or_modify_collection():
    chroma = FakeChromaClient()
    store = VectorStore(
        Settings(ai_provider="openai", openai_api_key="test-key"),
        chroma_client=chroma,
        openai_client=FakeOpenAIClient(),
    )
    store.index_chunks(
        [DocumentChunk("auth-0", "authentication", None, "existing")]
    )
    existing_records = dict(chroma.collection.records)
    gets_before = len(chroma.collection.get_calls)

    store.index_chunks([])

    assert chroma.collection.records == existing_records
    assert chroma.collection.delete_calls == []
    assert len(chroma.collection.get_calls) == gets_before


def test_repeated_indexing_is_idempotent_and_preserves_current_records():
    chroma = FakeChromaClient()
    store = VectorStore(
        Settings(ai_provider="openai", openai_api_key="test-key"),
        chroma_client=chroma,
        openai_client=FakeOpenAIClient(),
    )
    chunks = [
        DocumentChunk("auth-0", "authentication", "Authentication", "first"),
        DocumentChunk("auth-1", "authentication", "Authentication", "second"),
    ]

    store.index_chunks(chunks)
    records_after_first_index = dict(chroma.collection.records)
    store.index_chunks(chunks)

    assert chroma.collection.records == records_after_first_index
    assert set(chroma.collection.records) == {"auth-0", "auth-1"}


def test_search_embeds_query_and_returns_typed_results():
    settings = Settings(
        ai_provider="openai",
        openai_api_key="test-key",
        openai_embedding_model="configured-embedding-model",
    )
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


def test_ollama_embeddings_use_configured_url_and_model_for_index_and_search(monkeypatch):
    calls = []
    chroma = FakeChromaClient()
    settings = Settings(
        ai_provider="ollama",
        ollama_base_url="http://ollama-test:11434/",
        ollama_embedding_model="embed-test:latest",
    )

    def fake_post(url, json, timeout):
        calls.append((url, json))
        return FakeHttpResponse({"embeddings": [[0.1, 0.2]]})

    monkeypatch.setattr("app.vector_store.httpx.post", fake_post)
    store = VectorStore(settings, chroma_client=chroma)
    chunk = DocumentChunk(
        chunk_id="authentication-0",
        document="authentication",
        title="Authentication",
        text="OAuth setup",
    )

    store.index_chunks([chunk])
    store.search("How do I set up OAuth?")

    assert calls == [
        (
            "http://ollama-test:11434/api/embed",
            {"model": "embed-test:latest", "input": ["OAuth setup"]},
        ),
        (
            "http://ollama-test:11434/api/embed",
            {"model": "embed-test:latest", "input": ["How do I set up OAuth?"]},
        ),
    ]
    assert chroma.collection.records["authentication-0"]["embedding"] == [0.1, 0.2]


def test_ollama_embedding_errors_are_actionable(monkeypatch):
    settings = Settings(ai_provider="ollama")
    store = VectorStore(settings, chroma_client=FakeChromaClient())
    monkeypatch.setattr(
        "app.vector_store.httpx.post",
        lambda *args, **kwargs: FakeHttpResponse({}, status_code=503),
    )

    with pytest.raises(RuntimeError, match="Verify Ollama is running"):
        store.index_chunks(
            [DocumentChunk("authentication-0", "authentication", None, "OAuth")]
        )


def test_invalid_embedding_response_is_rejected(monkeypatch):
    store = VectorStore(
        Settings(ai_provider="ollama"),
        chroma_client=FakeChromaClient(),
    )
    monkeypatch.setattr(
        "app.vector_store.httpx.post",
        lambda *args, **kwargs: FakeHttpResponse({"embeddings": [[]]}),
    )

    with pytest.raises(RuntimeError, match="empty or invalid embedding"):
        store.index_chunks(
            [DocumentChunk("authentication-0", "authentication", None, "OAuth")]
        )


def test_openai_embedding_requires_key():
    with pytest.raises(ValueError, match="OPENAI_API_KEY is required"):
        VectorStore(
            Settings(ai_provider="openai"),
            chroma_client=FakeChromaClient(),
        )


def test_openai_embedding_failure_is_actionable(monkeypatch):
    openai = FakeOpenAIClient()

    def fail_embedding(model, input):
        raise RuntimeError("provider unavailable")

    monkeypatch.setattr(openai.embeddings, "create", fail_embedding)
    store = VectorStore(
        Settings(ai_provider="openai", openai_api_key="test-key"),
        chroma_client=FakeChromaClient(),
        openai_client=openai,
    )

    with pytest.raises(RuntimeError, match="OpenAI embedding request failed"):
        store.index_chunks(
            [DocumentChunk("authentication-0", "authentication", None, "OAuth")]
        )


def test_invalid_openai_embedding_response_is_rejected(monkeypatch):
    openai = FakeOpenAIClient()
    monkeypatch.setattr(
        openai,
        "create",
        lambda model, input: SimpleNamespace(
            data=[SimpleNamespace(embedding=[float("nan")])]
        ),
    )
    store = VectorStore(
        Settings(ai_provider="openai", openai_api_key="test-key"),
        chroma_client=FakeChromaClient(),
        openai_client=openai,
    )

    with pytest.raises(RuntimeError, match="non-numeric embedding values"):
        store.index_chunks(
            [DocumentChunk("authentication-0", "authentication", None, "OAuth")]
        )


def test_embedding_collections_are_isolated_by_provider_and_model():
    settings = [
        Settings(
            ai_provider="openai",
            openai_api_key="test-key",
            openai_embedding_model="embedding-a",
        ),
        Settings(
            ai_provider="openai",
            openai_api_key="test-key",
            openai_embedding_model="embedding-b",
        ),
        Settings(ai_provider="ollama", ollama_embedding_model="embedding-a"),
    ]
    collection_names = []

    for setting in settings:
        chroma = FakeChromaClient()
        VectorStore(
            setting,
            chroma_client=chroma,
            openai_client=FakeOpenAIClient() if setting.ai_provider == "openai" else None,
        )
        collection_names.append(chroma.collection_name)

    assert len(set(collection_names)) == 3
    assert all(name.startswith("knowledge_base_") for name in collection_names)
