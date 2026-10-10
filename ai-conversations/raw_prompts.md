# TASKS
## Task 1 - Initial project
Create the initial project structure and configuration only. Do not implement RAG, frontend functionality, or API endpoints yet. Context "Enterprise Knowledge Base RAG Chatbot.md"

## Task 2 - Knowledge Base documents and document loader
Continue from the existing project structure.

For this task, implement ONLY the knowledge-base document loading functionality.

### Requirements
We already have four mock enterprise documents in:

`data/`

- `authentication.md`
- `payments.md`
- `integrations.md`
- `troubleshooting.md`
Do not create additional documents unless one of the existing files is clearly missing or invalid.

Implement a small document loader in:

`backend/app/ingestion.py`

The loader should:

1. Read all supported Markdown files from the configured data directory.
2. Return a simple internal representation containing:

- document name
- document title if available
- full document text
3. Validate that the data directory exists.
4. Handle the case where no documents are found with a clear error.
5. Keep the implementation simple and synchronous.
Do NOT implement yet:

- chunking
- embeddings
- ChromaDB
- OpenAI calls
- retrieval
- RAG
- FastAPI endpoints
- frontend changes
- Docker changes

### Design guidance
Use small, readable functions rather than one large function.

If a data model is useful, define an appropriate Pydantic model or simple dataclass for a loaded document.

Avoid unnecessary abstractions.

### Tests
Add unit tests under:

`backend/tests/`

Tests should verify:

1. All four documents can be loaded.
2. The document names are preserved.
3. Document text is not empty.
4. Missing data directory produces a clear error.
5. Empty data directory produces a clear error.
Use temporary directories in tests rather than depending on the real repository data where appropriate.

### Important
Do not modify unrelated files.

After implementing the task:

1. Show a concise summary of files changed.
2. Show the important design decisions.
3. Run the relevant tests.
4. Report the test result.
Do not proceed to chunking or any other RAG functionality.

## Task 3 - Implement ONLY document chunking for the RAG pipeline.

Context:

- Task 2 implemented `load_documents()` in `backend/app/ingestion.py`.
- `LoadedDocument` contains: `name`, `title`, and full `text`.
- Do not implement embeddings, ChromaDB, retrieval, LLM calls, RAG orchestration, API endpoints, frontend, or Docker changes yet.
Goal:
Create a simple, deterministic chunking function that splits loaded knowledge-base documents into smaller chunks suitable for later embedding and retrieval.

Requirements:

1. Add the chunking logic to `backend/app/ingestion.py` or create a small dedicated module if that is cleaner. Prefer keeping it in `ingestion.py` for now unless there is a strong reason not to.
2. Introduce a simple `DocumentChunk` dataclass containing:

- `chunk_id`
- `document`
- `title`
- `text`
3. Implement:
`chunk_documents(documents, chunk_size=500, overlap=50)`
4. Use character-based chunking for simplicity.
5. Chunks should have deterministic IDs, for example:
`authentication-0`, `authentication-1`, etc.
6. Preserve the source document name and title in every chunk.
7. Support overlap between consecutive chunks.
8. Validate invalid parameters:

- `chunk_size` must be greater than 0
- `overlap` must be >= 0
- `overlap` must be smaller than `chunk_size`
9. Do not add external dependencies.
Add unit tests covering:

- one short document produces one chunk
- a long document produces multiple chunks
- chunks preserve document name and title
- chunk IDs are deterministic
- overlap works as expected
- invalid `chunk_size` raises a clear error
- invalid `overlap` raises a clear error
- empty/whitespace-only document text is handled sensibly
Keep the implementation simple and easy to explain in an interview.

After implementation:

- run the relevant tests
- report which files were changed
- briefly explain the chunking approach and its complexity
- do not make any unrelated changes
- STOP and wait for my next instruction.

## Task - Cleanup
Please make only formatting cleanup in the files changed for Task 3:

- remove trailing whitespace
- use 4 spaces consistently
- ensure files end with a newline
- Do not change the implementation or tests.

## Task 4 - Implement ONLY the embedding and vector-store layer for the RAG pipeline.

Context:

- Task 2 implemented `load_documents()`.
- Task 3 implemented `DocumentChunk` and `chunk_documents()`.
- We now need to store document chunks in a local vector store for later retrieval.
- Keep the implementation simple and easy to explain.
- Do not implement retrieval/search, LLM calls, RAG orchestration, FastAPI endpoints, frontend, or Docker changes yet.
Requirements:

1. Add the necessary dependency for ChromaDB and the OpenAI Python SDK to `backend/requirements.txt`.
2. Create a small vector-store module, preferably:
`backend/app/vector_store.py`
3. Implement a simple class responsible for:

- creating/opening a local persistent ChromaDB collection
- generating embeddings for chunks using OpenAI embeddings
- storing chunks together with their metadata
- avoiding accidental duplicate IDs when ingestion is run more than once
4. Use the OpenAI embedding model from configuration rather than hard-coding it. Add an appropriate setting such as:
`openai_embedding_model`
with a sensible default.
5. Keep the OpenAI API key configuration compatible with the existing `Settings`.
6. Store enough metadata to reconstruct the source citation later:

- document
- title
- chunk_id
7. Use the chunk ID as the Chroma document ID.
8. Do not put the OpenAI API key or any real credentials in the repository.
9. Keep the vector-store API small and explicit. For example, a method/function similar to:
`index_chunks(chunks)`
10. Add unit tests where possible without making real OpenAI API calls.
Mock the embedding/OpenAI dependency in tests.
Test at least:

