import pytest

from app.rag import INFORMATION_UNAVAILABLE, RAGResponse, answer_question
from app.vector_store import RetrievedChunk


class FakeVectorStore:
    def __init__(self, chunks):
        self.chunks = chunks
        self.search_calls = []

    def search(self, query, top_k):
        self.search_calls.append({"query": query, "top_k": top_k})
        return self.chunks


def sample_chunks():
    return [
        RetrievedChunk(
            chunk_id="authentication-0",
            document="authentication",
            title="Authentication Guide",
            text="OAuth redirects must use HTTPS.",
            distance=0.12,
        ),
        RetrievedChunk(
            chunk_id="authentication-1",
            document="authentication",
            title="Authentication Guide",
            text="Rotate credentials every 90 days.",
            distance=0.2,
        ),
    ]


def test_answer_question_searches_and_passes_grounded_prompt_to_llm():
    chunks = sample_chunks()
    vector_store = FakeVectorStore(chunks)
    prompts = []

    def fake_answer_generator(prompt):
        prompts.append(prompt)
        return "Use HTTPS for OAuth redirect URLs."

    response = answer_question(
        "What should OAuth redirect URLs use?",
        vector_store,
        top_k=2,
        answer_generator=fake_answer_generator,
    )

    assert vector_store.search_calls == [
        {"query": "What should OAuth redirect URLs use?", "top_k": 2}
    ]
    assert "OAuth redirects must use HTTPS." in prompts[0]
    assert "Rotate credentials every 90 days." in prompts[0]
    assert "Do not invent facts." in prompts[0]
    assert "authentication-0" not in prompts[0]
    assert "Authentication Guide" not in prompts[0]

    assert response.answer == "Use HTTPS for OAuth redirect URLs."
    assert response.sources == chunks
    assert response.sources[0].distance == 0.12

def test_no_retrieved_chunks_returns_unavailable_without_calling_llm():
    vector_store = FakeVectorStore([])
    llm_calls = []

    response = answer_question(
        "What is the retention period?",
        vector_store,
        answer_generator=lambda prompt: llm_calls.append(prompt),
    )

    assert response == RAGResponse(answer=INFORMATION_UNAVAILABLE, sources=[])
    assert llm_calls == []


def test_rag_sources_are_typed_retrieved_chunks_not_raw_store_data():
    chunks = sample_chunks()
    response = answer_question(
        "When should credentials rotate?",
        FakeVectorStore(chunks),
        answer_generator=lambda prompt: "Every 90 days.",
    )

    assert all(isinstance(source, RetrievedChunk) for source in response.sources)
    assert [
        (source.chunk_id, source.document, source.title, source.distance)
        for source in response.sources
    ] == [
        ("authentication-0", "authentication", "Authentication Guide", 0.12),
        ("authentication-1", "authentication", "Authentication Guide", 0.2),
    ]


def test_empty_question_raises_clear_error():
    with pytest.raises(ValueError, match="question must not be empty"):
        answer_question(" \n\t ", FakeVectorStore([]))