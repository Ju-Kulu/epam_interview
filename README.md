# Enterprise Knowledge Base RAG Chatbot

A Docker Compose RAG prototype that answers questions from four mock enterprise Markdown guides and returns inspectable source references.

## Start

Prerequisites: Docker Desktop on Windows, or Docker Engine and the Compose plugin on Linux; network access for container images and Ollama models; and several gigabytes of free disk space. No host Python, Node.js, Ollama installation, or manual model download is required for the default setup.

From the repository root, run:

```powershell
docker compose up --build
```

Keep this terminal open. On first startup, Compose builds the frontend/backend images, downloads the Ollama image and configured models, starts ChromaDB, then starts the backend after dependencies are ready. Docker reported the Ollama image at about 3.8 GB in this audit; model weights add more, so the first pull can take several minutes or substantially longer depending on network speed. The models and Chroma database persist across restarts.

When backend startup/indexing has completed, open:

- Chat UI: <http://localhost:5173>
- Backend health: <http://localhost:8000/health>
- Interactive API docs: <http://localhost:8000/docs>

To stop the stack, press `Ctrl+C`, or from another terminal in the repository run:

```powershell
docker compose down
```

This stops and removes containers but keeps named data volumes. Do not add `-v` unless you intend to delete the persisted Chroma database and Ollama models.

## What runs

Compose starts the React/Vite frontend (`frontend`), FastAPI backend (`backend`), ChromaDB (`chromadb`), Ollama (`ollama`), and a one-shot `ollama-models` job. The model job pulls the configured chat and embedding models from the Ollama service; Ollama stores model files in the `ollama_data` volume. ChromaDB stores vectors in `chroma_data`. The backend reaches Ollama at `http://ollama:11434` and ChromaDB at `chromadb:8000`; host ports are 5173, 8000, and 8001 respectively.

At backend startup, the service loads Markdown from `/data` (the read-only Compose mount of `./data`), chunks it, generates embeddings, and upserts chunks with source metadata into a provider/model-specific Chroma collection. The backend waits for Chroma health and for the model-pull job to finish before starting. Ollama health is checked before pulling models.

For `POST /chat`, the backend embeds the question with the same embedding model used for indexing, retrieves the three nearest chunks, and sends only their text as context to the chat model. The response contains an answer and source metadata (`chunk_id`, `document`, `title`, `distance`). Click a source title in the UI to open the original document through `GET /documents/{document_id}`.

Similarity distance is not a confidence score. Retrieval has no relevance threshold, reranker, hybrid search, authentication, or authorization. The prompt asks the model to stay within the context but does not guarantee factual correctness.

## Configuration

The defaults work without a `.env` file. Compose also reads an optional root `.env` for overrides. `.env.example` is a safe template; copy it only if you want to edit settings. Never commit real API keys.

| Variable | Default | Use |
|---|---|---|
| `AI_PROVIDER` | `ollama` | `ollama` or `openai`; selects both chat and embedding providers. |
| `OLLAMA_CHAT_MODEL` | `llama3.2` | Ollama answer-generation model. |
| `OLLAMA_EMBEDDING_MODEL` | `nomic-embed-text` | Ollama document/question embedding model. |
| `OLLAMA_BASE_URL` | Compose sets `http://ollama:11434` | Backend-to-Ollama address inside Compose. |
| `OPENAI_API_KEY` | unset | Required only for OpenAI mode. Store the key in ignored `.env`. |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI chat model. |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model. |
| `CHROMA_COLLECTION` | `knowledge_base` | Base name; provider and embedding model are added to the actual collection name. |

To use OpenAI, set `AI_PROVIDER=openai` and provide `OPENAI_API_KEY` in `.env`; then rerun `docker compose up --build`. Compose skips Ollama model downloads in OpenAI mode, though the Ollama service remains defined. This mode is implemented but has not been verified against the live OpenAI service.

The backend configuration has local defaults `CHROMA_HOST=localhost` and `CHROMA_PORT=8001`; Compose overrides these to `chromadb:8000`. `APP_ENV`, `BACKEND_HOST`, and `BACKEND_PORT` are accepted settings, but the Dockerfile's Uvicorn command fixes the bind host/port. `FRONTEND_PORT` in `.env.example` is informational and is not used to change the fixed 5173 mapping. The data path is `/data` and is not configurable by environment variable.

## Verify and troubleshoot

From another PowerShell window at the repository root:

```powershell
docker compose ps
Invoke-RestMethod http://localhost:8000/health
$body = @{ question = 'What should OAuth redirect URLs use?' } | ConvertTo-Json
$result = Invoke-RestMethod -Method Post -Uri http://localhost:8000/chat -ContentType 'application/json' -Body $body
$result.answer
$result.sources | Format-Table chunk_id, document, title, distance
```

The health response is `{"status":"healthy"}`; it is not a downstream readiness probe. A successful chat response with sources verifies more of the path. Backend API docs are at `/docs`.

Common checks:

- **Startup still in progress:** model/image downloads can take minutes. Inspect `docker compose logs -f ollama-models backend chromadb` in another terminal.
- **Ollama/model error:** inspect `docker compose logs ollama ollama-models`; check model names in `.env` and network access for downloads. Models are downloaded automatically on startup when absent.
- **Chroma connection error:** check `docker compose logs chromadb`; backend-to-Chroma uses `chromadb:8000`, not host port 8001.
- **Port already in use:** free host port 5173, 8000, or 8001 before starting, or intentionally edit the corresponding Compose mapping.
- **HTTP 422 from `/chat`:** send JSON with a non-empty string `question`.
- **Backend exits during startup:** inspect `docker compose logs backend`; indexing needs `/data`, Chroma, and the configured embedding provider available.

Backend tests (run in another terminal while the stack is up):

```powershell
docker compose exec backend python -m pytest tests -q
```

The backend Docker image installs the pinned packages from `backend/requirements.txt` during its image build. Backend tests use fakes for provider/vector-store behavior and do not require model calls. There is no frontend unit-test framework; its production build is `npm run build` inside `frontend/` or `docker compose exec frontend npm run build`.

## Data and limitations

The four source guides are in `data/` and mounted read-only into the backend. Backend startup reindexes all current documents each time, upserting current IDs and deleting stale chunks for documents still present in that indexing batch. Removing an entire document from `data/` does not currently trigger deletion of all its old vectors.

Changing provider or embedding model selects a separate collection. Current documents are indexed there at backend startup; previous collections are kept and are not migrated or deleted. Model files persist in `ollama_data`; Chroma vectors persist in `chroma_data`. A normal `docker compose down` preserves both; `docker compose down -v` deletes them.

This is a local prototype with four mock guides and no production frontend server, authentication, access control, monitoring, or remote deployment configuration. The original assignment requests an AI-assistant conversation export; the repository contains task summaries and archived prompts, not a complete transcript export. Review whether that satisfies the evaluator's requirement.

Task-by-task AI usage summaries are in `ai-conversations/`; raw prompts are archived in `ai-conversations/raw_prompts.md`. The source code and tests remain the authority for implemented behavior.