- chunks are converted into vector-store records
- chunk IDs are preserved
- metadata is preserved
- repeated indexing does not create duplicate records
- the embedding dependency is called with the chunk text
- configuration/model selection is respected
11. If ChromaDB's API requires a particular implementation detail, keep it isolated inside `vector_store.py` rather than spreading Chroma-specific code throughout the application.
12. Do not change unrelated files or implement later RAG stages.
After implementation:

- run the relevant tests
- report the files changed
- briefly explain how embeddings and ChromaDB are being used
- mention any assumptions or limitations
- STOP

## Task - AI logs
Before continuing with Task 5, set up the required AI assistant conversation logs for this repository.

EPAM requires the repository to contain logs of AI assistant usage.

Create this directory:

`ai-conversations/`

Create one Markdown file for each completed implementation task:

- `copilot-task-1.md`
- `copilot-task-2.md`
- `copilot-task-3.md`
- `copilot-task-4.md`
For each file, document:

1. Task name / goal
2. The prompt/instructions given to the AI assistant
3. A concise summary of the AI assistant's implementation/result
4. Files changed
5. Tests run and result
6. Any important decisions, assumptions, or corrections
Important:

- Do not copy large amounts of generated source code into the logs.
- The repository itself is the source of truth for the implementation.
- Keep the logs concise but sufficient to demonstrate how AI assistance was used.
- Do not invent prompts or implementation details that are not supported by the repository history or available task context.
- If exact historical prompt text is unavailable, clearly label the section as a summary rather than pretending it is an exact transcript.
- Do not modify application code.
- Do not change tests.
- Do not change the existing README except if a small reference to `ai-conversations/` is necessary.
- Do not create logs for Task 5 yet.
Also add a short `README.md` section describing that `ai-conversations/` contains the AI assistant usage logs required by the assignment.

After completing this:

- show me the files created/changed
- do not modify anything else
- STOP and wait for my review.

## Task 5 Implement ONLY the retrieval/search layer for the RAG pipeline.

Context:

- Task 2: `load_documents()` loads the Markdown knowledge base.
- Task 3: `DocumentChunk` and `chunk_documents()` split documents into chunks.
- Task 4: `VectorStore` embeds chunks with OpenAI and stores them in persistent ChromaDB.
- We now need to retrieve the most relevant chunks for a user's question.
Do NOT implement LLM calls, prompt construction, RAG orchestration, FastAPI endpoints, frontend, or Docker changes yet.

Requirements:

1. Extend `backend/app/vector_store.py` with a small retrieval method, for example:
`search(query: str, top_k: int = 3)`
2. The search method must:

- validate that the query is not empty or whitespace-only
- validate that `top_k` is greater than 0
- create an embedding for the user query using the configured OpenAI embedding model
- query the existing ChromaDB collection for the nearest matching chunks
- return the retrieved chunks in a simple, typed representation
3. Add an appropriate result dataclass, for example:
`RetrievedChunk`

It should contain:

- `chunk_id`
- `document`
- `title`
- `text`
- `distance`
4. Preserve the metadata stored during indexing.
5. Keep ChromaDB-specific response parsing inside `vector_store.py`.
6. Do not expose raw ChromaDB response dictionaries to the rest of the application.
7. Use the same configured embedding model as indexing.
8. Make `top_k` configurable through the function argument, with a sensible default such as 3.
9. Add unit tests using the existing fake Chroma/OpenAI clients. Do not make real API calls.
Tests should cover at least:

- the query text is embedded using the configured embedding model
- the query embedding is passed to ChromaDB
- `top_k` is respected
- returned metadata is converted into `RetrievedChunk`
- distance is preserved
- an empty query raises a clear error
- invalid `top_k` raises a clear error
If necessary, extend the fake clients only inside the tests to support the Chroma query operation.

Keep the implementation simple and easy to explain in an interview.

After implementation:

- run the relevant tests
- report the files changed
- briefly explain the retrieval flow
- do not make unrelated changes
- STOP and wait for my next instruction.

## Task - Create the file `ai-conversations/copilot-task-5.md`.

Do not modify any source code, tests, README, plan, or other files.

This log documents the already completed Retrieval/Search implementation (Task 5).

Include:
- Task name / goal
- Prompt/instructions given to the AI assistant: summarize the retrieval task that was requested
- Implementation summary:
  - added RetrievedChunk dataclass
  - added VectorStore.search()
  - validates query and top_k
  - embeds the user query using the configured embedding model
  - queries ChromaDB for the nearest chunks
  - converts ChromaDB results into typed RetrievedChunk objects
  - preserves metadata and distance
  - keeps ChromaDB-specific parsing inside vector_store.py
- Files changed:
  - backend/app/vector_store.py
  - backend/tests/test_vector_store.py
- Tests:
  - 20 tests passed
  - no real API calls were made
- Important decisions / assumptions:
  - retrieval uses the same embedding model as indexing
  - top_k defaults to 3
  - ChromaDB remains an implementation detail of VectorStore
  - fake clients are used in unit tests

Do not claim anything that was not actually done.
Do not reproduce source code.
Keep the log concise and easy to review.

After creating the file, STOP.

## Task 6 - Implement ONLY Task 6: the RAG orchestration layer.

Context:

- Task 2: `load_documents()` loads the Markdown knowledge base.
- Task 3: `DocumentChunk` and `chunk_documents()` split documents into chunks.
- Task 4: `VectorStore.index_chunks()` embeds and stores chunks in ChromaDB.
- Task 5: `VectorStore.search()` embeds a user question and retrieves the most relevant `RetrievedChunk` objects.
- We now need to connect retrieval with an LLM to produce a grounded answer.
Do NOT implement FastAPI endpoints, frontend changes, Docker changes, or unrelated improvements yet.

### Requirements

