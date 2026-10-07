from types import SimpleNamespace

from app.config import Settings
from app.ingestion import DocumentChunk
from app.vector_store import VectorStore


class FakeCollection:
    def __init__(self):
        self.records = {}

    def upsert(self, ids, embeddings, documents, metadatas):
        for record_id, embedding, document, metadata in zip(
            ids, embeddings, documents, metadatas
        ):
            self.records[record_id] = {
                "embedding": embedding,
                "document": document,
                "metadata": metadata,
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