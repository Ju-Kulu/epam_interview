import pytest
from fastapi.testclient import TestClient

from app.main import app, get_rag_function
from app.rag import RAGResponse
from app.vector_store import RetrievedChunk


@pytest.fixture
def client():
    app.dependency_overrides.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_health_returns_healthy_status(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_chat_calls_rag_and_returns_api_response(client):
    calls = []
    rag_response = RAGResponse(
        answer="OAuth redirect URLs must use HTTPS.",
        sources=[
            RetrievedChunk(
                chunk_id="authentication-0",
                document="authentication",
                title="Authentication Guide",
                text="Use HTTPS redirect URLs.",
                distance=0.14,
            )
        ],
    )

    def fake_rag(question):
        calls.append(question)
        return rag_response

    app.dependency_overrides[get_rag_function] = lambda: fake_rag

    response = client.post(
        "/chat", json={"question": "What should OAuth redirect URLs use?"}
    )

    assert response.status_code == 200
    assert calls == ["What should OAuth redirect URLs use?"]
    assert response.json() == {
        "answer": "OAuth redirect URLs must use HTTPS.",
        "sources": [
            {
                "chunk_id": "authentication-0",
                "document": "authentication",
                "title": "Authentication Guide",
                "distance": 0.14,
            }
        ],
    }
    assert "text" not in response.json()["sources"][0]


@pytest.mark.parametrize("question", ["", " \n\t "])
def test_chat_rejects_empty_or_whitespace_question(client, question):
    response = client.post("/chat", json={"question": question})

    assert response.status_code == 422


@pytest.mark.parametrize("body", [{}, {"question": 123}, None])
def test_chat_rejects_invalid_request_body(client, body):
    response = client.post("/chat", json=body)

    assert response.status_code == 422