1. Implement the RAG orchestration in `backend/app/rag.py`.
2. Add a small, typed result representation for the RAG response if appropriate.
3. The RAG flow should:

- accept a user's question
- call `VectorStore.search()` to retrieve the most relevant chunks
- build an LLM prompt using ONLY the retrieved chunk text as context
- call the existing LLM abstraction in `backend/app/llm.py`
- return the generated answer together with the retrieved source information
4. Keep responsibilities separated:

- `VectorStore` is responsible for embeddings and retrieval
- `rag.py` is responsible for orchestration and prompt construction
- `llm.py` is responsible for communicating with the LLM
- do not put ChromaDB-specific logic into `rag.py`
5. The LLM prompt must clearly instruct the model:

- answer using only the supplied knowledge-base context
- do not invent facts
- if the context does not contain enough information, say that the information is not available in the knowledge base
- do not generate or modify citation metadata
6. Source information must come from the retrieved `RetrievedChunk` objects, not from the LLM.
7. Preserve at least:

- `chunk_id`
- `document`
- `title`
- `distance`
8. Keep the implementation simple and easy to explain in an interview. Do not introduce LangChain, LangGraph, agents, MCP, or other unnecessary frameworks.

### Tests
Add unit tests for the RAG layer using fake/mocked dependencies. Do not make real OpenAI API calls.

Test at least:

- the question is passed to `VectorStore.search()`
- retrieved chunks are included in the LLM prompt
- the LLM receives the expected grounded-context prompt
- the generated answer is returned
- source metadata comes from the retrieved chunks
- the no-results / insufficient-context case is handled appropriately
- the RAG layer does not expose raw ChromaDB responses

### AI conversation log
After the implementation and tests are complete, create:

`ai-conversations/copilot-task-6.md`

This file must document the Task 6 work that you just performed.

Include:

- Task name / goal
- Prompt / instructions given to the AI assistant: concise summary
- Implementation summary
- Files changed
- Tests run and actual result
- Important decisions / assumptions
- Any corrections or limitations
Do not reproduce source code in the log.
Do not invent results or claim tests passed unless you actually ran them.
Do not modify existing `copilot-task-1.md` through `copilot-task-5.md`.

### Final step
After implementation:

1. Run the relevant backend tests.
2. Report the actual test result.
3. Report all files changed.
4. Briefly explain the RAG flow implemented.
5. Confirm that `ai-conversations/copilot-task-6.md` was created.
6. STOP and wait for my next instruction.
Do not make unrelated changes.

## Task 7 - Implement ONLY Task 7: expose the existing RAG pipeline through a FastAPI API.

Context:

- Task 2: Markdown documents can be loaded.
- Task 3: documents are split into `DocumentChunk` objects.
- Task 4: chunks are embedded and indexed in ChromaDB through `VectorStore`.
- Task 5: `VectorStore.search()` retrieves `RetrievedChunk` objects.
- Task 6: `answer_question()` performs the RAG orchestration and returns `RAGResponse`.
- We now need to expose the existing RAG functionality through HTTP.
Do NOT implement frontend changes, Docker changes, new RAG logic, new retrieval logic, or unrelated improvements.

### Requirements

1. Implement the FastAPI application in `backend/app/main.py`.
2. Add:
`GET /health`

It should return a simple JSON response indicating that the service is healthy.

1. Add:
`POST /chat`

Request body:

```
{
  "question": "What should OAuth redirect URLs use?"
}
```
Response should contain:

```
{
  "answer": "...",
  "sources": [...]
}
```

1. Create appropriate Pydantic request/response models in `backend/app/models.py`.
The response source model should expose the source information needed by the API, including:

- `chunk_id`
- `document`
- `title`
- `distance`
Do not expose internal Python dataclasses directly as the FastAPI response model.

1. The `/chat` endpoint must call the existing `answer_question()` function from `rag.py`.
Do not duplicate the RAG flow inside `main.py`.

The responsibility should remain:

- `main.py` → HTTP/API layer
- `models.py` → API request/response schemas
- `rag.py` → RAG orchestration
- `vector_store.py` → retrieval
- `llm.py` → LLM communication

1. Handle invalid/empty questions using appropriate FastAPI/Pydantic validation.
2. Keep the endpoint synchronous for now. Do not introduce unnecessary async/background processing.
3. Make the RAG dependency easy to replace in tests.
For example, use dependency injection or another simple mechanism so `/chat` tests can use a fake RAG function instead of making real OpenAI calls.

### Tests
Add or update API tests using FastAPI's test client and fake dependencies.

Do not make real OpenAI or ChromaDB calls.

Test at least:

- `GET /health` returns HTTP 200 and the expected health response
- `POST /chat` accepts a valid question
- `/chat` calls the RAG layer with the supplied question
- the RAG answer is correctly converted to the API response
- source metadata is correctly returned
- empty/whitespace-only questions are rejected with a client validation error
- invalid request bodies are rejected
- the API does not expose raw `RetrievedChunk` objects or raw ChromaDB response dictionaries
Keep the API implementation simple and easy to explain in an interview.

### AI conversation log
After implementation and tests are complete, create:

`ai-conversations/copilot-task-7.md`

This file must document the Task 7 work that you just performed.

Include:

- Task name / goal
- Prompt / instructions given to the AI assistant: concise summary
- Implementation summary
- Files changed
- Tests run and actual result
- Important decisions / assumptions
- Any corrections or limitations
Do not reproduce source code in the log.
Do not invent test results.
Do not modify existing `copilot-task-1.md` through `copilot-task-6.md`.

### Final step
After implementation:

