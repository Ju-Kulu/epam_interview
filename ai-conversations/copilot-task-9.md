# Task 9 - Application Startup Indexing

## Task name / goal
Run knowledge-base indexing when the FastAPI application starts so indexed chunks are ready for `/chat`.

## Prompt summary
Use the existing `index_knowledge_base()` from a modern FastAPI lifespan, without duplicating ingestion or indexing logic. Keep startup testable without external services and leave endpoints, RAG, frontend, and Docker behavior unchanged.

## Implementation / result
Added an `asynccontextmanager` lifespan to `backend/app/main.py` that calls `index_knowledge_base()` before the application serves requests. API tests monkeypatch that function so TestClient startup does not construct real OpenAI or ChromaDB clients. Added a focused test confirming startup invokes indexing once; existing health and chat tests continue to pass.

## Files changed
- `backend/app/main.py`
- `backend/tests/test_main.py`
- `ai-conversations/copilot-task-9.md`

## Tests and results
From `backend/`, `python -m pytest tests -q`: **36 passed, 2 warnings**. Warnings are deprecations from the installed Starlette/TestClient stack. Tests use a monkeypatched indexing function and make no external service calls.

## Important decisions / assumptions
The existing indexing function is synchronous, so the lifespan calls it directly during startup. This keeps the startup flow simple and ensures indexing completes before the app is ready.

## Corrections
No implementation corrections were needed after the focused and full test runs.
