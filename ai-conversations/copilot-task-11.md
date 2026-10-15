# Task 11 - Configuration and Docker/Chroma Integration

## Task name and goal
Read application settings from environment variables and connect the backend container to the dedicated ChromaDB service over HTTP.

## Prompt summary
Use `pydantic-settings` for the required environment values, change `VectorStore` to Chroma's HTTP client while preserving client injection, correct local versus Compose Chroma addresses, and add focused configuration tests. Do not change RAG, retrieval behavior, API, frontend, or Docker architecture.

## Implementation / result
- Converted `Settings` to `pydantic_settings.BaseSettings`, mapped `APP_ENV` explicitly, and retained sensible local defaults including `localhost:8001` for Chroma.
- Added the pinned `pydantic-settings` dependency and removed the no-longer-used persistent-directory setting.
- Changed default Chroma construction to `chromadb.HttpClient(host, port)`; existing fake client injection remains supported.
- Compose now sets the backend's Chroma address to `chromadb:8000`; the host mapping remains `8001:8000`, the named volume and frontend proxy are retained.
- `.env.example` uses local Chroma values (`localhost:8001`) and `VITE_API_PROXY_TARGET`.

## Files changed
- `.env.example`
- `docker-compose.yml`
- `backend/app/config.py`
- `backend/app/vector_store.py`
- `backend/requirements.txt`
- `backend/tests/test_config.py`
- `backend/tests/test_vector_store.py`
- `ai-conversations/copilot-task-11.md`

The removal of Compose's obsolete `version` field and the `VITE_API_PROXY_TARGET` variable were already present as user edits before this task; they were preserved.

## Tests and result
From `backend/`, `python -m pytest tests -q`: **39 passed, 2 warnings**. The warnings are existing Starlette/TestClient deprecations. Tests use fake clients and make no ChromaDB or OpenAI calls.

## Important decisions / assumptions
Local development uses Chroma at `localhost:8001`; Compose overrides the backend container to use the Chroma service name and its internal port, `chromadb:8000`. `APP_ENV` is an alias for the existing `Settings.env` field.

## Corrections / limitations
A first full-suite invocation was made from the repository root, where `tests/` is absent; rerunning from `backend/` passed. A duplicate HTTP-client test definition was found during review and removed, retaining a single test that verifies configured host and port. The editor reports unresolved `chromadb` and `openai` imports in its selected interpreter; the dependencies remain declared, and the test suite passes with fake clients.
