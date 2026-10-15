# Task 7 - FastAPI HTTP API

## Task name / goal
Expose the existing RAG answer flow through synchronous FastAPI health and chat endpoints.

## Prompt / instructions given
**Prompt summary:** Add `GET /health` and `POST /chat`, define typed Pydantic request/response models, validate invalid questions, and make the RAG function overrideable in API tests. Do not add frontend, Docker, or new RAG/retrieval behavior.

## Implementation summary
- Added a healthy status response at `GET /health`.
- Added synchronous `POST /chat`, which calls the injected `answer_question()` function and converts its result to API response models.
- Updated `SourceReference` to expose `chunk_id`, `document`, `title`, and `distance`; source dataclasses are explicitly mapped rather than used as response models.
- Added API tests using FastAPI's `TestClient` and a fake RAG dependency.

## Files changed
- `backend/app/main.py`
- `backend/app/models.py`
- `backend/tests/test_main.py`
- `ai-conversations/copilot-task-7.md`

## Tests run and actual result
`python -m pytest tests -q` from `backend/`: **31 passed**. The suite emitted two deprecation warnings from the installed Starlette/TestClient dependencies. API tests used a fake RAG function; no OpenAI or ChromaDB calls were made.

## Important decisions / assumptions
The RAG function is supplied through a FastAPI dependency so tests can replace it without patching orchestration. The existing `ChatRequest` validator strips and rejects empty or whitespace-only questions. The health response is `{"status": "healthy"}`.

## Corrections or limitations
The existing request model already validated whitespace-only questions; it was retained. The response source schema was updated to the fields required by the API. Only the dependency-stack deprecation warnings remain; tests pass.
