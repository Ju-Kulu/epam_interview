# Task 13 - Configurable Ollama/OpenAI Providers

## Task name and goal

Implement runtime provider selection for chat generation and embeddings, and isolate ChromaDB collections by provider and embedding model.

## Prompt summary

Implement configurable AI provider support for both chat generation and text embeddings, supporting Ollama and OpenAI. Add provider-specific model configuration, handle provider API requests and errors, and isolate ChromaDB collections by embedding provider and model to prevent mixing incompatible embeddings. Preserve existing RAG behavior and API contracts, add tests for provider-specific functionality and error handling, and update relevant configuration and documentation.

## Constraints
- Do not change the frontend or the `/chat` API contract.
- Do not rewrite the RAG pipeline or retrieval algorithm.
- Do not delete existing ChromaDB data.
- Do not add an OpenAI dependency if the project already has a suitable one.
- Do not add a new testing framework.
- Do not commit changes.
- Do not start another task automatically.
Before finishing, show the code diff, the complete Task 13 conversation log, and the actual test results. If any requirement cannot be safely implemented within this scope, explain the blocker rather than silently omitting it.

## Implementation / result
- `generate_answer()` now selects Ollama (`/api/chat`) or OpenAI based on `settings.ai_provider`, using the corresponding configured model and URL/key. Missing OpenAI keys, initialization/network failures, and empty responses raise clear errors.
- `VectorStore` routes indexing and query text through a shared provider-aware embedding method. Ollama uses the `/api/embed` endpoint through the already-declared `httpx` dependency; OpenAI uses the existing SDK. Invalid vector counts, empty vectors, and non-finite/non-numeric values are rejected.
- Chroma collection names now include the configured base name, provider, and a stable hash of the embedding model. This prevents mixing incompatible embedding spaces while leaving prior collections untouched.
- Tests use fake OpenAI clients and mocked Ollama HTTP responses; no live providers are required by the passing test suite.

## Files changed
- `backend/app/llm.py`
- `backend/app/vector_store.py`
- `backend/tests/test_llm.py`
- `backend/tests/test_vector_store.py`
- `ai-conversations/copilot-task-13.md`

## Tests and results
All commands were run from `backend/`:

- `python -m pytest tests/test_llm.py -q` - **5 passed**.
- `python -m pytest tests/test_vector_store.py -q` - **16 passed**.
- `python -m pytest tests/test_config.py -q` - **5 passed**.
- `python -m pytest tests -q` - **54 passed, 2 warnings**.

The two warnings are existing Starlette/TestClient deprecations.

## Important decisions and assumptions
- The project already declares `openai` and `httpx`; no dependency was added. Ollama's current `/api/embed` request/response shape (`model`, list `input`, `embeddings`) is used, and chat uses `/api/chat` with `stream: false`.
- A provider/model fingerprint namespaces collections deterministically. Existing collections are not deleted. The legacy unsuffixed collection is not automatically reused because its embedding configuration is not recorded; reindex documents into the provider/model-specific collection after switching providers or embedding models.
- Indexing and searching use the same configured provider/model through the same `_embed_texts()` method.
- The OpenAI key is only required for OpenAI mode; Ollama mode does not initialize an OpenAI client.

## Corrections and limitations
- The first vector-store test run failed because pre-existing tests injected fake OpenAI clients but relied on the new default provider (`ollama`). Those tests attempted the configured local Ollama URL and failed name resolution. The fixtures were updated to select OpenAI explicitly, and Ollama calls are now mocked; the focused and full suites subsequently passed.
- No corrective user prompts were sent during this task.
- The selected editor interpreter reports `openai` and `chromadb` imports unresolved, although both remain declared project dependencies. Provider and full-suite tests use fakes, so no live provider or Chroma service integration was exercised.
- Existing data remains on disk in its original collection; reindexing is required to populate the new provider/model-specific collection.