1. Run the backend test suite.
2. Report the actual test result.
3. Report all files changed.
4. Briefly explain the API flow.
5. Confirm that `ai-conversations/copilot-task-7.md` was created.
6. STOP and wait for my next instruction.
Do not make unrelated changes.


## Task 8 - Knowledge Base Indexing

### Goal
Implement the knowledge-base indexing orchestration layer.

The existing project already has:

- `load_documents()` in `backend/app/ingestion.py`
- `chunk_documents()` in `backend/app/ingestion.py`
- `VectorStore.index_chunks()` in `backend/app/vector_store.py`
Connect these existing pieces through a small, dedicated indexing function.

### Requirements
Create a new module:

`backend/app/indexing.py`

Add a function such as:

```
def index_knowledge_base(
    data_dir: str | Path | None = None,
    vector_store: VectorStore | None = None,
) -> int:
```
The function should:

1. Load Markdown knowledge-base documents using the existing `load_documents()`.
2. Chunk them using the existing `chunk_documents()`.
3. Create/use the provided `VectorStore`.
4. Call `vector_store.index_chunks(chunks)`.
5. Return the number of chunks indexed.
Use dependency injection for `vector_store` so the function can be tested without creating a real Chroma/OpenAI client.

Use the existing default data directory when `data_dir` is not provided.

Do not duplicate document loading, chunking, or embedding logic.

### Tests
Create:

`backend/tests/test_indexing.py`

Use a fake VectorStore.

Test at least:

1. Documents are loaded and chunked, then passed to `index_chunks()`.
2. The returned value is the number of chunks indexed.
3. The provided `data_dir` is passed to the existing ingestion layer.
4. A provided fake VectorStore is used instead of creating a real VectorStore.
5. An empty knowledge base results in `index_chunks([])` and returns `0`, if this is consistent with the existing ingestion/chunking behavior.
Do not make real OpenAI or Chroma calls in tests.

### Scope restrictions
For this task ONLY:

- Do not modify the `/chat` endpoint.
- Do not modify the `/health` endpoint.
- Do not modify the RAG retrieval logic.
- Do not modify the embedding logic.
- Do not add startup/lifespan integration yet.
- Do not modify the frontend.
- Do not modify Docker Compose.
- Do not add new external dependencies.
Keep the implementation small and focused.

### AI conversation log
After completing the task, create:

`ai-conversations/copilot-task-8.md`

Include:

- Task name and goal
- Summary of the prompt/instructions
- Implementation/result
- Files changed
- Tests run and result
- Important decisions or assumptions
- Any corrections made after reviewing the generated code
Do not copy large source-code blocks into the log.

### Validation
Run:

```
python -m pytest tests -q
```
Stop after completing this task and report:

- files changed
- tests result
- any warnings/errors
- brief explanation of the implementation

## Task 9 - Application startup indexing

### Goal
Integrate the existing knowledge-base indexing flow with FastAPI application startup.

The application should index the knowledge base when the FastAPI application starts, so that the `/chat` endpoint can immediately retrieve indexed chunks.

### Existing functionality to reuse
Use the existing:

- `app.indexing.index_knowledge_base()`
- `app.vector_store.VectorStore`
- existing FastAPI app in `app.main`
Do not duplicate document loading, chunking, embedding, or indexing logic.

### Requirements

1. Update `backend/app/main.py` to run `index_knowledge_base()` during FastAPI application startup.
2. Prefer FastAPI's modern lifespan mechanism rather than deprecated startup/shutdown event handlers.
3. Keep the application behavior simple:

- startup runs indexing
- after startup the API is ready to serve `/chat`
4. Make the startup indexing testable without calling real OpenAI or Chroma services.
5. Add focused tests for:

- startup calls `index_knowledge_base()`
- startup does not require real external services in tests
- the existing `/health` and `/chat` tests continue to pass
6. Use monkeypatch/fakes where appropriate rather than real external services.
7. Do not change the RAG implementation, retrieval logic, vector store implementation, frontend, or Docker configuration.
8. Do not introduce a new dependency or abstraction unless it is necessary.
9. Create `ai-conversations/copilot-task-9.md` documenting:

- task name/goal
- prompt summary
- implementation/result
- files changed
- tests and results
- important decisions/assumptions
- any corrections made during implementation

### Important
Stop after completing this task. Do not proceed to frontend, Docker, or other tasks.

## Task 10 - Frontend Chat UI

### Goal
Implement the frontend chat interface for the existing Enterprise Knowledge Base RAG Chatbot.

The frontend should allow a user to enter a natural-language question, send it to the existing backend `POST /chat` endpoint, display the generated answer, and display the returned source references.

### Existing backend API
`POST /chat`

Request:

```
{
  "question": "What should OAuth redirect URLs use?"
}
```
Response:

```
{
  "answer": "OAuth redirect URLs must use HTTPS.",
  "sources": [
    {
      "chunk_id": "authentication-0",
      "document": "authentication",
      "title": "Authentication",
      "distance": 0.12
    }
  ]
}
```

### Requirements

1. Implement the chat UI in the existing React/Vite/TypeScript frontend.
2. Provide:

- a text input or textarea for the question
- a Send button
- display of the user's question
- display of the assistant answer
- display of returned source references
- loading state while waiting for the backend
- readable error state when the request fails
3. Send requests to the existing backend `POST /chat`.
4. Do not duplicate any RAG, retrieval, embedding, or LLM logic in the frontend.
5. Keep the UI simple and clean. This is a technical take-home prototype, not a production design exercise.
6. Keep TypeScript types for the `/chat` request and response instead of using `any`.
7. Keep the implementation small and easy to understand.
8. Do not add a frontend state-management library or UI framework unless already present in the project.
9. Do not modify backend Python code.
10. Do not modify Docker configuration in this task.
11. Add or update frontend tests only if a testing setup already exists. Do not introduce a large new frontend testing framework just for this task.
12. Create `ai-conversations/copilot-task-10.md` documenting:

- task name/goal
- prompt summary
- implementation/result
- files changed
- tests/result
- important decisions/assumptions
- any corrections made

### Important
Stop after completing this task. Do not proceed to Docker, production improvements, README polishing, or other tasks.

## Task 11 - Configuration and Docker/Chroma integration

### Goal
Fix the application's configuration and Docker integration so that the backend container uses the dedicated ChromaDB service defined in `docker-compose.yml`.

Do not change the RAG logic, retrieval behavior, API contract, frontend code, or LLM behavior.

### Required changes

1. **Configuration**
Update `backend/app/config.py` so that `Settings` reads configuration values from environment variables instead of only using hard-coded defaults.

Use the standard Pydantic settings approach (`pydantic-settings` / `BaseSettings`).

The following environment variables must be supported:

- `APP_ENV`
- `BACKEND_HOST`
- `BACKEND_PORT`
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `OPENAI_EMBEDDING_MODEL`
- `CHROMA_HOST`
- `CHROMA_PORT`
- `CHROMA_COLLECTION`
Keep sensible defaults for local development.

Remove stale comments/docstrings saying that configuration will be wired later.

If `pydantic-settings` is not already in `backend/requirements.txt`, add it.

1. **Chroma client**
Update `backend/app/vector_store.py`.

The current implementation uses:

```
chromadb.PersistentClient(...)
```
This must be changed because the project already provides a dedicated ChromaDB container through Docker Compose.

Use Chroma's HTTP client instead:

```
chromadb.HttpClient(
    host=self.settings.chroma_host,
    port=self.settings.chroma_port,
)
```
Keep the existing dependency injection support for `chroma_client` and `openai_client` so the existing unit tests continue to use fake clients.

Do not change `index_chunks()` or `search()` behavior except where necessary to support the new client construction.

Update the module docstring if necessary so it no longer incorrectly describes the implementation as an embedded `PersistentClient`.

1. **Docker Compose**
Update `docker-compose.yml`:

- Remove the obsolete top-level `version: "3.9"` field.
- The backend must use `CHROMA_HOST=chromadb`.
- The backend must use `CHROMA_PORT=8000` because port `8000` is the Chroma container's internal port.
- Keep the host mapping `"8001:8000"` so Chroma remains accessible from the host on port 8001.
- Keep the existing named `chroma_data` volume.
- Keep the existing frontend proxy configuration:
`VITE_API_PROXY_TARGET: http://backend:8000`.
Do not redesign Docker Compose.

1. **Environment example**
Update `.env.example` to match the actual configuration.

Remove the obsolete:

```
VITE_API_URL
```
and use:

```
VITE_API_PROXY_TARGET=http://localhost:8000
```
Make sure the Chroma values represent host/local development correctly. The Docker Compose environment should still override them for container-to-container communication.

Do not add real secrets.

1. **Tests**
Add or update focused tests for configuration so that environment variables are actually read.

Keep all existing tests passing.

Do not add a new testing framework.

Run:

```
python -m pytest tests -q
```
from the `backend` directory.

1. **Conversation log**
Create/update:

```
ai-conversations/copilot-task-11.md
```
Include:

- Task name and goal
- Prompt summary
- Implementation/result
- Files changed
- Tests and result
- Important decisions/assumptions
- Any corrections made during implementation
Do not copy large amounts of source code into the log.

### Important constraints

- Do NOT modify `rag.py`.
- Do NOT modify `ingestion.py`.
- Do NOT modify `indexing.py`.
- Do NOT modify `main.py` except if absolutely required for configuration integration.
- Do NOT modify frontend files.
- Do NOT change the `/chat` API contract.
- Do NOT add local LLM or local embedding support yet.
- Do NOT add retries, healthchecks, or other production infrastructure unless required for this task.
- Keep the existing dependency injection used by the unit tests.
- Stop after this task; do not start the next task automatically.

## Task 1 - Add configurable AI provider settings

Update only `backend/app/config.py` and the relevant configuration tests.

**Goal:** Prepare the configuration for switching between local Ollama and remote OpenAI without changing the existing RAG behavior yet.

Requirements:

1. Add an `ai_provider` setting, read from `AI_PROVIDER`, defaulting to `"ollama"`.
2. Accept only `"ollama"` or `"openai"`. Normalize the value to lowercase so `OLLAMA` and `OpenAI` are also accepted. Reject any other value with a clear validation error.
3. Add these Ollama settings:

- `ollama_base_url`: default `"http://host.docker.internal:11434"`, environment variable `OLLAMA_BASE_URL`.
- `ollama_chat_model`: default `"llama3.2"`, environment variable `OLLAMA_CHAT_MODEL`.
- `ollama_embedding_model`: default `"nomic-embed-text"`, environment variable `OLLAMA_EMBEDDING_MODEL`.
4. Keep the existing OpenAI settings and defaults unchanged.
5. Keep all existing ChromaDB and application settings unchanged.
6. Add or update focused tests to verify:

- The default provider is `"ollama"`.
- Both supported providers are accepted.
- Provider values are case-insensitive.
- An unsupported provider raises a validation error.
- Ollama settings have the expected defaults.
7. Do not change `llm.py`, `vector_store.py`, `requirements.txt`, Docker Compose, `.env`, or any other files.
8. Follow the project's existing coding and testing conventions. Do not modify unrelated code.
Before finishing, summarize the changed files and show the test results. Do not commit changes.
9. Create a conversation log at `ai-conversations/copilot-task-N.md`, using the next available sequential task number. Follow the format of existing task logs. Include the task name, the full prompt given to Copilot, a summary of the implementation, the files changed, the tests executed and their results. Do not overwrite existing logs. If the directory or previous logs do not exist, inspect the repository and handle this safely.

## Task 12 - Correct Configuration and Conversation Log

The current Task 12 is not complete. Fix the existing task; do not start a new task.

### Scope
Modify only:

- `backend/app/config.py`
- `backend/tests/test_config.py`
- `ai-conversations/copilot-task-12.md`
Do not modify any other files.

### Configuration requirements

1. Read `AI_PROVIDER` explicitly from the environment using the project's existing Pydantic Settings conventions.
2. Keep `ollama` as the default only when `AI_PROVIDER` is not set. The provider must remain configurable through environment variables; do not hardcode the selected runtime into application logic.
3. Accept only `ollama` and `openai`, normalizing case and surrounding whitespace. Reject unsupported values with a clear validation error.
4. Read all Ollama settings from their respective environment variables: `OLLAMA_BASE_URL`, `OLLAMA_CHAT_MODEL`, and `OLLAMA_EMBEDDING_MODEL`.
5. Preserve the existing OpenAI, ChromaDB, and application settings and defaults.
6. Do not implement provider clients or change runtime behavior in this task.
7. Add or adjust focused tests to verify environment-variable loading, defaults, case normalization, and validation failure. Ensure the tests isolate environment variables from the developer's actual environment.
8. Run the configuration tests and the full backend test suite. Report the actual command output and results; do not claim tests passed unless they were executed successfully.

### Conversation log requirements
Correct `ai-conversations/copilot-task-12.md` to match the structure and conventions of the existing `ai-conversations/copilot-task-11.md`.

- Use the heading `Task 12`, not `Task 1`.
- Preserve the full prompt given to Copilot accurately, including this corrective prompt. Do not convert URLs or code into different Markdown content.
- Include the task name and goal, full prompt(s), implementation summary, exact files changed, actual test commands and results, important decisions, and corrections/limitations.
- Do not overwrite or remove the history of the original Task 12 prompt and implementation. Record the correction as part of the same task log.
- Do not create another task log or change the numbering.
- Inspect Task 11 and follow its format rather than inventing a new one.
Before finishing, show the code diff, the updated Task 12 log, and the actual test results. Do not commit changes.

## Task 13 - Implement Configurable Ollama/OpenAI Providers

### Goal

Implement runtime selection between local Ollama and remote OpenAI using the configuration introduced in Task 12.

The application must use the selected provider for both chat generation and document embeddings. Preserve the existing RAG pipeline, retrieval behavior, citations, API contract, and frontend.

Before making changes, inspect the existing implementation and the Task 11 and Task 12 conversation logs. Follow the existing project architecture and testing conventions. Do not assume the current implementation details without inspecting the files.

### Required changes

#### 1. Chat generation

Update the existing LLM integration so that it selects the provider using `settings.ai_provider`.

* When `AI_PROVIDER=ollama`, use the configured `OLLAMA_BASE_URL` and `OLLAMA_CHAT_MODEL`.
* When `AI_PROVIDER=openai`, preserve the existing OpenAI chat behavior and use `OPENAI_API_KEY` and `OPENAI_MODEL`.
* Do not require an OpenAI API key when using Ollama.
* Fail with a clear, actionable error if the selected provider cannot be initialized or used.
* Reuse existing abstractions and dependencies where practical. Do not introduce a new framework unnecessarily.

#### 2. Embeddings

Update the existing embedding integration so that it uses the same selected provider.

* Ollama must use `OLLAMA_BASE_URL` and `OLLAMA_EMBEDDING_MODEL`.
* OpenAI must continue using `OPENAI_API_KEY` and `OPENAI_EMBEDDING_MODEL`.
* Use the embedding API supported by the installed Ollama version. Inspect the existing dependencies before deciding whether to use an existing client library or HTTP client.
* Handle provider errors without silently returning invalid or empty embeddings.
* Keep the embedding output compatible with the existing ChromaDB indexing and search interfaces.

#### 3. ChromaDB collection and embedding compatibility

Different embedding models can produce vectors with different dimensions and incompatible embedding spaces.

* Ensure documents indexed with one embedding configuration are not silently mixed with vectors from another configuration.
* Inspect the existing ChromaDB collection configuration and persistence behavior before implementing a solution.
* Prefer the smallest safe change that isolates collections by provider and embedding model, or another equally safe approach consistent with the current design.
* Preserve existing indexed data where possible. Do not automatically delete collections or erase persisted data.
* Document any required reindexing when changing embedding models.
* Keep indexing and retrieval consistent: queries must use the same embedding configuration as the indexed documents.

#### 4. Configuration and compatibility

Use the settings added in Task 12. Do not duplicate configuration or hardcode provider selection in application logic.

* Preserve the existing FastAPI endpoints and request/response models.
* Preserve the `/chat` API contract.
* Preserve citations and the current retrieval flow.
* Do not change frontend behavior.
* Do not add unrelated infrastructure, retries, health checks, or features.
* Do not require an OpenAI account or API key for local Ollama mode.

#### 5. Tests

Add or update focused unit tests for:

* Ollama chat selection and configured model/URL.
* OpenAI chat selection and preservation of existing behavior.
* Ollama embedding selection and configured model/URL.
* OpenAI embedding selection and preservation of existing behavior.
* Missing or invalid provider configuration where applicable.
* Provider failures and invalid embedding responses.
* Consistent embedding configuration between indexing and query retrieval.
* Isolation of collections or other protection against mixing incompatible embedding models.
* Existing dependency injection and test compatibility.

Use fake clients or mocked HTTP responses. Unit tests must not require a running Ollama server, network access, or a real OpenAI API key.

Run the configuration tests and the full backend test suite from the `backend/` directory:

`python -m pytest tests/test_config.py -q`
`python -m pytest tests -q`

Report the actual test results. Do not claim that a test passed unless it was executed successfully.

#### 6. Conversation log

Create `ai-conversations/copilot-task-13.md`, using the next sequential task number.

Follow the structure and conventions established by `ai-conversations/copilot-task-11.md` and corrected in Task 12.

Include:

* Task name and goal.
* The complete original prompt given to Copilot, verbatim.
* Implementation/result.
* Exact files changed.
* Actual test commands and results.
* Important decisions and assumptions.
* Corrections and limitations, including any required reindexing.
* Any corrective prompts sent during this task, verbatim, and the corresponding corrections.

Do not overwrite previous task logs. Do not replace the original prompt with a summary. Preserve URLs and code exactly as sent rather than converting them into different Markdown content.

### Constraints

* Do not change the frontend or the `/chat` API contract.
* Do not rewrite the RAG pipeline or retrieval algorithm.
* Do not delete existing ChromaDB data.
* Do not add an OpenAI dependency if the project already has a suitable one.
* Do not add a new testing framework.
* Do not commit changes.
* Do not start another task automatically.

Before finishing, show the code diff, the complete Task 13 conversation log, and the actual test results. If any requirement cannot be safely implemented within this scope, explain the blocker rather than silently omitting it.

## Task 14 - Improve Markdown-aware document chunking

### Goal

Improve the deterministic character-based chunking in `backend/app/ingestion.py` so chunks preserve meaningful Markdown content and avoid splitting paragraphs or sentences unnecessarily.

### Current problem

`chunk_documents()` currently splits text at fixed character offsets. This can split words, sentences, Markdown sections, and list items in the middle. For example, a chunk may end with `Log each sync event for aud` and the next chunk may start with the remainder.

### Requirements

1. Keep the public `chunk_documents(documents, chunk_size=500, overlap=50)` function signature unchanged.
2. Keep `LoadedDocument` and `DocumentChunk` unchanged.
3. Preserve deterministic chunk ordering, metadata, and IDs in the format `<document-name>-<zero-based-index>`.
4. Keep current parameter validation:

   * `chunk_size` must be greater than zero.
   * `overlap` must be non-negative and smaller than `chunk_size`.
5. Prefer splitting at meaningful boundaries, in this order:

   * Markdown block / paragraph boundaries.
   * Sentence boundaries when a block exceeds the chunk limit.
   * Character boundaries only when a single sentence or indivisible block is too long.
6. Never exceed `chunk_size` characters per chunk.
7. Preserve all non-whitespace document content. Do not silently drop text.
8. Keep overlap deterministic and avoid producing chunks that contain only overlap or whitespace.
9. Preserve short documents as a single chunk.
10. Empty or whitespace-only documents must still produce no chunks.
11. Do not modify `vector_store.py`, `indexing.py`, RAG logic, API behavior, configuration, Docker files, or dependencies.
12. Do not introduce third-party libraries.

### Tests

Update `backend/tests/test_ingestion.py` to cover:

- Existing loading and validation behavior.
- Existing short-document behavior.
- Deterministic chunk IDs and ordering.
- Chunks staying within `chunk_size`.
- Preference for paragraph boundaries.
- Preference for sentence boundaries when a paragraph is too long.
- Character-level fallback for a long sentence or token.
- Correct overlap behavior.
- Preservation of the original non-whitespace content without accidental omissions.
- Empty and whitespace-only documents.

Do not keep tests that require arbitrary fixed character slices when the new algorithm is expected to prefer semantic boundaries. Replace those assertions with behavior-based expectations.

### Acceptance criteria

- Run `pytest backend/tests/test_ingestion.py -q` from the repository root, or run `pytest tests/test_ingestion.py -q` from `backend`.
- Run the full backend test suite afterward.
- Report the exact test commands and actual results.
- Review the final diff and ensure only `backend/app/ingestion.py` and `backend/tests/test_ingestion.py` changed.

Implement the smallest clear solution. Do not make unrelated refactors.

## Task 15 - Keep Markdown Section Headings with Their Content

### Goal

Improve Markdown-aware chunking so section headings stay with the content they introduce whenever possible. Preserve the existing behavior for paragraph boundaries, sentence splitting, overlap, maximum chunk size, deterministic IDs, and content preservation.

## Context

The current implementation in `backend/app/ingestion.py` produces 8 chunks from the four knowledge-base documents. Some section headings end up at the end of the previous chunk while their content starts in the next one.

Examples observed:

- `## Best Practices` is at the end of `authentication-0`, while its bullet list is in `authentication-1`.
- `## Operational Notes` is at the end of `integrations-0`, while its bullet list is in `integrations-1`.
- `## Billing Rules` is at the end of `payments-0`, while its bullet list is split across the two chunks.
- `## Resolution Steps` is at the end of `troubleshooting-0`, while the numbered steps are split across the two chunks.

This can reduce retrieval quality when a query retrieves a chunk containing the heading but not the associated content, or vice versa.

### Requirements

1. Inspect the existing implementation and tests before editing.
2. Update Markdown-aware chunking so a section heading is preferably grouped with the first content block it introduces, rather than being packed at the end of the preceding chunk.
3. Preserve heading and content text exactly; do not drop, duplicate, or rewrite source content except for the existing intentional overlap behavior.
4. Keep chunks at or below `chunk_size` characters.
5. Preserve current sentence-aware splitting and word-aware fallback behavior for oversized content.
6. Preserve the existing `chunk_documents()` function signature, metadata, deterministic chunk IDs, and validation behavior.
7. Keep paragraph and list formatting as intact as reasonably possible. Do not split a short list unnecessarily if it can fit in one chunk.
8. Add focused tests that reproduce the heading/content boundary issue. Cover at least:

- A heading followed by a short paragraph.
- A heading followed by a short bullet list.
- A heading followed by a numbered list.
- A heading that must still be split from content when the size limit makes grouping impossible.
- Existing overlap and content-preservation behavior.
9. Run `pytest backend/tests/test_ingestion.py -q`, then `pytest backend/tests -q`. Report the actual outputs and do not claim success if a command was not run.
10. Keep the change scoped to `backend/app/ingestion.py` and `backend/tests/test_ingestion.py`, plus the required AI usage logs. Do not change the RAG prompt, retrieval algorithm, vector store, API, frontend, or Docker configuration.

### AI usage logging - required

Update or create `ai-conversations/copilot-task-15.md`. Include:

- Task number and goal.
- The exact prompt used for this task.
- A concise summary of the implementation.
- Files changed.
- Tests actually run and their actual results.
- Any limitations or follow-up work.

Append this exact task prompt to `ai-conversations/raw_prompts.md` as well. Do not merely summarize the prompt there.

Do not claim test results that have not been observed. If tests cannot be run, record them as pending and explain why.

### Completion response

Summarize the implementation, explain the heading-grouping behavior, list files changed, and provide actual test results. Flag any unrelated changes already present in the working tree instead of silently reverting them.

## Task 16 - Safely remove stale chunks during reindexing

### Goal

Update the ChromaDB indexing logic to remove obsolete chunks when a document produces fewer chunks after reindexing, while preserving unrelated documents and avoiding premature deletion of existing records.

### Context

* `backend/app/indexing.py` loads Markdown documents, chunks them, and calls `VectorStore.index_chunks(chunks)`.
* `backend/app/vector_store.py` generates embeddings and uses ChromaDB `upsert` with deterministic chunk IDs.
* Upsert inserts or updates matching IDs but does not remove obsolete IDs from previous indexing runs.
* ChromaDB collections are separated by embedding provider and embedding model.
* Task 15 improved Markdown heading and content grouping. Reindexing must not leave obsolete chunks from earlier indexing runs.

### Requirements

1. Keep existing public interfaces unchanged unless a change is strictly necessary.
2. Preserve embedding-provider behavior, collection naming, metadata, deterministic IDs, and the search API.
3. Generate and validate all embeddings before modifying the collection.
4. Successfully upsert the incoming chunks before attempting to delete obsolete records.
5. After a successful upsert, remove stale records belonging to documents represented in the incoming chunks. Preserve records belonging to all other documents.
6. If embedding generation fails, do not modify existing collection records.
7. If upsert fails, do not attempt stale-record deletion.
8. An empty chunk list must not delete existing records.
9. Repeated indexing of the same chunks must be idempotent.
10. Use APIs compatible with the project's installed ChromaDB version.
11. Keep the implementation simple and avoid unrelated refactoring.
12. Do not claim transactional guarantees that ChromaDB does not provide.

### Tests

Add focused unit tests using fake clients or collections as appropriate. Verify actual stored IDs and metadata where possible.

Cover:

* Reindexing a document with fewer chunks removes obsolete IDs.
* Existing IDs are updated and new chunks are stored.
* Chunks belonging to unrelated documents are preserved.
* Embedding-generation failure leaves existing records unchanged.
* Upsert failure does not trigger stale-record deletion.
* Empty input leaves the collection unchanged.
* Repeated indexing creates no duplicates and preserves valid records.
* Existing provider-specific behavior and tests continue to pass.

### Scope restrictions

* Do not change ingestion or chunking behavior.
* Do not change RAG prompts, retrieval ranking, API contracts, frontend, or Docker configuration.
* Do not clear or recreate the entire collection.
* Do not revert unrelated user changes.

### AI usage logging requirements

Create `ai-conversations/copilot-task-16.md` using **exactly these seven sections, in this order**, with the same headings and no additional sections:

1. `## Task name and goal`
2. `## Prompt summary`
3. `## Implementation / result`
4. `## Files changed`
5. `## Tests and result`
6. `## Important decisions / assumptions`
7. `## Corrections / limitations`

Fill them as follows:

* **Task name and goal:** Give the task name and concise goal.
* **Prompt summary:** Summarize the task in your own words. Do not paste the complete prompt here and do not use a heading or field named `Exact Prompt`.
* **Implementation / result:** Describe what was actually implemented and the result. Do not invent completed work.
* **Files changed:** List only files actually changed and briefly describe each change.
* **Tests and result:** Record actual test commands and results, distinguishing passed, failed, and not-run tests.
* **Important decisions / assumptions:** Record relevant implementation choices and assumptions, including the stale-record deletion strategy.
* **Corrections / limitations:** Record relevant warnings, unresolved issues, limitations, or corrections. If none were found, say so only after checking.

Append the **complete Task 16 prompt verbatim** to `ai-conversations/raw_prompts.md` under the Task 16 heading. Do not put the full prompt in `copilot-task-16.md`.

Preserve existing logs and unrelated user changes. Do not reformat or rewrite earlier task entries.

### Validation

1. Run the focused vector-store tests first.
2. Run the full backend test suite.
3. Review the final diff and `git status --short`.
4. Record actual commands and outputs in the task log and final summary.
5. Investigate failures and report them honestly. Do not weaken tests merely to obtain a passing result.
6. If the implementation or validation is incomplete, explicitly document that in the task log.
